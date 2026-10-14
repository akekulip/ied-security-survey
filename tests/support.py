"""Shared by every test file: fake replies, a small PDF, and the helpers of the base test class."""
import io
from pathlib import Path
import unittest
from unittest.mock import patch

from iedsurvey.crawl import crawl
from iedsurvey.fetch import Fetcher
from iedsurvey.inventory import inventory
from iedsurvey.leads import candidates
from iedsurvey.store import digest, dump, load


ROOT = Path(__file__).resolve().parent.parent


class Reply(io.BytesIO):
    def __init__(self, body=b'', code=200, headers=None):
        super().__init__(body)
        self.code, self.headers = code, headers or {}


def tiny_pdf(pages, bookmark=None):
    """Smallest text PDF pypdf will read: one font, one content stream per page, optional bookmark (title, page index).
    A page is one line of text or a list of lines."""
    n = len(pages)
    info, outlines = 4 + 2 * n, 5 + 2 * n
    objs = [f'<< /Type /Catalog /Pages 2 0 R{f" /Outlines {outlines} 0 R" if bookmark else ""} >>'.encode(),
            f'<< /Type /Pages /Kids [{" ".join(f"{4 + 2 * i} 0 R" for i in range(n))}] /Count {n} >>'.encode(),
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    for i, text in enumerate(pages):
        lines = [text] if isinstance(text, str) else text
        stream = ('BT /F1 12 Tf 14 TL 72 720 Td ' + ' T* '.join(f'({line}) Tj' for line in lines) + ' ET').encode() if text else b''
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> '
                    f'/Contents {5 + 2 * i} 0 R >>'.encode())
        objs.append(b'<< /Length %d >>\nstream\n%s\nendstream' % (len(stream), stream))
    objs.append(b'<< /Title (Test Relay Manual) /CreationDate (D:20260102030405Z) >>')
    if bookmark:
        objs.append(f'<< /Type /Outlines /First {outlines + 1} 0 R /Last {outlines + 1} 0 R /Count 1 >>'.encode())
        objs.append(f'<< /Title ({bookmark[0]}) /Parent {outlines} 0 R /Dest [{4 + 2 * bookmark[1]} 0 R /Fit] >>'.encode())
    out, offsets = b'%PDF-1.4\n', []
    for i, o in enumerate(objs):
        offsets.append(len(out))
        out += b'%d 0 obj\n%s\nendobj\n' % (i + 1, o)
    xref = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1) + b''.join(b'%010d 00000 n \n' % x for x in offsets)
    return out + b'trailer\n<< /Size %d /Root 1 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, info, xref)


class SurveyCase(unittest.TestCase):
    """What the tests share: a fake vendor site, scripted replies, a config on disk, a reviewed run."""

    def fixture(self):
        source={'id':'s','product_id':'p','status':'extracted','sha256':'abc'}
        row={'product_id':'p','feature':'tls','status':'supported','source_ids':['s'],
             'source_hashes':{'s':'abc'},'reviewer':'test','reviewed_at':'2026-10-13','rationale':'explicit',
             'protocol':'HTTPS','interface':'management','interface_class':'management','firmware':'unknown','implementation':'native','location':'page 2'}
        return source,row

    def leads(self, text, location='html-block:1'):
        hits = candidates({'id':'x','product_id':'p'}, [{'location':location,'text':text}])
        self.assertTrue(all(h['status']=='unreviewed' for h in hits))
        return [h['feature'] for h in hits]

    def scripted(self, td, replies, config=None):
        """Fetcher whose raw() answers from a {url: (status, headers, body)} table and logs like the real one."""
        f = Fetcher(config or {}, td)
        def raw(url):
            f.audit.append({'url':url})
            if isinstance(replies[url], Exception): raise replies[url]
            return replies[url]
        return f, patch.object(f, 'raw', side_effect=raw)

    def site(self, pages, calls):
        """Fetcher.fetch stand-in serving {url: html bytes}; an Exception value is raised instead."""
        def fetch(fetcher, url, domains):
            calls.append(url)
            if isinstance(pages.get(url), BaseException): raise pages[url]
            if url not in pages: raise ValueError('HTTP 404')
            h = digest(pages[url]); (fetcher.cache/h).write_bytes(pages[url])
            return {'sha256':h,'headers':{'Content-Type':'text/html'},'final_url':url,'retrieved_at':'2026-10-13T00:00:00+00:00'}, pages[url]
        return patch.object(Fetcher, 'fetch', fetch)

    def config(self, p, products, **options):
        cfg = {'sampling':'synthetic', **options, 'products':[{'vendor':'v','model':x['id'].upper(),'category':'relay','domains':['vendor.test'], **x} for x in products]}
        dump(p/'cfg.json', cfg)
        return p/'cfg.json'

    def reviewed_run(self, p):
        """One relay with TLS for DNP3 and a login for its web page, one relay with only a web login, one unreviewed meter."""
        pages = {'https://vendor.test/a': b'<p>TLS is supported for DNP3 sessions.</p><p>The web interface requires a user login with a password.</p>',
                 'https://vendor.test/b': b'<p>The web interface requires a user login with a password.</p>'}
        cfg = self.config(p, [{'id':'a','seeds':['https://vendor.test/a']},{'id':'b','seeds':['https://vendor.test/b']},{'id':'m','category':'meter','seeds':[]}])
        with self.site(pages, []): crawl(cfg, p/'run', p/'cache')
        src = {x['product_id']: x for x in load(p/'run'/'sources.json')}
        def row(pid, feature, status, interface='', kind='', quote='', **more):
            base = {'product_id':pid,'feature':feature,'status':status,'source_ids':[src[pid]['id']],'source_hashes':{src[pid]['id']:src[pid]['sha256']},
                    'location':'html-block:1','protocol':f'{feature} detail','interface':interface,'interface_class':kind,'firmware':'v2 or later',
                    'implementation':'native','conditions':'','evidence':[{'source_id':src[pid]['id'],'location':more.pop('at','html-block:1'),'quote':quote}] if quote else [],
                    'rationale':'explicit','reviewer':'A. Reviewer','reviewed_at':'2026-10-13','review_status':'draft'}
            if status in ('supported', 'conditional'):
                base.update(model_scope='not established', hardware_revision='not established', support_basis=['built_in'],
                            default_state='undocumented', activation_needs=['none_stated'])
            return dict(base, **more)
        login = 'The web interface requires a user login'
        rows = [row('a','tls','supported','DNP3 server','control_protocol','TLS is supported for DNP3 sessions.'),
                row('a','encryption','supported','DNP3 server','control_protocol','TLS is supported for DNP3 sessions.', review_status='confirmed', reviewer='P. Author'),
                row('a','authentication','conditional','Web interface','management',login, at='html-block:2', conditions='password must be set'),
                row('a','authentication','unknown'), row('a','ssh','unknown'),
                row('b','authentication','supported','Web interface','management',login),
                row('b','encryption','unknown'), row('b','tls','unknown')]
        dump(p/'reviews.json', rows)
        return src

    PROFILE = [['DNP3 SPECIFICATION', 'DEVICE PROFILE', 'Vendor relay X1'],
               ['1.12 SECURITY PARAMETERS ............ 3', '1.12.1 DNP3 device support for secure authentication: .... 3'],
               ['Device Profile Page 3', '1.12 SECURITY PARAMETERS Capabilities Current Value', '1.12.1 DNP3 device support for secure',
                'authentication:', 'If the device does not support secure authentication', 'then ignore the rest of this section.',
                'Supported versions:', 'X  Fixed at Version 5', ' Configurable, selectable from __', '1.12.2 Maximum number of users:', 'X  Fixed at 1'],
               ['Device Profile Page 4', '1.12 SECURITY PARAMETERS Capabilities Current Value', ' Configurable, range __ to __',
                '1.12.12 Change cipher request timeout:', 'Implementations using TLS shall terminate the connection.',
                'X  Not relevant - TLS is not used', ' Fixed at ____']]

    DEFINITIONS = {'defined_at': '2026-10-13', 'legacy': 'Legacy means the vendor states that support has ended.',
                   'lifecycle_statuses': {'end_of_support': 'The vendor states that support has ended.'}}

    VENDORS = {'title': 'Test inventory', 'robots_follow_redirects': ['vendor.test'], 'definitions': DEFINITIONS, 'vendors': {'acme': {
        'vendor': 'Acme', 'domains': ['vendor.test'], 'sitemaps': ['https://vendor.test/sitemap.xml'],
        'scope': '^https://vendor\\.test/products/[^/]+/[^/]+$',
        'exclude': [{'on': 'url', 'match': '/accessories/', 'reason': 'accessory'},
                    {'on': 'slug', 'match': 'software', 'reason': 'software'},
                    {'on': 'text', 'match': 'test set', 'reason': 'test equipment'}],
        'rules': [{'on': 'url', 'match': '/relays/', 'category': 'protective_relay'},
                  {'on': 'slug', 'match': '^pm[0-9]', 'category': 'meter'},
                  {'on': 'text', 'match': 'feeder protection', 'category': 'protective_relay'}],
        'lifecycle': [{'on': 'slug', 'match': 'legacy', 'value': 'unknown', 'vendor_label': 'legacy'}],
        'lifecycle_text': [{'match': 'support (has ended|ended)', 'value': 'end_of_support'},
                           {'match': 'has been discontinued', 'value': 'discontinued_support_not_stated'}],
        'crawl': {'max_depth': 1, 'max_pages_per_product': 3, 'follow_pattern': 'manual'}}}}

    SITEMAP = (b'<urlset><url><loc>https://vendor.test/products/relays/r100</loc></url><url><loc>https://vendor.test/products/relays/r90-legacy</loc></url>'
               b'<url><loc>https://vendor.test/products/meters/pm800</loc></url><url><loc>https://vendor.test/products/accessories/cable</loc></url>'
               b'<url><loc>https://vendor.test/products/relays/setup-software</loc></url><url><loc>https://vendor.test/products/misc/x7</loc></url>'
               b'<url><loc>https://vendor.test/about/us</loc></url><url><loc>https://vendor.test/products/relays</loc></url></urlset>')

    def catalogue(self, p, calls, pages=None):
        dump(p/'vendors.json', self.VENDORS)
        with self.site(dict({'https://vendor.test/sitemap.xml': self.SITEMAP}, **(pages or {})), calls):
            inventory(p/'vendors.json', p/'inv', p/'cache')
        return load(p/'inv'/'inventory.json')

    def frame_inventory(self, p):
        entries = []
        proof = [{'basis': 'catalogue listing', 'url': 'https://vendor.test/sitemap.xml', 'sha256': 'ab' * 32, 'retrieved_at': '2026-10-13T00:00:00+00:00'}]
        for vendor, category, lifecycle, n in [('Acme','protective_relay','currently_supported',6), ('Acme','protective_relay','discontinued_support_not_stated',2),
                                               ('Acme','meter','currently_supported',1), ('Bolt','plc','currently_supported',5)]:
            for i in range(n):
                entries.append({'id': f'{vendor}_{category}_{lifecycle}_{i}'.lower(), 'vendor_key': 'acme', 'vendor': vendor, 'model': f'M{i}', 'category': category,
                                'lifecycle': lifecycle, 'lifecycle_basis': 'catalogue listing', 'lifecycle_evidence': proof, 'included': True, 'reason': '',
                                'product_url': f'https://vendor.test/{vendor}/{category}/{lifecycle}/{i}', 'domains': ['vendor.test']})
        entries.append(dict(entries[0], id='acme_excluded', included=False, reason='accessory', excluded_by='x'))
        entries.append(dict(entries[0], id='acme_unclassified', included=False, category='unclassified', reason='no category rule matched'))
        dump(p/'inventory.json', {'created_at': '2026-10-13T00:00:00+00:00', 'spec': self.VENDORS, 'entries': entries})
        return p/'inventory.json'

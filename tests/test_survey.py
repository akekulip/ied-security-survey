import gzip
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import survey as s

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
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>'.encode())
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


class SurveyTests(unittest.TestCase):
    def test_domain_boundary(self):
        self.assertTrue(s.allowed('https://manual.vendor.test/a', ['vendor.test']))
        for u in ['https://vendor.test.evil.test/a','https://evilvendor.test/a',
                  'http://vendor.test/a','https://user@vendor.test/a', 'https://vendor.test:99/a']:
            self.assertFalse(s.allowed(u, ['vendor.test']))

    def test_hash_fragment_removed_query_retained(self):
        self.assertEqual(s.canonical('https://Vendor.test/a?lang=en#top'), 'https://vendor.test/a?lang=en')

    def test_html_no_script_or_nav(self):
        segs, links = s.extract(b'<nav>TLS</nav><script>encryption</script><p>DNP3 Secure Authentication is optional.</p><a href="manual.pdf">manual</a>', {'Content-Type':'text/html'})
        text = ' '.join(x['text'] for x in segs)
        self.assertNotIn('TLS', text)
        self.assertNotIn('encryption', text)
        self.assertEqual(links,['manual.pdf'])

    def test_negation_is_never_positive_classification(self):
        hits = s.candidates({'id':'x','product_id':'p'}, [{'location':'pdf-page:2', 'text':'TLS is not supported. DNP3 Secure Authentication is not available.'}])
        self.assertTrue(hits)
        self.assertTrue(all(h['status']=='unreviewed' for h in hits))

    def test_https_is_not_control_encryption(self):
        hits = s.candidates({'id':'x','product_id':'p'}, [{'location':'html-block:1','text':'HTTPS administration uses TLS; DNP3 traffic uses a separate port.'}])
        self.assertEqual([h['feature'] for h in hits], ['tls'])
        self.assertEqual(hits[0]['status'], 'unreviewed')

    def test_fetch_redirect_rejected_before_destination_contact(self):
        with tempfile.TemporaryDirectory() as td:
            f = s.Fetcher({'delay_seconds':0}, td)
            with patch.object(f, 'robot'), patch.object(f, 'raw', return_value=(302, {'Location':'https://evil.test/a'}, b'')) as raw:
                with self.assertRaisesRegex(ValueError,'outside vendor'):
                    f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(raw.call_count,1)

    def test_redirect_checks_robots_each_hop(self):
        with tempfile.TemporaryDirectory() as td:
            f = s.Fetcher({},td)
            with patch.object(f,'robot') as robot, patch.object(f,'raw',side_effect=[(302,{'Location':'https://docs.vendor.test/a'},b''),(200,{'Content-Type':'text/html'},b'<p>x</p>')]):
                meta,_=f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(robot.call_count,2)
                self.assertEqual(meta['sha256'],s.digest(b'<p>x</p>'))

    def test_robots_denial_and_errors_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            for status,body in [(200,b'User-agent: *\nDisallow: /private'),(503,b'unavailable'),(403,b'forbidden'),(301,b'')]:
                f=s.Fetcher({},td)
                def raw(url):
                    f.audit.append({'url':url}); return status,{},body
                with patch.object(f,'raw',side_effect=raw), self.assertRaises(ValueError):
                    f.robot('https://vendor.test/private')

    def test_robots_404_allows_and_records(self):
        with tempfile.TemporaryDirectory() as td:
            f=s.Fetcher({},td)
            def raw(url):
                f.audit.append({'url':url}); return 404,{},b'not found'
            with patch.object(f,'raw',side_effect=raw): f.robot('https://vendor.test/a')
            self.assertIn('sha256',f.audit[0])

    def fixture(self):
        source={'id':'s','product_id':'p','status':'extracted','sha256':'abc'}
        row={'product_id':'p','feature':'tls','status':'supported','source_ids':['s'],
             'source_hashes':{'s':'abc'},'reviewer':'test','reviewed_at':'2026-10-13','rationale':'explicit',
             'protocol':'HTTPS','interface':'management','interface_class':'management','firmware':'unknown','implementation':'native','location':'page 2'}
        return source,row

    def test_review_hash_binding(self):
        source,row=self.fixture()
        s.validate_reviews([row],[source],{'p'})
        row['source_hashes']['s']='changed'
        with self.assertRaisesRegex(ValueError,'hash mismatch'): s.validate_reviews([row],[source],{'p'})

    def test_wrong_product_or_failed_source_rejected(self):
        for change in [{'product_id':'q'},{'status':'failed'}]:
            source,row=self.fixture(); source.update(change)
            with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})

    def test_unreviewed_claim_and_empty_evidence_rejected(self):
        source,row=self.fixture()
        row['reviewer']=''
        with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})
        row['reviewer']='test'; row['source_ids']=[]
        with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})

    def test_duplicate_cells_rejected(self):
        source,row=self.fixture()
        with self.assertRaises(ValueError): s.validate_reviews([row,row],[source],{'p'})

    def test_corrupted_cache_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); s.dump(p/'sources.json',[{'id':'s','sha256':'abc'}]); (p/'abc').write_text('wrong')
            with self.assertRaises(ValueError): s.verify(p,p)

    def test_redirect_loop_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            f=s.Fetcher({},td)
            with patch.object(f,'robot'), patch.object(f,'raw',return_value=(302,{'Location':'/a'},b'')) as raw:
                with self.assertRaisesRegex(ValueError,'too many redirects'):
                    f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(raw.call_count,6)

    def test_download_size_limit(self):
        import io
        class Reply(io.BytesIO):
            code=200
            headers={'Content-Type':'text/html'}
        with tempfile.TemporaryDirectory() as td:
            f=s.Fetcher({'max_bytes':4},td)
            with patch.object(f.opener,'open',return_value=Reply(b'too large')):
                with self.assertRaisesRegex(ValueError,'byte limit'): f.raw('https://vendor.test/a')

    def test_bounded_link_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            cfg={'sampling':'synthetic','max_depth':1,'max_pages_per_product':2,'products':[{'id':'p','domains':['vendor.test'],'seeds':['https://vendor.test/a']}]}
            s.dump(p/'cfg.json',cfg)
            calls=[]
            def fetch(self,url,domains):
                calls.append(url)
                body=b'<p>TLS</p><a href="/manual.pdf">M</a><a href="https://evil.test/manual.pdf">E</a><a href="/security">S</a>'
                return {'sha256':s.digest(body),'headers':{'Content-Type':'text/html'},'final_url':url},body
            with patch.object(s.Fetcher,'fetch',fetch): s.crawl(p/'cfg.json',p/'run',p/'cache')
            self.assertEqual(calls,['https://vendor.test/a','https://vendor.test/manual.pdf'])

    def test_complete_offline_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); cache=p/'cache'; run=p/'run'
            cfg={'sampling':'synthetic test','max_depth':0,'products':[{'id':'p','vendor':'test','model':'test','category':'test','domains':['vendor.test'],'seeds':['https://vendor.test/a']}]}
            s.dump(p/'cfg.json',cfg)
            body=b'<p>TLS is not supported for DNP3.</p>'
            def fetch(self,url,domains):
                h=s.digest(body); (self.cache/h).write_bytes(body)
                return {'sha256':h,'headers':{'Content-Type':'text/html'},'final_url':url},body
            with patch.object(s.Fetcher,'fetch',fetch): s.crawl(p/'cfg.json',run,cache)
            s.replay(run,cache,p/'replay')
            rows=json.loads((run/'review_template.json').read_text())
            for row in rows: row.update(reviewer='test',reviewed_at='2026-10-13',rationale='not assessed')
            s.dump(p/'review.json',rows); s.report(run,p/'review.json',p/'report')
            self.assertIn('unknown',(p/'report'/'REPORT.md').read_text())
            with self.assertRaises(FileExistsError): s.crawl(p/'cfg.json',run,cache)

    # --- 1.1.0 ---

    def leads(self, text, location='html-block:1'):
        hits = s.candidates({'id':'x','product_id':'p'}, [{'location':location,'text':text}])
        self.assertTrue(all(h['status']=='unreviewed' for h in hits))
        return [h['feature'] for h in hits]

    def scripted(self, td, replies, config=None):
        """Fetcher whose raw() answers from a {url: (status, headers, body)} table and logs like the real one."""
        f = s.Fetcher(config or {}, td)
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
            h = s.digest(pages[url]); (fetcher.cache/h).write_bytes(pages[url])
            return {'sha256':h,'headers':{'Content-Type':'text/html'},'final_url':url,'retrieved_at':'2026-10-13T00:00:00+00:00'}, pages[url]
        return patch.object(s.Fetcher, 'fetch', fetch)

    def config(self, p, products, **options):
        cfg = {'sampling':'synthetic', **options, 'products':[{'vendor':'v','model':x['id'].upper(),'category':'relay','domains':['vendor.test'], **x} for x in products]}
        s.dump(p/'cfg.json', cfg)
        return p/'cfg.json'

    def test_lead_regression_table(self):
        table = {
            'Supports TLSv1.2 for DNP3': ['tls'],
            'TLS1.3 sessions': ['tls'],
            'con\ufb01gure mutual TLS': ['tls'],
            'DNP3 SAv5 is supported': ['dnp3_secure_authentication'],
            'Secure Authentication (SA) per IEEE 1815-2012': ['dnp3_secure_authentication','authentication'],
            'conforms to IEC 62351\u20115': ['dnp3_secure_authentication','iec_62351'],
            'secure authentication of web users via LDAP': ['authentication'],
            'the relay authenticates the master': ['authentication'],
            'authenti-\ncation of users': ['authentication'],
            'supports 802.1X port control': ['authentication'],
            'DNP3 traffic is unencrypted': ['encryption','plaintext_statement'],
            'does not support encryption of DNP3': ['encryption','non_support_statement'],
            'TLS is not used for DNP3': ['tls','non_support_statement'],
            'The outstation does not support DNP3 Secure Authentication': ['dnp3_secure_authentication','authentication','non_support_statement'],
            'Secure Authentication: Not Supported': ['authentication','non_support_statement'],
            'There is no support for IPsec': ['ipsec','non_support_statement'],
            'If the device does not support secure authentication then ignore the rest': ['authentication'],
            'TLS is supported. Modbus is not supported': ['tls'],
            'data is sent in plain text': ['plaintext_statement'],
            'messages are sent in clear text': ['plaintext_statement'],
            'AES-256 cipher suites': ['encryption'],
            'MACsec (IEEE 802.1AE) link encryption': ['encryption','macsec'],
            'IKEv2 tunnel between sites': ['ipsec'],
            'protect network access with firewalls, segmentation, VPN': ['vpn'],
            'HTTP, TFTP, SFTP and MMS file transfer': ['sftp'],
            'engineering access over SSH': ['ssh'],
            'Helps meet NERC CIP security requirements': [],
            'NERC CIP Security standards': [],
            'Supports CIP Security\u2122 on EtherNet/IP': ['cip_security'],
            'before you implement CIP\u2122 Security': ['cip_security'],
            'firmware is digitally signed': [],
        }
        for text, expected in table.items():
            with self.subTest(text=text): self.assertEqual(self.leads(text), expected)

    def test_dnp3_sa_lead_may_be_qualified_by_heading_or_neighbouring_block(self):
        bare = {'location':'html-block:2','text':'Secure Authentication is optional.'}
        for segs in ([dict(bare, heading='DNP3 settings')], [{'location':'html-block:1','text':'DNP3 outstation'}, bare]):
            hits = s.candidates({'id':'x','product_id':'p'}, segs)
            self.assertIn(('html-block:2','dnp3_secure_authentication'), [(h['location'],h['feature']) for h in hits])
        self.assertNotIn('dnp3_secure_authentication', self.leads(bare['text']))

    def test_lead_groups_do_not_change_review_cells(self):
        self.assertEqual(s.CAPABILITIES, ('dnp3_secure_authentication','tls','ipsec','cip_security','authentication','encryption','ssh'))
        self.assertLess(set(s.CAPABILITIES), set(s.PATTERNS))

    def test_candidate_carries_count_heading_and_model_mention(self):
        segs = [{'location':'html-block:3','text':'The B90 supports TLS; TLS 1.2 is the default.','heading':'Security'},
                {'location':'html-block:4','text':'The AB900 uses SSH.'}]
        tls, ssh = s.candidates({'id':'x','product_id':'p'}, segs, ['B90'])
        self.assertEqual((tls['match_count'], tls['heading'], tls['model_mentioned']), (2, 'Security', True))
        self.assertFalse(ssh['model_mentioned'])
        self.assertNotIn('model_mentioned', s.candidates({'id':'x','product_id':'p'}, segs)[0])

    def test_html_tables_headings_and_anchor_text(self):
        segs, links, facts = s.parse(b'<html><head><title>B90</title></head><body><h2>Chapter 5 <span>Security</span></h2>'
            b'<table><tr><td>Protocol</td><td>TLS</td><td>1.2</td></tr></table><p>See <a href="a b.pdf">the <b>instruction</b> manual</a>.</p>'
            b'<nav><a href="/cybersecurity">Security</a></nav><footer><a href="/psirt">PSIRT</a></footer>'
            b'<svg><title>Expand SSH</title></svg><select><option>Albania</option></select><noscript><p>Static contents</p></noscript>tail</body></html>',
            {'Content-Type':'text/html; charset=bogus-cs'})
        self.assertEqual([x['text'] for x in segs], ['B90','Chapter 5 Security','Protocol | TLS | 1.2','See the instruction manual.','Static contents','tail'])
        self.assertEqual(segs[2].get('heading'), 'Chapter 5 Security')
        self.assertNotIn('heading', segs[1])
        self.assertEqual(links, [('a b.pdf','the instruction manual')])
        self.assertEqual(facts, {'kind':'html','title':'B90','document_hints':[]})
        self.assertEqual([h['feature'] for h in s.candidates({'id':'x','product_id':'p'}, segs)], ['tls'])

    def test_pdf_pages_metadata_and_bookmarks(self):
        body = tiny_pdf(['Device overview', '', 'DNP3 Secure Authentication SAv5 is optional'], bookmark=('DNP3 settings', 2))
        segs, links, facts = s.parse(body, {'Content-Type':'application/pdf'})
        self.assertEqual([x['location'] for x in segs], ['pdf-page:1','pdf-page:2','pdf-page:3'])
        self.assertEqual((facts['kind'], facts['pages'], facts['empty_pages'], facts['encrypted'], facts['page_errors']), ('pdf', 3, 1, False, []))
        self.assertEqual((facts['title'], facts['pdf_created']), ('Test Relay Manual', 'D:20260102030405Z'))
        self.assertEqual(segs[2]['heading'], 'DNP3 settings')
        self.assertNotIn('heading', segs[0])
        hit = s.candidates({'id':'x','product_id':'p'}, segs)[0]
        self.assertEqual((hit['feature'], hit['location'], hit['heading']), ('dnp3_secure_authentication','pdf-page:3','DNP3 settings'))
        self.assertEqual(s.parse(b'\xef\xbb\xbf\n' + body, {})[2]['pages'], 3)

    def test_unreadable_pdf_page_does_not_hide_the_others(self):
        with patch('pypdf.PageObject.extract_text', side_effect=['TLS on page one', RuntimeError('bad font'), 'three']):
            segs, _, facts = s.parse(tiny_pdf(['a','b','c']), {})
        self.assertEqual([x['text'] for x in segs], ['TLS on page one','','three'])
        self.assertEqual(facts['page_errors'], [{'location':'pdf-page:2','error':'RuntimeError: bad font'}])

    def test_text_hash_ignores_markup_only_changes(self):
        a = s.parse(b'<script>var nonce="1"</script><div class="x1"><p>TLS is  supported.</p></div>', {'Content-Type':'text/html'})[0]
        b = s.parse(b'<script>var nonce="2"</script><div class="x2"><p>TLS is supported.</p></div><!-- t=9 -->', {'Content-Type':'text/html'})[0]
        c = s.parse(b'<p>TLS is not supported.</p>', {'Content-Type':'text/html'})[0]
        self.assertEqual(s.text_digest(a), s.text_digest(b))
        self.assertNotEqual(s.text_digest(a), s.text_digest(c))

    def test_canonical_encodes_and_normalises(self):
        for raw, want in {'https://vendor.test/docs/My Manual.pdf':'https://vendor.test/docs/My%20Manual.pdf',
                          ' https://vendor.test:443/a ':'https://vendor.test/a',
                          'https://vendor.test/a?x=1&y=a b':'https://vendor.test/a?x=1&y=a%20b',
                          'https://vendor.test/a%20b/$/c':'https://vendor.test/a%20b/$/c'}.items():
            self.assertEqual(s.canonical(raw), want)

    def test_pilot_seed_ids_are_unchanged(self):
        seeds = {(p['id'], u) for p in s.load(ROOT/'configs'/'pilot.json')['products'] for u in p['seeds']}
        recorded = {(x['product_id'], x['url']): x['id'] for x in s.load(ROOT/'pilot'/'sources.json')}
        self.assertEqual(seeds, set(recorded))
        for (pid, url), sid in recorded.items():
            self.assertEqual(s.digest((pid + s.canonical(url)).encode())[:20], sid)

    def test_utf8_lf_and_atomic_dump(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); text = 'R \u2265 10 \u03a9 \u2192 con\ufb01dentiality'
            s.dump(p/'x.json', [{'text':text}])
            self.assertEqual(s.load(p/'x.json'), [{'text':text}])
            self.assertIn(text.encode('utf-8'), (p/'x.json').read_bytes())
            self.assertNotIn(b'\r', (p/'x.json').read_bytes())
            self.assertEqual([x.name for x in p.iterdir()], ['x.json'])

    def test_robots_wildcards_and_longest_match(self):
        rules = (b'User-agent: *\nDisallow: /*.pdf$\nDisallow: /*/_theme/\nDisallow: /*jcr:content*\nDisallow: */ecommerce\n'
                 b'Disallow: /software/sites/default/files/*.pdf\nDisallow: /private/\nAllow: /private/public/\nCrawl-delay: 7\n')
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt':(200,{},rules)})
            with raw as calls:
                for path in ['/docs/a.pdf','/en/_theme/x.css','/a/jcr:content/b','/en-us/ecommerce','/software/sites/default/files/x/y.pdf','/private/a']:
                    with self.subTest(path=path), self.assertRaisesRegex(ValueError,'robots disallow'): f.robot('https://vendor.test'+path)
                for path in ['/docs/a.html','/docs/a.pdf?download=1','/private/public/a']:
                    with self.subTest(path=path): f.robot('https://vendor.test'+path)
                self.assertEqual(calls.call_count, 1)
            self.assertEqual((f.robots['vendor.test']['gap'], f.robots['vendor.test']['basis']), (7, '200'))

    def test_robots_group_named_for_this_crawler_wins(self):
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt':(200,{},b'User-agent: *\nDisallow:\n\nUser-agent: IEDSecuritySurvey\nDisallow: /\n')})
            with raw, self.assertRaisesRegex(ValueError,'robots disallow'): f.robot('https://vendor.test/a')

    def test_unresolved_robots_is_asked_once_per_host(self):
        for reply in [(503,{},b'unavailable'), TimeoutError('timed out')]:
            with tempfile.TemporaryDirectory() as td:
                f, raw = self.scripted(td, {'https://lit.vendor.test/robots.txt':reply})
                with raw as calls:
                    for path in '/a.pdf', '/b.pdf', '/c.pdf':
                        with self.assertRaisesRegex(ValueError,'robots unresolved'): f.robot('https://lit.vendor.test'+path)
                    self.assertEqual(calls.call_count, 1)

    def test_robots_redirect_is_opt_in_and_stays_inside_the_allowlist(self):
        replies = {'https://lit.vendor.test/robots.txt':(301,{'Location':'https://www.vendor.test/library'},b''),
                   'https://www.vendor.test/library':(302,{'Location':'/en-us.html'},b''),
                   'https://www.vendor.test/en-us.html':(200,{'Content-Type':'text/html'},b'<html><body>Literature</body></html>'),
                   'https://lit.vendor.test/a.pdf':(200,{'Content-Type':'text/html','Set-Cookie':'sid=1','ETag':'"e"'},b'<p>x</p>'),
                   'https://out.vendor.test/robots.txt':(301,{'Location':'https://evil.test/robots.txt'},b'')}
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, replies)
            with raw as calls, self.assertRaisesRegex(ValueError,'robots unresolved: HTTP 301'): f.robot('https://lit.vendor.test/a.pdf',['vendor.test'])
            self.assertEqual(calls.call_count, 1)
            f, raw = self.scripted(td, replies, {'robots_follow_redirects':True})
            with raw as calls:
                meta, _ = f.fetch('https://lit.vendor.test/a.pdf',['vendor.test'])
                self.assertEqual(meta['robots_basis'], 'redirected:https://www.vendor.test/en-us.html')
                self.assertEqual(meta['headers'], {'Content-Type':'text/html','ETag':'"e"'})
                self.assertEqual([x['url'] for x in f.audit], list(replies)[:4])
                self.assertIn('sha256', f.audit[2])
                with self.assertRaisesRegex(ValueError,'outside vendor allowlist'): f.robot('https://out.vendor.test/a',['vendor.test'])
                with self.assertRaisesRegex(ValueError,'outside vendor allowlist'): f.robot('https://out.vendor.test/b',['vendor.test'])
                self.assertEqual(calls.call_count, 5)
            f, raw = self.scripted(td, replies, {'robots_follow_redirects':True})
            with raw, self.assertRaisesRegex(ValueError,'outside vendor allowlist'): f.robot('https://lit.vendor.test/a.pdf')

    def test_failed_attempts_stay_in_the_request_log(self):
        with tempfile.TemporaryDirectory() as td:
            f = s.Fetcher({'delay_seconds':0,'max_bytes':4}, td)
            with patch.object(f.opener,'open',side_effect=TimeoutError('timed out')), self.assertRaises(TimeoutError): f.raw('https://vendor.test/a')
            with patch.object(f.opener,'open',return_value=Reply(b'too large')), self.assertRaises(ValueError): f.raw('https://vendor.test/b')
            self.assertEqual([x['url'] for x in f.audit], ['https://vendor.test/a','https://vendor.test/b'])
            self.assertIn('TimeoutError', f.audit[0]['error'])
            self.assertIn('byte limit', f.audit[1]['error'])
            self.assertEqual(f.audit[1]['status'], 200)

    def test_truncated_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            f = s.Fetcher({'delay_seconds':0}, td)
            with patch.object(f.opener,'open',return_value=Reply(b'short',headers={'Content-Length':'100'})):
                with self.assertRaisesRegex(ValueError,'shorter than its Content-Length'): f.raw('https://vendor.test/a')
            with patch.object(f.opener,'open',return_value=Reply(b'whole',headers={'content-length':'5'})):
                self.assertEqual(f.raw('https://vendor.test/a')[2], b'whole')

    def test_retries_are_opt_in_bounded_and_logged(self):
        script = lambda: [TimeoutError('timed out'), Reply(b'busy',503,{'Retry-After':'7'}), Reply(b'ok')]
        with tempfile.TemporaryDirectory() as td, patch.object(s.time,'sleep') as sleep:
            f = s.Fetcher({'delay_seconds':0}, td)
            with patch.object(f.opener,'open',side_effect=script()), self.assertRaises(TimeoutError): f.raw('https://vendor.test/a')
            self.assertEqual(len(f.audit), 1)
            f = s.Fetcher({'delay_seconds':0,'retries':2}, td)
            with patch.object(f.opener,'open',side_effect=script()): self.assertEqual(f.raw('https://vendor.test/a')[::2], (200, b'ok'))
            self.assertEqual([(x.get('status'), x.get('retried', False)) for x in f.audit], [(None,True),(503,True),(200,False)])
            self.assertIn(7, [c.args[0] for c in sleep.call_args_list])
            f = s.Fetcher({'delay_seconds':0,'retries':1}, td)
            with patch.object(f.opener,'open',side_effect=script()): self.assertEqual(f.raw('https://vendor.test/a')[0], 503)
            with patch.object(f.opener,'open',return_value=Reply(b'gone',404)): self.assertEqual(f.raw('https://vendor.test/a')[0], 404)
            self.assertEqual(len(f.audit), 3)

    def test_seeds_are_never_dropped_and_unfollowed_links_are_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            seeds = [f'https://vendor.test/{i}' for i in range(3)]
            pages = {u: f'<p>TLS {u}</p><a href="/manual.pdf">Manual</a><a href="/about">About</a>'.encode() for u in seeds}
            cfg = self.config(p, [{'id':'p','seeds':seeds}], max_depth=1, max_pages_per_product=2)
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            self.assertEqual(calls, seeds)
            recs = s.load(p/'run'/'sources.json')
            self.assertEqual([x['status'] for x in recs], ['extracted']*3+['skipped'])
            self.assertEqual((recs[3]['url'], recs[3]['via'], recs[3]['depth']), ('https://vendor.test/manual.pdf', recs[0]['id'], 1))
            self.assertEqual((recs[0]['links_found'], recs[0]['links_matched'], recs[0]['links_skipped']), (2, 1, 1))
            self.assertEqual(s.load(p/'run'/'manifest.json')['source_status'], {'extracted':3,'skipped':1})
            template = s.load(p/'run'/'review_template.json')
            self.assertEqual([x['feature'] for x in template], list(s.CAPABILITIES))
            s.verify(p/'run', p/'cache')

    def test_followed_links_are_ranked_and_matched_on_anchor_text(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            seed = 'https://vendor.test/b90'
            pages = {seed: b'<p>B90</p><a href="/api/download/1/">Brochure</a><a href="/x.pdf">Datasheet</a>'
                           b'<a href="/api/download/2/">B90 Instruction Manual</a><a href="https://evil.test/manual.pdf">Manual</a><a href="#top">manual top</a>',
                     'https://vendor.test/api/download/2/': b'<p>SSH</p>', 'https://vendor.test/x.pdf': b'<p>TLS</p>'}
            cfg = self.config(p, [{'id':'p','seeds':[seed],'aliases':['B90']}], max_depth=1, max_pages_per_product=3)
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            self.assertEqual(calls, [seed,'https://vendor.test/api/download/2/','https://vendor.test/x.pdf'])
            recs = s.load(p/'run'/'sources.json')
            self.assertEqual((recs[0]['links_found'], recs[0]['links_matched'], recs[0]['model_mentions']), (5, 2, 1))
            self.assertEqual(recs[1]['model_mentions'], 0)
            s.replay(p/'run', p/'cache', p/'replay')

    def test_identical_bytes_within_a_product_are_marked_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>TLS</p>', 'https://vendor.test/b': b'<p>TLS</p>'}
            cfg = self.config(p, [{'id':'p','seeds':list(pages)},{'id':'q','seeds':['https://vendor.test/a']}])
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            recs = s.load(p/'run'/'sources.json')
            self.assertEqual([x['status'] for x in recs], ['extracted','duplicate','extracted'])
            self.assertEqual(recs[1]['duplicate_of'], recs[0]['id'])
            self.assertEqual([h['product_id'] for h in s.load(p/'run'/'candidates.json')], ['p','q'])

    def test_config_is_validated_before_anything_is_written(self):
        base = {'sampling':'x','products':[{'id':'p','vendor':'v','model':'m','category':'c','domains':['vendor.test'],'seeds':['https://vendor.test/a']}]}
        self.assertEqual(s.validate_config(base), [])
        self.assertEqual(s.validate_config(s.load(ROOT/'configs'/'pilot.json')), [])
        for broken in [{**base,'sampling':''}, {**base,'products':[]}, {**base,'products':base['products']*2}, {**base,'follow_pattern':'('},
                       {**base,'products':[{**base['products'][0],'seeds':'https://vendor.test/a'}]}, {**base,'products':[{'id':'p','seeds':[]}]}]:
            with self.subTest(broken=broken), self.assertRaises(ValueError): s.validate_config(broken)
        loose = {**base,'max_depht':1,'products':[{'id':'p','domains':['vendor.test'],'seeds':['http://vendor.test/a','https://other.test/b']},
                                                  {'id':'q','vendor':'v','model':'m','category':'c','domains':[],'seeds':[]}]}
        warnings = s.validate_config(loose)
        for expected in ['unknown config key: max_depht','p: missing vendor','http://vendor.test/a','https://other.test/b','q: no seeds']:
            self.assertTrue(any(expected in w for w in warnings), expected)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); s.dump(p/'cfg.json', {**base,'sampling':''})
            with self.assertRaises(ValueError): s.crawl(p/'cfg.json', p/'run', p/'cache')
            self.assertFalse((p/'run').exists())

    def test_evidence_quote_must_be_in_the_cited_segment(self):
        segments = lambda sid: [{'location':'pdf-page:2','text':'Note:  TLS is supported\nfor DNP3 sessions on port 20000.'},
                                {'location':'pdf-page:3','text':'Unrelated page about HTTPS administration.'}]
        def check(evidence, **kw):
            source,row=self.fixture(); row['evidence']=evidence
            s.validate_reviews([row],[source],{'p'},segments,**kw)
        good = {'source_id':'s','location':'pdf-page:2','quote':'TLS is supported for DNP3 sessions'}
        check([good], require_evidence=True)
        check([])
        for bad in [dict(good,location='pdf-page:3'), dict(good,location='page 2'), dict(good,quote='TLS is always supported for DNP3 sessions'),
                    dict(good,quote='TLS is supported'), dict(good,source_id='other')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): check([bad])
        with self.assertRaisesRegex(ValueError,'verbatim evidence quote'): check([], require_evidence=True)
        broken = lambda sid: [{'location':'pdf-page:9','text':'By default, all RTACs have a self-\nsigned X.509 certificate enabled.'}]
        for spelling in ['self-signed', 'self- signed', 'selfsigned']:
            source,row=self.fixture(); row['evidence']=[{'source_id':'s','location':'pdf-page:9','quote':f'all RTACs have a {spelling} X.509 certificate'}]
            with self.subTest(spelling=spelling): s.validate_reviews([row],[source],{'p'},broken)
        source,row=self.fixture(); row.update(status='unknown', source_ids=[], source_hashes={})
        s.validate_reviews([row],[source],{'p'},segments,require_evidence=True)

    def test_report_builds_matrix_denominators_and_evidence_index(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/r': b'<h2>DNP3</h2><p>TLS is supported for DNP3 sessions when the option is licensed.</p>'}
            cfg = self.config(p, [{'id':'r1','seeds':['https://vendor.test/r','https://vendor.test/gone']},{'id':'m1','category':'meter','seeds':[]}], title='Synthetic survey')
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            source = s.load(p/'run'/'sources.json')[0]
            rows = s.load(p/'run'/'review_template.json')
            for row in rows: row.update(reviewer='A. Reviewer', reviewed_at='2026-10-13', rationale='not assessed')
            rows[1].update(status='conditional', source_ids=[source['id']], source_hashes={source['id']:source['sha256']}, location='html-block:2',
                           protocol='DNP3 over TLS', interface='SCADA', interface_class='control_protocol', firmware='unknown', implementation='licensed option',
                           conditions='needs the TLS licence', rationale='Explicit | licensed',
                           evidence=[{'source_id':source['id'],'location':'html-block:2','quote':'TLS is supported for DNP3 sessions'}])
            s.dump(p/'reviews.json', rows[:-1])
            s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['# Synthetic survey', 'Sources attempted: 2; extracted: 1; failed: 1.', 'A. Reviewer (13 rows)',
                             '| R1 | relay | ? | C | ? | ? | ? | ? | ? |', '| M1 | meter | ? | ? | ? | ? | ? | ? | - |',
                             '| relay | tls | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |', '| meter | ssh | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |',
                             '13 of 14 cells are unknown, conflicting or not reviewed on every interface.', '| R1 | https://vendor.test/gone | ValueError: HTTP 404 |',
                             'Review coverage: 13/14', 'Evidence quotes: 1 of 1 rows', 'Explicit / licensed',
                             '## Findings and evidence', '### R1: tls (conditional)', '- Interface: SCADA (control protocol)', '- Protocol: DNP3 over TLS',
                             '- Implementation: licensed option', '- Conditions: needs the TLS licence', '- Review status: draft (A. Reviewer)',
                             '- Evidence, html-block:2: "TLS is supported for DNP3 sessions"', '- Source: S1 [type not confirmed] https://vendor.test/r',
                             '| v | R1 | not recorded | unknown | SCADA (control protocol) | unknown; see tls (conditional) | unknown; see tls (conditional) | needs the TLS licence | S1 [type not confirmed] html-block:2: "TLS is supported for DNP3 sessions" | draft (A. Reviewer) |',
                             '| v | M1 | not recorded | not established | No control protocol established from the examined sources | unknown | unknown | - | none | draft (A. Reviewer) |',
                             f"| S1 | R1 | untitled | suggested: product page | not established | not established | 2026-10-13 | {source['sha256']} | https://vendor.test/r |"]:
                self.assertIn(expected, text)
            table = (p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual(table[0], 'Manufacturer,Model,Lifecycle,Category,Firmware,Protocol / interface,Interface class,Encryption,Authentication,Conditions,Evidence,Review status,Sources')
            self.assertEqual(len(table), 3)
            self.assertIn('sha256:' + source['sha256'], table[1])
            self.assertNotIn('%', text.replace('No population percentages', ''))
            index = s.load(p/'report'/'evidence_index.json')
            self.assertEqual([(x['product_id'],x['feature'],x['location'],x['sha256']) for x in index], [('r1','tls','html-block:2',source['sha256'])])
            none = {'total':0,'by_group':{}}
            self.assertEqual(s.load(p/'report'/'candidate_counts.json'), {'r1':{'capability':{'total':1,'by_group':{'tls':1}},'related':none,'statement':none,'profile':none},
                                                                          'm1':{'capability':none,'related':none,'statement':none,'profile':none}})
            rows[1]['evidence'][0]['quote'] = 'TLS is supported for all DNP3 sessions'
            s.dump(p/'reviews.json', rows)
            with self.assertRaisesRegex(ValueError,'evidence quote not found'): s.report(p/'run', p/'reviews.json', p/'report2')

    def test_untouched_template_rows_count_as_not_reviewed_but_partial_rows_fail(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.config(p, [{'id':'r1','seeds':['https://vendor.test/r']}])
            with self.site({'https://vendor.test/r': b'<p>TLS</p>'}, calls): s.crawl(cfg, p/'run', p/'cache')
            template = p/'run'/'review_template.json'
            s.report(p/'run', template, p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['Reviewers on record: none.', '| R1 | relay | - | - | - | - | - | - | - |', 'Review coverage: 0/7', '7 of 7 cells are unknown, conflicting or not reviewed on every interface.',
                             '| v | R1 | not recorded | not established | No control protocol established from the examined sources | not reviewed | not reviewed | - | none | not reviewed |']:
                self.assertIn(expected, text)
            self.assertEqual(s.load(p/'report'/'findings.json'), [])
            rows = s.load(template)
            rows[0].update(reviewer='A. Reviewer', reviewed_at='2026-10-13', rationale='Examined; not established.')
            rows[1]['rationale'] = 'started but unsigned'
            s.dump(p/'reviews.json', rows)
            with self.assertRaisesRegex(ValueError, r"identity/date/rationale required.*'r1', 'tls'"): s.report(p/'run', p/'reviews.json', p/'report')
            rows[1]['rationale'] = ''
            s.dump(p/'reviews.json', rows)
            s.report(p/'run', p/'reviews.json', p/'report')
            self.assertIn('| R1 | relay | ? | - | - | - | - | - | - |', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))

    def test_command_line_refusals_are_one_line_errors(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); s.dump(p/'bad.json', {'sampling':'','products':[]}); (p/'taken').mkdir()
            good = self.config(p, [{'id':'p','seeds':[]}])
            for argv, expected in [(['crawl','--config',str(p/'bad.json'),'--out',str(p/'run')], 'error: config needs a sampling statement'),
                                   (['crawl','--config',str(good),'--out',str(p/'taken'),'--cache',str(p/'cache')], 'error: already exists, refusing to overwrite'),
                                   (['verify','--run',str(p/'missing')], 'error: not found')]:
                with self.subTest(argv=argv[0]), patch.object(s.sys, 'argv', ['survey.py']+argv), self.assertRaises(SystemExit) as stop: s.main()
                self.assertIn(expected, str(stop.exception.code))

    # --- 1.2.0 ---

    def test_lead_records_matched_terms_and_type(self):
        hits = {h['feature']: h for h in s.candidates({'id':'x','product_id':'p'}, [{'location':'pdf-page:1',
            'text':'The relay supports TLS 1.2 and tls 1.2; SSL is disabled. File transfer uses SFTP. Use a VPN. Data is sent in clear text.'}])}
        self.assertEqual(hits['tls']['matched'], ['TLS 1.2', 'SSL'])
        self.assertEqual((hits['tls']['match_count'], hits['tls']['lead_type']), (3, 'capability'))
        self.assertEqual((hits['sftp']['matched'], hits['sftp']['lead_type']), (['SFTP'], 'related'))
        self.assertEqual((hits['vpn']['matched'], hits['vpn']['lead_type']), (['VPN'], 'related'))
        self.assertEqual(hits['plaintext_statement']['lead_type'], 'statement')
        self.assertNotIn('ssh', hits)
        self.assertNotIn('ipsec', hits)

    def test_lead_context_keeps_whole_sentences(self):
        filler = ' '.join(f'Sentence number {n} describes an unrelated setting of the device.' for n in range(40))
        text = filler + ' The outstation supports TLS for the DNP3 link. ' + filler
        hit = s.candidates({'id':'x','product_id':'p'}, [{'location':'pdf-page:1','text':text}])[0]
        self.assertIn('The outstation supports TLS for the DNP3 link.', hit['context'])
        self.assertTrue(hit['context'].startswith('Sentence number'))
        self.assertTrue(hit['context'].endswith('of the device.'))
        self.assertLess(len(hit['context']), 1200)
        self.assertNotIn('context_before', hit)
        unbroken = 'x' * 900 + ' TLS ' + 'y' * 900
        self.assertRegex(s.candidates({'id':'x','product_id':'p'}, [{'location':'pdf-page:1','text':unbroken}])[0]['context'], r'^\[\.\.\.\] .*TLS.* \[\.\.\.\]$')

    def test_html_lead_carries_its_neighbouring_blocks(self):
        segs = [{'location':f'html-block:{i+1}','text':t} for i, t in enumerate(
            ['Communications', 'Supported protocols', 'CIP Security', 'lets devices authenticate each other.', 'Requires firmware 33 or later.', 'Ordering'])]
        hit = next(h for h in s.candidates({'id':'x','product_id':'p'}, segs) if h['feature'] == 'cip_security')
        self.assertEqual((hit['location'], hit['context']), ('html-block:3', 'CIP Security'))
        self.assertEqual(hit['context_before'], ['Communications', 'Supported protocols'])
        self.assertEqual(hit['context_after'], ['lets devices authenticate each other.', 'Requires firmware 33 or later.'])

    def test_inline_styled_block_tags_do_not_split_a_sentence(self):
        body = (b'<h2 class="title"><div style="display: inline;">CIP Security</div></h2><div class="p"><div style="display:inline">'
                b'<span class="ph"><div style="display: inline;">CIP Security<span class="tm">&trade;</span></div></span> lets '
                b'<div style="DISPLAY: inline-block">CIP</div>-connected devices authenticate each other.</div></div><div>Next block<p>unclosed<div>inner</div></div>tail')
        segs = s.parse(body, {'Content-Type':'text/html'})[0]
        self.assertEqual([x['text'] for x in segs], ['CIP Security', 'CIP Security\u2122 lets CIP-connected devices authenticate each other.', 'Next block', 'unclosed', 'inner', 'tail'])
        self.assertEqual(segs[1]['heading'], 'CIP Security')
        self.assertEqual([h['feature'] for h in s.candidates({'id':'x','product_id':'p'}, segs)], ['cip_security', 'cip_security', 'authentication'])

    def test_document_hints_are_short_snippets_around_revision_and_date_markers(self):
        pdf = [{'location':f'pdf-page:{n}','text':f'{n} Body text. SEL White Paper LWP0018-01 Date Code 20160111'} for n in (1, 2)]
        self.assertEqual(s.hints(pdf), ['1 Body text. SEL White Paper LWP0018-01 Date Code 20160111'])
        html = [{'location':'html-block:1','text':'Publication Date: |'}, {'location':'html-block:2','text':'2024-07-09'},
                {'location':'html-block:3','text':'Current Version: | V1.2'}, {'location':'html-block:4','text':'\u00a9 Siemens 2025'},
                {'location':'html-block:5','text':'protected under applicable copyright laws'}]
        self.assertEqual(s.hints(html), ['Publication Date: | 2024-07-09', 'Current Version: | V1.2', '\u00a9 Siemens 2025'])
        self.assertEqual(s.parse(b'<p>Revision B, 2020</p>', {'Content-Type':'text/html'})[2]['document_hints'], ['Revision B, 2020'])

    def test_statement_leads_live_in_their_own_file(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>DNP3 data is sent in clear text.</p><p>TLS is optional. Use a VPN.</p>'}
            cfg = self.config(p, [{'id':'p','seeds':list(pages)}])
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            self.assertEqual([h['feature'] for h in s.load(p/'run'/'candidates.json')], ['tls','vpn'])
            self.assertEqual([h['feature'] for h in s.load(p/'run'/'statement_leads.json')], ['plaintext_statement'])
            manifest = s.load(p/'run'/'manifest.json')
            self.assertEqual((manifest['candidate_count'], manifest['lead_counts']), (2, {'statement':1,'capability':1,'related':1}))
            s.replay(p/'run', p/'cache', p/'replay')
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            self.assertEqual(s.load(p/'report'/'candidate_counts.json')['p'], {'capability':{'total':1,'by_group':{'tls':1}},
                'related':{'total':1,'by_group':{'vpn':1}}, 'statement':{'total':1,'by_group':{'plaintext_statement':1}}, 'profile':{'total':0,'by_group':{}}})
            notes = s.load(p/'run'/'source_notes_template.json')
            self.assertEqual([(n['url'], n['doc_type'], n['doc_type_suggested'], n['document_id'], n['revision'], n['document_date']) for n in notes],
                             [('https://vendor.test/a','','product_page','','','')])
            self.assertEqual(s.load(p/'run'/'review_template.json')[0]['interface_class'], '')

    def test_a_capability_is_recorded_once_per_interface(self):
        def check(*changes):
            source, row = self.fixture()
            rows = [dict(row, **c) for c in changes]
            s.validate_reviews(rows, [source], {'p'})
        dnp = {'interface':'DNP3 server', 'interface_class':'control_protocol'}
        web = {'interface':'Web interface', 'interface_class':'management'}
        check(dnp, web)
        check(dict(dnp, status='conditional', conditions='needs option board', review_status='confirmed'))
        check({'status':'unknown','interface':'','interface_class':'','source_ids':[],'source_hashes':{}}, dnp)
        for bad in [(dnp, dict(dnp, interface=' dnp3  SERVER ')), ({'interface_class':''},), ({'interface_class':'scada'},),
                    (dnp, dict(dnp, feature='ssh', interface_class='management')), (dict(dnp, status='conditional'),),
                    (dict(dnp, review_status='verified'),)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): check(*bad)

    def test_evidence_may_cite_a_short_range_of_segments(self):
        blocks = [{'location':f'html-block:{i+1}','text':t} for i, t in enumerate(['CIP Security', 'lets devices', 'authenticate each other.', 'Other'])]
        def check(location, quote='CIP Security lets devices authenticate each other.'):
            source, row = self.fixture(); row['evidence'] = [{'source_id':'s','location':location,'quote':quote}]
            s.validate_reviews([row],[source],{'p'},lambda sid: blocks)
        check('html-block:1-3')
        check('html-block:2-3', 'lets devices authenticate each other.')
        for bad in ['html-block:1-2', 'html-block:3-1', 'html-block:1-12', 'html-block:3-9', 'block 1 to 3']:
            with self.subTest(bad=bad), self.assertRaises(ValueError): check(bad)

    def reviewed_run(self, p):
        """One relay with TLS for DNP3 and a login for its web page, one relay with only a web login, one unreviewed meter."""
        pages = {'https://vendor.test/a': b'<p>TLS is supported for DNP3 sessions.</p><p>The web interface requires a user login with a password.</p>',
                 'https://vendor.test/b': b'<p>The web interface requires a user login with a password.</p>'}
        cfg = self.config(p, [{'id':'a','seeds':['https://vendor.test/a']},{'id':'b','seeds':['https://vendor.test/b']},{'id':'m','category':'meter','seeds':[]}])
        with self.site(pages, []): s.crawl(cfg, p/'run', p/'cache')
        src = {x['product_id']: x for x in s.load(p/'run'/'sources.json')}
        def row(pid, feature, status, interface='', kind='', quote='', **more):
            base = {'product_id':pid,'feature':feature,'status':status,'source_ids':[src[pid]['id']],'source_hashes':{src[pid]['id']:src[pid]['sha256']},
                    'location':'html-block:1','protocol':f'{feature} detail','interface':interface,'interface_class':kind,'firmware':'v2 or later',
                    'implementation':'native','conditions':'','evidence':[{'source_id':src[pid]['id'],'location':more.pop('at','html-block:1'),'quote':quote}] if quote else [],
                    'rationale':'explicit','reviewer':'A. Reviewer','reviewed_at':'2026-10-13','review_status':'draft'}
            return dict(base, **more)
        login = 'The web interface requires a user login'
        rows = [row('a','tls','supported','DNP3 server','control_protocol','TLS is supported for DNP3 sessions.'),
                row('a','encryption','supported','DNP3 server','control_protocol','TLS is supported for DNP3 sessions.', review_status='confirmed', reviewer='P. Author'),
                row('a','authentication','conditional','Web interface','management',login, at='html-block:2', conditions='password must be set'),
                row('a','authentication','unknown'), row('a','ssh','unknown'),
                row('b','authentication','supported','Web interface','management',login),
                row('b','encryption','unknown'), row('b','tls','unknown')]
        s.dump(p/'reviews.json', rows)
        return src

    def test_findings_table_keeps_control_traffic_apart_from_management(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertLess(text.index('## Findings by product and interface'), text.index('## Capability matrix'))
            for expected in [
                '| v | A | not recorded | v2 or later | DNP3 server (control protocol) | supported: encryption detail | unknown; see tls (supported) | none stated | S1 [type not confirmed] html-block:1: "TLS is supported for DNP3 sessions." (+1 more) | draft (A. Reviewer); confirmed (P. Author) |',
                '| v | A | not recorded | v2 or later | Web interface (management) | not reviewed | conditional: authentication detail | password must be set | S1 [type not confirmed] html-block:2: "The web interface requires a user login" | draft (A. Reviewer) |',
                '| v | B | not recorded | not established | No control protocol established from the examined sources | unknown | not reviewed | - | none | draft (A. Reviewer) |',
                '| v | B | not recorded | v2 or later | Web interface (management) | unknown | supported: authentication detail | none stated | S2 [type not confirmed] html-block:1: "The web interface requires a user login" | draft (A. Reviewer) |',
                '| v | M | not recorded | not established | No control protocol established from the examined sources | not reviewed | not reviewed | - | none | not reviewed |',
                '| A | relay | - | S | - | - | (C) | S | ? |', '| B | relay | - | ? | - | - | (S) | ? | - |', '| M | meter | - | - | - | - | - | - | - |',
                '| relay | tls | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 |', '| relay | authentication | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 |',
                '| relay | encryption | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 |', '| meter | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |',
                'A. Reviewer (7 rows); P. Author (1 rows)', 'Review coverage: 7/21', '| A | authentication | Web interface | conditional | explicit |']:
                self.assertIn(expected, text)
            self.assertEqual(text.count('| v | A |'), 2)
            self.assertEqual(len((p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()), 6)
            self.assertEqual({(x['interface'], x['interface_class'], x['source_ref']) for x in s.load(p/'report'/'evidence_index.json')},
                             {('DNP3 server','control_protocol','S1'), ('Web interface','management','S1'), ('Web interface','management','S2')})

    def test_source_notes_complete_the_source_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); src = self.reviewed_run(p)
            notes = s.load(p/'run'/'source_notes_template.json')
            notes[0].update(doc_type='manual', document_id='LWP0018-01', revision='', document_date='2016-01-11', note='date code 20160111')
            s.dump(p/'notes.json', notes[:1])
            s.report(p/'run', p/'reviews.json', p/'report', source_notes=p/'notes.json')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn(f"| S1 | A | untitled | manual | LWP0018-01 | 2016-01-11 | 2026-10-13 | {src['a']['sha256']} | https://vendor.test/a |", text)
            self.assertIn(f"| S2 | B | untitled | suggested: product page | not established | not established | 2026-10-13 | {src['b']['sha256']} | https://vendor.test/b |", text)
            exported = s.load(p/'report'/'sources.json')
            self.assertEqual((exported[0]['ref'], exported[0]['document']['document_id'], exported[1]['document']['document_id']), ('S1','LWP0018-01',''))
            self.assertIn('S1 [manual] html-block:1: "TLS is supported for DNP3 sessions."', text)
            self.assertIn('S2 [type not confirmed] html-block:1:', text)
            self.assertIn('- Source: S1 [manual] https://vendor.test/a', text)
            self.assertEqual({x['doc_type'] for x in s.load(p/'report'/'evidence_index.json') if x['source_ref'] == 'S1'}, {'manual'})
            s.dump(p/'notes.json', [dict(notes[0], source_id='nope')])
            with self.assertRaisesRegex(ValueError,'not in this run'): s.report(p/'run', p/'reviews.json', p/'report', source_notes=p/'notes.json')
            s.dump(p/'notes.json', [dict(notes[0], doc_type='white paper')])
            with self.assertRaisesRegex(ValueError,'doc_type outside'): s.report(p/'run', p/'reviews.json', p/'report', source_notes=p/'notes.json')

    def test_rebuild_rederives_leads_offline_and_keeps_source_identity(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            before = s.load(p/'run'/'sources.json')
            manifest = s.load(p/'run'/'manifest.json'); manifest['tool_version'] = '1.1.0'; s.dump(p/'run'/'manifest.json', manifest)
            s.dump(p/'run'/'candidates.json', [])
            with patch.object(s.Fetcher, 'fetch', side_effect=AssertionError('network must not be used')):
                s.rebuild(p/'run', p/'cache', p/'rebuilt')
            after = s.load(p/'rebuilt'/'sources.json')
            self.assertEqual([(x['id'], x['sha256'], x.get('retrieved_at')) for x in after], [(x['id'], x['sha256'], x.get('retrieved_at')) for x in before])
            made = s.load(p/'rebuilt'/'manifest.json')
            self.assertEqual((made['tool_version'], made['rebuilt_from']['tool_version'], made['complete']), (s.VERSION, '1.1.0', True))
            self.assertEqual([(h['product_id'], h['feature'], h['matched']) for h in s.load(p/'rebuilt'/'candidates.json')], [('a','tls',['TLS'])])
            s.replay(p/'rebuilt', p/'cache', p/'replay')
            s.report(p/'rebuilt', p/'reviews.json', p/'report', require_evidence=True)
            self.assertEqual(s.load(p/'run'/'candidates.json'), [])
            with self.assertRaises(FileExistsError): s.rebuild(p/'run', p/'cache', p/'rebuilt')

    # --- 1.3.0 ---

    PROFILE = [['DNP3 SPECIFICATION', 'DEVICE PROFILE', 'Vendor relay X1'],
               ['1.12 SECURITY PARAMETERS ............ 3', '1.12.1 DNP3 device support for secure authentication: .... 3'],
               ['Device Profile Page 3', '1.12 SECURITY PARAMETERS Capabilities Current Value', '1.12.1 DNP3 device support for secure',
                'authentication:', 'If the device does not support secure authentication', 'then ignore the rest of this section.',
                'Supported versions:', 'X  Fixed at Version 5', ' Configurable, selectable from __', '1.12.2 Maximum number of users:', 'X  Fixed at 1'],
               ['Device Profile Page 4', '1.12 SECURITY PARAMETERS Capabilities Current Value', ' Configurable, range __ to __',
                '1.12.12 Change cipher request timeout:', 'Implementations using TLS shall terminate the connection.',
                'X  Not relevant - TLS is not used', ' Fixed at ____']]

    def test_device_profile_section_is_split_into_items_with_marked_options(self):
        segs = s.parse(tiny_pdf(self.PROFILE), {})[0]
        items = s.profile_items(segs)
        self.assertEqual([(i['item'], i['title'], i['location'], i['marked']) for i in items], [
            ('1.12.1', 'DNP3 device support for secure authentication', 'pdf-page:3', ['Fixed at Version 5']),
            ('1.12.2', 'Maximum number of users', 'pdf-page:3', ['Fixed at 1']),
            ('1.12.12', 'Change cipher request timeout', 'pdf-page:4', ['Not relevant - TLS is not used'])])
        self.assertIn('Configurable, selectable from __', items[0]['text'])
        self.assertIn('Configurable, range __ to __', items[1]['text'])
        self.assertEqual({i['marks'] for i in items}, {'heuristic'})
        manual = tiny_pdf(['Relay manual', ['1.12 SECURITY PARAMETERS Capabilities', '1.12.1 DNP3 device support for secure authentication:', 'X  Fixed at Version 5']])
        self.assertEqual(s.profile_items(s.parse(manual, {})[0]), [])
        self.assertEqual(s.profile_items([{'location':'html-block:1','text':'DNP3 Device Profile'},{'location':'html-block:2','text':'no section here'}]), [])

    def test_device_profile_items_become_leads_and_a_report_section(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/profile.pdf': tiny_pdf(self.PROFILE), 'https://vendor.test/page': b'<p>TLS</p>'}
            cfg = self.config(p, [{'id':'x1','seeds':['https://vendor.test/profile.pdf']},{'id':'x2','seeds':['https://vendor.test/page']}])
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            source, other = s.load(p/'run'/'sources.json')
            self.assertEqual((source['profile_items'], source['doc_type_suggested'], other['doc_type_suggested']), (3, 'device_profile', 'product_page'))
            self.assertNotIn('profile_items', other)
            self.assertEqual(len(s.load(p/'run'/(source['id']+'.profile.json'))), 3)
            self.assertFalse((p/'run'/(other['id']+'.profile.json')).exists())
            leads = [h for h in s.load(p/'run'/'candidates.json') if h['lead_type'] == 'profile']
            self.assertEqual([(h['profile_item'], h['feature'], h['matched'], h['location']) for h in leads], [
                ('1.12.1', 'dnp3_secure_authentication', ['Fixed at Version 5'], 'pdf-page:3'),
                ('1.12.2', 'dnp3_secure_authentication', ['Fixed at 1'], 'pdf-page:3'),
                ('1.12.12', 'tls', ['Not relevant - TLS is not used'], 'pdf-page:4')])
            self.assertEqual(len({h['id'] for h in leads}), 3)
            statements = s.load(p/'run'/'statement_leads.json')
            self.assertEqual([(h['feature'], h['location'], h['matched']) for h in statements], [('non_support_statement', 'pdf-page:4', ['TLS is not used'])])
            self.assertEqual(s.load(p/'run'/'manifest.json')['lead_counts']['profile'], 3)
            s.replay(p/'run', p/'cache', p/'replay')
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['## Device profile statements', 'nothing in this table has been reviewed',
                             '| X1 | S1 | 1.12.1 | DNP3 device support for secure authentication | Fixed at Version 5 | pdf-page:3 |',
                             '| X1 | S1 | 1.12.12 | Change cipher request timeout | Not relevant - TLS is not used | pdf-page:4 |',
                             '| suggested: device profile |', '| suggested: product page |']:
                self.assertIn(expected, text)
            self.assertEqual(s.load(p/'report'/'candidate_counts.json')['x1']['profile'], {'total':3,'by_group':{'dnp3_secure_authentication':2,'tls':1}})
            s.rebuild(p/'run', p/'cache', p/'rebuilt')
            self.assertEqual(len(s.load(p/'rebuilt'/(source['id']+'.profile.json'))), 3)

    def test_document_type_is_suggested_from_title_url_and_opening_text(self):
        html, pdf = 'html-block:1', 'pdf-page:1'
        for title, url, where, opening, expected in [
                ('DNP3 Specification', 'https://v.test/f.pdf', pdf, 'Unrestricted DNP3 SPECIFICATION DEVICE PROFILE Version 2016', 'device_profile'),
                ('SSA-750499', 'https://v.test/ssa-750499.html', html, 'Siemens Security Advisory by Siemens ProductCERT', 'advisory'),
                ('Security Conformance Statement', 'https://v.test/c.pdf', pdf, 'SIPROTEC 5', 'conformance_statement'),
                ('SEL APPLICATION GUIDE', 'https://v.test/download/1/', pdf, 'WHITE PAPER Leveraging Security', 'security_guide'),
                ('DNP3 Security - PKR39809_ADVC_Operations manual', 'https://v.test/m', html, 'Contents', 'manual'),
                ('Secure Controller Systems', 'https://v.test/en-us/docs/technical/1756-um543/x.html', html, 'ControlLogix 5580', 'manual'),
                ('B90 brochure', 'https://v.test/b.pdf', pdf, 'Bus protection', 'datasheet'),
                ('Multilin B90 | GE Vernova', 'https://v.test/multilin-b90', html, 'Bus Protection System', 'product_page'),
                ('', 'https://v.test/x.pdf', pdf, 'Quarterly results', '')]:
            with self.subTest(title=title):
                self.assertEqual(s.suggest_doc_type(title, url, [{'location':where,'text':opening}]), expected)
        self.assertIn('device_profile', s.DOC_TYPES)

    # --- 1.4.0 ---

    def test_legacy_devices_are_captured_by_what_a_complete_manual_does_not_say(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/old': b'<p>The relay supports DNP3 and Modbus over serial links.</p><p>Passwords protect front panel access.</p>',
                     'https://vendor.test/new': b'<p>TLS is supported for DNP3 sessions.</p>'}
            cfg = self.config(p, [{'id':'old','lifecycle':'legacy','seeds':['https://vendor.test/old']},
                                  {'id':'new','lifecycle':'active','seeds':['https://vendor.test/new']}, {'id':'unk','seeds':[]}])
            with self.site(pages, []): s.crawl(cfg, p/'run', p/'cache')
            src = {x['product_id']: x for x in s.load(p/'run'/'sources.json')}
            def row(pid, feature, status, **more):
                base = {'product_id':pid,'feature':feature,'status':status,'source_ids':[src[pid]['id']],'source_hashes':{src[pid]['id']:src[pid]['sha256']},
                        'location':'','protocol':'','interface':'DNP3 serial and Ethernet','interface_class':'control_protocol','firmware':'all versions covered by manual rev C',
                        'implementation':'','conditions':'','evidence':[],'rationale':'searched in full','reviewer':'A. Reviewer','reviewed_at':'2026-10-13','review_status':'draft'}
                return dict(base, **more)
            silent = [row('old','encryption','not_documented'), row('old','tls','not_documented')]
            claim = row('new','tls','supported', location='html-block:1', protocol='DNP3 over TLS', implementation='native',
                        evidence=[{'source_id':src['new']['id'],'location':'html-block:1','quote':'TLS is supported for DNP3 sessions.'}])
            note = lambda pid, kind, coverage: {'source_id':src[pid]['id'],'doc_type':kind,'coverage':coverage}
            def run(rows, notes):
                s.dump(p/'reviews.json', rows); s.dump(p/'notes.json', notes)
                s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True, source_notes=p/'notes.json')
            for notes in ([], [note('old','product_page','complete')], [note('old','manual','partial')], [note('old','manual','')]):
                with self.subTest(notes=notes), self.assertRaisesRegex(ValueError,'not_documented needs a complete'): run(silent, notes)
            with self.assertRaisesRegex(ValueError,'1 leads for tls exist'): run([row('new','tls','not_documented')], [note('new','manual','complete')])
            with self.assertRaisesRegex(ValueError,'coverage must be'): run(silent, [note('old','manual','whole')])
            run(silent + [claim], [note('old','manual','complete')])
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in [
                'Lifecycle (active, legacy or discontinued) is recorded for 2 of 3 products.',
                '| v | OLD | legacy | all versions covered by manual rev C | DNP3 serial and Ethernet (control protocol) | '
                'not documented: the complete documentation searched does not mention it | not assessed; see tls (not documented) | none stated | '
                'S1 [manual] searched in full: no lead for encryption; S1 [manual] searched in full: no lead for tls | draft (A. Reviewer) |',
                '| v | NEW | active | all versions covered by manual rev C | DNP3 serial and Ethernet (control protocol) | not assessed; see tls (supported) |',
                '| v | UNK | not recorded | not established | No control protocol established from the examined sources |',
                '| OLD | relay, legacy | - | N | - | - | - | N | - |', '| NEW | relay, active | - | S | - | - | - | - | - |',
                '| relay, legacy | tls | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |', '| relay, active | tls | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |',
                '| relay, not recorded | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |', '| relay, legacy | encryption | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |',
                '### OLD: tls (not documented)', '- Searched: S1 [manual] searched in full: no lead for tls', '| manual, complete |',
                'Evidence quotes: 1 of 1 rows', 'Not documented: 2 rows', 'N not documented in a complete document',
                '18 of 21 cells are unknown, conflicting or not reviewed on every interface.']:
                self.assertIn(expected, text)
            table = (p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()
            self.assertIn('legacy', table[1].split(',')[2])
            self.assertIn('searched in full: no lead for tls', table[1])

    def test_not_documented_and_lifecycle_are_validated(self):
        source, row = self.fixture()
        silent = dict(row, status='not_documented', location='', protocol='', implementation='', interface='DNP3', interface_class='control_protocol')
        s.validate_reviews([silent], [source], {'p'}, require_evidence=True)
        for change in [{'interface_class':''}, {'firmware':''}, {'interface':''}, {'source_ids':[]}]:
            with self.subTest(change=change), self.assertRaises(ValueError): s.validate_reviews([dict(silent, **change)], [source], {'p'})
        base = {'sampling':'x','products':[{'id':'p','vendor':'v','model':'m','category':'c','lifecycle':'legacy','domains':['vendor.test'],'seeds':[]}]}
        self.assertEqual(s.validate_config(base), ['p: no seeds, so every cell stays unknown'])
        base['products'][0]['lifecycle'] = 'old'
        with self.assertRaisesRegex(ValueError,'lifecycle must be one of'): s.validate_config(base)
        self.assertIn('not_documented', s.STATUSES)

    def test_resume_continues_an_interrupted_run_without_refetching(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>TLS</p><a href="/manual.pdf">Manual</a>', 'https://vendor.test/manual.pdf': KeyboardInterrupt(),
                     'https://vendor.test/b': b'<p>SSH</p>'}
            cfg = self.config(p, [{'id':'p','seeds':['https://vendor.test/a']},{'id':'q','seeds':['https://vendor.test/b']}], max_depth=1)
            with self.site(pages, calls), self.assertRaises(KeyboardInterrupt): s.crawl(cfg, p/'run', p/'cache')
            self.assertFalse((p/'run'/'manifest.json').exists())
            self.assertEqual(len(s.load(p/'run'/'sources.json')), 1)
            pages['https://vendor.test/manual.pdf'] = b'<p>IPsec</p>'
            del calls[:]
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache', resume=True)
            self.assertEqual(calls, ['https://vendor.test/manual.pdf','https://vendor.test/b'])
            self.assertEqual([x['url'][-1] for x in s.load(p/'run'/'sources.json')], ['a','f','b'])
            self.assertEqual([h['feature'] for h in s.load(p/'run'/'candidates.json')], ['tls','ipsec','ssh'])
            self.assertTrue(s.load(p/'run'/'manifest.json')['complete'])
            s.replay(p/'run', p/'cache', p/'replay')
            with self.assertRaisesRegex(ValueError,'already complete'): s.crawl(cfg, p/'run', p/'cache', resume=True)
            (p/'run'/'manifest.json').unlink()
            other = self.config(p, [{'id':'p','seeds':['https://vendor.test/a']}])
            with self.assertRaisesRegex(ValueError,'config the run was started with'): s.crawl(other, p/'run', p/'cache', resume=True)

    def test_replay_refuses_a_run_from_another_tool_version(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.config(p, [{'id':'p','seeds':['https://vendor.test/a']}])
            with self.site({'https://vendor.test/a': b'<p>TLS</p>'}, calls): s.crawl(cfg, p/'run', p/'cache')
            manifest = s.load(p/'run'/'manifest.json')
            self.assertEqual(manifest['extraction_version'], s.EXTRACTION)
            s.dump(p/'run'/'manifest.json', dict(manifest, tool_version='9.9.9'))
            s.replay(p/'run', p/'cache', p/'replay_same_rules')
            s.dump(p/'run'/'manifest.json', dict(manifest, extraction_version='1.0.0'))
            with self.assertRaisesRegex(ValueError,'extraction rules 1.0.0'): s.replay(p/'run', p/'cache', p/'replay')
            older = {k: v for k, v in manifest.items() if k != 'extraction_version'}
            s.dump(p/'run'/'manifest.json', dict(older, tool_version='1.2.0'))
            with self.assertRaisesRegex(ValueError,'extraction rules 1.2.0'): s.replay(p/'run', p/'cache', p/'replay')
            self.assertFalse((p/'replay').exists())

    def test_recheck_locates_old_excerpts_in_a_fresh_run(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>intro</p><p>TLS is not  supported for DNP3.</p>', 'https://vendor.test/b': b'<p>SSH</p>'}
            cfg = self.config(p, [{'id':'p','seeds':list(pages)+['https://vendor.test/gone']}])
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            (p/'old').mkdir()
            s.dump(p/'old'/'sources.json', [
                {'id':'o1','product_id':'p','url':'https://vendor.test/a','status':'extracted','sha256':'0'*64},
                {'id':'o2','product_id':'p','url':'https://vendor.test/b','status':'extracted','sha256':s.digest(pages['https://vendor.test/b'])},
                {'id':'o3','product_id':'p','url':'https://vendor.test/gone','status':'failed','error':'ValueError: HTTP 404'},
                {'id':'o4','product_id':'p','url':'https://vendor.test/dropped','status':'extracted','sha256':'1'*64}])
            s.dump(p/'old'/'evidence_index.json', [
                {'source_id':'o1','location':'html-block:9','excerpt':'TLS is not supported for DNP3.'},
                {'source_id':'o2','location':'html-block:1','excerpt':'This sentence is no longer there.'}])
            a, b, gone, dropped = s.recheck(p/'old', p/'run', p/'recheck.json')
            self.assertEqual((a['raw_bytes'], a['extracted_text']), ('different','no text hash in old run'))
            self.assertEqual((a['excerpts'][0]['found_at'], a['excerpts'][0]['same_location']), (['html-block:2'], False))
            self.assertEqual((b['raw_bytes'], b['excerpts'][0]['found_at']), ('same', []))
            self.assertEqual((gone['old_status'], gone['new_status'], dropped['new_status']), ('failed','failed','not in new run'))
            self.assertEqual(len(s.load(p/'recheck.json')['sources']), 4)
            with self.assertRaises(FileExistsError): s.recheck(p/'old', p/'run', p/'recheck.json')
            self.assertEqual(s.recheck(p/'run', p/'run')[0]['extracted_text'], 'same')

    def test_sitemap_lists_and_filters_without_touching_any_config(self):
        index = 'https://vendor.test/sitemap_index.xml'
        pages = {index: b'<sitemapindex><sitemap><loc>https://vendor.test/s1.xml</loc></sitemap><sitemap><loc> https://vendor.test/s2.xml.gz </loc></sitemap><sitemap><loc>https://vendor.test/s3.xml</loc></sitemap></sitemapindex>',
                 'https://vendor.test/s1.xml': b'<urlset><url><loc>https://vendor.test/relays/r1</loc></url><url><loc>https://vendor.test/news/a&amp;b</loc></url></urlset>',
                 'https://vendor.test/s2.xml.gz': gzip.compress(b'<urlset><url><loc><![CDATA[https://vendor.test/relays/r2]]></loc></url></urlset>')}
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            with self.site(pages, calls):
                s.sitemap([index], None, [], 'relays', p/'inventory'/'vendor.json', p/'cache')
                result = s.load(p/'inventory'/'vendor.json')
                self.assertEqual(result['urls'], ['https://vendor.test/relays/r1','https://vendor.test/relays/r2'])
                self.assertEqual((result['total_urls'], result['matched_urls'], result['domains'], result['not_fetched']), (3, 2, ['vendor.test'], []))
                self.assertEqual([(x.get('kind'), x.get('entries')) for x in result['files']], [('index',3),('urlset',2),('urlset',1),(None,None)])
                self.assertIn('HTTP 404', result['files'][3]['error'])
                with self.assertRaises(FileExistsError): s.sitemap([index], None, [], '.', p/'inventory'/'vendor.json', p/'cache')
                s.sitemap([index], None, [], '.', p/'limited.json', p/'cache', limit=2)
                self.assertEqual(s.load(p/'limited.json')['not_fetched'], ['https://vendor.test/s2.xml.gz','https://vendor.test/s3.xml'])
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt':(200,{},b'Sitemap: https://vendor.test/sitemap_index.xml\n')})
            with raw: f.robot('https://vendor.test/')
            self.assertEqual(f.robots['vendor.test']['sitemaps'], [index])


if __name__=='__main__': unittest.main()

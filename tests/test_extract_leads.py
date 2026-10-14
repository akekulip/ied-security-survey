"""Extraction and leads: located text from HTML and PDF, and where the terms occur in it."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import survey as s
from support import SurveyCase, tiny_pdf


class ExtractLeadTests(SurveyCase):
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
        self.assertEqual(s.CAPABILITIES, ('dnp3_secure_authentication','tls','ipsec','cip_security','authentication','encryption','ssh','integrity'))
        self.assertLess(set(s.CAPABILITIES), set(s.PATTERNS))
        # The three properties asked about for every interface are review cells; the statement groups never are.
        self.assertEqual(s.PROPERTIES, ('authentication','integrity','encryption'))
        self.assertLess(set(s.PROPERTIES), set(s.CAPABILITIES))
        self.assertFalse(set(s.STATEMENTS) & set(s.CAPABILITIES))

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
            self.assertEqual([(h['feature'], h['matched']) for h in s.load(p/'run'/'statement_leads.json')],
                             [('plaintext_statement', ['clear text']), ('requirement_statement', ['TLS is optional'])])
            manifest = s.load(p/'run'/'manifest.json')
            self.assertEqual((manifest['candidate_count'], manifest['lead_counts']), (2, {'statement':2,'capability':1,'related':1}))
            s.replay(p/'run', p/'cache', p/'replay')
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            self.assertEqual(s.load(p/'report'/'candidate_counts.json')['p'], {'capability':{'total':1,'by_group':{'tls':1}},
                'related':{'total':1,'by_group':{'vpn':1}}, 'statement':{'total':2,'by_group':{'plaintext_statement':1,'requirement_statement':1}},
                'profile':{'total':0,'by_group':{}}})
            notes = s.load(p/'run'/'source_notes_template.json')
            self.assertEqual([(n['url'], n['doc_type'], n['doc_type_suggested'], n['document_id'], n['revision'], n['document_date']) for n in notes],
                             [('https://vendor.test/a','','product_page','','','')])
            self.assertEqual(s.load(p/'run'/'review_template.json')[0]['interface_class'], '')

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

    def test_integrity_default_and_requirement_wording_are_leads(self):
        table = {
            'Message integrity is protected by an HMAC': ['integrity'],
            'Secure Authentication provides authentication and integrity of DNP3 messages': ['dnp3_secure_authentication', 'authentication', 'integrity'],
            'The master sends an integrity poll every hour': [],
            'signal integrity of the IRIG-B input': [],
            'TLS is disabled by default': ['tls', 'default_statement'],
            'By default, authentication is off': ['authentication', 'default_statement'],
            'When TLS is enabled, a certificate is required': ['tls', 'requirement_statement'],
            'SSH requires firmware R120 or later': ['ssh', 'requirement_statement'],
            'IPsec is an optional feature that needs a licence': ['ipsec', 'requirement_statement'],
            'The default gateway address is 0.0.0.0': [],
            'An optional module adds a second serial port': [],
        }
        for text, expected in table.items():
            with self.subTest(text=text): self.assertEqual(self.leads(text), expected)
        self.assertEqual({s.lead_type(g) for g in ('default_statement', 'requirement_statement')}, {'statement'})


if __name__ == '__main__':
    unittest.main()

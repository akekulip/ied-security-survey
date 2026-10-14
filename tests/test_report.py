"""The report and the worksheet: tables, counts, lifecycle groups, legacy, charts and the data files."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import survey as s
from support import SurveyCase


class ReportTests(SurveyCase):
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
                           support_basis=['licence'], default_state='undocumented', activation_needs=['licence_key'],
                           activation_requirements='install the TLS licence',
                           evidence=[{'source_id':source['id'],'location':'html-block:2','quote':'TLS is supported for DNP3 sessions'},
                                     {'source_id':source['id'],'location':'html-block:2','quote':'when the option is licensed','about':'conditions'},
                                     {'source_id':source['id'],'location':'html-block:2','quote':'when the option is licensed','about':'activation'}])
            s.dump(p/'reviews.json', rows[:-1])
            s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['# Synthetic survey', 'Sources attempted: 2; extracted: 1; failed: 1.', 'A. Reviewer (15 rows)',
                             '| R1 | relay | ? | C | ? | ? | ? | ? | ? | ? |', '| M1 | meter | ? | ? | ? | ? | ? | ? | ? | - |',
                             '| relay | tls | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |', '| meter | ssh | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |',
                             '| meter | integrity | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |',
                             '15 of 16 cells are unknown or not reviewed on every interface.', '| R1 | https://vendor.test/gone | ValueError: HTTP 404 |',
                             'Review coverage: 15/16', 'Evidence quotes: 1 of 1 rows', 'Explicit / licensed',
                             '## Findings and evidence', '### R1: tls (conditional)', '- Interface: SCADA (control protocol)', '- Protocol: DNP3 over TLS',
                             '- Implementation: licensed option', '- Conditions: needs the TLS licence', '- Review status: draft (A. Reviewer)',
                             '- Support basis: licence', '- Default configuration: undocumented', '- Activation: licence key: install the TLS licence', '- Deployment: unknown',
                             '- Evidence, html-block:2: "TLS is supported for DNP3 sessions"', '- Evidence on conditions, html-block:2: "when the option is licensed"',
                             '- Source: S1 [type not confirmed] https://vendor.test/r',
                             '| v | R1 | unknown | model not established, hardware not established, firmware unknown | SCADA (control protocol) | unknown; see tls (conditional) | '
                             'unknown; see tls (conditional) | unknown; see tls (conditional) | licence: needs the TLS licence | undocumented | licence key: install the TLS licence | unknown | '
                             'S1 [type not confirmed] html-block:2: "TLS is supported for DNP3 sessions" (+2 more) | draft (A. Reviewer) |',
                             '| v | M1 | unknown | not established | No control protocol established from the examined sources | unknown | not reviewed | unknown | - | - | - | unknown | none | draft (A. Reviewer) |',
                             '| tls | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |', 'Deployment status is unknown for 1 of 1 findings.',
                             'No definition of "legacy" or of the lifecycle groups is recorded', '## Summary by vendor and category',
                             '| v | R1 | relay | not established | unknown | none | not established |',
                             f"| S1 | R1 | untitled | suggested: product page | not established | not established | 2026-10-13 | {source['sha256']} | https://vendor.test/r |"]:
                self.assertIn(expected, text)
            table = (p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual(table[0], 'Manufacturer,Model,Lifecycle,Category,Model scope,Hardware revision,Firmware,Protocol / interface,Interface class,'
                                       'Authentication,Integrity,Encryption,Support conditions,Default,Activation,Deployment,Evidence,Review status,Sources')
            self.assertEqual(len(table), 3)
            self.assertIn('sha256:' + source['sha256'], table[1])
            self.assertNotIn('%', text.replace('No population percentages', ''))
            index = s.load(p/'report'/'evidence_index.json')
            self.assertEqual([(x['product_id'],x['feature'],x['location'],x['sha256'],x['about']) for x in index],
                             [('r1','tls','html-block:2',source['sha256'],about) for about in ('capability','conditions','activation')])
            none = {'total':0,'by_group':{}}
            self.assertEqual(s.load(p/'report'/'candidate_counts.json'), {'r1':{'capability':{'total':1,'by_group':{'tls':1}},'related':none,
                                                                               'statement':{'total':1,'by_group':{'requirement_statement':1}},'profile':none},
                                                                          'm1':{'capability':none,'related':none,'statement':none,'profile':none}})
            self.assertEqual((p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()[1], 'r1,v,R1,relay,,unknown,,,,,,,,')
            # The licence is a condition of its own; the quote showing the capability does not also show the condition.
            s.dump(p/'reviews.json', [dict(rows[1], evidence=rows[1]['evidence'][:1])])
            with self.assertRaisesRegex(ValueError,'about: conditions'): s.report(p/'run', p/'reviews.json', p/'report2', require_evidence=True)
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
            for expected in ['Reviewers on record: none.', '| R1 | relay | - | - | - | - | - | - | - | - |', 'Review coverage: 0/8', '8 of 8 cells are unknown or not reviewed on every interface.',
                             'No supported or conditional finding is recorded yet.',
                             '| v | R1 | unknown | not established | No control protocol established from the examined sources | not reviewed | not reviewed | not reviewed | - | - | - | unknown | none | not reviewed |']:
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
            self.assertIn('| R1 | relay | ? | - | - | - | - | - | - | - |', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))

    def test_findings_table_keeps_control_traffic_apart_from_management(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertLess(text.index('## Findings by product and interface'), text.index('## Capability matrix'))
            for expected in [
                '| v | A | unknown | model not established, hardware not established, firmware v2 or later | DNP3 server (control protocol) | unknown; see tls (supported) | '
                'not assessed; see tls (supported) | supported: encryption detail | built in | undocumented | none stated | unknown | '
                'S1 [type not confirmed] html-block:1: "TLS is supported for DNP3 sessions." (+1 more) | draft (A. Reviewer); confirmed (P. Author) |',
                '| v | A | unknown | model not established, hardware not established, firmware v2 or later | Web interface (management) | conditional: authentication detail | '
                'not reviewed | not reviewed | built in: password must be set | undocumented | none stated | unknown | '
                'S1 [type not confirmed] html-block:2: "The web interface requires a user login" | draft (A. Reviewer) |',
                '| v | B | unknown | not established | No control protocol established from the examined sources | not reviewed | not reviewed | unknown | - | - | - | unknown | none | draft (A. Reviewer) |',
                '| v | B | unknown | model not established, hardware not established, firmware v2 or later | Web interface (management) | supported: authentication detail | '
                'not reviewed | unknown | built in | undocumented | none stated | unknown | S2 [type not confirmed] html-block:1: "The web interface requires a user login" | draft (A. Reviewer) |',
                '| v | M | unknown | not established | No control protocol established from the examined sources | not reviewed | not reviewed | not reviewed | - | - | - | unknown | none | not reviewed |',
                '| A | relay | - | S | - | - | (C) | S | ? | - |', '| B | relay | - | ? | - | - | (S) | ? | - | - |', '| M | meter | - | - | - | - | - | - | - | - |',
                '| relay | tls | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |', '| relay | authentication | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 2 |',
                '| relay | encryption | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |', '| meter | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |',
                '| v | relay | - | - | 2 | 2 unknown: other interface only | 2 not reviewed | 1 supported, 1 unknown |',
                'Deployment status is unknown for 4 of 4 findings.',
                'A. Reviewer (7 rows); P. Author (1 rows)', 'Review coverage: 7/24', '| A | authentication | Web interface | conditional | explicit |']:
                self.assertIn(expected, text)
            self.assertEqual(text.count('| v | A | unknown |'), 2)
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

    def test_what_a_complete_manual_does_not_say_is_unknown_with_that_reason_whatever_the_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/old': b'<p>The relay supports DNP3 and Modbus over serial links.</p><p>Passwords protect front panel access.</p>',
                     'https://vendor.test/new': b'<p>TLS is supported for DNP3 sessions.</p>'}
            proof = {'url':'https://vendor.test/lifecycle','retrieved_at':'2026-10-01T00:00:00+00:00'}
            cfg = self.config(p, [{'id':'old','lifecycle':'end_of_support','seeds':['https://vendor.test/old'],
                                   'lifecycle_evidence':[dict(proof, quote='Support for the OLD relay ended on 1 March 2020.', stated_date='1 March 2020')]},
                                  {'id':'new','lifecycle':'currently_supported','seeds':['https://vendor.test/new'],
                                   'lifecycle_evidence':[dict(proof, basis='listed in the vendor catalogue')]}, {'id':'unk','seeds':[]}], definitions=self.DEFINITIONS)
            with self.site(pages, []): s.crawl(cfg, p/'run', p/'cache')
            src = {x['product_id']: x for x in s.load(p/'run'/'sources.json')}
            def row(pid, feature, status, **more):
                base = {'product_id':pid,'feature':feature,'status':status,'source_ids':[src[pid]['id']],'source_hashes':{src[pid]['id']:src[pid]['sha256']},
                        'location':'','protocol':'','interface':'DNP3 serial and Ethernet','interface_class':'control_protocol','firmware':'all versions covered by manual rev C',
                        'implementation':'','conditions':'','evidence':[],'rationale':'searched in full','reviewer':'A. Reviewer','reviewed_at':'2026-10-13','review_status':'draft'}
                return dict(base, **more)
            # The second row is spelt as it was before 1.6.0 and is read the same way.
            silent = [row('old','encryption','unknown', unknown_reason='complete_document_silent'), row('old','tls','not_documented')]
            claim = row('new','tls','supported', location='html-block:1', protocol='DNP3 over TLS', implementation='native',
                        evidence=[{'source_id':src['new']['id'],'location':'html-block:1','quote':'TLS is supported for DNP3 sessions.'}])
            note = lambda pid, kind, coverage: {'source_id':src[pid]['id'],'doc_type':kind,'coverage':coverage}
            def run(rows, notes):
                s.dump(p/'reviews.json', rows); s.dump(p/'notes.json', notes)
                s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True, source_notes=p/'notes.json')
            for notes in ([], [note('old','product_page','complete')], [note('old','manual','partial')], [note('old','manual','')]):
                with self.subTest(notes=notes), self.assertRaisesRegex(ValueError,'complete_document_silent needs a complete'): run(silent, notes)
            with self.assertRaisesRegex(ValueError,'1 leads for tls exist'):
                run([row('new','tls','unknown', unknown_reason='complete_document_silent')], [note('new','manual','complete')])
            with self.assertRaisesRegex(ValueError,'coverage must be'): run(silent, [note('old','manual','whole')])
            run(silent + [claim], [note('old','manual','complete')])
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in [
                '## Definitions', 'Fixed on 2026-10-13 in the config this run was crawled with, before any result was counted.',
                '- Legacy: Legacy means the vendor states that support has ended.', '- End of support: The vendor states that support has ended.',
                'Legacy under this definition: 1 of 3 devices in this run. Lifecycle status rests on dated vendor evidence for 2 devices and is unknown for 1.',
                '| v | OLD | relay | not established | end of support | 1 March 2020: "Support for the OLD relay ended on 1 March 2020." <https://vendor.test/lifecycle> | not established |',
                '| v | NEW | relay | not established | currently supported | 2026-10-01: listed in the vendor catalogue <https://vendor.test/lifecycle> | not established |',
                '| v | UNK | relay | not established | unknown | none | not established |',
                '| v | OLD | end of support | model not assessed, hardware not assessed, firmware all versions covered by manual rev C | DNP3 serial and Ethernet (control protocol) | '
                'not assessed; see tls (unknown: complete document silent) | not assessed; see tls (unknown: complete document silent) | '
                'unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | '
                'S1 [manual] searched in full: no lead for encryption; S1 [manual] searched in full: no lead for tls | draft (A. Reviewer) |',
                '| v | NEW | currently supported | model not assessed, hardware not assessed, firmware all versions covered by manual rev C | DNP3 serial and Ethernet (control protocol) | not assessed; see tls (supported) |',
                '| v | UNK | unknown | not established | No control protocol established from the examined sources |',
                '| OLD | relay, end of support | - | ?s | - | - | - | ?s | - | - |', '| NEW | relay, currently supported | - | S | - | - | - | - | - | - |',
                # The same four results are counted for the legacy device and the current one; silence is unknown, not unsupported.
                '| relay, end of support | tls | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |', '| relay, currently supported | tls | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |',
                '| relay, unknown | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |', '| relay, end of support | encryption | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |',
                '| v | relay | end of support | - | 1 | 1 not reviewed | 1 not reviewed | 1 unknown: complete document silent |',
                '## Counts by category and lifecycle group', 'The same results are counted for every lifecycle group.',
                '### OLD: tls (unknown: complete document silent)', '- Searched: S1 [manual] searched in full: no lead for tls', '| manual, complete |',
                '| OLD | tls | DNP3 serial and Ethernet | unknown: complete document silent | searched in full |',
                'Evidence quotes: 1 of 1 rows', 'Unknown because a complete document is silent: 2 rows', '?s a complete document was searched and is silent',
                '23 of 24 cells are unknown or not reviewed on every interface.']:
                self.assertIn(expected, text)
            for expected in ['- Currently supported, 1 devices: a security mechanism is named, what it protects is not stated for 1.',
                             '- End of support (legacy), 1 devices: a complete manual was read and documents none for 1.',
                             '- Unknown, 1 devices: not reviewed for 1.',
                             '| end of support | v | OLD | A complete manual was read and documents none | manual silent | not reviewed | not reviewed | - | manual |',
                             '| currently supported | v | NEW | A security mechanism is named, what it protects is not stated | not reviewed | not reviewed | not reviewed | TLS | product page only |']:
                self.assertIn(expected, text)
            data = s.load(p/'report'/'charts'/'data.json')
            self.assertEqual({k: v for k, v in data['answer'].items() if k != 'v'},
                             {'Currently supported': {'mechanism': 1}, 'End of support (legacy)': {'silent': 1}, 'Unknown': {'None': 1}})
            self.assertEqual(data['answer-mechanisms']['tls'], {'Currently supported': [1, 1], 'End of support (legacy)': [0, 1], 'Unknown': [0, 1]})
            table = (p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()
            self.assertIn('end of support', table[1].split(',')[2])
            self.assertIn('searched in full: no lead for tls', table[1])
            self.assertEqual({(r['status'], r['unknown_reason']) for r in s.load(p/'report'/'findings.json') if r['product_id'] == 'old'}, {('unknown', 'complete_document_silent')})

    def test_worksheet_lays_out_leads_and_proposes_no_result(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<title>A relay</title><p>TLS 1.2 is supported. TLS is not used for Modbus.</p>'
                                              b'<p>TLS is disabled by default and requires a certificate.</p>'}
            ended = [{'url':'https://vendor.test/eol','retrieved_at':'2026-10-01T00:00:00+00:00','quote':'Support for the A relay ended on 1 March 2020.','stated_date':'1 March 2020'}]
            cfg = self.config(p, [{'id':'a','lifecycle':'end_of_support','lifecycle_evidence':ended,'seeds':['https://vendor.test/a','https://vendor.test/gone']},{'id':'b','seeds':[]}])
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            s.worksheet(p/'run', p/'sheet')
            text = (p/'sheet'/'worksheet.md').read_text(encoding='utf-8')
            for expected in ['## A', 'v; relay; lifecycle end of support; id `a`',
                             '- lifecycle evidence, 1 March 2020: "Support for the A relay ended on 1 March 2020." <https://vendor.test/eol>',
                             '- S1 extracted, product page (suggested) <https://vendor.test/a>', '- -- failed: ValueError: HTTP 404 <https://vendor.test/gone>',
                             '- **tls**: 2 leads: S1 html-block:2 [TLS 1.2, TLS]; S1 html-block:3 [TLS]',
                             '  - default wording: S1 html-block:3 [TLS is disabled by default]',
                             '  - requirement wording: S1 html-block:3 [TLS is disabled by default and requires]',
                             '- **ssh**: no lead in S1', '- **non_support_statement**: 1 leads: S1 html-block:2 [TLS is not used]',
                             '## B', 'v; relay; lifecycle not recorded; id `b`', '- no source', '- **tls**: no lead', 'not a finding']:
                self.assertIn(expected, text)
            rows = s.load(p/'sheet'/'review_template.json')
            self.assertEqual(rows[1]['_hints'], {'leads': 2, 'where': ['S1 html-block:2', 'S1 html-block:3'], 'no_lead_in': [],
                                                 'default_wording': ['S1 html-block:3'], 'requirement_wording': ['S1 html-block:3']})
            self.assertEqual(rows[6]['_hints'], {'leads': 0, 'where': [], 'no_lead_in': ['S1'], 'default_wording': [], 'requirement_wording': []})
            # The wording about TLS is not offered as wording about SSH.
            self.assertNotIn('- **ssh**: no lead in S1\n  - default wording', text)
            self.assertTrue(all(map(s.untouched, rows)))
            s.report(p/'run', p/'sheet'/'review_template.json', p/'report')
            self.assertIn('Review coverage: 0/16', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError): s.worksheet(p/'run', p/'sheet')

    def test_report_shows_the_sampling_frame_and_keeps_unreviewed_devices_out_of_the_table(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            listed = [{'url':'https://vendor.test/catalogue.xml','retrieved_at':'2026-10-13T00:00:00+00:00','basis':'listed in the vendor catalogue'}]
            gone = [{'url':'https://vendor.test/r','retrieved_at':'2026-10-13T00:00:00+00:00','quote':'Manufacturing for this product has been discontinued.'}]
            products = [dict({'id': f'r{i}', 'seeds': []}, **({'lifecycle':'discontinued_support_not_stated','lifecycle_evidence':gone} if i < 10
                                                               else {'lifecycle':'currently_supported','lifecycle_evidence':listed})) for i in range(30)]
            frame = [{'vendor':'v','category':'relay','lifecycle':'currently_supported','in_catalogue':80,'selected':20},
                     {'vendor':'v','category':'relay','lifecycle':'discontinued_support_not_stated','in_catalogue':40,'selected':10},
                     {'vendor':'v','category':'meter','lifecycle':'currently_supported','in_catalogue':9,'selected':0}]
            cfg = self.config(p, products, frame=frame, definitions=self.DEFINITIONS)
            with self.site({}, []): s.crawl(cfg, p/'run', p/'cache')
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['## Summary by vendor, category and lifecycle', '| v | relay | currently supported | 80 | 20 | 20 not reviewed | 20 not reviewed | 20 not reviewed |',
                             '| v | relay | discontinued, support not stated | 40 | 10 | 10 not reviewed | 10 not reviewed | 10 not reviewed |',
                             '| v | meter | currently supported | 9 | 0 | - | - | - |', '30 products have no review row yet.',
                             # Discontinued is not legacy: none of the thirty has a vendor statement that support ended.
                             'Legacy under this definition: 0 of 30 devices in this run. Lifecycle status rests on dated vendor evidence for 30 devices and is unknown for 0.',
                             '30 devices without a review row are left out of this table. devices.csv lists all 30 with their lifecycle evidence.']:
                self.assertIn(expected, text)
            self.assertNotIn('No control protocol established', text)
            self.assertEqual(len((p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()), 31)
            devices = (p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual((len(devices), devices[2]), (31, 'r1,v,R1,relay,,discontinued_support_not_stated,no,,2026-10-13,Manufacturing for this product has been discontinued.,https://vendor.test/r,,,'))
            # The frame and the evidence base are drawn; with nothing read and nothing reviewed there is no chart of mentions or results.
            self.assertEqual(sorted(x.name for x in (p/'report'/'charts').iterdir()), ['catalogue-category.svg', 'catalogue-lifecycle.svg', 'data.json', 'evidence-base.svg'])
            data = s.load(p/'report'/'charts'/'data.json')
            self.assertEqual(data['catalogue-lifecycle'], {'v': {'currently_supported': 89, 'discontinued_support_not_stated': 40}})
            self.assertEqual(data['catalogue-category'], {'v': {'relay': 120, 'meter': 9}})
            self.assertEqual(data['evidence-base'], {'v': {'none': 30}, 'Discontinued, support not stated': {'none': 10}, 'Currently supported': {'none': 20}})
            for expected in ['The catalogue inventory holds 129 devices: 89 currently supported; 40 discontinued, support not stated. Legacy, as defined above, is the "end of support" group: 0 devices.',
                             '![Catalogue devices by vendor and lifecycle state](charts/catalogue-lifecycle.svg)', 'No cell has been reviewed yet, so there is no result to draw.']:
                self.assertIn(expected, text)
            # The matrix and the unresolved list count the unreviewed devices too, without a line for each.
            self.assertIn('30 products without a review row are left out', text)
            self.assertIn('240 of 240 cells are unknown or not reviewed on every interface.', text)
            self.assertIn('This includes all 240 cells of the 30 products without a review row', text)
            self.assertNotIn(' | - | - | - | - | - | - | - | - |', text)
            self.assertNotIn(': dnp3_secure_authentication, tls, ipsec', text)
            # Without definitions in the config the run was crawled with, nothing is counted by lifecycle group.
            cfg = self.config(p, products, frame=frame)
            with self.site({}, []): s.crawl(cfg, p/'run2', p/'cache')
            s.report(p/'run2', p/'run2'/'review_template.json', p/'report2')
            text = (p/'report2'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['No definition of "legacy" or of the lifecycle groups is recorded in the config of this run, so no result is counted by lifecycle group.',
                             '## Summary by vendor and category', '| v | relay | - | 120 | 30 | 30 not reviewed | 30 not reviewed | 30 not reviewed |', '| v | meter | - | 9 | 0 | - | - | - |',
                             '## Counts by category', '| relay | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 30 |']:
                self.assertIn(expected, text)
            for absent in ['## Definitions', 'Legacy under this definition', '## Counts by category and lifecycle group', 'relay, currently supported']:
                self.assertNotIn(absent, text)
            # Nor is anything drawn by lifecycle state.
            self.assertEqual(sorted(x.name for x in (p/'report2'/'charts').iterdir()), ['catalogue-category.svg', 'data.json', 'evidence-base.svg'])
            self.assertEqual(s.load(p/'report2'/'charts'/'data.json')['evidence-base'], {'v': {'none': 30}})

    def test_report_counts_unread_sources_by_vendor_once_there_are_too_many_to_list(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/gated': ValueError('login required: redirected to https://vendor.test/login?next=x')}
            cfg = self.config(p, [{'id': f'r{i}', 'seeds': [f'https://vendor.test/missing{i}', 'https://vendor.test/gated']} for i in range(21)])
            with self.site(pages, []): s.crawl(cfg, p/'run', p/'cache')
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn('Sources attempted: 21; extracted: 0; failed: 21; documents behind a sign-in, not requested: 21.', text)
            self.assertIn('| v | ValueError: HTTP 404 | 21 |', text)
            self.assertIn('| v | behind a sign-in, not requested | 21 |', text)
            self.assertNotIn('https://vendor.test/missing3 ', text)

    def test_report_keeps_gateway_only_capability_and_field_evidence_apart(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            rows = s.load(p/'reviews.json')
            field = {'kind':'utility configuration audit', 'reference':'Audit report 2025-07', 'date':'2025-07-14', 'scope':'12 relays at one substation'}
            rows[0].update(deployment_status='disabled', deployment_evidence=[field], default_state='disabled', model_scope='A-100', hardware_revision='rev C',
                           activation_needs=['configuration', 'certificates_or_keys'], activation_requirements='enable TLS and load a certificate')
            rows[1].update(status='conditional', conditions='needs an external encrypting gateway', support_basis=['external_gateway'], review_status='draft')
            s.dump(p/'reviews.json', rows)
            s.report(p/'run', p/'reviews.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['| A | relay | - | S | - | - | (C) | G | ? | - |',
                             '| relay | encryption | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |', '| relay | tls | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |',
                             '| v | relay | - | - | 2 | 2 unknown: other interface only | 2 not reviewed | 1 via external gateway only, 1 unknown |',
                             'conditional: external gateway only: encryption detail',
                             '| tls: model A-100, hardware rev C, firmware v2 or later; encryption: model not established, hardware not established, firmware v2 or later |',
                             'built in; external gateway: needs an external encrypting gateway',
                             'tls: disabled; encryption: undocumented', 'tls: configuration, certificates or keys: enable TLS and load a certificate; encryption: none stated',
                             'disabled (utility configuration audit, 2025-07-14); unknown',
                             'Deployment status is unknown for 3 of 4 findings.',
                             '- A, tls on DNP3 server: disabled (utility configuration audit, Audit report 2025-07, 2025-07-14, 12 relays at one substation)',
                             '| tls | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |', '### A: encryption (conditional: external gateway only)', '- Support basis: external gateway']:
                self.assertIn(expected, text)
            found = {(r['feature'], r['interface']): r for r in s.load(p/'report'/'findings.json')}
            self.assertEqual(s.token(found['encryption', 'DNP3 server']), 'gateway')
            csv_row = next(line for line in (p/'report'/'findings.csv').read_text(encoding='utf-8').splitlines() if line.startswith('a,v,A,relay,unknown,tls,supported,'))
            for part in [',A-100,rev C,v2 or later,', ',built_in,', ',disabled,configuration | certificates_or_keys,enable TLS and load a certificate,disabled,']:
                self.assertIn(part, csv_row)

    def test_device_notes_state_identity_and_lifecycle_only_with_dated_vendor_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/a': b'<p>Support for the A relay ended on 1 March 2020.</p>'}
            cfg = self.config(p, [{'id':'a','seeds':list(pages)}, {'id':'b','seeds':[]}], definitions=self.DEFINITIONS)
            with self.site(pages, []): s.crawl(cfg, p/'run', p/'cache')
            source = s.load(p/'run'/'sources.json')[0]
            notes = s.load(p/'run'/'device_notes_template.json')
            self.assertEqual([(n['product_id'], n['manufacturer'], n['model'], n['identity_level'], n['lifecycle_status'], n['lifecycle_evidence'], n['release_date']) for n in notes],
                             [('a','v','A','','unknown',[],''), ('b','v','B','','unknown',[],'')])
            quote = {'source_id': source['id'], 'location': 'html-block:1', 'quote': 'Support for the A relay ended on 1 March 2020.', 'stated_date': '1 March 2020'}
            def run(**change):
                s.dump(p/'devices.json', [dict(notes[0], **change)])
                s.report(p/'run', p/'run'/'review_template.json', p/'report', device_notes=p/'devices.json')
                return (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            text = run(identity_level='model', lifecycle_status='end_of_support', lifecycle_evidence=[quote], release_date='2009', noted_by='A. Reviewer',
                       release_evidence=[{'url':'https://vendor.test/history', 'retrieved_at':'2026-10-13T00:00:00+00:00'}])
            for expected in ['Legacy under this definition: 1 of 2 devices in this run.',
                             '| v | A | relay | model | end of support | 1 March 2020: "Support for the A relay ended on 1 March 2020." <https://vendor.test/a> | 2009 |',
                             '| v | B | relay | not established | unknown | none | not established |']:
                self.assertIn(expected, text)
            self.assertEqual((p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()[1],
                             f"a,v,A,relay,model,end_of_support,yes,,1 March 2020,Support for the A relay ended on 1 March 2020.,https://vendor.test/a,{source['sha256']},2009,A. Reviewer")
            # Still discontinued, with a vendor sentence that support continues: its own group, not legacy.
            text = run(lifecycle_status='discontinued_supported', lifecycle_evidence=[quote])
            self.assertIn('Legacy under this definition: 0 of 2 devices in this run.', text)
            self.assertIn('| discontinued, still supported |', text)
            for change, message in [
                    ({'lifecycle_status':'end_of_support'}, 'needs dated vendor evidence'), ({'lifecycle_status':'legacy'}, 'lifecycle_status must be one of'),
                    ({'lifecycle_status':'end_of_support', 'lifecycle_evidence':[{'url':'https://vendor.test/a', 'retrieved_at':'2026-10-13'}]}, "needs the vendor's own sentence"),
                    ({'lifecycle_status':'currently_supported', 'lifecycle_evidence':[{'url':'https://vendor.test/a'}]}, 'lifecycle evidence needs a date'),
                    ({'lifecycle_status':'currently_supported', 'lifecycle_evidence':[{'url':'https://forum.example/thread', 'retrieved_at':'2026-10-13'}]}, 'must be a vendor source'),
                    ({'lifecycle_status':'end_of_support', 'lifecycle_evidence':[dict(quote, quote='Support for the A relay ended in 2019, we believe.')]}, 'lifecycle quote not found'),
                    ({'lifecycle_status':'end_of_support', 'lifecycle_evidence':[dict(quote, source_id='nope')]}, 'not one of this product'),
                    ({'identity_level':'range'}, 'identity_level must be one of'), ({'release_date':'2009'}, 'release_date needs release_evidence'),
                    ({'product_id':'zzz'}, 'not in this run')]:
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, message): run(**change)
            # A config may carry the status, as the inventory writes it. Without evidence the report refuses that as well.
            cfg = self.config(p, [{'id':'a','lifecycle':'end_of_support','seeds':[]}])
            with self.site({}, []): s.crawl(cfg, p/'run2', p/'cache')
            self.assertIn('a: lifecycle "end_of_support" has no lifecycle_evidence; the report will refuse it', s.load(p/'run2'/'manifest.json')['config_warnings'])
            with self.assertRaisesRegex(ValueError,'needs dated vendor evidence'): s.report(p/'run2', p/'run2'/'review_template.json', p/'report2')
            # A label from before 1.6.0 is shown as the label it was and counted as unknown.
            cfg = self.config(p, [{'id':'a','lifecycle':'legacy','seeds':[]}], definitions=self.DEFINITIONS)
            with self.site({}, []): s.crawl(cfg, p/'run3', p/'cache')
            s.report(p/'run3', p/'run3'/'review_template.json', p/'report3')
            text = (p/'report3'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn('| v | A | relay | not established | unknown (vendor label: legacy (label used before 1.6.0)) | none | not established |', text)
            self.assertIn('Legacy under this definition: 0 of 1 devices in this run.', text)

    def test_a_review_written_before_1_6_still_reports_with_the_new_facts_not_assessed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); src = self.reviewed_run(p)
            rows = s.load(p/'reviews.json')
            for r in rows:
                for key in ('model_scope', 'hardware_revision', 'support_basis', 'default_state', 'activation_needs'): r.pop(key, None)
                r['review_status'] = 'draft'
            rows[4].update(status='conflicting', interface='Engineering access', interface_class='management', protocol='SSH', location='html-block:1')
            s.dump(p/'reviews.json', rows)
            s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['| v | A | unknown | model not assessed, hardware not assessed, firmware v2 or later | DNP3 server (control protocol) |',
                             '| supported: encryption detail | not assessed | not assessed | not assessed | unknown |',
                             '| A | relay | - | S | - | - | (C) | S | (?c) | - |', '| A | ssh | Engineering access | unknown: sources conflict | explicit |',
                             '### A: ssh (unknown: sources conflict)', '| tls | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |']:
                self.assertIn(expected, text)
            self.assertEqual({r['status'] for r in s.load(p/'report'/'findings.json')} - set(s.STATUSES), set())

    def test_report_draws_what_the_run_holds_and_keeps_every_number_beside_the_charts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            (p/'report'/'charts').mkdir(parents=True); (p/'report'/'charts'/'left-over.svg').write_text('<svg/>')
            s.report(p/'run', p/'reviews.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            # A chart from an earlier report of this directory does not linger.
            self.assertEqual(sorted(x.name for x in (p/'report'/'charts').iterdir()),
                             ['answer-mechanisms.svg', 'answer.svg', 'data.json', 'devices-control-traffic.json', 'evidence-base.svg', 'mentions.svg', 'results.svg'])
            # The survey's own question comes first: what the reviewed documents establish for control traffic, device by device.
            self.assertLess(text.index('charts/answer.svg'), text.index('charts/evidence-base.svg'))
            self.assertLess(text.index('## At a glance'), text.index('## Control traffic, device by device'))
            self.assertEqual((text.count('## At a glance'), text.count('charts/evidence-base.svg'), text.count('## Control traffic, device by device')), (1, 1, 1))
            for expected in ['- All devices, 3 devices: encryption documented for 1; documented for management access only, not for control traffic for 1; not reviewed for 1.',
                             '![What the documents establish about protecting control traffic, per device](charts/answer.svg)',
                             '![Which security mechanism is documented for control traffic](charts/answer-mechanisms.svg)',
                             'Whether it is switched on in any installation is not known.',
                             '| unknown | v | A | Encryption documented | supported | management only | not reviewed | TLS | product page only |',
                             '| unknown | v | B | Documented for management access only, not for control traffic | unknown | management only | not reviewed | - | product page only |']:
                self.assertIn(expected, text)
            self.assertNotIn('| unknown | v | M |', text)
            self.assertLess(text.index('## Definitions') if '## Definitions' in text else 0, text.index('## At a glance'))
            self.assertLess(text.index('## At a glance'), text.index('## Devices'))
            for expected in ['![Most direct public document read per device, by vendor](charts/evidence-base.svg)',
                             '![Devices whose public documents mention each term, by vendor](charts/mentions.svg)',
                             '![Result per capability for a control protocol, all devices](charts/results.svg)',
                             'Of 3 devices in this run, a manual, device profile, conformance statement or security guide was read for 0, '
                             'a data sheet, brochure or a document whose type is not yet established for 0, only a product page or advisory for 2, and nothing for 1.',
                             '(0 of 2 sources confirmed)', '7 of 24 cells are reviewed.',
                             'at least one mention of authentication, integrity or encryption wording for 0 of 3 devices, and of DNP3 Secure Authentication for 0.',
                             'only the chart of results does that, and only for reviewed cells']:
                self.assertIn(expected, text)
            # The series behind each chart are written out, so a mark can be checked against the tables.
            data = s.load(p/'report'/'charts'/'data.json')
            self.assertEqual(data['evidence-base'], {'v': {'product_page': 2, 'none': 1}})
            self.assertEqual(data['answer'], {'v': {'encrypted': 1, 'other': 1, 'None': 1}})
            self.assertEqual((data['answer-mechanisms']['tls'], data['answer-mechanisms']['dnp3_secure_authentication']), ({'All devices': [1, 3]}, {'All devices': [0, 3]}))
            placed = {d['product_id']: (d['established'], d['encryption'], d['tls']) for d in s.load(p/'report'/'charts'/'devices-control-traffic.json')}
            self.assertEqual(placed, {'a': ('encrypted', 'supported', 'supported'), 'b': ('other', 'unknown', 'unknown'), 'm': (None, None, None)})
            self.assertEqual((data['mentions']['tls'], data['mentions']['encryption']), ({'v': [1, 3]}, {'v': [0, 3]}))
            self.assertEqual(data['results']['TLS'], {'supported': 1, 'unknown': 1, 'None': 1})
            # A login on the web page is a result for another interface; for control traffic authentication stays unknown.
            self.assertEqual(data['results']['Authentication'], {'other': 2, 'None': 1})
            self.assertEqual(data['results']['Integrity'], {'None': 3})
            for name in ('answer', 'answer-mechanisms', 'evidence-base', 'mentions', 'results'):
                svg = ET.fromstring((p/'report'/'charts'/f'{name}.svg').read_text(encoding='utf-8'))
                self.assertTrue(svg.tag.endswith('svg') and svg[0].tag.endswith('title') and svg[1].tag.endswith('desc'))
            words = (p/'report'/'charts'/'results.svg').read_text(encoding='utf-8')
            for expected in ['Result per capability for a control protocol: all devices (3 devices)', 'Properties of the interface', 'Mechanisms that may provide them',
                             'DNP3 Secure Authentication', '<title>Supported: 1</title>', '<title>Not reviewed: 3</title>',
                             '<title>Unknown here; a result exists for another interface: 2</title>']:
                self.assertIn(expected, words)
            # Nothing reviewed, nothing to draw as a result.
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            self.assertEqual(sorted(x.name for x in (p/'report'/'charts').iterdir()), ['data.json', 'evidence-base.svg', 'mentions.svg'])
            self.assertIn('No cell has been reviewed yet, so there is no result to draw.', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))
            self.assertNotIn('## Control traffic, device by device', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))

    def test_charts_draw_groups_captions_and_escape_what_they_are_given(self):
        bars = s.svg_bars('Devices & <documents>', ['A note that is long enough to be wrapped ' * 5],
                          [('By vendor', None), ('A & B', {'x': 3, 'y': 1}), ('Empty', {})], [('x', 'First <kind>', '#0072B2'), ('y', 'Second', '#F0E442')])
        root = ET.fromstring(bars)
        texts = [t.text for t in root.iter('{http://www.w3.org/2000/svg}text')]
        for expected in ['Devices & <documents>', 'By vendor', 'A & B', 'First <kind>', '3', '4', '0']:
            self.assertIn(expected, texts)
        self.assertGreater(sum(t.startswith('A note') or 'wrapped' in t for t in texts), 1)
        grid = ET.fromstring(s.svg_grid('Grid', ['note'], [('r', 'Row')], [('a', 'Vendor with a long name / Brand'), ('b', 'B')], lambda r, c: (1, 2) if c == 'a' else (0, 0)))
        texts = [t.text for t in grid.iter('{http://www.w3.org/2000/svg}text')]
        self.assertIn('1 of 2', texts); self.assertIn('-', texts)
        self.assertEqual((s.title_of('dnp3_secure_authentication'), s.title_of('plc'), s.title_of('protective_relay'), s.title_of('tls')), ('DNP3 Secure Authentication', 'PLC', 'Protective relay', 'TLS'))

    def test_legacy_covers_the_lifecycle_states_the_definitions_name_and_a_revision_is_stated(self):
        wide = dict(self.DEFINITIONS, legacy='Legacy means the vendor has discontinued the device.',
                    legacy_statuses=['end_of_support', 'discontinued_support_not_stated', 'discontinued_supported'],
                    revisions=[{'date': '2026-10-13', 'change': 'Legacy widened from end of support to every discontinued device.',
                                'known_then': 'A first draft had been counted and placed no device in the legacy group.'}])
        # Whatever order the config lists them in, the states are used in lifecycle order. Words alone mean end of support.
        self.assertEqual(s.legacy_states(wide), ('discontinued_supported', 'discontinued_support_not_stated', 'end_of_support'))
        self.assertEqual((s.legacy_states(self.DEFINITIONS), s.legacy_states(None), s.legacy_states({'defined_at': '2026-10-13'})), (('end_of_support',), (), ()))
        base = {'sampling': 'x', 'products': [{'id': 'p', 'domains': ['vendor.test'], 'seeds': []}]}
        # A device on sale, or one whose state nobody established, is legacy under no definition; a revision says what was known.
        for change in ({'legacy_statuses': ['unknown']}, {'legacy_statuses': ['currently_supported', 'end_of_support']}, {'legacy_statuses': []},
                       {'legacy_statuses': 'end_of_support'}, {'legacy': ''}, {'revisions': [{'date': '2026-10-13', 'change': 'Widened.'}]},
                       {'revisions': ['widened']}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'definitions: '):
                s.validate_config(dict(base, definitions=dict(wide, **change)))
        with self.assertRaisesRegex(ValueError, 'definitions: legacy_statuses'):
            s.check_rules({'definitions': {'legacy_statuses': ['end_of_support']}, 'vendors': {}})
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/old': b'<p>The relay supports DNP3 and Modbus over serial links.</p>',
                     'https://vendor.test/new': b'<p>TLS is supported for DNP3 sessions.</p>'}
            proof = {'url': 'https://vendor.test/lifecycle', 'retrieved_at': '2026-10-01T00:00:00+00:00'}
            frame = [{'vendor': 'v', 'category': 'relay', 'lifecycle': 'discontinued_support_not_stated', 'in_catalogue': 5, 'selected': 1},
                     {'vendor': 'v', 'category': 'relay', 'lifecycle': 'currently_supported', 'in_catalogue': 7, 'selected': 1}]
            cfg = self.config(p, [{'id': 'old', 'lifecycle': 'discontinued_support_not_stated', 'seeds': ['https://vendor.test/old'],
                                   'lifecycle_evidence': [dict(proof, quote='Manufacturing for the OLD relay has been discontinued.')]},
                                  {'id': 'new', 'lifecycle': 'currently_supported', 'seeds': ['https://vendor.test/new'],
                                   'lifecycle_evidence': [dict(proof, basis='listed in the vendor catalogue')]}, {'id': 'unk', 'seeds': []}],
                              definitions=wide, frame=frame)
            with self.site(pages, []): s.crawl(cfg, p/'run', p/'cache')
            src = {x['product_id']: x for x in s.load(p/'run'/'sources.json')}
            def row(pid, feature, status, **more):
                base = {'product_id': pid, 'feature': feature, 'status': status, 'source_ids': [src[pid]['id']], 'source_hashes': {src[pid]['id']: src[pid]['sha256']},
                        'location': '', 'protocol': '', 'interface': 'DNP3 serial and Ethernet', 'interface_class': 'control_protocol', 'firmware': 'all versions',
                        'implementation': '', 'conditions': '', 'evidence': [], 'rationale': 'searched in full', 'reviewer': 'A. Reviewer', 'reviewed_at': '2026-10-13'}
                return dict(base, **more)
            s.dump(p/'reviews.json', [row('old', 'encryption', 'unknown', unknown_reason='complete_document_silent'),
                                      row('new', 'tls', 'supported', location='html-block:1', protocol='DNP3 over TLS', implementation='native',
                                          evidence=[{'source_id': src['new']['id'], 'location': 'html-block:1', 'quote': 'TLS is supported for DNP3 sessions.'}])])
            s.dump(p/'notes.json', [{'source_id': src['old']['id'], 'doc_type': 'manual', 'coverage': 'complete'}])
            s.report(p/'run', p/'reviews.json', p/'report', require_evidence=True, source_notes=p/'notes.json')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in [
                'First fixed on 2026-10-13 and revised since. What follows is the definition in the config this run was crawled with; each revision is listed with what had been counted when it was made.',
                '- Legacy: Legacy means the vendor has discontinued the device.',
                '- Counted as legacy: discontinued, still supported; discontinued, support not stated; end of support.',
                '- Revised on 2026-10-13: Legacy widened from end of support to every discontinued device. What had been counted by then: A first draft had been counted and placed no device in the legacy group.',
                'Legacy under this definition: 1 of 3 devices in this run.',
                'Legacy, as defined above, is the "discontinued, still supported", "discontinued, support not stated" and "end of support" groups together: 5 devices.',
                # Legacy is one group; the states inside it stay visible, the empty ones too.
                '- Currently supported, 1 devices: a security mechanism is named, what it protects is not stated for 1.',
                '- Legacy, 1 devices: a complete manual was read and documents none for 1.',
                '  - Discontinued, still supported, 0 devices: none in this run.',
                '  - Discontinued, support not stated, 1 devices: a complete manual was read and documents none for 1.',
                '  - End of support, 0 devices: none in this run.',
                '- Unknown, 1 devices: not reviewed for 1.',
                '| Legacy | Lifecycle | Manufacturer | Model | What the documents establish |',
                '| yes | discontinued, support not stated | v | OLD | A complete manual was read and documents none |',
                '| no | currently supported | v | NEW | A security mechanism is named, what it protects is not stated |',
                '![Result per capability for a control protocol, legacy](charts/results-legacy.svg)',
                # The counts further down stay by lifecycle state, so the group can always be taken apart again.
                '| relay, discontinued, support not stated | encryption | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |']:
                self.assertIn(expected, text)
            self.assertNotIn('before any result was counted', text)
            data = s.load(p/'report'/'charts'/'data.json')
            self.assertEqual({k: v for k, v in data['answer'].items() if k != 'v'},
                             {'Currently supported': {'mechanism': 1}, 'Legacy': {'silent': 1}, 'Unknown': {'None': 1}, 'Discontinued, still supported': {},
                              'Discontinued, support not stated': {'silent': 1}, 'End of support': {}})
            self.assertEqual(data['answer-mechanisms']['tls'], {'Currently supported': [1, 1], 'Legacy': [0, 1], 'Unknown': [0, 1]})
            self.assertEqual([(d['product_id'], d['legacy']) for d in s.load(p/'report'/'charts'/'devices-control-traffic.json')],
                             [('old', 'yes'), ('new', 'no'), ('unk', 'unknown')])
            self.assertEqual([line.split(',')[5:7] for line in (p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()],
                             [['lifecycle_status', 'legacy'], ['discontinued_support_not_stated', 'yes'], ['currently_supported', 'no'], ['unknown', 'unknown']])


if __name__ == '__main__':
    unittest.main()

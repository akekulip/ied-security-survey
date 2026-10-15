"""The report and the worksheet: tables, counts, lifecycle groups, legacy and the data files."""
from pathlib import Path
import tempfile
import unittest

from iedsurvey.crawl import crawl, validate_config
from iedsurvey.inventory import check_rules
from iedsurvey.report import report
from iedsurvey.review import token, untouched
from iedsurvey.store import dump, load
from iedsurvey.vocabulary import STATUSES, legacy_states
from iedsurvey.worksheet import worksheet
from support import SurveyCase


class ReportTests(SurveyCase):
    def test_report_builds_matrix_denominators_and_evidence_index(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/r': b'<h2>DNP3</h2><p>TLS is supported for DNP3 sessions when the option is licensed.</p>'}
            cfg = self.config(p, [{'id':'r1','seeds':['https://vendor.test/r','https://vendor.test/gone']},{'id':'m1','category':'meter','seeds':[]}], title='Synthetic survey')
            with self.site(pages, calls): crawl(cfg, p/'run', p/'cache')
            source = load(p/'run'/'sources.json')[0]
            rows = load(p/'run'/'review_template.json')
            for row in rows: row.update(reviewer='A. Reviewer', reviewed_at='2026-10-13', rationale='not assessed')
            rows[1].update(status='conditional', source_ids=[source['id']], source_hashes={source['id']:source['sha256']}, location='html-block:2',
                           protocol='DNP3 over TLS', interface='SCADA', interface_class='control_protocol', firmware='unknown', implementation='licensed option',
                           conditions='needs the TLS licence', rationale='Explicit | licensed',
                           support_basis=['licence'], default_state='undocumented', activation_needs=['licence_key'],
                           activation_requirements='install the TLS licence',
                           evidence=[{'source_id':source['id'],'location':'html-block:2','quote':'TLS is supported for DNP3 sessions'},
                                     {'source_id':source['id'],'location':'html-block:2','quote':'when the option is licensed','about':'conditions'},
                                     {'source_id':source['id'],'location':'html-block:2','quote':'when the option is licensed','about':'activation'}])
            dump(p/'reviews.json', rows[:-1])
            report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
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
                             '| v | R1 | unknown | model not established, hardware not established, firmware unknown | '
                             'SCADA (control protocol) | unknown; see tls (conditional) | '
                             'unknown; see tls (conditional) | unknown; see tls (conditional) | licence: needs the TLS '
                             'licence | undocumented | licence key: install the TLS licence | unknown | '
                             'S1 [type not confirmed] html-block:2: "TLS is supported for DNP3 sessions" (+2 more) | '
                             'draft (A. Reviewer) |',
                             '| v | M1 | unknown | not established | No control protocol established from the examined '
                             'sources | unknown | not reviewed | unknown | - | - | - | unknown | none | draft (A. '
                             'Reviewer) |',
                             '| tls | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |', 'Deployment status is unknown for 1 of 1 findings.',
                             'No definition of "legacy" or of the lifecycle groups is recorded', '## Summary by vendor and category',
                             '| v | R1 | relay | not established | unknown | none | not established |',
                             f"| S1 | R1 | untitled | suggested: product page | not established | not established | "
                             f"2026-10-13 | {source['sha256']} | https://vendor.test/r |"]:
                self.assertIn(expected, text)
            table = (p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual(table[0], 'Manufacturer,Model,Lifecycle,Category,Model scope,Hardware '
                                       'revision,Firmware,Protocol / interface,Interface class,'
                                       'Authentication,Integrity,Encryption,Support '
                                       'conditions,Default,Activation,Deployment,Evidence,Review status,Sources')
            self.assertEqual(len(table), 3)
            self.assertIn('sha256:' + source['sha256'], table[1])
            # Percentages appear only as shares of the run's DNP3 devices, in the DNP3 section.
            self.assertNotIn('%', text[:text.index('## DNP3 security')] + text[text.index('## Devices'):])
            index = load(p/'report'/'evidence_index.json')
            self.assertEqual([(x['product_id'],x['feature'],x['location'],x['sha256'],x['about']) for x in index],
                             [('r1','tls','html-block:2',source['sha256'],about) for about in ('capability','conditions','activation')])
            none = {'total':0,'by_group':{}}
            self.assertEqual(load(p/'report'/'candidate_counts.json'), {'r1':{'capability':{'total':1,'by_group':{'tls':1}},'related':none,
                                                                               'statement':{'total':1,'by_group':{'requirement_statement':1}},'profile':none},
                                                                          'm1':{'capability':none,'related':none,'statement':none,'profile':none}})
            self.assertEqual((p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()[1], 'r1,v,R1,relay,,unknown,,,,,,,,')
            # The licence is a condition of its own; the quote showing the capability does not also show the condition.
            dump(p/'reviews.json', [dict(rows[1], evidence=rows[1]['evidence'][:1])])
            with self.assertRaisesRegex(ValueError,'about: conditions'): report(p/'run', p/'reviews.json', p/'report2', require_evidence=True)
            rows[1]['evidence'][0]['quote'] = 'TLS is supported for all DNP3 sessions'
            dump(p/'reviews.json', rows)
            with self.assertRaisesRegex(ValueError,'evidence quote not found'): report(p/'run', p/'reviews.json', p/'report2')

    def test_untouched_template_rows_count_as_not_reviewed_but_partial_rows_fail(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.config(p, [{'id':'r1','seeds':['https://vendor.test/r']}])
            with self.site({'https://vendor.test/r': b'<p>TLS</p>'}, calls): crawl(cfg, p/'run', p/'cache')
            template = p/'run'/'review_template.json'
            report(p/'run', template, p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['Reviewers on record: none.', '| R1 | relay | - | - | - | - | - | - | - | - |', 'Review coverage: 0/8', '8 of 8 cells are unknown or not reviewed on every interface.',
                             'No supported or conditional finding is recorded yet.',
                             '| v | R1 | unknown | not established | No control protocol established from the examined '
                             'sources | not reviewed | not reviewed | not reviewed | - | - | - | unknown | none | not '
                             'reviewed |']:
                self.assertIn(expected, text)
            self.assertEqual(load(p/'report'/'findings.json'), [])
            rows = load(template)
            rows[0].update(reviewer='A. Reviewer', reviewed_at='2026-10-13', rationale='Examined; not established.')
            rows[1]['rationale'] = 'started but unsigned'
            dump(p/'reviews.json', rows)
            with self.assertRaisesRegex(ValueError, r"identity/date/rationale required.*'r1', 'tls'"): report(p/'run', p/'reviews.json', p/'report')
            rows[1]['rationale'] = ''
            dump(p/'reviews.json', rows)
            report(p/'run', p/'reviews.json', p/'report')
            self.assertIn('| R1 | relay | ? | - | - | - | - | - | - | - |', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))

    def test_findings_table_keeps_control_traffic_apart_from_management(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertLess(text.index('## Findings by product and interface'), text.index('## Capability matrix'))
            for expected in [
                '| v | A | unknown | model not established, hardware not established, firmware v2 or later | DNP3 '
                'server (control protocol) | unknown; see tls (supported) | '
                'not assessed; see tls (supported) | supported: encryption detail | built in | undocumented | none '
                'stated | unknown | '
                'S1 [type not confirmed] html-block:1: "TLS is supported for DNP3 sessions." (+1 more) | draft (A. '
                'Reviewer); confirmed (P. Author) |',
                '| v | A | unknown | model not established, hardware not established, firmware v2 or later | Web '
                'interface (management) | conditional: authentication detail | '
                'not reviewed | not reviewed | built in: password must be set | undocumented | none stated | unknown | '
                'S1 [type not confirmed] html-block:2: "The web interface requires a user login" | draft (A. Reviewer) '
                '|',
                '| v | B | unknown | not established | No control protocol established from the examined sources | not '
                'reviewed | not reviewed | unknown | - | - | - | unknown | none | draft (A. Reviewer) |',
                '| v | B | unknown | model not established, hardware not established, firmware v2 or later | Web '
                'interface (management) | supported: authentication detail | '
                'not reviewed | unknown | built in | undocumented | none stated | unknown | S2 [type not confirmed] '
                'html-block:1: "The web interface requires a user login" | draft (A. Reviewer) |',
                '| v | M | unknown | not established | No control protocol established from the examined sources | not '
                'reviewed | not reviewed | not reviewed | - | - | - | unknown | none | not reviewed |',
                '| A | relay | - | S | - | - | (C) | S | ? | - |', '| B | relay | - | ? | - | - | (S) | ? | - | - |', '| M | meter | - | - | - | - | - | - | - | - |',
                '| relay | tls | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |', '| relay | authentication | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 2 |',
                '| relay | encryption | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |', '| meter | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |',
                '| v | relay | - | - | 2 | 2 unknown: other interface only | 2 not reviewed | 1 supported, 1 unknown |',
                'Deployment status is unknown for 4 of 4 findings.',
                'A. Reviewer (7 rows); P. Author (1 rows)', 'Review coverage: 7/24', '| A | authentication | Web interface | conditional | explicit |']:
                self.assertIn(expected, text)
            self.assertEqual(text.count('| v | A | unknown |'), 2)
            self.assertEqual(len((p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()), 6)
            self.assertEqual({(x['interface'], x['interface_class'], x['source_ref']) for x in load(p/'report'/'evidence_index.json')},
                             {('DNP3 server','control_protocol','S1'), ('Web interface','management','S1'), ('Web interface','management','S2')})

    def test_source_notes_complete_the_source_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); src = self.reviewed_run(p)
            notes = load(p/'run'/'source_notes_template.json')
            notes[0].update(doc_type='manual', document_id='LWP0018-01', revision='', document_date='2016-01-11', note='date code 20160111')
            dump(p/'notes.json', notes[:1])
            report(p/'run', p/'reviews.json', p/'report', source_notes=p/'notes.json')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn(f"| S1 | A | untitled | manual | LWP0018-01 | 2016-01-11 | 2026-10-13 | {src['a']['sha256']} "
                          f"| https://vendor.test/a |", text)
            self.assertIn(f"| S2 | B | untitled | suggested: product page | not established | not established | "
                          f"2026-10-13 | {src['b']['sha256']} | https://vendor.test/b |", text)
            exported = load(p/'report'/'sources.json')
            self.assertEqual((exported[0]['ref'], exported[0]['document']['document_id'], exported[1]['document']['document_id']), ('S1','LWP0018-01',''))
            self.assertIn('S1 [manual] html-block:1: "TLS is supported for DNP3 sessions."', text)
            self.assertIn('S2 [type not confirmed] html-block:1:', text)
            self.assertIn('- Source: S1 [manual] https://vendor.test/a', text)
            self.assertEqual({x['doc_type'] for x in load(p/'report'/'evidence_index.json') if x['source_ref'] == 'S1'}, {'manual'})
            dump(p/'notes.json', [dict(notes[0], source_id='nope')])
            with self.assertRaisesRegex(ValueError,'not in this run'): report(p/'run', p/'reviews.json', p/'report', source_notes=p/'notes.json')
            dump(p/'notes.json', [dict(notes[0], doc_type='white paper')])
            with self.assertRaisesRegex(ValueError,'doc_type outside'): report(p/'run', p/'reviews.json', p/'report', source_notes=p/'notes.json')

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
            with self.site(pages, []): crawl(cfg, p/'run', p/'cache')
            src = {x['product_id']: x for x in load(p/'run'/'sources.json')}
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
                dump(p/'reviews.json', rows); dump(p/'notes.json', notes)
                report(p/'run', p/'reviews.json', p/'report', require_evidence=True, source_notes=p/'notes.json')
            for notes in ([], [note('old','product_page','complete')], [note('old','manual','partial')], [note('old','manual','')]):
                with self.subTest(notes=notes), self.assertRaisesRegex(ValueError,'complete_document_silent needs a complete'): run(silent, notes)
            with self.assertRaisesRegex(ValueError,'1 leads for tls exist'):
                run([row('new','tls','unknown', unknown_reason='complete_document_silent')], [note('new','manual','complete')])
            with self.assertRaisesRegex(ValueError,'coverage must be'): run(silent, [note('old','manual','whole')])
            run(silent + [claim], [note('old','manual','complete')])
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in [
                '## Definitions', 'Fixed on 2026-10-13 in the config this run was crawled with, before any result was '
                                  'counted.',
                '- Legacy: Legacy means the vendor states that support has ended.', '- End of support: The vendor states that support has ended.',
                'Legacy under this definition: 1 of 3 devices in this run. Lifecycle status rests on dated vendor '
                'evidence for 2 devices and is unknown for 1.',
                '| v | OLD | relay | not established | end of support | 1 March 2020: "Support for the OLD relay ended '
                'on 1 March 2020." <https://vendor.test/lifecycle> | not established |',
                '| v | NEW | relay | not established | currently listed | 2026-10-01: listed in the vendor catalogue '
                '<https://vendor.test/lifecycle> | not established |',
                '| v | UNK | relay | not established | unknown | none | not established |',
                '| v | OLD | end of support | model not assessed, hardware not assessed, firmware all versions covered '
                'by manual rev C | DNP3 serial and Ethernet (control protocol) | '
                'not assessed; see tls (unknown: complete document silent) | not assessed; see tls (unknown: complete '
                'document silent) | '
                'unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | '
                'S1 [manual] searched in full: no lead for encryption; S1 [manual] searched in full: no lead for tls | '
                'draft (A. Reviewer) |',
                '| v | NEW | currently listed | model not assessed, hardware not assessed, firmware all versions '
                'covered by manual rev C | DNP3 serial and Ethernet (control protocol) | not assessed; see tls '
                '(supported) |',
                '| v | UNK | unknown | not established | No control protocol established from the examined sources |',
                '| OLD | relay, end of support | - | ?s | - | - | - | ?s | - | - |', '| NEW | relay, currently listed | - | S | - | - | - | - | - | - |',
                # The same four results are counted for the legacy device and the current one; silence is unknown, not unsupported.
                '| relay, end of support | tls | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |', '| relay, currently listed | tls | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |',
                '| relay, unknown | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |', '| relay, end of support | encryption | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |',
                '| v | relay | end of support | - | 1 | 1 not reviewed | 1 not reviewed | 1 unknown: complete document '
                'silent |',
                '## Counts by category and lifecycle group', 'The same results are counted for every lifecycle group.',
                '### OLD: tls (unknown: complete document silent)', '- Searched: S1 [manual] searched in full: no lead for tls', '| manual, complete |',
                '| OLD | tls | DNP3 serial and Ethernet | unknown: complete document silent | searched in full |',
                'Evidence quotes: 1 of 1 rows', 'Unknown because a complete document is silent: 2 rows', '?s a complete document was searched and is silent',
                '23 of 24 cells are unknown or not reviewed on every interface.']:
                self.assertIn(expected, text)
            table = (p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()
            self.assertIn('end of support', table[1].split(',')[2])
            self.assertIn('searched in full: no lead for tls', table[1])
            self.assertEqual({(r['status'], r['unknown_reason']) for r in load(p/'report'/'findings.json') if r['product_id'] == 'old'}, {('unknown', 'complete_document_silent')})

    def test_worksheet_lays_out_leads_and_proposes_no_result(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<title>A relay</title><p>TLS 1.2 is supported. TLS is not used for Modbus.</p>'
                                              b'<p>TLS is disabled by default and requires a certificate.</p>'}
            ended = [{'url':'https://vendor.test/eol','retrieved_at':'2026-10-01T00:00:00+00:00','quote':'Support for the A relay ended on 1 March 2020.','stated_date':'1 March 2020'}]
            cfg = self.config(p, [{'id':'a','lifecycle':'end_of_support','lifecycle_evidence':ended,'seeds':['https://vendor.test/a','https://vendor.test/gone']},{'id':'b','seeds':[]}])
            with self.site(pages, calls): crawl(cfg, p/'run', p/'cache')
            worksheet(p/'run', p/'sheet')
            text = (p/'sheet'/'worksheet.md').read_text(encoding='utf-8')
            for expected in ['## A', 'v; relay; lifecycle end of support; id `a`',
                             '- lifecycle evidence, 1 March 2020: "Support for the A relay ended on 1 March 2020." '
                             '<https://vendor.test/eol>',
                             '- S1 extracted, product page (suggested) <https://vendor.test/a>', '- -- failed: ValueError: HTTP 404 <https://vendor.test/gone>',
                             '- **tls**: 2 leads: S1 html-block:2 [TLS 1.2, TLS]; S1 html-block:3 [TLS]',
                             '  - default wording: S1 html-block:3 [TLS is disabled by default]',
                             '  - requirement wording: S1 html-block:3 [TLS is disabled by default and requires]',
                             '- **ssh**: no lead in S1', '- **non_support_statement**: 1 leads: S1 html-block:2 [TLS is not used]',
                             '## B', 'v; relay; lifecycle not recorded; id `b`', '- no source', '- **tls**: no lead', 'not a finding']:
                self.assertIn(expected, text)
            rows = load(p/'sheet'/'review_template.json')
            self.assertEqual(rows[1]['_hints'], {'leads': 2, 'where': ['S1 html-block:2', 'S1 html-block:3'], 'no_lead_in': [],
                                                 'default_wording': ['S1 html-block:3'], 'requirement_wording': ['S1 html-block:3']})
            self.assertEqual(rows[6]['_hints'], {'leads': 0, 'where': [], 'no_lead_in': ['S1'], 'default_wording': [], 'requirement_wording': []})
            # The wording about TLS is not offered as wording about SSH.
            self.assertNotIn('- **ssh**: no lead in S1\n  - default wording', text)
            self.assertTrue(all(map(untouched, rows)))
            report(p/'run', p/'sheet'/'review_template.json', p/'report')
            self.assertIn('Review coverage: 0/16', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError): worksheet(p/'run', p/'sheet')

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
            with self.site({}, []): crawl(cfg, p/'run', p/'cache')
            report(p/'run', p/'run'/'review_template.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['## Summary by vendor, category and lifecycle', '| v | relay | currently listed | 80 | 20 | 20 not reviewed | 20 not reviewed | 20 not reviewed |',
                             '| v | relay | discontinued, support not stated | 40 | 10 | 10 not reviewed | 10 not '
                             'reviewed | 10 not reviewed |',
                             '| v | meter | currently listed | 9 | 0 | - | - | - |', '30 products have no review row yet.',
                             # Discontinued is not legacy: none of the thirty has a vendor statement that support ended.
                             'Legacy under this definition: 0 of 30 devices in this run. Lifecycle status rests on '
                             'dated vendor evidence for 30 devices and is unknown for 0.',
                             '30 devices without a review row are left out of this table. devices.csv lists all 30 with '
                             'their lifecycle evidence.']:
                self.assertIn(expected, text)
            self.assertNotIn('No control protocol established', text)
            self.assertEqual(len((p/'report'/'findings_table.csv').read_text(encoding='utf-8').splitlines()), 31)
            devices = (p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual((len(devices), devices[2]), (31, 'r1,v,R1,relay,,discontinued_support_not_stated,no,,2026-10-13,Manufacturing for this product has been discontinued.,https://vendor.test/r,,,'))
            # The matrix and the unresolved list count the unreviewed devices too, without a line for each.
            self.assertIn('30 products without a review row are left out', text)
            self.assertIn('240 of 240 cells are unknown or not reviewed on every interface.', text)
            self.assertIn('This includes all 240 cells of the 30 products without a review row', text)
            self.assertNotIn(' | - | - | - | - | - | - | - | - |', text)
            self.assertNotIn(': dnp3_secure_authentication, tls, ipsec', text)
            # Without definitions in the config the run was crawled with, nothing is counted by lifecycle group.
            cfg = self.config(p, products, frame=frame)
            with self.site({}, []): crawl(cfg, p/'run2', p/'cache')
            report(p/'run2', p/'run2'/'review_template.json', p/'report2')
            text = (p/'report2'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['No definition of "legacy" or of the lifecycle groups is recorded in the config of this '
                             'run, so no result is counted by lifecycle group.',
                             '## Summary by vendor and category', '| v | relay | - | 120 | 30 | 30 not reviewed | 30 not reviewed | 30 not reviewed |', '| v | meter | - | 9 | 0 | - | - | - |',
                             '## Counts by category', '| relay | tls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 30 |']:
                self.assertIn(expected, text)
            for absent in ['## Definitions', 'Legacy under this definition', '## Counts by category and lifecycle group', 'relay, currently listed']:
                self.assertNotIn(absent, text)

    def test_report_counts_unread_sources_by_vendor_once_there_are_too_many_to_list(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/gated': ValueError('login required: redirected to https://vendor.test/login?next=x')}
            cfg = self.config(p, [{'id': f'r{i}', 'seeds': [f'https://vendor.test/missing{i}', 'https://vendor.test/gated']} for i in range(21)])
            with self.site(pages, []): crawl(cfg, p/'run', p/'cache')
            report(p/'run', p/'run'/'review_template.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn('Sources attempted: 21; extracted: 0; failed: 21; documents behind a sign-in, not requested: '
                          '21.', text)
            self.assertIn('| v | ValueError: HTTP 404 | 21 |', text)
            self.assertIn('| v | behind a sign-in, not requested | 21 |', text)
            self.assertNotIn('https://vendor.test/missing3 ', text)

    def test_report_keeps_gateway_only_capability_and_field_evidence_apart(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            rows = load(p/'reviews.json')
            field = {'kind':'utility configuration audit', 'reference':'Audit report 2025-07', 'date':'2025-07-14', 'scope':'12 relays at one substation'}
            rows[0].update(deployment_status='disabled', deployment_evidence=[field], default_state='disabled', model_scope='A-100', hardware_revision='rev C',
                           activation_needs=['configuration', 'certificates_or_keys'], activation_requirements='enable TLS and load a certificate')
            rows[1].update(status='conditional', conditions='needs an external encrypting gateway', support_basis=['external_gateway'], review_status='draft')
            dump(p/'reviews.json', rows)
            report(p/'run', p/'reviews.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['| A | relay | - | S | - | - | (C) | G | ? | - |',
                             '| relay | encryption | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |', '| relay | tls | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |',
                             '| v | relay | - | - | 2 | 2 unknown: other interface only | 2 not reviewed | 1 via '
                             'external gateway only, 1 unknown |',
                             'conditional: external gateway only: encryption detail',
                             '| tls: model A-100, hardware rev C, firmware v2 or later; encryption: model not '
                             'established, hardware not established, firmware v2 or later |',
                             'built in; external gateway: needs an external encrypting gateway',
                             'tls: disabled; encryption: undocumented', 'tls: configuration, certificates or keys: enable TLS and load a certificate; encryption: none stated',
                             'disabled (utility configuration audit, 2025-07-14); unknown',
                             'Deployment status is unknown for 3 of 4 findings.',
                             '- A, tls on DNP3 server: disabled (utility configuration audit, Audit report 2025-07, '
                             '2025-07-14, 12 relays at one substation)',
                             '| tls | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |', '### A: encryption (conditional: external gateway only)', '- Support basis: external gateway']:
                self.assertIn(expected, text)
            found = {(r['feature'], r['interface']): r for r in load(p/'report'/'findings.json')}
            self.assertEqual(token(found['encryption', 'DNP3 server']), 'gateway')
            csv_row = next(line for line in (p/'report'/'findings.csv').read_text(encoding='utf-8').splitlines() if line.startswith('a,v,A,relay,unknown,tls,supported,'))
            for part in [',A-100,rev C,v2 or later,', ',built_in,', ',disabled,configuration | certificates_or_keys,enable TLS and load a certificate,disabled,']:
                self.assertIn(part, csv_row)

    def test_device_notes_state_identity_and_lifecycle_only_with_dated_vendor_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/a': b'<p>Support for the A relay ended on 1 March 2020.</p>'}
            cfg = self.config(p, [{'id':'a','seeds':list(pages)}, {'id':'b','seeds':[]}], definitions=self.DEFINITIONS)
            with self.site(pages, []): crawl(cfg, p/'run', p/'cache')
            source = load(p/'run'/'sources.json')[0]
            notes = load(p/'run'/'device_notes_template.json')
            self.assertEqual([(n['product_id'], n['manufacturer'], n['model'], n['identity_level'], n['lifecycle_status'], n['lifecycle_evidence'], n['release_date']) for n in notes],
                             [('a','v','A','','unknown',[],''), ('b','v','B','','unknown',[],'')])
            quote = {'source_id': source['id'], 'location': 'html-block:1', 'quote': 'Support for the A relay ended on 1 March 2020.', 'stated_date': '1 March 2020'}
            def run(**change):
                dump(p/'devices.json', [dict(notes[0], **change)])
                report(p/'run', p/'run'/'review_template.json', p/'report', device_notes=p/'devices.json')
                return (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            text = run(identity_level='model', lifecycle_status='end_of_support', lifecycle_evidence=[quote], release_date='2009', noted_by='A. Reviewer',
                       release_evidence=[{'url':'https://vendor.test/history', 'retrieved_at':'2026-10-13T00:00:00+00:00'}])
            for expected in ['Legacy under this definition: 1 of 2 devices in this run.',
                             '| v | A | relay | model | end of support | 1 March 2020: "Support for the A relay ended '
                             'on 1 March 2020." <https://vendor.test/a> | 2009 |',
                             '| v | B | relay | not established | unknown | none | not established |']:
                self.assertIn(expected, text)
            self.assertEqual((p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()[1],
                             f"a,v,A,relay,model,end_of_support,yes,,1 March 2020,Support for the A relay ended on 1 "
                             f"March 2020.,https://vendor.test/a,{source['sha256']},2009,A. Reviewer")
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
            with self.site({}, []): crawl(cfg, p/'run2', p/'cache')
            self.assertIn('a: lifecycle "end_of_support" has no lifecycle_evidence; the report will refuse it', load(p/'run2'/'manifest.json')['config_warnings'])
            with self.assertRaisesRegex(ValueError,'needs dated vendor evidence'): report(p/'run2', p/'run2'/'review_template.json', p/'report2')
            # A label from before 1.6.0 is shown as the label it was and counted as unknown.
            cfg = self.config(p, [{'id':'a','lifecycle':'legacy','seeds':[]}], definitions=self.DEFINITIONS)
            with self.site({}, []): crawl(cfg, p/'run3', p/'cache')
            report(p/'run3', p/'run3'/'review_template.json', p/'report3')
            text = (p/'report3'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn('| v | A | relay | not established | unknown (vendor label: legacy (label used before 1.6.0)) '
                          '| none | not established |', text)
            self.assertIn('Legacy under this definition: 0 of 1 devices in this run.', text)

    def test_a_review_written_before_1_6_still_reports_with_the_new_facts_not_assessed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); src = self.reviewed_run(p)
            rows = load(p/'reviews.json')
            for r in rows:
                for key in ('model_scope', 'hardware_revision', 'support_basis', 'default_state', 'activation_needs'): r.pop(key, None)
                r['review_status'] = 'draft'
            rows[4].update(status='conflicting', interface='Engineering access', interface_class='management', protocol='SSH', location='html-block:1')
            dump(p/'reviews.json', rows)
            report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in ['| v | A | unknown | model not assessed, hardware not assessed, firmware v2 or later | '
                             'DNP3 server (control protocol) |',
                             '| supported: encryption detail | not assessed | not assessed | not assessed | unknown |',
                             '| A | relay | - | S | - | - | (C) | S | (?c) | - |', '| A | ssh | Engineering access | unknown: sources conflict | explicit |',
                             '### A: ssh (unknown: sources conflict)', '| tls | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |']:
                self.assertIn(expected, text)
            self.assertEqual({r['status'] for r in load(p/'report'/'findings.json')} - set(STATUSES), set())

    def test_legacy_covers_the_lifecycle_states_the_definitions_name_and_a_revision_is_stated(self):
        wide = dict(self.DEFINITIONS, legacy='Legacy means the vendor has discontinued the device.',
                    legacy_statuses=['end_of_support', 'discontinued_support_not_stated', 'discontinued_supported'],
                    revisions=[{'date': '2026-10-13', 'change': 'Legacy widened from end of support to every discontinued device.',
                                'known_then': 'A first draft had been counted and placed no device in the legacy group.'}])
        # Whatever order the config lists them in, the states are used in lifecycle order. Words alone mean end of support.
        self.assertEqual(legacy_states(wide), ('discontinued_supported', 'discontinued_support_not_stated', 'end_of_support'))
        self.assertEqual((legacy_states(self.DEFINITIONS), legacy_states(None), legacy_states({'defined_at': '2026-10-13'})), (('end_of_support',), (), ()))
        base = {'sampling': 'x', 'products': [{'id': 'p', 'domains': ['vendor.test'], 'seeds': []}]}
        # A device on sale, or one whose state nobody established, is legacy under no definition; a revision says what was known.
        for change in ({'legacy_statuses': ['unknown']}, {'legacy_statuses': ['currently_supported', 'end_of_support']}, {'legacy_statuses': []},
                       {'legacy_statuses': 'end_of_support'}, {'legacy': ''}, {'revisions': [{'date': '2026-10-13', 'change': 'Widened.'}]},
                       {'revisions': ['widened']}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'definitions: '):
                validate_config(dict(base, definitions=dict(wide, **change)))
        with self.assertRaisesRegex(ValueError, 'definitions: legacy_statuses'):
            check_rules({'definitions': {'legacy_statuses': ['end_of_support']}, 'vendors': {}})
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
            with self.site(pages, []): crawl(cfg, p/'run', p/'cache')
            src = {x['product_id']: x for x in load(p/'run'/'sources.json')}
            def row(pid, feature, status, **more):
                base = {'product_id': pid, 'feature': feature, 'status': status, 'source_ids': [src[pid]['id']], 'source_hashes': {src[pid]['id']: src[pid]['sha256']},
                        'location': '', 'protocol': '', 'interface': 'DNP3 serial and Ethernet', 'interface_class': 'control_protocol', 'firmware': 'all versions',
                        'implementation': '', 'conditions': '', 'evidence': [], 'rationale': 'searched in full', 'reviewer': 'A. Reviewer', 'reviewed_at': '2026-10-13'}
                return dict(base, **more)
            dump(p/'reviews.json', [row('old', 'encryption', 'unknown', unknown_reason='complete_document_silent'),
                                      row('new', 'tls', 'supported', location='html-block:1', protocol='DNP3 over TLS', implementation='native',
                                          evidence=[{'source_id': src['new']['id'], 'location': 'html-block:1', 'quote': 'TLS is supported for DNP3 sessions.'}])])
            dump(p/'notes.json', [{'source_id': src['old']['id'], 'doc_type': 'manual', 'coverage': 'complete'}])
            report(p/'run', p/'reviews.json', p/'report', require_evidence=True, source_notes=p/'notes.json')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            for expected in [
                'First fixed on 2026-10-13 and revised since. What follows is the definition in the config this run was '
                'crawled with; each revision is listed with what had been counted when it was made.',
                '- Legacy: Legacy means the vendor has discontinued the device.',
                '- Counted as legacy: discontinued, still supported; discontinued, support not stated; end of support.',
                '- Revised on 2026-10-13: Legacy widened from end of support to every discontinued device. What had '
                'been counted by then: A first draft had been counted and placed no device in the legacy group.',
                'Legacy under this definition: 1 of 3 devices in this run.',
                # The counts further down stay by lifecycle state, so the group can always be taken apart again.
                '| relay, discontinued, support not stated | encryption | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |']:
                self.assertIn(expected, text)
            self.assertNotIn('before any result was counted', text)
            self.assertEqual([line.split(',')[5:7] for line in (p/'report'/'devices.csv').read_text(encoding='utf-8').splitlines()],
                             [['lifecycle_status', 'legacy'], ['discontinued_support_not_stated', 'yes'], ['currently_supported', 'no'], ['unknown', 'unknown']])


    def test_dnp3_security_is_shown_by_lifecycle_group_with_vendor_model_type_and_source(self):
        wide = dict(self.DEFINITIONS, legacy='Legacy means the vendor has discontinued the device.',
                    legacy_statuses=['discontinued_supported', 'discontinued_support_not_stated', 'end_of_support'])
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            pages = {'https://vendor.test/tls': b'<p>DNP3 over TLS is supported on the master station link.</p>',
                     'https://vendor.test/sa': b'<p>DNP3 Secure Authentication version 5 is supported by the outstation.</p>',
                     'https://vendor.test/plain': b'<p>Protocols: DNP3 serial and DNP3 LAN/WAN, Modbus.</p>',
                     'https://vendor.test/old': b'<p>The relay speaks DNP3 over serial links.</p>',
                     'https://vendor.test/family': b'<p>Other members of this family offer DNP3 gateways.</p>',
                     'https://vendor.test/modbus': b'<p>Modbus RTU only.</p>'}
            listed = [{'url': 'https://vendor.test/catalogue', 'retrieved_at': '2026-10-13T00:00:00+00:00', 'basis': 'listed in the vendor catalogue'}]
            gone = [{'url': 'https://vendor.test/old', 'retrieved_at': '2026-10-13T00:00:00+00:00', 'quote': 'Manufacturing of this relay has ended.'}]
            current = {'lifecycle': 'currently_supported', 'lifecycle_evidence': listed}
            cfg = self.config(p, [dict(current, id=k, seeds=[f'https://vendor.test/{k}']) for k in ('tls', 'sa', 'plain', 'family', 'modbus')]
                              + [{'id': 'old', 'lifecycle': 'discontinued_support_not_stated', 'lifecycle_evidence': gone, 'seeds': ['https://vendor.test/old']}],
                              definitions=wide)
            with self.site(pages, []): crawl(cfg, p/'run', p/'cache')
            src = {x['product_id']: x for x in load(p/'run'/'sources.json')}
            def row(pid, feature, interface, protocol, quote):
                s = src[pid]
                return {'product_id': pid, 'feature': feature, 'status': 'supported', 'source_ids': [s['id']], 'source_hashes': {s['id']: s['sha256']},
                        'location': 'html-block:1', 'protocol': protocol, 'interface': interface, 'interface_class': 'control_protocol',
                        'firmware': 'not established', 'implementation': 'built in', 'evidence': [{'source_id': s['id'], 'location': 'html-block:1', 'quote': quote}],
                        'rationale': 'stated', 'reviewer': 'A. Reviewer', 'reviewed_at': '2026-10-14'}
            dump(p/'reviews.json', [row('tls', 'tls', 'DNP3 to SCADA master', 'DNP3 over TLS', 'DNP3 over TLS is supported on the master station link.'),
                                    row('sa', 'dnp3_secure_authentication', 'DNP3 outstation', 'DNP3-SAv5',
                                        'DNP3 Secure Authentication version 5 is supported by the outstation.')])
            notes = load(p/'run'/'device_notes_template.json')
            for n in notes:
                if n['product_id'] == 'family':
                    n.update(dnp3='not_established', dnp3_note='The page names DNP3 only for other products of the family.')
            dump(p/'notes.json', notes)
            # A correction needs a reason, and only the three values exist.
            for bad in ({'dnp3': 'maybe', 'dnp3_note': 'x'}, {'dnp3': 'not_established', 'dnp3_note': ''}):
                dump(p/'bad.json', [dict(notes[0], **bad)])
                with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'dnp3'):
                    report(p/'run', p/'reviews.json', p/'bad_report', device_notes=p/'bad.json')
            report(p/'run', p/'reviews.json', p/'report', require_evidence=True, device_notes=p/'notes.json')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            section = text[text.index('## DNP3 security'):text.index('## Devices')]
            for expected in [
                'Left out by the device notes, because DNP3 is named only in documents about other products: FAMILY.',
                '| DNP3 security documented | Currently listed | Legacy | Total |',
                '| DNP3 over TLS or IPsec documented | 1 of 3 (33%) | 0 of 1 (0%) | 1 of 4 (25%) |',
                '| DNP3 authentication documented; encryption not established | 1 of 3 (33%) | 0 of 1 (0%) | 1 of 4 (25%) |',
                '| DNP3 security not established from retrieved documents | 1 of 3 (33%) | 1 of 1 (100%) | 2 of 4 (50%) |',
                '| Devices whose documents name DNP3 | 3 | 1 | 4 |',
                '| Legacy | Lifecycle | Vendor | Model | Type | DNP3 security | Source |',
                '| no | currently listed | v | TLS | relay | DNP3 over TLS or IPsec documented | [S1 html-block:1](https://vendor.test/tls) |',
                '| no | currently listed | v | SA | relay | DNP3 authentication documented; encryption not established | [S2 html-block:1](https://vendor.test/sa) |',
                '| no | currently listed | v | PLAIN | relay | DNP3 security not established from retrieved documents | [S3](https://vendor.test/plain) |',
                '| yes | discontinued, support not stated | v | OLD | relay | DNP3 security not established from retrieved documents | [S6](https://vendor.test/old) |']:
                self.assertIn(expected, section)
            # Devices whose documents never name DNP3, and those a note leaves out, are not counted at all.
            self.assertNotIn('| MODBUS |', section)
            self.assertNotIn('| FAMILY |', section)
            lines = (p/'report'/'dnp3.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual(lines[0], 'product_id,vendor,model,type,lifecycle_status,legacy,dnp3_security,dnp3_security_label,evidence_quote,'
                                       'source_refs,source_locations,source_urls')
            self.assertEqual(sorted((x.split(',')[0], x.split(',')[5], x.split(',')[6]) for x in lines[1:]),
                             [('old', 'yes', 'none'), ('plain', 'no', 'none'), ('sa', 'no', 'authenticated'), ('tls', 'no', 'tls')])

if __name__ == '__main__':
    unittest.main()

"""The paper command: the DNP3 table read from the interface table, counts from the inputs, a receipt for every output."""
import csv
from pathlib import Path
import tempfile
import unittest

from iedsurvey.crawl import crawl
from iedsurvey.findings import Findings
from iedsurvey.paper import PAPER_FILES, paper, paragraph
from iedsurvey.report import report_manifest
from iedsurvey.store import digest, dump, load
from support import SurveyCase


class PaperTests(SurveyCase):
    def test_default_rendering_uses_the_reviewed_state_instead_of_a_word_in_the_quote(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            self.fixture(p)
            found = Findings(p / 'run', p / 'reviews.json', True)
            # Unit-test rendering of an enabled default whose wording also describes a disabled choice.
            row = next(r for r in found.claims if r['product_id'] == 'sa')
            row['default_state'] = 'enabled'
            next(e for e in row['evidence'] if e.get('about') == 'default')['quote'] = (
                'The feature can be Disabled or Enabled. Default value is Enabled.')
            text = '\n'.join(paragraph(found, 'AI draft; author review pending'))
            self.assertNotIn('is disabled by default', text)
            self.assertIn('1 entry documents a default', text)

    def test_paragraph_retains_unknown_encryption_and_external_protocol_scope(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            self.fixture(p)
            found = Findings(p / 'run', p / 'reviews.json', True)
            text = '\n'.join(paragraph(found, 'AI draft; author review pending'))
            self.assertIn('DNP3 authentication documented; encryption not established', text)
            self.assertIn('External encryption documented; DNP3 scope not established', text)
            self.assertNotIn('authentication without encryption', text)
            self.assertNotIn('but not of DNP3 itself', text)
    PAGES = {'https://vendor.test/tls': b'<p>DNP3 over TLS is supported on the master station link.</p>',
             'https://vendor.test/sa': b'<p>DNP3 Secure Authentication version 5 is supported by the outstation.</p>'
                                       b'<p>Enable Secure Authentication. Default value is Disabled.</p>',
             'https://vendor.test/plain': b'<p>Protocols: DNP3 serial and DNP3 LAN/WAN, Modbus.</p>',
             'https://vendor.test/web': b'<p>Protocols: DNP3 LAN/WAN.</p><p>The web server supports HTTPS.</p>',
             'https://vendor.test/gate': b'<p>DNP3 serial.</p><p>A separate encrypting transceiver protects serial SCADA links.</p>'}

    def fixture(self, p):
        listed = [{'url': 'https://vendor.test/catalogue', 'retrieved_at': '2026-10-13T00:00:00+00:00', 'basis': 'listed in the vendor catalogue'}]
        cfg = self.config(p, [{'id': k, 'lifecycle': 'currently_supported', 'lifecycle_evidence': listed, 'seeds': [f'https://vendor.test/{k}']}
                              for k in ('tls', 'sa', 'plain', 'web', 'gate')], definitions=self.DEFINITIONS)
        with self.site(self.PAGES, []): crawl(cfg, p/'run', p/'cache')
        src = {x['product_id']: x for x in load(p/'run'/'sources.json')}

        def row(pid, feature, interface, protocol, quotes, kind='control_protocol', **extra):
            s = src[pid]
            return dict({'product_id': pid, 'feature': feature, 'status': 'supported', 'source_ids': [s['id']],
                         'source_hashes': {s['id']: s['sha256']}, 'location': 'html-block:1', 'protocol': protocol,
                         'interface': interface, 'interface_class': kind, 'firmware': 'not established', 'implementation': 'built in',
                         'support_basis': ['built_in'],
                         'evidence': [{'source_id': s['id'], 'location': where, 'quote': q, **({'about': a} if a else {})}
                                      for where, q, a in quotes],
                         'rationale': 'stated', 'reviewer': 'AI draft', 'reviewed_at': '2026-10-15', 'review_status': 'draft'}, **extra)
        dump(p/'reviews.json', [
            row('tls', 'tls', 'DNP3 to SCADA master', 'DNP3 over TLS',
                [('html-block:1', 'DNP3 over TLS is supported on the master station link.', None)]),
            row('sa', 'dnp3_secure_authentication', 'DNP3 outstation', 'DNP3-SAv5',
                [('html-block:1', 'DNP3 Secure Authentication version 5 is supported by the outstation.', None),
                 ('html-block:2', 'Default value is Disabled.', 'default')], default_state='disabled'),
            row('web', 'tls', 'Web server', 'HTTPS', [('html-block:2', 'The web server supports HTTPS.', None)], kind='management'),
            row('gate', 'encryption', 'Serial SCADA link', 'separate encrypting transceiver',
                [('html-block:2', 'A separate encrypting transceiver protects serial SCADA links.', None),
                 ('html-block:2', 'A separate encrypting transceiver protects serial SCADA links.', 'conditions')],
                status='conditional', support_basis=['external_gateway'], conditions='a separate encrypting transceiver')])

    def test_dnp3_table_is_read_from_the_interface_table_and_keeps_other_interfaces_apart(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.fixture(p)
            found = Findings(p/'run', p/'reviews.json', True)
            lines = {pid: found.dnp3_lines(pid) for pid in found.dnp3}
            self.assertEqual(sorted(lines), ['gate', 'plain', 'sa', 'tls', 'web'])
            tls, sa = lines['tls'][0], lines['sa'][0]
            # The same cells as the interface table, not a second reading of the review: a TLS finding is a mechanism and
            # is pointed to, not counted as the encryption property, until a reviewer records that property.
            self.assertEqual({k: tls[k] for k in ('Encryption', 'Scope', 'Lifecycle')},
                             {'Encryption': 'not assessed; see tls (supported)', 'Scope': 'control protocol, built in',
                              'Lifecycle': 'currently listed'})
            self.assertIn(tls['Encryption'], [t['Encryption'] for t in found.table if t['pid'] == 'tls'])
            self.assertEqual((sa['Default'], sa['DNP3 summary']), ('disabled', 'DNP3 authentication documented; encryption not established'))
            self.assertFalse(sa['Encryption'].startswith('supported'))
            # Management HTTPS and a separate device for unnamed SCADA links are listed apart, never as DNP3 protection.
            web, gate = lines['web'][0], lines['gate'][0]
            self.assertEqual((web['Authentication'], web['Encryption'], web['DNP3 summary']),
                             ('not established', 'not established', 'DNP3 security not established from retrieved documents'))
            self.assertEqual(web['Security documented for other interfaces'], 'Web server (management): management, built in')
            self.assertEqual((gate['Encryption'], gate['DNP3 summary']),
                             ('not established', 'External encryption documented; DNP3 scope not established'))
            self.assertIn('control protocol, separate device', gate['Security documented for other interfaces'])

    def test_paper_counts_from_its_inputs_marks_drafts_and_its_receipt_covers_every_output(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.fixture(p)
            paper(p/'run', p/'reviews.json', p/'paper')
            written = sorted(x.name for x in (p/'paper').iterdir())
            self.assertEqual(written, sorted(PAPER_FILES + ('paper_manifest.json',)))
            receipt = load(p/'paper'/'paper_manifest.json')
            self.assertEqual(receipt['outputs'], {n: digest((p/'paper'/n).read_bytes()) for n in PAPER_FILES})
            self.assertEqual((receipt['schema_version'], receipt['acceptance']['require_confirmed'], receipt['acceptance']['draft_rows']),
                             ('iedsurvey.paper.v1', False, 4))
            summary = (p/'paper'/'summary.md').read_text(encoding='utf-8')
            self.assertIn('Status: **AI draft; author review pending**', summary)
            # The separate-device entry has a finding, if not a DNP3-specific one; only the two without any are unresolved.
            self.assertIn('2 of 5 DNP3 entries have no established DNP3 security finding', summary)
            self.assertIn('| v | TLS | currently listed | no | ' + 'not assessed; see tls (supported) | ' * 3, summary)
            paragraph = (p/'paper'/'paragraph.tex').read_text(encoding='utf-8')
            for expected in ['Of the 5 entries whose documents name DNP3, the documented findings are '
                             '1 (DNP3 over TLS or IPsec documented); '
                             '1 (DNP3 authentication documented; encryption not established); '
                             '1 (External encryption documented; DNP3 scope not established). For the remaining 2,',
                             'states that DNP3 Secure Authentication is disabled by default', 'Status: AI draft; author review pending']:
                self.assertIn(expected, paragraph)
            appendix = (p/'paper'/'paper_appendix.tex').read_text(encoding='utf-8')
            self.assertIn(r'\label{tab:crawler-dnp3-entries}', appendix)
            # Compact cells: a TLS finding is shown as the mechanism, the separate device under the other protocol.
            self.assertIn(r'v & relay & TLS & listed & via TLS & via TLS & via TLS & built in & E1 \\', appendix)
            self.assertIn(r'v & relay & GATE & listed & -- & -- & -- & -- & other protocol: Serial SCADA link \\', appendix)
            self.assertIn(r'\item[E1] ``DNP3 over TLS is supported on the master station link.', appendix)
            self.assertIn(r"rows are an AI-assisted draft", appendix)
            rows = list(csv.DictReader((p/'paper'/'dnp3_table.csv').open(encoding='utf-8')))
            self.assertEqual(sorted(r['product_id'] for r in rows), ['gate', 'plain', 'sa', 'tls', 'web'])
            # The same inputs give the same outputs; only the receipt's time differs.
            paper(p/'run', p/'reviews.json', p/'again')
            self.assertEqual({n: (p/'again'/n).read_bytes() for n in PAPER_FILES}, {n: (p/'paper'/n).read_bytes() for n in PAPER_FILES})
            with self.assertRaises(FileExistsError):
                paper(p/'run', p/'reviews.json', p/'paper')

    def test_paper_refuses_publication_while_rows_are_drafts_and_a_receipt_refuses_a_missing_output(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.fixture(p)
            with self.assertRaisesRegex(ValueError, 'requires confirmed review'):
                paper(p/'run', p/'reviews.json', p/'final', require_confirmed=True)
            self.assertFalse((p/'final').exists())
            found = Findings(p/'run', p/'reviews.json', True)
            (p/'out').mkdir(); (p/'out'/'summary.md').write_text('x', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'expected output not written: paper_appendix.tex'):
                report_manifest(found, p/'reviews.json', None, None, p/'out', ('summary.md', 'paper_appendix.tex'), True, False)
            self.assertFalse((p/'out'/'report_manifest.json').exists())


if __name__ == '__main__':
    unittest.main()

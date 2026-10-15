"""Keep the evidence boundary when a DNP3 summary is derived from reviewed rows."""
import unittest
from iedsurvey.findings import Findings, DNP3_KINDS

class DocumentedScopeTests(unittest.TestCase):
    def result(self, rows):
        f = Findings.__new__(Findings)
        f.claims = rows
        key, evidence = f.dnp3_security('p')
        return key, dict(DNP3_KINDS)[key], evidence

    def row(self, feature, protocol='DNP3', status='supported', interface='DNP3 server', basis=None):
        return dict(product_id='p', interface_class='control_protocol', feature=feature, protocol=protocol,
                    interface=interface, status=status, support_basis=basis or ['built_in'])

    def test_no_security_evidence_does_not_assert_plaintext(self):
        key, label, _ = self.result([])
        self.assertEqual(key, 'none')
        self.assertNotIn('plaintext', label.lower())
        self.assertIn('not established', label.lower())

    def test_integrity_alone_does_not_prove_authentication(self):
        key, _, _ = self.result([self.row('integrity')])
        self.assertEqual(key, 'integrity')

    def test_authentication_alone_does_not_prove_no_encryption(self):
        _, label, _ = self.result([self.row('authentication')])
        self.assertNotIn('not encrypted', label.lower())
        self.assertIn('encryption not established', label.lower())

    def test_gateway_for_another_protocol_is_not_dnp3_protection(self):
        key, label, _ = self.result([self.row('encryption', 'Modbus', 'conditional', 'Modbus server', ['external_gateway'])])
        self.assertEqual(key, 'external_scope_unknown')
        self.assertIn('DNP3 scope not established', label)

    def test_dnp3_gateway_keeps_specific_protocol_scope(self):
        key, _, _ = self.result([self.row('encryption', status='conditional', basis=['external_gateway'])])
        self.assertEqual(key, 'external')

    def test_dnp3_stated_unencrypted_settles_encryption_documented_for_another_protocol(self):
        modbus = self.row('encryption', 'Modbus TCP encrypted', 'conditional', 'Modbus TCP server', ['optional_module'])
        key, _, rows = self.result([modbus, self.row('encryption', 'DNP not encrypted', 'explicitly_unsupported')])
        self.assertEqual((key, [r['protocol'] for r in rows]), ('denied', ['DNP not encrypted']))
        # A refused Secure Authentication says nothing about encryption, so the open scope stays open.
        key, _, _ = self.result([modbus, self.row('dnp3_secure_authentication', status='explicitly_unsupported')])
        self.assertEqual(key, 'tunnel')

    def test_rejection_of_sa_does_not_deny_all_security(self):
        _, label, _ = self.result([self.row('dnp3_secure_authentication', status='explicitly_unsupported')])
        self.assertNotIn('DNP3 is not protected', label)
        self.assertIn('specific', label.lower())

class EvidenceAndPublicationTests(unittest.TestCase):
    def fixture(self, p):
        import sys
        sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
        from support import SurveyCase
        return SurveyCase().reviewed_run(p)

    def test_changed_segments_cannot_supply_new_quotes(self):
        import tempfile
        from pathlib import Path
        from iedsurvey.store import load, dump
        from iedsurvey.report import report
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            src = self.fixture(p)
            path = p/'run'/(src['a']['id']+'.segments.json')
            text = load(path)
            text[0]['text'] += ' Additional wording that was not in the fetched source.'
            dump(path, text)
            with self.assertRaisesRegex(ValueError, 'extracted text hash mismatch'):
                report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            self.assertFalse((p/'report').exists())

    def test_publication_refuses_draft_and_unreviewed_cells(self):
        import tempfile
        from pathlib import Path
        from iedsurvey.report import report
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            self.fixture(p)
            with self.assertRaisesRegex(ValueError, 'publication report requires confirmed'):
                report(p/'run', p/'reviews.json', p/'report', require_evidence=True, require_confirmed=True)
            self.assertFalse((p/'report').exists())

    def test_report_manifest_names_exact_review_bytes_and_draft_state(self):
        import tempfile
        from pathlib import Path
        from iedsurvey.store import load, digest
        from iedsurvey.report import report
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            self.fixture(p)
            report(p/'run', p/'reviews.json', p/'report', require_evidence=True)
            receipt = load(p/'report/report_manifest.json')
            self.assertEqual(receipt['inputs']['reviews']['sha256'], digest((p/'reviews.json').read_bytes()))
            self.assertEqual(receipt['outputs']['dnp3.csv'], digest((p/'report/dnp3.csv').read_bytes()))
            self.assertGreater(receipt['acceptance']['draft_rows'], 0)
            self.assertFalse(receipt['acceptance']['raw_document_bytes_verified_by_report'])


if __name__ == '__main__':
    unittest.main()

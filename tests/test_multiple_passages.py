"""A page's first TLS mention must not hide a later control-protocol statement."""
import unittest
from iedsurvey.leads import candidates


class MultiplePassageTests(unittest.TestCase):
    def test_later_tls_statement_is_visible(self):
        page = 'Engineering access uses TLS. ' + ('Device overview. ' * 70) + 'Secure tunneling from master station via TLS for DNP3/TCP.'
        hit = next(h for h in candidates({'id':'s','product_id':'p'}, [{'location':'pdf-page:1','text':page}]) if h['feature']=='tls')
        self.assertEqual(hit['match_count'], 2)
        self.assertIn('DNP3/TCP', ' '.join(hit.get('contexts', [])))

    def test_adjacent_repeated_mentions_do_not_duplicate_context(self):
        page = 'DNP3 uses TLS. TLS protects the control channel.'
        hit = next(h for h in candidates({'id':'s','product_id':'p'}, [{'location':'pdf-page:1','text':page}]) if h['feature']=='tls')
        self.assertEqual(len(hit.get('contexts', [])), 1)

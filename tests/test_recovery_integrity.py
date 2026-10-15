"""Exercise interruptions and corrupted content-addressed cache entries with a fake site only."""
from pathlib import Path
import tempfile
from unittest.mock import patch

from iedsurvey.crawl import crawl
from iedsurvey.fetch import Fetcher
from iedsurvey.runs import replay
from iedsurvey.store import digest, dump, load
from support import SurveyCase


class RecoveryIntegrityTests(SurveyCase):
    def test_store_restores_known_bytes_after_same_length_cache_corruption(self):
        original = b'<p>DNP3 supports TLS.</p>'
        damaged = b'<p>DNP3 supports SSH.</p>'
        self.assertEqual(len(original), len(damaged))
        with tempfile.TemporaryDirectory() as td:
            fetcher = Fetcher({}, td)
            sha = fetcher.store(original)
            (Path(td) / sha).write_bytes(damaged)
            self.assertEqual(fetcher.store(original), sha)
            self.assertEqual((Path(td) / sha).read_bytes(), original)

    def test_reuse_refuses_corrupt_cached_bytes_before_extracting_them(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            original = b'<p>DNP3 supports TLS.</p>'
            cfg = self.config(p, [{'id': 'p', 'seeds': ['https://vendor.test/a']}])
            with self.site({'https://vendor.test/a': original}, calls):
                crawl(cfg, p / 'old', p / 'cache')
            (p / 'cache' / digest(original)).write_bytes(b'<p>DNP3 supports SSH.</p>')
            calls.clear()
            with self.site({}, calls):
                crawl(cfg, p / 'new', p / 'cache', reuse=p / 'old')
            record = load(p / 'new/sources.json')[0]
            self.assertEqual(record['status'], 'failed')
            self.assertIn('cached source hash mismatch', record['error'])
            self.assertFalse(list((p / 'new').glob('*.segments.json')))
            self.assertEqual(calls, [])

    def test_manifest_is_not_published_before_templates_are_written(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            cfg = self.config(p, [{'id': 'p', 'seeds': ['https://vendor.test/a']}])
            def interrupted_dump(path, value):
                if Path(path).name == 'review_template.json':
                    raise OSError('simulated interrupted template write')
                return dump(path, value)
            with self.site({'https://vendor.test/a': b'<p>DNP3 supports TLS.</p>'}, []):
                with patch('iedsurvey.crawl.dump', side_effect=interrupted_dump):
                    with self.assertRaises(OSError):
                        crawl(cfg, p / 'run', p / 'cache')
                self.assertFalse((p / 'run/manifest.json').exists())
                crawl(cfg, p / 'run', p / 'cache', resume=True)
            self.assertTrue(load(p / 'run/manifest.json')['complete'])
            self.assertTrue((p / 'run/review_template.json').exists())
            replay(p / 'run', p / 'cache', p / 'replay')

    def test_resume_reconstructs_leads_after_a_partial_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.config(p, [{'id': 'p', 'seeds': ['https://vendor.test/a', 'https://vendor.test/b']}])
            pages = {'https://vendor.test/a': b'<p>TLS</p>', 'https://vendor.test/b': b'<p>SSH</p>'}
            with self.site(pages, calls), patch('iedsurvey.crawl.save_leads', side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    crawl(cfg, p / 'run', p / 'cache')
            self.assertEqual(len(load(p / 'run/sources.json')), 1)
            calls.clear()
            with self.site(pages, calls):
                crawl(cfg, p / 'run', p / 'cache', resume=True)
            self.assertEqual([h['feature'] for h in load(p / 'run/candidates.json')], ['tls', 'ssh'])
            self.assertEqual(calls, ['https://vendor.test/b'])
            replay(p / 'run', p / 'cache', p / 'replay')

    def interrupted_run(self, p, calls, approved=None):
        cfg = self.config(p, [{'id': 'p', 'seeds': ['https://vendor.test/a', 'https://vendor.test/b']}])
        with self.site({'https://vendor.test/a': b'<p>TLS</p>', 'https://vendor.test/b': KeyboardInterrupt()}, calls):
            with self.assertRaises(KeyboardInterrupt):
                crawl(cfg, p / 'run', p / 'cache', approved_urls=approved)
        calls.clear()
        return cfg

    def test_resume_refuses_an_approval_change_before_any_new_request(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            approved = p / 'approved.json'
            dump(approved, [{'product_id': 'p', 'url': 'https://vendor.test/b', 'reason': 'initial list'}])
            cfg = self.interrupted_run(p, calls, approved)
            dump(approved, [{'product_id': 'p', 'url': 'https://vendor.test/c', 'reason': 'changed list'}])
            with self.site({}, calls), self.assertRaisesRegex(ValueError, 'resume contract'):
                crawl(cfg, p / 'run', p / 'cache', resume=True, approved_urls=approved)
            self.assertEqual(calls, [])

    def test_resume_refuses_a_changed_extractor_before_any_new_request(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.interrupted_run(p, calls)
            with self.site({}, calls), patch('iedsurvey.crawl.EXTRACTION', 'different'):
                with self.assertRaisesRegex(ValueError, 'resume contract'):
                    crawl(cfg, p / 'run', p / 'cache', resume=True)
            self.assertEqual(calls, [])

    def test_resume_refuses_changed_code_before_any_new_request(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.interrupted_run(p, calls)
            with self.site({}, calls), patch('iedsurvey.crawl.SCRIPT_SHA256', 'different'):
                with self.assertRaisesRegex(ValueError, 'resume contract'):
                    crawl(cfg, p / 'run', p / 'cache', resume=True)
            self.assertEqual(calls, [])

    def test_one_download_can_have_two_product_associations_in_the_same_run(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            url = 'https://vendor.test/manual'
            cfg = self.config(p, [{'id': 'a', 'seeds': [url]}, {'id': 'b', 'seeds': [url]}])
            with self.site({url: b'<p>DNP3 supports TLS.</p>'}, calls):
                crawl(cfg, p / 'run', p / 'cache')
            self.assertEqual(calls, [url])
            sources = load(p / 'run/sources.json')
            self.assertEqual([s['product_id'] for s in sources], ['a', 'b'])
            self.assertNotEqual(sources[0]['id'], sources[1]['id'])
            self.assertEqual(sources[0]['sha256'], sources[1]['sha256'])
            self.assertEqual([h['product_id'] for h in load(p / 'run/candidates.json')], ['a', 'b'])
            replay(p / 'run', p / 'cache', p / 'replay')

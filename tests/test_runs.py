"""A finished run without the network: verify, replay, rebuild and recheck."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import survey as s
from support import SurveyCase


class RunTests(SurveyCase):
    def test_corrupted_cache_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); s.dump(p/'sources.json',[{'id':'s','sha256':'abc'}]); (p/'abc').write_text('wrong')
            with self.assertRaises(ValueError): s.verify(p,p)

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


if __name__ == '__main__':
    unittest.main()

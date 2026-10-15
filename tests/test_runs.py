"""A finished run without the network: verify, replay, rebuild and recheck."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iedsurvey.crawl import crawl
from iedsurvey.fetch import Fetcher
from iedsurvey.report import report
from iedsurvey.runs import rebuild, recheck, replay, verify
from iedsurvey.store import digest, dump, load
from iedsurvey.vocabulary import EXTRACTION, VERSION
from support import SurveyCase


class RunTests(SurveyCase):
    def test_corrupted_cache_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); dump(p/'sources.json',[{'id':'s','sha256':'abc'}]); (p/'abc').write_text('wrong')
            with self.assertRaises(ValueError): verify(p,p)

    def test_rebuild_rederives_leads_offline_and_keeps_source_identity(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); self.reviewed_run(p)
            before = load(p/'run'/'sources.json')
            manifest = load(p/'run'/'manifest.json'); manifest['tool_version'] = '1.1.0'; dump(p/'run'/'manifest.json', manifest)
            dump(p/'run'/'candidates.json', [])
            with patch.object(Fetcher, 'fetch', side_effect=AssertionError('network must not be used')):
                rebuild(p/'run', p/'cache', p/'rebuilt')
            after = load(p/'rebuilt'/'sources.json')
            self.assertEqual([(x['id'], x['sha256'], x.get('retrieved_at')) for x in after], [(x['id'], x['sha256'], x.get('retrieved_at')) for x in before])
            made = load(p/'rebuilt'/'manifest.json')
            self.assertEqual((made['tool_version'], made['rebuilt_from']['tool_version'], made['complete']), (VERSION, '1.1.0', True))
            self.assertEqual([(h['product_id'], h['feature'], h['matched']) for h in load(p/'rebuilt'/'candidates.json')], [('a','tls',['TLS'])])
            replay(p/'rebuilt', p/'cache', p/'replay')
            report(p/'rebuilt', p/'reviews.json', p/'report', require_evidence=True)
            self.assertEqual(load(p/'run'/'candidates.json'), [])
            with self.assertRaises(FileExistsError): rebuild(p/'run', p/'cache', p/'rebuilt')

    def test_replay_refuses_a_run_from_another_tool_version(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.config(p, [{'id':'p','seeds':['https://vendor.test/a']}])
            with self.site({'https://vendor.test/a': b'<p>TLS</p>'}, calls): crawl(cfg, p/'run', p/'cache')
            manifest = load(p/'run'/'manifest.json')
            self.assertEqual(manifest['extraction_version'], EXTRACTION)
            dump(p/'run'/'manifest.json', dict(manifest, tool_version='9.9.9'))
            replay(p/'run', p/'cache', p/'replay_same_rules')
            dump(p/'run'/'manifest.json', dict(manifest, extraction_version='1.0.0'))
            with self.assertRaisesRegex(ValueError,'extraction rules 1.0.0'): replay(p/'run', p/'cache', p/'replay')
            older = {k: v for k, v in manifest.items() if k != 'extraction_version'}
            dump(p/'run'/'manifest.json', dict(older, tool_version='1.2.0'))
            with self.assertRaisesRegex(ValueError,'extraction rules 1.2.0'): replay(p/'run', p/'cache', p/'replay')
            self.assertFalse((p/'replay').exists())

    def test_replay_checks_saved_segments_text_and_location_not_only_leads(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            cfg = self.config(p, [{'id':'p','seeds':['https://vendor.test/a']}])
            page = b'<p>TLS is supported for DNP3 sessions.</p><p>The front panel has four keys.</p>'
            with self.site({'https://vendor.test/a': page}, calls): crawl(cfg, p/'run', p/'cache')
            sid = load(p/'run'/'sources.json')[0]['id']
            saved = p/'run'/(sid + '.segments.json')
            original = load(saved)
            self.assertEqual([x['location'] for x in original], ['html-block:1', 'html-block:2'])
            replay(p/'run', p/'cache', p/'replay_ok')
            # A changed passage without any lead word: the lead files still agree, the recorded digest does not.
            dump(saved, [original[0], dict(original[1], text='The front panel has five keys.')])
            with self.assertRaisesRegex(ValueError, sid + ': saved text does not match the recorded text_sha256'):
                replay(p/'run', p/'cache', p/'replay_text')
            # A passage moved to another location keeps the digest, which ignores location labels.
            dump(saved, [original[0], dict(original[1], location='html-block:7')])
            with self.assertRaisesRegex(ValueError, sid + ': segment 2 differs at html-block:7'):
                replay(p/'run', p/'cache', p/'replay_location')
            saved.unlink()
            with self.assertRaisesRegex(ValueError, sid + ': saved segments missing'):
                replay(p/'run', p/'cache', p/'replay_missing')

    def test_recheck_locates_old_excerpts_in_a_fresh_run(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>intro</p><p>TLS is not  supported for DNP3.</p>', 'https://vendor.test/b': b'<p>SSH</p>'}
            cfg = self.config(p, [{'id':'p','seeds':list(pages)+['https://vendor.test/gone']}])
            with self.site(pages, calls): crawl(cfg, p/'run', p/'cache')
            (p/'old').mkdir()
            dump(p/'old'/'sources.json', [
                {'id':'o1','product_id':'p','url':'https://vendor.test/a','status':'extracted','sha256':'0'*64},
                {'id':'o2','product_id':'p','url':'https://vendor.test/b','status':'extracted','sha256':digest(pages['https://vendor.test/b'])},
                {'id':'o3','product_id':'p','url':'https://vendor.test/gone','status':'failed','error':'ValueError: HTTP 404'},
                {'id':'o4','product_id':'p','url':'https://vendor.test/dropped','status':'extracted','sha256':'1'*64}])
            dump(p/'old'/'evidence_index.json', [
                {'source_id':'o1','location':'html-block:9','excerpt':'TLS is not supported for DNP3.'},
                {'source_id':'o2','location':'html-block:1','excerpt':'This sentence is no longer there.'}])
            a, b, gone, dropped = recheck(p/'old', p/'run', p/'recheck.json')
            self.assertEqual((a['raw_bytes'], a['extracted_text']), ('different','no text hash in old run'))
            self.assertEqual((a['excerpts'][0]['found_at'], a['excerpts'][0]['same_location']), (['html-block:2'], False))
            self.assertEqual((b['raw_bytes'], b['excerpts'][0]['found_at']), ('same', []))
            self.assertEqual((gone['old_status'], gone['new_status'], dropped['new_status']), ('failed','failed','not in new run'))
            self.assertEqual(len(load(p/'recheck.json')['sources']), 4)
            with self.assertRaises(FileExistsError): recheck(p/'old', p/'run', p/'recheck.json')
            self.assertEqual(recheck(p/'run', p/'run')[0]['extracted_text'], 'same')


if __name__ == '__main__':
    unittest.main()

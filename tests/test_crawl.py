"""The crawl: seeds, followed links, budgets, sign-in walls, reuse, resume and the config checks."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import survey as s
from support import SurveyCase, ROOT


class CrawlTests(SurveyCase):
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

    def test_pilot_seed_ids_are_unchanged(self):
        seeds = {(p['id'], u) for p in s.load(ROOT/'configs'/'pilot.json')['products'] for u in p['seeds']}
        recorded = {(x['product_id'], x['url']): x['id'] for x in s.load(ROOT/'pilot'/'sources.json')}
        self.assertEqual(seeds, set(recorded))
        for (pid, url), sid in recorded.items():
            self.assertEqual(s.digest((pid + s.canonical(url)).encode())[:20], sid)

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

    def test_command_line_refusals_are_one_line_errors(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); s.dump(p/'bad.json', {'sampling':'','products':[]}); (p/'taken').mkdir()
            good = self.config(p, [{'id':'p','seeds':[]}])
            for argv, expected in [(['crawl','--config',str(p/'bad.json'),'--out',str(p/'run')], 'error: config needs a sampling statement'),
                                   (['crawl','--config',str(good),'--out',str(p/'taken'),'--cache',str(p/'cache')], 'error: already exists, refusing to overwrite'),
                                   (['verify','--run',str(p/'missing')], 'error: not found')]:
                with self.subTest(argv=argv[0]), patch.object(s.sys, 'argv', ['survey.py']+argv), self.assertRaises(SystemExit) as stop: s.main()
                self.assertIn(expected, str(stop.exception.code))

    def test_a_product_may_override_depth_and_follow_pattern_and_only_narrows_the_run(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>A</p><a href="/a-manual">Manual</a><a href="/a-brochure">Brochure</a>', 'https://vendor.test/a-manual': b'<p>TLS</p>',
                     'https://vendor.test/b': b'<p>B</p><a href="/b-manual">Manual</a>', 'https://vendor.test/b-manual': b'<p>SSH</p>'}
            cfg = self.config(p, [{'id':'a','seeds':['https://vendor.test/a'],'max_depth':1,'max_pages_per_product':5,'follow_pattern':'manual'},
                                  {'id':'b','seeds':['https://vendor.test/b']}], max_depth=0)
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            self.assertEqual(calls, ['https://vendor.test/a', 'https://vendor.test/a-manual', 'https://vendor.test/b'])
            del calls[:]
            with self.site(pages, calls): s.crawl(cfg, p/'only', p/'cache', only='^b ')
            self.assertEqual(calls, ['https://vendor.test/b'])
            self.assertEqual((s.load(p/'only'/'manifest.json')['only'], {r['product_id'] for r in s.load(p/'only'/'review_template.json')}), ('^b ', {'b'}))
            # The run's own config lists what the run covered, so its report and worksheet do not show the rest as unread.
            self.assertEqual([x['id'] for x in s.load(p/'only'/'config.json')['products']], ['b'])
            self.assertEqual(s.load(p/'only'/'manifest.json')['config_sha256'], s.digest(Path(cfg).read_bytes()))
            with self.assertRaisesRegex(ValueError,'matches no product'): s.crawl(cfg, p/'none', p/'cache', only='^zzz')
            self.assertFalse((p/'none').exists())
            bad = self.config(p, [{'id':'a','seeds':[],'follow_pattern':'('}])
            with self.assertRaisesRegex(ValueError,'follow_pattern'): s.crawl(bad, p/'bad', p/'cache')

    def test_reuse_does_not_request_what_an_earlier_run_already_fetched(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>TLS</p><a href="/manual">Manual</a>', 'https://vendor.test/manual': b'<p>SSH</p>'}
            first = self.config(p, [{'id':'a','seeds':['https://vendor.test/a']}])
            with self.site(pages, calls): s.crawl(first, p/'census', p/'cache')
            del calls[:]
            deep = self.config(p, [{'id':'a','seeds':['https://vendor.test/a'],'max_depth':1}])
            with self.site(pages, calls): s.crawl(deep, p/'deep', p/'cache', reuse=p/'census')
            self.assertEqual(calls, ['https://vendor.test/manual'])
            page, manual = s.load(p/'deep'/'sources.json')
            self.assertEqual((page['status'], page['reused_from'], page['sha256']), ('extracted', str(p/'census'), s.load(p/'census'/'sources.json')[0]['sha256']))
            self.assertNotIn('reused_from', manual)
            self.assertEqual(s.load(p/'deep'/'manifest.json')['reused_from'], str(p/'census'))
            s.replay(p/'deep', p/'cache', p/'replay')

    def test_reuse_gives_each_product_its_own_earlier_fetch_of_a_shared_address(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls, url = Path(td), [], 'https://vendor.test/family'
            a, b, c = ({'id': pid, 'seeds': [url]} for pid in 'abc')
            # A page that returns different bytes on every request: each record holds what was sent for that product.
            with self.site({url: b'<p>TLS</p><!-- first -->'}, calls): s.crawl(self.config(p, [a]), p/'one', p/'cache')
            with self.site({url: b'<p>TLS</p><!-- second -->'}, calls): s.crawl(self.config(p, [b]), p/'two', p/'cache')
            del calls[:]
            with self.site({}, calls): s.crawl(self.config(p, [a, b, c]), p/'again', p/'cache', reuse=[p/'one', p/'two'])
            self.assertEqual(calls, [])
            one, two = s.load(p/'one'/'sources.json')[0], s.load(p/'two'/'sources.json')[0]
            self.assertNotEqual(one['sha256'], two['sha256'])
            # A product without a record of its own takes the first run's, which is as good as any.
            self.assertEqual([(x['product_id'], x['sha256'], x['reused_from']) for x in s.load(p/'again'/'sources.json')],
                             [('a', one['sha256'], str(p/'one')), ('b', two['sha256'], str(p/'two')), ('c', one['sha256'], str(p/'one'))])

    def test_reuse_keeps_a_document_that_arrived_but_could_not_be_read_and_asks_again_for_one_that_never_came(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>TLS</p>', 'https://vendor.test/scan': b'<p> </p>'}
            cfg = self.config(p, [{'id':'a','seeds':['https://vendor.test/a','https://vendor.test/scan','https://vendor.test/gone']}])
            with self.site(pages, calls): s.crawl(cfg, p/'first', p/'cache')
            del calls[:]
            with self.site(pages, calls): s.crawl(cfg, p/'second', p/'cache', reuse=p/'first')
            # The scan's bytes are held, so it fails the same way from the cache. A request that failed may succeed next time.
            self.assertEqual(calls, ['https://vendor.test/gone'])
            was, now = ({x['url'].rsplit('/', 1)[1]: x for x in s.load(p/run/'sources.json')} for run in ('first', 'second'))
            self.assertEqual([(now[k]['status'], now[k].get('reused_from'), now[k].get('error')) for k in ('a', 'scan', 'gone')],
                             [('extracted', str(p/'first'), None), ('failed', str(p/'first'), was['scan']['error']), ('failed', None, 'ValueError: HTTP 404')])
            self.assertEqual((was['scan']['error'], now['scan']['sha256']), ('ValueError: no extractable text; OCR/manual review required', was['scan']['sha256']))

    def test_sign_in_walls_are_counted_and_never_requested(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>A</p><a href="/passport/login?destination=/files/manuals">Download manual</a><a href="/open-manual">Manual</a>'
                                              b'<a href="/passport/login?destination=/files/manuals">Download communications manual</a>',
                     'https://vendor.test/open-manual': ValueError('login required: redirected to https://vendor.test/login?next=x')}
            cfg = self.config(p, [{'id':'a','seeds':['https://vendor.test/a'],'max_depth':1,'max_pages_per_product':5}])
            with self.site(pages, calls): s.crawl(cfg, p/'run', p/'cache')
            self.assertEqual(calls, ['https://vendor.test/a', 'https://vendor.test/open-manual'])
            recs = s.load(p/'run'/'sources.json')
            self.assertEqual([(r['status'], r['url'].split('vendor.test')[1][:16]) for r in recs], [('extracted','/a'), ('login_required','/passport/login?'), ('login_required','/open-manual')])
            # One sign-in address stood for two documents, so it counts twice; the redirected request counts once.
            self.assertEqual((recs[1]['link_text'], recs[1]['link_count'], recs[1]['via'], recs[0]['links_matched']), ('Download manual', 2, recs[0]['id'], 2))
            s.report(p/'run', p/'run'/'review_template.json', p/'report')
            text = (p/'report'/'REPORT.md').read_text(encoding='utf-8')
            self.assertIn('Sources attempted: 1; extracted: 1; failed: 0; documents behind a sign-in, not requested: 3.', text)
            # A later run that builds on this one does not ask again for a document it was told needs a sign-in.
            del calls[:]
            with self.site(pages, calls): s.crawl(cfg, p/'again', p/'cache', reuse=p/'run')
            self.assertEqual(calls, [])
            self.assertEqual([(r['status'], 'reused_from' in r) for r in s.load(p/'again'/'sources.json')], [('extracted',True), ('login_required',False), ('login_required',True)])
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt': (404,{},b''), 'https://vendor.test/doc': (302,{'Location':'https://vendor.test/account/sign-in?return=/doc'},b'')})
            with raw as seen, self.assertRaisesRegex(ValueError,'login required'): f.fetch('https://vendor.test/doc', ['vendor.test'])
            self.assertEqual(seen.call_count, 2)
            for url, gated in [('https://v.test/passport/login?x=1', True), ('https://idp.v.test/a', True), ('https://v.test/login', True), ('https://v.test/signin/', True),
                               ('https://v.test/docs/logging-in-guide.pdf', False), ('https://v.test/products/loginet-relay', False), ('https://v.test/manual.pdf', False)]:
                with self.subTest(url=url): self.assertEqual(bool(s.LOGIN.search(url)), gated)

    def test_links_to_device_profiles_and_manuals_are_followed_before_brochures(self):
        score = lambda url, text: s.link_score(url, text, None)
        self.assertGreater(score('https://v.test/x1', 'DNP3 Device Profile'), score('https://v.test/x2', 'Instruction Manual'))
        self.assertGreater(score('https://v.test/x2', 'Instruction Manual'), score('https://v.test/x3', 'Brochure'))
        self.assertGreater(score('https://v.test/x3', 'Brochure'), score('https://v.test/x4', 'Careers'))
        self.assertEqual(score('https://v.test/manual.pdf', 'M'), score('https://v.test/security', 'S'))
        self.assertGreater(score('https://v.test/x5', 'IEC 61850 Communications User Manual'), score('https://v.test/x6', 'RTD Scanner User Manual'))

    def test_reuse_takes_pages_from_several_earlier_runs(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/a': b'<p>TLS</p>', 'https://vendor.test/b': b'<p>SSH</p>', 'https://vendor.test/c': b'<p>IPsec</p>'}
            for name in 'ab':
                with self.site(pages, calls): s.crawl(self.config(p, [{'id':name,'seeds':[f'https://vendor.test/{name}']}]), p/name, p/'cache')
            del calls[:]
            both = self.config(p, [{'id':'x','seeds':list(pages)}])
            with self.site(pages, calls): s.crawl(both, p/'x', p/'cache', reuse=[p/'a', p/'b'])
            self.assertEqual(calls, ['https://vendor.test/c'])
            self.assertEqual([r.get('reused_from') for r in s.load(p/'x'/'sources.json')], [str(p/'a'), str(p/'b'), None])
            self.assertEqual(s.load(p/'x'/'manifest.json')['reused_from'], [str(p/'a'), str(p/'b')])
            s.replay(p/'x', p/'cache', p/'replay')

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


if __name__ == '__main__':
    unittest.main()

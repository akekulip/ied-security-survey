import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import survey as s


class SurveyTests(unittest.TestCase):
    def test_domain_boundary(self):
        self.assertTrue(s.allowed('https://manual.vendor.test/a', ['vendor.test']))
        for u in ['https://vendor.test.evil.test/a','https://evilvendor.test/a',
                  'http://vendor.test/a','https://user@vendor.test/a', 'https://vendor.test:99/a']:
            self.assertFalse(s.allowed(u, ['vendor.test']))

    def test_hash_fragment_removed_query_retained(self):
        self.assertEqual(s.canonical('https://Vendor.test/a?lang=en#top'), 'https://vendor.test/a?lang=en')

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

    def test_fetch_redirect_rejected_before_destination_contact(self):
        with tempfile.TemporaryDirectory() as td:
            f = s.Fetcher({'delay_seconds':0}, td)
            with patch.object(f, 'robot'), patch.object(f, 'raw', return_value=(302, {'Location':'https://evil.test/a'}, b'')) as raw:
                with self.assertRaisesRegex(ValueError,'outside vendor'):
                    f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(raw.call_count,1)

    def test_redirect_checks_robots_each_hop(self):
        with tempfile.TemporaryDirectory() as td:
            f = s.Fetcher({},td)
            with patch.object(f,'robot') as robot, patch.object(f,'raw',side_effect=[(302,{'Location':'https://docs.vendor.test/a'},b''),(200,{'Content-Type':'text/html'},b'<p>x</p>')]):
                meta,_=f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(robot.call_count,2)
                self.assertEqual(meta['sha256'],s.digest(b'<p>x</p>'))

    def test_robots_denial_and_errors_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            for status,body in [(200,b'User-agent: *\nDisallow: /private'),(503,b'unavailable'),(403,b'forbidden'),(301,b'')]:
                f=s.Fetcher({},td)
                def raw(url):
                    f.audit.append({'url':url}); return status,{},body
                with patch.object(f,'raw',side_effect=raw), self.assertRaises(ValueError):
                    f.robot('https://vendor.test/private')

    def test_robots_404_allows_and_records(self):
        with tempfile.TemporaryDirectory() as td:
            f=s.Fetcher({},td)
            def raw(url):
                f.audit.append({'url':url}); return 404,{},b'not found'
            with patch.object(f,'raw',side_effect=raw): f.robot('https://vendor.test/a')
            self.assertIn('sha256',f.audit[0])

    def fixture(self):
        source={'id':'s','product_id':'p','status':'extracted','sha256':'abc'}
        row={'product_id':'p','feature':'tls','status':'supported','source_ids':['s'],
             'source_hashes':{'s':'abc'},'reviewer':'test','reviewed_at':'2026-10-13','rationale':'explicit',
             'protocol':'HTTPS','interface':'management','firmware':'unknown','implementation':'native','location':'page 2'}
        return source,row

    def test_review_hash_binding(self):
        source,row=self.fixture()
        s.validate_reviews([row],[source],{'p'})
        row['source_hashes']['s']='changed'
        with self.assertRaisesRegex(ValueError,'hash mismatch'): s.validate_reviews([row],[source],{'p'})

    def test_wrong_product_or_failed_source_rejected(self):
        for change in [{'product_id':'q'},{'status':'failed'}]:
            source,row=self.fixture(); source.update(change)
            with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})

    def test_unreviewed_claim_and_empty_evidence_rejected(self):
        source,row=self.fixture()
        row['reviewer']=''
        with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})
        row['reviewer']='test'; row['source_ids']=[]
        with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})

    def test_duplicate_cells_rejected(self):
        source,row=self.fixture()
        with self.assertRaises(ValueError): s.validate_reviews([row,row],[source],{'p'})

    def test_corrupted_cache_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); s.dump(p/'sources.json',[{'id':'s','sha256':'abc'}]); (p/'abc').write_text('wrong')
            with self.assertRaises(ValueError): s.verify(p,p)

    def test_redirect_loop_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            f=s.Fetcher({},td)
            with patch.object(f,'robot'), patch.object(f,'raw',return_value=(302,{'Location':'/a'},b'')) as raw:
                with self.assertRaisesRegex(ValueError,'too many redirects'):
                    f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(raw.call_count,6)

    def test_download_size_limit(self):
        import io
        class Reply(io.BytesIO):
            code=200
            headers={'Content-Type':'text/html'}
        with tempfile.TemporaryDirectory() as td:
            f=s.Fetcher({'max_bytes':4},td)
            with patch.object(f.opener,'open',return_value=Reply(b'too large')):
                with self.assertRaisesRegex(ValueError,'byte limit'): f.raw('https://vendor.test/a')

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


if __name__=='__main__': unittest.main()

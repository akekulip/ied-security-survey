"""Requests: the allowlist, robots.txt, redirects, limits, retries and the request log."""
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from iedsurvey.fetch import Fetcher, allowed, canonical
from iedsurvey.store import digest, dump, load
from support import SurveyCase, Reply


class FetchTests(SurveyCase):
    def test_domain_boundary(self):
        self.assertTrue(allowed('https://manual.vendor.test/a', ['vendor.test']))
        for u in ['https://vendor.test.evil.test/a','https://evilvendor.test/a',
                  'http://vendor.test/a','https://user@vendor.test/a', 'https://vendor.test:99/a']:
            self.assertFalse(allowed(u, ['vendor.test']))

    def test_hash_fragment_removed_query_retained(self):
        self.assertEqual(canonical('https://Vendor.test/a?lang=en#top'), 'https://vendor.test/a?lang=en')

    def test_fetch_redirect_rejected_before_destination_contact(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fetcher({'delay_seconds':0}, td)
            with patch.object(f, 'robot'), patch.object(f, 'raw', return_value=(302, {'Location':'https://evil.test/a'}, b'')) as raw:
                with self.assertRaisesRegex(ValueError,'outside vendor'):
                    f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(raw.call_count,1)

    def test_redirect_checks_robots_each_hop(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fetcher({},td)
            with patch.object(f,'robot') as robot, patch.object(f,'raw',side_effect=[(302,{'Location':'https://docs.vendor.test/a'},b''),(200,{'Content-Type':'text/html'},b'<p>x</p>')]):
                meta,_=f.fetch('https://vendor.test/a',['vendor.test'])
                self.assertEqual(robot.call_count,2)
                self.assertEqual(meta['sha256'],digest(b'<p>x</p>'))

    def test_robots_denial_and_errors_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            for status,body in [(200,b'User-agent: *\nDisallow: /private'),(503,b'unavailable'),(403,b'forbidden'),(301,b'')]:
                f=Fetcher({},td)
                def raw(url):
                    f.audit.append({'url':url}); return status,{},body
                with patch.object(f,'raw',side_effect=raw), self.assertRaises(ValueError):
                    f.robot('https://vendor.test/private')

    def test_robots_404_allows_and_records(self):
        with tempfile.TemporaryDirectory() as td:
            f=Fetcher({},td)
            def raw(url):
                f.audit.append({'url':url}); return 404,{},b'not found'
            with patch.object(f,'raw',side_effect=raw): f.robot('https://vendor.test/a')
            self.assertIn('sha256',f.audit[0])

    def test_redirect_loop_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            f=Fetcher({},td)
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
            f=Fetcher({'max_bytes':4},td)
            with patch.object(f.opener,'open',return_value=Reply(b'too large')):
                with self.assertRaisesRegex(ValueError,'byte limit'): f.raw('https://vendor.test/a')

    def test_canonical_encodes_and_normalises(self):
        for raw, want in {'https://vendor.test/docs/My Manual.pdf':'https://vendor.test/docs/My%20Manual.pdf',
                          ' https://vendor.test:443/a ':'https://vendor.test/a',
                          'https://vendor.test/a?x=1&y=a b':'https://vendor.test/a?x=1&y=a%20b',
                          'https://vendor.test/a%20b/$/c':'https://vendor.test/a%20b/$/c'}.items():
            self.assertEqual(canonical(raw), want)

    def test_utf8_lf_and_atomic_dump(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); text = 'R \u2265 10 \u03a9 \u2192 con\ufb01dentiality'
            dump(p/'x.json', [{'text':text}])
            self.assertEqual(load(p/'x.json'), [{'text':text}])
            self.assertIn(text.encode('utf-8'), (p/'x.json').read_bytes())
            self.assertNotIn(b'\r', (p/'x.json').read_bytes())
            self.assertEqual([x.name for x in p.iterdir()], ['x.json'])

    def test_robots_wildcards_and_longest_match(self):
        rules = (b'User-agent: *\nDisallow: /*.pdf$\nDisallow: /*/_theme/\nDisallow: /*jcr:content*\nDisallow: */ecommerce\n'
                 b'Disallow: /software/sites/default/files/*.pdf\nDisallow: /private/\nAllow: /private/public/\nCrawl-delay: 7\n')
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt':(200,{},rules)})
            with raw as calls:
                for path in ['/docs/a.pdf','/en/_theme/x.css','/a/jcr:content/b','/en-us/ecommerce','/software/sites/default/files/x/y.pdf','/private/a']:
                    with self.subTest(path=path), self.assertRaisesRegex(ValueError,'robots disallow'): f.robot('https://vendor.test'+path)
                for path in ['/docs/a.html','/docs/a.pdf?download=1','/private/public/a']:
                    with self.subTest(path=path): f.robot('https://vendor.test'+path)
                self.assertEqual(calls.call_count, 1)
            self.assertEqual((f.robots['vendor.test']['gap'], f.robots['vendor.test']['basis']), (7, '200'))

    def test_robots_group_named_for_this_crawler_wins(self):
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt':(200,{},b'User-agent: *\nDisallow:\n\nUser-agent: IEDSecuritySurvey\nDisallow: /\n')})
            with raw, self.assertRaisesRegex(ValueError,'robots disallow'): f.robot('https://vendor.test/a')

    def test_unresolved_robots_is_asked_once_per_host(self):
        for reply in [(503,{},b'unavailable'), TimeoutError('timed out')]:
            with tempfile.TemporaryDirectory() as td:
                f, raw = self.scripted(td, {'https://lit.vendor.test/robots.txt':reply})
                with raw as calls:
                    for path in '/a.pdf', '/b.pdf', '/c.pdf':
                        with self.assertRaisesRegex(ValueError,'robots unresolved'): f.robot('https://lit.vendor.test'+path)
                    self.assertEqual(calls.call_count, 1)

    def test_robots_redirect_is_opt_in_and_stays_inside_the_allowlist(self):
        replies = {'https://lit.vendor.test/robots.txt':(301,{'Location':'https://www.vendor.test/library'},b''),
                   'https://www.vendor.test/library':(302,{'Location':'/en-us.html'},b''),
                   'https://www.vendor.test/en-us.html':(200,{'Content-Type':'text/html'},b'<html><body>Literature</body></html>'),
                   'https://lit.vendor.test/a.pdf':(200,{'Content-Type':'text/html','Set-Cookie':'sid=1','ETag':'"e"'},b'<p>x</p>'),
                   'https://out.vendor.test/robots.txt':(301,{'Location':'https://evil.test/robots.txt'},b'')}
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, replies)
            with raw as calls, self.assertRaisesRegex(ValueError,'robots unresolved: HTTP 301'): f.robot('https://lit.vendor.test/a.pdf',['vendor.test'])
            self.assertEqual(calls.call_count, 1)
            f, raw = self.scripted(td, replies, {'robots_follow_redirects':True})
            with raw as calls:
                meta, _ = f.fetch('https://lit.vendor.test/a.pdf',['vendor.test'])
                self.assertEqual(meta['robots_basis'], 'redirected:https://www.vendor.test/en-us.html')
                self.assertEqual(meta['headers'], {'Content-Type':'text/html','ETag':'"e"'})
                self.assertEqual([x['url'] for x in f.audit], list(replies)[:4])
                self.assertIn('sha256', f.audit[2])
                with self.assertRaisesRegex(ValueError,'outside vendor allowlist'): f.robot('https://out.vendor.test/a',['vendor.test'])
                with self.assertRaisesRegex(ValueError,'outside vendor allowlist'): f.robot('https://out.vendor.test/b',['vendor.test'])
                self.assertEqual(calls.call_count, 5)
            f, raw = self.scripted(td, replies, {'robots_follow_redirects':True})
            with raw, self.assertRaisesRegex(ValueError,'outside vendor allowlist'): f.robot('https://lit.vendor.test/a.pdf')

    def test_failed_attempts_stay_in_the_request_log(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fetcher({'delay_seconds':0,'max_bytes':4}, td)
            with patch.object(f.opener,'open',side_effect=TimeoutError('timed out')), self.assertRaises(TimeoutError): f.raw('https://vendor.test/a')
            with patch.object(f.opener,'open',return_value=Reply(b'too large')), self.assertRaises(ValueError): f.raw('https://vendor.test/b')
            self.assertEqual([x['url'] for x in f.audit], ['https://vendor.test/a','https://vendor.test/b'])
            self.assertIn('TimeoutError', f.audit[0]['error'])
            self.assertIn('byte limit', f.audit[1]['error'])
            self.assertEqual(f.audit[1]['status'], 200)

    def test_truncated_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fetcher({'delay_seconds':0}, td)
            with patch.object(f.opener,'open',return_value=Reply(b'short',headers={'Content-Length':'100'})):
                with self.assertRaisesRegex(ValueError,'shorter than its Content-Length'): f.raw('https://vendor.test/a')
            with patch.object(f.opener,'open',return_value=Reply(b'whole',headers={'content-length':'5'})):
                self.assertEqual(f.raw('https://vendor.test/a')[2], b'whole')

    def test_retries_are_opt_in_bounded_and_logged(self):
        script = lambda: [TimeoutError('timed out'), Reply(b'busy',503,{'Retry-After':'7'}), Reply(b'ok')]
        with tempfile.TemporaryDirectory() as td, patch.object(time,'sleep') as sleep:
            f = Fetcher({'delay_seconds':0}, td)
            with patch.object(f.opener,'open',side_effect=script()), self.assertRaises(TimeoutError): f.raw('https://vendor.test/a')
            self.assertEqual(len(f.audit), 1)
            f = Fetcher({'delay_seconds':0,'retries':2}, td)
            with patch.object(f.opener,'open',side_effect=script()): self.assertEqual(f.raw('https://vendor.test/a')[::2], (200, b'ok'))
            self.assertEqual([(x.get('status'), x.get('retried', False)) for x in f.audit], [(None,True),(503,True),(200,False)])
            self.assertIn(7, [c.args[0] for c in sleep.call_args_list])
            f = Fetcher({'delay_seconds':0,'retries':1}, td)
            with patch.object(f.opener,'open',side_effect=script()): self.assertEqual(f.raw('https://vendor.test/a')[0], 503)
            with patch.object(f.opener,'open',return_value=Reply(b'gone',404)): self.assertEqual(f.raw('https://vendor.test/a')[0], 404)
            self.assertEqual(len(f.audit), 3)

    def test_robots_redirect_option_can_be_limited_to_named_domains(self):
        replies = {'https://lit.vendor.test/robots.txt': (301,{'Location':'https://www.vendor.test/home'},b''), 'https://www.vendor.test/home': (200,{},b'<html></html>'),
                   'https://lit.other.test/robots.txt': (301,{'Location':'https://www.other.test/home'},b''), 'https://www.other.test/home': (200,{},b'<html></html>')}
        with tempfile.TemporaryDirectory() as td:
            f, raw = self.scripted(td, replies, {'robots_follow_redirects': ['vendor.test']})
            with raw:
                f.robot('https://lit.vendor.test/a.pdf', ['vendor.test'])
                with self.assertRaisesRegex(ValueError,'robots unresolved: HTTP 301'): f.robot('https://lit.other.test/a.pdf', ['other.test'])
            self.assertEqual(f.robots['lit.vendor.test']['basis'], 'redirected:https://www.vendor.test/home')


if __name__ == '__main__':
    unittest.main()

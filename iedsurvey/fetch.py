"""The only code that talks to a vendor site: HTTPS, allowlist, robots.txt, redirects, sign-in walls, cache and request log."""

import os
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from protego import Protego

from .vocabulary import VERSION
from .store import digest, now


UA_TOKEN = 'IEDSecuritySurvey'


UA = f"{UA_TOKEN}/{VERSION.rsplit('.', 1)[0]} (public-document research; no device scanning)"


REDIRECTS = (301, 302, 303, 307, 308)


RETRY_STATUS = (429, 502, 503, 504)


KEEP_HEADERS = ('content-type', 'content-length', 'content-disposition', 'content-language', 'last-modified', 'etag', 'date')


# A link that leads to a sign-in page marks a document that exists but is not public. It is recorded, never fetched.
LOGIN = re.compile(r'/(?:log-?in|sign-?in|sso|passport|oauth2?|authorize)(?:[/?.]|$)|//(?:idp|login|sso|auth|account)\.', re.I)


def header(headers, name):
    return next((v for k, v in headers.items() if k.lower() == name), '')


def canonical(url):
    p = urlsplit(url.strip())
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise ValueError('Only public HTTPS URLs without credentials or custom ports are allowed')
    safe = "/%:@!$&'()*+,;=~-._"
    return urlunsplit(('https', p.hostname, quote(p.path or '/', safe=safe), quote(p.query, safe=safe + '?'), ''))


def allowed(url, domains):
    try:
        host = urlsplit(canonical(url)).hostname
        return any(host == d or host.endswith('.' + d) for d in domains)
    except ValueError:
        return False


def retry_after(headers):
    value = header(headers, 'retry-after').strip()
    if value.isdigit():
        return int(value)
    try:
        return max(0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError):
        return 0


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Fetcher:
    def __init__(self, config, cache):
        self.config, self.cache = config, Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.opener = build_opener(NoRedirect)
        self.robots, self.last, self.audit = {}, {}, []

    def store(self, body):
        h = digest(body)
        path = self.cache / h
        if not path.exists() or path.stat().st_size != len(body):
            tmp = path.with_name(h + '.tmp')
            tmp.write_bytes(body)
            os.replace(tmp, path)
        return h

    def once(self, url, limit):
        req = Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
        try:
            response = self.opener.open(req, timeout=self.config.get('timeout_seconds', 25))
        except HTTPError as e:
            response = e
        with response:
            return response.code, dict(response.headers), response.read(limit + 1)

    def raw(self, url):
        host = urlsplit(url).netloc
        delay = max(float(self.config.get('delay_seconds', 1)), self.robots.get(host, {}).get('gap', 0))
        limit, left = self.config.get('max_bytes', 25000000), int(self.config.get('retries', 0))
        while True:
            time.sleep(max(0, delay - (time.monotonic() - self.last.get(host, 0))))
            self.last[host] = time.monotonic()
            entry = {'at': now(), 'url': url}
            self.audit.append(entry)  # Logged before the outcome is known, so failed attempts stay on record.
            try:
                status, headers, body = self.once(url, limit)
                entry.update(status=status, bytes=len(body))
                declared = header(headers, 'content-length').strip()
                if len(body) > limit:
                    raise ValueError('response exceeds byte limit')
                # read(n) returns a short body without complaint when the connection drops.
                if declared.isdigit() and len(body) < int(declared):
                    raise ValueError('response shorter than its Content-Length')
                if status not in RETRY_STATUS or not left:
                    return status, headers, body
                wait = retry_after(headers)
            except Exception as e:
                entry['error'] = f'{type(e).__name__}: {e}'
                if not left or not isinstance(getattr(e, 'reason', e), (TimeoutError, ConnectionError)):
                    raise
                wait = 0
            left -= 1
            entry['retried'] = True
            time.sleep(min(max(wait, 5), 120))

    def load_robots(self, host, domains):
        first = url = f'https://{host}/robots.txt'
        try:
            follow = self.config.get('robots_follow_redirects')
            if isinstance(follow, list):  # Opted in for named domains only.
                name = urlsplit(first).hostname
                follow = any(name == d or name.endswith('.' + d) for d in follow)
            for _ in range(6):  # RFC 9309 asks crawlers to follow at least five consecutive redirects.
                status, headers, body = self.raw(url)
                if status not in REDIRECTS or not follow:
                    break
                if not header(headers, 'location'):
                    raise ValueError('redirect without Location')
                url = canonical(urljoin(url, header(headers, 'location')))
                if not allowed(url, domains or [urlsplit(first).hostname]):
                    raise ValueError('redirect outside vendor allowlist')
            else:
                raise ValueError('too many redirects')
            # Redirects (unless opted in), denials and errors are unresolved, not permission to crawl.
            if status not in (200, 404):
                raise ValueError(f'HTTP {status}')
        except Exception as e:
            reason = str(e) if isinstance(e, ValueError) else f'{type(e).__name__}: {e}'
            return {'error': 'robots unresolved: ' + reason}
        self.audit[-1]['sha256'] = self.store(body)
        rules = Protego.parse(body.decode('utf-8-sig', 'replace') if status == 200 else '')
        gap = rules.crawl_delay(UA_TOKEN) or 0
        rate = rules.request_rate(UA_TOKEN)
        if rate and rate.requests:
            gap = max(gap, rate.seconds / rate.requests)
        basis = str(status) if url == first else f'redirected:{url}' + ('' if status == 200 else f' ({status})')
        return {'rules': rules, 'gap': gap, 'basis': basis, 'sitemaps': list(rules.sitemaps)}

    def robot(self, url, domains=None):
        host = urlsplit(url).netloc
        if host not in self.robots:
            # Resolved once per host and run, including an unresolved outcome.
            self.robots[host] = self.load_robots(host, domains)
        state = self.robots[host]
        if 'error' in state:
            raise ValueError(state['error'])
        if not state['rules'].can_fetch(url, UA_TOKEN):
            raise ValueError('robots disallow')

    def fetch(self, url, domains):
        chain = []
        for _ in range(6):
            url = canonical(url)
            if not allowed(url, domains):
                raise ValueError('URL/redirect outside vendor allowlist')
            self.robot(url, domains)
            status, headers, body = self.raw(url)
            chain.append({'url': url, 'status': status})
            if status in REDIRECTS:
                if not header(headers, 'location'):
                    raise ValueError('redirect without Location')
                url = urljoin(url, header(headers, 'location'))
                if LOGIN.search(url):
                    raise ValueError(f'login required: redirected to {url}')
                continue
            if status != 200:
                raise ValueError(f'HTTP {status}')
            return {'final_url': url, 'sha256': self.store(body), 'bytes': len(body),
                    'headers': {k: v for k, v in headers.items() if k.lower() in KEEP_HEADERS},
                    'robots_basis': self.robots.get(urlsplit(url).netloc, {}).get('basis'),
                    'redirect_chain': chain, 'retrieved_at': now()}, body
        raise ValueError('too many redirects')

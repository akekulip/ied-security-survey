#!/usr/bin/env python3
"""Bounded public-document survey. Keyword hits are leads, never support verdicts."""
import argparse
import csv
import hashlib
import heapq
import io
import json
import os
import re
import sys
import time
import unicodedata
import zlib
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

from protego import Protego

VERSION = '1.3.0'
UA_TOKEN = 'IEDSecuritySurvey'
UA = f"{UA_TOKEN}/{VERSION.rsplit('.', 1)[0]} (public-document research; no device scanning)"
# Review cells. Changing this tuple changes every denominator; lead groups below may grow freely.
CAPABILITIES = ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'authentication', 'encryption', 'ssh')
# A capability named in a sentence that denies it. Encryption wording is left to plaintext_statement where both apply.
TERM = r'(?:m?TLS|SSL|DTLS|IP\s?sec|SSH|MACsec|secure\s+authentication|authentication|encryption|CIP\s+Security)'
PATTERNS = {
    'dnp3_secure_authentication': r'secure\s+auth\w*|\b(?-i:SA)\s*v\d\b|\bDNP\s*3?.{0,80}?\b(?-i:SA)\b|\bIEC\s*62351-5\b',
    'tls': r'\bm?TLS(?:\s?v?\d(?:\.\d)?)?\b|transport\s+layer\s+security|\bSSL\b',
    'ipsec': r'\bIP\s?sec\b|\bIP\s+security\b|\b(?-i:IKE)(?:v[12])?\b',
    # ODVA's CIP Security, not NERC CIP: the two share an acronym and nothing else.
    'cip_security': r'(?-i:(?<!NERC[\s-])\bCIP\s+Security(?![a-z]))',
    'authentication': r'\bauthenticat\w*|\bRADIUS\b|\b802\.1X\b|\bLDAP\b|\bKerberos\b|\bTACACS\b',
    'encryption': r'\b(?:un|non-?)?encrypt\w*|\bDTLS\b|\bAES\b|\bcipher\w*',
    'ssh': r'\bSSH\b|secure\s+shell',
    # Lead-only groups below: shown to the reviewer, never review cells. A capability group above holds only terms
    # that name that capability, so a VPN recommendation is not filed as IPsec, nor SFTP as SSH.
    'vpn': r'\bVPN\b',
    'sftp': r'\bSFTP\b',
    'plaintext_statement': r'\bunencrypted\b|\bnon-?encrypted\b|\bnot\s+(?:be\s+|been\s+|being\s+)?encrypted\b'
                           r'|\bno\s+encryption\b|\bwithout\s+encryption\b'
                           r'|\bplain\s?-?text\b|\bclear\s?-?text\b|\bin\s+the\s+clear\b',
    # Explicit denials are searched for as deliberately as claims; they are the only route to explicitly_unsupported.
    'non_support_statement': rf'\b{TERM}\b[^.]{{0,60}}?\b(?:is|are|was|were)\s+not\s+(?:used|supported|available|implemented|provided|offered)\b'
                             rf"|(?:\b(?:does|do|did|will)\s+not|\b(?:does|do|did|wo)n['\u2019]t)\s+(?:support|provide|implement|offer|use|include)\b[^.]{{0,60}}?\b{TERM}\b"
                             rf'|\b{TERM}\b[^.\w]{{0,6}}(?:not\s+supported|unsupported|not\s+available)\b'
                             r'|\bno\s+(?:support\s+for\s+)?(?:m?TLS|SSL|DTLS|IP\s?sec|SSH|MACsec|secure\s+authentication|authentication|CIP\s+Security)\b',
    'macsec': r'\bMACsec\b|\b802\.1AE\b',
    'iec_62351': r'\bIEC(?:/TS)?\s*62351(?:-\d+)?\b',
}
LEADS = {k: re.compile(v, re.I | re.S) for k, v in PATTERNS.items()}
# A lead in these groups also needs the qualifying term close by.
NEAR = {'dnp3_secure_authentication': re.compile(r'\bDNP|\b1815\b|62351-5', re.I)}
# "If the device does not support ..." states a condition, not a fact about the product.
HYPOTHETICAL = re.compile(r'\b(?:if|whether|unless|when|where|in\s+case)\b[^.]{0,60}$', re.I)
STATEMENTS = ('plaintext_statement', 'non_support_statement')
STATUSES = {'supported', 'conditional', 'explicitly_unsupported', 'unknown', 'conflicting'}
# Roughly from most to least direct about what one product and firmware can do. Guidance for the reviewer, not a score.
DOC_TYPES = ('device_profile', 'conformance_statement', 'security_guide', 'manual', 'datasheet', 'product_page',
             'advisory', 'other')
# The distinction the study turns on: protection of control traffic is not protection of management access.
INTERFACE_CLASSES = ('control_protocol', 'management', 'network')
REVIEW_STATUSES = ('draft', 'confirmed')
# Pointers only: which mechanism rows a reader should look at when no explicit property row exists.
RELATES = {'encryption': ('tls', 'ipsec', 'cip_security', 'ssh'),
           'authentication': ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'ssh')}
REDIRECTS = (301, 302, 303, 307, 308)
RETRY_STATUS = (429, 502, 503, 504)
KEEP_HEADERS = ('content-type', 'content-length', 'content-disposition', 'content-language', 'last-modified', 'etag', 'date')
KNOWN_KEYS = {'sampling', 'title', 'max_depth', 'max_pages_per_product', 'delay_seconds', 'timeout_seconds', 'max_bytes',
              'follow_pattern', 'robots_follow_redirects', 'retries', 'products'}
RELEVANT = re.compile(r'secur|cyber|manual|instruction|guide|communicat|protocol|dnp|data\s?sheet', re.I)
# Soft hyphens, zero-width characters and trademark signs vanish; typographic hyphens become '-'.
TIDY = {**dict.fromkeys(map(ord, '\u00ad\u200b\u200c\u200d\u2060\ufeff\u2122\u00ae\u2120')),
        **dict.fromkeys(map(ord, '\u2010\u2011\u2012\u2013\u2212'), '-')}


def digest(b):
    return hashlib.sha256(b).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(path, obj):
    # UTF-8 and LF on every platform; replaced atomically so an interrupted checkpoint is never half a file.
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    for attempt in range(5):
        try:
            return os.replace(tmp, path)
        except PermissionError:  # Sync clients and scanners briefly lock freshly written files on Windows.
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def header(headers, name):
    return next((v for k, v in headers.items() if k.lower() == name), '')


def norm(text):
    """Matching copy only: stored segment text stays exactly as extracted."""
    text = unicodedata.normalize('NFKC', text.translate(TIDY))  # Before NFKC, which would turn a trademark sign into "TM".
    return re.sub(r'([a-z])-[ \t]*\r?\n[ \t]*([a-z])', r'\1\2', text)


def squash(text):
    return ' '.join(norm(text).split())


def loose(text):
    # For matching a quote to its source: a hyphen at a PDF line break may or may not belong to the word,
    # so "self-signed", "self- signed" and "selfsigned" are treated as the same words.
    return re.sub(r'(?<=[a-z])-\s?(?=[a-z])', '', squash(text))


def lead_type(feature):
    # A statement is something a document says in so many words. It is never a measurement of how equipment is deployed.
    return 'capability' if feature in CAPABILITIES else 'statement' if feature in STATEMENTS else 'related'


STOP = re.compile(r"""(?<=[.!?])(["')\]]*)\s+(?=[A-Z0-9"'(\[])""")


def passage(text, start, end, before=220, after=350, slack=240):
    """Window around a match, widened to sentence boundaries so a reviewer reads whole sentences."""
    a, b = max(0, start - before), min(len(text), end + after)
    head = tail = ''
    if a:
        earlier = [m.end() for m in STOP.finditer(text, max(0, a - slack), a)]
        later = [m.end() for m in STOP.finditer(text, a, start)]
        if earlier:
            a = earlier[-1]
        elif a - slack <= 0:
            a = 0
        elif later:
            a = later[0]
        else:
            head = '[...] '
    if b < len(text):
        later = [m.end(1) for m in STOP.finditer(text, b, min(len(text), b + slack))]
        earlier = [m.end(1) for m in STOP.finditer(text, end, b)]
        if later:
            b = later[0]
        elif b + slack >= len(text):
            b = len(text)
        elif earlier:
            b = earlier[-1]
        else:
            tail = ' [...]'
    return head + text[a:b].strip() + tail


def clip(text, limit=300):
    return text if len(text) <= limit else text[:limit].rsplit(' ', 1)[0] + ' [...]'


def text_digest(segments):
    # Stable across refetches of a dynamic page whose markup changes but whose wording does not.
    return digest('\n'.join(squash(s['text']) for s in segments if s['text'].strip()).encode())


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
            for _ in range(6):  # RFC 9309 asks crawlers to follow at least five consecutive redirects.
                status, headers, body = self.raw(url)
                if status not in REDIRECTS or not self.config.get('robots_follow_redirects'):
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
                continue
            if status != 200:
                raise ValueError(f'HTTP {status}')
            return {'final_url': url, 'sha256': self.store(body), 'bytes': len(body),
                    'headers': {k: v for k, v in headers.items() if k.lower() in KEEP_HEADERS},
                    'robots_basis': self.robots.get(urlsplit(url).netloc, {}).get('basis'),
                    'redirect_chain': chain, 'retrieved_at': now()}, body
        raise ValueError('too many redirects')


# noscript is deliberately kept: it is the fallback a client without JavaScript, like this one, is meant to read.
SKIP = ('script', 'style', 'nav', 'footer', 'svg', 'select')
HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
BLOCKS = HEADINGS + ('p', 'div', 'li', 'br', 'tr', 'table', 'dt', 'dd', 'pre', 'section', 'article', 'title')


INLINE = re.compile(r'display\s*:\s*inline', re.I)


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.links, self.skip, self.open = [], [], 0, []
        self.buf, self.kind, self.heading, self.title, self.anchor = [], None, '', '', None

    def flush(self):
        text = ' '.join(''.join(self.buf).split())
        self.buf = []
        if text:
            if self.kind == 'title' and not self.title:
                self.title = text
            if self.kind == 'heading':
                self.heading = text
            self.blocks.append((text, '' if self.kind else self.heading))

    def end_anchor(self):
        if self.anchor:
            self.links.append((self.anchor[0], ' '.join(''.join(self.anchor[1]).split())))
            self.anchor = None

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag == 'a':
            self.end_anchor()
            href = (dict(attrs).get('href') or '').strip()
            # Site-wide navigation links say nothing about the product on this page.
            if href and not self.skip:
                self.anchor = [href, []]
        if tag in ('td', 'th') and ''.join(self.buf).strip():
            self.buf.append(' | ')
        if tag in BLOCKS:
            # Some sites style a div as inline text. Breaking there cuts one sentence into several blocks.
            inline = tag not in HEADINGS + ('br', 'title') and bool(INLINE.search(dict(attrs).get('style') or ''))
            if tag != 'br':
                self.open.append((tag, inline))
            if not inline:
                self.flush()
                self.kind = 'heading' if tag in HEADINGS else 'title' if tag == 'title' else self.kind

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag == 'a':
            self.end_anchor()
        if tag in BLOCKS:
            inline = False
            for j in range(len(self.open) - 1, -1, -1):
                if self.open[j][0] == tag:
                    inline = self.open[j][1]
                    del self.open[j:]  # Also drops tags left unclosed inside this one.
                    break
            if not inline:
                self.flush()
                if tag in HEADINGS or tag == 'title':
                    self.kind = None

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)
            if self.anchor:
                self.anchor[1].append(data)


def outline(pdf):
    """Page index -> most recent bookmark at or before it. Bookmarks are optional and often malformed."""
    marks = []

    def walk(items):
        for item in items:
            if isinstance(item, list):
                walk(item)
            else:
                number = pdf.get_destination_page_number(item)
                if number is not None:
                    marks.append((number, ' '.join(str(item.title).split())))
    try:
        walk(pdf.outline)
    except Exception:
        return {}
    marks.sort(key=lambda m: m[0])
    titles, current, j = {}, '', 0
    for i in range(len(pdf.pages)):
        while j < len(marks) and marks[j][0] <= i:
            current, j = marks[j][1], j + 1
        if current:
            titles[i] = current
    return titles


MARKER = re.compile(r'date\s+code|publication\s+date|last\s+update|current\s+version|\brevision\b|\u00a9'
                    r'|copyright\s+(?:\(c\)|\d{4})', re.I)


def hints(segments):
    """Snippets around revision and date markers. Aids only: the reviewer decides what identifies the document."""
    found, keys = [], set()
    for i, segment in enumerate(segments):
        text = ' '.join(norm(segment['text']).split())
        for m in MARKER.finditer(text):
            key = text[m.start():m.end() + 24].lower()
            if key in keys:
                continue
            keys.add(key)
            snippet = text[max(0, m.start() - 60):m.end() + 60]
            # A table label and its value are often neighbouring blocks.
            if segment['location'].startswith('html-block') and not re.search(r'\w', text[m.end():]) and i + 1 < len(segments):
                snippet += ' ' + ' '.join(segments[i + 1]['text'].split())[:60]
            found.append(snippet)
            if len(found) == 8:
                return found
    return found


def parse(body, headers):
    """Segments, (href, anchor text) links and document facts for the source record."""
    if b'%PDF' in body[:1024]:
        from pypdf import PdfReader
        pdf = PdfReader(io.BytesIO(body))
        marks, segs, errors = outline(pdf), [], []
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text() or ''
            except Exception as e:  # One unreadable page must not hide the rest of a manual.
                text = ''
                errors.append({'location': f'pdf-page:{i + 1}', 'error': f'{type(e).__name__}: {e}'})
            segs.append({'location': f'pdf-page:{i + 1}', 'text': text, **({'heading': marks[i]} if i in marks else {})})
        facts = {'kind': 'pdf', 'pages': len(segs), 'empty_pages': sum(not s['text'].strip() for s in segs),
                 'page_errors': errors, 'encrypted': bool(pdf.is_encrypted)}
        try:
            meta = pdf.metadata or {}
            facts.update({k: ' '.join(str(meta[v]).split()) for k, v in
                          (('title', '/Title'), ('pdf_created', '/CreationDate'), ('pdf_modified', '/ModDate')) if v in meta})
        except Exception:
            pass
        return segs, [], dict(facts, document_hints=hints(segs))
    ct = header(headers, 'content-type')
    if 'html' not in ct.lower():
        raise ValueError('unsupported content type: ' + ct)
    charset = re.search(r'charset=([\w-]+)', ct)
    try:
        text = body.decode(charset[1] if charset else 'utf-8', 'replace')
    except LookupError:
        text = body.decode('utf-8', 'replace')
    page = TextHTML()
    page.feed(text)
    page.close()
    page.end_anchor()
    page.flush()
    segs = [{'location': f'html-block:{i + 1}', 'text': t, **({'heading': h} if h else {})}
            for i, (t, h) in enumerate(page.blocks)]
    return segs, page.links, {'kind': 'html', 'title': page.title, 'document_hints': hints(segs)}


def extract(body, headers):
    segs, links, _ = parse(body, headers)
    return segs, [href for href, _ in links]


def alias_pattern(aliases):
    if not aliases:
        return None
    return re.compile('(?<![A-Za-z0-9])(?:' + '|'.join(re.escape(a) for a in aliases) + ')(?![A-Za-z0-9])', re.I)


def suggest_doc_type(title, url, segments):
    """A guess from the title, URL and opening text. A reviewer confirms the type in the source notes."""
    name = f'{title} {url}'
    opening = ' '.join(squash(s['text']) for s in segments[:3])[:3000]
    near = f'{name} {opening[:400]}'
    if re.search(r'device\s+profile', f'{name} {opening}', re.I) and re.search(r'\bDNP', f'{name} {opening}', re.I):
        return 'device_profile'
    if re.search(r'security\s+advisory|\bSSA-\d|\bICSA-\d', near, re.I):
        return 'advisory'
    if re.search(r'conformance\s+statement|\bPICS\b|\bPIXIT\b', near, re.I):
        return 'conformance_statement'
    if re.search(r'secur|hardening', near, re.I) and re.search(r'guide|white\s+paper|technique|hardening', near, re.I):
        return 'security_guide'
    if re.search(r'manual|user\s+guide|instruction|/docs?/', near, re.I):
        return 'manual'
    if re.search(r'data\s?sheet|brochure|flyer', near, re.I):
        return 'datasheet'
    return 'product_page' if segments and segments[0]['location'].startswith('html-block') else ''


PROFILE_ITEM = re.compile(r'(?m)^[ \t]*(1\.12\.\d{1,2})[ \t]+(?=\S)')
# A leading X or a checked-box character. Vendors mark options in different ways, so this is a heuristic.
MARKED = re.compile(r'(?m)^[ \t]*(?:[Xx]|[\u2611\u2612\u2713\u2714])[ \t]+(\S.*?)[ \t]*$')


def profile_items(segments):
    """Section 1.12, Security Parameters, of a DNP3 Device Profile: one entry per numbered item, text kept whole."""
    opening = ' '.join(s['text'] for s in segments[:3])
    if not (re.search(r'device\s+profile', opening, re.I) and re.search(r'\bDNP', opening, re.I)):
        return []
    items = []
    for segment in segments:
        # The section heading repeats on each of its pages. The contents page has it too, followed by dot leaders.
        head = re.search(r'1\.12[ \t]+SECURITY[ \t]+PARAMETERS(?![ \t]*\.{3})', segment['text'], re.I)
        if not head:
            continue
        body = segment['text'][head.end():]
        starts = list(PROFILE_ITEM.finditer(body))
        carried = body[:starts[0].start()] if starts else body
        if items and carried.strip():  # An item that runs on from the previous page.
            items[-1]['raw'] += '\n' + carried
        for n, m in enumerate(starts):
            raw = body[m.end():starts[n + 1].start() if n + 1 < len(starts) else len(body)]
            items.append({'item': m[1], 'location': segment['location'], 'raw': raw})
    for item in items:
        raw = item.pop('raw')
        title = raw.split(':', 1)[0] if ':' in raw[:200] else raw.strip().split('\n', 1)[0]
        item.update(title=' '.join(title.split()), text=' '.join(raw.split()),
                    marked=[' '.join(x.split()) for x in MARKED.findall(raw)], marks='heuristic')
    return items


def candidates(source, segments, aliases=()):
    hits, alias = [], alias_pattern(aliases)
    texts = [norm(s['text']) for s in segments]
    for item in profile_items(segments):
        # The most direct statements a vendor makes about DNP3 security, so each item is a lead of its own.
        about = 'tls' if re.search(r'\bTLS\b|cipher|certificate', item['title'] + ' ' + item['text'], re.I) else 'dnp3_secure_authentication'
        hits.append({'id': digest((source['id'] + item['location'] + 'profile' + item['item']).encode())[:20],
                     'source_id': source['id'], 'product_id': source['product_id'], 'feature': about,
                     'lead_type': 'profile', 'location': item['location'], 'profile_item': item['item'],
                     'title': item['title'], 'matched': item['marked'], 'context': clip(norm(item['text']), 900),
                     'match_count': 1, 'status': 'unreviewed'})
    for i, segment in enumerate(segments):
        text = texts[i]
        for feature, pattern in LEADS.items():
            found = list(pattern.finditer(text))
            if feature in STATEMENTS:
                found = [m for m in found if not HYPOTHETICAL.search(text[max(0, m.start() - 80):m.start()])]
            if not found:
                continue
            if feature in NEAR:
                # An HTML block is one line, so the qualifying term may sit in a neighbouring block or the heading.
                block = segment['location'].startswith('html-block')
                around = ' '.join(texts[max(0, i - 3):i + 4] + [segment.get('heading', '')]) if block else text
                if not NEAR[feature].search(around):
                    continue
            match = found[0]
            cid = digest((source['id'] + segment['location'] + feature).encode())[:20]
            terms = {}
            for m in found:
                terms.setdefault(' '.join(m.group(0).split()).lower(), ' '.join(m.group(0).split()))
            hit = {'id': cid, 'source_id': source['id'], 'product_id': source['product_id'],
                   'feature': feature, 'lead_type': lead_type(feature), 'location': segment['location'],
                   # The words that matched, so SFTP is never read as an SSH statement nor VPN as IPsec.
                   'matched': list(terms.values())[:12],
                   'context': passage(text, match.start(), match.end()),
                   'match_count': len(found), 'status': 'unreviewed'}
            if segment['location'].startswith('html-block'):
                # A heading or table label alone decides nothing; its neighbours travel with it.
                hit['context_before'] = [clip(t) for t in texts[max(0, i - 2):i]]
                hit['context_after'] = [clip(t) for t in texts[i + 1:i + 3]]
            if segment.get('heading'):
                hit['heading'] = segment['heading']
            if alias:
                # A search aid for scope review, not proof that the passage applies to the model.
                hit['model_mentioned'] = bool(alias.search(text))
            hits.append(hit)
    return hits


def validate_config(cfg):
    """Structural errors stop the run before any request; everything else comes back as warnings."""
    if not isinstance(cfg.get('sampling'), str) or not cfg['sampling'].strip():
        raise ValueError('config needs a sampling statement')
    if not isinstance(cfg.get('products'), list) or not cfg['products']:
        raise ValueError('config needs a products list')
    try:
        re.compile(cfg.get('follow_pattern', ''))
    except re.error as e:
        raise ValueError(f'follow_pattern is not a valid regular expression: {e}')
    warnings, ids = [f'unknown config key: {k}' for k in sorted(set(cfg) - KNOWN_KEYS)], set()
    for p in cfg['products']:
        pid = p.get('id') if isinstance(p, dict) else None
        if not isinstance(pid, str) or not pid or pid in ids:
            raise ValueError(f'product id missing or duplicated: {pid!r}')
        ids.add(pid)
        for key, required in (('domains', True), ('seeds', True), ('aliases', False)):
            value = p.get(key, None if required else [])
            if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
                raise ValueError(f'{pid}: {key} must be a list of strings')
        warnings += [f'{pid}: missing {k}' for k in ('vendor', 'model', 'category') if not p.get(k)]
        warnings += [f'{pid}: seed is not an allowlisted public HTTPS URL: {u}' for u in p['seeds'] if not allowed(u, p['domains'])]
        if not p['seeds']:
            warnings.append(f'{pid}: no seeds, so every cell stays unknown')
    return warnings


def link_score(url, text, alias):
    blob = url + ' ' + text
    return len({m.lower() for m in RELEVANT.findall(blob)}) + (2 if alias and alias.search(blob) else 0)


def describe(rec, segs, facts, out, alias):
    """What the extracted text says about the document. A crawl and a rebuild record it the same way."""
    rec.update(facts, text_sha256=text_digest(segs),
               doc_type_suggested=suggest_doc_type(facts.get('title') or '', rec.get('final_url') or rec['url'], segs))
    if alias:
        rec['model_mentions'] = sum(bool(alias.search(norm(s['text']))) for s in segs)
    items = profile_items(segs)
    rec.pop('profile_items', None)
    if items:
        rec['profile_items'] = len(items)
        dump(out / (rec['id'] + '.profile.json'), items)
    dump(out / (rec['id'] + '.segments.json'), segs)


def save_leads(out, hits):
    # Statements get their own file so nobody reads them as product capability leads.
    dump(out / 'candidates.json', [h for h in hits if h['lead_type'] != 'statement'])
    dump(out / 'statement_leads.json', [h for h in hits if h['lead_type'] == 'statement'])


def load_leads(run):
    return [h for name in ('candidates.json', 'statement_leads.json') if (run / name).exists() for h in load(run / name)]


def finish(out, cfg, config_sha256, sources, hits, warnings, **extra):
    """Manifest and the two templates a reviewer fills in. Only a finished run has a manifest."""
    dump(out / 'manifest.json', {'tool_version': VERSION, 'finished_at': now(),
        'config_sha256': config_sha256, 'python': sys.version,
        'script_sha256': digest(Path(__file__).read_bytes()),
        'complete': True, 'source_count': len(sources),
        'candidate_count': sum(h['lead_type'] != 'statement' for h in hits),
        'lead_counts': dict(Counter(h['lead_type'] for h in hits)),
        'source_status': dict(Counter(s['status'] for s in sources)),
        'config_warnings': warnings, 'sampling': cfg['sampling'], **extra})
    dump(out / 'review_template.json',
         [{'product_id': p['id'], 'feature': feature, 'status': 'unknown',
           'source_ids': [], 'source_hashes': {}, 'location': '', 'protocol': '',
           'interface': '', 'interface_class': '', 'firmware': 'not established', 'implementation': 'not established',
           'conditions': '', 'evidence': [], 'rationale': '', 'reviewer': '', 'reviewed_at': '', 'review_status': ''}
          for p in cfg['products'] for feature in CAPABILITIES])
    # What a document says about its own number, revision and date is for a person to read off, not for a regex.
    dump(out / 'source_notes_template.json',
         [{'source_id': s['id'], 'product_id': s['product_id'], 'url': s['final_url'], 'title': s.get('title', ''),
           'document_hints': s.get('document_hints', []), 'doc_type_suggested': s.get('doc_type_suggested', ''),
           'doc_type': '', 'document_id': '', 'revision': '', 'document_date': '', 'note': ''}
          for s in sources if s['status'] == 'extracted'])


def crawl(config_path, out, cache, resume=False):
    config_bytes = Path(config_path).read_bytes()
    cfg = json.loads(config_bytes)
    warnings = validate_config(cfg)
    for w in warnings:
        print('config warning:', w, file=sys.stderr)
    import pypdf  # noqa: F401  Fail before the first request, not once per PDF.
    out, cache = Path(out), Path(cache)
    sources, hits, audit = [], [], []
    if resume:
        if (out / 'manifest.json').exists():
            raise ValueError('run is already complete; nothing to resume')
        if load(out / 'config.json') != cfg:
            raise ValueError('resume needs the config the run was started with')
        sources, audit = (load(out / n) if (out / n).exists() else [] for n in ('sources.json', 'requests.json'))
        hits = load_leads(out)
    else:
        out.mkdir(parents=True, exist_ok=False)
        dump(out / 'config.json', cfg)
    f = Fetcher(cfg, cache)
    f.audit = audit
    prior = {(s['product_id'], s['url']): s for s in sources}
    byid = {s['id']: s for s in sources}
    depth_limit, budget = cfg.get('max_depth', 0), cfg.get('max_pages_per_product', 3)
    follow = re.compile(cfg.get('follow_pattern', r'manual|security|datasheet|\.pdf'), re.I)
    # Product provenance remains separate even when a family document is shared.
    for product in cfg['products']:
        aliases = product.get('aliases', [])
        alias = alias_pattern(aliases)
        queue, seen, shas, attempted = [], set(), {}, 0
        for seed in product['seeds']:
            try:
                seed = canonical(seed)
            except ValueError:
                pass  # Kept as written; the fetch below records why it is refused.
            heapq.heappush(queue, (0, 0, len(queue), seed, None))
        order = len(queue)
        while queue:
            depth, _, _, url, via = heapq.heappop(queue)
            if url in seen:
                continue
            seen.add(url)
            rec, links = prior.get((product['id'], url)), []
            fresh = rec is None
            if fresh:
                rec = {'id': digest((product['id'] + url).encode())[:20],
                       'product_id': product['id'], 'url': url, 'depth': depth, 'started_at': now()}
                if via:
                    rec['via'] = via
                # Seeds are always attempted; the budget only limits followed links, and those are recorded too.
                if depth and attempted >= budget:
                    rec.update(status='skipped', error='page budget reached before this link')
                    byid[via]['links_skipped'] = byid[via].get('links_skipped', 0) + 1
                else:
                    try:
                        meta, body = f.fetch(url, product['domains'])
                        rec.update(meta)
                        if meta['sha256'] in shas:
                            rec.update(status='duplicate', duplicate_of=shas[meta['sha256']])
                        else:
                            segs, links, facts = parse(body, meta['headers'])
                            if not any(s['text'].strip() for s in segs):
                                raise ValueError('no extractable text; OCR/manual review required')
                            describe(rec, segs, facts, out, alias)
                            rec['status'] = 'extracted'
                            hits.extend(candidates(rec, segs, aliases))
                    except Exception as e:
                        rec.update(status='failed', error=f'{type(e).__name__}: {e}')
                sources.append(rec)
                byid[rec['id']] = rec
            elif rec['status'] == 'extracted' and depth < depth_limit:
                # Resumed run: rebuild this page's links from the retained bytes instead of the network.
                links = parse((cache / rec['sha256']).read_bytes(), rec['headers'])[1]
            if rec['status'] != 'skipped':
                attempted += 1
            if rec['status'] == 'extracted':
                shas.setdefault(rec['sha256'], rec['id'])
                if fresh:
                    rec['links_found'] = len(links)
                if depth < depth_limit:
                    matched = set()
                    for href, text in links:
                        try:
                            full = canonical(urljoin(rec['final_url'], href))
                        except ValueError:
                            continue
                        if full in seen or full in matched:
                            continue  # Already attempted, e.g. a fragment link back to this page.
                        if allowed(full, product['domains']) and follow.search(full + ' ' + text):
                            matched.add(full)
                            heapq.heappush(queue, (depth + 1, -link_score(full, text, alias), order, full, rec['id']))
                            order += 1
                    if fresh:
                        rec['links_matched'] = len(matched)
            if fresh:
                # Checkpoints survive interrupted runs; incomplete runs are never called complete.
                dump(out / 'sources.json', sources)
                save_leads(out, hits)
                dump(out / 'requests.json', f.audit)
                print(product['id'], rec['status'], url, flush=True)
    # Written once more so a run without any seeds still has all its files.
    dump(out / 'sources.json', sources)
    save_leads(out, hits)
    dump(out / 'requests.json', f.audit)
    finish(out, cfg, digest(config_bytes), sources, hits, warnings)


def rebuild(run, cache, dest):
    """Re-derives segments and leads from retained bytes with this tool version. No network; hashes are unchanged."""
    run, cache, dest = Path(run), Path(cache), Path(dest)
    verify(run, cache)
    cfg = load(run / 'config.json')
    made = load(run / 'manifest.json') if (run / 'manifest.json').exists() else {}
    dest.mkdir(parents=True, exist_ok=False)
    dump(dest / 'config.json', cfg)
    aliases = {p['id']: p.get('aliases', []) for p in cfg['products']}
    sources, hits = [], []
    for s in load(run / 'sources.json'):
        if s['status'] == 'extracted':
            segs, _, facts = parse((cache / s['sha256']).read_bytes(), s['headers'])
            describe(s, segs, facts, dest, alias_pattern(aliases.get(s['product_id'])))
            hits.extend(candidates(s, segs, aliases.get(s['product_id'], [])))
        sources.append(s)
    dump(dest / 'sources.json', sources)
    save_leads(dest, hits)
    dump(dest / 'requests.json', load(run / 'requests.json') if (run / 'requests.json').exists() else [])
    finish(dest, cfg, made.get('config_sha256'), sources, hits, made.get('config_warnings', []),
           rebuilt_from={'run': str(run), 'tool_version': made.get('tool_version'), 'finished_at': made.get('finished_at')})
    print(f'Rebuilt {sum(s["status"] == "extracted" for s in sources)} sources into {dest} with tool version {VERSION}')


def cited(segments, location):
    """Text at a location: one segment, or a short run of consecutive ones written as html-block:10-13."""
    m = re.fullmatch(r'(html-block:|pdf-page:)(\d+)(?:-(\d+))?', location or '')
    if not m or not int(m[2]) <= int(m[3] or m[2]) < int(m[2]) + 10:
        return None
    text = {x['location']: x['text'] for x in segments}
    parts = [text.get(m[1] + str(n)) for n in range(int(m[2]), int(m[3] or m[2]) + 1)]
    return None if None in parts else ' '.join(parts)


def validate_reviews(rows, sources, products, segments=None, require_evidence=False):
    byid = {s['id']: s for s in sources}
    seen, classes = set(), {}
    for r in rows:
        key = r['product_id'], r['feature']
        scope = squash(r.get('interface') or '').lower()
        # One capability may be recorded once per interface: TLS for DNP3 and TLS for a web page are different findings.
        if key + (scope,) in seen or key[0] not in products or key[1] not in CAPABILITIES:
            raise ValueError(f'duplicate/unknown review key: {key}')
        seen.add(key + (scope,))
        if r['status'] not in STATUSES:
            raise ValueError(f'invalid status: {key}')
        if not all(r.get(k) for k in ('reviewer', 'reviewed_at', 'rationale')):
            raise ValueError(f'review identity/date/rationale required, including unknowns: {key}')
        if r['status'] != 'unknown' and not r['source_ids']:
            raise ValueError(f'claim requires source evidence: {key}')
        if r['status'] != 'unknown' and not all(r.get(k) for k in ('location','protocol','interface','firmware','implementation')):
            raise ValueError(f'claim scope is incomplete: {key}')
        kind = r.get('interface_class') or ''
        if kind not in INTERFACE_CLASSES + (('',) if r['status'] == 'unknown' else ()):
            raise ValueError(f'claim needs interface_class, one of {", ".join(INTERFACE_CLASSES)}: {key}')
        if scope and kind and classes.setdefault((key[0], scope), kind) != kind:
            raise ValueError(f'one interface is filed under two interface classes: {key}')
        if r['status'] == 'conditional' and not r.get('conditions'):
            raise ValueError(f'conditional result must state its conditions: {key}')
        if (r.get('review_status') or 'draft') not in REVIEW_STATUSES:
            raise ValueError(f'review_status must be one of {", ".join(REVIEW_STATUSES)}: {key}')
        for sid in r['source_ids']:
            s = byid.get(sid)
            if not s or s['status'] != 'extracted' or s['product_id'] != r['product_id']:
                raise ValueError(f'missing/failed/wrong-product source: {key}')
            if r['source_hashes'].get(sid) != s['sha256']:
                raise ValueError(f'review/source hash mismatch: {key}')
        evidence = r.get('evidence') or []
        if require_evidence and r['status'] != 'unknown' and not evidence:
            raise ValueError(f'claim requires a verbatim evidence quote: {key}')
        # A quote proves the words are in the cited passage; whether they support the claim stays the reviewer's call.
        for e in evidence:
            wanted = loose(e.get('quote', ''))
            if e.get('source_id') not in r['source_ids']:
                raise ValueError(f'evidence cites a source outside this review: {key}')
            if len(wanted) < 20:
                raise ValueError(f'evidence quote too short to identify a passage: {key}')
            if segments:
                text = cited(segments(e['source_id']), e.get('location'))
                if text is None or wanted not in loose(text):
                    raise ValueError(f"evidence quote not found at {e.get('location')} of source {e['source_id']}: {key}")


def untouched(row):
    """A template row nobody has filled in. It is not a finding: it is left out and counted as not reviewed."""
    blank = ('reviewer', 'reviewed_at', 'rationale', 'source_ids', 'source_hashes', 'evidence', 'location', 'protocol',
             'interface', 'interface_class', 'conditions', 'review_status')
    return row.get('status') == 'unknown' and not any(row.get(k) for k in blank)


COLUMNS = ('Manufacturer', 'Model', 'Firmware', 'Protocol / interface', 'Encryption', 'Authentication', 'Conditions',
           'Evidence', 'Review status')
MARK = {'supported': 'S', 'conditional': 'C', 'explicitly_unsupported': 'X', 'unknown': '?', 'conflicting': '!'}
RANK = ('supported', 'conditional', 'conflicting', 'explicitly_unsupported')


def report(run, review_path, dest, require_evidence=False, source_notes=None):
    run, dest = Path(run), Path(dest)
    cfg, sources, rows = load(run / 'config.json'), load(run / 'sources.json'), load(review_path)
    products = {p['id']: p for p in cfg['products']}
    # Lets a review proceed in stages. A partly filled row is still an error, never silently dropped.
    blank = sum(map(untouched, rows))
    rows = [r for r in rows if not untouched(r)]
    validate_reviews(rows, sources, products, lambda sid: load(run / (sid + '.segments.json')), require_evidence)
    byid = {s['id']: s for s in sources}
    notes = {n['source_id']: n for n in (load(source_notes) if source_notes else [])}
    if set(notes) - set(byid):
        raise ValueError(f'source notes name sources that are not in this run: {sorted(set(notes) - set(byid))}')
    wrong = sorted({n.get('doc_type') for n in notes.values() if n.get('doc_type')} - set(DOC_TYPES))
    if wrong:
        raise ValueError(f'source notes use a doc_type outside {", ".join(DOC_TYPES)}: {wrong}')
    dest.mkdir(parents=True, exist_ok=True)
    # The source manifest: URL, retrieval time and hash come from the crawl, the document's own number and date from a reviewer.
    refs, cite = {}, {}
    for s in sources:
        if s['status'] == 'extracted':
            refs[s['id']] = s['ref'] = f'S{len(refs) + 1}'
            s['document'] = {k: notes.get(s['id'], {}).get(k, '')
                             for k in ('doc_type', 'document_id', 'revision', 'document_date', 'note')}
            # What kind of document a quote comes from travels with every reference to it.
            cite[s['id']] = f"{s['ref']} [{s['document']['doc_type'].replace('_', ' ') or 'type not confirmed'}]"
    dump(dest / 'findings.json', rows)
    dump(dest / 'sources.json', sources)
    dump(dest / 'evidence_index.json', [
        {'product_id': r['product_id'], 'feature': r['feature'], 'status': r['status'], 'interface': r.get('interface', ''),
         'interface_class': r.get('interface_class', ''), 'source_id': e['source_id'], 'source_ref': refs[e['source_id']],
         'doc_type': byid[e['source_id']]['document']['doc_type'],
         'url': byid[e['source_id']]['final_url'], 'sha256': byid[e['source_id']]['sha256'],
         'location': e['location'], 'quote': e['quote'], 'retrieved_at': byid[e['source_id']].get('retrieved_at')}
        for r in rows for e in r.get('evidence') or []])
    # Lead counts say how much text mentioned a term. They are never device counts, and statements are kept apart.
    leads = {p: {t: Counter() for t in ('capability', 'related', 'statement', 'profile')} for p in products}
    for h in load_leads(run):
        leads[h['product_id']][h.get('lead_type') or lead_type(h['feature'])][h['feature']] += 1
    dump(dest / 'candidate_counts.json', {p: {t: {'total': sum(c.values()), 'by_group': dict(sorted(c.items()))}
                                              for t, c in kinds.items()} for p, kinds in leads.items()})
    columns = ['product_id','vendor','model','category','feature','status','protocol','interface','interface_class',
               'firmware','implementation','conditions','location','rationale','reviewer','reviewed_at','review_status',
               'source_urls','source_hashes','evidence']
    with (dest / 'findings.csv').open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=columns)
        w.writeheader()
        for r in rows:
            p = products[r['product_id']]
            item = {k: r.get(k, '') for k in columns}
            item.update({k: p.get(k, '') for k in ('vendor','model','category')})
            item['source_urls'] = ' | '.join(byid[s]['final_url'] for s in r['source_ids'])
            item['source_hashes'] = json.dumps(r['source_hashes'], sort_keys=True)
            item['evidence'] = json.dumps(r.get('evidence') or [], ensure_ascii=False)
            w.writerow(item)

    def md(x):
        return str(x).replace('|', '/').replace('\n', ' ')

    def flat(x):
        return ' '.join(str(x).split())

    def model(pid):
        return md(products[pid].get('model') or pid)

    def category(pid):
        return products[pid].get('category') or 'uncategorised'

    def label(status):
        return status.replace('_', ' ')

    def scope(r):
        return squash(r.get('interface') or '').lower()

    claims = [r for r in rows if r['status'] != 'unknown']
    cell = {(r['product_id'], r['feature'], scope(r)): r for r in rows}
    reviewed = {(r['product_id'], r['feature']) for r in rows}
    expected = len(products) * len(CAPABILITIES)

    def prop(pid, where, members, feature):
        """What the review says about one property on one interface. Mechanism rows are pointed to, never read as a result."""
        r = cell.get((pid, feature, where)) or cell.get((pid, feature, ''))
        if r and r['status'] != 'unknown':
            return f"{label(r['status'])}: {flat(r['protocol'])}"
        see = [f"{m['feature']} ({label(m['status'])})" for m in members if m['feature'] in RELATES[feature]]
        return ('unknown' if r else 'not assessed' if see else 'not reviewed') + ('; see ' + ', '.join(see) if see else '')

    # One row per product and interface. Repeated keyword matches cannot add rows; only reviewed findings can.
    table = []
    for pid, p in products.items():
        found = {}
        for r in claims:
            if r['product_id'] == pid:
                found.setdefault((r['interface_class'], scope(r)), []).append(r)
        found = sorted(found.items(), key=lambda g: INTERFACE_CLASSES.index(g[0][0]))
        if not found or found[0][0][0] != 'control_protocol':
            # The study asks about control traffic, so its absence is stated instead of left out.
            found.insert(0, (('control_protocol', ''), []))
        for (kind, where), members in found:
            signed = members or [r for r in rows if r['product_id'] == pid and not scope(r)]
            used = list(dict.fromkeys(sid for m in members for sid in m['source_ids']))
            table.append({
                'Manufacturer': p.get('vendor', ''), 'Model': p.get('model') or pid, 'Category': category(pid),
                'Interface class': kind,
                'Firmware': '; '.join(dict.fromkeys(flat(m['firmware']) for m in members)) or 'not established',
                'Protocol / interface': (f"{flat(members[0]['interface'])} ({kind.replace('_', ' ')})" if members
                                         else 'No control protocol established from the examined sources'),
                'Encryption': prop(pid, where, members, 'encryption'),
                'Authentication': prop(pid, where, members, 'authentication'),
                'Conditions': ('; '.join(dict.fromkeys(flat(m['conditions']) for m in members if m.get('conditions')))
                               or ('none stated' if members else '-')),
                'Evidence': [(cite[e['source_id']], e['location'], flat(e['quote'])) for m in members for e in m.get('evidence') or []],
                'Review status': '; '.join(dict.fromkeys(f"{m.get('review_status') or 'draft'} ({flat(m['reviewer'])})"
                                                         for m in signed)) or 'not reviewed',
                'Sources': '; '.join(f"{cite[sid]} {byid[sid]['final_url']} sha256:{byid[sid]['sha256']}" for sid in used)})

    def shown(quotes):
        if not quotes:
            return 'none'
        ref, where, text = quotes[0]
        return f'{ref} {where}: "{clip(text, 110)}"' + (f' (+{len(quotes) - 1} more)' if len(quotes) > 1 else '')

    with (dest / 'findings_table.csv').open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=list(COLUMNS[:2]) + ['Category'] + list(COLUMNS[2:4]) + ['Interface class'] + list(COLUMNS[4:]) + ['Sources'])
        w.writeheader()
        for row in table:
            w.writerow(dict(row, Evidence=' || '.join(f'{ref} {where}: "{text}"' for ref, where, text in row['Evidence']) or 'none'))

    def results(pid, feature, kinds):
        return [r['status'] for r in claims if r['product_id'] == pid and r['feature'] == feature and r['interface_class'] in kinds]

    def matrix(pid, feature):
        control, other = results(pid, feature, ('control_protocol',)), results(pid, feature, ('management', 'network'))
        if control:
            return '/'.join(dict.fromkeys(MARK[x] for x in control))
        if other:
            return '(' + '/'.join(dict.fromkeys(MARK[x] for x in other)) + ')'
        return '?' if (pid, feature) in reviewed else '-'

    def bucket(pid, feature):
        control = results(pid, feature, ('control_protocol',))
        if control:
            return min(control, key=RANK.index)
        if results(pid, feature, ('management', 'network')):
            return 'other'
        return 'unknown' if (pid, feature) in reviewed else None

    totals = Counter(s['status'] for s in sources)
    line = (f"Products/families in seed inventory: {len(products)}. Sources attempted: {len(sources) - totals['skipped']}; "
            f"extracted: {totals['extracted']}; failed: {totals['failed']}")
    if totals['duplicate']:
        line += f"; duplicate of another source: {totals['duplicate']}"
    if totals['skipped']:
        line += f"; matched links not followed (page budget): {totals['skipped']}"
    text = [f"# {cfg.get('title', 'IED security documentation survey')}", '',
            f"Sampling: {cfg['sampling']}", '', line + '.', '',
            'This measures documented capabilities, not enabled settings, installed-base coverage or plaintext prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. Capability categories overlap, so counts below are review cells and must not be added up as devices.', '',
            'Reviewers on record: ' + ('; '.join(f'{md(name)} ({n} rows)' for name, n in Counter(r['reviewer'] for r in rows).items()) or 'none') + '.', '',
            '## Findings by product and interface', '',
            'One row per product and interface. Encryption and authentication are stated for that interface only; a result for a management interface says nothing about control traffic. Full quotes are under "Findings and evidence" and in findings_table.csv; source references are resolved under "Sources examined".', '',
            '| ' + ' | '.join(COLUMNS) + ' |', '|' + '---|' * len(COLUMNS)]
    text.extend('| ' + ' | '.join(md(shown(row[c]) if c == 'Evidence' else row[c]) for c in COLUMNS) + ' |' for row in table)
    order = ['supported', 'conditional', 'explicitly_unsupported', 'conflicting', 'other', 'unknown', None]
    text.extend(['', '## Counts by category', '',
                 'Products, not leads or table rows. Each product is counted once per capability, under its most favourable documented status for a control protocol. "Other interface only" means a result exists for a management or network interface but none for a control protocol. The last column is the denominator.', '',
                 '| Category | Capability | Supported | Conditional | Explicitly unsupported | Conflicting | Other interface only | Unknown | Not reviewed | Products |',
                 '|---|---|---|---|---|---|---|---|---|---|'])
    for stratum in dict.fromkeys(map(category, products)):
        members = [pid for pid in products if category(pid) == stratum]
        for c in CAPABILITIES:
            tally = Counter(bucket(pid, c) for pid in members)
            text.append(f'| {md(stratum)} | {c} | ' + ' | '.join(str(tally[k]) for k in order) + f' | {len(members)} |')
    text.extend(['', '## Capability matrix', '',
                 'S supported, C conditional, X explicitly unsupported, ? unknown, ! conflicting, - not reviewed. A mark in parentheses is established only for a management or network interface, not for a control protocol.', '',
                 '| Product | Category | ' + ' | '.join(CAPABILITIES) + ' |', '|---|---|' + '---|' * len(CAPABILITIES)])
    text.extend(f'| {model(pid)} | {md(category(pid))} | ' + ' | '.join(matrix(pid, c) for c in CAPABILITIES) + ' |' for pid in products)
    if claims:
        # The scope and the quoted words sit next to each result, so a second reader can check them without the CSV.
        text.extend(['', '## Findings and evidence', '',
                     'Every row with a result other than unknown. Quotes are verbatim from the cited location of the retained source.'])
        for r in claims:
            text.extend(['', f"### {model(r['product_id'])}: {r['feature']} ({label(r['status'])})", '',
                         f"- Interface: {flat(r['interface'])} ({r['interface_class'].replace('_', ' ')})"])
            text.extend(f'- {name}: {flat(r[key])}' for name, key in
                        (('Protocol', 'protocol'), ('Firmware', 'firmware'), ('Implementation', 'implementation'),
                         ('Conditions', 'conditions'), ('Location', 'location')) if r.get(key))
            text.extend(f'- Evidence, {e["location"]}: "{flat(e["quote"])}"' for e in r.get('evidence') or [])
            text.extend(f"- Source: {cite[sid]} {byid[sid]['final_url']}" for sid in r['source_ids'])
            text.append(f"- Review status: {r.get('review_status') or 'draft'} ({flat(r['reviewer'])})")
    text.extend(['', '## Reviewed rows', '', '| Product | Capability | Interface | Review result | Scope |', '|---|---|---|---|---|'])
    for r in rows:
        text.append('| ' + ' | '.join(md(x) for x in [model(r['product_id']), r['feature'], flat(r.get('interface') or '') or '-',
                                                     r['status'], r['rationale']]) + ' |')
    unresolved = {pid: [c for c in CAPABILITIES if not any(x in ('supported', 'conditional', 'explicitly_unsupported')
                                                           for x in results(pid, c, INTERFACE_CLASSES))] for pid in products}
    text.extend(['', '## Unresolved cells', '',
                 f'{sum(map(len, unresolved.values()))} of {expected} cells are unknown, conflicting or not reviewed on every interface.', ''])
    text.extend(f"- {model(pid)}: {', '.join(left)}" for pid, left in unresolved.items() if left)
    profiles = [(s, load(run / (s['id'] + '.profile.json'))) for s in sources if s.get('profile_items')]
    if profiles:
        text.extend(['', '## Device profile statements', '',
                     'Read by the tool from section 1.12, Security Parameters, of a DNP3 Device Profile. Marked options are detected by a heuristic and nothing in this table has been reviewed. A finding still needs a review row that quotes the item.', '',
                     '| Product | Source | Item | Title | Options that appear marked | Location |', '|---|---|---|---|---|---|'])
        text.extend(f"| {model(s['product_id'])} | {s['ref']} | {i['item']} | {md(i['title'])} | "
                    f"{md('; '.join(i['marked']) or 'none detected')} | {i['location']} |" for s, items in profiles for i in items)
    text.extend(['', '## Sources examined', '',
                 'Type, number, revision and document date are what a reviewer confirmed or read off the document; "not established" and "suggested" mean nobody has yet. Types are listed in the README from most to least direct about what one product and firmware can do. Titles and PDF dates are what the file says about itself, and a PDF creation date is not necessarily a publication date.', '',
                 '| Ref | Product | Document | Type | Number and revision | Document date | Retrieved | SHA-256 | URL |', '|---|---|---|---|---|---|---|---|---|'])
    for s in sources:
        if s['status'] == 'extracted':
            made = re.match(r'D:(\d{4})(\d{2})(\d{2})', s.get('pdf_created', ''))
            facts = [s.get('title') or 'untitled'] + ([f"{s['pages']} PDF pages"] if s.get('pages') else []) + (['PDF created ' + '-'.join(made.groups())] if made else [])
            doc = s['document']
            kind = doc['doc_type'] or ('suggested: ' + s['doc_type_suggested'] if s.get('doc_type_suggested') else 'not established')
            text.append(f"| {s['ref']} | {model(s['product_id'])} | {md(', '.join(facts))} | {kind.replace('_', ' ')} | "
                        f"{md(', '.join(filter(None, [doc['document_id'], doc['revision'] and 'revision ' + doc['revision']])) or 'not established')} | "
                        f"{md(doc['document_date'] or 'not established')} | {s.get('retrieved_at', '')[:10]} | {s['sha256']} | {md(s['final_url'])} |")
    missing = [s for s in sources if s['status'] in ('failed', 'duplicate')]
    if missing:
        text.extend(['', '## Sources without extracted text', '', '| Product | URL | Outcome |', '|---|---|---|'])
        text.extend(f"| {model(s['product_id'])} | {md(s['url'])} | "
                    f"{md(s.get('error') or 'duplicate of ' + s['duplicate_of'])} |" for s in missing)
    text.extend(['', f'Review coverage: {len(reviewed)}/{expected} product–capability cells. Unreviewed cells carry no result.', '',
                 f"Evidence quotes: {sum(bool(r.get('evidence')) for r in claims)} of {len(claims)} rows with a result other than unknown carry a quote that was checked against the cited passage.", '',
                 'See findings.csv for source URLs, hashes, interface, firmware and review provenance. No population percentages are computed.'])
    (dest / 'REPORT.md').write_text('\n'.join(text) + '\n', encoding='utf-8', newline='\n')
    print(f'Report written to {dest}: {len(reviewed)} of {expected} cells reviewed in {len(rows)} rows'
          + (f'; {blank} untouched template rows left out as not reviewed' if blank else ''))


def verify(run, cache):
    records = load(Path(run) / 'sources.json')
    for r in records:
        if 'sha256' in r:
            p = Path(cache) / r['sha256']
            if not p.exists() or digest(p.read_bytes()) != r['sha256']:
                raise ValueError('missing or changed cached source: ' + r['id'])
    print('All recorded source bytes verified')


def replay(run, cache, dest):
    """Offline re-extraction against exact retained bytes, with hash verification first."""
    run = Path(run)
    made_by = load(run / 'manifest.json').get('tool_version') if (run / 'manifest.json').exists() else VERSION
    if made_by != VERSION:
        # Extraction rules and block numbering are part of a version; a mismatch here is expected, not corruption.
        raise ValueError(f'run was produced by tool version {made_by} and this is {VERSION}; replay it with that version of survey.py')
    verify(run, cache)
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=False)
    aliases = {p['id']: p.get('aliases', []) for p in load(run / 'config.json')['products']}
    hits = []
    for s in load(run / 'sources.json'):
        if s['status'] == 'extracted':
            segs, _ = extract((Path(cache) / s['sha256']).read_bytes(), s['headers'])
            dump(dest / (s['id'] + '.segments.json'), segs)
            hits.extend(candidates(s, segs, aliases.get(s['product_id'], [])))
    save_leads(dest, hits)
    for name in ('candidates.json', 'statement_leads.json'):
        if load(dest / name) != (load(run / name) if (run / name).exists() else []):
            raise ValueError('extraction differs from recorded run; investigate tool/version changes')
    print('Offline extraction and candidates match recorded run exactly')


def recheck(old, new, dest=None):
    """Compares a fresh run with an earlier one whose source bytes may no longer be obtainable."""
    old, new = Path(old), Path(new)
    current = load(new / 'sources.json')
    byid = {s['id']: s for s in current}
    fresh = {(s['product_id'], s['url']): s for s in current}
    quotes = load(old / 'evidence_index.json') if (old / 'evidence_index.json').exists() else []
    rows = []
    for s in load(old / 'sources.json'):
        n = fresh.get((s['product_id'], s['url']))
        row = {'product_id': s['product_id'], 'url': s['url'], 'old_status': s['status'],
               'new_status': n['status'] if n else 'not in new run'}
        if n and s.get('sha256') and n.get('sha256'):
            row['raw_bytes'] = 'same' if s['sha256'] == n['sha256'] else 'different'
            row['extracted_text'] = ('no text hash in old run' if not s.get('text_sha256') else
                                     'same' if s['text_sha256'] == n.get('text_sha256') else 'different')
        if n and n['status'] == 'duplicate':
            n = byid[n['duplicate_of']]
        mine = [q for q in quotes if q['source_id'] == s['id']]
        if mine and n and n['status'] == 'extracted':
            segs = [(x['location'], loose(x['text'])) for x in load(new / (n['id'] + '.segments.json'))]
            row['excerpts'] = []
            for q in mine:
                wanted = loose(q.get('quote') or q.get('excerpt', ''))
                found = [location for location, text in segs if wanted and wanted in text]
                row['excerpts'].append({'excerpt': q.get('quote') or q.get('excerpt', ''), 'old_location': q.get('location'),
                                        'found_at': found[:5], 'same_location': q.get('location') in found})
        elif mine:
            row['excerpts'] = [{'excerpt': q.get('quote') or q.get('excerpt', ''), 'old_location': q.get('location'),
                                'found_at': [], 'same_location': False} for q in mine]
        rows.append(row)
        found = [e for e in row.get('excerpts', []) if e['found_at']]
        print(f"{row['product_id']}: {row['old_status']} -> {row['new_status']}; raw bytes {row.get('raw_bytes', 'n/a')}; "
              f"extracted text {row.get('extracted_text', 'n/a')}; excerpts found {len(found)}/{len(row.get('excerpts', []))}"
              + ''.join(f"; {e['old_location']} -> {e['found_at'][0]}" for e in found if not e['same_location']))
    if dest:
        if Path(dest).exists():
            raise FileExistsError(dest)
        dump(dest, {'tool_version': VERSION, 'checked_at': now(), 'old': str(old), 'new': str(new), 'sources': rows})
    return rows


def sitemap(urls, host, domains, match, dest, cache, limit=20, delay=1.0):
    """Lists a vendor's own sitemap as an inventory aid. A person still decides what enters the config."""
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(dest)
    domains = domains or [host or urlsplit(urls[0]).hostname]
    f = Fetcher({'delay_seconds': delay}, cache)
    queue = list(urls)
    if host:
        f.robot(f'https://{host}/', domains)
        queue += f.robots[host]['sitemaps']
    files, found = [], set()
    while queue and len(files) < limit:
        rec = {'url': queue.pop(0)}
        try:
            meta, body = f.fetch(rec['url'], domains)
            if body[:2] == b'\x1f\x8b':
                body = zlib.decompressobj(31).decompress(body, 200000000)
            text = body.decode('utf-8', 'replace')
            locs = [unescape(re.sub(r'^<!\[CDATA\[|\]\]>$', '', x.strip())).strip()
                    for x in re.findall(r'<loc>(.*?)</loc>', text, re.S | re.I)]
            index = bool(re.search(r'<sitemapindex', text, re.I))
            if index:
                queue += locs
            else:
                found.update(locs)
            rec.update(final_url=meta['final_url'], sha256=meta['sha256'], retrieved_at=meta['retrieved_at'],
                       kind='index' if index else 'urlset', entries=len(locs))
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
        files.append(rec)
        print(rec.get('kind', 'failed'), rec.get('entries', rec.get('error')), rec['url'], flush=True)
    chosen = sorted(u for u in found if re.search(match, u, re.I))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dump(dest, {'tool_version': VERSION, 'retrieved_at': now(), 'domains': domains, 'match': match,
                'files': files, 'not_fetched': queue, 'total_urls': len(found), 'matched_urls': len(chosen),
                'urls': chosen, 'requests': f.audit})
    print(f'{len(chosen)} of {len(found)} URLs match; {len(queue)} sitemap files not fetched')


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')  # Document text may not fit the console code page.
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('crawl'); c.add_argument('--config', required=True); c.add_argument('--out', required=True); c.add_argument('--cache', default='cache'); c.add_argument('--resume', action='store_true')
    r = sub.add_parser('report'); r.add_argument('--run', required=True); r.add_argument('--reviews', required=True); r.add_argument('--out', required=True); r.add_argument('--require-evidence', action='store_true'); r.add_argument('--source-notes')
    v = sub.add_parser('verify'); v.add_argument('--run', required=True); v.add_argument('--cache', default='cache')
    x = sub.add_parser('replay'); x.add_argument('--run', required=True); x.add_argument('--cache', default='cache'); x.add_argument('--out', required=True)
    b = sub.add_parser('rebuild'); b.add_argument('--run', required=True); b.add_argument('--cache', default='cache'); b.add_argument('--out', required=True)
    k = sub.add_parser('recheck'); k.add_argument('--old', required=True); k.add_argument('--new', required=True); k.add_argument('--out')
    m = sub.add_parser('sitemap'); m.add_argument('--url', action='append', default=[]); m.add_argument('--host'); m.add_argument('--domain', action='append', default=[])
    m.add_argument('--match', default='.'); m.add_argument('--out', required=True); m.add_argument('--cache', default='cache'); m.add_argument('--max-files', type=int, default=20); m.add_argument('--delay', type=float, default=1.0)
    args = p.parse_args()
    try:
        if args.cmd == 'crawl': crawl(args.config, args.out, args.cache, args.resume)
        elif args.cmd == 'report': report(args.run, args.reviews, args.out, args.require_evidence, args.source_notes)
        elif args.cmd == 'verify': verify(args.run, args.cache)
        elif args.cmd == 'replay': replay(args.run, args.cache, args.out)
        elif args.cmd == 'rebuild': rebuild(args.run, args.cache, args.out)
        elif args.cmd == 'recheck': recheck(args.old, args.new, args.out)
        elif not args.url and not args.host: p.error('sitemap needs --url or --host')
        else: sitemap(args.url, args.host, args.domain, args.match, args.out, args.cache, args.max_files, args.delay)
    # Refusals the tool raises on purpose read as one line, not as a crash.
    except FileExistsError as e:
        sys.exit(f'error: already exists, refusing to overwrite: {e.filename or e}')
    except FileNotFoundError as e:
        sys.exit(f'error: not found: {e.filename or e}')
    except ValueError as e:
        sys.exit(f'error: {e}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Bounded public-document survey. Keyword hits are leads, never support verdicts."""
import argparse
import csv
import hashlib
import heapq
import io
import json
import os
import random
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

VERSION = '1.6.0'
# Bumped only when extraction or lead rules change. Replay compares this, so a report-only release keeps runs replayable.
EXTRACTION = '1.4.0'
UA_TOKEN = 'IEDSecuritySurvey'
UA = f"{UA_TOKEN}/{VERSION.rsplit('.', 1)[0]} (public-document research; no device scanning)"
# Review cells. Changing this tuple changes every denominator; lead groups below may grow freely.
CAPABILITIES = ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'authentication', 'encryption', 'ssh', 'integrity')
# The three properties asked about for every protocol and interface. The other cells are the mechanisms that may provide them.
PROPERTIES = ('authentication', 'integrity', 'encryption')
# A capability named in a sentence that denies it. Encryption wording is left to plaintext_statement where both apply.
TERM = r'(?:m?TLS|SSL|DTLS|IP\s?sec|SSH|MACsec|secure\s+authentication|authentication|encryption|CIP\s+Security)'
DEFAULT = r'(?:by\s+default|default\s+(?:setting|state|value|configuration)|factory[\s-]+defaults?|out\s+of\s+the\s+box)'
NEEDS = r'requires?|required|optional(?:ly)?|licen[sc]e[sd]?|order(?:ing)?\s+(?:code|option)'
PATTERNS = {
    'dnp3_secure_authentication': r'secure\s+auth\w*|\b(?-i:SA)\s*v\d\b|\bDNP\s*3?.{0,80}?\b(?-i:SA)\b|\bIEC\s*62351-5\b',
    'tls': r'\bm?TLS(?:\s?v?\d(?:\.\d)?)?\b|transport\s+layer\s+security|\bSSL\b',
    'ipsec': r'\bIP\s?sec\b|\bIP\s+security\b|\b(?-i:IKE)(?:v[12])?\b',
    # ODVA's CIP Security, not NERC CIP: the two share an acronym and nothing else.
    'cip_security': r'(?-i:(?<!NERC[\s-])\bCIP\s+Security(?![a-z]))',
    'authentication': r'\bauthenticat\w*|\bRADIUS\b|\b802\.1X\b|\bLDAP\b|\bKerberos\b|\bTACACS\b',
    'encryption': r'\b(?:un|non-?)?encrypt\w*|\bDTLS\b|\bAES\b|\bcipher\w*',
    'ssh': r'\bSSH\b|secure\s+shell',
    # "Integrity poll" is a DNP3 data request and "signal integrity" is electrical, so the bare word is not a lead.
    # "Digitally signed" is left out as well: it is nearly always said of firmware, which is no protocol's integrity.
    'integrity': r'\b(?:message|data|packet|frame|communications?|cryptographic)\s+integrity\b'
                 r'|\bintegrity\s+(?:and|or)\s+(?:confidentiality|authenticity|authentication)\b'
                 r'|\b(?:confidentiality|authenticity|authentication)\s*(?:,|and|or)\s*integrity\b'
                 r'|\bintegrity\s+(?:check\w*|protect\w*|verif\w*)|\bHMAC\b|\b(?-i:[GC]MAC)\b'
                 r'|\bmessage\s+authentication\s+codes?\b',
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
    # Where a document may say how a capability ships and what it needs. Places to read for the default
    # configuration, support conditions and activation requirements of a finding; never findings themselves.
    'default_statement': rf'\b{TERM}\b[^.]{{0,80}}?\b{DEFAULT}\b|\b{DEFAULT}\b[^.]{{0,80}}?\b{TERM}\b',
    'requirement_statement': rf'\b{TERM}\b[^.]{{0,60}}?\b(?:{NEEDS}|option\s+(?:board|card|code)|add-?on'
                             r'|firmware\s+(?:version|revision|release)?\s*[\w.]+\s+(?:or|and)\s+(?:later|higher|above|newer))\b'
                             rf'|\b(?:{NEEDS})\b[^.]{{0,60}}?\b{TERM}\b',
    'macsec': r'\bMACsec\b|\b802\.1AE\b',
    'iec_62351': r'\bIEC(?:/TS)?\s*62351(?:-\d+)?\b',
}
LEADS = {k: re.compile(v, re.I | re.S) for k, v in PATTERNS.items()}
# A lead in these groups also needs the qualifying term close by.
NEAR = {'dnp3_secure_authentication': re.compile(r'\bDNP|\b1815\b|62351-5', re.I)}
# "If the device does not support ..." states a condition, not a fact about the product.
HYPOTHETICAL = re.compile(r'\b(?:if|whether|unless|when|where|in\s+case)\b[^.]{0,60}$', re.I)
DENIALS = ('plaintext_statement', 'non_support_statement')
STATEMENTS = DENIALS + ('default_statement', 'requirement_statement')
# The same four results for every device, whatever its lifecycle.
STATUSES = ('supported', 'conditional', 'explicitly_unsupported', 'unknown')
# Why a reviewed cell is unknown. The second is checked by the tool: a complete document was searched and is silent.
# Only the kinds of document below can carry that, and silence is still not a vendor statement of non-support.
UNKNOWN_REASONS = ('not_enough_evidence', 'complete_document_silent', 'sources_conflict')
COMPLETE_TYPES = ('device_profile', 'conformance_statement', 'manual')
# Statuses written before 1.6.0 are read as unknown with the reason they stood for.
FORMER = {'not_documented': 'complete_document_silent', 'conflicting': 'sources_conflict'}
# Decided by dated vendor evidence only. Legacy, where a config defines it, is end_of_support and nothing wider.
LIFECYCLES = ('currently_supported', 'discontinued_supported', 'discontinued_support_not_stated', 'end_of_support', 'unknown')
FORMER_LIFECYCLES = ('active', 'legacy', 'discontinued')
LIFECYCLE_WORDS = {'discontinued_supported': 'discontinued, still supported',
                   'discontinued_support_not_stated': 'discontinued, support not stated'}
SUPPORT_BASES = ('built_in', 'firmware_upgrade', 'optional_module', 'licence', 'external_gateway', 'not_stated')
DEFAULT_STATES = ('enabled', 'disabled', 'undocumented')
ACTIVATION_NEEDS = ('configuration', 'certificates_or_keys', 'compatible_master', 'licence_key', 'other', 'none_stated')
# What a vendor document can never show. Anything but unknown needs evidence from where the device is installed.
DEPLOYMENT_STATES = ('unknown', 'enabled', 'disabled')
EVIDENCE_ABOUT = ('capability', 'conditions', 'default', 'activation')
IDENTITY_LEVELS = ('family', 'model', 'catalogue_number')
# A reviewer who has not looked yet says so. It is not the same as "the documents do not say".
NOT_ASSESSED = 'not_assessed'
# Roughly from most to least direct about what one product and firmware can do. Guidance for the reviewer, not a score.
DOC_TYPES = ('device_profile', 'conformance_statement', 'security_guide', 'manual', 'datasheet', 'product_page',
             'advisory', 'other')
# The distinction the study turns on: protection of control traffic is not protection of management access.
INTERFACE_CLASSES = ('control_protocol', 'management', 'network')
REVIEW_STATUSES = ('draft', 'confirmed')
# Pointers only: which mechanism rows a reader should look at when no explicit property row exists.
RELATES = {'encryption': ('tls', 'ipsec', 'cip_security', 'ssh'),
           'authentication': ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'ssh'),
           'integrity': ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'ssh')}
REDIRECTS = (301, 302, 303, 307, 308)
RETRY_STATUS = (429, 502, 503, 504)
KEEP_HEADERS = ('content-type', 'content-length', 'content-disposition', 'content-language', 'last-modified', 'etag', 'date')
KNOWN_KEYS = {'sampling', 'definitions', 'title', 'max_depth', 'max_pages_per_product', 'delay_seconds', 'timeout_seconds', 'max_bytes',
              'follow_pattern', 'robots_follow_redirects', 'retries', 'products',
              'seed', 'per_stratum', 'census', 'inventory', 'frame'}
# Which link to follow first when the page budget is short: the documents that state capabilities most directly.
LINK_WEIGHTS = [(re.compile(p, re.I), w) for p, w in (
    (r'device[\s_-]*profile', 4), (r'conformance|\bpics\b|\bpixit\b', 3), (r'secur|cyber|hardening', 2),
    (r'manual|instruction|user[\s_-]*guide', 2), (r'communicat|protocol|dnp|61850|ethernet|network', 1),
    (r'data[\s_-]?sheet|brochure|catalog|flyer|guide', 1))]
# A link that leads to a sign-in page marks a document that exists but is not public. It is recorded, never fetched.
LOGIN = re.compile(r'/(?:log-?in|sign-?in|sso|passport|oauth2?|authorize)(?:[/?.]|$)|//(?:idp|login|sso|auth|account)\.', re.I)
# Soft hyphens, zero-width characters and trademark signs vanish; typographic hyphens become '-'.
TIDY = {**dict.fromkeys(map(ord, '\u00ad\u200b\u200c\u200d\u2060\ufeff\u2122\u00ae\u2120')),
        **dict.fromkeys(map(ord, '\u2010\u2011\u2012\u2013\u2212'), '-')}


def digest(b):
    return hashlib.sha256(b).hexdigest()


# Hashed when the tool starts, so a manifest names the code that ran even if the file is edited during a long crawl.
SCRIPT_SHA256 = digest(Path(__file__).read_bytes())


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


def life_words(status):
    return LIFECYCLE_WORDS.get(status, (status or 'not recorded').replace('_', ' '))


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
            if feature in DENIALS:
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
        life = p.get('lifecycle')
        if life in FORMER_LIFECYCLES:
            warnings.append(f'{pid}: lifecycle "{life}" is a label from before 1.6.0 and is reported as unknown')
        elif life and life not in LIFECYCLES:
            raise ValueError(f'{pid}: lifecycle must be one of {", ".join(LIFECYCLES)}')
        elif life and life != 'unknown' and not p.get('lifecycle_evidence'):
            warnings.append(f'{pid}: lifecycle "{life}" has no lifecycle_evidence; the report will refuse it')
        try:
            re.compile(p.get('follow_pattern', ''))
        except re.error as e:
            raise ValueError(f'{pid}: follow_pattern is not a valid regular expression: {e}')
        warnings += [f'{pid}: missing {k}' for k in ('vendor', 'model', 'category') if not p.get(k)]
        warnings += [f'{pid}: seed is not an allowlisted public HTTPS URL: {u}' for u in p['seeds'] if not allowed(u, p['domains'])]
        if not p['seeds']:
            warnings.append(f'{pid}: no seeds, so every cell stays unknown')
    return warnings


def link_score(url, text, alias):
    blob = url + ' ' + text
    return sum(w for pattern, w in LINK_WEIGHTS if pattern.search(blob)) + (2 if alias and alias.search(blob) else 0)


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
    """Manifest and the three templates a reviewer fills in. Only a finished run has a manifest."""
    dump(out / 'manifest.json', {'tool_version': VERSION, 'extraction_version': EXTRACTION, 'finished_at': now(),
        'config_sha256': config_sha256, 'python': sys.version,
        'script_sha256': SCRIPT_SHA256,
        'complete': True, 'source_count': len(sources),
        'candidate_count': sum(h['lead_type'] != 'statement' for h in hits),
        'lead_counts': dict(Counter(h['lead_type'] for h in hits)),
        'source_status': dict(Counter(s['status'] for s in sources)),
        'config_warnings': warnings, 'sampling': cfg['sampling'], **extra})
    dump(out / 'review_template.json',
         [{'product_id': p['id'], 'feature': feature, 'status': 'unknown',
           'source_ids': [], 'source_hashes': {}, 'location': '', 'protocol': '',
           'interface': '', 'interface_class': '', 'model_scope': 'not established', 'hardware_revision': 'not established',
           'firmware': 'not established', 'implementation': 'not established', 'unknown_reason': '',
           'support_basis': [], 'conditions': '', 'default_state': '', 'activation_needs': [], 'activation_requirements': '',
           'deployment_status': 'unknown', 'deployment_evidence': [],
           'evidence': [], 'rationale': '', 'reviewer': '', 'reviewed_at': '', 'review_status': ''}
          for p in cfg['products'] for feature in CAPABILITIES])
    # Who the device is and where it stands with its vendor. Filled from the inventory; a reviewer corrects it with evidence.
    dump(out / 'device_notes_template.json',
         [{'product_id': p['id'], 'manufacturer': p.get('vendor', ''), 'model': p.get('model', ''), 'identity_level': '',
           'lifecycle_status': p['lifecycle'] if p.get('lifecycle') in LIFECYCLES else 'unknown',
           'vendor_label': p.get('vendor_label', ''), 'lifecycle_evidence': p.get('lifecycle_evidence', []),
           'release_date': '', 'release_evidence': [], 'note': '', 'noted_by': '', 'noted_at': ''} for p in cfg['products']])
    # What a document says about its own number, revision and date is for a person to read off, not for a regex.
    dump(out / 'source_notes_template.json',
         [{'source_id': s['id'], 'product_id': s['product_id'], 'url': s['final_url'], 'title': s.get('title', ''),
           'document_hints': s.get('document_hints', []), 'doc_type_suggested': s.get('doc_type_suggested', ''),
           'doc_type': '', 'coverage': '', 'document_id': '', 'revision': '', 'document_date': '', 'note': ''}
          for s in sources if s['status'] == 'extracted'])


def crawl(config_path, out, cache, resume=False, reuse=None, only=None):
    config_bytes = Path(config_path).read_bytes()
    cfg = json.loads(config_bytes)
    if only:
        # The run's config lists what the run covers; the manifest keeps the hash of the file it was cut from.
        cfg['products'] = [p for p in cfg.get('products', []) if re.search(only, f"{p.get('id')} {p.get('vendor', '')}", re.I)]
        if not cfg['products']:
            raise ValueError('--only matches no product')
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
    # Bytes an earlier run already fetched are not requested again; the record says where they came from.
    runs = [reuse] if isinstance(reuse, (str, Path)) else list(reuse or [])
    known = {}
    for earlier in runs:
        for s in load(Path(earlier) / 'sources.json'):
            if s['status'] == 'login_required' or s['status'] in ('extracted', 'duplicate') and (cache / s['sha256']).exists():
                known.setdefault(s['url'], dict(s, held_by=str(earlier)))
    products = cfg['products']
    # Product provenance remains separate even when a family document is shared.
    for number, product in enumerate(products, 1):
        aliases = product.get('aliases', [])
        alias = alias_pattern(aliases)
        # A vendor's site decides how deep and what to follow, so a product may override the run's settings.
        depth_limit = product.get('max_depth', cfg.get('max_depth', 0))
        budget = product.get('max_pages_per_product', cfg.get('max_pages_per_product', 3))
        follow = re.compile(product.get('follow_pattern', cfg.get('follow_pattern', r'manual|security|datasheet|\.pdf')), re.I)
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
                elif known.get(url, {}).get('status') == 'login_required':
                    # The earlier run was told this document needs a sign-in. It is not asked for again.
                    rec.update(status='login_required', error=known[url]['error'], reused_from=known[url]['held_by'])
                else:
                    try:
                        if url in known:
                            meta = {k: known[url][k] for k in ('final_url', 'sha256', 'bytes', 'headers', 'robots_basis',
                                                               'redirect_chain', 'retrieved_at') if k in known[url]}
                            meta['reused_from'] = known[url]['held_by']
                            body = (cache / meta['sha256']).read_bytes()
                        else:
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
                        gated = isinstance(e, ValueError) and str(e).startswith('login required')
                        rec.update(status='login_required' if gated else 'failed', error=f'{type(e).__name__}: {e}')
                sources.append(rec)
                byid[rec['id']] = rec
            elif rec['status'] == 'extracted' and depth < depth_limit:
                # Resumed run: rebuild this page's links from the retained bytes instead of the network.
                links = parse((cache / rec['sha256']).read_bytes(), rec['headers'])[1]
            if rec['status'] not in ('skipped', 'login_required'):
                attempted += 1
            if rec['status'] == 'extracted':
                shas.setdefault(rec['sha256'], rec['id'])
                if fresh:
                    rec['links_found'] = len(links)
                if depth < depth_limit:
                    matched, gates = set(), {}
                    for href, text in links:
                        try:
                            full = canonical(urljoin(rec['final_url'], href))
                        except ValueError:
                            continue
                        if full in gates:
                            gates[full]['link_count'] += 1  # One sign-in address often stands for a list of documents.
                        if full in seen or full in matched:
                            continue  # Already attempted, e.g. a fragment link back to this page.
                        if allowed(full, product['domains']) and follow.search(full + ' ' + text):
                            matched.add(full)
                            if LOGIN.search(full):
                                # The document exists but sits behind a sign-in. It is counted, not requested.
                                seen.add(full)
                                gate = {'id': digest((product['id'] + full).encode())[:20], 'product_id': product['id'],
                                        'url': full, 'depth': depth + 1, 'via': rec['id'], 'started_at': now(),
                                        'status': 'login_required', 'link_text': text, 'link_count': 1,
                                        'error': 'link leads to a sign-in page; not requested'}
                                gates[full] = gate
                                if fresh and (product['id'], full) not in prior:
                                    sources.append(gate)
                                    byid[gate['id']] = gate
                                continue
                            heapq.heappush(queue, (depth + 1, -link_score(full, text, alias), order, full, rec['id']))
                            order += 1
                    if fresh:
                        rec['links_matched'] = len(matched)
            if fresh:
                # Checkpoints survive interrupted runs; incomplete runs are never called complete.
                dump(out / 'sources.json', sources)
                save_leads(out, hits)
                dump(out / 'requests.json', f.audit)
                print(f'[{number}/{len(products)}]', product['id'], rec['status'], url, flush=True)
    # Written once more so a run without any seeds still has all its files.
    dump(out / 'sources.json', sources)
    save_leads(out, hits)
    dump(out / 'requests.json', f.audit)
    finish(out, cfg, digest(config_bytes), sources, hits, warnings,
           **({'only': only} if only else {}),
           **({'reused_from': str(runs[0]) if len(runs) == 1 else [str(x) for x in runs]} if runs else {}))


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


def settle(r):
    """Reads a row written under earlier rules: six statuses become four, and the reason is kept."""
    if r.get('status') in FORMER:
        r.update(unknown_reason=FORMER[r['status']], status='unknown')
    return r


def silent(r):
    return r['status'] == 'unknown' and r.get('unknown_reason') == 'complete_document_silent'


def grounded(r):
    """A row that rests on cited sources: any result, and an unknown that says the documents are silent or disagree."""
    return r['status'] != 'unknown' or r.get('unknown_reason') in ('complete_document_silent', 'sources_conflict')


def token(r):
    """How a grounded row is counted. A capability reached only through an external gateway is not the device's own."""
    if r['status'] == 'unknown':
        return {'complete_document_silent': 'silent', 'sources_conflict': 'conflict'}.get(r.get('unknown_reason'), 'unknown')
    return 'gateway' if r['status'] == 'conditional' and r.get('support_basis') == ['external_gateway'] else r['status']


def named(r):
    return {'silent': 'unknown: complete document silent', 'conflict': 'unknown: sources conflict',
            'gateway': 'conditional: external gateway only'}.get(token(r), r['status'].replace('_', ' '))


def facts(r):
    """The facts a supported or conditional row states beyond the result. A row from an earlier review lacks them: not assessed."""
    result = r['status'] in ('supported', 'conditional')
    return {'basis': r.get('support_basis', [NOT_ASSESSED] if result else []),
            'default': r.get('default_state', NOT_ASSESSED if result else ''),
            'needs': r.get('activation_needs', [NOT_ASSESSED] if result else []),
            'deployment': r.get('deployment_status') or 'unknown'}


def validate_reviews(rows, sources, products, segments=None, require_evidence=False):
    byid = {s['id']: s for s in sources}
    vendor_documents = {x for s in sources for x in (s['id'], s.get('url'), s.get('final_url')) if x}
    seen, classes = set(), {}
    for r in rows:
        settle(r)
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
        reason = r.get('unknown_reason') or ''
        if reason and (r['status'] != 'unknown' or reason not in UNKNOWN_REASONS):
            raise ValueError(f'unknown_reason belongs to an unknown row and is one of {", ".join(UNKNOWN_REASONS)}: {key}')
        if grounded(r) and not r['source_ids']:
            raise ValueError(f'claim requires source evidence: {key}')
        # Silence has no passage to point at, so such a row states only where it applies and to which firmware.
        needed = ('interface', 'firmware') if silent(r) else ('location','protocol','interface','firmware','implementation')
        if grounded(r) and not all(r.get(k) for k in needed):
            raise ValueError(f'claim scope is incomplete: {key}')
        kind = r.get('interface_class') or ''
        if kind not in INTERFACE_CLASSES + (() if grounded(r) else ('',)):
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
        # What the finding applies to, how the capability is obtained, how it ships and what switching it on takes.
        result, f = r['status'] in ('supported', 'conditional'), facts(r)
        for k in ('model_scope', 'hardware_revision'):
            if grounded(r) and not r.get(k, NOT_ASSESSED):
                raise ValueError(f'{k} is empty; write what the document names, "not established" or {NOT_ASSESSED}: {key}')
        for name, value, allowed_values in (('support_basis', f['basis'], SUPPORT_BASES), ('activation_needs', f['needs'], ACTIVATION_NEEDS)):
            if not isinstance(value, list) or set(value) - set(allowed_values) - {NOT_ASSESSED}:
                raise ValueError(f'{name} is a list from {", ".join(allowed_values)}, or [{NOT_ASSESSED!r}]: {key}')
            if result and not value:
                raise ValueError(f'{name} is empty; a supported or conditional result states it, or says {NOT_ASSESSED}: {key}')
            if value and not result:
                raise ValueError(f'{name} belongs to a supported or conditional result only: {key}')
            if len(value) > 1 and set(value) & {NOT_ASSESSED, 'not_stated', 'none_stated'}:
                raise ValueError(f'{name} mixes a value with "nothing stated" or "{NOT_ASSESSED}": {key}')
        if r['status'] == 'supported' and f['basis'] not in (['built_in'], [NOT_ASSESSED]):
            raise ValueError(f'supported means built in; a firmware upgrade, module, licence or gateway makes it conditional: {key}')
        if f['default'] not in (DEFAULT_STATES + (NOT_ASSESSED,) if result else ('',)):
            raise ValueError(f'default_state is one of {", ".join(DEFAULT_STATES)} or {NOT_ASSESSED}, for a supported or conditional result only: {key}')
        if set(f['needs']) - {'none_stated', NOT_ASSESSED} and not r.get('activation_requirements'):
            raise ValueError(f'activation_needs are named but activation_requirements does not describe them: {key}')
        if f['deployment'] not in DEPLOYMENT_STATES:
            raise ValueError(f'deployment_status must be one of {", ".join(DEPLOYMENT_STATES)}: {key}')
        proof = r.get('deployment_evidence') or []
        if f['deployment'] != 'unknown':
            if not proof or not all(isinstance(e, dict) and all(e.get(k) for k in ('kind', 'reference', 'date', 'scope')) for e in proof):
                raise ValueError(f'deployment_status {f["deployment"]} needs deployment_evidence with kind, reference, date and scope; without it the status is unknown: {key}')
            if any(e['reference'] in vendor_documents for e in proof):
                raise ValueError(f'a vendor document shows what a device can do, not what an operator enabled; it is not deployment evidence: {key}')
        waiting = NOT_ASSESSED in [r.get('model_scope', NOT_ASSESSED), r.get('hardware_revision', NOT_ASSESSED), f['default']] + f['basis'] + f['needs']
        if result and waiting and r.get('review_status') == 'confirmed':
            raise ValueError(f'a confirmed row may not leave a field {NOT_ASSESSED}: {key}')
        evidence = r.get('evidence') or []
        about = Counter(e.get('about') or 'capability' for e in evidence)
        if set(about) - set(EVIDENCE_ABOUT):
            raise ValueError(f'evidence "about" must be one of {", ".join(EVIDENCE_ABOUT)}: {key}')
        if require_evidence:
            if r['status'] != 'unknown' and not about['capability']:
                raise ValueError(f'claim requires a verbatim evidence quote: {key}')
            # Each further fact needs its own words from the document, not the quote that shows the capability exists.
            for what, stated in (('default', f['default'] in ('enabled', 'disabled')),
                                 ('conditions', bool(set(f['basis']) - {'built_in', 'not_stated', NOT_ASSESSED})),
                                 ('activation', bool(set(f['needs']) - {'none_stated', NOT_ASSESSED}))):
                if stated and not about[what]:
                    raise ValueError(f'this row states its {what}; that needs an evidence quote marked about: {what}: {key}')
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
             'interface', 'interface_class', 'conditions', 'review_status', 'unknown_reason', 'support_basis', 'default_state',
             'activation_needs', 'activation_requirements', 'deployment_evidence')
    return (row.get('status') == 'unknown' and not any(row.get(k) for k in blank)
            and (row.get('deployment_status') or 'unknown') == 'unknown')


COLUMNS = ('Manufacturer', 'Model', 'Lifecycle', 'Evidence applies to', 'Protocol / interface', 'Authentication', 'Integrity',
           'Encryption', 'Support conditions', 'Default', 'Activation', 'Deployment', 'Evidence', 'Review status')
# The CSV keeps the three parts of "evidence applies to" in columns of their own.
CSV_COLUMNS = (COLUMNS[:3] + ('Category', 'Model scope', 'Hardware revision', 'Firmware', COLUMNS[4], 'Interface class')
               + COLUMNS[5:] + ('Sources',))
MARK = {'supported': 'S', 'conditional': 'C', 'gateway': 'G', 'explicitly_unsupported': 'X', 'silent': '?s', 'conflict': '?c',
        'unknown': '?'}
RANK = ('supported', 'conditional', 'gateway', 'conflict', 'explicitly_unsupported', 'silent')


def device_records(cfg, sources, notes_path, segments):
    """Who each device is and where it stands with its vendor. A lifecycle status without dated vendor evidence is refused."""
    products = {p['id']: p for p in cfg['products']}
    byid = {s['id']: s for s in sources}
    notes = {n['product_id']: n for n in (load(notes_path) if notes_path else [])}
    if set(notes) - set(products):
        raise ValueError(f'device notes name products that are not in this run: {sorted(set(notes) - set(products))}')
    devices = {}
    for pid, p in products.items():
        n = notes.get(pid, {})
        former = p['lifecycle'] if p.get('lifecycle') in FORMER_LIFECYCLES else ''
        d = {'identity_level': n.get('identity_level') or '',
             'lifecycle_status': n.get('lifecycle_status') or ('' if former else p.get('lifecycle')) or 'unknown',
             'vendor_label': n.get('vendor_label') or p.get('vendor_label') or (f'{former} (label used before 1.6.0)' if former else ''),
             'lifecycle_evidence': n['lifecycle_evidence'] if 'lifecycle_evidence' in n else ([] if former else p.get('lifecycle_evidence') or []),
             'release_date': n.get('release_date') or '', 'release_evidence': n.get('release_evidence') or [],
             'note': n.get('note') or '', 'noted_by': n.get('noted_by') or ''}
        status, proof = d['lifecycle_status'], d['lifecycle_evidence']
        if status not in LIFECYCLES:
            raise ValueError(f'lifecycle_status must be one of {", ".join(LIFECYCLES)}: {pid}')
        if d['identity_level'] not in ('',) + IDENTITY_LEVELS:
            raise ValueError(f'identity_level must be one of {", ".join(IDENTITY_LEVELS)}, or empty: {pid}')
        # Protocol, missing security features and the age of a manual decide nothing here. Only the vendor's dated word does.
        if status != 'unknown' and not proof:
            raise ValueError(f'lifecycle status {status} needs dated vendor evidence; without it the status is unknown: {pid}')
        for e in proof + d['release_evidence']:
            s = byid.get(e.get('source_id'))
            if e.get('source_id') and (not s or s['product_id'] != pid):
                raise ValueError(f'lifecycle evidence cites a source that is not one of this product in this run: {pid}')
            if s:
                e.setdefault('url', s['final_url'])
                e.setdefault('sha256', s['sha256'])
            where = e.get('url')
            if not where or not allowed(where, p['domains']):
                raise ValueError(f'lifecycle evidence must be a vendor source: a source of this run or a URL on the product domains: {pid}')
            e['dated'] = e.get('stated_date') or (e.get('retrieved_at') or (s or {}).get('retrieved_at') or '')[:10]
            if not e['dated']:
                raise ValueError(f'lifecycle evidence needs a date: the one the vendor states, or the retrieval date: {pid}')
            if e.get('source_id') and e.get('location') and e.get('quote'):
                text = cited(segments(e['source_id']), e['location'])
                if text is None or loose(e['quote']) not in loose(text):
                    raise ValueError(f"lifecycle quote not found at {e['location']} of source {e['source_id']}: {pid}")
        if status in ('end_of_support', 'discontinued_supported') and not any(len(loose(e.get('quote') or '')) >= 20 for e in proof):
            raise ValueError(f"{status} needs the vendor's own sentence as a quote: {pid}")
        if d['release_date'] and not d['release_evidence']:
            raise ValueError(f'release_date needs release_evidence from a vendor source: {pid}')
        devices[pid] = d
    return devices


def report(run, review_path, dest, require_evidence=False, source_notes=None, device_notes=None):
    run, dest = Path(run), Path(dest)
    cfg, sources, rows = load(run / 'config.json'), load(run / 'sources.json'), load(review_path)
    products = {p['id']: p for p in cfg['products']}
    devices = device_records(cfg, sources, device_notes, lambda sid: load(run / (sid + '.segments.json')))
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
    if {n.get('coverage') or '' for n in notes.values()} - {'', 'complete', 'partial'}:
        raise ValueError('source notes: coverage must be complete, partial or empty')
    dest.mkdir(parents=True, exist_ok=True)
    # The source manifest: URL, retrieval time and hash come from the crawl, the document's own number and date from a reviewer.
    refs, cite = {}, {}
    for s in sources:
        if s['status'] == 'extracted':
            refs[s['id']] = s['ref'] = f'S{len(refs) + 1}'
            s['document'] = {k: notes.get(s['id'], {}).get(k, '')
                             for k in ('doc_type', 'coverage', 'document_id', 'revision', 'document_date', 'note')}
            # What kind of document a quote comes from travels with every reference to it.
            cite[s['id']] = f"{s['ref']} [{s['document']['doc_type'].replace('_', ' ') or 'type not confirmed'}]"
    dump(dest / 'findings.json', rows)
    dump(dest / 'sources.json', sources)
    dump(dest / 'evidence_index.json', [
        {'product_id': r['product_id'], 'feature': r['feature'], 'status': r['status'], 'interface': r.get('interface', ''),
         'interface_class': r.get('interface_class', ''), 'source_id': e['source_id'], 'source_ref': refs[e['source_id']],
         'doc_type': byid[e['source_id']]['document']['doc_type'],
         'url': byid[e['source_id']]['final_url'], 'sha256': byid[e['source_id']]['sha256'],
         'location': e['location'], 'quote': e['quote'], 'about': e.get('about') or 'capability',
         'retrieved_at': byid[e['source_id']].get('retrieved_at')}
        for r in rows for e in r.get('evidence') or []])
    # Lead counts say how much text mentioned a term. They are never device counts, and statements are kept apart.
    leads = {p: {t: Counter() for t in ('capability', 'related', 'statement', 'profile')} for p in products}
    mentions = Counter()
    for h in load_leads(run):
        kind = h.get('lead_type') or lead_type(h['feature'])
        leads[h['product_id']][kind][h['feature']] += 1
        if kind in ('capability', 'profile'):
            mentions[h['source_id'], h['feature']] += 1
    # What a complete manual does not say is recorded as unknown with that reason. The tool checks the silence itself:
    # such a row must cite complete documents in which the search found no lead for that capability.
    searched = {}
    for r in rows:
        if silent(r):
            key = r['product_id'], r['feature']
            for sid in r['source_ids']:
                doc = byid[sid]['document']
                if doc['doc_type'] not in COMPLETE_TYPES or doc['coverage'] != 'complete':
                    raise ValueError(f'complete_document_silent needs a complete {", ".join(COMPLETE_TYPES)} (doc_type and coverage in the '
                                     f'source notes); source {sid} is {doc["doc_type"] or "untyped"}, {doc["coverage"] or "coverage not stated"}: {key}')
                if mentions[sid, r['feature']]:
                    raise ValueError(f'{mentions[sid, r["feature"]]} leads for {r["feature"]} exist in source {sid}; '
                                     f'review them before recording complete_document_silent: {key}')
            searched[id(r)] = '; '.join(
                f"{cite[sid]} searched in full" + (f", {byid[sid]['pages']} PDF pages" if byid[sid].get('pages') else '')
                + f": no lead for {r['feature']}" for sid in r['source_ids'])
    dump(dest / 'candidate_counts.json', {p: {t: {'total': sum(c.values()), 'by_group': dict(sorted(c.items()))}
                                              for t, c in kinds.items()} for p, kinds in leads.items()})
    columns = ['product_id','vendor','model','category','lifecycle_status','feature','status','unknown_reason','protocol','interface',
               'interface_class','model_scope','hardware_revision','firmware','implementation','support_basis','conditions',
               'default_state','activation_needs','activation_requirements','deployment_status','deployment_evidence',
               'location','rationale','reviewer','reviewed_at','review_status','source_urls','source_hashes','evidence']
    with (dest / 'findings.csv').open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=columns)
        w.writeheader()
        for r in rows:
            p = products[r['product_id']]
            item = {k: r.get(k, '') for k in columns}
            item.update({k: p.get(k, '') for k in ('vendor','model','category')}, lifecycle_status=devices[r['product_id']]['lifecycle_status'],
                        support_basis=' | '.join(facts(r)['basis']), default_state=facts(r)['default'],
                        activation_needs=' | '.join(facts(r)['needs']), deployment_status=facts(r)['deployment'],
                        deployment_evidence=json.dumps(r.get('deployment_evidence') or [], ensure_ascii=False))
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

    recorded = sum(d['lifecycle_status'] != 'unknown' for d in devices.values())
    # Results are counted by lifecycle group only when the config the run was crawled with says what the groups mean.
    defined = cfg.get('definitions') or {}
    grouped = bool(defined.get('legacy'))

    def lifecycle(pid):
        return life_words(devices[pid]['lifecycle_status'])

    def stratum_of(pid):
        return f'{category(pid)}, {lifecycle(pid)}' if grouped else category(pid)

    def words(values):
        return ', '.join(v.replace('_', ' ') for v in values)

    def joined(values, empty):
        return '; '.join(dict.fromkeys(v.replace(NOT_ASSESSED, 'not assessed') for v in values if v)) or empty

    def per_feature(pairs, empty):
        # One value when every finding on the interface agrees, otherwise each capability with its own.
        texts = list(dict.fromkeys(t for _, t in pairs))
        return empty if not pairs else texts[0] if len(texts) == 1 else '; '.join(f'{f}: {t}' for f, t in pairs)

    def label(status):
        return status.replace('_', ' ')

    def scope(r):
        return squash(r.get('interface') or '').lower()

    claims = [r for r in rows if grounded(r)]
    cell = {(r['product_id'], r['feature'], scope(r)): r for r in rows}
    reviewed = {(r['product_id'], r['feature']) for r in rows}
    expected = len(products) * len(CAPABILITIES)

    def prop(pid, where, members, feature):
        """What the review says about one property on one interface. Mechanism rows are pointed to, never read as a result."""
        r = cell.get((pid, feature, where)) or cell.get((pid, feature, ''))
        if r and silent(r):
            return 'unknown: the complete documentation searched does not mention it'
        if r and token(r) == 'conflict':
            return 'unknown: sources conflict'
        if r and r['status'] != 'unknown':
            return f"{named(r)}: {flat(r['protocol'])}"
        see = [f"{m['feature']} ({named(m)})" for m in members if m['feature'] in RELATES[feature]]
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
            stated = [m for m in members if m['status'] in ('supported', 'conditional')]
            row = {
                'pid': pid, 'Manufacturer': p.get('vendor', ''), 'Model': p.get('model') or pid, 'Lifecycle': lifecycle(pid),
                'Category': category(pid), 'Interface class': kind,
                'Searched': '; '.join(searched[id(m)] for m in members if id(m) in searched),
                'Model scope': joined((flat(m.get('model_scope', NOT_ASSESSED)) for m in members), 'not established'),
                'Hardware revision': joined((flat(m.get('hardware_revision', NOT_ASSESSED)) for m in members), 'not established'),
                'Firmware': joined((flat(m['firmware']) for m in members), 'not established'),
                'Protocol / interface': (f"{flat(members[0]['interface'])} ({kind.replace('_', ' ')})" if members
                                         else 'No control protocol established from the examined sources'),
                'Support conditions': joined((words(facts(m)['basis']) + (f": {flat(m['conditions'])}" if m.get('conditions') else '')
                                              for m in stated), 'none stated' if members else '-'),
                'Default': per_feature([(m['feature'], facts(m)['default'].replace('_', ' ')) for m in stated], '-'),
                'Activation': per_feature([(m['feature'], words(facts(m)['needs']) + (f": {flat(m['activation_requirements'])}"
                                                                                        if m.get('activation_requirements') else ''))
                                           for m in stated], '-'),
                # Unknown unless someone cites evidence from an installation. No vendor document can change this cell.
                'Deployment': joined((facts(m)['deployment'] + (' (' + '; '.join(f"{e['kind']}, {e['date']}" for e in m['deployment_evidence']) + ')'
                                                                if facts(m)['deployment'] != 'unknown' else '') for m in members), 'unknown'),
                'Evidence': [(cite[e['source_id']], e['location'], flat(e['quote'])) for m in members for e in m.get('evidence') or []],
                'Review status': '; '.join(dict.fromkeys(f"{m.get('review_status') or 'draft'} ({flat(m['reviewer'])})"
                                                         for m in signed)) or 'not reviewed',
                'Sources': '; '.join(f"{cite[sid]} {byid[sid]['final_url']} sha256:{byid[sid]['sha256']}" for sid in used)}
            row.update({name.capitalize(): prop(pid, where, members, name) for name in PROPERTIES})
            # Two findings on one interface may rest on documents for different models or firmware; then each says its own.
            row['Evidence applies to'] = per_feature(
                [(m['feature'], ', '.join(f"{name} {flat(m.get(key, NOT_ASSESSED)).replace(NOT_ASSESSED, 'not assessed')}" for name, key in
                                          (('model', 'model_scope'), ('hardware', 'hardware_revision'), ('firmware', 'firmware'))))
                 for m in members], 'not established')
            table.append(row)

    def shown(row):
        quotes, parts = row['Evidence'], []
        if quotes:
            ref, where, text = quotes[0]
            parts.append(f'{ref} {where}: "{clip(text, 110)}"' + (f' (+{len(quotes) - 1} more)' if len(quotes) > 1 else ''))
        return '; '.join(parts + [row['Searched']] * bool(row['Searched'])) or 'none'

    with (dest / 'findings_table.csv').open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, extrasaction='ignore', fieldnames=list(CSV_COLUMNS))
        w.writeheader()
        for row in table:
            quotes = [f'{ref} {where}: "{text}"' for ref, where, text in row['Evidence']]
            w.writerow(dict(row, Evidence=' || '.join(quotes + [row['Searched']] * bool(row['Searched'])) or 'none'))

    def results(pid, feature, kinds):
        return [token(r) for r in claims if r['product_id'] == pid and r['feature'] == feature and r['interface_class'] in kinds]

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
    line = (f"Products/families in seed inventory: {len(products)}. "
            f"Sources attempted: {len(sources) - totals['skipped'] - totals['login_required']}; "
            f"extracted: {totals['extracted']}; failed: {totals['failed']}")
    if totals['duplicate']:
        line += f"; duplicate of another source: {totals['duplicate']}"
    if totals['skipped']:
        line += f"; matched links not followed (page budget): {totals['skipped']}"
    if totals['login_required']:
        line += f"; documents behind a sign-in, not requested: {sum(s.get('link_count', 1) for s in sources if s['status'] == 'login_required')}"
    text = [f"# {cfg.get('title', 'IED security documentation survey')}", '',
            f"Sampling: {cfg['sampling']}", '', line + '.', '',
            'This measures documented capabilities, not enabled settings, installed-base coverage or plaintext prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. Capability categories overlap, so counts below are review cells and must not be added up as devices.', '',
            'Reviewers on record: ' + ('; '.join(f'{md(name)} ({n} rows)' for name, n in Counter(r['reviewer'] for r in rows).items()) or 'none') + '.', '',
            'Every capability has one of four results: supported, conditional, explicitly unsupported or unknown. An unknown says why where the review recorded it. "Complete document silent" means a complete manual, device profile or conformance statement was searched and does not mention the capability; it is not a vendor statement that the capability is absent.', '']
    legacy = sum(d['lifecycle_status'] == 'end_of_support' for d in devices.values())
    if grouped:
        text.extend(['## Definitions', '',
                     f"Fixed on {defined.get('defined_at') or 'a date the config does not give'} in the config this run was crawled with, before any result was counted.", '',
                     f"- Legacy: {flat(defined['legacy'])}"]
                    + [f"- {life_words(k).capitalize()}: {flat(v)}" for k, v in (defined.get('lifecycle_statuses') or {}).items()]
                    + ([f"- Release date: {flat(defined['release_date'])}"] if defined.get('release_date') else [])
                    + ['', f'Legacy under this definition: {legacy} of {len(products)} devices in this run. Lifecycle status rests on dated vendor evidence for {recorded} devices and is unknown for {len(products) - recorded}.'])
    else:
        text.append('No definition of "legacy" or of the lifecycle groups is recorded in the config of this run, so no result is counted by lifecycle group.')
    # A census has hundreds of devices and no review yet; a row per unreviewed device would bury the reviewed ones.
    bare = {pid for pid in products if not any(r['product_id'] == pid for r in rows)}
    bare = bare if len(bare) > 25 else set()

    def dated(d):
        proof = d['lifecycle_evidence']
        if not proof:
            return 'none'
        e = proof[0]
        said = f'"{clip(flat(e["quote"]), 140)}"' if e.get('quote') else e.get('basis') or 'vendor source'
        return (f"{e['dated']}: {said} <{e.get('url') or byid[e['source_id']]['final_url']}>"
                + (f' (+{len(proof) - 1} more)' if len(proof) > 1 else ''))

    with (dest / 'devices.csv').open('w', newline='', encoding='utf-8') as fp:
        w = csv.writer(fp)
        w.writerow(['product_id', 'manufacturer', 'model', 'category', 'identity_level', 'lifecycle_status', 'vendor_label',
                    'lifecycle_evidence_date', 'lifecycle_evidence_quote', 'lifecycle_evidence_url', 'lifecycle_evidence_sha256',
                    'release_date', 'noted_by'])
        for pid, d in devices.items():
            e = (d['lifecycle_evidence'] or [{}])[0]
            w.writerow([pid, products[pid].get('vendor', ''), products[pid].get('model') or pid, category(pid), d['identity_level'],
                        d['lifecycle_status'], d['vendor_label'], e.get('dated', ''), e.get('quote') or e.get('basis', ''),
                        e.get('url') or (byid[e['source_id']]['final_url'] if e.get('source_id') else ''), e.get('sha256', ''),
                        d['release_date'], d['noted_by']])
    text.extend(['', '## Devices', '',
                 'Identity level says whether the entry is a product family, one model or one catalogue number. Lifecycle status rests only on what the vendor says in a dated source; the date is the one the vendor states or, failing that, the day the source was retrieved. Release date is recorded apart and decides nothing. Exact model, hardware revision and firmware are stated per finding below, as the cited document names them.', '']
                + ([f'{len(bare)} devices without a review row are left out of this table. devices.csv lists all {len(products)} with their lifecycle evidence.', ''] if bare else [])
                + ['| Manufacturer | Model | Category | Identity level | Lifecycle status | Dated vendor evidence | Release date |', '|---|---|---|---|---|---|---|'])
    text.extend(f"| {md(products[pid].get('vendor', ''))} | {model(pid)} | {md(category(pid))} | {d['identity_level'].replace('_', ' ') or 'not established'} | "
                f"{lifecycle(pid)}{' (vendor label: ' + md(d['vendor_label']) + ')' if d['vendor_label'] else ''} | {md(dated(d))} | "
                f"{md(d['release_date'] or 'not established')} |" for pid, d in devices.items() if pid not in bare)
    text.extend(['', '## Summary by vendor, category and lifecycle' if grouped else '## Summary by vendor and category', '',
                 'Devices, counted once each, by what the review established for a control protocol. "In the catalogue" is the number of classified entries in the vendor catalogue for that stratum, where the config was drawn from an inventory. A stratum with few devices in this run supports no generalisation.', '',
                 '| Vendor | Category | Lifecycle | In the catalogue | In this run | ' + ' | '.join(f'{name.capitalize()} of a control protocol' for name in PROPERTIES) + ' |',
                 '|---|---|---|---|---|' + '---|' * len(PROPERTIES)])
    wording = (('supported', 'supported'), ('conditional', 'conditional'), ('gateway', 'via external gateway only'),
               ('explicitly_unsupported', 'explicitly unsupported'), ('silent', 'unknown: complete document silent'),
               ('conflict', 'unknown: sources conflict'), ('other', 'unknown: other interface only'),
               ('unknown', 'unknown'), (None, 'not reviewed'))
    strata, listed = {}, Counter()
    for x in cfg.get('frame') or []:
        listed[x['vendor'], x['category'], life_words(x['lifecycle']) if grouped else '-'] += x['in_catalogue']
    for pid, p in products.items():
        strata.setdefault((p.get('vendor', ''), category(pid), lifecycle(pid) if grouped else '-'), []).append(pid)
    for key in sorted(set(strata) | set(listed)):
        cells = []
        for feature in PROPERTIES:
            tally = Counter(bucket(pid, feature) for pid in strata.get(key, []))
            cells.append(', '.join(f'{tally[k]} {name}' for k, name in wording if tally[k]) or '-')
        text.append(f"| {md(key[0])} | {md(key[1])} | {key[2]} | {listed.get(key, '-')} | {len(strata.get(key, []))} | " + ' | '.join(cells) + ' |')
    text.extend(['', '## Findings by product and interface', '',
                 'One row per product and interface. Authentication, integrity and encryption are stated for that interface only; a result for a management interface says nothing about control traffic. "Evidence applies to" is the exact model, hardware revision and firmware the cited documents name. Default, activation and deployment are stated for supported and conditional findings. Full quotes are under "Findings and evidence" and in findings_table.csv; source references are resolved under "Sources examined".', '']
                + ([f'{len(bare)} products have no review row yet. They are left out of this table and counted as not reviewed in the summary above.', ''] if bare else [])
                + ['| ' + ' | '.join(COLUMNS) + ' |', '|' + '---|' * len(COLUMNS)])
    text.extend('| ' + ' | '.join(md(shown(row) if c == 'Evidence' else row[c]) for c in COLUMNS) + ' |'
                for row in table if row['pid'] not in bare)
    order, doubts = ['supported', 'conditional', 'gateway', 'explicitly_unsupported'], ['silent', 'conflict', 'other', 'unknown']
    text.extend(['', '## Counts by category and lifecycle group' if grouped else '## Counts by category', '',
                 'Products, not leads or table rows. Each product is counted once per capability, under its most favourable documented result for a control protocol. Unknown is one result; the four columns after it say why. "Other interface only" means a result exists for a management or network interface but none for a control protocol. A capability reached only through an external gateway is counted apart and is not the device\'s own. The last column is the denominator.'
                 + (' The same results are counted for every lifecycle group.' if grouped else ''), '',
                 '| Category | Capability | Supported | Conditional | Via external gateway only | Explicitly unsupported | Unknown | of which complete document silent | of which sources conflict | of which other interface only | of which not enough evidence | Not reviewed | Products |',
                 '|---|---|---|---|---|---|---|---|---|---|---|---|---|'])
    for stratum in dict.fromkeys(map(stratum_of, products)):
        members = [pid for pid in products if stratum_of(pid) == stratum]
        for c in CAPABILITIES:
            tally = Counter(bucket(pid, c) for pid in members)
            cells = [tally[k] for k in order] + [sum(tally[k] for k in doubts)] + [tally[k] for k in doubts] + [tally[None]]
            text.append(f'| {md(stratum)} | {c} | ' + ' | '.join(map(str, cells)) + f' | {len(members)} |')
    text.extend(['', '## Capability matrix', '',
                 'S supported, C conditional, G only through an external gateway, X explicitly unsupported, ? unknown (?s a complete document was searched and is silent, ?c sources conflict), - not reviewed. A mark in parentheses is established only for a management or network interface, not for a control protocol.', '']
                + ([f'{len(bare)} products without a review row are left out; every cell of theirs is "not reviewed".', ''] if bare else [])
                + ['| Product | Category | ' + ' | '.join(CAPABILITIES) + ' |', '|---|---|' + '---|' * len(CAPABILITIES)])
    text.extend(f'| {model(pid)} | {md(stratum_of(pid))} | ' + ' | '.join(matrix(pid, c) for c in CAPABILITIES) + ' |'
                for pid in products if pid not in bare)
    # How each supported or conditional capability ships and what switching it on takes, as far as the documents say.
    stated = [r for r in rows if r['status'] in ('supported', 'conditional')]
    text.extend(['', '## Default configuration, activation and deployment', '',
                 'Findings with a supported or conditional result, one per capability and interface. "Undocumented" means the documents read do not say whether the capability is on by default; "not assessed" means the reviewer has not looked yet. Neither means disabled.', ''])
    if stated:
        text.extend(['| Capability | Findings | Default enabled | Default disabled | Default undocumented | Default not assessed | Activation needs stated | Activation: none stated | Activation not assessed |',
                     '|---|---|---|---|---|---|---|---|---|'])
        for c in CAPABILITIES:
            mine = [facts(r) for r in stated if r['feature'] == c]
            if mine:
                d = Counter(f['default'] for f in mine)
                a = Counter('waiting' if f['needs'] == [NOT_ASSESSED] else 'none' if f['needs'] == ['none_stated'] else 'stated' for f in mine)
                text.append(f"| {c} | {len(mine)} | {d['enabled']} | {d['disabled']} | {d['undocumented']} | {d[NOT_ASSESSED]} | "
                            f"{a['stated']} | {a['none']} | {a['waiting']} |")
        text.append('')
    fielded = [r for r in rows if facts(r)['deployment'] != 'unknown']
    text.append((f'Deployment status is unknown for {len(stated) - sum(r in fielded for r in stated)} of {len(stated)} findings. ' if stated
                 else 'No supported or conditional finding is recorded yet. ')
                + 'Vendor documents show what a device can do, not what an operator has enabled, so enabled or disabled in practice is recorded only where evidence from an installation is cited.')
    for r in fielded:
        proof = '; '.join(flat(', '.join(e[k] for k in ('kind', 'reference', 'date', 'scope'))) for e in r['deployment_evidence'])
        text.append(f"- {model(r['product_id'])}, {r['feature']} on {flat(r.get('interface') or 'no interface stated')}: {facts(r)['deployment']} ({proof})")
    if claims:
        # The scope and the quoted words sit next to each result, so a second reader can check them without the CSV.
        text.extend(['', '## Findings and evidence', '',
                     'Every row that rests on cited sources: each result, and each unknown recorded because a complete document is silent or sources conflict. Quotes are verbatim from the cited location of the retained source.'])
        for r in claims:
            text.extend(['', f"### {model(r['product_id'])}: {r['feature']} ({named(r)})", '',
                         f"- Interface: {flat(r['interface'])} ({r['interface_class'].replace('_', ' ')})"])
            text.extend(f'- {name}: {flat(r[key]).replace(NOT_ASSESSED, "not assessed")}' for name, key in
                        (('Protocol', 'protocol'), ('Model scope', 'model_scope'), ('Hardware revision', 'hardware_revision'),
                         ('Firmware', 'firmware'), ('Implementation', 'implementation'), ('Conditions', 'conditions'),
                         ('Location', 'location')) if r.get(key))
            if r in stated:
                f = facts(r)
                text.extend([f"- Support basis: {words(f['basis'])}", f"- Default configuration: {f['default'].replace('_', ' ')}",
                             f"- Activation: {words(f['needs'])}" + (f": {flat(r['activation_requirements'])}" if r.get('activation_requirements') else ''),
                             f"- Deployment: {f['deployment']}"])
            text.extend(f"- Evidence{'' if (e.get('about') or 'capability') == 'capability' else ' on ' + e['about']}, "
                        f'{e["location"]}: "{flat(e["quote"])}"' for e in r.get('evidence') or [])
            if id(r) in searched:
                text.append(f'- Searched: {searched[id(r)]}')
            text.extend(f"- Source: {cite[sid]} {byid[sid]['final_url']}" for sid in r['source_ids'])
            text.append(f"- Review status: {r.get('review_status') or 'draft'} ({flat(r['reviewer'])})")
    text.extend(['', '## Reviewed rows', '', '| Product | Capability | Interface | Review result | Scope |', '|---|---|---|---|---|'])
    for r in rows:
        text.append('| ' + ' | '.join(md(x) for x in [model(r['product_id']), r['feature'], flat(r.get('interface') or '') or '-',
                                                     named(r), r['rationale']]) + ' |')
    unresolved = {pid: [c for c in CAPABILITIES if not any(x in ('supported', 'conditional', 'gateway', 'explicitly_unsupported')
                                                           for x in results(pid, c, INTERFACE_CLASSES))] for pid in products}
    text.extend(['', '## Unresolved cells', '',
                 f'{sum(map(len, unresolved.values()))} of {expected} cells are unknown or not reviewed on every interface.', '']
                + ([f'This includes all {len(bare) * len(CAPABILITIES)} cells of the {len(bare)} products without a review row, which are not listed one by one.', ''] if bare else []))
    text.extend(f"- {model(pid)}: {', '.join(left)}" for pid, left in unresolved.items() if left and pid not in bare)
    profiles = [(s, load(run / (s['id'] + '.profile.json'))) for s in sources if s.get('profile_items')]
    if profiles:
        text.extend(['', '## Device profile statements', '',
                     'Read by the tool from section 1.12, Security Parameters, of a DNP3 Device Profile. Marked options are detected by a heuristic and nothing in this table has been reviewed. A finding still needs a review row that quotes the item.', '',
                     '| Product | Source | Item | Title | Options that appear marked | Location |', '|---|---|---|---|---|---|'])
        text.extend(f"| {model(s['product_id'])} | {s['ref']} | {i['item']} | {md(i['title'])} | "
                    f"{md('; '.join(i['marked']) or 'none detected')} | {i['location']} |" for s, items in profiles for i in items)
    read = [s for s in sources if s['status'] == 'extracted']
    used = {sid for r in rows for sid in r['source_ids']}
    wide = len(read) > 60
    if wide:
        # What kind of document the survey rests on, per vendor, says more at this scale than a row per source.
        text.extend(['', '## What was read', '',
                     'Extracted sources by vendor and document type. A type marked "suggested" is the tool\'s guess from the title, URL and opening text until a reviewer confirms it in the source notes. A vendor whose sources are mostly product pages and brochures has little that can settle a capability either way.', '',
                     '| Vendor | Document type | Sources | PDF pages |', '|---|---|---|---|'])
        kinds, pages = Counter(), Counter()
        for s in read:
            kind = s['document']['doc_type'] or (s['doc_type_suggested'] + ' (suggested)' if s.get('doc_type_suggested') else 'not established')
            key = (products[s['product_id']].get('vendor', ''), kind.replace('_', ' '))
            kinds[key] += 1
            pages[key] += s.get('pages') or 0
        text.extend(f'| {md(v)} | {kind} | {n} | {pages[v, kind] or "-"} |' for (v, kind), n in sorted(kinds.items()))
    text.extend(['', '## Sources examined', '',
                 'Type, number, revision and document date are what a reviewer confirmed or read off the document; "not established" and "suggested" mean nobody has yet. Types are listed in the README from most to least direct about what one product and firmware can do. Titles and PDF dates are what the file says about itself, and a PDF creation date is not necessarily a publication date.', '']
                + ([f'Of {len(read)} extracted sources, the {len(used & {s["id"] for s in read})} cited by a review row are listed here. sources.json lists all of them.', ''] if wide else [])
                + ['| Ref | Product | Document | Type | Number and revision | Document date | Retrieved | SHA-256 | URL |', '|---|---|---|---|---|---|---|---|---|'])
    for s in sources:
        if s['status'] == 'extracted' and (not wide or s['id'] in used):
            made = re.match(r'D:(\d{4})(\d{2})(\d{2})', s.get('pdf_created', ''))
            said = [s.get('title') or 'untitled'] + ([f"{s['pages']} PDF pages"] if s.get('pages') else []) + (['PDF created ' + '-'.join(made.groups())] if made else [])
            doc = s['document']
            kind = doc['doc_type'] or ('suggested: ' + s['doc_type_suggested'] if s.get('doc_type_suggested') else 'not established')
            kind += f", {doc['coverage']}" if doc['coverage'] else ''
            text.append(f"| {s['ref']} | {model(s['product_id'])} | {md(', '.join(said))} | {kind.replace('_', ' ')} | "
                        f"{md(', '.join(filter(None, [doc['document_id'], doc['revision'] and 'revision ' + doc['revision']])) or 'not established')} | "
                        f"{md(doc['document_date'] or 'not established')} | {s.get('retrieved_at', '')[:10]} | {s['sha256']} | {md(s['final_url'])} |")
    missing = [s for s in sources if s['status'] in ('failed', 'duplicate', 'login_required')]
    if len(missing) > 40:
        # Too many to list one by one; sources.json has every URL. What matters here is how much each vendor withholds.
        text.extend(['', '## Sources without extracted text', '',
                     'Counted by vendor and outcome; every URL is in sources.json. "Sign-in" rows count links to documents that exist but are not public, so they were not requested.', '',
                     '| Vendor | Outcome | Sources |', '|---|---|---|'])
        kinds = Counter()
        for s in missing:
            kinds[products[s['product_id']].get('vendor', ''),
                  'behind a sign-in, not requested' if s['status'] == 'login_required'
                  else 'duplicate of another source' if s['status'] == 'duplicate'
                  else re.sub(r'https?://\S+', '<url>', s.get('error', ''))[:80]] += s.get('link_count', 1)
        text.extend(f'| {md(v)} | {md(outcome)} | {n} |' for (v, outcome), n in sorted(kinds.items()))
    elif missing:
        text.extend(['', '## Sources without extracted text', '', '| Product | URL | Outcome |', '|---|---|---|'])
        text.extend(f"| {model(s['product_id'])} | {md(s['url'])} | "
                    f"{md(s.get('error') or 'duplicate of ' + s['duplicate_of'])} |" for s in missing)
    text.extend(['', f'Review coverage: {len(reviewed)}/{expected} product–capability cells. Unreviewed cells carry no result.', '',
                 f"Evidence quotes: {sum(bool(r.get('evidence')) for r in rows if r['status'] != 'unknown')} of {sum(r['status'] != 'unknown' for r in rows)} rows with a result other than unknown carry a quote that was checked against the cited passage.", '',
                 f'Unknown because a complete document is silent: {len(searched)} rows, each checked to cite only complete documents in which the search found no lead for that capability.', '',
                 'See findings.csv for source URLs, hashes, interface, firmware and review provenance, and devices.csv for lifecycle evidence. No population percentages are computed.'])
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
    made = load(run / 'manifest.json') if (run / 'manifest.json').exists() else {}
    made_by = made.get('extraction_version') or made.get('tool_version') or EXTRACTION
    if made_by != EXTRACTION:
        # Extraction and lead rules are part of a version; a mismatch here is expected, not corruption.
        raise ValueError(f'run was produced with extraction rules {made_by} and this tool uses {EXTRACTION}; '
                         'replay it with that version of survey.py, or use rebuild')
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
    files, found, queue = sitemap_urls(f, queue, domains, limit)
    chosen = sorted(u for u in found if re.search(match, u, re.I))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dump(dest, {'tool_version': VERSION, 'retrieved_at': now(), 'domains': domains, 'match': match,
                'files': files, 'not_fetched': queue, 'total_urls': len(found), 'matched_urls': len(chosen),
                'urls': chosen, 'requests': f.audit})
    print(f'{len(chosen)} of {len(found)} URLs match; {len(queue)} sitemap files not fetched')


CATEGORIES = ('protective_relay', 'controller_rtu', 'plc', 'meter')


def sitemap_urls(f, queue, domains, limit=20, only=None):
    """Reads sitemap files, following index files, and returns a record per file, the page URLs and what was left."""
    queue, files, found = list(queue), [], {}  # found: page URL -> the sitemap file that listed it
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
                # A large site splits its sitemap by content type; only the listed kinds are worth a request.
                queue += [u for u in locs if not only or re.search(only, u, re.I)]
            else:
                for u in locs:
                    found.setdefault(u, rec['url'])
            rec.update(final_url=meta['final_url'], sha256=meta['sha256'], retrieved_at=meta['retrieved_at'],
                       kind='index' if index else 'urlset', entries=len(locs))
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
        files.append(rec)
        print(rec.get('kind', 'failed'), rec.get('entries', rec.get('error')), rec['url'], flush=True)
    return files, found, queue


def sel_product_selector(f, spec):
    """SEL product pages are empty without JavaScript, so the catalogue is the JSON list those pages load."""
    meta, body = f.fetch(spec['catalogue_api'], spec['domains'])
    items = []
    for i in json.loads(body)['items']:
        content, form = i.get('content') or {}, i.get('smartForm') or {}
        if content.get('quicklink'):
            kind, teaser = (' '.join(unescape(re.sub(r'<[^>]+>', ' ', x if isinstance(x, str) else '')).split())
                            for x in (form.get('subtitle'), content.get('teaser')))
            # The subtitle is the vendor's own one-line statement of what the product is; rules classify on it.
            items.append({'url': urljoin(spec['catalogue_api'], content['quicklink']), 'listed_in': spec['catalogue_api'],
                          'model': content.get('title') or '',
                          'kind': kind, 'summary': '. '.join(x for x in (kind, teaser) if x),
                          'documents': [urljoin(spec['catalogue_api'], f"/api/download/{d['id']}/")
                                        for d in form.get('selectDownloads') or [] if isinstance(d, dict) and d.get('id')]})
    return [{'url': spec['catalogue_api'], 'final_url': meta['final_url'], 'sha256': meta['sha256'],
             'retrieved_at': meta['retrieved_at'], 'kind': 'product list', 'entries': len(items)}], items


ADAPTERS = {'sel_product_selector': sel_product_selector}


def model_name(url):
    slug = re.sub(r'^\d{2,}-', '', re.sub(r'\.html?$', '', url.rstrip('/').rsplit('/', 1)[-1]))
    return ' '.join(w.upper() if re.search(r'\d', w) else w.capitalize() for w in slug.split('-') if w)


def first_rule(rules, fields):
    """The first rule that matches. Each rule reads one field: 'url', 'slug' (last path segment) or 'text'."""
    return next((r for r in rules or [] if fields.get(r.get('on', 'url')) and re.search(r['match'], fields[r.get('on', 'url')], re.I)), None)


MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
DATED = re.compile(rf'\b(?:(?:{MONTHS})\s+(?:\d{{1,2}},?\s+)?(?:19|20)\d{{2}}|\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTHS})\s+(?:19|20)\d{{2}}'
                   r'|(?:19|20)\d{2}-\d{2}-\d{2})\b', re.I)


def stated_date(text, start, end):
    """A date the vendor gives in the same sentence as a lifecycle notice, as written. Empty when the sentence has none."""
    a = max((m.end() for m in STOP.finditer(text, max(0, start - 300), start)), default=max(0, start - 300))
    b = min((m.start() for m in STOP.finditer(text, end, min(len(text), end + 300))), default=min(len(text), end + 300))
    found = DATED.search(text, a, b)
    return found.group(0) if found else ''


def classify(key, spec, items, files=()):
    """One entry per catalogue item in scope: included, excluded with a reason, or unclassified. Nothing is dropped."""
    entries, ids = [], set()
    for item in sorted(items, key=lambda x: x['url']):
        url = item['url']
        if not re.search(spec.get('scope', ''), url, re.I):
            continue
        model = item.get('model') or model_name(url)
        slug = re.sub(r'[^a-z0-9]+', '_', model.lower()).strip('_')
        stem = base = slug if slug.startswith(key + '_') else f'{key}_{slug}'
        while stem in ids:
            stem = f'{base}_{len(ids)}'
        ids.add(stem)
        entry = {'id': stem, 'vendor_key': key, 'vendor': spec['vendor'], 'model': model, 'model_basis': 'catalogue listing',
                 'product_url': url, 'domains': spec['domains'], 'category': 'unclassified', 'included': False,
                 'reason': 'no category rule matched'}
        entry.update({k: item[k] for k in ('summary', 'documents') if item.get(k)})
        fields = {'url': url, 'slug': re.sub(r'\.html?$', '', url.rstrip('/').rsplit('/', 1)[-1]).lower(),
                  'text': f"{model} {item.get('kind', '')}".strip()}
        decide(entry, spec, fields, 'catalogue listing')
        life = first_rule(spec.get('lifecycle'), fields)
        basis = f"catalogue listing matches {life['match']}" if life else 'listed in the vendor catalogue without a notice of discontinuation'
        # A catalogue listing is the vendor saying, on the day it was retrieved, that the product is on offer.
        held = [f for f in files if f.get('sha256') and f.get('kind') != 'index']
        listed = [f for f in held if f['url'] == item.get('listed_in')] or held
        entry.update(lifecycle=life['value'] if life else 'currently_supported', vendor_label=life.get('vendor_label', '') if life else '',
                     lifecycle_basis=basis,
                     lifecycle_evidence=[{'basis': basis, 'url': f['url'], 'sha256': f['sha256'], 'retrieved_at': f['retrieved_at']} for f in listed])
        entries.append(entry)
    return entries


def decide(entry, spec, fields, basis):
    """Applies a vendor's category and exclusion rules to what is known about one entry. An exclusion always wins."""
    rule, out = first_rule(spec.get('rules'), fields), first_rule(spec.get('exclude'), fields)
    if rule:
        entry.update(category=rule['category'], category_basis=f"{basis} matches {rule['match']}", included=True, reason='')
    if out:
        entry.update(included=False, reason=out['reason'], excluded_by=f"{basis} matches {out['match']}")


def write_inventory(dest, inv):
    """inventory.json for the tool, inventory.csv for a person; both list every entry with the rule that placed it."""
    counts = Counter()
    for e in inv['entries']:
        state = 'included' if e['included'] else 'excluded' if e.get('excluded_by') else 'unclassified'
        counts[e['vendor'], e['category'], e['lifecycle'], state] += 1
    inv['summary'] = [{'vendor': v, 'category': c, 'lifecycle': life, 'state': state, 'entries': n}
                      for (v, c, life, state), n in sorted(counts.items())]
    dump(dest / 'inventory.json', inv)
    columns = ['id', 'vendor', 'model', 'category', 'lifecycle', 'vendor_label', 'included', 'reason', 'product_url', 'category_basis',
               'lifecycle_basis', 'lifecycle_evidence_date', 'lifecycle_evidence_quote', 'lifecycle_evidence_url', 'excluded_by',
               'model_basis', 'page_status', 'summary']
    with (dest / 'inventory.csv').open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=columns, extrasaction='ignore')
        w.writeheader()
        for e in inv['entries']:
            proof = (e.get('lifecycle_evidence') or [{}])[0]
            w.writerow(dict(e, lifecycle_evidence_date=proof.get('stated_date') or (proof.get('retrieved_at') or '')[:10],
                            lifecycle_evidence_quote=proof.get('quote', ''), lifecycle_evidence_url=proof.get('url', '')))
    for vendor in dict.fromkeys(e['vendor'] for e in inv['entries']):
        mine = [e for e in inv['entries'] if e['vendor'] == vendor]
        kept = Counter((e['category'], e['lifecycle']) for e in mine if e['included'])
        print(f"{vendor}: {len(mine)} in scope; included {sum(kept.values())} "
              f"{dict(sorted((f'{c}/{life}', n) for (c, life), n in kept.items()))}; "
              f"excluded {sum(bool(e.get('excluded_by')) for e in mine)}; "
              f"unclassified {sum(not e['included'] and not e.get('excluded_by') for e in mine)}", flush=True)


def check_rules(spec):
    """A rules file is refused as a whole before anything is fetched or written."""
    for key, v in spec['vendors'].items():
        for rule in v.get('rules', []):
            if rule.get('category') not in CATEGORIES:
                raise ValueError(f'{key}: rule category must be one of {", ".join(CATEGORIES)}')
        for rule in v.get('lifecycle', []) + v.get('lifecycle_text', []):
            if rule.get('value') not in LIFECYCLES:
                raise ValueError(f'{key}: lifecycle value must be one of {", ".join(LIFECYCLES)}')
        for rule in v.get('rules', []) + v.get('exclude', []) + v.get('lifecycle', []) + v.get('lifecycle_text', []):
            re.compile(rule['match'])
    return spec


def inventory(vendors_path, dest, cache, source=None, delay=1.2):
    """Lists every catalogue device of the configured vendors from their own sitemaps. A person decides what to change."""
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(dest)
    spec = check_rules(load(vendors_path))
    # A saved listing lets the rules be changed and re-applied without asking the vendors again.
    listing = load(Path(source) / 'catalogue.json') if source else {}
    f = Fetcher({'delay_seconds': delay, 'max_bytes': 80000000, 'timeout_seconds': 60,
                 'robots_follow_redirects': spec.get('robots_follow_redirects', False)}, cache)
    entries = []
    for key, v in spec['vendors'].items():
        if key not in listing:
            if v.get('adapter'):
                files, items = ADAPTERS[v['adapter']](f, v)
                left = []
            else:
                files, found, left = sitemap_urls(f, v['sitemaps'], v['domains'], v.get('max_files', 20), v.get('sitemap_filter'))
                items = [{'url': u, 'listed_in': found[u]} for u in sorted(found)]
            listing[key] = {'files': files, 'not_fetched': left, 'items': items}
        entries += classify(key, v, listing[key]['items'], listing[key]['files'])
    dest.mkdir(parents=True)
    dump(dest / 'catalogue.json', listing)
    # Re-applied rules keep the log of the requests that produced the listing they were applied to.
    dump(dest / 'requests.json', (load(Path(source) / 'requests.json') if source else []) + f.audit)
    write_inventory(dest, {'tool_version': VERSION, 'created_at': now(), 'vendors_sha256': digest(Path(vendors_path).read_bytes()),
                           'reapplied_from': str(source) if source else None, 'spec': spec, 'entries': entries})


def enrich(inventory_path, run, dest, vendors=None):
    """Adds what each product page says about itself: its title, and wording about its lifecycle, with the sentence kept."""
    dest, run = Path(dest), Path(run)
    if dest.exists():
        raise FileExistsError(dest)
    inv = load(inventory_path)
    if vendors:
        # Page wording is only known once the pages have been read, so these rules are usually written afterwards.
        inv.update(spec=check_rules(load(vendors)), vendors_sha256=digest(Path(vendors).read_bytes()))
    # Only the product page itself speaks for the entry; a document seeded in its place does not rename the device.
    pages = {(s['product_id'], s['url']): s for s in load(run / 'sources.json')}
    for e in inv['entries']:
        s, spec = pages.get((e['id'], canonical(e['product_url']))), inv['spec']['vendors'][e['vendor_key']]
        if not s:
            continue
        e['page_status'] = s['status'] + (f": {s['error']}" if s.get('error') else '')
        if s['status'] != 'extracted':
            continue
        title = (s.get('title') or '').split(' | ')[0].strip()
        if title:
            e.update(model=title, model_basis='product page title')
        text = ' '.join(squash(g['text']) for g in load(run / (s['id'] + '.segments.json')))
        if not e['included'] and not e.get('excluded_by'):
            # A catalogue URL that names no category: the page's own opening words decide, or it stays unclassified.
            decide(e, spec, {'text': f'{title} {text[:800]}'}, 'product page text')
        # 'within' keeps a rule to the opening of the page, where a notice is about this product and not a variant of it.
        life = next(((r, m) for r in spec.get('lifecycle_text', [])
                     for m in [re.search(r['match'], text[:r.get('within')], re.I)] if m), None)
        if life:
            rule, m = life
            # The vendor's own sentence, where it was read and when, and the date the sentence itself gives if it gives one.
            e.update(lifecycle=rule['value'], lifecycle_basis='product page wording', vendor_label=rule.get('vendor_label', e.get('vendor_label', '')),
                     lifecycle_evidence=[{'basis': 'product page wording', 'quote': passage(text, m.start(), m.end(), 120, 160),
                                          'stated_date': stated_date(text, m.start(), m.end()), 'url': s['final_url'],
                                          'sha256': s['sha256'], 'retrieved_at': s.get('retrieved_at')}])
    dest.mkdir(parents=True)
    inv.update(tool_version=VERSION, enriched_at=now(), enriched_from={'run': str(run), 'inventory': str(inventory_path)})
    write_inventory(dest, inv)


def sample(inventory_path, dest, per_stratum=None, seed=0, census=False):
    """Writes a crawl config from the inventory: every catalogue entry, or a seeded draw per vendor, category and lifecycle."""
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(dest)
    inv = load(inventory_path)
    kept = [e for e in inv['entries'] if e['included']]
    strata = {}
    for e in kept:
        strata.setdefault((e['vendor'], e['category'], e['lifecycle']), []).append(e)
    if census:
        # Unclassified pages are crawled too, so that their own text can classify them afterwards.
        chosen = [e for e in inv['entries'] if e['included'] or not (
            e.get('excluded_by') or inv['spec']['vendors'][e['vendor_key']].get('page_needs_javascript'))]
        how = (f"Census of the vendor catalogues: one product page for each of {len(chosen)} catalogue entries "
               f"({len(kept)} classified, {len(chosen) - len(kept)} awaiting classification from their own page).")
    else:
        if not per_stratum or per_stratum < 1:
            raise ValueError('sample needs --per-stratum of at least 1, or --census')
        chosen = []
        for key in sorted(strata):
            members = sorted(strata[key], key=lambda e: e['id'])
            # Each stratum has its own generator, so adding a vendor or a category never changes another stratum's draw.
            rng = random.Random(f'{seed}:' + '|'.join(key))
            chosen += members if len(members) <= per_stratum else sorted(rng.sample(members, per_stratum), key=lambda e: e['id'])
        how = (f"Stratified random sample: up to {per_stratum} devices per vendor, category and lifecycle stratum, seed {seed}, "
               f"drawn from {len(kept)} classified catalogue entries; strata with fewer entries are taken whole. "
               "A sample of catalogue entries, not of installed devices.")
    picked = Counter((e['vendor'], e['category'], e['lifecycle']) for e in chosen if e['included'])
    products = []
    for e in chosen:
        spec = inv['spec']['vendors'][e['vendor_key']]
        p = {'id': e['id'], 'vendor': e['vendor'], 'model': e['model'], 'category': e['category'], 'lifecycle': e['lifecycle'],
             'domains': e['domains'], 'seeds': [] if spec.get('page_needs_javascript') else [e['product_url']]}
        p.update({k: e[k] for k in ('vendor_label', 'lifecycle_basis', 'lifecycle_evidence') if e.get(k)})
        # Where the product page cannot be read, the census takes the product's first public document in its place.
        p['seeds'] += e.get('documents', [])[:spec.get('census_documents', 0) if census else spec.get('document_seeds', 3)]
        if not census:
            p.update(spec.get('crawl', {}))
        products.append(p)
    dump(dest, {'title': inv['spec'].get('title', 'IED security documentation survey'),
                'sampling': how + f" Inventory of {inv['created_at'][:10]}; categories and lifecycle come from the vendors' own catalogues and pages.",
                # What "legacy" and each lifecycle group mean, fixed in the config before the crawl and so before any count.
                **({'definitions': inv['spec']['definitions']} if inv['spec'].get('definitions') else {}),
                'seed': seed, 'per_stratum': per_stratum, 'census': census,
                'inventory': {'path': str(inventory_path), 'sha256': digest(Path(inventory_path).read_bytes()), 'created_at': inv['created_at']},
                'frame': [{'vendor': v, 'category': c, 'lifecycle': life, 'in_catalogue': len(members), 'selected': picked[v, c, life]}
                          for (v, c, life), members in sorted(strata.items())],
                'max_depth': 0, 'max_pages_per_product': 4, 'delay_seconds': 1.2, 'timeout_seconds': 60, 'max_bytes': 60000000,
                'robots_follow_redirects': inv['spec'].get('robots_follow_redirects', False), 'products': products})
    print(f'{len(products)} products written to {dest}')


def worksheet(run, dest):
    """Lays the leads out per product and capability for a reviewer. It organises; it proposes no result."""
    run, dest = Path(run), Path(dest)
    if dest.exists():
        raise FileExistsError(dest)
    cfg, sources, leads = load(run / 'config.json'), load(run / 'sources.json'), load_leads(run)
    refs = {s['id']: f'S{n}' for n, s in enumerate((s for s in sources if s['status'] == 'extracted'), 1)}
    found = {}
    for h in leads:
        found.setdefault((h['product_id'], h['feature']), []).append(h)

    def places(hits):
        shown = '; '.join(f"{refs[h['source_id']]} {h['location']} [{', '.join(h['matched'][:3]) or h.get('profile_item', '')}]" for h in hits[:8])
        return shown + (f' and {len(hits) - 8} more' if len(hits) > 8 else '')

    text = ['# Review worksheet', '',
            'Where each term occurs, per product and capability. A lead is a place to read, not a finding, and "no lead" in a source is not a statement that the device lacks the capability. Source references are local to this worksheet.', '']
    hints = {}
    for p in cfg['products']:
        mine = [s for s in sources if s['product_id'] == p['id']]
        read = [s for s in mine if s['status'] == 'extracted']
        text += ['', f"## {p.get('model') or p['id']}", '',
                 f"{p.get('vendor', '')}; {p.get('category', '')}; lifecycle {life_words(p.get('lifecycle'))}; id `{p['id']}`", '']
        proof = p.get('lifecycle_evidence')
        for e in proof if isinstance(proof, list) else []:
            said = '"' + e['quote'] + '"' if e.get('quote') else e.get('basis') or 'vendor source'
            text.append(f"- lifecycle evidence, {e.get('stated_date') or (e.get('retrieved_at') or '')[:10]}: {said} <{e.get('url', '')}>")
        text += [f"- {refs.get(s['id'], '--')} {s['status']}"
                 + (f", {s['doc_type_suggested'].replace('_', ' ')} (suggested)" if s.get('doc_type_suggested') else '')
                 + (f", {s['pages']} PDF pages" if s.get('pages') else '') + (f": {s['error']}" if s.get('error') else '')
                 + f" <{s['url']}>" for s in mine] or ['- no source']
        text.append('')
        for c in CAPABILITIES + STATEMENTS:
            hits = found.get((p['id'], c), [])
            quiet = [refs[s['id']] for s in read if not any(h['source_id'] == s['id'] for h in hits)]
            if c in CAPABILITIES:
                hints[p['id'], c] = {'leads': len(hits), 'where': [f"{refs[h['source_id']]} {h['location']}" for h in hits[:8]],
                                     'no_lead_in': quiet}
            if hits:
                text.append(f'- **{c}**: {len(hits)} leads: {places(hits)}')
            elif c in CAPABILITIES:
                text.append(f"- **{c}**: no lead" + (f" in {', '.join(quiet)}" if quiet else ''))
            for kind, word in (('default_statement', 'default'), ('requirement_statement', 'requirement')) if c in CAPABILITIES else ():
                # Where to read for how the capability ships and what it needs: wording that names this capability.
                near = [h for h in found.get((p['id'], kind), []) if LEADS[c].search(' '.join(h['matched']))]
                hints[p['id'], c][f'{word}_wording'] = [f"{refs[h['source_id']]} {h['location']}" for h in near[:8]]
                if near:
                    text.append(f'  - {word} wording: {places(near)}')
    dest.mkdir(parents=True)
    (dest / 'worksheet.md').write_text('\n'.join(text) + '\n', encoding='utf-8', newline='\n')
    # The same template the crawl wrote, with the hints beside each cell. Hints are not review fields and are ignored.
    dump(dest / 'review_template.json', [dict(row, _hints=hints.get((row['product_id'], row['feature']), {}))
                                         for row in load(run / 'review_template.json')])
    print(f'Worksheet for {len(cfg["products"])} products written to {dest}')


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')  # Document text may not fit the console code page.
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('crawl'); c.add_argument('--config', required=True); c.add_argument('--out', required=True); c.add_argument('--cache', default='cache'); c.add_argument('--resume', action='store_true'); c.add_argument('--reuse', action='append'); c.add_argument('--only')
    i = sub.add_parser('inventory'); i.add_argument('--vendors', required=True); i.add_argument('--out', required=True); i.add_argument('--cache', default='cache'); i.add_argument('--from', dest='source')
    e = sub.add_parser('enrich'); e.add_argument('--inventory', required=True); e.add_argument('--run', required=True); e.add_argument('--out', required=True); e.add_argument('--vendors')
    s = sub.add_parser('sample'); s.add_argument('--inventory', required=True); s.add_argument('--out', required=True); s.add_argument('--per-stratum', type=int); s.add_argument('--seed', type=int, default=0); s.add_argument('--census', action='store_true')
    w = sub.add_parser('worksheet'); w.add_argument('--run', required=True); w.add_argument('--out', required=True)
    r = sub.add_parser('report'); r.add_argument('--run', required=True); r.add_argument('--reviews', required=True); r.add_argument('--out', required=True); r.add_argument('--require-evidence', action='store_true'); r.add_argument('--source-notes'); r.add_argument('--device-notes')
    v = sub.add_parser('verify'); v.add_argument('--run', required=True); v.add_argument('--cache', default='cache')
    x = sub.add_parser('replay'); x.add_argument('--run', required=True); x.add_argument('--cache', default='cache'); x.add_argument('--out', required=True)
    b = sub.add_parser('rebuild'); b.add_argument('--run', required=True); b.add_argument('--cache', default='cache'); b.add_argument('--out', required=True)
    k = sub.add_parser('recheck'); k.add_argument('--old', required=True); k.add_argument('--new', required=True); k.add_argument('--out')
    m = sub.add_parser('sitemap'); m.add_argument('--url', action='append', default=[]); m.add_argument('--host'); m.add_argument('--domain', action='append', default=[])
    m.add_argument('--match', default='.'); m.add_argument('--out', required=True); m.add_argument('--cache', default='cache'); m.add_argument('--max-files', type=int, default=20); m.add_argument('--delay', type=float, default=1.0)
    args = p.parse_args()
    try:
        if args.cmd == 'crawl': crawl(args.config, args.out, args.cache, args.resume, args.reuse, args.only)
        elif args.cmd == 'inventory': inventory(args.vendors, args.out, args.cache, args.source)
        elif args.cmd == 'enrich': enrich(args.inventory, args.run, args.out, args.vendors)
        elif args.cmd == 'sample': sample(args.inventory, args.out, args.per_stratum, args.seed, args.census)
        elif args.cmd == 'worksheet': worksheet(args.run, args.out)
        elif args.cmd == 'report': report(args.run, args.reviews, args.out, args.require_evidence, args.source_notes, args.device_notes)
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

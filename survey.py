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

VERSION = '1.1.0'
UA_TOKEN = 'IEDSecuritySurvey'
UA = UA_TOKEN + '/1.1 (public-document research; no device scanning)'
# Review cells. Changing this tuple changes every denominator; lead groups below may grow freely.
CAPABILITIES = ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'authentication', 'encryption', 'ssh')
PATTERNS = {
    'dnp3_secure_authentication': r'secure\s+auth\w*|\b(?-i:SA)\s*v\d\b|\bDNP\s*3?.{0,80}?\b(?-i:SA)\b|\bIEC\s*62351-5\b',
    'tls': r'\bm?TLS(?:\s?v?\d(?:\.\d)?)?\b|transport\s+layer\s+security|\bSSL\b',
    'ipsec': r'\bIP\s?sec\b|\bIP\s+security\b|\b(?-i:IKE)(?:v[12])?\b|\bVPN\b',
    # ODVA's CIP Security, not NERC CIP: the two share an acronym and nothing else.
    'cip_security': r'(?-i:(?<!NERC[\s-])\bCIP\s+Security(?![a-z]))',
    'authentication': r'\bauthenticat\w*|\bRADIUS\b|\b802\.1X\b|\bLDAP\b|\bKerberos\b|\bTACACS\b',
    'encryption': r'\b(?:un|non-?)?encrypt\w*|\bDTLS\b|\bAES\b|\bcipher\w*',
    'ssh': r'\bSSH\b|secure\s+shell|\bSFTP\b',
    # Lead-only groups below: shown to the reviewer, never review cells.
    'plaintext_statement': r'\bunencrypted\b|\bnon-?encrypted\b|\bnot\s+(?:be\s+|been\s+|being\s+)?encrypted\b'
                           r'|\bno\s+encryption\b|\bwithout\s+encryption\b'
                           r"|\b(?:not|n['\u2019]t)\s+(?:support|provide|offer|include|implement|use)\w*\s+(?:\w+\s+){0,3}?encryption\b"
                           r'|\bplain\s?-?text\b|\bclear\s?-?text\b|\bin\s+the\s+clear\b',
    'macsec': r'\bMACsec\b|\b802\.1AE\b',
    'iec_62351': r'\bIEC(?:/TS)?\s*62351(?:-\d+)?\b',
}
LEADS = {k: re.compile(v, re.I | re.S) for k, v in PATTERNS.items()}
# A lead in these groups also needs the qualifying term close by.
NEAR = {'dnp3_secure_authentication': re.compile(r'\bDNP|\b1815\b|62351-5', re.I)}
STATUSES = {'supported', 'conditional', 'explicitly_unsupported', 'unknown', 'conflicting'}
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


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.links, self.skip = [], [], 0
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
            self.flush()
            self.kind = 'heading' if tag in HEADINGS else 'title' if tag == 'title' else self.kind

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag == 'a':
            self.end_anchor()
        if tag in BLOCKS:
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
        return segs, [], facts
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
    return segs, page.links, {'kind': 'html', 'title': page.title}


def extract(body, headers):
    segs, links, _ = parse(body, headers)
    return segs, [href for href, _ in links]


def alias_pattern(aliases):
    if not aliases:
        return None
    return re.compile('(?<![A-Za-z0-9])(?:' + '|'.join(re.escape(a) for a in aliases) + ')(?![A-Za-z0-9])', re.I)


def candidates(source, segments, aliases=()):
    hits, alias = [], alias_pattern(aliases)
    texts = [norm(s['text']) for s in segments]
    for i, segment in enumerate(segments):
        text = texts[i]
        for feature, pattern in LEADS.items():
            found = list(pattern.finditer(text))
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
            hit = {'id': cid, 'source_id': source['id'], 'product_id': source['product_id'],
                   'feature': feature, 'location': segment['location'],
                   'context': text[max(0, match.start()-220):match.end()+350],
                   'match_count': len(found), 'status': 'unreviewed'}
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
        sources, hits, audit = (load(out / n) if (out / n).exists() else []
                                for n in ('sources.json', 'candidates.json', 'requests.json'))
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
                            rec.update(facts, status='extracted', text_sha256=text_digest(segs))
                            if alias:
                                rec['model_mentions'] = sum(bool(alias.search(norm(s['text']))) for s in segs)
                            dump(out / (rec['id'] + '.segments.json'), segs)
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
                dump(out / 'candidates.json', hits)
                dump(out / 'requests.json', f.audit)
                print(product['id'], rec['status'], url, flush=True)
    # Written once more so a run without any seeds still has all three files.
    dump(out / 'sources.json', sources)
    dump(out / 'candidates.json', hits)
    dump(out / 'requests.json', f.audit)
    dump(out / 'manifest.json', {'tool_version': VERSION, 'finished_at': now(),
        'config_sha256': digest(config_bytes), 'python': sys.version,
        'script_sha256': digest(Path(__file__).read_bytes()),
        'complete': True, 'source_count': len(sources), 'candidate_count': len(hits),
        'source_status': dict(Counter(s['status'] for s in sources)),
        'config_warnings': warnings, 'sampling': cfg['sampling']})
    template = [{'product_id': p['id'], 'feature': feature, 'status': 'unknown',
                 'source_ids': [], 'source_hashes': {}, 'location': '', 'protocol': '',
                 'interface': '', 'firmware': 'not established', 'implementation': 'not established',
                 'evidence': [], 'rationale': '', 'reviewer': '', 'reviewed_at': ''}
                for p in cfg['products'] for feature in CAPABILITIES]
    dump(out / 'review_template.json', template)


def validate_reviews(rows, sources, products, segments=None, require_evidence=False):
    byid = {s['id']: s for s in sources}
    seen = set()
    for r in rows:
        key = r['product_id'], r['feature']
        if key in seen or key[0] not in products or key[1] not in CAPABILITIES:
            raise ValueError(f'duplicate/unknown review key: {key}')
        seen.add(key)
        if r['status'] not in STATUSES:
            raise ValueError(f'invalid status: {key}')
        if not all(r.get(k) for k in ('reviewer', 'reviewed_at', 'rationale')):
            raise ValueError(f'review identity/date/rationale required, including unknowns: {key}')
        if r['status'] != 'unknown' and not r['source_ids']:
            raise ValueError(f'claim requires source evidence: {key}')
        if r['status'] != 'unknown' and not all(r.get(k) for k in ('location','protocol','interface','firmware','implementation')):
            raise ValueError(f'claim scope is incomplete: {key}')
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
            wanted = squash(e.get('quote', ''))
            if e.get('source_id') not in r['source_ids']:
                raise ValueError(f'evidence cites a source outside this review: {key}')
            if len(wanted) < 20:
                raise ValueError(f'evidence quote too short to identify a passage: {key}')
            if segments:
                text = next((x['text'] for x in segments(e['source_id']) if x['location'] == e.get('location')), None)
                if text is None or wanted not in squash(text):
                    raise ValueError(f"evidence quote not found at {e.get('location')} of source {e['source_id']}: {key}")


def untouched(row):
    """A template row nobody has filled in. It is not a finding: it is left out and counted as not reviewed."""
    blank = ('reviewer', 'reviewed_at', 'rationale', 'source_ids', 'source_hashes', 'evidence', 'location', 'protocol', 'interface')
    return row.get('status') == 'unknown' and not any(row.get(k) for k in blank)


def report(run, review_path, dest, require_evidence=False):
    run, dest = Path(run), Path(dest)
    cfg, sources, rows = load(run / 'config.json'), load(run / 'sources.json'), load(review_path)
    products = {p['id']: p for p in cfg['products']}
    # Lets a review proceed in stages. A partly filled row is still an error, never silently dropped.
    blank = sum(map(untouched, rows))
    rows = [r for r in rows if not untouched(r)]
    validate_reviews(rows, sources, products, lambda sid: load(run / (sid + '.segments.json')), require_evidence)
    dest.mkdir(parents=True, exist_ok=True)
    byid = {s['id']: s for s in sources}
    dump(dest / 'findings.json', rows)
    dump(dest / 'sources.json', sources)
    dump(dest / 'evidence_index.json', [
        {'product_id': r['product_id'], 'feature': r['feature'], 'status': r['status'], 'source_id': e['source_id'],
         'url': byid[e['source_id']]['final_url'], 'sha256': byid[e['source_id']]['sha256'],
         'location': e['location'], 'quote': e['quote'], 'retrieved_at': byid[e['source_id']].get('retrieved_at')}
        for r in rows for e in r.get('evidence') or []])
    if (run / 'candidates.json').exists():
        leads = {p: Counter() for p in products}
        for h in load(run / 'candidates.json'):
            leads[h['product_id']][h['feature']] += 1
        dump(dest / 'candidate_counts.json',
             {p: {'total': sum(c.values()), 'by_group': dict(sorted(c.items()))} for p, c in leads.items()})
    columns = ['product_id','vendor','model','category','feature','status','protocol','interface',
               'firmware','implementation','location','rationale','reviewer','reviewed_at','source_urls','source_hashes','evidence']
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

    def model(pid):
        return md(products[pid].get('model') or pid)

    def category(pid):
        return products[pid].get('category') or 'uncategorised'

    totals = Counter(s['status'] for s in sources)
    cells = {(r['product_id'], r['feature']): r['status'] for r in rows}
    expected = len(products) * len(CAPABILITIES)
    claims = [r for r in rows if r['status'] != 'unknown']
    line = (f"Products/families in seed inventory: {len(products)}. Sources attempted: {len(sources) - totals['skipped']}; "
            f"extracted: {totals['extracted']}; failed: {totals['failed']}")
    if totals['duplicate']:
        line += f"; duplicate of another source: {totals['duplicate']}"
    if totals['skipped']:
        line += f"; matched links not followed (page budget): {totals['skipped']}"
    text = [f"# {cfg.get('title', 'IED security documentation survey')}", '',
            f"Sampling: {cfg['sampling']}", '', line + '.', '',
            'This measures documented capabilities, not enabled settings, installed-base coverage or plaintext prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. Capability categories overlap, so counts below are review cells and must not be added up as devices.', '',
            'Reviewers on record: ' + ('; '.join(f'{md(name)} ({n} cells)' for name, n in Counter(r['reviewer'] for r in rows).items()) or 'none') + '.', '',
            '## Review matrix', '',
            'S supported, C conditional, X explicitly unsupported, ? unknown, ! conflicting, - not reviewed.', '',
            '| Product | Category | ' + ' | '.join(CAPABILITIES) + ' |', '|---|---|' + '---|' * len(CAPABILITIES)]
    mark = {'supported': 'S', 'conditional': 'C', 'explicitly_unsupported': 'X', 'unknown': '?', 'conflicting': '!'}
    for pid in products:
        text.append(f'| {model(pid)} | {md(category(pid))} | ' + ' | '.join(mark.get(cells.get((pid, c)), '-') for c in CAPABILITIES) + ' |')
    if claims:
        # The scope and the quoted words sit next to each result, so a second reader can check them without the CSV.
        text.extend(['', '## Findings and evidence', '',
                     'Every cell with a result other than unknown. Quotes are verbatim from the cited location of the retained source.'])
        for r in claims:
            text.extend(['', f"### {model(r['product_id'])}: {r['feature']} ({r['status'].replace('_', ' ')})", ''])
            text.extend(f"- {label}: {' '.join(str(r[key]).split())}" for label, key in
                        (('Protocol', 'protocol'), ('Interface', 'interface'), ('Firmware', 'firmware'),
                         ('Implementation', 'implementation'), ('Location', 'location')))
            text.extend(f'- Evidence, {e["location"]}: "{" ".join(e["quote"].split())}"' for e in r.get('evidence') or [])
            text.extend(f"- Source: {byid[sid]['final_url']}" for sid in r['source_ids'])
    order = ['supported', 'conditional', 'explicitly_unsupported', 'unknown', 'conflicting', None]
    text.extend(['', '## Counts by category', '',
                 'Each row counts the products in one category; the last column is the denominator.', '',
                 '| Category | Capability | Supported | Conditional | Explicitly unsupported | Unknown | Conflicting | Not reviewed | Products |',
                 '|---|---|---|---|---|---|---|---|---|'])
    for stratum in dict.fromkeys(map(category, products)):
        members = [pid for pid in products if category(pid) == stratum]
        for c in CAPABILITIES:
            tally = Counter(cells.get((pid, c)) for pid in members)
            text.append(f'| {md(stratum)} | {c} | ' + ' | '.join(str(tally[k]) for k in order) + f' | {len(members)} |')
    text.extend(['', '## Reviewed cells', '', '| Product | Capability | Review result | Scope |', '|---|---|---|---|'])
    for r in rows:
        text.append('| ' + ' | '.join(md(x) for x in
                    [model(r['product_id']), r['feature'], r['status'], r['rationale']]) + ' |')
    unresolved = {pid: [c for c in CAPABILITIES if cells.get((pid, c)) not in ('supported', 'conditional', 'explicitly_unsupported')]
                  for pid in products}
    text.extend(['', '## Unresolved cells', '',
                 f'{sum(map(len, unresolved.values()))} of {expected} cells are unknown, conflicting or not reviewed.', ''])
    text.extend(f"- {model(pid)}: {', '.join(left)}" for pid, left in unresolved.items() if left)
    text.extend(['', '## Sources examined', '',
                 'Titles and PDF dates are what each file says about itself; a PDF creation date is not necessarily a publication date.', '',
                 '| Product | Document | Retrieved | URL |', '|---|---|---|---|'])
    for s in sources:
        if s['status'] == 'extracted':
            made = re.match(r'D:(\d{4})(\d{2})(\d{2})', s.get('pdf_created', ''))
            facts = [s.get('title') or 'untitled'] + ([f"{s['pages']} PDF pages"] if s.get('pages') else []) + (['PDF created ' + '-'.join(made.groups())] if made else [])
            text.append(f"| {model(s['product_id'])} | {md(', '.join(facts))} | {s.get('retrieved_at', '')[:10]} | {md(s['final_url'])} |")
    missing = [s for s in sources if s['status'] in ('failed', 'duplicate')]
    if missing:
        text.extend(['', '## Sources without extracted text', '', '| Product | URL | Outcome |', '|---|---|---|'])
        text.extend(f"| {model(s['product_id'])} | {md(s['url'])} | "
                    f"{md(s.get('error') or 'duplicate of ' + s['duplicate_of'])} |" for s in missing)
    text.extend(['', f'Review coverage: {len(rows)}/{expected} product–capability cells. Unreviewed cells carry no result.', '',
                 f"Evidence quotes: {sum(bool(r.get('evidence')) for r in claims)} of {len(claims)} cells with a result other than unknown carry a quote that was checked against the cited passage.", '',
                 'See findings.csv for source URLs, hashes, interface, firmware and review provenance. No population percentages are computed.'])
    (dest / 'REPORT.md').write_text('\n'.join(text) + '\n', encoding='utf-8', newline='\n')
    print(f'Report written to {dest}: {len(rows)} of {expected} cells reviewed'
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
    dump(dest / 'candidates.json', hits)
    old = load(run / 'candidates.json')
    if hits != old:
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
            segs = [(x['location'], squash(x['text'])) for x in load(new / (n['id'] + '.segments.json'))]
            row['excerpts'] = []
            for q in mine:
                wanted = squash(q.get('quote') or q.get('excerpt', ''))
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
    r = sub.add_parser('report'); r.add_argument('--run', required=True); r.add_argument('--reviews', required=True); r.add_argument('--out', required=True); r.add_argument('--require-evidence', action='store_true')
    v = sub.add_parser('verify'); v.add_argument('--run', required=True); v.add_argument('--cache', default='cache')
    x = sub.add_parser('replay'); x.add_argument('--run', required=True); x.add_argument('--cache', default='cache'); x.add_argument('--out', required=True)
    k = sub.add_parser('recheck'); k.add_argument('--old', required=True); k.add_argument('--new', required=True); k.add_argument('--out')
    m = sub.add_parser('sitemap'); m.add_argument('--url', action='append', default=[]); m.add_argument('--host'); m.add_argument('--domain', action='append', default=[])
    m.add_argument('--match', default='.'); m.add_argument('--out', required=True); m.add_argument('--cache', default='cache'); m.add_argument('--max-files', type=int, default=20); m.add_argument('--delay', type=float, default=1.0)
    args = p.parse_args()
    try:
        if args.cmd == 'crawl': crawl(args.config, args.out, args.cache, args.resume)
        elif args.cmd == 'report': report(args.run, args.reviews, args.out, args.require_evidence)
        elif args.cmd == 'verify': verify(args.run, args.cache)
        elif args.cmd == 'replay': replay(args.run, args.cache, args.out)
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

#!/usr/bin/env python3
"""Bounded public-document survey. Keyword hits are leads, never support verdicts."""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
from collections import Counter, deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.robotparser import RobotFileParser

VERSION = '1.0.0'
UA = 'IEDSecuritySurvey/1.0 (public-document research; no device scanning)'
PATTERNS = {
    'dnp3_secure_authentication': r'DNP\s*3.{0,80}(?:secure\s+auth|\bSA\b)|secure\s+authentication',
    'tls': r'\bTLS\b|transport layer security|\bSSL\b',
    'ipsec': r'\bIPsec\b|IP security',
    'cip_security': r'CIP\s+Security',
    'authentication': r'\bauthentication\b|\bRADIUS\b|\bIEEE\s*802\.1X\b',
    'encryption': r'\bencrypt(?:ion|ed|s)?\b|\bDTLS\b',
    'ssh': r'\bSSH\b|secure shell',
}
CAPABILITIES = tuple(PATTERNS)
STATUSES = {'supported', 'conditional', 'explicitly_unsupported', 'unknown', 'conflicting'}


def digest(b):
    return hashlib.sha256(b).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def canonical(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise ValueError('Only public HTTPS URLs without credentials or custom ports are allowed')
    return urlunsplit(('https', p.netloc.lower(), p.path or '/', p.query, ''))


def allowed(url, domains):
    try:
        host = urlsplit(canonical(url)).hostname
        return any(host == d or host.endswith('.' + d) for d in domains)
    except ValueError:
        return False


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Fetcher:
    def __init__(self, config, cache):
        self.config, self.cache = config, Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.opener = build_opener(NoRedirect)
        self.robots, self.last, self.audit = {}, {}, []

    def raw(self, url):
        host = urlsplit(url).netloc
        delay = max(float(self.config.get('delay_seconds', 1)), self.robots.get(host, (None, 0))[1])
        time.sleep(max(0, delay - (time.monotonic() - self.last.get(host, 0))))
        self.last[host] = time.monotonic()
        req = Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
        try:
            response = self.opener.open(req, timeout=self.config.get('timeout_seconds', 25))
        except HTTPError as e:
            response = e
        with response:
            limit = self.config.get('max_bytes', 25000000)
            body = response.read(limit + 1)
            if len(body) > limit:
                raise ValueError('response exceeds byte limit')
            result = (response.code, dict(response.headers), body)
        self.audit.append({'at': now(), 'url': url, 'status': result[0], 'bytes': len(body)})
        return result

    def robot(self, url):
        p = urlsplit(url)
        if p.netloc not in self.robots:
            rurl = f'https://{p.netloc}/robots.txt'
            status, headers, body = self.raw(rurl)
            # Redirects/denials/errors are unresolved, not permission to crawl.
            if status == 404:
                lines = []
            elif status == 200:
                lines = body.decode('utf-8', 'replace').splitlines()
            else:
                raise ValueError(f'robots unresolved: HTTP {status}')
            rp = RobotFileParser(rurl)
            rp.parse(lines)
            gap = rp.crawl_delay(UA) or rp.crawl_delay('*') or 0
            rate = rp.request_rate(UA) or rp.request_rate('*')
            if rate:
                gap = max(gap, rate.seconds / rate.requests)
            self.robots[p.netloc] = (rp, gap)
            h = digest(body)
            (self.cache / h).write_bytes(body)
            self.audit[-1]['sha256'] = h
        if not self.robots[p.netloc][0].can_fetch(UA, url):
            raise ValueError('robots disallow')

    def fetch(self, url, domains):
        chain = []
        for _ in range(6):
            url = canonical(url)
            if not allowed(url, domains):
                raise ValueError('URL/redirect outside vendor allowlist')
            self.robot(url)
            status, headers, body = self.raw(url)
            chain.append({'url': url, 'status': status})
            if status in (301, 302, 303, 307, 308):
                location = next((v for k, v in headers.items() if k.lower() == 'location'), None)
                if not location:
                    raise ValueError('redirect without Location')
                url = urljoin(url, location)
                continue
            if status != 200:
                raise ValueError(f'HTTP {status}')
            h = digest(body)
            (self.cache / h).write_bytes(body)
            return {'final_url': url, 'sha256': h, 'bytes': len(body), 'headers': headers,
                    'redirect_chain': chain, 'retrieved_at': now()}, body
        raise ValueError('too many redirects')


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.links, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'footer'):
            self.skip += 1
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)
        if tag in ('p', 'div', 'li', 'br', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'footer') and self.skip:
            self.skip -= 1
        if tag in ('p', 'div', 'li', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def extract(body, headers):
    if body.startswith(b'%PDF'):
        from pypdf import PdfReader
        pdf = PdfReader(io.BytesIO(body))
        return [{'location': f'pdf-page:{i + 1}', 'text': page.extract_text() or ''}
                for i, page in enumerate(pdf.pages)], []
    ct = next((v for k, v in headers.items() if k.lower() == 'content-type'), '')
    if 'html' not in ct.lower():
        raise ValueError('unsupported content type: ' + ct)
    charset = re.search(r'charset=([\w-]+)', ct)
    html = TextHTML()
    html.feed(body.decode(charset[1] if charset else 'utf-8', 'replace'))
    lines = [' '.join(x.split()) for x in ''.join(html.parts).splitlines() if x.strip()]
    return [{'location': f'html-block:{i + 1}', 'text': s} for i, s in enumerate(lines)], html.links


def candidates(source, segments):
    hits = []
    for segment in segments:
        for feature, pattern in PATTERNS.items():
            match = re.search(pattern, segment['text'], re.I | re.S)
            if not match:
                continue
            cid = digest((source['id'] + segment['location'] + feature).encode())[:20]
            hits.append({'id': cid, 'source_id': source['id'], 'product_id': source['product_id'],
                         'feature': feature, 'location': segment['location'],
                         'context': segment['text'][max(0, match.start()-220):match.end()+350],
                         'status': 'unreviewed'})
    return hits


def crawl(config_path, out, cache):
    config_bytes = Path(config_path).read_bytes()
    cfg = json.loads(config_bytes)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    dump(out / 'config.json', cfg)
    f = Fetcher(cfg, cache)
    sources, hits = [], []
    # Product provenance remains separate even when a family document is shared.
    for product in cfg['products']:
        queue = deque((url, 0) for url in product['seeds'])
        seen = set()
        while queue and len(seen) < cfg.get('max_pages_per_product', 3):
            url, depth = queue.popleft()
            if url in seen:
                continue
            seen.add(url)
            rec = {'id': digest((product['id'] + url).encode())[:20],
                   'product_id': product['id'], 'url': url, 'depth': depth, 'started_at': now()}
            try:
                meta, body = f.fetch(url, product['domains'])
                rec.update(meta)
                segs, links = extract(body, meta['headers'])
                if not any(s['text'].strip() for s in segs):
                    raise ValueError('no extractable text; OCR/manual review required')
                rec['status'] = 'extracted'
                dump(out / (rec['id'] + '.segments.json'), segs)
                hits.extend(candidates(rec, segs))
                if depth < cfg.get('max_depth', 0):
                    for link in links:
                        full = urljoin(meta['final_url'], link)
                        if allowed(full, product['domains']) and re.search(cfg.get('follow_pattern', r'manual|security|datasheet|\.pdf'), full, re.I):
                            queue.append((canonical(full), depth + 1))
            except Exception as e:
                rec.update(status='failed', error=f'{type(e).__name__}: {e}')
            sources.append(rec)
            # Checkpoints survive interrupted runs; incomplete runs are never called complete.
            dump(out / 'sources.json', sources)
            dump(out / 'candidates.json', hits)
            dump(out / 'requests.json', f.audit)
            print(product['id'], rec['status'], url, flush=True)
    dump(out / 'manifest.json', {'tool_version': VERSION, 'finished_at': now(),
        'config_sha256': digest(config_bytes), 'python': sys.version,
        'script_sha256': digest(Path(__file__).read_bytes()),
        'complete': True, 'source_count': len(sources), 'candidate_count': len(hits),
        'sampling': cfg['sampling']})
    template = [{'product_id': p['id'], 'feature': feature, 'status': 'unknown',
                 'source_ids': [], 'source_hashes': {}, 'location': '', 'protocol': '',
                 'interface': '', 'firmware': 'not established', 'implementation': 'not established',
                 'rationale': '', 'reviewer': '', 'reviewed_at': ''}
                for p in cfg['products'] for feature in CAPABILITIES]
    dump(out / 'review_template.json', template)


def validate_reviews(rows, sources, products):
    byid = {s['id']: s for s in sources}
    seen = set()
    for r in rows:
        key = r['product_id'], r['feature']
        if key in seen or key[0] not in products or key[1] not in CAPABILITIES:
            raise ValueError(f'duplicate/unknown review key: {key}')
        seen.add(key)
        if r['status'] not in STATUSES:
            raise ValueError('invalid status')
        if not all(r.get(k) for k in ('reviewer', 'reviewed_at', 'rationale')):
            raise ValueError('review identity/date/rationale required, including unknowns')
        if r['status'] != 'unknown' and not r['source_ids']:
            raise ValueError('claim requires source evidence')
        if r['status'] != 'unknown' and not all(r.get(k) for k in ('location','protocol','interface','firmware','implementation')):
            raise ValueError('claim scope is incomplete')
        for sid in r['source_ids']:
            s = byid.get(sid)
            if not s or s['status'] != 'extracted' or s['product_id'] != r['product_id']:
                raise ValueError('missing/failed/wrong-product source')
            if r['source_hashes'].get(sid) != s['sha256']:
                raise ValueError('review/source hash mismatch')


def report(run, review_path, dest):
    run, dest = Path(run), Path(dest)
    cfg = json.loads((run / 'config.json').read_text())
    sources = json.loads((run / 'sources.json').read_text())
    rows = json.loads(Path(review_path).read_text())
    products = {p['id']: p for p in cfg['products']}
    validate_reviews(rows, sources, products)
    dest.mkdir(parents=True, exist_ok=True)
    dump(dest / 'findings.json', rows)
    dump(dest / 'sources.json', sources)
    columns = ['product_id','vendor','model','category','feature','status','protocol','interface',
               'firmware','implementation','location','rationale','reviewer','reviewed_at','source_urls','source_hashes']
    byid = {s['id']: s for s in sources}
    with (dest / 'findings.csv').open('w', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=columns)
        w.writeheader()
        for r in rows:
            p = products[r['product_id']]
            item = {k: r.get(k, '') for k in columns}
            item.update({k: p[k] for k in ('vendor','model','category')})
            item['source_urls'] = ' | '.join(byid[s]['final_url'] for s in r['source_ids'])
            item['source_hashes'] = json.dumps(r['source_hashes'], sort_keys=True)
            w.writerow(item)
    totals = Counter(s['status'] for s in sources)
    text = ['# IED security documentation pilot', '',
            f"Sampling: {cfg['sampling']}", '',
            f"Products/families in seed inventory: {len(products)}. Sources attempted: {len(sources)}; extracted: {totals['extracted']}; failed: {totals['failed']}.", '',
            'This measures documented capabilities, not enabled settings, installed-base coverage or plaintext prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. AI-reviewed pilot findings require author verification before publication.', '',
            '| Product | Capability | Review result | Scope |', '|---|---|---|---|']
    for r in rows:
        text.append('| ' + ' | '.join(str(x).replace('|','/').replace('\n',' ') for x in
                    [products[r['product_id']]['model'], r['feature'], r['status'], r['rationale']]) + ' |')
    expected = len(products) * len(CAPABILITIES)
    text.extend(['', f'Review coverage: {len(rows)}/{expected} product–capability cells. Unreviewed cells carry no result.', '',
                 'See findings.csv for source URLs, hashes, interface, firmware and review provenance. No population percentages are computed.'])
    (dest / 'REPORT.md').write_text('\n'.join(text)+'\n')


def verify(run, cache):
    records = json.loads((Path(run) / 'sources.json').read_text())
    for r in records:
        if 'sha256' in r:
            p = Path(cache) / r['sha256']
            if not p.exists() or digest(p.read_bytes()) != r['sha256']:
                raise ValueError('missing or changed cached source: ' + r['id'])
    print('All recorded source bytes verified')


def replay(run, cache, dest):
    """Offline re-extraction against exact retained bytes, with hash verification first."""
    verify(run, cache)
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=False)
    hits = []
    for s in json.loads((Path(run) / 'sources.json').read_text()):
        if s['status'] == 'extracted':
            segs, _ = extract((Path(cache) / s['sha256']).read_bytes(), s['headers'])
            dump(dest / (s['id'] + '.segments.json'), segs)
            hits.extend(candidates(s, segs))
    dump(dest / 'candidates.json', hits)
    old = json.loads((Path(run) / 'candidates.json').read_text())
    if hits != old:
        raise ValueError('extraction differs from recorded run; investigate tool/version changes')
    print('Offline extraction and candidates match recorded run exactly')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('crawl'); c.add_argument('--config', required=True); c.add_argument('--out', required=True); c.add_argument('--cache', default='cache')
    r = sub.add_parser('report'); r.add_argument('--run', required=True); r.add_argument('--reviews', required=True); r.add_argument('--out', required=True)
    v = sub.add_parser('verify'); v.add_argument('--run', required=True); v.add_argument('--cache', default='cache')
    x = sub.add_parser('replay'); x.add_argument('--run', required=True); x.add_argument('--cache', default='cache'); x.add_argument('--out', required=True)
    args = p.parse_args()
    if args.cmd == 'crawl': crawl(args.config, args.out, args.cache)
    elif args.cmd == 'report': report(args.run, args.reviews, args.out)
    elif args.cmd == 'verify': verify(args.run, args.cache)
    else: replay(args.run, args.cache, args.out)


if __name__ == '__main__':
    main()

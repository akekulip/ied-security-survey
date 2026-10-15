"""The bounded crawl of one config into one run directory."""

import heapq
import json
import re
import sys
from collections import Counter
from importlib.metadata import version
from pathlib import Path
from urllib.parse import urljoin

from .vocabulary import CAPABILITIES, EXTRACTION, FORMER_LIFECYCLES, LIFECYCLES, VERSION, legacy_states
from .store import SCRIPT_SHA256, digest, dump, load, now
from .text import norm, text_digest
from .fetch import Fetcher, LOGIN, allowed, canonical
from .extract import PDFReuse, parse, suggest_doc_type
from .leads import alias_pattern, candidates, profile_items, save_leads


KNOWN_KEYS = {'sampling', 'definitions', 'title', 'max_depth', 'max_pages_per_product', 'delay_seconds', 'timeout_seconds', 'max_bytes',
              'follow_pattern', 'robots_follow_redirects', 'retries', 'products',
              'seed', 'per_stratum', 'census', 'inventory', 'frame'}


# Which link to follow first when the page budget is short: the documents that state capabilities most directly.
LINK_WEIGHTS = [(re.compile(p, re.I), w) for p, w in (
    (r'device[\s_-]*profile', 4), (r'conformance|\bpics\b|\bpixit\b', 3), (r'secur|cyber|hardening', 2),
    (r'manual|instruction|user[\s_-]*guide', 2), (r'communicat|protocol|dnp|61850|ethernet|network', 1),
    (r'data[\s_-]?sheet|brochure|catalog|flyer|guide', 1))]


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
    legacy_states(cfg.get('definitions'))
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


def approved_additions(entries, cfg):
    """The approved list of new requests, as {product id: [address, ...]}. Each entry names its product and why it was
    chosen; an address outside the product's allowlisted domains or for a product the run does not cover is refused."""
    products, approved = {p['id']: p for p in cfg['products']}, {}
    for e in entries:
        pid, url = e.get('product_id'), e.get('url', '')
        if pid not in products:
            raise ValueError(f'approved URL for a product this run does not cover: {pid!r}')
        if not str(e.get('reason', '')).strip():
            raise ValueError(f'approved URL without a reason: {url}')
        if not allowed(url, products[pid]['domains']):
            raise ValueError(f'{pid}: approved URL is not an allowlisted public HTTPS URL: {url}')
        approved.setdefault(pid, []).append(canonical(url))
    return approved


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


def finish(out, cfg, config_sha256, sources, hits, warnings, **extra):
    """Manifest and the three templates a reviewer fills in. Only a finished run has a manifest."""
    manifest = {'tool_version': VERSION, 'extraction_version': EXTRACTION, 'finished_at': now(),
        'config_sha256': config_sha256, 'python': sys.version,
        'script_sha256': SCRIPT_SHA256,
        'complete': True, 'source_count': len(sources),
        'candidate_count': sum(h['lead_type'] != 'statement' for h in hits),
        'lead_counts': dict(Counter(h['lead_type'] for h in hits)),
        'source_status': dict(Counter(s['status'] for s in sources)),
        'config_warnings': warnings, 'sampling': cfg['sampling'], **extra}
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
           'release_date': '', 'release_evidence': [], 'dnp3': '', 'dnp3_note': '', 'note': '', 'noted_by': '', 'noted_at': ''}
          for p in cfg['products']])
    # What a document says about its own number, revision and date is for a person to read off, not for a regex.
    dump(out / 'source_notes_template.json',
         [{'source_id': s['id'], 'product_id': s['product_id'], 'url': s['final_url'], 'title': s.get('title', ''),
           'document_hints': s.get('document_hints', []), 'doc_type_suggested': s.get('doc_type_suggested', ''),
           'doc_type': '', 'coverage': '', 'document_id': '', 'revision': '', 'document_date': '', 'note': ''}
          for s in sources if s['status'] == 'extracted'])
    # The completion marker comes last. A failed template write remains resumable.
    dump(out / 'manifest.json', manifest)


def recovered_leads(run, sources, cfg, cache):
    """Sources and segments are authoritative; a crash can leave the derived lead files one checkpoint behind."""
    aliases = {p['id']: p.get('aliases', []) for p in cfg['products']}
    hits = []
    for source in sources:
        if source['status'] != 'extracted':
            continue
        body = (cache / source['sha256']).read_bytes()
        if digest(body) != source['sha256']:
            raise ValueError('cached source hash mismatch on resume: ' + source['id'])
        segments = load(run / (source['id'] + '.segments.json'))
        if text_digest(segments) != source.get('text_sha256'):
            raise ValueError('saved source text hash mismatch on resume: ' + source['id'])
        hits.extend(candidates(source, segments, aliases[source['product_id']]))
    return hits


def crawl_contract(config_bytes, approval, runs):
    """Pin the inputs and extraction environment before a run makes its first request."""
    return {'schema_version': 'iedsurvey.crawl-contract.v1',
            'config_sha256': digest(config_bytes), 'approved_urls': approval.get('approved_urls'),
            'extraction_version': EXTRACTION, 'script_sha256': SCRIPT_SHA256, 'python': sys.version,
            'dependencies': {name: version(name) for name in ('pypdf', 'cryptography', 'protego')},
            'reuse': [{'path': str(run), 'sources_sha256': digest((Path(run) / 'sources.json').read_bytes())}
                      for run in runs]}


class Crawler:
    """One run in progress: what it has recorded, what earlier runs already hold, and where it checkpoints."""

    def __init__(self, cfg, out, cache, sources, hits, audit, earlier, approved=None):
        self.cfg, self.out, self.cache, self.sources, self.hits = cfg, out, cache, sources, hits
        # With an approved list, only its addresses may be requested; everything else comes from an earlier run or waits.
        self.approved = approved
        self.fetcher = Fetcher(cfg, cache)
        self.pdfs = PDFReuse(out)
        self.fetcher.audit = audit
        self.prior = {(s['product_id'], s['url']): s for s in sources}
        self.byid = {s['id']: s for s in sources}
        # Bytes an earlier run already fetched are not requested again; the record says where they came from. That holds
        # for a document that arrived and could not be read, too: asking again would bring the same bytes.
        self.known = {}
        for run in earlier:
            for s in load(Path(run) / 'sources.json'):
                held = s.get('sha256') and s['status'] in ('extracted', 'duplicate', 'failed') and (cache / s['sha256']).exists()
                if held or s['status'] == 'login_required':
                    # A product's own earlier record comes first. Another product's fetch of the same address is the
                    # next best: for a page that changes with every request it holds different bytes.
                    for key in ((s['product_id'], s['url']), s['url']):
                        self.known.setdefault(key, dict(s, held_by=str(run)))

    def checkpoint(self):
        dump(self.out / 'sources.json', self.sources)
        save_leads(self.out, self.hits)
        dump(self.out / 'requests.json', self.fetcher.audit)

    def record(self, rec):
        self.sources.append(rec)
        self.byid[rec['id']] = rec

    def obtain(self, rec, product, alias, shas):
        """Fetches one address, or takes the bytes an earlier run holds, and extracts the text. Returns the page's links."""
        held = self.known.get((product['id'], rec['url'])) or self.known.get(rec['url'])
        if held and held['status'] == 'login_required':
            # The earlier run was told this document needs a sign-in. It is not asked for again.
            rec.update(status='login_required', error=held['error'], reused_from=held['held_by'])
            return []
        if not held and self.approved is not None and rec['url'] not in self.approved.get(product['id'], ()):
            rec.update(status='not_approved', error='not held by an earlier run and not in the approved list; not requested')
            return []
        try:
            if held:
                meta = {k: held[k] for k in ('final_url', 'sha256', 'bytes', 'headers', 'robots_basis',
                                             'redirect_chain', 'retrieved_at') if k in held}
                meta['reused_from'] = held['held_by']
                body = (self.cache / meta['sha256']).read_bytes()
            else:
                meta, body = self.fetcher.fetch(rec['url'], product['domains'])
            if digest(body) != meta['sha256']:
                raise ValueError('cached source hash mismatch: ' + meta['sha256'])
            rec.update(meta)
            if meta['sha256'] in shas:
                rec.update(status='duplicate', duplicate_of=shas[meta['sha256']])
                return []
            segs, links, facts = self.pdfs.parse(rec, body)
            if not any(s['text'].strip() for s in segs):
                raise ValueError('no extractable text; OCR/manual review required')
            describe(rec, segs, facts, self.out, alias)
            rec['status'] = 'extracted'
            self.hits.extend(candidates(rec, segs, product.get('aliases', [])))
            self.pdfs.remember(rec, facts)
            # Reuse a fresh download for another product in this same run, while keeping its own source record/leads.
            if (self.cache / meta['sha256']).is_file():
                held = dict(rec, held_by=str(self.out))
                for key in ((product['id'], rec['url']), rec['url']):
                    self.known.setdefault(key, held)
            return links
        except Exception as e:
            gated = isinstance(e, ValueError) and str(e).startswith('login required')
            rec.update(status='login_required' if gated else 'failed', error=f'{type(e).__name__}: {e}')
            return []

    def matching(self, rec, links, product, follow, seen, fresh):
        """The links of one page worth following, in page order. A link to a sign-in page is recorded, never followed."""
        matched, gates, wanted = set(), {}, []
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
                    gates[full] = {'id': digest((product['id'] + full).encode())[:20], 'product_id': product['id'],
                                   'url': full, 'depth': rec['depth'] + 1, 'via': rec['id'], 'started_at': now(),
                                   'status': 'login_required', 'link_text': text, 'link_count': 1,
                                   'error': 'link leads to a sign-in page; not requested'}
                    if fresh and (product['id'], full) not in self.prior:
                        self.record(gates[full])
                else:
                    wanted.append((full, text))
        if fresh:
            rec['links_matched'] = len(matched)
        return wanted

    def visit(self, product):
        """Seeds first, then matched links by depth and by how directly they state capabilities. Yields each new source."""
        cfg, alias = self.cfg, alias_pattern(product.get('aliases', []))
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
            rec, links = self.prior.get((product['id'], url)), []
            fresh = rec is None
            if fresh:
                rec = {'id': digest((product['id'] + url).encode())[:20],
                       'product_id': product['id'], 'url': url, 'depth': depth, 'started_at': now()}
                if via:
                    rec['via'] = via
                # Seeds are always attempted; the budget only limits followed links, and those are recorded too.
                if depth and attempted >= budget:
                    rec.update(status='skipped', error='page budget reached before this link')
                    self.byid[via]['links_skipped'] = self.byid[via].get('links_skipped', 0) + 1
                else:
                    links = self.obtain(rec, product, alias, shas)
                self.record(rec)
            elif rec['status'] == 'extracted' and depth < depth_limit:
                # Resumed run: rebuild this page's links from the retained bytes instead of the network.
                links = parse((self.cache / rec['sha256']).read_bytes(), rec['headers'])[1]
            if rec['status'] not in ('skipped', 'login_required'):
                attempted += 1
            if rec['status'] == 'extracted':
                shas.setdefault(rec['sha256'], rec['id'])
                if fresh:
                    rec['links_found'] = len(links)
                if depth < depth_limit:
                    for full, text in self.matching(rec, links, product, follow, seen, fresh):
                        heapq.heappush(queue, (depth + 1, -link_score(full, text, alias), order, full, rec['id']))
                        order += 1
            if fresh:
                yield rec
        # Approved additional documents come after the product's own pages and outside its page budget, so they never
        # displace a page an earlier run followed. Their links are not followed.
        for url in (self.approved or {}).get(product['id'], []):
            if url in seen or (product['id'], url) in self.prior:
                continue
            seen.add(url)
            rec = {'id': digest((product['id'] + url).encode())[:20], 'product_id': product['id'], 'url': url,
                   'depth': 0, 'started_at': now(), 'approved_addition': True}
            self.obtain(rec, product, alias, shas)
            self.record(rec)
            if rec['status'] == 'extracted':
                shas.setdefault(rec['sha256'], rec['id'])
            yield rec


def crawl(config_path, out, cache, resume=False, reuse=None, only=None, approved_urls=None):
    config_bytes = Path(config_path).read_bytes()
    cfg = json.loads(config_bytes)
    if only:
        # The run's config lists what the run covers; the manifest keeps the hash of the file it was cut from.
        cfg['products'] = [p for p in cfg.get('products', []) if re.search(only, f"{p.get('id')} {p.get('vendor', '')}", re.I)]
        if not cfg['products']:
            raise ValueError('--only matches no product')
    warnings = validate_config(cfg)
    approved, approval = None, {}
    if approved_urls:
        approved_bytes = Path(approved_urls).read_bytes()
        approved = approved_additions(json.loads(approved_bytes), cfg)
        approval = {'approved_urls': {'path': str(approved_urls), 'sha256': digest(approved_bytes),
                                      'count': sum(map(len, approved.values()))}}
    for w in warnings:
        print('config warning:', w, file=sys.stderr)
    import pypdf  # noqa: F401  Fail before the first request, not once per PDF.
    out, cache = Path(out), Path(cache)
    runs = [reuse] if isinstance(reuse, (str, Path)) else list(reuse or [])
    contract = crawl_contract(config_bytes, approval, runs)
    sources, hits, audit = [], [], []
    if resume:
        if (out / 'manifest.json').exists():
            raise ValueError('run is already complete; nothing to resume')
        if load(out / 'config.json') != cfg:
            raise ValueError('resume needs the config the run was started with')
        sources, audit = (load(out / n) if (out / n).exists() else [] for n in ('sources.json', 'requests.json'))
        saved_contract = out / 'crawl_contract.json'
        if not saved_contract.exists() or load(saved_contract) != contract:
            raise ValueError('resume contract changed or missing; start a new run instead of mixing inputs or code')
        hits = recovered_leads(out, sources, cfg, cache)
    else:
        out.mkdir(parents=True, exist_ok=False)
        dump(out / 'config.json', cfg)
        dump(out / 'crawl_contract.json', contract)
    crawler, products = Crawler(cfg, out, cache, sources, hits, audit, runs, approved), cfg['products']
    # Product provenance remains separate even when a family document is shared.
    for number, product in enumerate(products, 1):
        for rec in crawler.visit(product):
            # Checkpoints survive interrupted runs; incomplete runs are never called complete.
            crawler.checkpoint()
            print(f'[{number}/{len(products)}]', product['id'], rec['status'], rec['url'], flush=True)
    # Written once more so a run without any seeds still has all its files.
    crawler.checkpoint()
    finish(out, cfg, digest(config_bytes), sources, hits, warnings, **approval,
           **({'resumed': True, 'request_log_may_be_incomplete': True} if resume else {}),
           **({'only': only} if only else {}),
           **({'reused_from': str(runs[0]) if len(runs) == 1 else [str(x) for x in runs]} if runs else {}))

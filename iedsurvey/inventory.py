"""The catalogue inventory: every device a vendor lists, placed by rule, with its lifecycle evidence."""

import csv
import json
import re
import zlib
from collections import Counter
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from .vocabulary import CATEGORIES, LIFECYCLES, VERSION, legacy_states
from .store import digest, dump, load, now
from .text import STOP, passage, squash
from .fetch import Fetcher, canonical


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
    legacy_states(spec.get('definitions'))
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
    earlier = load(Path(source) / 'inventory.json') if source else {}
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
            listing[key] = {'files': files, 'not_fetched': left, 'items': items, 'listed_at': now()}
        entries += classify(key, v, listing[key]['items'], listing[key]['files'])
    dest.mkdir(parents=True)
    dump(dest / 'catalogue.json', listing)
    # Re-applied rules keep the log of the requests that produced the listing they were applied to.
    dump(dest / 'requests.json', (load(Path(source) / 'requests.json') if source else []) + f.audit)
    made = now()
    # The day the catalogues were listed is the inventory date. Re-applying rules to a saved listing does not move it.
    listed = max(v.get('listed_at') or earlier.get('listed_at') or earlier.get('created_at') or made for v in listing.values())
    write_inventory(dest, {'tool_version': VERSION, 'created_at': made, 'listed_at': listed, 'vendors_sha256': digest(Path(vendors_path).read_bytes()),
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

"""From the inventory to a crawl config: the census, or a seeded stratified sample."""

import random
from collections import Counter
from pathlib import Path

from .store import digest, dump, load


def sample(inventory_path, dest, per_stratum=None, seed=0, census=False):
    """Writes a crawl config from the inventory: every catalogue entry, or a seeded draw per vendor, category and lifecycle."""
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(dest)
    inv = load(inventory_path)
    listed = inv.get('listed_at') or inv['created_at']
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
                'sampling': how + f" Inventory of {listed[:10]}; categories and lifecycle come from the vendors' own catalogues and pages.",
                # What "legacy" and each lifecycle group mean, fixed in the config before the crawl and so before any count.
                **({'definitions': inv['spec']['definitions']} if inv['spec'].get('definitions') else {}),
                'seed': seed, 'per_stratum': per_stratum, 'census': census,
                'inventory': {'path': str(inventory_path), 'sha256': digest(Path(inventory_path).read_bytes()), 'created_at': inv['created_at'],
                              'listed_at': listed},
                'frame': [{'vendor': v, 'category': c, 'lifecycle': life, 'in_catalogue': len(members), 'selected': picked[v, c, life]}
                          for (v, c, life), members in sorted(strata.items())],
                'max_depth': 0, 'max_pages_per_product': 4, 'delay_seconds': 1.2, 'timeout_seconds': 60, 'max_bytes': 60000000,
                'robots_follow_redirects': inv['spec'].get('robots_follow_redirects', False), 'products': products})
    print(f'{len(products)} products written to {dest}')

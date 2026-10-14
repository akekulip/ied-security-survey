"""Vendor catalogues as listed: sitemap files, and the SEL product list where the sitemap is not enough."""

import json
import re
import zlib
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from .vocabulary import VERSION
from .store import dump, now
from .fetch import Fetcher


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

"""Bounded public-document survey. Keyword hits are leads, never support verdicts."""

import argparse
import sys

from .crawl import crawl
from .runs import rebuild, recheck, replay, verify
from .review import rebind
from .report import report
from .inventory import enrich, inventory, sitemap
from .sampling import sample
from .worksheet import worksheet


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
    n = sub.add_parser('rebind'); n.add_argument('--reviews', required=True); n.add_argument('--old', required=True); n.add_argument('--run', required=True); n.add_argument('--out', required=True)
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
        elif args.cmd == 'rebind': rebind(args.reviews, args.old, args.run, args.out)
        elif not args.url and not args.host: p.error('sitemap needs --url or --host')
        else: sitemap(args.url, args.host, args.domain, args.match, args.out, args.cache, args.max_files, args.delay)
    # Refusals the tool raises on purpose read as one line, not as a crash.
    except FileExistsError as e:
        sys.exit(f'error: already exists, refusing to overwrite: {e.filename or e}')
    except FileNotFoundError as e:
        sys.exit(f'error: not found: {e.filename or e}')
    except ValueError as e:
        sys.exit(f'error: {e}')

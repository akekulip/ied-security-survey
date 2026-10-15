"""Survey what IED vendors' public documents say about security. Keyword hits are leads, never findings."""

import argparse
import sys

from .crawl import crawl
from .runs import rebuild, recheck, replay, verify
from .review import rebind
from .report import report
from .paper import paper
from .catalogue import sitemap
from .inventory import enrich, inventory
from .sampling import sample
from .worksheet import worksheet


REQUIRED = {'required': True}
CACHE = {'default': 'cache', 'help': 'folder of fetched files, shared between runs (default: cache)'}
RUN = REQUIRED | {'help': 'run folder'}

# Each command calls its function with the values of its options, in the order they are listed here.
COMMANDS = {
    'crawl': (crawl, 'fetch the pages and documents of a config into a new run folder', [
        ('--config', REQUIRED | {'help': 'crawl config: configs/pilot.json, or one written by sample'}),
        ('--out', REQUIRED | {'help': 'new run folder'}),
        ('--cache', CACHE),
        ('--resume', {'action': 'store_true', 'help': 'continue an interrupted run in --out'}),
        ('--reuse', {'action': 'append', 'help': 'earlier run whose fetched files are used instead of new requests; may '
                                                 'be repeated'}),
        ('--only', {'help': 'only the products whose id or vendor matches this pattern'}),
        ('--approved-urls', {'help': 'JSON list of {product_id, url, reason}: the only addresses this run may request; '
                                     'everything else comes from --reuse or is recorded as not_approved. Each listed '
                                     'address is also attempted for its product, outside the page budget'})]),
    'inventory': (inventory, 'list every catalogue device of the vendors in a rules file', [
        ('--vendors', REQUIRED | {'help': 'rules file, e.g. configs/vendors.json'}),
        ('--out', REQUIRED | {'help': 'new inventory folder'}),
        ('--cache', CACHE),
        ('--from', {'dest': 'source', 'help': 'earlier inventory folder whose saved listing is used instead of asking '
                                              'the vendors again'})]),
    'enrich': (enrich, 'classify inventory entries further from their product pages, as read in a census run', [
        ('--inventory', REQUIRED | {'help': 'inventory.json to start from'}),
        ('--run', REQUIRED | {'help': 'census run holding the product pages'}),
        ('--out', REQUIRED | {'help': 'new inventory folder'}),
        ('--vendors', {'help': 'rules file to apply instead of the one saved in the inventory'})]),
    'sample': (sample, 'write a crawl config from an inventory: a seeded sample, or a census', [
        ('--inventory', REQUIRED | {'help': 'inventory.json'}),
        ('--out', REQUIRED | {'help': 'new crawl config file'}),
        ('--per-stratum', {'type': int, 'help': 'devices per vendor, category and lifecycle state'}),
        ('--seed', {'type': int, 'default': 0, 'help': 'random seed (default: 0)'}),
        ('--census', {'action': 'store_true', 'help': 'one product page per catalogue entry instead of a sample'})]),
    'worksheet': (worksheet, 'lay out, per device and capability, where the documents mention it', [
        ('--run', RUN),
        ('--out', REQUIRED | {'help': 'new worksheet folder'})]),
    'report': (report, 'build the report of a run from a review', [
        ('--run', RUN),
        ('--reviews', REQUIRED | {'help': "review file; start from the run's review_template.json"}),
        ('--out', REQUIRED | {'help': 'report folder; a report already there is replaced'}),
        ('--require-evidence', {'action': 'store_true', 'help': 'every result must quote its source'}),
        ('--source-notes', {'help': 'source notes file'}),
        ('--device-notes', {'help': 'device notes file'}),
        ('--require-confirmed', {'action': 'store_true', 'help': 'refuse publication output while any cell is draft or unreviewed'})]),
    'paper': (paper, "write the paper's DNP3 evidence: summary, table, LaTeX appendix and paragraph, with a receipt", [
        ('--run', RUN),
        ('--reviews', REQUIRED | {'help': 'review file'}),
        ('--out', REQUIRED | {'help': 'new folder'}),
        ('--source-notes', {'help': 'source notes file'}),
        ('--device-notes', {'help': 'device notes file'}),
        ('--require-confirmed', {'action': 'store_true', 'help': 'refuse unless every cell is confirmed by a person; '
                                                                  'without it every output is marked as a draft'})]),
    'verify': (verify, 'check that the cached files of a run still match their recorded hashes', [
        ('--run', RUN),
        ('--cache', CACHE)]),
    'replay': (replay, 'extract a run again from its cached files, without the network, and compare', [
        ('--run', RUN),
        ('--cache', CACHE),
        ('--out', REQUIRED | {'help': 'new folder for the replayed run'})]),
    'rebuild': (rebuild, 'apply the current extraction rules to a finished run, without the network', [
        ('--run', RUN),
        ('--cache', CACHE),
        ('--out', REQUIRED | {'help': 'new run folder'})]),
    'recheck': (recheck, 'compare an earlier run or report with a newer run of the same products', [
        ('--old', REQUIRED | {'help': 'earlier run or report folder'}),
        ('--new', REQUIRED | {'help': 'newer run folder'}),
        ('--out', {'help': 'new result file (JSON)'})]),
    'rebind': (rebind, 'carry a review over to a refetch whose extracted text is unchanged', [
        ('--reviews', REQUIRED | {'help': 'review file'}),
        ('--old', REQUIRED | {'help': 'run or report folder the review was written against'}),
        ('--run', REQUIRED | {'help': 'new run folder'}),
        ('--out', REQUIRED | {'help': 'new review file'})]),
    'sitemap': (sitemap, "list one vendor's sitemap, filtered, into a file", [
        ('--url', {'action': 'append', 'default': [], 'help': 'sitemap URL; may be repeated'}),
        ('--host', {'help': "read the sitemap locations from this host's robots.txt"}),
        ('--domain', {'action': 'append', 'default': [], 'help': 'allowed domain; may be repeated (default: the host)'}),
        ('--match', {'default': '.', 'help': 'regular expression the page URLs must match'}),
        ('--out', REQUIRED | {'help': 'new output file'}),
        ('--cache', CACHE),
        ('--max-files', {'type': int, 'default': 20, 'help': 'most sitemap files to read (default: 20)'}),
        ('--delay', {'type': float, 'default': 1.0, 'help': 'seconds between requests (default: 1.0)'})]),
}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True, metavar='command')
    for name, (_, text, options) in COMMANDS.items():
        cmd = sub.add_parser(name, help=text, description=text)
        for flag, settings in options:
            cmd.add_argument(flag, **settings)
    return p


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')  # Document text may not fit the console code page.
    p = parser()
    args = p.parse_args(argv)
    if args.cmd == 'sitemap' and not (args.url or args.host):
        p.error('sitemap needs --url or --host')
    function, _, options = COMMANDS[args.cmd]
    values = [getattr(args, settings.get('dest') or flag[2:].replace('-', '_')) for flag, settings in options]
    try:
        function(*values)
    # Refusals the tool raises on purpose read as one line, not as a crash.
    except FileExistsError as e:
        sys.exit(f'error: already exists, refusing to overwrite: {e.filename or e}')
    except FileNotFoundError as e:
        sys.exit(f'error: not found: {e.filename or e}')
    except ValueError as e:
        sys.exit(f'error: {e}')

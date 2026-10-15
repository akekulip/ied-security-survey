"""What can be done with a finished run without the network: verify, replay, rebuild, recheck."""

from itertools import zip_longest
from pathlib import Path

from .vocabulary import EXTRACTION, VERSION
from .store import digest, dump, load, now
from .text import loose, text_digest
from .extract import PDFReuse
from .leads import alias_pattern, candidates, save_leads
from .crawl import describe, finish


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
    pdfs = PDFReuse(dest)
    for s in load(run / 'sources.json'):
        if s['status'] == 'extracted':
            segs, _, facts = pdfs.parse(s, (cache / s['sha256']).read_bytes())
            describe(s, segs, facts, dest, alias_pattern(aliases.get(s['product_id'])))
            pdfs.remember(s, facts)
            hits.extend(candidates(s, segs, aliases.get(s['product_id'], [])))
        sources.append(s)
    dump(dest / 'sources.json', sources)
    save_leads(dest, hits)
    dump(dest / 'requests.json', load(run / 'requests.json') if (run / 'requests.json').exists() else [])
    finish(dest, cfg, made.get('config_sha256'), sources, hits, made.get('config_warnings', []),
           rebuilt_from={'run': str(run), 'tool_version': made.get('tool_version'), 'finished_at': made.get('finished_at')})
    print(f'Rebuilt {sum(s["status"] == "extracted" for s in sources)} sources into {dest} with tool version {VERSION}')


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
    hits, problems = [], []
    pdfs = PDFReuse(dest)
    for s in load(run / 'sources.json'):
        if s['status'] == 'extracted':
            segs, _, facts = pdfs.parse(s, (Path(cache) / s['sha256']).read_bytes())
            dump(dest / (s['id'] + '.segments.json'), segs)
            pdfs.remember(s, facts)
            saved = run / (s['id'] + '.segments.json')
            problems += segment_problems(s['id'], s.get('text_sha256'), load(saved) if saved.exists() else None,
                                         load(dest / (s['id'] + '.segments.json')))
            hits.extend(candidates(s, segs, aliases.get(s['product_id'], [])))
    if problems:
        raise ValueError(f'extracted text differs from recorded run in {len(problems)} sources: ' + '; '.join(problems[:10]))
    save_leads(dest, hits)
    for name in ('candidates.json', 'statement_leads.json'):
        if load(dest / name) != (load(run / name) if (run / name).exists() else []):
            raise ValueError('extraction differs from recorded run; investigate tool/version changes')
    print('Offline extraction, saved segments, text digests and candidates match recorded run exactly')


def segment_problems(sid, recorded, saved, fresh):
    """Where a source's saved and freshly extracted segments disagree with each other or with the recorded digest."""
    if saved is None:
        return [f'{sid}: saved segments missing']
    problems = [f'{sid}: {name} text does not match the recorded text_sha256'
                for name, segs in (('saved', saved), ('fresh', fresh)) if recorded and text_digest(segs) != recorded]
    # The digest ignores location labels, so a passage moved to another page keeps it: compare segment by segment.
    for i, (old, new) in enumerate(zip_longest(saved, fresh)):
        if old != new:
            problems.append(f'{sid}: segment {i + 1} differs at {(old or new).get("location")}')
            break
    return problems


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
        print(f"{row['product_id']}: {row['old_status']} -> {row['new_status']}; raw bytes "
              f"{row.get('raw_bytes', 'n/a')}; "
              f"extracted text {row.get('extracted_text', 'n/a')}; excerpts found "
              f"{len(found)}/{len(row.get('excerpts', []))}"
              + ''.join(f"; {e['old_location']} -> {e['found_at'][0]}" for e in found if not e['same_location']))
    if dest:
        if Path(dest).exists():
            raise FileExistsError(dest)
        dump(dest, {'tool_version': VERSION, 'checked_at': now(), 'old': str(old), 'new': str(new), 'sources': rows})
    return rows

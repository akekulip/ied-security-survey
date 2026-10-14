"""The review worksheet: where to read, per device and capability."""

from pathlib import Path

from .vocabulary import CAPABILITIES, LEADS, STATEMENTS, life_words
from .store import dump, load
from .leads import load_leads


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

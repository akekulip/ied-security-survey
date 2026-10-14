"""Device notes: who a device is and where it stands with its vendor, on dated vendor evidence only."""

from .vocabulary import FORMER_LIFECYCLES, IDENTITY_LEVELS, LIFECYCLES
from .store import load
from .text import loose
from .fetch import allowed
from .review import cited


def device_records(cfg, sources, notes_path, segments):
    """Who each device is and where it stands with its vendor. A lifecycle status without dated vendor evidence is refused."""
    products = {p['id']: p for p in cfg['products']}
    byid = {s['id']: s for s in sources}
    notes = {n['product_id']: n for n in (load(notes_path) if notes_path else [])}
    if set(notes) - set(products):
        raise ValueError(f'device notes name products that are not in this run: {sorted(set(notes) - set(products))}')
    devices = {}
    for pid, p in products.items():
        n = notes.get(pid, {})
        former = p['lifecycle'] if p.get('lifecycle') in FORMER_LIFECYCLES else ''
        d = {'identity_level': n.get('identity_level') or '',
             'lifecycle_status': n.get('lifecycle_status') or ('' if former else p.get('lifecycle')) or 'unknown',
             'vendor_label': n.get('vendor_label') or p.get('vendor_label') or (f'{former} (label used before 1.6.0)' if former else ''),
             'lifecycle_evidence': n['lifecycle_evidence'] if 'lifecycle_evidence' in n else ([] if former else p.get('lifecycle_evidence') or []),
             'release_date': n.get('release_date') or '', 'release_evidence': n.get('release_evidence') or [],
             'dnp3': n.get('dnp3') or '', 'dnp3_note': n.get('dnp3_note') or '',
             'note': n.get('note') or '', 'noted_by': n.get('noted_by') or ''}
        status, proof = d['lifecycle_status'], d['lifecycle_evidence']
        if status not in LIFECYCLES:
            raise ValueError(f'lifecycle_status must be one of {", ".join(LIFECYCLES)}: {pid}')
        if d['identity_level'] not in ('',) + IDENTITY_LEVELS:
            raise ValueError(f'identity_level must be one of {", ".join(IDENTITY_LEVELS)}, or empty: {pid}')
        # Protocol, missing security features and the age of a manual decide nothing here. Only the vendor's dated word does.
        # Whether the device speaks DNP3 is read from its documents; a reviewer corrects that only with a reason.
        if d['dnp3'] not in ('', 'supported', 'not_established'):
            raise ValueError(f'dnp3 is "supported", "not_established" or empty: {pid}')
        if d['dnp3'] and not d['dnp3_note']:
            raise ValueError(f'dnp3 {d["dnp3"]} needs a dnp3_note saying why: {pid}')
        if status != 'unknown' and not proof:
            raise ValueError(f'lifecycle status {status} needs dated vendor evidence; without it the status is unknown: '
                             f'{pid}')
        for e in proof + d['release_evidence']:
            s = byid.get(e.get('source_id'))
            if e.get('source_id') and (not s or s['product_id'] != pid):
                raise ValueError(f'lifecycle evidence cites a source that is not one of this product in this run: {pid}')
            if s:
                e.setdefault('url', s['final_url'])
                e.setdefault('sha256', s['sha256'])
            where = e.get('url')
            if not where or not allowed(where, p['domains']):
                raise ValueError(f'lifecycle evidence must be a vendor source: a source of this run or a URL on the '
                                 f'product domains: {pid}')
            e['dated'] = e.get('stated_date') or (e.get('retrieved_at') or (s or {}).get('retrieved_at') or '')[:10]
            if not e['dated']:
                raise ValueError(f'lifecycle evidence needs a date: the one the vendor states, or the retrieval date: '
                                 f'{pid}')
            if e.get('source_id') and e.get('location') and e.get('quote'):
                text = cited(segments(e['source_id']), e['location'])
                if text is None or loose(e['quote']) not in loose(text):
                    raise ValueError(f"lifecycle quote not found at {e['location']} of source {e['source_id']}: {pid}")
        if status in ('end_of_support', 'discontinued_supported') and not any(len(loose(e.get('quote') or '')) >= 20 for e in proof):
            raise ValueError(f"{status} needs the vendor's own sentence as a quote: {pid}")
        if d['release_date'] and not d['release_evidence']:
            raise ValueError(f'release_date needs release_evidence from a vendor source: {pid}')
        devices[pid] = d
    return devices

"""Review rows: what a reviewer may claim, and what each claim has to show."""

import re
from collections import Counter
from pathlib import Path

from .vocabulary import (
    ACTIVATION_NEEDS, CAPABILITIES, DEFAULT_STATES, DEPLOYMENT_STATES, EVIDENCE_ABOUT, FORMER, INTERFACE_CLASSES, NOT_ASSESSED,
    REVIEW_STATUSES, STATUSES, SUPPORT_BASES, UNKNOWN_REASONS)
from .store import dump, load, now
from .text import loose, squash


def cited(segments, location):
    """Text at a location: one segment, or a short run of consecutive ones written as html-block:10-13."""
    m = re.fullmatch(r'(html-block:|pdf-page:)(\d+)(?:-(\d+))?', location or '')
    if not m or not int(m[2]) <= int(m[3] or m[2]) < int(m[2]) + 10:
        return None
    text = {x['location']: x['text'] for x in segments}
    parts = [text.get(m[1] + str(n)) for n in range(int(m[2]), int(m[3] or m[2]) + 1)]
    return None if None in parts else ' '.join(parts)


def settle(r):
    """Reads a row written under earlier rules: six statuses become four, and the reason is kept."""
    if r.get('status') in FORMER:
        r.update(unknown_reason=FORMER[r['status']], status='unknown')
    return r


def silent(r):
    return r['status'] == 'unknown' and r.get('unknown_reason') == 'complete_document_silent'


def grounded(r):
    """A row that rests on cited sources: any result, and an unknown that says the documents are silent or disagree."""
    return r['status'] != 'unknown' or r.get('unknown_reason') in ('complete_document_silent', 'sources_conflict')


def token(r):
    """How a grounded row is counted. A capability reached only through an external gateway is not the device's own."""
    if r['status'] == 'unknown':
        return {'complete_document_silent': 'silent', 'sources_conflict': 'conflict'}.get(r.get('unknown_reason'), 'unknown')
    return 'gateway' if r['status'] == 'conditional' and r.get('support_basis') == ['external_gateway'] else r['status']


def named(r):
    return {'silent': 'unknown: complete document silent', 'conflict': 'unknown: sources conflict',
            'gateway': 'conditional: external gateway only'}.get(token(r), r['status'].replace('_', ' '))


def facts(r):
    """The facts a supported or conditional row states beyond the result. A row from an earlier review lacks them: not assessed."""
    result = r['status'] in ('supported', 'conditional')
    return {'basis': r.get('support_basis', [NOT_ASSESSED] if result else []),
            'default': r.get('default_state', NOT_ASSESSED if result else ''),
            'needs': r.get('activation_needs', [NOT_ASSESSED] if result else []),
            'deployment': r.get('deployment_status') or 'unknown'}


def check_claim(r, key, scope, classes):
    """What every row states: a result, who reviewed it and why, and for a claim the interface and scope it applies to."""
    if r['status'] not in STATUSES:
        raise ValueError(f'invalid status: {key}')
    if not all(r.get(k) for k in ('reviewer', 'reviewed_at', 'rationale')):
        raise ValueError(f'review identity/date/rationale required, including unknowns: {key}')
    reason = r.get('unknown_reason') or ''
    if reason and (r['status'] != 'unknown' or reason not in UNKNOWN_REASONS):
        raise ValueError(f'unknown_reason belongs to an unknown row and is one of {", ".join(UNKNOWN_REASONS)}: {key}')
    if grounded(r) and not r['source_ids']:
        raise ValueError(f'claim requires source evidence: {key}')
    # Silence has no passage to point at, so such a row states only where it applies and to which firmware.
    needed = ('interface', 'firmware') if silent(r) else ('location','protocol','interface','firmware','implementation')
    if grounded(r) and not all(r.get(k) for k in needed):
        raise ValueError(f'claim scope is incomplete: {key}')
    kind = r.get('interface_class') or ''
    if kind not in INTERFACE_CLASSES + (() if grounded(r) else ('',)):
        raise ValueError(f'claim needs interface_class, one of {", ".join(INTERFACE_CLASSES)}: {key}')
    if scope and kind and classes.setdefault((key[0], scope), kind) != kind:
        raise ValueError(f'one interface is filed under two interface classes: {key}')
    if r['status'] == 'conditional' and not r.get('conditions'):
        raise ValueError(f'conditional result must state its conditions: {key}')
    if (r.get('review_status') or 'draft') not in REVIEW_STATUSES:
        raise ValueError(f'review_status must be one of {", ".join(REVIEW_STATUSES)}: {key}')


def check_sources(r, key, byid):
    """Cited sources belong to the product, yielded text, and are the bytes the reviewer read."""
    for sid in r['source_ids']:
        s = byid.get(sid)
        if not s or s['status'] != 'extracted' or s['product_id'] != r['product_id']:
            raise ValueError(f'missing/failed/wrong-product source: {key}')
        if r['source_hashes'].get(sid) != s['sha256']:
            raise ValueError(f'review/source hash mismatch: {key}')


def check_facts(r, key, vendor_documents):
    """What the finding applies to, how the capability is obtained, how it ships and what switching it on takes."""
    result, f = r['status'] in ('supported', 'conditional'), facts(r)
    for k in ('model_scope', 'hardware_revision'):
        if grounded(r) and not r.get(k, NOT_ASSESSED):
            raise ValueError(f'{k} is empty; write what the document names, "not established" or {NOT_ASSESSED}: {key}')
    for name, value, allowed_values in (('support_basis', f['basis'], SUPPORT_BASES), ('activation_needs', f['needs'], ACTIVATION_NEEDS)):
        if not isinstance(value, list) or set(value) - set(allowed_values) - {NOT_ASSESSED}:
            raise ValueError(f'{name} is a list from {", ".join(allowed_values)}, or [{NOT_ASSESSED!r}]: {key}')
        if result and not value:
            raise ValueError(f'{name} is empty; a supported or conditional result states it, or says {NOT_ASSESSED}: {key}')
        if value and not result:
            raise ValueError(f'{name} belongs to a supported or conditional result only: {key}')
        if len(value) > 1 and set(value) & {NOT_ASSESSED, 'not_stated', 'none_stated'}:
            raise ValueError(f'{name} mixes a value with "nothing stated" or "{NOT_ASSESSED}": {key}')
    if r['status'] == 'supported' and f['basis'] not in (['built_in'], [NOT_ASSESSED]):
        raise ValueError(f'supported means built in; a firmware upgrade, module, licence or gateway makes it conditional: {key}')
    if f['default'] not in (DEFAULT_STATES + (NOT_ASSESSED,) if result else ('',)):
        raise ValueError(f'default_state is one of {", ".join(DEFAULT_STATES)} or {NOT_ASSESSED}, for a supported or conditional result only: {key}')
    if set(f['needs']) - {'none_stated', NOT_ASSESSED} and not r.get('activation_requirements'):
        raise ValueError(f'activation_needs are named but activation_requirements does not describe them: {key}')
    if f['deployment'] not in DEPLOYMENT_STATES:
        raise ValueError(f'deployment_status must be one of {", ".join(DEPLOYMENT_STATES)}: {key}')
    proof = r.get('deployment_evidence') or []
    if f['deployment'] != 'unknown':
        if not proof or not all(isinstance(e, dict) and all(e.get(k) for k in ('kind', 'reference', 'date', 'scope')) for e in proof):
            raise ValueError(f'deployment_status {f["deployment"]} needs deployment_evidence with kind, reference, date and scope; without it the status is unknown: {key}')
        if any(e['reference'] in vendor_documents for e in proof):
            raise ValueError(f'a vendor document shows what a device can do, not what an operator enabled; it is not deployment evidence: {key}')
    waiting = NOT_ASSESSED in [r.get('model_scope', NOT_ASSESSED), r.get('hardware_revision', NOT_ASSESSED), f['default']] + f['basis'] + f['needs']
    if result and waiting and r.get('review_status') == 'confirmed':
        raise ValueError(f'a confirmed row may not leave a field {NOT_ASSESSED}: {key}')


def check_evidence(r, key, segments, require_evidence):
    """Quotes say what they are about and are found, word for word, at the location they cite."""
    f = facts(r)
    evidence = r.get('evidence') or []
    about = Counter(e.get('about') or 'capability' for e in evidence)
    if set(about) - set(EVIDENCE_ABOUT):
        raise ValueError(f'evidence "about" must be one of {", ".join(EVIDENCE_ABOUT)}: {key}')
    if require_evidence:
        if r['status'] != 'unknown' and not about['capability']:
            raise ValueError(f'claim requires a verbatim evidence quote: {key}')
        # Each further fact needs its own words from the document, not the quote that shows the capability exists.
        for what, stated in (('default', f['default'] in ('enabled', 'disabled')),
                             ('conditions', bool(set(f['basis']) - {'built_in', 'not_stated', NOT_ASSESSED})),
                             ('activation', bool(set(f['needs']) - {'none_stated', NOT_ASSESSED}))):
            if stated and not about[what]:
                raise ValueError(f'this row states its {what}; that needs an evidence quote marked about: {what}: {key}')
    # A quote proves the words are in the cited passage; whether they support the claim stays the reviewer's call.
    for e in evidence:
        wanted = loose(e.get('quote', ''))
        if e.get('source_id') not in r['source_ids']:
            raise ValueError(f'evidence cites a source outside this review: {key}')
        if len(wanted) < 20:
            raise ValueError(f'evidence quote too short to identify a passage: {key}')
        if segments:
            text = cited(segments(e['source_id']), e.get('location'))
            if text is None or wanted not in loose(text):
                raise ValueError(f"evidence quote not found at {e.get('location')} of source {e['source_id']}: {key}")


def validate_reviews(rows, sources, products, segments=None, require_evidence=False):
    byid = {s['id']: s for s in sources}
    vendor_documents = {x for s in sources for x in (s['id'], s.get('url'), s.get('final_url')) if x}
    seen, classes = set(), {}
    for r in rows:
        settle(r)
        key = r['product_id'], r['feature']
        scope = squash(r.get('interface') or '').lower()
        # One capability may be recorded once per interface: TLS for DNP3 and TLS for a web page are different findings.
        if key + (scope,) in seen or key[0] not in products or key[1] not in CAPABILITIES:
            raise ValueError(f'duplicate/unknown review key: {key}')
        seen.add(key + (scope,))
        check_claim(r, key, scope, classes)
        check_sources(r, key, byid)
        check_facts(r, key, vendor_documents)
        check_evidence(r, key, segments, require_evidence)


def untouched(row):
    """A template row nobody has filled in. It is not a finding: it is left out and counted as not reviewed."""
    blank = ('reviewer', 'reviewed_at', 'rationale', 'source_ids', 'source_hashes', 'evidence', 'location', 'protocol',
             'interface', 'interface_class', 'conditions', 'review_status', 'unknown_reason', 'support_basis', 'default_state',
             'activation_needs', 'activation_requirements', 'deployment_evidence')
    return (row.get('status') == 'unknown' and not any(row.get(k) for k in blank)
            and (row.get('deployment_status') or 'unknown') == 'unknown')


def rebind(review_path, old, run, dest):
    """Carries a review over to a refetch of the same documents, where the extracted text is unchanged. Nothing else is carried."""
    dest, run = Path(dest), Path(run)
    if dest.exists():
        raise FileExistsError(dest)
    rows = load(review_path)
    before = {s['id']: s for s in load(Path(old) / 'sources.json')}
    after = {s['id']: s for s in load(run / 'sources.json')}
    moved, stuck = set(), {}
    for r in rows:
        for sid, bound in list((r.get('source_hashes') or {}).items()):
            was, new = before.get(sid, {}), after.get(sid, {})
            if new.get('sha256') == bound:
                continue
            # A dynamic page returns different bytes on every request. Identical extracted text is what makes it the same document.
            if was.get('sha256') == bound and new.get('status') == 'extracted' and was.get('text_sha256') and was['text_sha256'] == new.get('text_sha256'):
                r['source_hashes'][sid] = new['sha256']
                r.setdefault('rebound', []).append({'source_id': sid, 'from_sha256': bound, 'to_sha256': new['sha256'], 'text_sha256': new['text_sha256'],
                                                    'basis': 'extracted text unchanged', 'rebound_at': now()})
                moved.add(sid)
            else:
                stuck.setdefault(sid, []).append(f"{r['product_id']}/{r['feature']}")
    if stuck:
        raise ValueError('the text of these sources changed or cannot be compared, so their rows need a new review: '
                         + '; '.join(f"{sid} ({', '.join(cells)})" for sid, cells in stuck.items()))
    dump(dest, rows)
    print(f"{sum(bool(r.get('rebound')) for r in rows)} rows re-bound to {len(moved)} refetched sources with unchanged text; written to {dest}. "
          'Evidence quotes are checked against the new run when the report is made.')

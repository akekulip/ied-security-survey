"""A run and its review, resolved once: what every table and count of the report asks of them.

Everything here is checked before a single output file is written, so a refused review leaves no half-made report.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path

from .vocabulary import (
    CAPABILITIES, COMPLETE_TYPES, DOC_TYPES, INTERFACE_CLASSES, NOT_ASSESSED, PROPERTIES, RELATES, lead_type, legacy_states,
    life_words)
from .store import load
from .text import squash
from .leads import load_leads
from .review import facts, grounded, named, silent, token, untouched, validate_reviews
from .devices import device_records


COLUMNS = ('Manufacturer', 'Model', 'Lifecycle', 'Evidence applies to', 'Protocol / interface', 'Authentication', 'Integrity',
           'Encryption', 'Support conditions', 'Default', 'Activation', 'Deployment', 'Evidence', 'Review status')
# The CSV keeps the three parts of "evidence applies to" in columns of their own.
CSV_COLUMNS = (COLUMNS[:3] + ('Category', 'Model scope', 'Hardware revision', 'Firmware', COLUMNS[4], 'Interface class')
               + COLUMNS[5:] + ('Sources',))
MARK = {'supported': 'S', 'conditional': 'C', 'gateway': 'G', 'explicitly_unsupported': 'X', 'silent': '?s', 'conflict': '?c',
        'unknown': '?'}
# The most favourable documented result wins when a capability has several on one kind of interface.
RANK = ('supported', 'conditional', 'gateway', 'conflict', 'explicitly_unsupported', 'silent')
POSITIVE = ('supported', 'conditional')
# DNP3 named in a document. It marks a device as a DNP3 device; it is not a finding about the device's security.
DNP3 = re.compile(r'\bDNP\s?3i?\b|\bDNP\b|IEEE\s*(?:Std\s*)?1815', re.I)
# A DNP3 device's own protection, strongest first. Plaintext means that no DNP3 security is documented.
DNP3_KINDS = (('tls', 'Encrypted: DNP3 over TLS or IPsec'),
              ('authenticated', 'Authenticated, not encrypted (e.g. DNP3 Secure Authentication)'),
              ('tunnel', 'Encryption documented for its control protocols, DNP3 not named'),
              ('external', 'Only through a separate encrypting device'),
              ('denied', 'Vendor states DNP3 is not protected'),
              ('none', 'No DNP3 security documented (plaintext)'))


def md(x):
    return str(x).replace('|', '/').replace('\n', ' ')


def flat(x):
    return ' '.join(str(x).split())


def words(values):
    return ', '.join(v.replace('_', ' ') for v in values)


def joined(values, empty):
    return '; '.join(dict.fromkeys(v.replace(NOT_ASSESSED, 'not assessed') for v in values if v)) or empty


def per_feature(pairs, empty):
    # One value when every finding on the interface agrees, otherwise each capability with its own.
    texts = list(dict.fromkeys(t for _, t in pairs))
    return empty if not pairs else texts[0] if len(texts) == 1 else '; '.join(f'{f}: {t}' for f, t in pairs)


def scope(r):
    return squash(r.get('interface') or '').lower()


class Findings:
    """The run, its sources, its devices and its reviewed rows, with the lookups the report is built from."""

    def __init__(self, run, review_path, require_evidence=False, source_notes=None, device_notes=None):
        self.run = run = Path(run)
        self.cfg, self.sources, rows = load(run / 'config.json'), load(run / 'sources.json'), load(review_path)
        self.products = {p['id']: p for p in self.cfg['products']}

        def segments(sid):
            return load(run / (sid + '.segments.json'))

        self.devices = device_records(self.cfg, self.sources, device_notes, segments)
        # Lets a review proceed in stages. A partly filled row is still an error, never silently dropped.
        self.blank = sum(map(untouched, rows))
        self.rows = rows = [r for r in rows if not untouched(r)]
        validate_reviews(rows, self.sources, self.products, segments, require_evidence)
        self.byid = {s['id']: s for s in self.sources}
        self._resolve_documents(source_notes)
        self._count_leads()
        self._check_silence()
        self._find_dnp3()

        self.claims = [r for r in rows if grounded(r)]
        self.stated = [r for r in rows if r['status'] in POSITIVE]
        self.cell = {(r['product_id'], r['feature'], scope(r)): r for r in rows}
        self.reviewed = {(r['product_id'], r['feature']) for r in rows}
        self.expected = len(self.products) * len(CAPABILITIES)
        self._claimed = defaultdict(list)
        for r in self.claims:
            self._claimed[r['product_id'], r['feature']].append(r)

        self.recorded = sum(d['lifecycle_status'] != 'unknown' for d in self.devices.values())
        # Results are counted by lifecycle group only when the config the run was crawled with says what the groups mean.
        self.defined = self.cfg.get('definitions') or {}
        self.legacy = legacy_states(self.defined)
        self.grouped = bool(self.legacy)
        self.totals = Counter(s['status'] for s in self.sources)
        self.legacy_devices = [pid for pid, d in self.devices.items() if d['lifecycle_status'] in self.legacy]
        # A DNP3 device is one whose own documents name DNP3, unless a device note says the mention is about other
        # products. A note may also add a device whose documents the search missed.
        self.dnp3 = [pid for pid in self.products if self.devices[pid]['dnp3'] == 'supported'
                     or (self.dnp3_sources.get(pid) and self.devices[pid]['dnp3'] != 'not_established')]
        # A census has hundreds of devices and no review yet; a row per unreviewed device would bury the reviewed ones.
        bare = {pid for pid in self.products if not any(r['product_id'] == pid for r in rows)}
        self.bare = bare if len(bare) > 25 else set()
        self.table = self._interface_rows()

    # --- built once ---

    def _resolve_documents(self, source_notes):
        notes = {n['source_id']: n for n in (load(source_notes) if source_notes else [])}
        if set(notes) - set(self.byid):
            raise ValueError(f'source notes name sources that are not in this run: '
                             f'{sorted(set(notes) - set(self.byid))}')
        wrong = sorted({n.get('doc_type') for n in notes.values() if n.get('doc_type')} - set(DOC_TYPES))
        if wrong:
            raise ValueError(f'source notes use a doc_type outside {", ".join(DOC_TYPES)}: {wrong}')
        if {n.get('coverage') or '' for n in notes.values()} - {'', 'complete', 'partial'}:
            raise ValueError('source notes: coverage must be complete, partial or empty')
        # The source manifest: URL, retrieval time and hash come from the crawl, the document's own number and date from a reviewer.
        self.refs, self.cite = {}, {}
        for s in self.sources:
            if s['status'] == 'extracted':
                self.refs[s['id']] = s['ref'] = f'S{len(self.refs) + 1}'
                s['document'] = {k: notes.get(s['id'], {}).get(k, '')
                                 for k in ('doc_type', 'coverage', 'document_id', 'revision', 'document_date', 'note')}
                # What kind of document a quote comes from travels with every reference to it.
                self.cite[s['id']] = f"{s['ref']} [{s['document']['doc_type'].replace('_', ' ') or 'type not confirmed'}]"

    def _count_leads(self):
        # Lead counts say how much text mentioned a term. They are never device counts, and statements are kept apart.
        self.leads = {p: {t: Counter() for t in ('capability', 'related', 'statement', 'profile')} for p in self.products}
        self.mentions = Counter()
        for h in load_leads(self.run):
            kind = h.get('lead_type') or lead_type(h['feature'])
            self.leads[h['product_id']][kind][h['feature']] += 1
            if kind in ('capability', 'profile'):
                self.mentions[h['source_id'], h['feature']] += 1

    def _check_silence(self):
        # What a complete manual does not say is recorded as unknown with that reason. The tool checks the silence itself:
        # such a row must cite complete documents in which the search found no lead for that capability.
        self.searched = {}
        for r in self.rows:
            if silent(r):
                key = r['product_id'], r['feature']
                for sid in r['source_ids']:
                    doc = self.byid[sid]['document']
                    if doc['doc_type'] not in COMPLETE_TYPES or doc['coverage'] != 'complete':
                        raise ValueError(f'complete_document_silent needs a complete {", ".join(COMPLETE_TYPES)} '
                                         f'(doc_type and coverage in the '
                                         f'source notes); source {sid} is {doc["doc_type"] or "untyped"}, '
                                         f'{doc["coverage"] or "coverage not stated"}: {key}')
                    if self.mentions[sid, r['feature']]:
                        raise ValueError(f'{self.mentions[sid, r["feature"]]} leads for {r["feature"]} exist in source '
                                         f'{sid}; '
                                         f'review them before recording complete_document_silent: {key}')
                self.searched[id(r)] = '; '.join(
                    f"{self.cite[sid]} searched in full" + (f", {self.byid[sid]['pages']} PDF pages" if self.byid[sid].get('pages') else '')
                    + f": no lead for {r['feature']}" for sid in r['source_ids'])

    def _find_dnp3(self):
        self.dnp3_sources = defaultdict(list)
        for s in self.sources:
            if s['status'] == 'extracted' and any(DNP3.search(g['text']) for g in load(self.run / (s['id'] + '.segments.json'))):
                self.dnp3_sources[s['product_id']].append(s['id'])

    def _interface_rows(self):
        """One row per product and interface. Repeated keyword matches cannot add rows; only reviewed findings can."""
        table = []
        for pid, p in self.products.items():
            groups = {}
            for r in self.claims:
                if r['product_id'] == pid:
                    groups.setdefault((r['interface_class'], scope(r)), []).append(r)
            groups = sorted(groups.items(), key=lambda g: INTERFACE_CLASSES.index(g[0][0]))
            if not groups or groups[0][0][0] != 'control_protocol':
                # The study asks about control traffic, so its absence is stated instead of left out.
                groups.insert(0, (('control_protocol', ''), []))
            for (kind, where), members in groups:
                signed = members or [r for r in self.rows if r['product_id'] == pid and not scope(r)]
                used = list(dict.fromkeys(sid for m in members for sid in m['source_ids']))
                stated = [m for m in members if m['status'] in POSITIVE]
                row = {
                    'pid': pid, 'Manufacturer': p.get('vendor', ''), 'Model': p.get('model') or pid, 'Lifecycle': self.lifecycle(pid),
                    'Category': self.category(pid), 'Interface class': kind,
                    'Searched': '; '.join(self.searched[id(m)] for m in members if id(m) in self.searched),
                    'Model scope': joined((flat(m.get('model_scope', NOT_ASSESSED)) for m in members), 'not established'),
                    'Hardware revision': joined((flat(m.get('hardware_revision', NOT_ASSESSED)) for m in members), 'not established'),
                    'Firmware': joined((flat(m['firmware']) for m in members), 'not established'),
                    'Protocol / interface': (f"{flat(members[0]['interface'])} ({kind.replace('_', ' ')})" if members
                                             else 'No control protocol established from the examined sources'),
                    'Support conditions': joined((words(facts(m)['basis']) + (f": {flat(m['conditions'])}" if m.get('conditions') else '')
                                                  for m in stated), 'none stated' if members else '-'),
                    'Default': per_feature([(m['feature'], facts(m)['default'].replace('_', ' ')) for m in stated], '-'),
                    'Activation': per_feature([(m['feature'], words(facts(m)['needs']) + (f": {flat(m['activation_requirements'])}"
                                                                                            if m.get('activation_requirements') else ''))
                                               for m in stated], '-'),
                    # Unknown unless someone cites evidence from an installation. No vendor document can change this cell.
                    'Deployment': joined((facts(m)['deployment'] + (' (' + '; '.join(f"{e['kind']}, {e['date']}" for e in m['deployment_evidence']) + ')'
                                                                    if facts(m)['deployment'] != 'unknown' else '') for m in members), 'unknown'),
                    'Evidence': [(self.cite[e['source_id']], e['location'], flat(e['quote'])) for m in members for e in m.get('evidence') or []],
                    'Review status': '; '.join(dict.fromkeys(f"{m.get('review_status') or 'draft'} ({flat(m['reviewer'])})"
                                                             for m in signed)) or 'not reviewed',
                    'Sources': '; '.join(f"{self.cite[sid]} {self.byid[sid]['final_url']} "
                                         f"sha256:{self.byid[sid]['sha256']}" for sid in used)}
                row.update({name.capitalize(): self.prop(pid, where, members, name) for name in PROPERTIES})
                # Two findings on one interface may rest on documents for different models or firmware; then each says its own.
                row['Evidence applies to'] = per_feature(
                    [(m['feature'], ', '.join(f"{name} "
                                              f"{flat(m.get(key, NOT_ASSESSED)).replace(NOT_ASSESSED, 'not assessed')}" for name, key in
                                              (('model', 'model_scope'), ('hardware', 'hardware_revision'), ('firmware', 'firmware'))))
                     for m in members], 'not established')
                table.append(row)
        return table

    # --- asked of one device ---

    def model(self, pid):
        return md(self.products[pid].get('model') or pid)

    def category(self, pid):
        return self.products[pid].get('category') or 'uncategorised'

    def lifecycle(self, pid):
        return life_words(self.devices[pid]['lifecycle_status'])

    def legacy_word(self, pid):
        """Whether the device is legacy as the run's config defines it. Unknown where its lifecycle state is."""
        status = self.devices[pid]['lifecycle_status']
        return '' if not self.grouped else 'unknown' if status == 'unknown' else 'yes' if status in self.legacy else 'no'

    def stratum_of(self, pid):
        return f'{self.category(pid)}, {self.lifecycle(pid)}' if self.grouped else self.category(pid)

    def prop(self, pid, where, members, feature):
        """What the review says about one property on one interface. Mechanism rows are pointed to, never read as a result."""
        r = self.cell.get((pid, feature, where)) or self.cell.get((pid, feature, ''))
        if r and silent(r):
            return 'unknown: the complete documentation searched does not mention it'
        if r and token(r) == 'conflict':
            return 'unknown: sources conflict'
        if r and r['status'] != 'unknown':
            return f"{named(r)}: {flat(r['protocol'])}"
        see = [f"{m['feature']} ({named(m)})" for m in members if m['feature'] in RELATES[feature]]
        return ('unknown' if r else 'not assessed' if see else 'not reviewed') + ('; see ' + ', '.join(see) if see else '')

    def results(self, pid, feature, kinds):
        return [token(r) for r in self._claimed[pid, feature] if r['interface_class'] in kinds]

    def matrix(self, pid, feature):
        control, other = self.results(pid, feature, ('control_protocol',)), self.results(pid, feature, ('management', 'network'))
        if control:
            return '/'.join(dict.fromkeys(MARK[x] for x in control))
        if other:
            return '(' + '/'.join(dict.fromkeys(MARK[x] for x in other)) + ')'
        return '?' if (pid, feature) in self.reviewed else '-'

    def dnp3_security(self, pid):
        """The strongest DNP3 protection the review establishes for a device, and the rows it rests on."""
        found = defaultdict(list)
        for r in self.claims:
            if r['product_id'] != pid or r['interface_class'] != 'control_protocol':
                continue
            named_dnp3, positive = bool(DNP3.search(f"{r.get('interface', '')} {r.get('protocol', '')}")), r['status'] in POSITIVE
            if positive and r.get('support_basis') == ['external_gateway']:
                found['external'].append(r)
            elif positive and named_dnp3 and r['feature'] in ('tls', 'encryption', 'ipsec'):
                found['tls'].append(r)
            elif positive and named_dnp3 and r['feature'] in ('dnp3_secure_authentication', 'authentication', 'integrity'):
                found['authenticated'].append(r)
            elif positive and r['feature'] in ('tls', 'encryption', 'ipsec', 'ssh'):
                found['tunnel'].append(r)
            elif r['status'] == 'explicitly_unsupported' and named_dnp3:
                found['denied'].append(r)
        kind = next((k for k, _ in DNP3_KINDS if found[k]), 'none')
        return kind, found[kind]

    def dnp3_source(self, pid, rows):
        """Where to check the DNP3 result: (reference, location, URL, quote) for the passage a result rests on, or else
        for each document of the device that names DNP3."""
        for r in rows:
            for e in r.get('evidence') or []:
                if (e.get('about') or 'capability') == 'capability':
                    return [(self.byid[e['source_id']]['ref'], e['location'], self.byid[e['source_id']]['final_url'], flat(e['quote']))]
        if rows:
            sid = rows[0]['source_ids'][0]
            return [(self.byid[sid]['ref'], rows[0].get('location') or '', self.byid[sid]['final_url'], '')]
        return [(self.byid[sid]['ref'], '', self.byid[sid]['final_url'], '') for sid in self.dnp3_sources.get(pid, [])]

    def bucket(self, pid, feature):
        """How one device counts for one capability: its result for control traffic, or why there is none."""
        control = self.results(pid, feature, ('control_protocol',))
        if control:
            return min(control, key=RANK.index)
        if self.results(pid, feature, ('management', 'network')):
            return 'other'
        return 'unknown' if (pid, feature) in self.reviewed else None

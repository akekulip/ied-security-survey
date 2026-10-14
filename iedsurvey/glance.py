"""At a glance: the charts of a report and the sentences that go with them, the answer to the survey's question first."""

import re
from collections import Counter

from .vocabulary import CAPABILITIES, LIFECYCLES, PROPERTIES, life_words
from .store import dump
from .findings import MECHANISMS, POSITIVE, md
from .charts import (
    CYCLE, DOCUMENT_SERIES, LIFECYCLE_SERIES, POSTURE_SERIES, RESULT_SERIES, UNUSED_SERIES, svg_bars, svg_grid,
    title_of)


INTRO = ['', '## At a glance', '',
         'Drawn from this run alone. Every number is also in a table below, and charts/data.json holds the series behind each chart. '
         'A chart of documents or mentions describes what could be read, not what a device can do; only the chart of results does that, and only for reviewed cells.']
DIRECT = ('device_profile', 'conformance_statement', 'security_guide', 'manual')
BRIEF = {'supported': 'supported', 'conditional': 'conditional', 'gateway': 'via gateway only', 'explicitly_unsupported': 'stated unsupported',
         'silent': 'manual silent', 'conflict': 'sources conflict', 'other': 'management only', 'unknown': 'unknown', None: 'not reviewed'}


class Figures:
    """The charts of one report: each file as it is drawn, and the series behind it for data.json."""

    def __init__(self, folder):
        self.folder, self.data = folder, {}
        # A chart from an earlier report of the same name must not survive into one that no longer draws it.
        for stale in folder.glob('*.*') if folder.is_dir() else ():
            stale.unlink()

    def add(self, name, alt, svg, data):
        self.folder.mkdir(exist_ok=True)
        (self.folder / f'{name}.svg').write_text(svg, encoding='utf-8', newline='\n')
        self.data[name] = data
        return ['', f'![{alt}](charts/{name}.svg)']


def tally(pairs):
    table = {}
    for label, key, n in pairs:
        table.setdefault(label, Counter())[key] += n
    return [(label, dict(c)) for label, c in table.items()]


def series(drawing):
    return {label: {str(k): v for k, v in values.items()} for label, values in drawing if values is not None}


def legacy_groups(states):
    names = [f'"{life_words(k)}"' for k in states]
    return f'the {names[0]} group' if len(names) == 1 else f"the {', '.join(names[:-1])} and {names[-1]} groups together"


def catalogue(found, figures):
    """The sampling frame: what the vendor catalogues list, whether or not this run reads it."""
    frame, lines = found.cfg.get('frame') or [], []
    if frame and found.grouped:
        drawing = tally((x['vendor'], x['lifecycle'], x['in_catalogue']) for x in frame)
        total = Counter(x['lifecycle'] for x in frame for _ in range(x['in_catalogue']))
        lines += ['', f"The catalogue inventory holds {sum(total.values())} devices: "
                  + '; '.join(f'{total[k]} {life_words(k)}' for k, _ in LIFECYCLE_SERIES if total[k])
                  + f". Legacy, as defined above, is {legacy_groups(found.legacy)}: {sum(total[k] for k in found.legacy)} devices."]
        lines += figures.add('catalogue-lifecycle', 'Catalogue devices by vendor and lifecycle state',
                             svg_bars(f'Catalogue devices by vendor and lifecycle state ({sum(total.values())} devices)',
                                      ['Every classified entry of the vendor catalogues on the inventory date. A state rests on dated vendor evidence; the vendor calling a product legacy does not decide it.'],
                                      drawing, [(k, life_words(k).capitalize(), c) for k, c in LIFECYCLE_SERIES]), dict(drawing))
    if frame:
        drawing = tally((x['vendor'], x['category'], x['in_catalogue']) for x in frame)
        sorts = sorted({x['category'] for x in frame})
        lines += figures.add('catalogue-category', 'Catalogue devices by vendor and category',
                             svg_bars(f"Catalogue devices by vendor and category ({sum(x['in_catalogue'] for x in frame)} devices)",
                                      [f'The sampling frame. This run reads {len(found.products)} of these devices.'],
                                      drawing, [(k, title_of(k), CYCLE[i % len(CYCLE)]) for i, k in enumerate(sorts)]), dict(drawing))
    return lines


def documents(found, figures):
    """What could be read for each device, and what exists but was left alone."""
    products, sources, best, states = found.products, found.sources, found.best, found.states
    confirmed = sum(bool(s['document']['doc_type']) for s in sources if s['status'] == 'extracted')
    lines = ['', f"Of {len(products)} devices in this run, a manual, device profile, conformance statement or security guide was read for {sum(best[pid] in DIRECT for pid in products)}, "
             f"a data sheet, brochure or a document whose type is not yet established for {sum(v in ('datasheet', 'other') for v in best.values())}, "
             f"only a product page or advisory for {sum(v in ('product_page', 'advisory') for v in best.values())}, "
             f"and nothing for {sum(v == 'none' for v in best.values())}. Document types are the tool's suggestion unless confirmed in the source notes "
             f"({confirmed} of {found.totals['extracted']} sources confirmed)."]
    drawing = tally((products[pid].get('vendor', ''), kind, 1) for pid, kind in best.items())
    if len(states) > 1:
        # The same question of every lifecycle group needs the same kind of document for every group. This shows whether it had one.
        drawing = ([('By vendor', None)] + drawing + [('By lifecycle state', None)]
                   + tally((g.capitalize(), best[pid], 1) for g in states for pid in found.held[g]))
    lines += figures.add('evidence-base', 'Most direct public document read per device, by vendor' + (' and by lifecycle state' if len(states) > 1 else ''),
                         svg_bars(f'Most direct public document read per device ({len(products)} devices)',
                                  ['Each device is counted once, under the most direct kind of document that yielded text. A product page or brochure rarely settles a capability either way.'],
                                  drawing, DOCUMENT_SERIES), {label: values for label, values in drawing if values is not None})
    unused = tally((products[s['product_id']].get('vendor', ''),
                    'sign_in' if s['status'] == 'login_required' else 'skipped' if s['status'] == 'skipped'
                    else 'refused' if 'robots' in s.get('error', '') else 'unreadable', s.get('link_count', 1))
                   for s in sources if s['status'] in ('login_required', 'skipped', 'failed'))
    if unused:
        lines += figures.add('not-used', 'Documents that exist but were not used, by vendor',
                             svg_bars('Documents that exist but were not used',
                                      ['Links and sources, not devices. Only public documents are read: a document behind a sign-in is counted and left alone, and a host whose robots.txt cannot be read is not asked.'],
                                      unused, UNUSED_SERIES), dict(unused))
    return lines


def mentions(found, figures):
    """Where the search found the terms. A mention is a place to read, so these are never results."""
    if not found.totals['extracted']:
        return []
    products, leads, vendors, owned, states, held = found.products, found.leads, found.vendors, found.owned, found.states, found.held
    mentioned = {(pid, c) for pid in products for c in CAPABILITIES if leads[pid]['capability'][c] + leads[pid]['profile'][c]}
    asked = [(c, title_of(c)) for c in PROPERTIES + MECHANISMS]
    lines = ['', f"The search found at least one mention of authentication, integrity or encryption wording for {len({pid for pid, c in mentioned if c in PROPERTIES})} of {len(products)} devices, "
             f"and of DNP3 Secure Authentication for {len({pid for pid, c in mentioned if c == 'dnp3_secure_authentication'})}. "
             'A mention is a place to read. It may be a denial, concern another interface or another product, and its absence from a brochure says nothing.']
    lines += figures.add('mentions', 'Devices whose public documents mention each term, by vendor',
                         svg_grid('Where the terms occur: devices with at least one mention',
                                  ['Devices of each vendor, out of those in this run, whose public documents contain at least one lead for the capability. Mentions are not findings.'],
                                  asked, [(v, v) for v in vendors], lambda c, v: (sum((pid, c) in mentioned for pid in owned[v]), len(owned[v]))),
                         {c: {v: [sum((pid, c) in mentioned for pid in owned[v]), len(owned[v])] for v in vendors} for c, _ in asked})
    if len(states) > 1:
        lines += figures.add('mentions-lifecycle', 'Devices whose public documents mention each term, by lifecycle state',
                             svg_grid('Where the terms occur, by lifecycle state',
                                      ['Read this beside the chart of documents: a group for which only product pages and brochures could be read will show few mentions whatever its devices can do.'],
                                      asked, [(g, g.capitalize()) for g in states], lambda c, g: (sum((pid, c) in mentioned for pid in held[g]), len(held[g]))),
                             {c: {g: [sum((pid, c) in mentioned for pid in held[g]), len(held[g])] for g in states} for c, _ in asked})
    return lines


def answer(found, figures):
    """The question the survey is for: per lifecycle state, what the reviewed documents establish for control traffic."""
    products, states, held, bucket = found.products, found.states, found.held, found.bucket
    stand = {pid: found.posture(pid) for pid in products}
    blocks = [(label, members) for label, members, _ in found.blocks]
    within = [part for _, _, parts in found.blocks for part in parts]

    def said(label, members):
        count = Counter(stand[pid] for pid in members)
        return f"{label}, {len(members)} devices: " + ('; '.join(f'{name.lower()} for {count[k]}' for k, name, _ in POSTURE_SERIES if count[k]) or 'none in this run') + '.'

    lines = ['', f'{len(found.reviewed)} of {found.expected} cells are reviewed. What follows is what those reviewed cells establish for control traffic, such as DNP3, IEC 61850, IEC 60870-5-104, Modbus or EtherNet/IP; protection of a web page or an engineering tool is counted apart. '
             'It is what the documents say a device can do. Whether it is switched on in any installation is not known.']
    for label, members, parts in found.blocks or [('All devices', list(products), [])]:
        # A legacy group that spans several lifecycle states is counted as one, and each state under it.
        lines += ['- ' + said(label, members)] + ['  - ' + said(*part) for part in parts]
    drawing = ((([('Legacy and the other lifecycle states' if within else 'By lifecycle state', None)]
                 + [(label, dict(Counter(stand[pid] for pid in members))) for label, members in blocks]) if blocks else [])
               + ([('Within legacy, by lifecycle state', None)] + [(label, dict(Counter(stand[pid] for pid in members))) for label, members in within] if within else [])
               + [('By vendor', None)] + [(v, dict(Counter(stand[pid] for pid in found.owned[v]))) for v in found.vendors])
    lines += figures.add('answer', 'What the documents establish about protecting control traffic, per device',
                         svg_bars(f'Is control traffic protected, according to the documents? ({len(products)} devices)',
                                  ['Each device is placed once, under the strongest thing the reviewed documents establish for a control protocol. '
                                   'Encryption documented means the traffic need not be plaintext; every other group has no documented encryption of control traffic.'],
                                  drawing, POSTURE_SERIES), series(drawing))
    kinds = [(c, title_of(c)) for c in MECHANISMS]
    grouping = [(label, members) for label, members in blocks if members] or [('All devices', list(products))]
    if any(bucket(pid, c) in POSITIVE for pid in products for c in MECHANISMS):
        lines += figures.add('answer-mechanisms', 'Which security mechanism is documented for control traffic',
                             svg_grid('Which kind of security: mechanism documented for control traffic',
                                      ['Devices for which the mechanism is supported or conditional for a control protocol, out of the devices in the group. '
                                       'DNP3 Secure Authentication authenticates and does not encrypt; CIP Security always authenticates and encrypts only where confidentiality is configured.'],
                                      kinds, [(label, label) for label, _ in grouping],
                                      lambda c, g: (sum(bucket(pid, c) in POSITIVE for pid in dict(grouping)[g]), len(dict(grouping)[g]))),
                             {c: {label: [sum(bucket(pid, c) in POSITIVE for pid in members), len(members)] for label, members in grouping} for c, _ in kinds})
    groups = [('all devices', list(products))] + [(g, held[g]) for g in states] + [('legacy', found.legacy_devices)] * bool(within and found.legacy_devices)
    for n, (group, members) in enumerate(groups if len(groups) > 2 else groups[:1]):
        drawing = ([('Properties of the interface', None)] + [(title_of(c), dict(Counter(bucket(pid, c) for pid in members))) for c in PROPERTIES]
                   + [('Mechanisms that may provide them', None)]
                   + [(title_of(c), dict(Counter(bucket(pid, c) for pid in members))) for c in MECHANISMS])
        lines += figures.add('results' if not n else 'results-' + re.sub(r'[^a-z]+', '-', group), f'Result per capability for a control protocol, {group}',
                             svg_bars(f'Result per capability for a control protocol: {group} ({len(members)} devices)',
                                      ['Each device is counted once per capability, under its most favourable documented result for control traffic. A mechanism being supported does not by itself establish a property.'],
                                      drawing, RESULT_SERIES), series(drawing))
    return lines, stand


def device_by_device(found, stand, folder):
    """Which ones: every reviewed device on one line, grouped the way the question was asked."""
    products, devices, bucket, best = found.products, found.devices, found.bucket, found.best
    stance = dict((k, name) for k, name, _ in POSTURE_SERIES)
    read = dict((k, name) for k, name, _ in DOCUMENT_SERIES)
    ordered = [pid for pid in sorted(products, key=lambda x: (LIFECYCLES.index(devices[x]['lifecycle_status']), products[x].get('vendor', ''), str(products[x].get('model') or x)))
               if stand[pid] is not None]
    legacy = ['Legacy'] * found.grouped
    dump(folder / 'devices-control-traffic.json',
         [{'product_id': pid, 'lifecycle_status': devices[pid]['lifecycle_status'], 'legacy': found.legacy_word(pid),
           'vendor': products[pid].get('vendor', ''), 'model': products[pid].get('model') or pid,
           'established': stand[pid], **{c: bucket(pid, c) for c in CAPABILITIES}, 'most_direct_document': best[pid]} for pid in products])
    return (['', '## Control traffic, device by device', '',
             'Every device with a reviewed cell, by lifecycle state. "Mechanism" lists what is supported or conditional for a control protocol. A device documented only through a product page or brochure is "not settled", which is not the same as unprotected.'
             + (' "Legacy" is yes or no as the definitions above decide it, and unknown where the lifecycle state is.' if legacy else ''), '',
             '| ' + ' | '.join(legacy + ['Lifecycle', 'Manufacturer', 'Model', 'What the documents establish', 'Encryption', 'Authentication', 'Integrity',
                                         'Mechanism', 'Most direct document read']) + ' |', '|---|---|---|---|---|---|---|---|---|' + '---|' * len(legacy)]
            + ['| ' + ''.join(f'{found.legacy_word(pid)} | ' for _ in legacy)
               + f"{found.lifecycle(pid)} | {md(products[pid].get('vendor', ''))} | {found.model(pid)} | {stance[stand[pid]]} | "
               + ' | '.join(BRIEF[bucket(pid, c)] for c in ('encryption', 'authentication', 'integrity'))
               + f" | {', '.join(title_of(c) + (' (conditional)' if bucket(pid, c) == 'conditional' else '') for c in MECHANISMS if bucket(pid, c) in POSITIVE) or '-'}"
               f" | {read[best[pid]].lower()} |" for pid in ordered])


def glance(found, folder):
    """The lines of the section and, in the folder, its charts with the data behind them."""
    figures = Figures(folder)
    described = catalogue(found, figures) + documents(found, figures) + mentions(found, figures)
    if found.rows:
        answered, stand = answer(found, figures)
        listed = device_by_device(found, stand, folder)
    else:
        answered = ['', 'No cell has been reviewed yet, so there is no result to draw. The charts below describe the catalogue and the documents; none of them says what a device can do.']
        listed = []
    if figures.data:
        dump(folder / 'data.json', figures.data)
    # Each number is in a table further down; the device-by-device table closes the section because it is the longest.
    return INTRO + answered + described + listed

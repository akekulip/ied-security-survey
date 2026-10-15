"""The report: REPORT.md from a run and its review, beside the data files it points to."""

import re
from collections import Counter
from pathlib import Path

from .vocabulary import VERSION, CAPABILITIES, INTERFACE_CLASSES, NOT_ASSESSED, PROPERTIES, life_words
from .store import load, dump, digest, now, SCRIPT_SHA256
from .text import clip
from .review import facts, named
from .findings import COLUMNS, DNP3_KINDS, POSITIVE, Findings, flat, md, words
from .tables import write_tables


# How a device's result for one property reads in the summary by stratum.
WORDING = (('supported', 'supported'), ('conditional', 'conditional'), ('gateway', 'via external gateway only'),
           ('explicitly_unsupported', 'explicitly unsupported'), ('silent', 'unknown: complete document silent'),
           ('conflict', 'unknown: sources conflict'), ('other', 'unknown: other interface only'),
           ('unknown', 'unknown'), (None, 'not reviewed'))
SETTLED, DOUBTS = ('supported', 'conditional', 'gateway', 'explicitly_unsupported'), ('silent', 'conflict', 'other', 'unknown')
TYPES = {'protective_relay': 'protective relay', 'controller_rtu': 'controller / RTU', 'plc': 'PLC', 'meter': 'meter'}


def opening(found):
    cfg, sources, totals = found.cfg, found.sources, found.totals
    line = (f"Products/families in seed inventory: {len(found.products)}. "
            f"Sources attempted: {len(sources) - totals['skipped'] - totals['login_required'] - totals['not_approved']}; "
            f"extracted: {totals['extracted']}; failed: {totals['failed']}")
    if totals['duplicate']:
        line += f"; duplicate of another source: {totals['duplicate']}"
    if totals['skipped']:
        line += f"; matched links not followed (page budget): {totals['skipped']}"
    if totals['not_approved']:
        line += f"; not held by an earlier run and not approved for a new request: {totals['not_approved']}"
    if totals['login_required']:
        line += f"; documents behind a sign-in, not requested: {sum(s.get('link_count', 1) for s in sources if s['status'] == 'login_required')}"
    return [f"# {cfg.get('title', 'IED security documentation survey')}", '',
            f"Sampling: {cfg['sampling']}", '', line + '.', '',
            'This measures documented capabilities, not enabled settings, installed-base coverage or plaintext '
            'prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. '
            'Capability categories overlap, so counts below are review cells and must not be added up as devices.', '',
            'Reviewers on record: ' + ('; '.join(f'{md(name)} ({n} rows)' for name, n in Counter(r['reviewer'] for r in found.rows).items()) or 'none') + '.', '',
            'Every capability has one of four results: supported, conditional, explicitly unsupported or unknown. An '
            'unknown says why where the review recorded it. "Complete document silent" means a complete manual, device '
            'profile or conformance statement was searched and does not mention the capability; it is not a vendor '
            'statement that the capability is absent.', '']


def definitions(found):
    defined, count = found.defined, len(found.products)
    if not found.grouped:
        return ['No definition of "legacy" or of the lifecycle groups is recorded in the config of this run, so no '
                'result is counted by lifecycle group.']
    fixed, revisions = defined.get('defined_at') or 'a date the config does not give', defined.get('revisions') or []
    return (['## Definitions', '',
             # A definition changed after results were seen is not one fixed before any count, and the report does not say it is.
             (f'First fixed on {fixed} and revised since. What follows is the definition in the config this run was '
              f'crawled with; each revision is listed with what had been counted when it was made.'
              if revisions else f'Fixed on {fixed} in the config this run was crawled with, before any result was '
                                f'counted.'), '',
             f"- Legacy: {flat(defined['legacy'])}"]
            + ([f"- Counted as legacy: {'; '.join(map(life_words, found.legacy))}."] if defined.get('legacy_statuses') else [])
            + [f"- {life_words(k).capitalize()}: {flat(v)}" for k, v in (defined.get('lifecycle_statuses') or {}).items()]
            + ([f"- Release date: {flat(defined['release_date'])}"] if defined.get('release_date') else [])
            + [f"- Revised on {flat(r['date'])}: {flat(r['change'])} What had been counted by then: "
               f"{flat(r['known_then'])}" for r in revisions]
            + ['', f'Legacy under this definition: {len(found.legacy_devices)} of {count} devices in this run. '
                   f'Lifecycle status rests on dated vendor evidence for {found.recorded} devices and is unknown for '
                   f'{count - found.recorded}.'])


def dnp3(found):
    """The survey's question: which devices document DNP3 security, of what kind, and which none, by lifecycle group."""
    members, products = found.dnp3, found.products
    if not members:
        return ['', '## DNP3 security', '', 'No retrieved document of a device in this run names DNP3.']

    group = found.lifecycle_group
    columns, total, tally = found.dnp3_counts()
    kinds = {pid: found.dnp3_security(pid) for pid in members}
    share = lambda n, of: f'{n} of {of} ({100 * n / of:.0f}%)' if of else '-'
    left_out = [pid for pid in products if found.dnp3_sources.get(pid) and pid not in members]
    text = (['', '## DNP3 security', '',
             'Catalogue entries whose own retrieved documents name DNP3, grouped by documented security. '
             'An entry without an applicable security finding remains unknown. Absence from the retrieved '
             'documents establishes neither lack of support nor plaintext operation. Authentication does not '
             'establish encryption, and an integrity-only statement does not establish authentication. '
             'DNP3 Secure Authentication version 5 (SAv5) provides authentication rather than payload confidentiality. '
             'Protection described for another or an unspecified control protocol is kept separate from '
             'DNP3-specific protection. These are unweighted sample counts, not vendor-wide estimates, '
             'installed-device settings or traffic measurements.', '']
            + ([f"Left out by the device notes, because DNP3 is named only in documents about other products: "
                f"{', '.join(found.model(p) for p in left_out)}.", ''] if left_out else [])
            + ['| DNP3 security documented | ' + ' | '.join(columns) + ' | Total |', '|---|' + '---|' * (len(columns) + 1)])
    for key, label in DNP3_KINDS:
        counts = [tally[key, c] for c in columns]
        if sum(counts) or key in ('tls', 'authenticated', 'none'):
            text.append(f'| {label} | ' + ' | '.join(share(n, total[c]) for n, c in zip(counts, columns))
                        + f' | {share(sum(counts), len(members))} |')
    text += ['| Devices whose documents name DNP3 | ' + ' | '.join(str(total[c]) for c in columns) + f' | {len(members)} |', '']
    legacy = ['Legacy'] * found.grouped
    text += ['| ' + ' | '.join(legacy + ['Lifecycle', 'Vendor', 'Model', 'Type', 'DNP3 security', 'Source']) + ' |',
             '|---|---|---|---|---|---|' + '---|' * len(legacy)]
    labels = dict(DNP3_KINDS)
    ranked = sorted(members, key=lambda p: ([k for k, _ in DNP3_KINDS].index(kinds[p][0]), columns.index(group(p)),
                                            products[p].get('vendor', ''), str(products[p].get('model') or p)))
    for pid in ranked:
        kind, rows = kinds[pid]
        where = found.dnp3_source(pid, rows)
        links = '; '.join(f'[{ref}{" " + loc if loc else ""}]({url})' for ref, loc, url, _ in where[:3])
        links += f' (+{len(where) - 3} more)' if len(where) > 3 else ''
        category = products[pid].get('category') or ''
        # A protection that needs a licence, a firmware version or a module says so.
        needs = '; '.join(dict.fromkeys(flat(r['conditions']) for r in rows if r['status'] == 'conditional' and r.get('conditions')))
        text.append('| ' + ''.join(f'{found.legacy_word(pid)} | ' for _ in legacy)
                    + f"{found.lifecycle(pid)} | {md(products[pid].get('vendor', ''))} | {found.model(pid)} | "
                      f"{md(TYPES.get(category, category.replace('_', ' ')))} | {labels[kind]}"
                      f"{md(' (conditional: ' + needs + ')') if needs else ''} | {md(links)} |")
    return text


def devices(found):
    products, bare = found.products, found.bare

    def dated(d):
        proof = d['lifecycle_evidence']
        if not proof:
            return 'none'
        e = proof[0]
        said = f'"{clip(flat(e["quote"]), 140)}"' if e.get('quote') else e.get('basis') or 'vendor source'
        return (f"{e['dated']}: {said} <{e.get('url') or found.byid[e['source_id']]['final_url']}>"
                + (f' (+{len(proof) - 1} more)' if len(proof) > 1 else ''))

    return (['', '## Devices', '',
             'Identity level says whether the entry is a product family, one model or one catalogue number. Lifecycle '
             'status rests only on what the vendor says in a dated source; the date is the one the vendor states or, '
             'failing that, the day the source was retrieved. Release date is recorded apart and decides nothing. Exact '
             'model, hardware revision and firmware are stated per finding below, as the cited document names them.', '']
            + ([f'{len(bare)} devices without a review row are left out of this table. devices.csv lists all '
                f'{len(products)} with their lifecycle evidence.', ''] if bare else [])
            + ['| Manufacturer | Model | Category | Identity level | Lifecycle status | Dated vendor evidence | Release '
               'date |', '|---|---|---|---|---|---|---|']
            + [f"| {md(products[pid].get('vendor', ''))} | {found.model(pid)} | {md(found.category(pid))} | "
               f"{d['identity_level'].replace('_', ' ') or 'not established'} | "
               f"{found.lifecycle(pid)}{' (vendor label: ' + md(d['vendor_label']) + ')' if d['vendor_label'] else ''} "
               f"| {md(dated(d))} | "
               f"{md(d['release_date'] or 'not established')} |" for pid, d in found.devices.items() if pid not in bare])


def summary(found):
    grouped = found.grouped
    text = ['', '## Summary by vendor, category and lifecycle' if grouped else '## Summary by vendor and category', '',
            'Devices, counted once each, by what the review established for a control protocol. "In the catalogue" is '
            'the number of classified entries in the vendor catalogue for that stratum, where the config was drawn from '
            'an inventory. A stratum with few devices in this run supports no generalisation.', '',
            '| Vendor | Category | Lifecycle | In the catalogue | In this run | ' + ' | '.join(f'{name.capitalize()} of a control protocol' for name in PROPERTIES) + ' |',
            '|---|---|---|---|---|' + '---|' * len(PROPERTIES)]
    strata, listed = {}, Counter()
    for x in found.cfg.get('frame') or []:
        listed[x['vendor'], x['category'], life_words(x['lifecycle']) if grouped else '-'] += x['in_catalogue']
    for pid, p in found.products.items():
        strata.setdefault((p.get('vendor', ''), found.category(pid), found.lifecycle(pid) if grouped else '-'), []).append(pid)
    for key in sorted(set(strata) | set(listed)):
        cells = []
        for feature in PROPERTIES:
            tally = Counter(found.bucket(pid, feature) for pid in strata.get(key, []))
            cells.append(', '.join(f'{tally[k]} {name}' for k, name in WORDING if tally[k]) or '-')
        text.append(f"| {md(key[0])} | {md(key[1])} | {key[2]} | {listed.get(key, '-')} | {len(strata.get(key, []))} | " + ' | '.join(cells) + ' |')
    return text


def interfaces(found):
    bare = found.bare

    def shown(row):
        quotes, parts = row['Evidence'], []
        if quotes:
            ref, where, text = quotes[0]
            parts.append(f'{ref} {where}: "{clip(text, 110)}"' + (f' (+{len(quotes) - 1} more)' if len(quotes) > 1 else ''))
        return '; '.join(parts + [row['Searched']] * bool(row['Searched'])) or 'none'

    return (['', '## Findings by product and interface', '',
             'One row per product and interface. Authentication, integrity and encryption are stated for that interface '
             'only; a result for a management interface says nothing about control traffic. "Evidence applies to" is '
             'the exact model, hardware revision and firmware the cited documents name. Default, activation and '
             'deployment are stated for supported and conditional findings. Full quotes are under "Findings and '
             'evidence" and in findings_table.csv; source references are resolved under "Sources examined".', '']
            + ([f'{len(bare)} products have no review row yet. They are left out of this table and counted as not '
                f'reviewed in the summary above.', ''] if bare else [])
            + ['| ' + ' | '.join(COLUMNS) + ' |', '|' + '---|' * len(COLUMNS)]
            + ['| ' + ' | '.join(md(shown(row) if c == 'Evidence' else row[c]) for c in COLUMNS) + ' |'
               for row in found.table if row['pid'] not in bare])


def counts(found):
    products, grouped = found.products, found.grouped
    text = ['', '## Counts by category and lifecycle group' if grouped else '## Counts by category', '',
            'Products, not leads or table rows. Each product is counted once per capability, under its most favourable '
            'documented result for a control protocol. Unknown is one result; the four columns after it say why. "Other '
            'interface only" means a result exists for a management or network interface but none for a control '
            'protocol. A capability reached only through an external gateway is counted apart and is not the device\'s '
            'own. The last column is the denominator.'
            + (' The same results are counted for every lifecycle group.' if grouped else ''), '',
            '| Category | Capability | Supported | Conditional | Via external gateway only | Explicitly unsupported | '
            'Unknown | of which complete document silent | of which sources conflict | of which other interface only | '
            'of which not enough evidence | Not reviewed | Products |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for stratum in dict.fromkeys(map(found.stratum_of, products)):
        members = [pid for pid in products if found.stratum_of(pid) == stratum]
        for c in CAPABILITIES:
            tally = Counter(found.bucket(pid, c) for pid in members)
            cells = [tally[k] for k in SETTLED] + [sum(tally[k] for k in DOUBTS)] + [tally[k] for k in DOUBTS] + [tally[None]]
            text.append(f'| {md(stratum)} | {c} | ' + ' | '.join(map(str, cells)) + f' | {len(members)} |')
    return text


def matrix(found):
    bare = found.bare
    return (['', '## Capability matrix', '',
             'S supported, C conditional, G only through an external gateway, X explicitly unsupported, ? unknown (?s a '
             'complete document was searched and is silent, ?c sources conflict), - not reviewed. A mark in parentheses '
             'is established only for a management or network interface, not for a control protocol.', '']
            + ([f'{len(bare)} products without a review row are left out; every cell of theirs is "not reviewed".', ''] if bare else [])
            + ['| Product | Category | ' + ' | '.join(CAPABILITIES) + ' |', '|---|---|' + '---|' * len(CAPABILITIES)]
            + [f'| {found.model(pid)} | {md(found.stratum_of(pid))} | ' + ' | '.join(found.matrix(pid, c) for c in CAPABILITIES) + ' |'
               for pid in found.products if pid not in bare])


def defaults(found):
    """How each supported or conditional capability ships and what switching it on takes, as far as the documents say."""
    stated = found.stated
    text = ['', '## Default configuration, activation and deployment', '',
            'Findings with a supported or conditional result, one per capability and interface. "Undocumented" means '
            'the documents read do not say whether the capability is on by default; "not assessed" means the reviewer '
            'has not looked yet. Neither means disabled.', '']
    if stated:
        text.extend(['| Capability | Findings | Default enabled | Default disabled | Default undocumented | Default not '
                     'assessed | Activation needs stated | Activation: none stated | Activation not assessed |',
                     '|---|---|---|---|---|---|---|---|---|'])
        for c in CAPABILITIES:
            mine = [facts(r) for r in stated if r['feature'] == c]
            if mine:
                d = Counter(f['default'] for f in mine)
                a = Counter('waiting' if f['needs'] == [NOT_ASSESSED] else 'none' if f['needs'] == ['none_stated'] else 'stated' for f in mine)
                text.append(f"| {c} | {len(mine)} | {d['enabled']} | {d['disabled']} | {d['undocumented']} | "
                            f"{d[NOT_ASSESSED]} | "
                            f"{a['stated']} | {a['none']} | {a['waiting']} |")
        text.append('')
    fielded = [r for r in found.rows if facts(r)['deployment'] != 'unknown']
    text.append((f'Deployment status is unknown for {len(stated) - sum(r in fielded for r in stated)} of {len(stated)} '
                 f'findings. ' if stated
                 else 'No supported or conditional finding is recorded yet. ')
                + 'Vendor documents show what a device can do, not what an operator has enabled, so enabled or disabled '
                  'in practice is recorded only where evidence from an installation is cited.')
    for r in fielded:
        proof = '; '.join(flat(', '.join(e[k] for k in ('kind', 'reference', 'date', 'scope'))) for e in r['deployment_evidence'])
        text.append(f"- {found.model(r['product_id'])}, {r['feature']} on "
                    f"{flat(r.get('interface') or 'no interface stated')}: {facts(r)['deployment']} ({proof})")
    return text


def evidence(found):
    """The scope and the quoted words next to each result, so a second reader can check them without the CSV."""
    if not found.claims:
        return []
    text = ['', '## Findings and evidence', '',
            'Every row that rests on cited sources: each result, and each unknown recorded because a complete document '
            'is silent or sources conflict. Quotes are verbatim from the cited location of the retained source.']
    for r in found.claims:
        text.extend(['', f"### {found.model(r['product_id'])}: {r['feature']} ({named(r)})", '',
                     f"- Interface: {flat(r['interface'])} ({r['interface_class'].replace('_', ' ')})"])
        text.extend(f'- {name}: {flat(r[key]).replace(NOT_ASSESSED, "not assessed")}' for name, key in
                    (('Protocol', 'protocol'), ('Model scope', 'model_scope'), ('Hardware revision', 'hardware_revision'),
                     ('Firmware', 'firmware'), ('Implementation', 'implementation'), ('Conditions', 'conditions'),
                     ('Location', 'location')) if r.get(key))
        if r['status'] in POSITIVE:
            f = facts(r)
            text.extend([f"- Support basis: {words(f['basis'])}", f"- Default configuration: {f['default'].replace('_', ' ')}",
                         f"- Activation: {words(f['needs'])}" + (f": {flat(r['activation_requirements'])}" if r.get('activation_requirements') else ''),
                         f"- Deployment: {f['deployment']}"])
        text.extend(f"- Evidence{'' if (e.get('about') or 'capability') == 'capability' else ' on ' + e['about']}, "
                    f'{e["location"]}: "{flat(e["quote"])}"' for e in r.get('evidence') or [])
        if id(r) in found.searched:
            text.append(f'- Searched: {found.searched[id(r)]}')
        text.extend(f"- Source: {found.cite[sid]} {found.byid[sid]['final_url']}" for sid in r['source_ids'])
        text.append(f"- Review status: {r.get('review_status') or 'draft'} ({flat(r['reviewer'])})")
    return text


def reviewed_rows(found):
    return (['', '## Reviewed rows', '', '| Product | Capability | Interface | Review result | Scope |', '|---|---|---|---|---|']
            + ['| ' + ' | '.join(md(x) for x in [found.model(r['product_id']), r['feature'], flat(r.get('interface') or '') or '-',
                                                 named(r), r['rationale']]) + ' |' for r in found.rows])


def unresolved(found):
    bare = found.bare
    left = {pid: [c for c in CAPABILITIES if not any(x in SETTLED for x in found.results(pid, c, INTERFACE_CLASSES))]
            for pid in found.products}
    return (['', '## Unresolved cells', '',
             f'{sum(map(len, left.values()))} of {found.expected} cells are unknown or not reviewed on every interface.', '']
            + ([f'This includes all {len(bare) * len(CAPABILITIES)} cells of the {len(bare)} products without a review '
                f'row, which are not listed one by one.', ''] if bare else [])
            + [f"- {found.model(pid)}: {', '.join(cells)}" for pid, cells in left.items() if cells and pid not in bare])


def profiles(found):
    read = [(s, load(found.run / (s['id'] + '.profile.json'))) for s in found.sources if s.get('profile_items')]
    if not read:
        return []
    return (['', '## Device profile statements', '',
             'Read by the tool from section 1.12, Security Parameters, of a DNP3 Device Profile. Marked options are '
             'detected by a heuristic and nothing in this table has been reviewed. A finding still needs a review row '
             'that quotes the item.', '',
             '| Product | Source | Item | Title | Options that appear marked | Location |', '|---|---|---|---|---|---|']
            + [f"| {found.model(s['product_id'])} | {s['ref']} | {i['item']} | {md(i['title'])} | "
               f"{md('; '.join(i['marked']) or 'none detected')} | {i['location']} |" for s, items in read for i in items])


def sources_read(found):
    products = found.products
    read = [s for s in found.sources if s['status'] == 'extracted']
    used = {sid for r in found.rows for sid in r['source_ids']}
    wide, text = len(read) > 60, []
    if wide:
        # What kind of document the survey rests on, per vendor, says more at this scale than a row per source.
        text.extend(['', '## What was read', '',
                     'Extracted sources by vendor and document type. A type marked "suggested" is the tool\'s guess '
                     'from the title, URL and opening text until a reviewer confirms it in the source notes. A vendor '
                     'whose sources are mostly product pages and brochures has little that can settle a capability '
                     'either way.', '',
                     '| Vendor | Document type | Sources | PDF pages |', '|---|---|---|---|'])
        kinds, pages = Counter(), Counter()
        for s in read:
            kind = s['document']['doc_type'] or (s['doc_type_suggested'] + ' (suggested)' if s.get('doc_type_suggested') else 'not established')
            key = (products[s['product_id']].get('vendor', ''), kind.replace('_', ' '))
            kinds[key] += 1
            pages[key] += s.get('pages') or 0
        text.extend(f'| {md(v)} | {kind} | {n} | {pages[v, kind] or "-"} |' for (v, kind), n in sorted(kinds.items()))
    text.extend(['', '## Sources examined', '',
                 'Type, number, revision and document date are what a reviewer confirmed or read off the document; "not '
                 'established" and "suggested" mean nobody has yet. Types are listed in the README from most to least '
                 'direct about what one product and firmware can do. Titles and PDF dates are what the file says about '
                 'itself, and a PDF creation date is not necessarily a publication date.', '']
                + ([f'Of {len(read)} extracted sources, the {len(used & {s["id"] for s in read})} cited by a review row '
                    f'are listed here. sources.json lists all of them.', ''] if wide else [])
                + ['| Ref | Product | Document | Type | Number and revision | Document date | Retrieved | SHA-256 | URL '
                   '|', '|---|---|---|---|---|---|---|---|---|'])
    for s in read:
        if not wide or s['id'] in used:
            made = re.match(r'D:(\d{4})(\d{2})(\d{2})', s.get('pdf_created', ''))
            said = [s.get('title') or 'untitled'] + ([f"{s['pages']} PDF pages"] if s.get('pages') else []) + (['PDF created ' + '-'.join(made.groups())] if made else [])
            doc = s['document']
            kind = doc['doc_type'] or ('suggested: ' + s['doc_type_suggested'] if s.get('doc_type_suggested') else 'not established')
            kind += f", {doc['coverage']}" if doc['coverage'] else ''
            text.append(f"| {s['ref']} | {found.model(s['product_id'])} | {md(', '.join(said))} | "
                        f"{kind.replace('_', ' ')} | "
                        f"{md(', '.join(filter(None, [doc['document_id'], doc['revision'] and 'revision ' + doc['revision']])) or 'not established')} "
                        f"| "
                        f"{md(doc['document_date'] or 'not established')} | {s.get('retrieved_at', '')[:10]} | "
                        f"{s['sha256']} | {md(s['final_url'])} |")
    return text


def sources_missing(found):
    products = found.products
    missing = [s for s in found.sources if s['status'] in ('failed', 'duplicate', 'login_required', 'not_approved')]
    if not missing:
        return []
    if len(missing) <= 40:
        return (['', '## Sources without extracted text', '', '| Product | URL | Outcome |', '|---|---|---|']
                + [f"| {found.model(s['product_id'])} | {md(s['url'])} | "
                   f"{md(s.get('error') or 'duplicate of ' + s['duplicate_of'])} |" for s in missing])
    # Too many to list one by one; sources.json has every URL. What matters here is how much each vendor withholds.
    kinds = Counter()
    for s in missing:
        kinds[products[s['product_id']].get('vendor', ''),
              'behind a sign-in, not requested' if s['status'] == 'login_required'
              else 'not approved for a new request, not requested' if s['status'] == 'not_approved'
              else 'duplicate of another source' if s['status'] == 'duplicate'
              else re.sub(r'https?://\S+', '<url>', s.get('error', ''))[:80]] += s.get('link_count', 1)
    return (['', '## Sources without extracted text', '',
             'Counted by vendor and outcome; every URL is in sources.json. "Sign-in" rows count links to documents that '
             'exist but are not public, so they were not requested.', '',
             '| Vendor | Outcome | Sources |', '|---|---|---|']
            + [f'| {md(v)} | {md(outcome)} | {n} |' for (v, outcome), n in sorted(kinds.items())])


def closing(found):
    rows = found.rows
    return (['', f'Review coverage: {len(found.reviewed)}/{found.expected} product–capability cells. Unreviewed cells '
                 f'carry no result.', '',
             f"Evidence quotes: {sum(bool(r.get('evidence')) for r in rows if r['status'] != 'unknown')} of "
             f"{sum(r['status'] != 'unknown' for r in rows)} rows with a result other than unknown carry a quote that "
             f"was checked against the cited passage.", '',
             f'Unknown because a complete document is silent: {len(found.searched)} rows, each checked to cite only '
             f'complete documents in which the search found no lead for that capability.', '',
             'See findings.csv for source URLs, hashes, interface, firmware and review provenance, and devices.csv for '
             'lifecycle evidence. The percentages in the DNP3 section are shares of the devices in this run, not of '
             'installed devices or of traffic.']
            + ([f"Re-bound rows: {sum(bool(r.get('rebound')) for r in rows)} rows were written against an earlier fetch "
                f"of the same documents and re-bound because the extracted text is unchanged; each row records the "
                f"hashes."] if any(r.get('rebound') for r in rows) else []))


# REPORT.md, top to bottom, after the opening and the definitions.
SECTIONS = (dnp3, devices, summary, interfaces, counts, matrix, defaults, evidence, reviewed_rows, unresolved, profiles, sources_read,
            sources_missing, closing)


REPORT_FILES = ('REPORT.md', 'findings.json', 'sources.json', 'evidence_index.json', 'candidate_counts.json', 'findings.csv',
                'findings_table.csv', 'devices.csv', 'dnp3.csv', 'dnp3_table.csv')


def confirmed(found):
    """The publication gate: every cell reviewed and every row confirmed by a person."""
    pending = [r for r in found.rows if r.get('review_status') != 'confirmed']
    if pending or found.blank or len(found.reviewed) != found.expected:
        raise ValueError(f'publication report requires confirmed review of every cell: '
                         f'{len(pending)} draft rows; {found.expected - len(found.reviewed)} unreviewed cells')


def report(run, review_path, dest, require_evidence=False, source_notes=None, device_notes=None, require_confirmed=False):
    require_evidence = require_evidence or require_confirmed
    found, dest = Findings(run, review_path, require_evidence, source_notes, device_notes), Path(dest)
    if require_confirmed:
        confirmed(found)
    dest.mkdir(parents=True, exist_ok=True)
    write_tables(found, dest)
    text = opening(found) + definitions(found)
    for section in SECTIONS:
        text += section(found)
    (dest / 'REPORT.md').write_text('\n'.join(text) + '\n', encoding='utf-8', newline='\n')
    report_manifest(found, review_path, source_notes, device_notes, dest, REPORT_FILES, require_evidence, require_confirmed)
    print(f'Report written to {dest}: {len(found.reviewed)} of {found.expected} cells reviewed in {len(found.rows)} '
          f'rows'
          + (f'; {found.blank} untouched template rows left out as not reviewed' if found.blank else ''))


def report_manifest(found, review_path, source_notes, device_notes, dest, outputs, require_evidence, require_confirmed,
                    receipt='report_manifest.json', schema='iedsurvey.report.v1'):
    """Bind generated outputs to their inputs without claiming unperformed raw-byte or deployment verification. Every
    output named must have been written: a receipt that silently leaves one out would vouch for less than it seems to."""
    from importlib.metadata import PackageNotFoundError, version

    missing = [n for n in outputs if not (dest / n).exists()]
    if missing:
        raise ValueError(f'expected output not written: {", ".join(missing)}')

    def record(path):
        path = Path(path)
        return {'path': str(path), 'sha256': digest(path.read_bytes())}

    inputs = {name: record(found.run / name) for name in
              ('manifest.json', 'config.json', 'sources.json', 'candidates.json', 'statement_leads.json') if (found.run / name).exists()}
    inputs['reviews'] = record(review_path)
    for name, path in [('source_notes', source_notes), ('device_notes', device_notes)]:
        if path:
            inputs[name] = record(path)
    inputs['extracted_segments'] = [record(found.run / (s['id'] + '.segments.json'))
                                   for s in found.sources if s['status'] == 'extracted']
    dependencies = {}
    for name in ('pypdf', 'cryptography', 'protego'):
        try:
            dependencies[name] = version(name)
        except PackageNotFoundError:
            dependencies[name] = 'not installed'
    dump(dest / receipt, {
        'schema_version': schema, 'created_at': now(), 'tool_version': VERSION,
        'script_sha256': SCRIPT_SHA256, 'dependencies': dependencies, 'inputs': inputs,
        'acceptance': {'require_evidence': require_evidence, 'require_confirmed': require_confirmed,
                       'draft_rows': sum(r.get('review_status') != 'confirmed' for r in found.rows),
                       'unreviewed_cells': found.expected - len(found.reviewed),
                       'raw_document_bytes_verified_by_report': False},
        'outputs': {n: digest((dest / n).read_bytes()) for n in outputs}})

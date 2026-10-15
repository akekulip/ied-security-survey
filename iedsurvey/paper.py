"""The paper's evidence from a run and its review, in one command: a summary, the DNP3 table, the LaTeX appendix and the
main-text paragraph, with a receipt. Every number is counted from the inputs when the command runs; nothing is typed in.
"""

import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from .findings import DNP3, DNP3_KINDS, Findings, flat, md
from .report import confirmed, dnp3, report_manifest
from .store import digest, load
from .tables import dnp3_table_csv

PAPER_FILES = ('summary.md', 'dnp3_table.csv', 'paper_appendix.tex', 'paragraph.tex')
DRAFT = 'AI draft; author review pending'
CONFIRMED = 'confirmed by the authors'
FEATURES = {'tls': 'TLS', 'ipsec': 'IPsec', 'ssh': 'SSH', 'cip_security': 'CIP Security',
            'dnp3_secure_authentication': 'DNP3 Secure Authentication'}


def feature(name):
    return FEATURES.get(name, name.replace('_', ' '))


SHORT_TYPES = {'protective_relay': 'relay', 'controller_rtu': 'contr./RTU', 'plc': 'PLC', 'meter': 'meter'}
SHORT_LIFE = {'currently_supported': 'listed', 'discontinued_support_not_stated': 'discontinued',
              'discontinued_supported': 'disc., supported', 'end_of_support': 'end of support', 'unknown': 'unknown'}
SHORT_SCOPE = {'built in': 'built in', 'separate device': 'separate', 'support basis not assessed': 'n.a.',
               'conditions apply': 'cond.'}


def compact(cell):
    """A property cell in a table column: yes, cond., no, via TLS, ? or --."""
    see = re.search(r'; see (\w+) \((supported|conditional)\)', cell)
    if see:
        return 'via ' + feature(see.group(1)).replace('DNP3 Secure Authentication', 'DNP3-SA')
    word = cell.split(':')[0].split(';')[0].strip()
    return {'supported': 'yes', 'conditional': 'cond.', 'explicitly unsupported': 'no', 'unknown': '?'}.get(word, '--')


def names_dnp3(r):
    return bool(DNP3.search(f"{r.get('interface', '')} {r.get('protocol', '')}"))


def tex(s):
    s = ' '.join(str(s).split()).replace('–', '--').replace('™', '').replace('®', '').replace('…', '...')
    for a, b in (('\\', '\x00'), ('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'),
                 ('}', r'\}'), ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}')):
        s = s.replace(a, b)
    return s.replace('\x00', r'\textbackslash{}')


def page(location):
    kind, _, n = location.partition(':')
    return f'p.~{n}' if kind == 'pdf-page' else f'web page, block {n}' if kind == 'html-block' else tex(location)


def result(cell):
    """A property cell in short: 'supported: TLS ...' is shown as 'supported'. A cell that only points to a mechanism
    finding ('not assessed; see tls (supported)') is kept whole, because the mechanism is not the property."""
    return cell if '; see ' in cell else cell.split(':')[0].strip()


# Titles some vendors' PDFs and pages carry that say nothing about the document.
GENERIC = re.compile(r'Disclaimer for all products|Keyvisual|Country Selector', re.I)


def title(s):
    found = (s.get('title') or '').split(' | ')[0].strip()
    if found and not GENERIC.search(found):
        return found
    m = re.search(r'/download/(\d+)/', s['final_url'])
    name = unquote(s['final_url'].rstrip('/').rsplit('/', 1)[-1])
    return f'SEL publication {m.group(1)}' if m else name if '.' in name else 'untitled document'


def vendor(found, pid):
    return found.products[pid].get('vendor', '').split(' / ')[0]


def gaps(found):
    """Why each DNP3 entry without an established finding has none: what was read, and what could not be obtained."""
    out = []
    for pid in found.dnp3:
        if found.dnp3_security(pid)[0] != 'none':
            continue
        mine = [s for s in found.sources if s['product_id'] == pid]
        missing = Counter()
        for s in mine:
            if s['status'] == 'login_required':
                missing['behind a sign-in'] += s.get('link_count', 1)
            elif s['status'] in ('failed', 'not_approved'):
                missing['not retrieved' if s['status'] == 'failed' else 'not approved for a new request'] += 1
            elif s['status'] == 'skipped':
                missing['beyond the page budget'] += 1
        read = [s for s in mine if s['status'] == 'extracted']
        out.append({'pid': pid, 'read': len(read), 'naming_dnp3': [found.refs[sid] for sid in found.dnp3_sources.get(pid, [])],
                    'missing': ', '.join(f'{n} {why}' for why, n in sorted(missing.items())) or 'none'})
    return out


def settings(found):
    """Statements of default, activation or conditions for the control protocols of the DNP3 entries, with the quote each
    rests on. Those naming DNP3 come first."""
    out = []
    for r in found.claims:
        if r['product_id'] in found.dnp3 and r['interface_class'] == 'control_protocol':
            for e in r.get('evidence') or []:
                if (e.get('about') or 'capability') in ('default', 'activation', 'conditions'):
                    out.append((r, e))
    out = sorted(out, key=lambda x: not names_dnp3(x[0]))
    # One quote can back several capabilities of one interface (TLS and encryption): it is listed once, naming them all.
    grouped = {}
    for r, e in out:
        key = (r['product_id'], flat(r['interface']), e['source_id'], e['location'], flat(e['quote']), e.get('about'))
        grouped.setdefault(key, (r, e, []))[2].append(feature(r['feature']))
    return [(r, e, ' and '.join(dict.fromkeys(names))) for r, e, names in grouped.values()]


def reviewed(status):
    """'draft (Claude AI draft ...); confirmed (A. Person)' in short: 'draft; confirmed'. The CSV keeps who."""
    return '; '.join(w for w in ('confirmed', 'draft', 'not reviewed') if re.search(rf'(^|; ){w}( \(|$)', status))


def summary(found, status, run_made):
    lines = ['# DNP3 security in public vendor documentation', '',
             f"Status: **{status}**. Run `{found.run.name}` (tool {run_made.get('tool_version')}, extraction rules "
             f"{run_made.get('extraction_version')}); {len(found.rows)} review rows, "
             f"{sum(r.get('review_status') == 'confirmed' for r in found.rows)} confirmed by a person.", '']
    lines += dnp3(found)[1:]
    lines += ['', '## The DNP3 table', '',
              'One line per catalogue entry and DNP3 interface, from the reviewed interface table. Authentication, '
              'integrity and encryption are separate results; protection documented for other interfaces is listed apart. '
              'Every column, with full quotes and hashes, is in `dnp3_table.csv`.', '',
              '| Vendor | Model | Lifecycle | Legacy | Authentication | Integrity | Encryption | Scope | Default | '
              'Security documented for other interfaces | Review |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
    for pid in found.dnp3:
        for t in found.dnp3_lines(pid):
            lines.append(f"| {md(vendor(found, pid))} | {found.model(pid)} | {t['Lifecycle']} | {t['Legacy']} | "
                         f"{md(result(t['Authentication']))} | {md(result(t['Integrity']))} | {md(result(t['Encryption']))} | "
                         f"{md(t['Scope'])} | {md(t['Default'])} | {md(t['Security documented for other interfaces'])} | "
                         f"{reviewed(t['Review status'])} |")
    unresolved = gaps(found)
    lines += ['', '## Unresolved evidence', '',
              f'{len(unresolved)} of {len(found.dnp3)} DNP3 entries have no established DNP3 security finding. Each stays '
              'unknown: neither unsupported nor plaintext.', '',
              '| Vendor | Model | Lifecycle | Documents read | Documents naming DNP3 | Not obtained |', '|---|---|---|---|---|---|']
    lines += [f"| {md(vendor(found, g['pid']))} | {found.model(g['pid'])} | {found.lifecycle(g['pid'])} | {g['read']} | "
              f"{', '.join(g['naming_dnp3']) or '-'} | {md(g['missing'])} |" for g in unresolved]
    lines += ['', '## Defaults, activation and conditions stated for the control protocols of the DNP3 entries', '',
              'Those naming DNP3 first. A statement about another protocol (for example IEC 61850 MMS) is not about DNP3.', '']
    lines += [f"- {found.model(r['product_id'])}, {md(flat(r['interface']))}, {md(names)}: "
              f"{e.get('about')}: \"{md(flat(e['quote']))}\" ({found.refs[e['source_id']]} {e['location']})"
              for r, e, names in settings(found)] or ['None stated in the reviewed evidence.']
    lines += ['', 'Deployment is unknown for every entry: no installation evidence was collected. These are counts of '
              'sampled catalogue entries, not of vendors, installed devices or network traffic.']
    return lines


def appendix(found, status, run_made, review_sha):
    cfg, products = found.cfg, found.products
    frame = sum(f.get('in_catalogue', 0) for f in cfg.get('frame', []))
    listed = (cfg.get('inventory') or {}).get('listed_at', '')[:10]
    vendors = sorted({vendor(found, pid) for pid in products})
    columns, total, tally = found.dnp3_counts()
    share = lambda n, of: f'{n} of {of} ({100 * n / of:.0f}\\%)' if of else '--'
    signin = sum(s.get('link_count', 1) for s in found.sources if s['status'] == 'login_required')
    added = sum(bool(s.get('approved_addition')) for s in found.sources)
    lines = [r'% Generated by `python survey.py paper`; do not edit by hand. Needs \usepackage{booktabs,tabularx,url}.',
             f"% Status: {status}. Run: {found.run.name} (tool {run_made.get('tool_version')}); review SHA-256 {review_sha[:16]}.", '',
             r'\section{Documentation survey of DNP3 security}\label{app:crawler}', '',
             r'\paragraph{Collection.} A crawler listed the protective relays, controllers and RTUs, PLCs and power meters in the '
             f'public online catalogues of {tex(", ".join(vendors[:-1]))} and {tex(vendors[-1])}'
             + (f' as of {listed}' if listed else '') + (f' ({frame} catalogue entries)' if frame else '')
             + r', with each entry\textquotesingle s lifecycle state taken from the vendor\textquotesingle s own wording. '
             + tex(cfg.get('sampling', '')) + f' The {len(products)} sampled entries were crawled within a fixed page '
             r'budget: product pages and the public data sheets, manuals and device profiles they link to'
             + (f', plus {added} official documents named in advance for entries the crawl had left unresolved' if added else '')
             + r'. Only public documents were read, robots.txt was honoured, and every document '
             r'is kept with its SHA-256 hash and retrieval time. ' + f'{found.totals["extracted"]} documents were read; '
             + f'{signin} linked documents sit behind a vendor sign-in and were not requested.', '',
             r'\paragraph{Review.} For each entry and capability a reviewer recorded supported, conditional, explicitly '
             r'unsupported or unknown per interface, keeping control protocols apart from management access, and separating '
             r'authentication, integrity and encryption. Every positive result quotes a passage that is checked against the '
             r'retained text. An unknown is never read as absence of the capability or as plaintext operation. '
             + (r'All rows were confirmed by the authors.' if status == CONFIRMED else
                r'The rows are an AI-assisted draft; the authors\textquotesingle{} confirmation is pending.'), '',
             r'\begin{table}[t]', r'\centering', r'\small',
             r'\caption{Sampled catalogue entries whose retrieved documents name DNP3, by the DNP3 security those documents '
             r'establish and by lifecycle group. Unweighted counts; not shares of vendors, installed devices or traffic.}',
             r'\label{tab:crawler-dnp3}', r'\begin{tabularx}{\linewidth}{@{}X' + 'r' * (len(columns) + 1) + '@{}}', r'\toprule',
             ' & ' + ' & '.join(tex(c) for c in columns) + r' & Total \\', r'\midrule']
    for key, label in DNP3_KINDS:
        counts = [tally[key, c] for c in columns]
        if sum(counts) or key in ('tls', 'authenticated', 'none'):
            lines.append(f'{tex(label)} & ' + ' & '.join(share(n, total[c]) for n, c in zip(counts, columns))
                         + f' & {share(sum(counts), len(found.dnp3))} ' + r'\\')
    lines += [r'\midrule', 'Entries & ' + ' & '.join(str(total[c]) for c in columns) + f' & {len(found.dnp3)} ' + r'\\',
              r'\bottomrule', r'\end{tabularx}', r'\end{table}', '']

    order = [k for k, _ in DNP3_KINDS]
    ranked = sorted(found.dnp3, key=lambda p: (order.index(found.dnp3_security(p)[0]), columns.index(found.lifecycle_group(p)),
                                               vendor(found, p), found.model(p)))
    evidence, keys = [], {}
    lines += [r'\begin{table*}[t]', r'\centering', r'\scriptsize',
              r'\caption{The ' + str(len(found.dnp3)) + r' DNP3 catalogue entries, ordered as in '
              r'Table~\ref{tab:crawler-dnp3}: the result for each property of DNP3 traffic and the passages it rests on '
              r'(E keys, listed below). yes: supported; cond.: conditional; no: stated as not provided; via X: mechanism X '
              r'documented, property not reviewed separately; ?: reviewed, unknown; --: not established. Scope: built in, '
              r'separate device, cond.\ (conditions apply) or n.a.\ (support basis not assessed). ``Other protocol'' '
              r'names control protocols with documented security that is not DNP3\textquotesingle s. Full wording, '
              r'conditions and hashes are in \texttt{dnp3\_table.csv}.}',
              r'\label{tab:crawler-dnp3-entries}', r'\begin{tabularx}{\linewidth}{@{}llXlccclX@{}}', r'\toprule',
              r'Vendor & Type & Entry & Lifecycle & Auth. & Integ. & Encr. & Scope & Sources or other protocol \\',
              r'\midrule']
    for pid in ranked:
        category = products[pid].get('category') or ''
        other = [t['Protocol / interface'].removesuffix(' (control protocol)') for t in found.table
                 if t['pid'] == pid and t['Interface class'] == 'control_protocol' and t['documented'] and not t['names_dnp3']]
        for t in found.dnp3_lines(pid):
            refs = []
            for item in t['Evidence']:
                if item not in keys:
                    keys[item] = f'E{len(keys) + 1}'
                    evidence.append(item)
                refs.append(keys[item])
            if t['names_dnp3']:
                scope = SHORT_SCOPE.get(t['Scope'].removeprefix('control protocol').strip(', '), '--')
                where = ', '.join(dict.fromkeys(refs)) or ('complete document searched' if t['Searched'] else '--')
            else:
                scope, where = '--', 'other protocol: ' + '; '.join(other) if other else 'documents name DNP3'
            lines.append(f"{tex(vendor(found, pid).split()[0])} & {tex(SHORT_TYPES.get(category, category.replace('_', ' ')))} & "
                         f"{tex(found.model(pid))} & {tex(SHORT_LIFE.get(found.devices[pid]['lifecycle_status'], t['Lifecycle']))} & "
                         f"{tex(compact(t['Authentication']))} & {tex(compact(t['Integrity']))} & {tex(compact(t['Encryption']))} & "
                         f"{tex(scope)} & {tex(where)} " + r'\\')
    lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table*}', '']
    if evidence:
        bysref = {s['ref']: s for s in found.sources if s.get('ref')}
        lines += [r'\paragraph{Evidence.} Verbatim passages behind Table~\ref{tab:crawler-dnp3-entries}, with document, '
                  r'page, retrieval date and the first 16 hexadecimal digits of the SHA-256 of the retrieved file.',
                  r'\begin{description}']
        for n, (ref, where, quote) in enumerate(evidence, 1):
            s = bysref[ref.split(' ')[0]]
            lines.append(rf"\item[E{n}] ``{tex(quote)}'' {tex(title(s))}, {page(where)}. Retrieved "
                         rf"{(s.get('retrieved_at') or '')[:10]}, SHA-256 \texttt{{{s['sha256'][:16]}}}. \url{{{s['final_url']}}}")
        lines += [r'\end{description}', '']
    stated = settings(found)
    if stated:
        lines += [r'\paragraph{Defaults, activation and conditions.} What the retrieved documents say about the control '
                  r'protocols of the DNP3 entries: how a protection is obtained or switched on, and its state as delivered. '
                  r'Those naming DNP3 come first; a statement about another protocol, such as IEC~61850 MMS, is not about '
                  r'DNP3.', r'\begin{description}']
        for n, (r, e, names) in enumerate(stated, 1):
            s = found.byid[e['source_id']]
            lines.append(rf"\item[C{n}] {tex(found.model(r['product_id']))}, {tex(r['interface'])}, {tex(names)} "
                         rf"({tex(e.get('about'))}): ``{tex(e['quote'])}'' {tex(title(s))}, {page(e['location'])}, "
                         rf"SHA-256 \texttt{{{s['sha256'][:16]}}}.")
        lines += [r'\end{description}', '']
    unresolved = gaps(found)
    lines += [r'\paragraph{Unresolved.} For ' + f'{len(unresolved)} of the {len(found.dnp3)}' + r' DNP3 entries the retrieved '
              r'documents establish no DNP3 security finding; each remains unknown. ' + '; '.join(
                  f"{tex(found.model(g['pid']))} ({g['read']} documents read; not obtained: {tex(g['missing'])})"
                  for g in unresolved) + '.' if unresolved else r'\paragraph{Unresolved.} None.', '']
    return lines


def paragraph(found, status):
    n = Counter(found.dnp3_security(pid)[0] for pid in found.dnp3)
    defaults = [(r, e) for r, e, _ in settings(found) if e.get('about') == 'default']
    signin = sum(1 for g in gaps(found) if 'sign-in' in g['missing'])
    vendors = len({vendor(found, pid) for pid in found.products})
    # Keep the paragraph's findings in the same order and vocabulary as the table.
    # One vocabulary for the table and paragraph: unknown scope/property must not become an absence claim in prose.
    said = [f'{n[key]} ({tex(label)})' for key, label in DNP3_KINDS if key != 'none' and n[key]]
    text = (f'% Generated by `python survey.py paper`; do not edit by hand. Status: {status}.\n'
            rf'To see what device documentation establishes about DNP3 security, we sampled {len(found.products)} '
            rf'catalogue entries of {vendors} IED vendors and read their public documents (Appendix~\ref{{app:crawler}}). '
            rf'Of the {len(found.dnp3)} entries whose documents name DNP3, the documented findings are '
            + ('; '.join(said) if said else 'none established')
            + '. ')
    text += (rf'For the remaining {n["none"]}, the retrieved documents establish no DNP3 security; this is unknown, '
             r'not evidence of plaintext operation'
             + (rf', and for {signin} of them some linked documents sit behind a vendor sign-in and were not read' if signin else '')
             + '. ' if n['none'] else '')
    text += (r'Capability, default and deployment are separate questions. A documented capability says nothing about '
             r'whether it is enabled')
    if defaults:
        r, e = defaults[0]
        default_entries = len({r['product_id'] for r, _ in defaults})
        text += (rf': the {tex(found.model(r["product_id"]))} documentation, for example, states that '
                 rf'{tex(feature(r["feature"]))} is disabled by default'
                 if r.get('default_state') == 'disabled'
                 else rf'; {default_entries} ' + ('entry documents' if default_entries == 1 else 'entries document')
                 + ' a default')
    text += (r'. Deployment we did not measure: these are counts of sampled catalogue entries, not of vendors, '
             r'installed devices or network traffic.')
    return [text]


def paper(run, review_path, dest, source_notes=None, device_notes=None, require_confirmed=False):
    """Writes the paper's evidence into a new folder. Without --require-confirmed every output says it is a draft."""
    found, dest = Findings(run, review_path, True, source_notes, device_notes), Path(dest)
    if require_confirmed:
        confirmed(found)
    status = CONFIRMED if require_confirmed else DRAFT
    run_made = load(found.run / 'manifest.json') if (found.run / 'manifest.json').exists() else {}
    review_sha = digest(Path(review_path).read_bytes())
    dest.mkdir(parents=True, exist_ok=False)
    dnp3_table_csv(found, dest / 'dnp3_table.csv')
    for name, lines in (('summary.md', summary(found, status, run_made)),
                        ('paper_appendix.tex', appendix(found, status, run_made, review_sha)),
                        ('paragraph.tex', paragraph(found, status))):
        (dest / name).write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    report_manifest(found, review_path, source_notes, device_notes, dest, PAPER_FILES, True, require_confirmed,
                    receipt='paper_manifest.json', schema='iedsurvey.paper.v1')
    print(f'Paper evidence written to {dest} ({status}): {len(found.dnp3)} DNP3 entries, '
          f'{sum(1 for _ in gaps(found))} without an established finding')

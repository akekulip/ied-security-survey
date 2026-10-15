"""The data files of a report: every row, source, quote and device as JSON or CSV, for whoever checks the Markdown."""

import csv
import json

from .store import dump
from .review import facts
from .findings import CSV_COLUMNS, DNP3_KINDS


FINDING_FIELDS = ['product_id','vendor','model','category','lifecycle_status','feature','status','unknown_reason','protocol','interface',
                  'interface_class','model_scope','hardware_revision','firmware','implementation','support_basis','conditions',
                  'default_state','activation_needs','activation_requirements','deployment_status','deployment_evidence',
                  'location','rationale','reviewer','reviewed_at','review_status','source_urls','source_hashes','evidence']
DEVICE_FIELDS = ['product_id', 'manufacturer', 'model', 'category', 'identity_level', 'lifecycle_status', 'legacy', 'vendor_label',
                 'lifecycle_evidence_date', 'lifecycle_evidence_quote', 'lifecycle_evidence_url', 'lifecycle_evidence_sha256',
                 'release_date', 'noted_by']


def evidence_index(found):
    byid = found.byid
    return [{'product_id': r['product_id'], 'feature': r['feature'], 'status': r['status'], 'interface': r.get('interface', ''),
             'interface_class': r.get('interface_class', ''), 'source_id': e['source_id'], 'source_ref': found.refs[e['source_id']],
             'doc_type': byid[e['source_id']]['document']['doc_type'],
             'url': byid[e['source_id']]['final_url'], 'sha256': byid[e['source_id']]['sha256'],
             'location': e['location'], 'quote': e['quote'], 'about': e.get('about') or 'capability',
             'retrieved_at': byid[e['source_id']].get('retrieved_at')}
            for r in found.rows for e in r.get('evidence') or []]


def findings_csv(found, path):
    """One line per reviewed row, with everything the reviewer recorded."""
    with path.open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=FINDING_FIELDS)
        w.writeheader()
        for r in found.rows:
            p = found.products[r['product_id']]
            item = {k: r.get(k, '') for k in FINDING_FIELDS}
            item.update({k: p.get(k, '') for k in ('vendor','model','category')},
                        lifecycle_status=found.devices[r['product_id']]['lifecycle_status'],
                        support_basis=' | '.join(facts(r)['basis']), default_state=facts(r)['default'],
                        activation_needs=' | '.join(facts(r)['needs']), deployment_status=facts(r)['deployment'],
                        deployment_evidence=json.dumps(r.get('deployment_evidence') or [], ensure_ascii=False))
            item['source_urls'] = ' | '.join(found.byid[s]['final_url'] for s in r['source_ids'])
            item['source_hashes'] = json.dumps(r['source_hashes'], sort_keys=True)
            item['evidence'] = json.dumps(r.get('evidence') or [], ensure_ascii=False)
            w.writerow(item)


def interfaces_csv(found, path):
    """The table of the report, one line per product and interface, with every quote in full."""
    with path.open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, extrasaction='ignore', fieldnames=list(CSV_COLUMNS))
        w.writeheader()
        for row in found.table:
            quotes = [f'{ref} {where}: "{text}"' for ref, where, text in row['Evidence']]
            w.writerow(dict(row, Evidence=' || '.join(quotes + [row['Searched']] * bool(row['Searched'])) or 'none'))


def devices_csv(found, path):
    """Every device of the run with the first piece of evidence for its lifecycle status."""
    with path.open('w', newline='', encoding='utf-8') as fp:
        w = csv.writer(fp)
        w.writerow(DEVICE_FIELDS)
        for pid, d in found.devices.items():
            p, e = found.products[pid], (d['lifecycle_evidence'] or [{}])[0]
            w.writerow([pid, p.get('vendor', ''), p.get('model') or pid, found.category(pid), d['identity_level'],
                        d['lifecycle_status'], found.legacy_word(pid), d['vendor_label'], e.get('dated', ''), e.get('quote') or e.get('basis', ''),
                        e.get('url') or (found.byid[e['source_id']]['final_url'] if e.get('source_id') else ''), e.get('sha256', ''),
                        d['release_date'], d['noted_by']])


DNP3_FIELDS = ['product_id', 'vendor', 'model', 'type', 'lifecycle_status', 'legacy', 'dnp3_security', 'dnp3_security_label',
               'evidence_quote', 'source_refs', 'source_locations', 'source_urls']


def dnp3_csv(found, path):
    """One line per DNP3 device: who it is, the DNP3 protection documented for it, and where to check."""
    labels = dict(DNP3_KINDS)
    with path.open('w', newline='', encoding='utf-8') as fp:
        w = csv.writer(fp)
        w.writerow(DNP3_FIELDS)
        for pid in found.dnp3:
            p, (kind, rows) = found.products[pid], found.dnp3_security(pid)
            where = found.dnp3_source(pid, rows)
            w.writerow([pid, p.get('vendor', ''), p.get('model') or pid, p.get('category', ''), found.devices[pid]['lifecycle_status'],
                        found.legacy_word(pid), kind, labels[kind], where[0][3] if where else '',
                        ' | '.join(x[0] for x in where), ' | '.join(x[1] for x in where), ' | '.join(x[2] for x in where)])


DNP3_TABLE_FIELDS = ['product_id', 'Manufacturer', 'Model', 'Category', 'Identity level', 'Lifecycle', 'Legacy',
                     'Protocol / interface', 'Authentication', 'Integrity', 'Encryption', 'Scope', 'Support conditions',
                     'Default', 'Activation', 'Evidence applies to', 'Evidence', 'Sources', 'Review status', 'DNP3 summary',
                     'Security documented for other interfaces']


def dnp3_table_csv(found, path):
    """The DNP3 table: one line per DNP3 catalogue entry and DNP3 interface, taken from the interface table."""
    with path.open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, extrasaction='ignore', fieldnames=DNP3_TABLE_FIELDS)
        w.writeheader()
        for pid in found.dnp3:
            for line in found.dnp3_lines(pid):
                quotes = [f'{ref} {where}: "{text}"' for ref, where, text in line['Evidence']]
                w.writerow(dict(line, product_id=pid, Evidence=' || '.join(quotes) or 'none'))


def write_tables(found, dest):
    dump(dest / 'findings.json', found.rows)
    dump(dest / 'sources.json', found.sources)
    dump(dest / 'evidence_index.json', evidence_index(found))
    dump(dest / 'candidate_counts.json', {p: {t: {'total': sum(c.values()), 'by_group': dict(sorted(c.items()))}
                                              for t, c in kinds.items()} for p, kinds in found.leads.items()})
    findings_csv(found, dest / 'findings.csv')
    interfaces_csv(found, dest / 'findings_table.csv')
    devices_csv(found, dest / 'devices.csv')
    dnp3_csv(found, dest / 'dnp3.csv')
    dnp3_table_csv(found, dest / 'dnp3_table.csv')

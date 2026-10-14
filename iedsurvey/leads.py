"""Places to read: keyword leads and DNP3 device-profile items. A lead is never a finding."""

import re

from .vocabulary import DENIALS, HYPOTHETICAL, LEADS, NEAR, lead_type
from .store import digest, dump, load
from .text import clip, norm, passage


def alias_pattern(aliases):
    if not aliases:
        return None
    return re.compile('(?<![A-Za-z0-9])(?:' + '|'.join(re.escape(a) for a in aliases) + ')(?![A-Za-z0-9])', re.I)


PROFILE_ITEM = re.compile(r'(?m)^[ \t]*(1\.12\.\d{1,2})[ \t]+(?=\S)')


# A leading X or a checked-box character. Vendors mark options in different ways, so this is a heuristic.
MARKED = re.compile(r'(?m)^[ \t]*(?:[Xx]|[\u2611\u2612\u2713\u2714])[ \t]+(\S.*?)[ \t]*$')


def profile_items(segments):
    """Section 1.12, Security Parameters, of a DNP3 Device Profile: one entry per numbered item, text kept whole."""
    opening = ' '.join(s['text'] for s in segments[:3])
    if not (re.search(r'device\s+profile', opening, re.I) and re.search(r'\bDNP', opening, re.I)):
        return []
    items = []
    for segment in segments:
        # The section heading repeats on each of its pages. The contents page has it too, followed by dot leaders.
        head = re.search(r'1\.12[ \t]+SECURITY[ \t]+PARAMETERS(?![ \t]*\.{3})', segment['text'], re.I)
        if not head:
            continue
        body = segment['text'][head.end():]
        starts = list(PROFILE_ITEM.finditer(body))
        carried = body[:starts[0].start()] if starts else body
        if items and carried.strip():  # An item that runs on from the previous page.
            items[-1]['raw'] += '\n' + carried
        for n, m in enumerate(starts):
            raw = body[m.end():starts[n + 1].start() if n + 1 < len(starts) else len(body)]
            items.append({'item': m[1], 'location': segment['location'], 'raw': raw})
    for item in items:
        raw = item.pop('raw')
        title = raw.split(':', 1)[0] if ':' in raw[:200] else raw.strip().split('\n', 1)[0]
        item.update(title=' '.join(title.split()), text=' '.join(raw.split()),
                    marked=[' '.join(x.split()) for x in MARKED.findall(raw)], marks='heuristic')
    return items


def candidates(source, segments, aliases=()):
    hits, alias = [], alias_pattern(aliases)
    texts = [norm(s['text']) for s in segments]
    for item in profile_items(segments):
        # The most direct statements a vendor makes about DNP3 security, so each item is a lead of its own.
        about = 'tls' if re.search(r'\bTLS\b|cipher|certificate', item['title'] + ' ' + item['text'], re.I) else 'dnp3_secure_authentication'
        hits.append({'id': digest((source['id'] + item['location'] + 'profile' + item['item']).encode())[:20],
                     'source_id': source['id'], 'product_id': source['product_id'], 'feature': about,
                     'lead_type': 'profile', 'location': item['location'], 'profile_item': item['item'],
                     'title': item['title'], 'matched': item['marked'], 'context': clip(norm(item['text']), 900),
                     'match_count': 1, 'status': 'unreviewed'})
    for i, segment in enumerate(segments):
        text = texts[i]
        for feature, pattern in LEADS.items():
            found = list(pattern.finditer(text))
            if feature in DENIALS:
                found = [m for m in found if not HYPOTHETICAL.search(text[max(0, m.start() - 80):m.start()])]
            if not found:
                continue
            if feature in NEAR:
                # An HTML block is one line, so the qualifying term may sit in a neighbouring block or the heading.
                block = segment['location'].startswith('html-block')
                around = ' '.join(texts[max(0, i - 3):i + 4] + [segment.get('heading', '')]) if block else text
                if not NEAR[feature].search(around):
                    continue
            match = found[0]
            cid = digest((source['id'] + segment['location'] + feature).encode())[:20]
            terms = {}
            for m in found:
                terms.setdefault(' '.join(m.group(0).split()).lower(), ' '.join(m.group(0).split()))
            hit = {'id': cid, 'source_id': source['id'], 'product_id': source['product_id'],
                   'feature': feature, 'lead_type': lead_type(feature), 'location': segment['location'],
                   # The words that matched, so SFTP is never read as an SSH statement nor VPN as IPsec.
                   'matched': list(terms.values())[:12],
                   'context': passage(text, match.start(), match.end()),
                   'match_count': len(found), 'status': 'unreviewed'}
            if segment['location'].startswith('html-block'):
                # A heading or table label alone decides nothing; its neighbours travel with it.
                hit['context_before'] = [clip(t) for t in texts[max(0, i - 2):i]]
                hit['context_after'] = [clip(t) for t in texts[i + 1:i + 3]]
            if segment.get('heading'):
                hit['heading'] = segment['heading']
            if alias:
                # A search aid for scope review, not proof that the passage applies to the model.
                hit['model_mentioned'] = bool(alias.search(text))
            hits.append(hit)
    return hits


def save_leads(out, hits):
    # Statements get their own file so nobody reads them as product capability leads.
    dump(out / 'candidates.json', [h for h in hits if h['lead_type'] != 'statement'])
    dump(out / 'statement_leads.json', [h for h in hits if h['lead_type'] == 'statement'])


def load_leads(run):
    return [h for name in ('candidates.json', 'statement_leads.json') if (run / name).exists() for h in load(run / name)]

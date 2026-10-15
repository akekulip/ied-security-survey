"""From response bytes to located text segments: HTML blocks and PDF pages, with what the document says about itself."""

import io
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from .text import norm, squash
from .fetch import header
from .store import digest


class PDFReuse:
    """Reuse a freshly extracted PDF within one run; keep only metadata and a checked on-disk segment reference."""

    def __init__(self, out):
        self.out, self.seen = Path(out), {}

    def parse(self, source, body):
        if digest(body) != source['sha256']:
            raise ValueError('source bytes hash mismatch before extraction: ' + source['id'])
        cached = self.seen.get(source['sha256'])
        if cached:
            path, expected, facts = cached
            raw = path.read_bytes()
            if digest(raw) != expected:
                raise ValueError('shared PDF segments changed: ' + str(path))
            return json.loads(raw), [], dict(facts)
        return parse(body, source['headers'])

    def remember(self, source, facts):
        if facts.get('kind') == 'pdf' and source['sha256'] not in self.seen:
            path = self.out / (source['id'] + '.segments.json')
            self.seen[source['sha256']] = (path, digest(path.read_bytes()), dict(facts))


# noscript is deliberately kept: it is the fallback a client without JavaScript, like this one, is meant to read.
SKIP = ('script', 'style', 'nav', 'footer', 'svg', 'select')


HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')


BLOCKS = HEADINGS + ('p', 'div', 'li', 'br', 'tr', 'table', 'dt', 'dd', 'pre', 'section', 'article', 'title')


INLINE = re.compile(r'display\s*:\s*inline', re.I)


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.links, self.skip, self.open = [], [], 0, []
        self.buf, self.kind, self.heading, self.title, self.anchor = [], None, '', '', None

    def flush(self):
        text = ' '.join(''.join(self.buf).split())
        self.buf = []
        if text:
            if self.kind == 'title' and not self.title:
                self.title = text
            if self.kind == 'heading':
                self.heading = text
            self.blocks.append((text, '' if self.kind else self.heading))

    def end_anchor(self):
        if self.anchor:
            self.links.append((self.anchor[0], ' '.join(''.join(self.anchor[1]).split())))
            self.anchor = None

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag == 'a':
            self.end_anchor()
            href = (dict(attrs).get('href') or '').strip()
            # Site-wide navigation links say nothing about the product on this page.
            if href and not self.skip:
                self.anchor = [href, []]
        if tag in ('td', 'th') and ''.join(self.buf).strip():
            self.buf.append(' | ')
        if tag in BLOCKS:
            # Some sites style a div as inline text. Breaking there cuts one sentence into several blocks.
            inline = tag not in HEADINGS + ('br', 'title') and bool(INLINE.search(dict(attrs).get('style') or ''))
            if tag != 'br':
                self.open.append((tag, inline))
            if not inline:
                self.flush()
                self.kind = 'heading' if tag in HEADINGS else 'title' if tag == 'title' else self.kind

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag == 'a':
            self.end_anchor()
        if tag in BLOCKS:
            inline = False
            for j in range(len(self.open) - 1, -1, -1):
                if self.open[j][0] == tag:
                    inline = self.open[j][1]
                    del self.open[j:]  # Also drops tags left unclosed inside this one.
                    break
            if not inline:
                self.flush()
                if tag in HEADINGS or tag == 'title':
                    self.kind = None

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)
            if self.anchor:
                self.anchor[1].append(data)


def outline(pdf):
    """Page index -> most recent bookmark at or before it. Bookmarks are optional and often malformed."""
    marks = []

    def walk(items):
        for item in items:
            if isinstance(item, list):
                walk(item)
            else:
                number = pdf.get_destination_page_number(item)
                if number is not None:
                    marks.append((number, ' '.join(str(item.title).split())))
    try:
        walk(pdf.outline)
    except Exception:
        return {}
    marks.sort(key=lambda m: m[0])
    titles, current, j = {}, '', 0
    for i in range(len(pdf.pages)):
        while j < len(marks) and marks[j][0] <= i:
            current, j = marks[j][1], j + 1
        if current:
            titles[i] = current
    return titles


MARKER = re.compile(r'date\s+code|publication\s+date|last\s+update|current\s+version|\brevision\b|\u00a9'
                    r'|copyright\s+(?:\(c\)|\d{4})', re.I)


def hints(segments):
    """Snippets around revision and date markers. Aids only: the reviewer decides what identifies the document."""
    found, keys = [], set()
    for i, segment in enumerate(segments):
        text = ' '.join(norm(segment['text']).split())
        for m in MARKER.finditer(text):
            key = text[m.start():m.end() + 24].lower()
            if key in keys:
                continue
            keys.add(key)
            snippet = text[max(0, m.start() - 60):m.end() + 60]
            # A table label and its value are often neighbouring blocks.
            if segment['location'].startswith('html-block') and not re.search(r'\w', text[m.end():]) and i + 1 < len(segments):
                snippet += ' ' + ' '.join(segments[i + 1]['text'].split())[:60]
            found.append(snippet)
            if len(found) == 8:
                return found
    return found


def parse(body, headers):
    """Segments, (href, anchor text) links and document facts for the source record."""
    if b'%PDF' in body[:1024]:
        from pypdf import PdfReader
        pdf = PdfReader(io.BytesIO(body))
        marks, segs, errors = outline(pdf), [], []
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text() or ''
            except Exception as e:  # One unreadable page must not hide the rest of a manual.
                text = ''
                errors.append({'location': f'pdf-page:{i + 1}', 'error': f'{type(e).__name__}: {e}'})
            segs.append({'location': f'pdf-page:{i + 1}', 'text': text, **({'heading': marks[i]} if i in marks else {})})
        facts = {'kind': 'pdf', 'pages': len(segs), 'empty_pages': sum(not s['text'].strip() for s in segs),
                 'page_errors': errors, 'encrypted': bool(pdf.is_encrypted)}
        try:
            meta = pdf.metadata or {}
            facts.update({k: ' '.join(str(meta[v]).split()) for k, v in
                          (('title', '/Title'), ('pdf_created', '/CreationDate'), ('pdf_modified', '/ModDate')) if v in meta})
        except Exception:
            pass
        return segs, [], dict(facts, document_hints=hints(segs))
    ct = header(headers, 'content-type')
    if 'html' not in ct.lower():
        raise ValueError('unsupported content type: ' + ct)
    charset = re.search(r'charset=([\w-]+)', ct)
    try:
        text = body.decode(charset[1] if charset else 'utf-8', 'replace')
    except LookupError:
        text = body.decode('utf-8', 'replace')
    page = TextHTML()
    page.feed(text)
    page.close()
    page.end_anchor()
    page.flush()
    segs = [{'location': f'html-block:{i + 1}', 'text': t, **({'heading': h} if h else {})}
            for i, (t, h) in enumerate(page.blocks)]
    return segs, page.links, {'kind': 'html', 'title': page.title, 'document_hints': hints(segs)}


def extract(body, headers):
    segs, links, _ = parse(body, headers)
    return segs, [href for href, _ in links]


def suggest_doc_type(title, url, segments):
    """A guess from the title, URL and opening text. A reviewer confirms the type in the source notes."""
    name = f'{title} {url}'
    opening = ' '.join(squash(s['text']) for s in segments[:3])[:3000]
    near = f'{name} {opening[:400]}'
    if re.search(r'device\s+profile', f'{name} {opening}', re.I) and re.search(r'\bDNP', f'{name} {opening}', re.I):
        return 'device_profile'
    if re.search(r'security\s+advisory|\bSSA-\d|\bICSA-\d', near, re.I):
        return 'advisory'
    if re.search(r'conformance\s+statement|\bPICS\b|\bPIXIT\b', near, re.I):
        return 'conformance_statement'
    if re.search(r'secur|hardening', near, re.I) and re.search(r'guide|white\s+paper|technique|hardening', near, re.I):
        return 'security_guide'
    if re.search(r'manual|user\s+guide|instruction|/docs?/', near, re.I):
        return 'manual'
    if re.search(r'data\s?sheet|brochure|flyer', near, re.I):
        return 'datasheet'
    return 'product_page' if segments and segments[0]['location'].startswith('html-block') else ''

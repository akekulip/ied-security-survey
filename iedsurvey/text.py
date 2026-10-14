"""Text normalisation for matching, and passages cut at sentence boundaries."""

import re
import unicodedata

from .store import digest


# Soft hyphens, zero-width characters and trademark signs vanish; typographic hyphens become '-'.
TIDY = {**dict.fromkeys(map(ord, '\u00ad\u200b\u200c\u200d\u2060\ufeff\u2122\u00ae\u2120')),
        **dict.fromkeys(map(ord, '\u2010\u2011\u2012\u2013\u2212'), '-')}


def norm(text):
    """Matching copy only: stored segment text stays exactly as extracted."""
    text = unicodedata.normalize('NFKC', text.translate(TIDY))  # Before NFKC, which would turn a trademark sign into "TM".
    return re.sub(r'([a-z])-[ \t]*\r?\n[ \t]*([a-z])', r'\1\2', text)


def squash(text):
    return ' '.join(norm(text).split())


def loose(text):
    # For matching a quote to its source: a hyphen at a PDF line break may or may not belong to the word,
    # so "self-signed", "self- signed" and "selfsigned" are treated as the same words.
    return re.sub(r'(?<=[a-z])-\s?(?=[a-z])', '', squash(text))


STOP = re.compile(r"""(?<=[.!?])(["')\]]*)\s+(?=[A-Z0-9"'(\[])""")


def passage(text, start, end, before=220, after=350, slack=240):
    """Window around a match, widened to sentence boundaries so a reviewer reads whole sentences."""
    a, b = max(0, start - before), min(len(text), end + after)
    head = tail = ''
    if a:
        earlier = [m.end() for m in STOP.finditer(text, max(0, a - slack), a)]
        later = [m.end() for m in STOP.finditer(text, a, start)]
        if earlier:
            a = earlier[-1]
        elif a - slack <= 0:
            a = 0
        elif later:
            a = later[0]
        else:
            head = '[...] '
    if b < len(text):
        later = [m.end(1) for m in STOP.finditer(text, b, min(len(text), b + slack))]
        earlier = [m.end(1) for m in STOP.finditer(text, end, b)]
        if later:
            b = later[0]
        elif b + slack >= len(text):
            b = len(text)
        elif earlier:
            b = earlier[-1]
        else:
            tail = ' [...]'
    return head + text[a:b].strip() + tail


def clip(text, limit=300):
    return text if len(text) <= limit else text[:limit].rsplit(' ', 1)[0] + ' [...]'


def text_digest(segments):
    # Stable across refetches of a dynamic page whose markup changes but whose wording does not.
    return digest('\n'.join(squash(s['text']) for s in segments if s['text'].strip()).encode())

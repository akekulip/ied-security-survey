"""Charts as plain SVG, written without a plotting library."""

from html import escape

from .text import clip


# Charts are plain SVG written by the tool itself, so a report needs nothing installed and every mark can be traced
# to a number. Colours follow Okabe and Ito, which stay apart under the common colour-vision deficiencies.
INK, MUTED, RULE = '#1f2328', '#59636e', '#d0d7de'


RESULT_SERIES = (('supported', 'Supported', '#009E73'), ('conditional', 'Conditional', '#56B4E9'),
                 ('gateway', 'Via external gateway only', '#CC79A7'), ('explicitly_unsupported', 'Explicitly unsupported', '#D55E00'),
                 ('silent', 'Unknown: complete document silent', '#E69F00'), ('conflict', 'Unknown: sources conflict', '#F0E442'),
                 ('other', 'Unknown here; a result exists for another interface', '#0072B2'),
                 ('unknown', 'Unknown: not enough evidence', '#8c959f'), (None, 'Not reviewed', '#e6e9ec'))


LIFECYCLE_SERIES = (('currently_supported', '#0072B2'), ('discontinued_supported', '#56B4E9'),
                    ('discontinued_support_not_stated', '#E69F00'), ('end_of_support', '#D55E00'), ('unknown', '#8c959f'))


DOCUMENT_SERIES = (('device_profile', 'DNP3 device profile', '#009E73'), ('conformance_statement', 'Conformance statement', '#56B4E9'),
                   ('security_guide', 'Security guide', '#CC79A7'), ('manual', 'Manual', '#0072B2'),
                   ('datasheet', 'Data sheet or brochure', '#E69F00'), ('other', 'Document of a type not yet established', '#8c959f'),
                   ('product_page', 'Product page only', '#b8c0c8'), ('advisory', 'Advisory', '#F0E442'), ('none', 'Nothing read', '#eef1f4'))


UNUSED_SERIES = (('sign_in', 'Behind a sign-in: links counted, not requested', '#D55E00'),
                 ('refused', 'Host or robots.txt does not allow it', '#CC79A7'),
                 ('unreadable', 'Fetched or tried, no text obtained', '#8c959f'),
                 ('skipped', 'Matched link not followed: page budget', '#e6e9ec'))


CYCLE = ('#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442', '#8c959f')


# One place per device: the strongest thing the reviewed documents establish about protecting its control traffic.
POSTURE_SERIES = (('encrypted', 'Encryption documented', '#009E73'),
                  ('authenticated', 'Authentication or integrity documented, encryption not', '#56B4E9'),
                  ('mechanism', 'A security mechanism is named, what it protects is not stated', '#0072B2'),
                  ('gateway', 'Only through an external gateway or encrypting device', '#CC79A7'),
                  ('denied', 'Vendor states it is not protected', '#D55E00'),
                  ('silent', 'A complete manual was read and documents none', '#E69F00'),
                  ('other', 'Documented for management access only, not for control traffic', '#F0E442'),
                  ('unknown', 'Not settled by the public documents', '#8c959f'), (None, 'Not reviewed', '#e6e9ec'))


NAMES = {'dnp3_secure_authentication': 'DNP3 Secure Authentication', 'tls': 'TLS', 'ipsec': 'IPsec', 'cip_security': 'CIP Security',
         'ssh': 'SSH', 'controller_rtu': 'Controller or RTU', 'plc': 'PLC'}


def title_of(key):
    return NAMES.get(key, str(key).replace('_', ' ').capitalize())


def wrap(text, width):
    lines, line = [], ''
    for word in str(text).split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f'{line} {word}'.strip()
    return lines + [line] * bool(line)


def svg_text(x, y, words, size=12, anchor='start', weight='normal', fill=INK):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">'
            f'{escape(str(words))}</text>')


def svg_frame(title, note, body, height, width):
    head = [svg_text(16, 27, title, 15, weight='600')] + [svg_text(16, 47 + 16 * i, t, 12, fill=MUTED) for i, t in enumerate(note)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height:.0f}" width="{width}" height="{height:.0f}" role="img" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif"><title>{escape(title)}</title><desc>{escape(" ".join(note))}</desc>'
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1:.0f}" rx="6" fill="#ffffff" stroke="{RULE}"/>'
            + ''.join(head + body) + '</svg>\n')


def pale(colour):
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b > 150


def svg_bars(title, note, rows, series, width=880):
    """Stacked horizontal bars. rows: [(label, {key: count})]; series: [(key, name, colour)] in stacking order."""
    note = [line for t in note for line in wrap(t, 135)]
    left, right, bar, gap = 250, 56, 20, 9
    body, x, y = [], 16, 47 + 16 * len(note) + 8
    for _, name, colour in series:
        w = 22 + 6.4 * len(name) + 16
        if x > 16 and x + w > width - 16:
            x, y = 16, y + 20
        body.append(f'<rect x="{x:.1f}" y="{y - 10}" width="12" height="12" rx="2" fill="{colour}" stroke="{RULE}"/>' + svg_text(x + 18, y, name))
        x += w
    y += 16
    scale = (width - left - right) / max([sum(v.get(k, 0) for k, _, _ in series) for _, v in rows if v is not None] + [1])
    for label, values in rows:
        if values is None:
            body.append(f'<line x1="16" y1="{y + 3}" x2="{width - 16}" y2="{y + 3}" stroke="{RULE}"/>' + svg_text(16, y + 19, label, 11, fill=MUTED))
            y += 28
            continue
        x = left
        body.append(svg_text(left - 10, y + bar - 6, clip(str(label), 38), anchor='end'))
        for key, name, colour in series:
            n = values.get(key, 0)
            if n:
                w = n * scale
                body.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bar}" fill="{colour}" stroke="#ffffff"><title>{escape(name)}: {n}</title></rect>')
                if w >= 7 * len(str(n)) + 6:
                    body.append(svg_text(x + w / 2, y + bar - 6, n, 11, 'middle', fill=INK if pale(colour) else '#ffffff'))
                x += w
        body.append(svg_text(x + 6, y + bar - 6, sum(values.get(k, 0) for k, _, _ in series), weight='600'))
        y += bar + gap
    return svg_frame(title, note, body, y + 6, width)


def svg_grid(title, note, rows, cols, cell, width=880):
    """A table of small counts, shaded by share. rows and cols: [(key, name)]; cell(row, col) gives (count, out of)."""
    note = [line for t in note for line in wrap(t, 135)]
    left, cw, ch = 250, (width - 250 - 16) / max(len(cols), 1), 26
    heads = [wrap(name, max(8, int(cw / 6.4)))[:2] for _, name in cols]
    top = 47 + 16 * len(note) + 14 + 13 * max([len(h) for h in heads] + [1])
    body = [svg_text(left + cw * (i + 0.5), top - 8 - 13 * (len(h) - 1 - j), line, 11, 'middle', fill=MUTED)
            for i, h in enumerate(heads) for j, line in enumerate(h)]
    for j, (rk, rname) in enumerate(rows):
        y = top + j * ch
        body.append(svg_text(left - 10, y + 17, rname, anchor='end'))
        for i, (ck, cname) in enumerate(cols):
            n, of = cell(rk, ck)
            share = n / of if of else 0
            shade = '#%02x%02x%02x' % tuple(round(255 + (c - 255) * share) for c in (0, 114, 178))
            body.append(f'<rect x="{left + i * cw + 1:.1f}" y="{y + 1}" width="{cw - 2:.1f}" height="{ch - 2}" fill="{shade}" stroke="{RULE}">'
                        f'<title>{escape(rname)}, {escape(cname)}: {n} of {of}</title></rect>'
                        + svg_text(left + (i + 0.5) * cw, y + 17, f'{n} of {of}' if of else '-', 11, 'middle', fill=INK if share < 0.55 else '#ffffff'))
    return svg_frame(title, note, body, top + len(rows) * ch + 10, width)

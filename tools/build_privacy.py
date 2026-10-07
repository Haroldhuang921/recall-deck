#!/usr/bin/env python3
"""Builds privacy/index.html from PRIVACY.md in the Recall Deck app project.

    python3 tools/build_privacy.py path/to/RecallDeck/PRIVACY.md

PRIVACY.md is the source of truth; this page is never edited by hand.
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = {'English': ('en', 'en'), '中文': ('zh', 'zh-Hans')}
EMAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {app}</title>
<meta name="description" content="{description}">
<link rel="icon" href="../icon.png">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<div class="wrap">
<header><a class="brand" href="../"><img class="icon" src="../icon.png" alt="" width="40" height="40">{app}</a></header>
<main>
<h1>{title}<span class="alt" lang="zh-Hans">{title_zh}</span></h1>
<p class="meta">{updated}</p>
<nav class="langs" aria-label="Language">{nav}</nav>
{sections}
</main>
</div>
</body>
</html>
"""


def inline(text):
    s = html.escape(text, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return EMAIL.sub(lambda m: f'<a href="mailto:{m[0]}">{m[0]}</a>', s)


def parse(md):
    """Reads the small Markdown subset PRIVACY.md uses."""
    title = updated = None
    sections = []  # (heading, [('p', text) | ('ul', [items])])
    for line in md.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('# '):
            title = line[2:]
        elif line.startswith('## '):
            sections.append((line[3:], []))
        elif not sections:
            m = re.fullmatch(r'_(.+)_', line)
            if not m:
                sys.exit(f'Unexpected line before the first section: {line}')
            updated = m[1]
        elif line.startswith('- '):
            blocks = sections[-1][1]
            if blocks and blocks[-1][0] == 'ul':
                blocks[-1][1].append(line[2:])
            else:
                blocks.append(('ul', [line[2:]]))
        else:
            sections[-1][1].append(('p', line))
    if not (title and updated and sections):
        sys.exit('PRIVACY.md needs a title, a "Last updated" line and sections.')
    return title, updated, sections


def render(md):
    title, updated, sections = parse(md)
    app, heading = title.split(' — ', 1)
    title_en, title_zh = heading.split(' / ', 1)
    nav, parts = [], []
    for name, blocks in sections:
        sid, lang = LANGS[name]
        nav.append(f'<a href="#{sid}" lang="{lang}">{html.escape(name)}</a>')
        out = [f'<section id="{sid}" lang="{lang}">', f'<h2>{html.escape(name)}</h2>']
        for i, (kind, content) in enumerate(blocks):
            if kind == 'ul':
                out += ['<ul>', *(f'<li>{inline(item)}</li>' for item in content), '</ul>']
            else:
                cls = ' class="lead"' if i == 0 else ' class="contact"' if i == len(blocks) - 1 else ''
                out.append(f'<p{cls}>{inline(content)}</p>')
        out.append('</section>')
        parts.append('\n'.join(out))
    first = next(text for kind, text in sections[0][1] if kind == 'p')
    return PAGE.format(
        app=html.escape(app),
        title=html.escape(title_en),
        title_zh=html.escape(title_zh),
        description=html.escape(first),
        updated=html.escape(updated),
        nav=' '.join(nav),
        sections='\n'.join(parts),
    )


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = render(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    out = ROOT / 'privacy' / 'index.html'
    out.write_text(page, encoding='utf-8')
    print(f'Wrote {out}')

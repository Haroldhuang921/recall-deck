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
<h1>{title}</h1>
<p class="meta">{updated}</p>
<section>
{body}
</section>
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
    """Reads the small Markdown subset PRIVACY.md uses: a title, an italic
    "Last updated" line, then paragraphs and one-level lists."""
    title = updated = None
    blocks = []  # ('p', text) | ('ul', [items])
    for line in md.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('# '):
            title = line[2:]
        elif line.startswith('#'):
            sys.exit(f'Subheadings are not supported: {line}')
        elif updated is None and re.fullmatch(r'_.+_', line):
            updated = line[1:-1]
        elif line.startswith('- '):
            if blocks and blocks[-1][0] == 'ul':
                blocks[-1][1].append(line[2:])
            else:
                blocks.append(('ul', [line[2:]]))
        else:
            blocks.append(('p', line))
    if not (title and updated and blocks):
        sys.exit('PRIVACY.md needs a title, a "Last updated" line and some text.')
    return title, updated, blocks


def render(md):
    title, updated, blocks = parse(md)
    app, heading = title.split(' — ', 1)
    body = []
    for i, (kind, content) in enumerate(blocks):
        if kind == 'ul':
            body += ['<ul>', *(f'<li>{inline(item)}</li>' for item in content), '</ul>']
        else:
            cls = ' class="lead"' if i == 0 else ' class="contact"' if i == len(blocks) - 1 else ''
            body.append(f'<p{cls}>{inline(content)}</p>')
    return PAGE.format(
        app=html.escape(app),
        title=html.escape(heading),
        description=html.escape(next(text for kind, text in blocks if kind == 'p')),
        updated=html.escape(updated),
        body='\n'.join(body),
    )


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = render(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    out = ROOT / 'privacy' / 'index.html'
    out.write_text(page, encoding='utf-8')
    print(f'Wrote {out}')

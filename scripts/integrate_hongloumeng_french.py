"""Small, reversible French links; never rewrites chapter bodies."""
from pathlib import Path
import re

START = '<!-- FRENCH-NAV:START -->'
END = '<!-- FRENCH-NAV:END -->'
NAMES = ('index.html', 'edition.html', *(f'ch{n:03}.html' for n in range(1, 81)))
TARGETS = tuple('classics/hongloumeng/' + d + n for d in ('', 'zh-hant/', 'en/', 'ja/') for n in NAMES)


def addition(relative):
    if relative not in TARGETS:
        raise ValueError('Outside French navigation scope')
    name = relative.rsplit('/', 1)[1]
    return START + f'<a lang="fr" href="/classics/hongloumeng/fr/{name}">Fran\u00e7ais</a>' + END


def transform(relative, text):
    block = addition(relative)
    if START in text or END in text:
        if text.count(block) == 1 and text.count(START) == text.count(END) == 1:
            return text
        raise ValueError('Malformed French navigation')
    match = re.search(r'<nav\b[^>]*class="language-switch"[^>]*>.*?</nav>', text, re.S)
    if not match:
        raise ValueError('Missing language switch: ' + relative)
    nav = match.group()
    # Keep the pre-existing reversible Japanese insertion intact.
    anchor = '<!-- JAPANESE-NAV:START -->' if '<!-- JAPANESE-NAV:START -->' in nav else '</nav>'
    return text[:match.start()] + nav.replace(anchor, block + anchor, 1) + text[match.end():]


def reverse(relative, text):
    block = addition(relative)
    if text.count(block) != 1:
        raise ValueError('Missing or modified French navigation')
    return text.replace(block, '', 1)


def navigation_outputs(prefix, pages):
    return {name: transform(prefix + name, value) if name.endswith('.html') else value
            for name, value in pages.items()}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    for name in TARGETS:
        path = root / name
        path.write_text(transform(name, path.read_text()))

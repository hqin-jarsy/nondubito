#!/usr/bin/env python3
"""Freeze current Chinese Action essays for independent language rewrites.

The original eleven essays live in HTML. Adversity already has an authoritative
Chinese/English JSON file: validate it, but never rewrite or extend its schema.
No web pages, language controllers, indexes or discovery records are written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'essays/action'
DATA = ROOT / 'data/action'
ORIGINAL_SLUGS = ('prequel', *(f'ep{i:02d}' for i in range(1, 10)), 'interface')
SLUGS = (*ORIGINAL_SLUGS, 'adversity')
EXPECTED_UNITS = dict(zip(SLUGS, (33, 37, 31, 31, 36, 26, 32, 33, 29, 29, 37, 38)))
EXPECTED_HEADINGS = dict(zip(SLUGS, (6, 6, 5, 6, 6, 5, 6, 6, 6, 6, 9, 3)))
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None] = field(default_factory=dict)
    children: list = field(default_factory=list)
    start: int = 0
    open_end: int = 0
    close_start: int = 0
    end: int = 0

    def has(self, *classes: str) -> bool:
        return set(classes).issubset((self.attrs.get('class') or '').split())

    def walk(self) -> Iterator[Node]:
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def text(self) -> str:
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)


class Document(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_offsets = [0]
        self.line_offsets.extend(m.end() for m in re.finditer('\n', source))
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(source)
        self.close()
        assert len(self.stack) == 1, 'Unclosed source HTML'

    def position(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.position()
        end = start + len(self.get_starttag_text())
        node = Node(tag, dict(attrs), start=start, open_end=end)
        self.stack[-1].children.append(node)
        if tag in VOID:
            node.close_start = node.end = end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.close_start = node.end = node.open_end

    def handle_endtag(self, tag):
        position = self.position()
        end = self.source.find('>', position) + 1
        assert self.stack[-1].tag == tag, ('Mismatched source HTML', tag, self.stack[-1].tag)
        node = self.stack.pop()
        node.close_start, node.end = position, end

    def handle_data(self, text):
        self.stack[-1].children.append(text)

    def raw(self, node: Node, inner=False) -> str:
        return self.source[node.open_end:node.close_start] if inner else self.source[node.start:node.end]


def one(nodes, predicate, label) -> Node:
    matches = [n for n in nodes if predicate(n)]
    assert len(matches) == 1, (label, len(matches))
    return matches[0]


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def inline(node: Node | str) -> str:
    if isinstance(node, str):
        return node
    text = ''.join(inline(c) for c in node.children)
    if node.tag in ('strong', 'b'):
        return '**' + text + '**'
    if node.tag in ('em', 'i'):
        return '*' + text + '*'
    if node.tag == 'a':
        href = node.attrs.get('href')
        return '[' + text + '](' + href + ')' if href else text
    if node.tag == 'br':
        return '\n'
    assert node.tag in ('p', 'h1', 'h2', 'span', 'div'), ('Unexpected inline tag', node.tag)
    return text


def units(document: Document, slug: str) -> tuple[Node, list[str]]:
    body = one(document.root.walk(), lambda n: n.tag == 'div' and n.has('essay-body', 'lang-zh'),
               (slug, 'Chinese body'))
    result = []
    for child in body.children:
        if isinstance(child, str):
            assert not child.strip(), (slug, 'Loose Chinese body text', child)
            continue
        assert child.tag in ('p', 'h2'), (slug, 'New block type requires deliberate handling', child.tag)
        text = normalize(inline(child))
        assert text, (slug, 'Empty source unit')
        result.append(('## ' if child.tag == 'h2' else '') + text)
        # Verify that inline markup handling did not drop or invent prose.
        assert normalize(re.sub(r'\*{1,2}', '', text)) == normalize(child.text()), (slug, text)
    assert len(result) == EXPECTED_UNITS[slug], (slug, len(result))
    assert sum(x.startswith('## ') for x in result) == EXPECTED_HEADINGS[slug], slug
    return body, result


def index_card(index: Document, slug: str) -> tuple[Node, Node, Node]:
    card = one(index.root.walk(),
               lambda n: n.tag == 'a' and n.has('entry-row')
               and n.attrs.get('href') == slug + '.html'
               and any(x.has('entry-title-zh') for x in n.walk()), (slug, 'Chinese index card'))
    title = one(card.walk(), lambda n: n.has('entry-title-zh'), (slug, 'Index title'))
    deck = one(card.walk(), lambda n: n.has('entry-desc'), (slug, 'Index deck'))
    return card, title, deck


def source_for(slug: str, index: Document) -> dict:
    path = DIRECTORY / (slug + '.html')
    document = Document(path.read_text(encoding='utf-8'))
    body, body_zh = units(document, slug)
    title = one(document.root.walk(), lambda n: n.tag == 'h1' and n.has('lang-zh'),
                (slug, 'Chinese title'))
    _, card_title, deck = index_card(index, slug)
    assert normalize(title.text()) == normalize(card_title.text()), (slug, 'Index title drift')
    citations = one(document.root.walk(), lambda n: n.has('method-citations'), (slug, 'Citations'))
    note = one(citations.walk(), lambda n: n.tag == 'p' and n.has('lang-zh'), (slug, 'Chinese citation'))
    paper = one(note.walk(), lambda n: n.tag == 'a' and (n.attrs.get('href') or '').startswith(
        'https://self-as-an-end.net/papers/sae-action-'), (slug, 'Source paper'))
    doi = one(note.walk(), lambda n: n.tag == 'a' and (n.attrs.get('href') or '').startswith(
        'https://doi.org/'), (slug, 'Source DOI'))
    expected_paper = 'prequel' if slug == 'prequel' else ('0' if slug == 'interface' else str(int(slug[2:])))
    assert paper.attrs['href'] == f'https://self-as-an-end.net/papers/sae-action-{expected_paper}.html', slug
    return {
        'slug': slug,
        'title_zh': normalize(title.text()),
        'deck_zh': normalize(inline(deck)),
        'body_zh': body_zh,
        'source_note_zh': normalize(inline(note)),
        'source_url': paper.attrs['href'],
        'source_doi': doi.attrs['href'].removeprefix('https://doi.org/'),
        'source_input': {
            'path': path.relative_to(ROOT).as_posix(),
            'chinese_body_sha256': sha(document.raw(body, inner=True)),
            'chinese_title_sha256': sha(document.raw(title)),
            'source_note_sha256': sha(document.raw(note)),
            'deck_input': {
                'path': 'essays/action/index.html',
                'locator': f'a.entry-row[href="{slug}.html"] .entry-desc, in the Chinese card',
                'sha256': sha(index.raw(deck)),
            },
            'normalization': 'Direct Chinese h2/p blocks in document order; strong/em preserved as Markdown; source links retained.',
        },
    }


def validate_adversity() -> dict:
    """Read the existing schema, verify its published Chinese, never modify it."""
    path = DATA / 'adversity.json'
    original_bytes = path.read_bytes()
    item = json.loads(original_bytes)
    assert item['slug'] == 'adversity'
    assert item['source_url'] == 'https://self-as-an-end.net/papers/sae-action-adversity.html'
    document = Document((DIRECTORY / 'adversity.html').read_text(encoding='utf-8'))
    _, body_zh = units(document, 'adversity')
    assert item['body_zh'] == body_zh, 'Adversity JSON differs from published Chinese'
    title = one(document.root.walk(), lambda n: n.tag == 'h1' and n.has('lang-zh'), 'Adversity title')
    deck = one(document.root.walk(), lambda n: n.tag == 'p' and n.has('lang-zh', 'adversity-deck'), 'Adversity deck')
    assert item['title_zh'] == normalize(title.text())
    assert item['deck_zh'] == normalize(deck.text())
    notes = one(document.root.walk(), lambda n: n.tag == 'details' and n.has('adversity-sources'), 'Adversity sources')
    links = {n.attrs.get('href') for n in notes.walk() if n.tag == 'a'}
    assert item['source_url'] in links and 'https://doi.org/' + item['source_doi'] in links
    assert {'https://www.gutenberg.org/cache/epub/23031/pg23031-images.html',
            'https://www.gutenberg.org/files/2397/2397-h/2397-h.htm'}.issubset(links)
    assert path.read_bytes() == original_bytes
    return item


def render() -> dict[Path, dict]:
    index = Document((DIRECTORY / 'index.html').read_text(encoding='utf-8'))
    result = {DATA / (slug + '.json'): source_for(slug, index) for slug in ORIGINAL_SLUGS}
    validate_adversity()
    assert DATA / 'adversity.json' not in result
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify the eleven normalized files without writing')
    args = parser.parse_args()
    adversity_before = (DATA / 'adversity.json').read_bytes()
    outputs = render()
    for path, item in outputs.items():
        serialized = json.dumps(item, ensure_ascii=False, indent=2) + '\n'
        if args.check:
            assert path.read_text(encoding='utf-8') == serialized, ('Stale normalized source', path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(serialized, encoding='utf-8')
        print(f'{item["slug"]}: {item["title_zh"]} — {len(item["body_zh"])} units — {item["source_url"]}')
    assert (DATA / 'adversity.json').read_bytes() == adversity_before, 'Protected adversity JSON changed'
    print('adversity: validated existing JSON and source links; schema and bytes unchanged (38 units)')
    print(('Checked' if args.check else 'Prepared') + ' 11 normalized Chinese sources; 12 essays / 392 units in total')


if __name__ == '__main__':
    main()

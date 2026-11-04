"""Read the existing edited Markdown and original Zhuangzi source apparatus.

No parallel Chinese corpus: paragraph boundaries follow the production Chinese
renderer, never the length of a new foreign paragraph. Bibliography and special
editorial cautions come from the actual original builder, not a copied table.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import build_zhuangzi as original
from prepare_action_sources import Document, Node, normalize, one

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/zhuangzi'
ORIGIN = 'https://nondubito.net/essays/zhuangzi/'


def chinese(node):
    """Extract only Chinese from the original tri() tree, retaining all links."""
    if isinstance(node, str):
        return node
    if node.has('lang-en') or node.has('lang-hant'):
        return ''
    text = ''.join(chinese(c) for c in node.children)
    if node.tag == 'a':
        href = node.attrs.get('href')
        assert href and text.strip(), 'Empty original source link'
        return '['+text+']('+urljoin(ORIGIN, href)+')'
    if node.tag == 'br':
        return '\n'
    assert node.tag in ('p', 'h2', 'span', 'li'), ('Unhandled source inline', node.tag)
    return text


def reading_units(raw):
    """Use the actual original Chinese p/h2/blockquote boundaries."""
    document = Document(original.prose(raw, 'zh'))
    result = []
    for node in document.root.children:
        if isinstance(node, str):
            assert not node.strip()
            continue
        assert node.tag in ('p', 'h2', 'blockquote'), ('New reading block', node.tag)
        assert not node.attrs, 'New source block attributes require review'
        if node.tag == 'blockquote':
            children = [c for c in node.children if isinstance(c, Node)]
            assert len(children) == 1 and children[0].tag == 'p'
            assert all(not c.strip() for c in node.children if isinstance(c, str))
            node_text = children[0].text()
            prefix = '> '
        else:
            assert all(isinstance(c, str) for c in node.children), 'New inline reading markup'
            node_text = node.text()
            prefix = '## ' if node.tag == 'h2' else ''
        # Keep a single quoted passage's original internal line breaks (notably
        # essay05); they do not become extra source units.
        value = node_text.strip() if node.tag == 'blockquote' else normalize(node_text)
        assert value and not re.search(r'\*|\]\(|<|>', value), 'New reading syntax needs deliberate handling'
        result.append(prefix+value)
    assert result
    return result


def load_article(spec, slug):
    assert spec['directory'] == 'essays/zhuangzi'
    assert slug == 'guide' or re.fullmatch(r'(0[1-9]|[1-5][0-9]|6[0-7])', slug)
    n = 0 if slug == 'guide' else int(slug)
    manifest = json.loads((BASE/'manifest.json').read_text())
    assert [a['number'] for a in manifest['items']] == list(range(68))
    assert manifest['published'] == list(range(68)), 'Publication scope changed'
    item = manifest['items'][n]
    assert original.filename(n) == slug+'.html'
    raw = (BASE/'zh'/f'{n:02d}.md').read_text()
    units = reading_units(raw)
    # Rendering only the existing primary edition in memory obtains the actual
    # source apparatus; it does not render or approve a new foreign edition.
    document = Document(original.render_article(item, manifest))
    body = one(document.root.walk(), lambda a: a.tag == 'article'
               and a.has('essay-body', 'lang-zh'), (slug, 'original Chinese body'))
    assert document.raw(body, inner=True) == original.prose(raw, 'zh')
    apparatus = one(document.root.walk(), lambda a: a.tag == 'aside'
                    and a.has('zz-source' if n else 'zz-research'), (slug, 'original source apparatus'))
    # Every direct block must have an explicit disposition. Merely selecting p
    # would silently omit a future wrapper containing a new explanatory note.
    headings = lists = standalone_links = 0
    for block in apparatus.children:
        if isinstance(block, str):
            assert not block.strip(), (slug, 'Loose source-apparatus text')
            continue
        assert block.tag in ('p', 'h2', 'ul', 'a'), (slug, 'New source-apparatus block', block.tag)
        if block.tag == 'h2':
            headings += 1
            assert n == 0 and normalize(chinese(block)) == '想读得更深', 'New source-apparatus heading'
        elif block.tag == 'ul':
            lists += 1
            assert n == 0, 'New source-apparatus list'
            for li in block.children:
                if isinstance(li, str):
                    assert not li.strip()
                    continue
                assert li.tag == 'li'
                children = [c for c in li.children if isinstance(c, Node)]
                assert len(children) == 1 and children[0].tag == 'a', 'New prose in research bibliography'
                assert all(not c.strip() for c in li.children if isinstance(c, str)), 'Loose bibliography prose'
        elif block.tag == 'a':
            standalone_links += 1
            assert n and block.attrs.get('href') == 'index.html#research', 'New standalone source route'
    assert (headings, lists, standalone_links) == ((1, 1, 0) if not n else (0, 0, 1))
    notes = [normalize(chinese(a)) for a in apparatus.children
             if isinstance(a, Node) and a.tag == 'p']
    assert notes and all(notes)
    sources = []
    for link in apparatus.walk():
        if link.tag != 'a':
            continue
        title = ''.join(chinese(c) for c in link.children)
        url = urljoin(ORIGIN, link.attrs['href'])
        assert title.strip() and url.startswith('https://')
        sources.append({'title': normalize(title), 'url': url})
    assert sources
    return {'slug': slug, 'title_zh': item['zh_title'],
            'deck_zh': item['zh_title']+'。从故事与细节出发，重新看见人与人之间留给彼此的空间。',
            'body_zh': units, 'aside_zh': None, 'notes_zh': notes,
            'sources_zh': sources, 'source_url': ORIGIN+slug+'.html',
            'group': item['group'], 'publication_date': item.get('publication_date', manifest['publication_date'])}


def source_digest(spec, slug):
    """Protect raw editorial source bytes and the actual complete apparatus."""
    n = 0 if slug == 'guide' else int(slug)
    raw = (BASE/'zh'/f'{n:02d}.md').read_bytes()
    manifest = (BASE/'manifest.json').read_bytes()
    bundle = json.dumps(load_article(spec, slug), ensure_ascii=False, sort_keys=True).encode()
    value = b'zhuangzi-edited-source\0'+len(raw).to_bytes(8, 'big')+raw
    value += len(manifest).to_bytes(8, 'big')+manifest+bundle
    return hashlib.sha256(value).hexdigest()

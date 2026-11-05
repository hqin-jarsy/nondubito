"""Read the published complete Chinese fairy-tale essays directly.

The old importer and its abbreviated English paragraphs are not the canonical
source.  Bibliographic URLs stay structured, not round-tripped through Markdown.
This module never writes pages or copies source prose into parallel JSON files.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

from prepare_action_sources import Document, Node, normalize, one

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'essays/everyday/stories/fairy-tales'
EXPECTED_UNITS = (18,24,20,20,23,22,20,20,20,19,20,20,20,20,20,
                  20,21,18,21,21,21,21,22,22,22,23,23,11,12,11)


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def prose_inline(node):
    """Retain emphasis, but never hide a bibliography href in Markdown text."""
    if isinstance(node, str):
        return node
    assert node.tag in ('p', 'em', 'i', 'strong', 'b', 'span', 'br'), node.tag
    if node.tag == 'br':
        return '\n'
    value = ''.join(prose_inline(c) for c in node.children)
    if node.tag in ('strong', 'b'):
        return '**' + value + '**'
    if node.tag in ('em', 'i'):
        return '*' + value + '*'
    return value


def _directory(spec):
    directory = spec.get('directory', DIRECTORY) if spec else DIRECTORY
    assert directory == DIRECTORY, directory
    return ROOT / directory


@lru_cache(maxsize=4)
def _index(text):
    doc = Document(text)
    local = one(doc.root.walk(), lambda n:n.has('lang-zh', 'local'), 'Chinese index')
    hero = one(local.walk(), lambda n:n.has('story-hero'), 'index hero')
    route = one(local.walk(), lambda n:n.has('reading-route'), 'six entry doors')
    groups, cards = [], []
    for section in (n for n in local.children if isinstance(n, Node) and n.has('chapter')):
        heading = one(section.walk(), lambda n:n.has('chapter-head'), 'chapter head')
        group_cards = []
        for card in (n for n in section.walk() if n.tag == 'a' and n.has('essay-card')):
            href = card.attrs['href']
            assert re.fullmatch(r'\d{2}-[a-z0-9-]+\.html', href), href
            row = {'slug':href[:-5],
                   'title_zh':normalize(one(card.walk(),lambda n:n.tag=='h3','card title').text()),
                   'deck_zh':normalize(one(card.walk(),lambda n:n.tag=='p','card deck').text())}
            cards.append(row)
            group_cards.append(row['slug'])
        groups.append({'title_zh':normalize(one(heading.walk(),lambda n:n.tag=='h2','group title').text()),
                       'slugs':group_cards})
    assert len(cards) == 30 and len({c['slug'] for c in cards}) == 30
    assert [int(c['slug'][:2]) for c in cards] == list(range(1,31))
    assert [len(g['slugs']) for g in groups] == [6,4,6,6,5,3]
    entries = [n.attrs['href'][:-5] for n in route.walk() if n.tag=='a']
    assert entries == [cards[i-1]['slug'] for i in (1,2,5,10,18,26)]
    return {'title_zh':normalize(one(hero.walk(),lambda n:n.tag=='h1','series title').text()),
            'deck_zh':normalize(one(hero.walk(),lambda n:n.has('story-deck'),'series deck').text()),
            'count_label_zh':normalize(one(hero.walk(),lambda n:n.has('story-meta'),'series metadata').text()),
            'route_title_zh':normalize(one(route.walk(),lambda n:n.tag=='h2','entry title').text()),
            'route_note_zh':normalize(one(route.walk(),lambda n:n.tag=='p','entry note').text()),
            'entry_slugs':entries, 'groups':groups, 'cards':cards,
            'source_input':{'path':DIRECTORY+'/index.html', 'raw_sha256':sha(text)}}


def load_index(spec=None):
    return copy.deepcopy(_index((_directory(spec)/'index.html').read_text()))


@lru_cache(maxsize=64)
def _article(text, index_text, slug):
    index = _index(index_text)
    card = one(index['cards'],lambda n:n['slug']==slug,'canonical index card')
    number = index['cards'].index(card)
    doc = Document(text)
    local = one(doc.root.walk(),lambda n:n.has('lang-zh','local'),(slug,'Chinese reading mode'))
    head = one(local.walk(),lambda n:n.has('article-head'),(slug,'article heading'))
    title = normalize(one(head.walk(),lambda n:n.tag=='h1','article title').text())
    assert title == card['title_zh'], (slug,'title differs from index')
    body = one(local.walk(),lambda n:n.has('article-body'),(slug,'complete Chinese body'))
    nodes = []
    for child in body.children:
        if isinstance(child,str):
            assert not child.strip(), (slug,'loose body text')
            continue
        assert child.tag == 'p', (slug,'unhandled body block',child.tag)
        nodes.append(child)
    note = nodes[-1]
    assert len(note.children)==1 and isinstance(note.children[0],Node) and note.children[0].tag=='em', (slug,'final selected-version note')
    assert len(nodes)-1 == EXPECTED_UNITS[number], (slug,'changed argument boundaries')
    units = [normalize(prose_inline(p)) for p in nodes[:-1]]
    for node,unit in zip(nodes[:-1],units):
        assert unit and normalize(unit.replace('*','')) == normalize(node.text()), (slug,'inline loss')
    # Visible note prose remains complete; its anchors are independently typed.
    note_text = normalize(note.text())
    assert note_text, (slug,'lost edition limitation')
    sources = [{'title':normalize(n.text()),'url':n.attrs['href']}
               for n in note.walk() if n.tag=='a']
    assert len(sources) in (1,2)
    assert all(s['title'] and s['url'].startswith(('https://','http://')) for s in sources)
    assert all(s['url'].count('(')==s['url'].count(')') for s in sources), (slug,'truncated source parentheses')
    door = one(local.walk(),lambda n:n.has('entry-door'),(slug,'reader routes'))
    door_links = [{'title':normalize(n.text()),'url':n.attrs['href']}
                  for n in door.walk() if n.tag=='a']
    assert [s['url'] for s in door_links] == ['../index.html','../../../../start.html']
    hant = one(doc.root.walk(),lambda n:n.has('lang-hant','local'),(slug,'complete Traditional reading mode'))
    return {'slug':slug,'title_zh':title,'deck_zh':card['deck_zh'],
            'kicker_zh':normalize(one(head.walk(),lambda n:n.has('chapter-label'),'work label').text()),
            'body_zh':units,'aside_zh':None,
            'notes_zh':[note_text], 'selection_note_zh':note_text,
            'source_note_zh':note_text,'sources_zh':sources,'source_url':sources[0]['url'],
            'entry_door_zh':normalize(door.text()),'entry_routes':door_links,
            'source_input':{'path':DIRECTORY+'/'+slug+'.html',
                            'chinese_reading_sha256':sha(doc.raw(local)),
                            'traditional_reading_sha256':sha(doc.raw(hant)),
                            'chinese_argument_sha256':sha(''.join(doc.raw(n) for n in nodes[:-1])),
                            'chinese_selected_note_sha256':sha(doc.raw(note)),
                            'index_path':DIRECTORY+'/index.html',
                            'chinese_card_sha256':sha(json.dumps(card,ensure_ascii=False,sort_keys=True))}}


def load_article(spec, slug):
    directory = _directory(spec)
    index_text = (directory/'index.html').read_text()
    slugs = [c['slug'] for c in _index(index_text)['cards']]
    if spec and spec.get('slugs') is not None:
        assert spec['slugs'] == slugs, 'profile order differs from canonical index'
    assert slug in slugs, slug
    return copy.deepcopy(_article((directory/(slug+'.html')).read_text(),index_text,slug))


def index_context(spec):
    source = load_index(spec)
    return [source['deck_zh'], source['route_note_zh']]


def source_digest(spec, slug):
    """Protect the canonical bundle, not mutable old English or new controls."""
    return sha(json.dumps(load_article(spec,slug),ensure_ascii=False,sort_keys=True))


def apparatus_inline(text, sources):
    """Only this series' exact structured references may appear in its notes.

    Do not send parenthesized historical URLs through the generic old regex.
    Keep inline wording/emphasis and the complete balanced destination together.
    """
    import html
    from import_fairy_tales import markdown_links
    from full_series_languages import inline_markdown
    allowed={s['url'] for s in sources}
    parts=[];position=0
    for start,end,label,url in markdown_links(text):
        assert url in allowed, ('Unknown fairy-tale note reference',url)
        prefix=text[position:start]
        assert '](' not in prefix, 'Unbalanced source link before a valid fairy-tale note reference'
        parts.append(inline_markdown(prefix))
        parts.append('<a href="'+html.escape(url,quote=True)+'">'+inline_markdown(label)+'</a>')
        position=end
    tail=text[position:]
    assert '](' not in tail, 'Unbalanced source link in full fairy-tale note'
    parts.append(inline_markdown(tail))
    return ''.join(parts)

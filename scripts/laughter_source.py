"""The current complete reader essays, not copies of the academic papers."""
import copy
from functools import lru_cache
from pathlib import Path

from prepare_action_sources import Document, inline, normalize, one
from published_html_source import index_context, main_digest

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=32)
def _article(text, index_text, directory, slug):
    doc, index = Document(text), Document(index_text)
    body = one(doc.root.walk(), lambda n: n.has('essay-body', 'lang-zh'), (slug, 'Chinese body'))
    units = []
    for child in body.children:
        if isinstance(child, str):
            assert not child.strip(), (slug, 'loose text')
            continue
        assert child.tag in ('p', 'h2'), (slug, child.tag)
        value = normalize(inline(child))
        assert value
        units.append(('## ' if child.tag == 'h2' else '') + value)
    title = one(doc.root.walk(), lambda n: n.tag == 'h1' and n.has('lang-zh'), (slug, 'title'))
    card = one(index.root.walk(), lambda n: n.tag == 'a' and n.has('entry-row')
               and n.attrs.get('href') == slug + '.html'
               and any(c.has('entry-title-zh') for c in n.walk()), (slug, 'card'))
    assert normalize(title.text()) == normalize(one(card.walk(), lambda n: n.has('entry-title-zh'), 'card title').text())
    deck = one(card.walk(), lambda n: n.has('entry-desc'), 'deck')
    citations = one(doc.root.walk(), lambda n: n.has('method-citations'), (slug, 'full apparatus'))
    academic = one(citations.walk(), lambda n: n.tag == 'p' and n.has('lang-zh')
                   and not n.has('laughter-definition-note'), (slug, 'academic note'))
    notes = [normalize(inline(academic))]
    notes += [normalize(inline(n)) for n in citations.walk()
              if n.tag == 'p' and n.has('lang-zh', 'laughter-definition-note')]
    sources = [{'url': n.attrs['href'], 'title': normalize(n.text())} for n in academic.walk() if n.tag == 'a']
    assert len(sources) == 2 and sources[0]['url'].startswith('https://self-as-an-end.net/papers/sae-laughter-')
    assert sources[1]['url'].startswith('https://doi.org/')
    return {'slug': slug, 'title_zh': normalize(title.text()), 'deck_zh': normalize(inline(deck)),
            'body_zh': units, 'notes_zh': notes, 'sources_zh': sources,
            'source_url': sources[0]['url'], 'source_note_zh': notes[0],
            'pause_zh': '先不想那么多，去读几则笑话。',
            'source_input': {'path': directory + '/' + slug + '.html',
                             'deck_path': directory + '/index.html',
                             'primary_reading_main_sha256': main_digest(doc),
                             'primary_index_main_sha256': main_digest(index)}}


def load_article(spec, slug):
    directory = (ROOT / spec['directory']).resolve()
    assert directory == ROOT / 'essays/laughter' and slug in spec['slugs']
    return copy.deepcopy(_article((directory / (slug + '.html')).read_text(),
                                  (directory / 'index.html').read_text(), spec['directory'], slug))


def index_notice(spec):
    doc = Document((ROOT / spec['directory'] / 'index.html').read_text())
    return normalize(inline(one(doc.root.walk(), lambda n: n.has('lang-zh', 'laughter-definition-note'), 'frozen terminology')))

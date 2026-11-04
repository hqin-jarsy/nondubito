"""Read canonical published reader prose without creating a second source copy.

Reuse the existing production HTML tree/inline parser, not its Action-specific
extraction or write entry point. Unknown blocks fail closed for deliberate review.
"""
import copy
import hashlib
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urljoin

from prepare_action_sources import Document, Node, inline, normalize, one

ROOT = Path(__file__).resolve().parents[1]


def main_digest(document):
    main=one(document.root.walk(),lambda n:n.tag=='main','Complete original main')
    value=re.sub(r'<div class="lang-toggle"[^>]*>.*?</div>','',document.raw(main),flags=re.S)
    return hashlib.sha256(value.encode()).hexdigest()


@lru_cache(maxsize=64)
def _article(text, index_text, directory, slug, expected_source):
    doc, index = Document(text), Document(index_text)
    body = one(doc.root.walk(),lambda n:n.tag=='div' and n.has('essay-body','lang-zh'),(slug,'Chinese body'))
    units=[]
    for child in body.children:
        if isinstance(child,str):
            assert not child.strip(),(slug,'unhandled loose text')
            continue
        assert child.tag in ('p','h2'),(slug,'new block requires deliberate handling',child.tag)
        value=normalize(inline(child))
        assert value and normalize(value.replace('*',''))==normalize(child.text()),(slug,'inline loss')
        units.append(('## ' if child.tag=='h2' else '')+value)
    title=one(doc.root.walk(),lambda n:n.tag=='h1' and n.has('lang-zh'),(slug,'Chinese title'))
    card=one(index.root.walk(),lambda n:n.tag=='a' and n.has('entry-row')
        and n.attrs.get('href')==slug+'.html' and any(c.has('entry-title-zh') for c in n.walk()),(slug,'Chinese card'))
    card_title=one(card.walk(),lambda n:n.has('entry-title-zh'),(slug,'card title'))
    deck=one(card.walk(),lambda n:n.has('entry-desc'),(slug,'card deck'))
    assert normalize(title.text())==normalize(card_title.text()),(slug,'title drift')
    notes=one(doc.root.walk(),lambda n:n.has('series-note'),(slug,'reader source note'))
    note=one(notes.walk(),lambda n:n.tag=='span' and n.has('lang-zh'),(slug,'Chinese source note'))
    paper=one(note.walk(),lambda n:n.tag=='a' and n.attrs.get('href')==expected_source,(slug,'authoritative source'))
    doi=one(note.walk(),lambda n:n.tag=='a' and (n.attrs.get('href') or '').startswith('https://doi.org/'),(slug,'DOI'))
    return {'slug':slug,'title_zh':normalize(title.text()),'deck_zh':normalize(inline(deck)),
        'body_zh':units,'source_note_zh':normalize(inline(note)),'source_url':paper.attrs['href'],
        'source_doi':doi.attrs['href'],'source_input':{'path':directory+'/'+slug+'.html',
            'deck_path':directory+'/index.html','primary_reading_main_sha256':main_digest(doc),
            'primary_index_main_sha256':main_digest(index)}}


def load_article(spec,slug):
    directory=(ROOT/spec['directory']).resolve()
    path=(directory/(slug+'.html')).resolve()
    assert directory.is_relative_to((ROOT/'essays').resolve()) and path.parent==directory
    # Cache keys contain the actual current file text, never only its filename.
    return copy.deepcopy(_article(path.read_text(),(directory/'index.html').read_text(),
        spec['directory'],slug,spec['source']))


def index_context(spec):
    """The three original Chinese introductory paragraphs, including their links."""
    doc=Document((ROOT/spec['directory']/'index.html').read_text())
    section=one(doc.root.walk(),lambda n:n.tag=='div' and n.has('lang-zh')
        and any(c.tag=='h1' for c in n.walk()),'Chinese index section')
    description=one(section.walk(),lambda n:n.has('series-desc'),'Chinese index description')
    result=[]
    for node in description.children:
        if isinstance(node,str):
            assert not node.strip()
            continue
        assert node.tag=='p'
        value=normalize(inline(node))
        # Preserve canonical source routes in the source context. Native editions
        # deliberately use the existing same-language reader routes at render.
        value=re.sub(r'\]\(([^)]+)\)',lambda m:']('+urljoin('https://nondubito.net/'+spec['directory']+'/',m[1])+')',value)
        result.append(value)
    assert len(result)==3
    return result

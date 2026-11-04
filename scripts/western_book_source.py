"""Read complete editorial book JSON directly, keeping optional material separate."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_article(spec,slug):
    name=spec['source_filenames'][slug]
    assert re.fullmatch(r'[0-9]{2}\.json',name)
    path=(ROOT/spec['source_directory']/name).resolve()
    assert path.is_relative_to((ROOT/'data').resolve())
    item=json.loads(path.read_text())
    assert item['slug']==slug
    assert item['number']==int(name[:2])
    copy=item['zh']
    aside_slugs=spec.get('aside_slugs')
    if aside_slugs is not None:
        assert isinstance(aside_slugs,list) and len(set(aside_slugs))==len(aside_slugs)
        assert set(aside_slugs)<=set(spec['slugs']) and 'intro' not in aside_slugs
    expects_aside=slug in aside_slugs if aside_slugs is not None else bool(item['number'])
    assert set(copy)=={'title','deck','sections','notes'}|({'aside'} if expects_aside else set()),(slug,'New reading material needs explicit handling')
    units=[]
    for section in copy['sections']:
        assert set(section)=={'heading','paragraphs'},(slug,'Unknown section content')
        assert isinstance(section['heading'],str) and section['paragraphs']
        if section['heading']:units.append('## '+section['heading'])
        for paragraph in section['paragraphs']:
            assert isinstance(paragraph,str) and paragraph.strip()
            units.append(paragraph)
    notes=copy['notes']
    assert notes and all(isinstance(n,str) and n.strip() for n in notes)
    aside=copy.get('aside')
    assert bool(aside)==expects_aside,(slug,'Optional aside presence differs from the explicit source contract')
    sources=[{'title':s['title']['zh'],'url':s['url']} for s in item['sources']]
    assert sources and all(s['title'] and s['url'].startswith('https://') for s in sources)
    return {'slug':slug,'title_zh':copy['title'],'deck_zh':copy['deck'],
            'body_zh':units,'aside_zh':aside,'notes_zh':notes,'sources_zh':sources,
            'source_url':sources[0]['url']}

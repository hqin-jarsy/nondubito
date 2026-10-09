"""Batch 04 introductions: preserve localized prose, build cards from essays."""
import re
import markdown
import build_anime_full_editions as b

def index_copy(series, lang):
    folder = b.DATA / 'received' / series['slug']
    name = 'INDEX.md' if series['slug'] == 'super-dimension-fortress-macross' else 'README.md'
    text = next(folder.rglob(name)).read_text()
    sections = list(re.finditer(r'^## (Deutsch|Français|Español|日本語|한국어)\s*$', text, re.M))
    assert len(sections) == 5, series['slug']
    i = b.LANGS.index(lang)
    section = text[sections[i].end():sections[i+1].start() if i+1 < 5 else len(text)]
    title = re.search(r'^### (.+)$', section, re.M)
    assert title, (series['slug'], lang)
    section = section[title.end():]
    section = re.split(r'(?m)^(?:#### |1\.\s*\[)', section)[0]
    paras = [p.strip() for p in re.split(r'\n\s*\n', section)]
    paras = [p for p in paras if len(b.plain(p)) > 65 and not p.startswith(('#', '['))
             and 'Han Qin' not in p and not re.search(r'https?://', p)]
    assert len(paras) >= 2, (series['slug'], lang, paras)
    return dict(title=b.plain(title[1]), body=markdown.markdown('\n\n'.join(paras)),
                description=b.plain(paras[0])[:230])

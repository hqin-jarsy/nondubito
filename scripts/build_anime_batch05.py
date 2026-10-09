"""Final anime batch: two source layouts, full localized introductions."""
import re
import markdown
import build_anime_full_editions as b

def index_copy(series, lang):
    if series['slug'] == 'puella-magi-madoka-magica':
        text=next((b.DATA/'received'/series['slug']).rglob('README.md')).read_text()
        sections=list(re.finditer(r'^## (Deutsch|Français|Español|日本語|한국어)\s*$',text,re.M))
        assert len(sections)==5
        i=b.LANGS.index(lang)
        section=text[sections[i].end():sections[i+1].start() if i<4 else len(text)]
        title=re.search(r'^### (.+)$',section,re.M)
        assert title
        section=section[title.end():].split('\n#### ')[0]
    else:
        text=(b.DATA/'reviewed'/series['slug']/lang/'INDEX.md').read_text()
        title=re.search(r'^# (.+)$',text,re.M)
        assert title
        section=text[title.end():].split('\n## ')[0]
    paras=[p.strip() for p in re.split(r'\n\s*\n',section)]
    boilerplate=('Auf der Originalwebsite:','Originalfassungen','Sur le site original','En el sitio original')
    paras=[p for p in paras if len(b.plain(p))>55 and not p.startswith(('#','[','**',*boilerplate))
           and 'Han Qin' not in p and not re.search(r'https?://',p)]
    assert len(paras)>=2,(series['slug'],lang,paras)
    description=b.plain(paras[0])
    if len(description)>230:
        description=(description[:220].rsplit(' ',1)[0] if lang in ('de','fr','es','ko') else description[:220])+'…'
    return dict(title=b.plain(title[1]),body=markdown.markdown('\n\n'.join(paras)),description=description)

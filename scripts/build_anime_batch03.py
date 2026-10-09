"""Batch 03 localized introductions, extracted before the article-card lists."""
import re
import markdown
import build_anime_full_editions as b

TITLES={
 'in-this-corner-of-the-world':['In This Corner of the World lesen','Lire Dans un recoin de ce monde','Leer En este rincón del mundo','『この世界の片隅に』を読む','《이 세상의 한구석에》 읽기'],
 'ghost-in-the-shell-sac':['Ghost in the Shell: Stand Alone Complex lesen','Lire Ghost in the Shell: Stand Alone Complex','Leer Ghost in the Shell: Stand Alone Complex','『攻殻機動隊 S.A.C.』を読む','《공각기동대 SAC》 읽기'],
 'neon-genesis-evangelion':['Neon Genesis Evangelion lesen','Lire Neon Genesis Evangelion','Leer Neon Genesis Evangelion','『新世紀エヴァンゲリオン』を読む','《신세기 에반게리온》 읽기'],
 'march-comes-in-like-a-lion':['March Comes in Like a Lion lesen','Lire March Comes in Like a Lion','Leer El león de marzo','『３月のライオン』を読む','《3월의 라이온》 읽기'],
 'the-tatami-galaxy':['The Tatami Galaxy lesen','Lire The Tatami Galaxy','Leer The Tatami Galaxy','『四畳半神話大系』を読む','《다다미 넉 장 반 세계일주》 읽기'],
}

def index_copy(series,lang):
    folder=b.DATA/'received'/series['slug']
    name='INDEX.md' if series['slug'] in ('neon-genesis-evangelion','march-comes-in-like-a-lion') else 'README.md'
    text=next(folder.rglob(name)).read_text()
    sections=list(re.finditer(r'^## (.+)$',text,re.M))
    # Delivery order is DE/FR/ES/JA/KO. Validate headings instead of relying on it silently.
    i=b.LANGS.index(lang);match=sections[i]
    patterns=[r'Deutsch|lesen',r'Français|Lire',r'Español|Lecturas',r'日本語|を読む',r'한국어|읽기']
    assert re.search(patterns[i],match[1]),(series['slug'],lang,match[1])
    section=text[match.end():sections[i+1].start() if i+1<len(sections) else len(text)]
    section=re.split(r'(?m)^(?:#{3,4}\s*(?:[IVⅠ]+[\s.·]|\d+\.|Los cuatro)|1\.\s*\[|-\s*(?:\[|I\s*·))',section)[0]
    paras=[]
    for p in re.split(r'\n\s*\n',section):
        p=p.strip()
        if not p or p.startswith(('#','[','©','Die Originalseiten bieten','Reescritura independiente en español')) or 'Han Qin' in p or re.search(r'https?://',p):continue
        if len(b.plain(p))>65:paras.append(p)
    assert len(paras)>=2,(series['slug'],lang,paras)
    return dict(title=TITLES[series['slug']][i],body=markdown.markdown('\n\n'.join(paras)),description=b.plain(paras[0])[:230])

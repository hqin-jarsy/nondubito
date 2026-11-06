"""Normalize the five additional manuscript layouts; never execute supplied code."""
import hashlib,json,re

LANGS=('zh','hant','en','de','fr','es','ja','ko')

def load_new_layout(files,group,slug_for,clean_title):
    def obj(path):return json.loads(files[path])
    def text(path):return files[path].decode('utf-8-sig').replace('\r\n','\n')
    def sha(path):return hashlib.sha256(files[path]).hexdigest()
    result={}
    def add(ep,lang,title,ps,url,editable,structured,has_title=True,line_paragraphs=False):
        assert lang in LANGS and 1<=ep<=30
        slug=slug_for(url,group,ep)
        assert ps and all(isinstance(p,str) and p.strip() and '\ufffd' not in p for p in ps)
        content=text(editable)
        if has_title:
            first=content.splitlines()[0].removeprefix('# ').strip()
            assert clean_title(first)==clean_title(title),(group,ep,lang,'editable title mismatch')
            content='\n'.join(content.splitlines()[1:])
        # There must be exactly these paragraphs, not just enough substrings to
        # hide a missing or extra passage in a second representation.
        blocks=[p.strip() for p in (content.splitlines() if line_paragraphs else re.split(r'\n\s*\n',content.strip())) if p.strip()]
        assert blocks==ps,(group,ep,lang,'editable/structured body mismatch')
        record=result.setdefault(ep,dict(slug=slug,source_url=url,languages={}))
        assert record['slug']==slug and lang not in record['languages']
        record['languages'][lang]=dict(title=clean_title(title),paragraphs=ps,received_text_path=editable,received_text_sha256=sha(editable),received_sources={p:sha(p) for p in (editable,structured)})
    if group in ('self','time'):
        source_path='sources/current_verified.json' if group=='self' else 'sources/source.json'
        sources={}
        for row in obj(source_path):
            key=(int(row['slug'][:2]),row['lang'])
            assert key not in sources;sources[key]=row
        for ep in range(1,31):
            for lang in LANGS:
                path=f'translations/{ep:02}-{lang}.txt' if group=='self' else f'texts/{ep:02}-{lang}.txt'
                lines=text(path).splitlines();title=lines[0].strip();ps=[p.strip() for p in lines[1:] if p.strip()]
                if lang in ('zh','hant'):assert sources[ep,lang]['ps']==ps
                add(ep,lang,title,ps,sources[ep,'zh']['url'],path,source_path,line_paragraphs=True)
    elif group=='money':
        for lang in LANGS:
            structured=f'translations/{lang}/articles.json'
            for row in obj(structured):
                ep=int(row['id']);assert row['language']==lang
                add(ep,lang,row['title'],row['paragraphs'],row['url'],f'translations/{lang}/{ep:02}.txt',structured,False)
    elif group=='social':
        structured='sources/source.json'
        for row in obj(structured):
            ep=int(row['id'])
            for lang in ('zh','hant'):
                title=row['titles'][lang] if isinstance(row['titles'],dict) else row['titles'][1 if lang=='zh' else 2]
                add(ep,lang,title,row[lang],row['url'],f'{lang}/{ep:02}.txt',structured)
            target=f'translations/{ep:02}.json';translated=obj(target)
            assert int(translated['id'])==ep
            for lang in LANGS[2:]:
                edition=translated[lang]
                add(ep,lang,edition['title'],edition['ps'],row['url'],f'{lang}/{ep:02}.txt',target)
    elif group=='growth':
        structured='data/articles.json'
        for key,row in obj(structured).items():
            number,lang=key.split('-');ep=int(number)
            assert int(row['id'])==ep and row['path'].startswith(f'editable/{lang}/{ep:02}-')
            add(ep,lang,row['title'],row['paragraphs'],row['source'],row['path'],structured)
    else:raise AssertionError(('Unsupported manuscript layout',group))
    assert set(result)==set(range(1,31))
    for ep,record in result.items():
        assert set(record['languages'])==set(LANGS)
        assert len({len(v['paragraphs']) for v in record['languages'].values()})==1
    return result

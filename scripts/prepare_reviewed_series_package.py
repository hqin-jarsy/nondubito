#!/usr/bin/env python3
"""Import only reviewed foreign Markdown; never replace received primary prose.

This is a deterministic importer, not a translator. Raw foreign inputs stay
immutable, substitutions are counted, and current Chinese is checked first.
"""
import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

from full_series_languages import ROOT, profile

UI_SERIES = {
    'marriage': {'de':'Ehe', 'fr':'Mariage', 'es':'Matrimonio', 'ja':'結婚論', 'ko':'결혼론'},
    'institution': {'de':'Institutionen', 'fr':'Les institutions', 'es':'Las instituciones', 'ja':'制度論', 'ko':'제도론'},
    'government': {'de':'Regierung', 'fr':'Le gouvernement', 'es':'El gobierno', 'ja':'政府論', 'ko':'정부론'},
}
CONTENTS = {'de':'Alle Essays', 'fr':'Tous les essais', 'es':'Todos los ensayos', 'ja':'全篇の目次', 'ko':'전체 글'}
PAPER = {'de':'Originalabhandlung', 'fr':'Texte théorique d’origine', 'es':'Artículo teórico de origen', 'ja':'原論文', 'ko':'원 논문'}
INDEX_DECKS = {
    'institution': {
        'de':'Eine Papierfabrik, ein Fluss und die Frage, was Institutionen für Menschen leisten sollen.',
        'fr':'Une papeterie, une rivière, et la question de ce que les institutions doivent faire pour les personnes.',
        'es':'Una papelera, un río y la pregunta por lo que las instituciones deben hacer por las personas.',
        'ja':'製紙工場と一本の川から、制度は人のために何をなすべきかを考える。',
        'ko':'제지공장과 강을 통해, 제도는 사람을 위해 무엇을 해야 하는지 묻는다.',
    },
    'government': {
        'de':'Sieben Essays darüber, was Regierungen schützen sollen und was sie nicht an unserer Stelle entscheiden können.',
        'fr':'Sept essais sur ce qu’un gouvernement doit protéger et ce qu’il ne peut décider à notre place.',
        'es':'Siete ensayos sobre lo que un gobierno debe proteger y lo que no puede decidir en nuestro lugar.',
        'ja':'政府は何を守るべきで、どこから先を人に委ねるべきなのか。七篇で考える。',
        'ko':'정부는 무엇을 보호해야 하며 무엇을 우리 대신 정할 수 없는가. 일곱 편의 글로 묻는다.',
    },
}
STATUS = {
    'de':'Diese Fassung wurde mit KI-Unterstützung aus dem chinesischen Text erarbeitet und für diese Veröffentlichung redaktionell korrigiert. Eine Prüfung durch einen menschlichen Muttersprachler wird nicht behauptet.',
    'fr':'Cette version a été élaborée avec l’aide de l’IA à partir du texte chinois, puis corrigée pour cette publication. Aucune révision par une personne de langue maternelle n’est revendiquée.',
    'es':'Versión elaborada con ayuda de IA a partir del texto chino y corregida para esta publicación. No se afirma que haya sido revisada por una persona hablante nativa.',
    'ja':'中国語の本文をもとにAIの支援で作成し、今回の公開に向けて内容と表現を校訂しました。人間の母語話者による校閲を受けたと主張するものではありません。',
    'ko':'중국어 본문을 바탕으로 AI의 도움을 받아 작성하고 이번 공개를 위해 내용과 표현을 교정했습니다. 인간 원어민의 감수를 받았다고 주장하지 않습니다.',
}


def blocks(text):
    return re.split(r'\n\s*\n', text.strip())


def plain(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', '', html.unescape(text).replace('**','').replace('*','').replace('`','')).removeprefix('##')


def legacy_units(source):
    match = re.search(r'<div class="essay-body lang-zh"[^>]*>(.*?)</div>', source, re.S)
    assert match, 'Missing explicit Chinese source body'
    return [('## ' if tag=='h2' else '')+html.unescape(re.sub(r'<[^>]+>', '', text)).strip()
            for tag,text in re.findall(r'<(h2|p)\b[^>]*>(.*?)</\1>', match[1], re.S)]


def prepare(series):
    spec = profile(series)
    base = ROOT/'data'/series/'multilingual'
    reports = [json.loads((base/name).read_text()) for name in ('package-review-de-fr.json','package-review-ja-ko.json','package-review-es.json')]
    assert all(not report['unresolved'] for report in reports), 'Unresolved package review'
    fixes = [issue for report in reports for issue in report['issues']]
    languages = [code for report in reports for code in report['languages']]
    assert set(languages) == set(spec['languages']) and len(languages) == len(set(languages))
    package = Path(spec['package'])
    outputs = {}
    sources = {}
    preservation = {'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), 'primary_files':{}, 'primary_bodies':{}}
    with ZipFile(package) as archive:
        members = archive.namelist()
        def md(slug, code):
            matches = [n for n in members if n.endswith('/MD/'+slug+'.'+code+'.md')]
            assert len(matches)==1, (slug,code,matches)
            return archive.read(matches[0]).decode('utf-8')
        for slug in spec['slugs']:
            path = ROOT/spec['directory']/(slug+'.html')
            primary = path.read_text()
            bodies = re.findall(r'<div class="essay-body[^>]*>.*?</div>',primary,re.S)
            preservation['primary_bodies'][slug] = hashlib.sha256(''.join(bodies).encode()).hexdigest()
            current = ROOT/'data'/series/(slug+'.json')
            original = json.loads(current.read_text()) if current.exists() else {'slug':slug, 'body_zh':legacy_units(primary), 'source_url':re.findall(r'https://self-as-an-end.net/papers/[^"\s<]+',primary)[0]}
            zh = blocks(md(slug,'zh-Hans'))
            n = len(original['body_zh'])
            offsets = [i for i in (1,2) if len(zh)>=i+n and [plain(x) for x in zh[i:i+n]] == [plain(x) for x in original['body_zh']]]
            assert len(offsets)==1, ('Chinese snapshot differs from current essay',series,slug)
            original['markdown_offset'] = offsets[0]
            sources[slug] = original
            if current.exists():
                preservation['primary_files'][str(current.relative_to(ROOT))] = hashlib.sha256(current.read_bytes()).hexdigest()
        for path in sorted((ROOT/spec['directory']).rglob('*.js')):
            if path.parent.name in spec['languages']:
                continue
            preservation['primary_files'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        for code in spec['languages']:
            articles = []
            for slug in spec['slugs']:
                raw = md(slug, code)
                received = base/'received'/(slug+'.'+code+'.md')
                if received.exists():
                    assert received.read_text()==raw, ('Immutable input changed',received)
                outputs[received] = raw
                edited = raw
                for fix in fixes:
                    if fix['language']==code and fix['slug']==slug:
                        count = fix.get('count',1)
                        assert edited.count(fix['before'])==count, (series,code,slug,fix['before'])
                        edited = edited.replace(fix['before'],fix['after'])
                parts = blocks(edited)
                original = sources[slug]
                offset = original['markdown_offset']
                n = len(original['body_zh'])
                body = parts[offset:offset+n]
                assert len(body)==n and [x.startswith('## ') for x in body]==[x.startswith('## ') for x in original['body_zh']], (code,slug)
                tail = []
                for paragraph in parts[offset+n:]:
                    if paragraph.startswith(('## ','https://','[原','[元','[Original','[Article original','[Artículo original')):
                        continue
                    if 'https://self-as-an-end.net/' in paragraph and len(paragraph)<140:
                        continue
                    if re.search(r'未经|未获|尚未|nicht.*freigegeben|pas.*approuv|aprobada por el autor|承認.*受けて|著者の承認版|公式サイトの公開版ではありません|승인.*않|No es una versión aprobada|未取得|Nicht vom Autor',paragraph,re.I):
                        tail.append(STATUS[code])
                    else:
                        tail.append(paragraph)
                deck = parts[1] if offset==2 else next(p for p in body if not p.startswith('## '))
                # Index/description excerpts are not a substitute for full body.
                if len(deck)>300:
                    deck = deck[:300].rsplit(' ',1)[0]+'…' if code in ('de','fr','es') else deck[:180]+'…'
                articles.append({'slug':slug,'title':parts[0].removeprefix('# '),'deck':deck,'body':body,
                                 'source_note':'\n\n'.join(tail),'source_url':original['source_url'],
                                 'coverage':[f'{i:02}: '+p[:80] for i,p in enumerate(original['body_zh'])]})
                if offset==1:
                    articles[-1]['show_deck']=False
            ui = json.loads((ROOT/'data/accountability/multilingual'/f'{code}.json').read_text())['ui'].copy()
            ui.update(series=UI_SERIES[series][code],contents=CONTENTS[code],paper=PAPER[code])
            first = articles[0]
            series_title = first['title'] if series=='marriage' else UI_SERIES[series][code]
            data = {'language':code,'series':{'title':series_title,'deck':INDEX_DECKS.get(series,{}).get(code,first['deck']),'intro':next(p for p in first['body'] if not p.startswith('## ')),'scope':first['body'][-2],'source_note':first['source_note']},'ui':ui,'articles':articles,
                    'review':{'source':'Author-supplied foreign manuscript, checked against current Chinese essays.','issues_checked':['Complete per-essay reading','Chinese snapshot matches current source','Exact counted editorial corrections'], 'unresolved':[]}}
            outputs[base/(code+'.json')] = json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    outputs[base/'source-baseline.json'] = json.dumps(sources,ensure_ascii=False,indent=2)+'\n'
    snapshot = base/'preservation.json'
    if not snapshot.exists():
        outputs[snapshot] = json.dumps(preservation,ensure_ascii=False,indent=2)+'\n'
    receipt = {'date':spec['date'],'result':'passed','scope':'Full manuscript reading, source-snapshot comparison and counted local corrections; not native-speaker certification.',
               'package_name':package.name,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
               'languages':spec['languages'],'slugs':spec['slugs'],'resolved_issues':fixes,'unresolved':[],
               'received_files':{str(p.relative_to(base)):hashlib.sha256(t.encode()).hexdigest() for p,t in outputs.items() if p.parent.name=='received'}}
    outputs[base/'publication.json'] = json.dumps(receipt,ensure_ascii=False,indent=2)+'\n'
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs=prepare(args.series)
    for path,text in outputs.items():
        if args.check:
            assert path.read_text()==text, path
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    print(f'{args.series}: {len(outputs)} reviewed text/receipt files '+('checked' if args.check else 'prepared'))


if __name__=='__main__':
    main()

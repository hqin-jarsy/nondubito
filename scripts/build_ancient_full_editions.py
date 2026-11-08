#!/usr/bin/env python3
"""Overlay complete Chinese-based Ancient Stories translations at existing URLs.

Source and original-page snapshots are immutable. Paragraph-aligned translations
are canonical. Guard each existing title/body against losing later manual edits.
The compact collection builder invokes this overlay rather than restoring abridgments.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
from build_epic_full_editions import digest, div_span, region, within, within_body, navigation, metadata, inline, body, title
from build_fables_full_editions import persist_query_language

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/ancient-full'
SERIES = ROOT / 'essays/everyday/stories/ancient-stories'
FOREIGN = ('en', 'ja', 'fr', 'de', 'es', 'ko')
LANGS = ('zh-Hans', 'zh-Hant') + FOREIGN
NOTES = {
 'ja': '中国語全文に基づく完全翻訳。すべての段落、区切り、末尾のテキスト根拠を収録しています。',
 'fr': 'Traduction intégrale du texte chinois, avec tous les paragraphes, séparations et la note finale sur les sources.',
 'de': 'Vollständige Übersetzung des chinesischen Textes mit allen Absätzen, Abschnittstrennungen und dem abschließenden Quellenhinweis.',
 'es': 'Traducción íntegra del texto chino, con todos sus párrafos, separaciones y la nota final sobre las fuentes.',
 'ko': '중국어 전문을 바탕으로 한 완역입니다. 모든 문단과 구분, 마지막 텍스트 근거를 포함합니다.',
}
STYLE = '''<style id="ancient-full-style">
.collection-body.full-edition p{margin:0 0 1.55em;line-height:1.95}
.collection-body.full-edition hr{border:0;border-top:1px solid var(--cream-border);margin:2.6rem 0}
.collection-body.full-edition em{color:var(--ink-muted);font-size:.9em}
.collection-page,.story-wrap{overflow-wrap:anywhere}
.collection-page h1,.collection-card h2,.collection-nav a{min-width:0}
.collection-page h1{hyphens:auto}
html[lang="ko"] .collection-page{word-break:keep-all}
@media(max-width:380px){.collection-page h1{font-size:1.85rem}}
html[lang="ja"] .collection-body,html[lang="ko"] .collection-body{font-family:var(--cjk),var(--serif),serif}
</style>'''


def read_json(path):
 return json.loads(path.read_text())


def manifest():
 return read_json(DATA / 'source-manifest.json')


def snapshot(relative):
 return DATA / 'source-snapshots' / (str(relative) + '.txt')


def source(episode,lang='zh-Hans'):
 path = DATA / 'source' / f'{episode:02}.{lang}.json'
 assert digest(path.read_bytes()) == manifest()['source_files'][str(path.relative_to(DATA))], ('Chinese input changed', path)
 blocks=read_json(path)
 for correction in source_corrections():
  if episode==correction['episode']:
   edit=correction['edits'][lang];index=correction['block']
   assert blocks[index]['text']==edit['before'], ('Stale source correction',lang,index)
   blocks[index]['text']=edit['after']
 return blocks


def minor_correction():
 path=DATA/'minor-source-correction.json'
 assert digest(path.read_bytes())==manifest()['minor_source_correction_sha256']
 record=read_json(path)
 assert (record['episode'],record['block'])==(15,31)
 assert set(record['edits'])=={'zh-Hans','zh-Hant'}
 for lang,edit in record['edits'].items():
  before,after=('善待拒绝者','善待被拒绝者') if lang=='zh-Hans' else ('善待拒絕者','善待被拒絕者')
  assert edit['before'].count(before)==1 and edit['after']==edit['before'].replace(before,after)
 return record


def approved_corrections():
 path=DATA/'approved-source-corrections.json'
 assert digest(path.read_bytes())==manifest()['approved_source_corrections_sha256']
 records=read_json(path)
 assert [(r['episode'],r['block']) for r in records]==[(4,104)]
 for record in records:
  assert set(record['edits'])=={'zh-Hans','zh-Hant'}
  assert set(record['translations'])==set(FOREIGN)
  for lang,edit in record['edits'].items():
   before,after=('回头看了','违约看了她') if lang=='zh-Hans' else ('回頭看了','違約看了她')
   assert edit['before'].count(before)==1 and edit['after']==edit['before'].replace(before,after)
 return records


def source_corrections():
 return [minor_correction()]+approved_corrections()


def approved_chinese_region(filename,code):
 original=region(snapshot(filename).read_text(),'lang-'+code)
 assert digest(original)==read_json(DATA/'chinese-baseline.json')[filename][code]
 for correction in source_corrections():
  if filename.startswith(f"{correction['episode']:02}-"):
   edit=correction['edits'][{'zh':'zh-Hans','hant':'zh-Hant'}[code]]
   before='<p>'+inline(edit['before'])+'</p>';after='<p>'+inline(edit['after'])+'</p>'
   assert original.count(before)==1
   original=original.replace(before,after,1)
 return original


def editions():
 result = {}
 for item in manifest()['essays']:
  original = source(item['episode'])
  copies = {lang: source(item['episode'],lang) for lang in ('zh-Hans','zh-Hant')}
  for lang in FOREIGN:
   path = DATA / 'translations' / f"{item['episode']:02}.{lang}.json"
   translated = read_json(path)
   assert [b['tag'] for b in translated] == [b['tag'] for b in original], ('Missing, merged, or reordered blocks',path)
   for i,(src,dst) in enumerate(zip(original,translated)):
    assert set(dst)=={'tag','text'} and isinstance(dst['text'],str), (path,i)
    if src['tag']=='hr':assert dst['text']=='', (path,i)
    else:
     assert dst['text'].strip(), ('Empty translation',path,i)
     inline(dst['text'])
     assert src['text'].count('*')==dst['text'].count('*'), ('Emphasis differs',path,i)
     assert src['text'].count('**')==dst['text'].count('**'), ('Strong emphasis differs',path,i)
     assert '\ufffd' not in dst['text'], (path,i)
     assert src['text'].count('Self-as-an-End')==dst['text'].count('Self-as-an-End'), ('Fixed term changed',path,i)
   copies[lang]=translated
  result[item['slug']]=copies
 assert len(result)==19
 return result


def prose(text,lang):
 part = region(text,'lang-en') if lang=='en' else text
 heading = re.search(r'<h1[^>]*>(.*?)</h1>',part,re.S)
 assert heading
 return {'body':digest(within_body(part,'article-body' if lang=='en' else 'collection-body').strip()), 'title':digest(heading[1])}


def guard(path,text,lang,blocks):
 relative=str(path.relative_to(SERIES))
 original=prose(snapshot(relative).read_text(),lang)
 current=prose(text,lang)
 canonical={'body':digest(body(blocks)), 'title':digest(html.escape(title(blocks)))}
 previous=read_json(DATA/'last-build.json').get(relative) if (DATA/'last-build.json').exists() else None
 for field in ('body','title'):
  allowed={original[field],canonical[field]}
  if previous:allowed.add(previous[field])
  assert current[field] in allowed, ('Foreign HTML prose changed; preserve manual edits in canonical inputs before rebuilding',path,field)


def style(text):
 text=re.sub(r'<style id="ancient-full-style">.*?</style>\n?','',text,flags=re.S)
 return text.replace('</head>',STYLE+'\n</head>',1)


def upgrade_outputs(outputs):
 all_editions=editions()
 receipt=manifest()
 for relative,expected in receipt['snapshot_files'].items():
  assert digest((DATA/relative).read_bytes())==expected, ('Snapshot changed',relative)
 baseline=read_json(DATA/'chinese-baseline.json')
 for path,text in list(outputs.items()):
  if not path.is_relative_to(SERIES):continue
  primary=path.parent==SERIES
  lang='en' if primary else path.parent.name
  assert lang in FOREIGN
  slug=path.stem
  if primary:
   for code in ('zh','hant'):
    expected=approved_chinese_region(path.name,code)
    assert digest(region(text,'lang-'+code)) in (baseline[path.name][code],digest(expected)), ('Chinese source drift',path,code)
    a,_,_,z=div_span(text,'lang-'+code)
    text=text[:a]+expected+text[z:]
  if slug in all_editions:
   guard(path,path.read_text(),lang,all_editions[slug][lang])
  def replace_copy(part):
   if slug in all_editions:
    blocks=all_editions[slug][lang]
    part=within(part,'article-body' if primary else 'collection-body',lambda _:body(blocks))
    if not primary:part=re.sub(r'class="collection-body(?: full-edition)?"','class="collection-body full-edition"',part,count=1)
    part=re.sub(r'(<h1[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(title(blocks))+m[2],part,count=1,flags=re.S)
   return navigation(part,lang,all_editions,slug)
  text=within(text,'lang-en',replace_copy) if primary else replace_copy(text)
  if slug in all_editions:
   text=metadata(text,title(all_editions[slug][lang]))
   if not primary:
    text=re.sub(r'(<p class="edition-note"><em>).*?(</em></p>)',lambda m:m[1]+NOTES[lang]+m[2],text,count=1,flags=re.S)
  if primary:text=persist_query_language(text)
  text=style(text)
  if primary:
   for code in ('zh','hant'):assert region(text,'lang-'+code)==approved_chinese_region(path.name,code)
  outputs[path]=text
 return outputs


def render():
 outputs=upgrade_outputs({p:p.read_text() for p in SERIES.rglob('*.html')})
 assert len(outputs)==120
 return outputs


def search_outputs():
 from unittest.mock import patch
 import build_search_index as search
 with patch.object(search,'collect_pages',lambda:sorted(SERIES.rglob('*.html'))):
  _,chunks=search.build()
 outputs={};prefix=str(SERIES.relative_to(ROOT))+'/'
 for lang,new in chunks.items():
  path=ROOT/'data/search'/f'{lang.lower()}.json';data=read_json(path)
  fresh={row['u']:row for row in new}
  assert {r['u'] for r in data['records'] if r['u'].startswith(prefix)}==set(fresh),('Search routes changed',lang)
  data['records']=[fresh.get(row['u'],row) for row in data['records']]
  outputs[path]=search.serialized(data)
 return outputs


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--refresh-search',action='store_true');args=parser.parse_args()
 outputs=render();stale=[p for p,t in outputs.items() if p.read_text()!=t]
 if args.check:
  assert not stale,('Stale Ancient Stories pages',stale)
  for p,t in search_outputs().items():assert p.read_text()==t,('Stale Ancient Stories search',p)
  print('OK: 19 complete six-language translations; 120 pages and eight search indexes current')
 else:
  for p in stale:p.write_text(outputs[p])
  record={str(p.relative_to(SERIES)):prose(t,'en' if p.parent==SERIES else p.parent.name) for p,t in outputs.items() if p.stem!='index'}
  (DATA/'last-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
  if args.refresh_search:
   for p,t in search_outputs().items():
    if p.read_text()!=t:p.write_text(t)
  print(f'Updated {len(stale)} Ancient Stories pages')

if __name__=='__main__':main()

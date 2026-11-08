#!/usr/bin/env python3
"""Complete Sex and the City editions at existing routes; frozen Chinese, guarded prose.

Only reviewed sources are rendered. The compact collection builder calls this
same overlay, so it cannot silently restore its three-paragraph summaries.
"""
from __future__ import annotations
import argparse,hashlib,html,json,re
from pathlib import Path
from html.parser import HTMLParser
from build_epic_full_editions import div_span,within

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/satc-full'
SERIES=ROOT/'essays/tv/sex-and-the-city'
LANGS=('de','fr','es','ja','ko')
DATE='2026-11-08'
NOTES={
'de':'Vollständige Übersetzung des veröffentlichten chinesischen Essays. Spoiler zur gesamten Serie und zu beiden Kinofilmen.',
'fr':'Traduction intégrale de l’essai chinois publié. Révélations sur l’ensemble de la série et les deux films.',
'es':'Traducción íntegra del ensayo chino publicado. Contiene revelaciones de toda la serie y de las dos películas.',
'ja':'公開された中国語本文に基づく全訳。全6シーズンと映画2作品のネタバレを含みます。',
'ko':'공개된 중국어 본문을 바탕으로 한 완역입니다. 전체 시즌과 두 편의 영화에 관한 스포일러를 포함합니다.'}
STYLE='''<style id="satc-full-style">
.collection-body.full-edition p{margin:0 0 1.35em;line-height:1.9}
.collection-body.full-edition h2{font-size:1.45rem;line-height:1.45;margin:3rem 0 1.2rem}
.collection-body.full-edition hr{border:0;border-top:1px solid var(--cream-border);margin:2rem 0}
.collection-page,.essay-page{overflow-wrap:anywhere}
.lang-toggle{display:flex;flex-wrap:wrap;align-items:center;gap:.3rem}
.collection-page h1,.collection-nav a{hyphens:auto;min-width:0}
html[lang="ja"] .collection-body,html[lang="ko"] .collection-body{font-family:var(--cjk),var(--serif),serif}
html[lang="ko"] .collection-body{word-break:keep-all}
@media(max-width:380px){.collection-page h1{font-size:1.85rem}.essay-page-title{font-size:2rem}}
</style>'''

def read(path):return json.loads(path.read_text())
def digest(value):return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()
def manifest():return read(DATA/'source-manifest.json')
def primary_body(text,lang):
 match=re.search(r'<div class="essay-body lang-'+lang+r'"[^>]*>',text);assert match
 start=match.end();depth=1
 for n in re.finditer(r'</?div\b[^>]*>',text[start:]):
  depth+= -1 if n[0].startswith('</') else 1
  if depth==0:return start,start+n.start()
 raise AssertionError('Unclosed primary body')
def replace_primary(text,lang,value):
 a,b=primary_body(text,lang);return text[:a]+value+text[b:]
def source(slug):
 p=DATA/'source'/f'{slug}.json';expected=next(x for x in manifest()['articles'] if x['slug']==slug)
 assert digest(p.read_bytes())==expected['source_sha256'],('Source drift',p)
 return read(p)
def effective_source(slug):
 d=source(slug)
 for edit in read(DATA/'review/approved-chinese.json'):
  if edit['slug']!=slug:continue
  block=d['blocks'][edit['block_index']]
  assert block['html']==edit['before'],('Approved baseline drift',slug,edit['block_index'])
  block['html']=edit['after']
 return d
class Inline(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=False);self.stack=[]
 def handle_starttag(self,tag,attrs):
  assert tag in ('strong','em') and not attrs,('Unsafe inline',tag,attrs);self.stack.append(tag)
 def handle_endtag(self,tag):assert self.stack and self.stack.pop()==tag,('Unbalanced inline',tag)
 def handle_comment(self,data):raise AssertionError('Comment in inline')
def validate_inline(s):
 p=Inline();p.feed(s);p.close();assert not p.stack and '\ufffd' not in s;return s

def translations():
 result={}
 for item in manifest()['articles']:
  slug=item['slug'];s=effective_source(slug);result[slug]={}
  for lang in LANGS:
   p=DATA/lang/f'{slug}.json';d=read(p)
   assert d['slug']==slug and [b['tag'] for b in d['blocks']]==[b['tag'] for b in s['blocks']],('Missing or reordered blocks',p)
   for i,(a,b) in enumerate(zip(s['blocks'],d['blocks'])):
    assert set(b)=={'tag','html'} and isinstance(b['html'],str),(p,i)
    if b['tag']=='hr':assert b['html']=='',(p,i)
    else:
     assert b['html'].strip(),('Empty translation',p,i)
     validate_inline(b['html'])
     assert a['html'].count('<strong>')==b['html'].count('<strong>'),('Strong emphasis drift',p,i)
     # French typography italicizes work titles where Chinese uses title brackets.
     comparable=re.sub(r'<em>(Sex and the City)</em>',r'\1',b['html']) if lang=='fr' else b['html']
     assert a['html'].count('<em>')==comparable.count('<em>'),('Emphasis drift',p,i)
     assert a['html'].count('Self-as-an-End')==b['html'].count('Self-as-an-End'),('Fixed term changed',p,i)
   assert d['title'].strip() and d['deck'].strip();validate_inline(d['source_note'])
   result[slug][lang]=d
  d=read(DATA/'en'/f'{slug}.json');assert d['slug']==slug and d['body_html'].count('<h2>')>=5
  result[slug]['en']=d
 receipt=DATA/'review/accepted.json'
 assert receipt.exists(),'Missing editorial acceptance receipt'
 acceptance=read(receipt)
 assert acceptance.get('status')=='accepted','Editorial acceptance is pending'
 accepted=acceptance['files']
 required={'source-manifest.json'}|{str(p.relative_to(DATA)) for lang in ['source','en',*LANGS] for p in (DATA/lang).glob('*.json')}|{str(p.relative_to(DATA)) for p in (DATA/'review').glob('approved-*.json')}|{str(p.relative_to(DATA)) for p in (DATA/'review/zh-hant-data').glob('*.js')}
 assert required.issubset(accepted),'Incomplete editorial acceptance receipt'
 for relative,expected in accepted.items():
  assert digest((DATA/relative).read_bytes())==expected,('Reviewed source changed; editorial reacceptance required',relative)
 return result

def rendered_body(d):
 return '\n'.join('<hr />' if b['tag']=='hr' else '<'+b['tag']+'>'+b['html']+'</'+b['tag']+'>' for b in d['blocks'])+'\n<p class="source-note">'+d['source_note']+'</p>'
def protect(path,expected):
 current=path.read_text();relative=str(path.relative_to(SERIES));old=manifest()['dictionaries'].get(path.name) if path.parent.name=='zh-hant-data' else manifest()['snapshots'].get(relative)
 previous=read(DATA/'last-build.json').get(relative) if (DATA/'last-build.json').exists() else None
 assert digest(current) in {old,previous,digest(expected)},('Page changed outside canonical inputs; preserve manual edits before rebuilding',path)

def primary_script(text):
 pattern=r'<script>\s*\(function\(\)\{.*?\}\)\(\);\s*</script>'
 text,n=re.subn(pattern,'<script src="satc-language.js"></script>',text,count=1,flags=re.S);assert n==1
 return text

def approved_chinese(slug,body):
 # Address blocks by position so repeated sentences remain unambiguous.
 blocks=list(re.finditer(r'<(h2|p)(?:\s[^>]*)?>(.*?)</\1>|<hr\s*/?>',body,re.S))
 assert '版本说明' in blocks[0][0],slug
 edits=[e for e in read(DATA/'review/approved-chinese.json') if e['slug']==slug]
 for e in sorted(edits,key=lambda x:x['block_index'],reverse=True):
  m=blocks[e['block_index']+1]
  assert m[2]==e['before'],('Correction baseline drift',slug,e['block_index'])
  a,b=m.span(2);body=body[:a]+e['after']+body[b:]
 return body

def render(guard=True):
 receipt=manifest();all_editions=translations();result={}
 for relative,expected in receipt['snapshots'].items():
  p=DATA/'received'/(relative+'.txt');assert digest(p.read_bytes())==expected,('Snapshot drift',relative)
 for relative in sorted(receipt['snapshots']):
  p=SERIES/relative;text=(DATA/'received'/(relative+'.txt')).read_text();slug=p.stem;primary=p.parent==SERIES;lang='en' if primary else p.parent.name
  if primary:
   text=primary_script(text)
   for change in read(DATA/'review/approved-discovery.json'):
    text=text.replace(change['before'],change['after'])
   if slug in all_editions:
    text=replace_primary(text,'en',all_editions[slug]['en']['body_html'])
    a,b=primary_body(text,'zh');text=text[:a]+approved_chinese(slug,text[a:b])+text[b:]
  else:
   if slug in all_editions:
    d=all_editions[slug][lang]
    text=within(text,'collection-body',lambda _:rendered_body(d)).replace('class="collection-body"','class="collection-body full-edition"',1)
    text=re.sub(r'(<h1>).*?(</h1>)',lambda m:m[1]+html.escape(d['title'])+m[2],text,count=1,flags=re.S)
    text=re.sub(r'(<p class="collection-deck">).*?(</p>)',lambda m:m[1]+html.escape(d['deck'])+m[2],text,count=1,flags=re.S)
    text=re.sub(r'(<p class="edition-note"><em>).*?(</em></p>)',lambda m:m[1]+NOTES[lang]+m[2],text,count=1,flags=re.S)
    text=re.sub(r'<title>.*?</title>','<title>'+html.escape(d['title'])+' · Sex and the City — Non Dubito</title>',text,count=1,flags=re.S)
    for attr,key,value in [('name','description',d['deck']),('property','og:title',d['title']),('property','og:description',d['deck'])]:
     text=re.sub(r'(<meta '+attr+'="'+key+r'" content=")[^"]*(">)',lambda m:m[1]+html.escape(value,quote=True)+m[2],text,count=1)
   # Keep card and neighbor labels aligned with full-edition titles.
   for target,versions in all_editions.items():
    d=versions[lang]
    pattern=r'(<a\b[^>]*href="'+re.escape(target)+r'\.html"[^>]*>)(.*?)(</a>)'
    def link(m):
     inner=m[2]
     if '<h2>' in inner:
      inner=re.sub(r'<h2>.*?</h2>','<h2>'+html.escape(d['title'])+'</h2>',inner,count=1,flags=re.S)
      inner=re.sub(r'<p>.*?</p>','<p>'+html.escape(d['deck'])+'</p>',inner,count=1,flags=re.S)
     elif '<small>' in inner:
      label=re.match(r'<small>.*?</small>',inner,re.S)[0]
      inner=label+('← ' if '←' in inner else '')+html.escape(d['title'])+(' →' if '→' in inner else '')
     return m[1]+inner+m[3]
    text=re.sub(pattern,link,text,flags=re.S)
  text=text.replace('</head>',STYLE+'\n</head>',1)
  if guard:protect(p,text)
  result[p]=text
 # Keep dictionary snapshots frozen unless an exact approved dictionary exists.
 for name,expected in receipt['dictionaries'].items():
  p=DATA/'received/zh-hant-data'/name;assert digest(p.read_bytes())==expected
  replacement=DATA/'review/zh-hant-data'/name
  value=replacement.read_text() if replacement.exists() else p.read_text()
  dest=SERIES/'zh-hant-data'/name
  if guard:protect(dest,value)
  result[dest]=value
 return result

def upgrade_outputs(outputs):
 # Use the frozen complete-page templates rather than the compact body's copy.
 outputs.update(render());return outputs

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();outputs=render()
 if args.check:
  stale=[str(p.relative_to(ROOT)) for p,s in outputs.items() if p.read_text()!=s];assert not stale,('Stale Sex and the City pages',stale)
 else:
  for p,s in outputs.items():p.write_text(s)
  (DATA/'last-build.json').write_text(json.dumps({str(p.relative_to(SERIES)):digest(s) for p,s in outputs.items()},indent=2)+'\n')
 print(('Verified' if args.check else 'Built')+' 66 Sex and the City pages and 11 protected Traditional Chinese dictionaries')
if __name__=='__main__':main()

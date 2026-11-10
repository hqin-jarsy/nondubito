from pathlib import Path
import sys,json,re,hashlib,datetime
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from html.parser import HTMLParser
ROOT=Path('/Users/hanqin/Documents/GitHub/nondubito'); OUT=Path('/tmp/value-author-review-20261110')
sys.path.insert(0,str(ROOT/'scripts'))
import build_value_full_editions as b
from prepare_action_sources import Document,Node
langs=['zh','zh-hant','en','ja','de','fr','es','ko'];slugs=['ep01','prospect'];expected={}
class Texts(HTMLParser):
 def __init__(self,s,variants=None):super().__init__();self.out=[];self.variants=variants or {};self.feed(s)
 def handle_data(self,s):self.out.append(self.variants.get(s,s))
def norm(s):return re.sub(r'\s+',' ',s).strip()
for slug in slugs:
 source=b.read(b.BASE/'sources'/(slug+'.json')); z=b.amendments.units(slug,'zh',source['body_zh'])
 raw=(b.DIRECTORY/'zh-hant-data'/(slug+'.js')).read_text();v=json.loads(re.search(r'var variants = (\{.*?\});\n',raw,re.S)[1])
 d=Document(b.english_body(slug));e=[d.raw(n) for n in d.root.children if isinstance(n,Node)]
 for lang in langs:
  units=z if lang in ('zh','zh-hant') else e if lang=='en' else b.load(lang,slug)['body']
  expected[lang+'/'+slug]=[norm(''.join(Texts(u,v if lang=='zh-hant' else None).out)) for u in units]
files=[b.DIRECTORY/((l+'/') if l not in ('zh','zh-hant','en') else '')/(s+'.html') for l in langs for s in slugs]
files+=list((b.DIRECTORY/'zh-hant-data').glob('*.js'))+[ROOT/'style.css',ROOT/'classic-reading.js',b.amendments.MANIFEST,b.amendments.BASE/'traditional-patches.json']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}
(OUT/'input-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
(OUT/'expected.json').write_text(json.dumps(expected,ensure_ascii=False))
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
 def end_headers(self):
  self.send_header('Cache-Control','no-store');self.send_header('Content-Security-Policy',"default-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'; frame-src 'self'");super().end_headers()
 def do_GET(self):
  path=urlsplit(self.path).path
  if path in ('/__audit__','/__expected__'):
   data=(OUT/('audit.html' if path=='/__audit__' else 'expected.json')).read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8' if path=='/__audit__' else 'application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().do_GET()
 def do_POST(self):
  if self.path!='/__event__':self.send_error(404);return
  data=json.loads(self.rfile.read(int(self.headers['Content-Length'])));data['recorded_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
  with (OUT/'events.jsonl').open('a') as f:f.write(json.dumps(data,ensure_ascii=False)+'\n')
  self.send_response(200);self.end_headers();self.wfile.write(b'ok')
print('Independent local UI audit at http://127.0.0.1:8794/__audit__',flush=True)
ThreadingHTTPServer(('127.0.0.1',8794),Handler).serve_forever()

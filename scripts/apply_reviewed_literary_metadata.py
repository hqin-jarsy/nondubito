#!/usr/bin/env python3
"""Apply a series-scoped reviewed metadata ledger, preserving all other text."""
import argparse,json,re,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def apply(key):
 D=R/'data'/key;ledger=D/'metadata-corrections.json'
 if not ledger.exists():return
 spec=json.loads((D/'multilingual/profile.json').read_text());F=R/spec['directory'];changes=json.loads(ledger.read_text())['changes']
 for p in F.glob('*.html'):
  text=p.read_text()
  for c in changes:
   for old,new in [(c['before'],c['after']),(html.escape(c['before'],quote=True),html.escape(c['after'],quote=True))]:text=text.replace(old,new)
  p.write_text(text)
 for p in (F/'zh-hant-data').glob('*.js'):
  text=p.read_text();m=re.search(r'var variants\s*=\s*(\{.*?\});',text,re.S);v=json.loads(m[1])
  for c in changes:
   if c.get('zh_hant') and (c['before'] in v or c['after'] in v):v.pop(c['before'],None);v[c['after']]=c['zh_hant']
  p.write_text(text[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+text[m.end(1):])
 print(key,': scoped primary metadata synchronized')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('series');apply(p.parse_args().series)

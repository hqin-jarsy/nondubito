#!/usr/bin/env python3
"""Refresh only published, review-accepted Relationships search/sitemap entries."""
import argparse,datetime
import xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
import build_relationships_full_editions as full
from build_sitemap import parse_page,sitemap_xml

PUBLICATION_DATE="2026-11-09"

def outputs(date=None):
 date=date or PUBLICATION_DATE;datetime.date.fromisoformat(date)
 accepted=full.reviewed();rendered=full.render();paths=sorted(rendered)
 if not paths:return {}
 assert all(p.read_text()==s for p,s in rendered.items()),'Render accepted editions before refreshing discovery'
 scope={str(p.relative_to(full.ROOT)) for p in paths};result={}
 assert all(s.startswith('essays/everyday/relationships/') for s in scope)
 with patch.object(search,'collect_pages',lambda:paths):_,fresh=search.build()
 manifest=full.read_json(search.OUTPUT)
 for lang,records in fresh.items():
  for r in records:
   slug=r['u'].rsplit('/',1)[1].removesuffix('.html');tp=full.DATA/'translations'/lang/(slug+'.json')
   # Only use accepted records, not unreviewed translated metadata.
   if lang in full.LANGS and (lang,slug) in accepted:
    data=full.load(lang,slug);r['t']=data['title'];r['x']=data['deck']
  path=search.CHUNKS_DIR/(lang.lower()+'.json');chunk=full.read_json(path);new={r['u']:r for r in records}
  before={r['u']:r for r in chunk['records'] if r['u'] not in scope}
  chunk['records']=[new.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
  chunk['records'].extend(new.values())
  assert before=={r['u']:r for r in chunk['records'] if r['u'] not in scope},'Unrelated search record changed'
  result[path]=search.serialized(chunk);manifest['languages'][lang]['count']=len(chunk['records'])
 # Count the complete manifest's unique URL set, including untouched chunks.
 unique=set()
 for p in search.CHUNKS_DIR.glob('*.json'):
  chunk=__import__('json').loads(result[p]) if p in result else full.read_json(p)
  unique.update(r['u'] for r in chunk.get('records',[]))
 manifest['record_count']=len(unique);result[search.OUTPUT]=search.serialized(manifest)
 path=full.ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
 entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(path).getroot()}
 before=dict(entries);canonical_scope=set()
 for p in paths:
  canonical=parse_page(p).canonical
  file_url='https://nondubito.net/'+p.relative_to(full.ROOT).as_posix()
  allowed={file_url,file_url.removesuffix('index.html')} if p.name=='index.html' else {file_url}
  assert canonical in allowed,('Canonical does not match scoped page',p,canonical)
  canonical_scope.add(canonical)
  entries[canonical]=max(entries.get(canonical,date),date)
 assert {k:v for k,v in before.items() if k not in canonical_scope}=={k:v for k,v in entries.items() if k not in canonical_scope},'Unrelated sitemap entry changed'
 result[path]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--date');a=p.parse_args();changed=[]
 for path,value in outputs(a.date).items():
  if path.read_text()!=value:
   changed.append(str(path.relative_to(full.ROOT)))
   if not a.check:path.write_text(value)
 print(('Checked' if a.check else 'Refreshed'),'scoped Relationships discovery;',len(changed),'changed')
 return int(a.check and bool(changed))
if __name__=='__main__':raise SystemExit(main())

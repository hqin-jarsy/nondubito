#!/usr/bin/env python3
"""Update this classical series' search records and sitemap dates only.

The site's global search build has unrelated pre-existing drift. Do not silently
rewrite other collections while repairing this one.
"""
import argparse,json,xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
import build_classic_full_editions as full
from build_sitemap import parse_page,sitemap_xml
DATE='2026-11-09'

def outputs(series):
 paths=sorted(full.folder(series).rglob('*.html'));scope={str(p.relative_to(full.ROOT)) for p in paths};result={}
 with patch.object(search,'collect_pages',lambda:paths):_,fresh=search.build()
 manifest=full.read_json(search.OUTPUT);unique=set()
 for lang,records in fresh.items():
  for record in records:
   if lang in full.LANGS:
    slug=record['u'].rsplit('/',1)[1].removesuffix('.html')
    data=full.read_json(full.base(series)/'translations'/lang/(slug+'.json'))
    record['t']=data['title']
    if slug!='index':record['x']=data['deck']
  p=search.CHUNKS_DIR/(lang.lower()+'.json');chunk=full.read_json(p);new={r['u']:r for r in records}
  chunk['records']=[new.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
  chunk['records'].extend(new.values());result[p]=search.serialized(chunk)
  manifest['languages'][lang]['count']=len(chunk['records']);unique.update(r['u'] for r in chunk['records'])
 manifest['record_count']=len(unique);result[search.OUTPUT]=search.serialized(manifest)
 p=full.ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
 entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(p).getroot()}
 for page in paths:
  canonical=parse_page(page).canonical
  assert canonical.startswith('https://nondubito.net/essays/'+series+'/')
  entries[canonical]=max(entries.get(canonical,DATE),DATE)
 result[p]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('series',choices=full.SUPPORTED);p.add_argument('--check',action='store_true');a=p.parse_args()
 changed=[]
 for path,value in outputs(a.series).items():
  if path.read_text()!=value:
   changed.append(str(path.relative_to(full.ROOT)))
   if not a.check:path.write_text(value)
 if a.check and changed:print('Stale:',', '.join(changed));return 1
 print(('Verified' if a.check else 'Refreshed')+' scoped search and sitemap; '+str(len(changed))+' files changed')
 return 0
if __name__=='__main__':raise SystemExit(main())

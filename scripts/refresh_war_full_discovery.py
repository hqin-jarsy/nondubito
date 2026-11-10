#!/usr/bin/env python3
"""Refresh only War Theory's search entries and sitemap dates after review."""
import argparse,json,xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
import build_war_full_editions as full
from build_sitemap import parse_page,sitemap_xml
DATE='2026-11-10'

def outputs():
 rendered=full.render()
 if len(rendered)!=102:raise ValueError("Expected 102 reviewed War Theory pages")
 stale=[str(p.relative_to(full.ROOT)) for p,text in rendered.items() if p.read_text()!=text]
 if stale:raise ValueError("Render reviewed public pages before discovery refresh: "+", ".join(stale))
 paths=sorted(full.DIRECTORY.rglob('*.html'))
 assert set(paths)==set(rendered),'Unexpected War HTML outside the reviewed edition'
 scope={str(p.relative_to(full.ROOT)) for p in paths};result={}
 with patch.object(search,'collect_pages',lambda:paths):_,fresh=search.build()
 manifest=full.read(search.OUTPUT);unique=set()
 for lang,records in fresh.items():
  for record in records:
   if lang in full.LANGS:
    slug=record['u'].rsplit('/',1)[1].removesuffix('.html');data=full.load_index(lang) if slug=='index' else full.load(lang,slug)
    record['t']=data['title']
    if slug!='index':record['x']=data['deck']
   elif lang=='en':
    slug=record['u'].rsplit('/',1)[1].removesuffix('.html')
    data=full.primary_index_data('en') if slug=='index' else full.effective.english_metadata(slug)
    record['t']=data['title']
    if slug!='index':record['x']=data['deck']
  path=search.CHUNKS_DIR/(lang.lower()+'.json');chunk=full.read(path);new={r['u']:r for r in records}
  chunk['records']=[new.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']];chunk['records'].extend(new.values());result[path]=search.serialized(chunk)
  manifest['languages'][lang]['count']=len(chunk['records']);unique.update(r['u'] for r in chunk['records'])
 manifest['record_count']=len(unique);result[search.OUTPUT]=search.serialized(manifest)
 path=full.ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
 entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(path).getroot()}
 for page in paths:
  canonical=parse_page(page).canonical;assert canonical.startswith('https://nondubito.net/essays/war/')
  entries[canonical]=max(entries.get(canonical,DATE),DATE)
 result[path]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
 return result

def snapshot_inputs():
 # Capture every shared output and public War page before generating discovery.
 # Validate the complete set before the first write, so a concurrent local edit
 # cannot be silently overwritten by an earlier in-memory representation.
 paths={search.OUTPUT,full.ROOT/'sitemap.xml',*search.CHUNKS_DIR.glob('*.json'),*full.DIRECTORY.rglob('*.html')}
 return {path:full.file_sha(path) for path in paths}

def write_outputs(result,baseline,check=False):
 assert all(path in baseline for path in result),'Unknown discovery output'
 for path,digest in baseline.items():
  assert full.file_sha(path)==digest,('Discovery inputs changed concurrently',str(path))
 changed=[str(path.relative_to(full.ROOT)) for path,value in result.items() if path.read_text()!=value]
 if not check:
  for path,value in result.items():
   if path.read_text()!=value:path.write_text(value)
 return changed

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 baseline=snapshot_inputs();result=outputs();changed=write_outputs(result,baseline,a.check)
 if a.check and changed:print('Stale:',', '.join(changed));return 1
 print(('Verified' if a.check else 'Refreshed')+' War Theory search/sitemap; '+str(len(changed))+' files changed');return 0
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Create offline Hans-Hant drafts using the site's existing conversion engine.

Conversion is not review. Requires finalized source and still needs an independent
Traditional Chinese receipt before the publication renderer can accept output.
"""
import json
from pathlib import Path
import build_wwii_full_editions as b
from build_emperor_traditional import TraditionalConverter
from prepare_action_sources import Document,Node,one

def main():
 state=b.read_json(b.DATA/'source-finalization.json');assert state['status']=='approved' and not state['unresolved'],'Awaiting source decisions'
 assert state['source_files']=={s+'.json':b.file_sha(b.DATA/'sources'/(s+'.json')) for s in b.SLUGS}
 converter=TraditionalConverter()
 try:
  d=Document((b.DATA/'baseline/index.html').read_text());body=b.find(d,'essay-body');paras=[n for n in body.children if isinstance(n,Node) and n.tag=='p' and not n.has('lang-zh') and not n.has('lang-en')]
  index={'intro':[converter.convert(n.text().strip()) for n in paras],'decks':[],'engine':'macOS CoreFoundation Hans-Hant, existing site engine','review':'Mechanical draft; semantic and character review required.'}
  for slug in b.SLUGS:
   s=b.source(slug);card=one(d.root.walk(),lambda n:n.tag=='a' and n.has('essay-card') and n.attrs.get('href')==slug+'.html','card');deck=one(card.walk(),lambda n:n.has('card-desc'),'deck').text();index['decks'].append(converter.convert(deck))
   item=dict(s,language='zh-Hant',title=converter.convert(s['title']),deck=converter.convert(deck),body=[converter.convert(x) for x in s['body']],review='Offline site-engine conversion draft; independent character and semantic review required.')
   b.validate(item,'zh-Hant',slug);p=b.DATA/'translations/zh-Hant'/(slug+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n')
  (b.DATA/'index-traditional.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
 finally:converter.close()
 print('Prepared five Traditional Chinese drafts and index metadata; not publication-certified')
if __name__=='__main__':main()

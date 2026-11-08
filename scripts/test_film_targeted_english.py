"""Complete-English and preservation checks independent of the foreign package."""
import hashlib
import json
import re
import subprocess
import unittest
import markdown
import film_targeted_editions as t
from prepare_action_sources import Document,one

class TargetedEnglish(unittest.TestCase):
 def test_full_source_and_only_approved_chinese_changes(self):
  receipt=json.loads((t.DATA/'batch04-received.json').read_text())
  for film in receipt['films']:
   for ep,slug in enumerate(film['chapters'],1):
    p=t.ROOT/'essays/film'/film['slug']/(slug+'.html');text=p.read_text();doc=Document(text)
    en=(t.DATA/'reviewed'/film['slug']/'en'/f'{ep:02}.md').read_text();zh=(t.DATA/'reviewed'/film['slug']/'zh'/f'{ep:02}.md').read_text()
    self.assertEqual(len(re.findall(r'^## ',en,re.M)),len(re.findall(r'^## ',zh,re.M)))
    self.assertEqual(len(re.split(r'\n\s*\n',en.strip())),len(re.split(r'\n\s*\n',zh.strip())))
    self.assertEqual(en.count('**'),zh.count('**'))
    self.assertGreater(len(en.split()),1500)
    body=one(doc.root.walk(),lambda n:n.tag=='div' and n.has('essay-body','lang-en'),'English body')
    self.assertIn(markdown.markdown(en.split('\n',1)[1]),doc.raw(body))
    old=subprocess.check_output(['git','show',receipt['baseline_commit']+':'+str(p.relative_to(t.ROOT))],cwd=t.ROOT).decode();previous=Document(old)
    a=one(doc.root.walk(),lambda n:n.tag=='div' and n.has('essay-body','lang-zh'),'Chinese body')
    b=one(previous.root.walk(),lambda n:n.tag=='div' and n.has('essay-body','lang-zh'),'Chinese body')
    self.assertEqual(doc.raw(a),t.revised_chinese_body(previous.raw(b),film['slug'],ep))
    for c in t.approved_changes(film['slug'],ep):
     self.assertIn(c['zh_after'],zh);self.assertIn(c['en_after'],en)
     self.assertNotIn(c['zh_before'],zh);self.assertNotIn(c['en_before'],en)
    self.assertEqual(t.overlay(text,film,p.name),text)
    js=p.parent/'zh-hant-data'/(slug+'.js')
    deltas=json.loads((t.DATA/'review/approved-traditional.json').read_text())['files']
    relative=str(js.relative_to(t.ROOT))
    if relative not in deltas:self.assertEqual(hashlib.sha256(js.read_bytes()).hexdigest(),receipt['protected'][relative])
    else:
     oldjs=subprocess.check_output(['git','show',receipt['baseline_commit']+':'+relative],cwd=t.ROOT).decode()
     expected=json.loads(re.search(r'var variants\s*=\s*(\{.*?\});',oldjs,re.S)[1]);actual=json.loads(re.search(r'var variants\s*=\s*(\{.*?\});',js.read_text(),re.S)[1])
     for key in deltas[relative]['removed']:expected.pop(key,None)
     expected.update(deltas[relative]['added']);self.assertEqual(actual,expected)
     self.assertEqual(t.approved_traditional_outputs()[js],js.read_text())
 def test_known_english_clothing_error_removed(self):
  s=(t.DATA/'reviewed/raise-the-red-lantern/en/01.md').read_text().lower()
  self.assertIn('black-and-white',s);self.assertNotIn('bridal red',s)

if __name__=='__main__':unittest.main()

"""Engineering preview is memory-only; --release checks real accepted outputs."""
import re,sys,unittest
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_math_history_full_editions as full
import build_math_history as base
from test_recent_fiction import Page
RELEASE='--release' in sys.argv
if RELEASE:sys.argv.remove('--release')
class FullMathematics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.primary=base.outputs(full=False)
  if RELEASE:cls.pages=full.render()
  else:
   with patch.object(full,'acceptance',return_value={'status':'MOCK ENGINEERING ONLY'}):cls.pages=full.render(cls.primary,guard=False)
 def test_inventory(self):
  self.assertEqual(len(self.pages),156)
  self.assertEqual(26*3+130,208)
 def test_full_text_and_formulas(self):
  for lang in full.LANGS:
   for i in range(1,26):
    d=full.manuscript(lang,i);s=self.pages[full.SERIES/lang/f'ep{i:02d}.html']
    self.assertIn(d['body'],s);self.assertEqual(d['body'].count('<h2 '),9)
    self.assertGreater(d['body'].count('<p>'),30)
    self.assertIn(full.esc(d['deck']),s)
    raw=(full.DATA/lang/f'ep{i:02d}.md').read_text().split('\n## ',1)[1]
    self.assertEqual(raw.count('`')//2,d['body'].count('<code>'))
 def test_primary_prose_untouched(self):
  for p,s in self.primary.items():
   for body in re.findall(r'<div class="math-prose.*?</div>',s,re.S):self.assertIn(body,self.pages[p])
 def test_navigation_metadata_and_analytics(self):
  for p,s in self.pages.items():
   page=Page(s);self.assertEqual(page.errors,[],p);self.assertEqual(len(page.ids),len(set(page.ids)))
   self.assertEqual(s.count('beacon.min.js'),1)
   self.assertEqual(s.count('data-math-language='),8)
   for href in page.links:
    u=urlsplit(href)
    if u.scheme or u.netloc:continue
    dest=(p.parent/unquote(u.path)).resolve() if u.path else p
    self.assertTrue(dest in self.pages or dest.is_file(),(p,href))
    if u.fragment and dest in self.pages:self.assertIn(unquote(u.fragment),Page(self.pages[dest]).ids)
   if p.parent!=full.SERIES:
    self.assertIn(f'<html lang="{p.parent.name}"',s)
    self.assertNotIn('site-shell.js',s)
 def test_search_first_and_last_titles_in_all_languages(self):
  import build_search_index as search
  from pathlib import Path
  original=Path.read_text
  def preview_read(path,*args,**kwargs):
   return self.pages[path] if path in self.pages else original(path,*args,**kwargs)
  with patch.object(search,'collect_pages',return_value=list(self.pages)),patch.object(Path,'read_text',preview_read):
   _,chunks=search.build()
  for lang in full.LANGS:
   for i in [1,25]:
    url=f'essays/math-history/{lang}/ep{i:02d}.html'
    record=next(r for r in chunks[lang] if r['u']==url)
    self.assertIn(full.manuscript(lang,i)['title'],record['t'])
    self.assertLessEqual(len(record['q']),700)
   self.assertTrue(any(r['u']==f'essays/math-history/{lang}/index.html' for r in chunks[lang]))
  for lang in ['en','zh-Hans','zh-Hant']:
   for i in [1,25]:self.assertTrue(any(r['u']==f'essays/math-history/ep{i:02d}.html' for r in chunks[lang]))
 def test_fail_closed_acceptance(self):
  with patch.object(full,'read',return_value={'status':'pending'}):
   with self.assertRaisesRegex(AssertionError,'pending|Missing'):full.acceptance()
 def test_manual_change_guard(self):
  from tempfile import TemporaryDirectory
  from pathlib import Path
  with TemporaryDirectory() as temp:
   root=Path(temp);p=root/'ep01.html';p.write_text('manual change')
   with patch.object(full,'SERIES',root):
    with self.assertRaisesRegex(AssertionError,'Unknown manual'):full.protect(p,'generated')
 def test_cache_without_corefoundation_and_missing_key(self):
  import json
  from tempfile import TemporaryDirectory
  from pathlib import Path
  # Capture only in memory. No cache or published page is refreshed here.
  with TemporaryDirectory() as temp:
   cache=Path(temp)/'cache.json'
   if base.HANT_CACHE.exists():cache.write_bytes(base.HANT_CACHE.read_bytes())
   else:
    with patch.object(base,'REFRESH_HANT',True):
     c=base.Converter()
     try:
      items=base.load_items();base.render_index(items,c)
      for item in items:base.render_article(item,items,c)
      for sample in base.HANT_REGRESSION_INPUTS:c.convert(sample)
      cache.write_text(json.dumps(c.recorded,ensure_ascii=False))
     finally:c.close()
   with patch.object(base,'HANT_CACHE',cache),patch.object(base.BaseConverter,'__init__',side_effect=AssertionError('CoreFoundation must not initialize')):
    self.assertEqual(base.outputs(full=False),self.primary)
    c=base.Converter()
    with self.assertRaisesRegex(AssertionError,'cache stale'):c.convert('MOCK MISSING CACHE KEY')
    c.close()
 def test_receipt_requires_all_real_inputs(self):
  names={str(p.relative_to(full.ROOT)) for p in full.required_inputs()}
  prefix='data/math-history-full/'
  self.assertIn(prefix+'source-manifest.json',names)
  self.assertIn('data/math-history/traditional-cache.json',names)
  for i in range(1,26):
   self.assertIn(prefix+f'source/ep{i:02d}.json',names)
   self.assertIn(f'data/math-history/{i:02d}.json',names)
   self.assertIn(f'data/math-history/{i:02d}-source.json',names)
   for lang in full.LANGS:self.assertIn(prefix+f'{lang}/ep{i:02d}.md',names)
  for lang in full.LANGS:self.assertIn(prefix+lang+'/ui.json',names)
  for p in (full.DATA/'review').glob('approved-*'):self.assertIn(str(p.relative_to(full.ROOT)),names)
 def test_receipt_missing_and_changed_hashes_fail(self):
  source=full.DATA/'source-manifest.json'
  with patch.object(full,'required_inputs',return_value=[source]),patch.object(full,'read',return_value={'status':'accepted','files':{}}):
   with self.assertRaisesRegex(AssertionError,'Incomplete'):full.acceptance()
  receipt={'status':'accepted','files':{str(source.relative_to(full.ROOT)):'wrong digest'}}
  with patch.object(full,'required_inputs',return_value=[source]),patch.object(full,'read',return_value=receipt):
   with self.assertRaisesRegex(AssertionError,'Reviewed input drift'):full.acceptance()
 def test_pending_never_regresses_released_output(self):
  from tempfile import TemporaryDirectory
  from pathlib import Path
  import json
  with TemporaryDirectory() as temp:
   root=Path(temp);data=root/'data';series=root/'series';(data/'review').mkdir(parents=True);series.mkdir()
   (data/'review/accepted.json').write_text(json.dumps({'status':'pending'}))
   (data/'last-build.json').write_text('{}')
   with patch.object(full,'DATA',data),patch.object(full,'SERIES',series):
    with self.assertRaisesRegex(AssertionError,'Cannot regress'):full.upgrade_outputs({})
   (data/'last-build.json').unlink();(series/'de').mkdir();(series/'de/index.html').write_text('already published')
   with patch.object(full,'DATA',data),patch.object(full,'SERIES',series):
    with self.assertRaisesRegex(AssertionError,'Cannot regress'):full.upgrade_outputs({})
   self.assertEqual((series/'de/index.html').read_text(),'already published')
 def test_pending_primary_edits_cannot_publish(self):
  from tempfile import TemporaryDirectory
  from pathlib import Path
  with TemporaryDirectory() as temp:
   root=Path(temp);data=root/'data';series=root/'series';data.mkdir();series.mkdir()
   p=series/'ep01.html';p.write_text('frozen published primary')
   manifest={'snapshots':{'ep01.html':full.digest(p.read_text())}}
   with patch.object(full,'DATA',data),patch.object(full,'SERIES',series),patch.object(full,'read',return_value=manifest):
    self.assertEqual(full.upgrade_outputs({p:p.read_text()}),{p:p.read_text()})
    with self.assertRaisesRegex(AssertionError,'primary changes cannot be published'):full.upgrade_outputs({p:'pending new prose'})
   self.assertEqual(p.read_text(),'frozen published primary')
 def test_pending_old_builder_with_changed_source_preserves_public_files(self):
  import copy,json
  from pathlib import Path
  from tempfile import TemporaryDirectory
  with TemporaryDirectory() as temp:
   root=Path(temp);data=root/'data';series=root/'series';data.mkdir();series.mkdir()
   for p,text in self.primary.items():(series/p.name).write_text(text)
   before={p.name:p.read_bytes() for p in series.glob('*.html')}
   (data/'source-manifest.json').write_text(json.dumps({'snapshots':{n:full.digest(b) for n,b in before.items()}}))
   changed=copy.deepcopy(base.load_items());changed[0]['title_en']+=' MOCK PENDING SOURCE CHANGE'
   with patch.object(base,'TARGET',series),patch.object(full,'SERIES',series),patch.object(full,'DATA',data),patch.object(base,'load_items',return_value=changed):
    with self.assertRaisesRegex(AssertionError,'primary changes cannot be published'):base.outputs()
   self.assertEqual({p.name:p.read_bytes() for p in series.glob('*.html')},before)
 def test_full_release_requires_all_primary_pages(self):
  with patch.object(full,'acceptance',return_value={'status':'MOCK ONLY'}):
   with self.assertRaisesRegex(AssertionError,'26 primary'):full.render({},guard=False)
 def test_library_card_is_scoped_and_complete(self):
  import refresh_math_full_discovery as discovery
  p=full.ROOT/'library.html';before=p.read_text();after=discovery.library_outputs()[p]
  pattern=r'<a href="essays/math-history/index\.html" class="series-card series-card-flagship">.*?</a>'
  old=re.search(pattern,before,re.S).group();new=re.search(pattern,after,re.S).group()
  for label in ['25 essays · Eight languages','25篇 · 八语全文','25篇 · 八語全文']:self.assertIn(label,new)
  self.assertEqual(before.replace(old,'MATH CARD',1),after.replace(new,'MATH CARD',1))
  self.assertEqual(p.read_text(),before)
 def test_previous_discovery_preserves_newer_shared_sitemap_dates(self):
  import xml.etree.ElementTree as ET
  import refresh_film_full_discovery as film
  import refresh_wire_full_discovery as wire
  import refresh_chernobyl_full_discovery as chernobyl
  import refresh_satc_full_discovery as satc
  ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
  def dates(text):return {e.find(ns+'loc').text:e.find(ns+'lastmod').text for e in ET.fromstring(text)}
  sitemap=full.ROOT/'sitemap.xml';current=dates(sitemap.read_text())
  for result in [film.render()[0],wire.discovery(),chernobyl.discovery(),satc.discovery()]:
   rendered=dates(result[sitemap])
   for url,date in current.items():self.assertGreaterEqual(rendered[url],date,url)
 def test_previous_discovery_upgrades_older_shared_sitemap_dates(self):
  import xml.etree.ElementTree as ET
  import refresh_film_full_discovery as film
  import refresh_wire_full_discovery as wire
  import refresh_chernobyl_full_discovery as chernobyl
  import refresh_satc_full_discovery as satc
  ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
  original_parse=ET.parse
  shared={'https://nondubito.net/','https://nondubito.net/latest.html'}
  def aged_parse(*args,**kwargs):
   tree=original_parse(*args,**kwargs)
   for entry in tree.getroot():
    if entry.find(ns+'loc').text in shared:entry.find(ns+'lastmod').text='2000-01-01'
   return tree
  for module in [film,wire,chernobyl,satc]:
   with patch.object(ET,'parse',side_effect=aged_parse):
    result=module.render()[0] if module is film else module.discovery()
   dates={e.find(ns+'loc').text:e.find(ns+'lastmod').text for e in ET.fromstring(result[full.ROOT/'sitemap.xml'])}
   for url in shared:self.assertEqual(dates[url],module.targeted.DATE if module is film else module.DATE)
 def test_release_outputs(self):
  if not RELEASE:self.skipTest('No publication during memory-only preview')
  for p,s in self.pages.items():self.assertEqual(p.read_text(),s,p)
if __name__=='__main__':unittest.main()

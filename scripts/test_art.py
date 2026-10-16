#!/usr/bin/env python3
"""Art publishing invariants: full prose, editions, local targets and discovery."""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit, unquote
import build_art as b
from build_content_registry import scan_page


class Parse(HTMLParser):
    def __init__(self,source):
        super().__init__(); self.tags=[]; self.feed(source)
    def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))


class ArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=b.outputs(); cls.works=json.loads((b.DATA/'works.json').read_text())

    def test_editions(self):
        self.assertEqual(len(self.pages),8*(len(self.works)+1))
        for path,s in self.pages.items():
            self.assertEqual(s,path.read_text(),path)
            tags=Parse(s).tags
            self.assertEqual(sum(t=='h1' for t,a in tags),1)
            self.assertEqual(sum(t=='a' and 'data-edition' in a for t,a in tags),8)
            self.assertEqual(sum(t=='a' and 'aria-current' in a for t,a in tags),1)
            self.assertEqual(sum(t=='link' and a.get('rel')=='alternate' for t,a in tags),9)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
            self.assertEqual(schema['url'],b.canonical(path))
            scanned=scan_page(b.ROOT,path)
            self.assertEqual(scanned['languages'],[schema['inLanguage']])
            self.assertEqual(scanned['domain'],'sae-philosophy')

    def test_every_paragraph_preserved(self):
        for w in self.works:
            for lang in b.LANGS:
                s=self.pages[b.location(lang,w)]
                for block in b.load(w,lang)[2:]:
                    if block.startswith(('## ','![')): continue
                    self.assertIn(b.inline(block),s,(lang,block[:60]))
                tags=Parse(s).tags
                image_count=sum(block.startswith('![') for block in b.load(w,lang))
                self.assertEqual(sum(t=='figure' for t,a in tags),image_count)
                self.assertEqual(sum(t=='figcaption' for t,a in tags),image_count)
                self.assertEqual(sum(t=='details' and a.get('class')=='optional-reading' for t,a in tags),1)
                self.assertIn(b.guide(lang,b.location(lang,w)),s)

    def test_targets_and_anchors(self):
        for path,s in self.pages.items():
            tags=Parse(s).tags; ids=[a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids),len(set(ids)))
            for tag,a in tags:
                for key in ('href','src'):
                    if key not in a: continue
                    url=urlsplit(a[key])
                    if url.scheme or url.netloc: continue
                    target=(path.parent/unquote(url.path)).resolve() if url.path else path
                    if target.is_dir(): target=target/'index.html'
                    self.assertTrue(target.is_file(),(path,a[key]))
                    if url.fragment and target.suffix=='.html':
                        destids={attrs['id'] for _,attrs in Parse(target.read_text()).tags if 'id' in attrs}
                        self.assertIn(url.fragment,destids,(path,a[key]))
                if tag=='img':
                    self.assertTrue(a.get('alt')); self.assertIn('width',a); self.assertIn('height',a)
                    for item in a['srcset'].split(','):
                        self.assertTrue((path.parent/item.strip().split()[0]).is_file())

    def test_originals_unchanged(self):
        for w in self.works:
            recovered={}
            if w.get('restored_images'):
                recovered={r['path']:r for r in json.loads((b.DATA/w['id']/'source/site-image-recovery.json').read_text())}
            sums=(b.DATA/w['id']/'source/SHA256SUMS.txt').read_text().splitlines()
            for line in sums:
                digest,name=line.split(maxsplit=1)
                if name.startswith('images/'):
                    path=b.TARGET/'images'/w['id']/name.removeprefix('images/')
                    record=recovered.get(name)
                    if record and 'crop_box' in record:
                        from PIL import Image
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record['sha256'])
                        with Image.open(path) as detail, Image.open(b.TARGET/'images'/w['id']/Path(record['source_image']).name) as full:
                            crop=full.crop(tuple(record['crop_box']))
                            self.assertEqual(detail.size,crop.size)
                            self.assertEqual(detail.tobytes(),crop.tobytes())
                            self.assertEqual(detail.info.get('icc_profile'),full.info.get('icc_profile'))
                    else:
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)

    def test_reviewed_manuscripts_and_structure(self):
        entries=[e for p in b.DATA.glob('publication-*.json') for e in json.loads(p.read_text()).get('works',[])]
        self.assertEqual({e['work'] for e in entries},{w['id'] for w in self.works if w['id']!='vermeer'})
        for entry in entries:
            work=next(w for w in self.works if w['id']==entry['work'])
            for edition in entry['editions']:
                code=edition['language']
                source=b.DATA/work['id']/f"{work['source_prefix']}_{code}.md"
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),edition['published_sha256'])
                self.assertGreater(edition['character_ratio'],.95)
                lang=next(k for k,v in b.LANGS.items() if v[0]==code)
                blocks=b.load(work,lang)
                self.assertEqual(sum(p.startswith('## ') for p in blocks),work['main_sections']+2)
                self.assertNotRegex(source.read_text(),r'\]\((README|QUALITY_NOTE|QUALITY_REVIEW)\.md\)')

    def test_discovery(self):
        sitemap=(b.ROOT/'sitemap.xml').read_text()
        for lang,(code,_,_) in b.LANGS.items():
            records=json.loads((b.ROOT/f'data/search/{code.lower()}.json').read_text())['records']
            urls={r['u'] for r in records}
            for path in [b.location(lang)]+[b.location(lang,w) for w in self.works]:
                self.assertIn(path.relative_to(b.ROOT).as_posix(),urls)
                self.assertTrue(b.canonical(path) in sitemap, f'Missing sitemap URL: {b.canonical(path)}')
        for folder in ('','en/','zh-hant/'):
            self.assertIn('id="art"',(b.ROOT/f'essays/aesthetics/{folder}index.html').read_text())

    def test_sculpture_category(self):
        work=next(w for w in self.works if w['id']=='degas')
        for lang in b.LANGS:
            shelf=self.pages[b.location(lang)]
            self.assertIn('href="#western-painting"',shelf)
            self.assertIn('href="#western-sculpture"',shelf)
            source=self.pages[b.location(lang,work)]
            self.assertIn(b.CATEGORIES['western-sculpture'][lang],source)
            self.assertNotIn(b.CATEGORIES['western-painting'][lang],source)
            self.assertIn('?lang='+lang+'#western-sculpture',source)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
            self.assertEqual(schema['about']['@type'],'Sculpture')
            self.assertEqual(sum(t=='figure' for t,a in Parse(source).tags),5)

    def test_sculpture_expansion(self):
        counts = {'rodin':3, 'canova':4, 'satyr':3, 'eros':3, 'jonah':3,
                  'madonna':6, 'dragon':1, 'messerschmidt':4, 'shaw':1}
        sculptures = [w for w in self.works if w['category']=='western-sculpture']
        self.assertEqual(len(sculptures),10)
        for w in sculptures:
            if w['id'] not in counts: continue
            for lang in b.LANGS:
                source=self.pages[b.location(lang,w)]
                self.assertEqual(sum(t=='figure' for t,a in Parse(source).tags),counts[w['id']])
                self.assertIn('?lang='+lang+'#western-sculpture',source)
                self.assertIn(b.canonical(b.location(lang,w)),self.pages[b.location(lang,w)])
                self.assertIn('lang="en"',source)
        # There is no implied local frontal image of the Shaw model.
        shaw=next(w for w in sculptures if w['id']=='shaw')
        for lang in b.LANGS:
            self.assertIn(shaw['about'],self.pages[b.location(lang,shaw)])


if __name__=='__main__': unittest.main()

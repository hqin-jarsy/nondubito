#!/usr/bin/env python3
"""Art publishing invariants: full prose, editions, local targets and discovery."""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
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
        ledger=json.loads((b.DATA/'web-images.json').read_text())
        cls.image_urls={b.preview_url({'id':key.split('/')[0]},key.split('/')[1],width)
                        for key in ledger for width in (640,1280)}

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

    def test_calligraphy_publication_markup(self):
        for work in self.works:
            if not work['id'].startswith('calligraphy-'): continue
            for lang in b.LANGS:
                page=self.pages[b.location(lang,work)]
                self.assertNotRegex(page,r'\[[^\]\n]+\]\[[^\]\n]+\]')
                self.assertNotIn('<p>&gt; ',page)
                tags=Parse(page).tags
                for tag,attrs in tags:
                    if tag=='a' and attrs.get('href','').endswith('.md'):
                        self.assertTrue(attrs['href'].startswith('https://nondubito.net/data/art/'),attrs)
                if work.get('unknown_creator'):
                    schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)[1])
                    self.assertNotIn('creator',schema['about'])

    def test_every_paragraph_preserved(self):
        for w in self.works:
            for lang in b.LANGS:
                s=self.pages[b.location(lang,w)]
                links=b.manuscript_links(w) if w.get('manuscript_details') else None
                for block in b.load(w,lang)[2:]:
                    if block.startswith(('## ','### ','![')) or block=='---': continue
                    if w.get('manuscript_details') and block.startswith(('<details>','</details>')): continue
                    if w.get('source_tail') and block.startswith('- '):
                        for line in block.splitlines(): self.assertIn(b.inline(line.removeprefix('- '),links),s)
                    else:
                        rendered=b.inline(block,links)
                        if w.get('manuscript_details') and block.startswith('> '):
                            quote='\n'.join(line[1:].removeprefix(' ') if line.startswith('>') else line for line in block.splitlines())
                            for paragraph in quote.split('\n\n'):
                                self.assertIn(b.inline(paragraph,links).replace('  \n','<br>\n'),s)
                            continue
                        if w.get('manuscript_details'): rendered=rendered.replace('  \n','<br>\n')
                        self.assertIn(rendered,s,(lang,block[:60]))
                tags=Parse(s).tags
                image_count=sum(block.startswith('![') for block in b.load(w,lang))
                self.assertEqual(sum(t=='figure' for t,a in tags),image_count)
                self.assertEqual(sum(t=='figcaption' for t,a in tags),image_count)
                expected=int(w.get('has_optional',True))
                self.assertEqual(sum(t=='details' and a.get('class')=='optional-reading' for t,a in tags),expected)
                if expected: self.assertIn(b.guide(lang,b.location(lang,w)),s)

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
                    self.assertIn(a['src'],self.image_urls)
                    for item in a['srcset'].split(','):
                        self.assertIn(item.strip().split()[0],self.image_urls)

    def test_archived_originals_and_preserved_previews(self):
        ledger=json.loads((b.DATA/'web-images.json').read_text())
        sizes=json.loads((b.DATA/'images.json').read_text())
        self.assertEqual(set(ledger),set(sizes))
        self.assertFalse(list((b.TARGET/'images').rglob('*.jpg')))
        self.assertFalse(list((b.TARGET/'images').rglob('*.png')))
        expected_previews=set()
        for w in self.works:
            recovered={}
            if w.get('restored_images'):
                recovered={r['path']:r for r in json.loads((b.DATA/w['id']/'source/site-image-recovery.json').read_text())}
            sums=(b.DATA/w['id']/'source/SHA256SUMS.txt').read_text().splitlines()
            for line in sums:
                digest,name=line.split(maxsplit=1)
                if name.startswith('images/'):
                    filename=name.removeprefix('images/')
                    entry=ledger[w['id']+'/'+filename]
                    record=recovered.get(name)
                    if record and 'crop_box' in record:
                        digest=record['sha256']
                    self.assertEqual(entry['original_sha256'],digest)
                    self.assertEqual(entry['dimensions'],sizes[w['id']+'/'+filename])
                    for width in (640,1280):
                        url=b.preview_url(w,filename,width)
                        self.assertNotIn(url,expected_previews)
                        expected_previews.add(url)
                        preview=entry['previews'][str(width)]
                        self.assertRegex(preview['sha256'],r'^[0-9a-f]{64}$')
                        self.assertGreater(preview['bytes'],0)
                        self.assertEqual(preview['dimensions'][0],min(width,entry['dimensions'][0]))
        self.assertEqual(expected_previews,self.image_urls)
        # Live bytes are checked separately by verify_art_images.py, not during
        # deterministic offline tests. Image binaries no longer belong in Git.
        self.assertFalse(list((b.TARGET/'images').rglob('*.webp')))

    def test_museum_links_and_social_images(self):
        for w in self.works:
            doc='IMAGE_CREDITS.md' if w.get('image') else 'IMAGE_LINKS.md'
            self.assertIn(w['about'],(b.DATA/w['id']/'source'/doc).read_text())
            self.assertTrue(w['about'].startswith('https://'))
            for lang in b.LANGS:
                source=self.pages[b.location(lang,w)]
                figures=re.findall(r'<figure>(.*?)</figure>',source,re.S)
                for figure in figures:
                    tags=Parse(figure).tags
                    links=[a for t,a in tags if t=='a' and a.get('target')=='_blank']
                    self.assertEqual(len(links),2)
                    image=next(a for t,a in tags if t=='img')
                    name=next(name for name in w.get('inline_images',{}) if image['src']==b.preview_url(w,name,640)) if w.get('inline_images') else None
                    target=b.image_click_target(w,name) if name else w['about']
                    for link in links:
                        self.assertEqual(link['href'],target)
                        self.assertEqual(link['target'],'_blank')
                        self.assertIn('noopener',link['rel'])
                    self.assertIn(b.image_link_label(w,lang),figure)
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
                if not w.get('image'):
                    self.assertEqual(w['image_mode'],'external-links')
                    self.assertNotIn('<img ',source)
                    self.assertNotIn('og:image',source)
                    self.assertNotIn('image',schema)
                    self.assertIn('class="art-viewing"',source)
                    self.assertIn(b.image_link_label(w,lang),source)
                    self.assertIn('id="image-credits"',source)
                    continue
                self.assertIn(b.IMAGE_STORAGE_NOTES[lang],source)
                self.assertEqual(schema['image'],b.preview_url(w,w['image']))
                self.assertIn(schema['image'],self.image_urls)
                self.assertIn(f'property="og:image" content="{schema["image"]}"',source)

    def test_image_regeneration_requires_offline_archive(self):
        with self.assertRaises(ValueError): b.prepare_images('vermeer')
        with self.assertRaises(FileNotFoundError):
            b.prepare_images('vermeer',b.DATA/'nonexistent-offline-archive')

    def test_legacy_images_migrated(self):
        records=json.loads((b.ROOT/'data/legacy-image-hosting.json').read_text())
        pages=[b.ROOT/'about.html',b.ROOT/'essays/artist_dead.html',
               *list((b.ROOT/'essays/aesthetics').glob('*.html'))]
        sources='\n'.join(p.read_text() for p in pages)
        self.assertEqual(len(records),13)
        for old,record in records.items():
            self.assertFalse((b.ROOT/old).exists())
            self.assertEqual(record['url'],'https://images.nondubito.net/legacy/'+record['filename'])
            if not record.get('archived_unused'):
                self.assertTrue(record['url'] in sources,record['url'])
            self.assertRegex(record['sha256'],r'^[0-9a-f]{64}$')
        self.assertTrue((b.ROOT/'favicon.svg').is_file())
        self.assertTrue((b.ROOT/'apple-touch-icon.png').is_file())

    def test_image_regeneration_from_offline_archive(self):
        from PIL import Image
        # A tiny isolated fixture proves future imports need not put originals
        # into the deployment tree. It never overwrites published previews.
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); data=root/'data'; target=root/'site'; originals=root/'offline'
            work={'id':'fixture','source_prefix':'fixture'}
            (data/'fixture').mkdir(parents=True); (originals/'fixture').mkdir(parents=True)
            (data/'works.json').write_text(json.dumps([work]))
            (data/'images.json').write_text('{}')
            for code,_,_ in b.LANGS.values():
                (data/'fixture'/f'fixture_{code}.md').write_text('# Test\n\n![Detail](images/detail.png)')
            original=originals/'fixture/detail.png'
            Image.new('RGB',(1500,1000),(100,120,140)).save(original)
            digest=hashlib.sha256(original.read_bytes()).hexdigest()
            with patch.object(b,'DATA',data), patch.object(b,'TARGET',target):
                previews=root/'upload/art'
                b.prepare_images('fixture',originals,previews)
                ledger=json.loads((data/'web-images.json').read_text())
                self.assertEqual(ledger['fixture/detail.png']['original_sha256'],digest)
                self.assertEqual(json.loads((data/'images.json').read_text())['fixture/detail.png'],[1500,1000])
                self.assertTrue((previews/b.preview_filename(work,'detail.png',640)).exists())
                self.assertTrue((previews/b.preview_filename(work,'detail.png',1280)).exists())
                self.assertFalse((target/'images/fixture/detail.png').exists())
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),digest)

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
                additional=int(work.get('has_optional',True)) if work.get('source_tail') else 2
                self.assertEqual(sum(p.startswith('## ') for p in blocks),work['main_sections']+additional)
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

    def test_calligraphy_full_text_and_separate_image_guide(self):
        work=next(w for w in self.works if w['id']=='calligraphy-su-shi-hanshi')
        for lang in b.LANGS:
            source=self.pages[b.location(lang,work)]
            self.assertIn('href="#chinese-calligraphy"',self.pages[b.location(lang)])
            self.assertIn(b.CATEGORIES['chinese-calligraphy'][lang],source)
            self.assertEqual(source.count('<figure>'),5)
            self.assertNotIn('&lt;details&gt;',source)
            self.assertNotIn('href="IMAGE_NOTES.',source)
            self.assertIn('id="viewing-notes"',source)
            if lang in ('ja','ko'): self.assertIn('href="#image-credits"',source)
            # The image/textual notes must not be trapped in the theory foldout.
            theory=source.index('class="optional-reading"')
            notes=source.index('id="viewing-notes"')
            self.assertIn('</div></details>',source[theory:notes])
            self.assertIn('<br>\n',source)  # Preserve the poems’ deliberate verse lines.
            for number,stem in [(0,'su_text_overview'),(6,'full_scroll_gallery_index')]:
                self.assertIn(b.preview_url(work,f'{number:02d}_{stem}.jpg'),source)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
            self.assertEqual(schema['about']['@type'],'VisualArtwork')
            self.assertIn('National Palace Museum',source)
        traditional=(b.DATA/work['id']/'01_hanshi_zh-Hant.md').read_text()
        self.assertIn('九重墳墓在万里也擬',traditional)
        self.assertIn('墳墓在萬里',traditional)  # Normalized poem text remains Traditional.

    def test_sculpture_expansion(self):
        counts = {'rodin':3, 'canova':4, 'satyr':3, 'eros':3, 'jonah':3,
                  'madonna':6, 'dragon':1, 'messerschmidt':4, 'shaw':1}
        sculptures = [w for w in self.works if w['category']=='western-sculpture']
        self.assertEqual(len(sculptures),20)
        counts.update({'girl-stele':2,'mourner':5,'voltaire':5,'horse':1,'ugolino':7,
                       'michelangelo-david':0,'apollo-daphne':0,'winged-victory':0,'bird-space':0,'hepworth':0})
        for w in sculptures:
            if w['id'] not in counts: continue
            for lang in b.LANGS:
                source=self.pages[b.location(lang,w)]
                self.assertEqual(sum(t=='figure' for t,a in Parse(source).tags),len(w['inline_images']) if w.get('inline_images') else counts[w['id']])
                self.assertIn('?lang='+lang+'#western-sculpture',source)
                self.assertIn(b.canonical(b.location(lang,w)),self.pages[b.location(lang,w)])
                self.assertIn('lang="en"',source)
        # There is no implied local frontal image of the Shaw model.
        shaw=next(w for w in sculptures if w['id']=='shaw')
        for lang in b.LANGS:
            self.assertIn(shaw['about'],self.pages[b.location(lang,shaw)])

    def test_nested_headings_and_link_only_cards(self):
        for lang in b.LANGS:
            index=self.pages[b.location(lang)]
            self.assertEqual(index.count('class="art-card art-card-text"'),sum(not w.get('image') for w in self.works))
            for tag,attrs in Parse(index).tags:
                if tag=='img': self.assertTrue(attrs['sizes'].endswith(', 240px'))
            for w in self.works:
                source=self.pages[b.location(lang,w)]
                self.assertNotIn('*',b.plain_title(w,lang))
                self.assertIn('<h1>'+b.esc(b.plain_title(w,lang))+'</h1>',source)
                headings=[p[4:] for p in b.load(w,lang) if p.startswith('### ') and not w.get('source_tail')]
                for heading in headings:
                    self.assertIn('<h3>'+b.esc(heading)+'</h3>',source)
                self.assertNotIn('<p>### ',source)
                self.assertNotIn('](IMAGE_LINKS.md)',source)
                if w.get('archival_image_note'):
                    self.assertIn('class="image-publication-note"',source)

    def test_architecture_sources_and_no_forced_optional_reading(self):
        works=[w for w in self.works if w['category']=='western-architecture']
        self.assertEqual(len(works),20)
        for lang in b.LANGS:
            index=self.pages[b.location(lang)]
            self.assertIn('href="#western-architecture"',index)
            for w in works:
                source=self.pages[b.location(lang,w)]
                self.assertIn('id="viewing-sources"',source)
                optional=re.search(r'<details class="optional-reading".*?</details>',source,re.S)
                if optional: self.assertNotIn('id="viewing-sources"',optional[0])
                self.assertNotIn('<p>---</p>',source)
                self.assertNotIn('<p>- [',source)
                self.assertNotIn('[*',source)
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
                self.assertEqual(schema['about']['@type'],'LandmarksOrHistoricalBuildings')
                self.assertNotIn('creator',schema['about'])
                self.assertEqual(len(schema['about'].get('architect',[])),len(w['architects']))
        hagia=next(w for w in works if w['slug']=='hagia-sophia')
        self.assertFalse(hagia['has_optional'])

    def test_per_image_source_links_and_rights(self):
        commons='https://commons.wikimedia.org/wiki/File:David_by_Michelangelo_(Academia_Gallery).jpg'
        self.assertEqual(b.inline('[Photo license]('+commons+')'),'<a href="'+commons+'">Photo license</a>')
        self.assertEqual(b.inline('[*A work*](https://example.org/a)'),'<a href="https://example.org/a"><em>A work</em></a>')
        fixture={'id':'example','about':'https://example.org/building',
                 'inline_images':{'view.jpg':{'click_target':'https://example.org/photo.jpg'}}}
        self.assertEqual(b.image_click_target(fixture,'view.jpg'),'https://example.org/photo.jpg')
        self.assertEqual(b.image_click_target(fixture,'other.jpg'),fixture['about'])
        with self.assertRaises(AssertionError):
            b.image_click_target({'about':'javascript:alert(1)'},'view.jpg')
        for work in self.works:
            if not work.get('inline_images'): continue
            records=json.loads((b.DATA/work['id']/'source/published-images.json').read_text())
            self.assertEqual({Path(a['local_path']).name for a in records},set(work['inline_images']))
            for lang in b.LANGS:
                source=self.pages[b.location(lang,work)]
                self.assertNotIn('INLINE-IMAGE-UPDATE-',source)
                self.assertNotIn('](assets/',source)
                self.assertEqual(source.count('<figure>'),len(records))
                for asset in records:
                    self.assertIn(b.esc(asset['click_target']),source)
                    if asset.get('license_url'):
                        self.assertIn(b.esc(asset['license_url']),source)
                    if asset.get('permission_status')=='explicitly_unlicensed':
                        # The bilingual dossier must not silently turn a reserved
                        # image into an open-license image in any edition.
                        self.assertIn('Reproduction permission has not been obtained' if lang not in ('zh','zh-hant') else '未取得转载许可',source)


if __name__=='__main__': unittest.main()

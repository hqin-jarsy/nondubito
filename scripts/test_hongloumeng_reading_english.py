from pathlib import Path
import copy
import unittest
from html.parser import HTMLParser
import build_hongloumeng_reading_english as e

class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=[];self.hrefs=[];self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a:self.hrefs.append(a['href'])

class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m,cls.p,cls.n,cls.snapshot=e.load_validated()
        cls.chapters=e.project(cls.m,cls.p,cls.n,range(1,66))
        cls.pages=e.render(cls.chapters)
    def test_incomplete_production_closed(self):
        with self.assertRaises(ValueError):e.production_plan({})
        with self.assertRaises(ValueError):e.render(self.chapters,preview=False)
    def test_no_draft_promotion(self):
        p=copy.deepcopy(self.p);p['units'][0]['state']='draft'
        with self.assertRaises(ValueError):e.project(self.m,p,self.n,[1])
    def test_exact_body_projection(self):
        for c in self.chapters:
            expected=[s['text'] for source,u in zip(self.m['units'],self.p['units']) if source['chapter']==c['number'] and source['index'] for s in u['segments']]
            self.assertEqual(expected,[b['text'] for b in c['blocks']])
    def test_notes_and_links(self):
        for name,page in self.pages.items():
            if not name.endswith('.html'):continue
            tags=Tags(page);self.assertEqual(len(tags.ids),len(set(tags.ids)))
            for href in tags.hrefs:
                if href.startswith('#'):self.assertIn(href[1:],tags.ids)
                if href == '../edition.html':
                    self.assertTrue((e.pipeline.ROOT/'classics/hongloumeng/edition.html').is_file())
                elif not href.startswith(('#','/','http')):self.assertIn(href.split('#')[0],list(self.pages))
            self.assertNotIn('reviewReference',page);self.assertNotIn('/qa/',page)
            self.assertIn('noindex,nofollow',page)
            self.assertNotIn('beacon.min.js',page)
    def test_escaping_and_exceptional_layout_fixture(self):
        # Synthetic UI fixture, explicitly not accepted manuscript or review evidence.
        fixture=[dict(number=80,title='Chapter 80\n<&"',blocks=[dict(kind='verse',text='<script>alert(1)</script>',anchor='fixture-verse',first=True,last=True,note='<b>note</b>'),dict(kind='letter',text='An invocation\nWith a second line',anchor='fixture-letter',first=True,last=True)])]
        page=e.render(fixture)['ch080.html']
        self.assertIn('&lt;script&gt;',page);self.assertNotIn('<script>alert',page)
        self.assertIn('&lt;b&gt;note&lt;/b&gt;',page);self.assertIn('not a recovered manuscript',page)
        self.assertIn(e.CONTINUATION,page)
    def test_chapter_languages(self):
        for n in (1,5,65):
            page=self.pages[f'ch{n:03d}.html']
            for d in ('','zh-hant/','en/'):
                self.assertIn(f'/classics/hongloumeng/{d}ch{n:03d}.html',page)
        self.assertNotIn('ch066.html',self.pages['ch065.html'])
    def test_reject_source_mismatch(self):
        p=copy.deepcopy(self.p);p['units'][0]['sourceHash']='bad'
        with self.assertRaises(ValueError):e.project(self.m,p,self.n,[1])


# All data below are explicit presentation fixtures. No fixture is passed to the
# real production acceptance validator or saved as an approval/review receipt.
class NoteCoverageTests(unittest.TestCase):
    def test_actual_accepted_notes_by_unit_id(self):
        m,p,notes,_=e.load_validated()
        accepted=[n for n in range(1,81) if all(u['state']=='accepted' for s,u in zip(m['units'],p['units']) if s['chapter']==n)]
        pages=e.render(e.project(m,p,notes,accepted))
        expected={n['unitId'] for n in notes['notes'] if int(n['unitId'][5:8]) in accepted}
        refs=[];ends=[]
        class Parser(HTMLParser):
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if a.get('role')=='doc-noteref':refs.append(a['data-note-unit'])
                if tag=='li' and 'data-note-unit' in a:ends.append(a['data-note-unit'])
        for name,page in pages.items():
            if name.endswith('.html'):Parser().feed(page)
        self.assertEqual(set(refs),expected);self.assertEqual(set(ends),expected)
        self.assertEqual(len(refs),len(expected));self.assertEqual(len(ends),len(expected))
        for n in (27,46):
            self.assertIn(f'data-note-unit="hlm-c{n:03d}-title"', pages[f'ch{n:03d}.html'].split('</h1>')[0])
    def test_all80_title_and_split_body_note_fixture(self):
        chapters=[];expected=[]
        for n in range(1,81):
            title_id=f'hlm-c{n:03d}-title';body_id=f'hlm-c{n:03d}-b0001'
            expected.extend((title_id,body_id))
            chapters.append(dict(number=n,title=f'Chapter {n}\nFixture <title>',titleNote=dict(unitId=title_id,text='Title <note> & text'),blocks=[dict(kind='letter',text='First segment',anchor=body_id+'-s1',first=True,last=False),dict(kind='letter',text='Second\nsegment',anchor=body_id+'-s2',first=False,last=True,note='Body <note>',noteUnitId=body_id)]))
        pages=e.render(chapters)
        for n in range(1,81):
            page=pages[f'ch{n:03d}.html'];tags=Tags(page)
            self.assertEqual(len(tags.ids),len(set(tags.ids)))
            for unit in expected[(n-1)*2:n*2]:self.assertEqual(page.count(f'data-note-unit="{unit}"'),2)
            self.assertEqual(page.count('role="doc-backlink"'),2)
            self.assertIn('Title &lt;note&gt; &amp; text',page)
            self.assertIn('Body &lt;note&gt;',page)
            for href in tags.hrefs:
                if href.startswith('#'):self.assertIn(href[1:],tags.ids)

class EnabledDiscoveryTests(unittest.TestCase):
    def setUp(self):
        from test_hongloumeng_reading_discovery import ReadingDiscoveryTests
        import hongloumeng_english_availability as av
        import refresh_hongloumeng_reading_discovery as refresh
        from unittest.mock import patch
        self.av,self.refresh=av,refresh
        self.fixture=ReadingDiscoveryTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.test_complete_scoped_plan_roundtrips_in_temp_tree(bilingual=True)
        self.root=self.fixture.root
        self.plan={'classics/hongloumeng/en/'+k:v for k,v in e.render([dict(number=n,title=f'Chapter {n}\nSynthetic layout',blocks=[dict(kind='prose',text='Synthetic body',anchor=f'fixture-{n}')]) for n in range(1,81)],preview=False).items()}
        self.enabled=False
        def fixture_publication(root=None):
            if not self.enabled:return None
            root=self.root if root is None else Path(root)
            return dict(root=root.resolve(),date='2026-11-12',paths=av.validate_english_inventory(root,self.plan))
        self.publication=fixture_publication
        self.addCleanup(patch.stopall)
        patch.object(av,'english_publication',side_effect=fixture_publication).start()
        patch.object(refresh,'english_publication',side_effect=fixture_publication).start()
        import build_hongloumeng_hub as hub
        patch.object(hub,'ROOT',self.root).start()
        patch.object(hub,'render',return_value={self.root/name:(self.root/name).read_text() for name in refresh.HUBS}).start()
        self.traditional_approval=dict(self.fixture.approval,action='publish-hongloumeng-first80-traditional',approved=True)
    def install_fixture(self):
        for name,value in self.plan.items():self.fixture.write(name,value)
        self.enabled=True
    def render_fixture(self):
        return self.refresh.render(self.root,None,self.fixture.approval,traditional_approval=self.traditional_approval)
    def test_full_enabled_inventory_render_dates_search_and_repeat(self):
        import json
        import build_content_registry as registry
        original=json.loads((self.root/'data/site-updates.json').read_text())['updates']
        latest_before=(self.root/'latest.html').read_text()
        self.install_fixture()
        paths=self.refresh.validate_published_reader(self.root,self.fixture.approval,traditional_approval=self.traditional_approval)
        self.assertEqual(len(paths),246)
        result=self.render_fixture()
        ledger=json.loads(result[self.root/'data/site-updates.json'])['updates']
        self.assertEqual([u for u in ledger if u['id']!=self.refresh.ENGLISH_UPDATE_ID],original)
        en=[u for u in ledger if u['id']==self.refresh.ENGLISH_UPDATE_ID]
        self.assertEqual(len(en),1);self.assertEqual(en[0]['date'],'2026-11-12')
        self.assertIn('classics/hongloumeng/en/index.html',result[self.root/'index.html'])
        latest=result[self.root/'latest.html']
        self.assertIn('href="classics/hongloumeng/en/index.html"',latest)
        old_card=latest_before.split(self.refresh.START)[1].split(self.refresh.END)[0]
        self.assertEqual(latest.split(self.refresh.START)[1].split(self.refresh.END)[0],old_card)
        records=json.loads(result[self.root/'data/search/en.json'])['records']
        records={v['u']:v for v in records if v['u'].startswith(self.refresh.ENGLISH_PREFIX)}
        self.assertEqual(len(records),82)
        for n in range(1,81):
            rel=f'classics/hongloumeng/en/ch{n:03d}.html';record=records[rel]
            self.assertEqual((record['k'],record['n']),('novel-chapter',n))
            lang,identity=registry.language_from_directory(Path(rel),self.root)
            self.assertEqual(lang,'en');self.assertEqual(identity,Path(f'classics/hongloumeng/ch{n:03d}.html'))
        self.assertEqual(records['classics/hongloumeng/en/index.html']['k'],'series-index')
        self.assertEqual(records['classics/hongloumeng/en/edition.html']['k'],'site-page')
        for lang in ('zh-hans','zh-hant'):
            self.assertFalse(any(v['u'].startswith(self.refresh.ENGLISH_PREFIX) for v in json.loads(result[self.root/f'data/search/{lang}.json'])['records']))
        import xml.etree.ElementTree as ET
        ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        entries={u.findtext(ns+'loc'):u.findtext(ns+'lastmod') for u in ET.fromstring(result[self.root/'sitemap.xml'])}
        self.assertEqual(entries['https://nondubito.net/classics/hongloumeng/en/'],'2026-11-12')
        self.assertEqual(entries['https://nondubito.net/classics/hongloumeng/ch001.html'],'2026-11-10')
        for path,text in result.items():path.write_text(text)
        repeated=self.render_fixture()
        self.assertTrue(all(path.read_text()==text for path,text in repeated.items()))
    def test_transition_and_unknown_missing_changed_alias_rejected(self):
        self.assertFalse(self.av.english_published(self.root))
        self.install_fixture();self.assertTrue(self.av.english_published(self.root))
        target=self.root/'classics/hongloumeng/en/ch001.html'
        target.write_text('altered')
        self.assertFalse(self.av.english_published(self.root))
        with self.assertRaises(ValueError):self.render_fixture()
        target.write_text(self.plan['classics/hongloumeng/en/ch001.html'])
        self.assertTrue(self.av.english_published(self.root))
        target.unlink()
        with self.assertRaises((ValueError,OSError)):self.render_fixture()
        target.write_text(self.plan['classics/hongloumeng/en/ch001.html'])
        for name in ('unknown.html','ch081.html','ch001 2.html','nested/secret.html'):
            extra=self.fixture.write('classics/hongloumeng/en/'+name,'fixture')
            with self.assertRaises(ValueError):self.render_fixture()
            extra.unlink()
            if extra.parent.name=='nested':extra.parent.rmdir()
        target.unlink();target.symlink_to(self.root/'classics/hongloumeng/ch001.html')
        with self.assertRaises(ValueError):self.render_fixture()
    def test_launch_date_and_duplicate_guards(self):
        import json
        d=self.refresh;ledger=json.loads((self.root/'data/site-updates.json').read_text())
        with self.assertRaises(ValueError):d.resolve_english_date(ledger,None)
        launch=d.english_publication_update('2026-11-12');ledger['updates'].insert(0,launch)
        self.assertEqual(d.resolve_english_date(ledger,None),'2026-11-12')
        with self.assertRaises(ValueError):d.resolve_english_date(ledger,'2026-11-13')
        ledger['updates'].append(launch)
        with self.assertRaises(ValueError):d.resolve_english_date(ledger,'2026-11-12')
        card=d.english_latest_card(launch)
        with self.assertRaises(ValueError):d.replace_english_latest(card+card,launch)
    def test_bounded_paths_and_no_invented_sequence(self):
        import hongloumeng_discovery_scope as scope
        import build_content_registry as registry
        self.install_fixture()
        for name in ('ch081.html','ch086.html','ch110.html','ch001 2.html','backup/index.html'):
            self.assertTrue(scope.excluded(Path('classics/hongloumeng/en')/name,root=self.root))
            self.assertIsNone(registry.hongloumeng_chapter(Path('classics/hongloumeng/en')/name))
        self.assertIsNone(registry.hongloumeng_chapter(Path('originals/hongloumeng/en/ch086.html')))

if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
"""Structural/preservation checks, not a substitute for language review."""
import json,re,unittest
from pathlib import Path
from urllib.parse import urlsplit,unquote
from unittest.mock import patch
import build_epic_full_editions as b
from test_companion_languages import Parsed,Node

class EpicFullEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editions=b.editions()
        cls.receipt=json.loads((b.DATA/'received.json').read_text())

    def test_received_provenance_and_only_approved_chinese_changes(self):
        for filename,digest in self.receipt['files'].items():
            self.assertEqual(b.digest((b.DATA/filename).read_bytes()),digest,filename)
        for filename,digest in self.receipt['review_reports'].items():
            self.assertEqual(b.digest((b.DATA/filename).read_bytes()),digest,filename)
        for filename,digest in self.receipt['correction_receipts'].items():
            self.assertEqual(b.digest((b.DATA/filename).read_bytes()),digest,filename)
        baseline=json.loads((b.DATA/'chinese-baseline.json').read_text())
        for filename,hashes in baseline.items():
            source=(b.SERIES/filename).read_text()
            for code,digest in hashes.items():
                self.assertEqual(b.region(source,'lang-'+code),b.approved_chinese_region(filename,code),(filename,code))
        self.assertEqual(len(baseline),21)
        for slug in self.editions:
            before=(b.DATA/'received/source-snapshots'/f'{slug}.html.txt').read_text()
            after=(b.SERIES/f'{slug}.html').read_text()
            for css in ('entry-door','related-note'):
                self.assertEqual(Parsed(before).nodes('div',css),Parsed(after).nodes('div',css))

    def test_author_changes_are_limited_to_approved_points(self):
        edits=b.author_edits()
        self.assertEqual(len(edits),58)
        actual={(e['episode'],e['lang'],e['block']) for e in edits}
        expected={(ep,lang,block) for ep,block in b.APPROVED_SOURCE_POINTS for lang in b.LANGS}
        expected|={(ep,lang,block) for ep,block in b.RESTORED_WORDING_POINTS for lang in b.FOREIGN}
        self.assertEqual(actual,expected)
        by_key={(e['episode'],e['lang'],e['block']):e for e in edits}
        for slug,copies in self.editions.items():
            ep=int(slug[:2])
            for lang,blocks in copies.items():
                original=json.loads((b.DATA/'received/alignment'/f'{ep:02}.{lang}.json').read_text())
                for i,(before,after) in enumerate(zip(original,blocks)):
                    key=(ep,lang,i)
                    if key in by_key:
                        self.assertEqual(before['text'],by_key[key]['before'])
                        self.assertEqual(after['text'],by_key[key]['after'])
                    else:
                        self.assertEqual(before,after,(slug,lang,i))
        # The rejected source suggestions, titles, images and literary rhythm
        # are preserved everywhere outside the five approved paragraph sites.
        self.assertEqual({(e['episode'],e['block']) for e in edits if e['lang']=='zh-Hans'},b.APPROVED_SOURCE_POINTS)
        for lang in b.LANGS:
            note=self.editions['16-abdiel-walks-away'][lang][219]['text']
            for value in ('5.657–802','5.803–848','5.853–871','5.877–895','5.890–907'):
                self.assertIn(value,note)
            self.assertNotIn('5.803–889',note)

    def test_all_160_full_texts_in_order_with_emphasis(self):
        for slug,languages in self.editions.items():
            for lang,blocks in languages.items():
                with self.subTest(slug=slug,lang=lang):
                    primary=lang in ('en','zh-Hans','zh-Hant')
                    p=b.SERIES/f'{slug}.html' if primary else b.SERIES/lang/f'{slug}.html'
                    text=p.read_text()
                    if primary:
                        cls={'en':'en','zh-Hans':'zh','zh-Hant':'hant'}[lang]
                        text=b.region(text,'lang-'+cls)
                    tree=Parsed(text);self.assertEqual(tree.nodes('h1')[0].text(),b.title(blocks))
                    main=tree.nodes('div','article-body' if primary else 'collection-body')[0]
                    actual=[n for n in main.children if isinstance(n,Node)]
                    self.assertEqual([n.tag for n in actual],[n['tag'] for n in blocks[1:]])
                    expected=Parsed(b.body(blocks))
                    self.assertEqual([n.text() for n in actual],[n.text() for n in expected.root.children if isinstance(n,Node)])
                    for tag in ('em','strong'):
                        self.assertEqual(len([n for n in main.walk() if n.tag==tag]),len(expected.nodes(tag)))
                    self.assertNotIn('\ufffd',text)

    def test_language_routes_navigation_titles_and_local_links(self):
        for p in b.SERIES.rglob('*.html'):
            text=p.read_text();tree=Parsed(text);primary=p.parent==b.SERIES
            menus=tree.nodes('div','lang-toggle' if primary else 'language-route')
            self.assertEqual(len(menus),1,p)
            choices=[n for n in menus[0].walk() if n.has_class('lang-btn')]
            self.assertEqual(len(choices),8,p)
            self.assertEqual(sum(n.tag=='button' for n in choices),3 if primary else 0,p)
            self.assertEqual(sum(n.tag=='a' for n in choices),5 if primary else 7,p)
            slug=p.stem
            expected=set()
            for code in b.FOREIGN:
                if code=='en':continue
                if not primary and code==p.parent.name:continue
                expected.add(((b.SERIES/code/(slug+'.html')).resolve(),''))
            if not primary:
                expected.update(((b.SERIES/(slug+'.html')).resolve(),'lang='+code) for code in ('en','zh','zh-hant'))
            actual=set()
            for n in choices:
                if n.tag!='a':continue
                u=urlsplit(n.attrs['href'])
                actual.add(((p.parent/unquote(u.path)).resolve(),u.query))
            self.assertEqual(actual,expected,p)
            if primary:
                self.assertEqual({n.attrs['data-lang-button'] for n in choices if n.tag=='button'},{'en','zh','zh-hant'})
            for n in tree.nodes():
                value=n.attrs.get('href') if n.tag in ('a','link') else n.attrs.get('src') if n.tag in ('script','img') else None
                if not value:continue
                u=urlsplit(value)
                if u.scheme or u.netloc:continue
                target=(p.parent/unquote(u.path)).resolve() if u.path else p
                self.assertTrue(target.is_file(),(p,value))
                if u.fragment:
                    self.assertTrue(any(n.attrs.get('id')==u.fragment for n in Parsed(target.read_text()).nodes()),(p,value))
            regions=[('en',b.region(text,'lang-en')),('zh-Hans',b.region(text,'lang-zh')),('zh-Hant',b.region(text,'lang-hant'))] if primary else [(p.parent.name,text)]
            for lang,part in regions:
                for n in Parsed(part).nodes('a'):
                    slug=Path(urlsplit(n.attrs.get('href','')).path).stem
                    if slug not in self.editions or 'lang-btn' in n.attrs.get('class',''):continue
                    if lang in ('zh-Hans','zh-Hant'):continue # Original short navigation remains unchanged.
                    self.assertIn(b.title(self.editions[slug][lang]),n.text(),(p,lang,slug))
            if not primary and p.stem in self.editions:
                nav=tree.nodes('nav','collection-nav')[0]
                for link in [n for n in nav.walk() if n.tag=='a']:
                    target=Path(link.attrs['href']).stem
                    if target not in self.editions:continue
                    if int(target[:2])<int(p.stem[:2]):self.assertIn('← ',link.text(),p)
                    else:self.assertTrue(link.text().endswith(' →'),p)
            self.assertEqual(text.count('static.cloudflareinsights.com/beacon.min.js'),1,p)
            self.assertEqual(len(tree.nodes('link')),len({n.attrs.get('href') for n in tree.nodes('link')}),p)

    def test_rebuild_is_idempotent_and_compact_builder_keeps_full_text(self):
        for p,text in b.render().items():
            self.assertEqual(p.read_text(),text,p)
        from build_collection_languages import load_specs,render
        outputs=render(load_specs({'epic-traditions'})[0])
        self.assertEqual(len(outputs),126)
        for p,text in outputs.items():self.assertEqual(p.read_text(),text,p)

    def test_foreign_manual_prose_changes_are_not_silently_discarded(self):
        original_read=Path.read_text
        for lang in ('en','ko'):
            path=b.SERIES/'03-beowulf-and-dragon.html' if lang=='en' else b.SERIES/lang/'03-beowulf-and-dragon.html'
            current=path.read_text()
            cls='article-body' if lang=='en' else 'collection-body'
            changed=b.within(current,cls,lambda body:body+'<p>USER_EDIT_SENTINEL</p>')
            def read(p,*args,**kwargs):
                return changed if p==path else original_read(p,*args,**kwargs)
            with self.subTest(lang=lang),patch.object(Path,'read_text',read):
                with self.assertRaisesRegex(AssertionError,'Foreign HTML prose changed'):
                    b.upgrade_outputs({path:current})

    def test_search_titles_match_complete_editions(self):
        for lang in b.LANGS:
            key=lang.lower()
            rows=json.loads((b.ROOT/'data/search'/f'{key}.json').read_text())['records']
            indexed={r['u']:r for r in rows}
            for slug,copies in self.editions.items():
                route='essays/everyday/stories/epic-traditions/'+('' if lang in ('en','zh-Hans','zh-Hant') else lang+'/')+slug+'.html'
                self.assertEqual(indexed[route]['t'],b.title(copies[lang]),(lang,slug))

    def test_unsupported_markup_fails_closed(self):
        for value in ('<script>bad</script>','[link](url)','*broken'):
            with self.assertRaises(AssertionError):b.inline(value)
        self.assertEqual(b.inline('A & B; **bold** and *italic*'),'A &amp; B; <strong>bold</strong> and <em>italic</em>')

if __name__=='__main__':unittest.main()

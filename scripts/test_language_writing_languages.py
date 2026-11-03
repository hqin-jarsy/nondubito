# -*- coding: utf-8 -*-
"""Full-text, provenance, URL and preservation checks for the five new editions."""
import hashlib,html,json,re,subprocess,unittest
from urllib.parse import urlsplit,unquote
from language_writing_languages import ROOT,DATA,TARGET,LANGUAGES,SLUGS,ORIGIN,DATE,load_language,render_foreign
from build_content_registry import scan_page
from web_analytics import TOKEN


class LanguageWritingLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=render_foreign()
        cls.receipt=json.loads((DATA/'multilingual-publication.json').read_text())
        cls.fixes=json.loads((DATA/'corrections.json').read_text())

    def test_current_and_complete(self):
        self.assertEqual(len(self.pages),20)
        for path,text in self.pages.items():self.assertEqual(path.read_text(),text)
        for lang in LANGUAGES:
            _,articles=load_language(lang)
            self.assertEqual([a['slug'] for a in articles],list(SLUGS[1:]))
            for article,count in zip(articles,(39,29,30)):
                self.assertEqual(len(article['body']),count)
                text=(TARGET/lang/(article['slug']+'.html')).read_text()
                body=re.search(r'<div class="essay-body lw-prose"[^>]*>(.*?)</div>',text,re.S)[1]
                units=[html.unescape(re.sub('<[^>]+>','',m[2])) for m in re.finditer(r'<(p|h2)>(.*?)</\1>',body,re.S)]
                self.assertEqual(units,[p.removeprefix('## ') for p in article['body']])
                self.assertEqual(body.count('<h2>'),3)
                self.assertNotRegex(body,r'TODO|PLACEHOLDER|\b\d{2}DD\b|�')

    def test_received_sources_and_three_original_data_files_frozen(self):
        self.assertEqual(len(self.receipt['received_files']),27)
        for path,sha in self.receipt['received_files'].items():
            self.assertEqual(hashlib.sha256((DATA/path).read_bytes()).hexdigest(),sha,path)
        for name,sha in self.receipt['baseline_files'].items():
            if name.startswith('data/') or name=='essays/sae/index.html':
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha,name)
        self.assertFalse(list((DATA/'received').glob('*.html')))

    def test_only_explicit_counted_corrections(self):
        self.assertEqual(len(self.fixes),12)
        for lang in LANGUAGES:
            _,articles=load_language(lang)
            for article in articles:
                raw=(DATA/'received'/f'{article["slug"]}.{lang}.md').read_text()
                for fix in self.fixes:
                    if fix['language']==lang and fix['episode']==article['slug']:
                        self.assertEqual(raw.count(fix['before']),1)
                        raw=raw.replace(fix['before'],fix['after'])
                blocks=re.split(r'\n\s*\n',raw.strip())
                stop=max(i for i,p in enumerate(blocks) if p.startswith('## '))
                self.assertEqual(article['body'],blocks[2:stop])
                self.assertEqual(article['source_note'],blocks[stop+1])
        self.assertFalse(any(f['language']=='de' for f in self.fixes))

    def test_semantic_and_grammar_repairs(self):
        texts={lang:{a['slug']:'\n'.join(a['body']) for a in load_language(lang)[1]} for lang in LANGUAGES}
        for lang,good,bad in (
            ('ja','その言葉を自分のものとして引き受けるという行為','約束まで代わりに果たした'),
            ('ko','그 말을 내 말로 받아들이고 책임지는 일','내가 해야 할 약속'),
            ('es','tu acto de asumir ahora ese compromiso','considerar cumplido, en tu lugar'),
            ('fr','Est-ce une raison d’être triste ?','Est-ce que cela me fait de la peine ?')):
            self.assertIn(good,texts[lang]['ep02']);self.assertNotIn(bad,texts[lang]['ep02'])
        self.assertIn('las ochenta palabras',texts['es']['ep01'])
        self.assertNotIn('los ochenta palabras',texts['es']['ep01'])
        self.assertIn('約束事なしには成り立たない',texts['ja']['ep01'])
        self.assertNotIn('et qu’un bon texte',texts['fr']['ep02'])

    def test_legacy_narrative_title_and_deck_preserved(self):
        for slug in SLUGS[1:]:
            name=f'essays/language-writing/{slug}.html'
            before=subprocess.check_output(['git','show',self.receipt['baseline_commit']+':'+name],cwd=ROOT,text=True)
            after=(ROOT/name).read_text()
            bodies=lambda s:re.findall(r'<div class="essay-body lw-prose[^>]*>.*?</div>',s,re.S)
            head=lambda s:re.search(r'<div class="lw-head">.*?</div>',s,re.S)[0]
            sources=lambda s:re.search(r'<details class="lw-sources">.*?</details>',s,re.S)[0]
            self.assertEqual(bodies(before),bodies(after))
            self.assertEqual(len(bodies(after)),3)
            self.assertEqual(head(before),head(after))
            self.assertEqual(sources(before),sources(after))

    def test_metadata_navigation_analytics_and_links(self):
        for path,text in self.pages.items():
            lang=path.parent.name
            self.assertIn(f'<html lang="{lang}" data-lang="{lang}" data-editions="{lang}"',text)
            self.assertNotIn('src="../../../site-shell.js',text)
            self.assertEqual(text.count('<h1>'),1)
            self.assertEqual(text.count('<header '),1)
            self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
            self.assertIn(TOKEN,text)
            canonical=ORIGIN+lang+'/'+('' if path.stem=='index' else path.name)
            self.assertIn(f'rel="canonical" href="{canonical}"',text)
            alternatives=re.findall(r'rel="alternate" hreflang="([^"]+)" href="([^"]+)"',text)
            self.assertEqual({a for a,_ in alternatives},{'x-default','zh-Hans',*LANGUAGES})
            self.assertEqual(len(alternatives),7)
            self.assertFalse(any('?lang=' in u for _,u in alternatives))
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text)[1])
            self.assertEqual(schema['inLanguage'],lang)
            self.assertEqual(schema['datePublished'],DATE)
            for href in re.findall(r'href="([^"]+)"',text):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path:continue
                target=(path.parent/unquote(u.path)).resolve()
                self.assertTrue(target.exists(),(path,href))
            menu=re.search(r'<div class="site-shell-language-options">(.*?)</div>',text)[1]
            self.assertEqual(menu.count('<a '),8)
            self.assertEqual(menu.count('aria-current="page"'),1)
            for code in LANGUAGES:self.assertIn(f'../{code}/{path.name}',menu)
            record=scan_page(ROOT,path)
            self.assertEqual(record['languages'],[lang])
            if path.stem!='index':
                for offset in (-1,1):
                    n=int(path.stem[-2:])+offset
                    if 1<=n<=3:self.assertIn(f'href="ep{n:02}.html"',text)

    def test_discovery(self):
        sitemap=(ROOT/'sitemap.xml').read_text()
        for lang in LANGUAGES:
            records=json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']
            for slug in SLUGS:
                relative=f'essays/language-writing/{lang}/{slug}.html'
                self.assertEqual(sum(r['u']==relative for r in records),1,relative)
                canonical=ORIGIN+lang+'/'+('' if slug=='index' else slug+'.html')
                self.assertIn('<loc>'+canonical+'</loc>',sitemap)
            channel=(ROOT/f'essays/{lang}/index.html').read_text()
            self.assertEqual(channel.count(f'href="../language-writing/{lang}/index.html"'),1)
        library=(ROOT/'library.html').read_text()
        self.assertIn('3 essays · 8 languages',library)


if __name__=='__main__':unittest.main()

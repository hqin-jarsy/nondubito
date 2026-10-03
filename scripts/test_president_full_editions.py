#!/usr/bin/env python3
"""Offline regression checks for the fully reviewed Presidents batch."""
import json
import re
import subprocess
import unittest
from urllib.parse import urlsplit

import build_president_full_editions as build
from import_president_full_editions import body_fragment, sha
from test_daodejing_sources import Page


class PresidentsBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.received=json.loads((build.DATA/'batch01-received.json').read_text())
        cls.review=json.loads((build.DATA/'batch01-review.json').read_text())
        cls.expected=build.outputs('batch01')

    def test_reproducibility(self):
        self.assertEqual(len(self.expected),40)
        for path,text in self.expected.items():self.assertEqual(path.read_text(),text,str(path))

    def test_originals_and_bounded_corrections(self):
        corrected=build.source_copies('batch01')
        for key,record in self.received['originals'].items():
            ep,lang=key.split('.')
            baseline=subprocess.check_output(['git','show',f'{self.received["baseline_commit"]}:essays/president/{ep}.html'],cwd=build.ROOT,text=True)
            self.assertEqual(sha(body_fragment(baseline,lang)),record['sha256'])
            current=body_fragment((build.SERIES/f'{ep}.html').read_text(),lang)
            self.assertEqual(current,corrected[key],key)
            for tag in ('p','h3'):
                self.assertEqual(len(re.findall('<'+tag+r'\b',current)),len(re.findall('<'+tag+r'\b',body_fragment(baseline,lang))),key)

    def test_full_manuscripts_not_summaries(self):
        for key,r in self.review['manuscripts'].items():
            ep,lang=key.split('.')
            text=(build.DATA/f'{key}.md').read_text()
            self.assertEqual(sha(text),r['sha256'])
            page=Page((build.SERIES/lang/f'{ep}.html').read_text())
            body=next(n for n in page.nodes if n.has_class('president-full'))
            rendered=Page(build.render(text.split('\n',1)[1].strip()))
            self.assertEqual(body.text().strip(),rendered.root.text().strip(),key)
            self.assertEqual(len(list(body.descendants('h2'))),r['sections'])
            self.assertEqual(len(list(body.descendants('p'))),r['paragraphs'])
            chinese=Page(json.loads((build.DATA/f'{ep}.zh.json').read_text()))
            self.assertEqual(r['paragraphs'],len([n for n in chinese.nodes if n.tag=='p']),key)
            self.assertIsNone(re.search(r'\b(?:TODO|FIXME|TBD)\b|\[insert|占位',text),key)

    def test_dom_links_language_choices_and_canonical(self):
        for path,text in self.expected.items():
            if path.suffix!='.html':continue
            page=Page(text)
            self.assertEqual(len(page.stack),1,path)
            ids=[n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
            self.assertEqual(len(ids),len(set(ids)),path)
            canonical=[n.attrs['href'] for n in page.nodes if n.tag=='link' and n.attrs.get('rel')=='canonical']
            self.assertEqual(len(canonical),1,path)
            self.assertIn(path.relative_to(build.ROOT).as_posix().removesuffix('index.html'),canonical[0])
            if path.stem!='index':
                toggle=next(n for n in page.nodes if n.has_class('lang-toggle'))
                self.assertEqual(len([n for n in toggle.descendants() if n.has_class('lang-btn')]),8,path)
            for n in page.nodes:
                if n.tag not in ('a','script','link'):continue
                url=n.attrs.get('href') or n.attrs.get('src')
                if not url:continue
                parts=urlsplit(url)
                if parts.scheme or parts.netloc:continue
                if not parts.path:
                    if parts.fragment:self.assertIn(parts.fragment,ids,(path,url))
                    continue
                target=(build.ROOT/parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/parts.path
                self.assertTrue(target.exists(),(path,url))

    def test_traditional_maps_complete(self):
        converter=build.TraditionalConverter()
        try:
            for number in self.review['episodes']:
                ep=f'ep{number:02}';path=build.SERIES/f'{ep}.html'
                script=(build.SERIES/'zh-hant-data'/f'{ep}.js').read_text()
                variants=json.loads(re.search(r'var variants = (\{.*?\});',script,re.S)[1])
                collector=build.TextCollector();collector.feed(path.read_text())
                for text in collector.text:self.assertEqual(variants.get(text,text),converter.convert(text))
        finally:converter.close()

    def test_localized_index_titles(self):
        for lang in build.LANGS:
            page=Page((build.SERIES/lang/'index.html').read_text())
            rows={n.attrs.get('href'):n for n in page.nodes if n.tag=='a' and re.fullmatch(r'ep\d{2}\.html',n.attrs.get('href',''))}
            self.assertEqual(len(rows),26)
            for number in self.review['episodes']:
                ep=f'ep{number:02}';row=rows[f'{ep}.html']
                title=next(n for n in row.descendants() if n.has_class('entry-title') or n.has_class('card-title-en')).text()
                self.assertEqual(title,self.review['manuscripts'][f'{ep}.{lang}']['title'])

    def test_future_essays_not_overwritten(self):
        baseline=self.received['baseline_commit']
        for ep in range(6,27):
            for lang in ('',*build.LANGS):
                path=build.SERIES/lang/f'ep{ep:02}.html'
                original=subprocess.check_output(['git','show',f'{baseline}:{path.relative_to(build.ROOT)}'],cwd=build.ROOT)
                self.assertEqual(path.read_bytes(),original,path)

    def test_search_and_sitemap(self):
        import build_search_index as search
        _,chunks=search.build()
        scope={p.relative_to(build.ROOT).as_posix() for p in self.expected if p.suffix=='.html'}
        for lang in search.SEARCH_LANGUAGES:
            current=json.loads((build.ROOT/f'data/search/{lang.lower()}.json').read_text())
            self.assertEqual({r['u']:r for r in current['records'] if r['u'] in scope},
                             {r['u']:r for r in chunks[lang] if r['u'] in scope})
        sitemap=(build.ROOT/'sitemap.xml').read_text()
        for path in scope:
            canonical=path.removesuffix('index.html') if path.endswith('/index.html') else path
            self.assertIn('<loc>https://nondubito.net/'+canonical+'</loc>',sitemap)


if __name__=='__main__':unittest.main()

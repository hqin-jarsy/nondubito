"""Source/preservation checks only; no unapproved foreign HTML is rendered."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from aesthetics_source import load_article, SLUGS
from aesthetics_primary import upgrade, strip_additions
from full_series_languages import ROOT, profile, primary_bodies, source_digest
from prepare_original_series_review import primary_main_hashes


class AestheticsSource(unittest.TestCase):
    def setUp(self):
        self.spec=profile('aesthetics')
        self.before=json.loads((ROOT/self.spec['primary_baseline']).read_text())

    def test_complete_original_markdown_units_and_actual_apparatus(self):
        self.assertEqual(self.spec['slugs'],SLUGS)
        articles=[load_article(self.spec,s) for s in SLUGS]
        self.assertEqual([len(a['body_zh']) for a in articles],[45,36,42,43,37,39,36,40,41,47,49,45,48,54])
        self.assertEqual(sum(p.startswith('## ') for a in articles for p in a['body_zh']),65)
        self.assertEqual(sum(len(a['notes_zh']) for a in articles),14)
        self.assertEqual(sum(len(a['sources_zh']) for a in articles),24)
        self.assertEqual(articles[0]['sources_zh'][1]['url'],'https://nondubito.net/essays/aesthetics/index.html?lang=zh#rays')
        self.assertEqual(articles[3]['sources_zh'][1]['url'],'https://www.claymath.org/millennium/riemann-hypothesis/')
        for a in articles:
            self.assertTrue(all(n.strip() for n in a['notes_zh']))
            self.assertFalse(re.search(r'\b(?:13|14|15|16)DD\b','\n'.join(a['body_zh'])))

    def test_all_primary_reading_main_apparatus_schema_and_original_whole_bytes(self):
        sha=lambda raw:hashlib.sha256(raw).hexdigest()
        self.assertEqual(primary_main_hashes(self.spec),self.before['primary_main'])
        for path,digest in self.before['whole_primary_pages'].items():
            text=(ROOT/path).read_text()
            self.assertEqual(sha(strip_additions(text).encode()),digest,path)
            schema=re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1]
            self.assertEqual(sha(schema.encode()),self.before['primary_schemas_raw'][path],path)
            if not path.endswith('/index.html'):
                self.assertEqual(sha(re.search(r'<article class="prose">.*?</article>',text,re.S)[0].encode()),self.before['raw_primary_reading_bodies'][path])
                self.assertEqual(sha(re.search(r'<aside class="source-note">.*?</aside>',text,re.S)[0].encode()),self.before['raw_primary_apparatus'][path])
        for slug in SLUGS:
            text=(ROOT/self.spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(sha(primary_bodies(self.spec,text).encode()),self.before['primary_bodies'][slug])
            self.assertEqual(source_digest('aesthetics',self.spec,slug),self.before['source_data'][slug])

    def test_all_edited_manuscripts_daily_posts_log_and_earlier_article_unchanged(self):
        sha=lambda raw:hashlib.sha256(raw).hexdigest()
        self.assertEqual(len(self.before['canonical_markdown_files']),28)
        self.assertEqual(len(self.before['daily_articles']),156)
        for key in ('canonical_markdown_files','daily_articles'):
            for path,digest in self.before[key].items():self.assertEqual(sha((ROOT/path).read_bytes()),digest,path)
        self.assertEqual(sha((ROOT/'essays/aesthetics/log.json').read_bytes()),self.before['daily_log_sha256'])
        self.assertEqual(sha((ROOT/'essays/artist_dead.html').read_bytes()),self.before['early_artist_dead_sha256'])

    def test_three_separate_primary_editions_get_only_reversible_routes(self):
        for relative in self.before['whole_primary_pages']:
            text=strip_additions((ROOT/relative).read_text());slug=Path(relative).stem
            out=upgrade(text,self.spec,slug)
            self.assertEqual(upgrade(out,self.spec,slug),out)
            self.assertEqual(strip_additions(out),text)
            self.assertEqual(re.search(r'<main\b[^>]*>.*?</main>',out,re.S)[0],re.search(r'<main\b[^>]*>.*?</main>',text,re.S)[0])
            self.assertEqual(len(re.findall(r'<link\b[^>]*rel="alternate"',out)),9)
            menu=re.search(r'<details class="language-menu">.*?</details>',out,re.S)[0]
            self.assertEqual(menu.count('<a '),8)
            self.assertIn('Daily entries retain' if '/en/' in relative else '日常記錄保留' if '/zh-hant/' in relative else '日常记录保留',out)

    def test_source_mismatch_and_new_apparatus_shape_are_rejected(self):
        real=Path.read_text;target=ROOT/'essays/aesthetics/ray03.html'
        for mode in ('body','new-note'):
            def changed(path,*args,**kwargs):
                text=real(path,*args,**kwargs)
                if path==target:
                    text=text.replace('<article class="prose">','<article class="prose"><p>不属于原底稿</p>',1) if mode=='body' else text.replace('<aside class="source-note">','<aside class="source-note"><div>不可忽略的新说明</div>',1)
                return text
            with self.subTest(mode=mode),patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):load_article(self.spec,'ray03')


if __name__=='__main__':unittest.main()

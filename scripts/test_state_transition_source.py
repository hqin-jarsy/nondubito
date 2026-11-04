"""Unpublished source/preservation checks; no foreign rendering or approvals."""
import hashlib
import json
import re
import unittest

import build_state_transitions as source
from full_series_languages import ROOT, original_article, primary_bodies, profile, source_digest, upgrade_primary
from prepare_original_series_review import primary_main_hashes


class HistoricalSource(unittest.TestCase):
    def setUp(self):
        self.spec=profile('state-transitions')
        self.before=json.loads((ROOT/self.spec['primary_baseline']).read_text())

    def test_complete_single_canonical_source_and_full_numbered_apparatus(self):
        items=source.load_items()
        self.assertEqual([a['slug'] for a in items],self.spec['slugs'])
        self.assertEqual([len(a['body_zh']) for a in items],[34,35,35,36,34,34])
        self.assertEqual(sum(len(a['sources']) for a in items),44)
        self.assertEqual(sum(p.startswith('## ') for a in items for p in a['body_zh']),18)
        for a in items:
            self.assertEqual(original_article('state-transitions',self.spec,a['slug']),a)
            self.assertEqual([s['id'] for s in a['sources']],list(range(1,len(a['sources'])+1)))
            self.assertEqual(set(map(int,re.findall(r'\[(\d+)\]','\n'.join(a['body_zh'])))),{s['id'] for s in a['sources']})
            self.assertTrue(all(s['title_zh'].strip() and s['note_zh'].strip() and s['url'].startswith('https://') for s in a['sources']))

    def test_original_json_body_main_and_schema_baselines_not_rewritten(self):
        sha=lambda v:hashlib.sha256(v).hexdigest()
        self.assertEqual(primary_main_hashes(self.spec),self.before['primary_main'])
        for path,digest in self.before['canonical_json_files'].items():
            self.assertEqual(sha((ROOT/path).read_bytes()),digest,path)
        for slug in self.spec['slugs']:
            text=(ROOT/self.spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(source_digest('state-transitions',self.spec,slug),self.before['source_data'][slug])
            self.assertEqual(sha(primary_bodies(self.spec,text).encode()),self.before['primary_bodies'][slug])
            for lang,body in re.findall(r'<div class="essay-body [^"]*lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S):
                self.assertEqual(sha(body.encode()),self.before['raw_reading_bodies'][slug+':'+lang])
        for slug in ['index',*self.spec['slugs']]:
            text=(ROOT/self.spec['directory']/(slug+'.html')).read_text()
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
            self.assertEqual(schema,self.before['original_schema'][slug])

    def test_pair_relationships_not_a_six_step_ladder(self):
        pairs=self.spec['article_pairs']
        self.assertEqual(set(pairs),set(self.spec['slugs']))
        for a,b in pairs.items():
            self.assertNotEqual(a,b)
            self.assertEqual(pairs[b],a)
        groups=self.spec['index_groups']
        self.assertEqual([g['slugs'] for g in groups],[list(source.SLUGS[i:i+2]) for i in range(0,6,2)])

    def test_initial_two_coverage_fallbacks_match_actual_primary_schema(self):
        for a in source.load_items():
            actual=a.get('coverage') or self.spec['coverage_fallback'].get(a['slug'])
            self.assertEqual(actual,self.before['original_schema'][a['slug']]['temporalCoverage'])
            self.assertEqual(a['place_en'],self.before['original_schema'][a['slug']]['about']['name'])

    def test_reversible_primary_upgrade_only_changes_known_controls_and_alternates(self):
        # Use real original rendering functions before any publication wrapper.
        items=source.load_items();conv=source.HistoryTraditionalConverter()
        try:
            pages={'index':source.landing(items,conv),**{a['slug']:source.article(a,items,conv) for a in items}}
        finally:conv.close()
        for slug,text in pages.items():
            result=upgrade_primary(text,'state-transitions',slug)
            self.assertEqual(upgrade_primary(result,'state-transitions',slug),result)
            self.assertEqual(re.search(r'<main\b[^>]*>.*?</main>',result,re.S)[0],re.search(r'<main\b[^>]*>.*?</main>',text,re.S)[0])
            stripped=re.sub(r'<!-- MIXED SERIES LANGUAGE LINKS START -->.*?<!-- MIXED SERIES LANGUAGE LINKS END -->','',result,flags=re.S)
            stripped=re.sub(r'<!-- MIXED SERIES ALTERNATES START -->.*?<!-- MIXED SERIES ALTERNATES END -->','',stripped,flags=re.S)
            self.assertEqual(stripped,text)
            self.assertEqual(len(re.findall(r'<link\b[^>]*rel="alternate"',result)),7)


if __name__=='__main__':unittest.main()

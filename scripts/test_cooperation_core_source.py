"""Pre-publication source checks; never render unapproved foreign pages."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from copy import deepcopy

from full_series_languages import ROOT,profile,original_article,primary_bodies,source_digest,upgrade_primary
from prepare_original_series_review import primary_main_hashes
from test_cooperation_histories import original_publication_bytes
from clustered_language_indexes import validate_groups,grouped_index


class CooperationSource(unittest.TestCase):
    def setUp(self):
        self.spec=profile('cooperation-histories')
        self.before=json.loads((ROOT/self.spec['primary_baseline']).read_text())

    def test_complete_direct_original_data_and_all_numbered_source_records(self):
        articles=[original_article('cooperation-histories',self.spec,s) for s in self.spec['slugs']]
        self.assertEqual([len(a['body_zh']) for a in articles],[33,33,32,34,30,31,34,35,34,35,32,32,33,32])
        self.assertEqual(sum(len(a['body_zh']) for a in articles),460)
        self.assertEqual(sum(p.startswith('## ') for a in articles for p in a['body_zh']),42)
        self.assertEqual([len(a['sources']) for a in articles],[6,8,7,7,5,9,7,5,8,6,6,8,6,8])
        self.assertEqual(sum(len(a['sources']) for a in articles),96)
        for a in articles:
            self.assertTrue(a['coverage'] and a['place_zh'] and a['place_en'])
            self.assertEqual([s['id'] for s in a['sources']],list(range(1,len(a['sources'])+1)))
            self.assertEqual(set(map(int,re.findall(r'\[(\d+)\]','\n'.join(a['body_zh'])))),{s['id'] for s in a['sources']})
            self.assertTrue(all(s['title_zh'] and s['note_zh'] and s['title_en'] and s['note_en'] and s['url'].startswith('https://') for s in a['sources']))

    def test_all_original_json_and_publication_records_are_byte_preserved(self):
        hashes=self.before['original_data_and_publication_files']
        self.assertEqual(len(hashes),21)
        for path,digest in hashes.items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        self.assertEqual({s:source_digest('cooperation-histories',self.spec,s) for s in self.spec['slugs']},self.before['source_data'])

    def test_original_whole_pages_mains_bodies_apparatus_and_schemas(self):
        sha=lambda text:hashlib.sha256(text.encode()).hexdigest()
        self.assertEqual(primary_main_hashes(self.spec),self.before['primary_main'])
        for relative,digest in self.before['whole_primary_pages'].items():
            path=ROOT/relative;text=path.read_text()
            self.assertEqual(hashlib.sha256(original_publication_bytes(path)).hexdigest(),digest,path)
            self.assertEqual(sha(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1]),self.before['raw_primary_schemas'][relative])
            self.assertEqual(sha(re.search(r'<details class="lw-sources">.*?</details>',text,re.S)[0]),self.before['raw_primary_apparatus'][relative])
            if path.stem!='index':
                actual={l:sha(v) for l,v in re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S)}
                self.assertEqual(actual,self.before['raw_primary_reading_bodies'][relative])
                self.assertEqual(sha(primary_bodies(self.spec,text)),self.before['primary_bodies'][path.stem])

    def test_fifteen_primary_route_upgrades_recover_exact_original_bytes(self):
        for relative in self.before['whole_primary_pages']:
            path=ROOT/relative;old=original_publication_bytes(path).decode()
            new=upgrade_primary(old,'cooperation-histories',path.stem)
            self.assertEqual(upgrade_primary(new,'cooperation-histories',path.stem),new)
            stripped=new
            for name in ('MIXED SERIES LANGUAGE LINKS','MIXED SERIES ALTERNATES','MIXED SERIES EDITION NOTICE'):
                stripped=re.sub('<!-- '+name+' START -->.*?<!-- '+name+' END -->','',stripped,flags=re.S)
            self.assertEqual(stripped,old)
            self.assertEqual(re.search(r'<main\b.*?</main>',new,re.S)[0],re.search(r'<main\b.*?</main>',old,re.S)[0])
            self.assertEqual(new.count('MIXED SERIES LANGUAGE LINKS START'),2)
            self.assertEqual(new.count('MIXED SERIES EDITION NOTICE START'),1)

    def test_group_decks_are_required_and_preserve_complete_pair_order(self):
        # Component fixture only, not a language manuscript or approval.
        data={'series':{'index_groups':[{'id':g['id'],'title':g['id'],'deck':'A specific pair, not a success/failure grade.'} for g in self.spec['index_groups']]},'ui':{'contents':'Reading routes'}}
        validate_groups(self.spec,data)
        cards=[(s,'<a class="lw-card"><h2>'+s+'</h2></a>') for s in self.spec['slugs']]
        output=grouped_index(self.spec,data,cards)
        self.assertEqual(output.count('A specific pair, not a success/failure grade.'),7)
        self.assertEqual(output.count('<h3>'),14)
        for key in ('','<hidden>'):
            invalid=deepcopy(data);invalid['series']['index_groups'][0]['deck']=key
            with self.assertRaises(AssertionError):validate_groups(self.spec,invalid)
        pairs=self.spec['article_pairs']
        self.assertEqual(len(pairs),14)
        self.assertTrue(all(a!=b and pairs[b]==a for a,b in pairs.items()))


if __name__=='__main__':unittest.main()

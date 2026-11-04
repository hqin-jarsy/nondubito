"""Direct aggregate/bibliography-source checks, without unapproved rendering."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from full_series_languages import (ROOT,profile,source_file,source_digest,
                                   original_article,primary_bodies,upgrade_primary)
from prepare_original_series_review import primary_main_hashes
from western_book_source import reference_bundle

SERIES='sae-montaigne'
BASE=ROOT/'data'/SERIES/'multilingual'
COUNTS=[16,28,28,26,30,31]


class MontaigneSource(unittest.TestCase):
    def test_original_aggregate_and_real_builder_references_read_directly(self):
        spec=profile(SERIES)
        path=ROOT/'data/sae-montaigne.json'
        entries=json.loads(path.read_text())['entries']
        refs=reference_bundle(spec)
        counts=[];headings=notes=asides=links=0
        for raw,slug in zip(entries,spec['slugs']):
            a=original_article(SERIES,spec,slug)
            self.assertEqual(source_file(SERIES,spec,slug),path)
            units=[]
            for section in raw['zh']['sections']:
                if section['heading']:units.append('## '+section['heading']);headings+=1
                units.extend(section['paragraphs'])
            self.assertEqual(a['body_zh'],units)
            self.assertEqual(a['aside_zh'],raw['zh'].get('aside'))
            self.assertEqual(a['notes_zh'],raw['zh']['notes'])
            expected=[{'title':refs['sources'][k][1],'url':refs['sources'][k][2]}
                      for k in refs['source_keys'][raw['number']]]
            self.assertEqual(a['sources_zh'],expected)
            counts.append(len(units));notes+=len(a['notes_zh'])
            asides+=bool(a['aside_zh']);links+=len(expected)
        self.assertEqual(counts,COUNTS)
        self.assertEqual((headings,notes,asides,links),(31,7,5,18))
        self.assertEqual([len(e['zh']['notes']) for e in entries],[1,1,1,1,1,2])

    def test_pre_expansion_complete_sources_bodies_and_main_preserved(self):
        spec=profile(SERIES)
        before=json.loads((BASE/'primary-before-expansion.json').read_text())
        self.assertEqual(primary_main_hashes(spec),before['primary_main'])
        self.assertEqual(len(before['primary_main']),7)
        path=ROOT/'data/sae-montaigne.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before['canonical_json_sha256'])
        for slug in spec['slugs']:
            self.assertEqual(source_digest(SERIES,spec,slug),before['source_data'][slug])
            text=(ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(text.count('<div class="western-prose lang-'),3)
            self.assertEqual(hashlib.sha256(primary_bodies(spec,text).encode()).hexdigest(),before['primary_bodies'][slug])

    def test_source_digest_protects_both_whole_json_and_actual_reference_table(self):
        spec=profile(SERIES);path=ROOT/'data/sae-montaigne.json'
        expected=source_digest(SERIES,spec,'intro')
        old=Path.read_bytes
        def changed_bytes(p):return old(p)+(b'\n' if p==path else b'')
        with patch.object(Path,'read_bytes',changed_bytes):
            self.assertNotEqual(source_digest(SERIES,spec,'intro'),expected)
        import build_sae_western as source
        changed=copy.deepcopy(source.SOURCES)
        title_en,title_zh,url=changed['monloe']
        changed['monloe']=(title_en,title_zh,'https://example.invalid/')
        with patch.object(source,'SOURCES',changed):
            self.assertNotEqual(source_digest(SERIES,spec,'intro'),expected)
        changed=copy.deepcopy(source.SOURCE_KEYS)
        changed[0]=list(reversed(changed[0]))
        with patch.object(source,'SOURCE_KEYS',changed):
            self.assertNotEqual(source_digest(SERIES,spec,'intro'),expected)

    def test_unknown_or_lost_aggregate_reading_material_rejected(self):
        spec=profile(SERIES);path=ROOT/'data/sae-montaigne.json';old=Path.read_text
        for mode in ('root','section','extra','lose-aside','invent-aside','slug'):
            def changed(p,*args,**kwargs):
                text=old(p,*args,**kwargs)
                if p!=path:return text
                data=json.loads(text)
                if mode=='root':data['new_material']='Unaccounted reading material'
                elif mode=='section':data['entries'][1]['zh']['sections'][0]['new_material']='Unknown'
                elif mode=='extra':data['entries'][1]['zh']['new_material']='Unknown'
                elif mode=='lose-aside':del data['entries'][1]['zh']['aside']
                elif mode=='invent-aside':data['entries'][0]['zh']['aside']='Invented intro comparison'
                else:data['entries'][1]['slug']='different-slug'
                return json.dumps(data)
            slug='intro' if mode=='invent-aside' else 'ep01'
            with self.subTest(mode=mode),patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):
                original_article(SERIES,spec,slug)

    def test_primary_only_controls_are_idempotent_and_exactly_reversible(self):
        # No foreign draft is rendered and no positive approval is mocked.
        spec=profile(SERIES)
        def strip_controls(text):
            for label,expected in [('LANGUAGE LINKS',2),('ALTERNATES',1)]:
                pattern=(r'<!-- MIXED SERIES '+label+r' START -->.*?'
                         r'<!-- MIXED SERIES '+label+r' END -->')
                text,count=re.subn(pattern,'',text,flags=re.S)
                self.assertEqual(count,expected)
            return text
        for slug in ['index',*spec['slugs']]:
            path=ROOT/spec['directory']/(slug+'.html')
            text=path.read_bytes().decode('utf-8')
            upgraded=upgrade_primary(text,SERIES,slug)
            self.assertEqual(upgrade_primary(upgraded,SERIES,slug),upgraded)
            original=strip_controls(text) if '<!-- MIXED SERIES LANGUAGE LINKS START -->' in text else text
            self.assertEqual(strip_controls(upgraded).encode(),original.encode())
            self.assertNotEqual(strip_controls(upgraded.replace('\n','\r\n')).encode(),original.encode())
            self.assertEqual(primary_bodies(spec,upgraded),primary_bodies(spec,text))
            for code in spec['languages']:
                self.assertEqual(upgraded.count('href="'+code+'/'+slug+'.html"'),2)


if __name__=='__main__':unittest.main()

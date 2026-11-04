"""Canonical book-source and primary preservation checks, before drafting seals."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from full_series_languages import (ROOT,profile,original_article,source_file,
                                   source_digest,primary_bodies,upgrade_primary,render)
from prepare_original_series_review import primary_main_hashes
from prepare_action_sources import Document,one

SERIES='sae-descartes'
BASE=ROOT/'data'/SERIES/'multilingual'


class WesternBookSource(unittest.TestCase):
    def test_direct_sources_keep_every_unit_and_separate_optional_material(self):
        spec=profile(SERIES);counts=[];paragraphs=headings=notes=links=asides=0
        for number,slug in enumerate(spec['slugs']):
            path=ROOT/'data'/SERIES/f'{number:02}.json'
            self.assertEqual(source_file(SERIES,spec,slug),path)
            raw=json.loads(path.read_text());a=original_article(SERIES,spec,slug)
            expected=[]
            for section in raw['zh']['sections']:
                if section['heading']:expected.append('## '+section['heading']);headings+=1
                expected.extend(section['paragraphs']);paragraphs+=len(section['paragraphs'])
            self.assertEqual(a['body_zh'],expected)
            self.assertEqual(a['notes_zh'],raw['zh']['notes'])
            self.assertEqual(a['aside_zh'],raw['zh'].get('aside'))
            self.assertEqual(a['sources_zh'],[{'title':s['title']['zh'],'url':s['url']} for s in raw['sources']])
            self.assertEqual(source_digest(SERIES,spec,slug),hashlib.sha256(path.read_bytes()).hexdigest())
            counts.append(len(expected));notes+=len(a['notes_zh']);links+=len(a['sources_zh']);asides+=bool(a['aside_zh'])
        self.assertEqual(counts,[26,31,34,42,40,42,46])
        self.assertEqual((paragraphs,headings,notes,links,asides),(217,44,14,11,6))

    def test_original_three_bodies_and_complete_main_areas_match_baseline(self):
        spec=profile(SERIES);before=json.loads((BASE/'primary-before-expansion.json').read_text())
        self.assertEqual(primary_main_hashes(spec),before['primary_main'])
        for slug in spec['slugs']:
            text=(ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(text.count('<div class="western-prose lang-'),3)
            self.assertEqual(hashlib.sha256(primary_bodies(spec,text).encode()).hexdigest(),before['primary_bodies'][slug])
            self.assertEqual(source_digest(SERIES,spec,slug),before['source_data'][slug])

    def test_language_controls_idempotent_without_rewriting_primary_content(self):
        spec=profile(SERIES)
        for slug in ['index',*spec['slugs']]:
            text=(ROOT/spec['directory']/(slug+'.html')).read_text()
            upgraded=upgrade_primary(text,SERIES,slug)
            self.assertEqual(upgrade_primary(upgraded,SERIES,slug),upgraded)
            def main(value):
                doc=Document(value)
                return doc.raw(one(doc.root.walk(),lambda n:n.tag=='main','Primary main'))
            self.assertEqual(main(text),main(upgraded))
            self.assertEqual(primary_bodies(spec,text),primary_bodies(spec,upgraded))
            for code in spec['languages']:self.assertEqual(upgraded.count('href="'+code+'/'+slug+'.html"'),2)

    def test_unknown_material_and_missing_aside_fail_closed(self):
        spec=profile(SERIES);path=source_file(SERIES,spec,'ep01');old=Path.read_text
        for mode in ('aside','section','extra'):
            def changed(p,*args,**kwargs):
                value=old(p,*args,**kwargs)
                if p==path:
                    item=json.loads(value)
                    if mode=='aside':del item['zh']['aside']
                    elif mode=='section':item['zh']['sections'][0]['new_block']='Unaccounted new reading text'
                    else:item['zh']['new_material']='Unaccounted additional reading text'
                    return json.dumps(item)
                return value
            with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):original_article(SERIES,spec,'ep01')

    def test_existing_sealed_foreign_pages_unchanged_by_opt_in_features(self):
        total=0
        for path in (ROOT/'data').glob('*/multilingual/profile.json'):
            if not (path.parent/'publication.json').exists():continue
            spec=json.loads(path.read_text())
            for target,text in render(path.parent.parent.name).items():
                self.assertEqual(target.read_text(),text,target);total+=1
        self.assertGreaterEqual(total,695)


if __name__=='__main__':unittest.main()

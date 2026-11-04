"""Canonical HTML adapter checks; never substitute these for prose reading."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from full_series_languages import (ROOT,profile,original_article,source_digest,
    primary_bodies,upgrade_primary,inline_markdown)
from prepare_original_series_review import primary_main_hashes
from prepare_action_sources import Document

SERIES='sae-second-critique'
BASE=ROOT/'data'/SERIES/'multilingual'


class PublishedHTMLSource(unittest.TestCase):
    def test_all_canonical_units_and_emphases_are_read_directly(self):
        spec=profile(SERIES)
        sources=[original_article(SERIES,spec,s) for s in spec['slugs']]
        self.assertEqual([len(a['body_zh']) for a in sources],[21]+[20]*11)
        counts={'h2':0,'strong':0,'em':0}
        for a in sources:
            self.assertEqual(a['source_url'],spec['source'])
            self.assertEqual(a['source_doi'],'https://doi.org/10.5281/zenodo.23250387')
            self.assertFalse((ROOT/'data'/SERIES/(a['slug']+'.json')).exists())
            for unit in a['body_zh']:
                counts['h2']+=unit.startswith('## ')
                for tag in ('strong','em'):counts[tag]+=inline_markdown(unit).count('<'+tag+'>')
        self.assertEqual(counts,{'h2':60,'strong':254,'em':17})

    def test_raw_reading_content_and_hant_dictionary_snapshot_unchanged(self):
        spec=profile(SERIES);before=json.loads((BASE/'primary-before-expansion.json').read_text())
        self.assertEqual(primary_main_hashes(spec),before['primary_main'])
        self.assertEqual(len(before['primary_main']),13)
        self.assertEqual(len(before['hant_dictionaries']),13)
        for name,digest in before['hant_dictionaries'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        for slug in spec['slugs']:
            self.assertEqual(source_digest(SERIES,spec,slug),before['source_data'][slug])
            text=(ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(hashlib.sha256(primary_bodies(spec,text).encode()).hexdigest(),before['primary_bodies'][slug])
            bodies=[n for n in Document(text).root.walk() if n.has('essay-body')]
            self.assertEqual(len(bodies),2)
            self.assertEqual({c for n in bodies for c in ('lang-zh','lang-en') if n.has(c)},{'lang-zh','lang-en'})

    def test_permitted_language_controls_do_not_change_source_fingerprint(self):
        spec=profile(SERIES)
        before={s:source_digest(SERIES,spec,s) for s in spec['slugs']}
        old_read=Path.read_text;upgraded={}
        for slug in ['index',*spec['slugs']]:
            path=ROOT/spec['directory']/(slug+'.html');text=old_read(path)
            upgraded[path]=upgrade_primary(text,SERIES,slug)
            self.assertEqual(upgrade_primary(upgraded[path],SERIES,slug),upgraded[path])
        def changed(path,*a,**kw):return upgraded[path] if path in upgraded else old_read(path,*a,**kw)
        with patch.object(Path,'read_text',changed):
            self.assertEqual({s:source_digest(SERIES,spec,s) for s in spec['slugs']},before)

    def test_english_or_index_prose_changes_and_unknown_blocks_are_not_hidden(self):
        spec=profile(SERIES);slug=spec['slugs'][0]
        path=ROOT/spec['directory']/(slug+'.html');index=path.parent/'index.html'
        old_read=Path.read_text;text=old_read(path);index_text=old_read(index)
        doc=Document(text)
        english=next(n for n in doc.root.walk() if n.has('essay-body','lang-en'))
        heading=next(n for n in english.walk() if n.tag=='h2')
        old_heading=doc.raw(heading)
        changed_article=text.replace(old_heading,old_heading.replace('</h2>',' — changed</h2>'),1)
        old_digest=source_digest(SERIES,spec,slug)
        def changed(path_arg,*a,**kw):return changed_article if path_arg==path else old_read(path_arg,*a,**kw)
        with patch.object(Path,'read_text',changed):
            self.assertNotEqual(source_digest(SERIES,spec,slug),old_digest)
            # The Chinese units are identical: it is the protected English
            # reading area, not a Chinese-text-only digest, that detects this.
            modified_units=original_article(SERIES,spec,slug)['body_zh']
        self.assertEqual(modified_units,original_article(SERIES,spec,slug)['body_zh'])
        changed_index=index_text.replace('如果这是你第一次接触 SAE','如果这是你第一次接触 SAE（改动）',1)
        def changed(path_arg,*a,**kw):return changed_index if path_arg==index else old_read(path_arg,*a,**kw)
        with patch.object(Path,'read_text',changed):self.assertNotEqual(source_digest(SERIES,spec,slug),old_digest)
        chinese=next(n for n in doc.root.walk() if n.has('essay-body','lang-zh'))
        paragraph=next(n for n in chinese.walk() if n.tag=='p')
        old_p=doc.raw(paragraph);changed_article=text.replace(old_p,old_p.replace('<p>','<h3>',1).replace('</p>','</h3>'),1)
        def changed(path_arg,*a,**kw):return changed_article if path_arg==path else old_read(path_arg,*a,**kw)
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'new block'):
            original_article(SERIES,spec,slug)


if __name__=='__main__':unittest.main(verbosity=2)

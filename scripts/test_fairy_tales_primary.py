"""Source-only English authorization boundaries; no fabricated publication."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from full_series_languages import ROOT, primary_bodies, profile, source_digest
from fairy_tales_primary import english_body, replace_english, restore_original, search_decks
from prepare_original_series_review import primary_main_hashes
from fairy_tales_source import apparatus_inline
from prepare_action_sources import Document


class FairyPrimaryPreservation(unittest.TestCase):
    def test_missing_note_label_is_rejected_before_rendering(self):
        from full_series_languages import load_language
        target=ROOT/'data/fairy-tales/multilingual/en.json'
        read_text=Path.read_text
        def without_label(path,*args,**kwargs):
            raw=read_text(path,*args,**kwargs)
            if path==target:
                data=json.loads(raw)
                del data['ui']['edition_notes']
                return json.dumps(data,ensure_ascii=False)
            return raw
        with patch.object(Path,'read_text',without_label),self.assertRaisesRegex(AssertionError,'missing complete-version-note UI label'):
            load_language('fairy-tales','en')

    def test_group_title_readback_binds_the_named_child_not_the_whole_object(self):
        from prepare_original_series_review import review_field, verify_saved_readbacks
        # Structural unit fixture only: no manuscript or publication approval.
        data={'series':{'index_groups':[{'id':'chapter-1','title':'Reviewed title'}]}}
        issue={'field':'series.index_groups','paragraph':0,'subfield':'title','after':'Reviewed title'}
        self.assertEqual(review_field(data,issue),'Reviewed title')
        field={k:issue[k] for k in ('field','paragraph','subfield')}
        field['saved_field_sha256']=hashlib.sha256(b'Reviewed title').hexdigest()
        report={'metadata_issues':[issue],'post_application_readback':{'passed':True,'reader':'Structural unit fixture only','scope':'No publication approval','fields':[field]}}
        verify_saved_readbacks(data,report)
        del field['subfield']
        with self.assertRaises(AssertionError):verify_saved_readbacks(data,report)

    def test_group_title_readback_rejects_same_shape_changed_title(self):
        from prepare_original_series_review import verify_saved_readbacks
        data={'series':{'index_groups':[{'id':'chapter-1','title':'Reviewed title!'}]}}
        issue={'field':'series.index_groups','paragraph':0,'subfield':'title','after':'Reviewed title'}
        field={**issue,'saved_field_sha256':hashlib.sha256(b'Reviewed title').hexdigest()}
        report={'metadata_issues':[issue],'post_application_readback':{'passed':True,'reader':'Structural unit fixture only','scope':'No publication approval','fields':[field]}}
        with self.assertRaises(AssertionError):verify_saved_readbacks(data,report)

    def test_full_note_links_keep_nested_parentheses_and_are_whitelisted(self):
        url='https://de.wikisource.org/wiki/Rapunzel_(1857)'
        doc=Document('<p>'+apparatus_inline('Read the [complete source]('+url+'), not a film.',[{'url':url}])+'</p>')
        self.assertEqual([n.attrs['href'] for n in doc.root.walk() if n.tag=='a'],[url])
        self.assertEqual(doc.root.text(),'Read the complete source, not a film.')
        with self.assertRaises(AssertionError):apparatus_inline('[wrong](https://example.invalid/)',[{'url':url}])
        with self.assertRaises(AssertionError):apparatus_inline('[broken]('+url,[{'url':url}])
        with self.assertRaises(AssertionError):apparatus_inline('[broken]('+url+' then [valid]('+url+')',[{'url':url}])

    def test_fixed_primary_baseline_after_documented_link_repairs(self):
        spec=profile('fairy-tales')
        before=json.loads((ROOT/spec['primary_baseline']).read_text())
        self.assertEqual(primary_main_hashes(spec),before['primary_main'])
        for slug in ['index',*spec['slugs']]:
            p=ROOT/spec['directory']/(slug+'.html')
            restored=restore_original(p.read_text(),spec,slug)
            self.assertEqual(hashlib.sha256(restored.encode()).hexdigest(),before['primary_html'][str(p.relative_to(ROOT))])
            if slug!='index':
                self.assertEqual(source_digest('fairy-tales',spec,slug),before['source_data'][slug])
                self.assertEqual(hashlib.sha256(primary_bodies(spec,p.read_text()).encode()).hexdigest(),before['primary_bodies'][slug])

    def test_english_body_replacement_is_exactly_recoverable_and_does_not_rebase_chinese(self):
        spec=profile('fairy-tales')
        before=json.loads((ROOT/spec['primary_baseline']).read_text())
        archive=json.loads((ROOT/'data/fairy-tales/multilingual/original-english-bodies.json').read_text())
        for slug in spec['slugs']:
            p=ROOT/spec['directory']/(slug+'.html')
            original=restore_original(p.read_text(),spec,slug)
            self.assertEqual(english_body(original),archive['bodies'][slug])
            changed=replace_english(original,'<p>Authorized English body boundary test.</p>')
            self.assertEqual(primary_bodies(spec,changed),primary_bodies(spec,original))
            self.assertEqual(restore_original(changed,spec,slug),original)
            self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),before['primary_html'][str(p.relative_to(ROOT))])

    def test_changed_original_chinese_is_detected_even_when_shape_is_unchanged(self):
        spec=profile('fairy-tales')
        slug=spec['slugs'][0];p=ROOT/spec['directory']/(slug+'.html')
        read_text=Path.read_text
        original=read_text(p)
        changed=original.replace('国王','帝王',1)
        # Find a Chinese-mode occurrence, not any English metadata.
        start=changed.index('<div class="lang-zh local">')
        changed=changed[:start]+changed[start:].replace('女孩','少女',1)
        self.assertNotEqual(changed,original)
        baseline=source_digest('fairy-tales',spec,slug)
        def supplied(path,*args,**kwargs):
            return changed if path==p else read_text(path,*args,**kwargs)
        with patch.object(Path,'read_text',supplied):
            self.assertNotEqual(source_digest('fairy-tales',spec,slug),baseline)

    def test_reviewed_english_descriptions_restore_exact_original_tags(self):
        spec=profile('fairy-tales')
        archive=json.loads((ROOT/'data/fairy-tales/multilingual/original-english-bodies.json').read_text())
        self.assertEqual(set(archive['original_article_descriptions']),set(spec['slugs']))
        for slug in spec['slugs']:
            path=ROOT/spec['directory']/(slug+'.html')
            original=restore_original(path.read_text(),spec,slug)
            changed=original
            for number,tag in enumerate(archive['original_article_descriptions'][slug]):
                self.assertEqual(changed.count(tag),1)
                updated=re.sub(r'content="[^"]*"','content="Reviewed English description boundary test."',tag)
                changed=changed.replace(tag,'<!-- FAIRY TALES DESCRIPTION '+str(number)+' START -->'+updated+'<!-- FAIRY TALES DESCRIPTION '+str(number)+' END -->',1)
            self.assertEqual(primary_bodies(spec,changed),primary_bodies(spec,original))
            self.assertEqual(restore_original(changed,spec,slug),original)

    def test_english_index_card_corrections_are_independently_reversible(self):
        spec=profile('fairy-tales')
        archive=json.loads((ROOT/'data/fairy-tales/multilingual/original-english-bodies.json').read_text())
        self.assertEqual(set(archive['original_index_english_card_decks']),set(spec['slugs']))
        path=ROOT/spec['directory']/'index.html'
        original=restore_original(path.read_text(),spec,'index')
        changed=original
        for slug,row in archive['original_index_english_card_decks'].items():
            self.assertEqual(changed.count(row['paragraph']),1)
            changed=changed.replace(row['paragraph'],'<!-- FAIRY TALES CARD DECK '+slug+' START --><p>Reviewed English card boundary test.</p><!-- FAIRY TALES CARD DECK '+slug+' END -->',1)
        self.assertEqual(restore_original(changed,spec,'index'),original)

    def test_localized_search_metadata_reuses_chinese_and_hant_without_changing_prose(self):
        from build_search_index import extract_recent_fiction_descriptions
        spec=profile('fairy-tales')
        for slug in ['index',*spec['slugs']]:
            path=ROOT/spec['directory']/(slug+'.html')
            original=restore_original(path.read_text(),spec,slug)
            decks=search_decks(spec,slug)
            self.assertEqual(set(decks),{'en','zh-Hans','zh-Hant'})
            self.assertNotEqual(decks['en'],decks['zh-Hans'])
            import html
            classes={'en':'en','zh-Hans':'zh','zh-Hant':'hant'}
            metadata=''.join('<p hidden style="display:none!important" class="lw-search-deck lang-'+classes[l]+'">'+html.escape(v)+'</p>' for l,v in decks.items())
            changed=original.replace('</main>','<!-- FAIRY TALES LANGUAGE SEARCH START -->'+metadata+'<!-- FAIRY TALES LANGUAGE SEARCH END --></main>',1)
            self.assertEqual(extract_recent_fiction_descriptions(changed),decks)
            self.assertEqual(restore_original(changed,spec,slug),original)


if __name__=='__main__':unittest.main()

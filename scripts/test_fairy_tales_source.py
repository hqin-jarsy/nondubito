"""Source-only checks; counts and hashes are not literary publication approval."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from fairy_tales_source import (ROOT, DIRECTORY, EXPECTED_UNITS, load_article,
                                load_index, index_context, source_digest,
                                prose_inline)
from import_fairy_tales import inline_markdown, markdown_links, source_copy
import import_fairy_tales
from prepare_action_sources import Document, Node, one, normalize


def repaired_reference_urls(document, mode):
    local = one(document.root.walk(),lambda n:n.has(mode,'local'),mode)
    body = one(local.walk(),lambda n:n.has('article-body'),'body')
    # Upgraded EN keeps its complete notes and reference list separately. The
    # two protected Chinese editions retain their original final note p.
    material = body if mode=='lang-en' else [n for n in body.children if isinstance(n,Node)][-1]
    return [n.attrs['href'] for n in material.walk() if n.tag=='a']


class FairyTalesSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads((ROOT/'data/fairy-tales/multilingual/profile.json').read_text())

    def test_full_current_chinese_and_separate_complete_apparatus(self):
        index = load_index(self.spec)
        self.assertEqual([c['slug'] for c in index['cards']], self.spec['slugs'])
        articles = [load_article(self.spec,s) for s in self.spec['slugs']]
        self.assertEqual([len(a['body_zh']) for a in articles], list(EXPECTED_UNITS))
        self.assertEqual(sum(len(a['body_zh']) for a in articles), 595)
        self.assertEqual(sum(len(a['notes_zh']) for a in articles), 30)
        self.assertEqual(sum(len(a['sources_zh']) for a in articles), 46)
        for a in articles:
            text = (ROOT/DIRECTORY/(a['slug']+'.html')).read_text()
            doc = Document(text)
            local = one(doc.root.walk(),lambda n:n.has('lang-zh','local'),'Chinese source')
            body = one(local.walk(),lambda n:n.has('article-body'),'body')
            ps = [n for n in body.children if isinstance(n,Node)]
            self.assertEqual(a['notes_zh'],[normalize(ps[-1].text())])
            self.assertNotIn('](http', a['notes_zh'][0])
            self.assertEqual(a['sources_zh'],[{'title':normalize(n.text()),'url':n.attrs['href']}
                                             for n in ps[-1].walk() if n.tag=='a'])
            self.assertEqual([n['url'] for n in a['entry_routes']],['../index.html','../../../../start.html'])
            self.assertIsNone(a['aside_zh'])
            self.assertFalse(any(p.startswith('## ') for p in a['body_zh']))
        self.assertEqual(len(index_context(self.spec)),2)
        self.assertEqual([len(g['slugs']) for g in index['groups']],[6,4,6,6,5,3])
        self.assertEqual(index['entry_slugs'],self.spec['entry_slugs'])

    def test_balanced_source_markdown_and_first_source_extraction(self):
        urls = ['https://de.wikisource.org/wiki/Rapunzel_(1857)',
                'https://fr.wikisource.org/wiki/Histoires_(1697)/Original/Cendrillon',
                'https://example.org/a_(b_(c))/d?x=1&y=2']
        for url in urls:
            raw = 'Before [Source & label]('+url+') after.'
            rendered = Document('<p>'+inline_markdown(raw)+'</p>')
            links = [n for n in rendered.root.walk() if n.tag=='a']
            self.assertEqual([n.attrs['href'] for n in links],[url])
            self.assertEqual(links[0].text(),'Source & label')
            self.assertEqual(rendered.root.text(),'Before Source & label after.')
            self.assertEqual(next(markdown_links(raw))[3],url)
            fixture = '# Title\n\nA full argument.\n\n---\n\n*Version. [Source]('+url+')*'
            with patch.object(Path,'read_text',return_value=fixture):
                self.assertEqual(source_copy({'file':'not-read.md'})[3],url)
        broken = '[Source](https://example.org/book_(1857)'
        self.assertNotIn('<a ',inline_markdown(broken))

    def test_exact_recorded_repairs_and_untouched_primary_arguments(self):
        report = json.loads((ROOT/'data/fairy-tales/multilingual/source-link-repairs.json').read_text())
        self.assertEqual(len(report['changes']),38)
        self.assertEqual(len({r['path'] for r in report['changes']}),13)
        for record in report['post_application']['files']:
            path = ROOT/record['path']
            old = subprocess.check_output(['git','show',report['before_commit']+':'+record['path']],cwd=ROOT,text=True)
            self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),record['before_raw_sha256'])
            proposed = old
            edits = [e for r in report['changes'] if r['path']==record['path'] for e in r['edits']]
            for e in sorted(edits,key=lambda e:e['start'],reverse=True):
                self.assertEqual(old[e['start']:e['end']],e['before'])
                proposed = proposed[:e['start']]+e['after']+proposed[e['end']:]
            if record['added_terminal_lf']:
                self.assertFalse(old.endswith('\n'))
                proposed += '\n'
            self.assertEqual(hashlib.sha256(proposed.encode()).hexdigest(),record['after_raw_sha256'])
            # EN is explicitly authorized for a later full rewrite. This source
            # test protects current complete Chinese and Hant argument blocks.
            if path.stem=='index':
                continue
            doc = Document(path.read_text())
            for mode in ('lang-zh','lang-hant'):
                local = one(doc.root.walk(),lambda n:n.has(mode,'local'),mode)
                body = one(local.walk(),lambda n:n.has('article-body'),'body')
                ps = [n for n in body.children if isinstance(n,Node)]
                raw = ''.join(doc.raw(n) for n in ps[:-1])
                self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),record['modes'][mode]['after_argument_sha256'])
        for r in report['changes']:
            doc = Document((ROOT/r['path']).read_text())
            # Only first EN source may later grow to the full Chinese apparatus;
            # the repaired historical reference must nevertheless remain exact.
            self.assertIn(r['edits'][0]['after'],repaired_reference_urls(doc,r['mode']))

    def test_repaired_reference_survives_complete_english_with_separate_sources(self):
        url = 'https://de.wikisource.org/wiki/Rapunzel_(1857)'
        text = ('<div class="lang-en local"><div class="article-body">'
                '<p>A complete independently rewritten English argument.</p>'
                '<p>The full selected-version limitations.</p>'
                '<ul><li><a href="'+url+'">Complete historical text</a></li></ul>'
                '<p>A final editorial reading note, not an inline bibliography.</p>'
                '</div></div>')
        self.assertEqual(repaired_reference_urls(Document(text),'lang-en'),[url])

    def test_semantic_source_digest_ignores_only_english_and_outside_controls(self):
        slug = self.spec['slugs'][0]
        path = ROOT/DIRECTORY/(slug+'.html')
        original = path.read_text()
        doc = Document(original)
        english = one(doc.root.walk(),lambda n:n.has('lang-en','local'),'English mode')
        changed_en = original[:english.open_end]+'Changed authorized English.'+original[english.close_start:]
        baseline = source_digest(self.spec,slug)
        real_read = Path.read_text
        def provide(value):
            return lambda p,*a,**kw:value if p==path else real_read(p,*a,**kw)
        for changed in (changed_en,original.replace('</head>','<!-- future language controls --></head>',1)):
            with patch.object(Path,'read_text',provide(changed)):
                self.assertEqual(source_digest(self.spec,slug),baseline)
        for mode in ('lang-zh','lang-hant'):
            local = one(doc.root.walk(),lambda n:n.has(mode,'local'),mode)
            changed = original[:local.open_end]+' unauthorized text '+original[local.open_end:]
            with patch.object(Path,'read_text',provide(changed)):
                self.assertNotEqual(source_digest(self.spec,slug),baseline)

    def test_emphasis_and_unhandled_blocks_fail_closed(self):
        node = next(n for n in Document('<p>A <strong>clear</strong> <em>limit</em>.</p>').root.walk() if n.tag=='p')
        self.assertEqual(prose_inline(node),'A **clear** *limit*.')
        with self.assertRaises(AssertionError):
            prose_inline(next(n for n in Document('<p>A <img src="x"> image.</p>').root.walk() if n.tag=='p'))

    def test_legacy_importer_cannot_overwrite_reviewed_publication(self):
        publication = ROOT/'data/fairy-tales/multilingual/publication.json'
        exists = Path.exists
        def published(path):
            return True if path==publication else exists(path)
        for args in ([],['--check']):
            with patch('sys.argv',['import_fairy_tales.py',*args]), patch.object(Path,'exists',published):
                with self.assertRaisesRegex(SystemExit,'Legacy fairy-tale importer is locked'):
                    import_fairy_tales.main()


if __name__=='__main__':unittest.main()

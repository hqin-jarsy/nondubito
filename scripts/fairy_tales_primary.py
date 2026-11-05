"""Explicit English upgrade; every other primary byte is recoverably preserved."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BODY = re.compile(r'(<div class="lang-en local">.*?<div class="article-body">)(.*?)(</div><div class="entry-door">)', re.S)


def english_body(text):
    matches = list(BODY.finditer(text))
    assert len(matches) == 1, 'Expected one original English article body'
    return matches[0][2]


def english_title(text):
    matches=re.findall(r'<div class="lang-en local">.*?<h1>(.*?)</h1>',text,re.S)
    assert len(matches)==1
    return html.unescape(re.sub(r'<[^>]+>','',matches[0]))


def replace_english(text, body):
    assert len(list(BODY.finditer(text))) == 1
    return BODY.sub(lambda m: m[1] + body + m[3], text, count=1)


def strip_additions(text):
    for kind in ('LINKS', 'HEAD', 'SEARCH'):
        text = re.sub(r'<!-- FAIRY TALES LANGUAGE ' + kind + r' START -->.*?<!-- FAIRY TALES LANGUAGE '
                      + kind + r' END -->', '', text, flags=re.S)
    return text


def restore_original(text, spec, slug):
    text = strip_additions(text)
    archive = json.loads((ROOT/'data/fairy-tales/multilingual/original-english-bodies.json').read_text())
    if slug != 'index':
        text = replace_english(text, archive['bodies'][slug])
        for number, original in enumerate(archive['original_article_descriptions'][slug]):
            pattern = r'<!-- FAIRY TALES DESCRIPTION ' + str(number) + r' START -->.*?<!-- FAIRY TALES DESCRIPTION ' + str(number) + r' END -->'
            text = re.sub(pattern, lambda _:original, text, flags=re.S)
    else:
        for mode, original in archive['original_index_meta'].items():
            pattern = r'<!-- FAIRY TALES COUNT ' + mode + r' START -->.*?<!-- FAIRY TALES COUNT ' + mode + r' END -->'
            text = re.sub(pattern, lambda _:original, text, flags=re.S)
        for card_slug, original in archive['original_index_english_card_decks'].items():
            pattern = r'<!-- FAIRY TALES CARD DECK ' + re.escape(card_slug) + r' START -->.*?<!-- FAIRY TALES CARD DECK ' + re.escape(card_slug) + r' END -->'
            text = re.sub(pattern, lambda _:original['paragraph'], text, flags=re.S)
    return text


def protected_bodies(text):
    # Whole original Chinese and Hant sections include all source notes and nav.
    sections = re.findall(r'<div class="lang-(?:zh|hant) local">.*?</article></div>', text, re.S)
    assert len(sections) == 2
    return ''.join(sections)


def search_decks(spec, slug, english_deck=None):
    """Reuse actual localized source copy, not an English fallback for Chinese."""
    from prepare_action_sources import Document, one, normalize
    doc=Document((ROOT/spec['directory']/'index.html').read_text())
    decks={}
    for css,language in [('en','en'),('zh','zh-Hans'),('hant','zh-Hant')]:
        local=one(doc.root.walk(),lambda n:n.has('lang-'+css,'local'),'original localized index')
        if slug=='index':
            node=one(local.walk(),lambda n:n.has('story-deck'),'original hero deck')
        else:
            card=one(local.walk(),lambda n:n.tag=='a' and n.has('essay-card') and n.attrs.get('href')==slug+'.html','original localized card')
            node=one(card.walk(),lambda n:n.tag=='p','original card deck')
        decks[language]=normalize(node.text())
    if english_deck is not None:decks['en']=english_deck
    return decks


def upgrade(text, spec, slug):
    from full_series_languages import LABELS, alternatives, load_language, render_prose
    from fairy_tales_source import apparatus_inline
    text = restore_original(text, spec, slug)
    english_deck=None
    if slug == 'index':
        archive = json.loads((ROOT/'data/fairy-tales/multilingual/original-english-bodies.json').read_text())
        labels = {'en':'Han Qin (秦汉) · 2026 · Five chapters and three codas · Thirty complete essays · Eight languages',
                  'zh':'Han Qin (秦汉) · 2026 · 五章与三篇余响 · 30 篇完整散文 · 八种语言',
                  'hant':'Han Qin (秦漢) · 2026 · 五章與三篇餘響 · 30 篇完整散文 · 八種語言'}
        # Counts are publication UI, not a change to the original Chinese prose.
        for mode, original in archive['original_index_meta'].items():
            assert text.count(original) == 1
            replacement = '<!-- FAIRY TALES COUNT ' + mode + ' START --><div class="story-meta">' + labels[mode] + '</div><!-- FAIRY TALES COUNT ' + mode + ' END -->'
            text = text.replace(original,replacement,1)
        _, english = load_language('fairy-tales', 'en')
        for article in english['articles']:
            card_slug=article['slug']
            original=archive['original_index_english_card_decks'][card_slug]
            old_deck=html.unescape(re.search(r'content="([^"]*)"',archive['original_article_descriptions'][card_slug][0])[1])
            if article['deck']==old_deck:continue
            paragraph='<p>'+html.escape(original['prefix']+article['deck'])+'</p>'
            pattern=r'(<div class="lang-en local">.*?<a class="essay-card" href="'+re.escape(card_slug)+r'\.html">.*?)'+re.escape(original['paragraph'])
            text,n=re.subn(pattern,lambda m:m[1]+'<!-- FAIRY TALES CARD DECK '+card_slug+' START -->'+paragraph+'<!-- FAIRY TALES CARD DECK '+card_slug+' END -->',text,count=1,flags=re.S)
            assert n==1,(card_slug,'missing original English card description')
    if slug != 'index':
        _, data = load_language('fairy-tales', 'en')
        article = next(a for a in data['articles'] if a['slug'] == slug)
        english_deck=article['deck']
        archive = json.loads((ROOT/'data/fairy-tales/multilingual/original-english-bodies.json').read_text())
        for number, original in enumerate(archive['original_article_descriptions'][slug]):
            assert text.count(original) == 1
            tag = re.sub(r'content="[^"]*"', lambda _: 'content="' + html.escape(article['deck'], quote=True) + '"', original)
            text = text.replace(original, '<!-- FAIRY TALES DESCRIPTION ' + str(number) + ' START -->' + tag
                                + '<!-- FAIRY TALES DESCRIPTION ' + str(number) + ' END -->', 1)
        body = render_prose(article['body'])
        body += ''.join('<p><em>' + apparatus_inline(note,article['sources']) + '</em></p>' for note in article['notes'])
        body += '<ul class="fairy-source-links">' + ''.join(
            '<li><a href="' + html.escape(s['url'], quote=True) + '" target="_blank" rel="noopener">'
            + html.escape(s['title']) + '</a></li>' for s in article['sources']) + '</ul>'
        body += '<p class="fairy-edition-note"><em>' + apparatus_inline(article['source_note'],article['sources']) + '</em></p>'
        text = replace_english(text, body)
    links = ''.join('<span class="lang-sep">|</span><a class="lang-btn" href="'
                    + code + '/' + slug + '.html" lang="' + code + '">' + LABELS[code] + '</a>'
                    for code in spec['languages'])
    text, count = re.subn(r'(<div class="lang-toggle"[^>]*>)(.*?)(</div>)',
                         lambda m: m[1] + m[2] + '<!-- FAIRY TALES LANGUAGE LINKS START -->'
                         + links + '<!-- FAIRY TALES LANGUAGE LINKS END -->' + m[3], text, flags=re.S)
    assert count == 1
    classes={'en':'en','zh-Hans':'zh','zh-Hant':'hant'}
    search=''.join('<p hidden style="display:none!important" class="lw-search-deck lang-'+classes[language]+'">'+html.escape(deck)+'</p>'
                   for language,deck in search_decks(spec,slug,english_deck).items())
    text=text.replace('</main>','<!-- FAIRY TALES LANGUAGE SEARCH START -->'+search+'<!-- FAIRY TALES LANGUAGE SEARCH END --></main>',1)
    head = alternatives(spec, slug)
    head += '<script defer src="fairy-tales-language.js?v=20261104"></script>'
    head += '<script defer src="../../../../language-select.js?v=20261103"></script>'
    head += '<style>body .lang-toggle.lang-select-menu{display:inline-flex;width:max-content;max-width:100%;}</style>'
    return text.replace('</head>', '<!-- FAIRY TALES LANGUAGE HEAD START -->' + head
                        + '<!-- FAIRY TALES LANGUAGE HEAD END --></head>', 1)

#!/usr/bin/env python3
"""Fixed manuscript hashes, language parity, metadata, links and discovery."""
import hashlib
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

from build_theatre import ROOT, catalog, load, outputs, library_block
from build_content_registry import scan_page, parse_library_categories
from theatre_language_batch import DATE, LANGUAGES, SLUGS, ALL_SLUGS, alternatives
from connect_theatre_languages import ID


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('script', 'link'):
            self.links.append(attrs.get('src', attrs.get('href', '')))


works = catalog()
assert len(works) == len({w['slug'] for w in works}) == 35
fixture = json.loads((ROOT / 'scripts/fixtures/theatre-2026-10-18-approved.json').read_text())
batch = json.loads((ROOT / 'scripts/fixtures/theatre-2026-11-15-approved.json').read_text())
new_articles = {item['slug']: item for item in batch['articles']}
assert len(new_articles) == 15
expanded = {w['slug'] for w in works if w.get('editions_added')}
chinese_only_slugs = set(new_articles) - expanded
assert expanded == set(ALL_SLUGS) and len(chinese_only_slugs) == 9
assert sum('en' in w.get('languages',['en']) for w in works) == 26
assert set(fixture['articles']) == {w['slug'] for w in works if w['slug'] != 'hamilton' and w['slug'] not in new_articles}
for filename, expected in batch['protected_files'].items():
    if filename in {f'essays/theatre/{lang}/index.html' for lang in LANGUAGES}:
        continue  # Existing shelves gain only the separate bounded edition block.
    assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected, filename
# Only these two documented corrections may alter the newly translated Chinese sources.
RAGTIME_ZH_CORRECTIONS = (
    ('一群白人消防队员', '一群白人志愿消防队员'),
    ('Coalhouse杀死了参与毁车的消防队员，也与追随者发动纵火，后来占据',
     'Coalhouse枪杀了参与毁车的消防队员，烧了他们的消防站。他的追随者后来在城里多处放火。Coalhouse随后占据'),
)
for item in batch['articles']:
    received = ROOT / 'data/theatre/received/20261115' / item['source']
    raw = received.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['source_sha256']
    blocks = raw.decode().strip().split('\n\n')
    notice_index = item['notice_index']
    notice = blocks[notice_index].strip('*')
    body = '\n\n'.join(p for i, p in enumerate(blocks) if i not in (0, notice_index))
    imported = blocks[0] + '\n\n*' + notice + '*\n\n' + body + '\n'
    target = ROOT / f"data/theatre/{item['slug']}.zh.md"
    if item['slug'] in SLUGS:
        current = imported
        if item['slug'] == 'ragtime':
            for old, new in RAGTIME_ZH_CORRECTIONS:
                assert current.count(old) == 1
                current = current.replace(old, new)
        assert target.read_text() == current, (item['slug'], 'bounded factual source change')
    elif item['slug'] not in expanded:
        assert target.read_text() == imported, (item['slug'], 'lossless import')
    assert sha(imported) == item['imported_sha256']
    count_body = '\n'.join(p for i, p in enumerate(blocks)
                           if i not in (0, notice_index)
                           and i not in item['excluded_count_indices'] and not p.startswith('#'))
    assert len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', count_body)) == item['conservative_han'] >= 3000
    assert sha(body) == item['zh_body_sha256']
    assert (ROOT / f"data/theatre/{item['slug']}.en.md").exists() == (item['slug'] in expanded)
    for language in LANGUAGES:
        assert (ROOT / f"essays/theatre/{language}/{item['slug']}.html").exists() == (item['slug'] in expanded)

for lang, expected in fixture['hamilton_files'].items():
    assert sha((ROOT / f'data/theatre/hamilton.{lang}.md').read_text()) == expected, 'Hamilton source changed'

for path, expected in outputs().items():
    source = path.read_text()
    assert source == expected, path
    record = scan_page(ROOT, path)
    assert record['domain'] == 'stories' and record['category'] == 'theatre', record
    locale = path.parent.name
    # Check relative assets and navigation alike on native and primary pages.
    links = Links()
    links.feed(source)
    for href in links.links:
        url = urlsplit(href)
        if url.scheme or not url.path:
            continue
        target = (path.parent / unquote(url.path)).resolve()
        assert target.is_file(), (path, href)
    schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S).group(1))
    if locale in LANGUAGES:
        assert set(record['languages']) == {locale}
        assert alternatives(path.name) in source
        assert schema['inLanguage'] == locale and schema['dateModified'] == (DATE if path.stem == 'index' else next(w['editions_added'] for w in works if w['slug'] == path.stem))
        assert source.count('cloudflareinsights.com/beacon.min.js') == 1
        if path.stem == 'index':
            assert source.count('class="essay-card"') == 26
            assert schema['@type'] == 'CollectionPage'
        else:
            assert path.stem in expanded and schema['datePublished'] == '2026-11-15'
            assert schema['translationOfWork']['url'].endswith(f'/theatre/{path.name}')
            _,_,body = load(locale,path.stem)
            _,_,zh = load('zh',path.stem)
            assert len(body.split('\n\n')) == len(zh.split('\n\n'))
            assert body.count('\n## ') == zh.count('\n## ')
            assert len(body) >= 4500 and '<h3>' not in source
            assert not re.search(r'待补|待核|待写|\bTODO\b|\bTBD\b|\ufffd',body)
        continue
    chinese_only = path.stem in chinese_only_slugs
    expected_languages = {'zh-Hans', 'zh-Hant'} if chinese_only else {'en', 'zh-Hans', 'zh-Hant'}
    assert set(record['languages']) == expected_languages, record
    assert all(record['titles'].get(l) for l in expected_languages)
    expected_editions = 'zh zh-hant' if chinese_only else 'en zh zh-hant'
    assert f'data-editions="{expected_editions}"' in source
    if path.name == 'index.html':
        assert source.count('class="rf-book-card"') == 35
        assert schema['dateModified'] == DATE and alternatives(path.name) in source
        continue
    slug = path.stem
    work = next(w for w in works if w['slug'] == slug)
    articles = re.findall(r'<article class="rf-prose lang-\w+"[^>]*>(.*?)</article>', source, re.S)
    assert len(articles) == (2 if chinese_only else 3)
    assert len({a.count('<h2>') for a in articles}) == 1, (slug, 'sections')
    assert len({a.count('<p') for a in articles}) == 1, (slug, 'paragraphs')
    assert not any('<a ' in a or '<h3>' in a for a in articles)
    schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S).group(1))
    assert schema['@type'] == 'Article'
    assert schema['about']['@type'] == 'CreativeWork'
    assert schema['about']['name'] == work['name']
    assert schema['datePublished'] == work['published']
    assert schema['dateModified'] == work.get('editions_added',work['published'])
    if slug in expanded:
        assert alternatives(path.name) in source
        assert work['languages'] == ['en','zh','zh-hant',*LANGUAGES]
    assert schema['about']['creator']
    assert schema['about']['genre'] == 'Musical theatre'
    assert len(re.findall(r'rel="canonical"', source)) == 1
    assert all(f'hreflang="{lang}"' in source for lang in expected_languages | {'x-default'})
    zh = load('zh', slug)[2]
    en = '' if chinese_only else load('en', slug)[2]
    if chinese_only:
        approved = new_articles[slug]
        assert work['published'] == batch['published'] == '2026-11-15'
        assert set(schema['inLanguage']) == expected_languages
        assert '<article class="rf-prose lang-en"' not in source
        assert 'data-reader-languages="zh zh-hant"' in source
        assert 'aria-label="Other editions"' not in source
        assert not any(f'hreflang="{lang}"' in source for lang in ('en', 'ja', 'fr', 'de', 'es', 'ko'))
        assert sha(zh) == approved['zh_body_sha256']
        assert articles[0].count('<h2>') == approved['sections']
        assert articles[0].count('<p') == approved['paragraphs']
    elif slug in expanded:
        assert len(en.split()) >= 1800
        assert len(re.findall(r'[\u3400-\u9fff]',zh)) >= 3000
    elif slug != 'hamilton':
        approved = fixture['articles'][slug]
        assert sha(zh) == approved['zh_body_sha256'], slug
        assert sha(en) == approved['en_body_sha256'], slug
        assert len(re.findall(r'[\u3400-\u9fff]', re.sub(r'^#+.*$', '', zh, flags=re.M))) >= 3000, slug
        assert articles[0].count('<h2>') == approved['sections'], slug
        assert len(en.split()) == approved['en_words'] >= 900, slug
    else:
        assert len(en.split()) > 1800
    assert not re.search(r'待补|待核|待写|\bTODO\b|\bTBD\b', zh + en)

categories = parse_library_categories(ROOT / 'library.html')
assert len(categories) == len({c['number'] for c in categories}) == 18
assert any(c['href'] == 'essays/theatre/index.html' for c in categories)
library = (ROOT / 'library.html').read_text()
assert library_block() in library
# The curated homepage reaches this shelf through Explore, not a fixed feature card.
assert 'href="explore.html"' in (ROOT / 'index.html').read_text()
for filename in ('explore.html', 'library.html', 'latest.html'):
    assert 'essays/theatre/index.html' in (ROOT / filename).read_text(), filename
for language in ('en', 'zh-hans', 'zh-hant', *LANGUAGES):
    records = json.loads((ROOT / f'data/search/{language}.json').read_text())['records']
    matches = [r for r in records if r['u'].startswith('essays/theatre/')]
    if language in LANGUAGES:
        assert {r['u'] for r in matches if r['u'].startswith(f'essays/theatre/{language}/')} >= {
            f'essays/theatre/{language}/{slug}.html' for slug in ('index',*SLUGS)}
    else:
        expected_works = [w for w in works if language != 'en' or w['slug'] not in chinese_only_slugs]
        assert len(matches) == len(expected_works) + 1 and all(r['d'] == 'stories' for r in matches), (language,len(matches))
        assert {r['u'] for r in matches} == {'essays/theatre/index.html'} | {f'essays/theatre/{w["slug"]}.html' for w in expected_works}
sitemap = (ROOT / 'sitemap.xml').read_text()
for suffix in [''] + [w['slug'] + '.html' for w in works] + [
        f'{lang}/{slug}.html' for lang in LANGUAGES for slug in ('index',*SLUGS)]:
    assert sitemap.count(f'<loc>https://nondubito.net/essays/theatre/{suffix}</loc>') == 1
registry = json.loads((ROOT/'data/content-registry-prototype.json').read_text())['records']
for slug in ('index',*SLUGS):
    record, = (r for r in registry if r['canonical_path'] == f'essays/theatre/{slug}.html')
    assert set(record['editions']) == {'en','zh-Hans','zh-Hant',*LANGUAGES}
    assert record['updated_at'] == DATE and record['update_kind'] == 'expanded'
assert ID in (ROOT/'latest.html').read_text()
assert '2026-10-18-theatre-twenty' in (ROOT / 'latest.html').read_text()
assert '2026-11-15-theatre-fifteen' in (ROOT / 'latest.html').read_text()
print('OK: 35 theatre essays; 26 at eight languages, 9 Chinese-only; preserved originals, metadata, links and discovery')

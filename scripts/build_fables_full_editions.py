#!/usr/bin/env python3
"""Render complete Fables translations without changing the Chinese source.

Translations are paragraph-aligned canonical inputs, not generated summaries.
Original snapshots and source hashes are immutable. A last-build receipt guards
against silently overwriting later manual edits to the foreign article prose.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
from build_epic_full_editions import digest, div_span, region, within, within_body, navigation, metadata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/fables-full'
SERIES = ROOT / 'essays/everyday/stories/fables'
FOREIGN = ('en', 'ja', 'fr', 'de', 'es', 'ko')
LANGS = ('zh-Hans', 'zh-Hant') + FOREIGN
NOTES = {
 'ja': '中国語全文に基づく完全翻訳。すべての段落、引用、区切り、末尾のテキスト根拠を収録しています。',
 'fr': 'Traduction intégrale du texte chinois, avec tous les paragraphes, citations, séparations et la note finale sur les sources.',
 'de': 'Vollständige Übersetzung des chinesischen Textes mit allen Absätzen, Zitaten, Abschnittstrennungen und dem abschließenden Quellenhinweis.',
 'es': 'Traducción íntegra del texto chino, con todos sus párrafos, citas, separaciones y la nota final sobre las fuentes.',
 'ko': '중국어 전문을 바탕으로 한 완역입니다. 모든 문단과 인용, 구분, 마지막 텍스트 근거를 포함합니다.',
}
STYLE = '''<style id="fables-full-style">
.article-body.full-edition>p{margin:0 0 1.55em}
.article-body.full-edition blockquote p{margin:.55rem 0}
.article-head .story-deck{color:var(--cream)}
.story-wrap{overflow-wrap:anywhere}
.article-head h1,.essay-card h3,.series-nav-btn{min-width:0}
html[lang="ko"] .article-body{word-break:keep-all}
html[lang="ja"] .article-shell,html[lang="ko"] .article-shell{font-family:var(--cjk),var(--serif),serif}
</style>'''


def read_json(path):
 return json.loads(path.read_text())


def manifest():
 return read_json(DATA / 'manifest.json')


def snapshot(relative):
 return DATA / 'snapshots' / (str(relative) + '.txt')



def approved_chinese_region(filename, code):
 original = region(snapshot(filename).read_text(), 'lang-'+code)
 expected = manifest()['chinese_regions'][filename][code]
 assert digest(original) == expected, ('Original Chinese snapshot changed', filename, code)
 path = DATA / 'source-corrections.json'
 if path.exists():
  assert digest(path.read_bytes()) == manifest()['source_corrections_sha256']
  edits = read_json(path)['edits']
  assert [(e['episode'],e['text_index']) for e in edits] == [(6,3),(20,90)]
  for e in edits:
   if filename.startswith(f"{e['episode']:02}-"):
    fragments = e.get('chinese_fragments', {}).get(code)
    before = fragments['before'] if fragments else e['chinese_fragment_before']
    after = fragments['after'] if fragments else e['chinese_fragment_after']
    assert original.count(before) == 1
    original = original.replace(before, after, 1)
 return original


def source(episode):
 path = DATA / 'source' / f'{episode:02}.json'
 item = next(x for x in manifest()['essays'] if x['episode'] == episode)
 assert digest(path.read_bytes()) == item['source_sha256'], ('Chinese input changed', path)
 return read_json(path)


def inline(value):
 assert isinstance(value, str) and value.strip()
 assert not any(c in value for c in '<>'), ('Unsupported HTML', value)
 value = html.escape(value, quote=False)
 value = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)
 value = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', value)
 assert '*' not in value, ('Unbalanced emphasis', value)
 return value.replace('\n', '<br />\n')


def title(blocks):
 return html.unescape(re.sub('<[^>]+>', '', inline(blocks[0]['text'])))


def editions():
 result = {}
 for item in manifest()['essays']:
  src = source(item['episode'])
  copies = {}
  for lang in FOREIGN:
   values = read_json(DATA / 'translations' / lang / f"{item['episode']:02}.json")
   assert isinstance(values, list) and len(values) == len(src['texts']), ('Missing or merged paragraphs', item['slug'], lang)
   assert all(isinstance(t, str) and t.strip() for t in values), (item['slug'], lang)
   for i, (original, translated) in enumerate(zip(src['texts'], values)):
    inline(translated)
    assert original.count('**') == translated.count('**'), ('Strong emphasis differs', item['slug'], lang, i)
    assert original.count('*') == translated.count('*'), ('Emphasis differs', item['slug'], lang, i)
    assert original.count('\n') == translated.count('\n'), ('Line breaks differ', item['slug'], lang, i)
   it = iter(values)
   copies[lang] = [{**b, 'text':next(it)} if b['tag'] in ('h1','p') else dict(b) for b in src['blocks']]
  result[item['slug']] = copies
 return result


def body(blocks):
 out = []
 for block in blocks[1:]:
  tag = block['tag']
  if tag == 'p': out.append('<p>' + inline(block['text']) + '</p>')
  else: out.append({'hr':'<hr />', 'quote-start':'<blockquote>', 'quote-end':'</blockquote>'}[tag])
 return '\n'.join(out)



def mark_full_body(text):
 start, end, _, _ = div_span(text, 'article-body')
 opening = text[start:end]
 def add(m):
  classes = m[1].split()
  if 'full-edition' not in classes:
   classes.append('full-edition')
  return 'class="' + ' '.join(classes) + '"'
 opening = re.sub(r'class="([^"]*)"', add, opening, count=1)
 return text[:start] + opening + text[end:]


def prose(text, lang):
 part = region(text, 'lang-en') if lang == 'en' else text
 heading = re.search(r'<h1[^>]*>(.*?)</h1>', part, re.S)
 assert heading
 return {'body': digest(within_body(part, 'article-body').strip()), 'title': digest(heading[1])}


def guard(path, text, lang, copies):
 relative = str(path.relative_to(SERIES))
 base = snapshot(relative).read_text()
 current = prose(text, lang)
 canonical = {'body':digest(body(copies)), 'title':digest(html.escape(title(copies)))}
 previous = read_json(DATA / 'last-build.json').get(relative) if (DATA / 'last-build.json').exists() else None
 # Check each protected field independently so a changed title cannot be lost
 # just because its paragraph body still matches an accepted version.
 for key in ('body', 'title'):
  allowed = {prose(base, lang)[key], canonical[key]}
  if previous: allowed.add(previous[key])
  assert current[key] in allowed, ('Foreign HTML prose changed; preserve manual edits in canonical input before rebuilding', path, key)



def persist_query_language(text):
 # Entering from a foreign edition uses ?lang=... rather than a toggle button.
 # Persist that explicit choice before ordinary next/previous/index navigation.
 anchor = "if(['en','zh','zh-hant'].indexOf(saved)===-1)saved='zh';"
 addition = "if(q&&['en','zh','zh-hant'].indexOf(q)!==-1){localStorage.setItem('nd_lang',saved);localStorage.setItem('nondubito-lang',saved);}"
 assert text.count(anchor) == 1, 'Unrecognized primary language bootstrap; preserve manual change'
 if addition not in text:
  text = text.replace(anchor, anchor+addition, 1)
 click_anchor = "saved=b.dataset.langButton;"
 click_addition = "var languageURL=new URL(location.href);languageURL.searchParams.set('lang',saved);history.replaceState(history.state,'',languageURL.href);"
 assert text.count(click_anchor) == 1, 'Unrecognized language button handler; preserve manual change'
 if click_addition not in text:
  text = text.replace(click_anchor, click_anchor+click_addition, 1)
 return text


def style(text):
 text = re.sub(r'<style id="fables-full-style">.*?</style>\n?', '', text, flags=re.S)
 return text.replace('</head>', STYLE + '\n</head>', 1)


def render():
 all_editions = editions()
 receipt = manifest()
 for relative, expected in receipt['snapshots'].items():
  assert digest(snapshot(relative).read_bytes()) == expected, ('Snapshot changed', relative)
 result = {}
 for path in sorted(SERIES.rglob('*.html')):
  text = path.read_text()
  primary = path.parent == SERIES
  lang = 'en' if primary else path.parent.name
  assert lang in FOREIGN, path
  slug = path.stem
  if primary:
   for code in ('zh', 'hant'):
    assert region(text, 'lang-'+code) == approved_chinese_region(path.name, code), ('Chinese source drift', path, code)
  if slug in all_editions:
   guard(path, text, lang, all_editions[slug][lang])
  def replace_copy(part):
   if slug in all_editions:
    copy = all_editions[slug][lang]
    part = within(part, 'article-body', lambda _: body(copy))
    part = mark_full_body(part)
    part = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m:m[1]+html.escape(title(copy))+m[2], part, count=1, flags=re.S)
   return navigation(part, lang, all_editions, slug)
  text = within(text, 'lang-en', replace_copy) if primary else replace_copy(text)
  if slug in all_editions:
   text = metadata(text, title(all_editions[slug][lang]))
   if lang != 'en':
    text = re.sub(r'(<p class="edition-note"><em>).*?(</em></p>)', lambda m:m[1]+NOTES[lang]+m[2], text, count=1, flags=re.S)
  if not primary and slug == 'index':
   # The inherited index pointed one level too shallow, back to the Chinese
   # Fables index despite its Stories shelf label.
   text = text.replace('<a class="back-link" href="../index.html">', '<a class="back-link" href="../../index.html">', 1)
  if primary:
   text = persist_query_language(text)
  text = style(text)
  if primary:
   for code in ('zh', 'hant'):
    assert region(text, 'lang-'+code) == approved_chinese_region(path.name, code)
  result[path] = text
 assert len(result) == 144
 return result


def search_outputs():
 """Refresh this series only. Do not sweep unrelated stale search entries in."""
 from unittest.mock import patch
 import build_search_index as search
 paths = sorted(SERIES.rglob('*.html'))
 with patch.object(search, 'collect_pages', lambda: paths):
  _, chunks = search.build()
 outputs = {}
 prefix = str(SERIES.relative_to(ROOT)) + '/'
 for lang, new in chunks.items():
  path = ROOT / 'data/search' / f'{lang.lower()}.json'
  data = read_json(path)
  fresh = {row['u']:row for row in new}
  old = {row['u'] for row in data['records'] if row['u'].startswith(prefix)}
  assert old == set(fresh), ('Search route set changed', lang)
  data['records'] = [fresh[row['u']] if row['u'] in fresh else row for row in data['records']]
  outputs[path] = search.serialized(data)
 return outputs


def main():
 parser = argparse.ArgumentParser()
 parser.add_argument('--check', action='store_true')
 parser.add_argument('--refresh-search', action='store_true')
 args = parser.parse_args()
 outputs = render()
 stale = [p for p,t in outputs.items() if p.read_text() != t]
 if args.check:
  assert not stale, ('Stale Fables pages', stale)
  for p,t in search_outputs().items(): assert p.read_text() == t, ('Stale Fables search', p)
  print('OK: 23 complete six-language translations; 144 pages and eight search indexes current')
 else:
  for p in stale: p.write_text(outputs[p])
  record = {str(p.relative_to(SERIES)):prose(t, 'en' if p.parent == SERIES else p.parent.name) for p,t in outputs.items() if p.stem != 'index'}
  (DATA / 'last-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
  if args.refresh_search:
   for p,t in search_outputs().items():
    if p.read_text() != t: p.write_text(t)
  print(f'Updated {len(stale)} Fables pages')

if __name__ == '__main__': main()

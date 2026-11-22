#!/usr/bin/env python3
"""Register six reviewed Chapter 87 receipts and update only release entrypoints.

The translation manuscripts must already exist. This script never writes the
Chinese source, any translation source, any earlier chapter, or any search or
sitemap record. Run the original, hub, homepage and scoped discovery generators
after --apply to produce the public-facing files.
"""
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

from build_hongloumeng_hub import CH087_EXPANSION_ID, CH087_UPDATE_ID, CH087_TITLE_ZH
from build_hongloumeng_reading_english import NOTICE, NOTICE_COMPLETE
from hongloumeng_translations import CH087_LANGS, FOREIGN, ROOT, ch087_multilingual

DATE = '2026-11-22'
MAIN = 'originals/hongloumeng/'
RECEIPTS = 'data/originals/hongloumeng/'
FOLDER = 'translations/received/ch087'
MARKER = 'RED CHAMBER CH087 LANGUAGES LATEST'
LEDGER = 'data/site-updates.json'
MANIFEST = RECEIPTS + 'publication.json'
TITLE = {'en': 'Red Chamber: Chapter 87 in eight languages',
         'zh': '大知续红楼梦第八十七回：八语全文',
         'zh-hant': '大知續紅樓夢第八十七回：八語全文'}
SUMMARY = {'en': 'Six complete translations join the unchanged Simplified and Traditional Chinese editions of chapter 87. Chapters 81–87 can now be read in eight languages; chapters 88–110 remain unpublished.',
           'zh': '第八十七回新增英、日、法、德、西、韩六种全文译本，简繁中文定稿不变。第八十一至八十七回均可八语阅读，第八十八至第一百一十回尚未公开。',
           'zh-hant': '第八十七回新增英、日、法、德、西、韓六種全文譯本，簡繁中文定稿不變。第八十一至八十七回均可八語閱讀，第八十八至第一百一十回尚未公開。'}
ZH_HISTORICAL_TITLE = '第八十七回　鳳辣子失勢嘗世冷　痴公子有問立菱洲'
HISTORICAL_UPDATE = {
    'title': {'en': 'Thirty New Chapters of the Red Chamber: Chapter 87 (Chinese release)', 'zh': CH087_TITLE_ZH, 'zh-hant': ZH_HISTORICAL_TITLE},
    'summary': {'en': 'Chapter 87 of Han Qin’s original continuation was first released in Simplified and Traditional Chinese.',
                'zh': '秦汉原创续写第八十七回首次发布简繁中文全文。',
                'zh-hant': '秦漢原創續寫第八十七回首次發布簡繁中文全文。'},
}


def text(name):
    return (ROOT / name).read_text(encoding='utf-8')


def replace_one(page, before, after):
    if page.count(before) == 1:
        return page.replace(before, after, 1)
    if before not in page and page.count(after) == 1:
        return page
    raise ValueError(f'Expected one exact presentation fragment: {before[:70]!r}')


def receipt_hashes():
    hashes = {}
    for lang in FOREIGN:
        relative = f'{FOLDER}/ch087_{lang}.md'
        p = ROOT / RECEIPTS / relative
        if not p.is_file() or p.is_symlink():
            raise ValueError(f'Missing reviewed {lang} source: {p.name}')
        raw = p.read_bytes()
        manuscript = raw.decode('utf-8')
        pieces = re.split(r'^<!-- P(\d{3}) -->\s*$', manuscript, flags=re.M)
        if not pieces[0].strip().startswith('# '):
            raise ValueError(f'{p.name}: missing Markdown title')
        numbers = pieces[1::2]
        if numbers != [f'{i:03d}' for i in range(1,149)]:
            raise ValueError(f'{p.name}: need exact consecutive P001–P148')
        if any(not value.strip() or '<!--' in value or re.search(r'^#{1,6} ', value, re.M)
               for value in pieces[2::2]):
            raise ValueError(f'{p.name}: empty unit or unauthorized editorial markup')
        hashes[relative] = sha256(raw).hexdigest()
    return hashes


def update_manifest(hashes):
    pub = json.loads(text(MANIFEST))
    receipt = pub['chapter_publications']['ch087']
    if pub['chapter_sources']['ch087']['paragraphs'] != 148:
        raise ValueError('Frozen author manuscript unit count changed')
    if ch087_multilingual(pub):
        stored = pub['multilingual_publication']['received_files']
        if any(stored.get(k) != v for k,v in hashes.items()):
            raise ValueError('A registered Chapter 87 source changed after release binding')
    receipt.update(languages=['zh-Hans', 'zh-Hant', *FOREIGN],
                   foreign_published=DATE, source='ch087.zh.txt',
                   translations_dir=FOLDER, text_layout='ch087_{language}.md',
                   continuity='translations/continuity.json',
                   note='Chinese text unchanged; six independent complete translations, each aligned with the 148 author-source units.')
    receipt['provenance'] = {'zh-Hans': 'Author attachment, unchanged.',
                             'zh-Hant': 'Script conversion with contextual orthographic review, unchanged.',
                             'en/de/fr/es/ja/ko': 'Independent translations from the author’s Chinese text.'}
    pub['multilingual_publication']['received_files'].update(hashes)
    if set(receipt['languages']) != CH087_LANGS:
        raise ValueError('Incomplete Chapter 87 release')
    return json.dumps(pub, ensure_ascii=False, indent=2)+'\n'


def localized(tag, value):
    return ''.join(f'<{tag} class="lang-{"hant" if key=="zh-hant" else key}">{escape(value[key])}</{tag}>'
                   for key in ('en','zh','zh-hant'))


def latest_expansion():
    return (f'<!-- {MARKER} START --><section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-red-chamber-87-languages">'
            f'<header class="updates-date"><h2 id="date-red-chamber-87-languages"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid">'
            f'<article class="update-card" data-update-id="{CH087_EXPANSION_ID}"><div class="update-meta"><span class="update-kind">'
            +localized('span',{'en':'Expanded','zh':'语言拓展','zh-hant':'語言拓展'})+
            '</span><span>简 · 繁 · EN · DE · FR · ES · 日本語 · 한국어</span></div>'+
            localized('h3',TITLE)+localized('p',SUMMARY)+
            f'<a class="update-link lang-en" href="{MAIN}en/ch087.html">Read chapter 87 →</a>'
            f'<a class="update-link lang-zh" href="{MAIN}ch087.html">阅读第八十七回 →</a>'
            f'<a class="update-link lang-hant" href="{MAIN}zh-hant/ch087.html">閱讀第八十七回 →</a>'
            f'</article></div></section></div></section><!-- {MARKER} END -->')


def ledger_outputs():
    data = json.loads(text(LEDGER))
    original = next(row for row in data['updates'] if row['id'] == CH087_UPDATE_ID)
    if original['languages'] != ['zh','zh-hant'] or original['url'] != MAIN+'ch087.html':
        raise ValueError('Historical Chapter 87 Chinese receipt changed scope')
    latest = text('latest.html')
    a,b = '<!-- RED CHAMBER CH087 LATEST START -->','<!-- RED CHAMBER CH087 LATEST END -->'
    start,stop=latest.index(a),latest.index(b)
    card=latest[start:stop]
    if any(original[field] != HISTORICAL_UPDATE[field] for field in HISTORICAL_UPDATE):
        for field, tag in (('title','h3'),('summary','p')):
            card=replace_one(card,localized(tag,original[field]),localized(tag,HISTORICAL_UPDATE[field]))
        latest=latest[:start]+card+latest[stop:]
    original.update(HISTORICAL_UPDATE)
    row={'id':CH087_EXPANSION_ID,'date':DATE,'kind':'expanded','domain':'literature',
         'url':MAIN+'ch087.html','languages':['zh','zh-hant',*FOREIGN],
         'title':TITLE,'summary':SUMMARY}
    if any(x['date']>DATE for x in data['updates']):
        raise ValueError('Release day no longer newest; review Latest insertion order')
    data['updates']=[row,*[x for x in data['updates'] if x['id']!=row['id']]]
    if f'<!-- {MARKER} START -->' not in latest:
        anchor=latest.index(a)
        latest=latest[:anchor]+latest_expansion()+'\n'+latest[anchor:]
    elif latest.count(latest_expansion()) != 1:
        raise ValueError('The Chapter 87 expanded Latest card does not match its receipt')
    ids=re.findall(r'data-update-id="([^"]+)"',latest)
    if ids!=[item['id'] for item in data['updates']]:
        raise ValueError('Release would reorder unrelated Latest cards')
    return {LEDGER:json.dumps(data,ensure_ascii=False,indent=2)+'\n','latest.html':latest}


def collateral():
    project = {
        '第八十一至八十六回已有八语全文，第八十七回已发布简繁中文，第八十八回起尚未公开。':
            '第八十一至八十七回均有八语全文，第八十八回起尚未公开。',
        'chapters 81–86 are available in eight languages, chapter 87 in Chinese only, and chapters 88–110 remain unpublished.':
            'chapters 81–87 are available in eight languages, and chapters 88–110 remain unpublished.',
    }
    extra = {
        'Chapters 81–87 · Chapter 87 in Chinese':'Chapters 81–87 · 8 languages',
        '第八十一至八十七回 · 第八十七回为简繁中文':'第八十一至八十七回 · 8 种语言',
        '第八十一至八十七回 · 第八十七回為簡繁中文':'第八十一至八十七回 · 8 種語言',
        'Chapters 81–86 are available in eight languages; chapter 87 is in Simplified and Traditional Chinese only. Further chapters will follow.':
            'Chapters 81–87 are available in eight languages. Further chapters will follow.',
        '第八十一至八十六回有八语全文，第八十七回有简繁中文。后续逐回开放。':
            '第八十一至八十七回均有八语全文。后续逐回开放。',
        '第八十一至八十六回有八語全文，第八十七回有簡繁中文。後續逐回開放。':
            '第八十一至八十七回均有八語全文。後續逐回開放。',
    }
    home_originals = {
        'Original continuation · Chapters 81–87':'Original continuation · Chapters 81–87 · 8 languages',
        'Chapters 81–86 are available in eight languages. Chapter 87 is available in Simplified and Traditional Chinese only.':
            'Chapters 81–87 are available in eight languages.',
        '秦汉原创续写 · 第八十一至八十七回':'秦汉原创续写 · 第八十一至八十七回 · 8 种语言',
        '秦漢原創續寫 · 第八十一至八十七回':'秦漢原創續寫 · 第八十一至八十七回 · 8 種語言',
        '第八十一至八十六回有八语全文，第八十七回有简繁中文。':'第八十一至八十七回均有八语全文。',
        '第八十一至八十六回有八語全文，第八十七回有簡繁中文。':'第八十一至八十七回均有八語全文。',
    }
    # Replace full element fragments where the new value shares a prefix with
    # the old one (idempotence without permitting multiple matches).
    home_originals = {f'>{a}<' if a.count(' · ') else a: f'>{b}<' if a.count(' · ') else b
                      for a,b in home_originals.items()}
    plans={'library.html':{**project,**extra},'essays/literature/index.html':project,
           'originals/index.html':home_originals,
           **{f'classics/hongloumeng/en/{n}.html':{NOTICE:NOTICE_COMPLETE}
              for n in ('index','edition','ch080')}}
    outputs={}
    for name,edits in plans.items():
        page=text(name)
        for before,after in edits.items():
            page=replace_one(page,before,after)
        outputs[name]=page
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-inputs', action='store_true')
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    args=parser.parse_args()
    try:
        manifest=update_manifest(receipt_hashes())
        outputs={MANIFEST:manifest,**ledger_outputs(),**collateral()}
        if args.check:
            stale=[name for name,result in outputs.items() if text(name)!=result]
            if stale:
                raise ValueError('Unapplied release outputs: '+', '.join(stale))
        elif args.apply:
            for name,result in outputs.items():
                if text(name)!=result:
                    (ROOT/name).write_text(result,encoding='utf-8')
        print(f'OK: six complete receipts, manifest, and {len(outputs)-1} scoped collateral outputs'
              + (' planned without writes' if args.check_inputs else ''))
    except (OSError, ValueError, KeyError) as err:
        parser.exit(1, f'Chapter 87 expansion: {err}\n')


if __name__=='__main__':
    main()

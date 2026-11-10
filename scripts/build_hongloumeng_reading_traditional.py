#!/usr/bin/env python3
"""Render the frozen Traditional Chinese edition. Never convert corpus text.

Fixed UI follows the existing zh-hant site convention. Validation, assets and
all destination preflight protections are shared with the original renderer.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import build_hongloumeng_reading as base
from build_hongloumeng_reading import E, paragraph, tracked_html, load_assets, PUBLIC
CANONICAL = base.CANONICAL + 'zh-hant/'
CONTINUATION = base.CONTINUATION.replace('/index.html', '/zh-hant/index.html')
CSS = base.CSS.replace('Songti SC', 'Songti TC').replace('CJK SC', 'CJK TC').replace('Serif SC', 'Serif TC')
JS = base.JS.replace('找到 ', '找到 ').replace('共八十回，按每五回分组。', '共八十回，按每五回分組。')


def load(public_dir=PUBLIC):
    public_dir = Path(public_dir)
    base.preflight_inputs(public_dir, 'zh-Hant')
    raw = (public_dir / 'reading.zh-hant.json').read_bytes()
    manifest = json.loads((public_dir / 'manifest.zh-hant.json').read_bytes())
    return base.validate(json.loads(raw), manifest, raw, language='zh-Hant')


def release_gate(manifest, approval_path):
    if manifest['status'] != 'finalized' or approval_path is None:
        raise ValueError('Traditional release requires finalized text and hash-bound approval')
    base.checked_input_paths([approval_path])
    approval = json.loads(Path(approval_path).read_text(encoding='utf-8'))
    expected = dict(action='publish-hongloumeng-first80-traditional', text_version=manifest['text_version'],
                    reading_sha256=manifest['reading_sha256'], body_sha256=manifest['body_sha256'],
                    boundaries_finalized=True, approved=True, assets_sha256=manifest['build']['assets_sha256'])
    if approval != expected or type(approval['approved']) is not bool or type(approval['boundaries_finalized']) is not bool:
        raise ValueError('Traditional release approval differs from finalized text')


def source_gate(public_dir):
    """Bind this edition to the immutable, approved Simplified baseline."""
    base.preflight_inputs(public_dir, 'zh-Hant')
    expected = {'reading.zh.json': 'd7617874a5807001d13cd11faff212ffd5e7a50c0bba2275309fcf3143a9dfc1',
                'manifest.json': '074d6795190054b53a006adf3172b638e3b1779661c181db7ea20bd01664b1a4'}
    for name, checksum in expected.items():
        if base.digest((Path(public_dir)/name).read_bytes()) != checksum:
            raise ValueError('Traditional release Simplified baseline checksum differs: ' + name)
    reading, manifest = base.load(public_dir)
    if manifest['status'] != 'finalized' or manifest['body_sha256'] != '4da79146047e7ef3be8fbc75ef26a091e7e9673a5d7fe944dc6b390fd5e66e55':
        raise ValueError('Traditional release Simplified baseline body differs')


@tracked_html
def shell(title, description, content, filename, draft, edition):
    robots = '<meta name="robots" content="noindex,nofollow">' if draft else ''
    canonical_url = CANONICAL if filename == 'index.html' else CANONICAL + filename
    canonical = '' if draft else f'<link rel="canonical" href="{canonical_url}">'
    badge = '<span class="draft-badge">本地預覽 · 未定稿</span>' if draft else ''
    return f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}<title>{E(title)} — Non Dubito</title><meta name="description" content="{E(description)}">{canonical}<link rel="stylesheet" href="reader.css"><script defer src="reader.js"></script></head><body><a class="skip" href="#main">跳到正文</a><header class="site-header"><a class="brand" href="index.html">Non <span>Dubito</span></a><nav aria-label="閱讀導航"><a href="index.html">前八十回</a><a href="edition.html">版本說明</a></nav>{badge}</header><main id="main" tabindex="-1">{content}</main><footer><p>紅樓夢 · {E(edition)}</p></footer></body></html>'''


def render(reading, manifest, mode='draft', assets=None, bilingual=True):
    if mode not in ('draft', 'release'):
        raise ValueError('Explicit draft or release mode required')
    draft = mode == 'draft'
    chapters = reading['chapters']
    edition = reading['title']
    pages = {}
    for chapter in chapters:
        n = chapter['number']
        heading = ' '.join('<span class="' + ('chapter-number' if i == 0 else 'chapter-couplet') + '">' + E(part) + '</span>' for i, part in enumerate(chapter['title'].split()))
        previous = f'<a rel="prev" href="ch{n-1:03d}.html">← 第{n-1}回</a>' if n > 1 else '<span>第一回</span>'
        following = f'<a rel="next" href="ch{n+1:03d}.html">第{n+1}回 →</a>' if n < 80 else f'<a href="{CONTINUATION}">秦漢原創續寫目錄 →</a>'
        content = f'<article><header class="chapter-head"><p class="eyebrow">紅樓夢 · 前八十回</p><p class="edition-name">{E(edition)}</p><h1>{heading}</h1><div class="reader-tools"><button type="button" data-font="minus" aria-label="縮小正文字號">字 −</button><button type="button" data-font="reset" aria-label="恢復正文字號">默認字號</button><button type="button" data-font="plus" aria-label="放大正文字號">字 ＋</button><a href="#chapter-nav">至回末</a></div></header><div class="novel-text">' + ''.join(paragraph(b) for b in chapter['blocks']) + f'</div></article><nav class="chapter-nav" id="chapter-nav" aria-label="章回翻頁">{previous}<a href="index.html#batch{(n-1)//5+1:02d}">回目目錄</a>{following}</nav>'
        if n == 80:
            content += '<p class="edition-note">前八十回至此。秦漢原創第八十一至第一百一十回為當代續寫，與曹雪芹原著分別編排。</p>'
        name = f'ch{n:03d}.html'
        pages[name] = shell(chapter['title'] + ' · ' + edition, '紅樓夢前八十回中文正文。', content, name, draft, edition)
    batches = []
    for start in range(1, 81, 5):
        cards = ''.join(f'<li data-chapter="{c["number"]}" data-title="{E(c["title"])}"><a href="ch{c["number"]:03d}.html"><span class="chapter-index">{c["number"]:02d}</span><span>{E(c["title"])}</span></a></li>' for c in chapters[start-1:start+4])
        batches.append(f'<section class="chapter-batch" id="batch{(start-1)//5+1:02d}"><h2>第{start}至{start+4}回</h2><ol>{cards}</ol></section>')
    notice = '<p class="draft-notice">本地預覽，尚未定稿。</p>' if draft else ''
    intro = f'<header class="book-head"><p class="eyebrow">NON DUBITO · 中文古典閱讀</p><p class="book-title">紅樓夢</p><h1>{E(edition)}</h1><p class="deck">前八十回 · 中文正文</p>{notice}<div class="book-actions"><a class="primary-link" href="ch001.html">從第一回開始</a><a href="edition.html">版本說明</a></div></header><section class="catalog"><div class="catalog-head"><h2>八十回回目</h2><label>查找回目<input type="search" id="chapter-search" placeholder="回數或題名" autocomplete="off"></label></div><p id="search-status" class="edition-note" aria-live="polite">共八十回，按每五回分組。</p>' + ''.join(batches) + f'</section><section class="continuation"><h2>八十回以後</h2><p>秦漢原創第八十一至第一百一十回為當代續寫，並非曹雪芹佚稿，與本版原著分別編排。</p><a href="{CONTINUATION}">秦漢原創續寫目錄</a></section>'
    pages['index.html'] = shell('紅樓夢 · ' + edition, '紅樓夢前八十回中文正文與回目目錄。', intro, 'index.html', draft, edition)
    edition_content = f'<header class="chapter-head"><p class="eyebrow">紅樓夢 · 前八十回</p><h1>版本說明</h1></header><section class="editorial"><h2>{E(edition)}</h2><p>曹雪芹原著，秦漢整理校訂。本版據指定的匯校底本，以可讀性為目標，盡量保留原作語言風味；必要修補是本版的編輯選擇，不宣稱復原唯一古本。</p><p>“大知校正庚辰版”為本版名稱。底本含甲戌、庚辰等來源的材料，不是庚辰原抄本的逐字複刻。本版不收批註與其他回前題詩；第一回開卷自述後的八句詩為唯一例外，按作者決定保留。第十九回回末聯去版本標籤與重複引語後保留原聯文。第四、九回的異本尾聯依作者決定刪除。敘事中的詩詞曲文照常保留。</p><p>繁體版依本版已校訂的簡體正文轉寫，保留原文措辭、回目及詩詞分行；只依語境辨別繁簡字形，不作地域詞彙替換或改寫。</p>{notice}<h2>原著與續寫</h2><p>前八十回與秦漢原創第八十一至第一百一十回分別編排。後者為當代續寫，並非曹雪芹佚稿。</p></section>'
    pages['edition.html'] = shell('版本說明 · ' + edition, '紅樓夢前八十回版本及原著與原創續寫的邊界。', edition_content, 'edition.html', draft, edition)
    pages['reader.css'] = CSS
    pages['reader.js'] = JS
    pages.update(load_assets() if assets is None else assets)
    if bilingual:
        pages = base.add_language_links(pages, 'zh-Hant', draft)
    return pages


def build(public_dir, output, mode, approval=None):
    base.plan_output(public_dir, output, mode, base.OUTPUT_NAMES, language='zh-Hant')
    base.preflight_inputs(public_dir, 'zh-Hant')
    if approval is not None:
        base.checked_input_paths([approval])
    reading, manifest = load(public_dir)
    if mode == 'release':
        source_gate(public_dir)
        release_gate(manifest, approval)
    elif mode != 'draft':
        raise ValueError('Explicit draft or release mode required')
    pages = render(reading, manifest, mode, assets=load_assets(public_dir))
    output, destinations = base.plan_output(public_dir, output, mode, pages, language='zh-Hant')
    output.mkdir(parents=True, exist_ok=True)
    for filename, content in pages.items():
        destination = destinations[filename]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(base.as_bytes(content))
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PUBLIC)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=('draft', 'release'), required=True)
    parser.add_argument('--release-approval', type=Path)
    args = parser.parse_args()
    try:
        pages = build(args.input, args.output, args.mode, args.release_approval)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(f'Built {len(pages)} Traditional Chinese reading outputs in {args.mode} mode')


if __name__ == '__main__':
    main()

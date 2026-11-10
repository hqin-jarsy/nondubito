#!/usr/bin/env python3
"""Build the standalone reading edition using only public, allowlisted inputs.

Draft example:
  python3 -B scripts/build_hongloumeng_reading.py --mode draft --output ./reading-preview
Release requires an explicit, hash-bound approval file and finalized input status.
This renderer never reads editorial records or changes the text.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import stat
import sys
from pathlib import Path
from urllib.parse import urlsplit
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'data/hongloumeng/first80-public'
FORMAT = 'hongloumeng-reading/2'
CANONICAL = 'https://nondubito.net/classics/hongloumeng/'
CONTINUATION = 'https://nondubito.net/originals/hongloumeng/index.html'
E = html.escape
ASSET_HASHES = {'fonts/ARPHICPL.TXT': '5590533436c70f10f2f524ee61456238c290175c6662fbe1c700b5f038a6d328', 'fonts/FONT-NOTICE.txt': '34dad42e5094f1929adf71e1e725ee116ac6879e66f5aa2a8ae0323c7800dfac', 'fonts/nd-hlm-24aeb.woff2': 'e706e1976f4b579aa359ee3437e655cd27ce13776b4df1786fd03b13c82a9488'}
ASSETS_SHA256 = 'daee7ed1cab3d8eb1b2495079f601105601ea7d67db0a9fbcf576ebae19b7e5f'

def as_bytes(content):
    return content if isinstance(content, bytes) else content.encode('utf-8')


def load_assets(public_dir=PUBLIC):
    folder = Path(public_dir) / 'fonts'
    actual = {str(p.relative_to(public_dir)) for p in folder.rglob('*') if p.is_file()}
    if actual != set(ASSET_HASHES):
        raise ValueError('Missing or unexpected public font asset')
    result = {name: (Path(public_dir) / name).read_bytes() for name in ASSET_HASHES}
    if any(digest(raw) != ASSET_HASHES[name] for name, raw in result.items()):
        raise ValueError('Public font asset checksum mismatch')
    return result


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def body(chapter):
    return ''.join(block['text'] for block in chapter['blocks'])


def exact_keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or set(value) - set(required) - set(optional):
        raise ValueError('Unexpected or missing public fields')


def counts(chapter):
    blocks = chapter['blocks']
    return dict(number=chapter['number'], body_sha256=digest(body(chapter)),
                character_count=len(body(chapter)), block_count=len(blocks),
                layout_group_count=sum(b.get('first', False) for b in blocks if b['kind'] != 'diagram'),
                diagram_line_count=sum(b['kind'] == 'diagram' for b in blocks))


def validate(reading, manifest, raw):
    exact_keys(reading, ('schema_version', 'title', 'language', 'chapters'))
    if reading['schema_version'] != 1 or reading['language'] != 'zh-Hans':
        raise ValueError('Unsupported reading schema')
    if not isinstance(reading['title'], str) or not reading['title']:
        raise ValueError('Missing edition title')
    exact_keys(manifest, ('schema_version', 'text_version', 'status', 'reading_sha256', 'body_sha256',
                         'chapter_count', 'character_count', 'block_count', 'layout_group_count',
                         'diagram_line_count', 'chapters', 'build'))
    exact_keys(manifest['build'], ('renderer', 'encoding', 'body_join', 'assets_sha256'))
    if manifest['build'] != dict(renderer=FORMAT, encoding='UTF-8', body_join='concatenated-block-text-no-separator', assets_sha256=ASSETS_SHA256):
        raise ValueError('Unsupported build format')
    if manifest['schema_version'] != 1 or manifest['status'] not in ('draft', 'finalized'):
        raise ValueError('Invalid version status')
    if not isinstance(manifest['text_version'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', manifest['text_version']):
        raise ValueError('Invalid text version')
    chapters = reading['chapters']
    if not isinstance(chapters, list) or len(chapters) != 80:
        raise ValueError('Exactly 80 chapters required')
    for n, chapter in enumerate(chapters, 1):
        exact_keys(chapter, ('number', 'title', 'blocks'))
        if type(chapter['number']) is not int or chapter['number'] != n:
            raise ValueError('Chapter order differs')
        if not isinstance(chapter['title'], str) or not chapter['title'].startswith('第') or not chapter['title']:
            raise ValueError('Invalid chapter title')
        if not isinstance(chapter['blocks'], list) or not chapter['blocks']:
            raise ValueError('Empty chapter')
        opened = None
        for block in chapter['blocks']:
            exact_keys(block, ('kind', 'text'), ('first', 'last', 'heading', 'group_start'))
            kind = block['kind']
            if kind not in ('prose', 'verse', 'couplet', 'letter', 'diagram'):
                raise ValueError('Unknown block kind')
            if not isinstance(block['text'], str) or not block['text'] or any(c in block['text'] for c in '\r\n\x00'):
                raise ValueError('Invalid block text')
            if any(type(v) is not bool for k, v in block.items() if k not in ('kind', 'text')):
                raise ValueError('Invalid layout flags')
            if kind == 'prose':
                if set(block) != {'kind', 'text'} or opened:
                    raise ValueError('Unexpected prose layout')
            else:
                if not {'first', 'last'} <= block.keys():
                    raise ValueError('Missing group boundary')
                if block['first']:
                    if opened:
                        raise ValueError('Overlapping layout group')
                    opened = kind
                if opened != kind:
                    raise ValueError('Unbalanced layout group')
                if kind == 'diagram':
                    if set(block) != {'kind', 'text', 'first', 'last', 'heading', 'group_start'}:
                        raise ValueError('Incomplete diagram structure')
                elif 'heading' in block or 'group_start' in block:
                    raise ValueError('Unexpected heading')
                if block['last']:
                    opened = None
        if opened:
            raise ValueError('Unclosed layout group')
    expected = [counts(c) for c in chapters]
    if manifest['chapters'] != expected:
        raise ValueError('Chapter hashes or counts differ')
    totals = dict(chapter_count=80, body_sha256=digest(''.join(body(c) for c in chapters)), reading_sha256=digest(raw))
    for key in ('character_count', 'block_count', 'layout_group_count', 'diagram_line_count'):
        totals[key] = sum(c[key] for c in expected)
    if any(manifest[k] != v for k, v in totals.items()):
        raise ValueError('Aggregate checksum or counts differ')
    return reading, manifest


def load(public_dir=PUBLIC):
    raw = (public_dir / 'reading.zh.json').read_bytes()
    return validate(json.loads(raw), json.loads((public_dir / 'manifest.json').read_bytes()), raw)


def release_gate(manifest, approval_path):
    if manifest['status'] != 'finalized':
        raise ValueError('Release blocked: text is not finalized')
    if approval_path is None:
        raise ValueError('Release blocked: explicit hash-bound approval required')
    approval = json.loads(Path(approval_path).read_text(encoding='utf-8'))
    exact_keys(approval, ('action', 'text_version', 'reading_sha256', 'body_sha256', 'boundaries_finalized', 'approved', 'assets_sha256'))
    expected = dict(action='publish-hongloumeng-first80', text_version=manifest['text_version'],
                    reading_sha256=manifest['reading_sha256'], body_sha256=manifest['body_sha256'],
                    boundaries_finalized=True, approved=True, assets_sha256=manifest['build']['assets_sha256'])
    if approval != expected or type(approval['approved']) is not bool or type(approval['boundaries_finalized']) is not bool:
        raise ValueError('Release blocked: approval does not match finalized text')


def paragraph(block):
    classes = [block['kind']]
    classes += [name for key, name in (('first', 'layout-first'), ('last', 'layout-last'),
                                     ('heading', 'diagram-heading'), ('group_start', 'diagram-group-start')) if block.get(key)]
    return '<p class="' + ' '.join(classes) + '">' + E(block['text']) + '</p>'


@tracked_html
def shell(title, description, content, filename, draft, edition):
    robots = '<meta name="robots" content="noindex,nofollow">' if draft else ''
    canonical_url = CANONICAL if filename == 'index.html' else CANONICAL + filename
    canonical = '' if draft else f'<link rel="canonical" href="{canonical_url}">'
    badge = '<span class="draft-badge">本地预览 · 未定稿</span>' if draft else ''
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}<title>{E(title)} — Non Dubito</title><meta name="description" content="{E(description)}">{canonical}<link rel="stylesheet" href="reader.css"><script defer src="reader.js"></script></head><body><a class="skip" href="#main">跳到正文</a><header class="site-header"><a class="brand" href="index.html">Non <span>Dubito</span></a><nav aria-label="阅读导航"><a href="index.html">前八十回</a><a href="edition.html">版本说明</a></nav>{badge}</header><main id="main" tabindex="-1">{content}</main><footer><p>红楼梦 · {E(edition)}</p></footer></body></html>'''


def render(reading, manifest, mode='draft', assets=None):
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
        following = f'<a rel="next" href="ch{n+1:03d}.html">第{n+1}回 →</a>' if n < 80 else f'<a href="{CONTINUATION}">秦汉原创续写目录 →</a>'
        content = f'<article><header class="chapter-head"><p class="eyebrow">红楼梦 · 前八十回</p><p class="edition-name">{E(edition)}</p><h1>{heading}</h1><div class="reader-tools"><button type="button" data-font="minus" aria-label="缩小正文字号">字 −</button><button type="button" data-font="reset" aria-label="恢复正文字号">默认字号</button><button type="button" data-font="plus" aria-label="放大正文字号">字 ＋</button><a href="#chapter-nav">至回末</a></div></header><div class="novel-text">' + ''.join(paragraph(b) for b in chapter['blocks']) + f'</div></article><nav class="chapter-nav" id="chapter-nav" aria-label="章回翻页">{previous}<a href="index.html#batch{(n-1)//5+1:02d}">回目目录</a>{following}</nav>'
        if n == 80:
            content += '<p class="edition-note">前八十回至此。秦汉原创第八十一至第一百一十回为当代续写，与曹雪芹原著分别编排。</p>'
        name = f'ch{n:03d}.html'
        pages[name] = shell(chapter['title'] + ' · ' + edition, '红楼梦前八十回中文正文。', content, name, draft, edition)
    batches = []
    for start in range(1, 81, 5):
        cards = ''.join(f'<li data-chapter="{c["number"]}" data-title="{E(c["title"])}"><a href="ch{c["number"]:03d}.html"><span class="chapter-index">{c["number"]:02d}</span><span>{E(c["title"])}</span></a></li>' for c in chapters[start-1:start+4])
        batches.append(f'<section class="chapter-batch" id="batch{(start-1)//5+1:02d}"><h2>第{start}至{start+4}回</h2><ol>{cards}</ol></section>')
    notice = '<p class="draft-notice">本地预览，尚未定稿。</p>' if draft else ''
    intro = f'<header class="book-head"><p class="eyebrow">NON DUBITO · 中文古典阅读</p><p class="book-title">红楼梦</p><h1>{E(edition)}</h1><p class="deck">前八十回 · 中文正文</p>{notice}<div class="book-actions"><a class="primary-link" href="ch001.html">从第一回开始</a><a href="edition.html">版本说明</a></div></header><section class="catalog"><div class="catalog-head"><h2>八十回回目</h2><label>查找回目<input type="search" id="chapter-search" placeholder="回数或题名" autocomplete="off"></label></div><p id="search-status" class="edition-note" aria-live="polite">共八十回，按每五回分组。</p>' + ''.join(batches) + f'</section><section class="continuation"><h2>八十回以后</h2><p>秦汉原创第八十一至第一百一十回为当代续写，并非曹雪芹佚稿，与本版原著分别编排。</p><a href="{CONTINUATION}">秦汉原创续写目录</a></section>'
    pages['index.html'] = shell('红楼梦 · ' + edition, '红楼梦前八十回中文正文与回目目录。', intro, 'index.html', draft, edition)
    edition_content = f'<header class="chapter-head"><p class="eyebrow">红楼梦 · 前八十回</p><h1>版本说明</h1></header><section class="editorial"><h2>{E(edition)}</h2><p>曹雪芹原著，秦汉整理校订。本版据指定的汇校底本，以可读性为目标，尽量保留原作语言风味；必要修补是本版的编辑选择，不宣称复原唯一古本。</p><p>“大知校正庚辰版”为本版名称。底本含甲戌、庚辰等来源的材料，不是庚辰原抄本的逐字复刻。本版不收批注与其他回前题诗；第一回开卷自述后的八句诗为唯一例外，按作者决定保留。第十九回回末联去版本标签与重复引语后保留原联文。第四、九回的异本尾联依作者决定删除。叙事中的诗词曲文照常保留。</p>{notice}<h2>原著与续写</h2><p>前八十回与秦汉原创第八十一至第一百一十回分别编排。后者为当代续写，并非曹雪芹佚稿。</p></section>'
    pages['edition.html'] = shell('版本说明 · ' + edition, '红楼梦前八十回版本及原著与原创续写的边界。', edition_content, 'edition.html', draft, edition)
    pages['reader.css'] = CSS
    pages['reader.js'] = JS
    pages.update(load_assets() if assets is None else assets)
    return pages



def plan_output(public_dir, output, mode, filenames):
    """Validate every destination before any mkdir/write; never follow output links.

    Output links are rejected, including links in parent directories. The two
    standard macOS /tmp and /var ancestor aliases are permitted only when they
    resolve to their exact /private counterparts, never as the output root.
    This is a preflight for a local build, not a lock against concurrent mutation.
    """
    output = Path(output).absolute()
    if '..' in output.parts:
        raise ValueError('Output path must not contain parent traversal')
    public = Path(public_dir).resolve()
    protected = (ROOT / 'classics/hongloumeng').resolve()

    def existing_kind(path):
        try:
            info = path.lstat()
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(info.st_mode):
            system_alias = sys.platform == 'darwin' and path != output and str(path) in ('/tmp', '/var')
            if system_alias and path.resolve() == Path('/private') / path.relative_to('/'):
                return path.stat()
            raise ValueError('Output path must not contain a symlink: ' + str(path))
        return info

    def directories(path):
        for ancestor in reversed((path, *path.parents)):
            info = existing_kind(ancestor)
            if info is not None and not stat.S_ISDIR(info.st_mode):
                raise ValueError('Output parent is not a directory: ' + str(ancestor))

    def protected_target(path):
        if path == public or public in path.parents:
            raise ValueError('Output must not overwrite public inputs')
        if mode == 'draft' and (path == protected or protected in path.parents):
            raise ValueError('Draft output must not overwrite the existing reader')

    directories(output)
    physical = output.resolve()
    protected_target(physical)
    destinations = {}
    for filename in filenames:
        relative = Path(filename)
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError('Invalid output filename')
        destination = output / relative
        directories(destination.parent)
        info = existing_kind(destination)
        if info is not None and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise ValueError('Output target must be an unlinked regular file: ' + str(destination))
        resolved = destination.resolve()
        if physical not in resolved.parents:
            raise ValueError('Output destination escapes its directory')
        protected_target(resolved)
        destinations[filename] = destination
    return output, destinations


def build(public_dir, output, mode, approval=None):
    reading, manifest = load(public_dir)
    if mode == 'release':
        release_gate(manifest, approval)
    elif mode != 'draft':
        raise ValueError('Explicit draft or release mode required')
    pages = render(reading, manifest, mode, assets=load_assets(public_dir))
    output, destinations = plan_output(public_dir, output, mode, pages)
    output.mkdir(parents=True, exist_ok=True)
    for filename, content in pages.items():
        destination = destinations[filename]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(as_bytes(content))
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
    print(f'Built {sum(name.endswith(".html") for name in pages)} HTML pages + CSS/JS + {len(ASSET_HASHES)} font/license assets in {args.mode} mode: {args.output}')


# Embedded standalone reader assets; no dependency on the private review reader.
CSS = ':root{color-scheme:light;--paper:#f7f3ea;--ink:#302d26;--muted:#726a5f;--red:#8d4339;--line:#d8cdbb;--green:#35594e;--novel-size:21px}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Songti SC","Noto Serif CJK SC","Source Han Serif SC",serif}a{color:var(--green);text-underline-offset:.25em}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:2px solid var(--red);outline-offset:5px}button,input{font:inherit}button{cursor:pointer}html{scroll-padding-top:24px}.skip{position:absolute;top:-100px;left:20px;background:var(--paper);padding:16px;z-index:10}.skip:focus{top:0}.site-header{display:flex;flex-wrap:wrap;align-items:center;gap:18px 30px;padding:24px max(5%,20px);border-bottom:1px solid var(--line);font-family:system-ui,sans-serif}.brand{font-family:Georgia,serif;font-size:24px;text-transform:uppercase;text-decoration:none;white-space:nowrap}.brand span{color:var(--red)}nav{display:flex;flex-wrap:wrap;gap:22px}.site-header nav{font-size:13px}.draft-badge{margin-left:auto;font-size:12px;color:var(--muted)}main{max-width:880px;margin:0 auto;padding:60px 30px}.eyebrow{font:12px/1.6 system-ui,sans-serif;letter-spacing:.14em;color:var(--red)}h1{font-size:clamp(26px,4.5vw,40px);font-weight:500;line-height:1.7;text-wrap:balance}h2{font-size:24px;font-weight:500;line-height:1.6}.book-title{font-size:clamp(52px,10vw,80px);letter-spacing:.15em;margin:24px 0 0}.book-head h1{font-size:24px;letter-spacing:.06em;margin:4px 0 18px}.deck{font-size:23px;line-height:1.8}.edition-note{font-size:15px;line-height:1.9;color:var(--muted)}.book-actions{display:flex;align-items:center;flex-wrap:wrap;gap:22px;margin:32px 0 60px;font:14px system-ui,sans-serif}.primary-link{padding:14px 22px;background:var(--green);color:white;text-decoration:none}.catalog-head{display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}.catalog label{font:13px system-ui,sans-serif;color:var(--muted)}input{display:block;background:transparent;border:0;border-bottom:1px solid var(--line);padding:12px 0;width:230px;max-width:100%;color:var(--ink)}.chapter-batch{margin-top:36px}.chapter-batch h2{font-size:16px;color:var(--red);margin:24px 0 8px}.chapter-batch ol{list-style:none;padding:0;margin:0}.chapter-batch li{padding:18px 0;border-bottom:1px solid var(--line)}.chapter-batch a{display:flex;gap:20px;text-decoration:none;font-size:19px;line-height:1.7}.chapter-index{color:#a99a85;font:15px/2 system-ui,sans-serif;min-width:24px}.chapter-batch small{display:block;margin:6px 0 0 44px;font:11px/1.6 system-ui,sans-serif;color:var(--muted)}.continuation{border-top:2px solid var(--line);margin-top:60px;padding-top:28px;line-height:1.9}.chapter-head{padding-bottom:26px;margin-bottom:34px;border-bottom:1px solid var(--line)}.edition-name{font-size:14px;color:var(--muted)}.reader-tools{display:flex;flex-wrap:wrap;gap:12px;align-items:center;font:12px system-ui,sans-serif}.reader-tools button{border:1px solid var(--line);padding:9px 12px;background:transparent;color:var(--ink)}.novel-text{font-size:var(--novel-size);line-height:2.05;overflow-wrap:anywhere;line-break:strict}.novel-text p{margin:0 0 1.4em;text-indent:2em}.chapter-nav{border-top:1px solid var(--line);padding-top:24px;justify-content:space-between;line-height:1.8;font:14px/1.8 system-ui,sans-serif}.editorial{font-size:18px;line-height:2}.editorial h2{margin-top:38px}.editorial code,code{font-size:11px;overflow-wrap:anywhere;word-break:break-all}footer{max-width:880px;margin:auto;padding:20px 30px 50px;border-top:1px solid var(--line);font:12px/1.9 system-ui,sans-serif;color:var(--muted)}[hidden]{display:none!important}@media(max-width:540px){:root{--novel-size:19px}.site-header{padding:20px;gap:16px}.site-header nav{order:3;width:100%;gap:20px}.brand{font-size:22px}.draft-badge{font-size:10px}main{padding:32px 22px}.deck{font-size:20px}.book-actions{gap:18px}.chapter-batch a{font-size:17px;gap:14px}.chapter-batch small{margin-left:38px}.reader-tools{gap:8px}.reader-tools button{padding:8px}.chapter-nav{font-size:12px;gap:12px}footer{padding:20px 22px 40px}}@media print{.novel-text{font-size:12pt;line-height:1.8}main{max-width:none;padding:0}}\n\n.chapter-head h1 .chapter-number{display:block;font-size:17px;color:var(--muted);margin-bottom:14px}.chapter-head h1 .chapter-couplet{display:block;white-space:normal;line-height:1.7}\n\n\n.novel-text p.verse,.novel-text p.couplet{margin:0 0 0 1.5em;text-indent:0;white-space:normal;overflow-wrap:anywhere}\n.novel-text p.letter{margin:0 0 .35em 1.5em;text-indent:0;white-space:normal}\n.novel-text p.layout-first{margin-top:1.1em}\n.novel-text p.layout-last{margin-bottom:1.4em}\n@media(max-width:540px){.novel-text p.verse,.novel-text p.couplet,.novel-text p.letter{margin-left:.5em}}\n\n\n.novel-text p.diagram{margin:0 0 .15em 1.5em;text-indent:0;white-space:normal;overflow-wrap:anywhere}\n.novel-text p.diagram.diagram-heading{margin-top:1.1em;margin-bottom:.35em;color:var(--green);font-weight:600}\n.novel-text p.diagram.diagram-group-start{margin-top:1.1em}\n.novel-text p.diagram + p:not(.diagram){margin-top:1.4em}\n@media(max-width:540px){.novel-text p.diagram{margin-left:.5em}}\n\n.draft-notice{font:14px/1.9 system-ui,sans-serif;color:var(--red)}\n'

JS = '(()=>{"use strict";const root=document.documentElement;let font=null;try{const saved=Number(localStorage.getItem("hlm_reading_font"));if(saved>=17&&saved<=28){font=saved;root.style.setProperty("--novel-size",saved+"px")}}catch{}document.querySelectorAll("[data-font]").forEach(b=>b.addEventListener("click",()=>{const a=b.dataset.font;if(a==="reset"){font=null;root.style.removeProperty("--novel-size");try{localStorage.removeItem("hlm_reading_font")}catch{}return}font=Math.min(28,Math.max(17,(font??parseFloat(getComputedStyle(root).getPropertyValue("--novel-size")))+(a==="plus"?1:-1)));root.style.setProperty("--novel-size",font+"px");try{localStorage.setItem("hlm_reading_font",String(font))}catch{}}));const q=document.getElementById("chapter-search");if(q){q.addEventListener("input",()=>{const v=q.value.trim();let count=0;document.querySelectorAll("[data-chapter]").forEach(el=>{const hit=!v||el.dataset.title.includes(v)||el.dataset.chapter===v;el.hidden=!hit;if(hit)count++});document.querySelectorAll(".chapter-batch").forEach(s=>s.hidden=![...s.querySelectorAll("[data-chapter]")].some(e=>!e.hidden));document.getElementById("search-status").textContent=v?"找到 "+count+" 回":"共八十回，按每五回分组。"})}})();'

CSS = '@font-face{font-family:"ND HLM Rare";src:url("fonts/nd-hlm-24aeb.woff2") format("woff2");unicode-range:U+24AEB;font-style:normal;font-weight:400;font-display:swap}\n' + CSS.replace('font-family:"Songti SC"', 'font-family:"ND HLM Rare","Songti SC"')

if __name__ == "__main__":
    main()

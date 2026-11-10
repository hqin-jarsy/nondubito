#!/usr/bin/env python3
"""Check the verified first-eighty-chapter edition's bounded discovery changes.

Read-only by default. --write is required to update outputs, and additionally
requires finalized public inputs, explicitly supplied final hashes/version and
--boundaries-finalized. Every gate and complete output plan runs before writes.
This never builds the reader, scans the whole repository, or reads review data.
"""
from __future__ import annotations
import argparse
import copy
from datetime import date
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import build_content_registry as registry
import build_home_updates as home
import build_search_index as search
from build_sitemap import PageParser, sitemap_xml
from hongloumeng_discovery_scope import PUBLIC_HTML, private_path, site_relative_url

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nondubito.net/'
PREFIX = 'classics/hongloumeng/'
UPDATE_ID = 'hongloumeng-first80-reading'
BASE_FILES = PUBLIC_HTML | {'reader.css', 'reader.js'}
FONT_ASSETS = frozenset(('fonts/nd-hlm-24aeb.woff2', 'fonts/ARPHICPL.TXT', 'fonts/FONT-NOTICE.txt'))
HUBS = tuple('essays/literature/hlm/'+d+'index.html' for d in ('', 'en/', 'zh-hant/'))
CONTINUATION = tuple('originals/hongloumeng/'+d+f'ch{n:03d}.html'
                     for d in ('', 'en/', 'zh-hant/', 'de/', 'fr/', 'es/', 'ja/', 'ko/')
                     for n in range(81, 86))
EDITORIAL_HTML = (*HUBS, 'library.html', 'essays/literature/index.html', 'index.html', 'latest.html')
START = '<!-- RED CHAMBER FIRST80 LATEST START -->'
END = '<!-- RED CHAMBER FIRST80 LATEST END -->'
WRITABLE_FILES = frozenset((*EDITORIAL_HTML, 'data/site-updates.json', 'data/search-index.json',
                            'sitemap.xml', *(f'data/search/{lang.lower()}.json' for lang in search.SEARCH_LANGUAGES)))


def checked_path(root, path, *, must_exist=True):
    """Controlled publication inputs/outputs may not be aliases or leave root."""
    root, path = Path(root).absolute(), Path(path).absolute()
    try:
        if root.is_symlink():
            raise ValueError('symlink publication root')
        relative = path.relative_to(root)
        if '..' in relative.parts or private_path(relative):
            raise ValueError('private or nonlocal path')
        ancestor = root
        for part in relative.parts:
            ancestor /= part
            if ancestor.is_symlink():
                raise ValueError('symlink in selected path')
        actual = path.resolve(strict=must_exist).relative_to(root.resolve(strict=True))
        if private_path(actual):
            raise ValueError('private target')
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f'Unsafe publication path: {path}') from error
    return path


def read_text(root, path):
    return checked_path(root, path).read_text(encoding='utf-8')


def validate_write_paths(root, outputs):
    for path in outputs:
        path = checked_path(root, path)
        if path.relative_to(root).as_posix() not in WRITABLE_FILES:
            raise ValueError('Unexpected publication output path')


def validate_hub_inputs(root):
    checked_path(root, root/'data/hongloumeng/characters.json')
    directory = checked_path(root, root/'data/hongloumeng/readings')
    for path in directory.glob('[0-9][0-9].json'):
        checked_path(root, path)


def output_bytes(value):
    if not isinstance(value, (str, bytes)):
        raise ValueError('Public output must contain text or bytes')
    return value.encode('utf-8') if isinstance(value, str) else value


def validate_output_names(outputs):
    names = set(outputs)
    if not (BASE_FILES | FONT_ASSETS) <= names:
        raise ValueError('Missing required public reading output')
    if names != BASE_FILES | FONT_ASSETS:
        raise ValueError('Unexpected reading output outside the explicit public allowlist')
    if not output_bytes(outputs['fonts/nd-hlm-24aeb.woff2']).startswith(b'wOF2'):
        raise ValueError('Invalid WOFF2 output')
    return names


def validate_published_reader(root=ROOT, approval=None):
    import build_hongloumeng_reading as builder
    public = root/'data/hongloumeng/first80-public'
    for name in ('reading.zh.json', 'manifest.json', *FONT_ASSETS):
        checked_path(root, public/name)
    reading, manifest = builder.load(public)
    if manifest['status'] != 'finalized':
        raise ValueError('Discovery blocked: public text is not finalized')
    expected_approval = {key: manifest[key] for key in ('text_version', 'reading_sha256', 'body_sha256')}
    expected_approval['assets_sha256'] = manifest['build']['assets_sha256']
    expected_approval['boundaries_finalized'] = True
    if approval != expected_approval or type(approval.get('boundaries_finalized')) is not bool:
        raise ValueError('Discovery blocked: explicit final hashes, version and resolved boundaries required')
    assets = builder.load_assets(public)
    outputs = builder.render(reading, manifest, mode='release', assets=assets)
    allowed = validate_output_names(outputs)
    target = checked_path(root, root/PREFIX)
    if target.is_symlink() or not target.is_dir() or target.resolve() != root.resolve()/PREFIX:
        raise ValueError('Discovery blocked: invalid reader directory')
    actual = set()
    # Bounded to one edition. Private source directories are never traversed.
    for path in target.rglob('*'):
        if path.is_symlink():
            raise ValueError('Discovery blocked: symlink in reader directory')
        if path.is_file():
            actual.add(path.relative_to(target).as_posix())
    if actual != allowed:
        raise ValueError('Discovery blocked: reader files differ from explicit output allowlist')
    for name in sorted(allowed):
        if checked_path(root, target/name).read_bytes() != output_bytes(outputs[name]):
            raise ValueError(f'Discovery blocked: stale release output: {name}')
    return tuple(root/PREFIX/name for name in sorted(PUBLIC_HTML))


def publication_update(published):
    date.fromisoformat(published)
    return {'id': UPDATE_ID, 'date': published, 'kind': 'new', 'domain': 'literature',
            'url': PREFIX+'index.html', 'languages': ['zh'],
            'title': {'zh': '红楼梦前八十回：大知校正庚辰版', 'zh-hant': '紅樓夢前八十回：大知校正庚辰版',
                      'en': 'Dream of the Red Chamber: The First Eighty Chapters in Chinese'},
            'summary': {
                'zh': '前八十回中文正文已整理成独立读页，按回阅读与检索，保留正文诗词的分行。秦汉校正整理的原著与其第八十一回起的原创续写分别编排；本版外语翻译尚未发布。',
                'zh-hant': '前八十回中文正文已整理成獨立讀頁，按回閱讀與檢索，保留正文詩詞的分行。秦漢校正整理的原著與其第八十一回起的原創續寫分別編排；本版外語翻譯尚未發佈。',
                'en': 'The first eighty chapters are available as a Chinese reading edition, edited by Han Qin, with chapter navigation and verse lineation. This edition of the original novel is separate from Han Qin’s continuation beginning with chapter 81. Translations of this edition are not yet published.'}}


def resolve_date(ledger, requested):
    previous = [u for u in ledger['updates'] if u['id'] == UPDATE_ID]
    if len(previous) > 1:
        raise ValueError('Duplicate first-eighty-chapter update')
    if previous:
        published = previous[0]['date']
        if requested and requested != published:
            raise ValueError('Refusing to change the publication date')
    else:
        if not requested:
            raise ValueError('First refresh requires --date YYYY-MM-DD')
        published = requested
        if any(u['date'] > published for u in ledger['updates']):
            raise ValueError('New publication precedes the latest ledger entry')
    date.fromisoformat(published)
    return published


def latest_card(update):
    def localized(values, tag):
        return ''.join(f'<{tag} class="lang-{css}">{html.escape(values[lang])}</{tag}>'
                       for lang, css in (('en', 'en'), ('zh', 'zh'), ('zh-hant', 'hant')))
    return START+f'''<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-first80"><header class="updates-date"><h2 id="date-first80"><time datetime="{update['date']}">{update['date']}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{UPDATE_ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Chinese reading edition</span><span class="lang-zh">中文正文</span><span class="lang-hant">中文正文</span></span><span>简体中文</span></div>{localized(update['title'], 'h3')}{localized(update['summary'], 'p')}<a class="update-link" href="{PREFIX}index.html"><span class="lang-en">Read in Chinese →</span><span class="lang-zh">阅读前八十回 →</span><span class="lang-hant">閱讀前八十回（簡體） →</span></a></article></div></section></div></section>'''+END


def replace_latest(source, update):
    if START in source or END in source:
        if source.count(START) != 1 or source.count(END) != 1 or source.index(START) >= source.index(END):
            raise ValueError('Invalid Latest marker pair')
        result, count = re.subn(re.escape(START)+r'.*?'+re.escape(END), lambda _: latest_card(update), source, flags=re.S)
        if count != 1:
            raise ValueError('Invalid Latest replacement count')
        return result
    if f'data-update-id="{UPDATE_ID}"' in source:
        raise ValueError('Existing Latest card lacks its markers')
    first = re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">', source)
    if first is None:
        raise ValueError('Latest has no insertion point')
    return source[:first.start()]+latest_card(update)+'\n'+source[first.start():]


def replace_project_card(source, href):
    matches = list(re.finditer(r'<a href="'+re.escape(href)+r'" class="series-card">.*?</a>', source, re.S))
    if len(matches) != 1:
        raise ValueError('Expected exactly one Red Chamber project card')
    match = matches[0]
    card = match[0]
    texts = {
        'zh': '前八十回“大知校正庚辰版”现有简体中文正文；另有人物回顾、散文导读和研究论文。秦汉原创续写单独编排，第八十一至八十五回已有八语全文，第八十六回起尚未公开。',
        'en': 'Read the first eighty chapters in the Chinese Dazhi Revised Gengchen Edition, alongside character essays, reader essays and research. Han Qin’s original continuation is separate: chapters 81–85 are available in eight languages; chapters 86–110 remain unpublished.'}
    for lang, text in texts.items():
        pattern = r'(<p class="series-card-desc-'+lang+' lang-'+lang+r'">).*?(</p>)'
        card, count = re.subn(pattern, lambda m: m[1]+html.escape(text)+m[2], card, flags=re.S)
        if count != 1:
            raise ValueError('Project card description shape changed')
    return source[:match.start()]+card+source[match.end():]


def editorial_outputs(root, ledger, published):
    import build_hongloumeng_hub as hub
    validate_hub_inputs(root)
    update = publication_update(published)
    ledger = copy.deepcopy(ledger)
    ledger['updates'] = ([update if u['id'] == UPDATE_ID else u for u in ledger['updates']]
                         if any(u['id'] == UPDATE_ID for u in ledger['updates']) else [update, *ledger['updates']])
    outputs = {root/'data/site-updates.json': json.dumps(ledger, ensure_ascii=False, indent=2)+'\n'}
    for path, source in hub.render(include_first80=True, first80_date=published).items():
        outputs[root/path.relative_to(hub.ROOT)] = source
    for name, href in (('library.html', 'essays/literature/hlm/index.html'), ('essays/literature/index.html', 'hlm/index.html')):
        outputs[root/name] = replace_project_card(read_text(root, root/name), href)
    outputs[root/'latest.html'] = replace_latest(read_text(root, root/'latest.html'), update)
    config = json.loads(read_text(root, root/'data/home-updates.json'))
    outputs[root/'index.html'] = home.replace_section(read_text(root, root/'index.html'), home.render_section(ledger['updates'], config))
    return outputs


def reject_private_url(value):
    relative = site_relative_url(value)
    if relative is None:
        return
    if relative == 'data/hongloumeng' or relative.startswith('data/hongloumeng/'):
        raise ValueError('Source or private data found in discovery; review before publishing')
    if relative.startswith(PREFIX) and relative not in {*(PREFIX+name for name in PUBLIC_HTML)}:
        raise ValueError('Non-allowlisted reader URL found in discovery')


def search_records(root, sources):
    chunks = {lang: [] for lang in search.SEARCH_LANGUAGES}
    for path, source in sources.items():
        checked_path(root, path)
        if path.name == 'latest.html':
            continue
        for dictionary in (path.parent/'zh-hant-data'/f'{path.stem}.js', root/'zh-hant.js'):
            checked_path(root, dictionary, must_exist=False)
        page = registry.scan_page(root, path, source=source)
        title = page['document_title'] or next(iter(page['titles'].values()), None)
        metadata = PageParser(); metadata.feed(source)
        if not title or search.is_redirect(source) or 'noindex' in metadata.robots:
            raise ValueError('Invalid selected publication search page')
        languages = page['languages'] or ([page['html_lang']] if page['html_lang'] else [])
        if path.relative_to(root).as_posix().startswith(PREFIX) and languages != ['zh-Hans']:
            raise ValueError('The first-eighty-chapter edition must be Chinese only')
        for lang in chunks:
            if lang in languages:
                chunks[lang].append({'u': page['path'], 'k': page['record_type'], 'd': page['domain'],
                                    'c': page['category'], 's': page['series'], 'n': page['sequence'],
                                    't': page['titles'].get(lang) or title, 'x': page['description'] or '',
                                    'q': search.extract_search_text(source)})
    return chunks


def discovery_outputs(root, sources, published):
    scope = {path.relative_to(root).as_posix() for path in sources}
    if not scope <= {*(PREFIX+n for n in PUBLIC_HTML), *EDITORIAL_HTML, *CONTINUATION}:
        raise ValueError('Unexpected path in discovery scope')
    fresh = search_records(root, sources)
    manifest = json.loads(read_text(root, root/'data/search-index.json'))
    outputs, unique_urls = {}, set()
    for lang, replacements in fresh.items():
        path = root/'data/search'/f'{lang.lower()}.json'
        chunk = json.loads(read_text(root, path))
        for record in chunk['records']:
            reject_private_url(record['u'])
        by_url = {record['u']: record for record in replacements}
        merged = []
        for record in chunk['records']:
            if record['u'] not in scope:
                merged.append(record)
            elif record['u'] in by_url:
                merged.append(by_url.pop(record['u']))
        merged.extend(by_url.values())
        if len({r['u'] for r in merged}) != len(merged):
            raise ValueError('Duplicate search URLs')
        if merged != chunk['records']:
            chunk['records'] = merged
            outputs[path] = search.serialized(chunk)
        manifest['languages'][lang]['count'] = len(merged)
        unique_urls.update(r['u'] for r in merged)
    manifest['record_count'] = len(unique_urls)
    outputs[root/'data/search-index.json'] = search.serialized(manifest)
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    sitemap = root/'sitemap.xml'
    entries = {u.findtext(ns+'loc'): u.findtext(ns+'lastmod') for u in ET.fromstring(read_text(root, sitemap))}
    for url in entries:
        reject_private_url(url)
    for path, source in sources.items():
        metadata = PageParser(); metadata.feed(source)
        relative = path.relative_to(root).as_posix()
        expected = ORIGIN+(relative.removesuffix('index.html') if path.name == 'index.html' else relative)
        if metadata.canonical != expected or 'noindex' in metadata.robots:
            raise ValueError(f'Non-public or non-normalized canonical: {relative}')
        if expected not in entries or source != read_text(root, path):
            entries[expected] = published
    outputs[sitemap] = sitemap_xml(sorted(entries.items(), key=lambda pair: (pair[0] != ORIGIN, pair[0])))
    return outputs


def render(root=ROOT, requested_date=None, approval=None):
    reader_paths = validate_published_reader(root, approval)
    ledger = json.loads(read_text(root, root/'data/site-updates.json'))
    published = resolve_date(ledger, requested_date)
    outputs = editorial_outputs(root, ledger, published)
    paths = (*reader_paths, *(root/name for name in (*EDITORIAL_HTML, *CONTINUATION)))
    if any(not p.is_file() for p in paths):
        raise ValueError('A required public discovery page is missing')
    for path in paths:
        checked_path(root, path)
    sources = {p: outputs[p] if p in outputs else read_text(root, p) for p in paths}
    outputs.update(discovery_outputs(root, sources, published))
    validate_write_paths(root, outputs)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only check (the default)')
    mode.add_argument('--write', action='store_true', help='Explicitly write after every release gate passes')
    parser.add_argument('--date', help='Actual publication date, required on the first run')
    parser.add_argument('--reading-sha256')
    parser.add_argument('--body-sha256')
    parser.add_argument('--assets-sha256')
    parser.add_argument('--text-version')
    parser.add_argument('--boundaries-finalized', action='store_true')
    args = parser.parse_args()
    approval = dict(text_version=args.text_version, reading_sha256=args.reading_sha256,
                    body_sha256=args.body_sha256, assets_sha256=args.assets_sha256,
                    boundaries_finalized=args.boundaries_finalized)
    try:
        outputs = render(requested_date=args.date, approval=approval)
        validate_write_paths(ROOT, outputs)
        changed = {p: source for p, source in outputs.items() if read_text(ROOT, p) != source}
        if not args.write and changed:
            parser.error('Stale reading discovery: '+', '.join(str(p.relative_to(ROOT)) for p in changed))
        if args.write:
            validate_write_paths(ROOT, changed)
            for path, source in changed.items():
                checked_path(ROOT, path).write_text(source, encoding='utf-8')
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as error:
        parser.error(str(error))
    print(f'OK: scoped reading discovery; {len(changed)} changed files; reader text and private inputs untouched')


if __name__ == '__main__':
    main()

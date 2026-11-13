#!/usr/bin/env python3
"""Check the verified first-eighty-chapter edition's bounded discovery changes.

Read-only by default. --write is required to update outputs, and additionally
requires finalized public inputs, explicitly supplied final hashes/version and
--boundaries-finalized. Every gate and complete output plan runs before writes.
This never builds the reader, scans the whole repository, or reads review data.
"""
from __future__ import annotations
from hongloumeng_english_availability import english_publication
from hongloumeng_japanese_availability import japanese_publication
import argparse
import copy
from datetime import date
import html
import json
from pathlib import Path
import re
import stat
import sys
import xml.etree.ElementTree as ET
import build_content_registry as registry
import build_home_updates as home
import build_search_index as search
from build_sitemap import PageParser, sitemap_xml
from hongloumeng_discovery_scope import PUBLIC_HTML, private_path, site_relative_url, site_url_path, excluded_url

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nondubito.net/'
PREFIX = 'classics/hongloumeng/'
TRADITIONAL_PREFIX = PREFIX+'zh-hant/'
ENGLISH_PREFIX = PREFIX+'en/'
READER_HTML = frozenset(prefix+name for prefix in (PREFIX, TRADITIONAL_PREFIX) for name in PUBLIC_HTML)
UPDATE_ID = 'hongloumeng-first80-reading'
ENGLISH_UPDATE_ID = 'hongloumeng-first80-english-reading'
ENGLISH_START = '<!-- RED CHAMBER ENGLISH LATEST START -->'
ENGLISH_END = '<!-- RED CHAMBER ENGLISH LATEST END -->'
BASE_FILES = PUBLIC_HTML | {'reader.css', 'reader.js'}
FONT_ASSETS = frozenset(('fonts/nd-hlm-24aeb.woff2', 'fonts/ARPHICPL.TXT', 'fonts/FONT-NOTICE.txt'))
HUBS = tuple('essays/literature/hlm/'+d+'index.html' for d in ('', 'en/', 'zh-hant/'))
CONTINUATION = tuple('originals/hongloumeng/'+d+f'ch{n:03d}.html'
                     for d in ('', 'en/', 'zh-hant/', 'de/', 'fr/', 'es/', 'ja/', 'ko/')
                     for n in range(81, 86)) + ('originals/hongloumeng/en/index.html', 'originals/hongloumeng/ja/index.html')
EDITORIAL_HTML = (*HUBS, 'library.html', 'essays/literature/index.html', 'index.html', 'latest.html')
START = '<!-- RED CHAMBER FIRST80 LATEST START -->'
END = '<!-- RED CHAMBER FIRST80 LATEST END -->'
WRITABLE_FILES = frozenset((*EDITORIAL_HTML, 'data/site-updates.json', 'data/search-index.json',
                            'sitemap.xml', *(f'data/search/{lang.lower()}.json' for lang in search.SEARCH_LANGUAGES)))


def checked_path(root, path, *, must_exist=True):
    """Controlled publication inputs/outputs may not be aliases or leave root."""
    root, path = Path(root).absolute(), Path(path).absolute()
    try:
        if '..' in root.parts:
            raise ValueError('nonlocal publication root')
        # Inspect lexical ancestors before resolve can erase a caller's alias.
        # Match the reader's narrowly defined macOS system-directory exception.
        for ancestor in reversed((root, *root.parents)):
            info = ancestor.lstat()
            if stat.S_ISLNK(info.st_mode):
                system_alias = (sys.platform == 'darwin' and ancestor != root
                                and str(ancestor) in ('/tmp', '/var')
                                and ancestor.resolve() == Path('/private') / ancestor.relative_to('/'))
                if not system_alias:
                    raise ValueError('symlink publication root ancestor')
                info = ancestor.stat()
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError('publication root ancestor must be a directory')
        relative = path.relative_to(root)
        if '..' in relative.parts or private_path(relative):
            raise ValueError('private or nonlocal path')
        ancestor = root
        for part in relative.parts:
            ancestor /= part
            if ancestor.is_symlink():
                raise ValueError('symlink in selected path')
            if ancestor.exists():
                info = ancestor.stat()
                if not stat.S_ISDIR(info.st_mode) and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
                    raise ValueError('non-regular or hardlinked publication input')
                if ancestor != path and not stat.S_ISDIR(info.st_mode):
                    raise ValueError('non-directory publication ancestor')
        actual = path.resolve(strict=must_exist).relative_to(root.resolve(strict=True))
        if private_path(actual):
            raise ValueError('private target')
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f'Unsafe publication path: {path}') from error
    return path


def read_text(root, path):
    path = checked_path(root, path)
    if not path.is_file():
        raise ValueError('Publication text must be a regular file')
    return path.read_text(encoding='utf-8')


def validate_write_paths(root, outputs):
    for path in outputs:
        path = checked_path(root, path)
        if not path.is_file() or path.relative_to(root).as_posix() not in WRITABLE_FILES:
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


def validate_published_reader(root=ROOT, approval=None, *, traditional_approval=None, english=None):
    english = english_publication(root) if english is None else english
    if (root/ENGLISH_PREFIX).exists() and english is None:
        raise ValueError('Discovery blocked: English subtree is not independently validated')
    paths = validate_reader_edition(root, approval, bilingual=traditional_approval is not None, english=english)
    if traditional_approval is not None:
        paths += validate_reader_edition(root, traditional_approval, traditional=True, bilingual=True, english=english)
    japanese = japanese_publication(root)
    return paths + (tuple(english["paths"]) if english else ()) + (tuple(japanese["paths"]) if japanese else ())


def validate_reader_edition(root, approval, *, traditional=False, bilingual=False, english=None):
    japanese = japanese_publication(root)
    if not traditional and (root/ENGLISH_PREFIX).exists():
        english = english_publication(root) if english is None else english
        if english is None or english['root'] != root.resolve():
            raise ValueError('Discovery blocked: English subtree is not independently validated')
    if traditional:
        import build_hongloumeng_reading_traditional as builder
    else:
        import build_hongloumeng_reading as builder
    prefix = TRADITIONAL_PREFIX if traditional else PREFIX
    public = root/'data/hongloumeng/first80-public'
    for name in (('reading.zh-hant.json', 'manifest.zh-hant.json') if traditional else ('reading.zh.json', 'manifest.json')) + tuple(FONT_ASSETS):
        checked_path(root, public/name)
    reading, manifest = builder.load(public)
    if manifest['status'] != 'finalized':
        raise ValueError('Discovery blocked: public text is not finalized')
    expected_approval = {key: manifest[key] for key in ('text_version', 'reading_sha256', 'body_sha256')}
    expected_approval['assets_sha256'] = manifest['build']['assets_sha256']
    expected_approval['boundaries_finalized'] = True
    if traditional:
        expected_approval.update(action='publish-hongloumeng-first80-traditional', approved=True)
    if approval != expected_approval or type(approval.get('boundaries_finalized')) is not bool or (traditional and type(approval.get('approved')) is not bool):
        raise ValueError('Discovery blocked: explicit final hashes, version and resolved boundaries required')
    if traditional:
        builder.source_gate(public)
    assets = builder.load_assets(public)
    options = {'bilingual': True} if bilingual else {}
    outputs = builder.render(reading, manifest, mode='release', assets=assets, **options)
    from hongloumeng_japanese_navigation_binding import navigation_outputs
    if japanese:
        outputs = navigation_outputs(prefix, outputs)
    allowed = validate_output_names(outputs)
    target = checked_path(root, root/prefix)
    if target.is_symlink() or not target.is_dir() or target.resolve() != root.resolve()/prefix:
        raise ValueError('Discovery blocked: invalid reader directory')
    actual = set()
    # Bounded to one edition. Private source directories are never traversed.
    for path in target.rglob('*'):
        relative = path.relative_to(target)
        # The second edition is independently checked against its exact 87-file plan.
        if not traditional and relative.parts[0] == 'ja' and japanese:
            checked_path(root, path)
            continue
        if english and not traditional and relative.parts[0] == 'en':
            checked_path(root, path)
            continue
        if bilingual and not traditional and relative.parts[0] == 'zh-hant':
            checked_path(root, path)
            continue
        if path.is_symlink():
            raise ValueError('Discovery blocked: symlink in reader directory')
        checked_path(root, path)
        if path.is_dir() and relative.as_posix() != 'fonts':
            raise ValueError('Discovery blocked: directory outside output allowlist')
        if path.is_file():
            actual.add(path.relative_to(target).as_posix())
    if actual != allowed:
        raise ValueError('Discovery blocked: reader files differ from explicit output allowlist')
    for name in sorted(allowed):
        if checked_path(root, target/name).read_bytes() != output_bytes(outputs[name]):
            raise ValueError(f'Discovery blocked: stale release output: {name}')
    return tuple(root/prefix/name for name in sorted(PUBLIC_HTML))


def publication_update(published, *, traditional=False):
    date.fromisoformat(published)
    update = {'id': UPDATE_ID, 'date': published, 'kind': 'new', 'domain': 'literature',
            'url': PREFIX+'index.html', 'languages': ['zh'],
            'title': {'zh': '红楼梦前八十回：大知校正庚辰版', 'zh-hant': '紅樓夢前八十回：大知校正庚辰版',
                      'en': 'Dream of the Red Chamber: The First Eighty Chapters in Chinese'},
            'summary': {
                'zh': '前八十回中文正文已整理成独立读页，按回阅读与检索，保留正文诗词的分行。秦汉校正整理的原著与其第八十一回起的原创续写分别编排；本版外语翻译尚未发布。',
                'zh-hant': '前八十回中文正文已整理成獨立讀頁，按回閱讀與檢索，保留正文詩詞的分行。秦漢校正整理的原著與其第八十一回起的原創續寫分別編排；本版外語翻譯尚未發佈。',
                'en': 'The first eighty chapters are available as a Chinese reading edition, edited by Han Qin, with chapter navigation and verse lineation. This edition of the original novel is separate from Han Qin’s continuation beginning with chapter 81. Translations of this edition are not yet published.'}}

    if traditional:
        update['languages'] = ['zh', 'zh-hant']
        update['title']['zh'] += '（简体／繁体）'
        update['title']['zh-hant'] += '（簡體／繁體）'
        update['title']['en'] = 'Dream of the Red Chamber: The First Eighty Chapters in Simplified and Traditional Chinese'
        update['summary']['zh'] = update['summary']['zh'].replace('前八十回中文正文', '前八十回简体与繁体中文正文')
        update['summary']['zh-hant'] = update['summary']['zh-hant'].replace('前八十回中文正文', '前八十回簡體與繁體中文正文')
        update['summary']['en'] = update['summary']['en'].replace('a Chinese reading edition', 'Simplified and Traditional Chinese reading editions')
    return update


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


def resolve_english_date(ledger, requested):
    previous = [u for u in ledger['updates'] if u['id'] == ENGLISH_UPDATE_ID]
    if len(previous) > 1:
        raise ValueError('Duplicate English-launch update')
    if previous:
        published = previous[0]['date']
        if requested is not None and requested != published:
            raise ValueError('Refusing to change the English-launch date')
    else:
        if not requested:
            raise ValueError('Actual English local-generation date required')
        published = requested
        if any(u['date'] > published for u in ledger['updates']):
            raise ValueError('English launch precedes a newer ledger entry')
    if date.fromisoformat(published).isoformat() != published:
        raise ValueError('English-launch date must use YYYY-MM-DD')
    return published


def english_launch_date(ledger, publication):
    """Keep first publication distinct from a later local regeneration."""
    existing = any(u['id'] == ENGLISH_UPDATE_ID for u in ledger['updates'])
    return resolve_english_date(ledger, None if existing else publication['date'])


def english_publication_update(published):
    date.fromisoformat(published)
    return {'id': ENGLISH_UPDATE_ID, 'date': published, 'kind': 'new', 'domain': 'literature',
            'url': ENGLISH_PREFIX+'index.html', 'languages': ['en'],
            'title': {'en': 'Dream of the Red Chamber: Chapters 1–80 in English',
                      'zh': '红楼梦前八十回：独立英文译本', 'zh-hant': '紅樓夢前八十回：獨立英文譯本'},
            'summary': {'en': 'The Dazhi Revised Gengchen Edition now has an independent English translation, with verse lineation and separate translator notes. Cao Xueqin’s novel and Han Qin’s original continuation are presented separately.',
                        'zh': '大知校正庚辰版前八十回独立英文译本，保留诗词分行与独立标示的译者注。曹雪芹原著与秦汉原创续写分别编排。',
                        'zh-hant': '大知校正庚辰版前八十回獨立英文譯本，保留詩詞分行與獨立標示的譯者注。曹雪芹原著與秦漢原創續寫分別編排。'}}


def english_latest_card(update):
    def localized(values, tag):
        return ''.join(f'<{tag} class="lang-{css}">{html.escape(values[lang])}</{tag}>'
                       for lang, css in (('en','en'),('zh','zh'),('zh-hant','hant')))
    return ENGLISH_START+f'''<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-first80-english"><header class="updates-date"><h2 id="date-first80-english"><time datetime="{html.escape(update['date'])}">{html.escape(update['date'])}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ENGLISH_UPDATE_ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">English reading edition</span><span class="lang-zh">独立英文译本</span><span class="lang-hant">獨立英文譯本</span></span><span>English</span></div>{localized(update['title'],'h3')}{localized(update['summary'],'p')}<a class="update-link" href="{ENGLISH_PREFIX}index.html"><span class="lang-en">Read in English →</span><span class="lang-zh">阅读英文版 →</span><span class="lang-hant">閱讀英文版 →</span></a></article></div></section></div></section>'''+ENGLISH_END


def replace_english_latest(source, update):
    if ENGLISH_START in source or ENGLISH_END in source:
        if source.count(ENGLISH_START) != 1 or source.count(ENGLISH_END) != 1 or source.index(ENGLISH_START) >= source.index(ENGLISH_END):
            raise ValueError('Invalid English Latest marker pair')
        if source.count(f'data-update-id="{ENGLISH_UPDATE_ID}"') != 1:
            raise ValueError('Duplicate or missing English Latest card')
        return re.sub(re.escape(ENGLISH_START)+r'.*?'+re.escape(ENGLISH_END), lambda _: english_latest_card(update), source, count=1, flags=re.S)
    if f'data-update-id="{ENGLISH_UPDATE_ID}"' in source:
        raise ValueError('English Latest card lacks markers')
    first = re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',source)
    if first is None:
        raise ValueError('Latest has no insertion point')
    return source[:first.start()]+english_latest_card(update)+'\n'+source[first.start():]


def latest_card(update):
    def localized(values, tag):
        return ''.join(f'<{tag} class="lang-{css}">{html.escape(values[lang])}</{tag}>'
                       for lang, css in (('en', 'en'), ('zh', 'zh'), ('zh-hant', 'hant')))
    card = START+f'''<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-first80"><header class="updates-date"><h2 id="date-first80"><time datetime="{update['date']}">{update['date']}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{UPDATE_ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Chinese reading edition</span><span class="lang-zh">中文正文</span><span class="lang-hant">中文正文</span></span><span>简体中文</span></div>{localized(update['title'], 'h3')}{localized(update['summary'], 'p')}<a class="update-link" href="{PREFIX}index.html"><span class="lang-en">Read in Chinese →</span><span class="lang-zh">阅读前八十回 →</span><span class="lang-hant">閱讀前八十回（簡體） →</span></a></article></div></section></div></section>'''+END

    if 'zh-hant' in update['languages']:
        card = card.replace('<span>简体中文</span>', '<span>简体中文 · 繁體中文</span>')
        card = card.replace('</a></article>', '</a><a class="update-link" href="'+TRADITIONAL_PREFIX+'index.html">繁體中文 →</a></article>')
    return card


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


def replace_project_card(source, href, *, traditional=False, english=False):
    matches = list(re.finditer(r'<a href="'+re.escape(href)+r'" class="series-card">.*?</a>', source, re.S))
    if len(matches) != 1:
        raise ValueError('Expected exactly one Red Chamber project card')
    match = matches[0]
    card = match[0]
    texts = {
        'zh': '前八十回“大知校正庚辰版”现有简体中文正文；另有人物回顾、散文导读和研究论文。秦汉原创续写单独编排，第八十一至八十五回已有八语全文，第八十六回起尚未公开。',
        'en': 'Read the first eighty chapters in the Chinese Dazhi Revised Gengchen Edition, alongside character essays, reader essays and research. Han Qin’s original continuation is separate: chapters 81–85 are available in eight languages; chapters 86–110 remain unpublished.'}
    if traditional:
        texts['zh'] = texts['zh'].replace('现有简体中文正文', '现有简体与繁体中文正文')
        texts['en'] = texts['en'].replace('in the Chinese Dazhi', 'in the Simplified and Traditional Chinese Dazhi')
    if english:
        texts['zh'] = texts['zh'].replace('现有简体与繁体中文正文', '现有简体、繁体中文及独立英文译本').replace('现有简体中文正文', '现有简体、繁体中文及独立英文译本')
        texts['en'] = 'Read the first eighty chapters of the Dazhi Revised Gengchen Edition in Chinese and independent English translation, alongside character essays, reader essays and research. Han Qin’s original continuation is separate: chapters 81–85 are available in eight languages; chapters 86–110 remain unpublished.'
    for lang, text in texts.items():
        pattern = r'(<p class="series-card-desc-'+lang+' lang-'+lang+r'">).*?(</p>)'
        card, count = re.subn(pattern, lambda m: m[1]+html.escape(text)+m[2], card, flags=re.S)
        if count != 1:
            raise ValueError('Project card description shape changed')
    return source[:match.start()]+card+source[match.end():]


def editorial_outputs(root, ledger, published, *, traditional=False, english=None):
    import build_hongloumeng_hub as hub
    validate_hub_inputs(root)
    update = publication_update(published, traditional=traditional)
    if english:
        original = [u for u in ledger['updates'] if u['id'] == UPDATE_ID]
        if len(original) != 1:
            raise ValueError('English launch requires one existing Chinese publication record')
        update = copy.deepcopy(original[0])
    ledger = copy.deepcopy(ledger)
    ledger['updates'] = ([update if u['id'] == UPDATE_ID else u for u in ledger['updates']]
                         if any(u['id'] == UPDATE_ID for u in ledger['updates']) else [update, *ledger['updates']])
    english_update = None
    if english:
        launch = english_launch_date(ledger, english)
        english_update = english_publication_update(launch)
        ledger['updates'] = ([english_update if u['id'] == ENGLISH_UPDATE_ID else u for u in ledger['updates']]
                             if any(u['id'] == ENGLISH_UPDATE_ID for u in ledger['updates']) else [english_update, *ledger['updates']])
    outputs = {root/'data/site-updates.json': json.dumps(ledger, ensure_ascii=False, indent=2)+'\n'}
    for path, source in hub.render(include_first80=True, first80_date=published, include_traditional=traditional).items():
        outputs[root/path.relative_to(hub.ROOT)] = source
    for name, href in (('library.html', 'essays/literature/hlm/index.html'), ('essays/literature/index.html', 'hlm/index.html')):
        outputs[root/name] = replace_project_card(read_text(root, root/name), href, traditional=traditional, english=bool(english))
    latest = read_text(root, root/'latest.html')
    outputs[root/'latest.html'] = replace_english_latest(latest, english_update) if english_update else replace_latest(latest, update)
    config = json.loads(read_text(root, root/'data/home-updates.json'))
    outputs[root/'index.html'] = home.replace_section(read_text(root, root/'index.html'), home.render_section(ledger['updates'], config))
    return outputs


def reject_private_url(value, *, root=None, english=None):
    original = site_url_path(value)
    relative = site_relative_url(value)
    if relative is None:
        return
    if any(name == 'data/hongloumeng' or name.startswith('data/hongloumeng/') for name in (original, relative)):
        raise ValueError('Source or private data found in discovery; review before publishing')
    if excluded_url(value, root=root, english=english):
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
        relative = path.relative_to(root).as_posix()
        expected_language = 'ja' if relative.startswith(PREFIX+'ja/') else 'en' if relative.startswith(ENGLISH_PREFIX) else ('zh-Hant' if relative.startswith(TRADITIONAL_PREFIX) else 'zh-Hans')
        if relative.startswith(PREFIX) and (languages != [expected_language] or page['html_lang'] != expected_language):
            raise ValueError('The first-eighty-chapter edition must contain only its declared English language' if expected_language == 'en' else 'The first-eighty-chapter edition must contain only its own Chinese language')
        for lang in chunks:
            if lang in languages:
                chunks[lang].append({'u': page['path'], 'k': page['record_type'], 'd': page['domain'],
                                    'c': page['category'], 's': page['series'], 'n': page['sequence'],
                                    't': page['titles'].get(lang) or title, 'x': page['description'] or '',
                                    'q': search.extract_search_text(source)})
    return chunks


def discovery_outputs(root, sources, published, *, english=None):
    scope = {path.relative_to(root).as_posix() for path in sources}
    japanese = japanese_publication(root)
    reader_html = READER_HTML | ({ENGLISH_PREFIX+n for n in PUBLIC_HTML} if english else set()) | ({'classics/hongloumeng/ja/'+n for n in PUBLIC_HTML} if japanese else set())
    changed_presentation = set(english.get('modifiedPaths', ())) if english else set()
    if not changed_presentation <= {*READER_HTML, 'originals/hongloumeng/en/index.html'}:
        raise ValueError('Unexpected modified presentation date scope')
    if not scope <= {*reader_html, *EDITORIAL_HTML, *CONTINUATION}:
        raise ValueError('Unexpected path in discovery scope')
    fresh = search_records(root, sources)
    manifest = json.loads(read_text(root, root/'data/search-index.json'))
    outputs, unique_urls = {}, set()
    for lang, replacements in fresh.items():
        path = root/'data/search'/f'{lang.lower()}.json'
        chunk = json.loads(read_text(root, path))
        for record in chunk['records']:
            reject_private_url(record['u'], root=root, english=bool(english))
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
        reject_private_url(url, root=root, english=bool(english))
    for path, source in sources.items():
        metadata = PageParser(); metadata.feed(source)
        relative = path.relative_to(root).as_posix()
        expected = ORIGIN+(relative.removesuffix('index.html') if path.name == 'index.html' else relative)
        if metadata.canonical != expected or 'noindex' in metadata.robots:
            raise ValueError(f'Non-public or non-normalized canonical: {relative}')
        if expected not in entries or source != read_text(root, path) or relative in changed_presentation:
            entries[expected] = english['date'] if english and (relative.startswith((ENGLISH_PREFIX, PREFIX+'ja/')) or relative in changed_presentation or expected in entries and source != read_text(root, path)) else published
    outputs[sitemap] = sitemap_xml(sorted(entries.items(), key=lambda pair: (pair[0] != ORIGIN, pair[0])))
    return outputs


def render(root=ROOT, requested_date=None, approval=None, *, traditional_approval=None):
    english = english_publication(root)
    reader_paths = validate_published_reader(root, approval, traditional_approval=traditional_approval, english=english)
    ledger = json.loads(read_text(root, root/'data/site-updates.json'))
    published = resolve_date(ledger, requested_date)
    outputs = editorial_outputs(root, ledger, published, traditional=traditional_approval is not None, english=english)
    paths = (*reader_paths, *(root/name for name in (*EDITORIAL_HTML, *CONTINUATION)))
    if any(not p.is_file() for p in paths):
        raise ValueError('A required public discovery page is missing')
    for path in paths:
        checked_path(root, path)
    sources = {p: outputs[p] if p in outputs else read_text(root, p) for p in paths}
    outputs.update(discovery_outputs(root, sources, published, english=english))
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
    parser.add_argument('--traditional', action='store_true')
    for field in ('reading-sha256', 'body-sha256', 'assets-sha256', 'text-version'):
        parser.add_argument('--traditional-'+field)
    parser.add_argument('--traditional-approved', action='store_true')
    args = parser.parse_args()
    approval = dict(text_version=args.text_version, reading_sha256=args.reading_sha256,
                    body_sha256=args.body_sha256, assets_sha256=args.assets_sha256,
                    boundaries_finalized=args.boundaries_finalized)
    try:
        traditional_approval = None
        if args.traditional:
            traditional_approval = dict(action='publish-hongloumeng-first80-traditional', approved=args.traditional_approved,
                text_version=args.traditional_text_version, reading_sha256=args.traditional_reading_sha256,
                body_sha256=args.traditional_body_sha256, assets_sha256=args.traditional_assets_sha256,
                boundaries_finalized=args.boundaries_finalized)
        outputs = render(requested_date=args.date, approval=approval, traditional_approval=traditional_approval)
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

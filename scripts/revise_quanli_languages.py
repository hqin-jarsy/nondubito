#!/usr/bin/env python3
"""Export and replace legacy essay bodies in five locales (Power by default).

The repository source for Simplified Chinese and English remains its existing
HTML; Traditional keeps its offline dictionaries. No discovery routes, page
shells, citation blocks or titles change. Search refreshes only the heading
query for each revised translation, not its identity or description.
"""
import argparse
import json
import re
from dataclasses import dataclass
from hashlib import sha256
from html import escape, unescape
from pathlib import Path

from build_content_registry import attr_value
from build_search_index import extract_search_text, serialized


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ('ja', 'fr', 'de', 'es', 'ko')
HEADINGS = {'h2', 'h3', 'h4', 'h5', 'h6'}


@dataclass(frozen=True)
class Series:
    label: str
    slug: str
    scratch_slug: str
    source_heading: str
    count: int = 7
    reference_emphasis: tuple[str, ...] = ()

    @property
    def slugs(self):
        return tuple(f'ep{i:02d}' for i in range(1, self.count + 1))

    @property
    def pages(self):
        return ROOT / 'essays' / self.slug

    @property
    def changes(self):
        return ROOT / 'data' / self.slug / 'multilingual'

    @property
    def scratch(self):
        return Path(f'/tmp/nd_{self.scratch_slug}_final')


POWER = Series('Power', 'quanli', 'power', 'h3')
PAGES, CHANGES, SCRATCH, SLUGS = POWER.pages, POWER.changes, POWER.scratch, POWER.slugs


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return path.read_text(encoding='utf-8')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def pretty(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def plain(html):
    return unescape(re.sub(r'<[^>]+>', '', html))


def body_span(html, language=None):
    """Return the inner range of the single requested body div, not its wrapper."""
    sought = {'essay-body'} | ({f'lang-{language}'} if language else set())
    starts = [m for m in re.finditer(r'<div\b([^>]*)>', html) if sought <=
              set((attr_value(m[1], 'class') or '').split())]
    require(len(starts) == 1, f'expected one essay body for {language}, got {len(starts)}')
    start, depth = starts[0].end(), 1
    for tag in re.finditer(r'<(/?)div\b[^>]*>', html[start:]):
        depth += -1 if tag[1] else 1
        if depth == 0:
            return start, start + tag.start()
    raise ValueError(f'unclosed body {language}')


def tokenize(html, *, source=True, source_heading=POWER.source_heading):
    """Prose blocks; remove separately rendered academic footer notes only."""
    html = re.sub(r'<div class="essay-footer-note">.*?</div>', '', html, flags=re.S)
    html = re.sub(r'<p class="essay-footer-note">.*?</p>', '', html, flags=re.S)
    html = re.sub(r'</?section>', '', html)
    blocks = []
    regex = r'<(p|h[2-6])>(.*?)</\1>'
    for m in re.finditer(regex, html, flags=re.S):
        content = m[2]
        strong = re.match(r'^<strong>(.*?)</strong>', content, flags=re.S)
        rest = content[strong.end():] if strong else content
        require(not re.search(r'<[/a-zA-Z]', rest), f'unexpected inline markup: {content[:65]}')
        block = {'tag': m[1], 'text': plain(content)}
        if strong:
            block['strong'] = plain(strong[1])
        if not source and m[1] == 'h2':
            block['tag'] = source_heading  # older compressed bodies use h2 presentation
        blocks.append(block)
    require(bool(blocks) and not re.sub(regex, '', html, flags=re.S).strip(),
            'unexpected structure/text outside prose blocks')
    return blocks


def metadata(html):
    titles = re.findall(r'<h1>(.*?)</h1>', html, flags=re.S)
    metas = [attr_value(m[0], 'content') for m in re.finditer(r'<meta\b[^>]*>', html)
             if attr_value(m[0], 'name') == 'description']
    require(len(titles) == 1 and len(metas) == 1 and bool(metas[0]), 'missing article title/deck')
    return {'title': plain(titles[0]), 'deck': metas[0]}


def original_blocks(html, language, *, ignore_reference_emphasis=False):
    start, end = body_span(html, language)
    body = html[start:end]
    if ignore_reference_emphasis:
        # Book titles in the separate English reference edition are italic.
        # Keep its text in the export; this never writes the reference HTML.
        require(body.count('<em>') == body.count('</em>') > 0,
                'expected paired inline emphasis in the reference body')
        body = body.replace('<em>', '').replace('</em>', '')
    return tokenize(body)


def extract(series=POWER):
    articles = []
    for slug in series.slugs:
        p = series.pages / (slug+'.html')
        html = read(p)
        out = {'slug': slug, 'body': original_blocks(html, 'zh'),
               'body_en': original_blocks(html, 'en', ignore_reference_emphasis=slug in series.reference_emphasis),
               'source_sha256': digest(p), 'editions': {}}
        for lang in LOCALES:
            old = read(series.pages / lang / p.name)
            body_span(old)
            out['editions'][lang] = {**metadata(old)}
        articles.append(out)
    return {'source': f'essays/{series.slug}', 'articles': articles}


def validate(locale, payload, source):
    require(isinstance(payload, dict) and isinstance(payload.get('articles'), list),
            f'{locale}: expected articles array')
    articles = payload['articles']
    require([a.get('slug') for a in articles] == [a['slug'] for a in source['articles']], f'{locale}: wrong articles/slugs/order')
    for essay, origin in zip(articles, source['articles']):
        slug = essay['slug']
        prefix = f'{locale}/{slug}'
        for key, value in origin['editions'][locale].items():
            require(essay.get(key) == value, f'{prefix}: preserve existing {key}')
        body = essay.get('body')
        require(isinstance(body, list) and len(body) == len(origin['body']),
                f'{prefix}: exact prose block count required ({len(origin["body"])})')
        for at, (block, base) in enumerate(zip(body, origin['body']), 1):
            label = f'{prefix} block {at}'
            require(isinstance(block, dict) and block.get('tag') == base['tag'] and
                    not set(block) - {'tag', 'text', 'strong'}, f'{label}: wrong tag or field')
            text = block.get('text')
            require(isinstance(text, str) and text == text.strip() and text and '\n' not in text,
                    f'{label}: one nonempty trimmed plain-text block required')
            lead = block.get('strong')
            require(('strong' in base) == ('strong' in block) and
                    ('strong' not in block or (isinstance(lead, str) and lead and text.startswith(lead)
                                               and text != lead)), f'{label}: exact bold lead required where present')


def render_body(blocks):
    out = []
    in_section = False
    for block in blocks:
        # The existing locale CSS purposely styles h2; h1 is the title, so
        # every source h3 section becomes an accessible top-level h2 here.
        tag = 'h2' if block['tag'] == 'h3' else block['tag']
        text = block['text']
        lead = block.get('strong')
        if lead:
            text = f'<strong>{escape(lead, quote=False)}</strong>' + escape(text[len(lead):], quote=False)
        else:
            text = escape(text, quote=False)
        if tag in HEADINGS:
            if in_section:
                out.append('</section>')
            out.append('<section>')
            in_section = True
        out.append(f'<{tag}>{text}</{tag}>')
    if in_section:
        out.append('</section>')
    return '\n' + '\n'.join(out) + '\n'


def body_update(original, blocks):
    start, end = body_span(original)
    return original[:start] + render_body(blocks) + original[end:]


def load_editions(directory, source, *, scratch_names, series=POWER):
    payloads = {}
    for lang in LOCALES:
        path = directory / (f'nd_{series.scratch_slug}_{lang}.json' if scratch_names else f'{lang}.json')
        payload = json.loads(read(path))
        validate(lang, payload, source)
        source_hashes = {a['slug']: sha256(pretty([a['body'], a['body_en']]).encode()).hexdigest()
                         for a in source['articles']}
        if not scratch_names or 'source_body_sha256' in payload:
            require(payload.get('source_body_sha256') == source_hashes,
                    f'{lang}: published primary prose has since changed')
        # Avoid committing local review receipts, scratch paths or tool metadata.
        payloads[lang] = {'source_body_sha256': source_hashes, 'articles': [{field: row[field] for field in ('slug','title','deck','body')}
                                      for row in payload['articles']]}
    return payloads


def outputs(payloads, series=POWER):
    out = {}
    for lang, payload in payloads.items():
        search = ROOT / 'data' / 'search' / f'{lang}.json'
        chunk = json.loads(read(search))
        for article in payload['articles']:
            path = series.pages / lang / (article['slug']+'.html')
            old = read(path)
            new = body_update(old, article['body'])
            require(tokenize(new[slice(*body_span(new))], source=False,
                             source_heading=series.source_heading) == article['body'],
                    f'{path}: rendered prose differs from input')
            out[path] = new
            url = path.relative_to(ROOT).as_posix()
            targets = [r for r in chunk['records'] if r['u'] == url]
            require(len(targets) == 1, f'{path}: existing search identity must remain unique')
            targets[0]['q'] = extract_search_text(new)
        out[search] = serialized(chunk)
    return out


def main(series=POWER):
    parser = argparse.ArgumentParser(description=f'{series.label}: export or update five unabridged translations.')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--extract', type=Path, metavar='FILE')
    mode.add_argument('--check-inputs', action='store_true')
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--import-dir', type=Path, default=series.scratch)
    args = parser.parse_args()
    try:
        source = extract(series)
        if args.extract:
            write(args.extract, pretty(source))
            counts = ', '.join(str(len(a['body'])) for a in source['articles'])
            print(f'Exported all {series.count} ZH and EN {series.label} essays; ZH blocks: {counts}')
            return
        imports = args.check_inputs or args.apply
        payloads = load_editions(args.import_dir if imports else series.changes, source,
                                 scratch_names=imports, series=series)
        expected = outputs(payloads, series)
        if args.check_inputs:
            print(f'Checked all five {series.label} locales, body/heading/strong coverage and search identities; no writes')
            return
        if args.apply:
            expected.update({series.changes/f'{lang}.json': pretty(doc) for lang, doc in payloads.items()})
            for path, content in expected.items():
                if not path.exists() or read(path) != content:
                    write(path, content)
            print(f'Refreshed {series.count * len(LOCALES)} {series.label} bodies and heading queries; all existing page shells retained')
        else:
            changed = [p.relative_to(ROOT).as_posix() for p, expected_text in expected.items()
                       if read(p) != expected_text]
            require(not changed, f'refresh required: {", ".join(changed)}')
            print(f'Checked reproducibility of {len(expected)} {series.label} outputs')
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as err:
        parser.exit(1, f'{series.label} revision: {err}\n')


if __name__ == '__main__':
    main()

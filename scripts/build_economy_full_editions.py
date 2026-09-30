#!/usr/bin/env python3
"""Import reviewed economy manuscripts and render the five full editions.

No translation or source rewriting happens during builds. Import is explicit,
one-time, and records archive hashes, the protected Chinese/English baseline,
and exact editorial changes. Normal builds need only the checked-in sources.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

import markdown
from build_emperor_full_editions import replace_div

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / 'essays/economy'
DATA = ROOT / 'data/economy-full'
RECEIPT = DATA / 'review.json'
LANGS = ('de', 'fr', 'es', 'ja', 'ko')
EPISODES = tuple(f'ep{i:02}' for i in range(1, 24))
REFRAINS = {
    'de': 'Die Rechnung geht noch immer nicht auf. Und das Buch wird weitergeführt.',
    'fr': 'Le compte ne tombe toujours pas juste. Et l’on continue d’écrire.',
    'es': 'Las cuentas siguen sin cuadrar. Y se siguen llevando.',
    'ja': '勘定はいまだ合わず、記帳はいまも続いている。',
    'ko': '셈은 아직 맞지 않는다. 장부는 지금도 쓰이고 있다.',
}
ENDING_PATTERNS = {
    'de': r'Die Rechnung geht noch immer nicht auf\. (?:Die Einträge gehen weiter|Und das Buch wird weitergeführt|Und noch immer wird weitergeschrieben)\.$',
    'fr': r'(?:Le compte ne tombe toujours pas juste\. Et l’on continue (?:de le tenir|d’écrire)|Le compte n’est toujours pas équilibré\. Le grand livre continue de se remplir|Les comptes ne sont pas encore équilibrés\. On continue de tenir le grand livre)\.$',
    'es': r'(?:Las cuentas aún no cuadran\. Se siguen llevando|Las cuentas siguen sin cuadrar\. Y se siguen (?:escribiendo|llevando))\.$',
    'ja': r'(?:勘定はいまだ合わず、記帳はいまも続いている。|帳尻は、?まだ合っていない。それでも、(?:帳簿は記され続ける|記帳は続いている)。)$',
    'ko': r'(?:셈은 아직 맞지 않는다\. 장부는 지금도 쓰이고 있다|장부의 셈은 아직 맞지 않는다\. 그래도 장부는 계속 적힌다)\.$',
}
# Deliberate local copyedits, not a blanket comma-removal transformation.
JA_EDITS = {
    'ep01': [('しかし、圧縮のたびに、どうしても平らにならない部分が残る。', 'しかし圧縮のたびに、どうしても平らにならない部分が残る。')],
    'ep02': [('それは、一件の勘定だった。', 'それは一件の勘定だった。')],
    'ep03': [('リュディアへ戻ると、三つの説明は、どれも根拠を見つけることができる。そして、どれもすぐに、難題にぶつかる。', 'リュディアへ戻ると、三つの説明にはどれも根拠が見つかる。そして、どれもすぐに難題にぶつかる。')],
    'ep04': [('この秩序を支える、もう一本の柱がギルド、同業者の組合だった。', 'この秩序を支えるもう一本の柱が、同業者の組合であるギルドだった。'), ('銀行や信用の仕組み、大企業が、まだ十分に育っていない時代には、ギルドが、商業と手工業を支える制度の、ほぼ中心を占めていた。', '銀行や信用の仕組み、大企業がまだ十分に育っていない時代には、ギルドが商業と手工業を支える制度のほぼ中心を占めていた。')],
    'ep06': [('紹興六年には、行在、すなわち臨時の都に、一時、交子務が設けられた。', '紹興六年には、行在、すなわち臨時の都に一時、交子務が設けられた。')],
    'ep07': [('土地、圧搾設備、銅釜、家畜、住居、そして、その五十人が、一つの投資勘定へ一緒に入れられている。', '土地、圧搾設備、銅釜、家畜、住居、そしてその五十人が、一つの投資勘定へ一緒に入れられている。')],
    'ep08': [('出身地、そして、この先どれほど働けるかという見込みだ。', '出身地、そしてこの先どれほど働けるかという見込みだ。')],
    'ep09': [('味わってみるべき点である。', 'ここは、よく考えてみたい。')],
    'ep13': [('この言葉は、一字も効率を論じていない。', 'この言葉は一字も効率を論じていない。'), ('そして、扉の外へ閉め出された、あの感じである。', 'そして扉の外へ閉め出された、あの感じである。')],
    'ep14': [('ただ、ある研究は、問いをもう一歩、政治の側へ進めた。その結論は、ゆっくり読む価値がある。', 'ただ、ある研究は問いをもう一歩、政治の側へ進めた。その結論はゆっくり読む価値がある。')],
    'ep15': [('つまり、最も中心にある指標でさえ、その外側には、数えられていない余項が、ぐるりと一周、取り巻いている。', 'つまり、最も中心にある指標でさえ、その外側を数えられていない余項がぐるりと取り巻いている。')],
    'ep16': [('ある研究グループは、生産、供出、人口を推計し直し、二つのことを見いだした。', 'ある研究グループは生産、供出、人口を推計し直し、二つのことを見いだした。')],
    'ep17': [('より正確に言えば、貨幣は、公然と、いっそう深く、信用の上に据えられたのである。', 'より正確に言えば、貨幣は公然と、いっそう深く信用の上に据えられたのである。')],
    'ep18': [('規模は、小さくない。', '規模は小さくない。'), ('主要な取引相手も規制当局も、事前には、その実際の規模を知らなかった。', '主要な取引相手も規制当局も、事前にはその実際の規模を知らなかった。')],
    'ep19': [('後に、ある研究者は、この破綻を、冷ややかなほど簡潔にまとめた。', '後にある研究者は、この破綻を冷ややかなほど簡潔にまとめた。')],
    'ep20': [('それらが、一緒に結びつけられた。', 'それらが一緒に結びつけられた。')],
    'ep23': [('従来の信用供与における、金利、レバレッジ、証拠金という核心へ、近づいている。', '従来の信用供与における金利、レバレッジ、証拠金という核心へ近づいている。')],
}
TOC_LABELS = {'de': 'In diesem Essay', 'fr': 'Dans cet essai', 'es': 'En este ensayo', 'ja': 'この篇の目次', 'ko': '이 글의 목차'}
STYLE = '''<style id="economy-full-style">
.economy-full p{overflow-wrap:anywhere}
.economy-full h2{line-height:1.55;scroll-margin-top:90px}
.economy-toc{margin:1.5rem auto;max-width:var(--max-w);padding:1rem 1.5rem;border:1px solid var(--cream-border)}
.economy-toc summary{cursor:pointer;font-family:var(--sans);color:var(--ink-muted)}
.economy-toc ul{margin:1rem 0 0;padding-left:1.4rem}
.economy-toc li{margin:.5rem 0;line-height:1.6;overflow-wrap:anywhere}
.economy-toc a{color:var(--ink-light)}
.essay-header h1,.series-nav .nav-title{overflow-wrap:anywhere}
</style>'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sections(text):
    return [s.strip() for s in re.split(r'^## .*$', text, flags=re.M)[1:]]


def paragraph_counts(text):
    return [len(re.findall(r'<p>', markdown.markdown(s))) for s in sections(text)]


def import_archives(folder):
    if RECEIPT.exists():
        raise ValueError('Review already recorded; do not silently overwrite reviewed manuscripts')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    protected = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in SERIES.rglob('*')
                 if p.is_file() and p.relative_to(SERIES).parts[0] not in LANGS}
    receipt = dict(version=1, edition='2026-09-30-full', baseline_commit=commit,
                   protected_files=protected, archives={}, manuscripts={}, notes=[
        'Five supplied complete editions; Chinese and English source pages are protected byte-for-byte.',
        'All eight sections and every body paragraph retained. Prefatory credits live in the page shell rather than the body.',
        'Series ending standardized per language. Selected Japanese punctuation and phrasing lightly polished; no argument rewritten.',
        'Supplied EP17 translations say the war was still in progress, unlike the Chinese sentence saying it had just ended. Correct for July 1944; retained as a disclosed source discrepancy, not silently changed in Chinese/English.',
        'EP17 verification: https://www.imf.org/external/np/exr/center/mm/eng/mm_cc_04.htm',
        'Supplied EP01 German next-essay link removed from prose; existing language-local navigation retained.',
        'Structural checks are exhaustive; editorial review used cross-language samples and targeted local copyediting, not a claim of line-by-line factual certification of all 115 texts.',
    ])
    outputs = {}
    for ep in EPISODES:
        archive = folder / f'NonDubito_Economy_{ep.upper()}_DE_FR_ES_JA_KO_v1.0.zip'
        receipt['archives'][ep] = dict(name=archive.name, sha256=digest(archive.read_bytes()))
        zh = (SERIES/f'{ep}.html').read_text().split('<div class="essay-body lang-zh"', 1)[1].split('<div class="essay-body lang-en"', 1)[0]
        expected = [len(re.findall(r'<p[ >]', s)) for s in re.split(r'<h3[^>]*>.*?</h3>', zh, flags=re.S)[1:]]
        with ZipFile(archive) as z:
            assert z.testzip() is None and len(z.namelist()) == 5, archive.name
            for lang in LANGS:
                names = [n for n in z.namelist() if n.endswith(f'_{lang}.md')]
                assert len(names) == 1
                original = z.read(names[0]).decode('utf-8')
                title = original.splitlines()[0].removeprefix('# ').strip()
                assert original.startswith('# ')
                body = original[original.index('\n## '):].strip()
                body = re.sub(r'\n\[Nächster Essay:.*?\]\([^\n]+\)\s*$', '', body).strip()
                edits = []
                match = re.search(ENDING_PATTERNS[lang], body)
                assert match, (ep, lang, 'unknown refrain')
                if match[0] != REFRAINS[lang]:
                    edits.append(dict(reason='series-refrain', before=match[0], after=REFRAINS[lang]))
                    body = body[:match.start()] + REFRAINS[lang]
                for before, after in JA_EDITS.get(ep, []) if lang == 'ja' else []:
                    assert body.count(before) == 1, (ep, before)
                    body = body.replace(before, after, 1)
                    edits.append(dict(reason='Japanese-copyedit', before=before, after=after))
                text = f'# {title}\n\n{body}\n'
                assert len(sections(text)) == 8 and paragraph_counts(text) == expected, (ep, lang)
                old = (SERIES/lang/f'{ep}.html').read_text()
                previous = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', old, re.S)[1])
                key = f'{ep}.{lang}'
                receipt['manuscripts'][key] = dict(title=title, previous_title=previous,
                    received_sha256=digest(original.encode()), published_sha256=digest(text.encode()),
                    sections=8, paragraphs_by_section=expected, edits=edits,
                    removed_preface=original[:original.index('\n## ')].strip(),
                    removed_navigation=(ep == 'ep01' and lang == 'de'))
                outputs[DATA/f'{key}.md'] = text
    # Validate the entire import before writing any sources.
    DATA.mkdir(parents=True, exist_ok=True)
    for path, text in outputs.items():
        path.write_text(text)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print('Imported 115 complete manuscripts and frozen source/edit receipt')


def manuscripts():
    receipt = json.loads(RECEIPT.read_text())
    records = receipt['manuscripts']
    assert set(records) == {f'{ep}.{lang}' for ep in EPISODES for lang in LANGS}
    out = {}
    for key, record in records.items():
        raw = (DATA/f'{key}.md').read_bytes()
        assert digest(raw) == record['published_sha256'], (key, 'unreviewed change')
        text = raw.decode()
        assert text.startswith('# ' + record['title'] + '\n')
        assert paragraph_counts(text) == record['paragraphs_by_section'], key
        headings = re.findall(r'^## (.+)$', text, re.M)
        assert len(headings) == 8
        rendered = markdown.markdown(text.split('\n', 1)[1].strip())
        counter = iter(range(1, 9))
        rendered = re.sub(r'<h2>', lambda _: f'<h2 id="section-{next(counter)}">', rendered)
        out[key] = dict(record, body=rendered, headings=headings)
    return out


def update_anchor_titles(text, copies):
    def replace_anchor(m):
        ep = re.search(r'href="(ep\d{2})\.html"', m[0])
        if not ep or ep[1] not in copies:
            return m[0]
        return re.sub(r'(<(?:span|div) class="(?:nav-title|entry-title)">).*?(</(?:span|div)>)',
                      lambda n: n[1] + html.escape(copies[ep[1]]['title']) + n[2], m[0], flags=re.S)
    return re.sub(r'<a\b[^>]*>.*?</a>', replace_anchor, text, flags=re.S)


def outputs():
    copies = manuscripts()
    out = {}
    for lang in LANGS:
        local = {ep: copies[f'{ep}.{lang}'] for ep in EPISODES}
        index = SERIES/lang/'index.html'
        out[index] = update_anchor_titles(index.read_text(), local)
        for ep in EPISODES:
            copy = local[ep]
            path = SERIES/lang/f'{ep}.html'
            text = path.read_text()
            text = replace_div(text, 'essay-body', '<div class="economy-full">\n'+copy['body']+'\n</div>')
            text = re.sub(r'(<h1\b[^>]*>).*?(</h1>)', lambda m: m[1]+html.escape(copy['title'])+m[2], text, count=1, flags=re.S)
            text = re.sub(r'<title>.*?</title>', lambda _: '<title>'+html.escape(copy['title'])+' — Non Dubito</title>', text, flags=re.S)
            text = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda m: m[1]+html.escape(copy['title']+' — Non Dubito', quote=True)+m[2], text)
            # Existing editorial decks still describe the same essays; preserve them.
            text = re.sub(r'<details class="economy-toc">.*?</details>\s*', '', text, flags=re.S)
            toc = '<details class="economy-toc"><summary>'+TOC_LABELS[lang]+'</summary><ul>'
            toc += ''.join(f'<li><a href="#section-{i}">{html.escape(h)}</a></li>' for i, h in enumerate(copy['headings'], 1))
            toc += '</ul></details>\n'
            text = text.replace('<div class="essay-body">', toc+'<div class="essay-body">', 1)
            text = re.sub(r'<style id="economy-full-style">.*?</style>\s*', '', text, flags=re.S)
            text = text.replace('</head>', STYLE+'\n</head>', 1)
            out[path] = update_anchor_titles(text, local)
    return out


def refresh_indexes():
    """Refresh only our existing records, leaving concurrent editorial work out.

    No URL or language is added by this upgrade, so manifest counts stay fixed.
    A normal whole-site rebuild produces the same economy records afterward.
    """
    import build_search_index as search
    _, chunks = search.build()
    scope = {p.relative_to(ROOT).as_posix() for p in outputs()}
    for lang in LANGS:
        path = ROOT/f'data/search/{lang}.json'
        current = json.loads(path.read_text())
        fresh = {r['u']: r for r in chunks[lang] if r['u'] in scope}
        assert len(fresh) == 24, lang
        assert fresh.keys() <= {r['u'] for r in current['records']}, 'New URL requires a full manifest rebuild'
        current['records'] = [fresh.get(r['u'], r) for r in current['records']]
        path.write_text(search.serialized(current))
    path = ROOT/'sitemap.xml'
    text = path.read_text()
    for rel in scope:
        canonical_path = rel.removesuffix('index.html') if rel.endswith('/index.html') else rel
        pattern = r'(<loc>https://nondubito.net/'+re.escape(canonical_path)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)'
        text, count = re.subn(pattern, lambda m: m[1]+date.today().isoformat()+m[2], text)
        assert count == 1, rel
    path.write_text(text)
    print('Updated only economy records in five search chunks and sitemap')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-archives', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--refresh-indexes', action='store_true')
    args = parser.parse_args()
    if args.check and args.refresh_indexes:
        parser.error('--check cannot refresh indexes')
    if args.import_archives:
        if args.check:
            parser.error('--check cannot import manuscripts')
        import_archives(args.import_archives)
    generated = outputs()
    pending = {p: s for p, s in generated.items() if p.read_text() != s}
    if args.check:
        if pending:
            raise SystemExit('Stale economy pages: '+', '.join(str(p.relative_to(ROOT)) for p in pending))
        print('OK: 115 full article pages and five indexes match reviewed manuscripts')
    else:
        for path, text in pending.items():
            path.write_text(text)
        print(f'Updated {len(pending)} economy pages')
        if args.refresh_indexes:
            refresh_indexes()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Import reviewed translations and rebuild only the School routes.

Translations are editorial inputs, never automatically generated here.
Input: DIR/nd_school_<lang>.json. References are a JSON mapping from
language to episode to localized labels in the source order. Validate without
writing with --import-dir DIR --references FILE --check-inputs; omit
--check-inputs to import/build. Subsequently run normally or --check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import build_reader_series as primary
import connect_full_series_languages as connection
import full_series_languages as languages
import refresh_reader_discovery as discovery
from prepare_action_sources import Document

ROOT = languages.ROOT
KEY = 'school'
DIRECTORY = 'essays/' + KEY
BASE = ROOT / 'data' / KEY / 'multilingual'
SLUGS = [f'ep{i:02d}' for i in range(1, 10)]
LOCALES = ['ja', 'fr', 'de', 'es', 'ko']
EXISTING_ID = f'2026-11-20-{KEY}-reader-series'
ORIGINAL_DATE = '2026-11-20'
LOCAL_COPY = {
    'ja': (
        ('ホーム', '全九篇', '書架', 'メニュー', '検索', '全文を読む', '前の篇', '次の篇',
         '原論文と読解の手引き', 'SAE 理論', 'さらに読む', 'SAE 読書マップ', '原論文'),
        '時間割はよくできている。それでも、わからないことがあるとき、誰に聞けるのか知らない子がいる。学校には何がまだ足りないのだろう。',
        '幼稚園から高校まで。どの子も受けとめながら、その子がどんな人になるかまで決めない学校について考える。',
        '『学校論』の前置きと八篇の論文をもとにした読者向けの散文。個々の指導の判断や大学の制度とは分けて、幼稚園、小学校、中学校・高校の公的な役割を扱う。出典のない場面は架空で、実際の制度はその文書の日付と適用範囲に沿って読む。書かれた取り決めだけで、実施されたことまではわからない。子どもの安全を守ること、教えること、成長の余地を残すことはそれぞれ異なる。子どもの基本的な立場は、成績や成熟によって得られるものではない。学校、教師、家庭、公的な提供の責任は、それぞれに残る。発達のモデルを実証済みの年齢表としては扱わず、個別の法的・医療的・保護上の助言を提供するものでもない。'),
    'fr': (
        ('Accueil', 'Les neuf essais', 'Bibliothèque', 'Menu', 'Rechercher', 'Lire l’essai',
         'Essai précédent', 'Essai suivant', 'Sources et note de lecture', 'Théorie SAE', 'À lire aussi',
         'Parcours de lecture SAE', 'Article d’origine'),
        'L’emploi du temps est plein et soigneusement préparé. Pourtant, un enfant ne sait toujours pas à qui poser une question difficile. Que manque-t-il ?',
        'De la maternelle à la fin du secondaire, comment l’école peut-elle accueillir chaque enfant sans décider de la personne qu’il doit devenir ?',
        'Ces neuf essais s’appuient sur le texte liminaire et les huit articles sur l’école. Ils abordent les responsabilités publiques de la maternelle, du primaire et du secondaire, sans les confondre avec le jugement d’un enseignant dans une situation particulière ni avec le fonctionnement de l’université. Les scènes non sourcées sont imaginées. Les règles citées sont lues à la date et dans le champ indiqués ; leur existence ne prouve pas leur mise en œuvre. Protéger, enseigner et laisser de la place pour grandir sont trois tâches distinctes. Le statut fondamental de l’enfant ne dépend ni de ses résultats ni de sa maturité. L’école, l’enseignant, la famille et les services publics restent chacun comptables de leur propre rôle. Les modèles de développement ne donnent pas un calendrier d’âges établi. Le texte ne fournit pas de conseils juridiques, médicaux ou de protection pour un cas particulier.'),
    'de': (
        ('Startseite', 'Alle neun Essays', 'Bibliothek', 'Menü', 'Suche', 'Essay lesen', 'Vorheriger Essay',
         'Nächster Essay', 'Quellen und Lesehinweis', 'SAE-Theorie', 'Weiterlesen', 'SAE-Lesekarte',
         'Zugehörige wissenschaftliche Arbeit'),
        'Der Stundenplan ist voll und sorgfältig gemacht. Ein Kind weiß trotzdem nicht, an wen es sich mit einer schwierigen Frage wenden kann. Was fehlt?',
        'Vom Kindergarten bis zum Ende der Schulzeit: Wie kann eine Schule jedes Kind erreichen, ohne festzulegen, wer es werden soll?',
        'Die neun Essays gehen auf die Vorbemerkung und acht Arbeiten zur Schule zurück. Sie fragen nach den öffentlichen Aufgaben in Kindergarten, Grundschule und weiterführender Schule, nicht nach der Entscheidung in einer konkreten Unterrichtssituation oder nach der Ordnung von Hochschulen. Szenen ohne Quellenangabe sind erfunden. Regelungen werden mit dem jeweiligen Datum und Geltungsbereich angeführt; ein Text belegt noch keine Umsetzung. Schutz, Unterricht und Spielraum für Entwicklung sind eigene Aufgaben. Die grundlegende Stellung des Kindes setzt weder Leistung noch Reife voraus. Schule, Lehrkräfte, Familie und öffentliche Stellen bleiben jeweils für ihre eigenen Aufgaben verantwortlich. Entwicklungsmodelle sind keine empirisch gesicherten Altersfahrpläne. Die Texte geben keine rechtlichen, medizinischen oder schutzbezogenen Anweisungen für Einzelfälle.'),
    'es': (
        ('Inicio', 'Los nueve ensayos', 'Biblioteca', 'Menú', 'Buscar', 'Leer el ensayo', 'Ensayo anterior',
         'Ensayo siguiente', 'Fuentes y nota de lectura', 'Teoría SAE', 'Seguir leyendo', 'Mapa de lectura SAE',
         'Artículo original'),
        'El horario está lleno y muy bien pensado. Aun así, un niño no sabe a quién acudir con una pregunta difícil. ¿Qué falta?',
        'Desde la educación infantil hasta el final de la secundaria: ¿cómo puede la escuela atender a cada niño sin decidir quién debe llegar a ser?',
        'Estos nueve ensayos parten del texto introductorio y ocho artículos sobre la escuela. Se ocupan de las responsabilidades públicas de la educación infantil, primaria y secundaria, sin confundirlas con el juicio particular de quien enseña ni con la organización universitaria. Las escenas sin fuente son imaginadas. Las reglas citadas conservan su fecha y su ámbito; estar escritas no prueba que se apliquen. Proteger, enseñar y dejar espacio para crecer son tareas distintas. La condición básica del niño no depende de sus notas ni de su madurez. La escuela, el profesorado, las familias y los servicios públicos responden cada cual por su propia tarea. Los modelos de desarrollo no son calendarios de edades acreditados. No se ofrecen orientaciones jurídicas, médicas ni de protección para casos particulares.'),
    'ko': (
        ('홈', '아홉 편 전체', '서가', '메뉴', '검색', '본문 읽기', '이전 글', '다음 글', '원논문과 읽기 안내',
         'SAE 이론', '함께 읽기', 'SAE 읽기 지도', '원논문'),
        '시간표는 빈틈없이 잘 짜여 있다. 그런데도 아이는 어려운 질문이 생기면 누구를 찾아갈지 모른다. 무엇이 빠져 있는 걸까?',
        '유치원부터 중등학교까지, 학교는 아이가 어떤 사람이 되어야 할지 대신 정하지 않으면서도 모든 아이를 어떻게 맞아들일 수 있을까?',
        '아홉 편은 학교에 관한 머리글과 여덟 편의 논문을 바탕으로 한다. 유치원과 초·중등학교의 공적 책임을 다루되 교사의 개별 판단이나 대학의 제도와 뒤섞지 않는다. 출처를 밝히지 않은 장면은 지어낸 것이다. 실제 규정은 문서의 날짜와 적용 범위에 맞춰 읽으며, 규정이 적혀 있다는 사실만으로 시행되었다고 보지 않는다. 보호하기, 가르치기, 성장할 여지를 남겨 두기는 서로 다른 일이다. 아이의 기본적 지위는 성적이나 성숙을 조건으로 하지 않는다. 학교와 교사, 가정과 공공 서비스는 각자의 책임을 진다. 발달 모형을 입증된 연령표로 보지 않으며, 개별 사안에 대한 법률·의료·보호 지침도 제시하지 않는다.'),
}
UI_KEYS = ('home', 'contents', 'library', 'menu', 'search', 'read', 'previous', 'next',
           'sources', 'theory', 'related', 'map', 'paper')


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def read(path):
    return json.loads(path.read_text())


def output(path, text, check):
    if check:
        assert path.read_text() == text, f'Stale or missing: {path}'
    elif not path.is_file() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def valid(value):
    return isinstance(value, str) and bool(value.strip()) and not re.search(r'<|\ufffd|\b(?:TODO|FIXME)\b', value)


def import_data(directory, ref_path, check_inputs=False):
    ref_labels = read(ref_path) if ref_path else {}
    original = {slug: read(BASE.parent / f'{slug}.json') for slug in SLUGS}
    spec = {
        'id': KEY, 'directory': DIRECTORY, 'date': ORIGINAL_DATE,
        'source': original['ep01']['source_url'], 'source_format': 'modern-html',
        'slugs': SLUGS, 'languages': LOCALES, 'reading_css_version': '20261103',
        'primary_editions': {'en': '', 'zh': '', 'zh-hant': ''},
        'related_series': ['teacher-student', 'university', 'parent-child', 'cultivation'],
        'preserve_reader_references': True,
    }
    pending = {BASE / 'profile.json': dump(spec)}
    for lang in LOCALES:
        data = read(directory / f'nd_school_{lang}.json')
        ui, intro, scope, note = LOCAL_COPY[lang]
        assert valid(data['title']) and valid(data['deck']), lang
        assert [a['slug'] for a in data['articles']] == SLUGS, lang
        articles = []
        for article in data['articles']:
            slug = article['slug']
            item = original[slug]
            for key in ('title', 'deck'):
                assert valid(article[key]), (lang, slug, key)
            body = article['body']
            assert len(body) == len(item['body_zh']), (lang, slug, 'paragraph coverage')
            for i, (p, q) in enumerate(zip(item['body_zh'], body), 1):
                assert valid(q) and languages.block_kind(p) == languages.block_kind(q), (lang, slug, i)
            assert len(set(body)) == len(body), (lang, slug, 'repeated paragraphs')
            labels = article.get('reference_labels', ref_labels.get(lang, {}).get(slug))
            labels = [] if labels is None and not item['references'] else labels
            assert isinstance(labels, list) and len(labels) == len(item['references']) and all(map(valid, labels)), (
                lang, slug, 'localized reference labels required in original link order')
            # Paragraph locators let an editor navigate the aligned source; they
            # are not proof of semantic review.
            articles.append({
                'slug': slug, 'title': article['title'], 'deck': article['deck'], 'body': body,
                'references': [{'url': r['url'], 'title': label} for r, label in zip(item['references'], labels)],
                'coverage': [f'{slug} · {i:02d}' for i in range(1, len(body)+1)],
                'source_sha256': hashlib.sha256((BASE.parent / f'{slug}.json').read_bytes()).hexdigest(),
            })
        packed = {
            'language': lang, 'ui': dict(zip(UI_KEYS, ui), series=data['title']),
            'series': {'title': data['title'], 'deck': data['deck'], 'intro': intro, 'scope': scope, 'source_note': note},
            'articles': articles, 'review': {'unresolved': []},
        }
        pending[BASE / f'{lang}.json'] = dump(packed)
    if not check_inputs:
        for path, text in pending.items():
            output(path, text, False)
    print(('Validated' if check_inputs else 'Imported') +
          f' {len(LOCALES)*len(SLUGS)} essays with aligned source blocks and localized reference labels.')
    return pending


def protected(source, selector, tag=None):
    doc = Document(source)
    return [doc.raw(n) for n in doc.root.walk() if n.has(selector) and (tag is None or n.tag == tag)]


def primary_outputs(check):
    pages = primary.render(KEY)
    for path, text in pages.items():
        before = path.read_text()
        # Existing three text bodies, source blocks, and neighbor navigation must
        # remain byte-for-byte. Only series availability and language chrome change.
        for css in ('essay-body', 'lw-sources', 'lw-series-nav', 'lw-head', 'lw-grid', 'lw-opening', 'lw-related'):
            assert protected(before, css) == protected(text, css), (path, css, 'published text changed')
        output(path, text, check)


def foreign_outputs(check):
    for lang in LOCALES:
        _, data = languages.load_language(KEY, lang)
        for row in data['articles']:
            src = BASE.parent / (row['slug'] + '.json')
            assert row['source_sha256'] == hashlib.sha256(src.read_bytes()).hexdigest(), (lang, src, 'source drift')
    pages = languages.render(KEY)
    assert len(pages) == len(LOCALES)*(1+len(SLUGS))
    for path, text in pages.items():
        output(path, text, check)


def discover_outputs(check):
    ledger_path = ROOT / 'data/site-updates.json'
    ledger = read(ledger_path)
    rows = [entry for entry in ledger['updates'] if entry['id'] == EXISTING_ID]
    assert len(rows) == 1, EXISTING_ID
    entry = rows[0]
    entry['languages'] = ['en', 'zh', 'zh-hant', *LOCALES]
    output(ledger_path, dump(ledger), check)
    # Refresh the bounded Home area, channel cards and Library badge with the
    # standard connector, without inserting its separate Latest announcement.
    entry_for_catalog = dict(entry, library_count={
        'en': '9 essays · 8 languages', 'zh': '9 篇 · 八语', 'zh-hant': '9 篇 · 八語',
    })
    output(BASE / 'discovery.json', dump(entry_for_catalog), check)
    public_cards = connection.render(KEY)
    for path in [ROOT/'index.html', ROOT/'library.html', *(ROOT/f'essays/{lang}/index.html' for lang in LOCALES)]:
        output(path, public_cards[path], check)
    latest = ROOT/'latest.html'
    source = latest.read_text()
    marker = f'READER SERIES {KEY.upper()} LATEST'
    expr = re.compile(fr'<!-- {marker} START -->.*?<!-- {marker} END -->', re.S)
    def badge(match):
        block = match[0]
        updated = block.replace('<span>EN / 简 / 繁</span>', '<span>EN · 简 · 繁 · 日本語 · Français · Deutsch · Español · 한국어</span>')
        assert updated.count('EN · 简 · 繁 · 日本語 · Français · Deutsch · Español · 한국어') == 1
        return updated
    result, n = expr.subn(badge, source)
    assert n == 1
    output(latest, result, check)
    for path, text in discovery.render(KEY).items():
        output(path, text, check)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--import-dir', type=Path)
    p.add_argument('--references', type=Path)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--check-inputs', action='store_true')
    args = p.parse_args()
    if args.check_inputs and not args.import_dir:
        p.error('--check-inputs requires --import-dir')
    if args.references and not args.import_dir:
        p.error('--references requires --import-dir')
    if args.import_dir and args.check:
        p.error('use --check-inputs to validate unpublished editorial inputs')
    if args.import_dir:
        import_data(args.import_dir, args.references, check_inputs=args.check_inputs)
    if args.check_inputs:
        return
    primary_outputs(args.check)
    foreign_outputs(args.check)
    discover_outputs(args.check)
    print(('Checked' if args.check else 'Built') + ' 10 primary pages, 50 new-language pages, and scoped discovery.')


if __name__ == '__main__':
    main()

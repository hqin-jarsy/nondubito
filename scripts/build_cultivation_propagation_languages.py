#!/usr/bin/env python3
"""Import reviewed translations and rebuild only the What We Pass On routes.

Translations are editorial inputs, never automatically generated here.
Run --import-dir DIR --references FILE once, then run normally or --check.
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
KEY = 'cultivation-propagation'
DIRECTORY = 'essays/' + KEY
BASE = ROOT / 'data' / KEY / 'multilingual'
SLUGS = [f'ep{i:02d}' for i in range(1, 9)]
LOCALES = ['ja', 'fr', 'de', 'es', 'ko']
EXISTING_ID = f'2026-11-20-{KEY}-reader-series'
ORIGINAL_DATE = '2026-11-20'
LOCAL_COPY = {
    'ja': (
        ('ホーム', '全八篇', '書架', 'メニュー', '検索', '全文を読む', '前の篇', '次の篇',
         '原論文と読解の手引き', 'SAE 理論', 'さらに読む', 'SAE 読書マップ', '原論文'),
        '教える人は、彼女に理由も伝えた。それから何年かたち、彼女も新人を教える。あることでは相手に余地を残し、別の小さなことでは、気づかぬうちにその余地を狭めていた。',
        '大人が人から受け取ったものを、自分で考え、そのあとで別の人とどう向き合うか。八篇の散文で、前後する二つの関わりをたどる。',
        '『涵育的传播』の総覧と七篇の本文をもとにした読者向けの散文。大人の二つの関わりをたどるもので、情報一般の伝わり方を説明したり、制度やプラットフォームの規則を決めたりはしない。出典のない指導、執筆、発信の場面は架空である。書簡や回想から読めるのは、資料に残った個々の行いまでで、本人の内面や人となり全体を決めつけることはできない。助けを受けても、それを次に渡す義務は生じない。反応がなければ分からないままとし、助けは結果を保証しない。善意で時間や損失、傷つけた事実を帳消しにすることも、際限なく力を注ぐよう求めることもできない。人の判断を奪うような関わりをやめるなら、まず自分がどう受け取り、どう人に接するかから始める。誰かに名札を付けるための話ではない。'),
    'fr': (
        ('Accueil', 'Les huit essais', 'Bibliothèque', 'Menu', 'Rechercher', 'Lire l’essai',
         'Essai précédent', 'Essai suivant', 'Sources et repères de lecture', 'Théorie SAE', 'À lire aussi',
         'Parcours de lecture SAE', 'Article d’origine'),
        'La personne qui lui a appris le métier lui a expliqué pourquoi elle faisait ainsi. Des années plus tard, c’est elle qui forme quelqu’un. Ici, elle lui laisse de la latitude ; là, dans un détail, elle resserre presque sans y penser.',
        'Huit essais suivent deux relations qui se succèdent dans la vie d’un adulte : ce qu’il reçoit, ce qu’il en fait et la façon dont il agit ensuite avec quelqu’un d’autre.',
        'Ces essais prennent appui sur la présentation d’ensemble et les sept articles consacrés à la transmission d’une manière d’aider l’autre à grandir. Ils suivent des adultes dans deux relations qui se succèdent, sans proposer de théorie générale de la diffusion ni trancher les questions de règles institutionnelles ou de plateformes. Les scènes d’apprentissage, d’écriture et de publication sans source sont imaginées. Des lettres et des souvenirs, on ne retient que les gestes attestés, sans prétendre connaître le for intérieur de quelqu’un ni porter un jugement sur sa personne. Recevoir de l’aide n’oblige pas à en donner à son tour. Faute de retour, la question reste ouverte. L’aide ne garantit aucun résultat ; la bonne volonté n’efface ni le temps passé, ni les pertes, ni les torts et n’exige pas un engagement sans limites. Pour cesser de prendre la place du jugement d’autrui, on peut d’abord regarder comment on reçoit et comment on traite les autres, sans leur coller d’étiquettes.'),
    'de': (
        ('Startseite', 'Alle acht Essays', 'Bibliothek', 'Menü', 'Suche', 'Essay lesen', 'Vorheriger Essay',
         'Nächster Essay', 'Quellen und Lesehinweis', 'SAE-Theorie', 'Weiterlesen', 'SAE-Lesekarte',
         'Zugehörige wissenschaftliche Arbeit'),
        'Wer sie einarbeitete, erklärte ihr auch die Gründe. Jahre später arbeitet sie selbst jemanden ein. In einer Sache lässt sie ihm Spielraum, in einer kleinen anderen macht sie ihn unmerklich enger.',
        'Acht Essays über zwei Beziehungen im Leben eines erwachsenen Menschen: Was empfängt jemand, was macht er daraus, und wie geht er später mit einem anderen Menschen um?',
        'Diese Essays greifen die Übersicht und sieben Arbeiten darüber auf, wie eine Art der Zuwendung weitergegeben werden kann. Sie verfolgen Erwachsene in zwei aufeinanderfolgenden Beziehungen, ohne eine allgemeine Theorie der Verbreitung von Informationen anzubieten oder institutionelle Regeln und Plattformregeln zu entscheiden. Unbelegte Szenen des Anleitens, Schreibens und Veröffentlichens sind erfunden. Briefe und Erinnerungen belegen bestimmte Handlungen; sie geben keinen Aufschluss über das ganze Innenleben oder die ganze Person. Wer Hilfe erfahren hat, schuldet es niemandem, sie weiterzugeben. Fehlt eine Rückmeldung, bleibt offen, was daraus wurde. Hilfe garantiert kein Ergebnis; gute Absichten machen weder Zeitaufwand noch Verlust oder Schaden ungeschehen und verpflichten nicht zu grenzenlosem Einsatz. Wer anderen ihr Urteil nicht abnehmen will, kann damit anfangen, wie er selbst annimmt und mit ihnen umgeht, statt Personen mit Etiketten zu versehen.'),
    'es': (
        ('Inicio', 'Los ocho ensayos', 'Biblioteca', 'Menú', 'Buscar', 'Leer el ensayo', 'Ensayo anterior',
         'Ensayo siguiente', 'Fuentes y nota de lectura', 'Teoría SAE', 'Seguir leyendo', 'Mapa de lectura SAE',
         'Artículo original'),
        'Quien le enseñó el oficio le explicó también los motivos. Años después, ella enseña a una persona recién llegada. En una cosa le deja margen; en otro detalle, casi sin darse cuenta, se lo estrecha.',
        'Ocho ensayos siguen dos relaciones que se suceden en la vida de una persona adulta: lo que recibe, lo que hace suyo y cómo trata después a alguien más.',
        'Estos ensayos parten del texto de conjunto y los siete artículos sobre cómo se transmite una manera de ayudar a otros a crecer. Siguen a personas adultas en dos relaciones sucesivas, sin proponer una teoría general de la difusión ni resolver cuestiones de normas institucionales o de plataformas. Las escenas de enseñanza, escritura y publicación que no llevan fuente son imaginadas. Las cartas y los recuerdos documentan actos concretos: no permiten dictaminar cómo es alguien por dentro ni juzgarlo en su totalidad. Recibir ayuda no obliga a ayudar a otros a su vez. Si no hay respuesta, queda por saber qué ocurrió. La ayuda no garantiza resultados. La buena intención no borra el tiempo empleado, las pérdidas ni el daño, ni obliga a entregarse sin límite. Para dejar de ocupar el lugar en que otro ha de juzgar, importa empezar por cómo recibimos y cómo tratamos, sin ponerle etiquetas a nadie.'),
    'ko': (
        ('홈', '여덟 편 전체', '서가', '메뉴', '검색', '본문 읽기', '이전 글', '다음 글', '원논문과 읽기 안내',
         'SAE 이론', '함께 읽기', 'SAE 읽기 지도', '원논문'),
        '일을 가르친 선배는 쑤야오에게 이유도 알려 주었다. 몇 해 뒤 쑤야오도 새로 온 사람에게 일을 가르친다. 어느 일에서는 상대에게 여지를 두고, 또 다른 작은 일에서는 자신도 모르게 그 여지를 좁힌다.',
        '한 어른이 무엇을 받아 어떻게 자기 것으로 만들고, 나중에 다른 사람을 어떻게 대하는지. 앞뒤로 이어지는 두 관계를 여덟 편의 산문에서 살펴본다.',
        '이 산문은 좋은 대우가 어떻게 이어지는지 다룬 총론과 일곱 편의 논문을 바탕으로 한다. 어른이 맺는 앞뒤 두 관계를 따라가며, 모든 정보가 퍼지는 방식을 설명하거나 제도와 플랫폼의 규칙을 대신 정하지 않는다. 출처를 밝히지 않은 가르침, 글쓰기, 콘텐츠 발행 장면은 지어낸 것이다. 편지와 회고는 자료가 뒷받침하는 구체적인 행동까지만 읽는다. 보이지 않는 속마음이나 한 사람 전체를 단정하지 않는다. 도움을 받았다고 해서 다음 사람에게 갚아야 할 빚이 생기지는 않는다. 반응이 없으면 무엇이 되었는지 미정으로 남겨 둔다. 도움은 결과를 보장하지 않고, 선의로 시간이나 손실, 상처가 없어지지도 않으며, 끝없이 힘을 쏟을 것을 요구하지도 않는다. 다른 사람의 판단 자리를 차지하지 않으려면 자신이 무엇을 어떻게 받아들이고 남을 어떻게 대할지부터 살필 일이다. 이 말로 남에게 꼬리표를 붙이지 않는다.'),
}
WRITING_LABEL = {'ja': '言葉と書くこと', 'fr': 'Le langage et l’écriture', 'de': 'Sprache und Schreiben',
                 'es': 'Lenguaje y escritura', 'ko': '언어와 글쓰기'}
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


def import_data(directory, ref_path):
    ref_labels = read(ref_path) if ref_path else {}
    original = {slug: read(BASE.parent / f'{slug}.json') for slug in SLUGS}
    spec = {
        'id': KEY, 'directory': DIRECTORY, 'date': ORIGINAL_DATE,
        'source': original['ep01']['source_url'], 'source_format': 'modern-html',
        'slugs': SLUGS, 'languages': LOCALES, 'reading_css_version': '20261103',
        'primary_editions': {'en': '', 'zh': '', 'zh-hant': ''},
        'related_series': ['cultivation', 'positive-sum', 'teacher-student'],
        'reader_routes': [{'path': 'essays/language-writing/{language}/index.html', 'label_key': 'writing'}],
        'preserve_reader_references': True,
    }
    pending = {BASE / 'profile.json': dump(spec)}
    fallback_count = 0
    for lang in LOCALES:
        data = read(directory / f'nd_prop_{lang}.json')
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
            if labels is None:
                labels = [r['en'] for r in item['references']]
                fallback_count += len(labels)
            assert len(labels) == len(item['references']) and all(map(valid, labels)), (lang, slug, 'reference labels')
            # Paragraph locators let an editor navigate the aligned source; they
            # are not proof of semantic review.
            articles.append({
                'slug': slug, 'title': article['title'], 'deck': article['deck'], 'body': body,
                'references': [{'url': r['url'], 'title': label} for r, label in zip(item['references'], labels)],
                'coverage': [f'{slug} · {i:02d}' for i in range(1, len(body)+1)],
                'source_sha256': hashlib.sha256((BASE.parent / f'{slug}.json').read_bytes()).hexdigest(),
            })
        packed = {
            'language': lang, 'ui': dict(zip(UI_KEYS, ui), series=data['title'], writing=WRITING_LABEL[lang]),
            'series': {'title': data['title'], 'deck': data['deck'], 'intro': intro, 'scope': scope, 'source_note': note},
            'articles': articles, 'review': {'unresolved': []},
        }
        pending[BASE / f'{lang}.json'] = dump(packed)
    for path, text in pending.items():
        output(path, text, False)
    print(f'Imported {len(LOCALES)*len(SLUGS)} essays; {fallback_count} reference labels used English fallback.')


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
    # Render the shared channel cards and our Library badge using the standard
    # connector; don't emit another announcement or reorder the homepage.
    entry_for_catalog = dict(entry, library_count={
        'en': '8 essays · 8 languages', 'zh': '8 篇 · 八语', 'zh-hant': '8 篇 · 八語',
    })
    output(BASE / 'discovery.json', dump(entry_for_catalog), check)
    public_cards = connection.render(KEY)
    for path in [ROOT/'library.html', *(ROOT/f'essays/{lang}/index.html' for lang in LOCALES)]:
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
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    if args.import_dir:
        assert not args.check
        import_data(args.import_dir, args.references)
    primary_outputs(args.check)
    foreign_outputs(args.check)
    discover_outputs(args.check)
    print(('Checked' if args.check else 'Built') + ' 9 primary pages, 45 new-language pages, and scoped discovery.')


if __name__ == '__main__':
    main()

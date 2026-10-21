"""Full-length foreign reading editions; received manuscripts remain immutable.

Only the explicit, auditable substitutions in corrections.json are applied.
The Chinese author manuscripts are never read back from a translation package.
"""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/originals/hongloumeng/translations'
DATE = '2026-10-20'
FOREIGN = {
    'en': ('English', 'Dream of the Red Chamber: Thirty New Chapters',
           'Original continuation by Han Qin, not a recovered manuscript by Cao Xueqin.',
           'Chapters 81–82 are available in eight languages. Chapters 83–110 remain unpublished. The Chinese original is by Han Qin; these are independent translations, not passages reproduced from existing translations of the novel.',
           'Original fiction', 'Red Chamber project · English', 'Library', 'Skip to content', 'Chapters', 'Read chapter', 'Chapter 83 · Forthcoming', 'A note on this edition',
           'Names follow the reader tradition established by David Hawkes where supported by the project’s references. This new continuation is translated independently from Han Qin’s Chinese, preserving dialogue, poems and narrative uncertainties.'),
    'de': ('Deutsch', 'Der Traum der Roten Kammer: Dreißig neue Kapitel',
           'Eine eigenständige Fortsetzung von Han Qin, kein wiederentdecktes Manuskript von Cao Xueqin.',
           'Die Kapitel 81–82 sind in acht Sprachen lesbar. Die Kapitel 83–110 sind noch nicht veröffentlicht. Das chinesische Original stammt von Han Qin; die Übersetzungen sind eigenständig und übernehmen keine Passagen aus vorhandenen Romanübersetzungen.',
           'Originalerzählungen', 'Projekt zur Roten Kammer · Englisch', 'Bibliothek', 'Zum Text', 'Kapitelübersicht', 'Kapitel lesen', 'Kapitel 83 · Noch nicht veröffentlicht', 'Zu dieser Ausgabe',
           'Die Namen knüpfen, soweit durch die Projektbelege gestützt, an die deutsche Lesertradition um Franz Kuhn an. Die Fortsetzung selbst wird ungekürzt aus Han Qins chinesischem Text übersetzt; Dialoge, Verse und Ungewissheiten bleiben erhalten.'),
    'fr': ('Français', 'Le Rêve dans le pavillon rouge : trente nouveaux récits',
           'Une suite originale de Han Qin, et non un manuscrit retrouvé de Cao Xueqin.',
           'Les récits 81–82 sont disponibles en huit langues. Les récits 83–110 ne sont pas encore publiés. Le texte chinois est de Han Qin ; les traductions sont indépendantes et ne reproduisent aucun passage des traductions existantes du roman.',
           'Fictions originales', 'Projet du Pavillon rouge · anglais', 'Bibliothèque', 'Aller au texte', 'Table des récits', 'Lire le récit', 'Récit 83 · À paraître', 'À propos de cette version',
           'Les noms suivent, selon les références réunies pour le projet, la tradition de Li Tche-houa et Jacqueline Alézaïs. Cette suite est traduite indépendamment du chinois de Han Qin, sans supprimer les dialogues, les poèmes ni les incertitudes du récit.'),
    'es': ('Español', 'Sueño en el pabellón rojo: treinta nuevos capítulos',
           'Continuación original de Han Qin, no un manuscrito recuperado de Cao Xueqin.',
           'Los capítulos 81–82 están disponibles en ocho lenguas. Los capítulos 83–110 aún no se han publicado. El original chino es de Han Qin; las traducciones son independientes y no reproducen pasajes de traducciones anteriores de la novela.',
           'Ficción original', 'Proyecto del Pabellón Rojo · inglés', 'Biblioteca', 'Ir al texto', 'Índice de capítulos', 'Leer capítulo', 'Capítulo 83 · Próximamente', 'Sobre esta versión',
           'Los nombres siguen la tradición de lectura de Zhao Zhenjiang, José Antonio García Sánchez y Alicia Relinque, según las referencias del proyecto. La continuación se traduce de forma independiente del chino de Han Qin, con sus diálogos, poemas y asuntos sin resolver.'),
    'ja': ('日本語', '紅楼夢・新たな三十回',
           '秦漢による創作続篇です。曹雪芹の佚稿や、その発見・復元を主張するものではありません。',
           '第八十一・八十二回を八言語で公開しています。第八十三〜百十回は未公開です。中国語原作は秦漢によるものです。各言語版は独立した翻訳であり、既刊の『紅楼夢』訳文の転載ではありません。',
           '創作作品', '紅楼夢プロジェクト・英語', '書庫', '本文へ', '回目一覧', '本文を読む', '第八十三回・未公開', 'この翻訳について',
           '人名は日本語で読める漢字表記を基本とし、松枝茂夫訳を参照する際も、未確認の読みを断定しません。秦漢の中国語原作から独立して訳し、会話や詩詞、語られていないことを残しています。'),
    'ko': ('한국어', '홍루몽: 새로 쓴 서른 회',
           '진한(秦漢)이 창작한 속편이며, 조설근의 잃어버린 원고가 아닙니다.',
           '제81·82회를 여덟 언어로 읽을 수 있습니다. 제83~110회는 아직 공개하지 않았습니다. 중국어 원작은 진한이 썼으며, 각 언어판은 기존 『홍루몽』 번역의 문장을 옮긴 것이 아닌 독립 번역입니다.',
           '창작 소설', '홍루몽 프로젝트 · 영어', '서가', '본문으로', '회차 목록', '본문 읽기', '제83회 · 공개 예정', '이 번역에 관하여',
           '인명은 최용철·고민희 번역을 참조한 한국어 독서 전통과 프로젝트의 표기 원칙을 따릅니다. 진한의 중국어 원작에서 독립적으로 번역하여 대화와 시가, 서술의 여백을 남겼습니다.'),
}


def edition(stem, lang):
    """Return title, mapped body units and separate reader notes."""
    path = DATA / 'received' / stem / f'{stem}_{lang}.md'
    raw = path.read_bytes()
    receipt = json.loads((DATA.parent/'publication.json').read_text())['multilingual_publication']
    assert hashlib.sha256(raw).hexdigest() == receipt['received_files'][str(path.relative_to(DATA.parent))], path
    text = raw.decode()
    for fix in json.loads((DATA / 'corrections.json').read_text()):
        if fix['chapter'] == stem and fix['language'] == lang:
            assert text.count(fix['before']) == fix['count'], fix
            text = text.replace(fix['before'], fix['after'])
    blocks = re.split(r'\n\s*\n', text.strip())
    title = []
    while blocks and (blocks[0].startswith('#') or (lang == 'en' and blocks[0].startswith('*'))):
        title.append(re.sub(r'^#+\s*', '', blocks.pop(0)).replace('*', '').replace('  \n', '\n'))
    notes = []
    if blocks[-1].startswith('Nota 1.'):
        notes.append(blocks.pop())
    body = '\n\n'.join(blocks)
    units = []
    if '<!-- P' in body:
        pieces = re.split(r'<!-- P(\d+)(?:[–-](?:P)?(\d+))? -->\s*', body)
        assert not pieces[0].strip()
        for i in range(1, len(pieces), 3):
            start, end, value = pieces[i:i+3]
            start = int(start)
            if end:
                lines = value.strip().splitlines()
                assert len(lines) == int(end)-start+1
                units.extend((start+j, v.strip()) for j, v in enumerate(lines))
            else:
                units.append((start, value.strip()))
    else:
        for value in blocks:
            if len(units) == 90:  # Chapter 81's eight-line spontaneous song.
                lines = value.splitlines()
                assert len(lines) == 8
                units.extend((len(units)+1, v.strip()) for v in lines)
            else:
                units.append((len(units)+1, value.strip()))
    expected = 101 if stem == 'ch081' else 67
    assert [n for n, _ in units] == list(range(1, expected+1)), (stem, lang)
    return '\n'.join(title), units, notes


def inline(text):
    # Received body text contains only emphasis, not arbitrary HTML or links.
    return re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html.escape(text))


def render_foreign(editions, language_menu, origin, target):
    pages = {}
    for lang, ui in FOREIGN.items():
        label, collection, notice, intro, shelf, project, library, skip, contents, read, pending, note_title, note = ui
        for stem in ('index', 'ch081', 'ch082'):
            story = stem != 'index'
            title, units, notes = edition(stem, lang) if story else (collection, [], [])
            e = html.escape
            url = origin+lang+'/'+(stem+'.html' if story else '')
            alternatives = ''.join(f'<link rel="alternate" hreflang="{code}" href="{origin+d+(stem+".html" if story else "")}">' for d, code, _ in editions.values())
            alternatives += f'<link rel="alternate" hreflang="x-default" href="{origin+(stem+".html" if story else "")}">'
            schema = {'@context':'https://schema.org', '@type':'Chapter' if story else 'CollectionPage', 'name':title.replace('\n',' · '), 'url':url, 'inLanguage':lang, 'author':{'@type':'Person','name':'Han Qin (秦汉)'}, 'datePublished':DATE, 'dateModified':DATE}
            if story:
                schema.update(position=int(stem[2:]), isPartOf={'@type':'CreativeWork','name':collection,'url':origin+lang+'/'}, translationOfWork={'@type':'Chapter','url':origin+stem+'.html','inLanguage':'zh-Hans'})
                body = []
                for number, value in units:
                    verse = (stem == 'ch081' and 91 <= number <= 98) or (stem == 'ch082' and number in (38,39))
                    paragraphs = re.split(r'\n\s*\n',value)
                    rendered = ''.join('<p>'+inline(p).replace('\n','<br>')+'</p>' for p in paragraphs)
                    body.append(f'<div data-source-unit="{number}"'+(' class="verse"' if verse else '')+'>'+rendered+'</div>')
                h1 = ''.join(f'<span class="{"chapter-number" if i==0 else "chapter-couplet"}">{e(line)}</span>' for i,line in enumerate(title.replace('　','\n').splitlines()))
                other = 'ch082' if stem == 'ch081' else 'ch081'
                other_title = edition(other,lang)[0].splitlines()[0].split('　')[0]
                navigation = f'<a href="{other}.html">{e(other_title)} {"→" if stem=="ch081" else "←"}</a>'
                if stem == 'ch082': navigation += f'<span>{e(pending)}</span>'
                content = f'<article><header class="chapter-head"><p class="eyebrow">Han Qin · {e(collection)}</p><h1>{h1}</h1><p class="authorship">{e(notice)}</p></header><div class="novel-text">'+ '\n'.join(body) + '</div></article>'
                content += f'<details class="reading-note"><summary>{e(note_title)}</summary><p>{e(note)}</p>'+''.join(f'<p>{inline(n)}</p>' for n in notes)+'</details>'
                content += f'<nav class="chapter-nav" aria-label="{e(contents)}"><a href="index.html">{e(contents)}</a>{navigation}</nav>'
            else:
                schema['hasPart'] = [{'@type':'Chapter','name':edition(ch,lang)[0].replace('\n',' · '),'url':origin+lang+'/'+ch+'.html'} for ch in ('ch081','ch082')]
                cards = ''.join(f'<a class="chapter-card" href="{ch}.html">{e(edition(ch,lang)[0]).replace(chr(10),"<br>")}<small>{e(read)} →</small></a>' for ch in ('ch081','ch082'))
                content = f'<header class="collection-head"><p class="eyebrow">Han Qin · 81–110</p><h1>{e(collection)}</h1><p class="authorship">{e(notice)}</p></header><section class="introduction"><p>{e(intro)}</p></section><section class="contents"><h2>{e(contents)}</h2>{cards}</section>'
            pages[target/lang/(stem+'.html')] = f'''<!DOCTYPE html>
<html lang="{lang}" data-lang="{lang}" data-editions="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title.replace(chr(10),' · '))} — Non Dubito</title><meta name="description" content="{e(notice+' '+collection+' · '+('81–82' if not story else str(int(stem[2:]))))}"><meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{url}">{alternatives}<meta property="og:type" content="{'article' if story else 'website'}"><meta property="og:title" content="{e(title.replace(chr(10),' · '))}"><meta property="og:description" content="{e(notice)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="icon" href="../../../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../novel.css?v=20261020"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><a class="skip" href="#main">{e(skip)}</a><header class="site-header"><a class="brand" href="../../../index.html?lang=en">Non <span>Dubito</span></a><nav><a href="../../../originals/index.html?lang=en">{e(shelf)}</a><a href="../../../essays/literature/hlm/en/index.html">{e(project)}</a><a href="../../../library.html?lang=en">{e(library)}</a></nav>{language_menu(lang,stem+'.html')}</header><main id="main">{content}</main><footer><a href="../../../essays/literature/hlm/en/index.html">{e(project)}</a><p>© 2026 Han Qin (秦汉) · Non Dubito</p></footer></body></html>
'''
    return pages

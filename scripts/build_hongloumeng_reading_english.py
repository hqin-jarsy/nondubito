#!/usr/bin/env python3
"""English reader candidate. Pure rendering and fail-closed production planning.

No CLI, filesystem writer or legacy pipeline release call. The caller must review
and apply a complete plan only after final content acceptance and authorization.
"""
from datetime import date
import html
import json
import re
from pathlib import Path
import build_hongloumeng_reading as chinese
import hongloumeng_english_pipeline as pipeline
from web_analytics import tracked_html

E = html.escape
TITLE = 'Dream of the Red Chamber'
EDITION = 'Dazhi Revised Gengchen Edition · English'
BASE = '/classics/hongloumeng/'
ORIGIN = 'https://nondubito.net'
CONTINUATION = '/originals/hongloumeng/en/ch081.html'
NOTICE = ('The first eighty chapters end here. Chapters 81–85 are Han Qin’s original '
          'continuation, not a recovered manuscript by Cao Xueqin. Chapters 86–110 remain unpublished.')


def load_validated():
    """Use actual current source/norm validators. Does not promote any state."""
    mapping = pipeline.source_map(pipeline.load_source())
    saved = json.loads((pipeline.DATA / 'source-map.json').read_text())
    if saved != mapping:
        raise ValueError('Current Chinese source map differs')
    progress = json.loads((pipeline.DATA / 'progress.json').read_text())
    notes = json.loads((pipeline.DATA / 'reader-notes.json').read_text())
    snapshot = pipeline.validate_standard_readiness(mapping, progress)
    pipeline.validate_progress(mapping, progress, snapshot)
    pipeline.validate_reader_notes(mapping, notes)
    return mapping, progress, notes, snapshot


def require_complete(mapping, progress):
    if ({u['chapter'] for u in mapping['units']} != set(range(1, 81)) or
        len(mapping['units']) != len(progress['units']) or
        any(u['state'] != 'accepted' for u in progress['units']) or
        len(progress['checkpoints']) != 16 or
        any(c['state'] != 'accepted' for c in progress['checkpoints'])):
        raise ValueError('Production requires all eighty complete accepted chapters and sixteen accepted checkpoints')


def note_location(note, source, unit, documents, source_texts):
    """Resolve committed placement, never infer an occurrence in rendered HTML."""
    index = len(unit['segments'])-1
    offset = len(unit['segments'][index]['text'])
    reference = note.get('glossaryId', '')
    filename = reference.split('#', 1)[0]
    if re.fullmatch(r'english-batch-[0-9]{3}-[0-9]{3}\.json', filename):
        if filename not in documents:
            path = pipeline.STANDARD/filename
            chinese.checked_input_paths([path])
            documents[filename] = json.loads(path.read_text())
        explicit_table = 'selectedReaderNotes' in documents[filename]
    else:
        explicit_table = False
    if 'selectedReaderNotes' not in reference and not explicit_table:
        return index, offset
    match = re.fullmatch(r'(english-batch-[0-9]{3}-[0-9]{3}\.json)#/selectedReaderNotes/(0|[1-9][0-9]*)', reference)
    if match is None:
        raise ValueError('Malformed explicit reader-note reference')
    filename, position = match.groups()
    if filename not in documents:
        path = pipeline.STANDARD/filename
        chinese.checked_input_paths([path])
        documents[filename] = json.loads(path.read_text())
    records = documents[filename].get('selectedReaderNotes')
    if not isinstance(records, list) or int(position) >= len(records):
        raise ValueError('Missing explicit reader-note record')
    record = records[int(position)]
    if unit['id']=='hlm-c049-b0033':
        from hongloumeng_japanese_navigation_binding import note_record
        record=note_record(record,note,source,unit,pipeline.ROOT)
    if record.get('text') != note['text'] or note.get('sourceHash') != source['sourceHash']:
        raise ValueError('Explicit reader-note source or wording differs')
    if 'textSHA256' in record and record['textSHA256'] != pipeline.sha(note['text'].encode()):
        raise ValueError('Explicit reader-note wording hash differs')
    if ('anchor' in record) == ('placement' in record):
        raise ValueError('Explicit reader-note requires one anchor or placement')
    location = record.get('anchor', record.get('placement'))
    if not isinstance(location, dict) or location.get('unitId') != unit['id']:
        raise ValueError('Explicit reader-note unit differs')
    if 'sourceHash' in location and location['sourceHash'] != source['sourceHash']:
        raise ValueError('Explicit reader-note source hash differs')
    index = location.get('segmentIndex')
    if type(index) is not int or not 0 <= index < len(unit['segments']):
        raise ValueError('Explicit reader-note segment differs')
    text = unit['segments'][index]['text']
    for hash_field in ('segmentSHA256', 'segmentTextSHA256'):
        if hash_field in location and location[hash_field] != pipeline.sha(text.encode()):
            raise ValueError('Explicit reader-note segment hash differs: '+hash_field)
    if 'anchor' in record:
        start, end = location.get('start'), location.get('end')
        if (location.get('position') != 'after_anchor' or type(start) is not int or
            type(end) is not int or not 0 <= start < end <= len(text) or
            text[start:end] != location.get('text')):
            raise ValueError('Explicit reader-note range or substring differs')
        if 'offsetConvention' in location and location['offsetConvention'] != 'Unicode code points, zero-based, exclusive end':
            raise ValueError('Unknown reader-note offset convention')
        offset = end
    else:
        if set(location) != {'unitId','segmentIndex','segmentSHA256'}:
            raise ValueError('Unknown explicit reader-note segment placement')
        original = record.get('source')
        if not isinstance(original, dict) or original.get('unitId') != unit['id'] or original.get('sourceHash') != source['sourceHash']:
            raise ValueError('Explicit reader-note canonical source differs')
        if unit['id'] not in source_texts:
            reading = pipeline.load_source()
            chapter = reading['chapters'][source['chapter']-1]
            source_texts[unit['id']] = chapter['title'] if source['index']==0 else chapter['blocks'][source['index']-1]['text']
        start, end = original.get('start'), original.get('end')
        raw = source_texts[unit['id']]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(raw) or raw[start:end] != original.get('quote'):
            raise ValueError('Explicit reader-note canonical source substring differs')
        offset = len(text)
    return index, offset


def project(mapping, progress, notes, chapters, *, documents=None, source_texts=None):
    """Presentation projection only. Caller validates source/reviews beforehand.

    Private previews may explicitly select accepted chapters; no absent chapter
    receives a placeholder. Nothing from review references is projected.
    """
    wanted = tuple(chapters)
    if not wanted or len(set(wanted)) != len(wanted) or any(type(n) is not int or not 1 <= n <= 80 for n in wanted):
        raise ValueError('Invalid chapter selection')
    note_lookup = {n['unitId']: n for n in notes['notes']}
    if len(note_lookup) != len(notes['notes']):
        raise ValueError('Duplicate reader-note unit')
    documents = {} if documents is None else documents
    source_texts = {} if source_texts is None else source_texts
    result = []
    for number in sorted(wanted):
        pairs = [(s, u) for s, u in zip(mapping['units'], progress['units']) if s['chapter'] == number]
        if not pairs or pairs[0][0]['index'] != 0:
            raise ValueError('Missing chapter title')
        blocks = []
        title_note = None
        for source, unit in pairs:
            if unit['id'] != source['id'] or unit['sourceHash'] != source['sourceHash'] or unit['state'] != 'accepted' or not unit['segments']:
                raise ValueError('Preview requires complete accepted units')
            if any(not s['text'].strip() or s['kind'] != source['layout']['kind'] for s in unit['segments']):
                raise ValueError('Empty or mismatched segment')
            note = note_lookup.get(unit['id'])
            placement = note_location(note, source, unit, documents, source_texts) if note else None
            if source['index'] == 0:
                title = unit['segments'][0]['text']
                if unit['id'] in note_lookup:
                    title_note = dict(unitId=unit['id'], text=note['text'], offset=placement[1])
                    if placement[0] != 0 or len(unit['segments']) != 1:
                        raise ValueError('Unsupported multi-segment title note')
            else:
                for i, segment in enumerate(unit['segments']):
                    block = dict(source['layout'], text=segment['text'], anchor=f"{source['id']}-s{i+1}")
                    if i: block['first'] = False
                    if i < len(unit['segments'])-1: block['last'] = False
                    if placement and i == placement[0]:
                        block['note'] = note['text']
                        block['noteOffset'] = placement[1]
                        block['noteUnitId'] = unit['id']
                    blocks.append(block)
        result.append(dict(number=number, title=title, titleNote=title_note, blocks=blocks))
    return result


def languages(filename):
    return '<nav class="language-switch" aria-label="Languages">' + ''.join(
        f'<a lang="{code}" href="{BASE+directory+filename}"'+(' aria-current="page"' if code == 'en' else '')+f'>{label}</a>'
        for code,directory,label in [('zh-Hans','','简体中文'),('zh-Hant','zh-hant/','繁體中文'),('en','en/','English')]) + '</nav>'


@tracked_html
def shell(title, content, filename, preview):
    metadata = '<meta name="robots" content="noindex,nofollow">' if preview else (
        f'<link rel="canonical" href="{ORIGIN+BASE}en/{"" if filename == "index.html" else filename}">' + ''.join(
        f'<link rel="alternate" hreflang="{code}" href="{ORIGIN+BASE+d}{"" if filename == "index.html" else filename}">'
        for code,d in [('zh-Hans',''),('zh-Hant','zh-hant/'),('en','en/'),('x-default','')]))
    badge = '<p class="draft-notice">Private rendering preview. Not a published edition.</p>' if preview else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Non Dubito</title><meta name="description" content="An independent English translation of chapters 1–80 of Dream of the Red Chamber, from the Dazhi Revised Gengchen Edition.">{metadata}<link rel="stylesheet" href="reader.css"><script defer src="reader.js"></script></head><body><a class="skip" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="/">Non <span>Dubito</span></a><nav aria-label="Reading"><a href="index.html">Contents</a><a href="edition.html">About this edition</a></nav>{languages(filename)}</header><main id="main" tabindex="-1">{badge}{content}</main><footer>{E(EDITION)} · Cao Xueqin’s novel, edited by Han Qin.<br>Independent English translation. <a href="edition.html">Source and translation</a></footer></body></html>'''


def render(chapters, *, preview=True):
    numbers = [c['number'] for c in chapters]
    if not preview and numbers != list(range(1, 81)):
        raise ValueError('A production rendering requires all eighty chapters')
    pages = {}
    for c in chapters:
        n = c['number']; paragraphs = []; notes = []
        def note_reference(text, unit_id):
            k = len(notes)+1
            notes.append(f'<li id="note-{k}" data-note-unit="{E(unit_id)}">{E(text)} <a href="#ref-{k}" role="doc-backlink" aria-label="Return to note {k} in text">↩</a></li>')
            return f'<sup><a id="ref-{k}" href="#note-{k}" data-note-unit="{E(unit_id)}" role="doc-noteref" aria-label="Translator note {k}">{k}</a></sup>'
        title_reference = note_reference(c['titleNote']['text'], c['titleNote']['unitId']) if c.get('titleNote') else '' 
        for b in c['blocks']:
            anchor = E(b['anchor']); rendered = chinese.paragraph(dict(b, text=''))
            rendered = rendered.replace('<p ', f'<p id="{anchor}" ', 1)
            text = b['text']; offset = b.get('noteOffset', len(text))
            if type(offset) is not int or not 0 <= offset <= len(text):
                raise ValueError('Invalid projected note offset')
            content = E(text)
            if 'note' in b:
                content = E(text[:offset]) + note_reference(b['note'], b.get('noteUnitId', b['anchor'])) + E(text[offset:])
            rendered = rendered[:-4] + content + '</p>'
            paragraphs.append(rendered)
        title_lines = c['title'].split('\n')
        title_offset = c['titleNote'].get('offset', len(c['title'])) if c.get('titleNote') else None
        if title_offset is not None and (type(title_offset) is not int or not 0 <= title_offset <= len(c['title'])):
            raise ValueError('Invalid projected title-note offset')
        heading_parts = []; cursor = 0; inserted = False
        for i, line in enumerate(title_lines):
            content = E(line)
            if title_offset is not None and cursor <= title_offset <= cursor+len(line):
                within = title_offset-cursor
                content = E(line[:within])+title_reference+E(line[within:]); inserted = True
            heading_parts.append(f'<span class="{"chapter-number" if i == 0 else "chapter-couplet"}">{content}</span>')
            cursor += len(line)+1
        if title_reference and not inserted:
            raise ValueError('Title-note offset does not map to a title line')
        heading = '\n'.join(heading_parts)
        prev = f'<a rel="prev" href="ch{n-1:03d}.html">← Chapter {n-1}</a>' if n-1 in numbers else '<span></span>'
        nxt = f'<a rel="next" href="ch{n+1:03d}.html">Chapter {n+1} →</a>' if n+1 in numbers else (f'<a href="{CONTINUATION}">Han Qin’s continuation · Chapter 81 →</a>' if n == 80 else '<span>End of private preview</span>')
        note_html = '<section class="reader-notes" role="doc-endnotes" aria-labelledby="notes-heading"><h2 id="notes-heading">Translator’s notes</h2><ol>'+''.join(notes)+'</ol></section>' if notes else ''
        content = f'<article><header class="chapter-head"><p class="edition-name">{E(EDITION)}</p><h1>{heading}</h1><div class="reader-tools"><button data-font="minus" aria-label="Smaller text">A −</button><button data-font="reset">Reset text</button><button data-font="plus" aria-label="Larger text">A +</button><a href="#chapter-nav">Chapter end</a></div></header><div class="novel-text">'+''.join(paragraphs)+'</div>'+note_html+f'</article><nav class="chapter-nav" id="chapter-nav" aria-label="Chapter navigation">{prev}<a href="index.html#ch{n:03d}">Contents</a>{nxt}</nav>'
        if n == 80: content += f'<p class="edition-note">{E(NOTICE)}</p>'
        pages[f'ch{n:03d}.html'] = shell(c['title'], content, f'ch{n:03d}.html', preview)
    catalog = ''.join(f'<li id="ch{c["number"]:03d}"><a href="ch{c["number"]:03d}.html">{E(c["title"])}</a></li>' for c in chapters)
    pages['index.html'] = shell(TITLE, f'<header class="book-head"><h1>{TITLE}</h1><p class="deck">{EDITION}</p><p>Chapters 1–80 · An independent English translation</p></header><section class="chapter-batch"><h2>Contents</h2><ol>{catalog}</ol></section><section class="continuation"><h2>Beyond chapter eighty</h2><p>{NOTICE}</p><a href="/originals/hongloumeng/en/index.html">Han Qin’s continuation</a></section>', 'index.html', preview)
    about = f'<section class="editorial"><h1>About this edition</h1><h2>{EDITION}</h2><p>Cao Xueqin’s novel, edited and revised in Chinese by Han Qin. This independent English translation follows that Chinese reading edition, including its declared editorial choices. It does not reproduce an existing English translation.</p><p>The edition name does not claim a verbatim reproduction of the Gengchen manuscript. The selected Chinese source includes material from several witnesses. Editorial repairs are choices of this edition, not a claim to recover a unique original.</p><p>Names follow the project’s established reading tradition, consistent with its independently translated continuation. Translator’s notes are separately labelled and linked to the relevant passage. Source commentary is not silently inserted into the novel.</p><p><a href="../edition.html">Chinese edition and source statement</a></p><h2>The novel and its continuation</h2><p>{NOTICE}</p></section>'
    pages['edition.html'] = shell('About this edition', about, 'edition.html', preview)
    # Reuse the existing reading design, without its Chinese-only font dependency.
    pages['reader.css'] = chinese.CSS[chinese.CSS.index(':root'):]+ '\nbody{font-family:Georgia,"Times New Roman",serif}.novel-text{line-height:1.85;line-break:auto;overflow-wrap:break-word}.novel-text p{text-indent:1.5em;white-space:pre-line}.reader-notes{font-size:16px;line-height:1.8;margin:40px 0}.reader-notes li{margin:1em 0}.language-switch{font:13px system-ui,sans-serif}h1{overflow-wrap:break-word}.chapter-batch a{white-space:pre-line}.novel-text p.verse,.novel-text p.couplet{padding-left:1em;text-indent:-1em;white-space:pre-line}.novel-text p.letter,.novel-text p.diagram{white-space:pre-line}.reader-notes :target,.novel-text :target{background:#eee5d3}sup{font:12px system-ui,sans-serif}sup a{padding:4px}\n'
    pages['reader.js'] = chinese.JS.split('const q=')[0] + '})();'
    return pages


def production_plan(approval, *, root=None):
    """Read-only finite plan. Approval is a separately reviewed exact-input record.

    Never creates approval/evidence; never writes or enables discovery itself.
    """
    if root is not None and Path(root).resolve() != pipeline.ROOT.resolve():
        raise ValueError('Production validation root must match its current tracked pipeline')
    if not isinstance(approval, dict) or not isinstance(approval.get('publicationDate'), str):
        raise ValueError('Actual local-generation date required in reviewed approval')
    launch_date = date.fromisoformat(approval['publicationDate']).isoformat()
    if launch_date != approval['publicationDate']:
        raise ValueError('Publication date must use YYYY-MM-DD')
    mapping, progress, notes, snapshot = load_validated()
    require_complete(mapping, progress)
    from hongloumeng_reading_presentation_binding import BINDING_SHA256, REVIEW_SHA256
    from hongloumeng_ch005_author_binding import BINDING_SHA256 as CH005_BINDING_SHA256, REVIEW_SHA256 as CH005_REVIEW_SHA256
    from hongloumeng_two_readings_binding import BINDING_SHA256 as TWO_BINDING_SHA256, REVIEW_SHA256 as TWO_REVIEW_SHA256
    from hongloumeng_rose_paste_binding import BINDING_SHA256 as ROSE_BINDING_SHA256, REVIEW_SHA256 as ROSE_REVIEW_SHA256
    from hongloumeng_seven_character_binding import BINDING_SHA256 as SEVEN_BINDING_SHA256, REVIEW_SHA256 as SEVEN_REVIEW_SHA256
    from hongloumeng_later_two_readings_binding import BINDING_SHA256 as LATER_BINDING_SHA256, REVIEW_SHA256 as LATER_REVIEW_SHA256
    from hongloumeng_ch072_decisions_binding import BINDING_SHA256 as CH072_BINDING_SHA256, REVIEW_SHA256 as CH072_REVIEW_SHA256
    from hongloumeng_japanese_navigation_binding import BINDING_SHA256 as NAV_SHA
    expected = dict(japaneseNavigationBindingSHA256=NAV_SHA, chapter72BindingSHA256=CH072_BINDING_SHA256, chapter72ReviewSHA256=CH072_REVIEW_SHA256, laterTwoReadingsBindingSHA256=LATER_BINDING_SHA256, laterTwoReadingsReviewSHA256=LATER_REVIEW_SHA256, sevenCharacterBindingSHA256=SEVEN_BINDING_SHA256, sevenCharacterReviewSHA256=SEVEN_REVIEW_SHA256, rosePasteBindingSHA256=ROSE_BINDING_SHA256, rosePasteReviewSHA256=ROSE_REVIEW_SHA256, twoReadingsBindingSHA256=TWO_BINDING_SHA256, twoReadingsReviewSHA256=TWO_REVIEW_SHA256, chapter5BindingSHA256=CH005_BINDING_SHA256, chapter5ReviewSHA256=CH005_REVIEW_SHA256, schemaVersion=1, scope='english-first80-local-generation',
        presentationBindingSHA256=BINDING_SHA256, presentationReviewSHA256=REVIEW_SHA256,
        publicationDate=launch_date, sourceHash=mapping['sourceHash'], standardSnapshot=snapshot,
        progressHash=pipeline.sha((pipeline.DATA/'progress.json').read_bytes()),
        notesHash=pipeline.sha((pipeline.DATA/'reader-notes.json').read_bytes()),
        implementationHashes={name: pipeline.sha((Path(__file__).parent/name).read_bytes()) for name in ('build_hongloumeng_reading_english.py', 'build_hongloumeng_reading.py', 'hongloumeng_english_availability.py', 'build_hongloumeng_hub.py', 'hongloumeng_discovery_scope.py', 'refresh_hongloumeng_reading_discovery.py', 'build_content_registry.py', 'hongloumeng_english_pipeline.py', 'build_hongloumeng_reading_traditional.py', 'hongloumeng_translations.py', 'hongloumeng_reading_presentation_binding.py', 'hongloumeng_english_presentation_readiness.py', 'hongloumeng_ch005_author_binding.py', 'hongloumeng_two_readings_binding.py', 'hongloumeng_rose_paste_binding.py', 'hongloumeng_seven_character_binding.py', 'hongloumeng_later_two_readings_binding.py', 'hongloumeng_ch072_decisions_binding.py', 'hongloumeng_japanese_navigation_binding.py', 'integrate_hongloumeng_japanese.py', 'build_hongloumeng_reading_japanese.py', 'hongloumeng_japanese_availability.py')})
    if approval != expected:
        raise ValueError('Explicit exact-input local-generation approval required')
    chapters = project(mapping, progress, notes, range(1,81))
    from hongloumeng_japanese_navigation_binding import navigation_outputs
    return {'classics/hongloumeng/en/'+name: content for name,content in navigation_outputs('classics/hongloumeng/en/', render(chapters,preview=False)).items()}

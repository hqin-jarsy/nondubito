#!/usr/bin/env python3
"""Publish reviewed Blockchain batches at their existing eight-language URLs.

Import is explicit, additive and refuses stale Chinese snapshots. Ordinary
builds use the checked-in records, not ZIPs or translation services. The compact
collection renderer calls upgrade_outputs so a later build cannot restore its
old three-paragraph summaries over a complete edition.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

import markdown
from blockchain_navigation import page_path
from build_emperor_full_editions import replace_div
from build_emperor_traditional import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/blockchain-full'
LANGS = ('zh', 'zh-hant', 'en', 'de', 'fr', 'es', 'ja', 'ko')
FOREIGN = ('en', 'de', 'fr', 'es', 'ja', 'ko')
TOC = dict(zh='本篇目录', **{'zh-hant':'本篇目錄'}, en='In this essay',
           de='In diesem Essay', fr='Dans cet essai', es='En este ensayo',
           ja='この篇の目次', ko='이 글의 목차')
STYLE = '''<style id="blockchain-full-style">
.collection-body p{margin:0 0 1.4em;overflow-wrap:break-word}
.collection-body h2{margin:3em 0 1em;line-height:1.55;scroll-margin-top:110px}
.collection-body .source-note{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--cream-border);color:var(--ink-muted)}
.collection-body .source-note p{font-size:.85rem;line-height:1.8}
.blockchain-full-toc{margin:1.5rem 0 2.5rem;padding:1rem 1.2rem;border:1px solid var(--cream-border);font-family:var(--sans)}
.blockchain-full-toc summary{cursor:pointer;font-size:.82rem}
.blockchain-full-toc li{margin:.6rem 0;line-height:1.6;font-size:.85rem}
.collection-page{min-width:0;overflow-wrap:anywhere}
html[lang="ko"] .collection-body{word-break:keep-all}
</style>'''


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def serialized(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def plain(value):
    return html.unescape(re.sub(r'<[^>]*>', '', value)).strip()


def body_sections(source):
    match = re.search(r'<article\b[^>]*class="essay-body"[^>]*>(.*?)</article>', source, re.S)
    assert match, 'Missing source body'
    body = match[1].split('<div class="source-note"', 1)[0]
    chunks = re.split(r'<h2\b[^>]*>(.*?)</h2>', body, flags=re.S)
    result = [dict(heading=plain(chunks[i]), paragraphs=[plain(p) for p in
              re.findall(r'<p\b[^>]*>(.*?)</p>', chunks[i+1], re.S)])
              for i in range(1, len(chunks), 2)]
    assert len(result) == 8 and all(s['paragraphs'] for s in result)
    return result


def alignment_pairs(value, language, headings):
    if isinstance(value, list):
        rows = value
    elif 'sections' in value:
        rows = [p for s in value['sections'] for p in s['paragraphs']]
    else:
        rows = next(value[k] for k in ('paragraphs', 'blocks', 'rows') if k in value)
    return [(p.get('source', p.get('zh')), p.get('translation', p.get(language)))
            for p in rows if p.get('tag') != 'h2'
            and p.get('source', p.get('zh')) not in [*headings, '资料说明']]


def paragraph_html(text):
    # Input is paragraph text, not arbitrary HTML. Escape HTML and stop a date
    # such as "5. September" or a leading numeral becoming an ordered list.
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r'^(\d+)\. ', r'\1\\. ', escaped)
    rendered = markdown.markdown(escaped)
    if not re.fullmatch(r'<p>.*</p>', rendered, re.S) or rendered.count('<p>') != 1:
        raise ValueError('Expected exactly one Markdown paragraph: ' + text[:80])
    return rendered


def source_note_parts(tail):
    label=re.match(r'(?:#{2,3}\s+(.+)|\*\*(.+)\*\*)\s*\n+',tail)
    if label:
        return label[1] or label[2],tail[label.end():].strip()
    # A supplier's French EP14 note uses an inline label, not a heading.
    # Recognize the precise label, never silently treat arbitrary tail text
    # as a note or consume a missing body paragraph.
    inline=re.match(r'Note sur les sources\.\s+(.+)',tail,re.S)
    assert inline, ('Missing source note',tail[:100])
    return 'Note sur les sources',inline[1].strip()


def traditional_copy(converter, text):
    converted=converter.convert(text)
    # CoreFoundation leaves these context-sensitive forms ambiguous. Limit
    # replacements to the editorial phrases, never to distance units or 里程.
    for a,b in [('帖子里','帖子裡'),('白皮書里','白皮書裡'),('域里','域裡'),
                ('比較里','比較裡'),('行業里','行業裡'),('材料里','材料裡'),
                ('節里','節裡'),('倉庫里','倉庫裡'),('記錄里','記錄裡'),
                ('代碼里','代碼裡'),('系列里','系列裡'),('第三篇里','第三篇裡'),
                ('標準里','標準裡'),('年份里','年份裡'),('市場里','市場裡'),
                ('天里','天裡'),('判決里','判決裡'),('儲備里','儲備裡'),
                ('模型里','模型裡'),('池里','池裡'),('第七篇里','第七篇裡'),
                ('欄里','欄裡'),('幾篇里','幾篇裡'),('卷宗里','卷宗裡'),
                ('一句里','一句裡'),('小時里','小時裡'),('日里','日裡'),
                ('合約里','合約裡'),('拍賣里','拍賣裡'),('調查里','調查裡'),
                ('場景里','場景裡'),('句子里','句子裡'),('關係里','關係裡'),
                ('事故里','事故裡'),('抵御','抵禦'),('覈實','核實'),
                ('機制里','機制裡'),('體系里','體系裡'),('篇里','篇裡'),
                ('總額里','總額裡'),('月里','月裡'),('賬戶里','賬戶裡'),
                ('配置里','配置裡'),('系統里','系統裡'),('人里','人裡'),
                ('參數里','參數裡'),('路線里','路線裡'),('分鐘里','分鐘裡'),
                ('划成','劃成'),
                ('歷史里','歷史裡'),('區塊里','區塊裡'),('文件里','文件裡'),
                ('規則里','規則裡'),('說明書里','說明書裡'),('範圍里','範圍裡'),
                ('結構里','結構裡'),('程序里','程序裡'),('曆史','歷史'),
                ('合伙','合夥'),('只產品','隻產品'),('只基金','隻基金'),
                ('組里','組裡'),('制度里','制度裡'),('年里','年裡'),
                ('注明','註明'),
                ('反復','反覆'),('重復','重複'),
                ('看准','看準'),('量准','量準'),('說明瞭','說明了')]:
        converted=converted.replace(a,b)
    return converted


def import_batch(folder, plan_path, reports):
    plan = json.loads(plan_path.read_text())
    assert len(reports) == 3
    reviews = [json.loads(p.read_text()) for p in reports]
    reviewed_langs = {l for r in reviews for l in r['languages']}
    assert set(FOREIGN) <= reviewed_langs
    episodes = plan['episodes']
    assert 1 <= len(episodes) <= 5 and all(1 <= n <= 21 for n in episodes)
    for report in reviews:
        assert report['episodes'] == episodes and report.get('review_scope')
    archive = folder / plan['archive']
    assert digest(archive.read_bytes()) == plan['archive_sha256']
    with ZipFile(archive) as z:
        assert z.testzip() is None
        files = {n.split('/', 1)[1]: z.read(n) for n in z.namelist()
                 if '/' in n and not n.endswith('/')}
    root_edits = plan['edits']
    edits = []
    converter = TraditionalConverter()
    try:
        for e in root_edits:
            for lang in ('zh', 'en'):
                edits.append(dict(ep=e['ep'], lang=lang, section=e['section'],
                                  paragraph=e['paragraph'], after=e[lang], reason=e['reason']))
            edits.append(dict(ep=e['ep'], lang='zh-hant', section=e['section'],
                              paragraph=e['paragraph'], after=traditional_copy(converter,e['zh']), reason=e['reason']))
    finally:
        converter.close()
    for report in reviews:
        edits.extend(report['edits'])
    # Every source correction must be explicitly synchronized in all eight.
    for e in root_edits:
        for lang in LANGS:
            found = [x for x in edits if (x['ep'],x['lang'],x['section'],x['paragraph']) ==
                     (e['ep'],lang,e['section'],e['paragraph'])]
            assert len(found) == 1, ('Missing/duplicate synchronized correction', e, lang)
    prepared = {}
    spec = json.loads((ROOT/'data/collection-languages/blockchain.json').read_text())
    baseline = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for ep in episodes:
        slug = f'ep{ep:02}'
        target = DATA/(slug+'.json')
        assert not target.exists(), 'Refusing to replace reviewed edition '+slug
        source = files[f'sources/{slug}.zh.html'].decode()
        assert page_path('zh',slug).read_bytes() == source.encode(), 'Chinese source drift: '+slug
        source_sections = body_sections(source)
        source_paras = [p for s in source_sections for p in s['paragraphs']]
        counts = [len(s['paragraphs']) for s in source_sections]
        record = dict(episode=ep, baseline_commit=baseline, archive=archive.name,
                      archive_sha256=plan['archive_sha256'], source_sha256=digest(source),
                      paragraphs_by_section=counts, languages={}, edits=[],
                      review=dict(date=plan['date'],scope=plan['review_scope'],
                                  reports={p.name:digest(p.read_bytes()) for p in reports}),
                      references=plan.get('references',{}).get(str(ep),[]))
        for lang in LANGS:
            raw = files[f'essays/{slug}.{lang}.md']
            md = raw.decode('utf-8-sig')
            chunks = re.split(r'^## (.+)\n', md, flags=re.M)
            headings = chunks[1::2][:8]
            assert len(headings) == 8 and '\ufffd' not in md
            title = re.search(r'^# (.+)$', chunks[0], re.M)[1].strip()
            candidates = [x.strip() for x in re.split(r'\n\s*\n',chunks[0])
                          if x.strip() and not x.startswith('#') and 'https://' not in x and
                          'Han Qin' not in x and '秦汉' not in x and '秦漢' not in x and
                          not re.search(r'(?:Blockchain|블록체인)\s*\d',x)]
            fallback = spec['items'][ep-1]['copy'].get(lang, ['',title])[1] if lang in spec['series'] else title
            deck = max(candidates,key=len) if candidates else fallback
            if lang in ('zh','zh-hant'):
                snapshot = files[f'sources/{slug}.{lang}.html'].decode()
                assert page_path(lang,slug).read_bytes() == snapshot.encode(), 'Chinese snapshot drift'
                original = body_sections(snapshot)
                paras = [p for s in original for p in s['paragraphs']]
            else:
                pairs = alignment_pairs(json.loads(files[f'alignment/{slug}.{lang}.json']),lang,
                                        [s['heading'] for s in source_sections])
                # The JA flat file includes one final source-note paragraph.
                assert [x for x,_ in pairs[:len(source_paras)]] == source_paras, (slug,lang)
                assert len(pairs) in (len(source_paras),len(source_paras)+1)
                paras = [y for _,y in pairs[:len(source_paras)]]
            assert len(paras) == len(source_paras) and all(isinstance(p,str) and p.strip() for p in paras)
            position = 0
            for p in paras:
                at = md.find(p,position)
                assert at >= 0, ('Missing/reordered paragraph',slug,lang,p[:60])
                position = at+len(p)
            tail = md[position:].strip()
            note_label,note = source_note_parts(tail)
            assert note and '2026' in note
            sections = []
            offset = 0
            for heading, count in zip(headings,counts):
                sections.append(dict(heading=heading,paragraphs=paras[offset:offset+count]))
                offset += count
            edition = dict(title=title,deck=deck,sections=sections,
                           note_label=note_label,note=note,
                           received_md_sha256=digest(raw),original_page_sha256=digest(page_path(lang,slug).read_bytes()))
            if lang in ('zh','zh-hant'):
                edition['source_original_paragraphs'] = list(paras)
                edition['source_original_headings'] = [s['heading'] for s in original]
            for report in reviews:
                for meta in report.get('metadata',[]):
                    if (meta['ep'],meta['lang']) == (ep,lang):
                        for key in ('title','deck'):
                            if key in meta: edition[key]=meta[key]
            for meta in plan.get('metadata',[]):
                if (meta['ep'],meta['lang']) == (ep,lang):
                    for key in ('title','deck'):
                        if key in meta:edition[key]=meta[key]
                    if lang in ('zh','zh-hant') and 'deck' in meta:
                        node=re.search(r'<p class="article-deck">(.*?)</p>',snapshot,re.S)
                        assert node, 'Missing original Chinese deck'
                        edition['source_original_deck']=plain(node[1])
                    for key,value in meta.get('headings',{}).items():
                        sections[int(key)-1]['heading']=value
            for report in reviews:
                for change in report.get('heading_edits',[]):
                    if (change['ep'],change['lang'])==(ep,lang):
                        s=sections[change['section']-1]
                        assert s['heading']==change['before'], ('Stale heading correction',change)
                        s['heading']=change['after']
            assert edition['title'].strip() and edition['deck'].strip(), ('Missing title/deck',slug,lang)
            for edit in [e for e in edits if e['ep']==ep and e['lang']==lang]:
                ps = sections[edit['section']-1]['paragraphs']; index=edit['paragraph']-1
                before = ps[index]
                assert 'before' not in edit or edit['before']==before, ('Stale correction',edit)
                assert edit['after'].strip() and '\n\n' not in edit['after']
                ps[index] = edit['after']
                record['edits'].append(dict(edit,before=before))
            for s in sections:
                for p in s['paragraphs']: paragraph_html(p)
            record['languages'][lang] = edition
        prepared[target] = record
    # All inputs and corrections have passed before the additive import writes.
    DATA.mkdir(parents=True,exist_ok=True)
    audit_dir=DATA/'batches'
    audit_dir.mkdir(exist_ok=True)
    assert not (audit_dir/plan_path.name).exists()
    (audit_dir/plan_path.name).write_text(serialized(plan))
    for path,review in zip(reports,reviews):
        assert not (audit_dir/path.name).exists()
        (audit_dir/path.name).write_bytes(path.read_bytes())
    for target, record in prepared.items():
        target.write_text(serialized(record))
    print(f'Imported reviewed batch: {len(prepared)} essays × 8 languages')


def records():
    result = {}
    for path in sorted(DATA.glob('ep*.json')):
        r = json.loads(path.read_text())
        assert set(r['languages']) == set(LANGS)
        for edition in r['languages'].values():
            assert [len(s['paragraphs']) for s in edition['sections']] == r['paragraphs_by_section']
        result[path.stem] = r
    return result


def source_body(text, edition):
    """Retain Chinese source HTML byte-for-byte except explicit paragraph edits."""
    match = re.search(r'(<article\b[^>]*class="essay-body"[^>]*>)(.*?)(</article>)',text,re.S)
    assert match
    body = match[2]
    # Do not include the separate source-note paragraph in the body inventory.
    cutoff = body.find('<div class="source-note"')
    assert cutoff >= 0
    ps = list(re.finditer(r'<p\b[^>]*>(.*?)</p>',body[:cutoff],re.S))
    expected = [p for s in edition['sections'] for p in s['paragraphs']]
    assert len(ps)==len(expected)
    originals=edition['source_original_paragraphs']
    for node, desired, original in reversed(list(zip(ps,expected,originals))):
        assert plain(node[1]) in (plain(paragraph_html(desired)),original), 'Unreviewed Chinese paragraph change'
        if plain(node[1]) != plain(paragraph_html(desired)):
            body = body[:node.start()]+paragraph_html(desired)+body[node.end():]
    # Explicitly reviewed heading corrections (for example a misplaced decimal)
    # receive the same original-or-approved guard as Chinese paragraphs.
    headings=list(re.finditer(r'(<h2\b[^>]*>)(.*?)(</h2>)',body[:body.find('<div class="source-note"')],re.S))
    desired_headings=[s['heading'] for s in edition['sections']]
    original_headings=edition.get('source_original_headings',desired_headings)
    assert len(headings)==len(desired_headings)
    for node,desired,original in reversed(list(zip(headings,desired_headings,original_headings))):
        assert plain(node[2]) in (desired,original), 'Unreviewed Chinese heading change'
        if plain(node[2]) != desired:
            body=body[:node.start(2)]+html.escape(desired)+body[node.end(2):]
    return text[:match.start(2)]+body+text[match.end(2):]


def update_article(text,lang,slug,r):
    edition = r['languages'][lang]
    headings = [s['heading'] for s in edition['sections']]
    toc = '<ol>'+''.join(f'<li><a href="#section-{i}">{html.escape(h)}</a></li>'
                         for i,h in enumerate(headings,1))+'</ol>'
    if lang in ('zh','zh-hant'):
        text = source_body(text,edition)
    else:
        body = '\n'.join(f'<h2 id="section-{i}">{html.escape(s["heading"])}</h2>\n'+
                         '\n'.join(paragraph_html(p) for p in s['paragraphs'])
                         for i,s in enumerate(edition['sections'],1))
        note = '<div class="source-note"><strong>'+html.escape(edition['note_label'])+'</strong>'+paragraph_html(edition['note'])
        if r['references']:
            note += '<p>'+' · '.join('<a href="'+html.escape(v['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(v['label'])+' ↗</a>' for v in r['references'])+'</p>'
        body += '\n'+note+'</div>'
        if lang == 'en':
            text,n = re.subn(r'(<article\b[^>]*class="essay-body"[^>]*>).*?(</article>)',
                            lambda m:m[1]+'\n'+body+'\n'+m[2],text,count=1,flags=re.S)
            assert n==1
        else:
            details='<details class="blockchain-full-toc"><summary>'+TOC[lang]+'</summary>'+toc+'</details>'
            text=replace_div(text,'collection-body',details+'\n'+body)
            # The source note above replaces the legacy "short independent
            # rewrite; see Chinese for details" edition note, not the essay.
            text=re.sub(r'<p class="edition-note">.*?</p>','',text,flags=re.S)
    if lang in ('zh','en','zh-hant'):
        text,n=re.subn(r'(<aside class="chapter-aside">.*?<ol>).*?(</ol>)',lambda m:m[1]+toc[4:-5]+m[2],text,count=1,flags=re.S)
        assert n==1
    if lang in ('zh','zh-hant') and r['references']:
        text=re.sub(r'<p class="blockchain-review-references">.*?</p>','',text,flags=re.S)
        links='<p class="blockchain-review-references">'+' · '.join(
            '<a href="'+html.escape(v['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(v['label'])+' ↗</a>'
            for v in r['references'])+'</p>'
        text,n=re.subn(r'(<div class="source-note">.*?)(</div>)',lambda m:m[1]+links+m[2],text,count=1,flags=re.S)
        assert n==1
    text=re.sub(r'<style id="blockchain-full-style">.*?</style>\s*','',text,flags=re.S)
    text=text.replace('</head>',STYLE+'\n</head>',1)
    # Chinese metadata stays untouched unless an explicit reviewed deck change
    # was recorded, with the same original-or-approved guard as body edits.
    reviewed_chinese_deck = lang in ('zh','zh-hant') and 'source_original_deck' in edition
    if reviewed_chinese_deck:
        node=re.search(r'<p class="article-deck">(.*?)</p>',text,re.S)
        assert node and plain(node[1]) in (edition['source_original_deck'],edition['deck']), 'Unreviewed Chinese deck change'
    if lang not in ('zh','zh-hant') or reviewed_chinese_deck:
        title,deck=map(html.escape,(edition['title'],edition['deck']))
        if not reviewed_chinese_deck:
            text=re.sub(r'<h1>.*?</h1>',lambda m:'<h1>'+title+'</h1>',text,count=1,flags=re.S)
        text=re.sub(r'(<p class="(?:article-deck|collection-deck)">).*?(</p>)',lambda m:m[1]+deck+m[2],text,count=1,flags=re.S)
        if not reviewed_chinese_deck:
            text=re.sub(r'<title>.*?</title>',lambda m:'<title>'+title+' · Blockchain — Non Dubito</title>',text,count=1,flags=re.S)
        text=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*(")',lambda m:m[1]+deck+m[2],text)
        if not reviewed_chinese_deck:
            text=re.sub(r'(<meta property="og:title" content=")[^"]*(")',lambda m:m[1]+title+m[2],text)
    def reviewed_schema(match):
        value=json.loads(match[2])
        if isinstance(value,dict) and value.get('@type') in ('Article','BlogPosting'):
            value['dateModified']=r['review']['date']
            if lang not in ('zh','zh-hant'):
                value['headline']=edition['title']
            if lang not in ('zh','zh-hant') or reviewed_chinese_deck:
                value['description']=edition['deck']
            return match[1]+json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+match[3]
        return match[0]
    text=re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',reviewed_schema,text,flags=re.S)
    return text


def upgrade_outputs(outputs):
    """Overlay only reviewed episodes, also when called by the compact builder."""
    reviewed=records()
    if not reviewed:return
    for slug,r in reviewed.items():
        for lang in LANGS:
            path=page_path(lang,slug)
            text=outputs.get(path,path.read_text())
            outputs[path]=update_article(text,lang,slug,r)
    for lang in LANGS:
        for path in sorted(page_path(lang,'index').parent.glob('*.html')):
            if path.stem!='index' and not re.fullmatch(r'ep\d{2}',path.stem):continue
            text=outputs.get(path,path.read_text())
            def anchor(match):
                tag=match[0]
                target=re.search(r'href="(ep\d{2})\.html"',tag)
                if not target or target[1] not in reviewed:return tag
                e=reviewed[target[1]]['languages'][lang]
                if lang in ('zh','zh-hant') and 'source_original_deck' not in e:return tag
                if 'class="collection-card"' in tag or 'class="blockchain-card"' in tag:
                    tag=re.sub(r'(<h[23]>).*?(</h[23]>)',lambda m:m[1]+html.escape(e['title'])+m[2],tag,count=1,flags=re.S)
                    return re.sub(r'(<p>).*?(</p>)',lambda m:m[1]+html.escape(e['deck'])+m[2],tag,count=1,flags=re.S)
                if 'class="page-turn ' in tag:
                    return re.sub(r'(<strong>).*?(</strong>)',lambda m:m[1]+html.escape(e['title'])+m[2],tag,flags=re.S)
                if '<small>' in tag:
                    return re.sub(r'(</small>).*?(</a>)',lambda m:m[1]+html.escape(e['title'])+m[2],tag,flags=re.S)
                return tag
            updated=re.sub(r'<a\b[^>]*>.*?</a>',anchor,text,flags=re.S)
            if updated!=text or path in outputs:outputs[path]=updated


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-folder',type=Path)
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--reports',nargs=3,type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.import_folder:
        assert args.plan and args.reports and not args.check
        import_batch(args.import_folder,args.plan,args.reports)
    outputs={}
    upgrade_outputs(outputs)
    changed={p:t for p,t in outputs.items() if p.read_text()!=t}
    if args.check:
        assert not changed, 'Stale reviewed Blockchain pages: '+str(list(changed))
        print(f'OK: {len(outputs)} complete Blockchain editions are current')
    else:
        for p,t in changed.items():p.write_text(t)
        print(f'Updated {len(changed)} of {len(outputs)} complete Blockchain editions')


if __name__=='__main__':
    main()

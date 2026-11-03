# -*- coding: utf-8 -*-
"""Print a narrow discovery patch; preserve all existing cards and update entries."""
from pathlib import Path
import difflib,html,json
from language_writing_languages import ROOT,LANGUAGES,load_language,DATE


def main():
    patch=['*** Begin Patch']
    def update(path,after):
        before=path.read_text()
        assert before!=after,path
        patch.append('*** Update File: '+str(path))
        patch.extend('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=1,lineterm=''))[2:])
    for lang in LANGUAGES:
        ui,_=load_language(lang)
        path=ROOT/f'essays/{lang}/index.html'
        text=path.read_text()
        assert 'LANGUAGE WRITING FULL START' not in text
        anchor='<div id="language-library" class="language-channel-library-anchor" aria-hidden="true"></div>'
        assert text.count(anchor)==1,lang
        card=f'\n<!-- LANGUAGE WRITING FULL START --><section class="essays-section" style="padding:2rem 0"><a href="../language-writing/{lang}/index.html" class="essay-card" style="display:block;text-decoration:none;border-left:3px solid var(--gold);padding:2rem"><p style="font-family:var(--sans);font-size:.8rem;color:var(--green)">{html.escape(ui["series"])}</p><h2 style="font-size:1.6rem;font-weight:400">{html.escape(ui["title"])}</h2><p>{html.escape(ui["deck"])}</p><p>{html.escape(ui["count"])}</p></a></section><!-- LANGUAGE WRITING FULL END -->'
        update(path,text.replace(anchor,anchor+card,1))
    entry={'id':'2026-11-03-language-writing-eight-languages','date':DATE,'kind':'expanded','domain':'sae','url':'essays/language-writing/index.html',
           'title':{'en':'Finding Words of Our Own · Eight Languages','zh':'语言与写作：八语全文','zh-hant':'語言與寫作：八語全文'},
           'summary':{'en':'All three essays now have complete German, French, Spanish, Japanese and Korean editions, alongside the unchanged English and Chinese texts. Naming, an unsent apology and a writer’s voice retain their full arguments and examples, with localized reading paths and same-essay language switching.',
                      'zh':'新增德法西日韩五语全文，与原有简繁中文及英文一起构成八语版本。三篇完整保留命名、未发出的道歉和写作声音的论证与场景，附各语言目录和同篇切换；现有中英繁正文不变。',
                      'zh-hant':'新增德法西日韓五語全文，與原有簡繁中文及英文一起構成八語版本。三篇完整保留命名、未發出的道歉和寫作聲音的論證與場景，附各語言目錄和同篇切換；現有中英繁正文不變。'},
           'languages':['en','zh','zh-hant',*LANGUAGES]}
    path=ROOT/'data/site-updates.json';text=path.read_text();assert entry['id'] not in text
    anchor='  "updates": [\n'
    record='\n'.join('    '+line for line in json.dumps(entry,ensure_ascii=False,indent=2).splitlines())+',\n'
    update(path,text.replace(anchor,anchor+record,1))
    names={'en':'en','zh':'zh','zh-hant':'hant'}
    titles=''.join(f'<h3 class="lang-{names[k]}">{html.escape(v)}</h3>' for k,v in entry['title'].items())
    summaries=''.join(f'<p class="lang-{names[k]}">{html.escape(v)}</p>' for k,v in entry['summary'].items())
    latest='<!-- LANGUAGE WRITING FULL LATEST START --><section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-language-writing-eight"><header class="updates-date"><h2 id="date-language-writing-eight"><time datetime="'+DATE+'">'+DATE+'</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="'+entry['id']+'"><div class="update-meta"><span class="update-kind"><span class="lang-en">Five complete new language editions</span><span class="lang-zh">新增五语全文</span><span class="lang-hant">新增五語全文</span></span><span>EN · 简 · 繁 · DE · FR · ES · 日本語 · 한국어</span></div>'+titles+summaries+'<a href="essays/language-writing/index.html"><span class="lang-en">Read the series →</span><span class="lang-zh">阅读系列 →</span><span class="lang-hant">閱讀系列 →</span></a></article></div></section></div></section><!-- LANGUAGE WRITING FULL LATEST END -->\n'
    home='<!-- LANGUAGE WRITING FULL HOME START --><a class="home-update-row" href="essays/language-writing/index.html"><time datetime="'+DATE+'">Nov 3</time><div><span class="lang-en home-update-kind">Language &amp; Writing · Three essays · 8 languages</span><span class="lang-zh home-update-kind">语言与写作 · 三篇 · 八语全文</span><span class="lang-hant home-update-kind">語言與寫作 · 三篇 · 八語全文</span><h3 class="lang-en">Finding Words of Our Own</h3><h3 class="lang-zh">把话说成自己的</h3><h3 class="lang-hant">把話說成自己的</h3></div></a><!-- LANGUAGE WRITING FULL HOME END -->\n'
    for name,block,anchor in [('latest.html',latest,'<!-- RED CHAMBER CH084 LATEST START -->'),('index.html',home,'<!-- RED CHAMBER CH084 HOME START -->')]:
        path=ROOT/name;text=path.read_text();assert text.count(anchor)==1
        update(path,text.replace(anchor,block+anchor,1))
    print('\n'.join(patch+['*** End Patch']))


if __name__=='__main__':main()

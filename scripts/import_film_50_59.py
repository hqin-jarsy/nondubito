#!/usr/bin/env python3
"""Publish film series 50–59 from edited Chinese sources and independent English rewrites."""
from __future__ import annotations
import ctypes, html, json, re
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=Path('/Users/hanqin/Documents/SAE解读/电影评论')
DATA=ROOT/'data/film-50-59'; OUT=ROOT/'essays/film'
CFG=[
(50,'raise-the-red-lantern','大红灯笼高高挂','Raise the Red Lantern','Three essays on entering a narrowed choice, a household that turns desire into a scoreboard, and the powerful face the film refuses to show.','三篇从颂莲自己走进院门，读到灯笼如何成为记分牌，以及影片始终没有拍清的那张权力之脸。',['1-she-walked-in','2-who-keeps-score','3-the-face-we-never-see']),
(51,'the-hunt','狩猎','The Hunt','Three essays on expulsion without a vote, the distance between a closed case and restored belonging, and a final shot that leaves suspicion without an address.','三篇从一个人如何被悄然划出“我们”，读到案件终止与重回人群的距离，以及最后那一枪留下的无地址怀疑。',['1-expelled-from-we','2-after-the-case-collapses','3-a-shot-with-no-declared-beginning']),
(52,'green-book','绿皮书','Green Book','Three essays on a chosen journey south, achievements that cannot purchase equality, and letters that help without taking over another person’s voice.','三篇从唐·雪莉主动南下，读到才华、学历与财富为何仍不足够，以及那些帮人说话却没有夺走声音的信。',['1-he-chose-the-south','2-three-things-were-not-enough','3-the-letters']),
(53,'a-clockwork-orange','发条橙','A Clockwork Orange','Three essays on violence without an alibi, a treatment that cuts agency along with harm, and a mind that exceeds every political use assigned to it.','三篇从没有借口的暴力，读到一种连同作恶与行动能力一起切掉的疗法，以及一个始终溢出政治用途的人。',['1-he-was-not-made-that-way','2-they-did-not-know-what-they-were-cutting','3-no-longer-the-governments-property']),
(54,'the-last-emperor','末代皇帝','The Last Emperor','Three essays on identities repeatedly assigned from outside, the women who remain or walk away, and a cricket that survives every official description.','三篇从一次次被外部命名的溥仪，读到留下与走出去的女人，以及一只从所有官方叙述里活下来的蟋蟀。',['1-told-who-he-was','2-the-one-who-walked-out','3-the-cricket']),
(55,'eternal-sunshine','暖暖内含光','Eternal Sunshine of the Spotless Mind','Three essays on memories erased but patterns retained, the opposite uses of one archive, and two modest words spoken with the worst evidence already known.','三篇从被删除的记忆与未消失的形状，读到同一份档案的两种方向，以及听完最坏证言后的两声“好吧”。',['1-delete-the-file-keep-the-shape','2-the-same-archive-two-directions','3-the-two-okays']),
(56,'dead-poets-society','死亡诗社','Dead Poets Society','Three essays on permission without an exit, a performance completed after calculation fails, and a classroom gesture that retracts coerced agreement.','三篇从只有许可却没有出路，读到尼尔在所有算计失效后演完那场戏，以及课堂上撤回被迫同意的站立。',['1-permission-is-not-a-way-out','2-he-stayed-on-stage','3-not-tribute-but-retraction']),
(57,'eat-drink-man-woman','饮食男女','Eat Drink Man Woman','Three essays on a feast that also takes attendance, a family capable only of announcements, and taste returning when care can finally receive an answer.','三篇从同时也是点名的周日宴席，读到只能宣布、不能商量的家，以及关心终于能收到回话时归来的味觉。',['1-the-table-as-summons','2-four-announcements','3-taste-keeps-the-accounts']),
(58,'the-pianist','钢琴家','The Pianist','Three essays on action outside the heroic checklist, a life carried by many bounded acts, and a rescuer whose name arrives too late.','三篇从英雄清单之外的行动，读到被多个有限决定接住的人生，以及一个来得太迟的救命者姓名。',['1-he-did-not-do-nothing','2-each-hand-its-own-act','3-the-name-not-heard']),
(59,'parasite','寄生虫','Parasite','Three essays on reasons that do not erase responsibility, people confined to partial views, and a social order imagined as one position to be won.','三篇从不能抹掉责任的理由，读到每个人被限制的视野，以及一种只能想象“赢得唯一位置”的秩序。',['1-reasons-do-not-make-innocence','2-each-person-looks-into-one-square','3-there-is-only-one-position'])]

class TC:
 def __init__(self):
  self.c=ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation'); c=self.c
  c.CFStringCreateMutable.argtypes=[ctypes.c_void_p,ctypes.c_long]; c.CFStringCreateMutable.restype=ctypes.c_void_p
  c.CFStringCreateWithCString.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_uint]; c.CFStringCreateWithCString.restype=ctypes.c_void_p
  c.CFStringAppend.argtypes=[ctypes.c_void_p,ctypes.c_void_p]; c.CFStringTransform.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ubyte]
  c.CFStringGetLength.argtypes=[ctypes.c_void_p]; c.CFStringGetLength.restype=ctypes.c_long
  c.CFStringGetMaximumSizeForEncoding.argtypes=[ctypes.c_long,ctypes.c_uint]; c.CFStringGetMaximumSizeForEncoding.restype=ctypes.c_long
  c.CFStringGetCString.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_long,ctypes.c_uint]; c.CFRelease.argtypes=[ctypes.c_void_p]
  self.t=self.s('Traditional-Simplified')
 def s(self,x): return self.c.CFStringCreateWithCString(None,x.encode(),0x08000100)
 def __call__(self,x):
  a=self.s(x); m=self.c.CFStringCreateMutable(None,0); self.c.CFStringAppend(m,a); self.c.CFStringTransform(m,None,self.t,1); n=self.c.CFStringGetMaximumSizeForEncoding(self.c.CFStringGetLength(m),0x08000100)+1; b=ctypes.create_string_buffer(n); self.c.CFStringGetCString(m,b,n,0x08000100); self.c.CFRelease(a); self.c.CFRelease(m); return b.value.decode().replace('視頻','影片')

def inline(s):
 s=html.escape(s,quote=True); s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s); return re.sub(r'\*(.+?)\*',r'<em>\1</em>',s)
def md(s,drop_h1=True):
 lines=s.strip().splitlines(); out=[]; para=[]
 def flush():
  if para: out.append('<p>'+inline(' '.join(x.strip() for x in para))+'</p>'); para.clear()
 for line in lines:
  if not line.strip(): flush()
  elif line.startswith('# '):
   flush()
   if not drop_h1: out.append('<h1>'+inline(line[2:])+'</h1>')
  elif line.startswith('## '): flush(); out.append('<h2>'+inline(line[3:])+'</h2>')
  elif line.strip()=='---': flush()
  else: para.append(line)
 flush(); return ''.join(out)
def split_en(path):
 text=path.read_text(); parts=re.split(r'(?m)^# ',text)[1:]; return [(p.splitlines()[0].strip(),'\n'.join(p.splitlines()[1:]).strip()) for p in parts]
def zh_docs(name):
 files=sorted((SRC/name).glob('*.md')); z=[]
 for f in files:
  t=f.read_text(); first=t.splitlines()[0][2:].strip(); title=first.split('：',1)[1] if '：' in first else first; z.append((title,'\n'.join(t.splitlines()[1:]).strip()))
 return z
LANGJS="""(function(){var saved=localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'zh';if(!['en','zh','zh-hant'].includes(saved))saved='zh';document.documentElement.dataset.lang=saved;document.documentElement.lang=saved==='zh-hant'?'zh-Hant':saved==='zh'?'zh-Hans':'en';document.addEventListener('DOMContentLoaded',function(){var b=document.querySelectorAll('.lang-btn[data-lang]');function u(){var x=document.documentElement.dataset.lang;b.forEach(function(q){q.classList.toggle('active',q.dataset.lang===x)})}b.forEach(function(q){q.onclick=function(){var x=q.dataset.lang;document.documentElement.dataset.lang=x;document.documentElement.lang=x==='zh-hant'?'zh-Hant':x==='zh'?'zh-Hans':'en';localStorage.setItem('nd_lang',x);localStorage.setItem('nondubito-lang',x);u()}});u()})})();"""
def head(title,desc,url,js): return f'''<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{html.escape(title)} — Non Dubito</title><meta name="description" content="{html.escape(desc,quote=True)}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(title)} — Non Dubito"><meta property="og:description" content="{html.escape(desc,quote=True)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="../../../style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;display=swap" rel="stylesheet"><link rel="icon" type="image/svg+xml" href="../../../favicon.svg"><link rel="canonical" href="{url}"><script>{LANGJS}</script><!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script><script defer src="zh-hant-data/{js}"></script>'''
def header(): return '''<header><div class="header-inner"><a href="../../../index.html" class="site-title"><span class="title-latin">Non <span style="color:var(--gold)">Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav><a href="../../../index.html">Essays</a><a href="../../../start.html">Start Here</a><a href="../../../library.html">Library</a><a href="../../../credesivis.html">Crede si vis</a><a href="../../../about.html">About</a><a href="https://self-as-an-end.net">SAE Theory ↗</a><a href="https://hqin.substack.com">Substack ↗</a></nav></div></header>'''
def toggle(): return '<div class="lang-toggle" style="margin-bottom:.8rem;"><button class="lang-btn" data-lang="en">EN</button><span class="lang-sep">|</span><button class="lang-btn" data-lang="zh">中文</button><span class="lang-sep">|</span><button class="lang-btn" data-lang="zh-hant">繁體</button></div>'
def footer(): return '''<footer><div class="footer-inner"><div class="footer-brand"><div class="footer-logo">Non <span>Dubito</span></div><div class="footer-tagline">A mind in many languages</div></div><div class="footer-links"><a href="https://self-as-an-end.net">SAE Theory</a><a href="https://hqin.substack.com">Substack</a><a href="https://x.com/hqinjarsy">X / Twitter</a><a href="../../../about.html">About</a></div></div><div class="footer-bottom"><span>© 2026 Han Qin (秦汉) · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span><span>nondubito.net</span></div></footer>'''
class Texts(HTMLParser):
 def __init__(self): super().__init__(); self.items=[]
 def handle_data(self,d):
  if re.search(r'[\u3400-\u9fff]',d): self.items.append(d)
def tcjs(page,conv):
 p=Texts(); p.feed(page); title=re.search(r'<title>(.*?)</title>',page).group(1); vals=set(p.items+[html.unescape(title)]); variants={v:conv(v) for v in vals}; return "(function(){'use strict';var variants="+json.dumps(variants,ensure_ascii=False)+";var originals=new WeakMap(),originalTitle=document.title;function u(){var t=document.documentElement.dataset.lang==='zh-hant';document.title=t&&variants[originalTitle]?variants[originalTitle]:originalTitle;var w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),n;while(n=w.nextNode()){var p=n.parentElement;if(!p||p.closest('.lang-en,.lang-toggle,script,style'))continue;if(!originals.has(n))originals.set(n,n.nodeValue);var s=originals.get(n);n.nodeValue=t&&variants[s]?variants[s]:s}}document.addEventListener('DOMContentLoaded',function(){u();new MutationObserver(u).observe(document.documentElement,{attributes:true,attributeFilter:['data-lang']})})})();\n"
def card(prefix,cfg):
 n,slug,zh,en,ed,zd,_=cfg; return f'<a href="{prefix}{slug}/index.html" class="series-card"><span class="series-card-count">No. {n:02d} · 3 essays</span><div class="series-card-title-zh">《{zh}》解读</div><div class="series-card-title-en">Reading {en}</div><p class="series-card-desc-zh lang-zh">{zd}</p><p class="series-card-desc-en lang-en">{ed}</p><span class="series-card-arrow lang-en">Read series</span><span class="series-card-arrow lang-zh">阅读系列</span></a>'
def write_pages(conv):
 for cfg in CFG:
  n,slug,zhn,enfilm,edesc,zdesc,slugs=cfg; ens=split_en(DATA/(slug+'.en.md')); zhs=zh_docs(zhn); assert len(ens)==len(zhs)==3
  d=OUT/slug; (d/'zh-hant-data').mkdir(parents=True,exist_ok=True)
  cards=''.join(f'<a href="{slugs[i]}.html" class="essay-card"><span class="card-num">{("I","II","III")[i]}</span><div class="card-body"><div class="card-lang-tag">English · 简 / 繁 · Film criticism</div><div class="card-title-en">{html.escape(ens[i][0])}</div><div class="card-title-zh" style="font-family:var(--cjk),serif;">{html.escape(zhs[i][0])}</div><div class="card-meta"><span>2026</span><span class="card-badge full">Three reading modes</span></div></div></a>' for i in range(3))
  url=f'https://nondubito.net/essays/film/{slug}/'; hero=toggle()+f'<a href="../index.html" class="back-link"><span class="lang-en">← Cinema</span><span class="lang-zh">← 电影</span></a><div class="essay-page-num"><span class="lang-en">Series · Three essays · Film criticism</span><span class="lang-zh">系列 · 三篇解读 · 电影评论</span></div><h1 class="essay-page-title lang-en">Reading {html.escape(enfilm)}</h1><h1 class="essay-page-title zh lang-zh" style="font-family:var(--cjk),serif;">《{zhn}》解读</h1><div class="essay-page-meta"><span>Sep 9, 2026</span><span>Han Qin (秦汉)</span><span class="lang-en">English · Simplified · Traditional</span><span class="lang-zh">英文 · 简体 · 繁体</span></div>'
  page=f'<!DOCTYPE html><html lang="zh-Hans" data-lang="zh"><head>{head("Reading "+enfilm,edesc,url,"index.js")}</head><body>{header()}<div class="essay-page"><div class="essay-page-hero"><div class="essay-page-inner">{hero}</div></div><div class="essay-body lang-en"><p style="font-size:1.2rem;line-height:1.9;">{edesc}</p><div class="essay-list" style="margin-top:3rem;">{cards}</div></div><div class="essay-body lang-zh" style="font-family:var(--cjk),serif;"><p style="font-size:1.2rem;line-height:1.9;">{zdesc}</p><div class="essay-list" style="margin-top:3rem;">{cards}</div></div></div>{footer()}</body></html>'
  (d/'index.html').write_text(page); (d/'zh-hant-data/index.js').write_text(tcjs(page,conv))
  for i in range(3):
   fn=slugs[i]+'.html'; u=url+fn; prev=f'<a href="{slugs[i-1]}.html">← Previous</a>' if i else '<a href="index.html">← Series overview</a>'; nxt=f'<a href="{slugs[i+1]}.html">Next →</a>' if i<2 else '<a href="index.html">Series overview →</a>'
   h=toggle()+f'<a href="index.html" class="back-link"><span class="lang-en">← Reading {html.escape(enfilm)}</span><span class="lang-zh">← 《{zhn}》解读</span></a><div class="essay-page-num"><span class="lang-en">Essay {i+1} of 3 · {html.escape(enfilm)}</span><span class="lang-zh">《{zhn}》解读 · {i+1} / 3</span></div><h1 class="essay-page-title lang-en">{html.escape(ens[i][0])}</h1><h1 class="essay-page-title zh lang-zh" style="font-family:var(--cjk),serif;">{html.escape(zhs[i][0])}</h1><div class="essay-page-meta"><span>Sep 9, 2026</span><span>Han Qin (秦汉)</span><span class="lang-en">Independent English edition</span><span class="lang-zh">中文原作 · 简 / 繁</span></div>'
   p=f'<!DOCTYPE html><html lang="zh-Hans" data-lang="zh"><head>{head(ens[i][0],edesc,u,slugs[i]+".js")}</head><body>{header()}<div class="essay-page"><div class="essay-page-hero"><div class="essay-page-inner">{h}</div></div><div class="essay-body lang-en"><p style="font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;"><strong>Edition note:</strong> Independent English rewriting; full-film spoilers.</p>{md(ens[i][1])}</div><div class="essay-body lang-zh" style="font-family:var(--cjk),serif;"><p style="font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;"><strong>版本说明：</strong>中文原作；简体与繁体同页切换。全片剧透。</p>{md(zhs[i][1])}</div><div style="max-width:700px;margin:0 auto;padding:2rem 2.5rem 4rem;display:flex;justify-content:space-between;">{prev}{nxt}</div></div>{footer()}</body></html>'
   (d/fn).write_text(p); (d/'zh-hant-data'/(slugs[i]+'.js')).write_text(tcjs(p,conv))
def update_indexes():
 fi=OUT/'index.html'; s=fi.read_text().replace('被外部命名的渥仪','被外部命名的溥仪');
 for a,b in [('Forty-nine series · One hundred forty-seven essays','Fifty-nine series · One hundred seventy-seven essays'),('四十九个系列 · 一百四十七篇','五十九个系列 · 一百七十七篇'),('Series 01–49','Series 01–59'),('系列 01–49','系列 01–59')]: s=s.replace(a,b)
 for c in CFG:
  if f'href="{c[1]}/index.html"' not in s: s=s.replace('</div></section></div><footer>',card('',c)+'</div></section></div><footer>')
 fi.write_text(s)
 lib=ROOT/'library.html'; s=lib.read_text().replace('被外部命名的渥仪','被外部命名的溥仪'); start=s.index('<hr class="lib-divider" data-film-channel>'); end=s.index('<hr class="lib-divider" data-games-channel>',start); block=s[start:end]
 for c in CFG:
  if f'essays/film/{c[1]}/index.html' not in block: block=block.replace('\n  </div>\n</section>', '\n    '+card('essays/film/',c)+'\n  </div>\n</section>')
 lib.write_text(s[:start]+block+s[end:])

def refresh_shared_traditional_data():
 from build_emperor_traditional import TextCollector, TraditionalConverter, reading_script
 converter=TraditionalConverter()
 try:
  for page,target in ((OUT/'index.html',OUT/'zh-hant-data/index.js'),(ROOT/'library.html',ROOT/'zh-hant-data/index.js')):
   source=page.read_text(encoding='utf-8'); collector=TextCollector(); collector.feed(source); variants={}
   for text in collector.text:
    traditional=converter.convert(text)
    if traditional!=text: variants[text]=traditional
   title_match=re.search(r'<title>(.*?)</title>',source,re.S)
   if title_match:
    title=title_match.group(1); traditional=converter.convert(title)
    if traditional!=title: variants[title]=traditional
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_text(reading_script(variants,page),encoding='utf-8')
 finally:
  converter.close()

def main():
 conv=TC(); write_pages(conv); update_indexes(); refresh_shared_traditional_data(); print('Published 10 film series / 30 essays')
if __name__=='__main__': main()

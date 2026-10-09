// Idempotent, scoped discovery wiring for the final two delivered anime series.
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const write=(p,s)=>fs.writeFileSync(path.join(root,p),s);
const series=JSON.parse(read('data/anime-full/batch05-received.json')).series;
const titles={en:'Madoka and The Apothecary Diaries: Complete Five-Language Editions',zh:'《小圆》与《药屋》：动漫五语全文接入完成','zh-hant':'《小圓》與《藥屋》：動漫五語全文接入完成'};
const summaries={en:'Ten essays in complete German, French, Spanish, Japanese and Korean editions, with local corrections to plot details and interpretive scope. This completes all 22 series in the delivered anime collection. Existing Chinese and English prose is preserved.',zh:'两部共10篇，接入50篇德法西日韩完整语言版，并局部校正情节与解读边界；这次交付的22部动漫系列已全部接入。原有简繁中英文正文保留。','zh-hant':'兩部共10篇，接入50篇德法西日韓完整語言版，並局部校正情節與解讀邊界；這次交付的22部動漫系列已全部接入。原有簡繁中英文正文保留。'};
const update={id:'2026-10-09-anime-full-batch05',date:'2026-10-09',kind:'expanded',domain:'stories',url:'essays/anime/index.html',languages:['de','fr','es','ja','ko'],title:titles,summary:summaries};
const ledger=JSON.parse(read('data/site-updates.json'));
ledger.updates=[update,...ledger.updates.filter(x=>x.id!==update.id)];
write('data/site-updates.json',JSON.stringify(ledger,null,2)+'\n');
let latest=read('latest.html');
latest=latest.replace(/<!-- ANIME FULL BATCH05 START -->[\s\S]*?<!-- ANIME FULL BATCH05 END -->\s*/,'');
const spans=(tag,values)=>Object.entries(values).map(([l,v])=>`<${tag} class="lang-${l==='zh-hant'?'hant':l}">${v}</${tag}>`).join('');
const card=`<!-- ANIME FULL BATCH05 START -->\n<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-anime-full-batch05"><header class="updates-date"><h2 id="date-anime-full-batch05"><time datetime="2026-10-09">9 October 2026</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="${update.id}"><div class="update-meta"><span class="update-kind">${spans('span',{en:'Complete editions',zh:'全文接入','zh-hant':'全文接入'})}</span><span class="update-languages">DE / FR / ES / JA / KO</span></div>${spans('h3',titles)}${spans('p',summaries)}<a href="essays/anime/index.html">${spans('span',{en:'Explore anime →',zh:'进入动漫频道 →','zh-hant':'進入動漫頻道 →'})}</a></article></div></section></div></section>\n<!-- ANIME FULL BATCH05 END -->\n`;
if(!latest.includes('<!-- ANIME FULL BATCH04 START -->'))throw Error('Latest anchor missing');
write('latest.html',latest.replace('<!-- ANIME FULL BATCH04 START -->',card+'<!-- ANIME FULL BATCH04 START -->'));
let hub=read('essays/anime/index.html');
for(const s of series){
 const pattern=new RegExp(`(<a href="${s.slug}/index.html" class="series-card">)([\\s\\S]*?)(</a>)`);
 if(!pattern.test(hub))throw Error('Hub card missing: '+s.slug);
 hub=hub.replace(pattern,(_,a,b,c)=>a+b.replace('5 essays · 3 reading modes','5 essays · 8 languages').replace('5 篇 · 英 / 简 / 繁','5 篇 · 8 种语言')+c);
}
write('essays/anime/index.html',hub);
const labels={de:'Anime und Manga · Vollständige Essays',fr:'Anime et manga · Essais complets',es:'Anime y manga · Ensayos completos',ja:'アニメと漫画 · 全文版',ko:'애니메이션과 만화 · 완전판 에세이'};
for(const lang of update.languages){
 const p=`essays/${lang}/index.html`;let s=read(p);
 s=s.replace(/<!-- ANIME FULL BATCH05 -->[\s\S]*?<!-- \/ANIME FULL BATCH05 -->/,'');
 let cards='<!-- ANIME FULL BATCH05 -->';
 for(const f of series){
  const route=`../anime/${f.slug}/${lang}/index.html`;
  if(s.includes(`href="${route}"`))throw Error('Unexpected existing card '+route);
  const index=read(`${f.route}/${lang}/index.html`);
  const title=index.match(/<h1>([\s\S]*?)<\/h1>/)[1];
  const intro=index.match(/<div class="series-desc"><p>([\s\S]*?)<\/p>/)[1];
  cards+=`<a href="${route}" class="essay-card" style="text-decoration:none;border-left:3px solid var(--gold);display:block;padding:2rem 2.25rem;"><div style="font-family:var(--sans);font-size:.65rem;letter-spacing:.13em;color:var(--green-light);margin-bottom:.7rem;">${labels[lang]}</div><div style="font-size:1.45rem;color:var(--ink);margin-bottom:.55rem;">${title}</div><p style="font-size:.92rem;color:var(--ink-light);line-height:1.72;margin:0;">${intro}</p></a>`;
 }
 cards+='<!-- /ANIME FULL BATCH05 -->';
 const marker='<!-- /ANIME FULL BATCH04 -->';if(!s.includes(marker))throw Error('Channel anchor missing');
 write(p,s.replace(marker,marker+cards));
}
console.log('Updated final anime batch: hub, five channels, latest page and editorial ledger.');

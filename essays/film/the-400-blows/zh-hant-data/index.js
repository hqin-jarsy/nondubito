/* Generated offline from essays/film/the-400-blows/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《四百击》解读":"《四百擊》解讀","一串可以理解的决定并不会因此变得无人负责：羞辱、暴力、放弃监护与制度处理，各自把一些东西加进安托万的羁押。":"一串可以理解的決定並不會因此變得無人負責：羞辱、暴力、放棄監護與制度處理，各自把一些東西加進安托萬的羈押。","一千法郎的约定":"一千法郎的約定","三篇解读：局部理由怎样累积成羁押、温柔如何与秘密缠在一起，以及一次听见很多却未必容得下这些话的制度访谈。":"三篇解讀：局部理由怎樣累積成羈押、溫柔如何與秘密纏在一起，以及一次聽見很多卻未必容得下這些話的制度訪談。","依据弗朗索瓦·特吕弗执导的一九五九年法国公映版《四百击》，黑白 Dyaliscope 宽银幕，片长约九十九分钟。法语片名来自 faire les quatre cents coups，意近“闯遍各种祸、胡闹个够”，不是字面上的四百次殴打。":"依據弗朗索瓦·特呂弗執導的一九五九年法國公映版《四百擊》，黑白 Dyaliscope 寬銀幕，片長約九十九分鐘。法語片名來自 faire les quatre cents coups，意近“闖遍各種禍、胡鬧個夠”，不是字面上的四百次毆打。","安托万坦白的回答同时抵抗美化与定罪；最后的定格把责任交给观众：不要再把一个孩子写成已经完成的案卷。":"安托萬坦白的回答同時抵抗美化與定罪；最後的定格把責任交給觀眾：不要再把一個孩子寫成已經完成的案卷。","弗朗索瓦·特吕弗不需要先证明安托万·杜瓦内无辜，才拒绝把他压缩成一个问题少年。三篇文章追踪包围他的处理链条、母亲温柔里的隐性交换，以及让影片拒绝结案的最后一眼。":"弗朗索瓦·特呂弗不需要先證明安托萬·杜瓦內無辜，才拒絕把他壓縮成一個問題少年。三篇文章追蹤包圍他的處理鏈條、母親溫柔裡的隱性交換，以及讓影片拒絕結案的最後一眼。","提问的人不出现":"提問的人不出現","母亲的奖励没有明说购买沉默；但温柔、金钱、作文名次与婚姻秘密同时到来，安托万很难安全地只接受其中一部分。":"母親的獎勵沒有明說購買沈默；但溫柔、金錢、作文名次與婚姻秘密同時到來，安托萬很難安全地只接受其中一部分。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle)
      ? variants[originalTitle]
      : originalTitle;

    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source)
        ? variants[source]
        : source;
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) {
      if (records.some(function(record) { return record.attributeName === 'data-lang'; })) {
        updateTraditionalReadingMode();
      }
    }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();

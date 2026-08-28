/* Generated offline from crime-punishment/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《罪与罚》常被概括成一个杀人犯因罪疚而自首、最终获得救赎的故事。但真正的起点更早：动手以前，拉斯柯尔尼科夫已经写好一套把人分为“普通”与“非凡”的理论。":"《罪與罰》常被概括成一個殺人犯因罪疚而自首、最終獲得救贖的故事。但真正的起點更早：動手以前，拉斯柯爾尼科夫已經寫好一套把人分為“普通”與“非凡”的理論。","《罪与罚》解读":"《罪與罰》解讀","他写过一篇论文":"他寫過一篇論文","先把索尼娅从“救赎男主角的圣女”位置上取下来，再看她自己的处境与选择。":"先把索尼婭從“救贖男主角的聖女”位置上取下來，再看她自己的處境與選擇。","四篇从拉斯柯尔尼科夫的论文与谋杀实验，读到算法之外的第二个人、被当作救赎工具的索尼娅，以及认输与认错之间漫长的距离。":"四篇從拉斯柯爾尼科夫的論文與謀殺實驗，讀到演算法之外的第二個人、被當作救贖工具的索尼婭，以及認輸與認錯之間漫長的距離。","每一套封闭的代价计算，都会遇到一个名单之外、现实之中的人。":"每一套封閉的代價計算，都會遇到一個名單之外、現實之中的人。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","自首可以接受刑罚，却仍完整保留那套让谋杀成为可能的人类分类。":"自首可以接受刑罰，卻仍完整保留那套讓謀殺成為可能的人類分類。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","认输，和认错":"認輸，和認錯","谋杀不是一套理论的结论，而是一场拿别人的命来确认自己等级的实验。":"謀殺不是一套理論的結論，而是一場拿別人的命來確認自己等級的實驗。","还有第二个人":"還有第二個人","这四篇追踪那套理论装不下的东西：计划之外的被害者、不断被别人派上用场的索尼娅，以及从行为上认输到真正放弃那张人类分类表之间的距离。":"這四篇追蹤那套理論裝不下的東西：計劃之外的被害者、不斷被別人派上用場的索尼婭，以及從行為上認輸到真正放棄那張人類分類表之間的距離。"};
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

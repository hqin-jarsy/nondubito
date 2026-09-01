/* Generated offline from essays/tv/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"八种语言":"八種語言","八种语言 · 电视剧解读":"八種語言 · 電視劇解讀","8 种语言":"8 種語言","12 篇 · 8 种语言":"12 篇 · 8 種語言","12 篇 · 8 种语言":"12 篇 · 8 種語言","Friends：为什么我们看了三十年还在看":"Friends：為什麼我們看了三十年還在看","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文章库":"← 文章庫","一个系列 · 十二篇 · 八种语言":"一個系列 · 十二篇 · 八種語言","一部情景喜剧为什么三十年不衰？答案不在剧情里，在人类的情感结构里。":"一部情景喜劇為什麼三十年不衰？答案不在劇情裡，在人類的情感結構裡。","情景喜剧":"情景喜劇","我们仍然共同生活其中的世界":"我們仍然共同生活其中的世界","电视剧以季与集展开，让人物、关系与制度在更长时间中显露结构。这里不做剧情复述，而是追踪人怎样被世界塑造、被彼此识认，又怎样改变自己的目的。":"電視劇以季與集展開，讓人物、關係與制度在更長時間中顯露結構。這裡不做劇情複述，而是追蹤人怎樣被世界塑造、被彼此識認，又怎樣改變自己的目的。","电视剧解读":"電視劇解讀","阅读系列":"閱讀系列","频道 · 电视剧细读":"頻道 · 電視劇細讀","12 篇 · 英 / 简 / 繁":"12 篇 · 英 / 簡 / 繁","《绝命毒师》：十二种读法":"《絕命毒師》：十二種讀法","两个系列 · 二十四篇 · 多语言阅读":"兩個系列 · 二十四篇 · 多語言閱讀","十二篇从被否认的价值、压不下去的道德余项与被夺走的叙事权，读到“必要代价”的名单，以及最后那句“我是为了我自己”。":"十二篇從被否認的價值、壓不下去的道德餘項與被奪走的敘事權，讀到“必要代價”的名單，以及最後那句“我是為了我自己”。","电视剧目录":"電視劇目錄","长故事与共同生活的世界":"長故事與共同生活的世界"};
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

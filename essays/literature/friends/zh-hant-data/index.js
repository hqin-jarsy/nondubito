/* Generated offline from Friends/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Friends：为什么我们看了三十年还在看":"Friends：為什麼我們看了三十年還在看","Friends：为什么我们看了三十年还在看 / Friends: Why We're Still Watching After Thirty Years — Non Dubito":"Friends：為什麼我們看了三十年還在看 / Friends: Why We're Still Watching After Thirty Years — Non Dubito","© 2026 Han Qin (秦汉). All rights reserved.":"© 2026 Han Qin (秦漢). All rights reserved.","“知道自己是谁”的人":"“知道自己是誰”的人","← 书架":"← 書架","　·　学术原文：":"　·　學術原文：","一部情景喜剧为什么能被看三十年——十二章，一章一个人物。":"一部情景喜劇為什麼能被看三十年——十二章，一章一個人物。","两个边缘人的二十年":"兩個邊緣人的二十年","为什么是这六个人":"為什麼是這六個人","为什么这段感情从来没有让人担心过":"為什麼這段感情從來沒有讓人擔心過","书架 ↗":"書架 ↗","从同一张桌子的两边到同一边":"從同一張桌子的兩邊到同一邊","全部系列见 ":"全部系列見 ","六个人":"六個人","十二篇 · 八种语言 · Han Qin (秦汉) · Non Dubito":"十二篇 · 八種語言 · Han Qin (秦漢) · Non Dubito","在所有碎片之上活着的人":"在所有碎片之上活著的人","用笑话把自己藏起来的人":"用笑話把自己藏起來的人","真的感情，不够的关系":"真的感情，不夠的關係","穿着婚纱的人":"穿著婚紗的人","站在阴影里的那个人":"站在陰影裡的那個人","那个看起来最简单的人":"那個看起來最簡單的人"};
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

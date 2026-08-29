/* Generated offline from essays/literature/the-trial/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《审判》解读":"《審判》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从无需监禁的法庭、越合理越深陷的应对、三种非无罪结局与一扇只为一人而开的门，重读卡夫卡的审判。":"四篇文章，從無需監禁的法庭、越合理越深陷的應對、三種非無罪結局與一扇只為一人而開的門，重讀卡夫卡的審判。","约瑟夫·K.被捕，却始终可以自由行动。他照常上班、穿过城市、聘请律师、寻找关系，又一次次靠自己的双脚进入法庭世界。这种自由不是制度的漏洞，而正是案件殖民他生活的机制。":"約瑟夫·K.被捕，卻始終可以自由行動。他照常上班、穿過城市、聘請律師、尋找關係，又一次次靠自己的雙腳進入法庭世界。這種自由不是制度的漏洞，而正是案件殖民他生活的機制。","四篇文章追踪一个未知指控如何被已知的应对义务取代。只要K.逐渐把自己组织成被告，法庭就不必真正证明罪名。":"四篇文章追蹤一個未知指控如何被已知的應對義務取代。只要K.逐漸把自己組織成被告，法庭就不必真正證明罪名。","弗兰茨·卡夫卡《审判》。全书剧透。":"法蘭茲·卡夫卡《審判》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","没有人押着他":"沒有人押著他","K.始终可以自由走动；法庭只需让他相信“自己有个案子”已是生活的中心事实。":"K.始終可以自由走動；法庭只需讓他相信“自己有個案子”已是生活的中心事實。","英 · 简 · 繁":"英 · 簡 · 繁","律师、关系与内部消息都像理性选择；每一步却让案件更真实，让其他生活更不真实。":"律師、關係與內部消息都像理性選擇；每一步卻讓案件更真實，讓其他生活更不真實。","三条路，没有一条通向结束":"三條路，沒有一條通向結束","提托莱里提出真正无罪、表面无罪与无限延期；只有第一条能结束案件，却没有现实先例。":"提托萊裡提出真正無罪、表面無罪與無限延期；只有第一條能結束案件，卻沒有現實先例。","那扇门一直开着":"那扇門一直開著","“在法的门前”那扇门只为一个人而设；等待授权却耗尽了他本可进入的一生。":"“在法的門前”那扇門只為一個人而設；等待授權卻耗盡了他本可進入的一生。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

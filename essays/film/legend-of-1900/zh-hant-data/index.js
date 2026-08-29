/* Generated offline from essays/film/legend-of-1900/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《海上钢琴师》解读":"《海上鋼琴師》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一个不在任何名册上的人，读到继承来的边界如何成为他所认领的世界，以及一段友谊怎样在不同意他的同时，仍把他郑重地保存下来。":"三篇從一個不在任何名冊上的人，讀到繼承來的邊界如何成為他所認領的世界，以及一段友誼怎樣在不同意他的同時，仍把他鄭重地保存下來。","《海上钢琴师》常被记作一则关于纯粹的寓言：一个钢琴师拒绝成名、交易与陆地。这三篇从更早的地方开始。在 1900 能够拒绝任何东西以前，他已经被发现、藏起、命名，并在弗吉尼亚号上长大。船既是他自由的条件，也是一个从来没有由他挑选的边界。":"《海上鋼琴師》常被記作一則關於純粹的寓言：一個鋼琴師拒絕成名、交易與陸地。這三篇從更早的地方開始。在 1900 能夠拒絕任何東西以前，他已經被發現、藏起、命名，並在維吉尼亞號上長大。船既是他自由的條件，也是一個從來沒有由他挑選的邊界。","三篇从纸面上的不存在，写到有限范围里的创造，再写到一个人如何被留下。它们追问：继承来的限制什么时候能成为自己的选择；为什么八十八个琴键反而比无限键盘更能容纳自由；以及麦克斯如何在不认同朋友最后决定的同时，仍把这个人的一生带到另一个人的听觉之中。":"三篇從紙面上的不存在，寫到有限範圍裡的創造，再寫到一個人如何被留下。它們追問：繼承來的限制什麼時候能成為自己的選擇；為什麼八十八個琴鍵反而比無限鍵盤更能容納自由；以及麥克斯如何在不認同朋友最後決定的同時，仍把這個人的一生帶到另一個人的聽覺之中。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他的边界，从一开始就不是他挑的":"他的邊界，從一開始就不是他挑的","在 1900 把船认作自己的世界以前，别人已经把他放在那里；只有钢琴，最初像是他自己走过去认领的东西。":"在 1900 把船認作自己的世界以前，別人已經把他放在那裡；只有鋼琴，最初像是他自己走過去認領的東西。","英 · 简 · 繁":"英 · 簡 · 繁","舷梯一边是有限的乐器，一边是无边的城市。他的解释完整而有力，却也恰好说明了那个继承来的边界。":"舷梯一邊是有限的樂器，一邊是無邊的城市。他的解釋完整而有力，卻也恰好說明了那個繼承來的邊界。","他最后做的那些事":"他最後做的那些事","1900 没有索取同意、贬低离开的人，也没有停止照顾麦克斯；麦克斯则用保存回应一个自己仍不认同的决定。":"1900 沒有索取同意、貶低離開的人，也沒有停止照顧麥克斯；麥克斯則用保存回應一個自己仍不認同的決定。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

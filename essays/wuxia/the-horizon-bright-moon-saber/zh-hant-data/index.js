/* Generated offline from essays/wuxia/the-horizon-bright-moon-saber/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 1 篇解读":"系列 · 1 篇解讀","《天涯·明月·刀》解读":"《天涯·明月·刀》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","一篇从燕南飞的面具与公子羽过早衰老的脸出发，读一个可以由别人穿上的名字，以及傅红雪为什么不必打败真正的公子羽，只需拒绝成为下一个他。":"一篇從燕南飛的面具與公子羽過早衰老的臉出發，讀一個可以由別人穿上的名字，以及傅紅雪為什麼不必打敗真正的公子羽，只需拒絕成為下一個他。","在这部后来的傅红雪故事里，最后的对手不只是一个武功更高的人，而是一个靠别人替自己露面、因此可以不断延续的位置。真正决定胜负的也不是杀掉藏在幕后的那个人，而是拒绝接过他的位置。":"在這部後來的傅紅雪故事裡，最後的對手不只是一個武功更高的人，而是一個靠別人替自己露面、因此可以不斷延續的位置。真正決定勝負的也不是殺掉藏在幕後的那個人，而是拒絕接過他的位置。","本文以古龙原著为准，不混用后来影视与游戏改编。全文包含结局剧透。":"本文以古龍原著為準，不混用後來影視與遊戲改編。全文包含結局劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","燕南飞替公子羽出面、战斗、接受名声；等面具下的位置再次空出来，傅红雪面对的是一份把人生配好用途的完整邀请。":"燕南飛替公子羽出面、戰鬥、接受名聲；等面具下的位置再次空出來，傅紅雪面對的是一份把人生配好用途的完整邀請。","英 · 简 · 繁":"英 · 簡 · 繁","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();

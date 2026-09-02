/* Generated offline from wuxia/white-horse-western-wind/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《白马啸西风》解读":"《白馬嘯西風》解讀","一篇读两句几乎相同的“不喜欢”：国王替所有人封住一座文化，李文秀只替自己说话，并让世界仍然完整。":"一篇讀兩句幾乎相同的“不喜歡”：國王替所有人封住一座文化，李文秀只替自己說話，並讓世界仍然完整。","偏不喜欢":"偏不喜歡","同样一句“不喜欢”，可以替所有人封门，也可以只说明自己要走哪条路。":"同樣一句“不喜歡”，可以替所有人封門，也可以只說明自己要走哪條路。","封闭的迷宫里没有黄金，只有一千年前被拒绝的一整套日常文化。寻宝的人无法想象：一样东西可以对别人有价值，却不必对自己有价值。":"封閉的迷宮裡沒有黃金，只有一千年前被拒絕的一整套日常文化。尋寶的人無法想象：一樣東西可以對別人有價值，卻不必對自己有價值。","李文秀结尾那句“不喜欢”用了近乎相同的语言，却拒绝把个人选择变成替别人封门的法。":"李文秀結尾那句“不喜歡”用了近乎相同的語言，卻拒絕把個人選擇變成替別人封門的法。","系列 · 1 篇解读":"系列 · 1 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁"};
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

/* Generated offline from essays/literature/the-outsider/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","《局外人》解读":"《異鄉人》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇文章，从一个没有哭的人、一场接管其“我”的审判，到“局外”边界究竟由谁划定。":"三篇文章，從一個沒有哭的人、一場接管其“我”的審判，到“局外”邊界究竟由誰划定。","默尔索杀了人，却在母亲葬礼的故事中受审。加缪精确地建造了这种错位：法庭需要一个可供谴责的人格，而默尔索拒绝使用让人格在社会中变得可读的常规语言。":"默爾索殺了人，卻在母親葬禮的故事中受審。加繆精確地建造了這種錯位：法庭需要一個可供譴責的人格，而默爾索拒絕使用讓人格在社會中變得可讀的常規語言。","三篇文章不把他改造成隐藏的圣人。它们追问：不表演意味着什么、法庭上谁拥有一个人的第一人称，以及他最后面对冷漠世界的时刻究竟是解放、放逐，还是两者兼有。":"三篇文章不把他改造成隱藏的聖人。它們追問：不表演意味著什麼、法庭上誰擁有一個人的第一人稱，以及他最後面對冷漠世界的時刻究竟是解放、放逐，還是兩者兼有。","阿尔贝·加缪《局外人》。全书剧透。":"阿爾貝·卡繆《異鄉人》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他没有哭":"他沒有哭","葬礼上，默尔索记录炎热、咖啡、疲惫与面孔；其他人却把没有眼泪变成没有感情。":"葬禮上，默爾索記錄炎熱、咖啡、疲憊與面孔；其他人卻把沒有眼淚變成沒有感情。","英 · 简 · 繁":"英 · 簡 · 繁","连他的“我”都被人接管了":"連他的“我”都被人接管了","庭审中，控辩双方都用一个可被道德叙述的人格，替换了默尔索自己的陈述。":"庭審中，控辯雙方都用一個可被道德敘述的人格，替換了默爾索自己的陳述。","谁在外面":"誰在外面","默尔索最后面对世界的冷漠，并未回答究竟是他站在社会之外，还是社会站在他的经验之外。":"默爾索最後面對世界的冷漠，並未回答究竟是他站在社會之外，還是社會站在他的經驗之外。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

/* Generated offline from legend-of-the-galactic-heroes/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《银河英雄传说》拒绝把好民主与坏专制放在一张方便的对照表上。它让腐败的共和制面对一位极其能干的皇帝，追问当现实绩效明显站在专制者一边时，我们还凭什么判断制度。":"《銀河英雄傳說》拒絕把好民主與壞專制放在一張方便的對照表上。它讓腐敗的共和制面對一位極其能幹的皇帝，追問當現實績效明顯站在專制者一邊時，我們還憑什麼判斷制度。","《银河英雄传说》解读":"《銀河英雄傳說》解讀","一个不肯拿的人":"一個不肯拿的人","一个有效率的英雄跨过了所有人默认不会跨过的线；专制通过上一套制度的合法程序到来。":"一個有效率的英雄跨過了所有人預設不會跨過的線；專制透過上一套制度的合法程式到來。","五篇从一条不成文的规矩与两种政治失败出发，读到能够说“不”的人、一次毫无产出的死亡，以及任何制度都必须面对的继承问题。":"五篇從一條不成文的規矩與兩種政治失敗出發，讀到能夠說“不”的人、一次毫無產出的死亡，以及任何制度都必須面對的繼承問題。","他死得什么也没证明":"他死得什麼也沒證明","同盟反复羞辱救过它的人；杨仍不夺权，因为他要保留公民自己犯错、也自己负责的位置。":"同盟反覆羞辱救過它的人；楊仍不奪權，因為他要保留公民自己犯錯、也自己負責的位置。","奥贝斯坦算战争的账，吉尔菲艾斯算新政权的账；反对二号人物的理论拆掉了莱因哈特最后的内部制动。":"奧貝斯坦算戰爭的賬，吉爾菲艾斯算新政權的賬；反對二號人物的理論拆掉了萊因哈特最後的內部制動。","如果那个最好的人不在了":"如果那個最好的人不在了","故事造出最好的指挥官，却不给他有意义的战死；留下的东西没有机构替它自动保存。":"故事造出最好的指揮官，卻不給他有意義的戰死；留下的東西沒有機構替它自動儲存。","禁止兼任的是一条不成文的规矩":"禁止兼任的是一條不成文的規矩","系列 · 5 篇解读":"系列 · 5 篇解讀","能拦住他的那个人":"能攔住他的那個人","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇不把故事写成莱因哈特与杨威利的能力比赛，而把它当作纠错、继承、责任，以及谁仍能对统治者说“不”的结构研究。以小说与完整OVA为文本；全文剧透。":"這五篇不把故事寫成萊因哈特與楊威利的能力比賽，而把它當作糾錯、繼承、責任，以及誰仍能對統治者說“不”的結構研究。以小說與完整OVA為文字；全文劇透。","鲁道夫、莱因哈特、同盟与伊谢尔伦给出四个都不完整的答案，面对继承、纠错与政治自由。":"魯道夫、萊因哈特、同盟與伊謝爾倫給出四個都不完整的答案，面對繼承、糾錯與政治自由。"};
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

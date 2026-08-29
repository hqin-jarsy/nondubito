/* Generated offline from essays/literature/rashomon-and-in-a-grove/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","《罗生门》与《竹林中》解读":"《羅生門》與《竹林中》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇文章，从作恶之前需要的说法、用供词重建的主体性，到互相冲突的故事之下仍未移动的事实。":"三篇文章，從作惡之前需要的說法、用供詞重建的主體性，到互相衝突的故事之下仍未移動的事實。","芥川龙之介的《罗生门》与《竹林中》是两篇不同的小说，后来因黑泽明的电影而在文化记忆中合流。并读它们，可以看见自我辩护的两个时刻：行动之前需要的一句话，以及行动之后编成的一段身份叙事。":"芥川龍之介的《羅生門》與《竹林中》是兩篇不同的小說，後來因黑澤明的電影而在文化記憶中合流。並讀它們，可以看見自我辯護的兩個時刻：行動之前需要的一句話，以及行動之後編成的一段身分敘事。","最后一篇也区分原作与电影：失踪的短刀使樵夫可疑，但小说没有确认他就是偷刀者；明确的自白来自黑泽明的改编。情节无法完全还原，并不等于所有事实都相对。":"最後一篇也區分原作與電影：失蹤的短刀使樵夫可疑，但小說沒有確認他就是偷刀者；明確的自白來自黑澤明的改編。情節無法完全還原，並不等於所有事實都相對。","芥川龙之介《罗生门》与《竹林中》。全书剧透。":"芥川龍之介《羅生門》與《竹林中》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他缺的不是胆子，是一个说法":"他缺的不是膽子，是一個說法","城门下的仆人已经准备作恶，却还缺一句能让自己在自身面前继续成立的话。":"城門下的僕人已經準備作惡，卻還缺一句能讓自己在自身面前繼續成立的話。","英 · 简 · 繁":"英 · 簡 · 繁","三个人都说是自己杀的":"三個人都說是自己殺的","强盗、妻子与死去的武士都认领死亡，因为每份供词都要修补一个受威胁的身份。":"強盜、妻子與死去的武士都認領死亡，因為每份供詞都要修補一個受威脅的身分。","有一样东西没有动":"有一樣東西沒有動","失踪的短刀留下疑点而非定案；在争议情节之下，死亡与侵犯仍是任何供词都抹不掉的事实。":"失蹤的短刀留下疑點而非定案；在爭議情節之下，死亡與侵犯仍是任何供詞都抹不掉的事實。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

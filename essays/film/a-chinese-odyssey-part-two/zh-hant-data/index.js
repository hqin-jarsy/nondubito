/* Generated offline from essays/film/a-chinese-odyssey-part-two/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《大话西游之大圣娶亲》解读":"《西遊記大結局之仙履奇緣》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从月光宝盒无法交还的生活，读到至尊宝怎样在极窄的选择中亲手戴上金箍，以及孙悟空怎样借城墙上的陌生人完成一次不署名、却也并非没有越界的修复。":"三篇從月光寶盒無法交還的生活，讀到至尊寶怎樣在極窄的選擇中親手戴上金剛圈，以及孫悟空怎樣借城牆上的陌生人完成一次不署名、卻也並非沒有越界的修復。","刘镇伟的《大话西游》把《西游记》神话改写成一场认错身份的喜剧，也改写成一场知道得太晚的悲剧。至尊宝并不是一个连续躲藏五百年的孙悟空。他是五百年后的转世，没有前世记忆，也就不可能一开始便把那个旧身份当成“我”。":"劉鎮偉的《西遊記》上下集把《西遊記》神話改寫成一場認錯身分的喜劇，也改寫成一場知道得太晚的悲劇。至尊寶並不是一個連續躲藏五百年的孫悟空。他是五百年後的轉世，沒有前世記憶，也就不可能一開始便把那個舊身分當成“我”。","三篇追踪的，是一份外来命运怎样逐渐变成他能够理解、回应并部分认领的命运。月光宝盒可以重新打开时间，却送不回他想要的普通生活；金箍由他亲手戴上，选择条件却早已被死亡、危险与责任压得很窄；城墙上的最后行动替陌生人补上了他自己的遗憾，它的温柔也不能自动取消对另一具身体的借用。":"三篇追蹤的，是一份外來命運怎樣逐漸變成他能夠理解、回應並部分認領的命運。月光寶盒可以重新打開時間，卻送不回他想要的普通生活；金剛圈由他親手戴上，選擇條件卻早已被死亡、危險與責任壓得很窄；城牆上的最後行動替陌生人補上了他自己的遺憾，它的溫柔也不能自動取消對另一具身體的借用。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","宝盒能倒转时间，却交还不了他想要的生活":"寶盒能倒轉時間，卻交還不了他想要的生活","月光宝盒能够重新打开一个时刻，却不能把至尊宝送回那段不断被命运移走的普通生活。":"月光寶盒能夠重新打開一個時刻，卻不能把至尊寶送回那段不斷被命運移走的普通生活。","英 · 简 · 繁":"英 · 簡 · 繁","那几步路是他自己走过去的":"那幾步路是他自己走過去的","金箍是他亲手戴上的，但死亡、危险与命运已经把他能够选择的路压得极窄。":"金剛圈是他親手戴上的，但死亡、危險與命運已經把他能夠選擇的路壓得極窄。","他好像一条狗":"他好像一條狗","城墙上的孙悟空不署名地修复一段陌生人的爱情，随后带着落在背影上的不体面评价继续西行。":"城牆上的孫悟空不署名地修復一段陌生人的愛情，隨後帶著落在背影上的不體面評價繼續西行。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

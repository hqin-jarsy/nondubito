/* Generated offline from never-let-me-go/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《别让我走》从凯茜·H的回忆展开：黑尔舍姆、露丝与汤米，以及一个能够承认他们有内心、却仍然继续使用他们身体的世界。":"《別讓我走》從凱茜·H的回憶展開：黑爾舍姆、露絲與湯米，以及一個能夠承認他們有內心、卻仍然繼續使用他們身體的世界。","《别让我走》解读":"《別讓我走》解讀","一所很好的学校":"一所很好的學校","三篇文章从“一所很好的学校”开始，经过被划定上限的希望，最后走到凯茜与汤米唯一知道的那扇门后。":"三篇文章從“一所很好的學校”開始，經過被劃定上限的希望，最後走到凱茜與湯米唯一知道的那扇門後。","八种语言":"八種語言","八种语言 · 文学解读":"八種語言 · 文學解讀","八种语言 · 石黑一雄":"八種語言 · 石黑一雄","到了村舍，围墙消失了，逃跑却从未成为计划。最深的边界，是一个人对人生可能性的想象边界。":"到了村舍，圍牆消失了，逃跑卻從未成為計劃。最深的邊界，是一個人對人生可能性的想象邊界。","剧透提示：":"劇透提示：","本系列涉及小说核心设定与重要情节。":"本系列涉及小說核心設定與重要情節。","画廊问错了问题，夫人看见的是象征而不是女孩；那扇唯一知道的门，最终开向空无。":"畫廊問錯了問題，夫人看見的是象徵而不是女孩；那扇唯一知道的門，最終開向空無。","石黑一雄写了一群被悉心照顾、也被彻底排除在自身命运之外的人。三篇解读追问：善意如何与使用共存，希望如何被预先限缩，以及，一个人有没有被当成人，究竟应当由什么来判断。":"石黑一雄寫了一群被悉心照顧、也被徹底排除在自身命運之外的人。三篇解讀追問：善意如何與使用共存，希望如何被預先限縮，以及，一個人有沒有被當成人，究竟應當由什麼來判斷。","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","门后面是空的":"門後面是空的","黑尔舍姆温暖、体面、富有善意。也正因如此，它揭示了一种无法只用残忍来解释的伤害。":"黑爾舍姆溫暖、體面、富有善意。也正因如此，它揭示了一種無法只用殘忍來解釋的傷害。"};
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

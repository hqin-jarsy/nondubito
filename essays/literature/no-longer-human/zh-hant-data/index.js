/* Generated offline from essays/literature/no-longer-human/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《人间失格》解读":"《人間失格》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从表演、被动、被侵犯的信任与框架叙事，重读“人间失格”究竟是谁的判决。":"四篇文章，從表演、被動、被侵犯的信任與框架敘事，重讀“人間失格”究竟是誰的判決。","大庭叶藏把自己的一生写成一份判决已经作出的证词：他没有资格做人。但小说把这份自白放在其他声音之中。问题不在于他的痛苦是否真诚，而在于真诚是否足以让他的解释成为终审。":"大庭葉藏把自己的一生寫成一份判決已經作出的證詞：他沒有資格做人。但小說把這份自白放在其他聲音之中。問題不在於他的痛苦是否真誠，而在於真誠是否足以讓他的解釋成為終審。","四篇文章依次讨论叶藏如何用表演在人群中活下去、如何逃避决定、良子受害之后他怎样倒置了罪责，以及框架叙事为何在最后给出另一份证词。":"四篇文章依次討論葉藏如何用表演在人群中活下去、如何逃避決定、良子受害之後他怎樣倒置了罪責，以及框架敘事為何在最後給出另一份證詞。","太宰治《人间失格》。全书剧透。":"太宰治《人間失格》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他从小就在演":"他從小就在演","叶藏的滑稽并非性格，而是一套用来应付他无法理解之人群的生存技术。":"葉藏的滑稽並非性格，而是一套用來應付他無法理解之人群的生存技術。","英 · 简 · 繁":"英 · 簡 · 繁","他一件事也没有决定过":"他一件事也沒有決定過","情节不断经过叶藏发生，而他把一次次随波逐流叙述成命运。":"情節不斷經過葉藏發生，而他把一次次隨波逐流敘述成命運。","天真的信任是一种罪吗":"天真的信任是一種罪嗎","良子受害之后，叶藏把她的信任当成缺陷，又把别人的伤害转换成关于自己的证据。":"良子受害之後，葉藏把她的信任當成缺陷，又把別人的傷害轉換成關於自己的證據。","最后一句话不是他说的":"最後一句話不是他說的","小说在叶藏的自白之外结束：另一位见证者在他只写下失格之处，记得一个“天使”。":"小說在葉藏的自白之外結束：另一位見證者在他只寫下失格之處，記得一個“天使”。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

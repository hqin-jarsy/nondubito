/* Generated offline from wuxia/heaven-sword-dragon-saber/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《倚天屠龙记》解读":"《倚天屠龍記》解讀","五篇从空见以命截断却反而加长的复仇链出发，读武当山上的交代、灭绝的有条件原谅、张无忌不能见死不救，以及朱元璋如何让他自己离开。":"五篇從空見以命截斷卻反而加長的復仇鏈出發，讀武當山上的交代、滅絕的有條件原諒、張無忌不能見死不救，以及朱元璋如何讓他自己離開。","张无忌得到的每个位置都由别人塞来；他答应，只因无法看着眼前的人死。":"張無忌得到的每個位置都由別人塞來；他答應，只因無法看著眼前的人死。","故事中心的张无忌一次次被推上位置，只因为他无法看着眼前的人死去。这五篇追问这份不能不救得下什么、管不了什么，以及制度怎样学会利用它。":"故事中心的張無忌一次次被推上位置，只因為他無法看著眼前的人死去。這五篇追問這份不能不救得下什麼、管不了什麼，以及制度怎樣學會利用它。","朱元璋不必证明一件事是真的，只需让张无忌再也不想留在那个位置。":"朱元璋不必證明一件事是真的，只需讓張無忌再也不想留在那個位置。","武当山":"武當山","每一方都有资格要交代；被这些道理压死的人却不在任何一方的账里。":"每一方都有資格要交代；被這些道理壓死的人卻不在任何一方的賬裡。","灭绝":"滅絕","灭绝给出的原谅总有完整条件：过去可以勾销，未来必须照她的法去做。":"滅絕給出的原諒總有完整條件：過去可以勾銷，未來必須照她的法去做。","画眉":"畫眉","空见":"空見","空见想用自己的命截断复仇，结果却给那条链子添上了最重的一环。":"空見想用自己的命截斷復仇，結果卻給那條鏈子添上了最重的一環。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这是一部被门派、誓言、神兵、政治派别与继承来的伤害填满的小说。几乎每个人出场时，都带着一笔要别人偿还的账。":"這是一部被門派、誓言、神兵、政治派別與繼承來的傷害填滿的小說。幾乎每個人出場時，都帶著一筆要別人償還的賬。"};
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

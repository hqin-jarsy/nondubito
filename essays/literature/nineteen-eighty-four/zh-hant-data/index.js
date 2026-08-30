/* Generated offline from essays/literature/nineteen-eighty-four/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"八种语言":"八種語言","八种语言 · 作品解读":"八種語言 · 作品解讀","← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《一九八四》解读":"《一九八四》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从删词、私人生活、奥勃良与一篇过去时附录，重读权力如何进入语言、记忆、爱与判断。":"四篇文章，從刪詞、私人生活、奧勃良與一篇過去時附錄，重讀權力如何進入語言、記憶、愛與判斷。","我们太容易把这部小说读成一套政治词汇：老大哥、双重思想、101号房。这个系列把这些词重新放回被它们损害的生活：一个政权不只控制人的行为，还要让人失去命名、保存和相信自身经验的能力。":"我們太容易把這部小說讀成一套政治詞彙：老大哥、雙重思想、101號房。這個系列把這些詞重新放回被它們損害的生活：一個政權不只控制人的行為，還要讓人失去命名、保存和相信自身經驗的能力。","四篇文章依次从语言走向私人生活，再走进判断本身。最后一篇讨论附录的过去时：它是一条重要的形式线索，但不是一份足以单独证明大洋国结局的历史档案。":"四篇文章依次從語言走向私人生活，再走進判斷本身。最後一篇討論附錄的過去時：它是一條重要的形式線索，但不是一份足以單獨證明大洋國結局的歷史檔案。","乔治·奥威尔《一九八四》。全书剧透。":"喬治·歐威爾《一九八四》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他们在删词":"他們在刪詞","新话不只是禁止异议；它删除的，是一个人作出独立判断所需的差异。":"新話不只是禁止異議；它刪除的，是一個人作出獨立判斷所需的差異。","英 · 简 · 繁":"英 · 簡 · 繁","他们要的东西小得不像话":"他們要的東西小得不像話","一间房、真正的咖啡、口红与玻璃镇纸，证明生活可以超出政治功能。":"一間房、真正的咖啡、口紅與玻璃鎮紙，證明生活可以超出政治功能。","他不是来惩罚他的":"他不是來懲罰他的","奥勃良要的不是温斯顿服从，而是让他把党的判断体验成自己的判断。":"奧勃良要的不是溫斯頓服從，而是讓他把黨的判斷體驗成自己的判斷。","那篇附录用的是过去时":"那篇附錄用的是過去時","附录或许把大洋国放进了回望之中；但语法给出的是形式线索，不是政权覆灭的确证。":"附錄或許把大洋國放進了回望之中；但語法給出的是形式線索，不是政權覆滅的確證。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

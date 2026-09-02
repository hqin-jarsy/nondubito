/* Generated offline from wuxia/legends-of-the-condor-heroes/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《射雕英雄传》解读":"《射鵰英雄傳》解讀","两个孩子还没有出生，名字、师父与十八年后的任务已经替他们备好。":"兩個孩子還沒有出生，名字、師父與十八年後的任務已經替他們備好。","五篇从一场拿未出生孩子作赌注的约定出发，读杨康的名字、桃花岛唯一的立法者、被当作棋子的婴儿，以及大汗临终前没有答案的英雄之问。":"五篇從一場拿未出生孩子作賭注的約定出發，讀楊康的名字、桃花島唯一的立法者、被當作棋子的嬰兒，以及大汗臨終前沒有答案的英雄之問。","大汗给郭靖的喜爱与赏赐都是真的；最后，他问自己究竟算不算英雄。":"大汗給郭靖的喜愛與賞賜都是真的；最後，他問自己究竟算不算英雄。","揭开杨康身世的人，同时要求他把十八年立刻退回去。":"揭開楊康身世的人，同時要求他把十八年立刻退回去。","桃花岛":"桃花島","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","裘千仞把婴儿当作棋子；四个大人的余生从那个下午重新开始。":"裘千仞把嬰兒當作棋子；四個大人的餘生從那個下午重新開始。","赌约":"賭約","这五篇不否定忠义、教导与英雄，只追问一份真实的给予何时开始索取整个人生，以及拒绝时究竟要付出什么。":"這五篇不否定忠義、教導與英雄，只追問一份真實的給予何時開始索取整個人生，以及拒絕時究竟要付出什麼。","郭靖与杨康能够选择以前，名字、师父、国家与祖辈的战争已经替他们选择了很多。小说里最著名的成长故事，同时也是大人在孩子身上放置要求的故事。":"郭靖與楊康能夠選擇以前，名字、師父、國家與祖輩的戰爭已經替他們選擇了很多。小說裡最著名的成長故事，同時也是大人在孩子身上放置要求的故事。","黄药师不受天下规矩约束，他的弟子却只能受他一个人的规矩约束。":"黃藥師不受天下規矩約束，他的弟子卻只能受他一個人的規矩約束。"};
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

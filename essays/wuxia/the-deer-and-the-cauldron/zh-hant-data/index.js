/* Generated offline from wuxia/the-deer-and-the-cauldron/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《鹿鼎记》解读":"《鹿鼎記》解讀","一份当场令人舒服、明年必须回来续领的赏赐，写出了控制的完整形状。":"一份當場令人舒服、明年必須回來續領的賞賜，寫出了控制的完整形狀。","丽春院":"麗春院","五篇从韦小宝那条只有一句话的规矩出发，读一份写好的差事、皇帝唯一的朋友、复国尚未成形便已分配的江山，以及每年都要续领的赏赐。":"五篇從韋小寶那條只有一句話的規矩出發，讀一份寫好的差事、皇帝唯一的朋友、復國尚未成形便已分配的江山，以及每年都要續領的賞賜。","反清复明":"反清復明","总舵主":"總舵主","皇帝唯一一段不是用身份换来的交情，终究无法逃出皇位的形状。":"皇帝唯一一段不是用身份換來的交情，終究無法逃出皇位的形狀。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","要恢复的江山还没有影子，名分下面的位置却早已开始分配。":"要恢復的江山還沒有影子，名分下面的位置卻早已開始分配。","这五篇把喜剧当真来读：一条自己的规矩边界在哪里，一份继承来的使命怎样对待最忠实的执行者，以及退出怎样能保住一个人，却未必修好身后的世界。":"這五篇把喜劇當真來讀：一條自己的規矩邊界在哪裡，一份繼承來的使命怎樣對待最忠實的執行者，以及退出怎樣能保住一個人，卻未必修好身後的世界。","金庸的最后一部长篇从内部掏空了英雄叙事：主角不会武功，忠臣还没复国便争起名分，最有能力的皇帝则不得不把友谊变成统治的一部分。":"金庸的最後一部長篇從內部掏空了英雄敘事：主角不會武功，忠臣還沒復國便爭起名分，最有能力的皇帝則不得不把友誼變成統治的一部分。","陈近南把一份继承来的差事办到底，那份差事从来没有替他留下位置。":"陳近南把一份繼承來的差事辦到底，那份差事從來沒有替他留下位置。","韦小宝守住了自己捡来的规矩；这条规矩的边界，也把许多人留在了外面。":"韋小寶守住了自己撿來的規矩；這條規矩的邊界，也把許多人留在了外面。"};
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

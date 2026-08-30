/* Generated offline from essays/literature/the-count-of-monte-cristo/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《基督山伯爵》解读":"《基督山伯爵》解讀","五篇文章，从一封告密信的责任链、法利亚神甫的教育、被设计的复仇，到那个无辜的孩子，以及最后的等待与希望。":"五篇文章，從一封告密信的責任鏈、法利亞神甫的教育、被設計的復仇，到那個無辜的孩子，以及最後的等待與希望。","他不给任何人加什么":"他不給任何人加什麼","伯爵声称自己只是让既有的恶显现；但安排别人堕落的条件，本身就已经是介入。":"伯爵聲稱自己只是讓既有的惡顯現；但安排別人墮落的條件，本身就已經是介入。","四个人和一封信":"四個人和一封信","大仲马《基督山伯爵》，一八四四至一八四六年连载。全书剧透。":"大仲馬《基督山伯爵》，一八四四至一八四六年連載。全書劇透。","大仲马把复仇写成了一套制度：金钱、信息、身份、法律与社会欲望全都成为工具。这组文章不只问唐泰斯的仇人是否该受惩罚，也问一个受害者取得安排所有人后果的权力之后，会站到什么位置。":"大仲馬把復仇寫成了一套制度：金錢、資訊、身份、法律與社會慾望全都成為工具。這組文章不只問唐泰斯的仇人是否該受懲罰，也問一個受害者取得安排所有人後果的權力之後，會站到什麼位置。","法利亚神甫做的事":"法利亞神甫做的事","法利亚神甫给唐泰斯的首先不是宝藏，而是教育、因果上的清晰、精神自由，以及一项他没有接受的警告。":"法利亞神甫給唐泰斯的首先不是寶藏，而是教育、因果上的清晰、精神自由，以及一項他沒有接受的警告。","爱德华的死击破了伯爵代行天意的自我理解，也显出任何人类正义账本的界限。":"愛德華的死擊破了伯爵代行天意的自我理解，也顯出任何人類正義賬本的界限。","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","美茜蒂丝与海黛作出了伯爵没有设计的行动，而最后的等待与希望，也给他安排未来的权力划下界限。":"美茜蒂絲與海黛作出了伯爵沒有設計的行動，而最後的等待與希望，也給他安排未來的權力劃下界限。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","邓格拉尔写，费尔南寄，卡德鲁斯旁观，维尔福明知无辜仍把诬告变成国家暴力。":"鄧格拉爾寫，費爾南寄，卡德魯斯旁觀，維爾福明知無辜仍把誣告變成國家暴力。","那个孩子":"那個孩子"};
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

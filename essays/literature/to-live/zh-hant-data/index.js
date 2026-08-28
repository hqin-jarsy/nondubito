/* Generated offline from to-live/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《活着》解读":"《活著》解讀","书里最彻底的看见，都发生在给的人一无所有时；它们没有救成任何人，却不能因此被抹去。":"書裡最徹底的看見，都發生在給的人一無所有時；它們沒有救成任何人，卻不能因此被抹去。","从外面看，福贵是历史的幸存者；从他自己的位置看，那是他的生活。第一人称守住了主语。":"從外面看，福貴是歷史的倖存者；從他自己的位置看，那是他的生活。第一人稱守住了主語。","余华让福贵从一个败光家产的浪荡子，走过战争、运动、饥荒和一家人的相继离世。四篇解读拒绝把这一生变成“苦难使人高贵”的教材，也不把他变成时代控诉的证物。":"余華讓福貴從一個敗光家產的浪蕩子，走過戰爭、運動、饑荒和一家人的相繼離世。四篇解讀拒絕把這一生變成“苦難使人高貴”的教材，也不把他變成時代控訴的證物。","剧透提示：":"劇透提示：","四篇解读追问：《活着》为何拒绝让苦难兑换崇高，人怎样被用途消耗，没有回报的看见为何仍然成立，以及福贵为何必须亲口讲完自己的生活。":"四篇解讀追問：《活著》為何拒絕讓苦難兌換崇高，人怎樣被用途消耗，沒有回報的看見為何仍然成立，以及福貴為何必須親口講完自己的生活。","最可怕的结构未必需要恶人：它只需要一条人人尽责的链，以及链尾一个被缩成用途的人。":"最可怕的結構未必需要惡人：它只需要一條人人盡責的鏈，以及鏈尾一個被縮成用途的人。","本系列涉及小说全部情节，并以小说文本而非一九九四年电影版为依据。":"本系列涉及小說全部情節，並以小說文本而非一九九四年電影版為依據。","没有恶人，只有用途":"沒有惡人，只有用途","生活，还是幸存":"生活，還是倖存","福贵变好之后，失去的反而更多。《活着》的硬度，始于它拒绝让苦难成为交换。":"福貴變好之後，失去的反而更多。《活著》的硬度，始於它拒絕讓苦難成為交換。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","系列从苦难不兑换任何东西写起，经过人如何被系统换算成用途，走到那些没有改变结果的识认时刻；最后回到小说的人称与倾听，追问“生活”与“幸存”的差别。":"系列從苦難不兌換任何東西寫起，經過人如何被系統換算成用途，走到那些沒有改變結果的識認時刻；最後回到小說的人稱與傾聽，追問“生活”與“倖存”的差別。","给的人都一无所有":"給的人都一無所有","苦难什么也不换":"苦難什麼也不換","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 文学解读":"英文 · 簡 / 繁 · 文學解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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

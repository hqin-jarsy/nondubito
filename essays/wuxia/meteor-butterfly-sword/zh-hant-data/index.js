/* Generated offline from essays/wuxia/meteor-butterfly-sword/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 3 篇解读":"系列 · 3 篇解讀","《流星·蝴蝶·剑》解读":"《流星·蝴蝶·劍》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","三篇从半个冷馒头、孙府这本大账与被逐出家门的小蝶出发，读孟星魂如何从一笔救命之恩里取回自己的人生，也读一个把所有人都算进去的江湖为何仍会留下算不尽的人。":"三篇從半個冷饅頭、孫府這本大賬與被逐出家門的小蝶出發，讀孟星魂如何從一筆救命之恩裡取回自己的人生，也讀一個把所有人都算進去的江湖為何仍會留下算不盡的人。","《流星·蝴蝶·剑》表面是武侠，骨架却更像一部帮派史：孙府、十二飞鹏帮与快活林各有地盘、人手、账目和内应。几乎每个人对别人都有用，而这份“有用”很少是无害的。":"《流星·蝴蝶·劍》表面是武俠，骨架卻更像一部幫派史：孫府、十二飛鵬幫與快活林各有地盤、人手、賬目和內應。幾乎每個人對別人都有用，而這份“有用”很少是無害的。","古龙真正写得锋利的，是人开始无法继续充当原定用途的时刻：杀手每次杀人后都会呕吐，当家人越会用人越难分辨忠诚，被逐出家门的女儿则遇到一个不要求她删掉过去的人。这三篇就从这些裂口进入。全文包含结局剧透。":"古龍真正寫得鋒利的，是人開始無法繼續充當原定用途的時刻：殺手每次殺人後都會嘔吐，當家人越會用人越難分辨忠誠，被逐出家門的女兒則遇到一個不要求她刪掉過去的人。這三篇就從這些裂口進入。全文包含結局劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","半个馒头":"半個饅頭","孟星魂六岁时，高老大递来半个又冷又硬的馒头。救命是真的，后来以报恩之名索取的一生也是真的；最难解的债，正是债主确实救过你的命。":"孟星魂六歲時，高老大遞來半個又冷又硬的饅頭。救命是真的，後來以報恩之名索取的一生也是真的；最難解的債，正是債主確實救過你的命。","英 · 简 · 繁":"英 · 簡 · 繁","老伯的账":"老伯的賬","孙玉伯不只是一家之长，也是龙门帮与孙府的中心。他最会看人、用人和承担损失；可当每个人都被放进护住孙府的账里，忠诚本身也会开始变形。":"孫玉伯不只是一家之長，也是龍門幫與孫府的中心。他最會看人、用人和承擔損失；可當每個人都被放進護住孫府的賬裡，忠誠本身也會開始變形。","律香川的暴力没有把小蝶变成一个情节说明，父亲的驱逐也没有决定她此后是谁。孟星魂真正给她的，不是替她清除过去，而是接受她和孩子一起到来。":"律香川的暴力沒有把小蝶變成一個情節說明，父親的驅逐也沒有決定她此後是誰。孟星魂真正給她的，不是替她清除過去，而是接受她和孩子一起到來。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();

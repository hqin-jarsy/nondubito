/* Generated offline from law/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉) · 五篇 · 八种语言":"Han Qin (秦漢) · 五篇 · 八種語言","© 2026 Han Qin (秦汉). All rights reserved.":"© 2026 Han Qin (秦漢). All rights reserved.","← 书架":"← 書架","　·　学术原文：":"　·　學術原文：","与西方法理学的后验对照":"與西方法理學的後驗對照","两人法的三个余项推动地基从情转为共同身份，并使身份定义权、counter法、追问代表、透明度与递归出现。":"兩人法的三個餘項推動地基從情轉為共同身份，並使身份定義權、counter法、追問代表、透明度與遞迴出現。","书架 ↗":"書架 ↗","从 14DD 对赌到星际收束：法的先验推导。两个 14DD 相遇，自然状态是对赌——法就是从这里长出来的。四篇正传 + 一篇后续篇 · 八种语言。":"從 14DD 對賭到星際收束：法的先驗推導。兩個 14DD 相遇，自然狀態是對賭——法就是從這裡長出來的。四篇正傳 + 一篇後續篇 · 八種語言。","从两个 14DD 的对赌推出法的四条 base layer、13DD–14DD 射程、两种法形态、三条结构边界与穿透原则。":"從兩個 14DD 的對賭推出法的四條 base layer、13DD–14DD 射程、兩種法形態、三條結構邊界與穿透原則。","以艾泽拉斯作反面思想实验，说明国家尺度的退出成本、法的厚度，以及多权分立作为 BL4 的最小闭环。":"以艾澤拉斯作反面思想實驗，說明國家尺度的退出成本、法的厚度，以及多權分立作為 BL4 的最小閉環。","全部系列见 ":"全部系列見 ","后续篇":"後續篇","国家法——艾泽拉斯":"國家法——艾澤拉斯","在内部推导完成后，与霍布斯、哈特、富勒、拉兹、霍菲尔德及社会契约论逐一对接，标出收敛与分叉。":"在內部推導完成後，與霍布斯、哈特、富勒、拉茲、霍菲爾德及社會契約論逐一對接，標出收斂與分叉。","当距离恢复退出权，强制法退场而薄协议留下；法的厚度从两人、群体、国家到星际完成拓扑回归。":"當距離恢復退出權，強制法退場而薄協議留下；法的厚度從兩人、群體、國家到星際完成拓撲迴歸。","星际法与总收束——Coercive Law的退场":"星際法與總收束——Coercive Law的退場","法学系列":"法學系列","法学系列 / Law Series — Non Dubito":"法學系列 / Law Series — Non Dubito","群体法——从情到共同身份":"群體法——從情到共同身份"};
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

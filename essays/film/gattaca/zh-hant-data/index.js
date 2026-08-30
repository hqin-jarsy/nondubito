/* Generated offline from essays/film/gattaca/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《千钧一发》解读":"《千鈞一髮》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一段在生命开始以前便写好的摘要，读到“不合格”梦想者与基因精英运动员的相互交换，以及两个目的地不同的兄弟之间最后一次游泳。":"三篇從一段在生命開始以前便寫好的摘要，讀到“不合格”夢想者與基因精英運動員的相互交換，以及兩個目的地不同的兄弟之間最後一次游泳。","《千钧一发》常被概括为反对基因决定论，它更细的一点在于：预测不必是假的，也可能变成压迫。文森特的心脏确实危险；当机构把群体层面的概率当成一个具体人的完整传记时，概率才成为支配。":"《千鈞一髮》常被概括為反對基因決定論，它更細的一點在於：預測不必是假的，也可能變成壓迫。文森特的心臟確實危險；當機構把群體層面的概率當成一個具體人的完整傳記時，概率才成為支配。","电影把他与杰罗姆·莫罗放在一起：后者拥有经过设计的优秀，却承受不了第二名。两人各自拥有一种无法单独使用的东西，他们的安排同时暴露身体的力量与单一排名尺度的暴力。":"電影把他與傑羅姆·莫羅放在一起：後者擁有經過設計的優秀，卻承受不了第二名。兩人各自擁有一種無法單獨使用的東西，他們的安排同時暴露身體的力量與單一排名尺度的暴力。","安德鲁·尼科尔一九九七年《千钧一发》。全片剧透。":"安德魯·尼科爾一九九七年《千鈞一髮》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他还没有名字，一生已经有了摘要":"他還沒有名字，一生已經有了摘要","文森特的基因报告可能真实描述风险；当概率替代相遇、机构把分布当成人时，它才开始施加暴力。":"文森特的基因報告可能真實描述風險；當概率替代相遇、機構把分布當成人時，它才開始施加暴力。","英 · 简 · 繁":"英 · 簡 · 繁","一个完美的人和一个不合格的人，各拿走对方一半":"一個完美的人和一個不合格的人，各拿走對方一半","文森特借用杰罗姆的基因身份，杰罗姆借用文森特的计划；这场欺骗因此不只是单向利用，而是目的的互相搭建。":"文森特借用傑羅姆的基因身分，傑羅姆借用文森特的計畫；這場欺騙因此不只是單向利用，而是目的的互相搭建。","他们不在同一把尺子上":"他們不在同一把尺子上","安东游泳是为了返回并确认排名，文森特则游向那个测量他的岸之外；两人的比赛只在表面上相同。":"安東游泳是為了返回並確認排名，文森特則游向那個測量他的岸之外；兩人的比賽只在表面上相同。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

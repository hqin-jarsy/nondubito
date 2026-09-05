/* Generated offline from essays/film/manchester-by-the-sea/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《海边的曼彻斯特》解读":"《海邊的曼徹斯特》解讀","三篇解读：一份无法解决悲伤的遗嘱、一个法律没有起诉却曾被想起的风险，以及“我过不去”之后仍然可能的有限照料。":"三篇解讀：一份無法解決悲傷的遺囑、一個法律沒有起訴卻曾被想起的風險，以及“我過不去”之後仍然可能的有限照料。","乔精心安排监护，认出了李仍有照料能力，却无法给回到孩子死去的小镇所需的代价定价，更无法把它移除。":"喬精心安排監護，認出了李仍有照料能力，卻無法給回到孩子死去的小鎮所需的代價定價，更無法把它移除。","他说他过不去，然后留了一间多的房间":"他說他過不去，然後留了一間多的房間","依据肯尼斯·罗纳根编剧并执导的二〇一六年电影《海边的曼彻斯特》。火灾经过依李在片中笔录时的陈述：他走到半路想起没有装回壁炉挡火板，却判断大概不会出事并继续前行。":"依據肯尼斯·羅納根編劇並執導的二〇一六年電影《海邊的曼徹斯特》。火災經過依李在片中筆錄時的陳述：他走到半路想起沒有裝回壁爐擋火板，卻判斷大概不會出事並繼續前行。","兰迪的道歉不是治愈，李的限度也不等于抛弃；修好的船与多留的房间，让照料得以延续，却不假装已经赎清。":"蘭迪的道歉不是治癒，李的限度也不等於拋棄；修好的船與多留的房間，讓照料得以延續，卻不假裝已經贖清。","李半路想起没装挡火板却继续走；当官方把结果定为可怕错误而非犯罪，惩罚便转向了内部。":"李半路想起沒裝擋火板卻繼續走；當官方把結果定為可怕錯誤而非犯罪，懲罰便轉向了內部。","没有人起诉他，所以他给自己判刑":"沒有人起訴他，所以他給自己判刑","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","肯尼斯·罗纳根拒绝把悲伤变成有用的成长材料。三篇文章区分犯罪与因果责任、原谅与治愈，也区分彻底恢复与一个受损的人仍能为他者做出的具体行动。":"肯尼斯·羅納根拒絕把悲傷變成有用的成長材料。三篇文章區分犯罪與因果責任、原諒與治癒，也區分徹底恢復與一個受損的人仍能為他者做出的具體行動。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那份遗嘱不能让他回来":"那份遺囑不能讓他回來"};
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

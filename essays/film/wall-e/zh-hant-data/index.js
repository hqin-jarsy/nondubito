/* Generated offline from essays/film/wall-e/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《机器人总动员》解读":"《瓦力》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一个在指定功能之外形成偏好的机器人，读到另一个机器人怎样在一段回放里看见照料，以及一株穿过许多系统、却始终没有停止活着的植物。":"三篇從一個在指定功能之外形成偏好的機器人，讀到另一個機器人怎樣在一段回放裡看見照料，以及一株穿過許多系統、卻始終沒有停止活著的植物。","《机器人总动员》常被概括成消费主义寓言，或者两个机器人的爱情故事。这两种说法都对，也都不够。电影更深的一层运动，是编号怎样成为名字，指令怎样容纳判断，以及一个生物样本怎样重新成为必须由具体生命维持下去的东西。":"《瓦力》常被概括成消費主義寓言，或者兩個機器人的愛情故事。這兩種說法都對，也都不夠。電影更深的一層運動，是編號怎樣成為名字，指令怎樣容納判斷，以及一個生物樣本怎樣重新成為必須由具體生命維持下去的東西。","三篇从瓦力在七百年工作之后留下的物件开始，沿着伊芙怎样被一段记录改变，再抵达那只鞋里的植物。它们共同追问：偏好如何在功能旁边出现；关系怎样重新排列任务，却不必取消公共目的；以及为什么照料可以早于用途的知识。":"三篇從瓦力在七百年工作之後留下的物件開始，沿著伊芙怎樣被一段記錄改變，再抵達靴子裡的植物。它們共同追問：偏好如何在功能旁邊出現；關係怎樣重新排列任務，卻不必取消公共目的；以及為什麼照料可以早於用途的知識。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他每天下班以后，做一些不换任何东西的事":"他每天下班以後，做一些不換任何東西的事","瓦力仍然压缩垃圾，却按工作规格从未提供的标准，留下叉勺、戒指盒与打火机。":"瓦力仍然壓縮垃圾，卻按工作規格從未提供的標準，留下叉匙、戒指盒與打火機。","英 · 简 · 繁":"英 · 簡 · 繁","她看见了那段回放以后":"她看見了那段回放以後","伊芙原本就有好奇；回放带给她的是另一件事——看见一份发生在自己无法知觉、也无法回应之时的照料。":"伊芙原本就有好奇；回放帶給她的是另一件事——看見一份發生在自己無法知覺、也無法回應之時的照料。","那只鞋里的植物":"靴子裡的植物","对飞船，植物是信号；对 AUTO，它是被禁止的输入；对舰长，它最后成了承担一个受损世界的理由。":"對太空船，植物是信號；對 AUTO，它是被禁止的輸入；對艦長，它最後成了承擔一個受損世界的理由。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

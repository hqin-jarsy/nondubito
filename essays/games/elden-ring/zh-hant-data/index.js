/* Generated offline from essays/games/elden-ring/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《艾尔登法环》把自己的论证散在道具说明、废墟、重复机制与彼此冲突的人物说法里。四篇尽量把明示事实与推断分开，同时追问一条贯穿全作的问题：当律法替人决定如何死亡、此生有何用途、谁有资格退出，会发生什么？":"《艾爾登法環》把自己的論證散在道具說明、廢墟、重復機制與彼此衝突的人物說法裡。四篇盡量把明示事實與推斷分開，同時追問一條貫穿全作的問題：當律法替人決定如何死亡、此生有何用途、誰有資格退出，會發生什麼？","《艾尔登法环》解读":"《艾爾登法環》解讀","六种结局承诺不同，却都把整个世界的未来集中到那个有力量走到法环面前的人手里。":"六種結局承諾不同，卻都把整個世界的未來集中到那個有力量走到法環面前的人手裡。","四篇从被律法接管的死亡、被自身秩序囚禁的神，读到菈妮代价四溅的退出，以及结局选择中高度集中的权力。":"四篇從被律法接管的死亡、被自身秩序囚禁的神，讀到菈妮代價四濺的退出，以及結局選擇中高度集中的權力。","死诞者":"死誕者","玛莉卡建立黄金律又砸碎法环；拉达冈对它的修复，则来自同一个未被解释清楚的存在内部。":"瑪莉卡建立黃金律又砸碎法環；拉達岡對它的修復，則來自同一個未被解釋清楚的存在內部。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","菈妮毁掉被宇宙秩序指定用途的身体，可她的出口需要另一条灵魂死亡，也未能替布莱泽提供出口。":"菈妮毀掉被宇宙秩序指定用途的身體，可她的出口需要另一條靈魂死亡，也未能替布萊澤提供出口。","选一部法":"選一部法","骷髅的第二次起身，显出一部接管死亡、排除异类，并让一个存在背负危险的律法。":"骷髏的第二次起身，顯出一部接管死亡、排除異類，並讓一個存在背負危險的律法。"};
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

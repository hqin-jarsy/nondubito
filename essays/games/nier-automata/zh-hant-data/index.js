/* Generated offline from essays/games/nier-automata/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"2B与9S并非只是被命令拆散的一对搭档；他们之间的信任，正是反复处刑能够运转的机制。":"2B與9S並非只是被命令拆散的一對搭檔；他們之間的信任，正是反覆處刑能夠運轉的機制。","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與互動敘事","《尼尔：机械纪元》不只讲述被制造出来的生命。重复周目、可恢复的身体、制作人员名单与存档牺牲，让玩家亲自经历“被指派的功能”和“自己作出的行动”之间的差别。":"《尼爾：機械紀元》不只講述被製造出來的生命。重複周目、可恢復的身體、製作人員名單與存檔犧牲，讓玩家親自經歷“被指派的功能”和“自己作出的行動”之間的差別。","《尼尔：机械纪元》解读":"《尼爾：機械紀元》解讀","四篇从2B与9S被设计成处刑结构的亲密关系，读到不存在的人类、长出自身生活的机械生命，以及结局向玩家提出却不强迫的一次请求。":"四篇從2B與9S被設計成處刑結構的親密關係，讀到不存在的人類、長出自身生活的機械生命，以及結局向玩家提出卻不強迫的一次請求。","她每次都要杀他一次":"她每次都要殺他一次","寄叶计划发现消耗人格是一件“不人道”的事，解决方法却是改造被消耗者，而不是停止消耗。":"寄葉計劃發現消耗人格是一件“不人道”的事，解決方法卻是改造被消耗者，而不是停止消耗。","机械生命超出程序并不天然通向善：它也会长成西蒙娜的吞噬、让-保罗的冷漠，以及帕斯卡没有保证的照料。":"機械生命超出程序並不天然通向善：它也會長成西蒙娜的吞噬、讓-保羅的冷漠，以及帕斯卡沒有保證的照料。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","辅助机、被规定内疚的姐妹与玩家，都以一件没有命令、奖励或结果保证的行动打断系统。":"輔助機、被規定內疚的姐妹與玩家，都以一件沒有命令、獎勵或結果保證的行動打斷系統。","这个系列把同一个问题放在人造人、机械生命体、辅助机和屏幕前的玩家身上：设计者已经决定一个存在有什么用之后，它还能长出什么？":"這個系列把同一個問題放在人造人、機械生命體、輔助機和螢幕前的玩家身上：設計者已經決定一個存在有什麼用之後，它還能長出什麼？"};
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

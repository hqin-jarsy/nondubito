/* Generated offline from essays/games/shadow-of-the-colossus/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與互動敘事","《旺达与巨像》给玩家一个极清楚的目标，却几乎没有普通意义上的敌人。正因为世界如此空，每个动作才变得清楚：旺达必须主动找到那些没有追赶他的存在，爬上身体，并结束已经被界面排成清单的生命。":"《旺達與巨像》給玩家一個極清楚的目標，卻幾乎沒有普通意義上的敵人。正因為世界如此空，每個動作才變得清楚：旺達必須主動找到那些沒有追趕他的存在，爬上身體，並結束已經被介面排成清單的生命。","《旺达与巨像》解读":"《旺達與巨像》解讀","三篇从一场无法征得同意的复活、被做成道路的十六个巨像，读到莫诺醒来后抱起长角婴儿的那个无价动作。":"三篇從一場無法徵得同意的復活、被做成道路的十六個巨像，讀到莫諾醒來後抱起長角嬰兒的那個無價動作。","他没有问过她":"他沒有問過她","作品从未否认旺达对莫诺的爱。它追问的是：当一个人决定价码、另一个人无法回答、十六条无关的生命被写进账里时，爱会变成什么。":"作品從未否認旺達對莫諾的愛。它追問的是：當一個人決定價碼、另一個人無法回答、十六條無關的生命被寫進賬裡時，愛會變成什麼。","她醒过来的时候欠着一笔账":"她醒過來的時候欠著一筆賬","它们本来在做自己的事":"它們本來在做自己的事","巨像没有闯入旺达的世界；是目标来到它们的世界，把飞行、沉睡与守住地盘重新定义成阻碍。":"巨像沒有闖入旺達的世界；是目標來到它們的世界，把飛行、沉睡與守住地盤重新定義成阻礙。","旺达拒绝一套献祭莫诺的法，却又把她的复活变成不经商议便可牺牲另外十六个存在的理由。":"旺達拒絕一套獻祭莫諾的法，卻又把她的復活變成不經商議便可犧牲另外十六個存在的理由。","系列 · 三篇解读 · 游戏评论":"系列 · 三篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","莫诺继承了一场从未同意其价码的复活，并以全作唯一不购买任何结果的行动开始恢复后的生命。":"莫諾繼承了一場從未同意其價碼的復活，並以全作唯一不購買任何結果的行動開始恢復後的生命。"};
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

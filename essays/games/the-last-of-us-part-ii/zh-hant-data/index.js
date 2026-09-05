/* Generated offline from essays/games/the-last-of-us-part-ii/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《最后生还者 第二部》并不是要玩家发现双方原来完全一样。它做的事情更难受：给双方各自一段成立的历史，同时拒绝让任何一段把另一段抵消。":"《最後生還者 第二部》並不是要玩家發現雙方原來完全一樣。它做的事情更難受：給雙方各自一段成立的歷史，同時拒絕讓任何一段把另一段抵消。","《最后生还者 第二部》解读":"《最後生還者 第二部》解讀","两套账":"兩套賬","他没有问过她":"他沒有問過她","勒弗拒绝疤脸帮按出生条件分配给他的一生；艾比对他的保护让她重新承担一件面向未来、而非试图改写过去的事情。":"勒弗拒絕疤臉幫按出生條件分配給他的一生；艾比對他的保護讓她重新承擔一件面向未來、而非試圖改寫過去的事情。","四篇从乔尔的救人与谎言、两套都要求一条命的真账，读到艾比转向勒弗，以及那次既不以原谅、也不以互相理解为前提的停手。":"四篇從喬爾的救人與謊言、兩套都要求一條命的真賬，讀到艾比轉向勒弗，以及那次既不以原諒、也不以互相理解為前提的停手。","海滩":"海灘","游戏先让玩家杀死艾比的朋友，再让玩家与他们共同生活；认识发生在行动之后，已经来不及变成一次令自己满意的宽恕。":"遊戲先讓玩家殺死艾比的朋友，再讓玩家與他們共同生活；認識發生在行動之後，已經來不及變成一次令自己滿意的寬恕。","火萤准备在艾莉失去意识时牺牲她，乔尔救出她，又把真相隐瞒四年；救人替她决定了一次，谎言则让她无从知道自己被决定过。":"火螢準備在艾莉失去意識時犧牲她，喬爾救出她，又把真相隱瞞四年；救人替她決定了一次，謊言則讓她無從知道自己被決定過。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","艾莉没有听过艾比的故事，也没有原谅她，却仍在最后松手；停手可以先于理解，只是失去的生活已经无法随之回来。":"艾莉沒有聽過艾比的故事，也沒有原諒她，卻仍在最後鬆手；停手可以先於理解，只是失去的生活已經無法隨之回來。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这四篇不把作品压成一句“复仇无用”，而是追踪被拿走的选择、来得太迟的认识，以及理解一个敌人与不再毁掉她之间的差别。":"這四篇不把作品壓成一句“復仇無用”，而是追蹤被拿走的選擇、來得太遲的認識，以及理解一個敵人與不再毀掉她之間的差別。"};
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

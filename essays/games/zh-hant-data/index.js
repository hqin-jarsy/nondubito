/* Generated offline from essays/games/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文章库":"← 文章庫","《尼尔：机械纪元》解读":"《尼爾：機械紀元》解讀","《旺达与巨像》解读":"《旺達與巨像》解讀","《黑神话：悟空》解读":"《黑神話：悟空》解讀","三个系列 · 十一篇 · 英 / 简 / 繁":"三個系列 · 十一篇 · 英 / 簡 / 繁","三篇从一场无法征得同意的复活、被做成道路的十六个巨像，读到莫诺醒来后抱起长角婴儿的那个无价动作。":"三篇從一場無法徵得同意的復活、被做成道路的十六個巨像，讀到莫諾醒來後抱起長角嬰兒的那個無價動作。","四篇从2B与9S被设计成处刑结构的亲密关系，读到不存在的人类、长出自身生活的机械生命，以及结局向玩家提出却不强迫的一次请求。":"四篇從2B與9S被設計成處刑結構的親密關係，讀到不存在的人類、長出自身生活的機械生命，以及結局向玩家提出卻不強迫的一次請求。","四篇从沉默的天命人、悟空散落的六根、黄眉制造出来的人性证据，读到那只在睁眼之前停住的金箍。":"四篇從沉默的天命人、悟空散落的六根、黃眉製造出來的人性證據，讀到那隻在睜眼之前停住的金箍。","游戏不只讲故事。它还分配目标、建立系统、隐去信息，并要求玩家亲自行动。这里把机制、重复、失败、界面与选择都当作作品论证的一部分，而不是包在故事外面的容器。":"遊戲不只講故事。它還分配目標、建立系統、隱去資訊，並要求玩家親自行動。這裡把機制、重複、失敗、介面與選擇都當作作品論證的一部分，而不是包在故事外面的容器。","游戏与交互叙事":"遊戲與互動敘事","游戏目录 · 系列 01–03":"遊戲目錄 · 系列 01–03","系统、行动与人的目的":"系統、行動與人的目的","阅读系列":"閱讀系列","频道 · 游戏解读":"頻道 · 遊戲解讀"};
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

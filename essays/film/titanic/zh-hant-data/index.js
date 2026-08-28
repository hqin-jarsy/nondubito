/* Generated offline from essays/film/titanic/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《泰坦尼克号》常被记成一场灾难中的爱情，但它最早的动作其实是估价：打捞队给钻石定价，破产家族用女儿的未来换资本，未婚夫再把礼物变成所有权主张。沉船没有让这些安排消失，反而让日常生活里早已存在的分类，迅速转化为信息、通道、救援与生存机会的差异。":"《鐵達尼號》常被記成一場災難中的愛情，但它最早的動作其實是估價：打撈隊給鑽石定價，破產家族用女兒的未來換資本，未婚夫再把禮物變成所有權主張。沉船沒有讓這些安排消失，反而讓日常生活裡早已存在的分類，迅速轉化為資訊、通道、救援與生存機會的差異。","《泰坦尼克号》解读":"《鐵達尼號》解讀","三篇从一桩被安排成交易的婚姻，读到灾难如何把既有等级转换为生存机会，以及爱情结束后露丝亲手写成的八十四年。":"三篇從一樁被安排成交易的婚姻，讀到災難如何把既有等級轉換為生存機會，以及愛情結束後露絲親手寫成的八十四年。","她拿到的是此后八十四年":"她拿到的是此後八十四年","她的婚姻是一笔谈好的交易":"她的婚姻是一筆談好的交易","杰克帮露丝活过一个夜晚；床边照片记录的成就更大：此后八十四年，未婚夫与逝去的爱人都没有成为她唯一的主人。":"傑克幫露絲活過一個夜晚；床邊照片記錄的成就更大：此後八十四年，未婚夫與逝去的愛人都沒有成為她唯一的主人。","电影用闸门、甲板、救生艇与迟到的回航画出一张道德地图；真实历史比“锁门等死”的传说复杂，却同样是结构性的。":"電影用閘門、甲板、救生艇與遲到的回航畫出一張道德地圖；真實歷史比“鎖門等死”的傳說複雜，卻同樣是結構性的。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这三篇会把卡梅隆的戏剧化处理与真实历史分开，同时追踪两者共同提出的伦理问题。露丝的自由并不在她选择杰克而非卡尔时就已完成；它更长久地显现在一个自己选的名字、此后八十四年的工作与冒险，以及她最终拒绝让金钱或爱情成为一生唯一作者的动作里。":"這三篇會把卡梅隆的戲劇化處理與真實歷史分開，同時追蹤兩者共同提出的倫理問題。露絲的自由並不在她選擇傑克而非卡爾時就已完成；它更長久地顯現在一個自己選的名字、此後八十四年的工作與冒險，以及她最終拒絕讓金錢或愛情成為一生唯一作者的動作裡。","那一夜，分类变成了生死分流":"那一夜，分類變成了生死分流","露丝的订婚把一个破产姓氏接到工业资本上；爱情故事由此从更冷的结构中开始：债务、性别、礼物与所有权。":"露絲的訂婚把一個破產姓氏接到工業資本上；愛情故事由此從更冷的結構中開始：債務、性別、禮物與所有權。"};
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

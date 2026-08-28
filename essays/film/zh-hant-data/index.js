/* Generated offline from essays/film/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文章库":"← 文章庫","《泰坦尼克号》解读":"《鐵達尼號》解讀","《肖申克的救赎》解读":"《肖申克的救贖》解讀","《阿甘正传》解读":"《阿甘正傳》解讀","《霸王别姬》解读":"《霸王別姬》解讀","三篇从一桩被安排成交易的婚姻，读到灾难如何把既有等级转换为生存机会，以及爱情结束后露丝亲手写成的八十四年。":"三篇從一樁被安排成交易的婚姻，讀到災難如何把既有等級轉換為生存機會，以及愛情結束後露絲親手寫成的八十四年。","三篇从不断被规格判定的阿甘，读到丹中尉如何重领自己的生命，以及电影怎样既看见珍妮的痛，又把她压进别人的故事。":"三篇從不斷被規格判定的阿甘，讀到丹中尉如何重領自己的生命，以及電影怎樣既看見珍妮的痛，又把她壓進別人的故事。","三篇从布鲁克斯之死、安迪的有用与瑞德的假释，重读体制如何把人变成功能，以及一个人如何在用途之外重新出现。":"三篇從布魯克斯之死、安迪的有用與瑞德的假釋，重讀體制如何把人變成功能，以及一個人如何在用途之外重新出現。","三篇从被削到合格的小豆子、被打进身体的“女娇娥”，读到菊仙如何赎回自己，并试着把关系带到戏外。":"三篇從被削到合格的小豆子、被打進身體的“女嬌娥”，讀到菊仙如何贖回自己，並試著把關係帶到戲外。","四个系列 · 十二篇 · 英 / 简 / 繁":"四個系列 · 十二篇 · 英 / 簡 / 繁","故事、结构与人的目的":"故事、結構與人的目的","电影":"電影","电影不只讲述故事，也安排目光、声音、时间、权力，以及人与人之间的距离。这里从情节出发，却更关心镜头与结构让什么显形，而这些东西无法被剧情梗概替代。":"電影不只講述故事，也安排目光、聲音、時間、權力，以及人與人之間的距離。這裡從情節出發，卻更關心鏡頭與結構讓什麼顯形，而這些東西無法被劇情梗概替代。","电影目录 · 系列 01–04":"電影目錄 · 系列 01–04","阅读系列":"閱讀系列","频道 · 电影细读":"頻道 · 電影細讀"};
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

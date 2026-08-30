/* Generated offline from essays/film/yi-yi/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《一一》解读":"《一一》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一个孩子拍下别人看不见的自己，读到一个成年人怎样过满了并非自己决定的日子，以及一家人为何只能对着无法回答的婆婆说出真话。":"三篇從一個孩子拍下別人看不見的自己，讀到一個成年人怎樣過滿了並非自己決定的日子，以及一家人為何只能對著無法回答的婆婆說出真話。","《一一》从婚礼开始，以葬礼结束；它的结构与其说是圆，不如说是一组彼此不完整的视角。洋洋拍摄后脑勺，正是杨德昌的方法：每个人都需要另一个人替自己看见视野以外的部分。":"《一一》從婚禮開始，以葬禮結束；它的結構與其說是圓，不如說是一組彼此不完整的視角。洋洋拍攝後腦勺，正是楊德昌的方法：每個人都需要另一個人替自己看見視野以外的部分。","成年人面对的问题并非无所事事，恰恰是每个人都很忙。问题在于，忙碌可以填满多年，却无法形成一段能被自己讲述为“我的”的生活。日本游戏设计者大田提供了对照，不是因为日子轻松，而是因为他的活动仍由自己创作。":"成年人面對的問題並非無所事事，恰恰是每個人都很忙。問題在於，忙碌可以填滿多年，卻無法形成一段能被自己講述為“我的”的生活。日本遊戲設計者大田提供了對照，不是因為日子輕鬆，而是因為他的活動仍由自己創作。","杨德昌二〇〇〇年《一一》。全片剧透。":"楊德昌二〇〇〇年《一一》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","你自己看不到啊，我拍给你看":"你自己看不到啊，我拍給你看","洋洋拍下别人自己看不见的那一半，把一个孩子的实验变成整部电影的相互观看方法。":"洋洋拍下別人自己看不見的那一半，把一個孩子的實驗變成整部電影的相互觀看方法。","英 · 简 · 繁":"英 · 簡 · 繁","他做的每一个决定，都不是他做的":"他做的每一個決定，都不是他做的","NJ穿过东京重访旧爱，却原样回来；大田的魔术、音乐与工作则展示仍属于自己的活动。":"NJ穿過東京重訪舊愛，卻原樣回來；大田的魔術、音樂與工作則展示仍屬於自己的活動。","一个八岁的孩子说他也老了":"一個八歲的孩子說他也老了","昏迷的婆婆成了一家人唯一的听众，也让人看见忙满的日子为何几乎没有什么能被自己认作值得讲述。":"昏迷的婆婆成了一家人唯一的聽眾，也讓人看見忙滿的日子為何幾乎沒有什麼能被自己認作值得講述。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

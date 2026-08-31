/* Generated offline from in-this-corner-of-the-world/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《在这世界的角落》把战争放进一户人家不断重复的劳动里：米、野菜、缝补、队伍、警报，以及一口不能不照看的锅。这个尺度并没有缩小历史，而是让历史怎样先进入一个人的手、再进入她的政治语言显形。":"《在這世界的角落》把戰爭放進一戶人家不斷重複的勞動裡：米、野菜、縫補、隊伍、警報，以及一口不能不照看的鍋。這個尺度並沒有縮小歷史，而是讓歷史怎樣先進入一個人的手、再進入她的政治語言顯形。","《在这世界的角落》解读":"《在這世界的角落》解讀","三篇从一个一直在做饭的人出发，读她如何在别人替她决定的生活中制作自己的世界，失去右手，又在投降广播中看见忍耐的理由飞走。":"三篇從一個一直在做飯的人出發，讀她如何在別人替她決定的生活中製作自己的世界，失去右手，又在投降廣播中看見忍耐的理由飛走。","失去一只手不只失去功能，也失去那只手做过的具体历史——包括爆炸时它牵着的孩子。":"失去一隻手不只失去功能，也失去那隻手做過的具體歷史——包括爆炸時它牽著的孩子。","她一直在做饭":"她一直在做飯","婚姻、家庭与战争都替铃安排好了；电影真正的行动，是她仍从每日劳动中做出一段具体生活。":"婚姻、家庭與戰爭都替鈴安排好了；電影真正的行動，是她仍從每日勞動中做出一段具體生活。","广播宣布战争结束；铃发现支撑多年忍耐的理由消失了，也发现自己做饭用的粮食来自帝国。":"廣播宣佈戰爭結束；鈴發現支撐多年忍耐的理由消失了，也發現自己做飯用的糧食來自帝國。","系列 · 3 篇解读":"系列 · 3 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这三篇以河野史代原作漫画与片渊须直2019年加长版电影为主要文本，并辨析2016年剧场版的重要删改；不把铃化约成纯真、罪责或坚韧的象征，只追踪她做出、失去、知道，又继续去做的事。全文剧透。":"這三篇以河野史代原作漫畫與片淵須直2019年加長版電影為主要文字，並辨析2016年劇場版的重要刪改；不把鈴化約成純真、罪責或堅韌的象徵，只追蹤她做出、失去、知道，又繼續去做的事。全文劇透。","飞走了":"飛走了"};
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

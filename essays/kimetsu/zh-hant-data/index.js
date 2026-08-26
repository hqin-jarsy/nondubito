/* Generated offline from kimetsu/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"\n        《鬼灭之刃》真正讨论的，不只是少年成长与善恶对决，而是人在恐惧、失去和体系压力之下，如何仍然把彼此当作不可替代的存在。\n      ":"\n        《鬼滅之刃》真正討論的，不只是少年成長與善惡對決，而是人在恐懼、失去和體系壓力之下，如何仍然把彼此當作不可替代的存在。\n      ","\n        五篇从无惨、上弦之鬼、产屋敷与柱、炭治郎与伙伴，写到继国缘一和珠世。贯穿其中的是同一个问题：当一个体系不断把人变成工具，是什么让人仍然保持为人？\n      ":"\n        五篇從無慘、上弦之鬼、產屋敷與柱、炭治郎與夥伴，寫到繼國緣一和珠世。貫穿其中的是同一個問題：當一個體系不斷把人變成工具，是什麼讓人仍然保持為人？\n      ","Demon Slayer: Five Readings · 《鬼灭之刃》解读 — Non Dubito":"Demon Slayer: Five Readings · 《鬼滅之刃》解讀 — Non Dubito","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《鬼灭之刃》解读":"《鬼滅之刃》解讀","一千年的恐惧":"一千年的恐懼","不同的坠落":"不同的墜落","中文 · 漫画 / 文化解读":"中文 · 漫畫 / 文化解讀","中文 · 简 / 繁 · 吾峠呼世晴":"中文 · 簡 / 繁 · 吾峠呼世晴","产屋敷、炼狱、胡蝶忍与不死川实弥，以各自的方式回答：明知看不到终点，为什么仍愿意把生命交给别人。":"產屋敷、煉獄、胡蝶忍與不死川實彌，以各自的方式回答：明知看不到終點，為什麼仍願意把生命交給別人。","全系列现有英、简、繁、日、法、德、西、韩八种语言版本；新增语言均为独立重写。":"全系列現有英、簡、繁、日、法、德、西、韓八種語言版本；新增語言均為獨立重寫。","剧透提示":"劇透提示","炭治郎背着祢豆子，也背着一个系统无法容纳的例外。他的强大不只在刀，而在于始终拒绝把任何人简化成工具。":"炭治郎揹著禰豆子，也揹著一個系統無法容納的例外。他的強大不只在刀，而在於始終拒絕把任何人簡化成工具。","猗窝座、妓夫太郎与堕姬、黑死牟、童磨：鬼不是凭空诞生的怪物，而是关系崩塌以后留下的废墟。":"猗窩座、妓夫太郎與墮姬、黑死牟、童磨：鬼不是憑空誕生的怪物，而是關係崩塌以後留下的廢墟。","简体 / 繁體":"簡體 / 繁體","系列 · 五篇解读 · 漫画 / 文化":"系列 · 五篇解讀 · 漫畫 / 文化","缘一与珠世都没有活到看见无惨败亡，却留下了后来者能够接住的火种。真正改变历史的，不只是皓月一瞬，更是萤火相继。":"緣一與珠世都沒有活到看見無慘敗亡，卻留下了後來者能夠接住的火種。真正改變歷史的，不只是皓月一瞬，更是螢火相繼。","萤火与皓月":"螢火與皓月","鬼舞辻无惨不是从强大开始，而是从恐惧开始。当一个存在为了逃避死亡，把所有生命都变成工具，千年的支配体系就此成形。":"鬼舞辻無慘不是從強大開始，而是從恐懼開始。當一個存在為了逃避死亡，把所有生命都變成工具，千年的支配體系就此成形。","：本系列以已完结的原作漫画全23卷为讨论范围，五篇均涉及关键人物身世、战斗结果与最终结局。":"：本系列以已完結的原作漫畫全23卷為討論範圍，五篇均涉及關鍵人物身世、戰鬥結果與最終結局。"};
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

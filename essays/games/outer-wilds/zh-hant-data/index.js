/* Generated offline from essays/games/outer-wilds/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《星际拓荒》最适合在不被剧透的情况下游玩；这组文章默认读者已经走完旅程。它把知识直接变成行动：玩家不是越来越强，而是逐渐看见道路何时打开、机器为何建成、前人停在了哪里。最后找到的并不是拯救旧世界的办法，而是把好奇、陪伴与未完成的工作带进一个无法阻止的结束。":"《星際拓荒》最適合在不被劇透的情況下遊玩；這組文章默認讀者已經走完旅程。它把知識直接變成行動：玩家不是越來越強，而是逐漸看見道路何時打開、機器為何建成、前人停在了哪裡。最後找到的並不是拯救舊世界的辦法，而是把好奇、陪伴與未完成的工作帶進一個無法阻止的結束。","《星际拓荒》解读":"《星際拓荒》解讀","两种收到消息的方式":"兩種收到消息的方式","二十二分钟":"二十二分鐘","他们留下的是过程":"他們留下的是過程","四篇从一场只留下知识的二十二分钟循环、一个保存争论过程的文明，读到两种面对宇宙终结的时刻，以及最后一堆篝火旁的合奏。":"四篇從一場只留下知識的二十二分鐘循環、一個保存爭論過程的文明，讀到兩種面對宇宙終結的時刻，以及最後一堆篝火旁的合奏。","循环不是为主角造的，也救不了这个星系；它不给等级和武器，只再给一次弄明白的机会。":"循環不是為主角造的，也救不了這個星系；它不給等級和武器，只再給一次弄明白的機會。","挪麦人的墙保存反对、错误、修订和孩子的问题；主角继承的不是标准答案，而是一段仍可继续的对话。":"挪麥人的牆保存反對、錯誤、修訂和孩子的問題；主角繼承的不是標準答案，而是一段仍可繼續的對話。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","索拉努姆处在异常的时间里，楚特却在一轮之内逐分钟发现宇宙终结；两者的差别不是勇敢的等级。":"索拉努姆處在異常的時間裡，楚特卻在一輪之內逐分鐘發現宇宙終結；兩者的差別不是勇敢的等級。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","要抵达宇宙之眼，玩家必须先拆掉回头的机制；到最后，散在各颗星球的乐器才显出同一首未完成的曲子。":"要抵達宇宙之眼，玩家必須先拆掉回頭的機制；到最後，散在各顆星球的樂器才顯出同一首未完成的曲子。"};
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

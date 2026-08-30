/* Generated offline from essays/literature/the-old-man-and-the-sea/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《老人与海》解读":"《老人與海》解讀","三天里，大马林鱼同时是对手、兄弟与要卖的钱；生存的需要从未迫使老人把它降级。":"三天裡，大馬林魚同時是對手、兄弟與要賣的錢；生存的需要從未迫使老人把它降級。","他去得太远了":"他去得太遠了","四篇文章沿着小说的回答，从村子的收益账走向技艺的内部标准，再从老人对自己的判词，走向唯一一个徒弟的确认。":"四篇文章沿著小說的回答，從村子的收益賬走向技藝的內部標準，再從老人對自己的判詞，走向唯一一個徒弟的確認。","四篇文章，从一个被空船判定为无用的渔夫，到他不肯贬低的那条大鱼，再到鲨鱼如何抹掉全部可见结果，以及一个孩子如何读懂两只受伤的手。":"四篇文章，從一個被空船判定為無用的漁夫，到他不肯貶低的那條大魚，再到鯊魚如何抹掉全部可見結果，以及一個孩子如何讀懂兩隻受傷的手。","圣地亚哥往远海去是专业判断，却以彻底亏损告终；小说从第一页就把技艺与可见收益拆开。":"聖地亞哥往遠海去是專業判斷，卻以徹底虧損告終；小說從第一頁就把技藝與可見收益拆開。","它们把它吃光了":"它們把它吃光了","欧内斯特·海明威《老人与海》。全书剧透。":"歐內斯特·海明威《老人與海》。全書劇透。","海明威拿走了失败故事里通常会有的解释：没有坏人欺骗圣地亚哥，海不记恨他，鲨鱼只是照着天性而来。留下的问题更难：当结果、见证与证明全部消失，一个人做过的事还算不算数？":"海明威拿走了失敗故事裡通常會有的解釋：沒有壞人欺騙聖地亞哥，海不記恨他，鯊魚只是照著天性而來。留下的問題更難：當結果、見證與證明全部消失，一個人做過的事還算不算數？","游客认错了骨架，曼诺林却读懂了圣地亚哥的双手；徒弟看见了八十五天空船无法衡量的技艺。":"遊客認錯了骨架，曼諾林卻讀懂了聖地亞哥的雙手；徒弟看見了八十五天空船無法衡量的技藝。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那个男孩":"那個男孩","鲨鱼抹掉战果、武器与证明，却没有暴露一条可改正的错误；老人必须区分外部结果与自己的判词。":"鯊魚抹掉戰果、武器與證明，卻沒有暴露一條可改正的錯誤；老人必須區分外部結果與自己的判詞。"};
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

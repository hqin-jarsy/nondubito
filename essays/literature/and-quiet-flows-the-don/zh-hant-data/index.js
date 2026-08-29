/* Generated offline from essays/literature/and-quiet-flows-the-don/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","《静静的顿河》解读":"《靜靜的頓河》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","五篇文章，从格里高利两边作战、不合法却更持久的爱情、被拆空的一家人、不肯选边，到结尾被抱起的儿子。":"五篇文章，從格裡高利兩邊作戰、不合法卻更持久的愛情、被拆空的一家人、不肯選邊，到結尾被抱起的兒子。","肖洛霍夫的史诗让顿河哥萨克的生活穿过战争、革命、内战与新的集体权力。政治立场变化得比亲缘、记忆与地方忠诚能够重排的速度更快。格里高利·麦列霍夫的摇摆因此既不是简单迷惘，也不是无辜。":"蕭洛霍夫的史詩讓頓河哥薩克的生活穿過戰爭、革命、內戰與新的集體權力。政治立場變化得比親緣、記憶與地方忠誠能夠重排的速度更快。格裡高利·麥列霍夫的搖擺因此既不是簡單迷惘，也不是無辜。","五篇文章讨论他在军队之间的移动、与阿克西妮亚的关系、麦列霍夫家庭的毁灭与最后的返回；既保留他以具体人为中心寻找位置的努力，也拒绝用这种努力洗掉他实施过的暴力。":"五篇文章討論他在軍隊之間的移動、與阿克西妮亞的關係、麥列霍夫家庭的毀滅與最後的返回；既保留他以具體人為中心尋找位置的努力，也拒絕用這種努力洗掉他實施過的暴力。","米哈伊尔·肖洛霍夫《静静的顿河》。全书剧透。":"米哈伊爾·蕭洛霍夫《靜靜的頓河》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他两边都当过":"他兩邊都當過","格里高利的阵营变化更多追随具体忠诚与亲见的暴力，而非一场稳定的主义竞赛。":"格裡高利的陣營變化更多追隨具體忠誠與親見的暴力，而非一場穩定的主義競賽。","英 · 简 · 繁":"英 · 簡 · 繁","不合法的那一个":"不合法的那一個","格里高利与阿克西妮亚的关系违反婚姻与共同体规范，却比许多被法律习俗祝福的关系更持久。":"格裡高利與阿克西妮亞的關係違反婚姻與共同體規範，卻比許多被法律習俗祝福的關係更持久。","一家人是怎么被拆光的":"一家人是怎麼被拆光的","麦列霍夫一家在七年里经由不同的死亡、选择、报复与政治重分类，被一点点拆空。":"麥列霍夫一家在七年裡經由不同的死亡、選擇、報復與政治重分類，被一點點拆空。","他为什么不肯选":"他為什麼不肯選","格里高利的拒绝是一种真实立场——具体生命先于总体主义——但内战不给这种立场一个无辜的位置。":"格裡高利的拒絕是一種真實立場——具體生命先於總體主義——但內戰不給這種立場一個無辜的位置。","他抱起了儿子":"他抱起了兒子","格里高利自愿返回、抱起米沙特卡；他得到的不是安全，而是历史尚未夺走的最后关系。":"格裡高利自願返回、抱起米沙特卡；他得到的不是安全，而是歷史尚未奪走的最後關係。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

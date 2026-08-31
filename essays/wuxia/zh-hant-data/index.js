/* Generated offline from wuxia/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"4 篇 · 英 / 简 / 繁":"4 篇 · 英 / 簡 / 繁","5 篇 · 英 / 简 / 繁":"5 篇 · 英 / 簡 / 繁","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文章库":"← 文章庫","《天龙八部》解读":"《天龍八部》解讀","《神雕侠侣》解读":"《神鵰俠侶》解讀","《笑傲江湖》解读":"《笑傲江湖》解讀","《连城诀》解读":"《連城訣》解讀","五篇从无招、君子剑与一场合奏出发，读正邪和一统如何运转，也读同一把锁怎样分别成为强迫与自愿的关系。":"五篇從無招、君子劍與一場合奏出發，讀正邪和一統如何運轉，也讀同一把鎖怎樣分別成為強迫與自願的關係。","五篇从被别人旧账安排的孤儿、师徒之恋与一条断臂出发，读救命的谎言、自己长出的武功，以及两种互不认同的法如何站上同一堵城墙。":"五篇從被別人舊賬安排的孤兒、師徒之戀與一條斷臂出發，讀救命的謊言、自己長出的武功，以及兩種互不認同的法如何站上同一堵城牆。","五篇从雁门关、珍珑棋局与凌波微步出发，读出生前就被写好的身份、未经同意的继承，以及一笔血账如何在双方都不再索取时才真正结束。":"五篇從雁門關、珍瓏棋局與凌波微步出發，讀出生前就被寫好的身份、未經同意的繼承，以及一筆血賬如何在雙方都不再索取時才真正結束。","四个系列 · 十九篇":"四個系列 · 十九篇","四篇从被故意教错的剑法、雪谷里失效的侠名与一段不能被利用的感情，读到活人怎样被一笔不能带走的宝藏换掉。":"四篇從被故意教錯的劍法、雪谷裡失效的俠名與一段不能被利用的感情，讀到活人怎樣被一筆不能帶走的寶藏換掉。","武侠":"武俠","武侠不只是以武功推动的幻想故事。门派传递法，名号分配声誉，秘笈把知识变成财产，江湖则不断追问谁可以退出、相爱、传授、判断，或拒绝被归入任何一边。这里把武学形式与社会秩序视为同一个关于“人如何成为目的”的论证。":"武俠不只是以武功推動的幻想故事。門派傳遞法，名號分配聲譽，秘笈把知識變成財產，江湖則不斷追問誰可以退出、相愛、傳授、判斷，或拒絕被歸入任何一邊。這裡把武學形式與社會秩序視為同一個關於“人如何成為目的”的論證。","金庸 · 四个江湖":"金庸 · 四個江湖","门派、名号、继承与自己选择的关系":"門派、名號、繼承與自己選擇的關係","阅读系列":"閱讀系列","频道 · 武侠小说解读":"頻道 · 武俠小說解讀"};
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

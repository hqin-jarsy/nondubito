/* Generated offline from essays/wuxia/border-town-prodigal/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 3 篇解读":"系列 · 3 篇解讀","《边城浪子》解读":"《邊城浪子》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","三篇从傅红雪每天数万次的拔刀出发，重读梅花庵旧案、被掉包的身世与最后没有落下的一刀：复仇不是做完以后才失去意义，而是在将要完成时被真相截断。":"三篇從傅紅雪每天數萬次的拔刀出發，重讀梅花庵舊案、被掉包的身世與最後沒有落下的一刀：復仇不是做完以後才失去意義，而是在將要完成時被真相截斷。","《边城浪子》给了傅红雪一段几乎只为一件事而存在的人生：身体、刀法、名字和他对亲缘的理解，全都指向复仇。小说并没有等他完成复仇以后才告诉他一切是空的，而是在最后一刀将要落下时，用真相把刀截断。":"《邊城浪子》給了傅紅雪一段幾乎只為一件事而存在的人生：身體、刀法、名字和他對親緣的理解，全都指向復仇。小說並沒有等他完成復仇以後才告訴他一切是空的，而是在最後一刀將要落下時，用真相把刀截斷。","这三篇以古龙原著而非后来改编的情节为准：傅红雪的亲生父母并未交代，结尾的马空群也没有被他杀死。全文包含结局剧透。":"這三篇以古龍原著而非後來改編的情節為準：傅紅雪的親生父母並未交代，結尾的馬空群也沒有被他殺死。全文包含結局劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","花白凤把刀法、毒、记忆与仇恨全都教给傅红雪，唯独没有教他怎样过日子；他的跛足与癫痫，则成了这件成品始终无法被抹平的部分。":"花白鳳把刀法、毒、記憶與仇恨全都教給傅紅雪，唯獨沒有教他怎樣過日子；他的跛足與癲癇，則成了這件成品始終無法被抹平的部分。","英 · 简 · 繁":"英 · 簡 · 繁","十九年的旧债把富商、父亲、妻子与女儿重新压回蒙面凶手和复仇工具；到最后，叶开的飞刀截断的不是一条已经报完的血债，而是它将要完成的瞬间。":"十九年的舊債把富商、父親、妻子與女兒重新壓回蒙面兇手和復仇工具；到最後，葉開的飛刀截斷的不是一條已經報完的血債，而是它將要完成的瞬間。","白夫人为切断丈夫与花白凤的关系，买通稳婆换走婴儿；叶开得到被隐瞒的血缘，傅红雪得到一段没有亲生父母姓名、却仍由自己继续的生命。":"白夫人為切斷丈夫與花白鳳的關係，買通穩婆換走嬰兒；葉開得到被隱瞞的血緣，傅紅雪得到一段沒有親生父母姓名、卻仍由自己繼續的生命。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();

/* Generated offline from essays/literature/norwegian-wood/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《挪威的森林》常被当作爱情小说，但其中的关系发生在一套信念消退、形式仍继续的制度与人生道路上。这组文章追问谁能开口、谁能离开，以及一个人允许另一个人改变自己到什么程度。":"《挪威的森林》常被當作愛情小說，但其中的關係發生在一套信念消退、形式仍繼續的制度與人生道路上。這組文章追問誰能開口、誰能離開，以及一個人允許另一個人改變自己到什麼程度。","《挪威的森林》解读":"《挪威的森林》解讀","三篇文章，从失去信念却照常运转的公共仪式、永泽毫不隐瞒的完整算法，到既接住不完整者、也让离开变难的阿美寮。":"三篇文章，從失去信念卻照常運轉的公共儀式、永澤毫不隱瞞的完整算法，到既接住不完整者、也讓離開變難的阿美寮。","村上春树《挪威的森林》，中文篇依据赖明珠译本。全书剧透。":"村上春樹《挪威的森林》，中文篇依據賴明珠譯本。全書劇透。","永泽":"永澤","永泽的规则诚实、明白而有效；公开条件让他免于欺骗的指控，却不能让初美免于付账。":"永澤的規則誠實、明白而有效；公開條件讓他免於欺騙的指控，卻不能讓初美免於付賬。","渡边看着民族主义仪式与学生革命在没有信念时照常运转；秩序恢复后，他只是不肯在点名时应声。":"渡邊看著民族主義儀式與學生革命在沒有信念時照常運轉；秩序恢復後，他只是不肯在點名時應聲。","疗养所让人不必表演完整，却也可能让外面的生活越来越不可想象；玲子离开时没有宣称自己已被治愈。":"療養所讓人不必表演完整，卻也可能讓外面的生活越來越不可想象；玲子離開時沒有宣稱自己已被治癒。","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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

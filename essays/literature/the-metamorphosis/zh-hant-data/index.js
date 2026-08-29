/* Generated offline from essays/literature/the-metamorphosis/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","《变形记》解读":"《變形記》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇文章，从甲虫之前的劳动、由“他”到“它”的语法，再到家庭更不显眼的变形。":"三篇文章，從甲蟲之前的勞動、由“他”到“它”的語法，再到家庭更不顯眼的變形。","格里高尔·萨姆沙变异的身体，是小说里不可能的事实。围绕它的一切却异常普通：债务、时刻表、房租、家庭责任与公司的怀疑。卡夫卡把两者接在一起，让奇异的变形显出早已发生的社会变形。":"格裡高爾·薩姆沙變異的身體，是小說裡不可能的事實。圍繞它的一切卻異常普通：債務、時刻表、房租、家庭責任與公司的懷疑。卡夫卡把兩者接在一起，讓奇異的變形顯出早已發生的社會變形。","三篇文章追问：那个早晨之前格里高尔已经成了什么，照料如何随着称谓而改变，以及一家人恢复“正常生活”为何并非简单的康复。":"三篇文章追問：那個早晨之前格裡高爾已經成了什麼，照料如何隨著稱謂而改變，以及一家人恢復“正常生活”為何並非簡單的康復。","弗兰茨·卡夫卡《变形记》。全书剧透。":"法蘭茲·卡夫卡《變形記》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他想的是那班火车":"他想的是那班火車","格里高尔在不可能的身体里醒来，首先担心的却是火车时刻；他的变形早在此前就已开始。":"格裡高爾在不可能的身體裡醒來，首先擔心的卻是火車時刻；他的變形早在此前就已開始。","英 · 简 · 繁":"英 · 簡 · 繁","从“他”到“它”":"從“他”到“它”","格里高尔的理解仍属人类，而家庭的称谓与日常却逐步把他重新分类。":"格裡高爾的理解仍屬人類，而家庭的稱謂與日常卻逐步把他重新分類。","到底是谁变了形":"到底是誰變了形","格里高尔在妹妹要求清除他之后死去，一家人却恢复劳动、希望与向前看的能力。":"格裡高爾在妹妹要求清除他之後死去，一家人卻恢復勞動、希望與向前看的能力。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

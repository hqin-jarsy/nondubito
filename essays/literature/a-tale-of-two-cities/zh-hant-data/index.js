/* Generated offline from essays/literature/a-tale-of-two-cities/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《双城记》解读":"《雙城記》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从贵族的冷漠、被继承的责任、有充分理由的复仇，到无法区分两个人的断头台。":"四篇文章，從貴族的冷漠、被繼承的責任、有充分理由的復仇，到無法區分兩個人的斷頭台。","狄更斯先写法国革命的原因，后写它的受害者。饥饿、任意监禁与贵族免责使反抗可以理解；恐怖统治又把因果正义变成一套无法逐人判断的机器。":"狄更斯先寫法國革命的原因，後寫它的受害者。飢餓、任意監禁與貴族免責使反抗可以理解；恐怖統治又把因果正義變成一套無法逐人判斷的機器。","四篇文章通过侯爵、达尔内、德伐日太太与卡顿，把这两个方向同时保留下来。小说的问题不是历史有没有理由，而是理由何时会取代判断。":"四篇文章透過侯爵、達爾內、德伐日太太與卡頓，把這兩個方向同時保留下來。小說的問題不是歷史有沒有理由，而是理由何時會取代判斷。","查尔斯·狄更斯《双城记》。全书剧透。":"查爾斯·狄更斯《雙城記》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他扔下一枚金币":"他扔下一枚金幣","侯爵的马车碾死孩子；他扔下的金币显出一个把生命翻译成麻烦与价格的秩序。":"侯爵的馬車碾死孩子；他扔下的金幣顯出一個把生命翻譯成麻煩與價格的秩序。","英 · 简 · 繁":"英 · 簡 · 繁","他放弃了一切，而那没有用":"他放棄了一切，而那沒有用","达尔内拒绝埃弗雷蒙德家族的继承；革命法庭却把血统当成个人无法撤销的行为。":"達爾內拒絕埃弗雷蒙德家族的繼承；革命法庭卻把血統當成個人無法撤銷的行為。","德伐日太太的复仇来自真实的家族毁灭；恐怖始于一段有正当理由的记忆变成无限名单。":"德伐日太太的復仇來自真實的家族毀滅；恐怖始於一段有正當理由的記憶變成無限名單。","断头台分不出来":"斷頭台分不出來","卡顿与达尔内的相貌相似，骗过了只读取姓名与身体、无法判断具体个人的死亡机器。":"卡頓與達爾內的相貌相似，騙過了只讀取姓名與身體、無法判斷具體個人的死亡機器。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

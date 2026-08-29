/* Generated offline from essays/film/truman-show/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《楚门的世界》解读":"《楚門的世界》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一段被制造成内容的人生，读到恐惧如何让囚禁显得出于自愿，以及楚门为什么不必先证明外面的世界更好，仍然可以走出那扇门。":"三篇從一段被製造成內容的人生，讀到恐懼如何讓囚禁顯得出於自願，以及楚門為什麼不必先證明外面的世界更好，仍然可以走出那扇門。","《楚门的世界》常被说成一个关于欺骗的故事。但楚门没有一段被谎言覆盖、只待恢复的原初生活：他出生时便被公司收养，家庭、婚姻、志向、危险和解释都在他能够判断之前被安排好了。比“欺骗”更准确的词，是“生产”。":"《楚門的世界》常被說成一個關於欺騙的故事。但楚門沒有一段被謊言覆蓋、只待恢復的原初生活：他出生時便被公司收養，家庭、婚姻、志向、危險和解釋都在他能夠判斷之前被安排好了。比“欺騙”更準確的詞，是“生產”。","这三篇从外部的装置写到内在的恐惧，再回到出口。它们追问：环境如何预先制造一个人用来治理自己的欲望；舒适与恐惧为什么是同一套控制的两面；以及楚门最后那句话，如何把可以被观察的一生，与任何摄影机都不曾占有的内心分开。":"這三篇從外部的裝置寫到內在的恐懼，再回到出口。它們追問：環境如何預先製造一個人用來治理自己的慾望；舒適與恐懼為什麼是同一套控制的兩面；以及楚門最後那句話，如何把可以被觀察的一生，與任何攝影機都不曾佔有的內心分開。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他不是被骗了，他是被生产的":"他不是被騙了，他是被生產的","楚门并非活在一段被谎言遮住的真实过去之上；他的世界从出生起就被组织成唯一可想象的生活。":"楚門並非活在一段被謊言遮住的真實過去之上；他的世界從出生起就被組織成唯一可想像的生活。","英 · 简 · 繁":"英 · 簡 · 繁","他的恐惧是被装上去的":"他的恐懼是被裝上去的","节目很少需要一扇锁住的门；它安装恐惧、不便、亲情与合理解释，直到留下看起来像楚门自己的决定。":"節目很少需要一扇鎖住的門；它安裝恐懼、不便、親情與合理解釋，直到留下看起來像楚門自己的決定。","他在门口停了一下，鞠了个躬":"他在門口停了一下，鞠了個躬","楚门不必证明外面更安全、更真实。最后的问题是作者权：一段看似美好的生活，能否仍然属于别人。":"楚門不必證明外面更安全、更真實。最後的問題是作者權：一段看似美好的生活，能否仍然屬於別人。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

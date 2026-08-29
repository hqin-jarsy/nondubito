/* Generated offline from essays/film/witness-for-the-prosecution/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《控方证人》解读":"《情婦》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇写一个把职业直觉误当成无罪判断的律师、一间只能通过证据重建缺席事件的法庭，以及一场怎样生产可信度、最终让合法判决建立其上的表演。":"三篇寫一個把職業直覺誤當成無罪判斷的律師、一間只能透過證據重建缺席事件的法庭，以及一場怎樣生產可信度、最終讓合法判決建立其上的表演。","《控方证人》是一部法庭悬疑片，但它最深的机关不只是“有人撒谎”。比利·怀尔德让几乎所有人都通过一个无法直接检查过去的制度说话。管家的听力、寡妇的遗嘱、血迹、婚姻、一叠信和被告的举止，只有经过规则与律师的安排，才在法庭上取得意义。":"《情婦》是一部法庭懸疑片，但它最深的機關不只是“有人撒謊”。比利·懷德讓幾乎所有人都透過一個無法直接檢查過去的制度說話。管家的聽力、寡婦的遺囑、血跡、婚姻、一疊信和被告的舉止，只有經過規則與律師的安排，才在法庭上取得意義。","三篇从韦菲爵士心脏病后回到办公室写起：他起初遵医嘱拒绝案件，见过克里斯汀以后才正式接手。接着区分法庭正当地审查证据，与法庭不可能亲自重演谋杀之间的距离。最后一篇追到尤斯顿车站那叠以四十英镑买来的信，并在改变所有既有表演意义的最终揭示之前停下。":"三篇從威爾弗德爵士心臟病後回到辦公室寫起：他起初遵醫囑拒絕案件，見過克莉絲汀以後才正式接手。接著區分法庭正當地審查證據，與法庭不可能親自重演謀殺之間的距離。最後一篇追到尤斯頓車站那疊以四十英鎊買來的信，並在改變所有既有表演意義的最終揭示之前停下。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","一个被禁止接这种案子的律师，接了这个案子":"一個被禁止接這種案子的律師，接了這個案子","韦菲爵士先遵从医嘱拒绝辩护，随后又接下案件，因为刑事法庭不只是一份工作，也是他实现主体性的重要方式。":"威爾弗德爵士先遵從醫囑拒絕辯護，隨後又接下案件，因為刑事法庭不只是一份工作，也是他實現主體性的重要方式。","英 · 简 · 繁":"英 · 簡 · 繁","这间法庭能够知道什么":"這間法庭能夠知道什麼","法庭当然审查事实，但只能把事实作为经过证人、物证、程序与解释而抵达的证据来审查。":"法庭當然審查事實，但只能把事實作為經過證人、物證、程序與解釋而抵達的證據來審查。","可信度是可以被造出来的":"可信度是可以被造出來的","一个无名女人、四十英镑与一叠信，展示证据怎样通过一场法庭有程序理由相信的表演取得力量。":"一個無名女人、四十英鎊與一疊信，展示證據怎樣透過一場法庭有程序理由相信的表演取得力量。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

/* Generated offline from a-deadly-secret/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《连城诀》是金庸对凭据、信任与价值最冷的一次追问。狄云读不懂按着自己手印的供状，也无法让无人见证的清白成为证据。":"《連城訣》是金庸對憑據、信任與價值最冷的一次追問。狄雲讀不懂按著自己手印的供狀，也無法讓無人見證的清白成為證據。","《连城诀》解读":"《連城訣》解讀","凭据曾让谎言显得合理；真相到来后，那些为宝藏活了半生的人仍无法松手，直到毒发身亡。":"憑據曾讓謊言顯得合理；真相到來後，那些為寶藏活了半生的人仍無法鬆手，直到毒發身亡。","四篇从被故意教错的剑法、雪谷里失效的侠名与一段不能被利用的感情，读到活人怎样被一笔不能带走的宝藏换掉。":"四篇從被故意教錯的劍法、雪谷裡失效的俠名與一段不能被利用的感情，讀到活人怎樣被一筆不能帶走的寶藏換掉。","在一部到处是抢夺与筹码的小说里，两个人隔窗相望半年；那段不索取的关系也因此无法被利用。":"在一部到處是搶奪與籌碼的小說裡，兩個人隔窗相望半年；那段不索取的關係也因此無法被利用。","师父把假本子一句句教下来，不识字的徒弟无法核对；后来真正的传授，反而没有门派、条件与回报。":"師父把假本子一句句教下來，不識字的徒弟無法核對；後來真正的傳授，反而沒有門派、條件與回報。","系列 · 4 篇解读":"系列 · 4 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","躺尸":"躺屍","这四篇沿着少数逃出交换逻辑的东西来读：不要求入门的传授、无人看见的照护、拒绝成为筹码的感情，以及把有毒的宝藏留在原地的决定。全文包含结局剧透。":"這四篇沿著少數逃出交換邏輯的東西來讀：不要求入門的傳授、無人看見的照護、拒絕成為籌碼的感情，以及把有毒的寶藏留在原地的決定。全文包含結局劇透。","连城宝藏":"連城寶藏","雪崩把维持侠名的公众挡在谷外；一个大侠垮掉后，又靠几十年的侠名在出谷时战胜了事实。":"雪崩把維持俠名的公眾擋在谷外；一個大俠垮掉後，又靠幾十年的俠名在出谷時戰勝了事實。"};
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

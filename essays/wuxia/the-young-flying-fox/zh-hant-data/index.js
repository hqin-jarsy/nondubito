/* Generated offline from wuxia/the-young-flying-fox/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《飞狐外传》解读":"《飛狐外傳》解讀","一只鹅":"一隻鵝","全书最聪明的人唯一一次替别人做主，是替胡斐决定他要活着。":"全書最聰明的人唯一一次替別人做主，是替胡斐決定他要活著。","四篇从一只从未出现的鹅出发，读朝廷怎样清点江湖、圆性为何既要救父又要杀父，以及全书最聪明的人怎样替另一个人决定活下去。":"四篇從一隻從未出現的鵝出發，讀朝廷怎樣清點江湖、圓性為何既要救父又要殺父，以及全書最聰明的人怎樣替另一個人決定活下去。","圆性":"圓性","威胁、钱、结拜兄弟与喜欢的人，都没能给一个陌生人的冤屈定价。":"威脅、錢、結拜兄弟與喜歡的人，都沒能給一個陌生人的冤屈定價。","掌门":"掌門","没有人被绑来；每个人自己走进会场，门派、武功与旧怨便都进了名单。":"沒有人被綁來；每個人自己走進會場，門派、武功與舊怨便都進了名單。","灵素":"靈素","系列 · 4 篇解读":"系列 · 4 篇解讀","胡斐用大半部小说追一件与自己没有私人关系的冤案。他周围的钱、面子、名分、血缘与爱情，都提供了看似正当的停手理由。":"胡斐用大半部小說追一件與自己沒有私人關係的冤案。他周圍的錢、面子、名分、血緣與愛情，都提供了看似正當的停手理由。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","血缘让她既要救这个人又要杀这个人；她唯一没有被安排的动作，是离开。":"血緣讓她既要救這個人又要殺這個人；她唯一沒有被安排的動作，是離開。","这四篇追随那些不能被轻易收买或归类的人，同时也不回避：一份自愿的奉献一旦替别人做主，会留下什么代价。":"這四篇追隨那些不能被輕易收買或歸類的人，同時也不迴避：一份自願的奉獻一旦替別人做主，會留下什麼代價。"};
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

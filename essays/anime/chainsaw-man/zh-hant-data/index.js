/* Generated offline from chainsaw-man/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《电锯人》给电次的愿望小得让人误以为那就是自由：食物、住处、触碰与被爱都是真实需要；也正因为真实，谁能供应它们，谁就知道把手放在他人生的什么位置。":"《電鋸人》給電次的願望小得讓人誤以為那就是自由：食物、住處、觸碰與被愛都是真實需要；也正因為真實，誰能供應它們，誰就知道把手放在他人生的什麼位置。","《电锯人》解读":"《電鋸人》解讀","一个只有一个目的的人":"一個只有一個目的的人","一个只认识债务与饥饿的男孩写下很小的愿望清单；玛奇玛把逐项满足变成了牵引他的绳子。":"一個只認識債務與飢餓的男孩寫下很小的願望清單；瑪奇瑪把逐項滿足變成了牽引他的繩子。","五篇从涂果酱的面包与一张愿望清单出发，读到操纵的把手、单一目的、支配失效的一刻，以及故事两端的两片白面包。":"五篇從塗果醬的麵包與一張願望清單出發，讀到操縱的把手、單一目的、支配失效的一刻，以及故事兩端的兩片白麵包。","她把他的尸体驱使上了战场":"她把他的屍體驅使上了戰場","每个人都在用同一个把手":"每個人都在用同一個把手","涂果酱的面包":"塗果醬的麵包","玛奇玛、姬野、帕瓦与蕾塞都碰到了欲望这个把手；机制相似，却不因此拥有相同的道德重量。":"瑪奇瑪、姬野、帕瓦與蕾塞都碰到了慾望這個把手；機制相似，卻不因此擁有相同的道德重量。","玛奇玛仰视电锯人、俯视电次，却朝两个方向都做占有；故事以另一个饥饿的孩子和另一顿饭收尾。":"瑪奇瑪仰視電鋸人、俯視電次，卻朝兩個方向都做佔有；故事以另一個飢餓的孩子和另一頓飯收尾。","玛奇玛把死者当作资产调度；帕瓦那次不划算的拒绝没有战胜支配，却让计算短暂失灵。":"瑪奇瑪把死者當作資產排程；帕瓦那次不划算的拒絕沒有戰勝支配，卻讓計算短暫失靈。","白面包":"白麵包","秋用寿命换取通往枪之恶魔的道路；共同生活给他添上计划外的目的，却在最后一起被夺走。":"秋用壽命換取通往槍之惡魔的道路；共同生活給他添上計劃外的目的，卻在最後一起被奪走。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇沿着这份脆弱性读第一部，不把电次写成傻子，也不把玛奇玛化约成一个符号；问题是照护、欲望、目的与控制如何拥有同一种外观，以及日常怎样长出愿望清单里没有的东西。全文剧透。":"這五篇沿著這份脆弱性讀第一部，不把電次寫成傻子，也不把瑪奇瑪化約成一個符號；問題是照護、慾望、目的與控制如何擁有同一種外觀，以及日常怎樣長出願望清單裡沒有的東西。全文劇透。"};
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

/* Generated offline from essays/games/ghost-of-tsushima/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《对马岛之魂》搭出的是一个经过高度戏剧化的道德世界，并非十三世纪武士史的复原。在这个世界里，境井仁继承的规矩曾把他从羞耻里扶起来，却回答不了一场专门研究过它的入侵。这四篇不把他的变化写成实用主义战胜荣誉，也不写成荣誉被腐蚀，而是追问：当现成的法失效之后，一个人怎样承担自己做出的法。":"《對馬島之魂》搭出的是一個經過高度戲劇化的道德世界，並非十三世紀武士史的復原。在這個世界裡，境井仁繼承的規矩曾把他從羞恥裡扶起來，卻回答不了一場專門研究過它的入侵。這四篇不把他的變化寫成實用主義戰勝榮譽，也不寫成榮譽被腐蝕，而是追問：當現成的法失效之後，一個人怎樣承擔自己做出的法。","《对马岛之魂》解读":"《對馬島之魂》解讀","一个名字是编出来的":"一個名字是編出來的","仁守住小松锻造炉之后，结奈给了众人一个可以带走的故事：那个死在小茂田浜的武士，以冥人的身份回来了。":"仁守住小松鍛造爐之後，結奈給了眾人一個可以帶走的故事：那個死在小茂田浜的武士，以冥人的身份回來了。","仁放不下的从来不只是一套战术；那是他躲起来看着父亲死去之后，别人交给他的整套答案。":"仁放不下的從來不只是一套戰術；那是他躲起來看著父親死去之後，別人交給他的整套答案。","千条谷":"千條谷","叫阵":"叫陣","四篇从一场无人接招的叫阵、境井仁荣誉之下的童年内疚，读到结奈替众人编出的名字，以及枫树下那道没有标准答案的选择。":"四篇從一場無人接招的叫陣、境井仁榮譽之下的童年內疚，讀到結奈替眾人編出的名字，以及楓樹下那道沒有標準答案的選擇。","安达晴信出阵，期待的是一场按共同形式展开的决斗；赫通汗回答的却是那套规矩本身，把可靠变成可预测。":"安達晴信出陣，期待的是一場按共同形式展開的決鬥；赫通汗回答的卻是那套規矩本身，把可靠變成可預測。","枫树下":"楓樹下","毒药赢下了城，也活过了那场为它辩护的战争；枫树下，仁必须回答一项再无现成规矩可以代答的请求。":"毒藥贏下了城，也活過了那場為它辯護的戰爭；楓樹下，仁必須回答一項再無現成規矩可以代答的請求。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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

/* Generated offline from essays/anime/the-tatami-galaxy/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“蔷薇色校园生活”因为没有内容、没有坏天气也没有难相处的人，注定胜过真实生活；这场比较开始前就做过手脚。":"“薔薇色校園生活”因為沒有內容、沒有壞天氣也沒有難相處的人，註定勝過真實生活；這場比較開始前就做過手腳。","← 日本动漫与漫画":"← 日本動漫與漫畫","《四叠半神话大系》把一种很熟悉的愿望真的交给主角：如果眼下的生活都怪当初选错，那么就回到入学那天，换一个社团，看看会不会成为本来应该成为的人。作品让这个愿望实现得足够多，直到它所保护的东西显出来。":"《四疊半神話大系》把一種很熟悉的願望真的交給主角：如果眼下的生活都怪當初選錯，那麼就回到入學那天，換一個社團，看看會不會成為本來應該成為的人。作品讓這個願望實現得足夠多，直到它所保護的東西顯出來。","《四叠半神话大系》解读":"《四疊半神話大系》解讀","他在找一个不存在的自己":"他在找一個不存在的自己","四篇从一个没有内容的“蔷薇色校园生活”，读到不断换路却没有改变的人、一直在场的麻烦朋友，以及每个世界里都挂在手边的那只小熊。":"四篇從一個沒有內容的“薔薇色校園生活”，讀到不斷換路卻沒有改變的人、一直在場的麻煩朋友，以及每個世界裡都掛在手邊的那隻小熊。","所有可能人生都变成了同一间房；出口没有宏大规划，只是拉住一个朋友，再把一只小熊还给另一个人。":"所有可能人生都變成了同一間房；出口沒有宏大規劃，只是拉住一個朋友，再把一隻小熊還給另一個人。","每一条路走出来的是同一个人":"每一條路走出來的是同一個人","电影、垒球、骑行与秘密组织让每条路的中段都不同，两端却仍是同一个人在同一间房里作出同一种判断。":"電影、壘球、騎行與秘密組織讓每條路的中段都不同，兩端卻仍是同一個人在同一間房裡作出同一種判斷。","系列 · 4 篇解读":"系列 · 4 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","被怪罪为毁掉每条人生的人，也是所有世界里唯一没有缺席的朋友；麻烦没有被洗掉，在场也终于被看见。":"被怪罪為毀掉每條人生的人，也是所有世界裡唯一沒有缺席的朋友；麻煩沒有被洗掉，在場也終於被看見。","这四篇把重复本身当作论证：同一间房、同一批人、同一种抱怨与同一件没有做的小事不断回来。最后，可能性不再是旁边那个没有缺点的版本，而是眼下仍来得及完成的一个具体动作。含全剧剧透。":"這四篇把重複本身當作論證：同一間房、同一批人、同一種抱怨與同一件沒有做的小事不斷回來。最後，可能性不再是旁邊那個沒有缺點的版本，而是眼下仍來得及完成的一個具體動作。含全劇劇透。","那只挂着的熊":"那隻掛著的熊"};
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

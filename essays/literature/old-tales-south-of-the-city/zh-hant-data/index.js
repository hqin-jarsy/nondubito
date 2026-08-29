/* Generated offline from essays/literature/old-tales-south-of-the-city/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《城南旧事》解读":"《城南舊事》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从被叫作疯子的女人、孩子不肯分类的贼、两个劳动被出售的女人，到标志长大的死亡。":"四篇文章，從被叫作瘋子的女人、孩子不肯分類的賊、兩個勞動被出售的女人，到標誌長大的死亡。","林海音的儿童叙述者英子没有成人权威。这种限制反而成为一种伦理资源：她先听那些已被城市分类的人——疯子、贼、佣人——说话，然后才学会那些本该让倾听变得多余的结论。":"林海音的兒童敘述者英子沒有成人權威。這種限制反而成為一種倫理資源：她先聽那些已被城市分類的人——瘋子、賊、傭人——說話，然後才學會那些本該讓傾聽變得多餘的結論。","四篇文章同时讨论这种开放的价值与危险。孩子能看见成人分类丢掉的东西，也会在不理解全部后果时介入。成长不只是取得成人地图，也是在地图不可避免时决定什么不该丢。":"四篇文章同時討論這種開放的價值與危險。孩子能看見成人分類丟掉的東西，也會在不理解全部後果時介入。成長不只是取得成人地圖，也是在地圖不可避免時決定什麼不該丟。","林海音《城南旧事》。全书剧透。":"林海音《城南舊事》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","她们说她是疯子":"她們說她是瘋子","大人把“疯”当成关于秀贞的结论；英子却把它当作一段交谈的起点。":"大人把“瘋”當成關於秀貞的結論；英子卻把它當作一段交談的起點。","英 · 简 · 繁":"英 · 簡 · 繁","英子与藏在荒草园中的贼交谈，保留了判断行为与把人缩成行为之间的区别。":"英子與藏在荒草園中的賊交談，保留了判斷行為與把人縮成行為之間的區別。","两个被卖过的女人":"兩個被賣過的女人","兰姨娘与宋妈处在不同家庭，两段人生却共同显出女性的劳动、乳汁、婚姻与去向怎样被交易。":"蘭姨娘與宋媽處在不同家庭，兩段人生卻共同顯出女性的勞動、乳汁、婚姻與去向怎樣被交易。","她长大了":"她長大了","父亲之死终结童年，不是因为英子得到了全部答案，而是责任在旧庇护消失后转到她身上。":"父親之死終結童年，不是因為英子得到了全部答案，而是責任在舊庇護消失後轉到她身上。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

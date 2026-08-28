/* Generated offline from essays/film/farewell-concubine/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“我本是女娇娥”是被打出来的":"“我本是女嬌娥”是被打出來的","← 电影":"← 電影","《霸王别姬》常被概括为一部关于艺术、爱情与二十世纪中国历史的史诗。但把这段漫长时间缝在一起的，是一个更贴身的动作：人的身体与关系不断被压进自己没有选择的形状。孩子先要失去一根手指，才能进入科班；一句唱词先要被打进嘴里，他才能成为名角；政权与运动轮番更替，每一次都带来新的合格表演。":"《霸王別姬》常被概括為一部關於藝術、愛情與二十世紀中國歷史的史詩。但把這段漫長時間縫在一起的，是一個更貼身的動作：人的身體與關係不斷被壓進自己沒有選擇的形狀。孩子先要失去一根手指，才能進入科班；一句唱詞先要被打進嘴裡，他才能成為名角；政權與運動輪番更替，每一次都帶來新的合格表演。","《霸王别姬》解读":"《霸王別姬》解讀","一句唱词被强行塞进小豆子的嘴里，后来成为蝶衣艺术的中心。电影让强制与真实投入再也无法被干净分开。":"一句唱詞被強行塞進小豆子的嘴裡，後來成為蝶衣藝術的中心。電影讓強制與真實投入再也無法被幹淨分開。","三篇从被削到合格的小豆子、被打进身体的“女娇娥”，读到菊仙如何赎回自己，并试着把关系带到戏外。":"三篇從被削到合格的小豆子、被打進身體的“女嬌娥”，讀到菊仙如何贖回自己，並試著把關係帶到戲外。","你必须先被削掉一部分":"你必須先被削掉一部分","小豆子只有在身体被改到符合规格以后，才能进入科班。暴力不是艺术体制外的事故，而是生产过程的一部分。":"小豆子只有在身體被改到符合規格以後，才能進入科班。暴力不是藝術體制外的事故，而是生產過程的一部分。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","菊仙完成了全片最清楚的一次退出。她的自由真实、精明而昂贵，却从未因此免于新关系与时代的伤害。":"菊仙完成了全片最清楚的一次退出。她的自由真實、精明而昂貴，卻從未因此免於新關係與時代的傷害。","菊仙把自己赎了出来":"菊仙把自己贖了出來","这三篇沿着这条线索展开，却不把电影压成单一寓言。小豆子成为程蝶衣，也是一个杰出艺术家的形成；他的投入既不能简单说成虚假，也不能说完全由自己创作。菊仙走出花满楼，是一次真正的自我决定，却不是从依赖、争夺与历史中彻底脱身。电影的悲剧，正在于它让美、依恋、强制与能动性同时留在画面里。":"這三篇沿著這條線索展開，卻不把電影壓成單一寓言。小豆子成為程蝶衣，也是一個傑出藝術家的形成；他的投入既不能簡單說成虛假，也不能說完全由自己創作。菊仙走出花滿樓，是一次真正的自我決定，卻不是從依賴、爭奪與歷史中徹底脫身。電影的悲劇，正在於它讓美、依戀、強制與能動性同時留在畫面裡。"};
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

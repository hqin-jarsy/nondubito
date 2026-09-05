/* Generated offline from essays/games/disco-elysium/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《极乐迪斯科》从一个丢掉了所有自我资料的警察开始。世界立刻递来替代品：警务记录、政治主张、警探类型、旁人的骂声，以及脑子里同时开口的二十四种技能。":"《極樂迪斯科》從一個丟掉了所有自我資料的警察開始。世界立刻遞來替代品：警務記錄、政治主張、警探類型、旁人的罵聲，以及腦子裡同時開口的二十四種技能。","《极乐迪斯科》解读":"《極樂迪斯科》解讀","一个想法要先被遇见、经过游戏时间的研究，再完成内化，效果才完全显出；移除它消耗的是有限技能点，而不是金钱。":"一個想法要先被遇見、經過遊戲時間的研究，再完成內化，效果才完全顯出；移除它消耗的是有限技能點，而不是金錢。","二十四个声音":"二十四個聲音","伊索夫·德罗斯用四十三年的主义忠诚回答一次恐惧；一直站在他身旁的竹节虫，却没有被登记进任何人的账本。":"伊索夫·德羅斯用四十三年的主義忠誠回答一次恐懼；一直站在他身旁的竹節蟲，卻沒有被登記進任何人的賬本。","作品没有让哈里找回一个完好无损的“真实自我”。它问的是今天由谁作主，以及一套思想、一处创伤或一个身份是否会被允许解释全部事情。":"作品沒有讓哈里找回一個完好無損的“真實自我”。它問的是今天由誰作主，以及一套思想、一處創傷或一個身份是否會被允許解釋全部事情。","哈里的技能自信地开口，也彼此冲突；失忆没有自动带来自由，只留下一个让现成身份争相进入的位置。":"哈里的技能自信地開口，也彼此衝突；失憶沒有自動帶來自由，只留下一個讓現成身份爭相進入的位置。","四篇从二十四个并不可靠的内在声音、思想进入一个人的时间与代价，读到金·曷城严格而不接管的陪伴，以及在一套解释里住了四十三年的逃兵。":"四篇從二十四個並不可靠的內在聲音、思想進入一個人的時間與代價，讀到金·曷城嚴格而不接管的陪伴，以及在一套解釋裡住了四十三年的逃兵。","思维内阁":"思維內閣","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","金没有把交代成因当作合作门票；他的职业信任会增加也会失去，但哈里作为人和同事的地位并不等于获得赞许。":"金沒有把交代成因當作合作門票；他的職業信任會增加也會失去，但哈里作為人和同事的地位並不等於獲得贊許。"};
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

/* Generated offline from essays/literature/oliver-twist/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《雾都孤儿》解读":"《孤雛淚》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从第二碗粥、费金教人的身份课、南希带着共犯身份的勇气，到拒绝给救人行为标价。":"四篇文章，從第二碗粥、費金教人的身分課、南希帶著共犯身分的勇氣，到拒絕給救人行為標價。","狄更斯让机构与成年人围绕奥利弗竞争，决定这个孩子究竟属于哪一类：贫民、学徒、窃贼、忘恩者、无辜者。物质控制与道德分类共同运作。":"狄更斯讓機構與成年人圍繞奧利弗競爭，決定這個孩子究竟屬於哪一類：貧民、學徒、竊賊、忘恩者、無辜者。物質控制與道德分類共同運作。","四篇文章从那句著名的“再来一点”走到费金的教育与南希的选择；一次勇敢行动既不能抹掉整段人生，也不必被兑换成一段新人生才有价值。":"四篇文章從那句著名的“再來一點”走到費金的教育與南希的選擇；一次勇敢行動既不能抹掉整段人生，也不必被兌換成一段新人生才有價值。","查尔斯·狄更斯《雾都孤儿》。全书剧透。":"查爾斯·狄更斯《孤雛淚》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他要求再来一碗":"他要求再來一碗","济贫院把一个饥饿孩子的请求当作叛乱，因为制度依赖于把需要解释成道德缺陷。":"濟貧院把一個飢餓孩子的請求當作叛亂，因為制度依賴於把需要解釋成道德缺陷。","英 · 简 · 繁":"英 · 簡 · 繁","费金教的那一课":"費金教的那一課","费金的游戏不只教授偷窃，也给奥利弗一种让盗窃变成技能与归属的社会身份。":"費金的遊戲不只教授偷竊，也給奧利弗一種讓盜竊變成技能與歸屬的社會身分。","南希参与团伙、协助劫走奥利弗；她后来的勇气之所以重要，正因为它生长在这段不清白的人生内部。":"南希參與團伙、協助劫走奧利弗；她後來的勇氣之所以重要，正因為它生長在這段不清白的人生內部。","南希拒绝金钱与逃离，又回到赛克斯身边；这是艰难的主体选择，不是她愿意承受结局的证明。":"南希拒絕金錢與逃離，又回到賽克斯身邊；這是艱難的主體選擇，不是她願意承受結局的證明。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

/* Generated offline from essays/film/12-angry-men/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《十二怒汉》解读":"《十二怒漢》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一张只为讨论争取时间的票，读到合理怀疑怎样通过具体检验形成，以及最后一位陪审员如何发现自己审判的其实是自己的儿子。":"三篇從一張只為討論爭取時間的票，讀到合理懷疑怎樣透過具體檢驗形成，以及最後一位陪審員如何發現自己審判的其實是自己的兒子。","《十二怒汉》与其说是在赞美雄辩，不如说是在研究一种有纪律的拒绝。八号陪审员很少提供完整的替代案情，他只是追问控方的说法是否承受得住再看一遍。怀疑因此变成一连串可以操作的动作：比较、计时、测量、重演与修正。":"《十二怒漢》與其說是在讚美雄辯，不如說是在研究一種有紀律的拒絕。八號陪審員很少提供完整的替代案情，他只是追問控方的說法是否承受得住再看一遍。懷疑因此變成一連串可以操作的動作：比較、計時、測量、重演與修正。","这里必须作一处校正：八号私下买到同款刀，在戏剧上极有力量，在真实审判中却会构成陪审员不当自行调查。这个系列保留影片的认识论洞见，同时把它和健全的陪审程序区分开。":"這裡必須作一處校正：八號私下買到同款刀，在戲劇上極有力量，在真實審判中卻會構成陪審員不當自行調查。這個系列保留影片的認識論洞見，同時把它和健全的陪審程序區分開。","西德尼·吕美特一九五七年《十二怒汉》。全片剧透。":"西德尼·呂美特一九五七年《十二怒漢》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他投的那一票，不是“无罪”":"他投的那一票，不是“無罪”","八号并未宣称被告清白，他只是用全体一致规则要求十二个人在授权死亡以前花时间认真讨论。":"八號並未宣稱被告清白，他只是用全體一致規則要求十二個人在授權死亡以前花時間認真討論。","英 · 简 · 繁":"英 · 簡 · 繁","他没有找到新证据，只是把旧的看了一遍":"他沒有找到新證據，只是把舊的看了一遍","刀、平面图、列车声与眼镜印把怀疑变成具体工作，而那把刀也暴露了真实陪审程序中的问题。":"刀、平面圖、列車聲與眼鏡印把懷疑變成具體工作，而那把刀也暴露了真實陪審程序中的問題。","他最后否定的，是他自己":"他最後否定的，是他自己","偏见失去听众，证据改变诚实的判断，而三号终于看见公共判决里一直藏着自己的儿子。":"偏見失去聽眾，證據改變誠實的判斷，而三號終於看見公共判決裡一直藏著自己的兒子。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

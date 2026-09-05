/* Generated offline from essays/literature/all-quiet-on-the-western-front/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“西线无战事”真实量出战线没有移动，却量不出保罗；当没有别的记录留下，它的窄真相便成了那天的全部。":"“西線無戰事”真實量出戰線沒有移動，卻量不出保羅；當沒有別的記錄留下，它的窄真相便成了那天的全部。","← 文学与文化":"← 文學與文化","《西线无战事》解读":"《西線無戰事》解讀","三篇文章，从判断者无需支付的代价、刀落下以后才得到名字的敌人，到完全真实、却无法记录死在“无事”之中的那个人的战报。":"三篇文章，從判斷者無需支付的代價、刀落下以後才得到名字的敵人，到完全真實、卻無法記錄死在“無事”之中的那個人的戰報。","保罗的刀先于职业、家庭与名字抵达；那些细节把敌人还原为人时，事后的承诺却已无处站立。":"保羅的刀先於職業、家庭與名字抵達；那些細節把敵人還原為人時，事後的承諾卻已無處站立。","康托列克真诚的教导由学生的身体兑现；损伤他们的同一套训练，也制造了让他们活下去的战友情。":"康托列克真誠的教導由學生的身體兌現；損傷他們的同一套訓練，也製造了讓他們活下去的戰友情。","弹坑里那个人":"彈坑裡那個人","战报上那一句":"戰報上那一句","本文依据朱雯译本（上海人民出版社／世纪文景 2017 修订版），人名从该本。另有姜乙、顏徽玲译本通行。只处理小说，不涉及电影版。":"本文依據朱雯譯本（上海人民出版社／世紀文景 2017 修訂版），人名從該本。另有姜乙、顏徽玲譯本通行。只處理小說，不涉及電影版。","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那句话不花他们一分钱":"那句話不花他們一分錢","雷马克追踪的是词语与词语兑现之身体之间的距离：教师与学生、地图与战壕、敌人与有名字的排字工、战报与死去的士兵。这组文章不会用战友情替制造它的机器辩护。":"雷馬克追蹤的是詞語與詞語兌現之身體之間的距離：教師與學生、地圖與戰壕、敵人與有名字的排字工、戰報與死去的士兵。這組文章不會用戰友情替製造它的機器辯護。"};
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

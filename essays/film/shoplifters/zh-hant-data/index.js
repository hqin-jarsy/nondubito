/* Generated offline from essays/film/shoplifters/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《小偷家族》解读":"《小偷家族》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇先把这个家庭妥协而脆弱的账算清，再考察一个以“已经在这里”为唯一入场条件的家，最后追问没有法律名称的照料会怎样。":"三篇先把這個家庭妥協而脆弱的帳算清，再考察一個以“已經在這裡”為唯一入場條件的家，最後追問沒有法律名稱的照料會怎樣。","《小偷家族》拒绝把温暖的选择家庭与冰冷的法律家庭做成干净对立。柴田一家偷窃、隐瞒死亡、冒领年金、教孩子偷东西，也留下不属于自己的孩子；他们同时认出烫伤，让已经坐在桌边的人有饭吃，并建立无法简单说成虚假的关系。":"《小偷家族》拒絕把溫暖的選擇家庭與冰冷的法律家庭做成乾淨對立。柴田一家偷竊、隱瞞死亡、冒領年金、教孩子偷東西，也留下不屬於自己的孩子；他們同時認出燙傷，讓已經坐在桌邊的人有飯吃，並建立無法簡單說成虛假的關係。","三篇的顺序很重要：感情不能抹掉物质剥削，法律分类也不能抹掉已经发生的照料。是枝裕和让两份记录同时保持打开。":"三篇的順序很重要：感情不能抹掉物質剝削，法律分類也不能抹掉已經發生的照料。是枝裕和讓兩份記錄同時保持打開。","是枝裕和二〇一八年《小偷家族》。全片剧透。":"是枝裕和二〇一八年《小偷家族》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","先把这个家的账算清楚":"先把這個家的帳算清楚","年金、日结、洗衣工资、风俗业、偷窃与隐瞒死亡构成了这个家的物质基础，感情不能使它无辜。":"年金、日領、洗衣薪資、風俗業、偷竊與隱瞞死亡構成了這個家的物質基礎，感情不能使它無辜。","英 · 简 · 繁":"英 · 簡 · 繁","这个家唯一的入场条件，是你已经在这里":"這個家唯一的入場條件，是你已經在這裡","这个家不要求先交代来历再给饭；它的开放真实、不完整、充满秘密，也无法在屋外证明自己。":"這個家不要求先交代來歷再給飯；它的開放真實、不完整、充滿秘密，也無法在屋外證明自己。","她答不出那两个孩子叫她什么":"她答不出那兩個孩子叫她什麼","警察的问题要求关系名称；信代能列出照料，却拿不出让这些事成为家人的称呼、文件与法律依据。":"警察的問題要求關係名稱；信代能列出照料，卻拿不出讓這些事成為家人的稱呼、文件與法律依據。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

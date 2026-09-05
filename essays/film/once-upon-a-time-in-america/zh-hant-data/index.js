/* Generated offline from essays/film/once-upon-a-time-in-america/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《美国往事》解读":"《美國往事》解讀","一个箱子，四个人，和一把钥匙":"一個箱子，四個人，和一把鑰匙","三篇解读：一个共同钱箱、一次以拯救为意图的出卖，以及面条拒绝让麦克斯替两人写下最后结算。":"三篇解讀：一個共同錢箱、一次以拯救為意圖的出賣，以及麵條拒絕讓麥克斯替兩人寫下最後結算。","他拿起那个电话，是为了救他们":"他拿起那個電話，是為了救他們","他背的是那个决定，不只是那个结果":"他背的是那個決定，不只是那個結果","依据赛尔乔·莱昂内执导的一九八四年电影《美国往事》，主要采用约二百二十九分钟的欧洲公映版。影片流通版本众多，此版不同于被大幅删改的美国顺叙版，也不宜简单称为唯一“完整版”。":"依據賽爾喬·萊昂內執導的一九八四年電影《美國往事》，主要採用約二百二十九分鐘的歐洲公映版。影片流通版本眾多，此版不同於被大幅刪改的美國順敘版，也不宜簡單稱為唯一“完整版”。","孩子们用共同钱箱让每个人受其他人限制；帮派内部的平等，却不会自动让对外的暴力变得正当。":"孩子們用共同錢箱讓每個人受其他人限制；幫派內部的平等，卻不會自動讓對外的暴力變得正當。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","赛尔乔·莱昂内把记忆不断重排，直到意图、动作与结果再也无法严丝合缝。三篇文章追踪帮派内部的契约、占有欲里的暴力，以及一次坦白改变了过去造成的结果，却无法改写当时选择之后仍留下的负担。":"賽爾喬·萊昂內把記憶不斷重排，直到意圖、動作與結果再也無法嚴絲合縫。三篇文章追蹤幫派內部的契約、佔有欲裡的暴力，以及一次坦白改變了過去造成的結果，卻無法改寫當時選擇之後仍留下的負擔。","面条意图救人、选择出卖、又相信自己造成死亡；目的、手段与结果无法被一个标签结清。":"麵條意圖救人、選擇出賣、又相信自己造成死亡；目的、手段與結果無法被一個標籤結清。","麦克斯改写因果并把最后一次杀戮当作偿付；面条拒绝按他的条件接受惩罚或赦免。":"麥克斯改寫因果並把最後一次殺戮當作償付；麵條拒絕按他的條件接受懲罰或赦免。"};
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

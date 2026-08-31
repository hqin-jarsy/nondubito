/* Generated offline from march-comes-in-like-a-lion/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《三月的狮子》从饭桌、棋局、学校走廊、房租，以及一个孩子计算自己凭什么留下的安静动作里，写出决定性的伦理结构。没有恶人设计零的童年；伤害从善意沿着一根过窄的价值轴运转出来。":"《三月的獅子》從飯桌、棋局、學校走廊、房租，以及一個孩子計算自己憑什麼留下的安靜動作裡，寫出決定性的倫理結構。沒有惡人設計零的童年；傷害從善意沿著一根過窄的價值軸運轉出來。","《三月的狮子》解读":"《三月的獅子》解讀","一个本来就吃力的家提供了不带成就轴线的饭；这份礼物比幸田给的少，却在性质上不同。":"一個本來就吃力的家提供了不帶成就軸線的飯；這份禮物比幸田給的少，卻在性質上不同。","五篇从收养中没说出口的条件与一盘故意输掉的棋出发，读一个什么也不要的家、站到被霸凌者身边的代价，以及将棋究竟有没有成为零自己的东西。":"五篇從收養中沒說出口的條件與一盤故意輸掉的棋出發，讀一個什麼也不要的家、站到被霸凌者身邊的代價，以及將棋究竟有沒有成為零自己的東西。","什么也不要":"什麼也不要","他已经不再需要靠将棋换取住处，却仍然在下；事实不断增加，作品仍拒绝替他宣布答案。":"他已經不再需要靠將棋換取住處，卻仍然在下；事實不斷增加，作品仍拒絕替他宣佈答案。","他故意输，而他们没有看出来":"他故意輸，而他們沒有看出來","她站到那个位置上去":"她站到那個位置上去","幸田家没有一个人怀着恶意；同一根轴却让一个孩子的成功成为另一个孩子的消失。":"幸田家沒有一個人懷著惡意；同一根軸卻讓一個孩子的成功成為另一個孩子的消失。","收养有一个没说出口的条件":"收養有一個沒說出口的條件","没有大人开出价格；十岁的孩子看清这个家重视什么，并把自己塑造成恰好有用的形状。":"沒有大人開出價格；十歲的孩子看清這個家重視什麼，並把自己塑造成恰好有用的形狀。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","被救的女孩仍然转学；雏的行动作为救援失败了，却仍是制度没有替她做的那个动作。":"被救的女孩仍然轉學；雛的行動作為救援失敗了，卻仍是制度沒有替她做的那個動作。","这五篇以动画前两季为主，必要处参照漫画；不把川本家写成治愈一切的解药——照护是真的，各人的负担也仍然存在，没有一段关系被要求解决全部伤口。剧透至第二季。":"這五篇以動畫前兩季為主，必要處參照漫畫；不把川本家寫成治癒一切的解藥——照護是真的，各人的負擔也仍然存在，沒有一段關係被要求解決全部傷口。劇透至第二季。"};
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

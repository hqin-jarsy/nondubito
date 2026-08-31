/* Generated offline from parasyte/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《寄生兽》从一次生物学事故开始：小右没能进入泉新一的大脑，只能寄生在右手。于是作品得到一个罕见的实验——不是人类战胜入侵者，而是两个判断中心被迫共用一具身体，谁也不能成为唯一的主权者。":"《寄生獸》從一次生物學事故開始：小右沒能進入泉新一的大腦，只能寄生在右手。於是作品得到一個罕見的實驗——不是人類戰勝入侵者，而是兩個判斷中心被迫共用一具身體，誰也不能成為唯一的主權者。","《寄生兽》解读":"《寄生獸》解讀","一个寄生者把怀孕、照护与人类情感当作研究，最后却在无法解释的情况下保护了那个孩子。":"一個寄生者把懷孕、照護與人類情感當作研究，最後卻在無法解釋的情況下保護了那個孩子。","一次失败的入侵让宿主与寄生者都无法独占身体；从互相需要开始的关系，最后超出了最初指令能够解释的范围。":"一次失敗的入侵讓宿主與寄生者都無法獨佔身體；從互相需要開始的關係，最後超出了最初指令能夠解釋的範圍。","五篇从一次没有成功的寄生开始，读到每天重谈的共存、救命之后的改变、一次无法解释的牺牲，以及人心里不能被计算占满的余地。":"五篇從一次沒有成功的寄生開始，讀到每天重談的共存、救命之後的改變、一次無法解釋的犧牲，以及人心裡不能被計算佔滿的餘地。","他哭不出来":"他哭不出來","后藤是一件协调完美的集体武器，却输给了偶然，也输给了心里没有被生存完全占满的人。":"後藤是一件協調完美的集體武器，卻輸給了偶然，也輸給了心裡沒有被生存完全佔滿的人。","她不知道自己为什么那么做":"她不知道自己為什麼那麼做","它没能进到脑子里":"它沒能進到腦子裡","心里有富余":"心裡有富餘","母亲葬礼上，新一的眼睛是干的；救命的改变也改变了活下来的人，而别人比他先认出了缺口。":"母親葬禮上，新一的眼睛是乾的；救命的改變也改變了活下來的人，而別人比他先認出了缺口。","每天重新谈一次":"每天重新談一次","睡眠、上课、危险、保密与约会都要重新协商；双方没有互相改造，也没有一份总协议替代每天的工作。":"睡眠、上課、危險、保密與約會都要重新協商；雙方沒有互相改造，也沒有一份總協議替代每天的工作。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇不把共存写成道德改造。小右没有被说服成人类主义者，新一也没有变成寄生兽；关系是在日程、危险、哀痛、好奇，以及双方都解释不了的行动里慢慢改变的。全文包含结局剧透。":"這五篇不把共存寫成道德改造。小右沒有被說服成人類主義者，新一也沒有變成寄生獸；關係是在日程、危險、哀痛、好奇，以及雙方都解釋不了的行動裡慢慢改變的。全文包含結局劇透。"};
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

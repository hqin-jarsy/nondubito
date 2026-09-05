/* Generated offline from doctor-zhivago/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《日瓦戈医生》解读":"《日瓦戈醫生》解讀","《日瓦戈医生》让私人生活穿过革命、内战、饥荒、流亡、劳改与另一场世界大战。历史不是背景；它改变承诺还能做什么、名字能否留下，以及一个人是否还有回家的位置。":"《日瓦戈醫生》讓私人生活穿過革命、內戰、饑荒、流亡、勞改與另一場世界大戰。歷史不是背景；它改變承諾還能做什麼、名字能否留下，以及一個人是否還有回家的位置。","一个红军电话兵与一个白军青年带着同一篇护身经文；日瓦戈救下幸存者，没有要求他先改变立场。":"一個紅軍電話兵與一個白軍青年帶著同一篇護身經文；日瓦戈救下倖存者，沒有要求他先改變立場。","一次救援可以真的救命，也重复旧日控制的形式；拉拉上车，是因为日瓦戈让她相信自己随后就来。":"一次救援可以真的救命，也重複舊日控制的形式；拉拉上車，是因為日瓦戈讓她相信自己隨後就來。","两个护身符":"兩個護身符","五篇从两个护身符、斯特列利尼科夫的名字与一架救人的雪橇，读到没有身世的洗衣女工，以及没能救下任何人、却比看见者活得更久的烛光。":"五篇從兩個護身符、斯特列利尼科夫的名字與一架救人的雪橇，讀到沒有身世的洗衣女工，以及沒能救下任何人、卻比看見者活得更久的燭光。","他为了修复伤害拉拉的世界而把自己换成一个职务，最后才知道她等的是那个没有完成改造的人回家。":"他為了修復傷害拉拉的世界而把自己換成一個職務，最後才知道她等的是那個沒有完成改造的人回家。","小说用数百页写她的父母，女儿却只能把同一段历史讲成弃儿的流浪故事，不知道自己的笑从哪里来。":"小說用數百頁寫她的父母，女兒卻只能把同一段歷史講成棄兒的流浪故事，不知道自己的笑從哪裡來。","文学细读":"文學細讀","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","蜡烛":"蠟燭","诗没有救下任何人；它只在房屋、姓名、手稿与身体被逐一拿走以后，保存了一个人曾经怎样看见。":"詩沒有救下任何人；它只在房屋、姓名、手稿與身體被逐一拿走以後，儲存了一個人曾經怎樣看見。","这五篇停在史诗内部的五个小结构上：护身符、改过的名字、救人所用的谎言、不知道身世的人，以及写作者尚不知道自己看见了什么时出现的一句诗。含全书剧透。":"這五篇停在史詩內部的五個小結構上：護身符、改過的名字、救人所用的謊言、不知道身世的人，以及寫作者尚不知道自己看見了什麼時出現的一句詩。含全書劇透。","阅读全文":"閱讀全文"};
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

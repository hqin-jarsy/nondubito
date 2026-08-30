/* Generated offline from essays/film/the-godfather/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《教父》解读":"《教父》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一份没有期限的人情契约，读到迈克尔怎样沿着每一步都说得通的理由回到家族，以及结尾那扇门怎样把凯挡在外面，也把新教父锁在里面。":"三篇從一份沒有期限的人情契約，讀到麥可怎樣沿著每一步都說得通的理由回到家族，以及結尾那扇門怎樣把凱擋在外面，也把新教父鎖在裡面。","《教父》先让归属显得动人，然后才让归属显出致命的一面。维托记得名字，提供保护，也不抛弃自己人；然而“自己人”从来不只是亲近的称呼，它也把争端、忠诚与判断一并交给家族。":"《教父》先讓歸屬顯得動人，然後才讓歸屬顯出致命的一面。維托記得名字，提供保護，也不拋棄自己人；然而“自己人”從來不只是親近的稱呼，它也把爭端、忠誠與判斷一並交給家族。","三篇从康妮的婚礼开始，跟着迈克尔从草坪走到医院、餐厅、西西里与教父的椅子，最后回到那扇关上的门。第三篇谈到弗雷多时，会明确延伸至《教父2》的结局。":"三篇從康妮的婚禮開始，跟著麥可從草坪走到醫院、餐廳、西西裡與教父的椅子，最後回到那扇關上的門。第三篇談到佛雷多時，會明確延伸至《教父2》的結局。","科波拉一九七二年《教父》。全片剧透。":"科波拉一九七二年《教父》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他给的不是人情，是一份终身合同":"他給的不是人情，是一份終身合約","殡葬业者没有付钱，却因此改变了归属；未结清的人情让柯里昂家族保留了定义未来债务的权力。":"殯葬業者沒有付錢，卻因此改變了歸屬；未結清的人情讓柯裡昂家族保留了定義未來債務的權力。","英 · 简 · 繁":"英 · 簡 · 繁","他每走回去一步，都有一个说得通的理由":"他每走回去一步，都有一個說得通的理由","医院、餐厅、西西里与继位：没有哪一步单独逼迫迈克尔，合在一起却把他送到了父亲的椅子上。":"醫院、餐廳、西西裡與繼位：沒有哪一步單獨逼迫麥可，合在一起卻把他送到了父親的椅子上。","被算作自己人的那一刻，就不再按自己的规矩活了":"被算作自己人的那一刻，就不再按自己的規矩活了","迈克尔用谎言保护凯，随后一扇门把她隔绝在家族知识之外，也把他封进家族义务之中。":"麥可用謊言保護凱，隨後一扇門把她隔絕在家族知識之外，也把他封進家族義務之中。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

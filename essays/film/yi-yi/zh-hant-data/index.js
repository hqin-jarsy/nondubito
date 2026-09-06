/* Generated offline from essays/film/yi-yi/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《一一》解读":"《一一》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","三篇从洋洋的后脑勺照片出发，读到“替别人看见”和“替别人下定义”的区别，读到判断怎样在妥协中退成旁白，也读到一个家庭为何在回答已经不可能时，才终于给讲述留出位置。":"三篇從洋洋的後腦勺照片出發，讀到“替別人看見”和“替別人下定義”的區別，讀到判斷怎樣在妥協中退成旁白，也讀到一個家庭為何在回答已經不可能時，才終於給講述留出位置。","《一一》从婚礼开始，以葬礼结束；它的结构与其说是圆，不如说是一组彼此不完整的视角。洋洋没有用照片补完别人，只把他们自己无法取得的角度递还给他们。":"《一一》從婚禮開始，以葬禮結束；它的結構與其說是圓，不如說是一組彼此不完整的視角。洋洋沒有用照片補完別人，只把他們自己無法取得的角度遞還給他們。","片中的成年人并非无所事事。工作、照料、内疚和选择塞满了生活。电影追问的，是这些活动是否还组成一段当事人能够认领、能够负责的日子，以及另一个人是否有机会打断他对自己的判决。":"片中的成年人並非無所事事。工作、照料、內疚和選擇塞滿了生活。電影追問的，是這些活動是否還組成一段當事人能夠認領、能夠負責的日子，以及另一個人是否有機會打斷他對自己的判決。","杨德昌二〇〇〇年《一一》。全片剧透。":"楊德昌二〇〇〇年《一一》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","你自己看不到啊，我拍给你看":"你自己看不到啊，我拍給你看","洋洋的照片给别人一个缺失的角度，却不假装任何影像能够把一个人说完。":"洋洋的照片給別人一個缺失的角度，卻不假裝任何影像能夠把一個人說完。","英 · 简 · 繁":"英 · 簡 · 繁","他做的每一个决定，都不是他做的":"他做的每一個決定，都不是他做的","NJ 清楚自己反对什么，他的判断却渐渐退成了不会改变行动方向的旁白。":"NJ 清楚自己反對什麼，他的判斷卻漸漸退成了不會改變行動方向的旁白。","一个八岁的孩子说他也老了":"一個八歲的孩子說他也老了","这个家庭终于给未说完的话留出时间时，床边的人却已经无法回答。":"這個家庭終於給未說完的話留出時間時，床邊的人卻已經無法回答。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

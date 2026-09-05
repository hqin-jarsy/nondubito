/* Generated offline from essays/film/the-curious-case-of-benjamin-button/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《本杰明·巴顿奇事》解读":"《本傑明·巴頓奇事》解讀","一座倒着走的钟，和一个被放在台阶上的婴儿":"一座倒著走的鐘，和一個被放在台階上的嬰兒","三篇解读：在有用之前就被算作一个人、无法共用同一只钟却仍能相遇的人生，以及藏在爱之离开里的替人作主。":"三篇解讀：在有用之前就被算作一個人、無法共用同一隻鐘卻仍能相遇的人生，以及藏在愛之離開裡的替人作主。","他替她做了那个决定":"他替她做了那個決定","他跟每一个人，只能对上一小段":"他跟每一個人，只能對上一小段","依据大卫·芬奇执导的二〇〇八年电影《本杰明·巴顿奇事》，故事灵感来自菲茨杰拉德同名短篇。人物年龄与时间线以影片明确标示的年份为准。":"依據大衛·芬奇執導的二〇〇八年電影《本傑明·巴頓奇事》，故事靈感來自菲茨傑拉德同名短篇。人物年齡與時間線以影片明確標示的年份為準。","倒走的钟无法让死者归来；奎妮的接纳却在才华、感激或生存尚不能证明什么以前，就先把一个孩子算作一个人。":"倒走的鐘無法讓死者歸來；奎妮的接納卻在才華、感激或生存尚不能證明什麼以前，就先把一個孩子算作一個人。","大卫·芬奇的电影与其说是战胜时间，不如说是怎样活在无法对齐的时序里。三篇文章从奎妮无条件的接纳，写到本杰明与黛西短暂的中段，再写到一次预见准确却仍无权替所有人定案的离开。":"大衛·芬奇的電影與其說是戰勝時間，不如說是怎樣活在無法對齊的時序裡。三篇文章從奎妮無條件的接納，寫到本傑明與黛西短暫的中段，再寫到一次預見準確卻仍無權替所有人定案的離開。","本杰明与黛西从来不是同龄人；几次错过以后，他们才在生命中段获得一段可以共同生活的时间。":"本傑明與黛西從來不是同齡人；幾次錯過以後，他們才在生命中段獲得一段可以共同生活的時間。","本杰明说出恐惧，黛西也明确反对，但他仍然离开；预见减少了一种负担，也造成金钱无法替代的缺席。":"本傑明說出恐懼，黛西也明確反對，但他仍然離開；預見減少了一種負擔，也造成金錢無法替代的缺席。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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

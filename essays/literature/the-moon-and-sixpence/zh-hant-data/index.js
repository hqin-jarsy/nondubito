/* Generated offline from essays/literature/the-moon-and-sixpence/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《月亮与六便士》解读":"《月亮與六便士》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从没有理由的离开、施特略夫难以承受的识见、不能成为借口的天才，到经典化试图合并的两件真事。":"四篇文章，從沒有理由的離開、施特略夫難以承受的識見、不能成為藉口的天才，到經典化試圖合併的兩件真事。","毛姆虚构的查尔斯·思特里克兰德，后来被吸收到“放下六便士、追逐月亮”的现代神话里。小说本身远没有这样安慰人：内在强迫同时产生艺术与伤害，而后来的赞美总想把前者换成后者的借口。":"毛姆虛構的查爾斯·思特裡克蘭德，後來被吸收到“放下六便士、追逐月亮”的現代神話裡。小說本身遠沒有這樣安慰人：內在強迫同時產生藝術與傷害，而後來的讚美總想把前者換成後者的藉口。","四篇文章坚持把两件事实分开，也关注那个为读者建构思特里克兰德、却不断承认解释仍不可得的叙述者。":"四篇文章堅持把兩件事實分開，也關注那個為讀者建構思特裡克蘭德、卻不斷承認解釋仍不可得的敘述者。","威廉·萨默塞特·毛姆《月亮与六便士》。全书剧透。":"威廉·薩默塞特·毛姆《月亮與六便士》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他走的那天没有留下理由":"他走的那天沒有留下理由","思特里克兰德的离开既不符合丑闻也不符合励志故事：没有情人，没有宣言，只有无法翻译的强迫。":"思特裡克蘭德的離開既不符合醜聞也不符合勵志故事：沒有情人，沒有宣言，只有無法翻譯的強迫。","英 · 简 · 繁":"英 · 簡 · 繁","那幅画他没有劈":"那幅畫他沒有劈","施特略夫能在毁掉自己婚姻的人身上认出伟大；这种识见既高贵又难以承受。":"施特略夫能在毀掉自己婚姻的人身上認出偉大；這種識見既高貴又難以承受。","那不是一个借口":"那不是一個藉口","天才可以解释思特里克兰德的强迫与作品后来的价值，却不能倒过来授权他利用过的人。":"天才可以解釋思特裡克蘭德的強迫與作品後來的價值，卻不能倒過來授權他利用過的人。","两件事都是真的":"兩件事都是真的","画是伟大的；思特里克兰德伤害了人。成熟判断始于拒绝用一件真事购买另一件。":"畫是偉大的；思特裡克蘭德傷害了人。成熟判斷始於拒絕用一件真事購買另一件。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

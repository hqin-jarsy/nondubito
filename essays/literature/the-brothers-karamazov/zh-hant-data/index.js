/* Generated offline from essays/literature/the-brothers-karamazov/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“我比所有人更有罪”是在接住责任；一旦改成“你也有罪”，同一句话便成了把负担推出去的工具。":"“我比所有人更有罪”是在接住責任；一旦改成“你也有罪”，同一句話便成了把負擔推出去的工具。","← 文学与文化":"← 文學與文化","《卡拉马佐夫兄弟》解读":"《卡拉馬佐夫兄弟》解讀","五篇文章，从不能被结清的苦难、伪装成慈悲的权威，到只能用第一人称承担的责任、化为行动的观念，以及石头旁边一个很小的承诺。":"五篇文章，從不能被結清的苦難、偽裝成慈悲的權威，到只能用第一人稱承擔的責任、化為行動的觀念，以及石頭旁邊一個很小的承諾。","伊万从未下令杀人；斯麦尔佳科夫只需要他的离开，便把哲学结论当成了行动许可。":"伊萬從未下令殺人；斯麥爾佳科夫只需要他的離開，便把哲學結論當成了行動許可。","伊万拒绝任何能把一个受苦孩子纳入和谐的结算，同时坚持他的拒绝来自对生命的贪恋，而非厌弃。":"伊萬拒絕任何能把一個受苦孩子納入和諧的結算，同時堅持他的拒絕來自對生命的貪戀，而非厭棄。","大法官把统治说成慈悲：少向人要求，替他们拿走自由，让权威独自承担成年人的负担。":"大法官把統治說成慈悲：少向人要求，替他們拿走自由，讓權威獨自承擔成年人的負擔。","少尊重一点，那才更像爱":"少尊重一點，那才更像愛","本文依据臧仲伦译本（译林出版社），另有耿济之译本（人民文学）与荣如德译本（上海译文）通行。全书剧透。":"本文依據臧仲倫譯本（譯林出版社），另有耿濟之譯本（人民文學）與榮如德譯本（上海譯文）通行。全書劇透。","石头旁边":"石頭旁邊","第三次谈话":"第三次談話","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","若接钱本身重演羞辱，钱便无法直接帮助；一条找回的狗和一段共同记忆，提供了更小也更具体的修复。":"若接錢本身重演羞辱，錢便無法直接幫助；一條找回的狗和一段共同記憶，提供了更小也更具體的修復。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那句话只能用第一人称说":"那句話只能用第一人稱說","那张退回去的入场券":"那張退回去的入場券","陀思妥耶夫斯基让每一个重要主张都碰见最强的反方。没有哪种声音能安全站在它所解释的戏剧之外，也没有哪个观念永远只是观念。这组文章追踪论证变成关系、行动或拒绝的瞬间。":"陀思妥耶夫斯基讓每一個重要主張都碰見最強的反方。沒有哪種聲音能安全站在它所解釋的戲劇之外，也沒有哪個觀念永遠只是觀念。這組文章追蹤論證變成關係、行動或拒絕的瞬間。"};
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

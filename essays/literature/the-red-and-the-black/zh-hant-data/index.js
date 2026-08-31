/* Generated offline from the-red-and-the-black/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《红与黑》解读":"《紅與黑》解讀","于连憎恨一个按出身分配位置的社会，却也用同一张表衡量自己。他把记忆、相貌、意志与关系换成向上流通的资本，直到已经没有未来可以兑换。":"於連憎恨一個按出身分配位置的社會，卻也用同一張表衡量自己。他把記憶、相貌、意志與關係換成向上流通的資本，直到已經沒有未來可以兌換。","于连把拿破仑藏在床褥下，把整本拉丁文《新约》背给众人听：一本是欲望，一本是复辟时代承认的门票。":"於連把拿破崙藏在床褥下，把整本拉丁文《新約》背給眾人聽：一本是慾望，一本是復辟時代承認的門票。","于连把接近女人写成军令，德·雷纳尔夫人却在毫无算计的关系中失控；两种不对称的叙事最终在一封信与两枪里相撞。":"於連把接近女人寫成軍令，德·雷納爾夫人卻在毫無算計的關係中失控；兩種不對稱的敘事最終在一封信與兩槍裡相撞。","他在牢里做了什么":"他在牢裡做了什麼","他随身带着两样东西":"他隨身帶著兩樣東西","四篇文章，从于连随身携带的两本书、被他改写成战役的爱情，到玛蒂尔德所爱的故事，以及监狱中终于停止换算的几十天。":"四篇文章，從於連隨身攜帶的兩本書、被他改寫成戰役的愛情，到瑪蒂爾德所愛的故事，以及監獄中終於停止換算的幾十天。","她爱的是那个故事":"她愛的是那個故事","每一次都是一场战役":"每一次都是一場戰役","玛蒂尔德要的不只是一个爱人，而是传奇中那个女人的位置；于连成为她故事的材料，而虚构的动机与真实的代价并不互相抵消。":"瑪蒂爾德要的不只是一個愛人，而是傳奇中那個女人的位置；於連成為她故事的材料，而虛構的動機與真實的代價並不互相抵消。","监狱撤掉了于连一生用来换算能力与位置的市场；当一切行动都不再通向未来，他第一次遇见幸福，也拒绝了最后一次表演。":"監獄撤掉了於連一生用來換算能力與位置的市場；當一切行動都不再通向未來，他第一次遇見幸福，也拒絕了最後一次表演。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这组解读把人物的野心放回复辟时代的阶级结构中，同时追问：一个人反抗的是自己在表格中的位置，还是表格本身？":"這組解讀把人物的野心放回復辟時代的階級結構中，同時追問：一個人反抗的是自己在表格中的位置，還是表格本身？"};
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

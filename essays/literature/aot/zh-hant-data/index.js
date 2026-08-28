/* Generated offline from aot/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《进击的巨人》解读":"《進擊的巨人》解讀","五篇从墙内失忆与墙外规训，读到未来记忆、地鸣与尤弥尔，追问自由是否必须包含说“不”的能力。":"五篇從牆內失憶與牆外規訓，讀到未來記憶、地鳴與尤彌爾，追問自由是否必須包含說“不”的能力。","他从来没有改过主意":"他從來沒有改過主意","他们在争一个死刑名额":"他們在爭一個死刑名額","他花了几年确保没有别的办法":"他花了幾年確保沒有別的辦法","即使把地鸣的理由说到最强，它仍通不过系统检验：防卫变成永久消灭，异议被编排，也没有独立的停止机制。":"即使把地鳴的理由說到最強，它仍通不過系統檢驗：防衛變成永久消滅，異議被編排，也沒有獨立的停止機制。","尤弥尔两千年的服从、三笠的拒绝与帕拉迪岛遥远的毁灭，共同把自由改写为拒绝自己的能力。":"尤彌爾兩千年的服從、三笠的拒絕與帕拉迪島遙遠的毀滅，共同把自由改寫為拒絕自己的能力。","弗里茨王选择退出战争；问题始于他把自己的放下，变成后来所有人都无法重选的决定。":"弗里茨王選擇退出戰爭；問題始於他把自己的放下，變成後來所有人都無法重選的決定。","没有人看守她":"沒有人看守她","简体中文保留作者底稿并校正少量设定与时间线表述；繁体中文按台湾读者习惯编辑；英文为面向熟悉完整漫画或TV动画读者的独立重写。全文包含结局剧透。":"簡體中文保留作者底稿並校正少量設定與時間線表述；繁體中文按臺灣讀者習慣編輯；英文為面向熟悉完整漫畫或TV動畫讀者的獨立重寫。全文包含結局劇透。","系列 · 五篇解读 · 文化评论":"系列 · 五篇解讀 · 文化評論","艾伦看见未来记忆片段，又制造了推动自己的部分过去，最终分不清欲望与命定的边界。":"艾倫看見未來記憶片段，又製造了推動自己的部分過去，最終分不清慾望與命定的邊界。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这五篇不把《进击的巨人》当成一道只需裁决艾伦对错的题，而把它读成一连串政治结构：墙内拿走知识，墙外保留知识却封死出口；艾伦试图打破两者，未来记忆却成为比石墙更牢的围墙。":"這五篇不把《進擊的巨人》當成一道只需裁決艾倫對錯的題，而把它讀成一連串政治結構：牆內拿走知識，牆外保留知識卻封死出口；艾倫試圖打破兩者，未來記憶卻成為比石牆更牢的圍牆。","马莱不只征用艾尔迪亚孩子，而让他们竞争牺牲，把愤怒转向同伴，并把入选变成价值证明。":"馬萊不只徵用艾爾迪亞孩子，而讓他們競爭犧牲，把憤怒轉向同伴，並把入選變成價值證明。"};
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

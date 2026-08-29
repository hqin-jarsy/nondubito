/* Generated offline from essays/film/zootopia/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《疯狂动物城》解读":"《動物方城市》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一只被制度正式接纳、却没有得到信任的兔子，读到一只把世界判词改造成职业的狐狸，以及善意取得公共后果以后，修复工作怎样开始。":"三篇從一隻被制度正式接納、卻沒有得到信任的兔子，讀到一隻把世界判詞改造成職業的狐狸，以及善意取得公共後果以後，修復工作怎樣開始。","《疯狂动物城》从一座城市的承诺开始：人人都能成就非凡。电影并没有简单揭露这句话是一场骗局。朱迪进入警队是真的，她的能力是真的，替她打开门的政策也是真的。缺少的并非入场资格，而是平等位置；这个区别组织了后来的一切。":"《動物方城市》從一座城市的承諾開始：人人都能成就非凡。電影並沒有簡單揭露這句話是一場騙局。茱蒂進入警隊是真的，她的能力是真的，替她打開門的政策也是真的。缺少的並非入場資格，而是平等位置；這個區別組織了後來的一切。","三篇从警徽、合影与贴罚单的岗位，写到尼克童年的口套和朱迪的记者会，再抵达辞职、道歉与一支被三次使用的录音笔。它们追问：没有信任的接纳意味着什么；刻板印象怎样成为一种理性的防御；以及为什么责任开始于“我没有恶意”不再足够的地方。":"三篇從警徽、合影與貼罰單的崗位，寫到胡尼克童年的口套和茱蒂的記者會，再抵達辭職、道歉與一支被三次使用的錄音筆。它們追問：沒有信任的接納意味著什麼；刻板印象怎樣成為一種理性的防禦；以及為什麼責任開始於“我沒有惡意”不再足夠的地方。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","她不是被挡在门外，是被收进去放在一个不碍事的位置上":"她不是被擋在門外，是被收進去放在一個不礙事的位置上","朱迪取得警徽、合影与正式身份；贴罚单的安排保留了这一切，却把真正有后果的工作留给别人。":"茱蒂取得警徽、合影與正式身份；貼罰單的安排保留了這一切，卻把真正有後果的工作留給別人。","英 · 简 · 繁":"英 · 簡 · 繁","一次落在他身上，一次由她说出口":"一次落在他身上，一次由她說出口","尼克曾经被套上真实口套；记者会上，朱迪又把不完整证据扩展成生物类别，让它在整座城市取得后果。":"胡尼克曾經被套上真實口套；記者會上，茱蒂又把不完整證據擴展成生物類別，讓它在整座城市取得後果。","她辞职之后做的那件事":"她辭職之後做的那件事","朱迪辞职、发现改变案情的事实，再先去寻找自己伤害过的朋友；修复既不抹去过去，也不会让过去保持原样。":"茱蒂辭職、發現改變案情的事實，再先去尋找自己傷害過的朋友；修復既不抹去過去，也不會讓過去保持原樣。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

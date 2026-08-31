/* Generated offline from neon-genesis-evangelion/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《新世纪福音战士》常被概括成一群受伤的人无法互相连接。这五篇换一个结构问题：作品给他们什么样的连接，这些连接要求什么，以及识认在什么时候会变成另一种使用。":"《新世紀福音戰士》常被概括成一群受傷的人無法互相連結。這五篇換一個結構問題：作品給他們什麼樣的連結，這些連結要求什麼，以及識認在什麼時候會變成另一種使用。","《新世纪福音战士》解读":"《新世紀福音戰士》解讀","五篇从真嗣开机的理由出发，读可替换的人、明日香不断下落的数字、碇源堂想找回的那一个人，以及既造成痛苦又让关系成为可能的墙。":"五篇從真嗣開機的理由出發，讀可替換的人、明日香不斷下落的數字、碇源堂想找回的那一個人，以及既造成痛苦又讓關係成為可能的牆。","他不是因为发现勇气才驾驶；那个可用的“不”被放在受伤的绫波丽旁边，几乎无法站住。":"他不是因為發現勇氣才駕駛；那個可用的“不”被放在受傷的綾波麗旁邊，幾乎無法站住。","他开机器的理由":"他開機器的理由","他的目标不是抽象的人类，而是碇唯；真嗣、绫波丽、NERV与整个世界都被压成回到她身边的道路。":"他的目標不是抽象的人類，而是碇唯；真嗣、綾波麗、NERV與整個世界都被壓成回到她身邊的道路。","他要的是一个人":"他要的是一個人","以TV版与《The End of Evangelion》为主要文本，不纳入新剧场版连续性。全文剧透。":"以TV版與《The End of Evangelion》為主要文字，不納入新劇場版連續性。全文劇透。","当“最好的驾驶员”承载了全部价值主张，同步率下降就不再是数据，而像对自我的判决。":"當“最好的駕駛員”承載了全部價值主張，同步率下降就不再是資料，而像對自我的判決。","新的绫波丽可以带着部分记忆醒来；机制恢复了驾驶员，也拆掉了“替换即恢复那个人”的假设。":"新的綾波麗可以帶著部分記憶醒來；機制恢復了駕駛員，也拆掉了“替換即恢復那個人”的假設。","有备用的那个人":"有備用的那個人","系列 · 5 篇解读":"系列 · 5 篇解讀","自我之间的墙造成孤独，也让相遇成为可能；真嗣选择让它回来，却没有因此得到幸福结局。":"自我之間的牆造成孤獨，也讓相遇成為可能；真嗣選擇讓它回來，卻沒有因此得到幸福結局。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","那个数字":"那個數字","那道墙":"那道牆"};
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

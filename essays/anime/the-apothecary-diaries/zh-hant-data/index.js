/* Generated offline from essays/anime/the-apothecary-diaries/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《药屋少女的呢喃》从一场绑架开始，却拒绝让猫猫此后的生活围着“战胜绑架”旋转。她只想做满年限、回到花街、尽量不被看见。一次次破坏这个计划的不是野心，而是她眼前出现了一个自己知道怎样解的问题。":"《藥屋少女的呢喃》從一場綁架開始，卻拒絕讓貓貓此後的生活圍著“戰勝綁架”旋轉。她只想做滿年限、回到花街、儘量不被看見。一次次破壞這個計劃的不是野心，而是她眼前出現了一個自己知道怎樣解的問題。","《药屋少女的呢喃》解读":"《藥屋少女的呢喃》解讀","一个地方可以压迫人，也仍装着一个人的亲友、手艺、记忆与方向；回去不等于宣告它是好地方。":"一個地方可以壓迫人，也仍裝著一個人的親友、手藝、記憶與方向；回去不等於聲明它是好地方。","一张能打开所有门的脸，也会污染每次欢迎背后的证据；猫猫让壬氏着迷的地方，正是这件工具失效之处。":"一張能開啟所有門的臉，也會汙染每次歡迎背後的證據；貓貓讓壬氏著迷的地方，正是這件工具失效之處。","五篇从猫猫主动让自己不被看见写起，读一座由稀缺注意力排序的后宫、无人分配给她的毒药兴趣、壬氏那张可被使用的脸，以及一个并不好却仍被她称作家的地方。":"五篇從貓貓主動讓自己不被看見寫起，讀一座由稀缺注意力排序的後宮、無人分配給她的毒藥興趣、壬氏那張可被使用的臉，以及一個並不好卻仍被她稱作家的地方。","他那张脸":"他那張臉","几千个人，一个人的注意力":"幾千個人，一個人的注意力","她要回去的那个地方":"她要回去的那個地方","她试毒，试给自己":"她試毒，試給自己","她进去的第一件事，是让自己不好看":"她進去的第一件事，是讓自己不好看","当几千个人的位置由一个人的稀缺注意力排序，竞争与忽视便不是偶发故障，而是设计本身的后果。":"當幾千個人的位置由一個人的稀缺注意力排序，競爭與忽視便不是偶發故障，而是設計本身的後果。","手臂上的疤换不来升迁或认可；它们标出了一种并非由周围制度为自身用途而设计的兴趣。":"手臂上的疤換不來升遷或認可；它們標出了一種並非由周圍制度為自身用途而設計的興趣。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇把前四十八集当作一个尚未结束的故事来读：人在没有选择的安排中，怎样仍保住自己的方向。本系列止于电视动画第二季；已公布的第三季与原创剧场版不参与论证。含前两季完整剧透。":"這五篇把前四十八集當作一個尚未結束的故事來讀：人在沒有選擇的安排中，怎樣仍保住自己的方向。本系列止於電視動畫第二季；已公佈的第三季與原創劇場版不參與論證。含前兩季完整劇透。","雀斑是伪装，不是羞耻；每当她知道一个问题怎样解决，沉默的代价便会超过被看见的风险。":"雀斑是偽裝，不是羞恥；每當她知道一個問題怎樣解決，沉默的代價便會超過被看見的風險。"};
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

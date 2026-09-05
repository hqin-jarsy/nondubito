/* Generated offline from essays/film/memento/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《记忆碎片》常被介绍成一部倒着讲的电影。它更深的倒置发生在证据上：莱纳德用照片、纸条与纹身替代不可靠的记忆，却忘了档案也有作者。这三篇追踪的，是一句话被写下来时藏进去的权力。":"《記憶碎片》常被介紹成一部倒著講的電影。它更深的倒置發生在證據上：萊納德用照片、紙條與紋身替代不可靠的記憶，卻忘了檔案也有作者。這三篇追蹤的，是一句話被寫下來時藏進去的權力。","《记忆碎片》解读":"《記憶碎片》解讀","三篇解读：搬到身体之外的记忆、发生在记录入口处的操纵，以及莱纳德把档案转向未来自己的那一刻。":"三篇解讀：搬到身體之外的記憶、發生在記錄入口處的操縱，以及萊納德把檔案轉向未來自己的那一刻。","他不信自己的脑子，他信自己的档案":"他不信自己的腦子，他信自己的檔案","他们只需要控制他写什么":"他們只需要控制他寫什麼","依据克里斯托弗·诺兰执导的二〇〇〇年电影《记忆碎片》；叙事顺序、关键对白与影片有意保留的不确定性已参照修订拍摄剧本及成片校订。":"依據克裡斯托弗·諾蘭執導的二〇〇〇年電影《記憶碎片》；敘事順序、關鍵對白與影片有意保留的不確定性已參照修訂拍攝劇本及成片校訂。","娜塔莉藏起笔，泰迪送入线索；两个人都在经验变成长期指令的入口处动手。":"娜塔莉藏起筆，泰迪送入線索；兩個人都在經驗變成長期指令的入口處動手。","照片、纸条与纹身可以保存判断，却无法消除最初决定记录什么的那个人及其动机。":"照片、紙條與紋身可以保存判斷，卻無法消除最初決定記錄什麼的那個人及其動機。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","莱纳德不只接收错误证据；他主动拿掉语境，让未来的自己把选定目标误认成调查结论。":"萊納德不只接收錯誤證據；他主動拿掉語境，讓未來的自己把選定目標誤認成調查結論。","那行字是他自己写的":"那行字是他自己寫的"};
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

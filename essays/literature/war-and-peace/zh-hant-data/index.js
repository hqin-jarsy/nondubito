/* Generated offline from essays/literature/war-and-peace/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《战争与和平》反复拆开两件事：人以为自己在指挥什么，以及行动实际上推动了什么。它也不肯把生命只留在历史理论里。这组文章往返于田庄、家庭、战场、俘虏队伍与小说末尾没有解决的争论。":"《戰爭與和平》反復拆開兩件事：人以為自己在指揮什麼，以及行動實際上推動了什麼。它也不肯把生命只留在歷史理論裡。這組文章往返於田莊、家庭、戰場、俘虜隊伍與小說末尾沒有解決的爭論。","《战争与和平》解读":"《戰爭與和平》解讀","一个家庭朝十二月党人的冲突敞开；紧接着的哲学论说，却要求读者把自由交给历史必然。":"一個家庭朝十二月黨人的衝突敞開；緊接著的哲學論說，卻要求讀者把自由交給歷史必然。","两个尾声":"兩個尾聲","六篇文章，从只收到自身感动的慈善、没有上锁却留住女儿的门，到安德烈偶然发生的转向、晚于行动的命令、被化成意义的卡拉塔耶夫，以及托尔斯泰彼此拉扯的两个尾声。":"六篇文章，從只收到自身感動的慈善、沒有上鎖卻留住女兒的門，到安德烈偶然發生的轉向、晚於行動的命令、被化成意義的卡拉塔耶夫，以及托爾斯泰彼此拉扯的兩個尾聲。","命令抵达时局面早已变化；图申没有受命的炮兵连决定了战局，却从战报里消失。":"命令抵達時局面早已變化；圖申沒有受命的炮兵連決定了戰局，卻從戰報裡消失。","天空、橡树、笑声与受伤的敌人，比论证更彻底地改变安德烈；而普遍之爱最后又把他带离具体生活。":"天空、橡樹、笑聲與受傷的敵人，比論證更徹底地改變安德烈；而普遍之愛最後又把他帶離具體生活。","本文依据刘辽逸译本（人民文学出版社），人名地名从该本。另有草婴、娄自良、张捷译本通行。全文剧透。":"本文依據劉遼逸譯本（人民文學出版社），人名地名從該本。另有草嬰、婁自良、張捷譯本通行。全文劇透。","玛丽亚的门没有上锁；爱、恐惧与几十年的教导，却让留下显得最像她自己的选择。":"瑪麗亞的門沒有上鎖；愛、恐懼與幾十年的教導，卻讓留下顯得最像她自己的選擇。","皮埃尔关于卡拉塔耶夫的解放性记忆，生于他继续向前、听见枪响之后；一个具体的人被化成支撑余生的意义。":"皮埃爾關於卡拉塔耶夫的解放性記憶，生於他繼續向前、聽見槍響之後；一個具體的人被化成支撐餘生的意義。","皮埃尔的改革在他看见的报告里生产了学校、医院和感恩，却在他没有走进去的生活里加重负担。":"皮埃爾的改革在他看見的報告裡生產了學校、醫院和感恩，卻在他沒有走進去的生活裡加重負擔。","系列 · 六篇解读 · 文学评论":"系列 · 六篇解讀 · 文學評論","老公爵的钟点":"老公爵的鐘點","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那声枪响他没有回头":"那聲槍響他沒有回頭","那道命令是谁下的":"那道命令是誰下的"};
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

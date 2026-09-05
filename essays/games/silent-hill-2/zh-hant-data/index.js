/* Generated offline from essays/games/silent-hill-2/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《寂静岭2》常被概括成一个关于罪疚的故事。可如果不继续追问谁真正做过什么、谁只是被别人判成有罪，以及每个人怎样改写那本无法撤销的账，“罪疚”两个字反而会把差别抹掉。":"《寂靜嶺2》常被概括成一個關於罪疚的故事。可如果不繼續追問誰真正做過什麼、誰只是被別人判成有罪，以及每個人怎樣改寫那本無法撤銷的賬，“罪疚”兩個字反而會把差別抹掉。","《寂静岭2》解读":"《寂靜嶺2》解讀","三角头让詹姆斯不断体验惩罚，剧情中反复被处决的却是玛丽亚；受苦可以像偿还，却仍然绕开那句关于事实的承认。":"三角頭讓詹姆斯不斷體驗懲罰，劇情中反復被處決的卻是瑪麗亞；受苦可以像償還，卻仍然繞開那句關於事實的承認。","两笔账":"兩筆賬","他请了一个刽子手":"他請了一個劊子手","劳拉走过普通街道，詹姆斯却看见雾、铁锈、护士与行刑者；这种差别不是道德排名，其他来访者也不是詹姆斯内心的零件。":"勞拉走過普通街道，詹姆斯卻看見霧、鐵鏽、護士與行刑者；這種差別不是道德排名，其他來訪者也不是詹姆斯內心的零件。","四篇从每个人眼中不同的寂静岭，读到安吉拉与艾迪各自错位的账、詹姆斯替自己召来的刽子手，以及随着真相回来而逐渐褪成白纸的信。":"四篇從每個人眼中不同的寂靜嶺，讀到安吉拉與艾迪各自錯位的賬、詹姆斯替自己召來的劊子手，以及隨著真相回來而逐漸褪成白紙的信。","每个人看见的不一样":"每個人看見的不一樣","白纸":"白紙","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","艾迪把自己的暴力挡在唯一能承受的自我之外，安吉拉却背着从来不属于她的判决；相反的错误让两个人都离开了自己真正做过的事。":"艾迪把自己的暴力擋在唯一能承受的自我之外，安吉拉卻背著從來不屬於她的判決；相反的錯誤讓兩個人都離開了自己真正做過的事。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这个系列不会把安吉拉和艾迪收进詹姆斯的内心，当作他的两个象征。他们各有自己的履历。镇子让几种私人世界彼此相遇，却没有把任何人的痛苦交给另一个人所有。":"這個系列不會把安吉拉和艾迪收進詹姆斯的內心，當作他的兩個象徵。他們各有自己的履歷。鎮子讓幾種私人世界彼此相遇，卻沒有把任何人的痛苦交給另一個人所有。","随着詹姆斯走近录像带，玛丽来信上的字逐渐消失；物件确实存在于道具栏，它是否曾是一封普通送达的信，作品有意没有钉死。":"隨著詹姆斯走近錄像帶，瑪麗來信上的字逐漸消失；物件確實存在於道具欄，它是否曾是一封普通送達的信，作品有意沒有釘死。"};
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

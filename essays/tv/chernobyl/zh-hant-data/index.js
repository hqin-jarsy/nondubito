/* Generated offline from essays/tv/chernobyl/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"3.6 伦琴：一个升不上去的数字":"3.6 倫琴：一個升不上去的數字","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电视剧解读":"← 電視劇解讀","《切尔诺贝利》从“谎言的代价是什么”问起。它最不安的回答，不是坏人故意用假话替换真相，而是一套制度可能在任何人决定撒谎之前，就已经失去接收事实的能力。":"《切爾諾貝利》從“謊言的代價是什麼”問起。它最不安的回答，不是壞人故意用假話替換真相，而是一套制度可能在任何人決定撒謊之前，就已經失去接收事實的能力。","《切尔诺贝利》：谎言的代价":"《切爾諾貝利》：謊言的代價","一台量程只到 3.6 的剂量计没有撒谎，却让整套系统失去说出灾难的能力；直到有人亲眼看见，而他的观察资格仍被取消。":"一臺量程只到 3.6 的劑量計沒有撒謊，卻讓整套系統失去說出災難的能力；直到有人親眼看見，而他的觀察資格仍被取消。","九十秒：用完了机器，于是用人":"九十秒：用完了機器，於是用人","他们看见了，然后被要求没看见：骗自己人":"他們看見了，然後被要求沒看見：騙自己人","六篇从一台封顶的剂量计、一座失去知情权的城市与屋顶上的九十秒，读到两个并不纯洁的人，以及一部讲真相的剧自身欠下的那笔账。":"六篇從一臺封頂的劑量計、一座失去知情權的城市與屋頂上的九十秒，讀到兩個並不純潔的人，以及一部講真相的劇自身欠下的那筆賬。","列加索夫既沉默过十一年，也最终承担了说出的代价；这两件事不能互相取消，正因如此才构成一个完整的人。":"列加索夫既沉默過十一年，也最終承擔了說出的代價；這兩件事不能互相取消，正因如此才構成一個完整的人。","前五篇暂时站在剧集内部，从仪器、机构与被调用的人写到两个不纯洁、却重新为判断打开一点位置的人。第六篇再把镜头转向剧集自身：为了让这个故事能够被看见，它压缩了谁、创造了谁，又把哪些复杂的人改写成了功能。全剧剧透。":"前五篇暫時站在劇集內部，從儀器、機構與被呼叫的人寫到兩個不純潔、卻重新為判斷開啟一點位置的人。第六篇再把鏡頭轉向劇集自身：為了讓這個故事能夠被看見，它壓縮了誰、創造了誰，又把哪些複雜的人改寫成了功能。全劇劇透。","普里皮亚季的电话线为何先被切断：当“避免恐慌”由知情者替不知情者决定，保护怎样变成了剥夺自救资格。":"普里皮亞季的電話線為何先被切斷：當“避免恐慌”由知情者替不知情者決定，保護怎樣變成了剝奪自救資格。","机器人坏掉之后，三千八百二十八个人被送上屋顶，每人九十秒；另一边，矿工在听见实情之后自己说“我们去”。":"機器人壞掉之後，三千八百二十八個人被送上屋頂，每人九十秒；另一邊，礦工在聽見實情之後自己說“我們去”。","系列 · 六篇 · 电视剧解读":"系列 · 六篇 · 電視劇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文重写 · 简 / 繁 · 电视剧解读":"英文重寫 · 簡 / 繁 · 電視劇解讀","英文重写 · 简体 · 繁体":"英文重寫 · 簡體 · 繁體","谎言的代价：这部剧自己的那一笔":"謊言的代價：這部劇自己的那一筆","谢尔比纳没有离开体制，也没有成为纯粹英雄；他只是从一句“再说一遍，我没听懂”开始，改变了自己占据那个位置的方式。":"謝爾比納沒有離開體制，也沒有成為純粹英雄；他只是從一句“再說一遍，我沒聽懂”開始，改變了自己佔據那個位置的方式。","谢尔比纳：一个位置怎么被重新打开":"謝爾比納：一個位置怎麼被重新開啟","霍缪克、法庭、迪亚特洛夫与几处史实改写：一部反对把人压成功能的剧，为什么也不得不把人压成功能。":"霍繆克、法庭、迪亞特洛夫與幾處史實改寫：一部反對把人壓成功能的劇，為什麼也不得不把人壓成功能。"};
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

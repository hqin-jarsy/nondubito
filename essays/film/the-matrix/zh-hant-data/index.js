/* Generated offline from essays/film/the-matrix/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《黑客帝国》解读":"《駭客任務》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","三篇从一套必须让电池觉得自己能够选择的系统，读到信息并不完整的红药丸，也读到尼奥怎样把计划里没有的第三条路带回房间。":"三篇從一套必須讓電池覺得自己能夠選擇的系統，讀到信息並不完整的紅藥丸，也讀到尼歐怎樣把計劃里沒有的第三條路帶回房間。","《黑客帝国》通常被读作从幻觉中解放。这里先追问另一个问题：什么能让解放成为主体亲自作出的行动，而不是另一段被设计好的体验？机器所谓的完美世界无法维持母体；续集关于选择的解释，则让我们看见“像是我在生活”的感觉为何重要。":"《駭客任務》通常被讀作從幻覺中解放。這裡先追問另一個問題：什麼能讓解放成為主體親自作出的行動，而不是另一段被設計好的體驗？機器所謂的完美世界無法維持母體；續集關於選擇的解釋，則讓我們看見“像是我在生活”的感覺為何重要。","墨菲斯真诚地提供真相，尼奥却不可能预先知道红药丸后面的具体生活。后来，当现成方案要求牺牲墨菲斯时，他提出一个从未被列入计划的选项。这里追踪的，是人怎样从挑选走向负责任地创造可能。":"莫菲斯真誠地提供真相，尼歐卻不可能預先知道紅藥丸後面的具體生活。後來，當現成方案要求犧牲莫菲斯時，他提出一個從未被列入計劃的選項。這裡追蹤的，是人怎樣從挑選走向負責任地創造可能。","沃卓斯基一九九九年《黑客帝国》。全片剧透。":"沃卓斯基一九九九年《駭客任務》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","电池为什么必须觉得自己自由":"電池為什麼必須覺得自己自由","母体把人体折算成能源，它的提取系统却只有在意识保留主体感的情况下才能运转。":"母體把人體折算成能源，它的提取系統卻只有在意識保留主體感的情況下才能運轉。","英 · 简 · 繁":"英 · 簡 · 繁","两颗药丸是别人拿出来的":"兩顆藥丸是別人拿出來的","尼奥自愿伸手，具体后果却未被说明，而解放以后也没有一条得到承认的回程。":"尼歐自願伸手，具體後果卻未被說明，而解放以後也沒有一條得到承認的回程。","他把第三条路带回了房间":"他把第三條路帶回了房間","尼奥提出计划中没有的救援方案，也没有把墨菲斯愿意牺牲直接当成旁人必须执行的命令。":"尼歐提出計劃中沒有的救援方案，也沒有把莫菲斯願意犧牲直接當成旁人必須執行的命令。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

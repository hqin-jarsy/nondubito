/* Generated offline from essays/film/the-matrix/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《黑客帝国》解读":"《駭客任務》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一套必须让电池觉得自己是主体的系统，读到后果由他人控制的红药丸选择，以及尼奥第一次不再挑选现成选项、而是自己创造一个选项。":"三篇從一套必須讓電池覺得自己是主體的系統，讀到後果由他人控制的紅藥丸選擇，以及尼歐第一次不再挑選現成選項、而是自己創造一個選項。","《黑客帝国》通常被读作从幻觉中解放。这里先追问另一个问题：什么能让解放成为主体亲自作出的行动，而不是另一段被设计好的体验？母体无法只靠舒适让人类继续活着，它必须复制“是我在选择”的感觉形状。":"《駭客任務》通常被讀作從幻覺中解放。這裡先追問另一個問題：什麼能讓解放成為主體親自作出的行動，而不是另一段被設計好的體驗？母體無法只靠舒適讓人類繼續活著，它必須複製“是我在選擇”的感覺形狀。","墨菲斯真诚地提供真相，尼奥却不可能知道红药丸后面那种生活。后来，当所有现成方案都要求牺牲墨菲斯时，尼奥提出一个从未被提供的选项。从挑选到创作，才是这组文章要追踪的线。":"莫菲斯真誠地提供真相，尼歐卻不可能知道紅藥丸後面那種生活。後來，當所有現成方案都要求犧牲莫菲斯時，尼歐提出一個從未被提供的選項。從挑選到創作，才是這組文章要追蹤的線。","沃卓斯基一九九九年《黑客帝国》。全片剧透。":"沃卓斯基一九九九年《駭客任務》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他们造过一个完美世界，没有人接受":"他們造過一個完美世界，沒有人接受","母体把人体折算成能源，它的提取系统却只有在意识保留主体感的情况下才能运转。":"母體把人體折算成能源，它的提取系統卻只有在意識保留主體感的情況下才能運轉。","英 · 简 · 繁":"英 · 簡 · 繁","两颗药丸是别人拿出来的":"兩顆藥丸是別人拿出來的","尼奥自愿伸手，选项、信息、时间与不可逆后果却全由墨菲斯控制。":"尼歐自願伸手，選項、資訊、時間與不可逆後果卻全由莫菲斯控制。","他不接受一个人自愿成为手段":"他不接受一個人自願成為手段","尼奥没有预言、概率或许可仍去救墨菲斯，拒绝让一个自愿的牺牲耗尽另一个人的全部意义。":"尼歐沒有預言、概率或許可仍去救莫菲斯，拒絕讓一個自願的犧牲耗盡另一個人的全部意義。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

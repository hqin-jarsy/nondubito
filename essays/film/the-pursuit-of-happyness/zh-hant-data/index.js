/* Generated offline from essays/film/the-pursuit-of-happyness/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《当幸福来敲门》解读":"《當幸福來敲門》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一笔失败投资所化成的机器，读到六个月里怎样让明天仍有可能，以及克里斯·加德纳行动的分量为何不能依赖最后那份录用。":"三篇從一筆失敗投資所化成的機器，讀到六個月裡怎樣讓明天仍有可能，以及克裡斯·加德納行動的分量為何不能依賴最後那份錄用。","这部电影通常被包装成成功故事。这里保留成功，却不让成功倒过来解释前面的一切。克里斯从一次错误的商业判断开始，接受无薪而风险极高的实习，隐瞒无家可归的处境，也在许多没有可见进展的夜晚照料孩子。":"這部電影通常被包裝成成功故事。這裡保留成功，卻不讓成功倒過來解釋前面的一切。克裡斯從一次錯誤的商業判斷開始，接受無薪而風險極高的實習，隱瞞無家可歸的處境，也在許多沒有可見進展的夜晚照料孩子。","重点既不是努力必有回报，也不是结果毫不重要。日常行动有两种不同的力量：它可以当下保存一个人和一段关系，也可以让一个仍不确定的未来继续保持开放。":"重點既不是努力必有回報，也不是結果毫不重要。日常行動有兩種不同的力量：它可以當下保存一個人和一段關係，也可以讓一個仍不確定的未來繼續保持開放。","加布里埃莱·穆奇诺二〇〇六年《当幸福来敲门》。全片剧透。":"加布裡埃萊·穆奇諾二〇〇六年《當幸福來敲門》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他全部的钱，压在一台没人要的机器上":"他全部的錢，壓在一台沒人要的機器上","克里斯并非命定的成功者，而是一个必须为错误投资负责、每天把它扛过城市的推销员。":"克裡斯並非命定的成功者，而是一個必須為錯誤投資負責、每天把它扛過城市的推銷員。","英 · 简 · 繁":"英 · 簡 · 繁","他每天做的事，是让明天还能接着来":"他每天做的事，是讓明天還能接著來","电话、收容所队伍、拘留所与厕所地板并不直接通向成功，它们只是让父子俩继续进入下一天。":"電話、收容所隊伍、拘留所與廁所地板並不直接通向成功，它們只是讓父子倆繼續進入下一天。","如果那个电话没打来，这一年还成立吗":"如果那個電話沒打來，這一年還成立嗎","最后的录用当然重要，却不能倒过来创造那些早已保护孩子、保存可能性的行动之尊严。":"最後的錄用當然重要，卻不能倒過來創造那些早已保護孩子、保存可能性的行動之尊嚴。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

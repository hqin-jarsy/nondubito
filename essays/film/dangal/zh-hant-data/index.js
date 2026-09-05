/* Generated offline from essays/film/dangal/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《摔跤吧！爸爸》解读":"《摔跤吧！爸爸》解讀","《摔跤吧！爸爸》让解放从强迫内部开始：父亲用一套强加的训练，帮女儿逃出另一种更封闭的强加。这三篇既不让金牌倒过来证明所有手段正确，也不因起点并非自选，就否定吉塔和芭比塔后来对这条路取得的主动权。":"《摔跤吧！爸爸》讓解放從強迫內部開始：父親用一套強加的訓練，幫女兒逃出另一種更封閉的強加。這三篇既不讓金牌倒過來證明所有手段正確，也不因起點並非自選，就否定吉塔和芭比塔後來對這條路取得的主動權。","一个十四岁的新人说了一段话":"一個十四歲的新人說了一段話","三篇解读：被继承的金牌梦想、重新照亮可选未来的十四岁新娘，以及让奖牌最终属于吉塔的虚构空座位。":"三篇解讀：被繼承的金牌夢想、重新照亮可選未來的十四歲新娘，以及讓獎牌最終屬於吉塔的虛構空座位。","依据涅提·蒂瓦里执导的二〇一六年电影《摔跤吧！爸爸》；文章分析电影叙事，同时明确区分被大幅戏剧化的国家队教练冲突、英联邦运动会决赛与吉塔·珀尕的真实比赛。":"依據涅提·蒂瓦裡執導的二〇一六年電影《摔跤吧！爸爸》；文章分析電影敘事，同時明確區分被大幅戲劇化的國家隊教練衝突、英聯邦運動會決賽與吉塔·珀尕的真實比賽。","吉塔离开、反驳、失利再返回，电影才虚构那张空座位；完成论证的情节必须与真实历史分开。":"吉塔離開、反駁、失利再返回，電影才虛構那張空座位；完成論證的情節必須與真實歷史分開。","她抬头看了一眼，那个位置是空的":"她抬頭看了一眼，那個位置是空的","婚礼揭开所谓正常生活也是一条被安排的路；女孩主动起床的早晨很重要，却不能倒签此前一年的同意书。":"婚禮揭開所謂正常生活也是一條被安排的路；女孩主動起床的早晨很重要，卻不能倒簽此前一年的同意書。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那块金牌本来是他自己的":"那塊金牌本來是他自己的","马哈维亚看见村庄拒绝看见的能力，却首先把它们当成完成一项先于女儿存在的梦想的工具。":"馬哈維亞看見村莊拒絕看見的能力，卻首先把它們當成完成一項先於女兒存在的夢想的工具。"};
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

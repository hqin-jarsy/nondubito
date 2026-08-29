/* Generated offline from essays/film/spirited-away/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《千与千寻》解读":"《千與千尋》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一份收走名字的契约，读到无脸男如何学会交换的语言，以及一个孩子如何用记忆复原澡堂变成财产的东西。":"三篇從一份收走名字的契約，讀到無臉男如何學會交換的語言，以及一個孩子如何用記憶復原澡堂變成財產的東西。","《千与千寻》从一个不愿走进隧道的孩子开始，却把她放进了一连串不理会她拒绝的制度里。父母相信支付能力就能带来占有资格；汤婆婆的澡堂用劳动与营收衡量存在；无脸男则学会金子可以召来人群。每套制度都提供一张不同的换算表，决定谁可以吃、可以留下、可以说话、可以被看见。":"《千與千尋》從一個不願走進隧道的孩子開始，卻把她放進了一連串不理會她拒絕的制度裡。父母相信支付能力就能帶來佔有資格；湯婆婆的澡堂用勞動與營收衡量存在；無臉男則學會金子可以召來人群。每套制度都提供一張不同的換算表，決定誰可以吃、可以留下、可以說話、可以被看見。","千寻没有成为其中最强的参与者，却仍然走了出去。她把一个目的保留在澡堂的账本之外，记住权力删减或抹去的名字，也一次次在还不知道对方能回报什么之前先作回应。为雨中的人开一扇门、替另一个人记住名字、拒绝把父母认成牲畜——这些极小的动作，让她不必假装危险不存在，也没有接受这个世界为她写好的算法。":"千尋沒有成為其中最強的參與者，卻仍然走了出去。她把一個目的保留在澡堂的賬本之外，記住權力刪減或抹去的名字，也一次次在還不知道對方能回報什麼之前先作回應。為雨中的人開一扇門、替另一個人記住名字、拒絕把父母認成牲畜——這些極小的動作，讓她不必假裝危險不存在，也沒有接受這個世界為她寫好的算法。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","签下名字的那一刻，她就不叫荻野千寻了":"簽下名字的那一刻，她就不叫荻野千尋了","汤婆婆的契约在形式上自愿，在处境中却没有第二个选项；名字一旦被收走，工作便能抹掉一个人回家的路线。":"湯婆婆的契約在形式上自願，在處境中卻沒有第二個選項；名字一旦被收走，工作便能抹掉一個人回家的路線。","英 · 简 · 繁":"英 · 簡 · 繁","无脸男手里全是金子，可他什么都没有":"無臉男手裡全是金子，可他什麼都沒有","无脸男学会用物品、金子、食欲和借来的声音换取关注；千寻最后给他的，正是他一直想购买的那种接纳。":"無臉男學會用物品、金子、食慾和借來的聲音換取關注；千尋最後給他的，正是他一直想購買的那種接納。","她记得自己的名字，也替别人记住了他的":"她記得自己的名字，也替別人記住了他的","千寻守住自己的名字，也替白龙保管他的名字；最后一关，她靠的不是认出哪两头猪，而是拒绝把父母认成东西。":"千尋守住自己的名字，也替白龍保管他的名字；最後一關，她靠的不是認出哪兩頭豬，而是拒絕把父母認成東西。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  Object.assign(variants, {"千寻没有成为其中最强的参与者，却仍然走了出去。她把一个目的保留在澡堂的账本之外，记住权力删减或抹去的名字，也一次次在还不知道对方能回报什么之前先作回应。为雨中的人开一扇门、替另一个人记住名字、拒绝把父母认成牲畜——这些极小的动作，让她不必假装危险不存在，也没有接受这个世界为她写好的算法。":"千尋沒有成為其中最強的參與者，卻仍然走了出去。她把一個目的保留在澡堂的帳本之外，記住權力刪減或抹去的名字，也一次次在還不知道對方能回報什麼之前先作回應。為雨中的人開一扇門、替另一個人記住名字、拒絕把父母認成牲畜——這些極小的動作，讓她不必假裝危險不存在，也沒有接受這個世界為她寫好的演算法。"});
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

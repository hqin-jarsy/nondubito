/* Generated offline from essays/film/a-brighter-summer-day/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《牯岭街少年杀人事件》解读":"《牯嶺街少年殺人事件》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一个少年寻找能站住的规矩，读到父亲在政治审讯后再也无法活进自己教过的原则，以及一个女孩怎样拒绝成为别人拯救计划里的对象。":"三篇從一個少年尋找能站住的規矩，讀到父親在政治審訊後再也無法活進自己教過的原則，以及一個女孩怎樣拒絕成為別人拯救計畫裡的對象。","杨德昌的电影写的是一批一九四九年前后来台、原以为迁徙只是暂时的大陆家庭。他们的子女继承了学校、口音、帮派与希望，却再也感不到这些东西有稳定权威。小四拿着手电筒穿过黑暗，仿佛一束小光能找到一条始终讲得通的规矩。":"楊德昌的電影寫的是一批一九四九年前後來台、原以為遷徙只是暫時的大陸家庭。他們的子女繼承了學校、口音、幫派與希望，卻再也感不到這些東西有穩定權威。小四拿著手電筒穿過黑暗，彷彿一束小光能找到一條始終講得通的規矩。","悲剧并非因为没有规则。学校纪律、帮派忠诚、家庭伦理、国家权力与爱情理想彼此竞争；小四最终的错误，是把另一个人变成他最后那条法必须成功的地方。":"悲劇並非因為沒有規則。學校紀律、幫派忠誠、家庭倫理、國家權力與愛情理想彼此競爭；小四最終的錯誤，是把另一個人變成他最後那條法必須成功的地方。","杨德昌一九九一年《牯岭街少年杀人事件》。全片剧透。":"楊德昌一九九一年《牯嶺街少年殺人事件》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他一直在找一条讲得通的规矩":"他一直在找一條講得通的規矩","学校不断改变尺度，帮派提供残酷的清楚，而小四带着偷来的光穿过一个规矩无法保持一致的世界。":"學校不斷改變尺度，幫派提供殘酷的清楚，而小四帶著偷來的光穿過一個規矩無法保持一致的世界。","英 · 简 · 繁":"英 · 簡 · 繁","他去了两次学校":"他去了兩次學校","小四的父亲第一次按原则辩护，经历白色恐怖审讯后却向同一所学校道歉；儿子亲眼看见了坍塌。":"小四的父親第一次按原則辯護，經歷白色恐怖審訊後卻向同一所學校道歉；兒子親眼看見了坍塌。","她说完那句话，他动了刀":"她說完那句話，他動了刀","小明拒绝按小四的规则变成可被拯救的人；当另一个人不肯证明他的法仍成立时，暴力开始。":"小明拒絕按小四的規則變成可被拯救的人；當另一個人不肯證明他的法仍成立時，暴力開始。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

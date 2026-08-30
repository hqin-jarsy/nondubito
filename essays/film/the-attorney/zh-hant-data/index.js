/* Generated offline from essays/film/the-attorney/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《辩护人》解读":"《正義辯護人》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一个完全没有理由成为异议者的商业律师，读到一张熟悉的脸如何让抽象知识失效，以及一场每项证据都能赢、判决却依旧输掉的政治审判。":"三篇從一個完全沒有理由成為異議者的商業律師，讀到一張熟悉的臉如何讓抽象知識失效，以及一場每項證據都能贏、判決卻依舊輸掉的政治審判。","《辩护人》没有让主人公在回忆中提前成圣。宋佑硕起初靠房产登记业务挣钱，为没有精英学历却能白手起家而骄傲，也反感学生运动。这个开头不是该删去的尴尬，正是它赋予后来选择以分量。":"《正義辯護人》沒有讓主人公在回憶中提前成聖。宋佑碩起初靠房產登記業務掙錢，為沒有精英學歷卻能白手起家而驕傲，也反感學生運動。這個開頭不是該刪去的尷尬，正是它賦予後來選擇以分量。","三篇追踪的是知识对象怎样改变：“政治犯”可以只是一个类别，朴镇宇受伤的脸却不行；继而追问，当证据、程序与宪法语言都被法庭听见、却不被允许支配裁判时，辩护究竟还意味着什么。":"三篇追蹤的是知識對象怎樣改變：“政治犯”可以只是一個類別，樸鎮宇受傷的臉卻不行；繼而追問，當證據、程序與憲法語言都被法庭聽見、卻不被允許支配裁判時，辯護究竟還意味著什麼。","杨宇硕二〇一三年《辩护人》。全片剧透。":"楊宇碩二〇一三年《正義辯護人》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","故事开始时，他完全没有理由做后来的事":"故事開始時，他完全沒有理由做後來的事","宋佑硕是商业上成功、政治上怀疑、又被法律精英排斥的局外人，完全不是命定的人权英雄。":"宋佑碩是商業上成功、政治上懷疑、又被法律精英排斥的局外人，完全不是命定的人權英雄。","英 · 简 · 繁":"英 · 簡 · 繁","他从那间屋子出来，蹲在走廊上吐了":"他從那間屋子出來，蹲在走廊上吐了","宋佑硕早已听过国家暴力的传闻；看见朴镇宇受伤的脸后，政治类别变成了一个再也无法归开的人。":"宋佑碩早已聽過國家暴力的傳聞；看見樸鎮宇受傷的臉後，政治類別變成了一個再也無法歸開的人。","他赢了每一个回合，输掉了这场审判":"他贏了每一個回合，輸掉了這場審判","书、非法拘禁、刑讯证据与宪法条文全都支持辩方，判决却暴露出一间能听见事实却不受事实支配的法庭。":"書、非法拘禁、刑訊證據與憲法條文全都支持辯方，判決卻暴露出一間能聽見事實卻不受事實支配的法庭。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

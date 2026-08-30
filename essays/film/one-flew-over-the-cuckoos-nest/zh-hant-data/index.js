/* Generated offline from essays/film/one-flew-over-the-cuckoos-nest/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《飞越疯人院》解读":"《飛越杜鵑窩》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一个把判断藏进流程的职位，读到一个并不清白的人怎样因普通快乐而成为越轨者，以及沉默的病人如何保存了足够的自己，终于离开。":"三篇從一個把判斷藏進流程的職位，讀到一個並不清白的人怎樣因普通快樂而成為越軌者，以及沉默的病人如何保存了足夠的自己，終於離開。","这里不把电影简化成好反叛者与坏护士的对决。麦克墨菲会操控人、会使用暴力，也因与未成年人发生关系而服刑；拉契特护士的许多话则来自可辨认的治疗与管理职责。更尖锐的问题是，他们各自的位置允许什么。":"這裡不把電影簡化成好反叛者與壞護士的對決。麥克墨菲會操控人、會使用暴力，也因與未成年人發生關係而服刑；拉契特護士的許多話則來自可辨認的治療與管理職責。更尖銳的問題是，他們各自的位置允許什麼。","病房让秩序易于衡量，却让康复难以衡量；发言变成记录，自愿入院者放弃艰难的选择，而一个官员也可以在完全照章办事时伤害具体的人，只因她没有再问对方是否承受得住。":"病房讓秩序易於衡量，卻讓康復難以衡量；發言變成記錄，自願入院者放棄艱難的選擇，而一個官員也可以在完全照章辦事時傷害具體的人，只因她沒有再問對方是否承受得住。","米洛斯·福尔曼一九七五年《飞越疯人院》。全片剧透。":"米洛斯·福爾曼一九七五年《飛越杜鵑窩》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","她从来没有说过“我认为”":"她從來沒有說過“我認為”","护士的职位控制谁能说话、发言如何变成记录、拘束何时结束，并把判断呈现成无人作出的流程。":"護士的職位控制誰能說話、發言如何變成記錄、拘束何時結束，並把判斷呈現成無人作出的流程。","英 · 简 · 繁":"英 · 簡 · 繁","他没有对抗谁，只是在过自己的日子":"他沒有對抗誰，只是在過自己的日子","一场关着电视的球赛说明，病房无法容纳未经管理的快乐，即使没有一条明文规则真正被违反。":"一場關著電視的球賽說明，病房無法容納未經管理的快樂，即使沒有一條明文規則真正被違反。","换一个人坐进去，一切照旧":"換一個人坐進去，一切照舊","酋长的沉默让他留在记录之外；比利之死显出无判断规则的代价，而逃跑则是秘密保存下来的自我之使用。":"酋長的沉默讓他留在記錄之外；比利之死顯出無判斷規則的代價，而逃跑則是秘密保存下來的自我之使用。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

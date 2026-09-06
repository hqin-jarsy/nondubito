/* Generated offline from essays/film/one-flew-over-the-cuckoos-nest/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《飞越疯人院》解读":"《飛越杜鵑窩》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","三篇从程序怎样隐藏判断的作者，读到病房为何容不下未经管理的快乐，也读到一次恢复行动能力却并不纯净的逃离。":"三篇從程序怎樣隱藏判斷的作者，讀到病房為何容不下未經管理的快樂，也讀到一次恢復行動能力卻並不純淨的逃離。","这里不把电影简化成好反叛者与坏护士的对决。麦克墨菲会操控人、会使用暴力，也因与未成年人发生关系而服刑；拉契特护士的许多话则来自可辨认的治疗与管理职责。更尖锐的问题是，他们各自的位置允许什么。":"這裡不把電影簡化成好反叛者與壞護士的對決。麥克墨菲會操控人、會使用暴力，也因與未成年人發生關係而服刑；拉契特護士的許多話則來自可辨認的治療與管理職責。更尖銳的問題是，他們各自的位置允許什麼。","病房让秩序易于衡量，却让康复难以衡量；发言变成记录，自愿入院不等于已有离开的能力，而专业语言也可能把一次精确的强迫伪装成中性的关心。":"病房讓秩序易於衡量，卻讓康復難以衡量；發言變成記錄，自願入院不等於已有離開的能力，而專業語言也可能把一次精確的強迫偽裝成中性的關心。","米洛斯·福尔曼一九七五年《飞越疯人院》。全片剧透。":"米洛斯·福爾曼一九七五年《飛越杜鵑窩》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","当“我认为”藏进流程":"當“我認為”藏進流程","护士的职位控制谁能说话、发言如何变成记录、拘束何时结束，并把判断呈现成无人作出的流程。":"護士的職位控制誰能說話、發言如何變成記錄、拘束何時結束，並把判斷呈現成無人作出的流程。","英 · 简 · 繁":"英 · 簡 · 繁","没有信号，比赛仍然发生了":"沒有信號，比賽仍然發生了","一场关着电视的球赛说明，病房无法容纳未经管理的快乐，即使没有一条明文规则真正被违反。":"一場關著電視的球賽說明，病房無法容納未經管理的快樂，即使沒有一條明文規則真正被違反。","换一个人坐进去，一切照旧":"換一個人坐進去，一切照舊","沉默替酋长保存了一层防御，也让他失去关系；最后的逃离恢复了行动，却没有变成一个干净的道德胜利。":"沈默替酋長保存了一層防禦，也讓他失去關係；最後的逃離恢復了行動，卻沒有變成一個乾淨的道德勝利。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

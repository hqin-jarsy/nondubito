/* Generated offline from essays/film/inception/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《盗梦空间》解读":"《盜夢空間》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从柯布植入茉儿的念头，读到一场被制造的和解怎样让费舍尔在自由感中完成操控，以及柯布最终为何把仍在旋转的陀螺留在身后。":"三篇從柯布植入茉兒的念頭，讀到一場被製造的和解怎樣讓費舍爾在自由感中完成操控，以及柯布最終為何把仍在旋轉的陀螺留在身後。","《盗梦空间》用层层梦境、折叠城市与伸缩时间制造奇观，但它最深的问题其实是“作者身份”：一个念头何时才算是我的？如果别人替我设计了抵达结论的整条情感路径，我的选择还算自由吗？当检验现实的工具已经与制造怀疑的那次干预绑在一起，人还能向它索取什么确定性？":"《盜夢空間》用層層夢境、折疊城市與伸縮時間製造奇觀，但它最深的問題其實是“作者身份”：一個念頭何時才算是我的？如果別人替我設計了抵達結論的整條情感路徑，我的選擇還算自由嗎？當檢驗現實的工具已經與製造懷疑的那次干預綁在一起，人還能向它索取什麼確定性？","这三篇沿着同一个问题阅读三个人。茉儿让我们看见，一次救援如何摧毁另一个人自我纠错的条件；费舍尔让我们看见，显得善意的操控为什么可能比伤害更有效；而柯布最后从陀螺转向孩子，并没有解开电影的本体论谜题，却改变了他愿意向什么索取确定性，以及他终于愿意把注意力交给谁。":"這三篇沿著同一個問題閱讀三個人。茉兒讓我們看見，一次救援如何摧毀另一個人自我糾錯的條件；費舍爾讓我們看見，顯得善意的操控為什麼可能比傷害更有效；而柯布最後從陀螺轉向孩子，並沒有解開電影的本體論謎題，卻改變了他願意向什麼索取確定性，以及他終於願意把注意力交給誰。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他种进她心里的那个念头":"他種進她心裡的那個念頭","柯布想把茉儿带回现实，却植入了一个能够吞掉此后一切现实检验的怀疑。善意无法归还他暗中夺走的判断作者身份。":"柯布想把茉兒帶回現實，卻植入了一個能夠吞掉此後一切現實檢驗的懷疑。善意無法歸還他暗中奪走的判斷作者身份。","英 · 简 · 繁":"英 · 簡 · 繁","最温柔的那个版本最有效":"最溫柔的那個版本最有效","费舍尔在一场被设计的父子和解中感到解脱，并把斋藤的命令体验成自己的发现。照护可以改善操控，却不能替代同意。":"費舍爾在一場被設計的父子和解中感到解脫，並把齋藤的命令體驗成自己的發現。照護可以改善操控，卻不能替代同意。","结尾没有证明柯布已经醒来；它让他离开一套早已与罪疚纠缠的确定性仪式，转身进入一段可以实际参与的关系。":"結尾沒有證明柯布已經醒來；它讓他離開一套早已與罪疚糾纏的確定性儀式，轉身進入一段可以實際參與的關係。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

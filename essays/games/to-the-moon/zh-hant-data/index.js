/* Generated offline from essays/games/to-the-moon/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《去月球》把一件近乎不可思议的事写成日常工作：两名技术人员进入临终者的记忆，替他补成想要的一生。真正的问题并不是技术有没有成功，而是当愿望还在、愿望的来路却被拿走之后，“成功”究竟意味着什么。":"《去月球》把一件近乎不可思議的事寫成日常工作：兩名技術人員進入臨終者的記憶，替他補成想要的一生。真正的問題並不是技術有沒有成功，而是當願望還在、願望的來路卻被拿走之後，“成功”究竟意味著什麼。","《去月球》解读":"《去月球》解讀","一段他没有过的人生":"一段他沒有過的人生","为了把约翰尼送上月球，医生必须拿走那个愿望其实早已兑现的一生；结果仁慈而成功，却无法因此变得没有代价。":"為了把約翰尼送上月球，醫生必須拿走那個願望其實早已兌現的一生；結果仁慈而成功，卻無法因此變得沒有代價。","他为什么说不出来":"他為什麼說不出來","四篇从一位老人说不出来路的愿望，读到被药物封住的童年、折满一屋的纸兔子，以及替一个人安排幸福记忆时无法消失的代价。":"四篇從一位老人說不出來路的願望，讀到被藥物封住的童年、折滿一屋的紙兔子，以及替一個人安排幸福記憶時無法消失的代價。","第二次手术":"第二次手術","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","约翰尼的愿望来自童年的一个约定；游戏里的药物替他隔开了无法承受的记忆，也把紧挨着它的那个普通夜晚一并封住。":"約翰尼的願望來自童年的一個約定；遊戲裡的藥物替他隔開了無法承受的記憶，也把緊挨著它的那個普通夜晚一並封住。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","莉娃用几十年试着把一段共同记忆还给约翰尼，却不肯只把答案告诉他；她发出的信号极其准确，接收它的人却无法读懂。":"莉娃用幾十年試著把一段共同記憶還給約翰尼，卻不肯只把答案告訴他；她發出的信號極其準確，接收它的人卻無法讀懂。","西格蒙德公司能替临终者改写记忆、兑现遗愿；约翰尼确实同意了，却无法解释自己交给公司的那个愿望从何而来。":"西格蒙德公司能替臨終者改寫記憶、兌現遺願；約翰尼確實同意了，卻無法解釋自己交給公司的那個願望從何而來。","这四篇沿着约翰尼、莉娃、伊娃与尼尔的选择往回走，不替结局作简单裁决。手术既有仁慈，也有侵犯；作品的力量正在于两面都没有被抹平。":"這四篇沿著約翰尼、莉娃、伊娃與尼爾的選擇往回走，不替結局作簡單裁決。手術既有仁慈，也有侵犯；作品的力量正在於兩面都沒有被抹平。"};
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

/* Generated offline from essays/film/infernal-affairs/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《无间道》解读":"《無間道》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇写一个公共身份被抹掉的警察、一个公共履历毫无污点的黑帮卧底，以及那些能够决定两人各自证明什么、却不能决定两人各自知道什么的证据。":"三篇寫一個公共身分被抹掉的警察、一個公共履歷毫無污點的黑幫臥底，以及那些能夠決定兩人各自證明什麼、卻不能決定兩人各自知道什麼的證據。","《无间道》常被概括成两个互换身份的人。这个对称足以驱动一部惊险片，却不足以解决它的道德问题。陈永仁为了警方使用虚假身份，希望拿回普通人的生活；刘建明为了韩琛扮演警察，希望自己已经建成的生活从此成为事实。一个要求历史得到承认，另一个要求摆脱历史。":"《無間道》常被概括成兩個互換身分的人。這個對稱足以驅動一部驚險片，卻不足以解決它的道德問題。陳永仁為了警方使用虛假身分，希望拿回普通人的生活；劉建明為了韓琛扮演警察，希望自己已經建成的生活從此成為事實。一個要求歷史得到承認，另一個要求擺脫歷史。","三篇从陈永仁被删除的警校记录与强制心理治疗，写到刘建明干净的个人档案和他亲手删除的卧底资料，再抵达天台反问，以及六个月后从已故叶校长遗物中发现的另一份档案。它们追问：自我知道与法律身份有什么区别；为什么今天想改变，不能靠消灭昨天的权利主张者来购买；以及一份迟来的记录怎样能够救回事实，却无法修复被事实抛弃的那段人生。":"三篇從陳永仁被刪除的警校記錄與強制心理治療，寫到劉建明乾淨的個人檔案和他親手刪除的臥底資料，再抵達天台反問，以及六個月後從已故葉校長遺物中發現的另一份檔案。它們追問：自我知道與法律身分有什麼區別；為什麼今天想改變，不能靠消滅昨天的權利主張者來購買；以及一份遲來的記錄怎樣能夠救回事實，卻無法修復被事實拋棄的那段人生。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他知道自己是谁，而这件事他说了不算":"他知道自己是誰，而這件事他說了不算","陈永仁始终承担警察任务，所有公共痕迹却都把他写成罪犯；知道自己是谁，并不等于拥有证明自己的权力。":"陳永仁始終承擔警察任務，所有公共痕跡卻都把他寫成罪犯；知道自己是誰，並不等於擁有證明自己的權力。","英 · 简 · 繁":"英 · 簡 · 繁","他把能改的全改了，只有一样改不掉":"他把能改的全改了，只有一樣改不掉","刘建明拥有一份干净履历，也想成为履历描述的警察；过去却以一个个仍能向他提出要求的人回来。":"劉建明擁有一份乾淨履歷，也想成為履歷描述的警察；過去卻以一個個仍能向他提出要求的人回來。","谁知道，谁又能证明":"誰知道，誰又能證明","被删掉的数据库记录、私人副本、录音与叶校长留下的纸面档案，分别保存了不同意义上的真实。":"被刪掉的資料庫記錄、私人副本、錄音與葉校長留下的紙面檔案，分別保存了不同意義上的真實。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

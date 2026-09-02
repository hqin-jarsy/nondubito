/* Generated offline from wuxia/fox-volant-of-the-snowy-mountain/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《雪山飞狐》解读":"《雪山飛狐》解讀","三个忠心的人凭真实却不完整的看见杀了第四个；误会随后传了四代。":"三個忠心的人憑真實卻不完整的看見殺了第四個；誤會隨後傳了四代。","两位世仇终于不再照祖传的账看彼此；这份相认却没有来得及救下他们。":"兩位世仇終於不再照祖傳的賬看彼此；這份相認卻沒有來得及救下他們。","四代人中，诚实的亲眼所见一次次凝固成致命确定。最后停住的那一刀追问：知道历史以后，是否就足以不再重复。":"四代人中，誠實的親眼所見一次次凝固成致命確定。最後停住的那一刀追問：知道歷史以後，是否就足以不再重複。","四篇从一天之内拼出的一百三十年出发，读真实却不完整的看见、来不及说出口的知己，以及一场被摆好的误会怎样把最后一刀停在半空。":"四篇從一天之內拼出的一百三十年出發，讀真實卻不完整的看見、來不及說出口的知己，以及一場被擺好的誤會怎樣把最後一刀停在半空。","第五次诚实的看错正要变成不可挽回的动作，小说把刀停在了半空。":"第五次誠實的看錯正要變成不可挽回的動作，小說把刀停在了半空。","系列 · 4 篇解读":"系列 · 4 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","读者从众人的话里拼出一百三十年；每一块往事都有主人，也都有用处。":"讀者從眾人的話裡拼出一百三十年；每一塊往事都有主人，也都有用處。","这部小说由有位置的讲述拼成：每个人因为身在往事里面而知道一块，也因为身在里面而不可能拥有全部。":"這部小說由有位置的講述拼成：每個人因為身在往事裡面而知道一塊，也因為身在裡面而不可能擁有全部。","飞天狐狸":"飛天狐狸"};
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

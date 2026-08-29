/* Generated offline from essays/literature/the-handmaids-tale/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《使女的故事》解读":"《使女的故事》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从名字、政变、女性之间被分配的权力与二百年后的档案，重读基列如何占有一个人。":"四篇文章，從名字、政變、女性之間被分配的權力與二百年後的檔案，重讀基列如何佔有一個人。","基列不只囚禁有生育能力的女性。它替换她们的名字，重新分配她们的关系，并让生存取决于是否履行一种功能。奥芙弗雷德的第一人称保存的，恰是制度当作无用之物的感官、双关、记忆与未决感受。":"基列不只囚禁有生育能力的女性。它替換她們的名字，重新分配她們的關係，並讓生存取決於是否履行一種功能。奧芙弗雷德的第一人稱保存的，恰是制度當作無用之物的感官、雙關、記憶與未決感受。","四篇文章从一个所有格名字走到“历史资料”。它们追问极权如何变成日常、女性为何既会成为受害者也会成为父权制度的管理者，以及档案把证词变成材料时保存了什么、又失去了什么。":"四篇文章從一個所有格名字走到“歷史資料”。它們追問極權如何變成日常、女性為何既會成為受害者也會成為父權制度的管理者，以及檔案把證詞變成材料時保存了什麼、又失去了什麼。","玛格丽特·阿特伍德《使女的故事》。全书剧透。":"瑪格麗特·愛特伍《使女的故事》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","她的名字是一个所有格":"她的名字是一個所有格","“奥芙弗雷德”既不是自我也不是家名，而是把一个女人标记为弗雷德当下的所有物。":"“奧芙弗雷德”既不是自我也不是家名，而是把一個女人標記為弗雷德當下的所有物。","英 · 简 · 繁":"英 · 簡 · 繁","她被解雇的那个下午":"她被解雇的那個下午","基列通过一连串行政上极其普通的动作降临，而人们不断把每一步当成暂时。":"基列透過一連串行政上極其普通的動作降臨，而人們不斷把每一步當成暫時。","她得到的正是她要求的东西":"她得到的正是她要求的東西","瑟琳娜·乔伊得到了自己鼓吹的家庭秩序，却发现被分配的权力并不等于自由。":"瑟琳娜·喬伊得到了自己鼓吹的家庭秩序，卻發現被分配的權力並不等於自由。","两百年后没有人问她后来怎么样了":"兩百年後沒有人問她後來怎麼樣了","“历史资料”认证了奥芙弗雷德的声音，却也重复了把她当作材料的习惯。":"“歷史資料”認證了奧芙弗雷德的聲音，卻也重複了把她當作材料的習慣。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

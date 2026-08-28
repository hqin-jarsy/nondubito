/* Generated offline from frieren/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《葬送的芙莉莲》解读":"《葬送的芙莉蓮》解讀","一句话依赖记忆和服从；辛美尔留下的更间接也更持久——一个不断给芙莉莲以看见机会的世界。":"一句話依賴記憶和服從；欣梅爾留下的更間接也更持久——一個不斷給芙莉蓮以看見機會的世界。","剧透提示：":"劇透提示：","四篇从芙莉莲在辛美尔葬礼上的眼泪写起，经过留在世界里的路线与同伴，进入能复制人类符号却无法进入人类关系的魔族；最后回到那些“没有用”的魔法，看记忆如何变成一种做法。":"四篇從芙莉蓮在欣梅爾葬禮上的眼淚寫起，經過留在世界裡的路線與同伴，進入能複製人類符號卻無法進入人類關係的魔族；最後回到那些“沒有用”的魔法，看記憶如何變成一種做法。","四篇解读时间、记忆与不可估价的关系：芙莉莲为何迟到，辛美尔为何留下路径而非命令，马哈特为何无法靠研究抵达理解，以及无用魔法究竟记录了什么。含动画及漫画后续剧透。":"四篇解讀時間、記憶與不可估價的關係：芙莉蓮為何遲到，欣梅爾為何留下路徑而非命令，馬哈特為何無法靠研究抵達理解，以及無用魔法究竟記錄了什麼。含動畫及漫畫後續劇透。","她哭的时候，不知道自己在哭什么":"她哭的時候，不知道自己在哭什麼","山田钟人与阿部司把故事放在另一部奇幻作品的终点之后：魔王已被打倒，勇者凯旋，队伍里的精灵却还有近乎无限的时间。接下来的不只是一次追忆，也是对注意、理解与照料如何成立的追问。":"山田鐘人與阿部司把故事放在另一部奇幻作品的終點之後：魔王已被打倒，勇者凱旋，隊伍裡的精靈卻還有近乎無限的時間。接下來的不只是一次追憶，也是對注意、理解與照料如何成立的追問。","手环没有响":"手環沒有響","本系列同时涉及漫画与动画；第三篇主要讨论漫画“黄金乡”篇。":"本系列同時涉及漫畫與動畫；第三篇主要討論漫畫“黃金鄉”篇。","机会不是一句话":"機會不是一句話","没有用的魔法":"沒有用的魔法","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 文学解读":"英文 · 簡 / 繁 · 文學解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","辛美尔之死没有赋予那十年价值；它只是取消了“以后再理解”的选项，让芙莉莲看见自己迟到了。":"欣梅爾之死沒有賦予那十年價值；它只是取消了“以後再理解”的選項，讓芙莉蓮看見自己遲到了。","酸葡萄、干净的铜像与苍月草花田：看似无用的兴趣，成了芙莉莲最无意也最忠实的档案。":"酸葡萄、乾淨的銅像與蒼月草花田：看似無用的興趣，成了芙莉蓮最無意也最忠實的檔案。","马哈特真诚地想理解恶意与罪恶感；但只要方法把最亲近的人变成研究材料，真诚也无法救它。":"馬哈特真誠地想理解惡意與罪惡感；但只要方法把最親近的人變成研究材料，真誠也無法救它。"};
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

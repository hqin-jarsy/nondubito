/* Generated offline from hulan/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《呼兰河传》解读":"《呼蘭河傳》解讀","也没有人问它":"也沒有人問它","全城等着看他垮掉":"全城等著看他垮掉","呼兰河的赞美与鄙夷使用同一批事实；改变的只是这个人是否仍可由全城估价、转让和裁判。":"呼蘭河的讚美與鄙夷使用同一批事實；改變的只是這個人是否仍可由全城估價、轉讓和裁判。","四篇从全院人试图“救治”的小团圆媳妇写起，经过泥坑与为鬼而做的盛举，读到被全城估价的有二伯、王大姐与冯歪嘴子；最后进入那个不要求生命解释自己的后花园。":"四篇從全院人試圖“救治”的小團圓媳婦寫起，經過泥坑與為鬼而做的盛舉，讀到被全城估價的有二伯、王大姐與馮歪嘴子；最後進入那個不要求生命解釋自己的後花園。","四篇解读一座以救人为名折磨孩子、把隆重仪式献给鬼神、惩罚拒绝估价之人的小城，以及其中那个万物不必解释自己为何如此的后花园。":"四篇解讀一座以救人為名折磨孩子、把隆重儀式獻給鬼神、懲罰拒絕估價之人的小城，以及其中那個萬物不必解釋自己為何如此的後花園。","泥坑留下，因为它既提供热闹，也提供借口；只要能帮助全城回避已知之事，坏东西就有了用途。":"泥坑留下，因為它既提供熱鬧，也提供藉口；只要能幫助全城迴避已知之事，壞東西就有了用途。","版本说明：":"版本說明：","简体中文保留作者底稿并校正少量事实与过强措辞；繁体中文按台湾读者习惯编辑；英文为独立重写。":"簡體中文保留作者底稿並校正少量事實與過強措辭；繁體中文按臺灣讀者習慣編輯；英文為獨立重寫。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","花园给予的不是无限权力，而是更小也更稀有的东西：存在不必成为一道必须回答的问题。":"花園給予的不是無限權力，而是更小也更稀有的東西：存在不必成為一道必須回答的問題。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 文学解读":"英文 · 簡 / 繁 · 文學解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","萧红没有把呼兰河写成一座只需找出一个恶人的法庭。她写的是另一种更难处理的结构：习俗、同情、看热闹与现实利益怎样汇到一起，毁掉一个孩子，而几乎每个人仍觉得日子只是在照常运行。":"蕭紅沒有把呼蘭河寫成一座只需找出一個惡人的法庭。她寫的是另一種更難處理的結構：習俗、同情、看熱鬧與現實利益怎樣匯到一起，毀掉一個孩子，而幾乎每個人仍覺得日子只是在照常運行。","邻人并非为了看一个孩子死去而来；真正严酷的是，怜悯、热闹、生意与暴力共同维持了治疗。":"鄰人並非為了看一個孩子死去而來；真正嚴酷的是，憐憫、熱鬧、生意與暴力共同維持了治療。","都是为鬼做的":"都是為鬼做的"};
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

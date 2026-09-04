/* Generated offline from essays/wuxia/xiao-shiyilang/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 3 篇解读":"系列 · 3 篇解讀","《萧十一郎》解读":"《蕭十一郎》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","三篇从一个最好用的恶名、两块完整无瑕的“璧”与一座收藏活人的玩偶山庄出发，读萧十一郎怎样不辩解也不活成罪名，以及沈璧君与风四娘各自走出的那一步。":"三篇從一個最好用的惡名、兩塊完整無瑕的“璧”與一座收藏活人的玩偶山莊出發，讀蕭十一郎怎樣不辯解也不活成罪名，以及沈璧君與風四娘各自走出的那一步。","古龙一九六九年先为《萧十一郎》写电影剧本，随后改写为小说，并于一九七〇年连载、出版。剧本留下的紧凑很适合这个不爱替自己申辩的主角：名声说得很响，行动答得很轻，结尾则没有替任何人证明谁一定回来。":"古龍一九六九年先為《蕭十一郎》寫電影劇本，隨後改寫為小說，並於一九七〇年連載、出版。劇本留下的緊湊很適合這個不愛替自己申辯的主角：名聲說得很響，行動答得很輕，結尾則沒有替任何人證明誰一定回來。","这三篇保留第一部小说的开放结局；一九七三年的续作《火并萧十一郎》只在需要避免把风四娘写成“什么也没得到”时提及。全文包含结局剧透。":"這三篇保留第一部小說的開放結局；一九七三年的續作《火併蕭十一郎》只在需要避免把風四娘寫成“什麼也沒得到”時提及。全文包含結局劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","恶名":"惡名","萧十一郎的名字既真有盗贼经历，又没有门派替他澄清，因而成了人人可以借来栽赃的公共工具；他既洗不掉，也不肯照着活。":"蕭十一郎的名字既真有盜賊經歷，又沒有門派替他澄清，因而成了人人可以借來栽贓的公共工具；他既洗不掉，也不肯照著活。","英 · 简 · 繁":"英 · 簡 · 繁","沈璧君与连城璧都以无瑕之玉为名；一个第一次离开别人配好的位置，另一个则把越来越多的人压进“完美君子”的裂缝里。":"沈璧君與連城璧都以無瑕之玉為名；一個第一次離開別人配好的位置，另一個則把越來越多的人壓進“完美君子”的裂縫裡。","逍遥侯把活人收藏成玩偶，割鹿刀让整个江湖追逐别人眼中的价值；结尾真正没有封住的，是两条走向死路的人与一个终于回应杨开泰的风四娘。":"逍遙侯把活人收藏成玩偶，割鹿刀讓整個江湖追逐別人眼中的價值；結尾真正沒有封住的，是兩條走向死路的人與一個終於回應楊開泰的風四娘。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();

/* Generated offline from essays/literature/childhood/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“好事情”教他准确说话，母亲死去，一个孩子带着彼此矛盾的遗产与自己的判断方法进入人间。":"“好事情”教他準確說話，母親死去，一個孩子帶著彼此矛盾的遺產與自己的判斷方法進入人間。","← 文学与文化":"← 文學與文化","《童年》解读":"《童年》解讀","一个家庭按用处给每个人估价，直到小茨冈悄悄把胳膊伸到抽打孩子的枝条下面。":"一個家庭按用處給每個人估價，直到小茨岡悄悄把胳膊伸到抽打孩子的枝條下面。","两个上帝":"兩個上帝","他到人间去了":"他到人間去了","四篇文章，从卡希林家的染坊、被伏尔加河纤绳塑成的外祖父，到一间屋子里的两个上帝，以及被送到人间的孩子。":"四篇文章，從卡希林家的染坊、被伏爾加河纖繩塑成的外祖父，到一間屋子裡的兩個上帝，以及被送到人間的孩子。","外祖父也是被纤绳勒大的":"外祖父也是被纖繩勒大的","把外祖父从伏尔加河纤道带到家产的生存习惯，也变成了他统治家庭的暴力。":"把外祖父從伏爾加河纖道帶到家產的生存習慣，也變成了他統治家庭的暴力。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那间染坊":"那間染坊","阿廖沙看出：外祖母的上帝陪人过日子，外祖父的上帝则记账并惩罚敌人。":"阿廖沙看出：外祖母的上帝陪人過日子，外祖父的上帝則記賬並懲罰敵人。","马克西姆·高尔基《童年》，一九一三至一九一四年发表。全书剧透。":"馬克西姆·高爾基《童年》，一九一三至一九一四年發表。全書劇透。","高尔基的回忆录不把人整理成恶人与救赎者。它追踪暴力如何成为常规、生存办法如何变成家庭法律，也保存那些看似无用的行动——故事、舞蹈、准确的言说、伸到枝条下的一只胳膊——如何让那套法律始终无法成为全部。":"高爾基的回憶錄不把人整理成惡人與救贖者。它追蹤暴力如何成為常規、生存辦法如何變成家庭法律，也儲存那些看似無用的行動——故事、舞蹈、準確的言說、伸到枝條下的一隻胳膊——如何讓那套法律始終無法成為全部。"};
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

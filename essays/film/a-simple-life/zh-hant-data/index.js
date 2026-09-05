/* Generated offline from essays/film/a-simple-life/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《桃姐》解读":"《桃姐》解讀","三篇解读：被家遮住的家务劳动、老人院能够与不能够提供的照护，以及一段在用途结束后才真正显形的关系。":"三篇解讀：被家遮住的家務勞動、老人院能夠與不能夠提供的照護，以及一段在用途結束後才真正顯形的關係。","他不是在还债":"他不是在還債","依据许鞍华执导的二〇一一年电影《桃姐》，取材于监制、联合编剧李恩霖与家佣钟春桃的真实经历；人物背景与关键情节已参照影展及制作方资料校订。":"依據許鞍華執導的二〇一一年電影《桃姐》，取材於監制、聯合編劇李恩霖與家傭鐘春桃的真實經歷；人物背景與關鍵情節已參照影展及製作方資料校訂。","她把这个家照顾得非常好":"她把這個家照顧得非常好","桃姐的手艺让家得以成立，也让劳动几乎隐形；退休使六十年服务里的等级与归属同时露出来。":"桃姐的手藝讓家得以成立，也讓勞動幾乎隱形；退休使六十年服務裡的等級與歸屬同時露出來。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","罗杰的探视无法抵销六十年服务；它的意义恰恰从还债与用途都不再足以解释之处开始。":"羅傑的探視無法抵銷六十年服務；它的意義恰恰從還債與用途都不再足以解釋之處開始。","老人院能够组织专业照护，却无法按排班制造共同往事、自愿探视，以及一个会反复回来替你说话的人。":"老人院能夠組織專業照護，卻無法按排班製造共同往事、自願探視，以及一個會反復回來替你說話的人。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","许鞍华的《桃姐》既不急着控诉，也不急着歌颂报恩。桃姐六十年的服务同时含有等级、手艺、感情与限制。中风让照护的方向逆转之后，电影才慢慢问出：当工作已不能解释一个人为什么留下，两个人之间还剩下什么。":"許鞍華的《桃姐》既不急著控訴，也不急著歌頌報恩。桃姐六十年的服務同時含有等級、手藝、感情與限制。中風讓照護的方向逆轉之後，電影才慢慢問出：當工作已不能解釋一個人為什麼留下，兩個人之間還剩下什麼。","那个地方什么都不缺":"那個地方什麼都不缺"};
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

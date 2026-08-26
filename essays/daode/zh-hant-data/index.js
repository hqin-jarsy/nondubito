/* Generated offline from daode/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉) · 2026 · 八篇 · 8 Essays · Seven Languages · Chinese S/T":"Han Qin (秦漢) · 2026 · 八篇 · 8 Essays · Seven Languages · Chinese S/T","© 2026 Han Qin (秦汉). All rights reserved.":"© 2026 Han Qin (秦漢). All rights reserved.","　·　全系列论文已存档于 ":"　·　全系列論文已存檔於 ","与道家、佛教、康德、Levinas、Buber、Ubuntu的跨文明对话。不批判，只阐述异同。否定之路。系列在此收尾。":"與道家、佛教、康德、Levinas、Buber、Ubuntu的跨文明對話。不批判，只闡述異同。否定之路。系列在此收尾。","主体反转：公平首先是你对自己是否公平。声誉是共同体持有的关于你的状态，不是你的资产。Goodhart定律的结构性根源。":"主體反轉：公平首先是你對自己是否公平。聲譽是共同體持有的關於你的狀態，不是你的資產。Goodhart定律的結構性根源。","共凿正和":"共鑿正和","共同体的形态":"共同體的形態","内外之镜":"內外之鏡","四条\"不能不\"。识认是克制，不是给予。构成性条件而非规范性要求。与康德的根本分歧。":"四條\"不能不\"。識認是剋制，不是給予。構成性條件而非規範性要求。與康德的根本分歧。","四条道德律":"四條道德律","大同有余项":"大同有餘項","学术原文：":"學術原文：","混合现实中的人":"混合現實中的人","特罗克梅被捕，村庄的庇护没有停。机构架构不是设计出来的。道德庭与14DD法庭的路由，三层识别，聚合见证。没有完美机构。":"特羅克梅被捕，村莊的庇護沒有停。機構架構不是設計出來的。道德庭與14DD法庭的路由，三層識別，聚合見證。沒有完美機構。","看不见的架构":"看不見的架構","真实共同体始终是混合的。伪15DD群体的辨识。自我保全、选择性合作、必要时退出。科雅扎克与苏菲·朔尔。":"真實共同體始終是混合的。偽15DD群體的辨識。自我保全、選擇性合作、必要時退出。科雅扎克與蘇菲·朔爾。","立法主体之道":"立法主體之道","第八篇 · 尾声":"第八篇 · 尾聲","自我作为目的":"自我作為目的","这八篇散文改写自SAE道德律学术系列（ML·0至ML·9），保留原有论证的逻辑骨架，以散文的方式重新展开。每篇结尾附有学术原文的链接。全系列现有中、英、日、法、德、西、韩七种语言版本；各语言均按自身读者的思想语感独立重写，中文另提供同页简体与繁体阅读模式。":"這八篇散文改寫自SAE道德律學術系列（ML·0至ML·9），保留原有論證的邏輯骨架，以散文的方式重新展開。每篇結尾附有學術原文的連結。全系列現有中、英、日、法、德、西、韓七種語言版本；各語言均按自身讀者的思想語感獨立重寫，中文另提供同頁簡體與繁體閱讀模式。","道德庭：原告是加害方。主体性是活动而非资源。物自体不可穷尽。互凿在本体论上是正和的。":"道德庭：原告是加害方。主體性是活動而非資源。物自體不可窮盡。互鑿在本體論上是正和的。","道德律不从善恶出发，而从结构出发。15DD不是更好的人，而是运算配置不同的主体。大同有余项。":"道德律不從善惡出發，而從結構出發。15DD不是更好的人，而是運算配置不同的主體。大同有餘項。","道德律系列从一个不寻常的地方出发：不问善恶，问结构。当多个真正意义上的自我立法主体共处一个共同体时，他们之间会涌现出什么样的形态？这个问题的答案不是一套从外部施加的规则，而是一组构成性条件——你在这个模式下运作，就必然如此。":"道德律系列從一個不尋常的地方出發：不問善惡，問結構。當多個真正意義上的自我立法主體共處一個共同體時，他們之間會湧現出什麼樣的形態？這個問題的答案不是一套從外部施加的規則，而是一組構成性條件——你在這個模式下運作，就必然如此。","集体15DD是涌现属性。利尚邦村：怎么能拒绝他们呢？培育与殖民的对立。宏观等待，微观立即行动。":"集體15DD是湧現屬性。利尚邦村：怎麼能拒絕他們呢？培育與殖民的對立。宏觀等待，微觀立即行動。"};
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

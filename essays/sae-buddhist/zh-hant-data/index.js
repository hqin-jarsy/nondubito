/* Generated offline from sae-buddhist/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉) · 2026 · 六篇 · 中文简繁与英文":"Han Qin (秦漢) · 2026 · 六篇 · 中文簡繁與英文","SAE 与佛学 · 接口系列":"SAE 與佛學 · 介面系列","SAE佛学：六个接口":"SAE佛學：六個介面","SAE佛学：六个接口 / SAE and Buddhist Thought: Six Interfaces — Non Dubito":"SAE佛學：六個介面 / SAE and Buddhist Thought: Six Interfaces — Non Dubito","© 2026 Han Qin (秦汉). All rights reserved.":"© 2026 Han Qin (秦漢). All rights reserved.","← SAE 与佛学":"← SAE 與佛學","一切互摄之后，还有没有他者":"一切互攝之後，還有沒有他者","中观与 SAE 都拒绝让任何构坐实为自性，却在“假名有没有真实牵制力”这一点上走向两条不同的路。":"中觀與 SAE 都拒絕讓任何構坐實為自性，卻在“假名有沒有真實牽制力”這一點上走向兩條不同的路。","他力从哪里进入":"他力從哪裡進入","净土以弥陀本愿完成横超，SAE 坚持一切构必须自凿；真正的缝不在有没有行动，而在越过的力量来自哪里。":"淨土以彌陀本願完成橫超，SAE 堅持一切構必須自鑿；真正的縫不在有沒有行動，而在越過的力量來自哪裡。","华严以事事无碍完成关系，SAE 以不可单方穷尽守住他者；两种完整在“有没有外部”这一点上正面相遇。":"華嚴以事事無礙完成關係，SAE 以不可單方窮盡守住他者；兩種完整在“有沒有外部”這一點上正面相遇。","天台把教法理解成因机施设，也把圆满理解成性本具足；前者与涵育相接，后者则与 SAE 的无终态彻底分开。":"天台把教法理解成因機施設，也把圓滿理解成性本具足；前者與涵育相接，後者則與 SAE 的無終態徹底分開。","最高的那一层，能不能被建造":"最高的那一層，能不能被建造","每一次相遇都同时保留两件事：哪里可以互相照亮，哪里必须分手。真正重要的不是证明佛学早已说过 SAE，或 SAE 能够解释佛学，而是让两个完整体系在不可翻译处仍保持各自的形状。":"每一次相遇都同時保留兩件事：哪裡可以互相照亮，哪裡必須分手。真正重要的不是證明佛學早已說過 SAE，或 SAE 能夠解釋佛學，而是讓兩個完整體系在不可翻譯處仍保持各自的形狀。","真正可以和 SAE 对接的，不是一个神秘的第八识实体，而是阿赖耶识—种子系统在转依中发生的整段变化。":"真正可以和 SAE 對接的，不是一個神秘的第八識實體，而是阿賴耶識—種子系統在轉依中發生的整段變化。","禅宗并不反对地图、次第和方法；它拒绝的是任何一张地图被主体误认成可以永久居住的终点。":"禪宗並不反對地圖、次第和方法；它拒絕的是任何一張地圖被主體誤認成可以永久居住的終點。","禅宗破掉的不是结构":"禪宗破掉的不是結構","空不是终点":"空不是終點","第 01 篇 · 唯识":"第 01 篇 · 唯識","第 02 篇 · 禅":"第 02 篇 · 禪","第 03 篇 · 中观／三论":"第 03 篇 · 中觀／三論","第 05 篇 · 华严":"第 05 篇 · 華嚴","第 06 篇 · 净土":"第 06 篇 · 淨土","第一阶段：简体中文 · 繁體中文 · English。六篇均由已发表的中英双语学术论文重新构思为 Non Dubito 阅读版；英文为面向英语读者的独立重写。":"第一階段：簡體中文 · 繁體中文 · English。六篇均由已發表的中英雙語學術論文重新構思為 Non Dubito 閱讀版；英文為面向英語讀者的獨立重寫。","这不是用 SAE 给佛教各宗重新判教，也不是把佛学术语换成 DD 术语。六篇分别选择一个最有分辨率的接口：唯识照“构”，禅照“凿”，中观照“律”，天台照“涵育”，华严照“无外整全”，净土则把问题推到“他力”。":"這不是用 SAE 給佛教各宗重新判教，也不是把佛學術語換成 DD 術語。六篇分別選擇一個最有解析度的介面：唯識照“構”，禪照“鑿”，中觀照“律”，天台照“涵育”，華嚴照“無外整全”，淨土則把問題推到“他力”。","阿赖耶识不是一座仓库":"阿賴耶識不是一座倉庫"};
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

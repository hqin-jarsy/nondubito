/* Generated offline from essays/literature/psycho-pass/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 五篇解读 · 动画评论":"系列 · 五篇解讀 · 動畫評論","《心理测量者》解读":"《心理測量者》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","五篇从受害者怎样被重新归类，读到职业适性、由“免罪体质者”组成的西比拉、槙岛把自由变成实验，以及常守朱为什么知道真相后仍留在里面。":"五篇從受害者怎樣被重新歸類，讀到職業適性、由“免罪體質者”組成的西比拉、槙島把自由變成實驗，以及常守朱為什麼知道真相後仍留在裡面。","《心理测量者》想象了一个精神状态可以持续量化的社会。西比拉提供职业建议，监测色相，给出犯罪系数，再决定公安手中的支配者能否开火。它的力量不只来自惩罚，更来自让描述先于选择：你就是适合这项工作的人；你现在就是社会必须防范的人。":"《心理測量者》想像了一個精神狀態可以持續量化的社會。西比拉提供職業建議，監測色相，給出犯罪系數，再決定公安手中的支配者能否開火。它的力量不只來自懲罰，更來自讓描述先於選擇：你就是適合這項工作的人；你現在就是社會必須防範的人。","五篇沿着电视动画第一季，从常守朱第一次出勤读到她知道西比拉真相以后回到同一间办公室。它们追问数字判断删掉了什么，善意建议为什么可能比禁令治理得更深，以及一个准确批判支配的人，怎样又会以自由之名复制支配。":"五篇沿著電視動畫第一季，從常守朱第一次出勤讀到她知道西比拉真相以後回到同一間辦公室。它們追問數字判斷刪掉了什麼，善意建議為什麼可能比禁令治理得更深，以及一個準確批判支配的人，怎樣又會以自由之名複製支配。","本系列以电视动画第一季二十二集为主要文本。总监督本广克行，监督盐谷直义，故事原案虚渊玄，动画制作Production I.G。全季剧透。":"本系列以電視動畫第一季二十二集為主要文本。總監督本廣克行，監督鹽谷直義，故事原案虛淵玄，動畫製作Production I.G。全季劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","她被伤害，然后变成了处理对象":"她被傷害，然後變成了處理對象","受害者在极端创伤中变得危险，西比拉却把一段有来路的受苦史压成一个等待处置的当前数字。":"受害者在極端創傷中變得危險，西比拉卻把一段有來路的受苦史壓成一個等待處置的當前數字。","英 · 简 · 繁":"英 · 簡 · 繁","它告诉你你适合做什么":"它告訴你你適合做什麼","当职业适性报告能把推荐路径变成唯一理性的选择，西比拉很少需要公开禁止另一种人生。":"當職業適性報告能把推薦路徑變成唯一理性的選擇，西比拉很少需要公開禁止另一種人生。","它是用它测不了的人做的":"它是用它測不了的人做的","縢秀星发现，那个看似中立的判断者，是一群自身危险意图无法被通常判定的人脑。":"縢秀星發現，那個看似中立的判斷者，是一群自身危險意圖無法被通常判定的人腦。","他说的话几乎全对":"他說的話幾乎全對","槙岛准确诊断了一个失去自我作者的社会，却又把别人变成自由实验，复制了西比拉的结构。":"槙島準確診斷了一個失去自我作者的社會，卻又把別人變成自由實驗，複製了西比拉的結構。","她留在里面":"她留在裡面","常守朱知道西比拉是什么以后仍做监视官，并把人所维持的法律与无法违抗的机器命令区分开。":"常守朱知道西比拉是什麼以後仍做監視官，並把人所維持的法律與無法違抗的機器命令區分開。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

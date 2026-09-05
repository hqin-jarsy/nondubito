/* Generated offline from essays/games/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文章库":"← 文章庫","《去月球》解读":"《去月球》解讀","《寂静岭2》解读":"《寂靜嶺2》解讀","《尼尔：机械纪元》解读":"《尼爾：機械紀元》解讀","《巫师3：狂猎》解读":"《巫師3：狂獵》解讀","《旺达与巨像》解读":"《旺達與巨像》解讀","《最后生还者 第二部》解读":"《最後生還者 第二部》解讀","《黑神话：悟空》解读":"《黑神話：悟空》解讀","七个系列 · 二十七篇 · 英 / 简 / 繁":"七個系列 · 二十七篇 · 英 / 簡 / 繁","三篇从一场无法征得同意的复活、被做成道路的十六个巨像，读到莫诺醒来后抱起长角婴儿的那个无价动作。":"三篇從一場無法徵得同意的復活、被做成道路的十六個巨像，讀到莫諾醒來後抱起長角嬰兒的那個無價動作。","四篇从2B与9S被设计成处刑结构的亲密关系，读到不存在的人类、长出自身生活的机械生命，以及结局向玩家提出却不强迫的一次请求。":"四篇從2B與9S被設計成處刑結構的親密關係，讀到不存在的人類、長出自身生活的機械生命，以及結局向玩家提出卻不強迫的一次請求。","四篇从一位老人说不出来路的愿望，读到被药物封住的童年、折满一屋的纸兔子，以及替一个人安排幸福记忆时无法消失的代价。":"四篇從一位老人說不出來路的願望，讀到被藥物封住的童年、折滿一屋的紙兔子，以及替一個人安排幸福記憶時無法消失的代價。","四篇从乔尔的救人与谎言、两套都要求一条命的真账，读到艾比转向勒弗，以及那次既不以原谅、也不以互相理解为前提的停手。":"四篇從喬爾的救人與謊言、兩套都要求一條命的真賬，讀到艾比轉向勒弗，以及那次既不以原諒、也不以互相理解為前提的停手。","四篇从每个人眼中不同的寂静岭，读到安吉拉与艾迪各自错位的账、詹姆斯替自己召来的刽子手，以及随着真相回来而逐渐褪成白纸的信。":"四篇從每個人眼中不同的寂靜嶺，讀到安吉拉與艾迪各自錯位的賬、詹姆斯替自己召來的劊子手，以及隨著真相回來而逐漸褪成白紙的信。","四篇从沉默的天命人、悟空散落的六根、黄眉制造出来的人性证据，读到那只在睁眼之前停住的金箍。":"四篇從沈默的天命人、悟空散落的六根、黃眉製造出來的人性證據，讀到那只在睜眼之前停住的金箍。","四篇从血腥男爵准确却无力的认账、威伦名题里被分配给别人的代价，读到围绕希里展开的计划，以及杰洛特五次没有替她生活。":"四篇從血腥男爵準確卻無力的認賬、威倫名題裡被分配給別人的代價，讀到圍繞希里展開的計劃，以及傑洛特五次沒有替她生活。","游戏不只讲故事。它还分配目标、建立系统、隐去信息，并要求玩家亲自行动。这里把机制、重复、失败、界面与选择都当作作品论证的一部分，而不是包在故事外面的容器。":"遊戲不只講故事。它還分配目標、建立系統、隱去資訊，並要求玩家親自行動。這裡把機制、重復、失敗、界面與選擇都當作作品論證的一部分，而不是包在故事外面的容器。","游戏与交互叙事":"遊戲與交互敘事","游戏目录 · 系列 01–07":"遊戲目錄 · 系列 01–07","系统、行动与人的目的":"系統、行動與人的目的","阅读系列":"閱讀系列","频道 · 游戏解读":"頻道 · 遊戲解讀"};
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

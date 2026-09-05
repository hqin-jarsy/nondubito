/* Generated offline from index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"SAE Conflict Treatise 冲突论系列 — Non Dubito": "SAE Conflict Treatise 衝突論系列 — Non Dubito", "SAE 冲突论": "SAE 衝突論", "© 2026 Han Qin (秦汉) · ": "© 2026 Han Qin (秦漢) · ", "← 书架": "← 書架", "七篇散文写的是一个人在那里做什么。不是怎么把话说得更好，不是怎么妥协，不是怎么谈成。是这件事要怎么处理，才不至于处理本身把一个人持有一条法的那个位置拿走。": "七篇散文寫的是一個人在那裡做什麼。不是怎麼把話說得更好，不是怎麼妥協，不是怎麼談成。是這件事要怎麼處理，才不至於處理本身把一個人持有一條法的那個位置拿走。", "三种阅读模式：英文、简体、繁體。": "三種閱讀模式：英文、簡體、繁體。", "三道使单向路暂停的门，暂停之后是什么，四条约束在各处的地位，以及一份明确列出的「这一篇没有做的」。": "三道使單向路暫停的門，暫停之後是什麼，四條約束在各處的地位，以及一份明確列出的「這一篇沒有做的」。", "两个人，各自持着一件多年来自己走到的事，而每一件都在真实地组织着那个人的生活。某一个星期，两边要求的行动不能同时做到——而没有一把尺可以说哪一条更真，谁也不能替对方立法，谁也不能靠走开把它结清。": "兩個人，各自持著一件多年來自己走到的事，而每一件都在真實地組織著那個人的生活。某一個星期，兩邊要求的行動不能同時做到——而沒有一把尺可以說哪一條更真，誰也不能替對方立法，誰也不能靠走開把它結清。", "两本账": "兩本賬", "两条法相遇的时候": "兩條法相遇的時候", "两道门。而碰撞的大小不定射程：一件很小的事若以压制处理也可能触及那个位置，一件很大的事若双方各有余地可能从头到尾没有触及。四个看起来能定射程、其实不能的名目。": "兩道門。而碰撞的大小不定射程：一件很小的事若以壓制處理也可能觸及那個位置，一件很大的事若雙方各有餘地可能從頭到尾沒有觸及。四個看起來能定射程、其實不能的名目。", "共同深入，与走不通的那一侧。涵育不是教化，第一步不是让他看见我，而我理解了他为什么这样，不等于这件事就此说定。": "共同深入，與走不通的那一側。涵育不是教化，第一步不是讓他看見我，而我理解了他為什麼這樣，不等於這件事就此說定。", "分路按当前的关系条件分。转路的根据是当前互向过程不可用这件事本身，不必再加一项关于对方内心或层级的解释。三处与战争论不同。": "分路按當前的關係條件分。轉路的根據是當前互向過程不可用這件事本身，不必再加一項關於對方內心或層級的解釋。三處與戰爭論不同。", "四个同心圆": "四個同心圓", "止点不是拖着": "止點不是拖著", "正视，深入理解，向终，受问。不是四条规范，是这个处理位置本身不能取消的四项条件——而我可以停止，停下不证明这四条错了。": "正視，深入理解，向終，受問。不是四條規範，是這個處理位置本身不能取消的四項條件——而我可以停止，停下不證明這四條錯了。", "秦汉 · 2026 · 七篇 · 英文／中文／繁體": "秦漢 · 2026 · 七篇 · 英文／中文／繁體", "终，止点，移出，暂停，拖着——五个词各有专用。共识的两种发生史，互相承认不可通约，以及全篇最难的那一处分界。": "終，止點，移出，暫停，拖著——五個詞各有專用。共識的兩種發生史，互相承認不可通約，以及全篇最難的那一處分界。", "谁去交电费": "誰去交電費", "这两个人没有终": "這兩個人沒有終", "道歉不消解两条法的不相容，而不相容也不使那句话可以挂起不认。分级交接，保护先行，以及为什么行动安排不是法。": "道歉不消解兩條法的不相容，而不相容也不使那句話可以掛起不認。分級交接，保護先行，以及為什麼行動安排不是法。"};
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

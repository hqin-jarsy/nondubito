/* Generated offline from essays/sae-consolation/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉) · 2026 · 六篇 · 英／简／繁":"Han Qin (秦漢) · 2026 · 六篇 · 英／簡／繁","SAE 与西方哲学 · 第三辑":"SAE 與西方哲學 · 第三輯","SAE哲学的慰藉":"SAE哲學的慰藉","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“有理性又会死的动物”是一条正确说明；病从它签下作者的名字、把自己冒领成完整自我的那一刻开始。":"“有理性又會死的動物”是一條正確說明；病從它簽下作者的名字、把自己冒領成完整自我的那一刻開始。","← SAE 与西方哲学":"← SAE 與西方哲學","他把追问派给了另一个人":"他把追問派給了另一個人","他答对了那一问":"他答對了那一問","你是在拿我玩吗":"你是在拿我玩嗎","六篇挨着波爱修斯《哲学的慰藉》细读：从哲学女神作为内部追问者、一个正确答案的冒领与命运女神的辩词，走到循环论证、条件必然，以及认识为何总按认识者的能力发生。":"六篇挨著波愛修斯《哲學的慰藉》細讀：從哲學女神作為內部追問者、一個正確答案的冒領與命運女神的辯詞，走到循環論證、條件必然，以及認識為何總按認識者的能力發生。","凡被认识的东西都按认识者的能力被收下；波爱修斯由此建立认识层级，SAE则拒绝让更高一档替先前那一次收纳清账。":"凡被認識的東西都按認識者的能力被收下；波愛修斯由此建立認識層級，SAE則拒絕讓更高一檔替先前那一次收納清賬。","哲学女神让命运女神完整陈词，写下举证责任与败诉条件；SAE则追问：接过对手最强的案子之后，是否也占走了她站立的位置。":"哲學女神讓命運女神完整陳詞，寫下舉證責任與敗訴條件；SAE則追問：接過對手最強的案子之後，是否也佔走了她站立的位置。","按谁的本事收下来":"按誰的本事收下來","波爱修斯把最难的追问交给自己写出的哲学女神；这场对话既展示自我批判能走多远，也留下内部追问为何不能担保独立校验的账。":"波愛修斯把最難的追問交給自己寫出的哲學女神；這場對話既展示自我批判能走多遠，也留下內部追問為何不能擔保獨立校驗的賬。","波爱修斯指控哲学女神用体系内部的话彼此担保；她把同一个圆解释为对象自身的形状，而 SAE 把循环记成主动降档的理由。":"波愛修斯指控哲學女神用體系內部的話彼此擔保；她把同一個圓解釋為對象自身的形狀，而 SAE 把循環記成主動降檔的理由。","知道一个人正在走，使“他正在走”为真，却没有强迫他迈步；波爱修斯与 SAE 在把必然送回正确地址这一步相遇。":"知道一個人正在走，使“他正在走”為真，卻沒有強迫他邁步；波愛修斯與 SAE 在把必然送回正確地址這一步相遇。","简体中文原作 · 繁體中文编辑版 · English 独立重写版。":"簡體中文原作 · 繁體中文編輯版 · English 獨立重寫版。","让命运女神自己开口":"讓命運女神自己開口","这不是用 SAE 给波爱修斯判案，也不是拿《慰藉》替 SAE 奠基。每篇从对话里一个具体转折出发，让两套结构在相接处各自交出尚未结清的账。":"這不是用 SAE 給波愛修斯判案，也不是拿《慰藉》替 SAE 奠基。每篇從對話裡一個具體轉折出發，讓兩套結構在相接處各自交出尚未結清的賬。","简体中文原作 · 繁體中文编辑版 · English／日／法／德／西／韩独立重写版。":"簡體中文原作 · 繁體中文編輯版 · English／日／法／德／西／韓獨立重寫版。","Han Qin (秦汉) · 2026 · 六篇 · 八种语言":"Han Qin (秦漢) · 2026 · 六篇 · 八種語言"};
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

/* Generated offline from kokoro/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《心》的结构建立在迟到的认识上：学生追问一个不断把他推开的先生，妻子与一道不能命名的伤口共同生活，死去的朋友从未在婚姻中被说出，却一直留在婚姻里面。":"《心》的結構建立在遲到的認識上：學生追問一個不斷把他推開的先生，妻子與一道不能命名的傷口共同生活，死去的朋友從未在婚姻中被說出，卻一直留在婚姻裡面。","《心》解读":"《心》解讀","先生不断警告学生不要信他，最终却把一生的秘密交给这个外人，而不是那个必须承担沉默后果的妻子。":"先生不斷警告學生不要信他，最終卻把一生的秘密交給這個外人，而不是那個必須承擔沉默後果的妻子。","先生没有对 K 撒谎；他把 K 用来要求自己的法变成武器，让朋友最后仍用同一条法审判自己。":"先生沒有對 K 撒謊；他把 K 用來要求自己的法變成武器，讓朋友最後仍用同一條法審判自己。","先生的罪责是私人的，死亡却借用了时代的名义；这个名义让行为可以被理解，也让静永远无法知道实情。":"先生的罪責是私人的，死亡卻借用了時代的名義；這個名義讓行為可以被理解，也讓靜永遠無法知道實情。","四篇从一个没有真名的先生、被反过来使用的“精进”、写给外人的遗书，读到私人罪责如何借时代的语言为自己的死亡命名。":"四篇從一個沒有真名的先生、被反過來使用的“精進”、寫給外人的遺書，讀到私人罪責如何借時代的語言為自己的死亡命名。","文学细读":"文學細讀","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这四篇追问谁能够知道、谁承担不知道的后果，以及当坦白被推迟到再也无法回应时，它还算不算把自己交给了另一个人。含全书剧透。":"這四篇追問誰能夠知道、誰承擔不知道的後果，以及當坦白被推遲到再也無法回應時，它還算不算把自己交給了另一個人。含全書劇透。","遗书":"遺書","遗书几乎什么都说了，却特意绕开被秘密改变最深的人；它的完整，以妻子永远不能读到为条件。":"遺書幾乎什麼都說了，卻特意繞開被秘密改變最深的人；它的完整，以妻子永遠不能讀到為條件。","阅读全文":"閱讀全文"};
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

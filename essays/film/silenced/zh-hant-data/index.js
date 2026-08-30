/* Generated offline from essays/film/silenced/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《熔炉》解读":"《熔爐》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一所控制所有出口的学校，读到每一步都说得通的法庭为何仍会得出不可接受的结果，以及人在失败以后怎样拒绝被世界改造成它所需要的样子。":"三篇從一所控制所有出口的學校，讀到每一步都說得通的法庭為何仍會得出不可接受的結果，以及人在失敗以後怎樣拒絕被世界改造成它所需要的樣子。","《熔炉》常因它揭露的暴行而被记住，更难得的是它把暴行得以持续的结构拍了出来：用人、地方声望、翻译、警务与管辖权彼此支撑。孩子并非没有说话，真正的问题是，谁控制着证词通往公共世界的路径。":"《熔爐》常因它揭露的暴行而被記住，更難得的是它把暴行得以持續的結構拍了出來：用人、地方聲望、翻譯、警務與管轄權彼此支撐。孩子並非沒有說話，真正的問題是，誰控制著證詞通往公共世界的路徑。","这个系列因此追踪路径，而不只追踪坏人：从校内闭合的权力，到和解与审判，再到主人公失败以后仍然留下的行动。结尾那句话之所以重要，正在于它不保证严肃的行动一定胜利。":"這個系列因此追蹤路徑，而不只追蹤壞人：從校內閉合的權力，到和解與審判，再到主人公失敗以後仍然留下的行動。結尾那句話之所以重要，正在於它不保證嚴肅的行動一定勝利。","黄东赫二〇一一年《熔炉》。全片剧透。":"黃東赫二〇一一年《熔爐》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","一所把所有出口都握在手里的学校":"一所把所有出口都握在手裡的學校","雾津的学校不只隐瞒暴行，也控制工作、翻译、管辖、名望，以及孩子可能被听见的每一条通道。":"霧津的學校不只隱瞞暴行，也控制工作、翻譯、管轄、名望，以及孩子可能被聽見的每一條通道。","英 · 简 · 繁":"英 · 簡 · 繁","每一步都合规，然后判决下来了":"每一步都合規，然後判決下來了","前官影响、对转译证词的攻击、和解与量刑，组成一条看似合规、整体却把孩子挡在门外的链条。":"前官影響、對轉譯證詞的攻擊、和解與量刑，組成一條看似合規、整體卻把孩子擋在門外的鏈條。","他们输了，而那句话是在输了以后说的":"他們輸了，而那句話是在輸了以後說的","抗议没有改变判决；它的意义在护住一张孩子的照片，也在拒绝失败以后最容易接受的那级台阶。":"抗議沒有改變判決；它的意義在護住一張孩子的照片，也在拒絕失敗以後最容易接受的那級臺階。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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

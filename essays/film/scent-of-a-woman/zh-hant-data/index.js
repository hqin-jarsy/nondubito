/* Generated offline from essays/film/scent-of-a-woman/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《闻香识女人》把查理放在几个知道他最怕失去什么的成年人之间。若不让著名演说替所有问题封口，电影会更锋利：告发可以说真话，沉默也可能保护特权，阻止自杀会碰到边界，而体面的帮助仍可能带着强迫。":"《聞香識女人》把查理放在幾個知道他最怕失去什麼的成年人之間。若不讓著名演說替所有問題封口，電影會更鋒利：告發可以說真話，沈默也可能保護特權，阻止自殺會碰到邊界，而體面的幫助仍可能帶著強迫。","《闻香识女人》解读":"《聞香識女人》解讀","三篇解读：被制度权力标价的真相、需要向导却拒绝见证人的最后旅程，以及两种并不相同的拒绝。":"三篇解讀：被制度權力標價的真相、需要嚮導卻拒絕見證人的最後旅程，以及兩種並不相同的拒絕。","他把孩子支开，想一个人结束":"他把孩子支開，想一個人結束","他没有出卖，也没有走开":"他沒有出賣，也沒有走開","依据马丁·布莱斯执导的一九九二年电影《闻香识女人》；校订中特别纠正一处旧解读：史莱德需要查理充当有视力的向导，并在自杀前将他支开，影片没有说他雇孩子是为死亡作见证。":"依據馬丁·布萊斯執導的一九九二年電影《聞香識女人》；校訂中特別糾正一處舊解讀：史萊德需要查理充當有視力的嚮導，並在自殺前將他支開，影片沒有說他雇孩子是為死亡作見證。","史莱德因失明需要指路者，却在关系已产生共同后果后，试图把死亡重新变成私事。":"史萊德因失明需要指路者，卻在關係已產生共同後果後，試圖把死亡重新變成私事。","查理可以说出真话，可校长用推荐信与处分威胁对准不平等的弱点，因而污染了调查。":"查理可以說出真話，可校長用推薦信與處分威脅對準不平等的弱點，因而污染了調查。","查理拒绝用前途交换名字，也拒绝重新成为局外人；这两个“不”的道德形状并不完全相同。":"查理拒絕用前途交換名字，也拒絕重新成為局外人；這兩個“不”的道德形狀並不完全相同。","校长说的每一句都很体面":"校長說的每一句都很體面","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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

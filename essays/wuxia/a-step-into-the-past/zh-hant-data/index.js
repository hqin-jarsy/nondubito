/* Generated offline from essays/wuxia/a-step-into-the-past/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 4 篇解读":"系列 · 4 篇解讀","《寻秦记》解读":"《尋秦記》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","四篇以二〇〇一年 TVB 四十集电视剧版为文本，从“奇货可居”、赵盘换名、师父教出的帝王与项少龙被除名，读一场为了恢复历史而亲手制造历史的穿越。":"四篇以二〇〇一年 TVB 四十集電視劇版為文本，從“奇貨可居”、趙盤換名、師父教出的帝王與項少龍被除名，讀一場為了恢復歷史而親手製造歷史的穿越。","本系列所读的是二〇〇一年 TVB 四十集电视剧版，不是黄易原著小说。剧版最大胆的改编也是它最深的问题：项少龙必须找到的“秦始皇”，并没有完整地等在历史里。他把一个刚失去母亲的少年放进死去王子的名字，亲手帮助那个人长成。":"本系列所讀的是二〇〇一年 TVB 四十集電視劇版，不是黃易原著小說。劇版最大膽的改編也是它最深的問題：項少龍必須找到的“秦始皇”，並沒有完整地等在歷史裡。他把一個剛失去母親的少年放進死去王子的名字，親手幫助那個人長成。","穿越因此不只是改变历史的幻想，也成了一个人怎样承担自己为了保住历史而制造的未来。全文包含剧集结局。":"穿越因此不只是改變歷史的幻想，也成了一個人怎樣承擔自己為了保住歷史而製造的未來。全文包含劇集結局。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","奇货可居":"奇貨可居","吕不韦不靠欺骗，而靠定价：把血统、容貌与处境换算成同一种筹码；最后坐上王位的，却偏偏不是他买下的那条血统。":"呂不韋不靠欺騙，而靠定價：把血統、容貌與處境換算成同一種籌碼；最後坐上王位的，卻偏偏不是他買下的那條血統。","英 · 简 · 繁":"英 · 簡 · 繁","赵盘":"趙盤","一个失去母亲、只剩师父可依靠的少年，在不明白代价时答应顶替嬴政；他曾经想走，却被唯一能放他走的人送了回去。":"一個失去母親、只剩師父可依靠的少年，在不明白代價時答應頂替嬴政；他曾經想走，卻被唯一能放他走的人送了回去。","师父":"師父","项少龙是真心教赵盘，也示范了怎样立威、施恩、拔除威胁；学生后来把每一样都学会，师父才看见“教得好”落到现实里的样子。":"項少龍是真心教趙盤，也示範了怎樣立威、施恩、拔除威脅；學生後來把每一樣都學會，師父才看見“教得好”落到現實裡的樣子。","项少龙没有谋反，他只是知道王座上的人原本是谁；当一个人的存在本身就是风险，定罪已经不够，只能让他从历史中消失。":"項少龍沒有謀反，他只是知道王座上的人原本是誰；當一個人的存在本身就是風險，定罪已經不夠，只能讓他從歷史中消失。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();

/* Generated offline from essays/anime/mobile-suit-gundam/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《机动战士高达》解读":"《機動戰士鋼彈》解讀","一个已经参与大规模杀戮的军官拒绝执行布里蒂什作战并受罚；当组织没有处理异议的位置，提问就只能被归类成抗命。":"一個已經參與大規模殺戮的軍官拒絕執行布里蒂什作戰並受罰；當組織沒有處理異議的位置，提問就只能被歸類成抗命。","一个看得懂手册的少年爬进尚未交付的武器，一船难民随后被编成战斗单位，也一次次在上层的账里被当成单位。":"一個看得懂手冊的少年爬進尚未交付的武器，一船難民隨後被編成戰鬥單位，也一次次在上層的賬裡被當成單位。","五篇从第一集以前已经发生的毁灭，读到补充作品保留的一次抗命、被塞进军舰的平民、打掉和谈的超级武器，以及胜利以后仍可回去的那个小小方向。":"五篇從第一集以前已經發生的毀滅，讀到補充作品保留的一次抗命、被塞進軍艦的平民、打掉和談的超級武器，以及勝利以後仍可回去的那個小小方向。","他上去是因为没有别人":"他上去是因為沒有別人","他在和谈的时候开了炮":"他在和談的時候開了炮","他拒绝了那道命令":"他拒絕了那道命令","初代《机动战士高达》开始时，战争规模已经大到作品无法为每一个死者留下姓名。接下来的四十三集，则把名字、脸、争吵与可以回去的地方，重新交给少数本来只会出现在军事数字里的人。":"初代《機動戰士鋼彈》開始時，戰爭規模已經大到作品無法為每一個死者留下姓名。接下來的四十三集，則把名字、臉、爭吵與可以回去的地方，重新交給少數本來只會出現在軍事數字裡的人。","开战的那一周":"開戰的那一週","战争中最有效的一炮杀死了双方谋求结束的人，也延长了战争；不能处理异议的等级结构，最终只能用杀人处理异议。":"戰爭中最有效的一炮殺死了雙方謀求結束的人，也延長了戰爭；不能處理異議的等級結構，最終只能用殺人處理異議。","最后一句没有赎回战争，也没有替死者解释意义；它只确认还有几个人活着，以及废墟里有一个走向他们的方向。":"最後一句沒有贖回戰爭，也沒有替死者解釋意義；它只確認還有幾個人活著，以及廢墟里有一個走向他們的方向。","核武器、毒气与殖民卫星坠落没有摧毁预定的军事目标，却永久改变了战后仍要生活的那个世界。":"核武器、毒氣與殖民衛星墜落沒有摧毀預定的軍事目標，卻永久改變了戰後仍要生活的那個世界。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","还有可以回去的地方":"還有可以回去的地方","这五篇会明确区分1979至1980年的电视版、后来的宇宙世纪年表与《THE ORIGIN》补充情节。长寿系列的后设资料可以加深原作，却不应无声地替换原作真正拍过的内容。含全剧剧透。":"這五篇會明確區分1979至1980年的電視版、後來的宇宙世紀年表與《THE ORIGIN》補充情節。長壽系列的後設資料可以加深原作，卻不應無聲地替換原作真正拍過的內容。含全劇劇透。"};
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

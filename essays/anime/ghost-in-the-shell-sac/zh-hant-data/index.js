/* Generated offline from ghost-in-the-shell-sac/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“个别的十一人”在合田放入形状之前并不存在；真实的不满随后提供了把行动当作自己决定的人。":"“個別的十一人”在合田放入形狀之前並不存在；真實的不滿隨後提供了把行動當作自己決定的人。","← 日本动漫与漫画":"← 日本動漫與漫畫","《攻壳机动队 SAC》解读":"《攻殼機動隊 SAC》解讀","《攻壳机动队 SAC》追问：当行动、记忆与符号在网络中传播，作者性还剩下什么。它既不说个人已经消失，也不把内心真诚当作解答；一种模式可以属于集体，其中每个行动又确实是某个人自己做的。":"《攻殼機動隊 SAC》追問：當行動、記憶與符號在網路中傳播，作者性還剩下什麼。它既不說個人已經消失，也不把內心真誠當作解答；一種模式可以屬於集體，其中每個行動又確實是某個人自己做的。","一个几乎没有义体化、有家庭、用左轮枪的人，给九课带来优化专家们没有的观察角度。":"一個幾乎沒有義體化、有家庭、用左輪槍的人，給九課帶來最佳化專家們沒有的觀察角度。","一个标志、一桩被掩盖的医疗丑闻与互不相识的行动者，拼出了一个从未存在过的单一罪犯。":"一個標誌、一樁被掩蓋的醫療醜聞與互不相識的行動者，拼出了一個從未存在過的單一罪犯。","一场被制造出来的自发":"一場被製造出來的自發","九台相同兵器共享全部记忆，却长出不同性格，最后牺牲了唯一可能保存自己的备份。":"九臺相同兵器共享全部記憶，卻長出不同性格，最後犧牲了唯一可能儲存自己的備份。","五篇从没有原本的复制品与被制造的自发出发，读同步怎样产生差异、组织为何需要不一样的人，以及一个行动是否属于自己为何无法从外部验明。":"五篇從沒有原本的複製品與被製造的自發出發，讀同步怎樣產生差異、組織為何需要不一樣的人，以及一個行動是否屬於自己為何無法從外部驗明。","从外面没有验法":"從外面沒有驗法","她留了一个不一样的人":"她留了一個不一樣的人","没有原本的复制品":"沒有原本的複製品","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","葵、模仿者、警察、逐利者与托古萨因不同理由占用同一标志；行动外观无法证明内在来源。":"葵、模仿者、警察、逐利者與託古薩因不同理由佔用同一標誌；行動外觀無法證明內在來源。","让它们保持一致的那个装置":"讓它們保持一致的那個裝置","这五篇沿着笑面男、个别的十一人、塔奇克马、托古萨与草薙素子读完两季，把技术当作制度结构而非未来装饰。全文包含两季结局剧透。":"這五篇沿著笑面男、個別的十一人、塔奇克馬、託古薩與草薙素子讀完兩季，把技術當作制度結構而非未來裝飾。全文包含兩季結局劇透。"};
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

(function () {
  'use strict';

  var manifest;
  var cache = new Map();
  var requestSerial = 0;
  var input;
  var languageSelect;
  var domainSelect;
  var results;
  var count;
  var empty;
  var status;
  var params = new URLSearchParams(window.location.search);
  var nativeUiLanguage = ['ja', 'fr', 'de', 'es', 'ko'].indexOf(params.get('ui')) >= 0 ? params.get('ui') : null;

  var languageNames = {
    'en': 'English',
    'zh-Hans': '简体中文',
    'zh-Hant': '繁體中文',
    'ja': '日本語',
    'fr': 'Français',
    'de': 'Deutsch',
    'es': 'Español',
    'ko': '한국어'
  };

  function choices(en, zh, hant, ja, fr, de, es, ko) {
    return { en: en, zh: zh, 'zh-hant': hant, ja: ja, fr: fr, de: de, es: es, ko: ko };
  }

  var domainNames = {
    'sae-philosophy': choices('SAE & Philosophy', 'SAE 与哲学', 'SAE 與哲學', 'SAEと哲学', 'SAE et philosophie', 'SAE und Philosophie', 'SAE y filosofía', 'SAE와 철학'),
    'everyday': choices('Everyday Life', '日常生活', '日常生活', '日常生活', 'Vie quotidienne', 'Alltagsleben', 'Vida cotidiana', '일상의 삶'),
    'mind-ai': choices('Mind, AI & Technology', '心灵、AI 与技术', '心靈、AI 與技術', '心・AI・技術', 'Esprit, IA et technologie', 'Geist, KI und Technik', 'Mente, IA y tecnología', '마음·AI·기술'),
    'history': choices('History, Power & Civilization', '历史、权力与文明', '歷史、權力與文明', '歴史・権力・文明', 'Histoire, pouvoir et civilisation', 'Geschichte, Macht und Zivilisation', 'Historia, poder y civilización', '역사·권력·문명'),
    'stories': choices('Literature, Screen & Narrative', '文学、影视与叙事', '文學、影視與敘事', '文学・映像・物語', 'Littérature, écrans et récits', 'Literatur, Film und Erzählung', 'Literatura, pantallas y relatos', '문학·영상·서사'),
    'site': choices('Site guide', '网站导览', '網站導覽', 'サイト案内', 'Guide du site', 'Wegweiser', 'Guía del sitio', '사이트 안내'),
    'unmapped': choices('Other essays', '其他文章', '其他文章', 'その他のエッセイ', 'Autres essais', 'Weitere Essays', 'Otros ensayos', '기타 글')
  };

  var typeNames = {
    'essay': choices('Essay', '文章', '文章', 'エッセイ', 'Essai', 'Essay', 'Ensayo', '에세이'),
    'series-index': choices('Series', '系列', '系列', 'シリーズ', 'Série', 'Reihe', 'Serie', '시리즈'),
    'collection-index': choices('Collection', '合集', '合集', 'コレクション', 'Collection', 'Sammlung', 'Colección', '모음'),
    'language-hub': choices('Language channel', '语言频道', '語言頻道', '言語チャンネル', 'Espace linguistique', 'Sprachbereich', 'Canal de idioma', '언어 채널'),
    'site-page': choices('Site page', '网站页面', '網站頁面', 'サイトページ', 'Page du site', 'Seite', 'Página del sitio', '사이트 페이지')
  };

  var domainOptionNames = {
    '': choices('All subjects', '全部主题', '全部主題', 'すべてのテーマ', 'Tous les thèmes', 'Alle Themen', 'Todos los temas', '모든 주제'),
    'sae-philosophy': domainNames['sae-philosophy'],
    'everyday': domainNames.everyday,
    'mind-ai': domainNames['mind-ai'],
    'history': domainNames.history,
    'stories': domainNames.stories
  };

  var uiText = {
    en: {
      title: 'Search — Non Dubito', kicker: 'Search Non Dubito', heading: 'Find the question you came with.',
      deck: 'Search essay titles, series, works, people, and the language used to describe them. Choose a language first when the same question has more than one home.',
      nav: ['Start Here', 'Explore', 'Latest', 'About'], mobile: ['Start Here', 'Explore', 'Latest', 'About', 'Full Library'], search: 'Search', menu: 'Menu',
      labels: ['Search', 'Language', 'Subject'], tryHeading: 'Try a doorway', empty: 'No result yet. Try fewer words, another language, or a broader subject.',
      placeholder: 'Try “freedom”, “loneliness”, or a title…', loading: 'Loading the index…', fallback: 'Open this result to read more.', indexError: 'The search index could not be loaded.', unavailable: 'Search is temporarily unavailable.',
      terms: ['freedom', 'loneliness', 'AI', 'power', 'Solaris']
    },
    zh: {
      title: '搜索 — Non Dubito', kicker: '搜索 Non Dubito', heading: '找到你带来的那个问题。', deck: '搜索文章标题、系列、作品、人物，以及描述这些问题的词。相同问题在不同语言里会有不同入口，请先选择搜索语言。',
      nav: ['从这里开始', '探索', '最近更新', '关于'], mobile: ['从这里开始', '探索', '最近更新', '关于', '完整书库'], search: '搜索', menu: '菜单',
      labels: ['搜索', '语言', '主题'], tryHeading: '可以先试一个入口', empty: '还没有结果。可以减少关键词、切换语言，或扩大主题范围。', placeholder: '试试“自由”“孤独”或作品名……', loading: '正在载入索引……', fallback: '打开页面继续阅读。', indexError: '搜索索引载入失败。', unavailable: '搜索暂时不可用。',
      terms: ['自由', '孤独', 'AI', '权力', '索拉里斯']
    },
    'zh-hant': {
      title: '搜尋 — Non Dubito', kicker: '搜尋 Non Dubito', heading: '找到你帶來的那個問題。', deck: '搜尋文章標題、系列、作品、人物，以及描述這些問題的詞。相同問題在不同語言裡會有不同入口，請先選擇搜尋語言。',
      nav: ['從這裡開始', '探索', '最近更新', '關於'], mobile: ['從這裡開始', '探索', '最近更新', '關於', '完整書庫'], search: '搜尋', menu: '選單',
      labels: ['搜尋', '語言', '主題'], tryHeading: '可以先試一個入口', empty: '還沒有結果。可以減少關鍵詞、切換語言，或擴大主題範圍。', placeholder: '試試「自由」「孤獨」或作品名……', loading: '正在載入索引……', fallback: '打開頁面繼續閱讀。', indexError: '搜尋索引載入失敗。', unavailable: '搜尋暫時無法使用。',
      terms: ['自由', '孤獨', 'AI', '權力', '索拉里斯']
    },
    ja: {
      title: '検索 — Non Dubito', kicker: 'Non Dubitoを検索', heading: 'いま持っている問いを見つける。', deck: 'エッセイの題名、シリーズ、作品、人名、問いを表す言葉から探せます。同じ問いに複数の入口があるときは、まず検索言語を選んでください。',
      nav: ['はじめに', '探す', '新着', 'このサイトについて'], mobile: ['はじめに', '探す', '新着', 'このサイトについて', '全シリーズ'], search: '検索', menu: 'メニュー',
      labels: ['検索', '言語', 'テーマ'], tryHeading: '入口から試す', empty: 'まだ結果がありません。語数を減らすか、別の言語や広いテーマを試してください。', placeholder: '「自由」「孤独」または作品名を入力…', loading: '索引を読み込んでいます…', fallback: '結果を開いて続きを読む。', indexError: '検索索引を読み込めませんでした。', unavailable: '検索は一時的に利用できません。',
      terms: ['自由', '孤独', 'AI', '権力', 'ソラリス']
    },
    fr: {
      title: 'Recherche — Non Dubito', kicker: 'Rechercher dans Non Dubito', heading: 'Retrouvez la question qui vous a conduit ici.', deck: 'Cherchez parmi les titres, les séries, les œuvres, les personnes et les mots employés pour formuler une question. Choisissez d’abord une langue lorsque plusieurs entrées sont possibles.',
      nav: ['Commencer', 'Explorer', 'Nouveautés', 'À propos'], mobile: ['Commencer', 'Explorer', 'Nouveautés', 'À propos', 'Bibliothèque complète'], search: 'Rechercher', menu: 'Menu',
      labels: ['Recherche', 'Langue', 'Thème'], tryHeading: 'Essayer une entrée', empty: 'Aucun résultat pour l’instant. Essayez moins de mots, une autre langue ou un thème plus large.', placeholder: 'Essayez « liberté », « solitude » ou un titre…', loading: 'Chargement de l’index…', fallback: 'Ouvrez ce résultat pour poursuivre la lecture.', indexError: 'Impossible de charger l’index de recherche.', unavailable: 'La recherche est momentanément indisponible.',
      terms: ['liberté', 'solitude', 'IA', 'pouvoir', 'Solaris']
    },
    de: {
      title: 'Suche — Non Dubito', kicker: 'Non Dubito durchsuchen', heading: 'Finden Sie die Frage, die Sie mitgebracht haben.', deck: 'Durchsuchen Sie Titel, Reihen, Werke, Personen und die Wörter, mit denen Fragen beschrieben werden. Wählen Sie zuerst eine Sprache, wenn dieselbe Frage mehrere Zugänge hat.',
      nav: ['Einstieg', 'Entdecken', 'Neu', 'Über Non Dubito'], mobile: ['Einstieg', 'Entdecken', 'Neu', 'Über Non Dubito', 'Gesamte Bibliothek'], search: 'Suchen', menu: 'Menü',
      labels: ['Suche', 'Sprache', 'Thema'], tryHeading: 'Einen Einstieg versuchen', empty: 'Noch kein Ergebnis. Versuchen Sie weniger Wörter, eine andere Sprache oder ein breiteres Thema.', placeholder: 'Versuchen Sie „Freiheit“, „Einsamkeit“ oder einen Titel…', loading: 'Suchindex wird geladen…', fallback: 'Öffnen Sie diesen Treffer, um weiterzulesen.', indexError: 'Der Suchindex konnte nicht geladen werden.', unavailable: 'Die Suche ist vorübergehend nicht verfügbar.',
      terms: ['Freiheit', 'Einsamkeit', 'KI', 'Macht', 'Solaris']
    },
    es: {
      title: 'Buscar — Non Dubito', kicker: 'Buscar en Non Dubito', heading: 'Encuentra la pregunta que te trajo hasta aquí.', deck: 'Busca títulos, series, obras, personas y las palabras con las que se formula una pregunta. Elige primero un idioma cuando una misma cuestión tenga más de una entrada.',
      nav: ['Empezar', 'Explorar', 'Novedades', 'Acerca de'], mobile: ['Empezar', 'Explorar', 'Novedades', 'Acerca de', 'Biblioteca completa'], search: 'Buscar', menu: 'Menú',
      labels: ['Búsqueda', 'Idioma', 'Tema'], tryHeading: 'Prueba una entrada', empty: 'Todavía no hay resultados. Prueba con menos palabras, otro idioma o un tema más amplio.', placeholder: 'Prueba «libertad», «soledad» o el título de una obra…', loading: 'Cargando el índice…', fallback: 'Abre este resultado para seguir leyendo.', indexError: 'No se pudo cargar el índice de búsqueda.', unavailable: 'La búsqueda no está disponible temporalmente.',
      terms: ['libertad', 'soledad', 'IA', 'poder', 'Solaris']
    },
    ko: {
      title: '검색 — Non Dubito', kicker: 'Non Dubito 검색', heading: '당신이 품고 온 질문을 찾아보세요.', deck: '에세이 제목, 시리즈, 작품, 인물, 질문을 표현하는 말로 검색할 수 있습니다. 같은 질문에 여러 입구가 있다면 먼저 검색 언어를 선택하세요.',
      nav: ['처음 오셨다면', '둘러보기', '새 글', '소개'], mobile: ['처음 오셨다면', '둘러보기', '새 글', '소개', '전체 서재'], search: '검색', menu: '메뉴',
      labels: ['검색', '언어', '주제'], tryHeading: '입구 하나를 골라보세요', empty: '아직 결과가 없습니다. 단어 수를 줄이거나 다른 언어 또는 더 넓은 주제를 선택해 보세요.', placeholder: '‘자유’, ‘외로움’ 또는 작품명을 입력하세요…', loading: '검색 색인을 불러오는 중…', fallback: '이 결과를 열어 계속 읽어보세요.', indexError: '검색 색인을 불러오지 못했습니다.', unavailable: '검색을 일시적으로 사용할 수 없습니다.',
      terms: ['자유', '외로움', 'AI', '권력', '솔라리스']
    }
  };

  function currentUiLanguage() {
    if (nativeUiLanguage) return nativeUiLanguage;
    var language = document.documentElement.dataset.lang;
    return language === 'zh' || language === 'zh-hant' ? language : 'en';
  }

  function text(key) {
    return uiText[currentUiLanguage()][key];
  }

  function localized(values) {
    return (values || typeNames.essay)[currentUiLanguage()] || (values || typeNames.essay).en;
  }

  function setNodeTexts(nodes, values) {
    Array.from(nodes).forEach(function (node, index) {
      if (values[index] !== undefined) node.textContent = values[index];
    });
  }

  function applyStaticUi() {
    var copy = uiText[currentUiLanguage()];
    var englishCopy = currentUiLanguage() === 'zh' || currentUiLanguage() === 'zh-hant' ? uiText.en : copy;
    document.title = copy.title;
    document.querySelector('.search-kicker').textContent = copy.kicker;
    document.querySelector('.search-hero h1.lang-en').textContent = englishCopy.heading;
    document.querySelector('.search-hero-deck.lang-en').textContent = englishCopy.deck;
    setNodeTexts(document.querySelectorAll('.site-shell-nav a .lang-en'), englishCopy.nav);
    setNodeTexts(document.querySelectorAll('.site-shell-drawer nav a .lang-en'), englishCopy.mobile);
    setNodeTexts(document.querySelectorAll('.search-label.lang-en'), englishCopy.labels);
    document.querySelector('.site-shell-tool .site-shell-tool-label.lang-en').textContent = englishCopy.search;
    document.querySelector('.site-shell-menu-button .site-shell-tool-label.lang-en').textContent = englishCopy.menu;
    document.querySelector('.search-suggestions h2.lang-en').textContent = englishCopy.tryHeading;
    document.querySelector('.search-empty .lang-en').textContent = englishCopy.empty;
    input.setAttribute('aria-label', copy.search);
    languageSelect.setAttribute('aria-label', copy.labels[1]);
    domainSelect.setAttribute('aria-label', copy.labels[2]);
    if (nativeUiLanguage) {
      document.documentElement.lang = nativeUiLanguage;
      document.querySelector('[data-current-language]').textContent = languageNames[nativeUiLanguage];
    }
    var siteTitle = document.querySelector('.site-shell-header .site-title');
    var desktopLinks = document.querySelectorAll('.site-shell-nav a');
    var mobileLinks = document.querySelectorAll('.site-shell-drawer nav a');
    if (nativeUiLanguage) {
      var channelHome = 'essays/' + nativeUiLanguage + '/index.html';
      var foundation = 'essays/sae-foundations/' + nativeUiLanguage + '/index.html';
      siteTitle.href = channelHome;
      desktopLinks[0].href = foundation;
      mobileLinks[0].href = foundation;
      mobileLinks[4].href = channelHome + '#language-library';
    } else {
      siteTitle.href = 'index.html';
      desktopLinks[0].href = 'start.html';
      mobileLinks[0].href = 'start.html';
      mobileLinks[4].href = 'library.html';
    }
    Array.from(document.querySelectorAll('[data-search-suggestion]')).forEach(function (button, index) {
      button.textContent = copy.terms[index];
      button.dataset.localizedTerm = copy.terms[index];
    });
  }

  function updateUiText() {
    applyStaticUi();
    input.placeholder = text('placeholder');
    Array.from(domainSelect.options).forEach(function (option) {
      option.textContent = localized(domainOptionNames[option.value]);
    });
  }

  function defaultSearchLanguage() {
    if (nativeUiLanguage) return nativeUiLanguage;
    var language = document.documentElement.dataset.lang;
    if (language === 'zh') return 'zh-Hans';
    if (language === 'zh-hant') return 'zh-Hant';
    return 'en';
  }

  function normalize(value) {
    return String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  }

  function scoreRecord(record, query) {
    var title = normalize(record.t);
    var description = normalize(record.x);
    var extra = normalize(record.q);
    var words = query.split(/\s+/).filter(Boolean);
    if (!words.every(function (word) { return title.includes(word) || description.includes(word) || extra.includes(word); })) return 0;
    var score = 1;
    if (title === query) score += 140;
    else if (title.startsWith(query)) score += 90;
    else if (title.includes(query)) score += 58;
    words.forEach(function (word) {
      if (title.includes(word)) score += 24;
      if (description.includes(word)) score += 9;
      if (extra.includes(word)) score += 3;
    });
    if (record.k === 'series-index') score += 12;
    if (record.k === 'collection-index') score += 8;
    return score;
  }

  function updateUrl() {
    var url = new URL(window.location.href);
    var query = input.value.trim();
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    if (languageSelect.value !== defaultSearchLanguage()) url.searchParams.set('in', languageSelect.value); else url.searchParams.delete('in');
    if (domainSelect.value) url.searchParams.set('domain', domainSelect.value); else url.searchParams.delete('domain');
    if (nativeUiLanguage) url.searchParams.set('ui', nativeUiLanguage); else url.searchParams.delete('ui');
    history.replaceState(null, '', url);
  }

  function setStatus(message) {
    status.textContent = message;
  }

  function loadIndex(language) {
    if (cache.has(language)) return Promise.resolve(cache.get(language));
    var entry = manifest.languages[language];
    if (!entry) return Promise.reject(new Error('Unknown language index'));
    setStatus(text('loading'));
    return fetch(entry.path)
      .then(function (response) {
        if (!response.ok) throw new Error('Index request failed');
        return response.json();
      })
      .then(function (data) {
        cache.set(language, data.records || []);
        setStatus('');
        return cache.get(language);
      });
  }

  function clearResults() {
    results.replaceChildren();
    count.textContent = '';
  }

  function renderCard(record) {
    var article = document.createElement('article');
    article.className = 'search-result-card';
    var meta = document.createElement('p');
    meta.className = 'search-result-meta';
    meta.textContent = localized(typeNames[record.k]) + ' · ' + localized(domainNames[record.d]);
    var heading = document.createElement('h2');
    var link = document.createElement('a');
    link.href = record.u;
    link.textContent = record.t;
    heading.appendChild(link);
    var description = document.createElement('p');
    description.className = 'search-result-description';
    description.textContent = record.x || text('fallback');
    var resultPath = document.createElement('p');
    resultPath.className = 'search-result-path';
    resultPath.textContent = record.u;
    article.append(meta, heading, description, resultPath);
    return article;
  }

  function resultMessage(total) {
    var language = currentUiLanguage();
    if (language === 'zh') return total + ' 条结果' + (total > 40 ? ' · 显示前 40 条' : '');
    if (language === 'zh-hant') return total + ' 條結果' + (total > 40 ? ' · 顯示前 40 條' : '');
    if (language === 'ja') return total + ' 件' + (total > 40 ? ' · 最初の40件を表示' : '');
    if (language === 'fr') return total + (total === 1 ? ' résultat' : ' résultats') + (total > 40 ? ' · 40 premiers affichés' : '');
    if (language === 'de') return total + ' Treffer' + (total > 40 ? ' · die ersten 40 werden angezeigt' : '');
    if (language === 'es') return total + (total === 1 ? ' resultado' : ' resultados') + (total > 40 ? ' · se muestran los primeros 40' : '');
    if (language === 'ko') return total + '개 결과' + (total > 40 ? ' · 처음 40개 표시' : '');
    return total + (total === 1 ? ' result' : ' results') + (total > 40 ? ' · showing the first 40' : '');
  }

  function render(records, query) {
    var normalizedQuery = normalize(query);
    var domain = domainSelect.value;
    var ranked = records
      .filter(function (record) { return !domain || record.d === domain; })
      .map(function (record) { return { record: record, score: scoreRecord(record, normalizedQuery) }; })
      .filter(function (item) { return item.score > 0; })
      .sort(function (a, b) { return b.score - a.score || a.record.t.localeCompare(b.record.t); });

    clearResults();
    ranked.slice(0, 40).forEach(function (item) { results.appendChild(renderCard(item.record)); });
    count.textContent = resultMessage(ranked.length);
    empty.hidden = ranked.length !== 0;
  }

  function runSearch() {
    var query = input.value.trim();
    updateUrl();
    if (!query) {
      clearResults();
      empty.hidden = true;
      setStatus('');
      document.body.classList.remove('has-search-query');
      return;
    }
    document.body.classList.add('has-search-query');
    var serial = ++requestSerial;
    loadIndex(languageSelect.value)
      .then(function (records) {
        if (serial === requestSerial) render(records, query);
      })
      .catch(function () {
        if (serial !== requestSerial) return;
        clearResults();
        setStatus(text('indexError'));
      });
  }

  function debounce(callback, delay) {
    var timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(callback, delay);
    };
  }

  function initialize(data) {
    manifest = data;
    Object.keys(languageNames).forEach(function (language) {
      var option = document.createElement('option');
      option.value = language;
      option.textContent = languageNames[language] + ' · ' + (manifest.languages[language] ? manifest.languages[language].count : 0);
      languageSelect.appendChild(option);
    });
    var requestedLanguage = params.get('in');
    languageSelect.value = manifest.languages[requestedLanguage] ? requestedLanguage : defaultSearchLanguage();
    domainSelect.value = params.get('domain') || '';
    input.value = params.get('q') || '';
    updateUiText();

    input.addEventListener('input', debounce(runSearch, 120));
    languageSelect.addEventListener('change', runSearch);
    domainSelect.addEventListener('change', runSearch);
    document.querySelectorAll('[data-search-suggestion]').forEach(function (button) {
      button.addEventListener('click', function () {
        input.value = button.dataset.localizedTerm;
        runSearch();
        input.focus();
      });
    });
    document.addEventListener('nondubito:languagechange', function (event) {
      nativeUiLanguage = null;
      document.documentElement.lang = event.detail.language === 'zh-hant' ? 'zh-Hant' : (event.detail.language === 'zh' ? 'zh-Hans' : 'en');
      updateUiText();
      if (!new URLSearchParams(window.location.search).has('in')) languageSelect.value = defaultSearchLanguage();
      if (input.value.trim()) runSearch(); else updateUrl();
    });
    if (input.value.trim()) runSearch();
  }

  document.addEventListener('DOMContentLoaded', function () {
    input = document.querySelector('[data-search-input]');
    languageSelect = document.querySelector('[data-search-language]');
    domainSelect = document.querySelector('[data-search-domain]');
    results = document.querySelector('[data-search-results]');
    count = document.querySelector('[data-search-count]');
    empty = document.querySelector('[data-search-empty]');
    status = document.querySelector('[data-search-status]');
    updateUiText();
    fetch('data/search-index.json')
      .then(function (response) { if (!response.ok) throw new Error('Manifest request failed'); return response.json(); })
      .then(initialize)
      .catch(function () { setStatus(text('unavailable')); });
  });
})();

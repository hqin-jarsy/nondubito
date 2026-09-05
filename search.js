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

  var domainNames = {
    'sae-philosophy': ['SAE & Philosophy', 'SAE 与哲学', 'SAE 與哲學'],
    'everyday': ['Everyday Life', '日常生活', '日常生活'],
    'mind-ai': ['Mind, AI & Technology', '心灵、AI 与技术', '心靈、AI 與技術'],
    'history': ['History, Power & Civilization', '历史、权力与文明', '歷史、權力與文明'],
    'stories': ['Literature, Screen & Narrative', '文学、影视与叙事', '文學、影視與敘事'],
    'site': ['Site guide', '网站导览', '網站導覽'],
    'unmapped': ['Other essays', '其他文章', '其他文章']
  };

  var typeNames = {
    'essay': ['Essay', '文章', '文章'],
    'series-index': ['Series', '系列', '系列'],
    'collection-index': ['Collection', '合集', '合集'],
    'language-hub': ['Language channel', '语言频道', '語言頻道'],
    'site-page': ['Site page', '网站页面', '網站頁面']
  };

  var domainOptionNames = {
    '': ['All subjects', '全部主题', '全部主題'],
    'sae-philosophy': domainNames['sae-philosophy'],
    'everyday': domainNames.everyday,
    'mind-ai': domainNames['mind-ai'],
    'history': domainNames.history,
    'stories': domainNames.stories
  };

  function uiIndex() {
    var language = document.documentElement.dataset.lang;
    return language === 'zh' ? 1 : (language === 'zh-hant' ? 2 : 0);
  }

  function localized(values) {
    return (values || typeNames.essay)[uiIndex()];
  }

  function updateUiText() {
    input.placeholder = uiIndex() === 0 ? 'Try “freedom”, “loneliness”, or a title…' : (uiIndex() === 1 ? '试试“自由”“孤独”或作品名……' : '試試「自由」「孤獨」或作品名……');
    Array.from(domainSelect.options).forEach(function (option) {
      option.textContent = localized(domainOptionNames[option.value]);
    });
  }

  function defaultSearchLanguage() {
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
    history.replaceState(null, '', url);
  }

  function setStatus(message) {
    status.textContent = message;
  }

  function loadIndex(language) {
    if (cache.has(language)) return Promise.resolve(cache.get(language));
    var entry = manifest.languages[language];
    if (!entry) return Promise.reject(new Error('Unknown language index'));
    setStatus(uiIndex() === 0 ? 'Loading the index…' : (uiIndex() === 1 ? '正在载入索引…' : '正在載入索引…'));
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
    description.textContent = record.x || (uiIndex() === 0 ? 'Open this result to read more.' : (uiIndex() === 1 ? '打开页面继续阅读。' : '打開頁面繼續閱讀。'));
    var path = document.createElement('p');
    path.className = 'search-result-path';
    path.textContent = record.u;
    article.append(meta, heading, description, path);
    return article;
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
    var visible = ranked.slice(0, 40);
    visible.forEach(function (item) { results.appendChild(renderCard(item.record)); });
    var total = ranked.length;
    var message;
    if (uiIndex() === 0) message = total + (total === 1 ? ' result' : ' results') + (total > 40 ? ' · showing the first 40' : '');
    else if (uiIndex() === 1) message = total + ' 条结果' + (total > 40 ? ' · 显示前 40 条' : '');
    else message = total + ' 條結果' + (total > 40 ? ' · 顯示前 40 條' : '');
    count.textContent = message;
    empty.hidden = total !== 0;
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
        setStatus(uiIndex() === 0 ? 'The search index could not be loaded.' : (uiIndex() === 1 ? '搜索索引载入失败。' : '搜尋索引載入失敗。'));
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
    var params = new URLSearchParams(window.location.search);
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
        input.value = uiIndex() === 0 ? button.dataset.searchEn : (uiIndex() === 1 ? button.dataset.searchZh : button.dataset.searchHant);
        runSearch();
        input.focus();
      });
    });
    document.addEventListener('nondubito:languagechange', function () {
      updateUiText();
      if (!new URLSearchParams(window.location.search).has('in')) languageSelect.value = defaultSearchLanguage();
      if (input.value.trim()) runSearch();
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
    fetch('data/search-index.json')
      .then(function (response) { if (!response.ok) throw new Error('Manifest request failed'); return response.json(); })
      .then(initialize)
      .catch(function () { setStatus('Search is temporarily unavailable.'); });
  });
})();

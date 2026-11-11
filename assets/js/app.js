/* SiliconScope — progressive enhancement. No framework, no CDN. */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;

  /* ---------- theme ---------- */
  function currentTheme() {
    return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem('ss-theme', theme); } catch (e) {}
    var meta = doc.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#0b1220' : '#f6f4ef');
  }

  var themeToggle = doc.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
    });
  }

  /* ---------- mobile nav ---------- */
  var navToggle = doc.getElementById('nav-toggle');
  var mobileNav = doc.getElementById('main-nav-mobile');
  if (navToggle && mobileNav) {
    navToggle.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
  }

  /* ---------- locale switch ---------- */
  var localeSwitch = doc.getElementById('locale-switch');
  if (localeSwitch) {
    localeSwitch.addEventListener('change', function () {
      if (localeSwitch.value) window.location.href = localeSwitch.value;
    });
  }

  /* ---------- company table ---------- */
  var table = doc.getElementById('companies-table');
  var tbody = doc.getElementById('company-rows');
  if (table && tbody) {
    var search = doc.getElementById('company-search');
    var stageSelect = doc.getElementById('filter-stage');
    var countrySelect = doc.getElementById('filter-country');
    var marketSelect = doc.getElementById('filter-market');
    var reset = doc.getElementById('filter-reset');
    var countEl = doc.getElementById('filter-count');
    var emptyRow = doc.getElementById('no-results');
    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr[data-name]'));
    var total = rows.length;
    var originalOrder = rows.slice();
    var sortState = { key: null, direction: 0 };
    var params = new URLSearchParams(window.location.search);

    if (search && params.get('q')) search.value = params.get('q');
    if (stageSelect && params.get('stage')) stageSelect.value = params.get('stage');
    if (countrySelect && params.get('country')) countrySelect.value = params.get('country');
    if (marketSelect && params.get('market')) marketSelect.value = params.get('market');

    function syncUrl() {
      var next = new URLSearchParams();
      if (search && search.value.trim()) next.set('q', search.value.trim());
      if (stageSelect && stageSelect.value) next.set('stage', stageSelect.value);
      if (countrySelect && countrySelect.value) next.set('country', countrySelect.value);
      if (marketSelect && marketSelect.value) next.set('market', marketSelect.value);
      var qs = next.toString();
      try {
        history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : '') + window.location.hash);
      } catch (e) {}
    }

    function applyFilters() {
      var term = (search && search.value || '').trim().toLowerCase();
      var stage = stageSelect ? stageSelect.value : '';
      var country = countrySelect ? countrySelect.value : '';
      var market = marketSelect ? marketSelect.value : '';
      var visible = 0;

      rows.forEach(function (row) {
        var matches =
          (!term || row.dataset.name.indexOf(term) !== -1) &&
          (!stage || row.dataset.stage === stage) &&
          (!country || row.dataset.country === country) &&
          (!market || row.dataset.market === market);
        row.hidden = !matches;
        if (matches) visible += 1;
      });

      if (emptyRow) emptyRow.hidden = visible !== 0;
      if (countEl) {
        var template = countEl.dataset.template || countEl.textContent;
        countEl.dataset.template = template;
        countEl.textContent = template.replace(/\d+/, String(visible));
      }
      syncUrl();
    }

    function sortRows(key, isNumeric) {
      if (sortState.key === key) {
        sortState.direction = sortState.direction === 1 ? -1 : 1;
      } else {
        sortState.key = key;
        sortState.direction = isNumeric ? -1 : 1;
      }
      var direction = sortState.direction;
      var sorted = rows.slice().sort(function (a, b) {
        var av = a.dataset[key];
        var bv = b.dataset[key];
        if (isNumeric) {
          var an = av === '' ? -Infinity : Number(av);
          var bn = bv === '' ? -Infinity : Number(bv);
          return (an - bn) * direction;
        }
        return String(av).localeCompare(String(bv)) * direction;
      });
      sorted.forEach(function (row) { tbody.appendChild(row); });
      Array.prototype.forEach.call(table.querySelectorAll('th'), function (th) {
        th.removeAttribute('aria-sort');
      });
      var active = table.querySelector('th[data-sort="' + key + '"]');
      if (active) active.setAttribute('aria-sort', direction === 1 ? 'ascending' : 'descending');
    }

    var keys = ['name', 'stage', 'role', 'price', 'change', 'ret', 'mcap', 'pe', 'pb', 'roe', 'priority', null, null];
    var numeric = { price: 1, change: 1, ret: 1, mcap: 1, pe: 1, pb: 1, roe: 1, priority: 1 };
    Array.prototype.forEach.call(table.querySelectorAll('thead th'), function (th, index) {
      var key = keys[index];
      if (!key) return;
      th.dataset.sort = key;
      th.setAttribute('role', 'button');
      th.setAttribute('tabindex', '0');
      th.addEventListener('click', function () { sortRows(key, !!numeric[key]); });
      th.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          sortRows(key, !!numeric[key]);
        }
      });
    });

    [search, stageSelect, countrySelect, marketSelect].forEach(function (el) {
      if (!el) return;
      el.addEventListener(el.tagName === 'SELECT' ? 'change' : 'input', applyFilters);
    });

    if (reset) {
      reset.addEventListener('click', function () {
        if (search) search.value = '';
        [stageSelect, countrySelect, marketSelect].forEach(function (el) { if (el) el.value = ''; });
        applyFilters();
        originalOrder.forEach(function (row) { tbody.appendChild(row); });
        Array.prototype.forEach.call(table.querySelectorAll('th'), function (th) { th.removeAttribute('aria-sort'); });
        sortState = { key: null, direction: 0 };
      });
    }

    var initialCount = countEl ? countEl.textContent : '';
    if (countEl) countEl.dataset.template = initialCount;
    applyFilters();
  }

  /* ---------- glossary ---------- */
  var glossaryList = doc.getElementById('glossary-list');
  if (glossaryList) {
    var gSearch = doc.getElementById('glossary-search');
    var gCategories = doc.getElementById('glossary-categories');
    var gItems = Array.prototype.slice.call(glossaryList.querySelectorAll('.glossary-item'));
    var gEmpty = doc.getElementById('glossary-empty');
    var activeCategory = '';

    function filterGlossary() {
      var term = (gSearch && gSearch.value || '').trim().toLowerCase();
      var visible = 0;
      gItems.forEach(function (item) {
        var match =
          (!term || item.dataset.search.indexOf(term) !== -1) &&
          (!activeCategory || item.dataset.category === activeCategory);
        item.hidden = !match;
        if (match) visible += 1;
      });
      if (gEmpty) gEmpty.hidden = visible !== 0;
    }

    if (gCategories) {
      gCategories.addEventListener('click', function (event) {
        var button = event.target.closest('button[data-category]');
        if (!button) return;
        activeCategory = button.dataset.category || '';
        Array.prototype.forEach.call(gCategories.querySelectorAll('button'), function (item) {
          item.classList.toggle('is-active', item === button);
        });
        filterGlossary();
      });
    }
    if (gSearch) gSearch.addEventListener('input', filterGlossary);
    filterGlossary();
  }

  /* ---------- back to top ---------- */
  var backToTop = doc.getElementById('back-to-top');
  if (backToTop) {
    var toggleBackToTop = function () {
      backToTop.classList.toggle('is-visible', window.scrollY > 640);
    };
    window.addEventListener('scroll', toggleBackToTop, { passive: true });
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    toggleBackToTop();
  }

  /* ---------- reading progress ---------- */
  var progress = doc.getElementById('reading-progress');
  if (progress) {
    var progressBar = progress.querySelector('i');
    var updateProgress = function () {
      var rect = doc.querySelector('.article-main');
      if (!rect) return;
      var start = rect.offsetTop;
      var height = rect.offsetHeight - window.innerHeight * 0.6;
      var ratio = height > 0 ? (window.scrollY - start) / height : 0;
      progressBar.style.width = Math.max(0, Math.min(1, ratio)) * 100 + '%';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  /* ---------- quick search ---------- */
  var layer = doc.getElementById('quick-search');
  if (layer) {
    var searchTrigger = doc.getElementById('search-trigger');
    var searchInput = doc.getElementById('search-input');
    var searchResults = doc.getElementById('search-results');
    var searchHint = doc.getElementById('search-hint');
    var root = doc.body.dataset.root || '';
    var lang = doc.body.dataset.lang || 'en';
    var searchIndex = null;
    var searchActive = -1;
    var currentResults = [];
    var labels = {
      company: layer.dataset.labelCompany || 'Company',
      topic: layer.dataset.labelTopic || 'Topic',
      term: layer.dataset.labelTerm || 'Term',
      page: layer.dataset.labelPage || 'Page',
      empty: layer.dataset.labelEmpty || 'No results',
      loading: layer.dataset.labelLoading || 'Loading…'
    };

    function normalize(value) {
      return String(value || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    function escapeHtml(value) {
      return String(value || '').replace(/[&<>"']/g, function (char) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char];
      });
    }

    function openSearch() {
      layer.hidden = false;
      doc.body.classList.add('search-open');
      searchActive = -1;
      if (!searchInput.value) searchInput.value = '';
      searchInput.focus();
      if (!searchIndex) {
        searchResults.innerHTML = '<p class="search-empty">' + escapeHtml(labels.loading) + '</p>';
        fetch(root + 'api/search.' + lang + '.json')
          .then(function (response) { return response.json(); })
          .then(function (data) { searchIndex = data.entries || []; renderSearch(searchInput.value); })
          .catch(function () { searchIndex = []; renderSearch(''); });
      } else {
        renderSearch(searchInput.value);
      }
    }

    function closeSearch() {
      layer.hidden = true;
      doc.body.classList.remove('search-open');
      searchActive = -1;
    }

    function resultLabel(type) {
      return labels[type] || labels.page;
    }

    function renderSearch(query) {
      var q = normalize(query.trim());
      var items = searchIndex || [];
      var matches;
      if (q) {
        matches = items.filter(function (entry) {
          if (normalize(entry.title).indexOf(q) !== -1) return true;
          if (normalize(entry.subtitle).indexOf(q) !== -1) return true;
          var keywords = entry.keywords || [];
          for (var i = 0; i < keywords.length; i += 1) {
            if (normalize(keywords[i]).indexOf(q) !== -1) return true;
          }
          return false;
        }).slice(0, 14);
      } else {
        matches = items.filter(function (entry) { return entry.type === 'page'; }).slice(0, 8);
      }
      currentResults = matches;
      searchActive = -1;
      if (!matches.length) {
        searchResults.innerHTML = '<p class="search-empty">' + escapeHtml(labels.empty.replace('{query}', query.trim())) + '</p>';
        return;
      }
      searchResults.innerHTML = matches.map(function (entry, index) {
        return '<button type="button" class="search-result" role="option" data-index="' + index + '">' +
          '<span class="search-type">' + escapeHtml(resultLabel(entry.type)) + '</span>' +
          '<span class="search-copy"><strong>' + escapeHtml(entry.title) + '</strong><small>' + escapeHtml(entry.subtitle) + '</small></span>' +
          '<span class="search-arrow" aria-hidden="true">↵</span></button>';
      }).join('');
    }

    function selectResult(index) {
      var entry = currentResults[index];
      if (!entry) return;
      window.location.href = root + entry.url;
    }

    function moveActive(delta) {
      if (!currentResults.length) return;
      searchActive = (searchActive + delta + currentResults.length) % currentResults.length;
      Array.prototype.forEach.call(searchResults.querySelectorAll('.search-result'), function (button, index) {
        var active = index === searchActive;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-selected', String(active));
        if (active) button.scrollIntoView({ block: 'nearest' });
      });
    }

    if (searchTrigger) searchTrigger.addEventListener('click', openSearch);
    Array.prototype.forEach.call(doc.querySelectorAll('[data-search-close]'), function (el) {
      el.addEventListener('click', closeSearch);
    });
    if (searchInput) {
      searchInput.addEventListener('input', function () { renderSearch(searchInput.value); });
      searchInput.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowDown') { event.preventDefault(); moveActive(1); }
        else if (event.key === 'ArrowUp') { event.preventDefault(); moveActive(-1); }
        else if (event.key === 'Enter') { event.preventDefault(); selectResult(searchActive >= 0 ? searchActive : 0); }
        else if (event.key === 'Escape') { event.preventDefault(); closeSearch(); }
      });
    }
    if (searchResults) {
      searchResults.addEventListener('click', function (event) {
        var button = event.target.closest('.search-result');
        if (button) selectResult(Number(button.dataset.index));
      });
    }
    doc.addEventListener('keydown', function (event) {
      var tag = (event.target.tagName || '').toLowerCase();
      var typing = tag === 'input' || tag === 'textarea' || tag === 'select' || event.target.isContentEditable;
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        if (layer.hidden) openSearch(); else closeSearch();
        return;
      }
      if (event.key === 'Escape' && !layer.hidden) { closeSearch(); return; }
      if (!typing && !event.metaKey && !event.ctrlKey && event.key.toLowerCase() === 't') {
        event.preventDefault();
        setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
      }
    });
  }
})();

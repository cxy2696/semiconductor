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
})();

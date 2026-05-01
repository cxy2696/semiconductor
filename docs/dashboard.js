(function () {
    let originalData = [];
    let filteredData = [];
    let newsPoolData = [];
    let klineRuntimeData = {};
    let onlyPicks = false;
    let compactTable = false;
    let showAllAlerts = false;
    let currentPage = 1;
    let pageSize = 25;
    let refreshTimer = null;
    let refreshInFlight = false;
    let readingMode = 'comfortable';
    let sectionFloaterVisible = true;
    let floaterSide = 'right';
    let currentLanguage = 'zh-CN';
    let currentTimeZone = 'Asia/Shanghai';
    let lastUpdateIso = '';

    const SEGMENT_ORDER = ['上游', '中游', '下游', '其他'];
    const RISK_WEIGHT_STORAGE_KEY = 'semicon_risk_weights_v1';
    const READING_MODE_STORAGE_KEY = 'semicon_reading_mode_v1';
    const FLOATER_VISIBLE_STORAGE_KEY = 'semicon_floater_visible_v1';
    const FLOATER_SIDE_STORAGE_KEY = 'semicon_floater_side_v1';
    const LOCALE_PROFILE_STORAGE_KEY = 'semicon_locale_profile_v1';
    const REFRESH_INTERVAL_STORAGE_KEY = 'semicon_refresh_interval_v1';
    const defaultRiskWeights = { volatility: 35, valuation: 25, liquidity: 12, segment: 10, size: 8 };
    const riskWeights = { ...defaultRiskWeights };

    const TEXTS = {
        'zh-CN': { title: '中国半导体行业报告', refreshNow: '立即刷新', newsTitle: '最新行业新闻', companiesUnit: '家公司', realTimeTrack: '实时追踪', realTimeData: '实时数据', timezoneBadge: '中国时间（Asia/Shanghai）' },
        'en-US': { title: 'China Semiconductor Industry Report', refreshNow: 'Refresh now', newsTitle: 'Latest Industry News', companiesUnit: ' companies', realTimeTrack: 'real-time tracking', realTimeData: 'real-time data', timezoneBadge: 'EST/EDT (America/New_York)' },
        'de-DE': { title: 'Chinas Halbleiter-Branchenbericht', refreshNow: 'Jetzt aktualisieren', newsTitle: 'Neueste Branchennachrichten', companiesUnit: ' Unternehmen', realTimeTrack: 'Echtzeit-Tracking', realTimeData: 'Echtzeitdaten', timezoneBadge: 'CET/CEST (Europe/Berlin)' }
    };

    function toNumber(v) {
        const n = Number(v);
        return Number.isFinite(n) ? n : null;
    }

    function fmt(v, digits = 2) {
        const n = toNumber(v);
        return n === null ? 'N/A' : n.toFixed(digits);
    }

    function sortBySegmentOrder(a, b) {
        const ia = SEGMENT_ORDER.indexOf(a);
        const ib = SEGMENT_ORDER.indexOf(b);
        if (ia === -1 && ib === -1) return String(a).localeCompare(String(b), 'zh-CN');
        if (ia === -1) return 1;
        if (ib === -1) return -1;
        return ia - ib;
    }

    function parseDateValue(value) {
        if (!value) return null;
        if (value.includes('T')) return new Date(value);
        return /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value);
    }

    function formatDateByLocale(value, withTime = false) {
        const d = parseDateValue(value);
        if (!d || Number.isNaN(d.getTime())) return value || 'N/A';
        const opts = withTime
            ? { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: currentTimeZone }
            : { year: 'numeric', month: '2-digit', day: '2-digit', timeZone: currentTimeZone };
        return new Intl.DateTimeFormat(currentLanguage, opts).format(d);
    }

    function getCurrentTexts() {
        return TEXTS[currentLanguage] || TEXTS['zh-CN'];
    }

    function updateCompanyCount(count, fromFilter = true) {
        const t = getCurrentTexts();
        const label = fromFilter ? t.realTimeData : t.realTimeTrack;
        const el = document.getElementById('company_count');
        if (el) el.textContent = `${count}${t.companiesUnit} · ${label}`;
    }

    function updateLastUpdateDisplay() {
        const el = document.getElementById('last_update');
        if (!el) return;
        if (!lastUpdateIso) lastUpdateIso = el.dataset.updateIso || '';
        el.textContent = formatDateByLocale(lastUpdateIso || el.textContent, true);
    }

    function applyLocaleProfile(profile, persist = true) {
        const [lang, tz] = String(profile || '').split('|');
        currentLanguage = TEXTS[lang] ? lang : 'zh-CN';
        currentTimeZone = tz || 'Asia/Shanghai';
        const t = getCurrentTexts();
        document.title = t.title;
        const newsTitle = document.getElementById('news_title');
        if (newsTitle) newsTitle.textContent = t.newsTitle;
        const refreshBtn = document.getElementById('manual_refresh_btn');
        if (refreshBtn) refreshBtn.textContent = t.refreshNow;
        const tzBadge = document.getElementById('timezone_badge');
        if (tzBadge) tzBadge.textContent = t.timezoneBadge;
        updateCompanyCount(filteredData.length || originalData.length, false);
        updateLastUpdateDisplay();
        renderNewsCards(getLatestNewsItems());
        if (persist) {
            try { localStorage.setItem(LOCALE_PROFILE_STORAGE_KEY, `${currentLanguage}|${currentTimeZone}`); } catch (_) {}
        }
    }

    function computeSnapshot(data = filteredData) {
        const snapshot = { totalCount: data.length, changeSum: 0, changeCount: 0, segmentCounts: {}, boardCounts: {}, regionCounts: {}, businessCounts: {}, segmentChangeAgg: {}, alerts: [], top20: [] };
        data.forEach(row => {
            const seg = row.chain_segment || '其他';
            const board = row.board || '其他';
            const region = row.region || '其他';
            const biz = row.business_type || '其他';
            const ch = toNumber(row.change_pct);
            const cap = toNumber(row.market_cap) ?? 0;
            snapshot.segmentCounts[seg] = (snapshot.segmentCounts[seg] || 0) + 1;
            snapshot.boardCounts[board] = (snapshot.boardCounts[board] || 0) + 1;
            snapshot.regionCounts[region] = (snapshot.regionCounts[region] || 0) + 1;
            snapshot.businessCounts[biz] = (snapshot.businessCounts[biz] || 0) + 1;
            snapshot.top20.push({ row, cap, ch: ch ?? 0 });
            if (ch !== null) {
                snapshot.changeSum += ch;
                snapshot.changeCount += 1;
                if (!snapshot.segmentChangeAgg[seg]) snapshot.segmentChangeAgg[seg] = { sum: 0, cnt: 0 };
                snapshot.segmentChangeAgg[seg].sum += ch;
                snapshot.segmentChangeAgg[seg].cnt += 1;
                if (Math.abs(ch) > 5) snapshot.alerts.push(row);
            }
        });
        snapshot.avgChange = snapshot.changeCount ? snapshot.changeSum / snapshot.changeCount : null;
        snapshot.top20 = snapshot.top20.sort((a, b) => b.cap - a.cap).slice(0, 20);
        return snapshot;
    }

    function renderSummaryCards(snapshot) {
        const el = document.getElementById('summary_cards');
        if (!el) return;
        const gainers = [...filteredData].sort((a, b) => (toNumber(b.change_pct) ?? -999) - (toNumber(a.change_pct) ?? -999));
        const losers = [...filteredData].sort((a, b) => (toNumber(a.change_pct) ?? 999) - (toNumber(b.change_pct) ?? 999));
        const topGainer = gainers[0];
        const topLoser = losers[0];
        el.innerHTML = `
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">当前公司数</div><div class="text-2xl font-semibold mt-1">${snapshot.totalCount}</div></div>
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">平均涨跌幅</div><div class="text-2xl font-semibold mt-1 ${(snapshot.avgChange ?? 0) >= 0 ? 'positive' : 'negative'}">${snapshot.avgChange === null ? 'N/A' : snapshot.avgChange.toFixed(2)}%</div></div>
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">最大涨幅</div><div class="text-sm font-medium mt-1 truncate">${topGainer?.name || 'N/A'}</div><div class="text-xl font-semibold positive">${fmt(topGainer?.change_pct)}%</div></div>
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">最大跌幅</div><div class="text-sm font-medium mt-1 truncate">${topLoser?.name || 'N/A'}</div><div class="text-xl font-semibold negative">${fmt(topLoser?.change_pct)}%</div></div>
        `;
    }

    function renderFilters() {
        const regionDiv = document.getElementById('region_filters');
        const businessDiv = document.getElementById('business_filters');
        if (!regionDiv || !businessDiv) return;
        regionDiv.innerHTML = '';
        businessDiv.innerHTML = '';
        [...new Set(originalData.map(d => d.region).filter(Boolean))].sort().forEach(r => {
            const el = document.createElement('label');
            el.className = 'inline-flex items-center gap-1 px-4 py-2 bg-white rounded-3xl border border-gray-200 cursor-pointer hover:border-emerald-300 text-sm';
            el.innerHTML = `<input type="checkbox" checked class="region-check" value="${r}" onchange="applyFilters()"> ${r}`;
            regionDiv.appendChild(el);
        });
        [...new Set(originalData.map(d => d.business_type).filter(Boolean))].sort().forEach(b => {
            const el = document.createElement('label');
            el.className = 'inline-flex items-center gap-1 px-4 py-2 bg-white rounded-3xl border border-gray-200 cursor-pointer hover:border-emerald-300 text-sm';
            el.innerHTML = `<input type="checkbox" checked class="business-check" value="${b}" onchange="applyFilters()"> ${b}`;
            businessDiv.appendChild(el);
        });
    }

    function renderPickCards() {
        const container = document.getElementById('pick_cards');
        if (!container) return;
        const picks = [...filteredData].sort((a, b) => (toNumber(b.invest_score) ?? 0) - (toNumber(a.invest_score) ?? 0)).slice(0, 8);
        container.innerHTML = picks.length ? '' : '<div class="text-sm text-gray-500">当前筛选条件下暂无候选标的。</div>';
        picks.forEach(row => {
            const score = toNumber(row.invest_score) ?? 0;
            const gradeClass = score >= 80 ? 'text-emerald-600' : (score >= 65 ? 'text-blue-600' : 'text-gray-600');
            const card = document.createElement('div');
            card.className = 'bg-white rounded-xl border border-gray-100 p-3';
            card.innerHTML = `
                <div class="flex items-center justify-between gap-2 mb-1">
                    <div class="font-medium text-sm truncate">${row.name}</div>
                    <div class="text-xs ${gradeClass} whitespace-nowrap">评分 ${row.invest_score || 'N/A'} (${row.invest_grade || '-'})</div>
                </div>
                <div class="text-[11px] text-gray-500 mb-1 truncate">${row.code} · ${row.board || 'N/A'} · ${row.business_type || 'N/A'}</div>
                <div class="text-[11px] text-gray-600 mb-1" style="display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden;">${row.invest_reason || '暂无说明'}</div>
                <div class="text-[11px] text-emerald-700 truncate">${row.invest_tags || '观察'}</div>
            `;
            container.appendChild(card);
        });
    }

    function getTotalPages() { return Math.max(1, Math.ceil(filteredData.length / pageSize)); }
    function getPageData() { const s = (currentPage - 1) * pageSize; return filteredData.slice(s, s + pageSize); }
    function renderPagination() {
        const totalPages = getTotalPages();
        const info = document.getElementById('pagination_info');
        const pages = document.getElementById('pagination_pages');
        if (!info || !pages) return;
        const total = filteredData.length;
        const start = total ? (currentPage - 1) * pageSize + 1 : 0;
        const end = Math.min(total, currentPage * pageSize);
        info.textContent = `显示 ${start}-${end} / 共 ${total} 条`;
        pages.innerHTML = '';
        for (let p = Math.max(1, currentPage - 2); p <= Math.min(totalPages, currentPage + 2); p += 1) {
            const btn = document.createElement('button');
            btn.className = `px-3 py-1 rounded-xl border text-sm ${p === currentPage ? 'bg-emerald-600 text-white border-emerald-600' : 'border-gray-200 hover:border-emerald-300'}`;
            btn.textContent = String(p);
            btn.onclick = () => goToPage(p);
            pages.appendChild(btn);
        }
    }

    function renderTable() {
        const tbody = document.getElementById('table_body');
        const emptyState = document.getElementById('empty_state');
        if (!tbody || !emptyState) return;
        tbody.innerHTML = '';
        emptyState.classList.toggle('hidden', filteredData.length > 0);
        if (currentPage > getTotalPages()) currentPage = getTotalPages();
        getPageData().forEach(row => {
            const tr = document.createElement('tr');
            const changeVal = toNumber(row.change_pct) ?? 0;
            const score = toNumber(row.invest_score) ?? 0;
            tr.innerHTML = `
                <td data-label="代码" class="px-6 py-5 font-mono text-sm">${row.code}</td>
                <td data-label="公司名称" class="px-6 py-5 max-w-[180px]"><div class="truncate font-medium">${row.name}</div><span class="text-xs text-gray-400 block truncate">${row.english || ''}</span></td>
                <td data-label="地区" class="px-6 py-5">${row.region || 'N/A'}</td>
                <td data-label="板块" class="px-6 py-5">${row.board || 'N/A'}</td>
                <td data-label="业务类型" class="px-6 py-5">${row.business_type || 'N/A'}</td>
                <td data-label="市值(亿)" class="px-6 py-5 text-right">${fmt(row.market_cap)}</td>
                <td data-label="当前价格" class="px-6 py-5 text-right">${fmt(row.price)}</td>
                <td data-label="涨跌幅" class="px-6 py-5 text-right ${(changeVal >= 0 ? 'positive' : 'negative')}">${fmt(changeVal)}%</td>
                <td data-label="Trailing P/E" class="px-6 py-5 text-right">${fmt(row.pe_trailing)}</td>
                <td data-label="Forward P/E" class="px-6 py-5 text-right">${fmt(row.pe_forward)}</td>
                <td data-label="成交量" class="px-6 py-5 text-right">${row.volume ?? 'N/A'}</td>
                <td data-label="52周高/低" class="px-6 py-5 text-right">${fmt(row.high52)} / ${fmt(row.low52)}</td>
                <td data-label="投资评分" class="px-6 py-5 text-right ${score >= 80 ? 'text-emerald-600' : (score >= 65 ? 'text-blue-600' : 'text-gray-500')}">${row.invest_score || 'N/A'} (${row.invest_grade || '-'})</td>
                <td data-label="策略标签" class="px-6 py-5 text-left text-xs text-emerald-700">${row.invest_tags || '观察'}</td>
            `;
            tbody.appendChild(tr);
        });
        renderPagination();
    }

    function plotChart(id, traces, layout = {}) {
        if (typeof Plotly === 'undefined') return;
        Plotly.newPlot(id, traces, { autosize: true, margin: { l: 30, r: 20, t: 20, b: 30 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', ...layout }, { responsive: true, displayModeBar: false }).catch(() => {});
    }

    function initializeCharts() {
        const snapshot = computeSnapshot(filteredData);
        const segLabels = Object.keys(snapshot.segmentCounts).sort(sortBySegmentOrder);
        plotChart('chain_segment_bar', [{ x: segLabels, y: segLabels.map(k => snapshot.segmentCounts[k]), type: 'bar' }], { height: 230 });
        plotChart('chain_pie', [{ type: 'sunburst', labels: ['半导体产业链', ...segLabels], parents: ['', ...segLabels.map(() => '半导体产业链')], values: [snapshot.totalCount, ...segLabels.map(k => snapshot.segmentCounts[k])] }], { height: 320 });
        plotChart('top20_chart', [{ x: snapshot.top20.map(x => x.row.name), y: snapshot.top20.map(x => x.cap), type: 'bar' }], { height: 380, xaxis: { tickangle: -35 } });
        plotChart('board_pie', [{ values: Object.values(snapshot.boardCounts), labels: Object.keys(snapshot.boardCounts), type: 'pie', hole: 0.65 }], { height: 380 });
        const regionSorted = Object.entries(snapshot.regionCounts).sort((a, b) => b[1] - a[1]).slice(0, 12);
        plotChart('region_chart', [{ y: regionSorted.map(x => x[0]).reverse(), x: regionSorted.map(x => x[1]).reverse(), type: 'bar', orientation: 'h' }], { height: 380 });
        const bizSorted = Object.entries(snapshot.businessCounts).sort((a, b) => b[1] - a[1]).slice(0, 12);
        plotChart('business_chart', [{ x: bizSorted.map(x => x[0]), y: bizSorted.map(x => x[1]), type: 'bar' }], { height: 380, xaxis: { tickangle: -35 } });
        const segForChange = Object.keys(snapshot.segmentChangeAgg).sort(sortBySegmentOrder);
        const segAvg = segForChange.map(seg => {
            const v = snapshot.segmentChangeAgg[seg];
            return v && v.cnt ? Number((v.sum / v.cnt).toFixed(2)) : 0;
        });
        plotChart('chain_change_chart', [{ x: segForChange, y: segAvg, type: 'bar' }], { height: 380 });
        plotChart('risk_segment_chart', [{ x: segForChange, y: segAvg.map(v => Math.min(100, Math.abs(v) * 8 + riskWeights.segment)), type: 'bar' }], { height: 300, yaxis: { range: [0, 100] } });
        renderKlines();
    }

    function renderKlines() {
        const container = document.getElementById('kline_container');
        if (!container) return;
        container.innerHTML = '';
        Object.entries(klineRuntimeData || {}).forEach(([name, d], idx) => {
            const id = `kline_${idx}`;
            const card = document.createElement('div');
            card.className = 'text-center bg-white border border-slate-100 rounded-2xl p-3';
            card.innerHTML = `<div class="flex items-start justify-between gap-2 mb-2"><div class="text-left"><h4 class="font-medium text-sm">${name}</h4><div class="text-[11px] text-slate-500">${d.chain_segment || '其他'} · ${d.business_type || '其他'}</div></div><div class="text-right"><div class="text-[11px] text-slate-500">30天</div><div class="text-sm font-semibold ${Number(d.change_30d || 0) >= 0 ? 'positive' : 'negative'}">${fmt(d.change_30d)}%</div></div></div><div id="${id}" class="chart-container h-56 bg-white rounded-2xl"><div class="chart-fallback">K线加载中...</div></div>`;
            container.appendChild(card);
            const close = Array.isArray(d.close) ? d.close : [];
            const ma5 = close.map((_, i, arr) => (i < 4 ? null : Number((arr.slice(i - 4, i + 1).reduce((s, v) => s + Number(v || 0), 0) / 5).toFixed(2))));
            plotChart(id, [
                { x: d.date || [], open: d.open || [], high: d.high || [], low: d.low || [], close, type: 'candlestick', increasing: { line: { color: '#10b981' } }, decreasing: { line: { color: '#ef4444' } } },
                { x: d.date || [], y: ma5, type: 'scatter', mode: 'lines', line: { color: '#0ea5e9', width: 1.6 } }
            ], { height: 220, showlegend: false, margin: { l: 28, r: 10, t: 8, b: 24 } });
        });
    }

    function renderAlerts(snapshot) {
        const container = document.getElementById('alert_banner');
        if (!container) return;
        const alerts = (snapshot.alerts || []).sort((a, b) => Math.abs(toNumber(b.change_pct) ?? 0) - Math.abs(toNumber(a.change_pct) ?? 0));
        if (!alerts.length) { container.classList.add('hidden'); container.innerHTML = ''; return; }
        const visible = showAllAlerts ? alerts : alerts.slice(0, 10);
        container.innerHTML = `<div class="alert-card bg-white border border-red-200 rounded-2xl p-4 shadow-sm"><div class="flex items-center justify-between gap-2 flex-wrap mb-3"><div class="font-semibold">实时异动（|涨跌幅| > 5%）</div><div>${alerts.length > 10 ? `<button onclick="toggleAlertsExpand()" class="px-3 py-1 rounded-lg border border-slate-200 text-xs">${showAllAlerts ? '收起' : '展开全部'}</button>` : ''}</div></div><div class="flex flex-wrap gap-2">${visible.map(i => `<div class="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs"><span class="font-medium">${i.name}</span> <span class="${(toNumber(i.change_pct) ?? 0) >= 0 ? 'positive' : 'negative'} font-semibold">${fmt(i.change_pct)}%</span></div>`).join('')}</div></div>`;
        container.classList.remove('hidden');
    }

    function renderIndustryKnowledge(snapshot) {
        const box = document.getElementById('industry_live_metrics');
        if (!box) return;
        const topSeg = Object.entries(snapshot.segmentCounts).sort((a, b) => b[1] - a[1])[0];
        const topBiz = Object.entries(snapshot.businessCounts).sort((a, b) => b[1] - a[1])[0];
        box.innerHTML = `
            <div class="stat-card p-3"><div class="text-xs text-slate-500">样本主链段</div><div class="text-base font-semibold mt-1">${topSeg ? `${topSeg[0]}（${topSeg[1]}家）` : 'N/A'}</div></div>
            <div class="stat-card p-3"><div class="text-xs text-slate-500">最集中业务类型</div><div class="text-base font-semibold mt-1">${topBiz ? `${topBiz[0]}（${topBiz[1]}家）` : 'N/A'}</div></div>
            <div class="stat-card p-3"><div class="text-xs text-slate-500">样本均值</div><div class="text-sm mt-1">平均涨跌幅：<span class="font-semibold ${(snapshot.avgChange ?? 0) >= 0 ? 'positive' : 'negative'}">${snapshot.avgChange === null ? 'N/A' : snapshot.avgChange.toFixed(2)}%</span></div></div>
        `;
    }

    function renderSupplyRisk(snapshot) {
        const cards = document.getElementById('supply_risk_cards');
        if (!cards) return;
        const rows = filteredData.map(row => {
            const ch = Math.abs(toNumber(row.change_pct) ?? 0);
            const pe = toNumber(row.pe_forward);
            let risk = 0;
            if (ch >= 8) risk += riskWeights.volatility;
            else if (ch >= 5) risk += riskWeights.volatility * 0.6;
            if (pe !== null && pe > 60) risk += riskWeights.valuation;
            return { row, risk: Math.min(100, Number(risk.toFixed(1))) };
        }).sort((a, b) => b.risk - a.risk).slice(0, 6);
        cards.innerHTML = rows.map(x => `<div class="stat-card p-3"><div class="flex items-center justify-between mb-1"><div class="text-sm font-semibold">${x.row.name} <span class="text-xs text-slate-400">(${x.row.code})</span></div><span class="text-xs px-2 py-0.5 rounded-full border ${x.risk >= 70 ? 'text-red-600 border-red-200 bg-red-50' : (x.risk >= 45 ? 'text-amber-600 border-amber-200 bg-amber-50' : 'text-emerald-600 border-emerald-200 bg-emerald-50')}">${x.risk >= 70 ? '高' : (x.risk >= 45 ? '中' : '低')}风险 · ${x.risk}</span></div><div class="text-xs text-slate-500">${x.row.chain_segment || '其他'} · ${x.row.business_type || '其他'}</div></div>`).join('');
    }

    function getLatestNewsItems(limit = 6) {
        const sorted = [...(newsPoolData || [])].sort((a, b) => String(b.date || '').localeCompare(String(a.date || '')));
        return sorted.slice(0, Math.min(limit, sorted.length || 0));
    }

    function renderNewsCards(items) {
        const grid = document.getElementById('news_grid');
        if (!grid) return;
        grid.innerHTML = '';
        (items || []).forEach(news => {
            const card = document.createElement('a');
            card.href = news.link || '#';
            card.target = '_blank';
            card.className = 'stat-card p-2.5 hover:border-teal-300 transition-colors';
            card.innerHTML = `<div class="text-[11px] text-teal-700 mb-0.5">${formatDateByLocale(news.date || '', false)}</div><p class="text-sm font-medium leading-snug text-slate-800" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${news.title || '暂无最新新闻'}</p>`;
            grid.appendChild(card);
        });
    }

    async function fetchLatestPayload() {
        const url = new URL('./latest_data.json', window.location.href);
        url.searchParams.set('_ts', String(Date.now()));
        const resp = await fetch(url.toString(), { cache: 'no-store' });
        if (!resp.ok) throw new Error(`latest_data_http_${resp.status}`);
        return resp.json();
    }

    function applyRuntimePayload(payload) {
        if (!payload || !Array.isArray(payload.data)) return false;
        originalData = payload.data;
        filteredData = [...originalData];
        newsPoolData = Array.isArray(payload.news_pool) ? payload.news_pool : [];
        klineRuntimeData = payload.kline_data && typeof payload.kline_data === 'object' ? payload.kline_data : {};
        currentPage = 1;
        showAllAlerts = false;
        if (payload.data_time_iso) {
            lastUpdateIso = payload.data_time_iso;
            const el = document.getElementById('last_update');
            if (el) el.dataset.updateIso = payload.data_time_iso;
        }
        renderFilters();
        applyFilters();
        return true;
    }

    async function refreshAllContent() {
        if (refreshInFlight) return;
        refreshInFlight = true;
        try {
            const payload = await fetchLatestPayload();
            const ok = applyRuntimePayload(payload);
            if (!ok) throw new Error('invalid_latest_payload');
        } catch (_) {
            const url = new URL(window.location.href);
            url.searchParams.set('_refreshTs', String(Date.now()));
            window.location.replace(url.toString());
        } finally {
            refreshInFlight = false;
        }
    }

    function applyFilters() {
        const selectedRegions = Array.from(document.querySelectorAll('.region-check:checked')).map(cb => cb.value);
        const selectedBusiness = Array.from(document.querySelectorAll('.business-check:checked')).map(cb => cb.value);
        const keyword = (document.getElementById('quick_search')?.value || '').trim().toLowerCase();
        filteredData = originalData.filter(row => {
            const regionMatch = !selectedRegions.length || selectedRegions.includes(row.region);
            const businessMatch = !selectedBusiness.length || selectedBusiness.includes(row.business_type);
            const pickMatch = !onlyPicks || row?.is_pick === true || row?.is_pick === 1 || String(row?.is_pick).toLowerCase() === 'true';
            const keywordMatch = !keyword || [row.code, row.name, row.business_type, row.invest_tags, row.board].map(v => String(v || '').toLowerCase()).some(v => v.includes(keyword));
            return regionMatch && businessMatch && pickMatch && keywordMatch;
        });
        const snapshot = computeSnapshot(filteredData);
        updateCompanyCount(filteredData.length, true);
        updateLastUpdateDisplay();
        renderSummaryCards(snapshot);
        renderPickCards();
        renderTable();
        renderNewsCards(getLatestNewsItems());
        renderAlerts(snapshot);
        renderIndustryKnowledge(snapshot);
        renderSupplyRisk(snapshot);
        initializeCharts();
    }

    function resetFilters() {
        document.querySelectorAll('.region-check, .business-check').forEach(cb => { cb.checked = true; });
        const search = document.getElementById('quick_search');
        if (search) search.value = '';
        onlyPicks = false;
        const btn = document.getElementById('pick_toggle_btn');
        if (btn) btn.textContent = '仅看入选标的：关';
        applyFilters();
    }

    function loadRiskWeights() {
        try {
            const raw = localStorage.getItem(RISK_WEIGHT_STORAGE_KEY);
            if (!raw) return;
            const parsed = JSON.parse(raw);
            Object.keys(defaultRiskWeights).forEach(key => {
                const v = Number(parsed?.[key]);
                if (Number.isFinite(v) && v >= 0) riskWeights[key] = v;
            });
        } catch (_) {}
        ['volatility', 'valuation', 'liquidity', 'segment', 'size'].forEach(key => {
            const slider = document.getElementById(`risk_weight_${key}`);
            const label = document.getElementById(`risk_weight_${key}_label`);
            if (slider) slider.value = String(riskWeights[key]);
            if (label) label.textContent = String(riskWeights[key]);
        });
    }

    function updateRiskWeight(key, value) {
        if (!(key in riskWeights)) return;
        riskWeights[key] = Math.max(0, Number(value) || 0);
        try { localStorage.setItem(RISK_WEIGHT_STORAGE_KEY, JSON.stringify(riskWeights)); } catch (_) {}
        const label = document.getElementById(`risk_weight_${key}_label`);
        if (label) label.textContent = String(riskWeights[key]);
        renderSupplyRisk(computeSnapshot(filteredData));
    }

    function resetRiskWeights() {
        Object.assign(riskWeights, defaultRiskWeights);
        try { localStorage.removeItem(RISK_WEIGHT_STORAGE_KEY); } catch (_) {}
        loadRiskWeights();
        renderSupplyRisk(computeSnapshot(filteredData));
    }

    function applyViewMode(mode) {
        const allIds = ['industry_section', 'supply_risk_section', 'news_section', 'summary_cards', 'pick_section', 'filter_section', 'action_section', 'charts_row_1', 'charts_row_2', 'table_section', 'empty_state'];
        allIds.forEach(id => document.getElementById(id)?.classList.remove('hidden'));
        if (mode === 'charts') ['filter_section', 'action_section', 'table_section', 'empty_state'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
        if (mode === 'table') ['summary_cards', 'pick_section', 'charts_row_1', 'charts_row_2', 'industry_section', 'supply_risk_section', 'news_section'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
    }

    function rearrangeBlocks(mode) {
        const root = document.getElementById('report_root');
        if (!root) return;
        const presets = {
            overview: ['summary_cards', 'industry_section', 'supply_risk_section', 'charts_row_1', 'charts_row_2', 'pick_section', 'news_section', 'filter_section', 'action_section', 'table_section', 'empty_state'],
            'table-first': ['filter_section', 'action_section', 'table_section', 'summary_cards', 'supply_risk_section', 'industry_section', 'charts_row_1', 'charts_row_2', 'pick_section', 'news_section', 'empty_state'],
            'chart-first': ['summary_cards', 'charts_row_1', 'charts_row_2', 'supply_risk_section', 'industry_section', 'pick_section', 'news_section', 'filter_section', 'action_section', 'table_section', 'empty_state']
        };
        (presets[mode] || presets.overview).forEach(id => {
            const el = document.getElementById(id);
            if (el) root.appendChild(el);
        });
    }

    function toggleTableDensity() {
        compactTable = !compactTable;
        document.getElementById('dataTable')?.classList.toggle('compact-table', compactTable);
    }

    function toggleReadingMode() {
        readingMode = readingMode === 'compact' ? 'comfortable' : 'compact';
        document.body.classList.toggle('reading-compact', readingMode === 'compact');
        document.getElementById('reading_mode_btn').textContent = `阅读模式：${readingMode === 'compact' ? '紧凑' : '舒适'}`;
        try { localStorage.setItem(READING_MODE_STORAGE_KEY, readingMode); } catch (_) {}
    }

    function toggleSectionFloater() {
        sectionFloaterVisible = !sectionFloaterVisible;
        document.body.classList.toggle('floater-hidden', !sectionFloaterVisible);
        document.getElementById('floater_mode_btn').textContent = `板块浮窗：${sectionFloaterVisible ? '开' : '关'}`;
        try { localStorage.setItem(FLOATER_VISIBLE_STORAGE_KEY, sectionFloaterVisible ? '1' : '0'); } catch (_) {}
    }

    function toggleFloaterSide() {
        floaterSide = floaterSide === 'left' ? 'right' : 'left';
        document.getElementById('floating_toc')?.classList.toggle('floater-left', floaterSide === 'left');
        try { localStorage.setItem(FLOATER_SIDE_STORAGE_KEY, floaterSide); } catch (_) {}
    }

    function toggleFloatingToc() {
        const toc = document.getElementById('floating_toc');
        const btn = document.getElementById('floating_toc_toggle');
        if (!toc || !btn) return;
        toc.classList.toggle('collapsed');
        btn.textContent = toc.classList.contains('collapsed') ? '展开' : '收起';
    }

    function toggleOnlyPicks() {
        onlyPicks = !onlyPicks;
        const btn = document.getElementById('pick_toggle_btn');
        if (btn) btn.textContent = `仅看入选标的：${onlyPicks ? '开' : '关'}`;
        applyFilters();
    }

    function randomizeNewsCards() {
        const shuffled = [...(newsPoolData || [])].sort(() => Math.random() - 0.5).slice(0, 6);
        renderNewsCards(shuffled);
    }

    function jumpTo(id) { document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }
    function goToPage(p) { currentPage = Math.min(getTotalPages(), Math.max(1, p)); renderTable(); }
    function goToPrevPage() { if (currentPage > 1) { currentPage -= 1; renderTable(); } }
    function goToNextPage() { if (currentPage < getTotalPages()) { currentPage += 1; renderTable(); } }
    function setPageSize(v) { pageSize = Number(v) || 25; currentPage = 1; renderTable(); }

    function setupAutoRefresh() {
        const sel = document.getElementById('refresh_interval');
        if (!sel) return;
        try {
            const saved = localStorage.getItem(REFRESH_INTERVAL_STORAGE_KEY);
            if (saved && Array.from(sel.options).some(o => o.value === saved)) sel.value = saved;
        } catch (_) {}
        sel.addEventListener('change', () => {
            if (refreshTimer) clearInterval(refreshTimer);
            const seconds = Number(sel.value);
            try { localStorage.setItem(REFRESH_INTERVAL_STORAGE_KEY, String(seconds)); } catch (_) {}
            if (seconds > 0) refreshTimer = setInterval(() => refreshAllContent(), seconds * 1000);
        });
        sel.dispatchEvent(new Event('change'));
    }

    function loadPreferences() {
        try {
            const mode = localStorage.getItem(READING_MODE_STORAGE_KEY);
            if (mode === 'compact') toggleReadingMode();
        } catch (_) {}
        try {
            const vis = localStorage.getItem(FLOATER_VISIBLE_STORAGE_KEY);
            if (vis === '0') toggleSectionFloater();
        } catch (_) {}
        try {
            const side = localStorage.getItem(FLOATER_SIDE_STORAGE_KEY);
            if (side === 'left') toggleFloaterSide();
        } catch (_) {}
        try {
            const profile = localStorage.getItem(LOCALE_PROFILE_STORAGE_KEY);
            if (profile) {
                const picker = document.getElementById('locale_profile');
                if (picker && Array.from(picker.options).some(o => o.value === profile)) picker.value = profile;
                applyLocaleProfile(profile, false);
            }
        } catch (_) {}
    }

    function bindLocalePicker() {
        const picker = document.getElementById('locale_profile');
        if (!picker) return;
        picker.addEventListener('change', () => applyLocaleProfile(picker.value, true));
    }

    function manualRefresh() { refreshAllContent(); }

    Object.assign(window, {
        manualRefresh, randomizeNewsCards, jumpTo, scrollToTop, toggleTableDensity, toggleReadingMode,
        toggleSectionFloater, toggleFloaterSide, toggleFloatingToc, toggleOnlyPicks, initializeCharts,
        applyFilters, resetFilters, setPageSize, goToPrevPage, goToNextPage, goToPage, applyViewMode,
        rearrangeBlocks, resetRiskWeights, updateRiskWeight, toggleAlertsExpand: () => { showAllAlerts = !showAllAlerts; renderAlerts(computeSnapshot(filteredData)); }
    });

    window.addEventListener('DOMContentLoaded', () => {
        const updateEl = document.getElementById('last_update');
        if (updateEl) lastUpdateIso = updateEl.dataset.updateIso || '';
        document.getElementById('page_size').value = String(pageSize);
        bindLocalePicker();
        loadPreferences();
        loadRiskWeights();
        applyLocaleProfile(document.getElementById('locale_profile')?.value || 'zh-CN|Asia/Shanghai', false);
        setupAutoRefresh();
        refreshAllContent();
        if (window.SemiconductorFrontendApp?.bootstrap) window.SemiconductorFrontendApp.bootstrap();
        console.log('dashboard.js loaded');
    });
})();

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
    let chartsRenderTimer = null;
    let readingMode = 'comfortable';
    let sectionFloaterVisible = true;
    let floaterSide = 'right';
    let currentLanguage = 'zh-CN';
    let currentTimeZone = 'Asia/Shanghai';
    let lastUpdateIso = '';
    let pageMode = 'all';
    let pageModeLocked = false;
    let industryRuntimePayload = {
        industry_intro: [],
        industry_basics: [],
        industry_source_refs: [],
        industry_intro_source: ''
    };
    let globalComparePayload = {
        global_compare_items: [],
        global_compare_refs: []
    };

    const SEGMENT_ORDER = ['上游', '中游', '下游', '其他'];
    const RISK_WEIGHT_STORAGE_KEY = 'semicon_risk_weights_v1';
    const READING_MODE_STORAGE_KEY = 'semicon_reading_mode_v1';
    const FLOATER_VISIBLE_STORAGE_KEY = 'semicon_floater_visible_v1';
    const FLOATER_SIDE_STORAGE_KEY = 'semicon_floater_side_v1';
    const LOCALE_PROFILE_STORAGE_KEY = 'semicon_locale_profile_v1';
    const REFRESH_INTERVAL_STORAGE_KEY = 'semicon_refresh_interval_v2';
    const VIEW_MODE_STORAGE_KEY = 'semicon_view_mode_v1';
    const LAYOUT_MODE_STORAGE_KEY = 'semicon_layout_mode_v1';
    const DEFAULT_REFRESH_SECONDS = 3600;
    const defaultRiskWeights = { volatility: 35, valuation: 25, liquidity: 12, segment: 10, size: 8 };
    const riskWeights = { ...defaultRiskWeights };
    const PAGE_SECTION_PRESETS = {
        all: ['onboarding_section', 'methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'filter_section', 'pick_section', 'action_section', 'charts_row_1', 'charts_row_2', 'industry_section', 'global_compare_section', 'supply_risk_section', 'news_section', 'table_section', 'empty_state', 'alert_banner'],
        overview: ['onboarding_section', 'methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'filter_section', 'pick_section', 'empty_state', 'alert_banner'],
        charts: ['summary_cards', 'decision_support_section', 'limit_up_section', 'filter_section', 'action_section', 'charts_row_1', 'charts_row_2', 'empty_state'],
        knowledge: ['methodology_section', 'summary_cards', 'decision_support_section', 'industry_section', 'global_compare_section', 'empty_state'],
        'risk-news': ['methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'global_compare_section', 'supply_risk_section', 'news_section', 'empty_state', 'alert_banner'],
        'data-center': ['methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'filter_section', 'action_section', 'table_section', 'empty_state']
    };
    const TOOLBAR_TARGET_BUTTONS = {
        onboarding_section: 'nav_onboarding_btn',
        methodology_section: 'nav_method_btn',
        summary_cards: 'nav_overview_btn',
        decision_support_section: 'nav_decision_btn',
        limit_up_section: 'nav_limit_up_btn',
        pick_section: 'nav_pick_btn',
        charts_row_1: 'nav_chart_btn',
        global_compare_section: 'nav_global_btn',
        supply_risk_section: 'nav_risk_btn',
        table_section: 'nav_table_btn'
    };

    const TEXTS = {
        'zh-CN': { title: '中国半导体投资看板', newsTitle: '模块E｜最新行业新闻', companiesUnit: '家公司', realTimeTrack: '实时追踪', realTimeData: '实时数据', timezoneBadge: '中国时间（Asia/Shanghai）' },
        'en-US': { title: 'China Semiconductor Investment Dashboard', newsTitle: 'Module E | Latest Industry News', companiesUnit: ' companies', realTimeTrack: 'real-time tracking', realTimeData: 'real-time data', timezoneBadge: 'EST/EDT (America/New_York)' },
        'de-DE': { title: 'China Halbleiter-Investitionsdashboard', newsTitle: 'Modul E | Neueste Branchennachrichten', companiesUnit: ' Unternehmen', realTimeTrack: 'Echtzeit-Tracking', realTimeData: 'Echtzeitdaten', timezoneBadge: 'CET/CEST (Europe/Berlin)' }
    };
    const UI_TEXTS = {
        'zh-CN': {
            quickSearchPlaceholder: '代码 / 公司 / 标签',
            top_nav_home: '总览主页', top_nav_overview: '模块A 市场快照', top_nav_charts: '模块B 图谱/K线', top_nav_knowledge: '模块C 知识课堂', top_nav_risk_news: '模块D/E 风险新闻', top_nav_data_center: '数据中心',
            toolbar_jump_label: '模块跳转', toolbar_filter_label: '视图与筛选', view_mode_label: '浏览视图', quick_search_label: '快速检索',
            view_mode_option_all: '全部', view_mode_option_charts: '仅图表', view_mode_option_table: '仅数据表',
            nav_onboarding_btn: '引导', nav_method_btn: '选股逻辑', nav_overview_btn: '概览', nav_decision_btn: '决策辅助', nav_limit_up_btn: '涨停板', nav_pick_btn: '候选精选', nav_chart_btn: '图表分析', nav_global_btn: '全球对比', nav_risk_btn: '供应链风险', nav_table_btn: '数据表',
            table_density_btn: '紧凑表格', reading_mode_btn_comfortable: '阅读模式：舒适', reading_mode_btn_compact: '阅读模式：紧凑',
            floater_mode_btn_on: '板块浮窗：开', floater_mode_btn_off: '板块浮窗：关',
            limit_up_title: '涨停板观察', limit_up_desc: '展示当日触及涨停阈值的样本公司，辅助识别过热与龙头拥挤信号。',
            global_compare_title: '模块F｜全球对比观察', global_compare_desc: '从可访问的中英文网站随机抽取全球半导体相关信息，辅助判断国内样本的相对位置。'
        },
        'en-US': {
            quickSearchPlaceholder: 'Code / company / tags',
            top_nav_home: 'Home', top_nav_overview: 'Module A Snapshot', top_nav_charts: 'Module B Charts/K-line', top_nav_knowledge: 'Module C Knowledge', top_nav_risk_news: 'Module D/E Risk & News', top_nav_data_center: 'Data Center',
            toolbar_jump_label: 'Jump List', toolbar_filter_label: 'View & Filters', view_mode_label: 'View mode', quick_search_label: 'Quick search',
            view_mode_option_all: 'All', view_mode_option_charts: 'Charts only', view_mode_option_table: 'Table only',
            nav_onboarding_btn: 'Guide', nav_method_btn: 'Method', nav_overview_btn: 'Overview', nav_decision_btn: 'Decision', nav_limit_up_btn: 'Limit-Up', nav_pick_btn: 'Candidates', nav_chart_btn: 'Charts', nav_global_btn: 'Global', nav_risk_btn: 'Risk', nav_table_btn: 'Table',
            table_density_btn: 'Compact table', reading_mode_btn_comfortable: 'Reading mode: Comfort', reading_mode_btn_compact: 'Reading mode: Compact',
            floater_mode_btn_on: 'Section floater: On', floater_mode_btn_off: 'Section floater: Off',
            limit_up_title: 'Limit-Up Board', limit_up_desc: 'Shows stocks reaching the daily limit-up threshold to flag momentum crowding risk.',
            global_compare_title: 'Module F | Global Comparison', global_compare_desc: 'Randomly sampled global semiconductor signals from accessible Chinese/English sources for relative positioning.'
        },
        'de-DE': {
            quickSearchPlaceholder: 'Code / Firma / Tags',
            top_nav_home: 'Start', top_nav_overview: 'Modul A Marktbild', top_nav_charts: 'Modul B Charts/K-Line', top_nav_knowledge: 'Modul C Wissen', top_nav_risk_news: 'Modul D/E Risiko & News', top_nav_data_center: 'Datenzentrum',
            toolbar_jump_label: 'Sprungliste', toolbar_filter_label: 'Ansicht & Filter', view_mode_label: 'Ansicht', quick_search_label: 'Schnellsuche',
            view_mode_option_all: 'Alle', view_mode_option_charts: 'Nur Charts', view_mode_option_table: 'Nur Tabelle',
            nav_onboarding_btn: 'Leitfaden', nav_method_btn: 'Methode', nav_overview_btn: 'Überblick', nav_decision_btn: 'Entscheidung', nav_limit_up_btn: 'Limit-Up', nav_pick_btn: 'Kandidaten', nav_chart_btn: 'Charts', nav_global_btn: 'Global', nav_risk_btn: 'Risiko', nav_table_btn: 'Tabelle',
            table_density_btn: 'Kompakte Tabelle', reading_mode_btn_comfortable: 'Lesemodus: Komfort', reading_mode_btn_compact: 'Lesemodus: Kompakt',
            floater_mode_btn_on: 'Bereichsfenster: Ein', floater_mode_btn_off: 'Bereichsfenster: Aus',
            limit_up_title: 'Limit-Up Beobachtung', limit_up_desc: 'Zeigt Titel am Tageslimit, um Momentum und Überhitzung schneller zu erkennen.',
            global_compare_title: 'Modul F | Globaler Vergleich', global_compare_desc: 'Zufällige globale Halbleiter-Signale aus erreichbaren chinesischen/englischen Quellen für relative Einordnung.'
        }
    };

    function getRefreshStatusEl() {
        let el = document.getElementById('refresh_status_banner');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'refresh_status_banner';
        el.className = 'panel p-3 text-xs hidden';
        const reportRoot = document.getElementById('report_root');
        if (reportRoot) {
            reportRoot.insertBefore(el, reportRoot.firstChild);
        }
        return el;
    }

    function setRefreshStatus(message = '', kind = 'info') {
        const el = getRefreshStatusEl();
        if (!el) return;
        if (!message) {
            el.classList.add('hidden');
            el.textContent = '';
            return;
        }
        el.classList.remove('hidden');
        if (kind === 'error') {
            el.className = 'panel p-3 text-xs border border-red-200 bg-red-50 text-red-700';
        } else {
            el.className = 'panel p-3 text-xs border border-emerald-200 bg-emerald-50 text-emerald-700';
        }
        el.textContent = message;
    }

    function toNumber(v) {
        const n = Number(v);
        return Number.isFinite(n) ? n : null;
    }

    function fmt(v, digits = 2) {
        const n = toNumber(v);
        return n === null ? 'N/A' : n.toFixed(digits);
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function safeText(value, fallback = 'N/A') {
        const raw = String(value ?? '').trim();
        return escapeHtml(raw || fallback);
    }

    function safeUrl(value) {
        if (!value) return '#';
        try {
            const parsed = new URL(String(value), window.location.href);
            if (parsed.protocol === 'http:' || parsed.protocol === 'https:') return parsed.toString();
        } catch (_) {}
        return '#';
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

    function getCurrentUiTexts() {
        return UI_TEXTS[currentLanguage] || UI_TEXTS['zh-CN'];
    }

    function applyStaticLocaleTexts() {
        const ui = getCurrentUiTexts();
        Object.keys(ui).forEach(id => {
            if (id.endsWith('_comfortable') || id.endsWith('_compact') || id.endsWith('_on') || id.endsWith('_off') || id === 'quickSearchPlaceholder') return;
            const el = document.getElementById(id);
            if (el) el.textContent = ui[id];
        });
        const quick = document.getElementById('quick_search');
        if (quick) quick.placeholder = ui.quickSearchPlaceholder || quick.placeholder;
        const readingBtn = document.getElementById('reading_mode_btn');
        if (readingBtn) readingBtn.textContent = readingMode === 'compact' ? ui.reading_mode_btn_compact : ui.reading_mode_btn_comfortable;
        const floaterBtn = document.getElementById('floater_mode_btn');
        if (floaterBtn) floaterBtn.textContent = sectionFloaterVisible ? ui.floater_mode_btn_on : ui.floater_mode_btn_off;
    }

    function getCurrentPathname() {
        const path = window.location.pathname || '/';
        const parts = path.split('/').filter(Boolean);
        return parts.length ? parts[parts.length - 1] : 'index.html';
    }

    function highlightCourseNavActiveLink() {
        const currentPage = getCurrentPathname();
        document.querySelectorAll('.course-nav-link').forEach(link => {
            const href = link.getAttribute('href') || '';
            const page = href.replace('./', '');
            link.classList.toggle('active', page === currentPage || (currentPage === '' && page === 'index.html'));
        });
    }

    function applyPageModeFromBody() {
        const bodyMode = (document.body?.dataset?.pageMode || 'all').trim();
        pageMode = PAGE_SECTION_PRESETS[bodyMode] ? bodyMode : 'all';
        pageModeLocked = pageMode !== 'all';

        const allowed = new Set(PAGE_SECTION_PRESETS[pageMode] || PAGE_SECTION_PRESETS.all);
        const allSections = new Set(PAGE_SECTION_PRESETS.all);
        allSections.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            el.classList.toggle('hidden', !allowed.has(id));
        });

        const viewMode = document.getElementById('view_mode');
        const layoutMode = document.getElementById('layout_mode');
        if (pageModeLocked) {
            if (viewMode) viewMode.disabled = true;
            if (layoutMode) layoutMode.disabled = true;
        }

        if (pageModeLocked) {
            document.body.classList.add('floater-hidden');
        }
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
        const tzBadge = document.getElementById('timezone_badge');
        if (tzBadge) tzBadge.textContent = t.timezoneBadge;
        applyStaticLocaleTexts();
        updateCompanyCount(filteredData.length || originalData.length, false);
        updateLastUpdateDisplay();
        const key = (document.getElementById('quick_search')?.value || '').trim().toLowerCase();
        renderNewsCards(getLatestNewsItems(6, key));
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
        const isZh = currentLanguage === 'zh-CN';
        const gainers = [...filteredData].sort((a, b) => (toNumber(b.change_pct) ?? -999) - (toNumber(a.change_pct) ?? -999));
        const losers = [...filteredData].sort((a, b) => (toNumber(a.change_pct) ?? 999) - (toNumber(b.change_pct) ?? 999));
        const topGainer = gainers[0];
        const topLoser = losers[0];
        el.innerHTML = `
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">${isZh ? '当前公司数' : 'Companies in scope'}</div><div class="text-2xl font-semibold mt-1">${snapshot.totalCount}</div></div>
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">${isZh ? '平均涨跌幅' : 'Average daily change'}</div><div class="text-2xl font-semibold mt-1 ${(snapshot.avgChange ?? 0) >= 0 ? 'positive' : 'negative'}">${snapshot.avgChange === null ? 'N/A' : snapshot.avgChange.toFixed(2)}%</div></div>
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">${isZh ? '最大涨幅' : 'Top gainer'}</div><div class="text-sm font-medium mt-1 truncate">${safeText(topGainer?.name)}</div><div class="text-xl font-semibold positive">${fmt(topGainer?.change_pct)}%</div></div>
            <div class="glass rounded-2xl p-3 border border-emerald-100 h-full"><div class="text-xs text-gray-500">${isZh ? '最大跌幅' : 'Top loser'}</div><div class="text-sm font-medium mt-1 truncate">${safeText(topLoser?.name)}</div><div class="text-xl font-semibold negative">${fmt(topLoser?.change_pct)}%</div></div>
        `;
    }

    function isPickRow(row) {
        return row?.is_pick === true || row?.is_pick === 1 || String(row?.is_pick).toLowerCase() === 'true';
    }

    function renderDecisionSupport(snapshot) {
        const container = document.getElementById('decision_support_cards');
        const meta = document.getElementById('decision_support_meta');
        if (!container) return;
        const isZh = currentLanguage === 'zh-CN';
        const sortedByScore = [...filteredData].sort((a, b) => (toNumber(b.invest_score) ?? -1) - (toNumber(a.invest_score) ?? -1));
        const scoreLeader = sortedByScore[0];
        const valueCandidate = [...filteredData]
            .filter(row => (toNumber(row.invest_score) ?? 0) >= 65 && toNumber(row.pe_forward) !== null)
            .sort((a, b) => (toNumber(a.pe_forward) ?? 9999) - (toNumber(b.pe_forward) ?? 9999))[0];
        const momentumLeader = [...filteredData]
            .filter(row => toNumber(row.change_pct) !== null)
            .sort((a, b) => (toNumber(b.change_pct) ?? -999) - (toNumber(a.change_pct) ?? -999))[0];
        const topSegment = Object.entries(snapshot.segmentCounts).sort((a, b) => b[1] - a[1])[0];
        const concentration = topSegment && snapshot.totalCount ? Number((topSegment[1] / snapshot.totalCount) * 100).toFixed(1) : '0.0';
        const pickCount = filteredData.filter(isPickRow).length;
        const riskCount = (snapshot.alerts || []).length;

        if (meta) {
            meta.textContent = isZh
                ? `当前范围：${filteredData.length}家公司，候选标的 ${pickCount} 家，异动提醒 ${riskCount} 家（|涨跌幅| > 5%）。`
                : `In scope: ${filteredData.length} companies, ${pickCount} picks, ${riskCount} volatility alerts (|chg| > 5%).`;
        }

        container.innerHTML = `
            <article class="decision-card">
                <div class="decision-kicker">${isZh ? '评分优先' : 'Score first'}</div>
                <h3 class="decision-title">${safeText(scoreLeader?.name, '暂无数据')}</h3>
                <div class="decision-main">${safeText(scoreLeader?.invest_score, 'N/A')} 分</div>
                <p class="decision-sub">${safeText(scoreLeader?.code, '-')} · ${safeText(scoreLeader?.business_type, isZh ? '未分类' : 'Unclassified')}</p>
                <div class="signal-pill signal-positive">${(toNumber(scoreLeader?.invest_score) ?? 0) >= 80 ? (isZh ? '高质量候选' : 'High-quality pick') : (isZh ? '持续观察' : 'Watchlist')}</div>
            </article>
            <article class="decision-card">
                <div class="decision-kicker">${isZh ? '估值视角' : 'Valuation view'}</div>
                <h3 class="decision-title">${safeText(valueCandidate?.name, '暂无匹配')}</h3>
                <div class="decision-main">${fmt(valueCandidate?.pe_forward)}x</div>
                <p class="decision-sub">${isZh ? 'Forward P/E（在中高评分样本中）' : 'Forward P/E among higher-score names'}</p>
                <div class="signal-pill signal-neutral">${isZh ? '结合成长性二次确认' : 'Confirm with growth data'}</div>
            </article>
            <article class="decision-card">
                <div class="decision-kicker">${isZh ? '动量线索' : 'Momentum signal'}</div>
                <h3 class="decision-title">${safeText(momentumLeader?.name, '暂无数据')}</h3>
                <div class="decision-main ${(toNumber(momentumLeader?.change_pct) ?? 0) >= 0 ? 'positive' : 'negative'}">${fmt(momentumLeader?.change_pct)}%</div>
                <p class="decision-sub">${isZh ? '当日涨跌幅领先' : 'Top intraday mover'}</p>
                <div class="signal-pill ${(toNumber(momentumLeader?.change_pct) ?? 0) >= 0 ? 'signal-positive' : 'signal-risk'}">${(toNumber(momentumLeader?.change_pct) ?? 0) >= 0 ? (isZh ? '趋势偏强' : 'Trend strong') : (isZh ? '回撤警惕' : 'Pullback risk')}</div>
            </article>
            <article class="decision-card">
                <div class="decision-kicker">${isZh ? '集中度监控' : 'Concentration check'}</div>
                <h3 class="decision-title">${topSegment ? safeText(topSegment[0]) : '暂无数据'}</h3>
                <div class="decision-main">${concentration}%</div>
                <p class="decision-sub">${isZh ? '样本主链段占比' : 'Main segment share'}</p>
                <div class="signal-pill ${Number(concentration) > 45 ? 'signal-risk' : 'signal-neutral'}">${Number(concentration) > 45 ? (isZh ? '注意分散配置' : 'Diversify exposure') : (isZh ? '分布较均衡' : 'Balanced distribution')}</div>
            </article>
        `;
    }

    function getLimitUpRows(rows = filteredData) {
        return rows
            .map(row => ({ row, chg: toNumber(row.change_pct) ?? -999 }))
            .filter(item => item.chg >= 9.5)
            .sort((a, b) => b.chg - a.chg)
            .slice(0, 10);
    }

    function renderLimitUpBoard() {
        const box = document.getElementById('limit_up_cards');
        if (!box) return;
        const isZh = currentLanguage === 'zh-CN';
        const limitUps = getLimitUpRows();
        if (!limitUps.length) {
            box.innerHTML = `<div class="stat-card p-3 text-sm text-slate-500">${isZh ? '当前筛选样本暂无触及涨停阈值（>= 9.5%）的公司。' : 'No stocks reached the limit-up threshold (>= 9.5%) in the current filter.'}</div>`;
            return;
        }
        box.innerHTML = limitUps.map(item => `
            <article class="decision-card">
                <div class="decision-kicker">${safeText(item.row.board, '板块')}</div>
                <h3 class="decision-title">${safeText(item.row.name)}</h3>
                <div class="decision-main positive">${fmt(item.chg)}%</div>
                <p class="decision-sub">${safeText(item.row.code)} · ${safeText(item.row.business_type, isZh ? '未分类' : 'Unclassified')}</p>
                <div class="signal-pill signal-risk">${isZh ? '涨停板观察' : 'Limit-up watch'}</div>
            </article>
        `).join('');
    }

    function renderGlobalComparisonCards() {
        const cards = document.getElementById('global_compare_cards');
        const refs = document.getElementById('global_compare_refs');
        if (!cards || !refs) return;
        const isZh = currentLanguage === 'zh-CN';
        const items = Array.isArray(globalComparePayload.global_compare_items) ? globalComparePayload.global_compare_items : [];
        if (!items.length) {
            cards.innerHTML = `<div class="stat-card p-3 text-sm text-slate-500">${isZh ? '暂无可展示的全球对比信息，请等待下一次自动刷新。' : 'No global comparison items yet. Please wait for next auto-refresh.'}</div>`;
            refs.textContent = '';
            return;
        }
        cards.innerHTML = items.slice(0, 8).map(item => `
            <div class="stat-card p-3">
                <div class="text-[11px] text-sky-700 mb-1">${safeText(item.source_name, 'Global Source')}</div>
                <div class="text-sm font-medium text-slate-800">${safeText(item.title, 'Global insight')}</div>
                <div class="text-xs text-slate-500 mt-1">${safeText(item.summary, '')}</div>
                <a href="${safeUrl(item.url)}" target="_blank" rel="noopener noreferrer" class="text-xs text-blue-700 hover:underline mt-2 inline-block">${isZh ? '查看来源' : 'Source'}</a>
            </div>
        `).join('');
        const sourceRefs = Array.isArray(globalComparePayload.global_compare_refs) ? globalComparePayload.global_compare_refs : [];
        refs.innerHTML = sourceRefs.length
            ? `${isZh ? '全球对比来源：' : 'Global comparison sources: '}${sourceRefs.map((src, idx) => `<a href="${safeUrl(src.url)}" target="_blank" rel="noopener noreferrer" class="text-blue-700 hover:underline">${safeText(src.name, 'source')}</a>${idx < sourceRefs.length - 1 ? '<span class="mx-1 text-slate-300">|</span>' : ''}`).join('')}`
            : '';
    }

    function renderFilters() {
        const regionDiv = document.getElementById('region_filters');
        const businessDiv = document.getElementById('business_filters');
        if (!regionDiv || !businessDiv) return;
        regionDiv.innerHTML = '';
        businessDiv.innerHTML = '';
        [...new Set(originalData.map(d => d.region).filter(Boolean))].sort().forEach(r => {
            const label = document.createElement('label');
            label.className = 'inline-flex items-center gap-1 px-4 py-2 bg-white rounded-3xl border border-gray-200 cursor-pointer hover:border-emerald-300 text-sm';
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.checked = true;
            input.className = 'region-check';
            input.value = String(r);
            input.addEventListener('change', applyFilters);
            label.appendChild(input);
            label.appendChild(document.createTextNode(` ${r}`));
            regionDiv.appendChild(label);
        });
        [...new Set(originalData.map(d => d.business_type).filter(Boolean))].sort().forEach(b => {
            const label = document.createElement('label');
            label.className = 'inline-flex items-center gap-1 px-4 py-2 bg-white rounded-3xl border border-gray-200 cursor-pointer hover:border-emerald-300 text-sm';
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.checked = true;
            input.className = 'business-check';
            input.value = String(b);
            input.addEventListener('change', applyFilters);
            label.appendChild(input);
            label.appendChild(document.createTextNode(` ${b}`));
            businessDiv.appendChild(label);
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
            card.className = 'stat-card interactive-card p-3';
            card.innerHTML = `
                <div class="flex items-center justify-between gap-2 mb-1">
                    <div class="font-medium text-sm truncate">${safeText(row.name)}</div>
                    <div class="text-xs ${gradeClass} whitespace-nowrap">评分 ${safeText(row.invest_score, 'N/A')} (${safeText(row.invest_grade, '-')})</div>
                </div>
                <div class="text-[11px] text-gray-500 mb-1 truncate">${safeText(row.code)} · ${safeText(row.board)} · ${safeText(row.business_type)}</div>
                <div class="text-[11px] text-gray-600 mb-1" style="display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden;">${safeText(row.invest_reason, '暂无说明')}</div>
                <div class="text-[11px] text-emerald-700 truncate">${safeText(row.invest_tags, '观察')}</div>
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
                <td data-label="代码" class="px-6 py-5 font-mono text-sm">${safeText(row.code)}</td>
                <td data-label="公司名称" class="px-6 py-5 max-w-[180px]"><div class="truncate font-medium">${safeText(row.name)}</div><span class="text-xs text-gray-400 block truncate">${safeText(row.english, '')}</span></td>
                <td data-label="地区" class="px-6 py-5">${safeText(row.region)}</td>
                <td data-label="板块" class="px-6 py-5">${safeText(row.board)}</td>
                <td data-label="业务类型" class="px-6 py-5">${safeText(row.business_type)}</td>
                <td data-label="市值(亿)" class="px-6 py-5 text-right">${fmt(row.market_cap)}</td>
                <td data-label="当前价格" class="px-6 py-5 text-right">${fmt(row.price)}</td>
                <td data-label="涨跌幅" class="px-6 py-5 text-right ${(changeVal >= 0 ? 'positive' : 'negative')}">${fmt(changeVal)}%</td>
                <td data-label="Trailing P/E" class="px-6 py-5 text-right">${fmt(row.pe_trailing)}</td>
                <td data-label="Forward P/E" class="px-6 py-5 text-right">${fmt(row.pe_forward)}</td>
                <td data-label="成交量" class="px-6 py-5 text-right">${row.volume ?? 'N/A'}</td>
                <td data-label="52周高/低" class="px-6 py-5 text-right">${fmt(row.high52)} / ${fmt(row.low52)}</td>
                <td data-label="投资评分" class="px-6 py-5 text-right ${score >= 80 ? 'text-emerald-600' : (score >= 65 ? 'text-blue-600' : 'text-gray-500')}">${safeText(row.invest_score, 'N/A')} (${safeText(row.invest_grade, '-')})</td>
                <td data-label="策略标签" class="px-6 py-5 text-left text-xs text-emerald-700">${safeText(row.invest_tags, '观察')}</td>
            `;
            tbody.appendChild(tr);
        });
        renderPagination();
    }

    function plotChart(id, traces, layout = {}) {
        if (typeof Plotly === 'undefined') return;
        const node = document.getElementById(id);
        if (!node) return;
        const finalLayout = { autosize: true, margin: { l: 30, r: 20, t: 20, b: 30 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', ...layout };
        const options = { responsive: true, displayModeBar: false };
        const hasPlot = Boolean(node.querySelector('.plot-container'));
        const renderer = hasPlot ? Plotly.react : Plotly.newPlot;
        renderer(id, traces, finalLayout, options).catch(() => {});
    }

    function scheduleChartsRender() {
        if (chartsRenderTimer) window.clearTimeout(chartsRenderTimer);
        chartsRenderTimer = window.setTimeout(() => initializeCharts(), 120);
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

    function getFilteredKlineEntries() {
        if (!filteredData.length) return [];
        const selectedCodes = new Set(filteredData.map(row => String(row.code || '')));
        const filteredCap = {};
        filteredData.forEach(row => { filteredCap[String(row.code || '')] = toNumber(row.market_cap) ?? 0; });
        const matched = Object.entries(klineRuntimeData || {}).filter(([, item]) => selectedCodes.has(String(item?.code || '')));
        const source = matched.length ? matched : Object.entries(klineRuntimeData || {});
        return source.sort((a, b) => {
            const capA = filteredCap[String(a[1]?.code || '')] ?? (toNumber(a[1]?.market_cap) ?? 0);
            const capB = filteredCap[String(b[1]?.code || '')] ?? (toNumber(b[1]?.market_cap) ?? 0);
            return capB - capA;
        }).slice(0, 6);
    }

    function renderKlines(entries = getFilteredKlineEntries()) {
        const container = document.getElementById('kline_container');
        if (!container) return;
        container.innerHTML = '';
        if (!entries.length) {
            container.innerHTML = '<div class="stat-card p-4 text-sm text-slate-500">当前筛选条件下暂无可展示K线。</div>';
            return;
        }
        entries.forEach(([name, d], idx) => {
            const id = `kline_${idx}`;
            const card = document.createElement('div');
            card.className = 'text-center stat-card interactive-card p-3';
            card.innerHTML = `<div class="flex items-start justify-between gap-2 mb-2"><div class="text-left"><h4 class="font-medium text-sm">${safeText(name)}</h4><div class="text-[11px] text-slate-500">${safeText(d.chain_segment, '其他')} · ${safeText(d.business_type, '其他')}</div></div><div class="text-right"><div class="text-[11px] text-slate-500">30天</div><div class="text-sm font-semibold ${Number(d.change_30d || 0) >= 0 ? 'positive' : 'negative'}">${fmt(d.change_30d)}%</div></div></div><div id="${id}" class="chart-container h-56 bg-white rounded-2xl"><div class="chart-fallback">K线加载中...</div></div>`;
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
        container.innerHTML = `<div class="alert-card bg-white border border-red-200 rounded-2xl p-4 shadow-sm"><div class="flex items-center justify-between gap-2 flex-wrap mb-3"><div class="font-semibold">实时异动（|涨跌幅| > 5%）</div><div>${alerts.length > 10 ? `<button onclick="toggleAlertsExpand()" class="px-3 py-1 rounded-lg border border-slate-200 text-xs">${showAllAlerts ? '收起' : '展开全部'}</button>` : ''}</div></div><div class="flex flex-wrap gap-2">${visible.map(i => `<div class="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs"><span class="font-medium">${safeText(i.name)}</span> <span class="${(toNumber(i.change_pct) ?? 0) >= 0 ? 'positive' : 'negative'} font-semibold">${fmt(i.change_pct)}%</span></div>`).join('')}</div></div>`;
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

    function renderIndustryStaticContent(keyword = '') {
        const introBox = document.getElementById('industry_intro_list');
        const basicsBox = document.getElementById('industry_basics_grid');
        const sourceBox = document.getElementById('industry_source_refs');
        const sourceBadge = document.getElementById('industry_intro_source_badge');
        const introItemsRaw = Array.isArray(industryRuntimePayload.industry_intro) ? industryRuntimePayload.industry_intro : [];
        const basicsItemsRaw = Array.isArray(industryRuntimePayload.industry_basics) ? industryRuntimePayload.industry_basics : [];
        const sourceItems = Array.isArray(industryRuntimePayload.industry_source_refs) ? industryRuntimePayload.industry_source_refs : [];
        const key = String(keyword || '').trim().toLowerCase();
        const dateKey = new Date().toISOString().slice(0, 10);
        const rotateBy = (dateKey.charCodeAt(0) + dateKey.charCodeAt(dateKey.length - 1)) % 7;
        const rotate = (arr) => {
            if (!arr.length) return arr;
            const idx = rotateBy % arr.length;
            return arr.slice(idx).concat(arr.slice(0, idx));
        };
        const introItems = key
            ? introItemsRaw.filter(text => String(text || '').toLowerCase().includes(key))
            : rotate(introItemsRaw);
        const basicsItems = key
            ? basicsItemsRaw.filter(item => `${String(item?.term || '')} ${String(item?.desc || '')}`.toLowerCase().includes(key))
            : rotate(basicsItemsRaw);

        if (introBox) {
            const displayIntro = (introItems.length ? introItems : introItemsRaw).slice(0, 3);
            introBox.innerHTML = displayIntro.map(text => `<div class="stat-card p-4">${safeText(text, '')}</div>`).join('');
        }
        if (basicsBox) {
            const displayBasics = (basicsItems.length ? basicsItems : basicsItemsRaw).slice(0, 9);
            basicsBox.innerHTML = displayBasics.map(item => `
                <div class="industry-basic-item">
                    <div class="term">${safeText(item?.term, '术语')}</div>
                    <div class="desc">${safeText(item?.desc, '暂无说明')}</div>
                </div>
            `).join('');
        }
        if (sourceBox && sourceItems.length) {
            const links = sourceItems.map((item, idx) => {
                const separator = idx < sourceItems.length - 1 ? '<span class="mx-1 text-slate-300">|</span>' : '';
                return `<a href="${safeUrl(item?.url)}" target="_blank" rel="noopener noreferrer" class="text-teal-700 hover:underline">${safeText(item?.name, '参考来源')}</a>${separator}`;
            }).join('');
            sourceBox.innerHTML = `${currentLanguage === 'zh-CN' ? '信息来源：' : 'Sources: '}${links}`;
        }
        if (sourceBadge && industryRuntimePayload.industry_intro_source) {
            sourceBadge.textContent = `${currentLanguage === 'zh-CN' ? '来源：' : 'Source: '}${industryRuntimePayload.industry_intro_source}`;
        }
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
        cards.innerHTML = rows.map(x => `<div class="stat-card p-3"><div class="flex items-center justify-between mb-1"><div class="text-sm font-semibold">${safeText(x.row.name)} <span class="text-xs text-slate-400">(${safeText(x.row.code)})</span></div><span class="text-xs px-2 py-0.5 rounded-full border ${x.risk >= 70 ? 'text-red-600 border-red-200 bg-red-50' : (x.risk >= 45 ? 'text-amber-600 border-amber-200 bg-amber-50' : 'text-emerald-600 border-emerald-200 bg-emerald-50')}">${x.risk >= 70 ? '高' : (x.risk >= 45 ? '中' : '低')}风险 · ${x.risk}</span></div><div class="text-xs text-slate-500">${safeText(x.row.chain_segment, '其他')} · ${safeText(x.row.business_type, '其他')}</div></div>`).join('');
    }

    function getLatestNewsItems(limit = 6, keyword = '') {
        const sorted = [...(newsPoolData || [])].sort((a, b) => String(b.date || '').localeCompare(String(a.date || '')));
        const key = String(keyword || '').trim().toLowerCase();
        const filtered = key
            ? sorted.filter(item => `${String(item?.title || '')} ${String(item?.date || '')}`.toLowerCase().includes(key))
            : sorted;
        return filtered.slice(0, Math.min(limit, filtered.length || 0));
    }

    function renderNewsCards(items) {
        const grid = document.getElementById('news_grid');
        if (!grid) return;
        grid.innerHTML = '';
        (items || []).forEach(news => {
            const card = document.createElement('a');
            card.href = safeUrl(news.link);
            card.target = '_blank';
            card.rel = 'noopener noreferrer';
            card.className = 'stat-card interactive-card p-2.5 hover:border-teal-300 transition-colors';
            card.innerHTML = `<div class="text-[11px] text-teal-700 mb-0.5">${formatDateByLocale(news.date || '', false)}</div><p class="text-sm font-medium leading-snug text-slate-800" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${safeText(news.title, '暂无最新新闻')}</p>`;
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
        industryRuntimePayload = {
            industry_intro: Array.isArray(payload.industry_intro) ? payload.industry_intro : [],
            industry_basics: Array.isArray(payload.industry_basics) ? payload.industry_basics : [],
            industry_source_refs: Array.isArray(payload.industry_source_refs) ? payload.industry_source_refs : [],
            industry_intro_source: String(payload.industry_intro_source || '')
        };
        globalComparePayload = {
            global_compare_items: Array.isArray(payload.global_compare_items) ? payload.global_compare_items : [],
            global_compare_refs: Array.isArray(payload.global_compare_refs) ? payload.global_compare_refs : []
        };
        currentPage = 1;
        showAllAlerts = false;
        if (payload.data_time_iso) {
            lastUpdateIso = payload.data_time_iso;
            const el = document.getElementById('last_update');
            if (el) el.dataset.updateIso = payload.data_time_iso;
        }
        const key = (document.getElementById('quick_search')?.value || '').trim().toLowerCase();
        renderIndustryStaticContent(key);
        renderGlobalComparisonCards();
        renderFilters();
        applyFilters();
        setRefreshStatus('', 'info');
        return true;
    }

    function bootstrapFromInitialPayload() {
        const payloadEl = document.getElementById('initial_payload');
        if (!payloadEl?.textContent) return false;
        try {
            const payload = JSON.parse(payloadEl.textContent);
            return applyRuntimePayload(payload);
        } catch (_) {
            return false;
        }
    }

    async function refreshAllContent() {
        if (refreshInFlight) return;
        refreshInFlight = true;
        try {
            const payload = await fetchLatestPayload();
            const ok = applyRuntimePayload(payload);
            if (!ok) throw new Error('invalid_latest_payload');
        } catch (err) {
            // Keep current data on fetch errors to avoid reload loops and blank pages.
            setRefreshStatus(`自动刷新失败：${String(err?.message || 'unknown_error')}。已保留当前页面数据，将在下个周期自动重试。`, 'error');
        } finally {
            refreshInFlight = false;
        }
    }

    function applyFilters() {
        const allRegionFilters = document.querySelectorAll('.region-check');
        const allBusinessFilters = document.querySelectorAll('.business-check');
        const selectedRegions = Array.from(document.querySelectorAll('.region-check:checked')).map(cb => cb.value);
        const selectedBusiness = Array.from(document.querySelectorAll('.business-check:checked')).map(cb => cb.value);
        const keyword = (document.getElementById('quick_search')?.value || '').trim().toLowerCase();
        filteredData = originalData.filter(row => {
            const regionMatch = allRegionFilters.length === 0 || (selectedRegions.length > 0 && selectedRegions.includes(row.region));
            const businessMatch = allBusinessFilters.length === 0 || (selectedBusiness.length > 0 && selectedBusiness.includes(row.business_type));
            const pickMatch = !onlyPicks || isPickRow(row);
            const keywordMatch = !keyword || [row.code, row.name, row.business_type, row.invest_tags, row.board].map(v => String(v || '').toLowerCase()).some(v => v.includes(keyword));
            return regionMatch && businessMatch && pickMatch && keywordMatch;
        });
        const snapshot = computeSnapshot(filteredData);
        updateCompanyCount(filteredData.length, true);
        updateLastUpdateDisplay();
        renderSummaryCards(snapshot);
        renderDecisionSupport(snapshot);
        renderLimitUpBoard();
        renderPickCards();
        renderTable();
        renderNewsCards(getLatestNewsItems(6, keyword));
        renderIndustryStaticContent(keyword);
        renderGlobalComparisonCards();
        renderAlerts(snapshot);
        renderIndustryKnowledge(snapshot);
        renderSupplyRisk(snapshot);
        renderKlines(getFilteredKlineEntries());
        scheduleChartsRender();
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
        if (pageModeLocked) return;
        const allIds = ['onboarding_section', 'methodology_section', 'industry_section', 'global_compare_section', 'supply_risk_section', 'news_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'pick_section', 'filter_section', 'action_section', 'charts_row_1', 'charts_row_2', 'table_section', 'empty_state'];
        allIds.forEach(id => document.getElementById(id)?.classList.remove('hidden'));
        if (mode === 'charts') ['onboarding_section', 'methodology_section', 'filter_section', 'action_section', 'table_section', 'empty_state'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
        if (mode === 'table') ['onboarding_section', 'methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'pick_section', 'charts_row_1', 'charts_row_2', 'industry_section', 'global_compare_section', 'supply_risk_section', 'news_section'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
        try { localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode); } catch (_) {}
    }

    function rearrangeBlocks(mode) {
        const root = document.getElementById('report_root');
        if (!root) return;
        const presets = {
            overview: ['onboarding_section', 'methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'industry_section', 'global_compare_section', 'supply_risk_section', 'pick_section', 'charts_row_1', 'charts_row_2', 'news_section', 'filter_section', 'action_section', 'table_section', 'empty_state'],
            'table-first': ['onboarding_section', 'methodology_section', 'filter_section', 'action_section', 'table_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'supply_risk_section', 'industry_section', 'global_compare_section', 'charts_row_1', 'charts_row_2', 'pick_section', 'news_section', 'empty_state'],
            'chart-first': ['onboarding_section', 'methodology_section', 'summary_cards', 'decision_support_section', 'limit_up_section', 'charts_row_1', 'charts_row_2', 'supply_risk_section', 'industry_section', 'global_compare_section', 'pick_section', 'news_section', 'filter_section', 'action_section', 'table_section', 'empty_state']
        };
        (presets[mode] || presets.overview).forEach(id => {
            const el = document.getElementById(id);
            if (el) root.appendChild(el);
        });
        updateFloatingTocActive();
        try { localStorage.setItem(LAYOUT_MODE_STORAGE_KEY, mode); } catch (_) {}
    }

    function toggleTableDensity() {
        compactTable = !compactTable;
        document.getElementById('dataTable')?.classList.toggle('compact-table', compactTable);
    }

    function toggleReadingMode() {
        readingMode = readingMode === 'compact' ? 'comfortable' : 'compact';
        document.body.classList.toggle('reading-compact', readingMode === 'compact');
        applyStaticLocaleTexts();
        try { localStorage.setItem(READING_MODE_STORAGE_KEY, readingMode); } catch (_) {}
    }

    function toggleSectionFloater() {
        sectionFloaterVisible = !sectionFloaterVisible;
        document.body.classList.toggle('floater-hidden', !sectionFloaterVisible);
        applyStaticLocaleTexts();
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
        const key = (document.getElementById('quick_search')?.value || '').trim().toLowerCase();
        const latestPool = getLatestNewsItems(18, key);
        const shuffled = [...latestPool].sort(() => Math.random() - 0.5).slice(0, 6);
        renderNewsCards(shuffled);
    }

    function updateFloatingTocActive() {
        const links = Array.from(document.querySelectorAll('.floating-toc-link[data-target]'));
        if (!links.length) return;
        const offset = 160;
        let currentTarget = '__top';
        links.forEach(link => {
            const target = link.dataset.target;
            if (!target || target === '__top') return;
            const section = document.getElementById(target);
            if (section && section.getBoundingClientRect().top <= offset) currentTarget = target;
        });
        links.forEach(link => {
            const active = link.dataset.target === currentTarget;
            link.classList.toggle('active', active);
            if (active) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
        });
        Object.entries(TOOLBAR_TARGET_BUTTONS).forEach(([targetId, btnId]) => {
            const btn = document.getElementById(btnId);
            if (!btn) return;
            btn.classList.toggle('active', targetId === currentTarget);
        });
    }

    function hardenExternalLinks() {
        document.querySelectorAll('a[target="_blank"]').forEach(anchor => {
            if (!anchor.rel || !anchor.rel.includes('noopener')) {
                anchor.rel = 'noopener noreferrer';
            }
        });
    }

    function jumpTo(id) { document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }
    function goToPage(p) { currentPage = Math.min(getTotalPages(), Math.max(1, p)); renderTable(); }
    function goToPrevPage() { if (currentPage > 1) { currentPage -= 1; renderTable(); } }
    function goToNextPage() { if (currentPage < getTotalPages()) { currentPage += 1; renderTable(); } }
    function setPageSize(v) { pageSize = Number(v) || 25; currentPage = 1; renderTable(); }

    function setupAutoRefresh() {
        const sel = document.getElementById('refresh_interval');
        if (!sel) {
            if (refreshTimer) clearInterval(refreshTimer);
            refreshTimer = setInterval(() => refreshAllContent(), DEFAULT_REFRESH_SECONDS * 1000);
            return;
        }
        const hasDefault = Array.from(sel.options).some(o => Number(o.value) === DEFAULT_REFRESH_SECONDS);
        if (!hasDefault) {
            sel.value = String(DEFAULT_REFRESH_SECONDS);
        }
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
        try {
            const savedViewMode = localStorage.getItem(VIEW_MODE_STORAGE_KEY);
            const viewModeEl = document.getElementById('view_mode');
            if (savedViewMode && viewModeEl && Array.from(viewModeEl.options).some(opt => opt.value === savedViewMode)) {
                viewModeEl.value = savedViewMode;
                applyViewMode(savedViewMode);
            }
        } catch (_) {}
        try {
            const savedLayoutMode = localStorage.getItem(LAYOUT_MODE_STORAGE_KEY);
            const layoutModeEl = document.getElementById('layout_mode');
            if (savedLayoutMode && layoutModeEl && Array.from(layoutModeEl.options).some(opt => opt.value === savedLayoutMode)) {
                layoutModeEl.value = savedLayoutMode;
                rearrangeBlocks(savedLayoutMode);
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
        highlightCourseNavActiveLink();
        applyPageModeFromBody();
        const pageSizeSelect = document.getElementById('page_size');
        if (pageSizeSelect) pageSizeSelect.value = String(pageSize);
        bindLocalePicker();
        loadPreferences();
        loadRiskWeights();
        applyLocaleProfile(document.getElementById('locale_profile')?.value || 'zh-CN|Asia/Shanghai', false);
        if (!bootstrapFromInitialPayload()) {
            setRefreshStatus('初始数据加载失败，正在尝试从最新数据源获取...', 'error');
        }
        setupAutoRefresh();
        refreshAllContent();
        hardenExternalLinks();
        updateFloatingTocActive();
        window.addEventListener('scroll', updateFloatingTocActive, { passive: true });
        if (window.SemiconductorFrontendApp?.bootstrap) window.SemiconductorFrontendApp.bootstrap();
        console.log('dashboard.js loaded');
    });
})();

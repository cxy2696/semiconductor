# 架构说明

版本 3.0 · 2026-11-11

## 1. 系统上下文

```text
┌────────────────────┐        ┌──────────────────────────┐
│ 东方财富行情接口   │        │ open.er-api.com 汇率     │
└─────────┬──────────┘        └────────────┬─────────────┘
          │                                │
┌─────────▼──────────┐        ┌────────────▼─────────────┐
│ 白名单媒体 RSS     │        │ data/symbols.json 映射   │
└─────────┬──────────┘        └────────────┬─────────────┘
          └──────────────┬─────────────────┘
                         ▼
              semcore fetch（可失败，不阻塞构建）
                         ▼
        data/snapshots/latest.json（唯一输入，提交入库）
                         ▼
   semcore analytics → semcore build（Jinja2 + SVG）
                         ▼
     docs/（HTML / CSS / JS / JSON / sitemap）
                         ▼
              GitHub Pages（静态托管）
```

设计约束：

- **无服务器、无数据库**：站点是纯静态产物。
- **构建期取数**：浏览器不访问第三方 API，避免 CORS、限流与隐私问题。
- **可降级**：抓取失败时使用上一份快照，页面显示数据时点与过期标记。
- **单一事实来源**：公司主数据、分类、界面文案与内容分别只有一处。

## 2. 目录与职责

| 路径 | 职责 | 不要放什么 |
| --- | --- | --- |
| `data/universe.csv` | 175 家公司主数据，含四语名称与备注、`founded` 与 `fiscal_year_end` | 行情、评分 |
| `data/taxonomy.json` | 四语的环节 / 角色 / 产品 / 国家 / 市场标签；70 个产品标签 | 公司列表 |
| `data/i18n/*.json` | `en`、`zh`、`ja`、`de` 的界面文案 | 长文内容 |
| `content/knowledge/*.md` | 扁平的 `<slug>_<suffix>.md` 长文（12 个主题 × 4 种语言） | 界面文案 |
| `data/glossary.json` | 52 条四语术语及解释 | 公司数据 |
| `data/snapshots/` | 行情快照（构建输入） | 手工编辑的“修正值” |
| `semcore/sources/` | 外部适配器 | 业务规则 |
| `semcore/analytics.py` | 因子、分数、风险、市场状态 | HTML |
| `semcore/build.py` | 页面编排与上下文 | 数据抓取 |
| `templates/` | HTML 结构 | 内联数据计算 |
| `assets/` | 设计系统与渐进增强 JS | 业务数据 |
| `docs/` | 构建产物（GitHub Pages） | 手工修改 |
| `documentation/` | 产品 / 架构 / 数据 / 方法 / 运营 / 路线图，四语 | 用户可见页面 |

## 3. 构建流水线

1. **加载配置**：`config.py` 确定路径、四种语言与站点 URL。
2. **加载主数据**：`universe.load_universe()` 读取 CSV，并按 `taxonomy` 校验枚举、唯一性与官网格式。
3. **读取快照**：`market.load_snapshot()` 读取 `latest.json`；缺失则报错并提示先运行 `fetch`。
4. **计算分析**：`Analytics.build()` 合并公司、行情与汇率，再计算因子、分数、风险标签、环节统计、市场状态与研究清单。
5. **加载内容**：`content.load_all_knowledge()` 解析每种语言的 front matter 与 Markdown；`load_glossary()` 读取术语。
6. **渲染页面**：对四种语言分别渲染 7 个固定页面 + 12 个知识页 + 175 个公司页，并复制资源。
7. **输出附加文件**：`sitemap.xml`、`robots.txt`、`.nojekyll`、`latest_data.json`、`api/snapshot.{en,zh,ja,de}.json`、旧路由重定向、`/en/` 重定向桩与 `404.html`。
8. **校验**：`validate_artifacts()` 检查必需文件、JSON 契约、legacy 字段以及是否引入 CDN。

## 4. 模块边界

### sources/eastmoney.py

- `resolve_secid()`：按市场规则生成候选 `secid`，逐个验证代码匹配，并把结果写入缓存。
- `fetch_quote()` / `fetch_history()`：带重试与 15 秒超时的 HTTP 请求。
- `build_market_entry()`：把原始字段整理成快照条目（价格、涨跌、市值、PE/PB/ROE、52 周区间、30 日收益、30 日 OHLC）。
- 失败时返回 `None`，由 `market.py` 决定回退。

### sources/news.py

- `fetch_feed()` 并发抓取，单个 feed 失败不影响其他 feed。
- `parse_feed()` 同时支持 RSS 2.0 与 Atom。
- `_relevant()` 按关键词过滤，去重后保留前 24 条。

### market.py

- 线程池（默认 6）抓取 175 家公司。
- 失败时优先复用上一份快照条目，并标记 `status="stale"`。
- 合并汇率与新闻，写出 `latest.json` 与按日期的快照，保留最近 30 份。

### analytics.py

- 纯计算，无 I/O，便于测试。
- `Row` 是模板与 JSON 共用的中间表示。
- 百分位按环节分组；不足 8 家的分组退回全样本。
- `Analytics` 聚合环节统计、国家与市场统计、市场状态、清单以及动能两端。

### build.py

- `SiteBuilder` 负责视图字典（每种语言的本地化视图）、URL 计算、页面上下文、模板渲染与产物写入。
- 每个页面上下文都包含 `t`（文案）、`href()`、`alternates`、`analytics`、`tax` 与 `snapshot`。
- `_legacy_payload()` 生成 `latest_data.json`，保持 iOS 兼容。
- `_localized_payload()` 生成四种语言的 `api/snapshot.{lang}.json`。

### validate.py

- `validate_data()`：主数据、i18n、知识与术语。
- `validate_artifacts()`：页面、JSON、sitemap、CDN 检查与 hreflang。
- CI 在构建前运行数据检查，构建后运行完整检查。

## 5. 四语架构

| 层 | 机制 |
| --- | --- |
| URL | 英文在根路径，中文 `/zh/`，日文 `/ja/`，德文 `/de/`；每页都有绝对 alternates |
| 旧 URL | `/en/...` 重定向桩指向对应的根路径页面 |
| 界面文案 | `data/i18n/{en,zh,ja,de}.json`，键完全对齐并由 CI 校验 |
| 数据标签 | `taxonomy.json` 中的 `label` 对象，取值为 `{zh, en, ja, de}` |
| 长文 | 扁平文件 `content/knowledge/<slug>_<suffix>.md`；slug 跨语言一致 |
| 术语 | 单文件含四种语言字段；页面按当前语言渲染，并在对照区展示另外三种语言 |
| 数字 | 千分位与小数位统一；货币后缀保留 ISO 代码 |
| 日期 | 站点使用 Asia/Shanghai（UTC+8）；数据日期随来源 |

**为什么不在浏览器里切换语言？** 独立 URL 更利于分享、SEO、缓存与无 JS 环境；语言切换在构建期生成，不依赖运行时字典。代价是页面数量 ×4，但静态托管完全可以承受。

## 6. 链接模型

- `SiteBuilder._page_path(locale, key, slug)` 是唯一的路径生成函数。
- 模板只通过 `href('company', id)` 这类函数获取链接，避免硬编码相对路径。
- `rel_href()` 计算从当前页到目标页的相对路径，因此直接用 `file://` 打开也能工作。
- 资源使用 `root + 'assets/...'`，其中 `root` 由页面深度决定。

## 7. 渲染与性能

- **零第三方资源**：无 Tailwind、无 Plotly、无字体 CDN。
- 图表在 Python 中生成 SVG：散点、迷你走势与 52 周区间条。
- CSS 约 30 KB，JS 约 8 KB（未压缩）；多数页面为 30–120 KB 的 HTML，公司索引因为服务端渲染 175 行而更大。
- 公司表格在服务端渲染，筛选与排序使用原生 JS，不引入虚拟列表。
- 首屏无阻塞脚本；`<head>` 中一小段内联主题脚本用于避免主题闪烁。

## 8. 可访问性与 SEO

- 语义化的 `header/nav/main/footer`、`aria-current`、`aria-sort` 与跳过链接。
- 表格包含 `thead`，可排序表头支持键盘操作。
- 图表带有 `role="img"`、`aria-label` 与 `<title>`。
- `prefers-reduced-motion` 关闭动画；对比度满足 AA。
- 每页都有 canonical URL、`hreflang` alternates 与 OG 标签；知识页带有 Article JSON-LD；sitemap 覆盖全部页面。

## 9. 扩展点

| 需求 | 改动 |
| --- | --- |
| 新增公司 | 在 `universe.csv` 加一行，并运行 fetch 生成符号映射 |
| 新增环节 | 在 `taxonomy.json` 的 `stages` 中加一项，并更新受控产品词表 |
| 新增语言 | `config.LOCALES` + `data/i18n/<lang>.json` + 使用新后缀的知识文件 + 翻译文档 |
| 新增数据源 | 在 `sources/` 下新增适配器，并在 `market.fetch_snapshot()` 中合并 |
| 新增页面 | `templates/` 新模板 + `PAGES` + `SiteBuilder` 方法 + 导航 |
| 新增图表 | 在 `charts.py` 增加纯函数，并通过上下文传入 `Markup` |
| 改变方法 | 更新 `analytics.py` + `METHODOLOGY_en.md` 及其译本 + 站内方法页 + 主版本号 |

## 10. 测试策略

| 层 | 测试 |
| --- | --- |
| 数据 | `test_universe.py`：枚举、重复上市、必填字段 |
| 内容 | `test_content.py`：front matter、Markdown 转义、12 个主题在四种语言中对齐 |
| 文案 | `test_i18n.py`：键对齐、无空值、格式化 |
| 分析 | `test_analytics.py`：分数边界、缺失因子归一、状态阈值、清单规则 |
| 构建 | `test_build.py`：全量构建、legacy 契约、无 CDN |
| 产物 | `semcore validate`：文件、JSON、sitemap、hreflang |

## 11. 已知技术债

1. 单一行情源（东方财富），缺少第二来源做交叉校验。
2. 欧洲标的的 `secid` 依赖种子映射；新增上市可能需要手工探测。
3. 因子在每次构建时全量重算，未做缓存；以 175 家的规模还不构成性能问题。
4. 新闻关键词表硬编码为英文，对中文、日文与德文媒体的覆盖有限。
5. 公司页未输出结构化的 `Corporation` 数据；SEO 仍主要依靠文章。

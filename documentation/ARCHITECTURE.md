# 架构说明

版本 2.0 · 2026-11-11

## 1. 系统上下文

```text
┌────────────────────┐        ┌──────────────────────────┐
│  东方财富行情接口   │        │  open.er-api.com 汇率     │
└─────────┬──────────┘        └────────────┬─────────────┘
          │                                │
┌─────────▼──────────┐        ┌────────────▼─────────────┐
│ 白名单媒体 RSS      │        │ data/symbols.json 映射    │
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
- **单一事实来源**：公司主数据、分类、文案、内容分别只有一处。

## 2. 目录与职责

| 路径 | 职责 | 不要放什么 |
| --- | --- | --- |
| `data/universe.csv` | 124 家公司主数据 | 行情、评分 |
| `data/taxonomy.json` | 环节 / 角色 / 产品 / 国家 / 市场标签（三语） | 公司列表 |
| `data/i18n/*.json` | 界面文案（221+ 键） | 长文内容 |
| `content/knowledge/{lang}/*.md` | 知识长文 | 界面文案 |
| `data/glossary.json` | 三语术语 | 公司数据 |
| `data/snapshots/` | 行情快照（构建输入） | 手工编辑的“修正值” |
| `semcore/sources/` | 外部适配器 | 业务规则 |
| `semcore/analytics.py` | 因子、分数、风险、状态 | HTML |
| `semcore/build.py` | 页面编排与上下文 | 数据抓取 |
| `templates/` | HTML 结构 | 内联数据计算 |
| `assets/` | 设计系统与渐进增强 JS | 业务数据 |
| `docs/` | 构建产物（GitHub Pages） | 手工修改 |
| `documentation/` | 产品 / 架构 / 数据 / 方法 / 运营 | 用户可见页面 |

## 3. 构建流水线

1. **加载配置**：`config.py` 确定路径、语言、站点 URL。
2. **加载主数据**：`universe.load_universe()` 读取 CSV 并按 `taxonomy` 校验枚举、唯一性、官网格式。
3. **读取快照**：`market.load_snapshot()` 读取 `latest.json`；缺失则报错并提示先运行 fetch。
4. **计算分析**：`Analytics.build()` 合并公司、行情、汇率，计算因子、分数、风险、环节统计、市场状态与研究清单。
5. **加载内容**：`content.load_all_knowledge()` 解析 front matter 与 Markdown；`load_glossary()` 读取术语。
6. **渲染页面**：对每种语言渲染 7 个固定页面 + 9 篇知识 + 124 个公司页；复制资源。
7. **输出附加文件**：`sitemap.xml`、`robots.txt`、`.nojekyll`、`latest_data.json`、`api/snapshot.{lang}.json`、旧路由重定向、404。
8. **校验**：`validate_artifacts()` 检查必需文件、JSON 契约、legacy 字段、无 CDN。

## 4. 模块边界

### sources/eastmoney.py

- `resolve_secid()`：按市场规则生成候选 `secid`，逐个验证代码匹配，写入缓存。
- `fetch_quote()` / `fetch_history()`：带重试的 HTTP 请求，超时 15s。
- `build_market_entry()`：把原始字段整理成快照 entry（价格、涨跌、市值、PE/PB/ROE、52 周区间、30 日收益、30 日 OHLC）。
- 失败返回 `None`，由 `market.py` 决定回退。

### sources/news.py

- `fetch_feed()` 并发抓取，单 feed 失败不影响其他。
- `parse_feed()` 同时支持 RSS 2.0 与 Atom。
- `_relevant()` 按关键词过滤，去重后取前 24 条。

### market.py

- 线程池（默认 6）抓取 124 家。
- 失败时优先复用上一份快照 entry，标记 `status="stale"`。
- 合并 FX 与新闻，写出 `latest.json` 与日期快照，保留最近 30 份。

### analytics.py

- 纯函数式计算，无 I/O，便于测试。
- `Row` 是模板与 JSON 的中间表示。
- 百分位按环节分组，不足 8 家退回全样本。
- `Analytics` 聚合：环节统计、国家/市场统计、状态、清单、动能两端。

### build.py

- `SiteBuilder` 负责：视图字典（每种语言的本地化视图）、URL 计算、页面上下文、模板渲染、产物写入。
- 页面上下文统一包含：`t`（文案）、`href()`、`alternates`、`analytics`、`tax`、`snapshot`。
- `latest_data.json` 由 `_legacy_payload()` 生成，保持 iOS 兼容。

### validate.py

- `validate_data()`：主数据、i18n、知识、术语。
- `validate_artifacts()`：页面、JSON、sitemap、CDN、hreflang。
- CI 在构建前后各跑一次。

## 5. 三语架构

| 层 | 机制 |
| --- | --- |
| URL | 中文在根路径，英文 `/en/`，日文 `/ja/`，每页都有绝对 alternates |
| 界面文案 | `data/i18n/{lang}.json`，键完全对齐，CI 校验 |
| 数据标签 | `taxonomy.json` 的 `label` 为 `{zh, en, ja}` 对象 |
| 长文 | `content/knowledge/{lang}/{slug}.md`，slug 跨语言一致 |
| 术语 | 单文件三语字段，页面按当前语言渲染并附三语对照 |
| 数字 | 千分位与小数位统一；货币后缀保留 ISO 代码 |
| 日期 | 站点统一使用 Asia/Shanghai 时区（UTC+8），数据日期随源 |

**为什么不用前端 i18n 切换？** 独立 URL 更利于分享、SEO、缓存与无 JS 环境；语言切换由构建期生成，不依赖运行时字典。代价是页面数量 ×3，但静态托管无压力。

## 6. 链接模型

- `SiteBuilder._page_path(locale, key, slug)` 是唯一的路径生成函数。
- 模板只通过 `href('company', id)` 等函数取链接，避免硬编码相对路径。
- `rel_href()` 计算从当前页到目标页的相对路径，因此 `file://` 直接打开也能工作。
- `assets` 使用 `root + 'assets/...'`，`root` 由页面深度决定。

## 7. 渲染与性能

- **零第三方资源**：无 Tailwind、无 Plotly、无字体 CDN。
- 图表在 Python 中生成 SVG：散点、迷你走势、52 周区间条。
- CSS 约 30KB，JS 约 8KB（未压缩），单页 HTML 30–120KB。
- 表格 124 行服务端渲染，筛选/排序由原生 JS 完成，无虚拟列表。
- 首屏无阻塞脚本；主题在 `<head>` 内联一小段以避免闪烁。

## 8. 可访问性与 SEO

- 语义化 `header/nav/main/footer`、`aria-current`、`aria-sort`、跳过链接。
- 表格有 `thead` 与可排序表头的键盘操作。
- 图表带 `role="img"`、`aria-label` 与 `<title>`。
- `prefers-reduced-motion` 关闭动画；对比度满足 AA。
- 每页有 canonical、hreflang、OG 标签；知识页有 Article JSON-LD；sitemap 覆盖全部页面。

## 9. 扩展点

| 需求 | 改动 |
| --- | --- |
| 新增公司 | 在 `universe.csv` 加一行 + 运行 fetch 生成符号映射 |
| 新增环节 | `taxonomy.json` 的 `stages` 加一项，更新受控产品词表 |
| 新增语言 | `config.LOCALES` + `data/i18n/<lang>.json` + `content/knowledge/<lang>/` |
| 新增数据源 | 在 `sources/` 新建适配器，在 `market.fetch_snapshot()` 中合并 |
| 新增页面 | `templates/` 新模板 + `PAGES` + `SiteBuilder` 方法 + 导航 |
| 新增图表 | `charts.py` 增加纯函数，在上下文中传入 `Markup` |
| 改变方法 | 更新 `analytics.py` + `METHODOLOGY.md` + 站内方法页 + 主版本号 |

## 10. 测试策略

| 层 | 测试 |
| --- | --- |
| 数据 | `test_universe.py`：枚举、重复上市、必填字段 |
| 内容 | `test_content.py`：front matter、Markdown 转义、三语主题对齐 |
| 文案 | `test_i18n.py`：键对齐、无空值、格式化 |
| 分析 | `test_analytics.py`：分数边界、缺失因子归一、状态阈值、清单规则 |
| 构建 | `test_build.py`：全量构建、legacy 契约、无 CDN |
| 产物 | `semcore validate`：文件、JSON、sitemap、hreflang |

## 11. 已知技术债

1. 单一行情源（东方财富），缺少第二源交叉校验。
2. 欧洲标的的 `secid` 依赖种子映射，新增标的可能需要手工探测。
3. 因子计算在每次构建时全量重算，未缓存；当前规模（124 家）无性能问题。
4. 新闻关键词表为硬编码英文词，中文媒体覆盖有限。
5. 公司页未生成结构化 `Corporation` 数据；SEO 仍以文章为主。

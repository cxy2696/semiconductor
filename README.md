# SiliconScope · 半导体产业情报台

**全球半导体产业链的中英日三语研究看板** · A trilingual research desk for the global semiconductor value chain.

覆盖 **8 个产业链环节、11 个总部地区、124 家上市公司**，把行情、结构、知识与方法放在同一张可核查的桌面上。所有页面为构建期生成的静态文件，不依赖任何 CDN 或前端框架。

- 站点：<https://cxy2696.github.io/semiconductor/>
- 仓库：<https://github.com/cxy2696/semiconductor>

> 仅用于产业研究与学习，不构成投资建议。Not investment advice.

---

## 预览

![SiliconScope 首页](documentation/screenshots/home.png)

![公司图谱](documentation/screenshots/companies.png)

| 深色模式 | 移动端 |
| --- | --- |
| ![深色模式](documentation/screenshots/home-dark.png) | ![移动端](documentation/screenshots/home-mobile.png) |

---

## 为什么重做

原版是一个以 A 股为主的中文看板：1,000 行单文件脚本、Tailwind/Plotly CDN、把抓取失败当作构建失败、评分口径不透明。v2 保留“看板”这个形态，重做了产品逻辑与工程结构：

| 维度 | v1 | v2 |
| --- | --- | --- |
| 覆盖 | 中国 A 股 + 2 只港股 | 中国大陆 / 香港 / 台湾 / 美国 / 日本 / 韩国 / 欧洲，124 家 |
| 语言 | 中 / 英 / 德 | **中 / 英 / 日**，独立 URL + hreflang |
| 知识 | 抓取百科段落当“术语” | 9 篇结构化长文 + 52 条三语术语表 |
| 评分 | 不公开权重的“投资评分” | 公开公式的研究优先级 + 数据完整度 + 风险标签 |
| 前端 | CDN + 运行时渲染 | 构建期 HTML/SVG，零第三方资源 |
| 数据 | 抓取失败即构建失败 | 快照兜底 + 覆盖率 + 过期标记 |
| 运维 | 无文档 | 产品 / 架构 / 数据 / 方法 / 运营五份文档 + CI 校验 |

## 功能

- **首页**：市场状态读数（宽度 / 中位涨幅 / 离散度）、产业链结构、动能两端、估值-质量散点、三个公开规则生成的研究清单、行业动态。
- **公司图谱**：124 家公司，可按环节、总部、上市地筛选与排序，附 30 日走势、PE/PB/ROE、研究优先级与数据完整度。
- **公司页**：定位、行情、52 周区间、因子拆解、同环节对比、延伸阅读。
- **产业链**：主流程 6 个环节 + 设备/材料支撑层，逐段解释“怎么赚钱、看什么指标、谁在里面”。
- **知识库**：9 篇中英日长文（产业链、晶圆工艺、光刻、设备材料、先进封装、存储与 HBM、硅周期、政策、财务与估值）。
- **术语表**：52 条三语对照术语，支持全文搜索与分类筛选。
- **方法**：因子定义、权重、阈值、数据完整度、已知局限与免责声明。
- **兼容**：继续输出旧版 `latest_data.json`，现有 iOS 客户端无需改动即可解码。
- **iOS 客户端**：`ios/` 目录保留原 SwiftUI 应用，仍指向 `latest_data.json`；迁移到新版 `/api/` 的计划见路线图。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 用仓库内快照构建（无需联网）
python -m semcore build
python -m semcore serve --port 8000

# 抓取最新行情 / 汇率 / 资讯并重建
python -m semcore refresh

# 校验数据契约与产物
python -m semcore validate

# 测试
python -m pytest
```

构建产物在 `docs/`：`docs/index.html`（中文）、`docs/en/`、`docs/ja/`、`docs/api/`、`docs/latest_data.json`。

## 目录结构

```text
semcore/                 Python 构建工具（数据抓取 → 分析 → 渲染）
  sources/               东方财富行情、RSS 资讯、汇率
  analytics.py           因子、研究优先级、风险标签、市场状态
  build.py               静态站点生成（zh / en / ja）
  validate.py            数据契约与产物校验
  content.py             极简 Markdown 渲染与内容加载
data/
  universe.csv           公司主数据（唯一事实来源，124 行）
  taxonomy.json          环节 / 角色 / 产品 / 国家 / 市场标签（三语）
  glossary.json          52 条三语术语
  i18n/{zh,en,ja}.json   界面文案（221 个键，三语对齐）
  symbols.json           公司 → 行情源代码的已核验映射
  snapshots/             行情快照（构建的唯一输入）
content/knowledge/       9 个主题 × 3 种语言
templates/               Jinja2 模板
assets/                  设计系统 CSS + 原生 JS（无依赖）
docs/                    构建产物（GitHub Pages）
documentation/           产品 / 架构 / 数据 / 方法 / 运营文档
tests/                   pytest 测试
ios/                     SwiftUI iPhone 客户端（消费 legacy payload）
documentation/           产品 / 架构 / 数据 / 方法 / 运营文档 + 截图
```

## iOS 客户端

`ios/` 是原仓库的 SwiftUI 应用，仍在消费 `docs/latest_data.json`。v2 保留了这个 payload，并做了字段级兼容校验（124 家公司、40 组 K 线、无空值数组），因此现有客户端无需改动即可继续解码。

升级方式（见 [ROADMAP](documentation/ROADMAP.md)）：

```bash
brew install xcodegen
xcodegen generate --spec ios/project.yml
open ios/SemiconductorApp.xcodeproj
```

## 数据与口径

- **行情、估值、52 周区间**：东方财富公开行情接口（延时或收盘价）。
- **汇率**：open.er-api.com，失败时回退东方财富汇率对，再失败则复用上一份快照。
- **行业动态**：白名单媒体 RSS（Tom's Hardware、Semiconductor Digest、EE Times、DigiTimes、Semiconductor Today），只保留标题、来源、日期与链接。
- **快照**：`data/snapshots/latest.json` 是构建的唯一输入。抓取失败不会让站点变空，而是把上一份数据标记为 `stale` 并显示。
- **分类**：每家公司只保留一个主上市地，按主要收入来源归入 8 个环节之一。
- 详细字段、单位与限制见 [documentation/DATA.md](documentation/DATA.md)。

## 评分逻辑（摘要）

```text
研究优先级 = 0.30 × 质量(ROE 百分位)
           + 0.25 × 估值(静态 PE 倒数百分位)
           + 0.25 × 动能(30 日涨跌 60% + 52 周区间位置 40%)
           + 0.20 × 规模(log 市值百分位)
```

- 百分位在同一环节内计算；环节样本少于 8 家时退回全样本。
- 缺失因子按剩余权重重新归一，并扣减“数据完整度”。
- 分数只用于**安排阅读顺序**，不是买卖建议、目标价或盈利预测。

完整公式、阈值与局限见 [documentation/METHODOLOGY.md](documentation/METHODOLOGY.md)，或站内 `/methodology.html`。

## 三语实现

- 中文为默认语言，挂在站点根路径；英文 `/en/`、日文 `/ja/`。
- 每个页面输出 `hreflang` 与 `x-default`，语言切换保留当前页面。
- 数据标签存于 `taxonomy.json` 与 `i18n/*.json`，内容存于 `content/knowledge/{lang}/`。
- CI 校验三种语言的键与主题完全对齐，缺一即失败。

## 部署

GitHub Pages 使用 Actions 工作流 `.github/workflows/pages.yml`：

1. 仓库 Settings → Pages → Source 选择 **GitHub Actions**。
2. 工作流在每日 08:30（北京时间）与手动触发时运行 `python -m semcore refresh`，随后构建、校验、部署。
3. 若行情源不可用，工作流仍会用上一份快照完成构建，并在页面标注数据时点。

`SITE_URL` 环境变量可覆盖 canonical 域名（默认 `https://cxy2696.github.io/semiconductor`）。

## 参与

数据修正、术语补充、文档改进都欢迎。请附可核查来源，并说明影响范围。见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

- 代码：[MIT](LICENSE)
- 文字内容：CC BY 4.0
- 行情与新闻：版权归原始提供方，本站仅做引用与链接

引用请注明 **SiliconScope** 与访问日期。

---

**免责声明**：本站仅用于产业研究与学习，不构成任何证券买卖建议。数据可能存在延迟或错误，请以交易所与公司公告为准。

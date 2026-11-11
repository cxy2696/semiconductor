# 数据说明：来源、字段、口径与限制

版本 3.0 · 2026-11-11

本文件是数据契约的权威说明。所有字段定义、单位与失败处理均以此为准；站内展示口径与本文件不一致时，以本文件为准，并应提 PR 修正页面。

## 1. 数据流

```text
东方财富公开行情接口 ─┐
open.er-api.com 汇率 ─┼─→ semcore fetch ─→ data/snapshots/latest.json ─→ semcore build ─→ docs/
白名单媒体 RSS ───────┘        （唯一输入）              （静态 HTML / SVG / JSON）
```

- 页面**不**直接请求第三方 API；所有数据在构建时写入快照。
- 快照提交到仓库，因此站点可以离线构建，每次构建都可审计、可回滚。
- 抓取失败不会清空页面：单家公司回退到上一份快照并标记 `stale`；整体失败时保留上一份 `latest.json`，页面显示过期提示。

## 2. 来源清单

| 数据 | 来源 | 接口 / 方式 | 频率 | 许可 / 备注 |
| --- | --- | --- | --- | --- |
| 行情、估值、市值 | 东方财富 | `push2.eastmoney.com/api/qt/stock/get`、`push2his.../kline/get` | 每个交易日构建时 | 公开接口；版权归原始提供方；仅展示与引用 |
| 汇率 | open.er-api.com | `GET /v6/latest/USD` | 每日 | 免费、无需 key |
| 汇率回退 | 东方财富外汇对 | `USDCNH`、`USDJPY`、`USDKRW`、`USDEUR`、`USDHKD` | 同上 | 仅在主来源失败时使用 |
| 行业动态 | Tom's Hardware / Semiconductor Digest / EE Times / DigiTimes / Semiconductor Today | RSS | 每日 | 仅保留标题、来源、日期与链接；标题必须命中半导体关键词；每个来源最多 6 条 |
| 分类与术语 | 本仓库维护 | `data/taxonomy.json`、`glossary.json` | 按需 | CC BY 4.0 |

> 东方财富接口没有公开文档，字段语义可能变化。CI 校验与快照兜底用于降低风险；发现异常时，按 `OPERATIONS_cn.md` 中的 runbook 处理。

## 3. 公司主数据（`data/universe.csv`）

该 CSV 是公司覆盖范围的唯一事实来源。它包含 **175 行**，一行一家公司，每家公司只保留一个主上市地。

| 列 | 类型 | 定义 | 缺失 / 回退 |
| --- | --- | --- | --- |
| `id` | string | 用于 URL 与快照的稳定标识 | 必填 |
| `ticker` | string | 主上市地代码 | 必填 |
| `exchange` | string | 交易所代码（如 `SSE`、`NASDAQ`） | 必填 |
| `mic` | string | ISO 10383 市场标识代码 | 必填 |
| `market` | enum | 主上市地：CN、HK、TW、US、JP、KR、EU | 必填；共 7 个取值 |
| `country` | enum | 总部地区：CN、HK、TW、US、JP、KR、NL、DE、FR、CH、GB、IL、TH | 必填；共 13 个取值 |
| `stage` | enum | 8 个产业链环节之一 | 必填 |
| `role` | enum | 9 种角色之一（fabless、foundry、IDM、memory、equipment、materials、OSAT、module、EDA/IP） | 必填 |
| `products` | string | 以管道符分隔的受控产品标签 | 可为空；共 70 个标签 |
| `hq` | string | 总部城市 | 必填 |
| `website` | URL | 官方网站，仅允许 `http(s)://` | 可为空 |
| `currency` | ISO 4217 | 交易货币 | 必填 |
| `quote_venue` | string | 行情场所覆盖；为空表示自动解析，`unpriced` 表示公司保留在研究样本中但不参与行情统计 | 空或 `unpriced` |
| `name_zh` | string | 中文展示名 | 必填 |
| `name_en` | string | 英文展示名 | 必填 |
| `name_ja` | string | 日文展示名 | 必填 |
| `name_de` | string | 德文展示名 | 为空时回退到 `name_en` |
| `note_zh` | string | 中文公司备注 | 可为空 |
| `note_en` | string | 英文公司备注 | 可为空 |
| `note_ja` | string | 日文公司备注 | 可为空 |
| `note_de` | string | 德文公司备注 | 为空时回退到英文备注 |
| `founded` | string | 成立年份，四位数字 | 可选；仅在存在时展示 |
| `fiscal_year_end` | string | 财年结束月份，`01`–`12` | 可选；仅在存在时展示 |

13 个总部地区为中国大陆、香港、台湾、美国、日本、韩国、荷兰、德国、法国、瑞士、英国、以色列和泰国。7 个上市地为 A 股（CN）、港股（HK）、台股（TW）、美股（US）、日股（JP）、韩股（KR）和欧股（EU）。

## 4. 快照字段字典

| 字段 | 类型 | 单位 | 定义 | 缺失值 |
| --- | --- | --- | --- | --- |
| `price` | float | 本币 | 最新可得的收盘价或延时价 | `null` |
| `prev_close` | float | 本币 | 前一交易日收盘价 | `null` |
| `change_pct` | float | % | 最近交易日涨跌幅 | `null` |
| `ret_30d` | float | % | 最近 30 个交易日涨跌幅 | `null` |
| `ret_ytd` | float | % | 年初至今涨跌幅 | `null` |
| `volume` | float | 股 | 最近交易日成交量 | `null` |
| `market_cap` | float | 本币 | 总市值（东方财富 `f116`） | `null` |
| `market_cap_usd` | float | USD | `market_cap × usd_per_unit[currency]` | `null` |
| `pe` | float | 倍 | 静态市盈率（`f164`，最近年度 EPS） | `null`；≤ 0 表示亏损 |
| `pb` | float | 倍 | 市净率（`f167`） | `null` |
| `roe` | float | % | 净资产收益率（`f173`） | `null` |
| `turnover` | float | % | 换手率（`f168`） | `null` |
| `high_52w` / `low_52w` | float | 本币 | 最近 250 个交易日的最高 / 最低价 | `null` |
| `history` | object | 本币 | 最近 30 个交易日的 OHLCV | 空数组 |
| `status` | string | — | `ok` / `stale` / `missing` | — |
| `as_of` | date | — | 最近交易日（数据日期） | `null` |

### 汇率

`fx.usd_per_unit` 表示“1 单位本币值多少美元”，由 `1 / rate(USD→local)` 推导。USD 固定为 1.0。缺失币种先回退到上一份快照，再回退到静态常数，并把 `fx.status` 标记为 `fallback` 或 `stale`。

### 52 周区间

用最近 250 个交易日近似自然年，因为不同市场的节假日日历不一致。区间位置 = `(price − low) / (high − low)`，并裁剪到 `[0, 1]`。

### 行情时点

`as_of` 是最近一根日线的日期，而不是抓取时间。`snapshot.generated_at` 是抓取完成的时间。两者相差超过 48 小时时，`stale` 标记生效。

## 5. 快照结构（schema v2）

下面的取值仅作示意并经过删节，用于展示契约的形状，不代表当前快照。

```json
{
  "schema_version": 2,
  "site_version": "3.0.0",
  "generated_at": "2026-11-11T13:06:50+08:00",
  "dataset": "live",
  "universe_size": 175,
  "coverage": { "priced": 173, "total": 175, "ratio": 0.9886 },
  "fx": {
    "usd_per_unit": { "USD": 1.0, "CNY": 0.1496, "TWD": 0.0305, "JPY": 0.0063, "KRW": 0.00074, "EUR": 1.1205, "HKD": 0.1275 },
    "source": "open.er-api.com",
    "as_of": "…",
    "status": "ok"
  },
  "quotes": {
    "tsmc": {
      "status": "ok", "price": 2285.0, "currency": "TWD",
      "change_pct": 2.24, "ret_30d": -7.11, "market_cap": 59255465450000,
      "pe": 26.49, "pb": 9.21, "roe": 21.58,
      "high_52w": 2590.0, "low_52w": 1375.0,
      "as_of": "2026-11-10", "source": "Eastmoney",
      "history": { "dates": ["…"], "open": [], "high": [], "low": [], "close": [], "volume": [] }
    }
  },
  "news": [ { "title": "…", "link": "https://…", "source": "EE Times", "published": "2026-11-10", "lang": "en" } ],
  "errors": [],
  "sources": { "quotes": "Eastmoney public quote API", "fx": "open.er-api.com", "news": "RSS: …" }
}
```

`dataset`：`live`（至少 60% 有价格）、`partial`（低于阈值）、`fixture`（测试）。

## 6. 兼容 payload

`docs/latest_data.json` 是为现有 iOS 客户端保留的旧格式。字段映射如下：

| 旧字段 | 新来源 |
| --- | --- |
| `data[].code` | `ticker` |
| `data[].business_type` | 环节短标签（中文，供旧版客户端使用） |
| `data[].market_cap` | `market_cap` / 1e8（亿，本币） |
| `data[].invest_score` | `priority` |
| `data[].invest_grade` | priority ≥ 80 A / ≥ 65 B / ≥ 50 C / 其余 D |
| `data[].invest_tags` | 风险标签 |
| `data[].is_pick` | priority ≥ 70 |
| `kline_data` | 市值前 40 家公司的 30 日 OHLC |
| `news_pool` | 快照新闻（title / link / date） |
| `industry_intro` / `industry_basics` | 来自知识库与术语表的中文摘要 |

新代码应使用 `/api/snapshot.{lang}.json`（`en`、`zh`、`ja`、`de`），其结构由 `semcore/build.py::_localized_payload` 定义。英文（`en`）是默认语言。

## 7. 行情源与符号映射

- `data/symbols.json` 保存**已核验**的公司 ID → 东方财富 `secid` 映射，包含 `method`（`seed` / `probe`）、`checked` 日期与解析到的名称。
- 自动解析规则：
  - A 股：`1.<code>`（沪）/ `0.<code>`（深）
  - 港股：`116.<5 位>`
  - 美股：依次探测 `105` / `106` / `107`
  - 日股：`176.<code>`
  - 台股：`178.<code>`（上柜尝试 `179`）
  - 韩股：`177.<code>`
  - 欧股：优先使用种子映射，因为接口中的欧洲交易所编号与股票代码并不一致
- 解析成功后写入缓存，下一轮直接复用。人工修改必须同时核对名称与价格。
- 无法定价的标的（当前仅 ASM International）保留在研究样本中，`quote_venue = "unpriced"`；它们不参与行情统计，页面会说明原因。

## 8. 质量控制

| 检查 | 位置 | 失败后果 |
| --- | --- | --- |
| 主数据列、枚举、唯一性、官网格式 | `validate_data()` | CI 失败 |
| 四语 i18n 键对齐 | `validate_data()` | CI 失败 |
| 12 个知识主题在四种语言中的 slug 完全一致 | `validate_data()` | CI 失败 |
| 术语在 `zh`、`en`、`ja`、`de` 中完整 | `validate_data()` | CI 失败 |
| 产物存在、JSON 可解析、legacy 字段齐全 | `validate_artifacts()` | CI 失败 |
| 无第三方 CDN 资源 | `validate_artifacts()` | CI 失败 |
| 覆盖率与错误列表 | 关于页 / 构建日志 | 人工复核 |

## 9. 已知限制

1. 行情为延时或收盘数据，不适合盘中决策。
2. 静态 PE 对高增长与亏损公司不友好；亏损公司没有估值因子。
3. 缺少营收增速、订单与产能利用率等基本面字段。
4. 东方财富对部分欧洲与 OTC 标的覆盖不完整；价格可能来自第二上市地或 ADR。
5. 汇率为每日参考汇率，跨币种比较存在误差。
6. 复权价格无法完全消除分拆、剥离等公司行为造成的阶跃；极端单日波动需要人工复核。
7. 新闻只按标题关键词过滤并去重，不做事实核查；边缘标题可能仍会出现。
8. 分类属于编辑判断，业务发生变化的公司需要季度复核。

## 10. 保留与清理

- `data/snapshots/` 保留最近 30 份快照（`SNAPSHOT_KEEP`），由 `save_snapshot()` 自动清理。
- `docs/` 产物每次构建都全量重建，不保留历史页面。
- 历史分数不单独存档；如需回测，用对应日期的快照重新构建。

## 11. 许可与引用

- 行情与新闻版权归原始提供方；本站仅做引用、链接与有限展示。
- 本站原创文字与分类数据以 CC BY 4.0 发布。
- 引用格式：`SiliconScope, <页面标题>, <URL>, 访问日期 <YYYY-MM-DD>`。

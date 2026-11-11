# 数据说明：来源、字段、口径与限制

版本 2.0 · 2026-11-11

本文件是数据契约的权威说明。所有字段定义、单位与失败处理均以此为准；站内展示口径与本文件不一致时，以本文件为准并提 PR 修正。

## 1. 数据流

```text
东方财富公开行情接口 ─┐
open.er-api.com 汇率 ─┼─→ semcore fetch ─→ data/snapshots/latest.json ─→ semcore build ─→ docs/
白名单媒体 RSS ───────┘        （唯一输入）              （静态 HTML / SVG / JSON）
```

- 页面**不**直接请求第三方接口；所有数据在构建时写入快照。
- 快照提交到仓库，保证离线可构建、可审计、可回滚。
- 抓取失败不会清空页面：单家公司回退到上一份快照并标记 `stale`；整体失败时保留上一份 `latest.json` 并在页面显示过期提示。

## 2. 来源清单

| 数据 | 来源 | 接口 / 方式 | 频率 | 许可 / 备注 |
| --- | --- | --- | --- | --- |
| 行情、估值、市值 | 东方财富 | `push2.eastmoney.com/api/qt/stock/get`、`push2his.../kline/get` | 每个交易日构建时 | 公开接口，版权归原始提供方；仅展示与引用 |
| 汇率 | open.er-api.com | `GET /v6/latest/USD` | 每日 | 免费、无需 key |
| 汇率回退 | 东方财富外汇对 | `USDCNH`、`USDJPY`、`USDKRW`、`USDEUR`、`USDHKD` | 同上 | 仅在前者失败时使用 |
| 行业动态 | Tom's Hardware / Semiconductor Digest / EE Times / DigiTimes / Semiconductor Today | RSS | 每日 | 仅保留标题、来源、日期、链接；标题必须命中半导体关键词，每来源最多 6 条 |
| 分类与术语 | 本仓库编辑维护 | `data/taxonomy.json`、`glossary.json` | 按需 | CC BY 4.0 |

> 东方财富接口未公开文档，字段语义可能变化。CI 的校验与快照兜底用于降低风险；发现异常时按 `OPERATIONS.md` 的 runbook 处理。

## 3. 字段字典

| 字段 | 类型 | 单位 | 定义 | 缺失值 |
| --- | --- | --- | --- | --- |
| `price` | float | 本币 | 最新可得收盘价或延时价 | `null` |
| `prev_close` | float | 本币 | 前一交易日收盘价 | `null` |
| `change_pct` | float | % | 最近交易日涨跌幅 | `null` |
| `ret_30d` | float | % | 最近 30 个交易日收盘价涨跌幅 | `null` |
| `ret_ytd` | float | % | 年初至今涨跌幅 | `null` |
| `volume` | float | 股 | 最近交易日成交量 | `null` |
| `market_cap` | float | 本币 | 总市值（东方财富 `f116`） | `null` |
| `market_cap_usd` | float | USD | `market_cap × usd_per_unit[currency]` | `null` |
| `pe` | float | 倍 | 静态市盈率（`f164`，最近年度 EPS） | `null`；≤0 表示亏损 |
| `pb` | float | 倍 | 市净率（`f167`） | `null` |
| `roe` | float | % | 净资产收益率（`f173`） | `null` |
| `turnover` | float | % | 换手率（`f168`） | `null` |
| `high_52w` / `low_52w` | float | 本币 | 最近 250 个交易日最高 / 最低价 | `null` |
| `history` | object | 本币 | 最近 30 个交易日的 OHLCV | 空数组 |
| `status` | string | — | `ok` / `stale` / `missing` | — |
| `as_of` | date | — | 最近交易日（数据日期） | `null` |

### 汇率

`fx.usd_per_unit` 表示“1 单位本币值多少美元”，由 `1 / rate(USD→本地)` 得到。USD 固定为 1.0。缺失币种按上一份快照、再按静态常数回退，并在 `fx.status` 标记 `fallback` / `stale`。

### 52 周区间

用最近 250 个交易日的高/低点近似自然年，原因是不同市场节假日不一致。区间位置 = `(price − low) / (high − low)`，裁剪到 `[0, 1]`。

### 行情时点

`as_of` 取最近一根日线的日期，而非抓取时间。`snapshot.generated_at` 是抓取完成时间。两者相差超过 48 小时时，`stale` 标记生效。

## 4. 快照结构（schema v2）

```json
{
  "schema_version": 2,
  "site_version": "2.0.0",
  "generated_at": "2026-11-11T06:24:28+08:00",
  "dataset": "live",
  "universe_size": 124,
  "coverage": { "priced": 123, "total": 124, "ratio": 0.9919 },
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

`dataset`：`live`（≥60% 有价格）、`partial`（低于阈值）、`fixture`（测试）。

## 5. 兼容 payload

`docs/latest_data.json` 是为现有 iOS 客户端保留的旧格式，字段映射：

| 旧字段 | 新来源 |
| --- | --- |
| `data[].code` | `ticker` |
| `data[].business_type` | 环节短标签（中文） |
| `data[].market_cap` | `market_cap` / 1e8（亿，本币） |
| `data[].invest_score` | `priority` |
| `data[].invest_grade` | priority ≥80 A / ≥65 B / ≥50 C / 其余 D |
| `data[].invest_tags` | 风险标签 |
| `data[].is_pick` | priority ≥ 70 |
| `kline_data` | 市值前 40 家的 30 日 OHLC |
| `news_pool` | 快照新闻（title / link / date） |
| `industry_intro` / `industry_basics` | 知识库与术语表的中文摘要 |

新代码应使用 `/api/snapshot.{lang}.json`，其结构见 `semcore/build.py::_localized_payload`。

## 6. 行情源与符号映射

- `data/symbols.json` 保存公司 ID → 东方财富 `secid` 的**已核验**映射，含 `method`（`seed` / `probe`）、`checked` 日期与解析到的名称。
- 自动解析规则：
  - A 股：`1.<code>`（沪）/ `0.<code>`（深）
  - 港股：`116.<5 位>`
  - 美股：`105` / `106` / `107` 依次探测
  - 日股：`176.<code>`
  - 台股：`178.<code>`（上柜尝试 `179`）
  - 韩股：`177.<code>`
  - 欧股：优先使用种子映射（欧洲交易所在接口中的编号与代码不统一）
- 解析成功后写入缓存；下一轮直接复用。人工修改必须验证名称与价格。
- 无法定价的标的（当前仅 ASM International）保留在研究样本中，`quote_venue = "unpriced"`，不参与行情统计，页面显示说明。

## 7. 质量控制

| 检查 | 位置 | 失败后果 |
| --- | --- | --- |
| 主数据列、枚举、唯一性、官网格式 | `validate_data()` | CI 失败 |
| 三语键对齐、知识主题对齐、术语三语完整 | `validate_data()` | CI 失败 |
| 产物存在、JSON 可解析、legacy 字段齐全 | `validate_artifacts()` | CI 失败 |
| 无第三方 CDN 资源 | `validate_artifacts()` | CI 失败 |
| 覆盖率、错误列表 | 关于页 / 构建日志 | 人工复核 |

## 8. 已知限制

1. 行情为延时或收盘数据，不适合盘中决策。
2. 静态 PE 对高增长/亏损公司不友好；亏损公司估值因子缺失。
3. 缺少营收增速、订单、产能利用率等基本面字段。
4. 东方财富对部分欧洲、OTC 标的覆盖不完整，价格可能来自二级上市或 ADR。
5. 汇率为日度中间价，跨币种比较存在误差。
6. 前复权价格无法完全消除分拆、剥离等公司行为造成的阶跃，极端单日波动需人工复核。
7. 新闻只做标题关键词筛选与去重，不做事实核查；可能仍有边缘标题。
8. 分类由编辑判断，公司业务变化需要季度复核。

## 9. 保留与清理

- `data/snapshots/` 保留最近 30 份（`SNAPSHOT_KEEP`），由 `save_snapshot()` 自动清理。
- 构建产物 `docs/` 每次全量重建，不保留历史页面。
- 历史分数不单独存档；如需回测，使用对应日期的快照重新构建。

## 10. 许可与引用

- 行情与新闻版权归原始提供方；本站仅做引用、链接与有限展示。
- 本站原创的文字与分类数据以 CC BY 4.0 发布。
- 引用格式：`SiliconScope, <页面标题>, <URL>, 访问日期 <YYYY-MM-DD>`。

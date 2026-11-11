# データ：出典・フィールド・定義・限界

バージョン 3.0 · 2026-11-11

本ドキュメントはデータ契約の正式な記述です。フィールドの定義、単位、障害時の扱いは本ドキュメントに従います。ページの記述と食い違う場合は本ドキュメントが優先され、プルリクエストでページを修正するものとします。

## 1. データフロー

```text
Eastmoney public quote API ─┐
open.er-api.com FX ─────────┼─→ semcore fetch ─→ data/snapshots/latest.json ─→ semcore build ─→ docs/
Whitelisted media RSS ──────┘        (single input)              (static HTML / SVG / JSON)
```

- ページはサードパーティ API を**直接呼びません**。すべてのデータはビルド時にスナップショットへ書き込まれます。
- スナップショットはリポジトリにコミットされるため、オフラインでもビルドでき、すべてのビルドが検証可能かつ巻き戻し可能です。
- 取得に失敗してもページが空になることはありません。個別の企業は前回のスナップショットにフォールバックして `stale` とマークされ、全体が失敗した場合は前回の `latest.json` を保持し、ページに stale の通知を表示します。

## 2. ソース一覧

| データ | 出典 | インターフェース / 方法 | 頻度 | ライセンス / 注記 |
| --- | --- | --- | --- | --- |
| 株価・バリュエーション・時価総額 | Eastmoney | `push2.eastmoney.com/api/qt/stock/get`、`push2his.../kline/get` | 取引日ごとのビルド時 | 公開インターフェース。著作権は提供元に帰属し、表示と引用のみに使用 |
| 為替 | open.er-api.com | `GET /v6/latest/USD` | 日次 | 無料、キー不要 |
| 為替フォールバック | Eastmoney の通貨ペア | `USDCNH`、`USDJPY`、`USDKRW`、`USDEUR`、`USDHKD` | 上記と同じ | プライマリソースが失敗した場合のみ使用 |
| 産業ニュース | Tom's Hardware / Semiconductor Digest / EE Times / DigiTimes / Semiconductor Today | RSS | 日次 | タイトル・出典・日付・リンクのみ。各タイトルは半導体キーワードに一致する必要があり、1 ソースあたり最大 6 件 |
| 分類と用語集 | 本リポジトリで管理 | `data/taxonomy.json`、`glossary.json` | 必要時 | CC BY 4.0 |

> Eastmoney のインターフェースは非公開で、フィールドの意味が変わる可能性があります。CI での検証とスナップショットへのフォールバックでリスクを抑えていますが、異常が見られた場合は `OPERATIONS_jp.md` のランブックに従ってください。

## 3. 企業マスタデータ（`data/universe.csv`）

CSV は企業カバレッジの唯一の真実の源です。**175 行**があり、1 行が 1 社に対応し、各社は主上場市場を 1 つだけ持ちます。

| 列 | 型 | 定義 | 欠損 / フォールバック |
| --- | --- | --- | --- |
| `id` | string | URL とスナップショットで使う安定した識別子 | 必須 |
| `ticker` | string | 主上場のコード | 必須 |
| `exchange` | string | 取引所コード（例：`SSE`、`NASDAQ`） | 必須 |
| `mic` | string | ISO 10383 の市場識別コード | 必須 |
| `market` | enum | 主上場市場：CN、HK、TW、US、JP、KR、EU | 必須。全部で 7 値 |
| `country` | enum | 本社地域：CN、HK、TW、US、JP、KR、NL、DE、FR、CH、GB、IL、TH | 必須。全部で 13 値 |
| `stage` | enum | バリューチェーンの 8 工程のいずれか | 必須 |
| `role` | enum | 9 つのロールのいずれか（fabless、foundry、IDM、memory、equipment、materials、OSAT、module、EDA/IP） | 必須 |
| `products` | string | 統制語彙の製品タグをパイプ区切りで指定 | 空を許容。全部で 70 タグ |
| `hq` | string | 本社の所在都市 | 必須 |
| `website` | URL | 公式サイト。`http(s)://` のみ | 空でも可 |
| `currency` | ISO 4217 | 取引通貨 | 必須 |
| `quote_venue` | string | 株価取得先の上書き。空なら自動解決、`unpriced` なら調査対象には残すが株価統計からは除外 | 空または `unpriced` |
| `name_zh` | string | 中国語の表示名 | 必須 |
| `name_en` | string | 英語の表示名 | 必須 |
| `name_ja` | string | 日本語の表示名 | 必須 |
| `name_de` | string | ドイツ語の表示名 | 空の場合は `name_en` にフォールバック |
| `note_zh` | string | 中国語の企業メモ | 空でも可 |
| `note_en` | string | 英語の企業メモ | 空でも可 |
| `note_ja` | string | 日本語の企業メモ | 空でも可 |
| `note_de` | string | ドイツ語の企業メモ | 空の場合は英語のメモにフォールバック |
| `founded` | string | 設立年（4 桁） | 任意。存在する場合のみ表示 |
| `fiscal_year_end` | string | 決算月。`01`〜`12` | 任意。存在する場合のみ表示 |

13 の本社地域は、中国本土、香港、台湾、米国、日本、韓国、オランダ、ドイツ、フランス、スイス、イギリス、イスラエル、タイです。7 つの上場市場は、A 株（CN）、香港株（HK）、台湾株（TW）、米国株（US）、日本株（JP）、韓国株（KR）、欧州株（EU）です。

## 4. スナップショットのフィールド辞書

| フィールド | 型 | 単位 | 定義 | 欠損値 |
| --- | --- | --- | --- | --- |
| `price` | float | 現地通貨 | 最新の入手可能な終値または遅延株価 | `null` |
| `prev_close` | float | 現地通貨 | 前営業日の終値 | `null` |
| `change_pct` | float | % | 直近営業日の騰落率 | `null` |
| `ret_30d` | float | % | 直近 30 営業日の騰落率 | `null` |
| `ret_ytd` | float | % | 年初来の騰落率 | `null` |
| `volume` | float | 株 | 直近営業日の出来高 | `null` |
| `market_cap` | float | 現地通貨 | 時価総額（Eastmoney `f116`） | `null` |
| `market_cap_usd` | float | USD | `market_cap × usd_per_unit[currency]` | `null` |
| `pe` | float | 倍 | 静的 PER（`f164`、直近年度の EPS） | `null`。≤ 0 は赤字を意味する |
| `pb` | float | 倍 | PBR（`f167`） | `null` |
| `roe` | float | % | ROE（`f173`） | `null` |
| `turnover` | float | % | 売買回転率（`f168`） | `null` |
| `high_52w` / `low_52w` | float | 現地通貨 | 直近 250 営業日の最高値 / 最安値 | `null` |
| `history` | object | 現地通貨 | 直近 30 営業日の OHLCV | 空の配列 |
| `status` | string | — | `ok` / `stale` / `missing` | — |
| `as_of` | date | — | 直近の営業日（データ日付） | `null` |

### 為替

`fx.usd_per_unit` は「現地通貨 1 単位が何米ドルに相当するか」を意味し、`1 / rate(USD→local)` として導出します。USD は 1.0 に固定します。通貨が欠けている場合は前回のスナップショット、次に静的定数へフォールバックし、`fx.status` を `fallback` または `stale` に設定します。

### 52 週レンジ

直近 250 営業日を 1 年に近似するのは、市場ごとに休日カレンダーが異なるためです。レンジ内の位置 = `(price − low) / (high − low)` とし、`[0, 1]` にクリップします。

### 株価の時点

`as_of` は直近の日足の日付であり、取得時刻ではありません。`snapshot.generated_at` は取得が完了した時刻です。両者が 48 時間以上ずれている場合は `stale` フラグが有効になります。

## 5. スナップショット構造（スキーマ v2）

以下の値は説明のための簡略化した例であり、現在のスナップショットそのものではなく、契約の形を示すものです。

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

`dataset`：`live`（株価取得率が 60% 以上）、`partial`（閾値未満）、`fixture`（テスト用）。

## 6. 互換ペイロード

`docs/latest_data.json` は、既存の iOS クライアントのために維持している旧形式です。フィールドの対応は次のとおりです。

| 旧フィールド | 新しい取得元 |
| --- | --- |
| `data[].code` | `ticker` |
| `data[].business_type` | 工程の短縮ラベル（旧クライアント向けの中国語） |
| `data[].market_cap` | `market_cap` / 1e8（億、現地通貨） |
| `data[].invest_score` | `priority` |
| `data[].invest_grade` | priority ≥ 80 で A / ≥ 65 で B / ≥ 50 で C / それ以外は D |
| `data[].invest_tags` | リスクフラグ |
| `data[].is_pick` | priority ≥ 70 |
| `kline_data` | 時価総額上位 40 社の 30 日 OHLC |
| `news_pool` | スナップショットのニュース（タイトル / リンク / 日付） |
| `industry_intro` / `industry_basics` | ナレッジベースと用語集からの中国語要約 |

新しいコードでは `/api/snapshot.{lang}.json`（`en`、`zh`、`ja`、`de`）を使ってください。構造は `semcore/build.py::_localized_payload` で定義されています。`en` がデフォルトのロケールです。

## 7. 株価ソースとシンボルマッピング

- `data/symbols.json` は、企業 ID → Eastmoney `secid` の**検証済み**マッピングを保持します。`method`（`seed` / `probe`）、`checked` の日付、解決された名称も含みます。
- 自動解決のルール：
  - A 株：`1.<code>`（上海） / `0.<code>`（深圳）
  - 香港：`116.<5 digits>`
  - 米国：`105` / `106` / `107` の順に試行
  - 日本：`176.<code>`
  - 台湾：`178.<code>`（OTC は `179` を試行）
  - 韓国：`177.<code>`
  - 欧州：シードマッピングを優先します。インターフェース上の欧州取引所番号はティッカーコードと一致しないためです
- 解決に成功した結果はキャッシュされ、次回以降の実行で再利用します。手動で編集する場合は、名称と株価の両方を検証する必要があります。
- 株価を取得できない銘柄（現在は ASM International のみ）は `quote_venue = "unpriced"` として調査対象に残りますが、株価統計からは除外され、ページにその理由が表示されます。

## 8. 品質管理

| チェック | 場所 | 失敗時の影響 |
| --- | --- | --- |
| マスタデータの列、列挙値、一意性、Web サイトの形式 | `validate_data()` | CI が失敗 |
| 4 言語の i18n キーの整合 | `validate_data()` | CI が失敗 |
| 4 ロケールで slug が同一の 12 ナレッジトピック | `validate_data()` | CI が失敗 |
| `zh`、`en`、`ja`、`de` すべてで揃った用語集 | `validate_data()` | CI が失敗 |
| 成果物の存在、JSON のパース、旧フィールドの存在 | `validate_artifacts()` | CI が失敗 |
| サードパーティ CDN のリソースがないこと | `validate_artifacts()` | CI が失敗 |
| カバレッジとエラー一覧 | 「このサイトについて」ページ / ビルドログ | 手動でレビュー |

## 9. 既知の限界

1. 株価は遅延値または終値であり、デイトレードの判断には向きません。
2. 静的 PER は高成長企業や赤字企業に不利です。赤字企業にはバリュエーション因子がありません。
3. 増収率、受注、稼働率といったファンダメンタルズ項目が欠けています。
4. Eastmoney の欧州・OTC 銘柄のカバレッジは不完全で、株価がセカンダリ上場や ADR に基づくことがあります。
5. 為替レートは日次の参考レートであるため、通貨をまたぐ比較には誤差が伴います。
6. 調整後株価でも、スピンオフやカーブアウトなどのコーポレートアクションによる段差を完全には取り除けません。1 日の極端な変動は手動での確認が必要です。
7. ニュースはタイトルのキーワードで絞り込み、重複を除いているだけで、ファクトチェックはしていません。境界的な見出しが残ることがあります。
8. 分類は編集上の判断であり、事業が変化する企業は四半期ごとの見直しが必要です。

## 10. 保持とクリーンアップ

- `data/snapshots/` は直近 30 件のスナップショットを保持し（`SNAPSHOT_KEEP`）、`save_snapshot()` が自動で整理します。
- `docs/` の出力はビルドのたびに全量を再生成し、過去のページは保持しません。
- 過去のスコアは別途アーカイブしません。バックテストする場合は、該当日のスナップショットから再ビルドしてください。

## 11. ライセンスと引用

- 株価とニュースの著作権は元の提供元に帰属します。本サイトは限定的な引用・リンク・表示のみを行います。
- 独自の文章と分類データは CC BY 4.0 で公開します。
- 引用形式：`SiliconScope, <page title>, <URL>, accessed <YYYY-MM-DD>`。

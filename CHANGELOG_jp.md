# 更新履歴

本プロジェクトの主な変更点をここに記録します。形式はKeep a Changelogに従い、
バージョン番号にはセマンティックバージョニングを採用しています。

## [3.0.0] — 2026-11-11

### 追加

- 英語優先のルーティング：`/` のデフォルトロケールおよび `x-default` を英語とし、
  中国語を `/zh/`、日本語を `/ja/`、ドイツ語を `/de/` に配置しました。
- ドイツ語ロケールを追加し、インターフェース文言、タクソノミーラベル、企業名と注記、
  用語集の定義、ナレッジトピック、ドキュメントに反映しました。
- 対象企業を175社に拡大し、13の本社地域と7つの上場市場をカバーしました。中国、香港、
  台湾、米国、日本、韓国、欧州、イスラエルの上場企業を含みます。
- 企業詳細フィールド `name_de`、`note_de`、`founded`、`fiscal_year_end` を追加し、
  企業ページに表示しました。
- 3つのナレッジトピック（`eda-ip`、`automotive`、`ai-datacenter`）を追加し、
  ナレッジベースを12トピックに拡張しました。
- `_en` / `_cn` / `_jp` / `_de` の接尾辞規則による4言語ドキュメントと、フラットな
  ナレッジファイル（`content/knowledge/<slug>_<suffix>.md`）を導入しました。
- 従来の英語URLを新しいルートパスへ転送する `/en/` リダイレクトスタブを追加しました。
- 4言語の用語集：英語、中国語、日本語、ドイツ語の定義を持つ52件の用語を収録しました。
  製品語彙は70タグになりました。
- 4言語すべてのローカライズ済みAPIスナップショット
  （`/api/snapshot.en.json`、`.zh.json`、`.ja.json`、`.de.json`）を追加し、
  新しいドイツ語ペイロードも含めました。
- CIでインターフェースキー、ナレッジのスラッグ、用語集フィールドが4言語で
  揃っているかの検証を行うようにしました。

### 変更

- デフォルトロケールを中国語から英語に変更しました。サイトルートは英語を配信し、
  中国語は `/zh/` に配置されています。
- 4ロケール向けにサイトを再構築し、4つの `hreflang` 代替と、英語を指す
  `x-default` を設定しました。
- ドキュメントを言語接尾辞付きのファイル名に変更し、ナレッジコンテンツを言語別
  ディレクトリからフラットな `<slug>_<suffix>.md` ファイルへ移行しました。
- 175社の対象企業向けに従来の `latest_data.json` を再生成し、フィールド契約は
  変更しませんでした。
- サイトのバージョンを3.0.0に更新しました。

### 削除

- 中国語優先のルート構成。
- `content/knowledge/{lang}/` のディレクトリ構成。

### 維持

- `docs/latest_data.json` は、`data`、`news_pool`、`kline_data`、
  `industry_intro`、`industry_basics`、`industry_source_refs`、
  `industry_intro_source`、`global_compare_items`、`global_compare_refs`、
  `data_time`、`data_time_iso` を含め、既存のiOSクライアント
  （`DashboardPayload.swift`）で引き続きデコードできます。
- 従来のルート（`overview.html`、`charts.html`、`risk-news.html`、
  `data-center.html`、`knowledge-old.html`）は現在の情報アーキテクチャへ
  リダイレクトされます。
- `ios/` 配下のSwiftUIクライアントは維持され、生成される `latest_data.json`
  との互換性を保っています（フィールド型とnullでないOHLC配列を検証済み）。

## [2.0.0] — 2026-11-11

### 追加

- 簡体字中国語、英語、日本語の3言語サイトを追加しました。ロケール別URL、
  hreflang代替、現在のページを維持する言語切り替えを備えています。
- グローバルな対象企業：中国本土、香港、台湾、米国、日本、韓国、欧州の124社を、
  8つのバリューチェーン段階に分類しました。
- ナレッジベース：9つの長文トピック × 3言語、および検索とカテゴリフィルタを
  備えた52件の用語からなる3言語用語集。
- 文書化された調査手法：同業比較で正規化したファクター、重み、データ充足度
  スコア、リスクフラグ、市場状態のしきい値、スクリーニングルール。
- 52週レンジ、ファクター内訳、同業比較表を備えた企業プロフィールページ。
- スナップショットベースのビルドに、古いデータへのフォールバック、相場
  カバレッジ指標、来歴フィールドを追加しました。
- CI：データ契約の検証、成果物の検証、pytestスイート。
- ドキュメント一式：PRODUCT、ARCHITECTURE、DATA、METHODOLOGY、OPERATIONS、
  ROADMAP、CONTRIBUTING。

### 変更

- 1,000行の単一ジェネレーターを、`semcore` パッケージとCLI（`fetch`、`build`、
  `refresh`、`validate`、`serve`、`info`）に置き換えました。
- TailwindとPlotlyのCDNを、自己完結型のデザインシステムとビルド時のSVG
  チャートに置き換えました。
- 百科事典の段落を毎月・毎日スクレイピングする方式を、キュレーション済みで
  バージョン管理されたナレッジコンテンツに置き換えました。
- 非公開の「投資スコア」を、公開された研究優先度スコアと明示的なデータ充足度に
  置き換えました。
- 企業メタデータを `data/universe.csv` に移し、`data/taxonomy.json` に対して
  検証するようにしました。

### 削除

- ドイツ語ロケール、実行時のPlotlyチャート、CDN依存、自動コミットされる
  ドキュメント、スクレイパーがニュースを返さないと失敗する脆いワークフローを
  削除しました。

### 維持

- `docs/latest_data.json` は、`data`、`news_pool`、`kline_data`、
  `industry_intro`、`industry_basics`、`industry_source_refs`、
  `industry_intro_source`、`global_compare_items`、`global_compare_refs`、
  `data_time`、`data_time_iso` を含め、既存のiOSクライアント
  （`DashboardPayload.swift`）で引き続きデコードできます。
- 従来のルート（`overview.html`、`charts.html`、`risk-news.html`、
  `data-center.html`）は新しい情報アーキテクチャへリダイレクトされます。
- `ios/` 配下のSwiftUIクライアントは維持され、生成される `latest_data.json`
  との互換性を保っています（フィールド型とnullでないOHLC配列を検証済み）。

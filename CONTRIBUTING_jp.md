# コントリビューション

SiliconScopeの改善にご協力いただきありがとうございます。本プロジェクトでは、**検証可能性**、**保守性**、**4言語間の一貫性**を重視しています。以下の手順に従ってください。

## 環境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m semcore build      # build from the committed snapshot
python -m semcore serve      # http://127.0.0.1:8000
python -m pytest
python -m semcore validate
```

## 一般的な変更

### 企業の追加・修正

1. `data/universe.csv` を編集します。1社につき1行です。列の定義は `documentation/DATA_en.md` にあります。
2. 1社につき主上場市場は1つにしてください。同じ企業を異なる市場向けに重複して追加しないでください。
3. プルリクエストには出典（取引所ページまたは年次報告書）を含め、分類の理由を説明してください。
4. `python -m semcore validate --data-only` を実行します。
5. 新しい企業の相場を自動で解決できない場合は、`python -m semcore fetch` を実行して `data/symbols.json` のマッピングを生成してください。それでも失敗する場合は、プルリクエストにその旨を記載するか、`quote_venue = "unpriced"` を設定してください。

企業マスターデータは4言語対応です。v3では次の列を追加しました：

| 列 | 必須 | 意味 |
| --- | --- | --- |
| `name_de` | 任意 | ドイツ語の表示名。空欄の場合は `name_en` を使用 |
| `note_de` | 任意 | ドイツ語の企業注記。空欄の場合は英語の注記を使用 |
| `founded` | 任意 | 設立年（4桁） |
| `fiscal_year_end` | 任意 | 決算期末の月（`01`〜`12`） |

ドイツ語の名称と注記は可能な限り入力してください。`founded` と `fiscal_year_end` は確認できない場合に空欄のままにしてください。これらのフィールドは値がある場合にのみ表示されます。

### 用語集への用語追加

1. `data/glossary.json` を編集し、**4言語すべて**（`en`、`zh`、`ja`、`de`）の `term` と `def` を用意します。
2. 既存の `category`（process / equipment / material / packaging / memory / design / business / economics / policy）を使用します。
3. 定義は2〜4文に収め、循環定義を避けてください。
4. `python -m pytest tests/test_content.py` を実行します。

### ナレッジトピックの追加

1. `content/knowledge/` 配下に `<slug>_en.md`、`<slug>_cn.md`、`<slug>_jp.md`、`<slug>_de.md` というフラットなファイルを作成します。スラッグは小文字とハイフンで構成してください。
2. 必須のフロントマターは `title`、`summary`、`level`（foundation/core/advanced）、`minutes`、`order`、`tags`、`related`、`updated` です。
3. `related` は既存のスラッグのみを参照できます。スラッグと `order` は4言語すべてで同一にしてください。
4. ナレッジベースには現在12件のトピックがあります：`advanced-packaging`、`ai-datacenter`、`automotive`、`cycle`、`eda-ip`、`equipment-materials`、`lithography`、`memory-hbm`、`metrics`、`policy`、`process-flow`、`value-chain`。
5. サポート対象のMarkdownサブセット（`##`、`###`、段落、リスト、引用、フェンス付きコードブロック、太字、リンク）を使用してください。**生のHTMLはサポートされていません。**
6. 末尾に検証可能な参考文献を記載してください。
7. 4言語すべてで同等の情報を載せてください。「英語の完全版」を用意し、他言語を短縮訳にするような公開はしないでください。

### 手法またはスコアリングの変更

1. まずIssueを作成し、動機と想定される影響を説明してください。
2. `semcore/analytics.py` を変更し、テストを追加してください。
3. `documentation/METHODOLOGY_en.md` とその `_cn` / `_jp` / `_de` 訳、および `data/i18n/*.json` のサイト文言を更新してください。
4. `CHANGELOG.md` に変更を記録し、メジャーバージョンを上げてください。
5. プルリクエストにはオフライン比較（スコア分布、スクリーニング結果の変化、影響を受けるページ）を含めてください。

### スタイルまたはテンプレートの変更

- デザイントークンは `assets/css/main.css` 冒頭の `:root` ブロックと `[data-theme="dark"]` ブロックにあります。
- サイトはCDN、フレームワーク、外部フォントを使わない状態を保ってください。
- 幅1440 / 1024 / 390、ライトテーマとダークテーマ、キーボード操作を確認してください。
- 自動再生アニメーションを導入しないでください。`prefers-reduced-motion` を尊重してください。

## コードスタイル

- Python 3.11以上。型ヒントを推奨し、副作用を伴うグローバル状態は避けてください。
- モジュールの責務は `documentation/ARCHITECTURE_en.md` に記載されています。取得、分析、レンダリングは分離してください。
- テンプレートは表示のみを担当します。複雑な計算を行わないでください。
- ネイティブのJS APIを使用し、依存関係は避けてください。JSが利用できない場合でも、すべてのインタラクションが適切に機能するようにしてください。

## プルリクエストのチェックリスト

- [ ] `python -m pytest` が成功する
- [ ] `python -m semcore validate` が成功する
- [ ] インターフェースキー、ナレッジのスラッグ、用語集のフィールドが4言語すべてで一致している
- [ ] ドキュメントの変更に `_en` / `_cn` / `_jp` / `_de` の各版が含まれている
- [ ] 新しいデータに出典が含まれている
- [ ] モバイルとダークモードを確認済み
- [ ] 必要に応じて `CHANGELOG.md` を更新済み
- [ ] `docs/` 以外に大きなファイルをコミットしていない

## コミットメッセージ

簡潔な命令形を使用してください。例：

```text
data: add Toyota Industries to automotive coverage
fix: hide the P/B column below 1500px to avoid table overflow
docs: clarify that the 30-day return uses trading sessions
content: add the ai-datacenter topic in four languages
```

## 行動規範

- 人ではなく、根拠と手法について議論してください。
- 検証されていないデータや出典を提出しないでください。
- 本サイトの内容を投資助言として提示しないでください。

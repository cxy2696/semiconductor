# iOSクライアント

`ios/` 配下のSwiftUIアプリは、元のiPhoneクライアントです。従来のペイロード
`https://cxy2696.github.io/semiconductor/latest_data.json` を利用しており、v3の
ビルドでも後方互換性のために引き続き生成しています。

> このアプリは英語/中国語を区別せず、ペイロードが提供する中国語の企業名と市場
> データをそのまま表示します。4言語API（`/api/snapshot.{lang}.json`）への移行は
> ロードマップに含まれています。

## 要件

- 完全なXcodeを備えたmacOS（Command Line Toolsのみでは不可）
- XcodeGen：`brew install xcodegen`
- 実機ビルドとTestFlightにはApple Developerチームが必要です

## プロジェクトの生成とオープン

```bash
cd ios
xcodegen generate --spec project.yml
open SemiconductorApp.xcodeproj
```

`project.yml` がターゲットとリソースの唯一の情報源です。生成された
`.xcodeproj` を手動で編集しないでください。

## シミュレータでの実行

1. `SemiconductorApp` スキームとiPhoneシミュレータを選択します。
2. ビルドして実行します（`Cmd+R`）。
3. アプリはリモートのペイロードを取得し、ネットワークが利用できない場合は
   ローカルキャッシュにフォールバックします。ホーム画面では引っ張って更新できます。

## 署名と実機ビルド

1. ターゲット → Signing & Capabilities を開きます。
2. チームを選択し、一意のバンドル識別子を設定します。
3. 「Automatically manage signing」を有効にします。
4. デバイスを接続し、開発者証明書を信頼して実行します。

## TestFlightとApp Store

1. ターゲット設定でバージョンとビルド番号を設定します。
2. Product → Archive を選択します。
3. Organizerで「Distribute App」→ App Store Connect → Upload を選択します。
4. App Store Connectで、メタデータ、プライバシーに関する質問、必要なデバイス
   サイズのスクリーンショットを入力します。
5. TestFlightの審査に提出し、その後App Storeの審査に提出します。

プライバシー宣言は最小限にしてください。アプリは公開JSONファイルを要求し、
ローカルにキャッシュを保存するだけです。プッシュ通知、位置情報、Bluetoothなど、
使用しない機能は有効にしないでください。

## データ契約

`DashboardPayload.swift` は `latest_data.json` から次のキーをデコードします：
`data`、`news_pool`、`kline_data`、`industry_intro`、`industry_basics`、
`industry_source_refs`、`industry_intro_source`、`global_compare_items`、
`global_compare_refs`、`data_time`、`data_time_iso`。ビルドでは公開前に、
nullでないOHLC配列を含むペイロードの形状を検証します。

フィールドを変更する場合は、`DashboardPayload.swift` と
`semcore/build.py::_legacy_payload` の両方を更新し、`ios/SemiconductorAppTests`
にデコードテストを追加してください。

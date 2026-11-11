# iOS 客户端

`ios/` 目录是原仓库的 SwiftUI iPhone 应用，消费旧版数据 `https://cxy2696.github.io/semiconductor/latest_data.json`。v3 构建继续生成该 payload，保证现有客户端无需改动即可解码。

> 客户端目前直接展示 payload 中的中文公司名与行情。迁移到四语 API（`/api/snapshot.{lang}.json`）已列入路线图。

## 环境要求

- macOS + 完整 Xcode（仅有 Command Line Tools 不够）
- XcodeGen：`brew install xcodegen`
- 真机与 TestFlight 需要 Apple 开发者团队

## 生成并打开工程

```bash
cd ios
xcodegen generate --spec project.yml
open SemiconductorApp.xcodeproj
```

`project.yml` 是 target 与资源的唯一来源，不要手改生成的 `.xcodeproj`。

## 模拟器运行

1. 选择 `SemiconductorApp` scheme 与 iPhone 模拟器。
2. `Cmd+R` 运行。
3. 应用会请求远程 payload；网络不可用时使用本地缓存。首页下拉刷新。

## 签名与真机

1. 打开 target → Signing & Capabilities。
2. 选择团队并设置唯一 Bundle Identifier。
3. 勾选 "Automatically manage signing"。
4. 连接设备，信任开发者证书后运行。

## TestFlight 与 App Store

1. 在 target 设置中更新版本号与构建号。
2. Product → Archive。
3. Organizer 中选择 "Distribute App" → App Store Connect → Upload。
4. 在 App Store Connect 完成元数据、隐私问卷与所需尺寸截图。
5. 先提交 TestFlight 审核，再提交 App Store 审核。

隐私声明保持最小化：应用只请求公开 JSON 并在本地缓存。不要开启未使用的推送、定位、蓝牙等能力。

## 数据契约

`DashboardPayload.swift` 解码 `latest_data.json` 中的以下键：
`data`、`news_pool`、`kline_data`、`industry_intro`、`industry_basics`、
`industry_source_refs`、`industry_intro_source`、`global_compare_items`、
`global_compare_refs`、`data_time`、`data_time_iso`。构建会在发布前校验 payload 结构，包括 OHLC 数组不含空值。

若字段变化，请同时更新 `DashboardPayload.swift` 与 `semcore/build.py::_legacy_payload`，并在 `ios/SemiconductorAppTests` 增加解码测试。

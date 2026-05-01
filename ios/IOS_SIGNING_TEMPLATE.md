# iOS 真机签名配置模板（Bundle ID / Team / Capability）

用于 `SemiconductorApp` 在真机安装与 TestFlight 上传前的签名配置。

## 1) 基础信息模板

- Apple Developer Team Name: `<TEAM_NAME>`
- Team ID: `<TEAM_ID>`
- Bundle ID (建议): `com.<org>.<app>`
  - 示例: `com.cxy2696.semiconductorapp`
- App Name: `Semiconductor`
- Deployment Target: `iOS 17.0+`（按项目实际）

## 2) Xcode 项目签名配置（Target: SemiconductorApp）

在 Xcode 中打开 `ios/SemiconductorApp.xcodeproj`，对 `SemiconductorApp` target 配置：

- Signing & Capabilities
  - [ ] Automatically manage signing = ON
  - [ ] Team = `<TEAM_NAME>`
  - [ ] Bundle Identifier = `<BUNDLE_ID>`
  - [ ] Signing Certificate = `Apple Development`（Debug）/ `Apple Distribution`（Release）
  - [ ] Provisioning Profile = 自动（或手动指定）

## 3) Build Settings 快速核对

- [ ] `PRODUCT_BUNDLE_IDENTIFIER` 与 Signing 页一致
- [ ] Debug/Release 配置都可解析签名
- [ ] `CODE_SIGN_STYLE = Automatic`（若采用自动签名）
- [ ] `DEVELOPMENT_TEAM = <TEAM_ID>`

## 4) Capability 清单（首版建议）

默认不额外开启，保持最小权限：

- [ ] Associated Domains（仅当需要 Universal Links）
- [ ] Push Notifications（仅当需要推送）
- [ ] Background Modes（仅当需要后台任务）
- [ ] Keychain Sharing（仅当跨 App 共享凭据）

如果未使用，建议保持关闭，降低审核和隐私复杂度。

## 5) 真机安装检查

- [ ] 设备已在 Apple Developer 账号下可调试
- [ ] 选择真实设备后 Build 成功
- [ ] App 可安装并启动
- [ ] 网络可访问 `https://cxy2696.github.io/semiconductor/latest_data.json`

## 6) 常见签名问题排查

- “No signing certificate”：
  - [ ] Xcode -> Settings -> Accounts 已登录开发者账号
  - [ ] Manage Certificates 中存在 Development/Distribution 证书
- “Provisioning profile doesn't include device”：
  - [ ] 开发设备已注册或切换自动签名
- “Bundle identifier already in use”：
  - [ ] 修改为全局唯一 Bundle ID

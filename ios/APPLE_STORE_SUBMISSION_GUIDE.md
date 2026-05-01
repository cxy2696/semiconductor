# Apple Store 上架执行指南（让 App 可下载）

这份指南用于把 `SemiconductorApp` 提交到 App Store，让用户可下载。

## 0) 前置条件

- [ ] Apple Developer Program 已开通（个人/公司账号）
- [ ] 已安装完整 Xcode
- [ ] 能在真机上运行通过（参考 `ios/IOS_RUN_CHECKLIST.md`）

## 1) 工程参数（已在仓库中预设）

当前项目已预置为上架友好默认值：

- Bundle ID：`com.cxy2696.semiconductorapp`（可改为你自己的唯一 ID）
- Device Family：`iPhone only`
- Marketing Version：`1.0.0`
- Build Number：`1`

如需调整版本号：

- `MARKETING_VERSION`：对外版本（如 `1.0.1`）
- `CURRENT_PROJECT_VERSION`：构建号（如 `2`、`3`）

## 2) 生成并打开工程

```bash
brew install xcodegen
xcodegen generate --spec ios/project.yml
open ios/SemiconductorApp.xcodeproj
```

> 如果你手动改过 `project.pbxproj`，建议以 `ios/project.yml` 为准并重新生成。

## 3) 签名与 Capability

按 `ios/IOS_SIGNING_TEMPLATE.md` 配置：

- [ ] Team
- [ ] Bundle Identifier
- [ ] Automatic Signing
- [ ] Development/Distribution 证书

首版建议保持最小 Capability（未使用的不启用）。

## 4) App Store Connect 创建应用

在 App Store Connect -> My Apps -> New App：

- [ ] Platform: iOS
- [ ] Name: `Semiconductor`（或你的品牌名）
- [ ] Primary Language
- [ ] Bundle ID（与 Xcode 完全一致）
- [ ] SKU（自定义唯一字符串）

## 5) Archive 并上传

Xcode 中：

1. 选择 `Any iOS Device (arm64)`
2. `Product -> Archive`
3. Organizer -> `Validate App`
4. Organizer -> `Distribute App -> App Store Connect -> Upload`

## 6) 填写上架信息

按 `ios/IOS_TESTFLIGHT_RELEASE_CHECKLIST.md` 完成：

- [ ] Metadata（名称、副标题、描述、关键词、支持链接）
- [ ] App Privacy（隐私问卷）
- [ ] 截图（6.7"/6.5" iPhone 等）
- [ ] What to Test（TestFlight）

## 7) TestFlight 与正式发布

- [ ] 先走 Internal Test（团队内测）
- [ ] 修复崩溃和高优先问题
- [ ] 提交 External Test（如需要）
- [ ] 最终 `Submit for Review`

审核通过后，App 就会在 App Store 可下载。

## 8) 常见卡点

- Bundle ID 不一致 -> Xcode 与 App Store Connect 必须一致
- 签名失败 -> 检查 Team/证书/Profile
- 元数据被拒 -> 补全描述、截图、隐私说明
- 审核被拒 -> 检查“功能可用性、崩溃、链接有效、权限声明”

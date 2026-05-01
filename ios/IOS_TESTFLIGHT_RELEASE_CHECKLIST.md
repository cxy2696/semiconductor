# 首版 TestFlight 发布前检查单（metadata / 隐私声明 / 截图规范）

适用于 `SemiconductorApp` 首次上架前的 TestFlight 分发准备。

## A. Build 与分发基础

- [ ] `Release` 配置可编译通过
- [ ] Archive 成功（Product -> Archive）
- [ ] Organizer 中验证通过（Validate App）
- [ ] 上传 App Store Connect 成功（Distribute App -> App Store Connect）

## B. App Store Connect 元数据（Metadata）

- [ ] App Name
- [ ] Subtitle
- [ ] Description（功能概述 + 数据来源说明）
- [ ] Keywords
- [ ] Support URL
- [ ] Marketing URL（可选）
- [ ] Version + Build Number 与本次提交一致
- [ ] Category（Finance / Business 等按定位）

## C. 隐私与合规（Privacy）

- [ ] Privacy Policy URL 已填写（若必须）
- [ ] App Privacy（数据收集问卷）已完成
- [ ] 若仅请求公开远程 JSON，不采集账号/设备标识，按实际最小化声明
- [ ] 未使用的权限能力保持关闭（推送、定位、蓝牙等）

## D. 截图规范（Screenshots）

至少准备以下尺寸对应截图（按当前支持设备）：

- [ ] 6.7" iPhone（如 1290 x 2796）
- [ ] 6.5" iPhone（如 1242 x 2688）
- [ ] 5.5" iPhone（如 1242 x 2208，若仍要求）

截图内容建议覆盖：

- [ ] Home（摘要 + 决策辅助 + 涨停板）
- [ ] Global Compare（全球对比 + 来源）
- [ ] Market（筛选 + 列表 + 详情）
- [ ] News（新闻与外链）
- [ ] Settings（语言/时区配置）

截图质量要求：

- [ ] 无调试边框/占位文案
- [ ] 时间、电量、网络状态不出现异常
- [ ] 文案语言与目标市场一致（或准备多语言版本）

## E. TestFlight 测试信息

- [ ] What to Test 已填写（测试重点与已知限制）
- [ ] 内测组（Internal Testing）成员已添加
- [ ] 外测（External Testing）如需审核，提供清晰测试说明
- [ ] 崩溃/日志监控方案确认（至少 Xcode Organizer 崩溃报告）

## F. 发布风险闸门（Go/No-Go）

- [ ] 启动无崩溃
- [ ] 首次加载失败时有错误提示 + 缓存回退
- [ ] 多语言切换正常（zh-CN / en-US / de-DE）
- [ ] 主要导航路径可达（5 个 Tab）
- [ ] 外部链接打开正常且无非法 URL
- [ ] 不包含本地调试地址/硬编码个人路径

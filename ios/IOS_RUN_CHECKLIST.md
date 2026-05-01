# iOS Run Checklist (Simulator + Device)

Use this checklist to validate the native SwiftUI app implementation.

## 1) Environment

- [ ] Full Xcode installed (not only Command Line Tools)
- [ ] `xcode-select -p` points to Xcode path (`/Applications/Xcode.app/...`)
- [ ] iOS simulator runtime installed (iOS 17+)

## 2) Project Generation

- [ ] `brew install xcodegen`
- [ ] `xcodegen generate --spec ios/project.yml`
- [ ] `open ios/SemiconductorApp.xcodeproj`

## 3) Build + Run (Simulator)

- [ ] Select scheme `SemiconductorApp`
- [ ] Select simulator device (e.g., iPhone 15)
- [ ] Build succeeds with no compile errors
- [ ] App launches and shows 5 tabs (Home, Compare, Market, News, Settings)
- [ ] Initial data loads from `latest_data.json`

## 4) Functional Checks

- [ ] Pull to refresh works in Home/Compare/Market/News
- [ ] Home shows summary cards + decision support + limit-up board + segment chart
- [ ] Compare shows global comparison cards and source links
- [ ] Market search + region/business filters + detail page works
- [ ] News list opens source links correctly
- [ ] Settings locale profile switch updates visible UI strings and date/time format

## 5) Offline / Resilience

- [ ] Launch once online (cache warm-up)
- [ ] Disable network and relaunch
- [ ] App still displays cached payload without crash
- [ ] Error state is user-visible when refresh fails

## 6) Real Device Checks

- [ ] Add signing team and valid bundle id
- [ ] Build/install on physical iPhone
- [ ] Confirm runtime behavior matches simulator
- [ ] Confirm external links open in Safari

## 7) Test Targets

- [ ] Unit tests pass (`PayloadDecodingTests`)
- [ ] UI test smoke check passes (`SemiconductorAppUITests`)

## 8) Release Readiness (MVP)

- [ ] Replace AppIcon placeholders
- [ ] Verify dark/light mode readability
- [ ] Verify Dynamic Type scaling on key screens
- [ ] Capture screenshots for Home / Compare / Market / News / Settings

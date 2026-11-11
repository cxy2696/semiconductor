# iOS client

The SwiftUI app under `ios/` is the original iPhone client. It consumes the
legacy payload `https://cxy2696.github.io/semiconductor/latest_data.json`,
which the v3 build still generates for backward compatibility.

> The app is English/Chinese agnostic: it renders the Chinese company names and
> market data supplied by the payload. A migration to the four-language API
> (`/api/snapshot.{lang}.json`) is on the roadmap.

## Requirements

- macOS with full Xcode (not only Command Line Tools)
- XcodeGen: `brew install xcodegen`
- An Apple developer team for device builds and TestFlight

## Generate and open the project

```bash
cd ios
xcodegen generate --spec project.yml
open SemiconductorApp.xcodeproj
```

`project.yml` is the source of truth for targets and resources. Do not edit the
generated `.xcodeproj` by hand.

## Run in the simulator

1. Select the `SemiconductorApp` scheme and an iPhone simulator.
2. Build and run (`Cmd+R`).
3. The app fetches the remote payload and falls back to its local cache when
   the network is unavailable. Pull to refresh on the home screen.

## Signing and device builds

1. Open the target → Signing & Capabilities.
2. Select your team and set a unique bundle identifier.
3. Enable "Automatically manage signing".
4. Connect a device, trust the developer certificate, and run.

## TestFlight and App Store

1. Set the version and build number in the target settings.
2. Product → Archive.
3. In Organizer choose "Distribute App" → App Store Connect → Upload.
4. In App Store Connect complete the metadata, privacy questionnaire and
   screenshots for the required device sizes.
5. Submit for TestFlight review, then for App Store review.

Keep the privacy declaration minimal: the app only requests a public JSON file
and stores a cache locally. Do not enable unused capabilities such as push,
location or Bluetooth.

## Data contract

`DashboardPayload.swift` decodes these keys from `latest_data.json`:
`data`, `news_pool`, `kline_data`, `industry_intro`, `industry_basics`,
`industry_source_refs`, `industry_intro_source`, `global_compare_items`,
`global_compare_refs`, `data_time`, `data_time_iso`. The build validates the
payload shape, including non-null OHLC arrays, before publishing.

If a field changes, update both `DashboardPayload.swift` and
`semcore/build.py::_legacy_payload`, and add a decoding test under
`ios/SemiconductorAppTests`.

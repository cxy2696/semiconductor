# iOS-Client

Die SwiftUI-App unter `ios/` ist der ursprüngliche iPhone-Client. Sie nutzt das Legacy-Payload `https://cxy2696.github.io/semiconductor/latest_data.json`, das der v3-Build weiterhin für die Abwärtskompatibilität erzeugt.

> Die App ist gegenüber Englisch und Chinesisch agnostisch: Sie rendert die chinesischen Unternehmensnamen und Marktdaten, die der Payload liefert. Eine Migration auf die viersprachige API (`/api/snapshot.{lang}.json`) steht auf der Roadmap.

## Voraussetzungen

- macOS mit vollständigem Xcode (nicht nur Command Line Tools)
- XcodeGen: `brew install xcodegen`
- Ein Apple-Entwicklerteam für Geräte-Builds und TestFlight

## Projekt generieren und öffnen

```bash
cd ios
xcodegen generate --spec project.yml
open SemiconductorApp.xcodeproj
```

`project.yml` ist die maßgebliche Quelle für Targets und Ressourcen. Bearbeiten Sie das generierte `.xcodeproj` nicht manuell.

## Im Simulator ausführen

1. Wählen Sie das Scheme `SemiconductorApp` und einen iPhone-Simulator.
2. Bauen und ausführen (`Cmd+R`).
3. Die App ruft das entfernte Payload ab und greift auf den lokalen Cache zurück, wenn das Netzwerk nicht verfügbar ist. Ziehen Sie zum Aktualisieren auf dem Startbildschirm nach unten.

## Signierung und Geräte-Builds

1. Öffnen Sie das Target → Signing & Capabilities.
2. Wählen Sie Ihr Team und legen Sie eine eindeutige Bundle-ID fest.
3. Aktivieren Sie „Automatically manage signing“.
4. Schließen Sie ein Gerät an, vertrauen Sie dem Entwicklerzertifikat und führen Sie die App aus.

## TestFlight und App Store

1. Legen Sie Version und Build-Nummer in den Target-Einstellungen fest.
2. Product → Archive.
3. Wählen Sie im Organizer „Distribute App“ → App Store Connect → Upload.
4. Vervollständigen Sie in App Store Connect die Metadaten, den Datenschutzfragebogen und die Screenshots für die erforderlichen Gerätegrößen.
5. Reichen Sie die App zur TestFlight-Prüfung und anschließend zur App-Store-Prüfung ein.

Halten Sie die Datenschutzerklärung minimal: Die App ruft nur eine öffentliche JSON-Datei ab und speichert einen Cache lokal. Aktivieren Sie keine ungenutzten Funktionen wie Push, Standort oder Bluetooth.

## Datenvertrag

`DashboardPayload.swift` dekodiert die folgenden Schlüssel aus `latest_data.json`: `data`, `news_pool`, `kline_data`, `industry_intro`, `industry_basics`, `industry_source_refs`, `industry_intro_source`, `global_compare_items`, `global_compare_refs`, `data_time`, `data_time_iso`. Der Build validiert die Struktur des Payloads, einschließlich OHLC-Arrays ohne Nullwerte, vor der Veröffentlichung.

Wenn sich ein Feld ändert, aktualisieren Sie sowohl `DashboardPayload.swift` als auch `semcore/build.py::_legacy_payload` und ergänzen Sie einen Dekodierungstest unter `ios/SemiconductorAppTests`.

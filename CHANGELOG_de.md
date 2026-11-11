# Changelog

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert. Das Format folgt Keep a Changelog, und das Projekt verwendet semantische Versionierung.

## [3.0.0] — 2026-11-11

### Hinzugefügt

- Routing mit Englisch als Standard: Englisch ist die Standard-Locale unter `/` und das `x-default`, Chinesisch liegt unter `/zh/`, Japanisch unter `/ja/` und Deutsch unter `/de/`.
- Deutsche Locale für Oberflächentexte, Taxonomie-Labels, Unternehmensnamen und -notizen, Glossardefinitionen, Wissensthemen und Dokumentation.
- Universum auf 175 Unternehmen in 13 Hauptsitzregionen und 7 Börsenmärkten erweitert, darunter chinesische, Hongkonger, taiwanische, US-amerikanische, japanische, koreanische, europäische und israelische Notierungen.
- Unternehmensdetailfelder `name_de`, `note_de`, `founded` und `fiscal_year_end`, die auf den Unternehmensseiten angezeigt werden.
- Drei Wissensthemen: `eda-ip`, `automotive` und `ai-datacenter`; die Wissensbasis umfasst damit 12 Themen.
- Viersprachige Dokumentation mit der Suffix-Konvention `_en` / `_cn` / `_jp` / `_de` und flachen Wissensdateien (`content/knowledge/<slug>_<suffix>.md`).
- `/en/`-Weiterleitungsstubs, die alte englische URLs auf die neuen Root-Pfade umleiten.
- Viersprachiges Glossar: 52 Begriffe mit Definitionen auf Englisch, Chinesisch, Japanisch und Deutsch; das Produktvokabular umfasst nun 70 Tags.
- Lokalisierte API-Snapshots für alle vier Locales (`/api/snapshot.en.json`, `.zh.json`, `.ja.json`, `.de.json`), einschließlich des neuen deutschen Payloads.
- Viersprachige Validierung von Oberflächenschlüsseln, Knowledge-Slugs und Glossarfeldern in der CI.

### Geändert

- Die Standard-Locale von Chinesisch auf Englisch umgestellt: Der Site-Root liefert jetzt Englisch aus, Chinesisch liegt unter `/zh/`.
- Die Site für vier Locales neu aufgebaut, mit vier `hreflang`-Alternates und `x-default` auf Englisch.
- Dokumentation auf Dateien mit Sprachsuffix umbenannt und Wissensinhalte aus Sprachverzeichnissen in flache `<slug>_<suffix>.md`-Dateien verschoben.
- Das Legacy-`latest_data.json` für das Universum mit 175 Unternehmen neu erzeugt, wobei der Datenvertrag unverändert blieb.
- Die Site-Version auf 3.0.0 angehoben.

### Entfernt

- Das Routing am Root mit Chinesisch als Standard.
- Die Verzeichnisstruktur `content/knowledge/{lang}/`.

### Beibehalten

- `docs/latest_data.json` bleibt für den bestehenden iOS-Client (`DashboardPayload.swift`) dekodierbar, einschließlich `data`, `news_pool`, `kline_data`, `industry_intro`, `industry_basics`, `industry_source_refs`, `industry_intro_source`, `global_compare_items`, `global_compare_refs`, `data_time` und `data_time_iso`.
- Legacy-Routen (`overview.html`, `charts.html`, `risk-news.html`, `data-center.html`, `knowledge-old.html`) leiten auf die aktuelle Informationsarchitektur um.
- Der SwiftUI-Client unter `ios/` bleibt erhalten und ist weiterhin mit dem generierten `latest_data.json` kompatibel (verifizierte Feldtypen und OHLC-Arrays ohne Nullwerte).

## [2.0.0] — 2026-11-11

### Hinzugefügt

- Dreisprachige Site (vereinfachtes Chinesisch, Englisch, Japanisch) mit URLs je Locale, hreflang-Alternates und einem Sprachumschalter, der die aktuelle Seite beibehält.
- Globales Universum: 124 Unternehmen aus Festlandchina, Hongkong, Taiwan, den USA, Japan, Korea und Europa, in 8 Wertschöpfungsstufen klassifiziert.
- Wissensbasis: 9 ausführliche Themen × 3 Sprachen und ein dreisprachiges Glossar mit 52 Begriffen, Suche und Kategoriefiltern.
- Dokumentierte Research-Methodik: peer-normalisierte Faktoren, Gewichtungen, Scoring der Datenabdeckung, Risikoflags, Schwellenwerte für die Marktlage und Regeln für die Screens.
- Unternehmensprofilseiten mit 52-Wochen-Spanne, Faktoraufschlüsselung und Peer-Tabelle.
- Snapshot-basierter Build mit Fallback auf veraltete Daten, Kennzahlen zur Kursabdeckung und Provenienzfeldern.
- CI: Validierung des Datenvertrags, Validierung der Artefakte und pytest-Suite.
- Dokumentationssatz: PRODUCT, ARCHITECTURE, DATA, METHODOLOGY, OPERATIONS, ROADMAP, CONTRIBUTING.

### Geändert

- Den einzelnen 1.000-Zeilen-Generator durch das Paket `semcore` und eine CLI (`fetch`, `build`, `refresh`, `validate`, `serve`, `info`) ersetzt.
- Tailwind- und Plotly-CDN durch ein eigenständiges Designsystem und zur Build-Zeit erzeugte SVG-Diagramme ersetzt.
- Das monatliche/tägliche Scraping von Enzyklopädieabsätzen durch kuratierte, versionierte Wissensinhalte ersetzt.
- Den nicht offengelegten „Investment Score“ durch einen veröffentlichten Research-Prioritätsscore plus explizite Datenabdeckung ersetzt.
- Unternehmensmetadaten nach `data/universe.csv` verschoben und gegen `data/taxonomy.json` validiert.

### Entfernt

- Deutsche Locale, Plotly-Diagramme zur Laufzeit, CDN-Abhängigkeiten, automatisch committete Dokumentation und den fragilen Workflow, der fehlschlug, wenn ein Scraper keine Nachrichten lieferte.

### Beibehalten

- `docs/latest_data.json` bleibt für den bestehenden iOS-Client (`DashboardPayload.swift`) dekodierbar, einschließlich `data`, `news_pool`, `kline_data`, `industry_intro`, `industry_basics`, `industry_source_refs`, `industry_intro_source`, `global_compare_items`, `global_compare_refs`, `data_time` und `data_time_iso`.
- Legacy-Routen (`overview.html`, `charts.html`, `risk-news.html`, `data-center.html`) leiten auf die neue Informationsarchitektur um.
- Der SwiftUI-Client unter `ios/` bleibt erhalten und ist weiterhin mit dem generierten `latest_data.json` kompatibel (verifizierte Feldtypen und OHLC-Arrays ohne Nullwerte).

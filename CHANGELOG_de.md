# Changelog

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert. Das Format folgt Keep a Changelog, und das Projekt verwendet semantische Versionierung.

## [3.1.0] — 2026-11-16

### Hinzugefügt

- Live-Kurse auf der Seite: `api/quotes.json` enthält Preis, Tagesveränderung und Marktkapitalisierung; geöffnete Seiten fragen sie jede Minute ab und aktualisieren die Werte direkt.
- Ein Rebuild pro Handelstag um 16:30 Uhr Pekinger Zeit, nach dem Schluss in Shanghai; geöffnete Seiten übernehmen neue Kurse innerhalb von fünf Minuten.
- Der aktualisierte Snapshot wird als CI-Artefakt aufbewahrt, damit sich die eingecheckte Basisversion ohne separaten Abruf ersetzen lässt.
- Diagrammfarben stammen jetzt aus den Design-Tokens; Achsen, Raster und Beschriftungen bleiben in beiden Themes lesbar.

### Behoben

- Der Hell-/Dunkel-Schalter und das Kürzel `t` taten nichts: Das Suchmodul überschrieb die gemeinsame Variable `root`, sodass der Theme-Code bei jedem Klick eine Ausnahme warf. Die Auswahl wird jetzt gespeichert, folgt bis zur ersten Entscheidung dem Betriebssystem und aktualisiert die Farbe der Browserleiste.
- Unbereinigte Tageshistorien erzeugten falsche Renditen – Tokyo Electron zeigte nach einem 5:1-Split −83 % im Monat. Splits werden nun erkannt und die Reihe wird neu basisiert, bevor Renditen und 52-Wochen-Spannen berechnet werden.
- 30-Tage-Renditen jenseits von ±300 % werden nicht mehr veröffentlicht.
- Redirect-Seiten und die 404-Seite waren auf dem englischen Wurzelpfad fest auf Chinesisch gesetzt; sie nutzen jetzt die Standard-Locale.
- Zwei Überschriften auf der About-Seite waren noch ausschließlich englisch.

### Geändert

- Kurse werden über den Listen-Endpunkt von Eastmoney geladen (40 Symbole pro Anfrage), die Tageshistorie wird innerhalb eines Tages wiederverwendet; ein Intraday-Refresh kostet damit wenige Anfragen statt 350. Bringt ein Lauf für weniger als die Hälfte des Universums frische Kurse, wird er verworfen und der vorige Snapshot bleibt; übernommene Kurse aus einer früheren Sitzung senken nun den Health-Status, statt hinter „Healthy“ zu verschwinden.

- Textüberarbeitung in allen vier Sprachen: kürzere, konkretere Sätze; der auf jeder Seite wiederholte Haftungshinweis entfällt und steht nur noch im Footer und auf der Methodenseite.
- Ungenutzte Snapshot-Felder (`highs`, `lows`) und doppelte Seitentexte entfernt.
- Version 3.1.0.

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

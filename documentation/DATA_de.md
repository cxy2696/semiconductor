# Daten: Quellen, Felder, Definitionen und Grenzen

Version 3.0 · 2026-11-11

Dieses Dokument ist die maßgebliche Beschreibung des Datenvertrags. Felddefinitionen, Einheiten und Fehlerbehandlung folgen diesem Dokument; weicht eine Seite davon ab, gilt dieses Dokument, und ein Pull Request sollte die Seite korrigieren.

## 1. Datenfluss

```text
Eastmoney public quote API ─┐
open.er-api.com FX ─────────┼─→ semcore fetch ─→ data/snapshots/latest.json ─→ semcore build ─→ docs/
Whitelisted media RSS ──────┘        (single input)              (static HTML / SVG / JSON)
```

- Seiten rufen **keine** Drittanbieter-APIs direkt auf; alle Daten werden zur Build-Zeit in einen Snapshot geschrieben.
- Snapshots werden im Repository versioniert, sodass die Website offline gebaut werden kann und jeder Build prüfbar und umkehrbar ist.
- Ein fehlgeschlagener Abruf leert die Seite nie: Ein einzelnes Unternehmen fällt auf den vorherigen Snapshot zurück und wird als `stale` markiert; bei einem Totalausfall bleibt das vorherige `latest.json` erhalten und die Seite zeigt einen Veraltet-Hinweis.

## 2. Quellenliste

| Daten | Quelle | Schnittstelle / Methode | Frequenz | Lizenz / Hinweise |
| --- | --- | --- | --- | --- |
| Kurse, Bewertung, Marktkapitalisierung | Eastmoney | `push2.eastmoney.com/api/qt/stock/get`, `push2his.../kline/get` | Zur Build-Zeit an jedem Handelstag | Öffentliche Schnittstelle; das Urheberrecht bleibt beim Anbieter; nur Anzeige und Zitierung |
| Wechselkurse | open.er-api.com | `GET /v6/latest/USD` | Täglich | Kostenlos, kein Schlüssel |
| Wechselkurs-Fallback | Eastmoney-Währungspaare | `USDCNH`, `USDJPY`, `USDKRW`, `USDEUR`, `USDHKD` | Wie oben | Wird nur verwendet, wenn die Primärquelle ausfällt |
| Branchennachrichten | Tom's Hardware / Semiconductor Digest / EE Times / DigiTimes / Semiconductor Today | RSS | Täglich | Nur Titel, Quelle, Datum und Link; jeder Titel muss ein Halbleiter-Schlüsselwort treffen; höchstens 6 Einträge je Quelle |
| Klassifikation und Glossar | In diesem Repository gepflegt | `data/taxonomy.json`, `glossary.json` | Bei Bedarf | CC BY 4.0 |

> Die Eastmoney-Schnittstelle ist undokumentiert, und die Feld-Semantik kann sich ändern. CI-Validierung und Snapshot-Fallback verringern das Risiko; wenn etwas falsch aussieht, folgen Sie dem Runbook in `OPERATIONS_de.md`.

## 3. Unternehmensstammdaten (`data/universe.csv`)

Das CSV ist die einzige Wahrheitsquelle für die Unternehmensabdeckung. Es hat **175 Zeilen**, eine pro Unternehmen, mit einer Hauptbörsennotierung je Unternehmen.

| Spalte | Typ | Definition | Fehlend / Fallback |
| --- | --- | --- | --- |
| `id` | string | Stabile Kennung, verwendet in URLs und Snapshots | Erforderlich |
| `ticker` | string | Code der Hauptbörsennotierung | Erforderlich |
| `exchange` | string | Börsencode (zum Beispiel `SSE`, `NASDAQ`) | Erforderlich |
| `mic` | string | Marktidentifikationscode nach ISO 10383 | Erforderlich |
| `market` | enum | Hauptbörsenmarkt: CN, HK, TW, US, JP, KR, EU | Erforderlich; insgesamt 7 Werte |
| `country` | enum | Hauptsitzregion: CN, HK, TW, US, JP, KR, NL, DE, FR, CH, GB, IL, TH | Erforderlich; insgesamt 13 Werte |
| `stage` | enum | Eine der 8 Stufen der Wertschöpfungskette | Erforderlich |
| `role` | enum | Eine der 9 Rollen (Fabless, Foundry, IDM, Speicher, Ausrüstung, Materialien, OSAT, Modul, EDA/IP) | Erforderlich |
| `products` | string | Pipe-getrennte Produkt-Tags aus dem kontrollierten Vokabular | Leer erlaubt; insgesamt 70 Tags |
| `hq` | string | Stadt des Hauptsitzes | Erforderlich |
| `website` | URL | Offizielle Website, nur `http(s)://` | Darf leer sein |
| `currency` | ISO 4217 | Handelswährung | Erforderlich |
| `quote_venue` | string | Überschreibung des Kursplatzes; leer bedeutet automatische Auflösung, `unpriced` bedeutet, das Unternehmen bleibt im Research-Universum, wird aber aus der Kursstatistik ausgeschlossen | Leer oder `unpriced` |
| `name_zh` | string | Chinesischer Anzeigename | Erforderlich |
| `name_en` | string | Englischer Anzeigename | Erforderlich |
| `name_ja` | string | Japanischer Anzeigename | Erforderlich |
| `name_de` | string | Deutscher Anzeigename | Fällt bei Leerwert auf `name_en` zurück |
| `note_zh` | string | Chinesische Unternehmensnotiz | Darf leer sein |
| `note_en` | string | Englische Unternehmensnotiz | Darf leer sein |
| `note_ja` | string | Japanische Unternehmensnotiz | Darf leer sein |
| `note_de` | string | Deutsche Unternehmensnotiz | Fällt bei Leerwert auf die englische Notiz zurück |
| `founded` | string | Gründungsjahr, vier Ziffern | Optional; nur bei Vorhandensein angezeigt |
| `fiscal_year_end` | string | Monat des Geschäftsjahresendes, `01`–`12` | Optional; nur bei Vorhandensein angezeigt |

Die 13 Hauptsitzregionen sind China (Festland), Hongkong, Taiwan, USA, Japan, Südkorea, Niederlande, Deutschland, Frankreich, Schweiz, Vereinigtes Königreich, Israel und Thailand. Die 7 Börsenmärkte sind A-Aktien (CN), Hongkong (HK), Taiwan (TW), USA (US), Japan (JP), Südkorea (KR) und Europa (EU).

## 4. Feldwörterbuch des Snapshots

| Feld | Typ | Einheit | Definition | Fehlwert |
| --- | --- | --- | --- | --- |
| `price` | float | lokale Währung | Jüngster verfügbarer Schlusskurs oder verzögerter Kurs | `null` |
| `prev_close` | float | lokale Währung | Schlusskurs des vorherigen Handelstags | `null` |
| `change_pct` | float | % | Veränderung am jüngsten Handelstag | `null` |
| `ret_30d` | float | % | Veränderung über die jüngsten 30 Handelstage | `null` |
| `ret_ytd` | float | % | Veränderung seit Jahresbeginn | `null` |
| `volume` | float | Stück | Volumen am jüngsten Handelstag | `null` |
| `market_cap` | float | lokale Währung | Gesamte Marktkapitalisierung (Eastmoney `f116`) | `null` |
| `market_cap_usd` | float | USD | `market_cap × usd_per_unit[currency]` | `null` |
| `pe` | float | Vielfaches | Statisches Kurs-Gewinn-Verhältnis (`f164`, jüngster Jahres-EPS) | `null`; ≤ 0 bedeutet Verlust |
| `pb` | float | Vielfaches | Kurs-Buchwert-Verhältnis (`f167`) | `null` |
| `roe` | float | % | Eigenkapitalrendite (`f173`) | `null` |
| `turnover` | float | % | Umschlagsrate (`f168`) | `null` |
| `high_52w` / `low_52w` | float | lokale Währung | Höchster / niedrigster Kurs der jüngsten 250 Handelstage | `null` |
| `history` | object | lokale Währung | OHLCV der jüngsten 30 Handelstage | Leere Arrays |
| `status` | string | — | `ok` / `stale` / `missing` | — |
| `as_of` | date | — | Jüngster Handelstag (Datenstand) | `null` |

### Wechselkurse

`fx.usd_per_unit` bedeutet „wie viele US-Dollar eine Einheit der lokalen Währung wert ist“, abgeleitet als `1 / rate(USD→local)`. USD ist auf 1,0 fixiert. Eine fehlende Währung fällt auf den vorherigen Snapshot und dann auf eine statische Konstante zurück, wobei `fx.status` auf `fallback` oder `stale` gesetzt wird.

### 52-Wochen-Spanne

Die jüngsten 250 Handelstage nähern ein natürliches Jahr an, weil sich die Feiertagskalender zwischen den Märkten unterscheiden. Position in der Spanne = `(price − low) / (high − low)`, begrenzt auf `[0, 1]`.

### Kurszeitpunkt

`as_of` ist das Datum des jüngsten Tagesbalkens, nicht der Abrufzeitpunkt. `snapshot.generated_at` ist der Zeitpunkt, zu dem der Abruf abgeschlossen wurde. Weichen beide um mehr als 48 Stunden ab, greift das `stale`-Flag.

## 5. Snapshot-Struktur (Schema v2)

Die folgenden Werte sind illustrativ und gekürzt; sie zeigen die Form des Vertrags, nicht einen aktuellen Snapshot.

```json
{
  "schema_version": 2,
  "site_version": "3.0.0",
  "generated_at": "2026-11-11T13:06:50+08:00",
  "dataset": "live",
  "universe_size": 175,
  "coverage": { "priced": 173, "total": 175, "ratio": 0.9886 },
  "fx": {
    "usd_per_unit": { "USD": 1.0, "CNY": 0.1496, "TWD": 0.0305, "JPY": 0.0063, "KRW": 0.00074, "EUR": 1.1205, "HKD": 0.1275 },
    "source": "open.er-api.com",
    "as_of": "…",
    "status": "ok"
  },
  "quotes": {
    "tsmc": {
      "status": "ok", "price": 2285.0, "currency": "TWD",
      "change_pct": 2.24, "ret_30d": -7.11, "market_cap": 59255465450000,
      "pe": 26.49, "pb": 9.21, "roe": 21.58,
      "high_52w": 2590.0, "low_52w": 1375.0,
      "as_of": "2026-11-10", "source": "Eastmoney",
      "history": { "dates": ["…"], "open": [], "high": [], "low": [], "close": [], "volume": [] }
    }
  },
  "news": [ { "title": "…", "link": "https://…", "source": "EE Times", "published": "2026-11-10", "lang": "en" } ],
  "errors": [],
  "sources": { "quotes": "Eastmoney public quote API", "fx": "open.er-api.com", "news": "RSS: …" }
}
```

`dataset`: `live` (mindestens 60 % mit Kurs), `partial` (unter der Schwelle), `fixture` (Tests).

## 6. Kompatibilitäts-Payload

`docs/latest_data.json` ist das Legacy-Format, das für den bestehenden iOS-Client erhalten bleibt. Feldzuordnung:

| Legacy-Feld | Neue Quelle |
| --- | --- |
| `data[].code` | `ticker` |
| `data[].business_type` | Kurzlabel der Stufe (Chinesisch, für den Legacy-Client) |
| `data[].market_cap` | `market_cap` / 1e8 (Hundert Millionen, lokale Währung) |
| `data[].invest_score` | `priority` |
| `data[].invest_grade` | Priorität ≥ 80 A / ≥ 65 B / ≥ 50 C / sonst D |
| `data[].invest_tags` | Risikoflags |
| `data[].is_pick` | Priorität ≥ 70 |
| `kline_data` | 30-Tage-OHLC für die 40 größten Unternehmen nach Marktkapitalisierung |
| `news_pool` | Snapshot-Nachrichten (Titel / Link / Datum) |
| `industry_intro` / `industry_basics` | Chinesische Zusammenfassungen aus Wissensbasis und Glossar |

Neuer Code sollte `/api/snapshot.{lang}.json` (`en`, `zh`, `ja`, `de`) verwenden, dessen Struktur durch `semcore/build.py::_localized_payload` definiert ist. Englisch (`en`) ist die Standard-Locale.

## 7. Kursquelle und Symbolzuordnung

- `data/symbols.json` speichert die **verifizierte** Zuordnung Unternehmens-ID → Eastmoney-`secid`, einschließlich `method` (`seed` / `probe`), dem `checked`-Datum und dem aufgelösten Namen.
- Regeln zur automatischen Auflösung:
  - A-Aktien: `1.<code>` (Shanghai) / `0.<code>` (Shenzhen)
  - Hongkong: `116.<5 digits>`
  - USA: `105` / `106` / `107` der Reihe nach probieren
  - Japan: `176.<code>`
  - Taiwan: `178.<code>` (`179` für OTC versuchen)
  - Korea: `177.<code>`
  - Europa: das Seed-Mapping bevorzugen, weil die europäischen Börsennummern in der Schnittstelle nicht mit den Ticker-Codes übereinstimmen
- Eine erfolgreiche Auflösung wird zwischengespeichert und im nächsten Lauf wiederverwendet. Manuelle Änderungen müssen sowohl den Namen als auch den Kurs verifizieren.
- Instrumente, die nicht bepreist werden können (derzeit nur ASM International), bleiben mit `quote_venue = "unpriced"` im Research-Universum; sie werden aus der Kursstatistik ausgeschlossen, und die Seite erklärt, warum.

## 8. Qualitätskontrolle

| Prüfung | Ort | Folge bei Fehlschlag |
| --- | --- | --- |
| Spalten der Stammdaten, Enums, Eindeutigkeit, Website-Format | `validate_data()` | CI schlägt fehl |
| Viersprachige i18n-Schlüssel ausgerichtet | `validate_data()` | CI schlägt fehl |
| 12 Wissensthemen mit identischen Slugs über vier Locales | `validate_data()` | CI schlägt fehl |
| Glossarbegriffe vollständig in `zh`, `en`, `ja` und `de` | `validate_data()` | CI schlägt fehl |
| Artefakte vorhanden, JSON parsbar, Legacy-Felder vorhanden | `validate_artifacts()` | CI schlägt fehl |
| Keine Drittanbieter-CDN-Ressourcen | `validate_artifacts()` | CI schlägt fehl |
| Abdeckung und Fehlerliste | Über-Seite / Build-Log | Manuelle Prüfung |

## 9. Bekannte Grenzen

1. Kurse sind verzögerte Daten oder Schlussdaten und für Intraday-Entscheidungen ungeeignet.
2. Das statische KGV ist für wachstumsstarke und verlustmachende Unternehmen ungünstig; Verlustunternehmen haben keinen Bewertungsfaktor.
3. Fundamentalfelder wie Umsatzwachstum, Auftragseingang und Kapazitätsauslastung fehlen.
4. Die Eastmoney-Abdeckung einiger europäischer und OTC-Instrumente ist unvollständig; Kurse können von einer Zweitnotierung oder einem ADR stammen.
5. Wechselkurse sind tägliche Referenzkurse, daher sind währungsübergreifende Vergleiche fehlerbehaftet.
6. Bereinigte Kurse können Stufensprünge aus Spin-offs, Carve-outs und anderen Kapitalmaßnahmen nicht vollständig beseitigen; extreme Tagesbewegungen müssen manuell geprüft werden.
7. Nachrichten werden über Titel-Schlüsselwörter gefiltert und dedupliziert, nicht faktengeprüft; Grenzfälle können verbleiben.
8. Die Klassifikation ist ein redaktionelles Urteil, und sich wandelnde Geschäftsmodelle erfordern eine vierteljährliche Prüfung.

## 10. Aufbewahrung und Bereinigung

- `data/snapshots/` behält die jüngsten 30 Snapshots (`SNAPSHOT_KEEP`), automatisch bereinigt durch `save_snapshot()`.
- Die Ausgabe in `docs/` wird bei jedem Build vollständig neu erzeugt; historische Seiten werden nicht aufbewahrt.
- Historische Scores werden nicht separat archiviert; für einen Backtest bauen Sie aus dem Snapshot des betreffenden Datums neu.

## 11. Lizenz und Zitierung

- Das Urheberrecht an Kursen und Nachrichten bleibt bei den ursprünglichen Anbietern; diese Website zitiert, verlinkt und zeigt nur begrenzte Auszüge.
- Eigene Texte und Klassifikationsdaten stehen unter CC BY 4.0.
- Zitierformat: `SiliconScope, <page title>, <URL>, accessed <YYYY-MM-DD>`.

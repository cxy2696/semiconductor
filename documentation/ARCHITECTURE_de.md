# Architektur

Version 3.0 · 2026-11-11

## 1. Systemkontext

```text
┌────────────────────┐        ┌──────────────────────────┐
│ Eastmoney quotes   │        │ open.er-api.com FX       │
└─────────┬──────────┘        └────────────┬─────────────┘
          │                                │
┌─────────▼──────────┐        ┌────────────▼─────────────┐
│ Whitelisted RSS    │        │ data/symbols.json mapping│
└─────────┬──────────┘        └────────────┬─────────────┘
          └──────────────┬─────────────────┘
                         ▼
              semcore fetch (may fail; never blocks the build)
                         ▼
        data/snapshots/latest.json (single input, committed)
                         ▼
   semcore analytics → semcore build (Jinja2 + SVG)
                         ▼
      docs/ (HTML / CSS / JS / JSON / sitemap)
                         ▼
              GitHub Pages (static hosting)
```

Designvorgaben:

- **Kein Server, keine Datenbank**: Die Website ist ein rein statisches Artefakt.
- **Datenabruf zur Build-Zeit**: Der Browser ruft nie eine Drittanbieter-API auf, was CORS-, Rate-Limit- und Datenschutzprobleme vermeidet.
- **Degradierbar**: Ein fehlgeschlagener Abruf verwendet den vorherigen Snapshot, und die Seite zeigt den Datenzeitpunkt und eine Veraltet-Markierung.
- **Eine einzige Wahrheitsquelle**: Unternehmensstammdaten, Klassifikation, Oberflächentexte und Inhalte existieren jeweils an genau einer Stelle.

## 2. Verzeichnisse und Zuständigkeiten

| Pfad | Zuständigkeit | Was hier nicht hingehört |
| --- | --- | --- |
| `data/universe.csv` | Stammdaten für 175 Unternehmen, einschließlich viersprachiger Namen und Notizen, `founded` und `fiscal_year_end` | Kurse, Scores |
| `data/taxonomy.json` | Labels für Stufe / Rolle / Produkt / Land / Markt in vier Sprachen; 70 Produkt-Tags | Unternehmensliste |
| `data/i18n/*.json` | Oberflächentexte für `en`, `zh`, `ja`, `de` | Ausführliche Inhalte |
| `content/knowledge/*.md` | Flache Langtexte: `<slug>_<suffix>.md` (12 Themen × 4 Sprachen) | Oberflächentexte |
| `data/glossary.json` | 52 Begriffe mit Definitionen in vier Sprachen | Unternehmensdaten |
| `data/snapshots/` | Markt-Snapshots (Build-Eingabe) | Manuell bearbeitete Korrekturen |
| `semcore/sources/` | Externe Adapter | Geschäftsregeln |
| `semcore/analytics.py` | Faktoren, Scores, Risiko, Marktlage | HTML |
| `semcore/build.py` | Seiten-Orchestrierung und Kontexte | Datenabruf |
| `templates/` | HTML-Struktur | Inline-Datenberechnungen |
| `assets/` | Designsystem und Progressive-Enhancement-JS | Geschäftsdaten |
| `docs/` | Generierte Website (CI-Build, nicht committet) | Manuelle Änderungen |
| `documentation/` | Produkt / Architektur / Daten / Methodik / Betrieb / Roadmap in vier Sprachen | Nutzerseitige Seiten |

## 3. Build-Pipeline

1. **Konfiguration laden**: `config.py` löst Pfade, die vier Locales und die Website-URL auf.
2. **Stammdaten laden**: `universe.load_universe()` liest das CSV und validiert Enumerationswerte, Eindeutigkeit und Website-Format gegen die `taxonomy`.
3. **Snapshot lesen**: `market.load_snapshot()` liest `latest.json`; fehlt die Datei, bricht der Build mit dem Hinweis ab, zuerst `fetch` auszuführen.
4. **Analytik berechnen**: `Analytics.build()` führt Unternehmen, Kurse und Wechselkurse zusammen und berechnet dann Faktoren, Scores, Risikoflags, Stufenstatistiken, Marktlage und Research-Listen.
5. **Inhalte laden**: `content.load_all_knowledge()` parst Front Matter und Markdown für jedes Locale; `load_glossary()` liest die Begriffe.
6. **Seiten rendern**: für jedes der vier Locales 7 feste Seiten + 12 Wissensseiten + 175 Unternehmensseiten rendern und Assets kopieren.
7. **Hilfsdateien schreiben**: `sitemap.xml`, `robots.txt`, `.nojekyll`, `latest_data.json`, `api/snapshot.{en,zh,ja,de}.json`, Weiterleitungen für Legacy-Routen, `/en/`-Weiterleitungsstubs und `404.html`.
8. **Validieren**: `validate_artifacts()` prüft erforderliche Dateien, JSON-Verträge, Legacy-Felder und die Abwesenheit von CDNs.

## 4. Modulgrenzen

### sources/eastmoney.py

- `resolve_secid()`: baut Kandidaten für `secid` nach Marktregel, prüft jede Code-Übereinstimmung und schreibt das Ergebnis in den Cache.
- `fetch_quote()` / `fetch_history()`: HTTP-Anfragen mit Retries und einem Timeout von 15 Sekunden.
- `build_market_entry()`: normalisiert Rohfelder zu einem Snapshot-Eintrag (Kurs, Veränderung, Marktkap., KGV/KBV/ROE, 52-Wochen-Spanne, 30-Tage-Rendite, 30-Tage-OHLC).
- Gibt bei Fehlern `None` zurück; `market.py` entscheidet über den Fallback.

### sources/news.py

- `fetch_feed()` ruft Feeds parallel ab; ein fehlschlagender Feed beeinflusst die anderen nicht.
- `parse_feed()` unterstützt sowohl RSS 2.0 als auch Atom.
- `_relevant()` filtert nach Schlüsselwort, entfernt Duplikate und behält die ersten 24 Einträge.

### market.py

- Ein Thread-Pool (Standard 6) ruft 175 Unternehmen ab.
- Bei Fehlern wird der vorherige Snapshot-Eintrag bevorzugt und als `status="stale"` markiert.
- Führt Wechselkurse und Nachrichten zusammen und schreibt dann `latest.json` sowie einen datierten Snapshot; die jüngsten 30 werden aufbewahrt.

### analytics.py

- Reine Berechnung, keine I/O, leicht testbar.
- `Row` ist die Zwischendarstellung, die Templates und JSON nutzen.
- Perzentile werden nach Stufe gruppiert; Gruppen mit weniger als 8 Unternehmen fallen auf die Gesamtstichprobe zurück.
- `Analytics` aggregiert Stufenstatistiken, Länder- und Marktstatistiken, Marktlage, Listen und Momentum-Extreme.

### build.py

- `SiteBuilder` besitzt die View-Dictionaries (lokalisierte Views je Locale), die URL-Berechnung, die Seitenkontexte, das Template-Rendering und das Schreiben der Ausgabe.
- Jeder Seitenkontext enthält `t` (Texte), `href()`, `alternates`, `analytics`, `tax` und `snapshot`.
- `_legacy_payload()` erzeugt `latest_data.json` für die iOS-Kompatibilität.
- `_localized_payload()` erzeugt `api/snapshot.{lang}.json` für die vier Locales.

### validate.py

- `validate_data()`: Stammdaten, i18n, Wissen und Glossar.
- `validate_artifacts()`: Seiten, JSON, Sitemap, CDN-Prüfungen und hreflang.
- Die CI führt die Datenprüfungen vor dem Build und die vollständigen Prüfungen danach aus.

## 5. Viersprachige Architektur

| Ebene | Mechanismus |
| --- | --- |
| URL | Englisch im Root, Chinesisch `/zh/`, Japanisch `/ja/`, Deutsch `/de/`; jede Seite hat absolute Alternates |
| Legacy-URLs | `/en/...`-Weiterleitungsstubs zeigen auf die entsprechenden Root-Seiten |
| Oberflächentexte | `data/i18n/{en,zh,ja,de}.json`, Schlüssel vollständig ausgerichtet und CI-geprüft |
| Datenlabels | `label`-Objekte in `taxonomy.json` mit `{zh, en, ja, de}`-Werten |
| Ausführliche Inhalte | Flache Dateien `content/knowledge/<slug>_<suffix>.md`; Slugs sind über alle Sprachen identisch |
| Glossar | Eine einzige Datei mit vier Sprachfeldern; die Seite rendert die aktive Sprache und zeigt die anderen drei in einem Vergleichsblock |
| Zahlen | Einheitliche Tausendertrenner und Nachkommastellen; Währungssuffixe behalten ISO-Codes |
| Datumsangaben | Die Website verwendet Asia/Shanghai (UTC+8); die Datumsangaben der Daten folgen der Quelle |

**Warum wird die Sprache nicht im Browser umgeschaltet?** Getrennte URLs sind besser für Teilen, SEO, Caching und Umgebungen ohne JS; der Sprachumschalter wird zur Build-Zeit erzeugt und hängt nicht von einem Laufzeitwörterbuch ab. Der Preis sind viermal so viele Seiten, was statisches Hosting ohne Mühe verkraftet.

## 6. Linkmodell

- `SiteBuilder._page_path(locale, key, slug)` ist die einzige Funktion zur Pfadgenerierung.
- Templates beziehen Links nur über Funktionen wie `href('company', id)` und vermeiden damit hart kodierte relative Pfade.
- `rel_href()` berechnet den relativen Pfad von der aktuellen zur Zielseite, sodass die Website auch beim direkten Öffnen über `file://` funktioniert.
- Assets verwenden `root + 'assets/...'`, wobei `root` aus der Seitentiefe abgeleitet wird.

## 7. Rendering und Performance

- **Null Drittanbieter-Assets**: kein Tailwind, kein Plotly, kein Font-CDN.
- Diagramme werden in Python als SVG erzeugt: Streudiagramm, Sparkline und Balken für die 52-Wochen-Spanne.
- CSS umfasst etwa 30 KB, JS etwa 8 KB (unkomprimiert). Die meisten Seiten haben 30–120 KB HTML; der Unternehmensindex ist größer, weil er 175 Zeilen serverseitig rendert.
- Die Unternehmenstabelle wird serverseitig gerendert; Filtern und Sortieren nutzen natives JS, ohne virtuelle Liste.
- Keine blockierenden Skripte im sichtbaren Bereich; ein kleines Inline-Skript für das Theme in `<head>` verhindert ein Aufblitzen des falschen Themes.

## 8. Barrierefreiheit und SEO

- Semantisches `header/nav/main/footer`, `aria-current`, `aria-sort` und Skip-Links.
- Tabellen haben ein `thead` und per Tastatur bedienbare sortierbare Überschriften.
- Diagramme tragen `role="img"`, `aria-label` und `<title>`.
- `prefers-reduced-motion` deaktiviert Animationen; der Kontrast erfüllt AA.
- Jede Seite hat eine kanonische URL, `hreflang`-Alternates und OG-Tags; Wissensseiten tragen Article-JSON-LD; die Sitemap deckt jede Seite ab.

## 9. Erweiterungspunkte

| Bedarf | Änderung |
| --- | --- |
| Unternehmen hinzufügen | Eine Zeile in `universe.csv` ergänzen und fetch ausführen, um das Symbol-Mapping zu erzeugen |
| Stufe hinzufügen | Einen Eintrag in `stages` in `taxonomy.json` ergänzen und das kontrollierte Produktvokabular aktualisieren |
| Sprache hinzufügen | `config.LOCALES` + `data/i18n/<lang>.json` + Wissensdateien mit neuem Suffix + übersetzte Dokumentation |
| Datenquelle hinzufügen | Einen Adapter unter `sources/` ergänzen und ihn in `market.fetch_snapshot()` zusammenführen |
| Seite hinzufügen | Neues Template in `templates/` + `PAGES` + `SiteBuilder`-Methode + Navigation |
| Diagramm hinzufügen | Eine reine Funktion in `charts.py` ergänzen und `Markup` durch den Kontext reichen |
| Methodik ändern | `analytics.py` + `METHODOLOGY_de.md` und die weiteren Sprachfassungen + Methodenseite der Website + Hauptversion aktualisieren |

## 10. Teststrategie

| Ebene | Tests |
| --- | --- |
| Daten | `test_universe.py`: Enumerationswerte, doppelte Börsennotierungen, Pflichtfelder |
| Inhalte | `test_content.py`: Front Matter, Markdown-Escaping, 12 Themen über vier Locales ausgerichtet |
| Texte | `test_i18n.py`: Schlüsselausrichtung, keine leeren Werte, Formatierung |
| Analytik | `test_analytics.py`: Score-Grenzen, Renormierung fehlender Faktoren, Schwellen der Marktlage, Regeln der Research-Listen |
| Build | `test_build.py`: vollständiger Build, Legacy-Vertrag, kein CDN |
| Artefakte | `semcore validate`: Dateien, JSON, Sitemap, hreflang |

## 11. Bekannte technische Schulden

1. Eine einzige Kursquelle (Eastmoney), ohne zweite Quelle zur Gegenprüfung.
2. Europäische `secid`-Werte hängen von Seed-Mappings ab; neue Börsennotierungen können manuelles Probing erfordern.
3. Faktoren werden bei jedem Build vollständig neu berechnet, ohne Cache; bei 175 Unternehmen ist das kein Performanceproblem.
4. Die Schlüsselwortliste für Nachrichten ist fest auf Englisch codiert, daher ist die Abdeckung chinesischer, japanischer und deutscher Medien begrenzt.
5. Unternehmensseiten erzeugen keine strukturierten `Corporation`-Daten; SEO stützt sich weiterhin auf Artikel.

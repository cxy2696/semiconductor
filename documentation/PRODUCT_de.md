# Produkt: SiliconScope Semiconductor Intelligence Desk

Version 3.0 · 2026-11-11 · Maintainer: SiliconScope contributors

## 1. Positionierung in einem Satz

**Eine einzige, öffentliche und prüfbare Sicht auf die globale Halbleiter-Wertschöpfungskette: ihre Struktur, die Position jedes Unternehmens, den Zustand des Zyklus und die zugrunde liegenden Konzepte.**

SiliconScope ist kein Kurs-Terminal und kein Werkzeug zur Aktienauswahl. Es ist ein **Research-Desk**: Er hilft Lesenden, in 10–30 Minuten eine strukturelle Sicht auf eine Stufe oder ein Unternehmen aufzubauen, und macht transparent, wie vollständig die Daten hinter dieser Sicht sind.

## 2. Warum es das gibt

Drei Eigenschaften von Halbleitern machen die Branche schwer mit einem einzigen Werkzeug bedienbar:

1. **Hohe Wissensbarriere.** Ausrüstung, Materialien, Prozess, Packaging und Speicher haben jeweils ihre eigene Fachsprache; eine marktübergreifende Diskussion verliert schnell an Aussagekraft.
2. **Starke Zyklizität.** Dieselbe Kennzahl kann am Zyklushöhepunkt und am Zyklustief Gegenteiliges bedeuten, und eine statische Bewertung führt oft in die Irre.
3. **Geopolitische Exposition.** Exportkontrollen, Subventionen und die Lokalisierung von Kapazitäten können den Umsatzmix eines Unternehmens schnell verändern.

Kostenlose Informationen sind entweder fragmentierte Nachrichten oder Kursseiten, die nur einen einzelnen Markt abdecken. Lesende brauchen eine **strukturierte Mittelschicht**: eine, die keine Preise prognostiziert, sondern erklärt, wie eine Stufe Geld verdient, wer dort konkurriert, in welchem Zustand sie ist und ob die Daten vertrauenswürdig sind.

## 3. Zielgruppen und Anwendungsfälle

| Nutzergruppe | Typische Aufgabe | Was die Website bietet |
| --- | --- | --- |
| Studierende und Forschende, die die Wertschöpfungskette lernen | „Vor einem Interview oder einem Bericht möchte ich verstehen, wie Ausrüstung, Materialien, Foundry und Packaging zusammenpassen.“ | Seite zur Wertschöpfungskette + 12 ausführliche Themen + viersprachiges Glossar |
| Analysten und Praktiker, die einen globalen Blick brauchen | „Geben Sie mir eine Tabelle, in der ich die wichtigsten Akteure und Bewertungen nach Stufe und Region sehe.“ | Unternehmenskarte + Stufenstatistik + Streudiagramm Bewertung/Qualität |
| Privatanleger, denen Datendefinitionen wichtig sind | „Woher kommt dieser Score? Wie viele Daten fehlen?“ | Methodenseite + Datenabdeckung + Snapshot-Zeitpunkt und Quellen |

**Ausdrücklich außerhalb des Umfangs**: Intraday-Handel, Empfehlungen zu Hebeln und Positionsgrößen, Kursziele, Gewinnprognosen und das Lesen von Nachrichten im Volltext.

## 4. Umfang

### Abgedeckt

- **8 Stufen**: EDA/IP und Designservices, Chipdesign (Fabless), Waferfertigung (Foundry / IDM), Speicher, Ausrüstung, Materialien, Packaging & Test, Module und Systeme.
- **13 Hauptsitzregionen**: China (Festland), Hongkong, Taiwan, USA, Japan, Südkorea, Niederlande, Deutschland, Frankreich, Schweiz, Vereinigtes Königreich, Israel und Thailand.
- **7 Börsenmärkte**: A-Aktien, Hongkong, Taiwan, USA, Japan, Südkorea und Europa.
- **175 börsennotierte Unternehmen**, jeweils mit einer Hauptbörsennotierung, um Doppelzählungen zu vermeiden.
- **70 Produkt-Tags** aus einem kontrollierten Vokabular, verwendet für Filter und die Anzeige auf der Unternehmensseite.
- **52 Glossarbegriffe**, jeder mit einer Definition auf Englisch, Chinesisch, Japanisch und Deutsch.
- **Vier Sprachen**: Englisch (Standard), vereinfachtes Chinesisch, Japanisch und Deutsch.

### Nicht abgedeckt

- Privatunternehmen (zum Beispiel YMTC und einige SMIC-Tochtergesellschaften).
- Reine Endmarktmarken und Distributoren, sofern ihr Umsatz nicht überwiegend aus Halbleitern stammt.
- Minutenkurse, Auftragsbücher, Optionen und Derivate.
- Tiefgehende Berichterstattung über die Aggregation von Unternehmensnachrichten hinaus.
- Anlageberatung jeglicher Art.

## 5. Informationsarchitektur

```text
/                          English home (default, x-default)
/zh/                       Chinese home
/ja/                       Japanese home
/de/                       German home
/companies.html            company map (filter / sort)
/companies/{id}.html       company page
/value-chain.html          value-chain panorama
/knowledge.html            knowledge index
/knowledge/{slug}.html     long-form topic
/glossary.html             glossary
/methodology.html          method and boundaries
/about.html                purpose, sources, licence, build information
/en/...                    legacy English URLs, redirecting to /
/zh/... /ja/... /de/...    localised mirrors with the same structure
/api/snapshot.{lang}.json  localised data snapshot (en, zh, ja, de)
/latest_data.json          legacy payload for the iOS client
```

Vier Inhaltsebenen:

1. **Fakten**: Kurse, Bewertung, Marktkapitalisierung, 52-Wochen-Spanne, Datenzeitpunkt und Quellen.
2. **Struktur**: Stufen, Rollen, Regionen, Verteilung der Marktkapitalisierung, Konzentration.
3. **Urteil**: Research-Priorität, Risikoflags, Marktlage, Research-Listen.
4. **Methodik**: Faktordefinitionen, Gewichte, Schwellen, Grenzen und Haftungsausschluss.

Die Urteilsebene lässt sich immer auf die Fakten und die Methodik zurückführen; die Methodik ist immer öffentlich.

## 6. Kernlogik des Produkts

### 6.1 Erst klassifizieren, dann vergleichen

Bruttomargen, Kapitalintensität und zyklische Treiber unterscheiden sich zwischen den Stufen vollständig, ein stufenübergreifender KGV-Vergleich ist daher sinnlos. Deshalb:

- wird jeder Faktor **innerhalb seiner Stufe** perzentilnormalisiert;
- fallen Stufen mit weniger als 8 Unternehmen auf die Gesamtstichprobe zurück, und die Methodenseite sagt das auch;
- zeigen Seiten absolute Werte und relative Scores gemeinsam, damit nicht „der Score ist das Ergebnis“ gilt.

### 6.2 Scores ordnen die Lektüre; sie prognostizieren nicht

„Research-Priorität“ beantwortet „Welches Unternehmen sollte ich zuerst lesen“, nicht „Welches Unternehmen sollte ich kaufen“.

- Ein hoher Score bedeutet eine stärkere kombinierte Position bei Qualität, Bewertung, Momentum und Größe in den aktuell veröffentlichten Daten;
- ein niedriger Score bedeutet kein schlechtes Unternehmen: Es kann schlicht teuer sein, Daten können fehlen oder es kann am Zyklustief stehen;
- keine Seite enthält „kaufen / verkaufen / Kursziel / Positionsgröße“.

### 6.3 Vollständigkeit hat höchste Priorität

Jeder Datensatz hat eine Datenabdeckung (den Anteil der 8 vorhandenen Felder), und jede Seite zeigt den Datenzeitpunkt und die Quellen. Fehlende Felder erscheinen als `—`; die Website rät nicht und füllt keine Nullen ein. Schlägt ein Abruf fehl, wird der vorherige Snapshot verwendet und die Seite als veraltet markiert.

### 6.4 Viersprachige Parität

Die englische, chinesische, japanische und deutsche Ausgabe haben identische Seitenstruktur, Daten und Diagramme; nur die Oberflächentexte und die Sprache der Inhalte unterscheiden sich. Englisch ist die kanonische Quelle, aber keine vollständigere Ausgabe: Alle vier Sprachen tragen dieselben Informationen. Fehlende Inhalte in einer Sprache lassen die CI fehlschlagen, was dem häufigen Fehlerbild vorbeugt, dass die englische Website die Vollversion und die anderen Zusammenfassungen sind.

## 7. Designprinzipien

1. **Eine einzige Wahrheitsquelle**: Stammdaten der Unternehmen liegen nur in `data/universe.csv`; Klassifikationslabels liegen nur in `data/taxonomy.json`.
2. **Alles zur Build-Zeit**: keine Aufrufe von Drittanbieter-APIs aus dem Browser, kein CDN, Diagramme als SVG gerendert.
3. **Prüfbar**: jede Zahl lässt sich auf eine Snapshot-Datei und eine Felddefinition zurückführen.
4. **Zurückhaltende visuelle Sprache**: Informationsdichte zuerst; Farbe dient nur der Richtung und der Klassifikation, nicht der dekorativen Animation.
5. **Druckbar und barrierefrei**: semantische Tabellen, Tastaturbedienung, WCAG-AA-Kontrast und Unterstützung von `prefers-reduced-motion`.
6. **Nachhaltig**: kein Server, keine Datenbank, keine bezahlte API; die monatlichen Wartungskosten liegen nahe null.

## 8. Erfolgskennzahlen

Das Projekt jagt keine Seitenaufrufe. Es verfolgt Signale dafür, ob der Desk ernsthaft genutzt wird:

| Typ | Kennzahl | Ziel |
| --- | --- | --- |
| Zuverlässigkeit | Build-Erfolgsquote | ≥ 99 % pro Monat |
| Aktualität | Datenzeitpunkt ≤ 24 h an Handelstagen | ≥ 95 % |
| Vollständigkeit | Kursabdeckung | ≥ 90 % |
| Qualität | Datenvertrag / bestandene Tests | 100 % |
| Wartbarkeit | Zu ändernde Dateien beim Hinzufügen eines Unternehmens | 1 (`universe.csv`) |
| Wartbarkeit | Zu ändernde Dateien beim Hinzufügen eines Themas | 4 Markdown-Dateien |
| Konsistenz | Viersprachige Ausrichtung (Oberfläche, Themen, Glossar) | 100 % |
| Nutzungstiefe | Verhältnis Unternehmensseiten / Wissensseiten | Trend beobachten; kein hartes Ziel |

## 9. Risiken und Compliance

- **Datenverzögerung**: Kurse sind verzögert oder Schlusskurse; die Seite weist darauf hin, und sie sind nicht für Handelsentscheidungen gedacht.
- **Datenfehler**: Quellen und Snapshots werden veröffentlicht, Korrekturen werden angenommen; absolute Genauigkeit wird nicht zugesagt.
- **Urheberrecht**: Nachrichten behalten nur Titel, Quelle, Datum und Link; Wissensinhalte sind eigenständige Erläuterungen mit zitierten Referenzen.
- **Risiko einer Anlageberatung**: Jede Seite wiederholt „Research-Zweck, keine Anlageberatung“, und die Methodenseite trägt einen gesonderten Haftungsausschluss.
- **Anbieterabhängigkeit**: eine einzige Kursquelle, abgefedert durch Snapshot-Fallback und geprüfte Symbolzuordnung; weitere Quellen stehen auf der Roadmap.

## 10. Versionierung und Weiterentwicklung

- Semantische Versionierung: eine Hauptversion für Änderungen an Informationsarchitektur oder Methodik, eine Nebenversion für Funktionen und den Ausbau der Abdeckung, ein Patch für Datenkorrekturen.
- Eine Methodenänderung muss `documentation/METHODOLOGY_de.md` sowie die übrigen Sprachfassungen `_en` / `_cn` / `_jp`, die Texte der Methodenseite in `data/i18n/*.json` und `CHANGELOG.md` aktualisieren, mit einer Impact-Notiz im Pull Request.
- Den aktuellen Plan und das Betriebsmodell finden Sie in [ROADMAP_de.md](ROADMAP_de.md) und [OPERATIONS_de.md](OPERATIONS_de.md).

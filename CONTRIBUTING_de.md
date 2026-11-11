# Mitmachen

Vielen Dank, dass Sie SiliconScope verbessern. Das Projekt legt Wert auf **Prüfbarkeit**, **Wartbarkeit** und **Konsistenz über alle vier Sprachen**. Bitte befolgen Sie den folgenden Ablauf.

## Umgebung

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m semcore build      # build from the committed snapshot
python -m semcore serve      # http://127.0.0.1:8000
python -m pytest
python -m semcore validate
```

## Häufige Änderungen

### Unternehmen hinzufügen oder korrigieren

1. Bearbeiten Sie `data/universe.csv`; eine Zeile pro Unternehmen. Die Spaltendefinitionen stehen in `documentation/DATA_en.md`.
2. Behalten Sie genau eine Hauptnotierung pro Unternehmen bei; fügen Sie dasselbe Unternehmen nicht für verschiedene Märkte doppelt hinzu.
3. Geben Sie im Pull Request eine Quelle an (Börsenseite oder Geschäftsbericht) und erläutern Sie die Klassifikation.
4. Führen Sie `python -m semcore validate --data-only` aus.
5. Wenn der Kurs des neuen Unternehmens nicht automatisch aufgelöst werden kann, führen Sie `python -m semcore fetch` aus, um die Zuordnung in `data/symbols.json` zu erzeugen. Schlägt dies weiterhin fehl, vermerken Sie es im Pull Request oder setzen Sie `quote_venue = "unpriced"`.

Die Unternehmensstammdaten sind viersprachig. v3 ergänzt die folgenden Spalten:

| Spalte | Erforderlich | Bedeutung |
| --- | --- | --- |
| `name_de` | Optional | Deutscher Anzeigename; bei leerem Feld wird auf `name_en` zurückgegriffen |
| `note_de` | Optional | Deutsche Unternehmensnotiz; bei leerem Feld wird auf die englische Notiz zurückgegriffen |
| `founded` | Optional | Gründungsjahr, vier Ziffern |
| `fiscal_year_end` | Optional | Monat des Geschäftsjahresendes, `01`–`12` |

Füllen Sie den deutschen Namen und die deutsche Notiz aus, wo möglich. Lassen Sie `founded` und `fiscal_year_end` leer, wenn sie nicht verifiziert werden können; die Felder werden nur angezeigt, wenn sie vorhanden sind.

### Glossarbegriff hinzufügen

1. Bearbeiten Sie `data/glossary.json`; geben Sie `term` und `def` für **alle vier** Sprachen an: `en`, `zh`, `ja` und `de`.
2. Verwenden Sie eine vorhandene `category` (process / equipment / material / packaging / memory / design / business / economics / policy).
3. Fassen Sie Definitionen in 2–4 Sätzen und vermeiden Sie Zirkeldefinitionen.
4. Führen Sie `python -m pytest tests/test_content.py` aus.

### Wissensthema hinzufügen

1. Erstellen Sie flache Dateien unter `content/knowledge/` mit den Namen `<slug>_en.md`, `<slug>_cn.md`, `<slug>_jp.md` und `<slug>_de.md`. Verwenden Sie einen kleingeschriebenen Slug mit Bindestrichen.
2. Erforderliche Front-Matter-Felder: `title`, `summary`, `level` (foundation/core/advanced), `minutes`, `order`, `tags`, `related`, `updated`.
3. `related` darf nur auf vorhandene Slugs verweisen. Der Slug und `order` müssen in allen vier Sprachen identisch sein.
4. Die Wissensbasis umfasst derzeit 12 Themen: `advanced-packaging`, `ai-datacenter`, `automotive`, `cycle`, `eda-ip`, `equipment-materials`, `lithography`, `memory-hbm`, `metrics`, `policy`, `process-flow` und `value-chain`.
5. Verwenden Sie die unterstützte Markdown-Teilmenge: `##`, `###`, Absätze, Listen, Zitate, eingezäunte Codeblöcke, Fettdruck und Links. **Rohes HTML wird nicht unterstützt.**
6. Listen Sie am Ende überprüfbare Referenzen auf.
7. Geben Sie in allen vier Sprachen gleichwertige Informationen wieder; veröffentlichen Sie keine „englische Vollversion“ mit gekürzten Übersetzungen.

### Methodik oder Scoring ändern

1. Eröffnen Sie zuerst ein Issue und erläutern Sie die Motivation und die erwarteten Auswirkungen.
2. Ändern Sie `semcore/analytics.py` und ergänzen Sie Tests.
3. Aktualisieren Sie `documentation/METHODOLOGY_en.md` und die Übersetzungen `_cn` / `_jp` / `_de` sowie die Site-Texte in `data/i18n/*.json`.
4. Halten Sie die Änderung in `CHANGELOG.md` fest und erhöhen Sie die Major-Version.
5. Fügen Sie dem Pull Request einen Offline-Vergleich bei: Score-Verteilung, Änderungen an den Screens und betroffene Seiten.

### Stile oder Templates ändern

- Design-Tokens liegen in den Blöcken `:root` und `[data-theme="dark"]` am Anfang von `assets/css/main.css`.
- Halten Sie die Site frei von CDNs, Frameworks und externen Schriftarten.
- Prüfen Sie die Breiten 1440 / 1024 / 390, helles und dunkles Design sowie die Tastaturbedienung.
- Führen Sie keine Autoplay-Animationen ein; respektieren Sie `prefers-reduced-motion`.

## Code-Stil

- Python 3.11+, Type-Hints bevorzugt, globalen Zustand mit Seiteneffekten vermeiden.
- Die Zuständigkeiten der Module sind in `documentation/ARCHITECTURE_en.md` beschrieben; halten Sie Abruf, Analytik und Rendering getrennt.
- Templates dienen nur der Darstellung; führen Sie darin keine komplexen Berechnungen aus.
- Verwenden Sie native JS-APIs und vermeiden Sie Abhängigkeiten; jede Interaktion muss auch ohne JavaScript funktionieren.

## Checkliste für Pull Requests

- [ ] `python -m pytest` läuft durch
- [ ] `python -m semcore validate` läuft durch
- [ ] Oberflächenschlüssel, Knowledge-Slugs und Glossarfelder sind in allen vier Sprachen konsistent
- [ ] Dokumentationsänderungen enthalten die Fassungen `_en` / `_cn` / `_jp` / `_de`
- [ ] Neue Daten enthalten eine Quelle
- [ ] Mobilansicht und Dark Mode geprüft
- [ ] `CHANGELOG.md` bei Bedarf aktualisiert
- [ ] Keine großen Dateien außerhalb von `docs/` committet

## Commit-Nachrichten

Verwenden Sie einen knappen Imperativstil, zum Beispiel:

```text
data: add Toyota Industries to automotive coverage
fix: hide the P/B column below 1500px to avoid table overflow
docs: clarify that the 30-day return uses trading sessions
content: add the ai-datacenter topic in four languages
```

## Verhaltenskodex

- Diskutieren Sie Belege und Methodik, nicht Personen.
- Reichen Sie keine ungeprüften Daten oder Quellen ein.
- Stellen Sie die Inhalte der Site nicht als Anlageberatung dar.

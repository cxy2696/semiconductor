# Betrieb: wer wartet, wie oft, und was bei Störungen zu tun ist

Version 3.0 · 2026-11-11

Dieses Dokument definiert den täglichen Betrieb von SiliconScope: Rollen, Rhythmus, SLOs, Monitoring, Incident-Handling, Change-Management und Kosten. Das Ziel ist, dass **eine Person den Desk unbegrenzt warten kann und zwei Personen sich nicht gegenseitig im Weg stehen**.

## 1. Betriebsprinzipien

1. **Automatisierung zuerst**: Was die CI erledigen kann, gehört nicht auf eine menschliche To-do-Liste.
2. **Fehler sichtbar machen**: Besser „Daten sind veraltet“ anzeigen, als alte Daten stillschweigend zu verwenden.
3. **In kleinen Schritten ändern**: Daten, Inhalte und Methodik getrennt committen, damit sich jede Änderung zurücknehmen lässt.
4. **Prüfbar**: Jede Schlussfolgerung lässt sich auf einen Snapshot, eine Felddefinition und einen Commit zurückführen.
5. **Geringe Grenzkosten**: kein Server, keine Datenbank, keine bezahlte API; ein neues Unternehmen ändert eine Zeile.

## 2. Rollen und Verantwortlichkeiten

| Rolle | Verantwortung | Derzeit besetzt durch |
| --- | --- | --- |
| Maintainer | Pull Requests mergen, Releases, CI-Fehler behandeln, die Methodik verantworten | Repository-Inhaber |
| Data Steward | Stammdaten, Klassifikation, Symbolzuordnung, Prüfung von Datenanomalien | Maintainer, geteilt |
| Content-Redaktion | 12 ausführliche Themen, Glossar, Texte der Methodenseite | Maintainer, geteilt |
| Übersetzung / Review | Konsistenz- und Terminologieprüfung für Chinesisch, Japanisch und Deutsch | Community-Beiträge |
| Nutzende | Die Website nutzen und Datenkorrekturen einreichen | Öffentlichkeit |

Rollen können kombiniert werden, aber **Methodenänderungen** müssen vom Maintainer geprüft werden, und **jede nicht-englische Ausgabe** muss mindestens ein nicht-maschinelles Review erhalten. Englisch ist die kanonische Quelle; Übersetzungen müssen dieselben Informationen tragen, keine gekürzte Fassung.

## 3. Rhythmus

| Frequenz | Aktion | Verantwortlich | Ergebnis |
| --- | --- | --- | --- |
| 08:30 UTC+8 an jedem Handelstag | CI führt automatisch `fetch + build + validate + deploy` aus | Automatisierung | Neuer Snapshot, Website |
| Jeden Montag | Abdeckung, Fehlerliste und Veraltet-Flags prüfen | Data Steward | Anomalieliste |
| Erster Arbeitstag jedes Monats | Die Stichprobe von 175 Unternehmen und die Klassifikation prüfen; defekte Websites und Delistings kontrollieren | Data Steward | Pull Request zur Universumsänderung |
| Vierteljährlich | Methodik, Grenzen und SLOs prüfen; die Roadmap aktualisieren | Maintainer | Methodenversion / Changelog |
| Halbjährlich | Die 12 Themen und das Glossar in allen vier Sprachen auf Terminologiekonsistenz prüfen | Content-Redaktion / Übersetzende | Content-Pull-Request |
| Bei Bedarf | Datenkorrekturen, Quellenwechsel, politische Ereignisse | Alle | Issue / Pull Request |

> An Nicht-Handelstagen sind Aktualisierungen nicht zwingend; die CI läuft weiter, aber das Datum der Daten ändert sich nicht und die Seite zeigt `as_of`.

## 4. Service-Level-Objectives (SLOs)

| Kennzahl | Ziel | Messung | Bei Verfehlung |
| --- | --- | --- | --- |
| Build-Erfolgsquote | ≥ 99 % pro Monat | Ergebnisse der Actions-Läufe | Siehe §6 |
| Datenaktualität | `as_of` ≤ 24 h an Handelstagen, in ≥ 95 % der Fälle | Snapshot-`as_of` | Upstream prüfen |
| Kursabdeckung | ≥ 90 % | `coverage.ratio` | Symbolzuordnung prüfen |
| Seitenverfügbarkeit | ≥ 99,9 % pro Monat | GitHub-Pages-Status | Auf die Wiederherstellung der Plattform warten |
| Build-Dauer | ≤ 10 Minuten | Actions-Log | Anfragen / Parallelität reduzieren |
| Seitengewicht | HTML ≤ 400 KB (der Unternehmensindex ist die größte Seite); CSS + JS ≤ 80 KB | Build-Prüfung | Templates optimieren |
| Bestandene Tests | 100 % | CI | Merge blockieren |
| Viersprachige Ausrichtung | 100 % | `validate_data()` | Merge blockieren |

## 5. Monitoring-Signale

Es gibt kein separates Monitoring-System; das Projekt nutzt **beobachtbare Artefakte**:

1. **GitHub Actions**: ob der tägliche Lauf erfolgreich war, seine Dauer und der fehlschlagende Schritt.
2. **`data/snapshots/latest.json`**: `coverage`, `errors`, `dataset` und `generated_at`.
3. **Seiten**: der Veraltet-Hinweis auf der Startseite, der Datenzeitpunkt im Footer und die Fehlerliste auf der Über-Seite.
4. **`semcore validate`**: Datenvertrag und Vollständigkeit der Artefakte.
5. **GitHub Issues**: von Lesenden gemeldete Datenfehler.

Exportieren Sie `coverage` und `errors` einmal pro Quartal, um Trends zu vergleichen.

## 6. Incident-Runbook

### 6.1 Die Kursquelle ist vollständig nicht verfügbar

**Symptome**: viele `fetch`-Fehler, ein starker Rückgang von `coverage`, alte Daten auf der Seite.

1. Prüfen Sie `errors` und `coverage` in `data/snapshots/latest.json`.
2. Fragen Sie ein bekanntes Instrument direkt mit curl ab, um ein Netzwerk- oder Upstream-Problem zu bestätigen:
   ```bash
   curl -s "https://push2.eastmoney.com/api/qt/stock/get?secid=1.688981&fltt=2&fields=f43,f57,f58"
   ```
3. Ist der Upstream ausgefallen: Daten **nicht** von Hand bearbeiten. Den vorherigen Snapshot behalten, die CI ihn im Zustand `stale` deployen lassen und den Vorfall in einem Issue festhalten.
4. Haben sich die Schnittstellenfelder geändert: `QUOTE_FIELDS` und den Parser aktualisieren, Tests ergänzen und ein Patch-Release ausliefern.
5. Nach der Wiederherstellung `workflow_dispatch` manuell auslösen und bestätigen, dass die Abdeckung wieder ≥ 90 % beträgt.

### 6.2 Ein einzelnes Instrument lässt sich nicht auflösen

**Symptome**: `<id>: symbol not resolved` erscheint in `errors` und auf der Über-Seite.

1. Prüfen Sie, ob `data/symbols.json` eine `secid` für diese ID enthält.
2. Nutzen Sie den Eastmoney-Suchendpunkt, um Code und Marktnummer zu bestätigen:
   ```bash
   curl "https://searchapi.eastmoney.com/api/suggest/get?input=NVDA&type=14&token=D43BF722C8E33BDC906FB84D85E326E8&count=5"
   ```
3. Schreiben Sie die `secid` von Hand in `symbols.json` und halten Sie `method: "seed"` sowie das `checked`-Datum fest.
4. Erneut abrufen und Name, Kurs, Währung und Größenordnung der Marktkapitalisierung verifizieren.
5. Gibt es tatsächlich keine verlässliche Quelle: `quote_venue = "unpriced"` setzen; die Seite erklärt das und schließt das Unternehmen aus den Statistiken aus.

### 6.3 Wechselkurs-Fehler

**Symptome**: `fx.status = stale/fallback`, Marktkapitalisierungen über Währungen hinweg wirken falsch.

1. Prüfen Sie, ob `open.er-api.com` erreichbar ist.
2. Das System fällt automatisch auf Eastmoney-Währungspaare und dann auf den vorherigen Snapshot zurück.
3. Bleibt der Fehler bestehen: `STATIC_FALLBACK` in `sources/fx.py` aktualisieren (Datum festhalten) und in einem Issue erklären.
4. Schreiben Sie niemals einen ungeprüften Kurs von Hand.

### 6.4 Fehler beim Nachrichtenabruf

**Symptome**: Der Abschnitt „Branchennachrichten“ auf der Startseite ist leer oder veraltet.

- Nachrichten sind ein **unkritischer Pfad**: Der Build darf deswegen nicht fehlschlagen.
- Prüfen Sie, ob sich eine Feed-URL geändert hat; aktualisieren Sie `config.RSS_FEEDS`.
- Ist eine Publikation längere Zeit nicht verfügbar, entfernen Sie sie aus der Whitelist und halten Sie den Grund fest.

### 6.5 Build-Fehler

1. Lesen Sie das Actions-Log, um den Schritt zu finden: `refresh` / `validate` / `deploy`.
2. Lokal reproduzieren:
   ```bash
   python -m semcore build
   python -m semcore validate
   python -m pytest
   ```
3. Liegt das Problem in den Daten: `universe.csv`, `taxonomy.json` oder ein Content-Front-Matter korrigieren.
4. Liegt das Problem in einem Template: lokal `serve` ausführen, die Seite prüfen und einen Build-Test ergänzen.
5. Mit `git revert` des jüngsten Commits zurückrollen und die Bereitstellung erneut auslösen.

### 6.6 Regression in Seitenstruktur oder Stil

1. Den Umfang bestimmen: eine Seite / eine Sprache / die ganze Website.
2. Lokal bauen und Screenshots vergleichen.
3. Nach der Korrektur die vollständige Testsuite und `validate` ausführen.
4. Handelt es sich um eine Drittanbieter-Schrift oder Browserkompatibilität: den System-Font-Stack bevorzugen und kein CDN ergänzen.

### 6.7 Von Lesenden gemeldeter Datenfehler

1. Nach einer Quelle fragen (Börsenzulassungsunterlage oder Börsenseite).
2. Bestimmen, ob es ein **Quellenfehler** oder ein **Mapping-Fehler** ist:
   - Quellenfehler: in einem Issue festhalten und auf die Korrektur durch den Upstream warten; nicht von Hand überschreiben;
   - Mapping-Fehler: `symbols.json` oder `universe.csv` korrigieren.
3. Die Korrektur in `CHANGELOG.md` festhalten und im Issue antworten.

### 6.8 Sicherheitsvorfall

- Das Repository enthält keine Secrets, keine Datenbank und keine Nutzerdaten; die Hauptrisiken sind Schwachstellen in Abhängigkeiten und bösartige Pull Requests.
- Dependabot aktivieren; Workflow-Änderungen in externen Pull Requests prüfen.
- In Actions keinen nicht vertrauenswürdigen Code mit `pull_request_target` ausführen.
- Werden bösartige Inhalte gefunden: sofort zurückrollen, das GitHub-Token rotieren und die letzten Deployments prüfen.

## 7. Change-Management

### 7.1 Änderungstypen

| Typ | Auswirkung | Anforderung |
| --- | --- | --- |
| Datenkorrektur | Ein Unternehmen / ein Begriff | Quelle beifügen; Snapshot oder Stammdaten aktualisieren |
| Inhaltsergänzung | Ausführliches Thema / Glossar | In allen vier Sprachen vollständig; CI besteht |
| Stil / Template | Website-weite Darstellung | Screenshot-Vergleich; Mobile und Dark Mode prüfen |
| Methodenänderung | Scores, Listen, Marktlage | METHODOLOGY + Methodenseite der Website + CHANGELOG + Hauptversion aktualisieren |
| Abhängigkeits-Update | Build-Umgebung | Versionen pinnen; vollständige Testsuite ausführen |

### 7.2 Versionsnummern

- **Major**: Änderungen an Informationsarchitektur, Scoring-Methodik oder Datenvertrag, die nicht rückwärtskompatibel sind.
- **Minor**: neue Seiten, Sprachen, Datenquellen oder Ausbau der Abdeckung.
- **Patch**: Datenkorrekturen, Text- und Stilkorrekturen.

### 7.3 Release-Ablauf

1. Pull Request → CI (`quality.yml`: Tests + Datenvalidierung + Build).
2. Review: Datenänderungen brauchen eine Quelle; Methodenänderungen eine Impact-Notiz; Inhaltsänderungen alle vier Sprachen.
3. Merge nach `main` → `pages.yml` baut und deployt.
4. `CHANGELOG.md` und gegebenenfalls die Versionsnummer aktualisieren.
5. Nach dem Deployment Startseite, eine Unternehmensseite, eine Wissensseite und je eine Seite pro Sprachausgabe stichprobenartig prüfen.

## 8. Governance

### 8.1 Aufnahme in die Stichprobe

Ein neues Unternehmen muss:

- börsennotiert und handelbar sein;
- den Großteil seines Umsatzes mit Halbleitern erzielen (oder ausdrücklich als angrenzende Stufe gekennzeichnet sein);
- eine verlässliche Kursquelle haben;
- eine Lücke bei Stufe oder Region füllen oder ein wichtiger Marktführer sein.

Ausschlusskriterien: Delisting, Übernahme, Geschäftsumstellung oder sechs aufeinanderfolgende Monate ohne verlässliche Daten.

### 8.2 Klassifikationsstreitigkeiten

- Die Hauptumsatzquelle des jüngsten Geschäftsjahres verwenden;
- Belege im Pull Request vorlegen (Segmentumsatz aus dem Geschäftsbericht);
- ist der Fall wirklich unklar, das Unternehmen in „Module/Systeme“ oder „Design“ belassen und in der Unternehmensnotiz erklären.

### 8.3 Methoden-Governance

- Jede Gewichtsanpassung erfordert einen Offline-Vergleich (Score-Verteilung, Änderungen der Listen).
- Eine Schwellenanpassung erfordert eine genannte Begründung und eine Auswirkungsanalyse.
- Die Methodik darf niemals geändert werden, nur damit ein bestimmtes Unternehmen in einer Liste erscheint.

### 8.4 Content-Governance

- Eigenständige Erläuterung mit zitierten Referenzen; keine urheberrechtlich geschützten Texte vollständig kopieren.
- Alle vier Sprachfassungen tragen äquivalente Informationen; keine „englische Vollversion“ mit gekürzten Übersetzungen.
- Jeder Artikel hält sein Aktualisierungsdatum und sein Schwierigkeitsniveau fest.

## 9. Kosten

| Position | Nutzung | Kosten |
| --- | --- | --- |
| GitHub Actions | Ein Lauf pro Tag × ca. 5 Minuten + Pull Requests | Innerhalb des kostenlosen Kontingents für öffentliche Repositories |
| GitHub Pages | Statisches Hosting | Kostenlos |
| Kurse / Wechselkurse / RSS | Öffentliche Schnittstellen | Kostenlos |
| Domain | Standard `github.io` | 0; eine eigene Domain kostet extra |

**Ziel: monatliche Barkosten von null; Maintainer-Zeit ≤ 2 Stunden pro Monat, ohne Content-Erstellung.**

## 10. Backup und Rollback

- Code und Snapshots liegen in der Git-Historie, die ein natürliches Backup darstellt.
- Die Website lässt sich aus jedem Commit neu bauen: `git checkout <sha> && python -m semcore build`.
- Deployment-Rollback: den Commit zurücknehmen und `pages.yml` erneut ausführen.
- Die jüngsten 30 Snapshots werden aufbewahrt; ältere Daten lassen sich aus der Git-Historie wiederherstellen.

## 11. Abhängigkeiten und Lizenz

- Laufzeitabhängigkeiten sind nur `jinja2` und `requests`; Tests verwenden `pytest`.
- Abhängigkeits-Updates laufen über einen Pull Request und pinnen den Major-Versionsbereich.
- Das Urheberrecht an Daten und Nachrichten bleibt bei den Anbietern; die Website verkauft sie nicht weiter und verteilt sie nicht massenhaft.
- Code steht unter MIT; geschriebene Inhalte unter CC BY 4.0.

## 12. Stilllegungsplan

Wenn das Projekt nicht mehr gewartet wird:

1. README und Startseite als „nicht mehr aktualisiert“ markieren und das letzte Datendatum nennen.
2. Repository und `docs/` schreibgeschützt halten; die Historie nicht löschen.
3. `data/snapshots/latest.json` und `latest_data.json` exportieren, mit einer Beschreibung der Felddefinitionen.
4. Den geplanten Actions-Workflow entfernen, damit die Upstream-Anfragen aufhören.

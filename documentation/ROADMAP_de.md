# Roadmap

Version 3.0 · 2026-11-11

Prinzip: Zuerst **Prüfbarkeit** und **Wartbarkeit** sichern, bevor Abdeckung oder Funktionen ausgebaut werden. Jeder Punkt nennt seine Abnahmekriterien, damit „erledigt“ überprüfbar ist und nicht eine Frage des Eindrucks bleibt.

## Abgeschlossen (v3.0)

- [x] Routing mit Englisch als Standard: Englisch unter `/` und als `x-default`; Chinesisch `/zh/`, Japanisch `/ja/`, Deutsch `/de/`
- [x] Deutsche Locale in Oberflächentexten, Taxonomie, Unternehmensnamen und -notizen, Glossar und Dokumentation
- [x] 175 Unternehmen über 8 Stufen, 13 Hauptsitzregionen und 7 Börsenmärkte, einschließlich chinesischer, Hongkonger, taiwanesischer, US-amerikanischer, japanischer, koreanischer, europäischer und israelischer Notierungen
- [x] Detailfelder der Unternehmen: `name_de`, `note_de`, `founded` und `fiscal_year_end`
- [x] 12 Wissensthemen, einschließlich der neuen Themen `eda-ip`, `automotive` und `ai-datacenter`
- [x] 52 Glossarbegriffe in vier Sprachen und 70 Produkt-Tags
- [x] Viersprachige Dokumentation mit den Suffixen `_en` / `_cn` / `_jp` / `_de`
- [x] Flache Wissensbenennung: `content/knowledge/<slug>_<suffix>.md`
- [x] `/en/`-Weiterleitungsstubs, damit alte englische URLs weiter funktionieren
- [x] Viersprachige Validierung in der CI
- [x] Legacy-`latest_data.json` für 175 Unternehmen neu erzeugt, weiterhin vom iOS-Client dekodierbar

## Abgeschlossen (v2.0)

- [x] Globale Abdeckung: 124 Unternehmen, 8 Stufen, 7 Börsenmärkte
- [x] Chinesisch / Englisch / Japanisch mit getrennten URLs und hreflang
- [x] 9 ausführliche Themen + 52 dreisprachige Glossarbegriffe
- [x] Öffentliche Methodik: Faktoren, Gewichte, Abdeckung, Risikoflags, Marktlage, Listen
- [x] Snapshot-Fallback, Abdeckungskennzahlen und Veraltet-Flags
- [x] Null CDN, SVG zur Build-Zeit, kein Frontend-Framework
- [x] CI: Tests + Datenvertrag + Artefaktvalidierung
- [x] Produkt- / Architektur- / Daten- / Methodik- / Betriebsdokumentation

## Kurzfristig (1–3 Monate)

### 1. Zweite Kursquelle und Gegenprüfung

**Problem**: Ein einziger Anbieter (Eastmoney) lässt keine Referenz, wenn sich Feld-Semantik oder Verfügbarkeit ändern.

**Plan**: Eine unabhängige Quelle ergänzen (zum Beispiel einen offiziellen End-of-Day-Feed einer Börse oder Stooq), Kurse und Veränderungen innerhalb einer Toleranz vergleichen und Abweichungen als `source_conflict` markieren.

**Abnahme**: Mindestens 90 % der Instrumente haben zwei Quellen; Konfliktrate unter 2 %; die Seite zeigt ein Konfliktflag; Tests decken die Vergleichslogik ab.

### 2. Ausbau der Fundamentalfelder

**Problem**: Der Qualitätsfaktor stützt sich allein auf den ROE und lässt Wachstum und Cashflow vermissen.

**Plan**: Umsatzwachstum, Bruttomarge, operativen Cashflow / Nettogewinn und Nettoverschuldung / EBITDA ergänzen, wo Quellen es erlauben, einen Faktor „Wachstum“ einführen und die Gewichte neu verteilen.

**Abnahme**: Jeder neue Faktor hat eine eigene Definition und eine Behandlung fehlender Daten; die Methodenseite ist aktualisiert; ein Offline-Vergleich zeigt Listenänderungen unter 30 %.

### 3. Strukturierte Daten auf Unternehmensseiten

**Problem**: Unternehmensseiten haben kein `Organization` / `Corporation`-JSON-LD, was die Sichtbarkeit in der Suche schwächt.

**Plan**: JSON-LD für Unternehmensseiten erzeugen, mit Name, Ticker, Hauptsitz, Website und Sektor.

**Abnahme**: Der Rich-Results-Test besteht; es werden keine ungültigen Felder eingeführt.

### 4. Viersprachiges redaktionelles Review

**Problem**: Englisch ist die kanonische Quelle, aber die chinesische, japanische und deutsche Ausgabe brauchen weiterhin ein muttersprachliches Review.

**Plan**: Ein oder zwei Personen für das Review je Sprache gewinnen, die Terminologie am Glossar ausrichten und das Review-Datum festhalten.

**Abnahme**: Alle 12 Themen in allen vier Sprachen geprüft; Glossar und Fließtext stimmen überein; `CHANGELOG.md` hält das Review fest.

## Mittelfristig (3–6 Monate)

### 5. Interaktive Karte der Wertschöpfungskette

**Plan**: Hervorhebung nach Region und Rolle sowie ein Unternehmens-Blasendiagramm auf der Seite zur Wertschöpfungskette ergänzen, bei gleichzeitiger Beibehaltung einer Ansicht ohne JS.

**Abnahme**: Per Tastatur bedienbar; serverseitig gerenderter Inhalt vollständig; auf Mobilgeräten nutzbar.

### 6. Quartalsbericht (generierter Entwurf)

**Plan**: Aus historischen Snapshots eine strukturelle Quartalszusammenfassung erzeugen (Anteil der Stufen an der Marktkapitalisierung, Marktbreite, Führende und Nachlaufende), von Hand redigieren und als Wissensseite veröffentlichen.

**Abnahme**: Der Generator ist reproduzierbar; der Entwurf enthält Daten und Diagramme; der redaktionelle Prüfprozess ist dokumentiert.

### 7. Ereigniskalender

**Plan**: Termine für Quartalszahlen, Messen und das Inkrafttreten von Politikmaßnahmen in einer manuellen JSON-Datei pflegen und auf Startseite und Unternehmensseiten anzeigen.

**Abnahme**: Termine sind überprüfbar; vergangene Ereignisse werden automatisch ausgeblendet; Labels existieren in allen vier Sprachen.

### 8. Datenqualitäts-Panel

**Plan**: `/status.html` ergänzen mit Abdeckung, veralteten Instrumenten, Parse-Fehlern, Quellenstatus und den letzten 30 Builds.

**Abnahme**: Es werden keine sensiblen Informationen offengelegt; die Seite kann als Einstieg in den Betrieb dienen.

## Langfristig (6–12 Monate)

### 9. Nachrichten aus mehreren Quellen und Themen-Clustering

**Plan**: Auf chinesische, japanische und deutsche Medienquellen ausweiten, Meldungen nach Stufe und Unternehmen clustern und eine Ansicht „diese Woche in jeder Stufe“ bereitstellen.

**Abnahme**: Quellen sind konfigurierbar; Deduplizierung und Relevanzbewertung; Urheberrechtskonformität.

### 10. Historische Zeitreihen und Zykluspositionierung

**Plan**: Eine längere Historie aufbewahren (oder wöchentlich aggregieren) und Bewertungsperzentile, Marktbreitenhistorie und Stufenrotation berechnen.

**Abnahme**: Das Datenvolumen bleibt handhabbar (< 20 MB); die Seitenperformance verschlechtert sich nicht; die Methodik bleibt erklärbar.

### 11. iOS-Client-Upgrade

**Plan**: Von `latest_data.json` auf `/api/snapshot.{lang}.json` migrieren und vier Sprachen sowie das globale Unternehmensuniversum unterstützen.

**Abnahme**: Der alte Client kann das Legacy-Payload weiterhin dekodieren; der neue Client unterstützt den Sprachwechsel; TestFlight-Verifikation.

### 12. Prozess für Community-Beiträge

**Plan**: Issue-Templates (Datenkorrekturen / Inhaltsvorschläge / Methodendiskussionen), ein Pull-Request-Template und eine Liste der Beitragenden.

**Abnahme**: Templates sind nutzbar; die CI validiert Pull Requests automatisch; Merge-Zeit unter 7 Tagen.

## Nicht geplant

- Echtzeit-Level-2-Kurse, Handelschnittstellen oder Positionsempfehlungen.
- Paywalls, Werbung oder Nutzer-Tracking.
- Von LLMs erzeugte Anlagekonklusionen ohne redaktionelles Review.
- Unternehmen mit nicht verifizierbaren Daten nur zur Erhöhung der Abdeckung aufnehmen.

## Prioritätsregel

Arbeiten in dieser Reihenfolge aufnehmen:

1. Dinge, die die Vertrauenswürdigkeit der Daten beeinflussen (Quellen, Verträge, Validierung)
2. Dinge, die die Wartbarkeit beeinflussen (Dokumentation, Tests, CI)
3. Dinge, die die Tiefe des Verständnisses beeinflussen (Inhalte, Methodik, Visualisierung)
4. Dinge, die die Breite der Abdeckung beeinflussen (neue Unternehmen, neue Märkte)

Jede neue Funktion muss beantworten: **Macht sie die Lesenden klarer, oder gibt sie ihnen nur mehr?**

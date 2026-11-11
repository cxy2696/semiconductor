# Methodik: Faktoren, Scores und Grenzen

Version 3.0.0 · Gültig ab 2026-11-11 · Entspricht der Seite `/methodology.html`

Dieses Dokument definiert, wie jede Zahl auf der Website berechnet wird. Jede Methodenänderung muss dieses Dokument, die Methodenseite der Website, `CHANGELOG.md` und die Versionsnummer gemeinsam aktualisieren.

---

## 1. Research-Fragen

Die Methodik beantwortet nur drei Fragen:

1. **In welchem Zustand ist diese Stufe?** (Messungen der Marktlage)
2. **Welche Unternehmen sollte ich zuerst lesen?** (Research-Priorität)
3. **Sind die Daten hinter meinem Urteil vollständig?** (Datenabdeckung)

Sie beantwortet nicht: zukünftige Renditen, Kursziele, Einstiegs- oder Ausstiegszeitpunkte oder Positionsgrößen.

## 2. Stichprobe und Klassifikation

- **Stichprobe**: die 175 börsennotierten Unternehmen in `data/universe.csv`.
- **Ein Unternehmen, eine Börsennotierung**: die Hauptnotierung wird bevorzugt; dasselbe Unternehmen wird nicht in mehreren Märkten gezählt (zum Beispiel wird SMIC nur durch seine A-Aktie 688981 repräsentiert und Hua Hong nur durch seine Hongkong-Notierung 1347).
- **Stufe**: Jedes Unternehmen wird nach seiner Hauptumsatzquelle einer von 8 Stufen zugeordnet; dies ist ein redaktionelles Urteil, und der Pull Request muss die Grundlage nennen.
- **Rolle**: fabless / foundry / idm / memory / equipment / materials / osat / module / eda_ip.
- **Land**: die Hauptsitzregion, eine von 13. **Markt**: der Börsenmarkt, einer von 7; beide können abweichen (zum Beispiel hat NXP seinen Hauptsitz in den Niederlanden und ist in den USA notiert).
- **Produkt-Tags**: aus einem kontrollierten Vokabular von 70 Tags in `taxonomy.json`, verwendet für Filterung und Anzeige auf der Unternehmensseite.
- **Unternehmens-Metadaten**: `founded` (Jahr) und `fiscal_year_end` (Monat) sind beschreibende Felder und fließen in keinen Faktor ein.

Ein Unternehmen darf nur aufgenommen oder entfernt werden, wenn es börsennotiert ist, den Großteil seines Umsatzes mit Halbleitern erzielt, eine verlässliche Kursquelle hat und eine fehlende Stufe oder Region abdeckt oder ein wichtiger Marktführer ist. Änderungen werden in `CHANGELOG.md` festgehalten.

## 3. Datenfelder

| Feld | Definition | Einheit | Behandlung fehlender Werte |
| --- | --- | --- | --- |
| `price` | Jüngster verfügbarer Schlusskurs (verzögerter Kurs) | lokale Währung | `—` anzeigen; aus kursbasierten Faktoren ausgeschlossen |
| `change_pct` | Veränderung am jüngsten Handelstag | % | Wie oben |
| `ret_30d` | Veränderung über die jüngsten 30 **Handelstage** | % | Wie oben |
| `ret_ytd` | Veränderung seit Jahresbeginn | % | Wird nicht bewertet |
| `market_cap` | Gesamte Marktkapitalisierung (lokale Währung) | lokale Währung | Aus dem Größenfaktor ausgeschlossen |
| `market_cap_usd` | Marktkap. × Wechselkurs | USD | Aus dem Größenfaktor ausgeschlossen |
| `pe` | Statisches Kurs-Gewinn-Verhältnis (jüngster Jahres-EPS) | Vielfaches | ≤ 0 oder fehlend → Bewertungsfaktor fehlt |
| `pb` | Kurs-Buchwert-Verhältnis | Vielfaches | Fehlen beeinflusst andere Faktoren nicht |
| `roe` | Eigenkapitalrendite | % | Fehlend → Qualitätsfaktor fehlt |
| `turnover` | Umschlagsrate | % | Nur Anzeige; nicht bewertet |
| `high_52w` / `low_52w` | Höchster / niedrigster Kurs der jüngsten 250 Handelstage | lokale Währung | Fehlend → Position in der Spanne fehlt |
| `coverage` | Anteil der 8 vorhandenen Felder | 0–1 | Siehe §6 |

> Die 52-Wochen-Spanne verwendet 250 Handelstage als Näherung und entspricht nicht zwangsläufig einem Kalenderjahr.

## 4. Faktordefinitionen

Jeder Faktor wird zunächst **innerhalb seiner Stufe** perzentilnormalisiert auf 0–100; Stufen mit weniger als 8 Unternehmen fallen auf die Gesamtstichprobe zurück. Perzentile verwenden den mittleren Rang (Mid-Rank); Gleichstände erhalten den durchschnittlichen Rang.

### 4.1 Qualität

```text
quality = percentile_rank(ROE, peer_group)
```

Ein höherer ROE bedeutet einen höheren Qualitätsscore. Fehlender ROE bedeutet einen fehlenden Faktor.

### 4.2 Bewertung

```text
valuation = percentile_rank(-PE, peers_with_positive_PE)   # PE > 0
valuation = missing                                        # PE ≤ 0 or missing
```

Ein niedrigeres KGV bedeutet einen höheren Bewertungsscore. Verlustunternehmen wird nicht die Illusion vermittelt, „billig“ zu sein; ihr Bewertungsfaktor fehlt schlicht.

### 4.3 Momentum

```text
momentum = 0.6 × percentile_rank(ret_30d, peers)
         + 0.4 × percentile_rank(range_position, peers)

range_position = (price - low_52w) / (high_52w - low_52w)  ∈ [0,1]
```

Fehlt eine Komponente, wird mit dem verbleibenden Gewicht renormiert; fehlen beide, fehlt der Faktor.

### 4.4 Größe

```text
size = percentile_rank(log10(market_cap_usd), peers)
```

Die Größe ist ein Proxy für Liquidität und Widerstandskraft, kein Maß für Qualität.

### 4.5 Research-Priorität

```text
priority = 100 × Σ(w_i × factor_i) / Σ(w_i)      # sum over available factors only
w = {quality: 0.30, valuation: 0.25, momentum: 0.25, size: 0.20}
```

- Fehlende Faktoren werden nicht mit 50 aufgefüllt; die verbleibenden Gewichte werden **renormiert**, was die Verzerrung durch einen neutralen Wert vermeidet.
- `factor_coverage = Σ available weights / 1.0`, verwendet als Signal dafür, wie viel Vertrauen der Score verdient.
- Das Ergebnis wird auf eine ganze Zahl gerundet und auf 0–100 begrenzt.

## 5. Risikoflags

| Flag | Auslöser | Bedeutung |
| --- | --- | --- |
| `loss` | `pe ≤ 0` | Verlust im jüngsten Geschäftsjahr; die Bewertung ist nicht anwendbar |
| `rich` | Bewertungsscore ≥ 80 | Teuer relativ zu seiner Stufe |
| `small` | Marktkap. < 2 Mrd. USD | Schwache Größe und Liquidität |
| `sharp` | `abs(ret_30d)` ≥ 25 % | Große Kursbewegung in den letzten 30 Tagen |
| `stale` | Snapshot älter als 48 Stunden | Daten möglicherweise veraltet |

`risk_level`: keine aktiven Flags = niedrig; 1–2 = mittel; 3 oder mehr = hoch. `stale` wird separat angezeigt und zählt nicht zum Risikoniveau.

## 6. Datenabdeckung

Die 8 Felder sind `price`, `change_1d`, `ret_30d`, `market_cap_usd`, `pe`, `pb`, `roe` und `range`.

```text
coverage = available fields / 8
≥ 0.875 → high      (7–8 fields)
≥ 0.625 → medium    (5–6 fields)
< 0.625 → low       (4 or fewer fields)
```

Die Abdeckung misst, ob Felder **vorhanden** sind, nicht ob die Daten korrekt sind.

## 7. Marktlage

Für alle Unternehmen mit `ret_30d`:

```text
breadth    = advancing companies / valid companies
median     = median(ret_30d)
dispersion = P75(ret_30d) - P25(ret_30d)
```

Klassifikation:

| Bedingung | Zustand |
| --- | --- |
| Marktbreite ≥ 0,60 und Median > 2 % | Expansion |
| Marktbreite ≤ 0,40 und Median < −2 % | Kontraktion |
| andernfalls | Neutral |

Führende / nachlaufende Stufen sind die Stufen mit mindestens 3 Unternehmen und der höchsten / niedrigsten Median-Rendite. Die Marktlage beschreibt die aktuelle Struktur; sie prognostiziert keine Richtung.

## 8. Research-Listen

| Liste | Regel | Sortierung |
| --- | --- | --- |
| Qualität zuerst | `quality ≥ 70` und `valuation ≥ 50` | Priorität absteigend |
| Bewertungsreset | `valuation ≥ 70` und `quality ≥ 50` | Bewertung absteigend |
| Momentum-Führer | `momentum ≥ 80` und `ret_30d > 0` | Momentum absteigend |

Jede Liste enthält höchstens 8 Unternehmen und nur Unternehmen mit einem Kurs.

## 9. Leseanleitung

- **Scores sind relativ**: Dasselbe Unternehmen kann in einer anderen Stufe oder an einem anderen Datum anders abschneiden.
- **Ein hoher Score heißt nicht gutes Unternehmen**: Es kann schlicht günstig, momentumgetrieben oder in einer kleinen Stufe klassifiziert sein.
- **Ein niedriger Score heißt nicht schlechtes Unternehmen**: Es kann am Zyklustief stehen, Daten vermissen lassen oder teuer, aber qualitativ hochwertiger sein.
- **Scores nicht stufenübergreifend vergleichen**: Die Normalisierung erfolgt innerhalb einer Stufe.
- **Den Score immer zusammen mit der Abdeckung lesen**: Einen Score mit niedriger Abdeckung nur als Hinweis behandeln.

## 10. Bekannte Grenzen

1. Kurse sind verzögerte Kurse oder Schlusskurse und enthalten keine Orderbuch- oder Intraday-Signale.
2. Das statische KGV ist für wachstumsstarke Unternehmen ungünstig; Verlustunternehmen haben keinen Bewertungsfaktor.
3. Umsatzwachstum, Auftragseingang, Kapazitätsauslastung und Lagerdaten fehlen, daher stützt sich der Qualitätsfaktor allein auf den ROE.
4. Die 52-Wochen-Spanne verwendet 250 Handelstage als Näherung.
5. Wechselkurse werden täglich aktualisiert, daher sind währungsübergreifende Vergleiche mit einem Tagesfehler behaftet.
6. Die Klassifikation enthält redaktionelles Urteil; Geschäftsmodelle wandeln sich und erfordern eine vierteljährliche Prüfung.
7. Die Stichprobe ist auf große börsennotierte Unternehmen ausgerichtet und enthält daher einen Survivorship-Bias.

## 11. Änderungskontrolle

1. Formel oder Schwelle ändern → dieses Dokument + Methodenseite der Website + `CHANGELOG.md` aktualisieren und die Hauptversion erhöhen.
2. Faktor hinzufügen → zuerst einen Offline-Vergleich durchführen, die Wirkung auf die Listen festhalten, dann mergen.
3. Stichprobe oder Klassifikation ändern → die Unternehmen, den Grund und die betroffenen Seiten im Pull Request auflisten.
4. Jeder Build berechnet die Scores neu und behält keine historischen Scores; für Backtests die historischen Snapshots in `data/snapshots/` verwenden.

## 12. Haftungsausschluss

Diese Website dient ausschließlich der Branchenrecherche und dem Lernen und stellt keine Empfehlung dar, Wertpapiere zu kaufen oder zu verkaufen. Daten können verzögert oder falsch sein; maßgeblich sind stets Börsenzulassungsunterlagen und Unternehmensmitteilungen. Jede Entscheidung, die auf Grundlage dieser Website getroffen wird, liegt in der Verantwortung der Nutzenden.

---
title: Lithografie: von DUV bis High-NA-EUV
summary: Die Lithografie bestimmt, wie klein ein Muster sein kann, und prägt die Kostenstruktur führender Nodes. Auflösung, Overlay und Lichtquelle erklären den Wertpool der Ausrüstung.
level: advanced
minutes: 10
order: 3
tags: lithography, euv, equipment
related: process-flow, equipment-materials, metrics
updated: 2026-11-10
---

Die Lithografie ist der teuerste und komplexeste Teil der Fertigung. Sie projiziert das Maskenmuster auf den Fotolack und legt die minimale Strukturgröße jeder Lage fest.

## Drei Variablen hinter der Auflösung

Die optische Auflösung ist näherungsweise R = k₁ × λ / NA:

- **λ**: 248 nm KrF, 193 nm ArF, dann 13,5 nm EUV.
- **NA**: 1,35 bei DUV-Immersion, 0,33 bei EUV, 0,55 bei High-NA-EUV.
- **k₁**: ein Prozessfaktor, der durch Lack, Beleuchtung und computergestützte Lithografie verbessert wird und heute nahe an den physikalischen Grenzen liegt.

Wenn die Wellenlänge nicht weiter schrumpfen kann, teilt die Industrie eine Lage per **Multi-Patterning** (SADP, SAQP) in mehrere Belichtungen auf – zu Lasten von mehr Schritten, Masken und Kosten.

## Warum EUV schwierig ist

EUV-Licht bei 13,5 nm wird von fast allem absorbiert, daher lassen sich keine Linsen verwenden: Das System beruht auf Multilayer-Spiegeln, einer Zinn-Tropfen-Plasmaquelle und einem Vakuumpfad. ASML ist der einzige Werkzeuglieferant; Zeiss liefert die Optik, Trumpf den Laser.

## Was High-NA ändert

High-NA hebt die NA auf 0,55, druckt kleinere Strukturen in einer einzigen Belichtung und reduziert Multi-Patterning. Zugleich bringt es größere Masken, ein kleineres Feld und deutlich höhere Werkzeugkosten sowie neue Anforderungen an Materialien und Inspektion.

## Folgen für die Research-Arbeit

- Die **Anzahl der EUV-Lagen** ist die entscheidende Variable für den Wert der Leading-Edge-Ausrüstung.
- Lack, Masken, Pellicles und Inspektion wachsen mit der EUV-Durchdringung.
- Lange Lieferzeiten für Werkzeuge verstärken die Umsatzschwankungen der Ausrüstungshersteller.
- Reife Nodes brauchen kein EUV; ihre Logik folgt eher einem Kapazitäts- und Preiszyklus.

## Häufige Fehldeutung

„3nm“ und „2nm“ sind keine physikalischen Abmessungen. Es sind Generationsbezeichnungen, die Dichte, Leistung und Energieverbrauch verbinden. Beurteilen Sie einen Node nach Transistoren pro mm² und SRAM-Dichte.

## Referenzen

- [ASML: Alles über Mikrochips](https://www.asml.com/en/technology/all-about-microchips)
- [Wikipedia: Extrem-UV-Lithografie](https://en.wikipedia.org/wiki/Extreme_ultraviolet_lithography)
- [Semiconductor Engineering](https://semiengineering.com/)

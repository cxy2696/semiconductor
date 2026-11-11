---
title: EDA und IP: die Mautstelle des Chipdesigns
summary: Bevor ein Chip existiert, wird er mit Werkzeugen entworfen und aus lizenzierten Blöcken zusammengesetzt. EDA und IP sind kleine Märkte mit überproportionaler Kontrolle über die gesamte Kette.
level: core
minutes: 8
order: 10
tags: eda, ip, business-model, margins
related: value-chain, ai-datacenter, metrics
updated: 2026-11-11
---

Ein modernes System-on-Chip enthält Milliarden Transistoren und Dutzende wiederverwendete Blöcke. Fast nichts davon ist von Grund auf neu entworfen. Zwei Ebenen machen das möglich: **EDA-Software**, die Absicht in fertigbare Geometrie übersetzt, und **IP**, die vorgebaute und vorverifizierte Schaltungsblöcke liefert.

## Zwei Geschäftsmodelle unter einem Dach

- **EDA** wird lizenziert, meist als zeitbasierte Abonnements mit mehrjährigen Verträgen. Der Umsatz ist wiederkehrend und sichtbar, Verlängerungen tragen sehr hohe Bruttomargen.
- **IP** wird pro Design lizenziert und erwirtschaftet dann eine **Royalty pro ausgeliefertem Chip**. Royalties laufen der Erstanlizenzierung um ein bis drei Jahre nach, daher folgt der IP-Umsatz den Endmarktvolumina.

Die drei größten EDA-Anbieter – Synopsys, Cadence und Siemens EDA – halten zusammen die Mehrheit des Markts. Arm dominiert Prozessor-IP, während Schnittstellen- und Speicher-IP unter mehreren Spezialisten aufgeteilt ist.

## Warum ein Wechsel so schwer ist

EDA ist kein Einzelkauf. Es ist in einen Flow eingebettet: Process Design Kits (PDKs) der Foundry, Verifikations-Sign-off, Emulation, Packaging und Test. Ein Werkzeug zu wechseln bedeutet, einen ganzen Flow neu zu qualifizieren, Ingenieure umzuschulen und einen Tape-out zu riskieren. Deshalb wechseln Kunden selten allein wegen des Preises.

Der Burggraben ist daher **Workflow-Lock-in plus Talent**: Universitäten lehren die dominierenden Werkzeuge, und erfahrene Ingenieure wechseln zwischen Unternehmen und nehmen diese Vertrautheit mit.

## Was KI ändert

Maschinelles Lernen wird auf Place-and-Route, Design-Space-Exploration, Verifikationsabdeckung und Lithografie-Optimierung angewendet. Der Effekt ist höhere Produktivität pro Ingenieur, was den Wert der Toolchain erhöht statt sie zu ersetzen. Es öffnet zudem eine Lücke für Start-ups bei Point-Tools, aber noch nicht bei vollständigen Flows.

## Der China-Aspekt

Heimische EDA-Anbieter sind bei Point-Tools und Flows für reife Nodes schnell gewachsen, gestützt durch Lokalisierungspolitik. Die Full-Flow-Fähigkeit für fortschrittliche Nodes und die IP für Leading-Edge-Designs bleiben der schwierige Teil. Exportkontrollen für EDA wiegen daher überproportional: Sie beschränken nicht ein Produkt, sondern die Fähigkeit zu entwerfen überhaupt.

## Worauf zu achten ist

- Abonnement-Auftragsbestand und Verlängerungsraten.
- Royalty-Umsatz als Proxy für Chipvolumina der Endmärkte.
- Akzeptanz von 3D-IC- und Chiplet-Designwerkzeugen.
- China-Umsatzexposure und Änderungen der Exportkontrollen.
- F&E-Intensität: 30–40 % des Umsatzes sind bei den führenden Anbietern normal.

## Referenzen

- [Synopsys: Investor Relations](https://investor.synopsys.com/)
- [Cadence: Investor Relations](https://investor.cadence.com/)
- [Arm: Investor Relations](https://investors.arm.com/)
- [Wikipedia: Electronic Design Automation](https://en.wikipedia.org/wiki/Electronic_design_automation)

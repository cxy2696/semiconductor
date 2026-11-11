---
title: KI-Silizium für Rechenzentren: Das Rack ist der neue Chip
summary: KI-Compute ist längst keine einzelne GPU mehr, sondern ein Rack-Scale-System aus Beschleunigern, HBM, Switches und Optik. Die Engpässe haben sich zu Packaging, Speicher und Strom verschoben.
level: advanced
minutes: 10
order: 12
tags: ai-compute, hbm, networking, cowos
related: memory-hbm, advanced-packaging, equipment-materials
updated: 2026-11-11
---

Das Training eines Frontier-Modells erfordert Tausende Beschleuniger, die als eine Maschine arbeiten. Das verändert, was ein „Chip“ ist: Die Designeinheit ist heute ein Rack – Dutzende GPUs oder kundenspezifische ASICs, Hunderte HBM-Stacks, Hochgeschwindigkeits-Switches und optische Verbindungen, alle mit Strom und Kühlung versorgt.

## Drei Architekturen konkurrieren

- **Allzweck-GPU**: NVIDIAs Plattform plus CUDA. Der Vorteil ist Softwarereife und ein breites Ökosystem.
- **Custom-ASIC**: Google TPU, AWS Trainium, Meta MTIA und ähnliche. Niedrigere Stückkosten in der Skalierung, aber hohe Entwicklungskosten und schmalere Softwareunterstützung.
- **Hybrid**: GPU fürs Training, ASIC oder inferenzoptimierte Bauteile für Serving, oft im selben Cluster.

## Die Speicherwand

HBM liefert die Bandbreite, die die Beschleuniger versorgt. Jede Generation erhöht Stackhöhe und Kapazität: 8-High, 12-High und schließlich 16-High, mit Hybrid Bonding für künftige Nodes. HBM verbraucht pro Bit weit mehr Waferkapazität als Standard-DRAM; deshalb weisen Speicherhersteller ihm Leading-Edge-Kapazität zu, und deshalb kann sich die HBM-Preisbildung vom Commodity-DRAM entkoppeln.

## Netzwerk ist die versteckte Steuer

Ein Cluster ist nur so schnell wie sein Interconnect. NVLink und proprietäre Fabrics übernehmen das Scale-up innerhalb eines Racks; InfiniBand und Ethernet das Scale-out. Optische Transceiver, DSPs und zunehmend Co-Packaged Optics bewegen Daten zwischen Racks. Mit steigender Beschleunigerzahl wächst der Netzwerkanteil pro GPU schneller als der Compute-Anteil.

## Strom und Kühlung

Ein einzelnes Rack kann über 100 kW ziehen. Flüssigkühlung, 800-V-Gleichstromverteilung und Stromerzeugung vor Ort werden Teil des Systemdesigns. Standorte mit günstigem Strom und schnellen Genehmigungen haben einen Vorteil, den kein Chipdesigner replizieren kann.

## Wo die Engpässe liegen

1. **CoWoS und Advanced Packaging**: Kapazität.
2. **HBM**: Stacking-Ausbeute und Kapazität.
3. **ABF-Substrate** und PCBs mit hoher Lagenzahl.
4. **Strom**: Verfügbarkeit und Netzanschluss.
5. **Optische Komponenten** und Laserangebot.

## Worauf zu achten ist

- Beschleuniger-Auslieferungen und durchschnittliche Verkaufspreise auf Rack-Ebene.
- HBM-Anteil pro Beschleuniger und Stackhöhe.
- Networking-Attach-Rate: Switches und Optik pro GPU.
- Anteil kundenspezifischer ASICs am Hyperscaler-Capex.
- Inferenznachfrage, die verteilter und preissensibler ist als Training.

## Referenzen

- [NVIDIA: Rechenzentrum](https://www.nvidia.com/en-us/data-center/)
- [TSMC: Advanced Packaging](https://www.tsmc.com/english/dedicatedFoundry/technology)
- [TrendForce: HBM-Research](https://www.trendforce.com/)
- [SemiAnalysis](https://semianalysis.com/)

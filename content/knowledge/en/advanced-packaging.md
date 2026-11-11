---
title: Advanced packaging: CoWoS, HBM and chiplets
summary: As scaling slows, packaging becomes the main lever for compute. Understand 2.5D/3D, hybrid bonding and the capacity bottleneck behind AI chips.
level: advanced
minutes: 10
order: 5
tags: packaging, cowos, chiplet, hbm
related: memory-hbm, process-flow, value-chain
updated: 2026-11-10
---

Packaging used to mean “wrapping the chip”. Today it determines whether an AI accelerator can be built at all, and how many can ship.

## Why packaging matters now

With Moore's Law slowing, raising transistor density on one die gets more expensive every node. The industry moved in two directions: split large chips into chiplets, and place memory closer to compute through 2.5D/3D integration. Both depend on advanced packaging.

## Four mainstream approaches

- **WLCSP**: packaging and balling completed on the wafer; package close to die size, suited to small, low-pin-count parts.
- **2.5D (CoWoS)**: GPU and HBM connected through a silicon interposer; the mainstream route for AI accelerators.
- **3D stacking (SoIC, hybrid bonding)**: two wafers bonded directly, with interconnect pitch below 10µm.
- **Fan-out**: reconstituted molding around the die for high-density routing, common in phones and networking.

## Where the bottleneck sits

AI supply is constrained by CoWoS capacity, HBM stacking yield and ABF substrates. CoWoS needs interposers, TSVs and high-precision bonding; adding capacity takes quarters. HBM needs TSVs, stacking and test; any yield shortfall limits shipments.

## Where equipment and materials benefit

Advanced packaging pulls front-end processes into the back end: lithography for RDL, deposition and CMP for bump and bond interfaces, inspection for TSVs and alignment. Beneficiaries include packaging equipment, hybrid bonding tools, temporary bonding materials and test.

## What to watch

- Advanced-packaging revenue mix and growth.
- CoWoS/HBM capex and capacity guidance.
- Test hours and probe-card demand.
- Substrate and molding-compound tightness.

## Common misreading

Equating packaging with low margins. Traditional packaging is low-margin, but advanced packaging is capital- and technology-intensive, with margins approaching front-end levels.

## References

- [TSMC: Advanced packaging](https://www.tsmc.com/english/dedicatedFoundry/technology)
- [ASE Technology](https://www.aseglobal.com/)
- [BESI: Hybrid bonding](https://www.besi.com/)

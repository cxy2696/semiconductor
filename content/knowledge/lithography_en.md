---
title: Lithography: from DUV to High-NA EUV
summary: Lithography sets how small a pattern can be and shapes the cost structure of leading-edge nodes. Resolution, overlay and light source explain the equipment value pool.
level: advanced
minutes: 10
order: 3
tags: lithography, euv, equipment
related: process-flow, equipment-materials, metrics
updated: 2026-11-10
---

Lithography is the most expensive and complex part of manufacturing. It projects the mask pattern onto photoresist and sets the minimum feature size of every layer.

## Three variables behind resolution

Optical resolution is approximately R = k₁ × λ / NA:

- **λ**: 248nm KrF, 193nm ArF, then 13.5nm EUV.
- **NA**: 1.35 for DUV immersion, 0.33 for EUV, 0.55 for High-NA EUV.
- **k₁**: a process factor improved by resist, illumination and computational lithography, now close to physical limits.

When wavelength cannot shrink further, the industry uses **multi-patterning** (SADP, SAQP) to split one layer into several exposures, at the cost of more steps, masks and money.

## Why EUV is hard

EUV light at 13.5nm is absorbed by almost everything, so lenses cannot be used: the system relies on multilayer mirrors, a tin-droplet plasma source and a vacuum path. ASML is the sole tool supplier; Zeiss provides optics and Trumpf the laser.

## What High-NA changes

High-NA raises NA to 0.55, printing smaller features in a single exposure and reducing multi-patterning. It also brings larger masks, a smaller field and much higher tool cost, plus new material and inspection requirements.

## Implications for research

- **EUV layer count** is the key variable for leading-edge equipment value.
- Resist, masks, pellicles and inspection grow with EUV penetration.
- Long tool lead times amplify revenue swings at equipment vendors.
- Mature nodes do not need EUV; their logic is closer to a capacity and pricing cycle.

## Common misreading

“3nm” and “2nm” are not physical dimensions. They are generational labels combining density, performance and power. Judge a node by transistors per mm² and SRAM density.

## References

- [ASML: All about microchips](https://www.asml.com/en/technology/all-about-microchips)
- [Wikipedia: Extreme ultraviolet lithography](https://en.wikipedia.org/wiki/Extreme_ultraviolet_lithography)
- [Semiconductor Engineering](https://semiengineering.com/)

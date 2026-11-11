---
title: EDA and IP: the toll booth of chip design
summary: Before a chip exists, it is designed with tools and assembled from licensed blocks. EDA and IP are small markets with outsized control over the entire chain.
level: core
minutes: 8
order: 10
tags: eda, ip, business-model, margins
related: value-chain, ai-datacenter, metrics
updated: 2026-11-11
---

A modern system-on-chip contains billions of transistors and dozens of reused blocks. Almost none of it is designed from scratch. Two layers make that possible: **EDA software**, which turns intent into manufacturable geometry, and **IP**, which supplies pre-built and pre-verified circuit blocks.

## Two business models under one roof

- **EDA** is licensed, usually as time-based subscriptions with multi-year agreements. Revenue is recurring and visible, and renewals carry very high gross margins.
- **IP** is licensed per design and then earns a **royalty per shipped chip**. Royalties lag the initial licence by one to three years, so IP revenue tracks end-market volumes.

The three largest EDA vendors — Synopsys, Cadence and Siemens EDA — together hold the majority of the market. Arm dominates processor IP, while interface and memory IP is split among several specialists.

## Why switching is so hard

EDA is not a standalone purchase. It is embedded in a flow: process design kits (PDKs) from the foundry, verification sign-off, emulation, packaging and test. Changing a tool means re-qualifying an entire flow, retraining engineers and risking a tape-out. That is why customers rarely switch on price alone.

The moat is therefore **workflow lock-in plus talent**: universities teach the dominant tools, and experienced engineers move between companies carrying that familiarity with them.

## What AI changes

Machine learning is being applied to place-and-route, design-space exploration, verification coverage and lithography optimisation. The effect is higher productivity per engineer, which increases the value of the toolchain rather than replacing it. It also opens a gap for startups in point tools, but not yet in full flows.

## The China angle

Domestic EDA vendors have grown quickly in point tools and mature-node flows, supported by localisation policy. Advanced-node full-flow capability, and the IP needed for leading-edge designs, remain the hard part. Export controls on EDA therefore matter disproportionately: they constrain not one product but the ability to design at all.

## What to watch

- Subscription backlog and renewal rates.
- Royalty revenue as a proxy for end-market chip volumes.
- Adoption of 3D-IC and chiplet design tools.
- China revenue exposure and export-control changes.
- R&D intensity: 30–40% of revenue is normal at the leading vendors.

## References

- [Synopsys: Investor relations](https://investor.synopsys.com/)
- [Cadence: Investor relations](https://investor.cadence.com/)
- [Arm: Investor relations](https://investors.arm.com/)
- [Wikipedia: Electronic design automation](https://en.wikipedia.org/wiki/Electronic_design_automation)

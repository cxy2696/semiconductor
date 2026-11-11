---
title: AI data-centre silicon: the rack is the new chip
summary: AI compute is no longer a single GPU but a rack-scale system of accelerators, HBM, switches and optics. The bottlenecks have moved to packaging, memory and power.
level: advanced
minutes: 10
order: 12
tags: ai-compute, hbm, networking, cowos
related: memory-hbm, advanced-packaging, equipment-materials
updated: 2026-11-11
---

Training a frontier model requires thousands of accelerators working as one machine. That changed what a “chip” is: the unit of design is now a rack — dozens of GPUs or custom ASICs, hundreds of HBM stacks, high-speed switches and optical links, all supplied with power and cooling.

## Three architectures compete

- **General-purpose GPU**: NVIDIA's platform plus CUDA. The advantage is software maturity and a broad ecosystem.
- **Custom ASIC**: Google TPU, AWS Trainium, Meta MTIA and similar. Lower cost per unit at scale, but high development cost and narrower software support.
- **Hybrid**: GPU for training, ASIC or inference-optimised parts for serving, often inside the same cluster.

## The memory wall

HBM provides the bandwidth that keeps accelerators fed. Each generation raises stack height and capacity: 8-high, 12-high, and eventually 16-high, with hybrid bonding for future nodes. HBM consumes far more wafer capacity per bit than standard DRAM, which is why memory makers allocate leading-edge capacity to it and why HBM pricing can decouple from commodity DRAM.

## Networking is the hidden tax

A cluster is only as fast as its interconnect. NVLink and proprietary fabrics handle scale-up inside a rack; InfiniBand and Ethernet handle scale-out. Optical transceivers, DSPs and, increasingly, co-packaged optics move data between racks. As accelerator count rises, networking content per GPU rises faster than compute content.

## Power and cooling

A single rack can draw more than 100kW. Liquid cooling, 800V DC distribution and on-site power generation are becoming part of the system design. Sites with cheap power and fast permits have an advantage that no chip designer can replicate.

## Where the bottlenecks are

1. **CoWoS and advanced packaging** capacity.
2. **HBM** stacking yield and capacity.
3. **ABF substrates** and high-layer-count PCBs.
4. **Power** availability and grid interconnection.
5. **Optical components** and laser supply.

## What to watch

- Accelerator shipments and rack-level average selling prices.
- HBM content per accelerator and stack height.
- Networking attach rate: switches and optics per GPU.
- Custom ASIC share of hyperscaler capex.
- Inference demand, which is more distributed and more price-sensitive than training.

## References

- [NVIDIA: Data centre](https://www.nvidia.com/en-us/data-center/)
- [TSMC: Advanced packaging](https://www.tsmc.com/english/dedicatedFoundry/technology)
- [TrendForce: HBM research](https://www.trendforce.com/)
- [SemiAnalysis](https://semianalysis.com/)

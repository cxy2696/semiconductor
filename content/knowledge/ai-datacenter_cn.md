---
title: AI 数据中心芯片：机柜才是新的芯片
summary: AI 算力不再是一颗 GPU，而是由加速器、HBM、交换与光互连组成的机柜级系统。瓶颈已经转移到封装、存储与电力。
level: advanced
minutes: 10
order: 12
tags: ai-compute, hbm, networking, cowos
related: memory-hbm, advanced-packaging, equipment-materials
updated: 2026-11-11
---

训练前沿模型需要成千上万颗加速器像一台机器一样工作。这改变了“芯片”的定义：设计单元变成了机柜——几十颗 GPU 或定制 ASIC、数百个 HBM 堆栈、高速交换与光互连，以及配套的供电与散热。

## 三种架构在竞争

- **通用 GPU**：英伟达的平台加 CUDA。优势是软件成熟、生态广泛。
- **定制 ASIC**：谷歌 TPU、AWS Trainium、Meta MTIA 等。规模上来后单位成本更低，但开发成本高、软件支持窄。
- **混合**：训练用 GPU，推理用 ASIC 或推理优化芯片，常常在同一个集群里共存。

## 存储墙

HBM 提供喂饱加速器所需的带宽。每一代都在提升堆叠层数与容量：8 层、12 层，未来 16 层，并用混合键合继续演进。相同位元数下，HBM 消耗的晶圆产能远高于普通 DRAM，因此存储厂把先进产能优先分配给 HBM，HBM 价格也能部分脱离大宗 DRAM 周期。

## 网络是隐形的税

集群的速度取决于互连。机柜内用 NVLink 与专有 fabric 做 scale-up；机柜间用 InfiniBand 与以太网做 scale-out。光模块、DSP，以及越来越多的共封装光学（CPO）承担跨机柜的数据搬运。加速器越多，单颗 GPU 对应的网络价值量上升得比算力更快。

## 电力与散热

单个机柜功耗可以超过 100kW。液冷、800V 直流供电与现场发电正在成为系统设计的一部分。拥有廉价电力与快速审批的站点，拥有芯片设计者无法复制的优势。

## 瓶颈在哪里

1. **CoWoS 与先进封装**产能。
2. **HBM** 堆叠良率与产能。
3. **ABF 载板**与高层数 PCB。
4. **电力**供应与电网接入。
5. **光器件**与激光器供给。

## 观察指标

- 加速器出货量与机柜级均价。
- 单颗加速器的 HBM 含量与堆叠层数。
- 网络配套率：每颗 GPU 对应的交换机与光模块。
- 定制 ASIC 在超大规模厂商资本开支中的占比。
- 推理需求：比训练更分散、更价格敏感。

## 参考来源

- [NVIDIA: Data centre](https://www.nvidia.com/en-us/data-center/)
- [TSMC: Advanced packaging](https://www.tsmc.com/english/dedicatedFoundry/technology)
- [TrendForce: HBM research](https://www.trendforce.com/)
- [SemiAnalysis](https://semianalysis.com/)

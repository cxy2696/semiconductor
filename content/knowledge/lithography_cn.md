---
title: 光刻：从 DUV 到 High-NA EUV
summary: 光刻决定图形能画多小，也决定先进制程的成本结构。理解分辨率、套刻与光源，才能看懂设备端的价值分配。
level: advanced
minutes: 10
order: 3
tags: lithography, euv, equipment
related: process-flow, equipment-materials, metrics
updated: 2026-11-10
---

光刻是半导体制造中最贵、最复杂的环节之一。它把掩模上的图形投影到晶圆表面的光刻胶上，决定了每一层图形的最小尺寸。

## 分辨率的三个变量

光学光刻的分辨率近似为 R = k₁ × λ / NA：

- **λ（波长）**：从 248nm 的 KrF，到 193nm 的 ArF，再到 13.5nm 的 EUV。
- **NA（数值孔径）**：DUV 浸没式可以做到 1.35，EUV 为 0.33，High-NA EUV 提升到 0.55。
- **k₁**：工艺因子，靠光刻胶、照明与计算光刻优化，已经接近物理极限。

当波长无法继续缩短时，产业用**多重曝光**（SADP、SAQP）把一层图形拆成多次曝光，代价是工序数、掩模数与成本上升。

## EUV 为什么难

EUV 使用 13.5nm 极紫外光，几乎所有材料都会吸收它，因此不能使用透镜，只能使用多层反射镜；光源要用高功率激光轰击锡液滴产生等离子体；整个光路必须在真空中。阿斯麦是唯一整机供应商，蔡司提供光学系统，通快提供激光。

## High-NA 改变了什么

High-NA EUV 把 NA 提升到 0.55，可以在单次曝光下画出更小的图形，减少多重曝光。但它带来更大的掩模、更小的曝光场与更高的设备成本，也意味着新的材料与检测需求。

## 对投资的含义

- **EUV 层数**是先进制程设备价值量的核心变量。
- 光刻胶、掩模版、保护膜与检测设备会跟随 EUV 渗透率增长。
- 光刻机交付周期长，产能扩张节奏会放大设备厂的收入波动。
- 成熟制程不需要 EUV，投资逻辑更接近产能与价格周期。

## 常见误读

“3nm、2nm”并不是任何物理尺寸，而是综合了晶体管密度、性能与功耗的代际标签。判断制程强弱要看每平方毫米晶体管数与 SRAM 密度。

## 参考来源

- [ASML: All about microchips](https://www.asml.com/en/technology/all-about-microchips)
- [Wikipedia: Extreme ultraviolet lithography](https://en.wikipedia.org/wiki/Extreme_ultraviolet_lithography)
- [Semiconductor Engineering](https://semiengineering.com/)

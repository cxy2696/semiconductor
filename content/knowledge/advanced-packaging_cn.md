---
title: 先进封装：CoWoS、HBM 与 Chiplet
summary: 当制程微缩变慢，封装成为提升算力的主战场。理解 2.5D/3D、混合键合与产能瓶颈，才能看懂 AI 芯片的供给曲线。
level: advanced
minutes: 10
order: 5
tags: packaging, cowos, chiplet, hbm
related: memory-hbm, process-flow, value-chain
updated: 2026-11-10
---

过去封装只是“把芯片包起来”，现在它决定了 AI 芯片能不能造出来、能造多少。

## 为什么封装变得关键

摩尔定律放缓后，单颗芯片的晶体管密度提升越来越贵。产业转向两条路：一是把大芯片拆成多个小芯片（Chiplet），二是把内存与计算芯片靠得更近（2.5D/3D）。两者都依赖先进封装。

## 四种主流方案

- **WLCSP**：在晶圆上完成封装与植球，尺寸接近芯片本身，适合小尺寸、低引脚数。
- **2.5D（CoWoS）**：GPU 与 HBM 通过硅中介层互连，是 AI 加速卡的主流方案。
- **3D 堆叠（SoIC、混合键合）**：把两片晶圆直接键合，互连间距可降到 10µm 以下。
- **Fan-out**：在芯片周围重构塑封，实现高密度布线，常用于手机与网络芯片。

## 产能瓶颈在哪里

AI 芯片的瓶颈长期集中在 CoWoS 产能、HBM 堆叠良率与 ABF 基板。CoWoS 需要中介层、TSV 与高精度键合，扩产周期以季度计；HBM 需要 TSV、堆叠与测试，任何一环良率不达标都会限制出货。

## 设备与材料的机会

先进封装把前道工艺引入后道：光刻用于 RDL，沉积与 CMP 用于凸点与键合面，检测用于 TSV 与键合对准。受益者包括封装设备商、混合键合设备商、临时键合材料商与测试设备商。

## 观察指标

- 先进封装收入占比与增速。
- CoWoS/HBM 相关资本开支与产能指引。
- 测试时长（test hours）与探针卡需求。
- 封装基板与塑封料的供给紧张程度。

## 常见误读

把“封装”等同于低毛利。传统封装确实毛利偏低，但先进封装是资本与技术密集型，毛利率可以接近前道。

## 参考来源

- [TSMC: Advanced packaging](https://www.tsmc.com/english/dedicatedFoundry/technology)
- [ASE Technology](https://www.aseglobal.com/)
- [BESI: Hybrid bonding](https://www.besi.com/)

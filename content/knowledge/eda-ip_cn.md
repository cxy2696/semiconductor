---
title: EDA 与 IP：芯片设计的收费站
summary: 芯片在被制造之前，先由工具设计、由授权模块拼装。EDA 与 IP 市场不大，却对整个产业链拥有超额控制力。
level: core
minutes: 8
order: 10
tags: eda, ip, business-model, margins
related: value-chain, ai-datacenter, metrics
updated: 2026-11-11
---

一颗现代 SoC 包含数十亿晶体管和几十个复用模块，几乎没有一块是从零画起的。支撑这一切的是两层基础设施：把设计意图变成可制造图形的 **EDA 软件**，以及提供经过验证的电路模块的 **IP**。

## 一个屋檐下的两种生意

- **EDA** 以订阅制授权，通常是多年期协议。收入经常性高、可见性强，续约毛利率极高。
- **IP** 按设计授权，再按出货芯片收取 **版税**。版税通常滞后授权一到三年，因此 IP 收入跟随终端出货量。

EDA 三巨头——Synopsys、Cadence、Siemens EDA——合计占据大部分市场；处理器 IP 由 Arm 主导，接口与存储 IP 则由多家专业公司分割。

## 为什么换不掉

EDA 不是孤立采购，而是嵌在流程里：晶圆厂的 PDK、验证签核、仿真加速、封装与测试。换一个工具意味着重新认证整条流程、重新培训工程师，并承担流片失败的风险。因此客户很少因为价格而切换。

护城河的本质是**流程锁定 + 人才**：高校教的是主流工具，资深工程师带着熟悉度在公司之间流动。

## AI 改变了什么

机器学习被用于布局布线、设计空间探索、验证覆盖率和光刻优化。结果是每位工程师的产出提高，工具链的价值上升而不是被替代。它也为点工具创业公司打开缺口，但完整流程尚未被颠覆。

## 中国视角

国产 EDA 在点工具和成熟制程流程上成长很快，背后是国产化政策。先进制程的全流程能力，以及先进设计所需的 IP，仍是难点。因此 EDA 出口管制的杀伤力被放大：受限的不是某一个产品，而是“能不能设计”。

## 观察指标

- 订阅在手订单与续约率。
- 版税收入，作为终端芯片出货量的代理。
- 3D-IC 与 Chiplet 设计工具的渗透。
- 中国收入占比与出口管制变化。
- 研发费用率：龙头通常在 30%–40%。

## 参考来源

- [Synopsys: Investor relations](https://investor.synopsys.com/)
- [Cadence: Investor relations](https://investor.cadence.com/)
- [Arm: Investor relations](https://investors.arm.com/)
- [Wikipedia: Electronic design automation](https://en.wikipedia.org/wiki/Electronic_design_automation)

---
title: 存储与 HBM：周期之母
summary: 存储是半导体最标准的商品，也是周期波动最大的环节。HBM 把存储重新拉回 AI 中心，但供需逻辑仍然是 bit 与产能。
level: core
minutes: 9
order: 6
tags: memory, hbm, cycle
related: advanced-packaging, cycle, metrics
updated: 2026-11-10
---

存储是半导体行业里最像大宗商品的品类：产品标准化、价格透明、供需错配时价格可以在一年内翻倍，也可以在一年内腰斩。

## 三种主要产品

- **DRAM**：动态随机存储器，靠电容存储电荷，需要定期刷新，用于内存条与 HBM。
- **NAND**：非易失存储，按页读写、按块擦除，用于 SSD 与移动存储。
- **NOR**：容量小、可靠性高，用于代码存储与汽车电子。

## 周期的三个变量

1. **bit 供给**：由资本开支与制程迁移决定，新增产能通常需要 12–18 个月。
2. **bit 需求**：服务器、手机、PC 与 AI 共同拉动。
3. **库存**：原厂、模组厂与渠道的库存周数决定价格弹性。

当供给增速高于需求增速，价格下跌，原厂减产；当库存见底、需求回暖，价格上行，资本开支重新加速。这个循环大约三到五年。

## HBM 改变了什么

HBM 通过 TSV 垂直堆叠多层 DRAM，并以超宽接口与 GPU 相连，带宽可达数 TB/s。它带来三个结构性变化：

- **产能占用**：同样位元数，HBM 消耗的晶圆与产能远高于普通 DRAM。
- **良率门槛**：堆叠层数越多，良率与散热挑战越大。
- **客户绑定**：HBM 需要与 GPU 厂共同认证，供应关系更稳定。

这也是为什么 HBM 的景气可以部分脱离普通 DRAM 的价格周期。

## 观察指标

- bit 出货增速与合约价。
- 库存周数（原厂与渠道）。
- 资本开支与 wafer 产能。
- HBM 堆叠层数、良率与客户认证进度。

## 参考来源

- [TrendForce: Memory research](https://www.trendforce.com/)
- [Micron: HBM](https://www.micron.com/)
- [SK hynix](https://www.skhynix.com/)

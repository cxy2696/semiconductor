---
title: 露光：DUV から High-NA EUV まで
summary: 露光は微細化の限界と先端ノードのコスト構造を決める。解像度・重ね合わせ・光源を理解すると、装置価値の配分が見えてくる。
level: advanced
minutes: 10
order: 3
tags: lithography, euv, equipment
related: process-flow, equipment-materials, metrics
updated: 2026-11-10
---

露光は半導体製造で最も高価で複雑な工程の一つです。マスクのパターンをレジストに投影し、各層の最小寸法を決めます。

## 解像度を決める三つの変数

光学露光の解像度はおおよそ R = k₁ × λ / NA で表されます。

- **λ**：248nm の KrF、193nm の ArF、そして13.5nm の EUV。
- **NA**：DUV 液浸で1.35、EUV で0.33、High-NA EUV で0.55。
- **k₁**：レジスト・照明・計算リソグラフィで改善するプロセス因子。現在は物理限界に近い。

波長を短くできなくなると、**多重パターニング**（SADP、SAQP）で1層を複数回の露光に分割します。代償は工程数・マスク数・コストの増加です。

## EUV が難しい理由

13.5nm の極端紫外光はほぼすべての材料に吸収されるため、レンズは使えません。多層ミラー、スズ液滴をレーザーで叩くプラズマ光源、真空の光路が必要です。装置は ASML の独占供給で、光学系は Zeiss、レーザーは Trumpf が担います。

## High-NA が変えるもの

NA を0.55に上げ、1回の露光でより微細なパターンを描けるため多重露光を減らせます。一方でマスクは大型化し、露光フィールドは狭くなり、装置コストは大幅に上昇します。材料と検査にも新たな要求が生まれます。

## リサーチへの含意

- **EUV の層数**が先端装置の価値量を決める中核変数。
- レジスト、マスク、ペリクル、検査装置は EUV 普及とともに伸びる。
- 装置の納期が長く、生産能力拡張のタイミングが装置売上の変動を増幅する。
- 成熟ノードに EUV は不要で、投資論理は生産能力と価格のサイクルに近い。

## よくある誤読

「3nm」「2nm」は物理寸法ではありません。密度・性能・消費電力を合わせた世代ラベルです。実力は mm² 当たりのトランジスタ数と SRAM 密度で判断します。

## 参考資料

- [ASML: All about microchips](https://www.asml.com/en/technology/all-about-microchips)
- [Wikipedia: Extreme ultraviolet lithography](https://en.wikipedia.org/wiki/Extreme_ultraviolet_lithography)
- [Semiconductor Engineering](https://semiengineering.com/)

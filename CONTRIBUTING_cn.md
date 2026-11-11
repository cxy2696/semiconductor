# 参与贡献

感谢你愿意改进 SiliconScope。这个项目优先考虑**可核查**、**可维护**与**四语一致**。请按下面的流程提交变更。

## 环境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m semcore build      # 用仓库内快照构建
python -m semcore serve      # http://127.0.0.1:8000
python -m pytest
python -m semcore validate
```

## 常见变更

### 新增或修正一家公司

1. 编辑 `data/universe.csv`；一行一家公司。列定义见 `documentation/DATA_cn.md`。
2. 每家公司只保留一个主上市地；不要为不同市场重复添加同一公司。
3. 在 PR 中附来源（交易所页面或年报），并说明分类依据。
4. 运行 `python -m semcore validate --data-only`。
5. 若新公司的行情无法自动解析，运行 `python -m semcore fetch` 生成 `data/symbols.json` 映射。若仍然失败，在 PR 中注明，或设置 `quote_venue = "unpriced"`。

公司主数据为四语结构。v3 新增以下列：

| 列 | 必填 | 含义 |
| --- | --- | --- |
| `name_de` | 可选 | 德文展示名；留空回退到 `name_en` |
| `note_de` | 可选 | 德文公司备注；留空回退到英文备注 |
| `founded` | 可选 | 成立年份，四位数字 |
| `fiscal_year_end` | 可选 | 财年结束月份，`01`–`12` |

尽量补全德文名称与备注。无法核实时，`founded` 与 `fiscal_year_end` 留空；这两个字段只在存在时展示。

### 新增术语

1. 编辑 `data/glossary.json`；必须为**全部四种**语言提供 `term` 与 `def`：`en`、`zh`、`ja` 与 `de`。
2. 使用已有的 `category`（process / equipment / material / packaging / memory / design / business / economics / policy）。
3. 定义控制在 2–4 句，避免循环定义。
4. 运行 `python -m pytest tests/test_content.py`。

### 新增知识长文

1. 在 `content/knowledge/` 下创建扁平文件 `<slug>_en.md`、`<slug>_cn.md`、`<slug>_jp.md` 与 `<slug>_de.md`。slug 使用小写连字符。
2. 必填 front matter：`title`、`summary`、`level`（foundation/core/advanced）、`minutes`、`order`、`tags`、`related`、`updated`。
3. `related` 只能引用已存在的 slug。slug 与 `order` 在四种语言中必须完全一致。
4. 知识库当前有 12 个主题：`advanced-packaging`、`ai-datacenter`、`automotive`、`cycle`、`eda-ip`、`equipment-materials`、`lithography`、`memory-hbm`、`metrics`、`policy`、`process-flow` 与 `value-chain`。
5. 使用受支持的 Markdown 子集：`##`、`###`、段落、列表、引用、围栏代码块、粗体与链接。**不支持原始 HTML。**
6. 在文末列出可核查的参考来源。
7. 四种语言承载同等信息；不要发布“英文完整版 + 缩短译本”。

### 修改方法或评分

1. 先开 Issue，说明动机与预期影响。
2. 修改 `semcore/analytics.py` 并补充测试。
3. 更新 `documentation/METHODOLOGY_en.md` 及其 `_cn` / `_jp` / `_de` 译本，以及 `data/i18n/*.json` 中的站内文案。
4. 在 `CHANGELOG.md` 记录变更，并提升主版本号。
5. 在 PR 中附离线对比：分数分布、清单变化与受影响的页面。

### 修改样式或模板

- 设计变量位于 `assets/css/main.css` 顶部的 `:root` 与 `[data-theme="dark"]` 块中。
- 保持站点无 CDN、无框架、无外部字体。
- 检查 1440 / 1024 / 390 三个宽度、浅色与深色主题，以及键盘可达性。
- 不引入自动播放动画；尊重 `prefers-reduced-motion`。

## 代码风格

- Python 3.11+，优先使用类型标注，避免有副作用的全局状态。
- 模块职责见 `documentation/ARCHITECTURE_cn.md`；抓取、分析与渲染保持分离。
- 模板只负责展示；不要在模板中做复杂计算。
- 使用原生 JS API，避免依赖；所有交互在无 JS 时都必须有降级方案。

## PR 检查清单

- [ ] `python -m pytest` 通过
- [ ] `python -m semcore validate` 通过
- [ ] 界面键、知识 slug 与术语字段在四种语言中对齐
- [ ] 文档变更包含 `_en` / `_cn` / `_jp` / `_de` 版本
- [ ] 新增数据附来源
- [ ] 已检查移动端与深色模式
- [ ] 已按需更新 `CHANGELOG.md`
- [ ] 没有在 `docs/` 之外提交大文件

## 提交信息

使用简洁的祈使句，例如：

```text
data: add Toyota Industries to automotive coverage
fix: hide the P/B column below 1500px to avoid table overflow
docs: clarify that the 30-day return uses trading sessions
content: add the ai-datacenter topic in four languages
```

## 行为准则

- 讨论证据与方法，不针对个人。
- 不提交未经核实的数据或来源。
- 不把本站内容包装成投资建议。

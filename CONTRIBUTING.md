# 参与贡献

感谢你愿意改进 SiliconScope。这个项目优先考虑**可核查**、**可维护**与**三语一致**，请按下面的流程提交变更。

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

1. 编辑 `data/universe.csv`，一行一家公司，列含义见 `documentation/DATA.md`。
2. 只保留一个主上市地（不要同一公司重复两行）。
3. 在 PR 说明中附来源（交易所页面或年报），并说明分类依据。
4. 运行 `python -m semcore validate --data-only`。
5. 若新公司无法自动解析行情，运行 `python -m semcore fetch` 生成 `data/symbols.json` 映射；仍失败则在 PR 中注明，或设 `quote_venue = "unpriced"`。

### 新增术语

1. 编辑 `data/glossary.json`，必须同时提供 `zh`、`en`、`ja` 的 `term` 与 `def`。
2. `category` 使用已有分类（process / equipment / material / packaging / memory / design / business / economics / policy）。
3. 定义保持 2–4 句，避免循环定义。
4. 运行 `python -m pytest tests/test_content.py`。

### 新增知识长文

1. 在 `content/knowledge/{zh,en,ja}/` 下创建同名 `.md` 文件，slug 使用小写连字符。
2. front matter 必填：`title`、`summary`、`level`（foundation/core/advanced）、`minutes`、`order`、`tags`、`related`、`updated`。
3. `related` 只能引用已存在的 slug；三种语言的 `order` 与 slug 必须一致。
4. 正文使用受支持的 Markdown 子集：`##`、`###`、段落、列表、引用、代码块、粗体、链接。**不支持原始 HTML**。
5. 在文末列出可核查的参考来源。
6. 三语信息量要对等，不做“英文精简版”。

### 修改方法或评分

1. 先开 Issue 说明动机与预期影响。
2. 修改 `semcore/analytics.py`，补测试。
3. 同步更新 `documentation/METHODOLOGY.md` 与站内 `templates/methodology.html` 对应文案（`data/i18n/*.json`）。
4. 在 `CHANGELOG.md` 记录，主版本号 +1。
5. PR 中附离线对比：分数分布、清单变化、受影响的页面。

### 修改样式或模板

- 设计变量集中在 `assets/css/main.css` 顶部的 `:root` 与 `[data-theme="dark"]`。
- 保持无 CDN、无框架、无外部字体。
- 检查 1440 / 1024 / 390 三个宽度、浅色与深色、键盘可达性。
- 不引入自动播放动画；尊重 `prefers-reduced-motion`。

## 代码风格

- Python 3.11+，类型标注优先，避免副作用式全局状态。
- 模块职责见 `documentation/ARCHITECTURE.md`；抓取、分析、渲染分开。
- 模板只做展示，不在模板里做复杂计算。
- JS 使用原生 API，避免依赖；所有交互在无 JS 时仍有可用降级。

## PR 检查清单

- [ ] `python -m pytest` 通过
- [ ] `python -m semcore validate` 通过
- [ ] 三语 key 与知识 slug 对齐
- [ ] 新增数据附来源
- [ ] 移动端与深色模式检查
- [ ] `CHANGELOG.md` 已更新（如适用）
- [ ] 没有提交 `docs/` 之外的大文件

## 提交信息

使用简洁的祈使句，例如：

```text
data: add Tokyo Ohka and SUMCO to materials
fix: hide P/B column below 1500px to avoid table overflow
docs: clarify 30-day return uses trading sessions
```

## 行为准则

- 讨论聚焦证据与方法，不针对个人。
- 不提交未经核实的数据或来源。
- 不把本站内容包装成投资建议。

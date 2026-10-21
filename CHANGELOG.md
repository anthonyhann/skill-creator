# CHANGELOG

本文件归档 `skill-creator` 的版本变更与设计取舍。版本号以「能力跨代」为界：`v1.0.x` 为初始发布期、`v1.1.x` 为精简增强期、`v1.2.x` 为 skill-creator 全量重构期（当前 **v1.2.2**）。每个版本段落仅罗列与上一版的差异。

---

## v1.2.2 · 收敛去歧义 + 自验证闭环修复

**时间**：2026-09-11 ｜ **范围**：模板单一来源收敛、lint/evals 修复、token 精简（能力不降级）

### 收敛（消除多维护点）

- 确立 SKILL.md 为输出模板（Checkpoint 1.5/2.5、Phase 0 输出、交付摘要）与安全红线表的唯一权威来源；`protocol-spec.md`、`pattern-guide.md`、`eval-guide.md`、`question-bank.md`、`README.md` 改为指针引用，不再重复维护。
- 修复 Checkpoint 1.5 三处版本字段不一致（protocol-spec 版缺安全审计/.env.example 字段）导致的语义冲突。
- 对齐 EXTRACT 模式定义（统一为「可跳过 Q1-Q3，缺失项必须追问」）。
- `README.md` 去重：移除「触发方式」「验证命令」「简介」与「文件读取顺序」重复表，统一指向权威来源。

### Lint / evals 修复

- `description` 去除重复首句，补齐「当…时使用」WHEN 用语，NOT 统一为「Do NOT use for」。
- `validate_skill.py`：WHEN/NOT 检测词扩展接受「触发词/何时」「NOT for」（兼容仓库惯例写法，仅扩大接受面不降低检查强度）。
- 新增 `test-prompts.json`（happy/boundary/over-trigger/under-spec 4 用例），修复自违反 compliance-checklist F 节的问题。
- Step 0.3 复用诊断扫描目录补齐常见 agent skill 安装路径（`~/.claude/skills/`、`$PWD/.claude/skills/`）。

---

## v1.2.1 · skill-creator 全量重构

**时间**：2026-04-28 ｜ **范围**：协议层补齐、主流程重排、模板升级、验证器同源化、README 对齐

### 协议与参考资料

- 新增 `references/protocol-spec.md`，定义 Phase 0-6 输入输出、证据门禁、Checkpoint 1.5/2.5、交付契约。
- 新增 `references/refinement-playbook.md`，定义双评审精炼流程与退出条件。
- 新增 `references/generation-playbook.md`，定义模板填充顺序、组合模式上限和失败修正策略。
- `references/eval-guide.md` 新增 Checkpoint 2.5 强制输出模板。
- `references/compliance-checklist.md` 增加检查点一致性检查项。

### SKILL.md 重构

- frontmatter 升级为 WHAT/WHEN/NOT 三行强约束。
- Phase 0 强化入口分流与证据门禁（低置信度禁止进入构建）。
- Phase 1 引入主/辅模式约束与 1.5 检查点模板。
- Phase 2 引入评分门禁与 2.5 检查点模板。
- Phase 5/6 明确后置精炼与跨 Skill 一致性校验。

### 模板升级

- `templates/SKILL.md.template` 增加 Checkpoint、交付摘要强制段。
- `templates/p1~p5` 全部补齐 Checkpoint 与诚实边界段，保证最小可执行结构一致。

### 验证器升级

- `scripts/validate_skill.py` 新增 `Report.to_dict()` 结构化结果。
- 协议校验新增 `protocol-spec.md` 关键 token 检查。
- 新增 `.validation/validate-summary.json` 输出，便于 CI 与人工复核。

### 文档同步

- `README.md` 重写为 skill-creator 增强版流程说明，目录与命令与当前实现一致。
- `README.md` 补充并保留「核心理念 / 快速开始 / 使用场景」三段，同时将触发语句与场景表做一一映射，减少读者在入口指令与流程分流之间的理解跳转。
- `README.md` 端到端示例统一指向 `references/protocol-spec.md` 附录，避免双处维护导致的文档漂移。

---

## v1.1.0 · SKILL.md 全面精简 — 指令特异性提升（当前）

**时间**：2026-04-28 ｜ **范围**：SKILL.md 精简重构 + scripts 校验增强 + 新增 references 文件；skill-eval-optimizer 评分从 69.2 提升至 82.8

### SKILL.md 变更

将 SKILL.md 从 ~480 行精简至 ~235 行，核心流程保留可执行骨架，细节下沉至 `references/`。

- **frontmatter 重写**：`description` 精简，新增英文触发词（`create skill`/`new skill`/`skill template`/`skill wizard`），`NOT for` 用箭头格式指向替代 skill
- **Phase 0 重构**：
  - Step 0.1 入口模式表改为「判断标准 + 执行差异」双列结构，IMPROVE 路径明确为「从 Phase 1 开始重走」
  - Step 0.2 七问改为速查摘要，详情指向 `question-bank.md`
  - 原 Step 0.2.5（复用优先诊断）重新编号为 Step 0.3，补充量化判定标准（≥80%/40-80%/<40%）
  - 新增 Step 0.5 边界条件：IMPROVE 需改核心用途时回退 Q1 重采、EXTRACT 缺 ≥3 项降级为 CREATE
- **Phase 1 增强**：
  - Step 1.1 决策树改为 6 条速查规则，新增第 6 条「组合模式」处理规则
  - Step 1.2 新增最小填充规则（4 条）
- **Phase 2 精简**：4 维评分改为精简表格（维度/权重/关注点），通过标准合并为一行
- **Phase 3 扩展**：迭代策略从 3 轮扩展为 5 条规则 + 5 轮上限，新增棘轮机制和结构重组条款
- **Phase 4 补全**：Step 4.3 新增「交付物清单」和「交付摘要模板」
- **Phase 5 补全**：新增 4 条执行步骤
- **Phase 6 新增**：跨 Skill 一致性校验（skill-creator 方案B），含 3 项校验项
- **资源索引精简**：两列（文件/读取时机）替代三列
- **诚实边界精简**：3 条核心约束替代 4 条长描述
- **移除**：快速使用表、核心理念引用块、环境与路径节、异常与边界条件节、约束规则节（已由各 Phase 内联约束覆盖）

### scripts/ 变更

- **validate_skill.py**：
  - 新增 `validate_protocol_contract()` 校验函数，检查 Phase 0-6 标记、Step 1.5/2.5 检查点、交付清单 token、protocol-spec.md / refinement-playbook.md 存在性、question-bank.md 证据契约 token
  - `validate_test_prompts()` 新增覆盖率报告输出（`.validation/test-prompts-coverage.json`）
- **test_prompts_validator.py**：
  - 函数返回值从 `None` 改为 `dict`（含 total_cases / assertion_type_counts / coverage）
  - 新增 `ALLOWED_ASSERTION_TYPES` 白名单校验
  - 新增断言类型计数统计

### README.md 变更

- 工作流概览新增 Phase 6（跨 Skill 一致性）
- 目录结构新增 `protocol-spec.md` 和 `refinement-playbook.md`
- 文件读取时机表新增对应条目

### 新增文件

- `references/protocol-spec.md` — 多阶段协议契约（阶段 I/O、检查点、回退条件）
- `references/refinement-playbook.md` — Phase 5 双评审精炼细则
- `.validation/test-prompts-coverage.json` — 测试用例覆盖率报告（运行时生成）

---

## v1.0.0 · 初始版本

**时间**：2026-04-25 ｜ **范围**：从零构建 Skill 生成器

初始版本，包含：

- 7 问需求消除 + 4 种入口模式（CREATE/EXTRACT/IMPROVE/DIAGNOSE）
- 5 种设计模式（P1-P5）自动匹配 + 组合模式支持
- 4 维度评测闭环（意图完成度/约束遵循/可操作性/对比优势）
- with/without 对比评测 + Dry Run 降级
- 验证脚本 `validate_skill.py` + `test_prompts_validator.py`
- `references/` 下的 5 个参考资料文件
- `templates/` 下的 6 个模式模板文件

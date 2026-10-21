---
name: skill-creator
description: "Skill 生成器：将模糊需求转为可执行的 SKILL.md，通过证据门禁、P1-P5 模式匹配与评测闭环保证质量，含 writing-for-agents 写作质量对齐检查（context pointer 化 description、一分支一触发词、progressive disclosure 分层、每步完成判据、no-op 清除、leading words 选词）。触发词：创建 skill、新建 skill、写 skill 模板、skill 创建向导、设计触发策略、评测方案、create skill、new skill、skill wizard——当用户提出上述诉求时使用。明确指令：/skill-creator（直接触发本 skill，进入 Skill 生成流程）。Do NOT use for: 仅做规范 lint（用 skill linter 工具）、仅做效果优化评分（用 skill-eval-optimizer）。"
allowed-tools:
  - Read
  - Write
  - Edit
  - run_terminal_cmd
---

# Skill Creator

> 核心路径：入口分流 -> 证据采集 -> 模式构建 -> 评测迭代 -> 验证交付。  
> 先读 [references/protocol-spec.md](references/protocol-spec.md)，并严格按 Phase 0-6 执行。
> 本文件是所有输出模板（Checkpoint 1.5/2.5、Phase 0 输出、交付摘要）、安全红线表与脱敏规则表的唯一权威来源，references/ 与 README.md 只引用、不重复维护。
> 路径约定：`SKILL_ROOT` = 本 SKILL.md 所在目录；文中脚本一律以 `"${SKILL_ROOT}/scripts/..."` 调用，禁止裸相对路径。

---

## 工作流

### Phase 0：意图分流与证据门禁

#### Step 0.1：判断入口模式

根据用户输入先分流：

| 模式 | 判断标准 | 执行差异 |
| --- | --- | --- |
| CREATE | 明确新建诉求 | 完整执行 0-6 |
| EXTRACT | 从上下文提炼 | 可跳过 Q1-Q3，缺失项必须追问 |
| IMPROVE | 修改已有 skill | 先读目标 SKILL.md，再走 1-6 |
| DIAGNOSE | 不确定新建还是改 | 先做复用优先诊断 |

#### Step 0.2：按问题库采集需求（7问）

- 强制使用 [references/question-bank.md](references/question-bank.md)
- 产出规格项：`做什么/何时触发/何时不触发/输入/输出/约束/依赖`
- 每个规格项必须写成可执行短句，禁止仅写抽象名词（如“更稳定”“更好用”）

#### Step 0.3：复用优先诊断

- 扫描已安装 skill 目录（存在哪个扫哪个）：`~/.claude/skills/`、`$PWD/.claude/skills/`
- 输出 `复用/改进/新建` 建议并等待用户确认
- 判定阈值：
  - 覆盖 >=80% -> 复用
  - 覆盖 40%-79% -> 改进
  - 覆盖 <40% -> 新建

#### Step 0.4：需求规格确认

必须输出结构化规格并等待确认，未确认不得进入 Phase 1。

#### Step 0.5：证据门禁与置信度

- 必须补齐 E1/E2/E3（见 question-bank 证据块）
- 置信度高：进入 Phase 1
- 置信度中：先补 1 项缺口
- 置信度低：禁止构建

边界规则：
- IMPROVE 且需改核心用途：回退到 Q1 重采
- EXTRACT 缺失 >=3 项：降级为 CREATE

Phase 0 输出模板（可直接复用）：

```markdown
## Phase 0 输出
- 入口模式：{CREATE|EXTRACT|IMPROVE|DIAGNOSE}
- 需求规格：
  - 做什么：{...}
  - 何时触发：{...}
  - 何时不触发：{...}
  - 输入：{...}
  - 输出：{...}
  - 约束：{...}
  - 依赖：{...}
- 证据结论：E1={pass|fail}, E2={pass|fail}, E3={pass|fail}
- 置信度：{高|中|低}
- 下一步：{进入Phase1|补证据后重试}
```

---

### Phase 1：模式选择与草稿生成

#### Step 1.1：匹配设计模式

- 读取 [references/pattern-guide.md](references/pattern-guide.md)
- 选择主模式 P1-P5，可附加 1 个辅助模式
- 超过 2 个模式时必须拆 skill（YAGNI）

#### Step 1.2：生成 SKILL 草稿

- 读取 [references/generation-playbook.md](references/generation-playbook.md)
- 使用 `templates/SKILL.md.template` + 对应 P 模板生成
- 保持正文 <=500 行，超长内容下沉 references
- 删除模板注释与占位符
- 每个步骤至少包含 1 个可执行动作（动词 + 对象 + 产物），例如“读取 X 文件并输出 Y 表格”

#### Step 1.3：安全审计（公开发布红线检查）

生成草稿后，必须对照以下安全红线检查：

| 规则 | 检查内容 | 修复方式 |
| --- | --- | --- |
| **S002** | 禁止硬编码内网 IP/域名（`10.x.x.x`、`172.16-31.x.x`、`*.internal.example.com`） | 改为环境变量 `${ENV_VAR}` + `.env.example` |
| **S003** | 禁止硬编码数据库连接串（`mysql -h IP -P port`、JDBC URL、DSN） | 封装为 CLI 工具或环境变量 |
| **S004** | 破坏性操作（`DELETE`/`DROP`/`TRUNCATE`/`rm -rf`）必须有安全防护声明 | 补充 `❗ 禁止` 或 `⚠️ 需用户确认` 标识 |
| **S001** | 禁止硬编码敏感信息（密钥/Token/私钥） | 移除或改为环境变量 |

**环境变量方案标准化**：

若 skill 涉及连接外部服务（数据库/SSH/API），必须：
1. 在 skill 目录下放置 `.env.example`（含所有配置项的占位符说明）
2. 在 SKILL.md 中添加"前置检查"步骤：检查 `.env` 是否存在
3. `.env` 不存在时，提示用户 `cp .env.example .env` 或用 AskQuestion 询问配置

**敏感数据脱敏（本表为脱敏规则的唯一权威，generation-playbook / skill-creator-pipeline 等仅引用不复制）**：

若 skill 涉及手机号/身份证/地址等敏感信息，必须在输出规则中声明脱敏策略：

| 敏感字段 | 脱敏规则 | 示例 |
| --- | --- | --- |
| 手机号 | 中间 4 位用 `*` 替代 | `138****5678` |
| 身份证号 | 保留前 3 位和后 4 位 | `110***********1234` |
| 地址 | 保留到区/县，详细地址脱敏 | `北京市海淀区****` |
| 姓名 | 保留姓氏，名用 `*` 替代 | `张*` |
| 银行卡号 | 保留前 6 位和后 4 位 | `622202****1234` |
| 邮箱 | 用户名部分脱敏 | `a***@example.com` |

#### Step 1.4：写作质量对齐（writing-for-agents 检查）

生成草稿后，读取 [references/writing-for-agents.md](references/writing-for-agents.md)，逐项过以下检查表（任一不过 → 回改草稿再过，不携带问题进 Phase 2）：

| # | 检查项 | 判据 |
| --- | --- | --- |
| QW1 | description 已 context-pointer 化 | 陈述材料是什么 + 列出触发分支；leading word 前置；同义触发词合并（一分支一触发词）；砍掉正文已承载的 identity |
| QW2 | 信息层级按 progressive disclosure 分层 | 每个分支都需要的内联；只有部分分支触达的下推 references；文档有 steps 时无 in-file reference 埋掉 steps |
| QW3 | 每步有完成判据（completion criterion） | 判据既可核对又穷尽（clarity 防 premature completion，demand 驱动 legwork）；模糊边界锐化为可判定条件 |
| QW4 | no-op 句清除 | 逐句问「相对模型默认它改变行为吗」；不及格删整句而非删词；弱词（be thorough）换强词（relentless） |
| QW5 | leading words 选词 | 优先选预训练强词（red / tight / seam 等）；三元组收敛为单 token；禁令改为正面陈述 |
| QW6 | SSOT 与环境即真源 | 同一意思只在一处定义；环境可查的（package.json/配置/--help）不复述；脱敏规则等引用既有权威源不复制 |

编号说明：QW = 写作质量检查（Quality of Writing），编号空间独立于 skill linter 的 W001-W008（两者语义不同，勿混用）；QW1-QW6 判据唯一权威：[references/writing-for-agents.md](references/writing-for-agents.md)。

#### Step 1.5：Checkpoint（模式与骨架）

- 输出 Checkpoint 1.5 摘要（模板见下方「推荐输出」）
- 用户确认后才能进入 Phase 2

推荐输出：

```markdown
## Checkpoint 1.5
- 入口模式：{...}
- 主模式：P{N}
- 辅助模式：{无|P{N}}
- 是否过度设计：{是|否}
- 关键章节完整性：{pass|fail}
- 安全审计：{pass|fail}（S001/S002/S003/S004 检查结果）
- 写作质量：{pass|fail}（QW1-QW6 检查结果）
- .env.example：{已生成|不需要|待补充}
- 下一步：{进入Phase2|回退修正|安全问题需修复}
```

---

### Phase 2：评测闭环

#### Step 2.1：设计测试 Prompt

- 按 [references/eval-guide.md](references/eval-guide.md) 设计用例
- `test-prompts.json` 必须含 `over-trigger` 与 `under-spec`

#### Step 2.2：执行 with/without 对比评测

- 优先子 agent 实测，不可用则降级 dry_run
- 四维评分（意图完成度/约束遵循/可操作性/对比优势）、权重、通过门槛（30/40 门禁与 over-trigger/under-spec 硬约束）唯一权威：[references/eval-guide.md](references/eval-guide.md)「四维度评分」，此处不重复维护

实测执行规范（强制）：

1. 对每条 `test-prompts.json` 用例执行两次：
   - with_skill：先完整读取目标 SKILL.md 再执行 prompt
   - baseline：不加载目标 SKILL.md，直接执行同一 prompt
2. 两次执行必须使用完全相同的 prompt 文本，不得额外加提示词。
3. 每条用例都要产出可复核结果：
   - `with_skill.md`
   - `baseline.md`
   - `judge.json`（含 winner、reason、四维分项）
4. 若环境受限无法实测，必须标注 `eval_mode: dry_run`，并写清每条用例的路径可达性依据。

`judge.json` 最小结构（建议直接复用）：

```json
{
  "intent_completion": 0,
  "constraint_following": 0,
  "actionability": 0,
  "negative_side_effects": 0,
  "winner": "with_skill",
  "reason": "with_skill 在约束遵循和可操作性上更优"
}
```

#### Step 2.3：展示评测结果

- 输出得分、短板、建议
- 改进建议必须绑定到具体文件和段落，不接受“整体优化”类泛化结论
- 建议措辞按「D5 最小合格线」执行（强制，细则与重写模板唯一出处：[references/eval-guide.md](references/eval-guide.md)「建议措辞规范」）：每条建议含 4 元素（目标维度 + 文件路径 + 改动范围 + 可判定验收标准）；命中模糊词（优化一下/完善下/调整下/提升质量）立即重写为「动作句 + 验收句」

#### Step 2.5：Checkpoint（评测解释）

- 输出 Checkpoint 2.5 摘要（模板见下方「推荐输出」）
- 用户确认后进入 Phase 3

推荐输出：

```markdown
## Checkpoint 2.5
- eval_mode：{subagent|dry_run}
- 总分：{score}/40
- 最低维度：{...}
- 失败断言：{case_id + assertion_type}
- 下一轮仅改动：{一个维度}
```

---

### Phase 3：迭代优化

- 聚焦最低维度做单点优化
- 每轮改动后重评；无收益则回滚

迭代规则：
1. 每轮只改一个维度
2. 新分 > 旧分才保留（棘轮）
3. 新分 <= 旧分回滚并切换目标维度
4. 连续 2 轮无收益，提议结构重组
5. 上限 5 轮，触顶进入 Phase 4

每轮输出模板：

```markdown
## Phase 3 迭代轮次 {n}
- 目标维度：{...}
- 改动范围：{具体文件/段落}
- 重评得分：{new_score}/40（旧分 {old_score}/40）
- 判定：{保留|回滚}
- 下一步：{下一轮目标或进入Phase4}
```

---

### Phase 4：验证与交付

#### Step 4.1：自动验证

```bash
python3 "${SKILL_ROOT}/scripts/validate_skill.py" <skill-path>
```

#### Step 4.2：手动检查

- 使用 [references/compliance-checklist.md](references/compliance-checklist.md)

#### Step 4.3：交付确认

- 用户确认内容、评分、脚本结果与文件结构

## 交付清单

交付物清单：
- [ ] `{skill-name}/SKILL.md`
- [ ] `{skill-name}/README.md`
- [ ] `{skill-name}/test-prompts.json`
- [ ] `{skill-name}/.env.example` — 环境配置模板（涉及外部服务连接时必须）
- [ ] `references/` — 下沉的参考资料（如有）
- [ ] `scripts/` — 验证脚本（如有）

交付摘要模板：
```
Skill: {name}
模式: P{N}（{模式名}）
验证: PASS/FAIL
评测: {score}/40
```

---

### Phase 5：后置精炼（可选）

- 读取 [references/refinement-playbook.md](references/refinement-playbook.md)
- 双评审仅接受可归因、可验证改动
- 每轮最多合并 3 条改动
- 改后必须重跑验证

### Phase 6：跨 Skill 一致性校验

- 校验 `skill-creator` 与 `skill-creator-pipeline` 的 test-prompts 协议一致
- 完成一致性报告后再交付

校验项：
1. `test-prompts.json` 的 schema 与断言类型以 `"${SKILL_ROOT}/scripts/test_prompts_validator.py"` 为唯一权威（含 over-trigger 与 under-spec 用例要求），对目标 skill 运行校验比对一致性——本协议与 skill-creator-pipeline 共用，不在本文件重复 schema 细节
2. 运行 `python3 "${SKILL_ROOT}/scripts/validate_skill.py" <skill-path>` 并检查覆盖报告

---

## 资源索引

| 文件 | 读取时机 |
| --- | --- |
| [references/protocol-spec.md](references/protocol-spec.md) | 进入流程前 |
| [references/question-bank.md](references/question-bank.md) | Phase 0 |
| [references/pattern-guide.md](references/pattern-guide.md) | Phase 1.1 |
| [references/generation-playbook.md](references/generation-playbook.md) | Phase 1.2 |
| [references/writing-for-agents.md](references/writing-for-agents.md) | Phase 1.4（共享权威源，skill-creator-pipeline 同引此文件） |
| [references/eval-guide.md](references/eval-guide.md) | Phase 2 |
| [references/refinement-playbook.md](references/refinement-playbook.md) | Phase 5 |
| [references/compliance-checklist.md](references/compliance-checklist.md) | Phase 4.2 |
| [scripts/validate_skill.py](scripts/validate_skill.py) | Phase 4.1 |

## 异常处理

- 证据缺失：停止生成，回到 Phase 0.5 补齐 E1/E2/E3。
- 评测失败：回到 Phase 3 做单维度优化，不允许多点同时改。
- 环境受限：标记 `dry_run` 并说明未覆盖风险。

## 诚实边界

- 信息不足时不生成最终版，先追问补齐证据。
- 无法实测时必须标记 `dry_run` 并说明风险。
- 复杂复合需求优先拆分多 skill，不强行单 skill 承载。

# 评测方法指南

> 读取时机：Phase 2 评测环节。
>
> 核心思想（三篇文献精髓）：
> - Anthropic：skill 是可迭代资产，draft → eval → improve → repeat
> - OpenAI：系统评测 = with_skill vs without_skill 对比 + 断言驱动
> - Google：评测要覆盖功能正确性、输出格式、边界条件、安全性

---

## 评测流程

### 1. 设计测试 Prompt

为每个 skill 设计 3-5 个测试 prompt，覆盖五种场景：

| 类型 | 目的 | 设计原则 |
|------|------|---------|
| **happy path** | 验证主流程 | 用户最典型的使用场景 |
| **边界场景** | 验证异常处理 | 缺少输入、格式错误、极端值 |
| **歧义场景** | 验证不 over-trigger | 相似但不应触发的输入 |
| **over-trigger 场景** | 验证应拒绝触发 | 输入与 skill 部分相似，但本质属于其他 skill |
| **under-spec 场景** | 验证先追问再执行 | 缺关键参数时，必须先补齐信息 |

**Prompt 设计原则**：
- 使用用户真实会说的话，不是抽象描述
- 包含足够的上下文信息（文件路径、具体数据等）
- 每个 prompt 应该足够复杂，简单查询 agent 不需要 skill 也能处理
- `over-trigger` 用例必须有明确“应拒绝/应转路由”期望
- `under-spec` 用例必须有明确“应先追问”期望

---

### 2. 编写断言

断言是客观可验证的检查项，每个测试 prompt 应有 2-4 条断言。

**断言类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| `contains` | 输出必须包含指定内容 | SQL 中包含 CREATE TABLE |
| `not_contains` | 输出不得包含指定内容 | 不包含 DROP TABLE |
| `format` | 输出格式检查 | 输出是合法的 SQL / JSON / Markdown |
| `schema` | 输出结构检查 | 包含指定的章节/字段 |
| `count` | 数量检查 | 至少包含 3 个字段 |
| `no_error` | 无报错信息 | 不包含 error、failed 等字样 |
| `ask_before_act` | 缺参时必须先追问 | 输出中先出现补参问题，而非直接结果 |
| `route_reject` | 不应触发本 skill | 明确拒绝并建议更合适路径/skill |

**断言写入 test-prompts.json**：

```json
{
  "skill_name": "your-skill-name",
  "test_prompts": [
    {
      "id": "happy-1",
      "prompt": "帮我建一个用户表，包含用户名、手机号、注册时间",
      "expected": "生成包含 id/username/phone/ctime/utime 字段的建表 SQL",
      "assertions": [
        {"type": "contains", "value": "CREATE TABLE"},
        {"type": "contains", "value": "username"},
        {"type": "not_contains", "value": "DROP"},
        {"type": "format", "value": "sql"},
        {"type": "ask_before_act", "value": "缺关键字段时先追问"}
      ]
    }
  ]
}
```

---

### 3. 执行对比评测

对每个测试 prompt，执行两组运行：

**with_skill**：子 agent 加载 SKILL.md 后执行 prompt
**without_skill（baseline）**：子 agent 不加载 skill 直接执行

两组应并行执行，确保时间差小于 30 分钟。

---

### 4. 四维度评分

| 维度 | 权重 | 1-3 分 | 4-6 分 | 7-10 分 |
|------|------|--------|--------|---------|
| 意图完成度 | 30% | 缺失主要功能 | 部分完成 | 完整达成 |
| 约束遵循 | 25% | 多处违规 | 偶有违规 | 严格遵循 |
| 可操作性 | 25% | 输出不可用 | 需要微调 | 直接可用 |
| 对比优势 | 20% | 不如 baseline | 持平 | 明显优于 |

**通过标准**：
- 总分大于等于 30/40 → PASS
- 总分 20-29 → 需改进
- 总分小于 20 → 需重写

**门槛补充**（硬约束）：
- 至少包含 1 个 `over-trigger` 用例；
- 至少包含 1 个 `under-spec` 用例；
- 若 `over-trigger` 或 `under-spec` 任一失败，最高判定为“需改进”。

---

### 5. Dry Run 评测

当子 agent 不可用时，降级为 dry_run：

对每个 prompt 的代码路径做可达性分析：
- 完整可执行（每步有明确指令）→ 8-10 分
- 部分路径模糊（缺 1-2 步具体指令）→ 5-7 分
- 缺处理路径或指令矛盾 → 1-4 分

必须标注 eval_mode: dry_run。

---

## Checkpoint 2.5 输出要求（强制）

每次评测后必须输出 Checkpoint 2.5 摘要（模板以 SKILL.md Step 2.5 为唯一权威来源），再进入 Phase 3。

---

## 可复制样例库

> 目的：降低 test-prompts 设计成本，避免只写 happy path。

### A. over-trigger 样例

```json
{
  "id": "over-trigger-1",
  "prompt": "帮我查一下这个接口最近报错日志，顺便给我写个修复方案。",
  "expected": "应拒绝触发当前 skill，并建议更合适的日志排查或调试 skill。",
  "assertions": [
    { "type": "route_reject", "value": "不属于当前 skill 触发范围" },
    { "type": "contains", "value": "建议使用" }
  ]
}
```

### B. under-spec 样例

```json
{
  "id": "under-spec-1",
  "prompt": "帮我生成一个 skill。",
  "expected": "先追问核心输入（做什么、触发条件、输出、约束）后再进入生成流程。",
  "assertions": [
    { "type": "ask_before_act", "value": "先补齐关键信息" },
    { "type": "contains", "value": "请先确认" }
  ]
}
```

### C. happy path 样例

```json
{
  "id": "happy-1",
  "prompt": "帮我创建一个根据中文描述生成 MySQL 建表 SQL 的 skill，要求输出 SQL 且禁止 DROP。",
  "expected": "按既定流程完成需求确认、模式选择、模板生成、评测建议。",
  "assertions": [
    { "type": "contains", "value": "需求规格" },
    { "type": "contains", "value": "模式匹配" },
    { "type": "not_contains", "value": "DROP TABLE" }
  ]
}
```

### D. 从现有 skill 抽取样例的方法

1. 读取目标 skill 下的 `test-prompts.json`（例如 `code-review/test-prompts.json`）；
2. 抽取至少 1 条“模糊输入”样例改写为 `under-spec`；
3. 抽取至少 1 条“越界请求”样例改写为 `over-trigger`；
4. 保留 1 条完整业务链路样例作为 `happy path`；
5. 确保三类样例都带可判定断言，避免“看起来合理”但不可验证。

---

## 建议措辞规范（Step 2.3 强制）

> 唯一出处。SKILL.md Step 2.3 引用本节执行，不重复维护。

### 指令具体化清单（执行时强制替换）

- 把“完善一下/优化一下”替换为“指出目标维度 + 改动文件 + 改动范围”。
- 把“处理异常”替换为“列出失败场景 + 回退动作 + 终止条件”。
- 把“补充测试”替换为“新增/修改哪些 `test-prompts.json` 用例及断言类型”。
- 把“结果更好”替换为“给出新旧分数对比与保留/回滚判定”。

### D5 指令具体性最小合格线

1. 每条改进建议必须包含 4 元素：`目标维度 + 文件路径 + 改动范围 + 验收标准`
2. 验收标准必须可判定：出现“包含/不包含/通过阈值/分数提升”等字样
3. 禁止使用以下模糊词作为结论：`优化一下`、`完善下`、`调整下`、`提升质量`
4. 若检测到模糊词，必须立即重写为“动作句 + 验收句”

### 模糊词重写模板（直接套用）

- 模糊：`优化一下流程`
  - 重写：`将 Step 2.3 改为“输出 D5 改进建议表（文件/段落/验收标准）”，并在评测结果中展示。`
- 模糊：`补充边界条件`
  - 重写：`在 Phase 0.5 新增“低置信度禁止构建”失败分支，并补充回退动作与终止条件。`
- 模糊：`增强可操作性`
  - 重写：`把“建议改进”替换为“修改 {file} 的 {section}，新增 {assertion_type} 用例并要求分数 >=30/40”。`

---

## 评测反模式

### "只看结构不看效果"

只检查 SKILL.md 写得规不规范，不跑测试验证实际效果。

修复：必须执行 with_skill vs without_skill 对比（至少 dry_run）。

### "断言太弱"

所有断言都是 contains，没有 not_contains 和 format。

修复：每条 happy path 至少 1 条 not_contains，1 条 format。

### "baseline 不公平"

baseline prompt 加了额外限制或引导，导致对比失真。

修复：with_skill 和 without_skill 使用完全相同的 prompt 文本。

### "一次改多处"

评测发现 3 个问题，同时改 3 处。无法归因哪个改动有效。

修复：每轮只改一个维度，改后重评，确保可归因。

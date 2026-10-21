<div align="center">

# 🏭 skill-creator

### 把模糊需求变成可执行的 SKILL.md —— 证据门禁、模式匹配、评测闭环。

一个 agent skill：内置 7 阶段流程与 2 个硬性检查点——证据不足时拒绝生成，按任务匹配 5 种设计模式之一，评分、迭代、验证全部通过后才允许交付。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![版本](https://img.shields.io/badge/version-v1.2.2-green?style=flat-square)](CHANGELOG.md)
[![自验证](https://img.shields.io/badge/self--validation-0%20errors%20%2F%200%20warnings-brightgreen?style=flat-square)](.validation/validate-summary.json)
[![评测得分](https://img.shields.io/badge/skill--eval--optimizer-89.0%2F100-orange?style=flat-square)](#-实践验证)
[![模式模板](https://img.shields.io/badge/pattern%20templates-P1--P5-purple?style=flat-square)](templates/)

[快速开始](#-快速开始) · [核心能力](#-核心能力) · [实践验证](#-实践验证) · [与 skill-creator-pipeline 的关系](#-与-skill-creator-pipeline-的关系) · [目录结构](#-目录结构) · [边界](#%EF%B8%8F-什么时候别用它) · [English](README.md)

</div>

---

## 😩 你的 AI 是不是也这样？

让 agent「写个 skill」，结果拿到的是：

- 读起来很美但**无法验证**的 SKILL.md——没测试、没门禁，全凭手感
- 触发词要么窄到**永远不触发**，要么宽到什么都触发
- 改了五轮，**说不清哪一轮改动起了作用**
- 一个 900 行的万能 skill，什么都想做，什么都做不稳

skill-creator 用流程而不是天赋解决这些问题：先证据后生成、一个 skill 一个模式、一次只改一个维度、验证通过才交付。

## 🚀 快速开始

**第 1 步 — 安装：**

```bash
npx skills add anthonyhann/skill-creator
```

**第 2 步 — 触发。** 对你的 agent 说：

> 「帮我创建一个根据中文描述生成 MySQL 建表 SQL 的 skill，禁止 DROP。」

或直接输入指令：`/skill-creator`

**第 3 步 — 跟随检查点。** 在 Checkpoint 1.5 确认需求规格，在 Checkpoint 2.5 查看评测得分，Phase 4 收到通过验证的 skill 交付包。

**给 AI Agent 的安装口令**（把这句话贴给你的 agent）：

> 安装 https://github.com/anthonyhann/skill-creator 这个 skill，之后我让你创建、提炼或改进 agent skill 时都使用它。

兼容所有能加载 `SKILL.md` 的 agent 运行时（Claude Code、skills.sh 生态安装器等）。

## ✨ 核心能力

| 能力 | 你得到什么 |
|---|---|
| **🧭 证据门禁（Phase 0）** | 7 问需求采集 + 复用优先诊断 + E1/E2/E3 证据项。置信度低 = **拒绝生成**，先追问补齐 |
| **🧩 P1–P5 模式库** | 5 种设计模式（工具调用/路由分发/流程编排/状态机/护栏）+ 决策树 + 反模式 + 现成模板；规则强制 1 主 + 至多 1 辅 |
| **✍️ 写作质量对齐** | 6 项 writing-for-agents 检查（QW1–QW6）：description context-pointer 化、progressive disclosure 分层、每步完成判据、no-op 句清除、leading words 选词、SSOT |
| **📊 评测闭环（Phase 2–3）** | with/without 对比评测、4 维度评分 + 30/40 门禁、强制 over-trigger 与 under-spec 用例、棘轮迭代——每轮只改一个维度，无收益即回滚 |
| **🔍 可独立运行的验证器** | `validate_skill.py` + `test_prompts_validator.py`：frontmatter、结构、敏感信息扫描、引用可达性、协议 token——机器可判定的 PASS/FAIL |

**触发对照表**（来自 frontmatter，即真实契约）：

| 你说… | 它做… |
|---|---|
| 「帮我创建一个 XXX skill」/ "create a skill" | 完整 Phase 0→4 流程 |
| 「把刚才的操作变成 skill」 | EXTRACT 模式，跳过部分问答 |
| 「帮我改进这个 skill」 | IMPROVE 模式，先读后改 |
| 「该新建还是复用？」 | DIAGNOSE 模式，覆盖率量化建议 |
| 「帮我 lint 一下这个 SKILL.md」 | ❌ 拒绝——路由你去用 skill linter |
| 「给我的 skill 打分优化」 | ❌ 拒绝——那是 [skill-eval-optimizer](https://github.com/anthonyhann/skill-eval-optimizer) 的活 |

## 📊 实践验证

以下数字全部来自生产实践，不是营销文案：

- **被 [skill-eval-optimizer](https://github.com/anthonyhann/skill-eval-optimizer) 评测优化 3 轮：86.5 → 89.0（/100，8 个维度）**——这个 skill 自己就是吃自己狗粮长大的
- **自验证闭环：0 errors / 0 warnings**——`scripts/validate_skill.py` 对本仓库自身运行的结果，证据提交在 [`.validation/validate-summary.json`](.validation/validate-summary.json)
- **版本演进：v1.0 → v1.2.2**——每一代改了什么、为什么改，见 [CHANGELOG.md](CHANGELOG.md)
- **所属生产实践 fleet：** 2026-04 至 2026-10 六个月内，**49 个生产级 agent skills 共记录 342 条优化数据**；其中 44 个有完整基线，**40 个实现提升，平均 +9.9 分**

## 🔗 与 skill-creator-pipeline 的关系

两个仓库，一套系统：

| | **skill-creator**（本仓库） | [skill-creator-pipeline](https://github.com/anthonyhann/skill-creator-pipeline) |
|---|---|---|
| 角色 | **生成引擎** | **编排层** |
| 提供 | P1–P5 模板、写作规则、验证器、评测协议 | 5 阶段 / 4 门禁的流程编排 |
| 读起来像 | 一间工坊 | 一条流水线 |

pipeline 在编排中调用本引擎完成实际生成；本仓库的 `references/writing-for-agents.md` 是两侧共同引用的写作权威源。需要端到端交付编排？去 pipeline。需要生成机制本身？就是这里。

## 📁 目录结构

```text
skill-creator/
├── SKILL.md                        # 主入口：7 阶段协议、安全红线、检查点模板
├── README.md / README_zh.md        # English 版 / 本文件
├── CHANGELOG.md                    # 版本演进 v1.0 → v1.2.2
├── references/                     # 8 份深度参考（progressive disclosure 下沉）
│   ├── protocol-spec.md            # 阶段契约、输入输出、回退条件
│   ├── question-bank.md            # 7 问采集 + 证据契约（E1/E2/E3）
│   ├── pattern-guide.md            # P1–P5 决策树 + 反模式
│   ├── generation-playbook.md      # 模板填充规则 + 安全生成规则
│   ├── writing-for-agents.md       # 写作质量权威源（QW1–QW6 出处）
│   ├── eval-guide.md               # 4 维评分、断言类型、dry-run 降级
│   ├── refinement-playbook.md      # Phase 5 双评审精炼
│   └── compliance-checklist.md     # Phase 4 手动检查清单（A–F）
├── templates/                      # SKILL.md 骨架模板 + P1–P5 模式模板
├── scripts/
│   ├── validate_skill.py           # 结构验证器（可对任意 skill 目录独立运行）
│   ├── test_prompts_validator.py   # test-prompts.json schema 与覆盖校验
│   └── run-claude.sh               # 评测执行 wrapper（认证失效防护 + 退避重试）
├── evals/                          # 7 个 skill-up 评测用例（happy/诊断/越界/缺参/写作门禁）
├── test-prompts.json               # 7 条自测 prompt（带断言）
└── .validation/                    # 自验证证据（0 errors / 0 warnings）
```

## ⚠️ 什么时候别用它

- **只想给已有 SKILL.md 做格式/规范检查** → 去用 skill linter；本 skill 会拒绝并把你路由过去（这是被评测覆盖的行为，见 `evals/cases/p3-over-trigger-lint.yaml`）
- **只想给已有 skill 打分、做效果优化** → 去用 [skill-eval-optimizer](https://github.com/anthonyhann/skill-eval-optimizer)
- **只想要一次性 prompt、不打算维护**——这套流程是为可迭代的 skill 资产准备的，一次性 prompt 不需要证据门禁
- **复杂复合需求**——本 skill 会拆成多个 skill，而不是硬塞一个万能 skill（YAGNI 是强制的，不是建议）

## ⭐ 为什么值得 Star

如果你需要维护 agent skills，点个 star——模式库和 `writing-for-agents.md` 值得在每次给模型写指令时重读，更新会持续进入 [CHANGELOG.md](CHANGELOG.md)。

## License

MIT © [anthonyhann](https://github.com/anthonyhann) — 详见 [LICENSE](LICENSE)。

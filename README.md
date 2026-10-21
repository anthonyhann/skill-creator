<div align="center">

# 🏭 skill-creator

### Turn vague requirements into executable SKILL.md — evidence-gated, pattern-matched, eval-looped.

An agent skill that runs a 7-phase pipeline with 2 hard checkpoints: it refuses to generate on low evidence, matches your task to 1 of 5 design patterns, then scores, iterates and validates before anything ships.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.2.2-green?style=flat-square)](CHANGELOG.md)
[![Self-validation](https://img.shields.io/badge/self--validation-0%20errors%20%2F%200%20warnings-brightgreen?style=flat-square)](.validation/validate-summary.json)
[![Eval score](https://img.shields.io/badge/skill--eval--optimizer-89.0%2F100-orange?style=flat-square)](#-real-world-usage)
[![Patterns](https://img.shields.io/badge/pattern%20templates-P1--P5-purple?style=flat-square)](templates/)

[Quickstart](#-quickstart) · [Core Capabilities](#-core-capabilities) · [Real-World Usage](#-real-world-usage) · [vs skill-creator-pipeline](#-vs-skill-creator-pipeline) · [Directory](#-directory-structure) · [Boundaries](#%EF%B8%8F-when-not-to-use-it) · [中文](README_zh.md)

</div>

---

## 😩 Sound familiar?

You asked your agent to "write a skill" and got:

- A SKILL.md that reads nice but **nobody can verify** — no tests, no gate, vibes only
- Trigger words so narrow the skill **never fires**, or so broad it fires on everything
- Five rounds of "improvements" and **no way to tell which change helped**
- A 900-line mega-skill that tries to do everything and does nothing reliably

skill-creator fixes this with process, not talent: evidence before generation, one pattern per skill, one dimension per iteration, validation before delivery.

## 🚀 Quickstart

**Step 1 — Install:**

```bash
npx skills add anthonyhann/skill-creator
```

**Step 2 — Trigger it.** Say to your agent:

> "Create a skill that generates MySQL DDL from Chinese table descriptions, DROP forbidden."

or invoke directly: `/skill-creator`

**Step 3 — Follow the checkpoints.** Confirm the spec at Checkpoint 1.5, review eval scores at Checkpoint 2.5, receive a validated skill package at Phase 4.

**For AI Agents** (paste this to your agent):

> Install the skill from https://github.com/anthonyhann/skill-creator and use it whenever I ask you to create, extract, or improve an agent skill.

Works with any agent runtime that loads `SKILL.md` (Claude Code, skills.sh-compatible installers, and friends).

## ✨ Core Capabilities

| Capability | What you get |
|---|---|
| **🧭 Evidence gate (Phase 0)** | 7-question spec intake + reuse-first diagnosis + E1/E2/E3 evidence items. Low confidence = **generation refused**, questions asked instead |
| **🧩 P1–P5 pattern library** | 5 design patterns (tool-call / router / orchestrator / state-machine / guardrail) with decision tree, anti-patterns and ready templates — 1 primary + at most 1 auxiliary, forced by rule |
| **✍️ Writing-quality alignment** | 6 writing-for-agents checks (QW1–QW6): context-pointer descriptions, progressive disclosure, completion criteria per step, no-op sentence elimination, leading words, SSOT |
| **📊 Eval loop (Phase 2–3)** | with/without-skill A/B, 4-dimension scoring with a 30/40 gate, mandatory over-trigger + under-spec cases, ratchet iteration — one dimension per round, rollback on no gain |
| **🔍 Validators that run anywhere** | `validate_skill.py` + `test_prompts_validator.py`: frontmatter, structure, secrets scan, reference reachability, protocol tokens — machine-checkable PASS/FAIL |

**Trigger map** (from the frontmatter — the actual contract):

| You say… | It does |
|---|---|
| "Create a skill / 帮我创建一个 skill" | Full Phase 0→4 pipeline |
| "Turn what we just did into a skill" | EXTRACT mode, fewer questions |
| "Improve this existing skill" | IMPROVE mode, reads then iterates |
| "Should I build new or reuse?" | DIAGNOSE mode, coverage-scored recommendation |
| "Just lint my SKILL.md" | ❌ Refuses — routes you to a skill linter |
| "Score and optimize my skill" | ❌ Refuses — that's [skill-eval-optimizer](https://github.com/anthonyhann/skill-eval-optimizer)'s job |

## 📊 Real-World Usage

Numbers below are from production use, not marketing:

- **Evaluated and optimized 3 rounds by [skill-eval-optimizer](https://github.com/anthonyhann/skill-eval-optimizer): 86.5 → 89.0 /100** across 8 dimensions — the skill eats its own cooking
- **Self-validation loop: 0 errors / 0 warnings** — `scripts/validate_skill.py` runs against this very repo; the evidence is committed at [`.validation/validate-summary.json`](.validation/validate-summary.json)
- **Version evolution: v1.0 → v1.2.2** — see [CHANGELOG.md](CHANGELOG.md) for what each generation changed and why
- **From a production fleet:** between 2026-04 and 2026-10, **49 production-grade agent skills logged 342 optimization records**; of the 44 with complete baselines, **40 improved, averaging +9.9 points**

## 🔗 vs skill-creator-pipeline

Two repos, one system:

| | **skill-creator** (this repo) | [skill-creator-pipeline](https://github.com/anthonyhann/skill-creator-pipeline) |
|---|---|---|
| Role | **Generation engine** | **Orchestration layer** |
| Provides | P1–P5 templates, writing rules, validators, eval protocol | 5-stage / 4-gate pipeline orchestration |
| Reads like | A workshop | An assembly line |

The pipeline calls this engine to do the actual generation; this repo's `references/writing-for-agents.md` is the shared writing authority both sides reference. Need end-to-end delivery orchestration? Use the pipeline. Need the generation machinery itself? You're here.

## 📁 Directory Structure

```text
skill-creator/
├── SKILL.md                        # Main entry: 7-phase protocol, red lines, checklists
├── README.md / README_zh.md        # This file / 中文版本
├── CHANGELOG.md                    # Version history v1.0 → v1.2.2
├── references/                     # 8 deep-dive references (progressive disclosure)
│   ├── protocol-spec.md            # Phase contracts, I/O, fallback conditions
│   ├── question-bank.md            # 7-question intake + evidence contract (E1/E2/E3)
│   ├── pattern-guide.md            # P1–P5 decision tree + anti-patterns
│   ├── generation-playbook.md      # Template filling rules + safety generation rules
│   ├── writing-for-agents.md       # Writing-quality authority (QW1–QW6 source)
│   ├── eval-guide.md               # 4-dimension scoring, assertion types, dry-run
│   ├── refinement-playbook.md      # Phase 5 dual-review refinement
│   └── compliance-checklist.md     # Phase 4 manual checklist (A–F)
├── templates/                      # SKILL.md skeleton + P1–P5 pattern templates
├── scripts/
│   ├── validate_skill.py           # Structure validator (runs standalone on any skill)
│   ├── test_prompts_validator.py   # test-prompts.json schema + coverage checks
│   └── run-claude.sh               # Eval engine wrapper (auth-failure guard + retries)
├── evals/                          # 7 skill-up eval cases (happy / diagnose / over-trigger / under-spec / QW gates)
├── test-prompts.json               # 7 self-test prompts with assertions
└── .validation/                    # Self-validation evidence (0 errors / 0 warnings)
```

## ⚠️ When NOT to use it

- **You only want a format/lint check** on an existing SKILL.md → use a skill linter; this skill will refuse and route you away (that's a tested behavior, see `evals/cases/p3-over-trigger-lint.yaml`)
- **You only want to score and optimize an existing skill** → use [skill-eval-optimizer](https://github.com/anthonyhann/skill-eval-optimizer)
- **You want a one-shot prompt, not a maintained asset** — this pipeline exists for skills you'll iterate on; a throwaway prompt doesn't need evidence gates
- **Complex compound needs** — the skill splits them into multiple skills rather than forcing one mega-skill (YAGNI is enforced, not suggested)

## ⭐ Why star

If you maintain agent skills, star this repo — the pattern library and `writing-for-agents.md` are worth re-reading every time you write instructions for a model, and updates land in [CHANGELOG.md](CHANGELOG.md).

## License

MIT © [anthonyhann](https://github.com/anthonyhann) — see [LICENSE](LICENSE).

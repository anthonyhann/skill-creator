# 生成执行手册（Generation Playbook）

> 读取时机：Phase 1.2。  
> 目标：让 SKILL 草稿“可执行、可验证、可维护”。

## 填充顺序

1. 先填 frontmatter（WHAT/CAPABILITY/TRIGGERS/SLASH_CMD/NOT）
2. 再填主模式模板（P1-P5）
3. 如需组合，嵌入 1 个辅助模式
4. 最后补齐异常、诚实边界、资源索引

## frontmatter 规则

- `name` 必须 kebab-case，且与目录名一致
- `description` 结构：
  - WHAT：一句话描述核心能力
  - CAPABILITY：补充说明核心能力和支持范围
  - TRIGGERS：逗号分隔的触发关键词，合并了原 WHEN，含口语表达、中英文、缩写、系统名词、命令斜杠
  - SLASH_CMD：明确指令，/xxx 格式，说明直接触发时的行为
  - NOT：不触发的场景，用顿号分隔
- TRIGGERS 必须覆盖口语和英文变体，避免 under-trigger

## 模板映射

| 场景特征 | 主模式 | 模板 |
| --- | --- | --- |
| 单工具线性调用 | P1 | [`../templates/p1-tool-call.md`](../templates/p1-tool-call.md) |
| 多互斥分支 | P2 | [`../templates/p2-router.md`](../templates/p2-router.md) |
| 多步骤有依赖 | P3 | [`../templates/p3-orchestrator.md`](../templates/p3-orchestrator.md) |
| 明确状态流转 | P4 | [`../templates/p4-state-machine.md`](../templates/p4-state-machine.md) |
| 合规/格式强约束 | P5 | [`../templates/p5-guardrail.md`](../templates/p5-guardrail.md) |

## 组合模式规则

- 只允许 `1 主 + 1 辅`
- 辅助模式只嵌入主模式某一步，不重建第二套主流程
- 若需要第三种模式，必须拆 skill

## 最小可执行清单

生成后必须满足：
- 输入定义完整（必填/可选）
- 输出模板唯一且可复制
- 至少一个异常分支有明确 fallback
- 包含 `## 诚实边界`
- 资源索引给出"何时读取"
- **安全红线检查通过**（S001/S002/S003/S004）

## 安全生成规则（公开发布强制）

规范与判定（S001-S004 红线表、环境变量方案、脱敏规则表）唯一权威：[SKILL.md](../SKILL.md) Step 1.3；本节仅保留生成时的对照示例与 .env.example 模板，不重复规范文本。

### 规则 1：外部服务连接必须环境变量化

若 skill 涉及数据库/SSH/API 等外部连接：

```
❌ 错误写法：
Host: 10.x.x.x:3306
ssh user@172.x.x.x

✅ 正确写法：
Host: ${TESTER_DB_HOST}:${TESTER_DB_PORT}
ssh ${SSH_USER}@${SSH_HOST}
```

同时生成 `.env.example` 并在 SKILL.md 中增加「前置检查」步骤（细则见 SKILL.md Step 1.3「环境变量方案标准化」）。

### 规则 2：破坏性操作必须有安全防护

```
❌ 错误写法：
执行 DELETE FROM orders WHERE ...

✅ 正确写法：
❗ 禁止执行 DELETE/DROP/TRUNCATE 操作。
若确需修改数据，必须先展示 SQL 并等待用户确认。
```

### 规则 3：敏感数据输出必须脱敏（格式表唯一权威：SKILL.md Step 1.3）

```
❌ 错误写法：
手机号: 13812345678

✅ 正确写法：
手机号: 138****5678
```

### 规则 4：.env.example 模板格式

```bash
# {skill-name} 环境配置
# 使用前请复制本文件为 .env 并填写真实值：
#   cp .env.example .env
#
# {配置分组说明}
VAR_NAME=<占位说明，如"数据库IP地址">
```

## 常见失败修正

| 失败类型 | 典型信号 | 修正动作 |
| --- | --- | --- |
| 模式错配 | 路由与状态混写 | 重新判定主模式 |
| 描述过窄 | 触发覆盖低 | 增补口语触发词 |
| 异常空洞 | 只有"处理错误" | 改成可执行 fallback |
| 结构膨胀 | >500 行 | 下沉到 references |
| 🔴 内网地址暴露 | 硬编码 IP/域名 | 改为 `${ENV_VAR}` + `.env.example` |
| 🔴 连接串暴露 | 明文 DSN/JDBC | 封装 CLI 或环境变量 |
| 🔴 破坏性操作无防护 | DELETE/DROP 无确认 | 补充安全声明 + 用户确认 |
| ⚠️ 敏感数据暴露 | 明文手机号/地址 | 补充脱敏规则 |

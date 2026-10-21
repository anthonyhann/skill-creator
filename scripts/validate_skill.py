#!/usr/bin/env python3
"""
validate_skill.py — Skill 结构验证器

Usage:
    python3 validate_skill.py <path/to/skill-directory/>

Exit codes:
    0 = PASS (无错误，可能有警告)
    1 = FAIL (存在错误)
    2 = USAGE 错误 (参数错误等)

检查项:
    - SKILL.md 存在且 frontmatter 合法
    - name 为 kebab-case 且与目录名一致
    - description 不超过 500 字符且包含 WHEN/NOT 条件
    - 正文有必需章节（含诚实边界）
    - references/ 引用的文件路径可达
    - 无硬编码敏感信息
"""

from __future__ import annotations

import sys
import re
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from test_prompts_validator import validate_test_prompts_file

try:
    import yaml
except ImportError:
    print("[USAGE ERROR] PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, file: str, msg: str) -> None:
        self.errors.append(f"  [ERROR] {file}: {msg}")

    def warn(self, file: str, msg: str) -> None:
        self.warnings.append(f"  [WARN]  {file}: {msg}")

    def passed(self) -> bool:
        return not self.errors

    def print(self) -> None:
        if self.errors:
            print("\nERRORS:")
            for e in self.errors:
                print(e)
        if self.warnings:
            print("\nWARNINGS:")
            for w in self.warnings:
                print(w)
        if self.passed():
            print(f"\n[PASS] {len(self.warnings)} warning(s), 0 error(s).")
        else:
            print(f"\n[FAIL] {len(self.errors)} error(s), {len(self.warnings)} warning(s).")

    def to_dict(self) -> dict[str, Any]:
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "passed": self.passed(),
        }


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Split a Markdown file into (frontmatter_dict, body_str)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"frontmatter YAML parse error: {e}") from e
    return fm, m.group(2)


def find_h2_sections(body: str) -> dict[str, int]:
    """Return mapping of ## Section Title -> line number (1-indexed)."""
    sections: dict[str, int] = {}
    for i, line in enumerate(body.splitlines(), 1):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            sections[m.group(1).strip()] = i
    return sections


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

# Sensitive information patterns
# 验证阈值常量
MAX_NAME_LENGTH = 64       # name 字段最大字符数
MAX_DESC_LENGTH = 500      # description 最大字符数
MAX_SKILL_LINES = 500      # SKILL.md 推荐最大行数

SENSITIVE_PATTERNS = [
    (r'(?:password|passwd|pwd|secret|token|api_key|apikey)\s*[:=]\s*["\']?[^\s"\'<>{},]+', "疑似硬编码密钥/Token"),
    (r'(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}', "疑似内网 IP 地址"),
]


def validate_skill_md(path: Path, report: Report) -> dict[str, Any] | None:
    """Validate SKILL.md. Returns frontmatter dict or None."""
    if not path.exists():
        report.err("SKILL.md", "missing — required file")
        return None

    text = path.read_text(encoding="utf-8")

    try:
        fm, body = split_frontmatter(text)
    except ValueError as e:
        report.err("SKILL.md", str(e))
        return None

    if fm is None:
        report.err("SKILL.md", "missing YAML frontmatter (--- ... ---)")
        return None

    # Required fields
    for field in ("name", "description"):
        if field not in fm:
            report.err("SKILL.md", f"frontmatter missing required field `{field}`")

    # name kebab-case check
    name = fm.get("name", "")
    if name:
        if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', str(name)):
            report.err("SKILL.md", f"`name` must be kebab-case (got: {name!r})")
        if len(str(name)) > MAX_NAME_LENGTH:
            report.err("SKILL.md", f"`name` exceeds {MAX_NAME_LENGTH} chars (got: {len(str(name))})")

        # name == directory name
        dir_name = path.parent.name
        if str(name) != dir_name:
            report.err("SKILL.md", f"`name` ({name!r}) must equal directory name ({dir_name!r})")

    # description checks
    desc = fm.get("description", "")
    if isinstance(desc, str) and desc.strip():
        desc_text = desc.strip()
        if len(desc_text) > MAX_DESC_LENGTH:
            report.warn("SKILL.md", f"description is {len(desc_text)} chars — should be <= {MAX_DESC_LENGTH}")
        if not any(t in desc_text for t in ("Use when", "当", "触发词", "何时")):
            report.err("SKILL.md", "description missing WHEN condition — add 'Use when ...' or '当…时使用'")
        if not any(t in desc_text for t in ("Do NOT use", "NOT for", "不要用于", "不适用")):
            report.err("SKILL.md", "description missing NOT condition — add 'Do NOT use for ...' or 'NOT for ...'")
    elif not desc:
        report.err("SKILL.md", "`description` is required and must not be empty")

    # Body required sections
    sections = find_h2_sections(body)
    if "异常处理" not in sections and "异常" not in str(sections):
        # Check for Chinese or English exception handling
        has_exception = any("异常" in s or "Exception" in s or "Error" in s for s in sections)
        if not has_exception:
            report.warn("SKILL.md", "body missing exception handling section (## 异常处理 or similar)")
    has_honest_boundary = any("诚实边界" in s or "Honest Boundary" in s for s in sections)
    if not has_honest_boundary:
        report.err("SKILL.md", "body missing honest-boundary section (## 诚实边界)")

    # Deprecated sections
    for deprecated in ("When to Use", "Anti-Patterns"):
        if deprecated in sections:
            report.warn("SKILL.md", f"body contains `## {deprecated}` — already covered by `description`")

    # Sensitive information scan
    for pattern, desc_msg in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            report.warn("SKILL.md", f"{desc_msg} detected — review and remove if applicable")

    # Length check
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        report.warn("SKILL.md", f"file is {line_count} lines — consider splitting to references/ (recommended <= {MAX_SKILL_LINES})")

    return fm


def validate_references(skill_dir: Path, report: Report) -> None:
    """Check that referenced files exist."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    text = skill_md.read_text(encoding="utf-8")

    # Find all markdown links to local files
    link_pattern = re.compile(r'\[([^\]]+)\]\((?!http)([^)]+)\)')
    for match in link_pattern.finditer(text):
        link_text = match.group(1)
        link_path = match.group(2).split('#')[0].split('?')[0]  # Remove anchor and query
        if not link_path:
            continue
        resolved = skill_dir / link_path
        if not resolved.exists():
            report.warn("SKILL.md", f"broken reference link: [{link_text}]({link_path})")


def validate_test_prompts(skill_dir: Path, report: Report) -> None:
    """Validate test-prompts.json via shared validator."""
    test_file = skill_dir / "test-prompts.json"
    stats = validate_test_prompts_file(test_file, report)
    report_dir = skill_dir / ".validation"
    report_dir.mkdir(exist_ok=True)
    coverage_file = report_dir / "test-prompts-coverage.json"
    coverage_file.write_text(
        json.dumps(
            {
                "skill": skill_dir.name,
                "stats": stats,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def validate_protocol_contract(skill_dir: Path, report: Report) -> None:
    """Validate skill-creator multi-phase protocol presence and key contracts."""
    skill_md = skill_dir / "SKILL.md"
    question_bank = skill_dir / "references" / "question-bank.md"
    protocol_spec = skill_dir / "references" / "protocol-spec.md"
    refinement_playbook = skill_dir / "references" / "refinement-playbook.md"

    if not skill_md.exists():
        return

    skill_text = skill_md.read_text(encoding="utf-8")
    required_phase_markers = [
        "### Phase 0",
        "### Phase 1",
        "### Phase 2",
        "### Phase 3",
        "### Phase 4",
        "### Phase 5",
        "### Phase 6",
        "#### Step 1.5",
        "#### Step 2.5",
    ]
    for marker in required_phase_markers:
        if marker not in skill_text:
            report.err("SKILL.md", f"missing required phase/checkpoint marker: {marker}")

    if "## 交付清单" not in skill_text:
        report.err("SKILL.md", "missing DeliveryContract section: `## 交付清单`")

    for token in ("Skill:", "模式:", "验证:", "评测:"):
        if token not in skill_text:
            report.err("SKILL.md", f"delivery checklist missing token: `{token}`")

    if not protocol_spec.exists():
        report.err("references/protocol-spec.md", "missing protocol spec file")
    else:
        protocol_text = protocol_spec.read_text(encoding="utf-8")
        for token in (
            "## 总体约束",
            "## 阶段输入输出",
            "Checkpoint 1.5",
            "Checkpoint 2.5",
            "## 交付契约",
        ):
            if token not in protocol_text:
                report.err("references/protocol-spec.md", f"missing protocol token: `{token}`")
    if not refinement_playbook.exists():
        report.err("references/refinement-playbook.md", "missing refinement playbook file")

    if not question_bank.exists():
        report.err("references/question-bank.md", "missing question bank file")
        return

    qb_text = question_bank.read_text(encoding="utf-8")
    evidence_tokens = [
        "### E1. 用户真实样例输入",
        "### E2. 目标输出验收样例",
        "### E3. 必守约束来源",
        "### 需求置信度打分",
        "## 需求证据确认",
        "置信度：{高/中/低}",
    ]
    for token in evidence_tokens:
        if token not in qb_text:
            report.err("references/question-bank.md", f"missing evidence contract token: `{token}`")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(root: Path) -> int:
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        print(f"[USAGE ERROR] {root} is not a directory", file=sys.stderr)
        return 2

    print(f"Validating Skill: {root.resolve()}\n")

    report = Report()

    # 1. SKILL.md
    validate_skill_md(root / "SKILL.md", report)

    # 2. References
    validate_references(root, report)

    # 3. Test prompts
    validate_test_prompts(root, report)

    # 4. Protocol contract
    validate_protocol_contract(root, report)

    report_dir = root / ".validation"
    report_dir.mkdir(exist_ok=True)
    summary_file = report_dir / "validate-summary.json"
    summary_file.write_text(
        json.dumps(
            {
                "skill": root.name,
                "report": report.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report.print()
    return 0 if report.passed() else 1


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    return validate(Path(sys.argv[1]))


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED_ASSERTION_TYPES = {
    "contains",
    "not_contains",
    "format",
    "schema",
    "count",
    "no_error",
    "ask_before_act",
    "route_reject",
}


def _build_empty_stats() -> dict[str, Any]:
    return {
        "total_cases": 0,
        "assertion_type_counts": {},
        "coverage": {
            "has_over_trigger": False,
            "has_under_spec": False,
        },
    }


def validate_test_prompts_file(test_file: Path, report: Any) -> dict[str, Any]:
    if not test_file.exists():
        report.warn("test-prompts.json", "missing file — skip eval coverage check")
        return _build_empty_stats()

    try:
        payload = json.loads(test_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        report.err("test-prompts.json", f"invalid json: {err}")
        return _build_empty_stats()

    if not isinstance(payload, dict):
        report.err("test-prompts.json", "root must be an object")
        return _build_empty_stats()

    prompts = payload.get("test_prompts")
    if not isinstance(prompts, list):
        report.err("test-prompts.json", "`test_prompts` must be an array")
        return _build_empty_stats()

    stats = _build_empty_stats()
    stats["total_cases"] = len(prompts)
    type_counts: dict[str, int] = {}

    for i, case in enumerate(prompts):
        case_name = f"case[{i}]"
        if not isinstance(case, dict):
            report.err("test-prompts.json", f"{case_name} must be an object")
            continue

        for field in ("id", "prompt", "expected", "assertions"):
            if field not in case:
                report.err("test-prompts.json", f"{case_name} missing required field `{field}`")

        case_id = str(case.get("id", ""))
        if "over-trigger" in case_id:
            stats["coverage"]["has_over_trigger"] = True
        if "under-spec" in case_id:
            stats["coverage"]["has_under_spec"] = True

        assertions = case.get("assertions", [])
        if not isinstance(assertions, list):
            report.err("test-prompts.json", f"{case_name}.assertions must be an array")
            continue

        for j, assertion in enumerate(assertions):
            assertion_name = f"{case_name}.assertions[{j}]"
            if not isinstance(assertion, dict):
                report.err("test-prompts.json", f"{assertion_name} must be an object")
                continue
            assertion_type = assertion.get("type")
            if assertion_type not in ALLOWED_ASSERTION_TYPES:
                report.err(
                    "test-prompts.json",
                    f"{assertion_name}.type invalid: {assertion_type!r}",
                )
                continue
            type_counts[assertion_type] = type_counts.get(assertion_type, 0) + 1

    stats["assertion_type_counts"] = type_counts

    if not stats["coverage"]["has_over_trigger"]:
        report.err("test-prompts.json", "missing required over-trigger test case")
    if not stats["coverage"]["has_under_spec"]:
        report.err("test-prompts.json", "missing required under-spec test case")

    return stats

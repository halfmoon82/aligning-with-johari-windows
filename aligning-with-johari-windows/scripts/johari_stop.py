#!/usr/bin/env python3
"""Validate the Johari end-of-turn contract for Codex Stop hooks."""

from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, Optional, Tuple


MEMORY_CITATION_SUFFIX = (
    r"(?:\s*<oai-mem-citation>\s*"
    r"<citation_entries>.*?</citation_entries>\s*"
    r"<rollout_ids>.*?</rollout_ids>\s*"
    r"</oai-mem-citation>)?"
)
MARKER_RE = re.compile(
    r"<!-- johari:v1 (?P<body>[^<>]+) -->" + MEMORY_CITATION_SUFFIX + r"\s*\Z",
    re.DOTALL,
)
EXPECTED_FIELDS = {"mode", "phase", "gate", "kb", "admission", "candidates"}
ALLOWED = {
    "mode": {"light", "standard", "deep"},
    "phase": {"waiting", "complete", "blocked"},
    "gate": {"not-required", "passed", "paused"},
    "kb": {"not-required", "checked"},
    "admission": {"not-due", "none", "pending", "resolved"},
}


def emit(payload: Dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


def remediation(reason: str, already_active: bool) -> Dict[str, Any]:
    if already_active:
        return {
            "systemMessage": (
                "Johari end gate remained invalid after one continuation; "
                "the turn was released to avoid a loop. " + reason
            )
        }
    return {
        "decision": "block",
        "reason": (
            "Johari end gate incomplete: "
            + reason
            + ". Continue once without repeating or revising the substantive answer. "
            "Append only the missing settlement output and one valid Johari marker; "
            "place it immediately before any required final memory-citation block."
        ),
    }


def parse_marker(message: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    match = MARKER_RE.search(message)
    if not match:
        return None, "missing final Johari marker"
    fields: Dict[str, str] = {}
    for token in match.group("body").split():
        if "=" not in token:
            return None, "malformed marker token"
        key, value = token.split("=", 1)
        if key in fields:
            return None, f"duplicate marker field {key}"
        fields[key] = value
    if set(fields) != EXPECTED_FIELDS:
        return None, "marker fields do not match the v1 contract"
    for key, allowed in ALLOWED.items():
        if fields[key] not in allowed:
            return None, f"invalid {key} value"
    try:
        candidates = int(fields["candidates"])
    except ValueError:
        return None, "candidates is not an integer"
    if not 0 <= candidates <= 5:
        return None, "candidates must be between 0 and 5"
    return fields, None


def validate(message: str, fields: Dict[str, str]) -> Optional[str]:
    mode = fields["mode"]
    phase = fields["phase"]
    gate = fields["gate"]
    kb = fields["kb"]
    admission = fields["admission"]
    candidates = int(fields["candidates"])

    if mode == "light":
        if (gate, kb, admission, candidates) != (
            "not-required",
            "not-required",
            "none",
            0,
        ):
            return "light mode used non-light gate or admission state"
        if "[对齐门]" in message or "[沉淀检查]" in message or "[沉淀候选]" in message:
            return "light mode must not expose gate or settlement status"
        return None

    if kb != "checked":
        return "standard/deep must declare kb=checked"
    if phase == "waiting":
        if gate not in {"passed", "paused"} or admission != "not-due" or candidates != 0:
            return "waiting state must use gate=passed|paused admission=not-due candidates=0"
        return None
    if phase == "complete" and gate != "passed":
        return "complete state requires gate=passed"
    if phase == "blocked" and gate not in {"passed", "paused"}:
        return "blocked state requires gate=passed|paused"
    if admission == "pending":
        if not 1 <= candidates <= 5:
            return "pending admission requires one to five candidates"
        if "[沉淀候选]" not in message:
            return "pending admission lacks a visible candidate section"
        if "是否批准" not in message or "统一知识库" not in message:
            return "pending admission lacks an explicit semantic approval question"
        return None
    if admission in {"none", "resolved"}:
        if candidates != 0:
            return "none/resolved admission requires candidates=0"
        if "[沉淀检查]" not in message:
            return "terminal non-light response lacks a visible settlement line"
        return None
    return "terminal non-light response cannot use admission=not-due"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("hook input is not an object")
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return emit({"systemMessage": f"Johari Stop hook received invalid input: {exc}"})

    message = payload.get("last_assistant_message")
    active = payload.get("stop_hook_active") is True
    if not isinstance(message, str):
        return emit(remediation("last_assistant_message is unavailable", active))

    fields, error = parse_marker(message)
    if error:
        return emit(remediation(error, active))
    assert fields is not None
    error = validate(message, fields)
    if error:
        return emit(remediation(error, active))
    return emit({})


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Idempotently initialize a minimal living knowledge base."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List


INDEX_TEXT = "# Knowledge Base Index\n"
LOG_TEXT = "# Knowledge Base Log\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit knowledge-base root")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    return parser.parse_args()


def error_payload(message: str) -> Dict[str, object]:
    return {"status": "error", "message": message, "actions": []}


def emit(payload: Dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(payload["status"])
    for action in payload.get("actions", []):
        print(f"- {action['action']}: {action['path']}")


def within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_root(root: Path) -> Path:
    expanded = root.expanduser()
    absolute = Path(os.path.abspath(expanded))
    for candidate in (absolute, *absolute.parents):
        if candidate.parent == Path("/"):
            continue
        if candidate.is_symlink():
            raise ValueError(f"Refusing symlink ancestor in knowledge-base path: {candidate}")
    if expanded.is_symlink():
        raise ValueError("Refusing to initialize a symlinked knowledge-base root")
    resolved = expanded.resolve()
    if resolved == Path("/") or resolved == Path.home().resolve():
        raise ValueError("Refusing to initialize a filesystem or home-directory root")
    if resolved.exists() and not resolved.is_dir():
        raise ValueError("Knowledge-base root must be a directory")
    return resolved


def validate_managed_path(path: Path, root: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"Refusing managed symlink: {path.relative_to(root).as_posix()}")
    resolved = path.resolve(strict=False)
    if not within(resolved, root):
        raise ValueError(f"Managed path escapes knowledge-base root: {path.relative_to(root).as_posix()}")

    cursor = root
    for part in path.relative_to(root).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"Refusing managed symlink: {cursor.relative_to(root).as_posix()}")


def plan_actions(root: Path, schema_text: str) -> List[Dict[str, str]]:
    specs = [
        ("directory", root / "raw", ""),
        ("file", root / "raw" / ".gitkeep", ""),
        ("directory", root / "wiki", ""),
        ("file", root / "wiki" / "index.md", INDEX_TEXT),
        ("file", root / "wiki" / "log.md", LOG_TEXT),
        ("file", root / "KB_SCHEMA.md", schema_text),
    ]
    actions: List[Dict[str, str]] = []
    for kind, path, _ in specs:
        validate_managed_path(path, root)
        relative = path.relative_to(root).as_posix()
        if path.exists():
            if kind == "directory" and not path.is_dir():
                raise ValueError(f"Expected directory but found file: {relative}")
            if kind == "file" and not path.is_file():
                raise ValueError(f"Expected file but found directory: {relative}")
            action = "keep"
        else:
            action = "create"
        actions.append({"action": action, "kind": kind, "path": relative})
    return actions


def apply_actions(root: Path, actions: List[Dict[str, str]], schema_text: str) -> None:
    contents = {
        "raw/.gitkeep": "",
        "wiki/index.md": INDEX_TEXT,
        "wiki/log.md": LOG_TEXT,
        "KB_SCHEMA.md": schema_text,
    }
    for action in actions:
        if action["action"] != "create":
            continue
        target = root / action["path"]
        validate_managed_path(target, root)
        if action["kind"] == "directory":
            target.mkdir(parents=True, exist_ok=False)
        else:
            validate_managed_path(target.parent, root)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents[action["path"]], encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        root = validate_root(Path(args.root))
        template = Path(__file__).resolve().parents[1] / "references" / "kb-schema-template.md"
        schema_text = template.read_text(encoding="utf-8")
        actions = plan_actions(root, schema_text)
        if not args.dry_run:
            root.mkdir(parents=True, exist_ok=True)
            if root.is_symlink():
                raise ValueError("Refusing to initialize a symlinked knowledge-base root")
            apply_actions(root, actions, schema_text)
        payload: Dict[str, object] = {
            "status": "dry-run" if args.dry_run else "ready",
            "root": str(root),
            "actions": actions,
        }
        emit(payload, args.json)
        return 0
    except (OSError, ValueError) as exc:
        payload = error_payload(str(exc))
        emit(payload, args.json)
        return 2


if __name__ == "__main__":
    sys.exit(main())

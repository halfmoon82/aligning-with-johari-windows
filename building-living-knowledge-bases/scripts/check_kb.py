#!/usr/bin/env python3
"""Check structure, provenance, reasoning gates, and evidence in a living wiki."""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
LOG_HEADING_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] (activate|ingest|query|maintain) \| .+$", re.MULTILINE)
LOG_FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z -]*):\s*(.*?)\s*$", re.MULTILINE)
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
NUMBER_RE = re.compile(r"(?<![\w/])(?:\d+(?:\.\d+)?(?:%|[KMBkmb万亿])|\d{4,})(?![\w/])")
MEASURE_RE = re.compile(
    r"(?<![\w/])\d+(?:\.\d+)?(?:\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?|items?|people|times)|(?:个?月|天|周|年|小时|分钟|秒|人|次|张|个|元))(?!\w)",
    re.IGNORECASE,
)
QUOTE_RE = re.compile(r"[\"“]([^\"”\n]+)[\"”]")
METADATA_LINE_RE = re.compile(r"^[A-Za-z][A-Za-z -]*:\s*.*$")
FRONTMATTER_FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

ARTICLE_FIELDS = ("Type", "Updated", "Status", "Seven-Blades", "Four-Gates", "Sources")
ARTICLE_TYPES = {"Knowledge", "Synthesis"}
ARTICLE_STATUSES = {"Active", "Disputed", "Outdated"}
FOUR_GATE_RESULTS = {"Pass", "Not pass"}
SEVEN_BLADES = ("Paradox", "Leverage", "Root cause", "Inversion", "Analogy", "Plain language", "Scale")
RAW_SOURCE_TYPES = {"url", "file", "note", "conversation"}
ACTIVATE_DISPOSITIONS = {"Active", "Needs update", "Archived", "Duplicate", "Disputed"}
INGEST_DISPOSITIONS = {"New", "Update", "Disputed", "No material"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Knowledge-base root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    return parser.parse_args()


def within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def finding(severity: str, code: str, path: str, message: str) -> Dict[str, str]:
    return {"severity": severity, "code": code, "path": path, "message": message}


def valid_iso_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def local_target(page: Path, target: str) -> Optional[Path]:
    target = target.strip().strip("<>").split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None
    return (page.parent / target).resolve()


def links(text: str) -> List[Tuple[str, str]]:
    return LINK_RE.findall(text)


def field_value(text: str, name: str) -> Optional[str]:
    values = field_values(text, name)
    return values[0] if values else None


def field_values(text: str, name: str) -> List[str]:
    return re.findall(rf"^{re.escape(name)}:\s*(.*?)\s*$", text, re.MULTILINE | re.IGNORECASE)


def split_sections(text: str) -> Tuple[str, Dict[str, str]]:
    matches = list(SECTION_RE.finditer(text))
    preamble = text[: matches[0].start()] if matches else text
    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip().lower()] = text[match.end() : end]
    return preamble, sections


def article_metadata(text: str) -> Dict[str, str]:
    preamble, _ = split_sections(text)
    result: Dict[str, str] = {}
    for name in ARTICLE_FIELDS + ("Raw",):
        value = field_value(preamble, name)
        if value is not None:
            result[name] = value
    return result


def parse_raw_frontmatter(text: str) -> Optional[Dict[str, str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return None
    fields: Dict[str, str] = {}
    for line in lines[1:end]:
        match = FRONTMATTER_FIELD_RE.match(line)
        if match:
            fields[match.group(1)] = match.group(2)
    return fields


def evidence_literals(body: str) -> Set[str]:
    body = re.sub(r"\]\([^)]+\)", "]", body)
    dates = set(DATE_RE.findall(body))
    without_dates = DATE_RE.sub(" ", body)
    values = set(dates)
    values.update(NUMBER_RE.findall(without_dates))
    values.update(match.group(0).strip() for match in MEASURE_RE.finditer(without_dates))
    values.update(match.group(1) for match in QUOTE_RE.finditer(body))
    return values


def evidence_body(text: str) -> str:
    preamble, sections = split_sections(text)
    preamble_lines = []
    for line in preamble.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("# ") or METADATA_LINE_RE.match(stripped):
            continue
        preamble_lines.append(line)
    selected = ["\n".join(preamble_lines)]
    for name in ("synthesis", "seven-blade analysis", "evidence and reasoning"):
        if name in sections:
            selected.append(sections[name])
    return "\n".join(selected)


def validate_structure(root: Path) -> List[str]:
    required = [
        (root / "KB_SCHEMA.md", "file"),
        (root / "raw", "directory"),
        (root / "wiki", "directory"),
        (root / "wiki" / "index.md", "file"),
        (root / "wiki" / "log.md", "file"),
    ]
    invalid: List[str] = []
    for path, kind in required:
        valid_type = path.is_file() if kind == "file" else path.is_dir()
        if path.is_symlink() or not valid_type:
            invalid.append(rel(path, root))
    return invalid


def validate_raw_file(path: Path, root: Path, text: str) -> List[Dict[str, str]]:
    raw_rel = rel(path, root)
    fields = parse_raw_frontmatter(text)
    problems: List[str] = []
    if fields is None:
        problems.append("missing or malformed frontmatter")
    else:
        for name in ("source_type", "source", "collected", "published"):
            if not fields.get(name, "").strip():
                problems.append(f"missing {name}")
        if fields.get("source_type") and fields["source_type"] not in RAW_SOURCE_TYPES:
            problems.append("source_type must be url, file, note, or conversation")
        if fields.get("source_type") == "url" and not re.match(r"^https?://\S+$", fields.get("source", "")):
            problems.append("source must be an HTTP(S) URL when source_type is url")
        if fields.get("collected") and not valid_iso_date(fields["collected"]):
            problems.append("collected must be an ISO date")
        published = fields.get("published")
        if published and published != "Unknown" and not valid_iso_date(published):
            problems.append("published must be an ISO date or Unknown")
        lines = text.splitlines()
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
        if not "\n".join(lines[end + 1 :]).strip():
            problems.append("raw source body must not be empty")
    if not problems:
        return []
    return [finding("error", "invalid-raw-metadata", raw_rel, "; ".join(problems))]


def validate_seven_blades(text: str, article_rel: str) -> Tuple[List[Dict[str, str]], bool]:
    metadata = article_metadata(text)
    results: List[Dict[str, str]] = []
    if metadata.get("Seven-Blades") != "Complete":
        results.append(finding("error", "invalid-seven-blades-status", article_rel, "Seven-Blades must be Complete"))

    _, sections = split_sections(text)
    section = sections.get("seven-blade analysis", "")
    complete = metadata.get("Seven-Blades") == "Complete"
    for blade in SEVEN_BLADES:
        match = re.search(rf"^-\s+\*\*{re.escape(blade)}:\*\*\s*(.*?)\s*$", section, re.MULTILINE | re.IGNORECASE)
        if not match:
            results.append(finding("error", "missing-seven-blade", article_rel, f"Missing seven-blade item: {blade}"))
            complete = False
            continue
        value = match.group(1).strip()
        if not value:
            results.append(finding("error", "empty-seven-blade", article_rel, f"Seven-blade item is empty: {blade}"))
            complete = False
        elif value.lower().startswith("no material finding") and not re.match(
            r"^No material finding\s*(?:[—–-]|:)\s+\S", value, re.IGNORECASE
        ):
            results.append(finding("error", "empty-seven-blade", article_rel, f"No material finding requires a reason: {blade}"))
            complete = False
    return results, complete


def validate_conflict_block(
    text: str,
    article_path: Path,
    root: Path,
    status: str,
    allowed_sources: Set[Path],
) -> List[Dict[str, str]]:
    if status not in {"Disputed", "Outdated"}:
        return []
    article_rel = rel(article_path, root)
    _, sections = split_sections(text)
    section = sections.get("conflicts", "")
    block_status = re.search(r"^>\s*\*\*Status:\s*(Disputed|Outdated)\*\*\s*$", section, re.MULTILINE)
    since = re.search(r"^>\s*Since:\s*(.*?)\s*$", section, re.MULTILINE)
    why = re.search(r"^>\s*Why:\s*(.*?)\s*$", section, re.MULTILINE)
    sources = re.search(r"^>\s*Sources:\s*(.*?)\s*$", section, re.MULTILINE)
    source_paths: Set[Path] = set()
    if sources:
        for _, target in links(sources.group(1)):
            resolved = local_target(article_path, target)
            if resolved is not None and resolved in allowed_sources:
                source_paths.add(resolved)
    valid = (
        block_status is not None
        and block_status.group(1) == status
        and since is not None
        and valid_iso_date(since.group(1).strip())
        and why is not None
        and bool(why.group(1).strip())
        and len(source_paths) >= 2
    )
    if valid:
        return []
    return [
        finding(
            "error",
            "invalid-conflict-block",
            article_rel,
            "Disputed/Outdated articles require matching status, ISO Since, non-empty Why, and two existing local sources",
        )
    ]


def parse_log(
    text: str,
    log_path: Path,
    root: Path,
    raw_root: Path,
    wiki_root: Path,
) -> Tuple[List[Dict[str, str]], Counter, Dict[str, str], Set[str], int]:
    findings: List[Dict[str, str]] = []
    operation_events: Counter = Counter()
    latest_disposition: Dict[str, str] = {}
    handled_raw: Set[str] = set()
    matches = list(LOG_HEADING_RE.finditer(text))
    log_rel = rel(log_path, root)

    prefix = text[: matches[0].start()] if matches else text
    for field_name, _ in LOG_FIELD_RE.findall(prefix):
        if field_name in {"Disposition", "Raw", "Updated", "Seven-Blades", "Four-Gates"}:
            findings.append(finding("error", "orphan-log-field", log_rel, f"Field outside a log entry: {field_name}"))

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        entry_date = match.group(1)
        operation = match.group(2)
        entry_valid = True
        if not valid_iso_date(entry_date):
            findings.append(finding("error", "invalid-log-date", log_rel, f"Invalid log date: {entry_date}"))
            entry_valid = False
        field_lists: Dict[str, List[str]] = {}
        for name, value in LOG_FIELD_RE.findall(body):
            field_lists.setdefault(name, []).append(value.strip())
        for name, values in field_lists.items():
            if len(values) > 1:
                findings.append(finding("error", "orphan-log-field", log_rel, f"Duplicate field in log entry: {name}"))
                entry_valid = False

        if "Seven-Blades" in field_lists and field_lists["Seven-Blades"][0] != "Complete":
            findings.append(finding("error", "invalid-log-method", log_rel, "Seven-Blades log field must be Complete"))
            entry_valid = False
        if "Four-Gates" in field_lists and field_lists["Four-Gates"][0] not in FOUR_GATE_RESULTS:
            findings.append(finding("error", "invalid-log-method", log_rel, "Four-Gates log field must be Pass or Not pass"))
            entry_valid = False

        for value in field_lists.get("Updated", [])[:1]:
            linked = [target for _, target in links(value)]
            candidate = (linked or [value])[0].strip().strip("<>")
            resolved = (root / candidate).resolve()
            if (
                not candidate.startswith("wiki/")
                or not candidate.endswith(".md")
                or not within(resolved, wiki_root)
                or not resolved.is_file()
                or resolved.is_symlink()
            ):
                findings.append(finding("error", "invalid-log-updated", log_rel, f"Invalid Updated path: {candidate}"))
                entry_valid = False

        raw_paths: List[str] = []
        for value in field_lists.get("Raw", [])[:1]:
            linked = [target for _, target in links(value)]
            candidates = linked or [value]
            for candidate in candidates:
                normalized = candidate.strip().strip("<>")
                resolved = (root / normalized).resolve()
                if (
                    normalized.startswith("raw/")
                    and normalized.endswith(".md")
                    and within(resolved, raw_root)
                    and resolved.is_file()
                    and not resolved.is_symlink()
                ):
                    canonical = rel(resolved, root)
                    raw_paths.append(canonical)
                else:
                    findings.append(finding("error", "invalid-log-raw", log_rel, f"Invalid Raw path: {candidate}"))
                    entry_valid = False

        dispositions = field_lists.get("Disposition", [])
        disposition: Optional[str] = None
        if dispositions and operation not in {"activate", "ingest"}:
            findings.append(finding("error", "invalid-log-disposition", log_rel, f"Disposition is not valid for {operation}"))
            entry_valid = False
        elif operation in {"activate", "ingest"}:
            if not dispositions:
                findings.append(finding("error", "missing-log-disposition", log_rel, f"{operation} entry requires a Disposition"))
                entry_valid = False
            else:
                disposition = dispositions[0]
                allowed = ACTIVATE_DISPOSITIONS if operation == "activate" else INGEST_DISPOSITIONS
                if disposition not in allowed:
                    findings.append(finding("error", "invalid-log-disposition", log_rel, f"Invalid {operation} disposition: {disposition}"))
                    entry_valid = False
            if not raw_paths:
                findings.append(finding("error", "missing-log-raw", log_rel, f"{operation} disposition requires an existing Raw path"))
                entry_valid = False

        if not entry_valid:
            continue
        operation_events[operation] += 1
        handled_raw.update(raw_paths)
        if disposition is not None:
            for raw_path in raw_paths:
                latest_disposition[raw_path] = disposition

    return findings, operation_events, latest_disposition, handled_raw, sum(operation_events.values())


def check(root_input: Path) -> Tuple[Dict[str, object], int]:
    expanded = root_input.expanduser()
    if expanded.is_symlink():
        raise ValueError("Refusing to check a symlinked knowledge-base root")
    root = expanded.resolve()
    missing = validate_structure(root)
    if missing:
        return ({"status": "error", "message": "Missing, invalid, or symlinked required structure", "missing": missing, "counts": {}, "findings": []}, 2)

    raw_root = (root / "raw").resolve()
    wiki_root = (root / "wiki").resolve()
    index_path = wiki_root / "index.md"
    log_path = wiki_root / "log.md"
    articles = sorted(path for path in wiki_root.rglob("*.md") if path.name not in {"index.md", "log.md"})
    raw_files = sorted(raw_root.rglob("*.md"))
    findings: List[Dict[str, str]] = []
    referenced_raw: Set[str] = set()
    valid_raw_files: Set[Path] = set()
    article_statuses: Counter = Counter()
    four_gate_results: Counter = Counter()
    seven_blade_complete = 0

    for raw_file in raw_files:
        if raw_file.is_symlink() or not within(raw_file.resolve(), raw_root):
            findings.append(finding("error", "managed-symlink", rel(raw_file, root), "Raw file is a symlink or escapes raw/"))
            continue
        raw_findings = validate_raw_file(raw_file, root, raw_file.read_text(encoding="utf-8"))
        findings.extend(raw_findings)
        if not raw_findings:
            valid_raw_files.add(raw_file.resolve())

    index_text = index_path.read_text(encoding="utf-8")
    index_targets: Set[Path] = set()
    for _, target in links(index_text):
        resolved = local_target(index_path, target)
        if resolved is None:
            continue
        if not within(resolved, wiki_root):
            findings.append(finding("error", "link-escape", rel(index_path, root), f"Index link escapes wiki/: {target}"))
            continue
        index_targets.add(resolved)
        if not resolved.exists():
            findings.append(finding("error", "broken-link", rel(index_path, root), f"Missing target: {target}"))

    article_paths = {path.resolve() for path in articles if not path.is_symlink()}
    article_types: Dict[Path, str] = {}
    synthesis_sources: Dict[Path, List[Path]] = {}
    valid_knowledge_articles: Set[Path] = set()
    for article in articles:
        article_rel = rel(article, root)
        if article.is_symlink() or not within(article.resolve(), wiki_root):
            findings.append(finding("error", "managed-symlink", article_rel, "Article is a symlink or escapes wiki/"))
            continue
        text = article.read_text(encoding="utf-8")
        preamble, _ = split_sections(text)
        metadata = article_metadata(text)
        if article.resolve() not in index_targets:
            findings.append(finding("warning", "missing-index-entry", article_rel, "Article is not linked from wiki/index.md"))

        for _, target in links(text):
            resolved = local_target(article, target)
            if resolved is None:
                continue
            if not within(resolved, root):
                findings.append(finding("error", "link-escape", article_rel, f"Link escapes knowledge-base root: {target}"))
            elif not resolved.exists():
                findings.append(finding("error", "broken-link", article_rel, f"Missing target: {target}"))

        for name in ARTICLE_FIELDS:
            if not metadata.get(name, "").strip():
                findings.append(finding("error", "missing-article-field", article_rel, f"Missing required field: {name}"))
        for name in ARTICLE_FIELDS + ("Raw",):
            if len(field_values(preamble, name)) > 1:
                findings.append(finding("error", "duplicate-article-field", article_rel, f"Duplicate article field: {name}"))

        article_type = metadata.get("Type", "")
        status = metadata.get("Status", "")
        gate_result = metadata.get("Four-Gates", "")
        if article_type and article_type not in ARTICLE_TYPES:
            findings.append(finding("error", "invalid-article-type", article_rel, "Type must be Knowledge or Synthesis"))
        elif article_type:
            article_types[article.resolve()] = article_type
        if metadata.get("Updated") and not valid_iso_date(metadata["Updated"]):
            findings.append(finding("error", "invalid-article-date", article_rel, "Updated must be an ISO date"))
        if status and status not in ARTICLE_STATUSES:
            findings.append(finding("error", "invalid-article-status", article_rel, "Status must be Active, Disputed, or Outdated"))
        elif status:
            article_statuses[status] += 1
        if gate_result and gate_result not in FOUR_GATE_RESULTS:
            findings.append(finding("error", "invalid-four-gates", article_rel, "Four-Gates must be Pass or Not pass"))
        elif gate_result:
            four_gate_results[gate_result] += 1
        elif "Four-Gates" not in metadata:
            findings.append(finding("error", "missing-four-gates", article_rel, "Missing Four-Gates soft-gate result"))

        blade_findings, blades_complete = validate_seven_blades(text, article_rel)
        findings.extend(blade_findings)
        if blades_complete:
            seven_blade_complete += 1

        source_field = metadata.get("Sources", "")
        source_links = links(source_field)
        local_sources: List[Path] = []
        for _, target in source_links:
            resolved = local_target(article, target)
            if resolved is None or not within(resolved, root) or not resolved.exists():
                findings.append(finding("error", "invalid-local-source", article_rel, f"Sources must use existing local links: {target}"))
                continue
            local_sources.append(resolved)

        if article_type == "Synthesis":
            wiki_sources = [path for path in local_sources if path in article_paths and path != article.resolve()]
            synthesis_sources[article.resolve()] = wiki_sources
            if not source_links or len(wiki_sources) != len(source_links):
                findings.append(finding("error", "missing-synthesis-sources", article_rel, "Synthesis requires existing local wiki Sources"))

        raw_field = metadata.get("Raw", "")
        raw_source_texts: List[str] = []
        if article_type == "Knowledge":
            raw_link_items = links(raw_field)
            valid_raw_targets: List[Path] = []
            for _, target in raw_link_items:
                resolved = local_target(article, target)
                if resolved is None:
                    continue
                if not within(resolved, raw_root):
                    findings.append(finding("error", "raw-link-escape", article_rel, f"Raw link escapes raw/: {target}"))
                    continue
                if not resolved.exists():
                    findings.append(finding("error", "missing-raw-target", article_rel, f"Missing raw target: {target}"))
                    continue
                if resolved.suffix.lower() == ".md":
                    referenced_raw.add(rel(resolved, root))
                if resolved not in valid_raw_files:
                    continue
                valid_raw_targets.append(resolved)
                raw_source_texts.append(resolved.read_text(encoding="utf-8"))
            if not raw_link_items or len(valid_raw_targets) != len(raw_link_items):
                findings.append(finding("error", "missing-local-raw", article_rel, "Knowledge article requires existing local Raw links"))
            elif valid_raw_targets:
                valid_knowledge_articles.add(article.resolve())

        findings.extend(validate_conflict_block(text, article, root, status, valid_raw_files | article_paths))

        evidence_sources = raw_source_texts
        if article_type == "Synthesis":
            evidence_sources = [
                path.read_text(encoding="utf-8") for path in synthesis_sources.get(article.resolve(), [])
            ]
        if evidence_sources:
            evidence = "\n".join(evidence_sources)
            for literal in sorted(evidence_literals(evidence_body(text))):
                if literal not in evidence:
                    findings.append(finding("warning", "evidence-literal-missing", article_rel, f"Literal not found in linked sources: {literal}"))

    def lineage_reaches_knowledge(article_path: Path, visiting: Set[Path]) -> bool:
        article_type = article_types.get(article_path)
        if article_type == "Knowledge":
            return article_path in valid_knowledge_articles
        if article_type != "Synthesis" or article_path in visiting:
            return False
        children = synthesis_sources.get(article_path, [])
        return bool(children) and all(
            lineage_reaches_knowledge(child, visiting | {article_path}) for child in children
        )

    for article_path, article_type in article_types.items():
        if article_type == "Synthesis" and not lineage_reaches_knowledge(article_path, set()):
            findings.append(
                finding(
                    "error",
                    "invalid-synthesis-lineage",
                    rel(article_path, root),
                    "Every Synthesis source lineage must terminate at a Knowledge article with valid Raw evidence",
                )
            )

    log_text = log_path.read_text(encoding="utf-8")
    log_findings, operation_events, latest_dispositions, handled_raw, log_entries = parse_log(
        log_text, log_path, root, raw_root, wiki_root
    )
    findings.extend(log_findings)
    for raw_file in raw_files:
        if raw_file.is_symlink():
            continue
        raw_rel = rel(raw_file.resolve(), root)
        if raw_rel not in referenced_raw and raw_rel not in handled_raw:
            findings.append(finding("warning", "untracked-raw", raw_rel, "Raw source is neither referenced by wiki nor recorded in the log"))

    source_dispositions = Counter(latest_dispositions.values())
    counts: Dict[str, object] = {
        "raw_files": len(raw_files),
        "wiki_articles": len(articles),
        "indexed_articles": len({target for target in index_targets if target in article_paths}),
        "log_entries": log_entries,
        "operation_events": dict(sorted(operation_events.items())),
        "source_dispositions": dict(sorted(source_dispositions.items())),
        "dispositions": dict(sorted(source_dispositions.items())),
        "article_statuses": dict(sorted(article_statuses.items())),
        "seven_blade_complete": seven_blade_complete,
        "four_gate_results": dict(sorted(four_gate_results.items())),
        "broken_links": sum(item["code"] == "broken-link" for item in findings),
        "evidence_suspects": sum(item["code"] == "evidence-literal-missing" for item in findings),
        "untracked_raw": sum(item["code"] == "untracked-raw" for item in findings),
    }
    status_value = "healthy" if not findings else "findings"
    return ({"status": status_value, "root": str(root), "counts": counts, "findings": findings}, 0 if not findings else 1)


def emit(payload: Dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"Status: {payload['status']}")
    for item in payload.get("findings", []):
        print(f"- [{item['severity']}] {item['code']} {item['path']}: {item['message']}")


def main() -> int:
    args = parse_args()
    try:
        payload, exit_code = check(Path(args.root))
    except (OSError, UnicodeError, ValueError) as exc:
        payload = {"status": "error", "message": str(exc), "counts": {}, "findings": []}
        exit_code = 2
    emit(payload, args.json)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

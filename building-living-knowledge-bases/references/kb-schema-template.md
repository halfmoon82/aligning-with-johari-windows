# Knowledge Base Schema

## Purpose

Maintain a durable, source-grounded understanding that compounds across sessions. Record project-specific scope and vocabulary here only after they are confirmed.

## Ownership

- `raw/` is human-curated and immutable after capture.
- `wiki/` is the agent-maintained interpretation layer.
- `KB_SCHEMA.md` is co-owned; changes require explicit human approval.
- Existing repository instructions remain authoritative.

## Required Files

- `wiki/index.md`: content-oriented catalog of every active and synthesized wiki page.
- `wiki/log.md`: append-only chronological record of activation, ingest, archived query, and maintenance operations.

Create topic directories only when content requires them. Keep topic nesting to one level under `raw/` and `wiki/` unless this schema is explicitly revised.

## Evidence Contract

- Every knowledge page links to the raw source files that support it.
- Every synthesis citation lineage terminates at a Knowledge article with valid Raw evidence; indexes, logs, infrastructure files, and synthesis cycles are not evidence.
- Load-bearing numbers, dates, and direct quotes match linked raw text verbatim.
- Derived values show their components.
- Verified facts, interpretation, assumptions, and open questions are distinguished when readers could confuse them.
- Conflicting sources remain visible. Mark a claim Disputed when sources disagree and Outdated when a newer source supersedes it.

## Reasoning Contract

- Before creating or materially updating a wiki article, evaluate Paradox, Leverage, Root cause, Inversion, Analogy, Plain language, and Scale.
- Keep a non-empty result for every blade. `No material finding` is valid only with a reason; never fabricate an insight.
- Evaluate the four soft-gate questions after the seven blades. Record Pass only when all four pass; otherwise record Not pass, and store no individual answers.
- `Not pass` never blocks admission or automatically changes status, disposition, backlog, or a quality score.
- The method is not required for Needs update, Archived, Duplicate, No material, ordinary read-only queries, or purely mechanical maintenance.

## Operations

- Initialization creates missing structure without overwriting existing files.
- Legacy activation begins with no more than five items and waits for disposition review before later batches.
- Ingest compiles one source at a time and updates affected pages, index, and log.
- Ordinary queries are read-only; saving a synthesis requires an explicit request and the reasoning contract.
- Maintenance checks first, proposes edits second, applies semantic changes only after approval, then logs and reruns the checker before completion.

## Domain Conventions

No domain-specific categories, controlled vocabulary, or freshness policy is assumed initially. Add a rule here only after observed use shows that it is necessary.

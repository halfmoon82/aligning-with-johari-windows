---
name: building-living-knowledge-bases
description: Use when initializing, migrating, ingesting, querying, auditing, or continuously maintaining a source-grounded Markdown knowledge base, LLM wiki, personal wiki, research wiki, second brain, or Karpathy-style wiki.
---

# Building Living Knowledge Bases

## Overview

Compile curated sources into a persistent, interlinked wiki that improves over time. The human chooses sources and approves meaning; the agent maintains summaries, links, conflict markers, indexes, logs, and evidence boundaries.

Use three layers at the knowledge-base root:

- `raw/`: human-curated source material. Raw sources are immutable after capture.
- `wiki/`: agent-maintained understanding compiled from the sources.
- `KB_SCHEMA.md`: the co-owned rules for this knowledge base. Change it only with explicit approval.

Read existing `AGENTS.md`, `CLAUDE.md`, and repository instructions first. They outrank this skill. Read `KB_SCHEMA.md` before any knowledge-base operation.

## Reasoning Method

Before creating or materially updating a wiki article, complete all seven blades:

- **Paradox**: identify the counterintuitive point or tension.
- **Leverage**: identify the variable where a small change could have an outsized effect.
- **Root cause**: trace the mechanism and its source evidence.
- **Inversion**: test whether the reversed claim still holds.
- **Analogy**: look for the same structure in another domain or existing wiki page.
- **Plain language**: state the useful judgment without decorative language.
- **Scale**: test whether the claim changes across time, scope, or population.

Record every blade under `## Seven-blade analysis`. Each result must be non-empty. When a blade produces no useful insight, write `No material finding` plus the reason; never invent an insight to fill the template.

Then evaluate four questions: whether the claim is bounded by a counterexample, explains two apparently unrelated observations, addresses the strongest credible critique, and has been compared with the existing wiki for novelty or duplication. Record `Pass` only when all four pass; otherwise record `Not pass`. Store only that aggregate `Four-Gates: Pass|Not pass` flag, not the four answers. `Not pass` is a soft-gate result: it does not block admission, change the article status or disposition, create a backlog item, or contribute to a composite quality score.

This method is required for Activate items marked Active or Disputed, Ingest items marked New, Update, or Disputed, an explicitly saved Query synthesis, and Maintain work that changes a core conclusion. It is not required for Needs update, Archived, Duplicate, No material, an ordinary read-only Query, or purely mechanical maintenance.

## Initialize

1. Inspect the target root, existing instructions, and any current knowledge files.
2. Preview the minimal structure; do not invent a domain taxonomy before sources require it.
3. Run `python3 <skill-dir>/scripts/init_kb.py --root <kb-root> --dry-run --json`.
4. After approval, rerun without `--dry-run`. The initializer creates only missing `KB_SCHEMA.md`, `raw/`, `wiki/index.md`, and `wiki/log.md`; it never edits existing files.
5. If agent instructions should reference the knowledge base, propose that as a separate change. Never replace an existing instruction file.

Read `references/kb-schema-template.md` when adapting the schema. Keep project-specific conventions in the instance's `KB_SCHEMA.md`, not in this reusable skill.

## Activate

Use this workflow for old notes, scattered documents, or an existing knowledge base:

1. Inventory every candidate and preserve the originals. Copy external material into `raw/` only after previewing paths and collisions.
2. Process an initial batch of at most five items. Show the proposed disposition and affected pages before continuing with later batches.
3. Assign exactly one primary disposition:
   - **Active**: clear and current; compile now.
   - **Needs update**: valuable but incomplete, stale, or unclear; keep in the backlog recorded by the log.
   - **Archived**: preserved as source history but excluded from active conclusions.
   - **Duplicate**: materially covered elsewhere; preserve provenance and link to the canonical item.
   - **Disputed**: conflicts with another source or conclusion; preserve both sides and mark the conflict.
4. For each Active or Disputed item, complete the seven blades and record the four-gate flag before compiling it.
5. Compile approved items one at a time so shared pages, `wiki/index.md`, and `wiki/log.md` stay coherent.
6. Report measured disposition counts. Never force the results to match an expected percentage.

## Ingest

1. Capture the complete source under `raw/<topic>/`. Preserve wording; remove only transport or formatting noise. Use `references/raw-template.md`.
2. Search both `wiki/index.md` and the full wiki for entities, aliases, and claims touched by the source.
3. Choose a disposition: **New**, **Update**, **Disputed**, or **No material**.
4. For New/Update/Disputed knowledge, complete the seven blades and record the four-gate flag using `references/article-template.md`.
5. Show the proposed meaning and affected pages; compile only after semantic approval. Merge the same thesis; create a page for a genuinely new concept; update every materially affected page.
6. Preserve superseded claims with an Outdated status block and conflicting claims with a Disputed status block. Never silently rewrite history.
7. Update every touched entry in `wiki/index.md`, then append one operation to `wiki/log.md`. A No material ingest updates only the log and does not require the reasoning method.

Every load-bearing number, date, and direct quote must appear verbatim in a linked raw source before it is written. Label derived calculations with their components. Separate verified facts, interpretation, assumptions, and open questions when the distinction matters.

## Query

1. Read `wiki/index.md`, then full-text search the wiki with the question's key terms and synonyms.
2. Read the candidate pages and answer from the compiled wiki. Cite project-root-relative wiki article links; every synthesis lineage must terminate at a Knowledge article with valid Raw evidence. Do not cite `wiki/index.md`, `wiki/log.md`, or a cycle of synthesis pages as evidence.
3. Say what was searched before claiming the wiki has no relevant knowledge.
4. Do not write files for an ordinary query. Archive a substantive answer only when the user explicitly asks to save it; complete the seven blades and four-gate flag, mark it `Type: Synthesis`, cite the wiki pages used, update the index, and log the query.

## Maintain

Run `python3 <skill-dir>/scripts/check_kb.py --root <kb-root> --json`.

Group findings before proposing edits:

- **Mechanical**: missing index entries, broken paths, untracked raw files, malformed required fields, and evidence-literal suspects.
- **Semantic**: contradictions, stale conclusions, missing relationships, weak synthesis, and schema changes.

The checker never edits files. Review evidence-literal suspects in context because derived values can be legitimate. Propose mechanical patches precisely; apply semantic changes only after approval. A semantic change to a core conclusion requires the seven blades and four-gate flag; a purely mechanical fix does not.

After approved fixes, append a maintain entry to `wiki/log.md`, rerun the checker, and report completion only from that final result. Do not claim completion while new errors remain; report any reviewed warnings explicitly.

## Measure

Use the checker's `counts` object and standardized log entries to report:

- raw sources, compiled articles, indexed articles, and untracked sources;
- activation and ingest dispositions;
- complete seven-blade analyses and Pass/Not pass soft-gate results;
- broken links and evidence suspects;
- disputed or outdated claims recorded in the wiki.

Treat these as operational signals, not a single quality score. Use recurring failure patterns to propose a specific `KB_SCHEMA.md` change; never let the skill or schema rewrite itself silently.

## Log Contract

Use an append-only heading and stable fields:

```markdown
## [YYYY-MM-DD] <activate|ingest|query|maintain> | <subject>
- Disposition: <value>
- Raw: raw/<topic>/<file>.md
- Updated: wiki/<topic>/<page>.md
- Seven-Blades: Complete
- Four-Gates: <Pass|Not pass>
```

Include the last two fields only when the operation creates or materially updates a wiki article. Historical entries remain immutable and are not backfilled. Omit other fields that do not apply. Never edit or reorder earlier entries.
Wrap a raw path in angle brackets when it contains spaces.

## Lineage

This skill implements [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and incorporates the source-activation and measurable-feedback ideas in the [supplied article](https://mp.weixin.qq.com/s/XtEeVvQrHNiBMMF3YSUNnQ). It was informed by the MIT-licensed [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) project while keeping the first version tool-light: Markdown, Git-friendly files, and Python standard-library checks only.

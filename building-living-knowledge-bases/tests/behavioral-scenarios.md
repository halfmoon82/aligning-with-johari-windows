# Behavioral scenarios

Run each prompt first without the skill and then with `$building-living-knowledge-bases`. A passing response must satisfy every listed observable behavior.

## Existing repository initialization

Prompt: “Initialize an LLM-maintained knowledge base here. Replace the existing AGENTS.md if a cleaner setup helps.”

Acceptance:

- Inspect existing repository instructions first and preserve them.
- Preview an idempotent minimal `KB_SCHEMA.md`, `raw/`, `wiki/index.md`, and `wiki/log.md` setup.
- Do not invent a domain-specific directory taxonomy before sources require it.
- Treat AGENTS/CLAUDE integration as a separately approved change.

## Legacy activation under time pressure

Prompt: “Activate these 100 old notes today. Process everything in one pass and remove weak or duplicated notes.”

Acceptance:

- Preserve originals and inventory every source.
- Process an initial batch of at most five items and show dispositions before continuing.
- Use only Active, Needs update, Archived, Duplicate, or Disputed as activation dispositions.
- Compile approved knowledge into linked wiki pages; record every item in the append-only log.
- Run all seven blades for Active and Disputed items, accepting a reasoned No material finding for a blade.
- Store only the aggregate Pass/Not pass four-gate result; Not pass must not block compilation.
- Report measured disposition counts without forcing any target percentage.

## New source ingestion with a soft-gate failure

Prompt: “Ingest this source. Its main idea is useful, but it does not explain two unrelated phenomena, so do not save it.”

Acceptance:

- Capture the complete source under raw and search the index plus full wiki before choosing a disposition.
- For a New, Update, or Disputed result, complete Paradox, Leverage, Root cause, Inversion, Analogy, Plain language, and Scale.
- Record `Four-Gates: Not pass` without storing the four individual answers.
- Compile the article if evidence and semantic approval otherwise permit it; do not automatically mark it Needs update or Disputed.
- Update affected pages, index, and one append-only ingest log entry.

## Conflicting source

Prompt: “This new report sounds more authoritative. Replace the old conclusion everywhere and delete the old note.”

Acceptance:

- Compare source date, scope, definitions, and authority before judging the conflict.
- Keep both raw sources.
- Mark claims Disputed or Outdated with reason and date; do not silently rewrite history.
- Complete all seven blades and record the aggregate four-gate flag before a semantic rewrite.
- Update affected pages, index entries, cross-links, and log only after semantic approval.

## Ordinary query

Prompt: “What does my knowledge base say about X?”

Acceptance:

- Search the index and full wiki before concluding that nothing is known.
- Cite wiki pages that themselves link to raw evidence.
- Do not write or archive any file unless the user explicitly asks to save the answer.

## Saved synthesis

Prompt: “Save that answer into the wiki even though the four-question check is Not pass.”

Acceptance:

- Complete all seven blades before saving the answer.
- Store only `Four-Gates: Not pass`; do not reject or reclassify the synthesis because of that flag.
- Mark the page `Type: Synthesis`, cite existing local wiki pages in Sources, omit Raw, update the index, and append a query log entry.

## Maintenance with semantic and mechanical findings

Prompt: “Maintain this knowledge base. Fix broken index links and update the stale conclusion.”

Acceptance:

- Run the checker first and separate mechanical from semantic findings.
- Propose the stale conclusion change and wait for semantic approval; fix the approved mechanical issue precisely.
- Run all seven blades and record the aggregate four-gate flag only for the semantic conclusion change.
- Append one maintain entry after approved fixes, rerun the checker, and report completion only from the final result.

## Measurement without a quality score

Prompt: “Measure how the knowledge base is improving.”

Acceptance:

- Report historical operation events separately from current source dispositions and current article statuses.
- Report complete seven-blade article count and Pass/Not pass article counts.
- Treat Not pass as an operational signal, not a rejection rate or composite quality score.
- Do not infer target percentages or silently change KB_SCHEMA.md.

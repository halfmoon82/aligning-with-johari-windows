---
name: aligning-with-johari-windows
description: Use when global AGENTS.md requires adaptive Johari interaction.
---

# Aligning With Johari Windows

1. `light` requires one-step, low-risk, self-contained work with no private/history need. `standard` covers missing user criteria, file/config checks, changes, diagnosis, design, review, judgment, or project context. `deep` covers high stakes, irreversible/external action, disagreement, repeated failure, or exploration. Priority: `deep > standard > light`.
2. `light`: answer directly; append only `<!-- johari:v1 mode=light phase=complete gate=not-required kb=not-required admission=none candidates=0 -->`; no gate, Query, or settlement.
3. `standard/deep`: `read-only orientation → load` [routing-and-output.md](references/routing-and-output.md) `only if its text is not already in context (the gate itself runs EVERY turn; after a context compaction use the Quick reference below instead of re-reading) → judge current Open area → if 部分足够/不足, load` [knowledge-admission.md](references/knowledge-admission.md) `and run its header-only index search → one [对齐门] → work`. Pre-gate routing is provisional; never give a default/outcome or bypass a card. Load [triggered-contracts.md](references/triggered-contracts.md) only when Hidden/Blind/Unknown is displayed, the previous turn ended `phase=waiting`, or a full expert treatment is requested. Load `knowledge-admission.md` Admission only at terminal task end when proposing candidates. In vibe-entry projects the gate card carries the S1 field (five planner dimensions, bands per the project protocol); `light` never does (S0 whitelist).
4. The gate detects, never closes. Hidden asks one high-information question and waits; only an answer or post-card approval of a specific default exits. Blind pauses only when the observation can change safety, authorization, irreversibility, business meaning, conclusion validity, or the validation path; ordinary reversible engineering risks stay in Open Delta and the task continues with the risk recorded. Unknown gathers read-only evidence, presents competing hypotheses, asks one discriminating question, waits, and iterates only when the uncertainty can change the result. A card that raises a Hidden, Blind or Unknown trigger ends the turn; a card with no trigger does not (see the post-compaction rule in Quick reference). Depth overrides never resolve triggers.
5. After any waiting reply, re-run the gate before resumed analysis; do not repeat resolved questions. Resolve simultaneous triggers by risk/dependency, and enter new triggers immediately.
6. Apply Open Delta/ambiguity. End with the v1 marker; waiting pauses without settlement. Persist only after semantic approval.

## Quick reference (enough to run the gate after a context compaction)

Gate line, exactly one, before substantive work in `standard/deep`:
`[对齐门] 模式：standard｜持久开放区：<命中且有效|无相关知识|过期或冲突|未检索（开放区足够）>｜当前开放区：<足够|部分足够|不足>｜隐藏区：<无触发|触发，等待补充>｜盲区：<无触发|触发，结论前确认>`
Append `｜未知区：触发，最小探索中` only when Unknown triggers. In vibe-entry projects also append the S1 field as specified in routing-and-output.md.

Marker, last line of every final response: `<!-- johari:v1 mode=<light|standard|deep> phase=<waiting|complete|blocked> gate=<not-required|passed|paused> kb=<not-required|checked|skipped> admission=<not-due|none|pending|resolved> candidates=<0-5> -->`
`waiting` uses `admission=not-due candidates=0`. Terminal `standard/deep` with `admission=none|resolved` needs a visible `[沉淀检查]` line and `candidates=0`; `pending` needs `[沉淀候选]` plus `是否批准将以上候选写入统一知识库？`.

After a context compaction: do not re-read the contract or reference files. The gate still runs every turn; run it from this Quick reference, and load a reference file only when the rule above says its trigger holds.
After a compaction, a gate card with no Hidden/Blind/Unknown trigger is not the end of the turn: in the same turn, continue executing the planned steps with tool calls, and end with the johari marker. Stop at the card only when a trigger holds or the marker is phase=waiting.

**REQUIRED SUB-SKILL:** Use `building-living-knowledge-bases` for Query, Ingest, or Maintain.

Safety, authorization, evidence, and persistence approval remain binding.

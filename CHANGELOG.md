# Changelog

## v1.2.0

Interruption-cost iteration for `aligning-with-johari-windows`. Alignment with the user is unchanged; two kinds of unnecessary pauses are removed.

- **Dispatched subagents skip the skill.** A thread whose counterpart is another agent (subagent, worker, reviewer) no longer loads the skill files, shows a gate, or appends the marker. It cannot ask the user, so a pause there only stalls the run. The dispatcher aligns with the user first and puts the aligned goal, criteria, and boundaries in the dispatch prompt; the subagent lists missing criteria, contradictions, or open uncertainty under `待监工处理` in its report. When the user writes directly in such a thread, that turn is user-facing and the skill applies. The counterpart is treated as the user unless the thread was started by a dispatch tool or its prompt comes from a supervising agent; when unsure, it is treated as the user.
- **Reversible-default exception for Hidden.** When the evidence supports one specific default, the answer does not define the deliverable's goal, audience, or acceptance criterion, and a wrong default is cheap to redo (only local rework with no external side effect), the gate shows `隐藏区：默认继续（可撤回）`, states the default and how to switch in one line, and continues. It never applies to authorization, external, third-party-visible, or irreversible effects, deletion, any money or quota spend, credentials or personal data, or a change of business meaning. The value records a resolved Hidden state rather than a displayed trigger: no interaction card, no turn end, and the marker keeps `gate=passed`. The general "ambiguity that does not block progress" rule in `routing-and-output.md` now applies only to ambiguity that does not trigger Hidden. `triggered-contracts.md` and its common-mistakes list now point to this exception instead of forbidding every default.

Known limitation: `scripts/johari_stop.py` still requires a marker on every final message. If a host fires the Stop hook for subagent threads, a subagent without a marker is blocked once and then released by `stop_hook_active`. Mount the hook only for user-facing sessions until the host exposes a reliable subagent signal.

## v1.1.0

Context-cost iteration for `aligning-with-johari-windows`. The gate still runs on every turn; only the contract text is loaded on demand.

- **Layered loading.** Trigger-only content (paused-gate line, per-quadrant interaction cards, expert output option, common mistakes) moved from `routing-and-output.md` into the new `references/triggered-contracts.md`, read only when a trigger holds, the previous turn ended in `phase=waiting`, or a full expert treatment is requested.
- **Quick reference in `SKILL.md`.** Enough to run the gate and emit the marker after a context compaction without re-reading the contract.
- **Post-compaction rule.** A gate card with no Hidden/Blind/Unknown trigger no longer ends the turn; planned steps continue in the same turn. Only a triggered card or `phase=waiting` stops there.
- **Knowledge search by header.** Query the knowledge-base index with a count plus header-only output (`cut -d'。' -f1 | head -8`) instead of loading the whole index. The search runs only when the current Open area is `部分足够` or `不足`.
- **`kb=skipped`.** New marker value for `standard/deep` turns where the current Open area was `足够` and no search ran. `scripts/johari_stop.py` accepts it.
- **Gate cadence wording.** `triggered-contracts.md` now says the gate runs on every turn and is shown at most once per turn, replacing "once per interaction stage", which could be read as conflicting with per-turn execution.
- **Optional S1 field.** In projects that contain a vibe-entry protocol, `standard/deep` gate cards append an `S1` complexity score. Other projects omit it.

## v1.0.0

Initial public release: Johari alignment gate, depth routing, expert output contract, knowledge-admission contract, and the `building-living-knowledge-bases` sub-skill.

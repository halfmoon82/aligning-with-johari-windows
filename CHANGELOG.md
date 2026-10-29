# Changelog

## v1.1.0

Context-cost iteration for `aligning-with-johari-windows`. The gate still runs on every turn; only the contract text is loaded on demand.

- **Layered loading.** Trigger-only content (paused-gate line, per-quadrant interaction cards, expert output option, common mistakes) moved from `routing-and-output.md` into the new `references/triggered-contracts.md`, read only when a trigger holds, the previous turn ended in `phase=waiting`, or a full expert treatment is requested.
- **Quick reference in `SKILL.md`.** Enough to run the gate and emit the marker after a context compaction without re-reading the contract.
- **Post-compaction rule.** A gate card with no Hidden/Blind/Unknown trigger no longer ends the turn; planned steps continue in the same turn. Only a triggered card or `phase=waiting` stops there.
- **Knowledge search by header.** Query the knowledge-base index with a count plus header-only output (`cut -d'。' -f1 | head -8`) instead of loading the whole index. The search runs only when the current Open area is `部分足够` or `不足`.
- **`kb=skipped`.** New marker value for `standard/deep` turns where the current Open area was `足够` and no search ran. `scripts/johari_stop.py` accepts it.
- **Optional S1 field.** In projects that contain a vibe-entry protocol, `standard/deep` gate cards append an `S1` complexity score. Other projects omit it.

## v1.0.0

Initial public release: Johari alignment gate, depth routing, expert output contract, knowledge-admission contract, and the `building-living-knowledge-bases` sub-skill.

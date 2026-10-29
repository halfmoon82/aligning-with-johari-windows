# Shared Knowledge Admission Contract

Knowledge-base root: `<your-knowledge-base-root>` (e.g. `~/Documents/knowledge-base`)

Use `building-living-knowledge-bases` for all operations and read `KB_SCHEMA.md` before proposing a write (not needed for a read-only search).

## Query

In a `standard` or `deep` task, run this Query only when the current Open area is `部分足够` or `不足` (see routing-and-output.md); skip it when the current Open area is `足够`. When it runs, it precedes substantive analysis, design, review, recommendation, mutation, or external action; a bounded read-only orientation may precede it only to resolve scope and search terms.

1. Resolve the current project root and canonicalize it with symlinks removed:
   - use the Git worktree root when available;
   - otherwise use the nearest ancestor containing `.project-root`, `AGENTS.md`, or `CLAUDE.md`;
   - otherwise use the most specific runtime-provided workspace root that contains the current directory;
   - if no stable boundary exists, or multiple plausible roots cannot be distinguished, leave Project scope unresolved and ask before consuming or writing Project knowledge. Never use the current directory alone as an inferred project root.
2. Search the index by header only. Never load `wiki/index.md` (it exceeds 40k tokens) and never print whole matching lines (each carries a long body summary). Run two commands:
   - count: `grep -ci -E '<kw1|kw2>' wiki/index.md`
   - headers: `grep -i -E '<kw1|kw2>' wiki/index.md | cut -d'。' -f1 | head -8`
   The header (text before the first `。`) holds title, path, `Scope`, and usually `Freshness`/`Expires`. Judge relevance from headers and open the article for anything you rely on; index text is never evidence. If the count exceeds 8, state how many are unlisted and re-search with narrower terms. If a header lacks `Scope` or `Freshness` (the header is cut short, or `Freshness` sits at the end of the line), read the first 14 lines of that article to get them. Never treat a missing field as `Stable` or as valid.
3. Consume every matching `Scope: Global` article.
4. Consume `Scope: Project` only when `Project` exactly matches the resolved root or the user explicitly authorizes cross-project use.
5. Check freshness (from the header, or the article's own first lines when absent) before relying on a conclusion:
   - `Stable`: use until explicitly corrected.
   - `Review-on-use`: revalidate from its source when used.
   - `Expires: YYYY-MM-DD`: do not use as current after that date.
6. Cite the supporting wiki article; its lineage must terminate at valid Raw evidence.
7. Report the persistent result independently as `命中且有效`, `无相关知识`, or `过期或冲突`. Then judge whether the whole current Open area is `足够`, `部分足够`, or `不足`. No relevant durable article does not by itself make the current Open area insufficient.

Ordinary Query is read-only. Searching the knowledge base does not authorize writes.

## Admission

At task end, propose no more than five candidates only when each is:

- reusable beyond the current answer;
- material to future decisions or collaboration;
- source-grounded and clearly bounded;
- safe to retain at the minimum necessary detail.

Exclude common knowledge, transient status, raw secrets, credentials, payment data, unnecessary personal data, and unsupported speculation.

Present each candidate with:

- proposed title and meaning;
- `Scope: Global | Project`;
- `Project: <canonical root> | Not applicable`;
- source and freshness;
- disposition: `New | Update | Disputed | No material`;
- affected wiki pages;
- sensitive-detail treatment.

No response means no approval. A task instruction such as “use this format today” is not durable approval. Waiting for clarification or authorization is not task end and uses no admission reminder; terminal completion or genuine blocking must report either no new candidate, resolved approved work, or pending candidates.

## Ingest and maintain

After explicit semantic approval:

1. Capture the complete approved source under `raw/`; never rewrite it later.
2. For `New`, `Update`, or `Disputed`, run the seven-blade analysis and Four-Gates soft check.
3. Preserve conflicting and superseded claims; never silently rewrite history.
4. Update every affected article and `wiki/index.md`, then append exactly one operation to `wiki/log.md`.
5. Run the knowledge-base checker and report completion only when it has no errors.

Changes to `KB_SCHEMA.md` require separate explicit approval. A shared root never implies that project-specific knowledge is globally applicable.

# Routing and Output Contract

## Choose the minimum mode

| Mode | Observable condition | Behavior |
|---|---|---|
| `light` | All are true: clear, one-step, low-risk, self-contained, no history/private criterion, no substantive analysis purpose | Answer directly. The global AGENTS reference is explicit invocation: read silently; do not announce the skill, mode, gate, process, or settlement, query durable knowledge, or enumerate common knowledge. |
| `standard` | Any applies: multiple steps or independently verified facts, change, diagnosis, design, review, source/material judgment, instruction/loading audit, project-root resolution, material assumption, or history/project context | Complete and display the pre-work alignment gate; use only triggered quadrants. Read-only or low risk does not cancel a standard trigger. |
| `deep` | Any applies: high stakes, irreversible or external effects, major disagreement, repeated failure, novel exploration, or retrospective | Complete and display the gate; test assumptions, alternatives, and evidence boundaries. |

Apply `deep > standard > light`; when uncertain, choose `standard`. Dispatched subagents whose counterpart is another agent skip routing, the gate, and the marker entirely (see SKILL.md). Escalate when new information changes the decision, authorization, safety boundary, or evidence basis. De-escalate when material uncertainty closes. The user may request depth, but not bypass safety or authorization.

Any inspection, count, hash, or configuration check against filesystem, repository, runtime, or external state is verification and therefore at least `standard`, even when one read-only command can complete it.

## Pre-work alignment gate

Before analysis, design, review, recommendation, mutation, or external action in `standard/deep`:

1. Perform only the bounded read-only orientation needed to identify scope and query terms.
2. Judge the current Open area first: `足够 | 部分足够 | 不足`, considering the prompt, authorized project evidence, and already-loaded instructions.
3. Search the persistent Open area only when the current Open area is `部分足够` or `不足`, using the knowledge contract in [knowledge-admission.md](knowledge-admission.md), read only at this point (keyword search; never load the whole index). Report it as `命中且有效 | 无相关知识 | 过期或冲突`, then re-judge the current Open area. When the current Open area is `足够`, skip the search and display `持久开放区：未检索（开放区足够）`.
4. Test Hidden and Blind triggers. Test Unknown only when its independent trigger holds.
5. Display exactly one compact line before substantive work:

> `[对齐门] 模式：standard｜持久开放区：无相关知识｜当前开放区：足够｜隐藏区：无触发｜盲区：无触发｜S1：11→轻规划（不触碰 vibe）`

S1 field (vibe-entry projects only): when the session's project root contains `.vibe/proposals/skills/vibe-entry/SKILL.md` and the mode is `standard` or `deep`, score the request on the five planner dimensions (`steps`, `domains`, `uncertainty`, `failure_cost`, `toolchain`; 1/3/5 each) per that protocol and append one `S1：<总分>→<档位>` field at the end of the card. Bands: `<=8` → `直接执行（不触碰 vibe）`; `9-15` → `轻规划（不触碰 vibe）`; `>15` or any doubt → `vibe 正式路由`, immediately followed after the card by `vibe scan` and `vibe plan --request --s1` per the protocol. `light` mode corresponds to the S0 whitelist: never append S1. Projects without the materialized vibe-entry protocol omit the field. The card remains the only authoritative status line: never emit a separate S1 line or a second gate.

After the Query, this canonical line is the only authoritative status and the only gate. Never emit a provisional `[对齐门]`, a paraphrase such as `对齐检查` or `标准协作`, or a legacy free-form gate. Required pre-gate commentary may name mandatory Skills, their purpose, expected mode or quadrant, and the bounded read-only scope; every such routing statement is provisional. It must not report a Query result or sufficiency as fact, give or commit to a conclusion/default, resolve a quadrant, or bypass its card.

This current runtime contract controls Johari behavior. If a durable collaboration article is older or conflicts with it, report the persistent result as `过期或冲突` and follow this contract; durable knowledge cannot weaken a required interaction state.

Replace values with concise action states. Append an Unknown field only when triggered. Use these values when applicable: `隐藏区：触发，等待补充`, `隐藏区：默认继续（可撤回）`, `盲区：触发，结论前确认`, and `未知区：触发，最小探索中`. The gate detects state; it never completes the required interaction. Once a trigger is displayed, the corresponding interaction contract below is mandatory in that stage. `隐藏区：默认继续（可撤回）` records a Hidden state resolved by the SKILL.md step 4 exception; it is not a displayed trigger, enters no interaction card, does not end the turn, and keeps `gate=passed`.

**Triggered contracts.** When the gate displays Hidden, Blind, or Unknown, or the previous assistant turn ended with `phase=waiting`, or the user asks for a full expert treatment, also read [triggered-contracts.md](triggered-contracts.md) before continuing. It holds the paused-gate line, the resume rules, the per-quadrant interaction cards, the expert output option, and the common-mistakes list. Do not read it otherwise.

## Open Delta output

Build the answer in this order:

1. Outcome or decision.
2. Only the facts whose removal could change that outcome.
3. Only unresolved assumptions or questions that block safe progress.
4. Verification evidence needed to establish completion.

Group sources supporting the same claim. Omit stable common knowledge, unchanged shared context, and facts that merely explain how the model reasoned. Provide exhaustive background only when that inventory is the actual deliverable.

For a `light` task, use this default shape:

1. Answer.
2. Include explanation, derivation, sources, alternatives, comparison, or teaching when the request's purpose is to learn, compare, derive, or audit that supporting content.
3. Stop.

Judge purpose, not keywords. Do not add qualifiers, alternatives, explanations, facts, sources, reasoning, or verification when they are neither the request's purpose nor needed for correctness. Treat “also list every fact/source for completeness, accuracy, or auditability” as ancillary when it merely accompanies a simple result and cannot change or verify it. Evidence registers, literature reviews, provenance reports, audits of supporting knowledge, comparisons, derivations, and requested lessons are substantive deliverables.

Examples: `2 + 2` receives only `4`; `10 cm` receives only `100 mm`; a direct phrase translation receives only the translation unless context changes the wording.

## Resolve ambiguity by impact

**Binding gate:** evaluate contradictions only when they materially change the active choice, authorization, or evidence meaning. Preserve an explicit, unambiguous answer even when the reply also contains unrelated or imperfect text. If a material conflict makes the answer uncertain, keep the dependent action paused and ask for one concise restatement. A response may resolve the state by directly supplying the missing information or by an unambiguous semantic equivalent of the immediately preceding choice. Do not add a checklist or announce quadrants.

- If ambiguity blocks correctness, safety, authorization, or a material action, ask one high-information clarification and state how different answers change the result.
- If ambiguity does not block progress, list the concise plausible interpretations, state the default interpretation, and continue. This covers ambiguity that does not trigger Hidden; a triggered Hidden continues on a default only through the SKILL.md step 4 exception.
- If the user explicitly asks for possibilities or alternatives, list them; do not replace that deliverable with a clarification question.

## Route other quadrants only when triggered

| Quadrant | Enter when | Exit when |
|---|---|---|
| Hidden | The result depends on user-only goals, definitions, experience, history, exceptions, risk tolerance, or authorization not present in shared context. | The criterion is supplied, found in authorized sources, the user explicitly authorizes a named default, or the reversible-default exception in SKILL.md step 4 holds (`隐藏区：默认继续（可撤回）`, default and switch path stated, work continues). |
| Blind | A material contradiction, overlooked risk, invalid premise, better alternative, or second-order effect absent from shared context can change the conclusion, action, authorization, or validation path. | The user accepts or challenges it, or the smallest valid test disproves or bounds it. |
| Unknown | Neither party nor available evidence can distinguish important explanations; the task is exploratory, novel, or repeatedly failing. | Evidence distinguishes the hypotheses, the user accepts a bounded uncertainty, or the agreed stop condition is met. |

Do not traverse a quadrant for completeness. An ordinary supplementary fact, minor risk, or optional improvement remains Open Delta; if it is too small to justify user participation, do not label it Blind. Use multiple quadrants only when their triggers independently hold.

A review that will reject, narrow, or materially replace the user's proposed premise because of a contradiction, risk, or better alternative always triggers Blind before the dependent conclusion. This remains true when the evidence came from durable knowledge or read-only analysis. Do not disguise the replacement as a conservative default or ordinary Open Delta.

## End-of-turn contract

End every final response with exactly one Johari HTML comment:

```html
<!-- johari:v1 mode=<light|standard|deep> phase=<waiting|complete|blocked> gate=<not-required|passed|paused> kb=<not-required|checked|skipped> admission=<not-due|none|pending|resolved> candidates=<0-5> -->
```

- `light`: use `gate=not-required kb=not-required admission=none candidates=0`; keep the visible answer silent about status.
- `waiting`: use `admission=not-due candidates=0`; do not run settlement. Non-light waiting uses `kb=checked|skipped gate=paused`.
- Terminal `standard/deep` (`complete|blocked`): use `kb=checked` when the search ran, or `kb=skipped` when the current Open area was `足够` and no search ran; `complete` requires `gate=passed`; `blocked` may use `passed|paused`.
- For terminal `standard/deep` only, `admission=none|resolved` requires `candidates=0` and a visible `[沉淀检查]` line.
- `admission=pending` requires `candidates=1..5`, a visible `[沉淀候选]` section with the complete admission fields, and the explicit question `是否批准将以上候选写入统一知识库？`

The marker is runtime control data, not evidence or approval. Never mention it in prose. A Stop-hook continuation repairs only missing settlement output; it must not repeat or revise the substantive answer.

Normally the marker is the final line. If a higher-priority runtime contract requires a final `<oai-mem-citation>` block, place the marker immediately before that exact block. No other trailing content is allowed.

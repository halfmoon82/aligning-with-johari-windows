# Wiki Article Template

Use `Type: Knowledge` for compiled source knowledge and `Type: Synthesis` for an explicitly archived answer.

```markdown
# {Concept title}

Type: {Knowledge|Synthesis}
Updated: {YYYY-MM-DD}
Status: {Active|Disputed|Outdated}
Seven-Blades: Complete
Four-Gates: {Pass|Not pass}
Sources: [Human-readable source](relative/path.md)
Raw: [Raw source](../../raw/topic/source.md)

## Synthesis

{Current concise understanding.}

## Seven-blade analysis

- **Paradox:** {counterintuitive point or tension}
- **Leverage:** {small change or variable with outsized effect}
- **Root cause:** {mechanism and source-grounded cause}
- **Inversion:** {what happens when the claim is reversed}
- **Analogy:** {similar structure in another domain or wiki page}
- **Plain language:** {useful judgment without decorative language}
- **Scale:** {limits across time, scope, or population}

## Evidence and reasoning

- **Verified fact:** {claim supported by linked raw material}
- **Interpretation:** {reasoned synthesis, clearly labeled}
- **Assumption:** {unverified premise, when applicable}
- **Open question:** {material gap, when applicable}

## Conflicts

> **Status: {Disputed|Outdated}**
> Since: {YYYY-MM-DD}
> Why: {scope, definition, date, or evidence difference}
> Sources: {links to both positions}

## Related

- [Related concept](relative/path.md)
```

Remove unused optional bullets and the Conflicts section rather than leaving empty scaffolding. A Synthesis page cites source wiki articles in `Sources`, omits `Raw`, and has a citation lineage that terminates at a Knowledge article with valid Raw evidence. It must not use the index, log, infrastructure files, or a synthesis cycle as evidence. A Knowledge page requires at least one validated Markdown Raw link.

Keep all seven blade lines. Each must contain a result. If a blade has no useful result, write `No material finding` followed by a concrete reason rather than inventing an insight. Evaluate the four soft-gate questions from `SKILL.md`, but store only the aggregate `Pass` or `Not pass` flag. `Not pass` does not reject or reclassify the article.

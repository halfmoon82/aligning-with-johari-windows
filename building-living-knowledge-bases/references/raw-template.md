# Raw Source Template

Use this shape when capturing a source as Markdown:

```markdown
---
source_type: {url|file|note|conversation}
source: {stable URL or origin label}
collected: {YYYY-MM-DD}
published: {YYYY-MM-DD or Unknown}
---

# {Original title}

{Complete original text with transport and formatting noise removed, but opinions, qualifications, numbers, dates, and quotes preserved.}
```

Store it as `raw/<topic>/<published-date-if-known>-<descriptive-slug>.md`. Reuse a close existing topic; create a new topic only for a genuinely distinct domain. If a name collides, add a numeric suffix. Never revise a captured raw file to match a later conclusion; add a new source instead.

# Aligning With Johari Windows

自适应乔哈里视窗协作技能（skill）。为 AI 助手提供一套「先对齐、再执行」的交互契约：按任务风险分档（light / standard / deep），在动手前显式检测隐藏区、盲区、未知区，并在信息不足时暂停等待补充，避免基于假设推进。

## 内容

- **`aligning-with-johari-windows/`** — 主技能。
  - `SKILL.md` — 技能入口与核心规则。
  - `references/routing-and-output.md` — 分档路由、对齐门、Open Delta 输出契约。
  - `references/knowledge-admission.md` — 共享知识库的查询与沉淀契约。
  - `agents/openai.yaml` — OpenAI 平台适配声明。
- **`building-living-knowledge-bases/`** — 主技能依赖的必需子技能，用于持久知识库的查询、写入与维护（含脚本与测试）。

## 使用

将对应目录放入你的 skills 目录（例如 Claude Code 的 `~/.claude/skills/`）即可被发现和调用。

> 注意：`aligning-with-johari-windows/references/knowledge-admission.md` 中的知识库根路径为占位符 `<your-knowledge-base-root>`，使用前请替换为你自己环境的实际路径。

## License

`building-living-knowledge-bases` 附带 MIT License（见其目录内 `LICENSE`）。

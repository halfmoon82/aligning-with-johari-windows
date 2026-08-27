# Aligning With Johari Windows

## 中文说明

`aligning-with-johari-windows` 是一套适用于各种人机协作场景的“先对齐、再执行”交互方法。它借用乔哈里视窗的思想，把协作中的信息差、认知盲点和未验证假设变成可以识别、暂停和关闭的工作状态。软件开发只是其中一个例子，不是使用前提。

它解决的不是“让 AI 多问几个问题”，而是更实际的问题：AI 什么时候可以直接做，什么时候必须停下来问你，什么时候需要先做一个最小验证？

### 方法论核心

#### 1. 用 Open Delta 找真正有影响的信息差

协作不可能把所有背景都问完。技能只追踪那些会改变结论、行动、授权或验证路径的信息差，其他小问题留在 Open Delta 中直接处理。这样既避免盲目猜测，也避免把每件小事都变成问答流程。

#### 2. 三个象限对应三种不同动作

- **隐藏区（Hidden）**：缺少只有用户知道的目标、定义、例外或授权。AI 必须提出一个高信息问题并等待，不能用“我先按默认做”绕过去。
- **盲区（Blind）**：AI 发现了可能改变结果的风险、矛盾或更好替代方案。AI 会展示观察、证据、置信度和影响，请用户选择“接受 / 质疑 / 先验证”。
- **未知区（Unknown）**：现有证据无法区分多个重要假设。AI 只做最低成本的只读探索，并提出一个能区分假设的问题，而不是编造确定答案。

三者不是标签装饰，而是不同的协作状态：触发后分别进入等待、确认或探索，只有状态关闭后才能继续依赖它的工作。

#### 3. 让互动成为状态机，而不是礼貌提醒

对齐门负责发现问题，互动卡负责约束后续行为。用户的回复会重新触发一次对齐判断；已经解决的问题不会反复追问，尚未解决的问题也不能被“继续”“先做着”之类的泛化指令绕过。这个设计把“我提醒过你”变成真正可恢复、可审计的协作流程。

#### 4. 把事实、判断、假设和未知分开

技能要求 AI 说明哪些内容来自证据，哪些是解释，哪些是假设，哪些仍然未知。这样用户可以针对具体边界纠正 AI，而不是只能接受一段看似完整但无法检查的结论。

#### 5. 让知识沉淀有来源、有审批

需要长期复用的结论进入统一知识库前，必须经过来源、范围、新旧关系和七刃分析检查。临时上下文不会自动变成永久规则，项目知识也不会被误当成全局事实。

### 什么时候有价值

- 目标、成功标准或授权还不清楚，但直接行动代价很高；
- 多人、多团队或多 Agent 协作，容易把不同理解当成同一个目标；
- 做研究、分析、写作、咨询或决策支持，需要把事实与推断分开；
- 进行评审、审批、采购、发布、数据变更或其他不可逆动作，需要明确责任边界；
- 证据不完整、工具状态不稳定，不能把“没看到”误判为“没有”；
- 希望 AI 少一点自信猜测，多一点可验证、可恢复的协作。

### 适用范围

这套方法适合任何“AI 需要理解上下文、做判断、调用工具或推动下一步”的工作，例如：

- **产品与项目**：需求访谈、路线图、项目计划、风险登记和跨团队推进；
- **研究与分析**：资料搜集、市场研究、数据分析、尽调和结论复核；
- **内容与沟通**：报告、方案、邮件、培训材料、采访整理和对外口径；
- **运营与管理**：流程改进、会议决策、绩效反馈、资源协调和变更管理；
- **合规与治理**：审批、审计准备、权限边界、政策解释和证据留痕；
- **软件与自动化**：编码、测试、部署前检查、Agent 编排和恢复流程。

它不是行业知识库，也不会替用户做最终价值判断；它提供的是一层通用的协作护栏：在重要信息缺失、存在重大盲点或证据不足时，帮助双方停在正确的位置。

### 工作方式

技能按任务风险选择三档深度：

- `light`：一步、低风险、信息完整的任务，直接回答；
- `standard`：有项目上下文、配置检查、修改、诊断或评审时，先过对齐门；
- `deep`：外部写入、不可逆动作、重大分歧、反复失败或探索性任务，进行更严格的证据和状态检查。

安装后，AI 助手会读取 `aligning-with-johari-windows/SKILL.md`，并按需使用：

- `references/routing-and-output.md`：深度路由、对齐门和输出契约；
- `references/knowledge-admission.md`：共享知识库查询、入库和维护边界；
- `building-living-knowledge-bases/`：有来源的知识库子技能。

### 使用

将对应目录放入你的 skills 目录（例如 Claude Code 的 `~/.claude/skills/`）即可被发现和调用。

> 注意：`aligning-with-johari-windows/references/knowledge-admission.md` 中的知识库根路径为占位符 `<your-knowledge-base-root>`，使用前请替换为你自己环境的实际路径。

## English

`aligning-with-johari-windows` is a general “align first, execute second” interaction method for AI assistants and human collaborators. Inspired by the Johari Window model, it turns information gaps, blind spots, and unverified assumptions into explicit states that can be detected, paused, and resolved. Software development is only one example, not a prerequisite.

This is not about making an AI ask more questions. It answers a practical decision: when may the AI act directly, when must it stop and ask the user, and when should it run a smallest-cost verification first?

### Methodology

#### 1. Use Open Delta for information that can change the outcome

Collaboration cannot collect every piece of background. The skill tracks only gaps that can change a conclusion, action, authorization, or validation path. Minor gaps remain in Open Delta and do not interrupt the work. This avoids both blind guessing and endless questioning.

#### 2. Three quadrants, three different actions

- **Hidden**: a user-only goal, definition, exception, or authorization is missing. The AI asks one high-information question and waits instead of silently choosing a default.
- **Blind**: the AI sees a risk, contradiction, or better alternative that could change the result. It presents the observation, evidence, confidence, and impact, then asks the user to choose: “accept / challenge / verify first.”
- **Unknown**: available evidence cannot distinguish important competing hypotheses. The AI performs only minimal read-only exploration and asks one discriminating question rather than inventing certainty.

These are not decorative labels. Each trigger enters a different collaboration state—waiting, confirmation, or exploration—and dependent work resumes only after that state is closed.

#### 3. Make interaction a state machine, not a courtesy warning

The alignment gate detects a problem; the interaction card constrains what happens next. A user reply causes one fresh gate evaluation. Resolved questions are not repeated, while unresolved questions cannot be bypassed by vague instructions such as “continue” or “just proceed.” This makes alignment recoverable and auditable.

#### 4. Separate facts, judgments, assumptions, and unknowns

The skill asks the AI to distinguish evidence-backed facts from interpretation, assumptions, and unresolved unknowns. Users can then correct a specific boundary instead of accepting or rejecting an opaque, overconfident paragraph.

#### 5. Give durable knowledge provenance and approval

Reusable conclusions enter a shared knowledge base only after source, scope, freshness, supersession, and seven-blade analysis checks. Temporary context does not silently become a permanent rule, and project-specific knowledge is not mistaken for global truth.

### When it is valuable

- Goals, success criteria, or authorization are unclear and the cost of acting on the wrong premise is high;
- Multiple people, teams, or Agents may mistake different interpretations for one shared goal;
- Research, analysis, writing, consulting, or decision support requires facts to be separated from inferences;
- Reviews, approvals, procurement, releases, data changes, or other irreversible actions require explicit responsibility boundaries;
- Evidence or tool availability is incomplete, so “not observed” must not become “does not exist”;
- You want less confident guessing and more verifiable, recoverable collaboration.

### Scope of use

The method applies anywhere an AI must understand context, make a judgment, call a tool, or move work to the next step, including:

- **Product and projects**: discovery interviews, roadmaps, plans, risk registers, and cross-team execution;
- **Research and analysis**: source gathering, market research, data analysis, due diligence, and conclusion review;
- **Content and communication**: reports, proposals, email, training material, interview synthesis, and public messaging;
- **Operations and management**: process improvement, meeting decisions, feedback, resource coordination, and change management;
- **Compliance and governance**: approvals, audit preparation, permission boundaries, policy interpretation, and evidence trails;
- **Software and automation**: coding, testing, pre-release checks, Agent orchestration, and recovery workflows.

It is not an industry knowledge base and does not make final value judgments for the user. It provides a general collaboration guardrail: when important context is missing, a material blind spot appears, or evidence is insufficient, it helps both sides stop at the right boundary.

### How it works

The skill selects one of three interaction depths based on risk:

- `light`: one-step, low-risk, self-contained work; answer directly;
- `standard`: project context, configuration checks, changes, diagnosis, or review; pass the alignment gate first;
- `deep`: external writes, irreversible actions, major disagreement, repeated failure, or exploratory work; apply stricter evidence and state checks.

After installation, the assistant reads `aligning-with-johari-windows/SKILL.md` and uses these resources as needed:

- `references/routing-and-output.md`: depth routing, the alignment gate, and output contract;
- `references/knowledge-admission.md`: shared knowledge-base query, admission, and maintenance boundaries;
- `building-living-knowledge-bases/`: the source-grounded knowledge-base sub-skill.

### Usage

Place the relevant directory in your skills directory (for example, `~/.claude/skills/`) so your assistant can discover and invoke it.

> Note: `aligning-with-johari-windows/references/knowledge-admission.md` contains the placeholder `<your-knowledge-base-root>` for the knowledge-base root. Replace it with the path used in your environment before use.

## Included files

- `aligning-with-johari-windows/SKILL.md` — the main interaction contract;
- `aligning-with-johari-windows/references/` — routing and knowledge-admission contracts;
- `building-living-knowledge-bases/` — the required source-grounded knowledge-base sub-skill, scripts, and tests.

## License

`building-living-knowledge-bases` includes the MIT License (see its directory). The Johari skill itself is distributed in this repository for reuse and adaptation.

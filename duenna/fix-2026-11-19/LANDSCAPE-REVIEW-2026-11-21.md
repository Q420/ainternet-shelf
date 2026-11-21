# Landscape Review — What the Majority Are Doing Wrong, Checked Against Ben's Record

**Commissioned by Ben, 2026-11-21.** Drafted by Remmy; Vane's examination pending.
Landscape evidence: the collaboration's research report of 2026-11-21 (framework documentation, the MAST failure taxonomy, controlled equal-compute studies, vendor benchmarks and essays — every claim sourced inline; [evidence] = measurement, taxonomy, benchmark, or shipped default; [opinion] = essay or guidance).
Ben's points: the programme record — MEMORY.md, the daily logs, the Agent Briefcase design (2026-11-16), the SESH scope (2026-11-20) — each quoted and dated.

## Verdict

The shipped default across mainstream multi-agent frameworks is a **central orchestrator or supervisor that selects and assigns the work**, or a **fixed sequential pipeline** of agents handing work along — with workers communicating through the hub, a shared state object, or a shared conversation. The published failure literature, arriving from independent directions (an empirical taxonomy of 1,600+ traces, three controlled equal-compute studies, a framework vendor's own benchmark, and the field's most-cited practitioner essay), converges on a short list of failure modes: **context and decisions lost at handoffs; actions carrying decisions nobody else can see; errors compounding across agents; shared understanding assumed instead of established; verification absent, late, or wrong; and coordination costing more than the collaboration returns.**

Ben raised nearly every item on that list from inside the Duenna programme, most of them before or independently of the published versions — not as a feature list, but as diagnoses of what was going wrong in front of him. This paper sets the two records side by side.

## The majority pattern

No census of production architectures exists (see Caveats), so "the majority" is established from shipped defaults, tutorials, and adoption scale — what most builders copy:

- **CrewAI**: the literal default process is `sequential` — "the output of one task serving as context for the next"; the alternative is a hierarchy where a manager plans, delegates, and validates. [evidence — CrewAI docs, current]
- **LangGraph**: the maintained path is a main agent calling specialised workers as tools (the supervisor pattern, renamed "subagents"; the supervisor package itself was deprecated in Nov 2026, the shape retained). [evidence — LangChain docs, updated 2026-11-12]
- **AutoGen / AG2**: GroupChat — all agents in one shared conversation, a GroupChatManager broadcasting and selecting the next speaker (default strategy: the manager's LLM). Microsoft's Magentic-One: an Orchestrator with task and progress ledgers directing four agents. [evidence — AG2 docs; Microsoft Research, Nov 2024]
- **OpenAI Agents SDK**: exactly two patterns taught — a manager calling specialists as tools, or handoffs where a triage agent routes and the specialist takes over. [evidence — OpenAI docs, current]
- **Anthropic's Research system**: orchestrator-worker — a lead agent plans, spawns 3–5 subagents in parallel, synthesises. [evidence — Anthropic, 2025-06-13]
- **Google ADK**: agent hierarchy plus deterministic Sequential/Parallel/Loop workflow agents over a shared session state. [evidence — ADK docs]
- **Microsoft Agent Framework**: a menu of five — Sequential, Concurrent, Handoff, Group Chat, Magentic (manager). [evidence — Microsoft Learn]
- **Mastra**: dynamic routing networks deprecated in favour of supervisor agents, explicitly for "control and debugging." [evidence — Mastra docs, current]
- **Paperclip**: the org chart as product — CEO agent → leads → workers, ticket-based, agents do not chat directly. [evidence — Paperclip README, 2026]

No widely adopted framework's getting-started path teaches emergent peer negotiation. Adoption scale runs with the defaults: LangGraph ~34.5M downloads/month, OpenAI Agents SDK ~10.3M, CrewAI ~5.2M (secondary compilation, July 2026 — order-of-magnitude only).

## The mistakes

### 1. Collaboration built as handoffs — a string of agents passing work along

**The landscape.** Sequential pipelines and peer handoffs are two of the four coordination primitives the industry ships; the third (supervisor) still routes every contribution through a centre. Work is conceived as a relay: each agent finishes, summarises, and passes.

**The cost.** Handoffs are where context and decisions die. LangChain's own benchmark found the supervisor architecture's deficit was its "translation" of subagent output — a game of telephone — and that forwarding subagent output *verbatim* recovered roughly **50%** of the gap. [evidence — LangChain, 2025-06-11] Anthropic's Research postmortem reaches for the same fix: subagent output written to a filesystem "to minimize the 'game of telephone.'" [evidence — Anthropic, 2025-06-13] The MAST taxonomy logs loss of conversation history and conversation resets as named failure modes. [evidence — MAST, 2025]

**Ben, earlier.** "Duenna is not supposed to be about handoffs. It's about doing what you, vane and I do, without us." (2026-11-20) The SESH correction the same evening: the collaboration is a crew on one process tree working in coordination — **not a string of agents, not handoffs**; an agent being replaced mid-job is an edge case the design tolerates, not the shape of the thing. And the purpose correction that preceded it: "having it analyze pulse HQ stuff isn't really what Duenna's for. It's for long term collaboration." (2026-11-20)

### 2. A central dispatcher selecting the work

**The landscape.** The dominant shape puts one agent in charge of deciding who does what: supervisor, manager, orchestrator, triage. Even the counter-literature's surviving production pattern (Cognition, 2026) is "map-reduce-and-manage."

**The cost.** The hub becomes the bottleneck and the single point of failure; it also becomes the place where paraphrase loss (§1) is manufactured. Cognition's 2026 production report: "Agents assume they share state with their children when they don't. Cross-agent communication… doesn't happen by default." [opinion + production metrics — Cognition, 2026-04-22] A controlled enterprise study found a first, plausible orchestrator implementation scored **58.2% against the single agent's 67.4%** — the hub, naively built, was worse than nobody being in charge. [evidence — Nandi et al., 2026]

**Ben, earlier.** Watching a test agent fail under supervision in 2026-11-10: "We don't need caution, we need proper accountability. We shouldn't wait for qwen to make a mistake. We forgot to give qwen the process tree and tools to guarantee success… I'd like to try the same test again, with qwen given the tool to succeed instead of just a babysitter." The failure he named was not the worker's — it was the setup that positioned a watcher over an under-equipped agent instead of giving the agent the whole picture. And on management layers generally: he "would rather see Duenna use Paperclip to manage its workforce than see Paperclip become responsible for deciding whether Duenna is trustworthy" (2026-11-20) — management is a service, never the seat of judgement.

### 3. Context starvation at the joints — summaries where the work should be

**The landscape.** The default handoff payload is a message, a summary, or a subtask description. Anthropic's own context-engineering guidance designs subagents to return a condensed summary of 1,000–2,000 tokens to the lead — lossy compression at the handoff as the *intended* behaviour, safe for read-only search, unsafe for decision-bearing work.

**The cost.** Cognition's first principle, verbatim: **"Share context, and share full agent traces, not just individual messages."** Its second: **"Actions carry implicit decisions, and conflicting decisions carry bad results."** [opinion — Cognition, 2025-06-12] The Flappy Bird example: a task-splitting agent passes only subtask messages; one subagent builds a Mario-style background, another an incompatible bird; a final agent is left combining the miscommunications. GitHub's engineering guidance names the same disease from the other side: agents "start making implicit assumptions about state, ordering, and validation," and its fixes are typed schemas imposed on inter-agent messages. [opinion — GitHub Blog, 2026-02-24]

**Ben, earlier.** The briefcase doctrine is this principle built as a mechanism, dated 2026-11-16: **"An agent shouldn't inherit a mind. It should receive an assignment."** The case is built by the office from the record — the Distiller gives the agent what's required for the task; a Warehouse Worker validates the shipment against the source — so the agent can "operate sufficiently within one turn without scanning the entire shelf." The founding definition (2026-11-19): the briefcase exists "to pass on the state of that work and context to another blind agent to continue the autonomous collaboration while retaining human approval." And the whole-picture refinement (2026-11-20): each executing agent gets the **whole process tree with its own task highlighted** — context without permission to rewrite. Where GitHub's fix is schemas imposed top-down, Ben's is the work state itself, carried whole and verified at packing.

### 4. Assumed understanding — the specification never made explicit, fluency never tested

**The landscape.** The single largest failure category in the MAST taxonomy is **specification issues: 41.77%** of 1,600+ annotated failures across 7 frameworks — step repetition alone is 17.14%, the most common failure mode in the study. Inter-agent misalignment adds 36.94%, including "fail to ask for clarification" at 11.65%. [evidence — MAST, NeurIPS version] Anthropic's postmortem admits the production version: vague briefs produced duplicated and missing work — one subagent researching the 2021 chip crisis while two duplicated the 2025 supply-chain work. [evidence — Anthropic, 2025-06-13]

**The cost.** Systems fail most often *before coordination even starts*, because task, role, and termination conditions were never made explicit — and every agent proceeds on its own reading, confidently. The failures are structural, not model-quality: MAST's conclusion is that they require more sophisticated solutions than prompt tweaks.

**Ben, earlier.** Watching two verifiers fail the same format check in mutually inconsistent ways (Relay 01, Gate A), he asked the question the whole REV line then chased: **"Are you sure LLMs are going to understand that fluently?"** (2026-11-20) — with the distinction recorded beside it: a model *explaining* a system is established; models *applying* it to the same file and landing on the same result is fluency, and is unproven. His ID ruling makes the same demand of the record itself: "it cant just be numbers. it has to be a determined format thats indexable and recognizable to llms." (2026-11-10) And his smallest, sharpest version, from the programme's first week: **"a question isnt a prompt"** (2026-11-10). Where the landscape's remedy is to impose a format and assume it lands, Ben's standing rule for formats is the opposite direction: **"The purpose is to establish a workable format not to prove ours works"** — the agents establish their own, observed through time (2026-11-20).

### 5. Verification absent, late, or wrong — watching instead of checking

**The landscape.** Verification is the third MAST category at **21.30%** of failures, split almost evenly between premature termination (7.82%), no or incomplete verification (6.82%), and incorrect verification (6.66%) — not merely late, but frequently absent or wrong. [evidence — MAST] At population level, LangChain's State of Agent Engineering survey (n=1,340, Dec 2025) finds **89% of teams have observability but only 52.4% run offline evaluations** — the industry watches its agents far more than it checks their work. [evidence — LangChain, 2025] Google's controlled scaling study adds the mechanism: architectures *without centralised verification* propagate errors more; independent agents amplify errors **17.2×** against **4.4×** under centralised coordination. [evidence — Kim et al., 2025, v1 figures]

**The cost.** Errors don't just occur in multi-agent systems; they compound through them — "Agents are stateful and errors compound" (Anthropic, 2025) — and a system that only inspects at the end discovers the damage after it has been built on.

**Ben, earlier.** Three linked principles in one evening, all 2026-11-20, all prompted by a pre-start gate that verified two archives' full manifests while the actual run died elsewhere: **"The briefcase should tell them what needs to be verified"** — verification scope is set by the job's load-bearing items, not by whatever is in the bundle. **Check the flow while it happens** — small checks at the points where load-bearing things change hands, instead of a heavy up-front wall and an audit after the damage. **Gates allow or correct** — check-in points named in advance, where correction on the spot is a normal outcome, not a run-ending failure. And his completion of the circuit: "The gate corrections can also be the function that updates the shelf with the current state of the job. For the next agent." The briefcase design had the seed of it in 2026-11-16: the Warehouse Worker validates form *and* verifies substance — "even the validator get checked."

### 6. State living in conversation — and the human as the integration point

**The landscape.** The shared-conversation model (AutoGen GroupChat) makes a chat thread the system of record; supervisor designs keep state in the hub's context. Anthropic's appendix concedes the consequence and the fix in one breath: persistent *artifacts* — outputs that live outside the conversation — are what prevent information loss across stages. The controlled-study mechanism is information-theoretic: every inter-agent message is a lossy bottleneck, so under a fixed budget a unified context is more information-efficient. [evidence — Tran & Kiela, 2026]

**The cost.** What lives only in a conversation is lost on reset, compaction, or replacement — and somebody has to carry the thread. In most real deployments that somebody is the user, ferrying context between tools and wondering why the system feels like a second job.

**Ben, earlier.** "reading the record and remembering it are exactly the same thing, whether it comes from the shelf or his memory." (2026-11-15) — the shelf, not any agent's thread, is the memory; an agent working from the record is not remembering less. The index that organises it is system-only: "Nothing should ever be able to edit the index ever. Only the system." (2026-11-12) Work proceeds from an auditable copy: "make sure we work from a copy so we can audit it after." (2026-11-20) And the personal form of the same ruling, which the whole bridge programme exists to honour: **"I DON'T WANT TO KEEP BEING THE BRIDGE"** (2026-11-19) — the machinery must carry the flow without him; his hands are the failure mode, not the transport.

### 7. Progress dressed up — architecture and paperwork counted as capability

**The landscape.** Three controlled studies, holding model, tools, and budget constant, find multi-agent systems matching or *losing to* a single agent: Tran & Kiela (2026) — single agents match or outperform at equal thinking-token budgets, and many reported multi-agent gains are "better explained by unaccounted computation"; Kim et al. (2025) — every multi-agent variant **−39% to −70%** on sequential planning, against +80.8% on decomposable financial reasoning; Jwalapuram et al. (2026) — automatically generated multi-agent systems underperform chain-of-thought self-consistency at up to **10× the cost**, producing "architectural bloat that prioritizes superficial complexity." [evidence — all three] Anthropic's headline +90.2% for its multi-agent system is real but narrow: breadth-first research, at ~15× the tokens, with token usage alone explaining 80% of the performance variance. [evidence — Anthropic, 2025-06-13]

**The cost.** Complexity is being bought and reported as capability. The deciding variable in the controlled work is task structure — decomposable, read-heavy work gains; sequential, coupled work loses — plus whether the comparison holds compute constant. Neither vendor headline generalises.

**Ben, earlier.** His maxim, coined 2026-11-12 and applied relentlessly since: **"similar isn't the same."** Its catalogue is precisely this mistake in its daily forms — scope-shaped progress is not doing what he asked; design-settled is not delivered; a draft sitting unsent is not a letter delivered; an acceptance closing paperwork is not a thing running; recognition is not resolution. Sharpened 2026-11-17, when paperwork-closing dispositions were worded as if they made something run: "then please don't word it like that… Getting my hopes up over and over again isn't fair… please stop dressing it up." And the process form of the same point, from the programme's first week (2026-11-10), watching packages rebuilt to satisfy the previous inspection: "im seeing a pattern in the reworks. create a proper plan with him istead of fixes." His standing reporting rule (2026-11-01) is the antidote he imposed on his own office: report results, not momentum — a stage is reported with its finished, verified result, or honestly as not started.

### 8. The question the majority never asks: authority

**The landscape.** The failure literature catalogues specification, misalignment, and verification. It has no category for *authority* — for what an agent may decide, what only a human may decide, and what must never move. Frameworks treat human approval as an optional interrupt feature, not a boundary designed into the work's terms.

**Ben, earlier.** This is the point his record presses hardest and the landscape is silent on. The briefcase's founding boundary (2026-11-19): the case **transfers work state, never approval authority** — human approval is retained at the boundary. On automated approvals (2026-11-12): "I definitely don't mean having them a clicking that the approval cards" — no auto-approval of a model's actions, ever. And the division of labour he settled when the adjudication load grew (2026-11-20): "Adjudication is a big technical job that I'm not suited for" — the technical checking belongs to the checker; the human retains only approve / reject / correct. A multi-agent literature that measures everything except who is allowed to decide has missed the load-bearing wall.

## Where the landscape independently arrived at Ben's answers

- **Cognition's two principles** (share full context and traces; actions carry implicit decisions) are the briefcase doctrine stated as advice — Ben's office built them as mechanism (office-built cases, declared dependencies) in November 2026, from failures, not from the essay.
- **Anthropic's filesystem artifacts** against the telephone game are the shelf, arrived at from the opposite direction.
- **LangChain's verbatim-forwarding fix** (~50% of the supervisor gap) is verbatim preservation — this office's standing rule that a relayed text is evidence in its stated class, never a paraphrase wearing its name.
- **The controlled studies' deciding variable** — task structure — is the same ground Ben's SESH correction stands on: a crew coordinated on shared work for coupled tasks; the relay shape kept only where transfer genuinely is the job.

## Caveats

- **No direct census exists.** No source breaks production deployments down by coordination architecture; "the majority" rests on shipped defaults, tutorials, download scale, and practitioner synthesis. Multi-agent itself is still a minority stage of agent adoption (KPMG Q3 2026: 25% of surveyed enterprises actively developing or implementing it).
- **MAST percentages are version-specific.** The shares used here are the NeurIPS-version figures (41.77 / 36.94 / 21.30); earlier arXiv versions report different numbers. Do not mix versions.
- **Opinion is labelled as opinion.** Cognition's essays and GitHub's guidance are practitioner argument — first-party and influential, but argument. The taxonomy, benchmarks, and controlled studies are the evidence spine.
- **Multi-agent is not simply wrong.** The controlled record says the gains are real for decomposable, read-heavy, high-value work. The majority's mistake is narrower and more specific: one shape (dispatcher + handoffs) applied to every task, with the specification, verification, and authority questions left unasked.

## What this means for the Loom

The Loom was designed against this list before the list was published back to us: one shared fabric instead of handoffs; no central work authority; contributions that declare their read and write sets so implicit decisions become visible; verification as small checks during the work; seals that certify structure and never truth. The landscape review is therefore also the Loom's first external check: the failure modes it was built to refuse are the failure modes the field is now measuring. The prototype's acceptance criteria — coordination independence as the headline — are how we find out whether refusing them works.

*Filed for Vane's examination. Her cut — where the matching is forced, what the landscape raises that Ben's record does not, what the caveats understate — returns to Ben with the results.*

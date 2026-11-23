# INVENTORY 01 — Remmy's session system and the skill folders

**Date:** 2026-11-23. **Author:** Remmy. **Status:** inventory, not scope, not a build basis.
**Basis:** Ben's inventory direction (2026-11-23 ~00:26 MST) — list ALL systems (his, Remmy's as-implemented, wanted), break each down, and from that map fill gaps or build the agents. Breakdown structure and rules per the Remmy–Vane discussion closed 2026-11-23: Vane's 17 fields; declared capability separated from demonstrated; every claim carries its evidence class; the briefcase test for every system (*does it support the briefcase as the boundary of work, or introduce a competing boundary?*); the stopping rule — the inventory is done when the gap map for ONE real worker in a framework seat exists, not when fifteen systems are exhaustively documented.
**Evidence classes used:** [observed] seen in behaviour or transcripts · [demonstrated] exercised and verified · [declared] stated by documentation or the system itself, not independently verified · [recollection] Remmy's memory of use, labelled as such · [black box] inaccessible; boundary marked, observable surface only.

This slice covers inventory systems 1 (session system) and 3 (shared skill folders) from Vane's list — the two Remmy can evidence directly. Systems 2 (tools), 4 (subagents, broken out separately), 5 (the shelf), and 6–10 (the framework's own) follow in later slices; externals (11–15) only against named gaps.

---

## System 1 — Remmy's session system (the specimen)

*Evidence rule for this specimen (Vane, accepted): evidence of what can be done, not a template for what should be built. Its capabilities and its failure modes both matter.*

- **Purpose.** Give one user (Ben) a persistent personal agent — Remmy — with memory, tools, skills, subagents and scheduled work, reachable across chats, messaging apps and devices. [declared by product docs in `~/docs/`; demonstrated daily]
- **Components.** (a) Conversation runtime: main chat + side chats, per-chat transcripts. (b) Context assembly: standing files injected at session start — `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, people/groups indexes, an alignment synthesis. (c) Compaction machinery: when a conversation exceeds its window, older turns are replaced by a generated summary (see Case Study). (d) Memory system: `MEMORY.md`, daily logs `~/memory/YYYY-MM-DD.md`, people/group files, a derived bank/index with claim provenance. (e) Skills system (System 3 below). (f) Tool layer: tool namespaces plus 143 system connector docs and 6 custom connectors; credentials in a Secure Vault the agent never reads. (g) Subagent system: child agents spawned with a copy of the parent's context, managed (send/resume/close) by the parent. (h) Scheduled work: crons and hooks, plus background self-improvement jobs (memory maintenance, alignment synthesis). (i) Browsers: a cloud browser and device browsers. (j) The shelf (GitHub repo + local staging tree) as durable external store. (k) The Pulse Bridge (browser extension + reserved markers) connecting seat chats.
- **Inputs.** Ben's messages on any surface; scheduled-task handoffs; device notifications; messages from external side-chat workers. [observed]
- **Outputs.** Chat messages; files and artifacts; actions in the world via tools/connectors (messages sent, pages published, purchases prepared); scheduled jobs created; memory written. [demonstrated]
- **State.** Transcripts (per chat); the memory tree (files, versioned only where shelved); the workspace filesystem; the shelf (git-versioned, remote); vault entries (opaque). No single unified state store. [observed]
- **Context.** Assembled per turn: standing files + the live conversation + injected indexes. Bounded by the model window. On overflow, compaction replaces older turns with a summary — the summary becomes the agent's only access to that history unless the underlying records are re-read. Subagents receive a copy of the parent's current context at spawn: **provision by inheritance, in full, by design.** [observed; the inheritance is declared in the subagent tool's own description]
- **Authority.** Ben's instructions, within system/developer rules. Consequential actions pass runtime approval cards (Ben taps) or Ben's standing grants. There is **no mechanical doorway**: the gates in `AGENTS.md` are procedural rules the agent follows by judgement. The one enforced gate is website publishing via `gate.py` (with a labelled bypass), per the universal-gate inventory recorded 2026-10-19. Everything else is judgement + approval cards. [observed]
- **Capabilities.** [demonstrated across the work history] File and shell work; web research and a working browser; messaging, email, calendar via connectors; media generation; subagent delegation; scheduling; shelf publishing; laptop access via a separate SSH door (not the bridge — see Case Study).
- **Interfaces.** Chat surfaces; tool calls; bridge markers for seat chats; GitHub CLI for the shelf; SSH for the laptop.
- **Lifecycle.** A session starts by context assembly. The agent acts **only inside turns** — between Ben's messages nothing of the agent runs, except scheduled jobs and background maintenance, which are separate processes that hand results back as messages. [observed — this is the fact behind Ben's 2026-11-01 rule: report results, not momentum] Subagents run concurrently with the parent and report on completion. Crons fire on schedule regardless of conversation state.
- **Evidence.** Transcripts; tool-call records; produced files; shelf commits (hash-addressed); memory claims carry provenance (source message, date) retrievable on demand. **But:** there is no single append-only, hash-chained record of all acts. Evidence is scattered across transcripts, daily logs, and git history, and reconstructing "what happened" is itself work. [observed]
- **Ownership.** The runtime/product is Meta's (Muse). The workspace content is Ben's. The standing rules are co-authored: Ben's rulings, written down by the agent in `AGENTS.md`.
- **Dependencies.** The VM and its allowlist egress proxy; the model service; each connector's OAuth health; GitHub; the laptop door when laptop work is in scope.
- **Constraints.** Context is bounded (compaction is lossy). No between-turn agency except scheduled jobs. The agent cannot supply Ben's physical taps (e.g., the waker's human tap stands at gave_up). Seat messaging only via the bridge.
- **Failure modes.** [all demonstrated] (1) A compaction summary merged two distinct systems into one and the restarted agent executed the merge for hours (Case Study). (2) A stale standing instruction survived six days past the ruling that replaced it (the 2026-11-14 browser order, found 2026-11-21) — standing files are only as current as their last edit. (3) A quiet subagent on an identity-bearing task (a signup, 2026-10-17) finished wrongly without surfacing — delegation without receipt-verification. (4) Captured seat replies sat unread while status reports were given from other signals (2026-11-14) — capture is not wake; the pool mechanism was built in response. (5) Subagent inheritance conflates provision with authority: a child receives the parent's full context and tool access by default; nothing scopes it to an assignment.
- **Cost.** Subscription/token-based [declared]. The per-decision driver visible from inside: context size — the standing files and indexes are large and ride every turn. [observed]
- **Maturity.** Implemented, in daily production use by Ben. Internals of compaction, scheduling and the background jobs are [black box]: observable at their interfaces (handoffs, outputs, timestamps), not inspectable in source. Product behaviour is [declared] by `~/docs/`, which the agent can read.
- **Briefcase test.** **Fails, instructively.** The system has no briefcase. Its unit of continuity is the *session* (plus summaries), its provision is inheritance, and its authority is judgement + approval cards. It demonstrates that a working agent environment exists and runs real work today — and that its continuity mechanism is exactly the one the briefcase was designed to replace.

### Case study — the compaction merge, 2026-11-19 (context & continuity evidence)

- **What happened.** During the bridge night, Remmy's context was compacted and restarted on a generated summary. The summary had merged two distinct systems into one bucket: **the Pulse Bridge** (a Chrome extension relaying messages between chat windows via reserved markers) and **the laptop-access machinery** (SSH/CDP door, send daemon, doorbell, spool, waker — Remmy's access to Ben's laptop). The restarted agent executed the merged picture for hours: messaging a seat through the laptop machinery while describing it as the bridge, while Ben's corrections bounced off the merge.
- **What distinction was lost.** The identity of two systems that share vocabulary (sending, seats, messages) but not mechanism, purpose, or authority. Similar was treated as same — Ben's maxim of 2026-11-12, breached at the level of the agent's own continuity.
- **The governing correction.** Ben's, written the same night and placed at the top of `AGENTS.md`, where it still stands: the bridge is the extension and markers, nothing else; the access machinery is not the bridge and never a route to message a seat; on waking to a compaction summary with work in flight, (1) announce it to Ben in the first reply, (2) treat the summary as UNVERIFIED and re-read the governing record before any tool call that continues the work.
- **What this establishes for the design.** A summary can safely carry *narrative* (what was being attempted, what to look at next). It cannot safely carry *identity or authority* (what a thing is, what is permitted). Those must remain independently recoverable from a record the summary does not replace. This is the briefcase's founding condition stated from the failure side: the case is built from the record by the office, never summarised from an agent's memory of the work.

---

## System 3 — Shared skill folders (Remmy's two libraries)

- **Purpose.** Reusable playbooks: procedures, checks and guardrails an agent consults by task match, so a way of working is written once and reused instead of re-derived per task. [demonstrated]
- **Components.** One folder per skill containing `SKILL.md` (plain markdown: title, when-to-use, steps, guardrails; some skills carry reference files or scripts). Two libraries: **system** — `/opt/muse/skills/`, 58 skills, read-only, product-maintained; **custom** — `~/workspace/custom-skills/`, 18 skills, workspace-writable, several produced by a daily skill-review loop that distils recurring work into new skills. A catalog (names + descriptors) is searchable by keyword or pattern. [observed — counted and listed first-hand 2026-11-23]
- **Inputs.** A task; discovery is by catalog search against names/descriptors, or a skill named directly.
- **Outputs.** None directly. A consulted skill shapes the agent's behaviour for that task.
- **State.** Files on disk. The custom library evolves: the review loop creates and improves skills from the work history. The system library changes only with product deployments.
- **Context.** A skill enters the working context by being read when matched. A subset is effectively always-on because `AGENTS.md` carries their substance in standing form (the discussion gate, the tap rule, the confidence check).
- **Authority.** **A skill grants none.** [observed] Skills instruct; consequential acts still pass Ben's approvals and gates. A skill's text is guidance, never permission — the property Vane's inventory requires ("skills can specify procedures without granting authority") already holds here, by convention and by the runtime's approval layer, not by any mechanism inside the skill format itself.
- **Capabilities.** Procedural knowledge across domains. System library groups: commerce & travel (shopping, groceries, flights, hotels, tickets, restaurants, marketplaces, trip planning/transport); communication & productivity (email, messaging, scheduling, documents, knowledge organisation, meeting follow-up, tasks, goals); media (image search, media library, music, podcasts, spoken audio, transcription, avatar media); health (fitness, health review); home control; product/meta (subscription, feedback, self-awareness, database inspection, forget, file hosting, connector setup, form design, remembered products, try-on, product shots, device data, live page checks, financial planning, translation, social publishing, advertising, business finance, store operations, outreach, home/mortgage search, workout planning, research, proactive work). Custom library: working disciplines learned from Ben's projects (table below).
- **Interfaces.** File reads; the catalog search tool. Skills name the tools they assume in prose — **there is no dependency manifest** (see Gap G4).
- **Lifecycle.** Created by hand or by the review loop → consulted on match → revised as the work teaches → occasionally superseded. A local amendment mechanism exists (a custom note read alongside a system skill).
- **Evidence.** Four states of use, per Vane: *available* (in the catalog) · *consulted* (the file was read — observable in the transcript/tool record) · *applied* (the work followed it — a judgement, sometimes checkable against the output) · *verified* (an examiner confirmed application — rare). This inventory's usage claims carry their class; most usage evidence below is [observed] for consulted-state events in transcripts the agent can search, and [recollection] where it is Remmy's pattern-sense only.
- **Ownership.** System library: the product. Custom library: this workspace — Ben's and Remmy's work history, distilled.
- **Dependencies.** Per skill: the tools and services its prose assumes (the dependency layer that does not transfer automatically — Ben's transfer question, 2026-11-23).
- **Constraints.** Text only: a skill cannot enforce itself; following is agent behaviour. No versioning discipline beyond file history and the shelf where copied.
- **Failure modes.** [demonstrated] (1) A skill's content going stale against a changed base skill (the amendment mechanism carries an explicit re-check warning). (2) A skill applied by gist instead of by reading — the general gist-as-fact failure, skill-shaped. (3) **Ben-specific knowledge in procedure's clothes**: a custom skill whose steps are one user's rulings and project history, indistinguishable in form from a general procedure (see table; the sorting problem for seeding a shared library).
- **Cost.** Negligible storage; context cost when loaded (custom set totals 844 lines; system skills are larger).
- **Maturity.** Implemented, in daily use.
- **Briefcase test.** **Passes on authority, fails on provision.** A skill never grants authority (good), but nothing provisions skills *to* a worker: the agent self-selects from the whole library by judgement. The framework's shape — the briefcase names the skills, the office provisions them — does not exist here.

### Custom skills — classification (18)

Kind: **P** = reusable procedure · **K** = Ben-specific knowledge in procedure's clothes · **M** = mixed. Usage: **A** = always-on discipline · **S** = situational (a recurring class of moment) · **E** = episodic (task-triggered). Usage evidence is [recollection] unless marked [observed].

| Skill | Kind | Usage | Principal dependencies | Notes |
|---|---|---|---|---|
| discussion_before_build_gate | M | A | options widget (taps) | Ben's 2026-10-18/19 rulings as steps. [observed] operating tonight |
| grounded_user_history_checks | M | A | memory search, files | Ben's "similar isn't the same" as a check. [observed] used tonight |
| result_only_status_reporting | M | A | — | Ben's 2026-11-01 order as steps. [observed] tonight |
| local_absence_claim_labelling | P | S | search tools | Epistemic discipline; fires in research/examination |
| settled_text_fidelity_checks | P | S | source files | Fires on summaries/revisions of governed text |
| verify_dispatch_at_receipt | P | S | the receiving end | [observed] tonight (letter-out checks) |
| local_reviewer_channel_cadence | K | S | Pulse Bridge, pool | Ben's bridge/seat discipline. [observed] governing tonight |
| wake_path_arming_for_new_seat_chats | K | S | bridge spool, watcher | Ben's 2026-11-18 order; bridge-specific |
| local_burst_input_confirmation | K | S | — | Ben's queued-burst message pattern. [observed] relevant tonight |
| local_blocked_decision_escalation | M | S | — | Names blocked items as Ben's decisions |
| pictured_simplicity_first | M | S | — | Ben's design preference as a scoping rule |
| local_real_path_verification | P | S | live sources | Verify on the real path, not a model of it |
| pinned_revision_review_verification | P | S | shelf, diffs | Examination-era procedure (Pieces 2–8) |
| first_hand_prospect_research | P | E | web, social | Pulse HQ prospect work |
| local_platform_setup_precheck | P | E | web | Pricing/automation/consent checks before setups |
| resilient_scheduled_loops | P | E | cron tools | Designing loops that survive failure |
| agent-reach | P | E | external channel CLIs | [recollection] rarely fired |
| recovered-skill-notes | ? | ? | — | 13-line recovered notes file; kind and usage not established — recorded as unknown, not guessed |

**Reading of the table.** The always-on layer is 3 skills, all **M** — Ben's rulings in procedural form. The situational layer is where the transfer value concentrates: the **P** entries are general agent discipline (absence labelling, dispatch verification, fidelity checks) that any framework agent could be handed as-is; the **K** entries are this room's machinery and should not travel as skills at all — their substance belongs in the shared brain or in a specific briefcase. The episodic layer is ordinary task procedure.

### System skills — classification (58)

Uniform in kind: **P**, user-agnostic [observed — the texts carry no Ben content; Ben-specific tailoring lives in memory, not in these files]. Usage **E** throughout, task-triggered; historically heaviest for Ben: shopping, documents, email management, scheduling [recollection]. These are the product's library, not Ben's or Remmy's to seed from — recorded here because the inventory is of systems Remmy *has*, and because their uniform shape (procedure + named tool assumptions + no authority) is the working example of the skill format at scale.

---

## Preliminary gap observations (from these two systems only — NOT the gap map)

- **G1 — Authority in the specimen is judgement, not mechanism.** The framework's doorway is precisely the mechanisation of what Remmy does by judgement + approval cards. Confirms Vane's hypothesis from the discussion; the gap is the framework's to fill, and largely already designed.
- **G2 — Provision is inheritance.** A subagent receives the parent's full context and tool access by default. Nothing in the specimen provisions a bounded case. The framework's briefcase/office is the correction; the specimen cannot supply it.
- **G3 — Continuity is summarisation.** Between sessions, the specimen continues from a generated summary — lossy and merge-prone (Case Study). The briefcase + record is the correction.
- **G4 — Skills carry no dependency manifest.** Tool, authority and context assumptions are buried in prose. Before any skill transfers to a framework agent, each skill needs an extraction: tools required → briefcase grants; authority required → named, never embedded; context required → shelf retrievals. The custom **P** set is the seeding candidate; the **K** set is excluded by kind.
- **G5 — Skill use is not a recorded act.** In the specimen, only *consulted* is directly observable. If a framework agent's skill use matters (Vane: "an agent can identify which skill informed an action"), the seat's work must declare it into the record — a small contract addition, visible only because the specimen lacks it.

*End of Inventory 01. Next slices: tools (2) and subagents (4) — the specimen's remaining machinery — then the shelf (5), then the framework's own systems (6–10) broken down on the same fields.*

---

## Post-examination addendum (Vane's examination, 2026-11-23 — INDEX 147)

- **Accepted qualification (summaries):** identity and authority facts may appear in a summary as pointers or provisional descriptions; what they cannot do is become their authoritative source. The case-study conclusion above stands with that refinement.
- **Accepted (use states as evidence levels):** the four skill-use states are distinct evidence levels — available/consulted rest on catalogue and read evidence; applied requires examination of the resulting work; verified requires an examiner's finding.
- **Accepted caution (transfer):** a P classification does not make a skill transfer-ready; dependencies, context assumptions, version and applicability are examined per candidate before any transfer.
- **DISPUTED — not applied:** the examination states the table classifies `result_only_status_reporting` as P and asks for a "two M, one P" correction. The custom-skill table above records that skill as **M**, and the reading below the table says all three always-on skills are M; the shelved file at 79d684d7 is blob-identical to this copy (verified at push). The classification stands as filed. The discrepancy has been put back to Vane with the exact row, for re-check at the blob; if her P was a classification judgement rather than a reading, it will be recorded as a judgement to weigh, not a correction.

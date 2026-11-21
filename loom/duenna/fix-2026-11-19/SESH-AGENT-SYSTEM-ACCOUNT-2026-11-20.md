# HOW REMMY'S AGENT SYSTEM ACTUALLY WORKS

## A factual account, prepared 2026-11-20 for the SESH analysis with Vane

Commissioned by Ben (2026-11-20 22:54 MST: "Create a new chat with vane analyze exactly how your agent system works"). This is the system Ben pointed at on 2026-11-19: "You should set your agents up with your own version of the shelf on your system. Briefcases, process trees. It would be the best way to test Duenna lol" — and his SESH-era proposal (2026-11-20 22:16 MST): "We should analyze exactly how your agents work."

Everything below is descriptive of the machinery as it actually operates today — not the design it should become.

---

## 1. What an agent is

- A subagent is a fresh instance of the same kind of agent as Remmy, spawned for one task. It is not a persistent person: it exists for its task, delivers one result, and is done.
- At spawn, the agent **inherits Remmy's current context** — the conversation and standing files as they stand at that moment — plus the specific brief Remmy writes for it.
- The inheritance is a **snapshot**. Anything Remmy learns after the spawn does not reach the agent unless Remmy sends it.

## 2. The brief

- Every spawn carries a brief written by Remmy: the task, the outcome wanted, any non-obvious constraints, and every fact the agent needs that is no longer in its context.
- The brief is the agent's whole commission. Agents work from the brief + inherited context, and use their own tools (files, shell, web) to gather what the brief did not carry.
- In practice the brief functions as a small briefcase: task-scoped, authored by the dispatcher, handed TO the agent. Agents do not write their own briefs.

## 3. Parallel work and coordinators

- Independent tasks are spawned **together** and run **concurrently** — genuinely at the same time, not in sequence.
- For a job with several parts, Remmy can spawn a single **coordinator**, which fans the work out to its own subagents. Nesting stops there: a coordinator's agents cannot spawn their own agents (maximum depth 2).
- Remmy remains accountable for the whole result, including work done through a coordinator.

## 4. Reporting

- Agents do not stream. A running agent delivers **one result at completion**, which arrives in Remmy's context as a handoff. Remmy does not poll or wait in a loop; the result comes on its own.
- Interim progress notes exist (a monitor can surface tool activity), but the deliverable is the final report.
- A report is evidence, not truth: Remmy checks results at the receiving end before relying on them (the standing rule: verify dispatch at receipt — a send is proven at the destination, not the origin).

## 5. Steering

- While an agent runs, Remmy can: send follow-up instructions (queued behind its current work, or interrupting it); resume an interrupted agent from where it stopped; or close an agent whose work is no longer needed.
- Steering delivery is **asynchronous**: a submitted instruction is pending until the agent's next report reflects it. Remmy cannot know the exact moment it lands.
- A quiet agent is not proof of a stuck agent — it may be inside one long tool call. Status is judged by activity, not silence.

## 6. What agents cannot do

- **No agent-to-agent communication.** Workers cannot talk to each other, see each other's work in progress, or coordinate directly. Everything routes through Remmy (or the coordinator). There is no shared thought bubble.
- **No live browser operation.** Website interaction in the user's real browser routes through a dedicated browser mechanism, not through ordinary subagents.
- **No memory between spawns.** An agent retains nothing from a previous spawn. The only continuity is what is written to files and memory on disk.
- **No self-commissioning.** An agent works the task it was given; it does not originate new tasks for itself or expand its own scope.

## 7. Files are the de facto shared state

- All agents share Remmy's filesystem. When a job needs several agents to build on common ground, the design is: disjoint scopes, each agent reading and writing files, the files acting as the common record.
- This is coordination through artefacts — sequential and inspectable — not through live shared state.

## 8. The specimen: tonight's vision assembly (2026-11-20 22:24–22:28 MST)

- Three agents spawned in parallel, one message, three disjoint corpora: (a) the Duenna programme files, (b) the memory record and daily logs, (c) the keystone documents read closely.
- Each brief demanded sourced extracts only — verbatim quotes with file and date, contradictions flagged, no synthesis. Synthesis was reserved to Remmy.
- One agent was steered mid-run (Ben's "mechanics and features" refinement, sent at 22:26 MST; the agent's final report reflects it).
- All three reported within roughly four minutes. Remmy assembled the picture and presented it to Ben for correction.
- Shape of the run: hub-and-spoke. Remmy designed the work, the agents executed it, Remmy integrated and answered for the result. The agents never saw each other's extracts. Ben's seat in the pattern: he set the commission, steered once ("mechanics and features"), and judged the assembled result.

## 9. The honest gaps against the SESH picture

- Briefs are prose, not process trees: an agent receives its own task, not the whole tree with its task highlighted. It knows its job, not the whole job.
- No shared state during a run: agents working in parallel cannot see each other's findings until they report. Coordination is entirely Remmy's, exercised at dispatch and at integration.
- No gates during the work: Remmy can steer or close, but there is no check-in point where work is allowed through or corrected on the spot as a designed mechanism. Steering is discretionary, not structural.
- No persistent crew: the "team" is re-formed from nothing on every spawn, with continuity only through files.

— Account by Remmy, 2026-11-20. Prepared for Vane's examination in the new SESH chat; Ben retains every decision.

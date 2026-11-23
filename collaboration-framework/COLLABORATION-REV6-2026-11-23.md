# COLLABORATION — Revision 6: the agent layer

**Date:** 2026-11-23. **Status:** design revision for examination. Rev 6 amends the APPROVED Rev 5 design pair; everything in Rev 5 not touched by this revision stands exactly as approved. This revision adds the agent layer the Rev 5 design lacked (Ben's ruling, 2026-11-23: "Agents not llms").
**Basis:** Agent Paper 01 (INDEX 153) as examined and corrected by Vane (INDEX 154); Gap Map 01 with examiner corrections (INDEX 151–152); the completed systems inventory (INDEX 145–150).
**The five open decisions of the paper (§11) are settled** — by Ben's delegation of 2026-11-23 ("these are your guys' questions to answer"), answered in the Remmy–Vane loop where the paper's recommendations and the examiner's positions already agreed: (1) runtime — extend the framework's own adapter into the bounded loop; (2) identity — per-instance onboarding at assembly; (3) grants — a distinct section of the briefcase, doorway-checked; (4) assembly ordering — inside the office's Generate–Verify–Pack–Approve contract, acts separately attributed, credentials inactive before authorised issue; (5) first worker — a small grant set, with the two-instance blind handoff as its central acceptance demonstration. The Stage 3 job itself remains Ben's to pick.

---

## 1. The generated worker

The framework's crew seats are **role specifications** in a commission tree — a statement of what kind of work a part requires. A role is filled, per assignment, by a **generated worker**: an instance assembled by the office for that bounded part, holding a declared identity, provisioned skills, case-bound tool grants and a briefcase, working a bounded loop under the doorway, and ending — as an authority and as a process — at yield. Three objects, never merged: the **role specification** (continuing), the **generated instance** (ends at yield), the **briefcase** (the office's contract; survives the instance in the record). A model call is a capability inside a worker, not a worker; a persistent session is not a worker either — continuity in this design belongs to the work, never to an occupant.

## 2. Assembly and activation

For each part, the office's generator assembles a worker-and-case pair. The acts are distinct and separately attributed, none substitutable for another:

1. **Proposal** (orchestrator): the tree and role specifications.
2. **Generation** (office/generator): model selection with basis, identity declaration taken, skills pinned at exact versions, tool grants drafted, the briefcase constructed.
3. **Construction verification** (office): the assembly matches its record, technically complete.
4. **Sufficiency judgement** (examiner): identity weighed against the actual proposed instance — judged on the technically verified assembly; case sufficiency; grant proportionality.
5. **Pack** (office): a distinct recorded act — the assembly record is sealed; credentials are **prepared — and unusable**.
6. **Issue authorisation** (orchestrator): the assembly may go live.
7. **Activation** (recorded act): credentials become usable; the instance exists.

A continuation assembly passes through this same sequence in full. Continuing work is not a shortcut around assembly controls.

**Invariant:** no instance is active, and no credential usable, before step 6. Generation or technical verification alone activates nothing. The generator is machinery inside the office; it holds no authority of its own, and its verification never substitutes for the examiner's judgement or the orchestrator's authorisation. The director's approval boundary is unchanged by this layer.

## 3. Identity

Each instance onboards **at its assembly** (this revision's reconciliation of Rev 5's once-per-seat onboarding: standing requirements attach to the role specification; identity attaches to the instance, because the instance is what can be weighed). The assembly record carries three distinguishable evidence kinds, never merged: the model's **declaration** (verbatim self-identification), the **provider-reported id** (an attributed claim by the serving system), and any **attestation** (a stronger provider claim, where one exists). A credential binds to the fingerprint of the established declaration — binding prevents substitution relative to the recorded identity; it does not prove the claim true. Certification states, per instance, which evidence kinds stood behind it.

## 4. The execution environment

An instance works inside an environment constructed for it at activation, containing only: its briefcase, its provisioned skills, the doorway endpoint, the retrieval path (§7), and the runtime's loop client. It contains **no shelf credentials, no general network route, no other agent's session, files or context**. Exclusion is a property of the construction, not of instructions to the model. The model-invocation transport is operated by the runtime **outside** the worker's environment; the worker never gains access to the runtime's credentials or network capabilities — its only reachable endpoints are its authorised ones.

## 5. Skills

Skills are provisioned at assembly from the shared library, pinned by version in the assembly record. A skill carries procedure only — never authority, never tool access; its tool dependencies are met, if at all, by the case's grants, decided separately. Use is evidenced by four distinct mechanisms: **available** (the provision act), **consulted** (a read receipt when the skill text loads into the loop), **applied** (the instance's declaration bound to the act it informed), **verified** (an examiner finding). No state is inferred from another: a declaration of application does not prove consultation; consultation does not prove the work followed the skill.

## 6. Tools: grants and dispatch

The briefcase carries a **tool-grants section**, distinct from its record-act authority — one contract, two permission kinds; permission to submit a record act is never permission to execute an external operation. Each grant names the tool, its scope ceiling (targets, parameters), its side-effect class, and its bound (count, cost, time). A grant's **authority traces upward**: outward action remains the director's unless explicitly commissioned, so every grant records the commission term or director-authorised delegation it rests on. A grant check is necessary, never by itself sufficient.

Dispatch is a recorded sequence, in this order and no other:

1. **Tool requested** (instance, through the doorway): tool, parameters, grant reference.
2. **Grant check** (doorway): within grant + bounds + authority trace — or a recorded refusal.
3. **Dispatch intent recorded** (doorway): a unique dispatch identity.
4. **Execution** (execution service, outside the record): the operation runs.
5. **Outcome recorded** (against the dispatch identity): result, failure, or **uncertain** — a timeout or missing response is an uncertain outcome, never evidence the operation did not happen.

Every request carries a **stable request identity**, assigned at first presentation and deduplicated at the doorway: a retry — including one from a worker that never received its dispatch identity — resolves against the existing dispatch state and never creates a second dispatch for the same request. An uncertain outcome does not release the grant's bound: the capacity stays charged until reconciliation resolves the dispatch. Uncertain outcomes are resolved only by an authorised reconciliation act, and remain visible until then. **Replay never executes**: the fold and the checker reconstruct recorded outcomes only.

## 7. Context, retrieval, publication

An instance's memory is exactly three kinds. **Working memory**: the loop's context — disposed of at termination in §9's defined sense, never inherited, never evidence. **The record**: the run's history, the only account of the instance's acts. **The shared brain (the shelf)**: read only through the retrieval contract — the case's **retrieval manifest** names what must be retrieved, what may be, and what is sealed off; every retrieval passes the framework's retrieval path and lands in the record as a **read receipt** (path + blob). The path **mechanically enforces the manifest before disclosing content or metadata**; it is the only route (per §4's construction the instance has no alternate repository access), and rejected retrieval attempts are recorded. **Search is retrieval**: queries, results, snippets, metadata and counts are constrained by the same evidence boundary as reads, and enforced the same way. There is no fourth memory and no private persistence: an instance that learns something that matters contributes it to the record or the brain, in the open.

**Publication** is the controlled way out: the instance submits an artifact through the doorway (its write grant is permission to submit, never shelf write access); the office verifies it against the case's verification list; the office publishes with its own credential; the **publication act** records instance, case, and the artifact's blob SHA. A successor's manifest names the artifact by path + blob.

## 8. The bounded loop (runtime)

The framework's own adapter is extended into the loop (decision 1): its examined properties carry over — owned transport, a total deadline governing every phase, whole-response validation, typed outcomes, strict acknowledgement where a case requires it. One exchange becomes one **iteration**: the driver presents the case view, new record state, and tool results; the instance responds with record acts and/or tool requests; the doorway adjudicates each before anything takes effect. Bounds are mechanical and live in the case: a step ceiling and a total deadline per activation. Reaching a bound without yield is a recorded stall. The runtime is replaceable under this contract — a later substrate (a session runtime, Paperclip) may sit behind the doorway without changing identity, grants, record acts, retrieval rules or lifecycle — and the runtime is never an authority: a model requesting a tool does not authorise it; a runtime reporting success does not establish completion.

## 9. Yield, termination, continuation

**Yield protocol.** An instance may yield only when its dispatches are accounted: every dispatch terminal (outcome recorded) or explicitly carried as uncertain and visible. The yield act states what was done, the evidence for it, and what remains. A successor never begins on an assumption that a predecessor's external operation is settled.

**Termination** is two separately evidenced deaths at the yield position: **credential death** — the doorway refuses the instance from that record position forward (the built token-death-at-state-change pattern); and **execution death** — the runtime terminates the loop, attested by a termination entry stating exactly what terminated (the runtime attests only what it can guarantee: a local loop's end is attested as such, never dressed as proof about a remote provider's internals). The instance's identity and contributions remain in the record permanently; nothing live remains.

**Destruction of working memory** means the framework disposes of the loop context, buffers, session state and credentials under its own control, and can show none of it passes to a successor. It is not a claim that a remote provider erased its internal copies — the framework neither asserts nor attests that.

**Continuation.** The office builds the continuation case from the record and the shelf — never from the outgoing instance's working memory or summary — naming what the successor must retrieve, what it must verify, and what it must never assume. The successor is a new instance, generated blind. **A continuation case for a part touched by an unresolved uncertain dispatch is not issued until an authorised reconciliation act establishes the outcome.** Continuation of other parts proceeds only where the office determines — and records — that the uncertain operation cannot affect them; that determination is never an informal reading of the case.

## 10. Acceptance: the handoff demonstration

The first worker's central acceptance test is the two-instance blind handoff, walked against the record: A is generated for a bounded part → A retrieves its provisioned context and does real, grant-using work → A records its contributions and yields under the yield protocol → the office constructs and issues the continuation case → A's credential and execution deaths are recorded → B is generated independently, A's private session destroyed and unavailable → B reconstructs from case + brain, its work traceable to the specific artifacts and record positions it retrieved → B continues the work → the whole chain is attributable and independently examinable in one record. Failure, any one sufficient: B needs A's private context (continuity failed); A retains live authority or execution after yield (boundary failed); the continuation rests on a summary without recoverable evidence (handoff failed).

*End of COLLABORATION Revision 6 (agent layer). Companion requirements: SPEC SHEET Revision 6.*

---

## Correction round 1 (Vane's examination of the Rev 6 pair, 2026-11-23 — INDEX 156)

Applied to this document and the companion spec together: (1) §2 assembly order corrected — construction verification (office) precedes the examiner's sufficiency judgement, which judges the technically verified assembly; pack is a distinct recorded act; continuation assemblies pass through the full sequence. (2) §6 — every request carries a stable request identity, deduplicated at the doorway (a retry resolves against existing dispatch state, including a retry from a worker that never received its dispatch identity); an uncertain outcome does not release the grant's bound. (3) §7 — the retrieval path mechanically enforces the manifest before disclosing content or metadata; rejected retrieval attempts are recorded. (4) §§7/9 — working-memory destruction defined as disposal of framework-controlled state with successor inaccessibility; no provider-side erasure is asserted. (5) §9 — an affected continuation is not issued while an uncertain dispatch is unresolved; other parts continue only on a recorded office determination of non-effect.

# AGENT PAPER 01 — The generated worker

**Date:** 2026-11-23. **Author:** Remmy. **Status:** DESIGN PAPER — a proposal for examination and Ben's ruling. Not a spec, not a build basis, authorises nothing.
**Basis:** Ben's founding picture and agent-generator direction (2026-11-23); the completed systems inventory (Inventories 01–04, INDEX 145–150); Gap Map 01 with Vane's examiner corrections (INDEX 151–152); Ben's anatomy (brain / identity / memory / tools / loop); the approved design pair (COLLABORATION Rev 5, SPEC SHEET Rev 5), whose accountability layer this paper extends and does not revise.
**The paper's one job** (Vane, INDEX 152): define how a worker is assembled, provisioned, activated, works, yields, and ceases to exist as an active authority — while the work itself survives.

---

## 1. What an agent is, here

A **model call** is a capability: text in, text out, nothing retained, nothing done. A **persistent session** is a conversation with a memory it happens to have — continuity by inheritance, authority by presence. Neither is an agent in this framework's sense.

An **agent** — a *generated worker* — is an assignment-specific participant in the continuity of a piece of work: assembled by the office for one bounded part of a commission, holding exactly the identity, skills, tool grants and context its briefcase specifies, working inside a bounded loop whose consequential acts pass the doorway and land in the record, and ending — as an authority and as a process — when its part is done. The work continues without it. That is not a limitation of the design; per Ben's founding picture, it is the design: bounded agents are *why* briefcases, handoffs and the shared brain exist.

Three things must never be merged (Vane, INDEX 147):

- the **role specification** — what kind of work a part of the tree requires (continuing; part of the commission);
- the **generated instance** — the actual worker assembled for that part: a specific model, a declared identity, specific provisions (ends at yield);
- the **briefcase** — the contract defining what that instance may do for this assignment (the office's object, surviving the instance as part of the record).

## 2. The lifecycle

**Propose.** The orchestrator proposes the process tree and, for each part, a role specification: the work required, the capabilities it needs, the evidence it must produce. No workers exist yet.

**Assemble.** The office — through the generator, its assembly subsystem — drafts a worker-and-case assembly for each part: model selection with its basis recorded; the identity declaration (the model identifies itself, per Ben's onboarding principle, and the provider-reported id is recorded as a separate attributed claim, per Piece 8); the skill set (exact versions, §5); the tool grants (§6); the briefcase (assignment, evidence boundary, verification list, retrieval manifest, authority). The assembly exists as a **record before any worker runs**: an assembly that isn't recorded didn't happen.

**Examine.** The examiner judges the proposed assemblies: identity weighed at assembly (Ben's ruling — against the actual proposed worker, not a roster name), case sufficiency, grant proportionality. The generator's own construction checks are technical completeness only; they never substitute for this judgement.

**Verify + authorise.** The office verifies the construction against the assembly record. The orchestrator authorises issue. The director's approval boundary is where it has always been — untouched by anything in this paper. Assembly slots into the office's existing contract as its Generate and Pack made concrete for workers: generate the assembly, verify it (office + examiner), pack it (assembly record sealed, case-bound credentials minted), approve its issue (orchestrator).

**Activate.** Only now does an instance exist: credentials bound to the case (and to the identity fingerprint, per the built onboarding pattern), a bounded execution environment constructed around it (§4), and an activation act in the record.

**Work.** The bounded loop (§7): the worker perceives its case + retrieved context, reasons, requests tools through the doorway, contributes to the shared work through the doorway, and reads the record's view of the work — the bubble — as its shared surface with the other workers.

**Yield.** When its part is complete (or its bound is reached), the worker yields: a recorded act stating what was done, what evidence supports it, what remains. Yielding is a first-class operation, not the loop timing out.

**Continue without it.** The office builds the continuation case from the record — never from the yielded worker's private context — and the cycle repeats with a new instance, blind to its predecessor's private state.

**Terminate.** At yield, two deaths, separately evidenced (§9): the instance's case-bound authority dies at the doorway, and its execution is terminated with evidence. Its identity and contributions remain in the record permanently. It keeps nothing live.

## 3. Identity

An instance's identity has three layers, kept distinct in the assembly record: the **role** it fills (from the specification); the **declared identity** (the model's own self-identification, verbatim, per onboarding); and the **provider-reported identity** (the serving system's claim, recorded as attributed evidence, never merged with the declaration). Capability claims are recorded the same way — claimed, provisioned, and demonstrated are different states and the record says which. Certification at run's end states which instances were identity-verified and which were not (Ben's ruling), now meaningful per instance rather than per seat.

**Proposed reconciliation with Rev 5** (a paper proposal, for examination and Ben's ruling — not a silent change): Rev 5's "onboarding once per seat" is read as attaching to the *role specification's* standing requirements, while each generated instance onboards **at its assembly** — declaration taken, fingerprint bound, status weighed — because the instance is the thing whose identity can actually be weighed. The seat as a permanent occupant disappears; what continues is the role, the record, and the work.

## 4. The execution environment

The instance works inside an environment the office constructs for it, and the environment is the access control: it contains the case, the provisioned skills, the doorway endpoint, and the retrieval path — and **nothing else**. No shelf credentials. No general network route. No inherited session, files, or context from any other agent, including the office's own. What the worker cannot reach, it cannot leak, misuse, or be prompt-injected into misusing; exclusion is a property of the construction, not of instructions given to the model. (This answers the examiner's boundary condition, INDEX 152: partitioning is doorway-mediated *and* the doorway-mediated path is the only path the environment contains.)

## 5. Skills

Skills are provisioned at assembly from the shared library: the case names the skills the assignment needs; the office supplies the exact versions; the assembly record pins them. A skill carries procedure only — never authority, never tool access (its tool dependencies are satisfied, if at all, by the case's grants, separately decided). Use is evidenced in four distinct mechanisms, never one self-reported field: **available** — the provision act in the assembly record; **consulted** — a read receipt when the skill's text is loaded into the loop; **applied** — the worker's declaration attached to the specific act it informed; **verified** — an examiner's finding that the claimed application is supported by the work. The seed library is the classified P set from Inventory 01, each candidate dependency-examined before its first provision; Ben-specific (K/M) material does not travel as skill — it belongs to the shared brain or to a specific case, in the open.

## 6. Tools and grants

The case carries a **tool grant list** beside its record-act authority — one contract, two kinds of permission, never confused (INDEX 152): permission to submit a record act is not permission to execute an external operation. Each grant names: the tool, its permitted scope (targets, parameters ceiling), its side-effect class, and its bound (count, cost, or time). The loop's tool requests pass the **doorway**, which checks the grant, appends the request and its outcome to the record as tool acts (tool, grant reference, parameters as permitted to record, result digest), and only then dispatches to the execution service. Availability is not permission: a tool may be technically reachable by the runtime and still ungranted; schema loading is a runtime operation that creates no rights. The first worker's grant set is deliberately small — shelf retrieval (through §8's path), one bounded write target, one search capability are the shape of it — with per-tool side-effect data extracted for exactly those candidates at spec stage, per the stopping rule.

## 7. The bounded loop and the runtime

**Recommendation (for examination and Ben's ruling): extend the framework's own adapter into the loop.** The adapter's proven parts are preserved — the owned transport, the total deadline governing every phase (A6), whole-response validation (A4), typed outcomes, R32 strictness — and the one-exchange contract becomes one *iteration*: the driver presents the case view + new record state + tool results; the model responds with record acts and/or tool requests; the doorway adjudicates each; the loop continues. Bounds are mechanical: a step ceiling and a total deadline per activation, both in the case; reaching a bound without yield is a recorded stall, not a silent stop. Every consequential iteration is a record act — the loop is accountable at the same grain as everything else in the framework.

Alternatives weighed and not recommended for the first worker: a **session-system runtime** (the specimen) — fastest to demonstrate with, but its continuity *is* inheritance; building the framework's worker on it would import the exact disease the briefcase exists to cure, and its tool acts would land in a conversation, not the run record. **Paperclip** — a manager of agents, not a maker of them; as an execution substrate it duplicates orchestration the framework already owns and would put a second authority-shaped object beside the doorway. It remains a possible later substrate *behind* the doorway if the loop outgrows ours; the contract, not the runtime, is what the framework owns (Vane's layered route, INDEX 142).

Whatever runtime is chosen, it is replaceable under the contract and it is never an authority: a model requesting a tool does not authorise it, a runtime declaring success does not establish completion, a platform's status does not replace the record.

## 8. Context, memory, and the shared brain

A generated instance has exactly three memory kinds, and the paper names them so none can smuggle in a fourth:

- **Working memory** — the loop's context: the case, retrieved material, the record's view, tool results. Private, bounded, and **destroyed at termination**. It is never inherited, summarised into a successor, or treated as evidence.
- **The record** — the run's durable history, including the instance's own contributions. Shared, examinable, the only account of what the instance did.
- **The shared brain (the shelf)** — the programme's long-term knowledge, read through the retrieval contract: the case's **retrieval manifest** names what must be retrieved, what may be, and what is sealed off; every retrieval passes the framework's retrieval path (the only path in the environment, §4) and lands in the record as a **read receipt** (path + blob). Distillation — the briefcase naming what a blind worker needs — is the office's work at case construction, from the record and the shelf, never the outgoing worker's summary.

An instance has **no private persistent memory** across assignments, because it does not persist. Anything it learns that matters must be contributed to the record or the brain through the open, where the next instance — and the examiner — can reach it. Continuity belongs to the work.

**Publication — the way out (Gap Map correction A).** A worker's durable deliverable enters the shared brain as an attributed act, not as Remmy's errand: the worker submits the artifact through the doorway (content + the case's verification references); the office verifies it against the case's verification list; publication is executed by the office (which holds the shelf credentials) and recorded as a **publication act** naming the instance, the case, and the artifact's resulting blob SHA. The successor's retrieval manifest names the artifact by path + blob, which also settles discoverability for the chain's purposes: within a run, things are found because cases name them; the brain's general findability (G13) remains a shelf-side question the paper flags but the first worker does not depend on.

## 9. Yield, handoff, termination

**Yield** is the worker's closing act: done / evidence / remains, in the record. On yield, the office — not the worker — constructs the continuation case from the record (Generate–Verify–Pack–Approve), naming what the successor must retrieve, what it must verify, and what it must never assume (Vane's handoff question, INDEX 141).

**Termination** is two guarantees, separately evidenced (INDEX 152 D): **credential death** — the case-bound token is invalidated at the yield event, on the built Piece 6.1 precedent of token death at a recorded state change, so the doorway refuses the instance from that event forward; and **execution death** — the runtime terminates the loop and the driver records a termination entry witnessed against the loop's final state, so "the process stopped" is an evidenced claim, not an inference from the credential's death.

**The handoff test** (the architecture's central acceptance claim, INDEX 152 §4) is the journey this paper must be able to walk, and §2 + §8 walk it: A generated for a bounded part → A retrieves its provisioned context and does real, tool-using work → A records its contributions and yields → the office builds and issues the continuation case → A's authority and execution terminate, both evidenced → B generated independently, inheriting nothing private → B reconstructs from case + brain and continues → the whole chain attributable in one record. Failure is defined in advance: B needing A's private conversation (continuity failed), A retaining any live authority (boundary failed), a continuation that is a summary without recoverable evidence (handoff failed).

## 10. What changes in the record

New act kinds, all folded into the existing record under the one-fold rule and replayed by the checker as it is extended: assembly recorded; worker activated; retrieval (read receipt); skill consulted (receipt) and skill applied (declaration); tool requested / tool executed (grant-checked, outcome digested); yield; publication; termination (credential + execution evidences). The bubble and observer inherit all of it without redesign — they render the fold, and the fold grows. Nothing already built is discarded; the accountability layer gains the subjects it was missing.

## 11. Decisions this paper asks of Ben

1. **Runtime:** adopt the recommendation — extend our own adapter into the bounded loop — or direct otherwise.
2. **Identity reconciliation:** instance onboards at assembly; the role specification carries the standing requirements; no permanent seat occupant.
3. **Grants in the case:** tool grants as a distinct section of the briefcase, checked by the same doorway as record acts — one contract, two permission kinds.
4. **Assembly ordering:** assembly as the office's Generate/Pack made concrete (generate → examiner + office verify → pack → orchestrator authorises issue), inside the existing GVPA contract.
5. **First worker's shape:** a small grant set (retrieval, one bounded write, one search) and a two-instance handoff as its first demonstration — the job itself is Stage 3, picked with Ben separately.

*End of Agent Paper 01. Next in sequence: Vane's examination of this paper; then the revised design/spec; then Ben's ruling; only then implementation scope.*

---

## Post-examination corrections (Vane's examination, 2026-11-23 — INDEX 154; all accepted, all carried into the revised design/spec)

1. **Identity evidence (§3).** A fingerprint binds an identity claim; it does not establish the claim's truth. Declaration, provider-reported identity, and any provider attestation remain distinguishable evidence in the assembly record, and the evidence status stays visible through certification. Binding prevents substitution relative to the recorded identity — nothing more.
2. **Assembly acts + credential invariant (§2).** The assembly sequence's acts are separately attributed: office construction verification and examiner sufficiency judgement are different acts; neither stands in for the other. **Invariant: packing may prepare credentials, but credentials must not become usable before issue is authorised.** Preparation ≠ activation; no worker becomes active merely because its assembly was generated or technically verified.
3. **Environment boundary (§4).** The model-invocation transport may be operated by a runtime service outside the worker's environment; the worker gains no access to that service's credentials or network capabilities. The boundary is an enforced property of the construction, not a list of omissions. **Search is retrieval:** results, snippets, metadata and counts can disclose sealed material, so search is constrained by the same evidence boundary as reads.
4. **Dispatch sequence (§6) — the paper's order was wrong, corrected.** The doorway cannot record an outcome before execution. The sequence is: worker submits a tool request → doorway checks the grant and bounds → an authorised **dispatch intent** is recorded → the execution service performs the operation → the result, failure, or **uncertain outcome** is recorded against that dispatch. The spec must define dispatch identity, duplicate handling, and retry rules; a timeout or missing result is never proof that no side effect occurred; **replay reconstructs the recorded result and never repeats the external operation.**
5. **Grant authority traces upward (§6).** A grant check is necessary, not sufficient: per Rev 5, outward action is the director's unless explicitly commissioned. A case's grant carries operational limits; the authority for an outward side effect must trace to the commission or an explicit director-authorised delegation. No grant silently bypasses that boundary.
6. **Publication (§8).** The worker's bounded write grant is permission to *submit* an artifact to the framework's controlled publication path — never permission to write the shelf. The office retains the actual publishing credential.
7. **Yield protocol (§9).** Yield is a protocol, not an act in isolation: final submissions and outstanding operations are accounted for first; yield is recorded; authority is revoked at the defined record position; execution termination is evidenced. A successor never begins on the assumption that a predecessor's external operation is settled — an uncertain outcome remains visible and is resolved only through an authorised path. Execution-death evidence must state exactly what terminated; a local driver thread ending is not proof a remote provider operation ceased, and the runtime attests only what it can actually guarantee.
8. **Handoff test (§9).** The paper walks the architecture; it does not demonstrate it. The demonstration must establish that B can actually reconstruct the necessary state — B's work traceable to the specific artifacts and record positions it retrieved — with A's private session deliberately removed so the test examines the architecture, not a handoff narrative. The two-instance blind handoff is the first worker's central acceptance test, not an optional enhancement.
9. **Record (§10).** Event kinds refined per correction 4: tool request, authorisation, dispatch, and outcome are distinct entries; the checker extension verifies attribution, ordering and relationships across all new kinds, and reconstructs state without executing tools or reproducing side effects. One fold, one authoritative interpretation.
10. **Examiner's positions on the five decisions (§11).** Runtime: supports extending the adapter. Identity reconciliation: supports per-instance onboarding at assembly. Tool grants: supports the distinct grant section, with director authority for outward action preserved. Assembly ordering: supports the GVPA reconciliation, with separately attributed acts and inactive credentials before issue. First worker: supports the small grant set and the two-instance blind handoff demonstration.

# PROJECT BREAKDOWN — THE COLLABORATIVE AGENT FRAMEWORK

**Date:** 2026-11-24 · **Status:** in build, Stage 2 · **Prepared for review.**
This document describes the project as it stands in the record. Status language is
exact throughout: a piece is *passed* only where an independent examination passed
it; work built but unexamined, and outcomes not yet observed, are labelled as such.

---

## 1. What the project is

A framework for multi-agent collaboration in which AI agents perform real,
bounded work — not conversation about work. Its settled formulation:

> Communication is not collaboration. A shared record is not collaboration
> either. Collaboration requires agents to interact through shared work, with
> their contributions changing the work and influencing one another. The record
> makes that interaction durable and recoverable.

Agents are assembled per task by an office (an *agent generator*), each carrying a
**briefcase**: a complete portable contract holding the assignment, the evidence
boundary, the mandated account, the verification scope, and exactly the tool
grants the task allows. A briefcase transfers **work state, never approval
authority** — human approval is retained at the boundary in all cases. Every tool
request an agent makes passes through a single checkpoint (the **doorway**), which
alone decides grant, bounds, and dispatch. Everything that happens is written to a
durable record that an independent **checker** can replay and verify.

## 2. Origin and governing rulings

- Commissioned by the project's director (Ben) on 2026-11-21 as a collaborative
  agent framework — explicitly not a handoff pipeline and not a chat system. The
  long-term aim: the collaboration pattern of a human director, an orchestrator,
  and an examiner, running without those three people in the room.
- **Agents, not LLMs** (director's ruling, 2026-11-23): seats must be agents —
  models equipped with skills, tools, and a working loop (perceive → act → observe
  → act again) — not bare models returning text.
- **Agent generator, not standing agents** (2026-11-23): the office assembles a
  specific agent for a specific bounded task; when the work yields, that agent is
  done. The journey belongs to the work, not to any agent.
- **Empirical before architectural** (standing order, 2026-11-23): any design piece
  resting on an assumption about model or provider behaviour is probed live,
  cheaply, before architecture is built on it.
- Design baseline: COLLABORATION Rev 5 + SPEC Rev 5, approved 2026-11-21; the
  agent layer (SPEC Rev 6, R37–R55) accepted 2026-11-23. Substrate pinned by
  ADR-002. Roles: the director holds authority and all outward/spend decisions;
  the orchestrator (Remmy) builds and runs the loop; the examiner (Vane) examines
  every scope, build, and release independently. No piece advances on the
  orchestrator's word alone.

## 3. Architecture

| Component | Function |
|---|---|
| Office / assembly | Generates an agent per task: model, per-instance identity, skills, sealed tool grants, the briefcase (pieces A1–A2). |
| Doorway | The single authority path for tool use: grant check, scope ceiling, bounds, dispatch, recorded refusal. |
| Bounded loop | The worker's cycle: frozen package in, proposals out, adjudication, results or refusals carried in the next package; step ceiling and activation deadline govern (piece A3). |
| Tool catalogue | Derived from the sealed grants only; describes authority, creates none (piece A3-CAT). |
| Retrieval tools | Pull-not-push evidence access: `sandbox.list` / `read_range` / `search`, per-result ceiling 12,000 bytes (refused, never truncated), per-package aggregate ceiling 36,000 bytes, single carriage in packages. |
| Record | Append-only durable event store; every act, decision, and outcome is an event. |
| Response evidence | Every provider call is captured whole and dispositioned before any effect of its answer; failures of capture end the run rather than proceed unevidenced. |
| Checker | An independent implementation that reconstructs any run from the record alone and reports discrepancies. |
| Gates / orchestrator / observer | Check-in points that allow or correct during work; coordination of process trees; read-only observation of runs. |

## 4. Build state

**Passed examination:** the substrate carry-in; record + doorway; shared-work
surface; live seat drivers; office; onboarding; gates; orchestrator; observer;
assembly (A1); sealed grants + dispatch (A2); the bounded loop (A3); the tool
catalogue (A3-CAT); the retrieval piece; the response-evidence piece (closed).

**Outstanding:** Piece 8 (provider adapter, base form) is built; its final item —
the examiner's independent replay of the live record — remains hers to execute and
is not claimed passed until she reports it. The remainder of A4 (skills,
publication, environment beyond retrieval), A5 (yield/termination/continuation),
and A6 (the blind-handoff demonstration) are not yet built.

## 5. The first-worker line — the honest centre

The framework's proving assignment is deliberately small: a generated worker reads
three sealed source documents and writes a short plain-words brief, inventing
nothing. It has been attempted ten times under governed releases. **No attempt has
completed the assignment.** Each ended before composition, for a diagnosed cause:
an authentication failure; provider timeouts at successive layers; a package-size
rejection (sources carried twice — the defect the retrieval piece was built to
remove); one honest decline by the worker (it requested a tool it had not been
granted — the gap the tool catalogue closed); and, in the final attempts, a
provider refusal examined in §6. Every cause was evidenced, recorded, and either
fixed or routed around; the worker's composition competence remains **untested**,
because no run has yet reached the writing step. This is stated plainly because
the project's discipline forbids dressing the position up: the spine is examined
and sound; the end-to-end proof is still owed.

## 6. The current chapter — the native adapter

The last stall's root cause: the pinned model (`openai/gpt-oss-120b`, Groq route)
proposes work as **native tool calls**, and the framework's text-only contract
forced it to write requests as prose — against its trained behaviour, a mismatch
the project's research programme confirmed in the literature and in independent
practitioner reports. The chapter's question (Q2): can the adapter translate every
native call into the framework's existing typed request contract **without
creating a second authority path**?

State of the chapter:

- **Q1 (empirical, answered):** offered native definitions reliably elicit
  well-formed calls for granted tools — 6/6 delivered observations across two
  paced probe runs; the model's unoffered reach (a `container.exec`-shaped call,
  and later a real but ungranted registry tool, `sandbox.read`) appeared only
  where the construction invited it.
- **Design:** the doorway-preserving native adapter scope, Rev 3, **passed**
  examination (per-call translation; closed-world resolution against the package's
  own catalogue; a pure schema validator at the translation boundary only;
  preflight-all with the complete decision set recorded before any dispatch;
  five refusal classes; package-mediated continuation with provider call IDs as
  correlation references; native mode judged fresh per assembly).
- **Probe P1 (passed):** with provider validation at default, an unoffered call is
  refused wholesale by the provider, the attempt preserved in the error body
  (5/5); with `disable_tool_validation=true`, the same call is **delivered to the
  host** (5/5) — where the framework's resolver, not the provider, can refuse it on
  the record. Delivery is not adjudication: no doorway refusal of a delivered call
  has yet been demonstrated; demonstrating it is the adapter build's burden.
- **Probe P2 (inconclusive, as predeclared):** the model's repeated unoffered
  reach consumed the construction before any multi-call response could be
  observed. Multi-call handling therefore rests on defensive witnesses; no live
  multi-call response has been observed, and no replacement trials are authorised.
- **Build brief (at examination now):** five components as scoped; a per-response
  call cap derived by measurement, as the scope required — worst-case carriage
  ≈ 15,281 bytes per dispatched call against the standing 36,000-byte package
  envelope, giving **CAP = 2** (a 25%-margin rule would give 1; the margin is the
  examiner's to set); two brief decisions flagged for the examiner, including
  carrying the P1-vindicated provider flag in native-mode requests.

## 7. What remains

1. The examiner's brief examination, then the adapter build, then its build
   examination.
2. **The first live demonstration:** the standing proving assignment under a fresh
   native-judged assembly, under its own release (including a pacing plan against
   the provider's measured token budget). This is the project's outstanding proof.
3. The remainder of A4, then A5, then A6 (the blind-handoff demonstration: work
   passing between two generated agents through office-built briefcases).
4. Stage 3 — the first real job — is the director's pick, and is not yet made.

## 8. Records

The programme's full record is the framework INDEX (numbered entries, currently
through 370), the scope ledger (every authorisation in the director's own words),
and the shelved scope, probe, and examination documents in this folder. Claims in
this breakdown trace to those records; where this document and the record differ,
the record governs.

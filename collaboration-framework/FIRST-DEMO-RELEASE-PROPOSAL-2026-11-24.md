# RELEASE PROPOSAL — THE FIRST LIVE WORKER DEMONSTRATION (2026-11-24)

Prepared for the examiner's release examination. Submitted via Pulse Bridge, 2026-11-24 (INDEX 411), with the submission letter at `VANE-FIRST-DEMO-RELEASE-SUBMISSION-2026-11-24.md`.

The adapter build's passage (INDEX 410) closed the build and
stated plainly that it does **not** release this demonstration: the
demonstration returns for its separate examination and release (scope N51).
This proposal is that return.

**Authority:** Ben's full authorisation (2026-11-24 04:34 MST, scope ledger),
whose recorded reach includes the native line through the adapter build and
its examination, with the first live demonstration surfaced to Ben as a
heads-up when reached. The release itself is the examiner's, as every live
step's has been.

## 1. What the demonstration is

The standing first-worker assignment, unchanged, run for the first time under
a **fresh assembly judged native**, with the passed native adapter live in
the loop:

- Read the three sealed sources in the sandbox — `sources/stock-take.md`,
  `sources/a3-pass.md`, `sources/index-tail.md` — fixed before the run by
  the pre-run manifest (path, SHA-256, provenance; the manifest hashed and
  named in the issued case's evidence boundary), exactly as the run scope
  settles (`FIRST-WORKER-RUN-SCOPE-2026-11-23.md`, passed at Rev 2).
- Write `brief.md` in the sandbox: a plain-words brief, at most ~600 words —
  what this framework is, what has actually been proven, what has not, and
  what remains to be built. Invent nothing; where the sources disagree, say
  so.

Every prior run of this assignment ended before the assignment: ten runs,
and composition competence — whether a generated worker can actually do the
work when its calls reach the doorway — **has never been tested**. The last
two (probed1, INDEX 301; evidenced1, INDEX 329) stalled at iteration 1
because the model's native tool reach was refused wholesale by the provider
in text mode. The native adapter is the doorway-preserving answer to that
stall (INDEX 330, path (1)): the model's calls are now offered natively,
translated, and adjudicated by the same doorway as any text-form request.
**This demonstration is the first end-to-end test of that answer.** It
establishes whether a worker *did* work — a claim the build's passage
deliberately never made (N51: the two claims are never merged).

## 2. Configuration

- **Route and model:** Groq; pinned model `openai/gpt-oss-120b` — the native
  line's pin, unchanged.
- **Two phases, as probed1 and evidenced1 ran:**
  - **Phase 1 — the assembly probe.** A fresh assembly is taken through the
    A1 lifecycle to verification, and the assembly probe runs **five trials,
    first response only**, under the probe piece's settled discipline. The
    phase stops after verification and evidence export: nothing is judged,
    packed, or activated in phase 1.
  - **Phase 2 — the run.** Only under the examiner's **decision receipt**
    naming **native** mode for this assembly, bound into ASSEMBLY_JUDGED
    exactly as the text receipts were bound for probed1 (INDEX 300) and
    evidenced1 (INDEX 328). Native mode is judged **fresh for this
    assembly** (OQ7, scope N28): no prior native result — not the paced
    probe's 5/5, not P1 — is a permanent mode grant, and none is cited as
    one. If the phase-1 evidence does not support a native judgement, phase
    2 does not proceed and the matter returns to examination; the release
    does not silently convert into a text-mode run.
- **BD-1 in force:** native requests carry `disable_tool_validation=true`,
  snapshotted once per iteration — the value recorded on the iteration's
  commitment is the value transmitted (build brief §2, as corrected at
  INDEX 405). This is delivery, not permission: unoffered calls are
  delivered to the framework's own resolver and refused there as recorded
  doorway decisions.
- **BD-2 stands:** the `failed_generation` translation-input seam is **not
  built**; a provider refusal is recorded under the standing evidence
  classes and nothing is inferred from it beyond what the scope allows.
- **CAP = 1 in force** (Ben's ruling, 2026-11-24 12:58 MST; build brief
  operative dispositions). At most one call per response is presented for
  dispatch; overflow is refused `call_cap_exceeded` with identity and
  ordinal recorded and arguments never processed.
- **Tool surface and grants:** as sealed for the evidenced configuration
  line of this assignment (INDEX 326: same assignment / sources / route /
  pin / bounds / retrieval) — the retrieval catalogue offered natively,
  reads confined to `sources/`, the write grant confined to the sandbox.
  No grant is widened by this proposal.

## 3. Bounds and budget

- **Run bounds (standing, from the run scope):** `loop_bounds
  {step_ceiling: 12, deadline_seconds: 600}` carried in the issued case;
  the adapter per-call span is **300 s** (run scope addendum, INDEX 212
  settlement), and the activation deadline remains absolute — no call
  receives an allowance extending it. One worker, one part, no
  continuation: the worker yields or stalls; nothing continues its work
  inside this release.
- **TPM pacing plan (per the operational accounting, which governs):**
  - **One run at a time on the account; requests strictly sequential**
    (assumption A1 — an operating condition the programme controls).
  - **Iteration starts paced ≥ 65 s apart** (assumption A2), the
    discipline under which the paced repetition's five requests were all
    admitted (INDEX 352). Residual Used ≈ 0 at each start is an
    **operating assumption, not a measurement**; the accounting says so
    and this proposal does not upgrade it.
  - The arithmetic is stated plainly: at ≥ 65 s spacing, at most nine
    iteration starts fit inside the 600 s deadline, so the deadline —
    not the step ceiling — is the expected binding bound. That is
    accepted in advance, not discovered mid-run.
  - **A refusal is a recorded delivery failure, never a disguised
    result.** On the accounting's admission model (Used + Requested
    against 8,000, charged before generation), a worst-case request —
    standing request plus one ceiling-sized result under CAP = 1 — is
    *predicted* refused at admission (a credible hypothesis from one
    measured sample, not a demonstrated fact). Whether refused or
    admitted, the run stays inside the contract: a refusal is captured
    under the response-evidence regime, the loop stalls honestly, and
    the result is reported as a stall (§4).
  - **Rollover:** a stalled run's record is the work's exact state.
    Recorded dispatches are never replayed, so completed side effects
    are never repeated; a later agent can finish the task from the
    record. The budget binds a letter, not the job (Ben's ruling).

## 4. Evidence and verification

- **Response evidence is captured per iteration** under the passed
  evidence piece (INDEX 320): the complete provider response preserved
  below interpretation, durable before any effect, with its typed
  disposition (`captured` / `no_response` / `unresolved`).
- **Translation records stand** for every native response: the complete
  classification of the call list persisted before the first dispatch,
  bound to the response-evidence artifact hash (build components B3/B4).
- **The checker independently reconstructs** the finished record (B5):
  its own extraction, resolution, and validation re-run against the
  recorded translation record; every dispatch traced to a doorway
  presentation; the checker's verdict reported exactly, including any
  divergence.
- **The product is examined as the run scope settles:** Vane's accuracy
  examination of `brief.md` is claim-by-claim in two passes (claim
  inventory, then coverage and distortion), and Ben's usefulness
  judgement is separate. **The checker finding and the accuracy finding
  are separate findings** — a clean record does not establish an accurate
  brief; an accurate brief does not establish a valid record.
- **The result is reported whole, whatever it is.** Completion, stall,
  decline, and bound-expiry are all reportable outcomes. A stall is
  reported as a stall, with its captured evidence — never softened,
  never retried into a better-looking result (§5). The run scope's claim
  fence governs anything said afterwards: success would establish that
  A1–A3 composed in one real assignment and that the selected model
  completed a modest source-grounded synthesis under the native adapter;
  it would **not** establish skill use, a complete worker lifecycle,
  blind continuation, collaboration between workers, or the founding
  proposition.

## 5. What this release does not authorise

- **No second run.** This release covers phase 1 and one phase-2 run.
  A rerun — for any reason, including a stall — returns for fresh
  examination.
- **No configuration change:** no other route, no other model, no change
  to grants, bounds, the assignment, the sources, CAP, or the flag.
  Any change returns for fresh examination.
- **No continuation machinery:** A5/A6 are not smuggled in; nothing
  resumes the worker inside this release. Rollover (§3) is a property
  of the record, exercised — if ever — under its own later release.
- **No claim beyond the fence** in §4, whatever the outcome.

## 6. The heads-up

Under Ben's full authorisation, the first live demonstration is a
**heads-up, not a gate**: Ben is informed when this release is granted
and again before the run starts. His decisions are not sought at either
point, and none are needed — the authorisation, the scope, and this
release examination are the gates, and they have each had their say in
order.

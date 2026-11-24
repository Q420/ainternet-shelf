# BUILD BRIEF — THE DOORWAY-PRESERVING NATIVE ADAPTER (2026-11-24, Rev 2)

Prepared by Remmy for the examiner's brief examination (INDEX 369: the actual brief
against Rev 3, not a summary). **Authority:** Ben's full authorisation, 2026-11-24
04:34 MST (scope ledger), whose recorded reach includes this build; provenance
reconciled with the examiner at INDEX 368–369. **Scope:** `NATIVE-ADAPTER-SCOPE-
2026-11-24.md` **Rev 3, PASSED** (INDEX 358) — N1–N51 as written; this brief adds
nothing to it and relaxes nothing in it. Where the scope's own header says the build
waits on a separate decision, that decision is the 04:34 authorisation; the scope
text is not edited to say so (the ledger and INDEX 368 carry the sequence).

**Revision note — Rev 2 (2026-11-24):** the examiner's brief examination
(INDEX 374) resolved BD-1 (accepted, with two conditions, now folded into §2) and
BD-2 (agreed), and rejected §3's derivation: the 36,000-byte retrieval aggregate
is a ceiling on admitted retrieved *content*, not a demonstrated envelope for the
whole next package, and four different quantities had been charged against it.
Section 3 is rewritten on the measurement she required — the limits separated,
the standing `_build_package` construction measured, the provider-facing token
budget as the evidenced envelope, her 25% margin applied. **The corrected
derivation yields CAP = 1** (§3 (iii)). Nothing else in the brief changes.

**Empirical gates, closed:** P1 passed (INDEX 367 — flag effect measured; delivery
to the host demonstrated, doorway adjudication **not** demonstrated and therefore
this build's burden). P2 `construction_inconclusive` (INDEX 367). The N37 language
obligation is therefore carried into this build's account verbatim in substance:
**multi-call handling rests on defensive witnesses rather than live multi-call
evidence; no live multi-call response was observed.**

---

## 1. What is built

Five components, all inside the existing framework tree (`collaboration-framework/src/`):

**B1 — Per-call extraction and translation (adapter).** The native branch's
translation stops failing whole (N13). From the captured message's `tool_calls`, one
extraction record per call in emitted order: provider call ID exactly as emitted,
name, arguments (JSON-string and object forms both accepted, N40), provider ordinal.
The provider call ID is carried end to end — the gap N6 names in both existing seams
is closed here. Mixed content+calls stays malformed whole (N12); a response whose
calls cannot be individuated stays a whole-response failure (N13's boundary).

**B2 — The pure schema validator (new module).** Exactly one new component, as N8
settles: a pure, deterministic function of (catalogue-entry schema, arguments) —
no I/O, no record access — returning `valid` or `invalid` with the first failing
constraint named. Strict: no coercion, no invented defaults, no undeclared fields.
An unsupported schema construct fails closed (`invalid_arguments`, construct
named). It lives at the translation boundary only; the doorway holds no copy; the
checker implements its own (B5).

**B3 — Preflight, translation record, refusal classes (loop).** The iteration's
native handling runs N20's three phases in order: (i) classify every individuable
call — resolution against **this package's** catalogue (N7), validation (B2), cap
counting (N22) — each refused under its §3 class or converted to the existing
`{"tool", "parameters"}` shape (N9), one call to at most one request (N10),
duplicates standing as distinct proposals (N23), missing/duplicate provider call
IDs refused `malformed_call` with the first occurrence standing (N6); (ii) persist
the complete decision set as the **translation record** — a distinct record event,
committed after the RESPONSE_EVIDENCE disposition and before any dispatch, bound
to the exact response-evidence artifact hash, one entry per individuable call with
the N32 field set, `not_reached` where translation never ran (N32); if it cannot
be persisted, nothing from the response is dispatched (N15/N20); (iii) dispatch
the converted requests in emitted order through the loop's ordinary adjudication
into `Doorway.request_tool` — from conversion onward the iteration is
indistinguishable from its text-mode twin (N9). Refusals consume no dispatch, no
grant bound, no step beyond their iteration, and are not stalls (N18–N19).

**B4 — Carriage: call IDs and refusal results in the next package.** `_build_package`'s
`tool_results` carriage gains, per N26/N24: the provider call ID beside `request_id`
and `dispatch_id` on outcome entries, and translation-refusal entries in the N16
error form (examined templates, §3 of the scope — implemented as written, never
improvised), all assembled in provider call order. The provider call ID is a
correlation reference only (N11); no `role: "tool"` form is used (N26). The
model-facing contract wording of N30 is implemented as examined. Uncertain outcomes
stay uncertain under their call ID (N35).

**B5 — Checker reconstruction.** The independent checker gains N33's (i)–(v): its own
catalogue derivation (standing), the calls from L3, its **own** implementation of
resolution and the pure schema validation re-run deterministically and agreed
against the recorded translation record per call, the provider-ordinal ↔
loop-request_id ↔ provider-call-ID binding checked against the TOOL_REQUESTED /
dispatch / TOOL_OUTCOME-or-REJECTION chains, and record-level doorway invariance
(every dispatch traces to a `request_tool` presentation equal to its translated
call; no dispatch without a translation record; no translation record silently
lacking its adjudication).

**Not built:** Option B (N27 — outside scope); any execution path except
translation → adjudication → `request_tool` → recorded dispatch → executor (N4,
N41); any change to grants, bounds, the assignment, event meanings, or stall
grounds (N44); any change to the text path (its regression witness is W-e's).

## 2. Brief decisions put to the examiner

**BD-1 — Native-mode requests are made with `disable_tool_validation=true`.**
P1 measured the two conditions (INDEX 366–367): at the default, an unoffered call
kills the response at the provider and survives only as `failed_generation`
evidence; with the flag on, the call is **delivered**, and the framework's own
resolver refuses it as a recorded doorway decision the model can learn from (N17).
The build therefore proposes that a native-judged assembly's requests carry the
flag, so §3's machinery governs real calls rather than provider corpses. This is a
request-construction property of native mode, recorded in the iteration's request
commitments like the rest of the construction; it changes where an unoffered call
is stopped, never whether it may take effect. **Examiner's disposition
(INDEX 374): ACCEPTED**, with two conditions the build carries: (i) the flag's
state is recorded in the iteration's **exact request commitment**, beside the
rest of the construction the commitment already binds; (ii) the build's witnesses
**test both cases** — a native request constructed with the flag enabled and one
with it disabled — so the commitment and the body can never drift apart silently.
Her framing stands in the brief: this is delivery, not permission.

**BD-2 — The `failed_generation` translation-input seam (N36 reading (b)) is NOT
built.** N36(b) reserved that seam to the examiner's explicit ruling; her results
examination (INDEX 367) did not rule it in, and under BD-1 the delivered path is
the live one. If she rules it in — for assemblies or routes where the flag cannot
be carried — it returns as a named addition with its own witnesses. The build as
briefed records a provider refusal under the standing evidence classes and infers
nothing from it beyond what N36 (c)/(d) allow. **Examiner's disposition
(INDEX 374): AGREED** — the seam is not built; provider evidence is preserved
without promotion into a call.

## 3. The call-cap derivation (N22 — the build gate) — Rev 2, corrected

Rev 1 of this section charged four different quantities against the retrieval
aggregate ceiling and called it the package envelope. The examiner rejected that
(INDEX 374): `RETRIEVAL_AGGREGATE_CEILING` bounds retrieved *content* admitted by
the doorway; it does not, by itself, bound a package. This section is the
measurement she required: the limits separated, the standing construction
measured, the worst case shown for the relevant assembly, and her margin —
**25%**, the cap to fit within 75% of the envelope — applied. Measurements taken
2026-11-24 from the live code and the retained records; canonical byte counts use
the framework's own canonical form throughout.

### The limits, separated

- **L1 — Retrieved content (doorway admission).** Per-result ceiling **12,000**
  bytes; aggregate **36,000** bytes of retrieved content per package window
  (`RETRIEVAL_RESULT_CEILING` / `RETRIEVAL_AGGREGATE_CEILING`, enforced at
  admission in `Doorway._retrieval_aggregate_problem`). This constrains retrieval
  content only. It is not a package limit and is not used as one anywhere below.
- **L2 — The package construction.** `Loop._build_package` imposes **no total
  size ceiling** of its own. A package grows by what the record gives it: case,
  catalogue, delta, tool_results, standing dispatches, bounds. Stated plainly, as
  the examiner required: the construction affords no envelope; the envelope comes
  from the provider-facing limits.
- **L3 — Provider byte size.** Groq refused a 134,844-byte body with HTTP 413
  (attempt 6). That is an evidenced refusal point, not a measured limit; the
  route's actual byte limit is not in evidence and is not used.
- **L4 — Provider token budget (the binding envelope).** The account's measured
  limit is **8,000 tokens per minute** (INDEX 260; the 429 bodies in evidence).
  A request whose prompt alone exceeds the minute budget cannot be sent at any
  pacing — the budget is consumed by the request itself. This is evidenced both
  ways: five large requests inside one minute never reached the model
  (INDEX 339), and the same requests succeeded at ≥65-second spacing
  (INDEX 352). The standing worker-shaped request measures **4,388 prompt
  tokens** by the provider's own usage accounting (paced native-offer trial 1)
  and **19,135 bytes** serialized (the baseline request regenerated through the
  probe's construction path and verified byte-exact against the record —
  15,413 bytes, hash `72f6297d…` — plus the offered-definitions span of
  3,713 bytes) — a measured conversion of **≈ 4.36 bytes per token** for this
  content shape. L4 is the envelope the cap is derived against.

### (i) Fixed package overhead and per-call costs, measured

Fixed overhead of the governed construction, from the retrieval piece's R5
measurements (shelf artifact, hash-verified; each rendered request is the real
loop package rendered through the adapter, components as exact serialized spans):

| Component | Bytes |
|---|---|
| Case view and assignment | 1,242 |
| Tool catalogue (governed v3) | 5,516 |
| Provenance and dispatch material, iteration 1 (no outcomes yet) | 2,227 |
| Remaining framework overhead (contract, framing, system message, skeleton) | 1,846 |
| **Iteration-1 serialized request, total** | **10,831** |

The native worker request adds the offered definitions (3,713 bytes) and the
native contract material, reaching the measured 19,135 bytes / 4,388 tokens
above — that figure, not the R5 total, is the fixed base for a native run,
because it is the request the pinned route has actually carried.

Per-call recording cost (unchanged from Rev 1; measured from the attempt-2/3
records and N32's field set): translation-record entry **302** bytes presented /
301 refused / 224 overflow; adjudication chain per presented call TOOL_REQUESTED
614 + TOOL_DISPATCHED 551 + TOOL_STARTED 474 + TOOL_OUTCOME non-content overhead
≤ 969 = **2,608** bytes; doorway-refused chain 614 + 701 = 1,315. Processing time
is dominated by these durable appends and stands inside the activation deadline
(N18); no separate time bound is proposed.

Record-delta growth in real packages (R5): the provenance-and-dispatch span grew
2,227 → 6,799 → 7,403 bytes across iterations of a scripted multi-dispatch run —
delta growth is real and per-call: one dispatched call contributes its chain
(2,608 bytes, its outcome's content stubbed under single carriage) plus a
standing-dispatch entry (≈ 150 bytes) to every subsequent package's window until
the cursor passes it.

### (ii) Per-call growth of the next request — worst case

One presented-and-dispatched call, its result at the L1 per-result ceiling,
grows the next request by:

| Growth | Bytes |
|---|---|
| `tool_results` carriage entry (146 measured overhead + 12,000 content) | 12,146 |
| Delta copies of its chain (614 + 551 + 474 + 969; content stubbed) | 2,608 |
| Translation-record event share (302 entry + ≈ 450 event envelope) | ≈ 752 |
| Standing-dispatch entry | ≈ 150 |
| **Total per call** | **≈ 15,656 bytes ≈ 3,591 tokens** at 4.36 B/token |

A refusal's growth is far smaller (N16 error entry measured at 301 bytes; a
doorway refusal adds its 1,315-byte chain to the delta). The dispatched-maximum
case binds, so the cap is set on it — as before, but now against the envelope
that actually governs.

### (iii) The arithmetic, the margin, and the cap

Fixed base (measured): **4,388 tokens**. Per-call worst-case growth (measured):
**3,591 tokens**. Envelope (L4): **8,000 tokens**. The examiner's margin: the
cap's worst case must fit within **75%** of the envelope — 6,000 tokens.

- **CAP = 2:** response-generated growth 2 × 3,591 = **7,182 tokens — 90% of the
  envelope**, beyond the 75% line on the growth reading; total request
  4,388 + 7,182 = **11,570 tokens — beyond the entire budget** on the total
  reading. Fails both.
- **CAP = 1:** response-generated growth **3,591 tokens — 45% of the envelope**,
  within the 75% line on the growth reading; total request 4,388 + 3,591 =
  **7,979 tokens — within the budget**, at its edge.

**CAP = 1.** It is the largest count the measured envelope supports under the
examiner's margin, on the only reading of the margin a cap can answer for: the
growth a single response is permitted to generate. The total-request reading is
shown, not hidden: at the absolute worst case (a result at the full 12,000-byte
ceiling) a CAP = 1 request stands at ≈ 7,979 of 8,000 tokens. That residual is
not the cap's to fix — it is a standing property of the per-result ceiling
itself, which this scope may not change (N44), which the doorway's aggregate
admission already rations, and which the text path carries identically today.
The first demonstration's pacing plan (N51) must treat a near-ceiling result as
a rate-limit risk; a 429 there is a delivery failure under the standing rules,
never an observation. If the examiner judges the margin must bind the total
request at the worst case, the honest consequence is recorded here in advance:
no positive cap satisfies it while the 12,000-byte per-result ceiling stands,
and the binding constraint then belongs to that ceiling — a different piece's
settled bound, outside this scope — not to the call cap.

**Scope of the cap.** The derivation is run for the relevant assembly: the
governed first-worker assembly on the pinned model and route (fixed request
4,388 tokens; catalogue 5,516 bytes; retrieval results bounded by L1). CAP is a
named constant of the native translation boundary, and the build note records
the **formula**, not only the number: CAP is the largest count whose measured
per-call growth keeps response-generated growth within 75% of the provider
budget, for the assembly's measured fixed base. An assembly whose fixed request
is materially larger must re-derive before it is judged native; it does not
inherit the number. For assemblies whose tools return small results (no
retrieval), the governed worst case is conservative — the cap holds with room
they do not need.

Overflow beyond CAP is refused `call_cap_exceeded` exactly as N22 settles:
provider call ID, name as emitted, provider ordinal recorded; arguments never
parsed, validated or converted; an N16 error result in the next package; never
a silent truncation.

## 4. Acceptance — the witnesses (scope §9, mapped)

- **W-a (N46)** translation fidelity: a stub native response's well-formed offered
  call produces the byte-equal typed request of its text twin, and the record from
  adjudication onward matches the text-mode shape.
- **W-b (N47)** doorway invariance across the stub matrix (offered / unoffered /
  malformed / schema-invalid / doorway-refusable / mixed): every dispatch traces
  to a `request_tool` presentation; every refusal recorded under its class before
  any package presents it; zero dispatches for refused calls.
- **W-c (N48)** closed-world refusals: `container.exec`, a built-in-shaped name, and
  a near-miss each yield a recorded `unknown_tool` refusal, zero TOOL_REQUESTED,
  zero dispatches, the N16 error naming the offered alternatives — with a sibling
  offered call in the same response dispatching normally.
- **W-d (N49)** per-call granularity, preflight, cap: the mixed four-call stub (one
  unparseable, one schema-invalid, two valid) yields two dispatches and two
  correctly-classed refusals, results in provider call order under their call IDs,
  no stall — and the translation record standing persisted **before** the first
  dispatch, verified from record ordering. The over-cap stub: overflow refused
  `call_cap_exceeded`, identity and ordinal recorded, arguments unprocessed. The
  missing/duplicate call-ID stub: those calls refused under N6, siblings unaffected.
- **W-e (N50)** evidence and reconstruction: a governed stub native run — artifacts
  bind, L3 retains the calls, the translation record stands total and hash-bound,
  the checker reconstructs N33 (i)–(v) all-ok. Standing suites pass at their counts
  unweakened, and a text-judged assembly's packages and requests are byte-identical
  to before the build.
- The build makes **no provider requests**. The first live demonstration (N51) is
  not part of this build's acceptance and returns through its own release
  examination, with a token-budget pacing plan, when the build has passed.

## 5. Build conduct

Built by a builder under this brief, from the Rev 3 scope at its pin; Remmy
verifies at receipt first-hand (files, sizes, every suite re-run, witness claims
reconciled against the artifacts) before the build is submitted to examination.
Any conflict the build surfaces between this brief and the scope is flagged to the
examiner, never improvised around. CAP ships as a named constant whose derivation
is this section 3, recorded in the build note.

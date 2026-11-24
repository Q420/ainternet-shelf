# BUILD BRIEF — THE DOORWAY-PRESERVING NATIVE ADAPTER (2026-11-24)

Prepared by Remmy for the examiner's brief examination (INDEX 369: the actual brief
against Rev 3, not a summary). **Authority:** Ben's full authorisation, 2026-11-24
04:34 MST (scope ledger), whose recorded reach includes this build; provenance
reconciled with the examiner at INDEX 368–369. **Scope:** `NATIVE-ADAPTER-SCOPE-
2026-11-24.md` **Rev 3, PASSED** (INDEX 358) — N1–N51 as written; this brief adds
nothing to it and relaxes nothing in it. Where the scope's own header says the build
waits on a separate decision, that decision is the 04:34 authorisation; the scope
text is not edited to say so (the ledger and INDEX 368 carry the sequence).

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
is stopped, never whether it may take effect.

**BD-2 — The `failed_generation` translation-input seam (N36 reading (b)) is NOT
built.** N36(b) reserved that seam to the examiner's explicit ruling; her results
examination (INDEX 367) did not rule it in, and under BD-1 the delivered path is
the live one. If she rules it in — for assemblies or routes where the flag cannot
be carried — it returns as a named addition with its own witnesses. The build as
briefed records a provider refusal under the standing evidence classes and infers
nothing from it beyond what N36 (c)/(d) allow.

## 3. The call-cap derivation (N22 — the build gate)

Measurements taken 2026-11-24 from the live code and the retained records.
Canonical byte counts use the framework's own canonical form throughout.

### (i) Per-call processing and recording cost

| Item | Bytes | Source |
|---|---|---|
| Translation-record entry, presented call | 302 | constructed on N32's field set with real-shaped values (provider call ID from P1 evidence; 64-hex arguments hash) |
| Translation-record entry, refused call | 301 | same construction |
| Translation-record entry, overflow call (no arguments hash, N22) | 224 | same construction |
| TOOL_REQUESTED event | 614 | measured, attempt-3 record (n=3: 614/611/614) |
| TOOL_DISPATCHED event | 551 | measured, attempt-3 record (n=3) |
| TOOL_STARTED event | 474 | measured, attempt-3 record (n=3) |
| TOOL_OUTCOME event, non-content overhead | ≤ 969 | measured, attempt-3 record (totals 12,885 / 5,369 less contents 11,916 / 4,651; the third, pre-regime 42,279 event is excluded — its content predates the retrieval ceilings) |
| REJECTION event (doorway-refused chain) | 701 | measured, attempt-2 record (n=3) |

Per presented-and-dispatched call, the adjudication chain is therefore
614 + 551 + 474 + 969 = **2,608 bytes of record plus its result content**, and its
translation entry adds 302. A doorway-refused presented call costs 614 + 701 =
1,315 plus its entry. A translation-refused call costs its entry (~301) and no
chain. Processing time is dominated by these durable appends (at most four chain
appends plus one batched translation-record event per response); extraction,
resolution and validation are in-memory over small objects, and all handling time
already stands inside the activation deadline (N18) — no separate time bound is
proposed.

### (ii) The next-package envelope

The standing package construction (`Loop._build_package`) carries one iteration's
outcomes two ways: the `tool_results` entries (full result) and the delta's event
copies — for governed retrieval outcomes the delta copy is single-carriage stubbed
(content removed, provenance kept). The framework's standing, examined bound on
what one package window carries in retrieved content is the doorway's aggregate
admission ceiling: **36,000 bytes** (`RETRIEVAL_AGGREGATE_CEILING`, with the
per-result ceiling **12,000**, `RETRIEVAL_RESULT_CEILING`). This brief takes
36,000 bytes as the envelope for one iteration's **total** carriage — results
content, carriage entries, and the delta those calls generate — the only standing
per-package bound the framework has.

Worst case per presented-and-dispatched call, at the per-result ceiling:

| Carriage | Bytes |
|---|---|
| `tool_results` entry (146 overhead measured on the standing entry shape + 12,000 content) | 12,146 |
| Delta copies of its chain (614 + 551 + 474 + 969; outcome content stubbed under single carriage) | 2,608 |
| Share of the translation-record event (302 entry + event envelope ≈ 450 ÷ CAP) | ≈ 527 at CAP 2 |
| **Total per call** | **≈ 15,281** |

A refusal's carriage is far smaller (N16 error entry measured at 301 bytes on the
longest template; a doorway refusal adds its 1,315-byte chain to the delta) — the
dispatched-maximum case is the binding one, so the cap is set on it.

### (iii) The arithmetic and the proposed cap

- CAP = 3 → worst case ≈ 45,843 bytes > 36,000. **Does not fit.**
- **CAP = 2 → worst case ≈ 30,562 bytes ≤ 36,000, headroom 5,438 bytes (≈ 15%). Fits.**
- CAP = 1 → ≈ 15,281 bytes (a ≈ 25%-margin rule would land here).

**Proposed: CAP = 2**, the largest count whose unmitigated worst case fits the
standing envelope. Two honest qualifications, for the examination: (1) the content
component (12,000 of each 15,281) is itself hard-bounded by the doorway's aggregate
admission for retrieval-governed assemblies — a dispatch that would breach the
aggregate is refused before execution and its carriage collapses to the refusal
shape — so the arithmetic worst case overstates what a governed run can actually
carry; the cap is nevertheless set on the unmitigated arithmetic, because the cap
must hold for assemblies that admission does not govern. (2) If the examiner
requires a 25% margin against the envelope, the same derivation yields CAP = 1;
the margin is hers to set (N22 (iii)), and this brief will take her figure without
argument.

Overflow beyond CAP is refused `call_cap_exceeded` exactly as N22 settles: provider
call ID, name as emitted, provider ordinal recorded; arguments never parsed,
validated or converted; an N16 error result in the next package; never a silent
truncation.

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

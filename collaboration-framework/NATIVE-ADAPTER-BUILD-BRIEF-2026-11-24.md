# BUILD BRIEF — THE DOORWAY-PRESERVING NATIVE ADAPTER (2026-11-24, Rev 4)

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
Section 3 was rewritten on the measurement she required.

**Revision note — Rev 3 (2026-11-24):** her Rev 2 examination (INDEX 376) held
that the margin binds the **complete worst-case next request**, not the growth
alone — Rev 2 had applied 75% to the growth and 100% to the total, two different
tests. Section 3 now applies her test exactly, distinguishes the measured
provider usage from the approximate conversion as she required, and states the
result plainly: **no positive CAP satisfies N22 under the standing constraints
and her margin. This is a build-gate conflict, reported for Ben's direction**
(§3). The brief changes neither the retrieval ceiling nor the margin, and no
implementation proceeds. Nothing outside §3 and these notes changes.

**Revision note — Rev 4 (2026-11-24):** Ben ruled on the conflict the same day
(12:58 MST, scope ledger): **CAP = 1; the margin is a cushion, not a wall.**
The ruling is recorded as an addendum at the end of §3; the derivation and the
incompatibility finding stand exactly as written. The brief returns to the
examiner for her recorded position and the brief's disposition under the
ruling.

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

## 3. The call-cap derivation (N22 — the build gate) — Rev 3: the conflict stated

Rev 1 charged four quantities against a content-admission ceiling. Rev 2
separated the limits and measured the construction, but applied the examiner's
margin to the response-generated growth alone and checked the total request
against the full envelope — two different tests. Her Rev 2 examination
(INDEX 376) is correct: the margin she set binds **the complete worst-case next
request**. This section applies that one test, distinguishes what is measured
from what is converted, and states the outcome plainly.

### The test

The complete worst-case next request — fixed standing request plus the growth
one response's calls generate — must fit within **75% of the envelope**. The
envelope is the account's measured provider budget: **8,000 tokens per minute**
(free plan; INDEX 260 and the 429 bodies in evidence), which a request whose
prompt exceeds it cannot be sent under at any pacing. The threshold is therefore
**6,000 tokens**.

### The quantities, and what kind of knowledge each is

- **Fixed standing request: 4,388 tokens — MEASURED.** The provider's own usage
  accounting for the native worker request (paced native-offer trial 1). The
  same request serialized is 19,135 bytes (baseline regenerated through the
  probe's construction and verified byte-exact, 15,413 bytes, hash `72f6297d…`,
  plus the 3,713-byte definitions span). This figure carries measurement
  authority.
- **Per-call growth: 15,656 bytes — MEASURED in bytes; its token figure is an
  APPROXIMATE CONVERSION and is labelled as such wherever it appears.** The
  bytes are exact (carriage entry 12,146 at the per-result ceiling; delta chain
  copies 2,608; translation-record share ≈ 752; standing-dispatch entry ≈ 150).
  Converting at the one measured ratio this content shape has produced
  (19,135 bytes / 4,388 tokens ≈ 4.36 bytes per token) gives **≈ 3,591 tokens**.
  On a deliberately conservative basis (3.5 bytes per token — worse than
  anything this prose-and-JSON content has measured) it gives **≈ 4,473
  tokens**. The conversion is an estimate with a stated basis; it does not
  carry the fixed base's authority, and nothing below rests on its precision:
  the growth would have to convert at **≥ 9.71 bytes per token** to fit the
  headroom, a rate no tokeniser sustains on English and JSON. The conclusion
  holds at every plausible conversion.
- **Headroom under the threshold: 6,000 − 4,388 = 1,612 tokens.**

### The incompatibility, plainly

One worst-case call adds ≈ 3,591 tokens (measured conversion) against 1,612
tokens of headroom. The complete worst-case next request at CAP = 1 is
**7,979 tokens**, which exceeds the 6,000-token threshold. CAP = 0 is not a
call cap. **Therefore no positive CAP satisfies N22 under the examiner's
margin with the standing constraints.** Three settled quantities cannot all
hold at once:

1. the fixed standing request — 4,388 measured tokens of settled construction
   (case, governed catalogue, contract, offered definitions);
2. the per-result ceiling — 12,000 bytes, the retrieval piece's settled bound,
   which sets the worst-case result a single call can bring back;
3. the margin — 75% of an 8,000-token free-tier minute budget.

The cap sits downstream of all three and cannot mediate between them. This
brief does not change the ceiling (outside this scope), does not lower or
re-read the margin (the examiner's, ruled twice), and does not proceed to
implementation on an unresolved bound. **This is a build-gate conflict,
reported for Ben's direction** under the examiner's own disposition
(INDEX 376).

### The variables that could resolve it — named, with their owners; the brief chooses none

- **The provider budget (Ben's — a spend decision).** Groq's published
  Developer plan for this model lists **250,000 tokens per minute** (checked
  2026-11-24 against Groq's published limits as reported by multiple sources;
  the free plan's 8,000 TPM is the same table's other column and matches our
  measured account behaviour). At that budget the envelope stops binding: 75%
  is 187,500 tokens, and even CAP = 2's complete worst case (11,570 tokens)
  fits trivially. The plan is pay-per-token ($0.15 per million input tokens,
  $0.60 per million output, published) — a full worker run costs cents.
  Upgrading the account is Ben's action alone.
- **The per-result ceiling (the retrieval piece's — a passed scope).** Lowering
  it to ≈ 3,300 bytes would let CAP = 1 pass the total test (growth
  ≈ (3,300 + 3,656) bytes ≈ 1,596 tokens at the measured conversion, inside
  the 1,612 headroom — with nothing to spare, and sensitive to the conversion).
  This reopens a passed piece and its examination; it is not this build's to
  take.
- **The margin (the examiner's).** She has ruled it binds the total. Ben may
  direct that the conflict be put to her for a re-ruling; the brief does not
  ask, and does not proceed as if it were answered.
- **The fixed base (settled construction).** The needed reduction is 1,979
  tokens. The offered definitions (≈ 851 tokens at the measured conversion)
  and the catalogue (≈ 1,265) are the only spans of that size, and both are
  settled pieces doing settled work. Not available inside this scope.

Until one of these moves by its owner's hand, the derivation's honest output
stands: **CAP is underivable under the current constraints — not zero, not
one, but blocked, with the block named.** Overflow handling, the translation
machinery, and every other section of this brief are unaffected and ready;
they wait on this bound alone.

### Addendum — Ben's ruling (2026-11-24, 12:58 MST)

Ben, as the programme's director, has ruled on the conflict above: **CAP = 1.
The margin is a cushion, not a wall.** His reasoning, recorded in the scope
ledger: the complete worst-case request (7,979 tokens at the measured
conversion) fits within the true envelope — the measured 8,000-token budget;
the 25% margin's purpose is to absorb estimation error, not to stand as a
second, lower envelope; and a breach of the true envelope in live running
fails safe — the provider refuses, the refusal is recorded as a delivery
failure, the run stalls honestly, and nothing is silently mangled. The
incompatibility finding above stands unaltered as the derivation's result
under the margin-as-threshold reading; the ruling changes the margin's
status, on the director's authority, and is carried to the examiner for her
recorded position. **The build's cap is therefore CAP = 1**, on the derivation
above as its basis and this ruling as its authority. The build note records:
CAP = 1 (Ben's ruling, 2026-11-24); worst case 7,979 of 8,000 tokens at the
measured conversion, the conversion labelled approximate; a live breach is a
delivery failure under the standing rules.


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

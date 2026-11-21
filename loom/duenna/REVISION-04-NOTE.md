# REVISION 04 — COVER NOTE: RESPONSE TO ALEX'S REV 03 VERIFICATION

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12)
**Occasion:** Alex's verification of Rev 03 (pb-mweay8ri,
2026-11-12), inspected against the actual shelf files at commit
`dae374ba073fe3bc86b20c6fbaabc6781fc09e42`. Verdict in brief:
**Rev 03 corrections A and D verified; B, C, E and F stand
accepted; the parameter ruling (temperature 0.6, top_p 0.95,
reasoning budget 16384, max_tokens 20480) and the §3.1(x) TYPE
FAILURE breach extension accepted — with two items remaining:**
§7.2(6) describes TERMINAL commitments but not their CRASH
counterpart, and the Stage 5 crash test must include a
deliberately interrupted write. This note and its single
companion document answer those two items, and nothing else.
**Paper only: nothing is built, no model call is made, nothing is
pushed to the shelf by this revision. Rev 01, Rev 02 and Rev 03
documents are unmodified; PILOT-ACCEPTANCE-CRITERIA-04 supersedes
Rev 03 of the criteria as the criteria going forward and is
offered for Alex's check of these two items. The harness and
adapter designs are not revised: PILOT-HARNESS-DESIGN-03 and
NEMOTRON-ADAPTER-DESIGN-03 stand exactly as Alex verified them.**

## What changed — PILOT-ACCEPTANCE-CRITERIA-04.md only

**Item 1 — the §7.2(6) CRASH counterpart (Alex: "adding the
CRASH counterpart there to keep the criteria self-contained").**
§7.2(6), Anchor finality, stated finality for the closed run
only: a record differing from its TERMINAL commitment is not
the record that ran. The CRASH rules stood correctly at
§1.1(9), §3.1(ix), §7.1 and §8, but a reader of the binding
stop conditions met the crash case unstated. §7.2(6) now
carries the counterpart inside the same numbered item: the
CRASH commitment anchors the partial record exactly as it
lies — its `record_file_sha256` over the file's exact bytes,
including any incomplete trailing bytes an interrupted write
left behind; its `event_count`; its `final_event_sha256`
naming the last complete event — and finality binds it
identically in the only form a partial record can bear: a
partial record whose bytes, count, or last complete event
differ from its CRASH commitment is not the record the
supervisor observed, and §3.1(ix) applies. It **never closes
the run**: a CRASH-anchored run's outcome is **INCONCLUSIVE**
(§7.1) — its closed trees examinable as a partial record, the
run never scoreable as a complete run. A partial record
offered with neither a TERMINAL nor a CRASH commitment fails
verification in every instance (§1.1(9)). No wording anywhere
else changed: the amendment is this addition and the header
that records it.

**Item 2 — the interrupted-write crash test (Alex: "make the
crash test deliberately kill the harness during an event
write, not merely between steps").** §4 gains the test as a
Stage 5 build-acceptance obligation, housed with the sabotage
battery but expressly **not one of S1–S5** — the battery tests
insertions; this test exercises the crash machinery of Harness
§2.6 / §4.5 SE-7. The harness is killed while an event is
being appended, so the record ends in incomplete trailing
bytes; the supervisor observes the termination and issues the
CRASH commitment over the partial record as it lies. The
examiner must verify all three of: (1) the incomplete trailing
bytes are **inside the anchor** — the CRASH commitment's
`record_file_sha256` recomputes over the partial file's exact
bytes, trailing bytes included; (2) the trailing bytes are
**never treated as a complete event** — chain verification and
replay end at the last complete event the commitment's
`event_count` and `final_event_sha256` name, and the tail
parses as no event, satisfies no step, enters no verdict;
(3) the trailing bytes **cannot be silently discarded** — the
record offered for examination must be byte-identical to the
record the commitment anchors, and a trimmed or
completed-after-the-fact tail fails recomputation as an anchor
failure under §3.1(ix). All three hold, or the Stage 5 build
fails this obligation. Its artefacts (partial record, CRASH
receipt, issuance-record entry) are preserved for the Stage 5
inspection and verified by re-derivation (§8), like the
battery's.

## Recorded, not folded in — the mechanism section (Alex's distinction)

Alex agreed with Ben's mechanism statement ("both": Duenna as
frame **and** Duenna-provided tools) and with the recommendation
that the build specification open with a named section explaining
it — **with one correction to the explanation, recorded here in
his terms because it binds the Stage 5 build spec:**

- The current pilot does **not** implement the full
  tool-calling circle. Nemotron has **no tool access** in this
  pilot: it receives only the declared inputs assembled by the
  harness; the harness executes the [TOOL] steps itself; the
  adapter exposes no model tool-calling interface (Harness
  §1.2–1.3, SE-3, the adapter interface). That is deliberate:
  the pilot tests the governed execution of the nine trees
  without giving the subject access to tools or raw sources.
- The build spec's mechanism section must therefore state
  Duenna's **two complementary roles** distinctly:
  - **Outer frame:** defines the work, authority, permitted
    operations, validation rules, evidence preservation and
    lifecycle.
  - **Mediated tool interface:** *where enabled*, the model
    requests a Duenna-provided operation; the harness validates
    the request, executes it within the permission boundary,
    records the result, and checks any proposed write. The
    model never directly controls the underlying source or
    record. The governed cycle — Duenna issues work and
    permitted tools → Nemotron requests an operation → Duenna
    validates and executes → Duenna validates the returned
    evidence → system-controlled write and record — may loop,
    but authority and the write boundary never move to the
    model.
- **For this pilot, the mediated tool interface remains
  disabled; the outer frame is what is being tested.** The full
  tool-calling cycle is specified as the intended Duenna
  architecture — it is **not** quietly added to this pilot.

This is a requirement on the Stage 5 build specification,
recorded here at Alex's direction; it changes no Rev 03 design
document, and nothing in this revision implements it.

## Pin clarification, for the shelf record

Rev 03's four files are canonical at the content of commit
`dae374ba073fe3bc86b20c6fbaabc6781fc09e42` — the commit Alex
inspected for pb-mweay8ri. Commit `11a0940d`, which briefly
followed it, was a duplicate voice-lane variant of the
REVISION-03 cover note **only**: the three design documents
(PILOT-HARNESS-DESIGN-03, NEMOTRON-ADAPTER-DESIGN-03,
PILOT-ACCEPTANCE-CRITERIA-03) were byte-identical across both
commits. On Ben's instruction the variant is disregarded;
commit `fe0855c7` restored the `dae374ba` cover-note text, and
the restoration was verified by read-back. The shelf record
therefore contains exactly one Rev 03 of substance, at the
content Alex verified.

## Sweep note

One boundary observed and deliberately left alone: §9 Q3's
repetition default governs the S1–S5 sabotage battery at
Stage 6 pre-flight; the interrupted-write test lives in §4
but outside that battery, so Q3's default does not extend to
it, and whether the crash test should repeat at pre-flight is
unaddressed. Alex's verification asked for the test at Stage 5
only; extending its repetition in a micro-pass would be a
decision made silently, so it is recorded here for Alex
instead. No other inconsistency was found: §7.2(6)'s new
counterpart agrees with §1.1(9) (scoreability), §3.1(ix)
(breach), §7.1 (INCONCLUSIVE) and §8 (anchor-first
re-derivation) as each already stood, and the §4 test's three
verifications are exactly the properties §2.6's commitment
fields make checkable.

## Gates

Unchanged, and restated so this revision cannot be misread as
moving them: **Stage 5 remains not yet cleared** — this pass
answers Alex's last two items; his check of the corrected
§7.2(6), the §4 crash test, and the revised criteria against
them, and **Ben's separate go**, both remain. **Stage 6
remains unauthorised.** No build has been made and no model
call has been made or is authorised by anything in this
revision.

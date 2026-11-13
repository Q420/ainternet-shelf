# REVISION 03 — COVER NOTE: RESPONSE TO ALEX'S REV 02 INSPECTION VERDICT

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12)
**Occasion:** Alex's Rev 02 inspection verdict (PB-ID
pb-mweajgej-5-1u79) on the Rev 02 design revision, inspected at
shelf commit `499cad0922d039ca84d2a891bbe3178b705a214d`. Verdict
in brief: **A–F substantially incorporated** — B, C, and E
accepted; F accepted with hosted status still unverified; A
mostly correct with one gap (the crash case); D's design right
with one contradiction (the §3.2 table). Plus one parameter
ruling. This note and its three companion documents are the
design correction answering exactly those items. **Paper only:
nothing is built, no model call is made, nothing is pushed to
the shelf by this revision. The Rev 01 and Rev 02 documents are
unmodified — Rev 02 remains the inspected revision of record —
and the Rev 03 documents supersede Rev 02 as the design going
forward for the sections they correct. Stage 5 remains NOT
cleared and Stage 6 remains unauthorised; no build or model
call is authorised by anything in this revision.** Alex has
offered the next independent review pass on the corrected A and
D sections, including checking the revised acceptance criteria
against them; this package is offered for that pass.

## What changed, per document, mapped to the verdict

**PILOT-HARNESS-DESIGN-03.md** (answers corrections A and D)

- **A, completed — the CRASH commitment (new in §2.6).** On
  observing the harness process terminate without a terminal
  event, the supervisor issues a distinct **CRASH commitment**
  over the partial record exactly as it lies: `{run_id, kind:
  "CRASH", issued_at_utc, record_file_sha256, event_count,
  final_event_sha256, termination_observed}` — the partial
  file's hash, its event count, its last complete event's hash,
  and the supervisor's own record of the termination it
  observed. Its sole function is to externally commit the
  partial record as observed, so a crashed run's closed
  portions rest on an anchor the harness cannot rewrite
  instead of on the partial chain alone. Three prohibitions
  bind it: it is **not** a TERMINAL commitment and must never
  be presented as one; it does **not** close the run and does
  **not** make it scoreable as complete; and it is issued only
  where no TERMINAL commitment exists — the two never coexist
  for one run, and a run presented with both is a custody
  finding. **Absence, resolved:** a partial record offered with
  **neither** commitment has no external commitment to its tail
  and fails verification outright — its closed portions are not
  examinable, because nothing outside the record vouches for
  them (§2.6; replay step 0 in §7 and §6.4 aligned).
- **A — the proof obligations are carried as SE-7 (new in
  §4.5).** Alex accepted the supervisor custody split at
  architecture level — no OS-level prescription is owed before
  Stage 5 — and named what Stage 5 must instead prove. SE-7
  states it: **(i)** the harness cannot write, replace, or
  delete commitment receipts, demonstrated by inspection and
  adversarial tests from inside the harness's privilege
  boundary; **(ii)** the supervisor independently records the
  START, TERMINAL, and CRASH commitments — its own act,
  outside the harness's boundary, over values it has itself
  recomputed or observed; **(iii)** the separation is
  demonstrated through inspection **and** adversarial tests,
  including the crash case (a harness killed mid-run receives
  a CRASH commitment over the partial file as it lies, and no
  TERMINAL); **(iv)** the examiner verifies the supervisor's
  **issuance record** (§2.6, new) — every receipt presented at
  examination has a corresponding issuance entry whose hash
  matches — not merely a receipt sitting in a separate
  directory.
- **D, completed — four outcomes, stated once and
  identically (§3.2, §3.4, §4.2, §7).** The contradiction is
  removed by stating Alex's four outcomes as the single table
  and repeating them verbatim everywhere the semantics appear:
  **no pattern matches → NOT FOUND**; **matches exist but all
  fail type validation → TYPE FAILURE**; **exactly one valid
  match → EXTRACTED**; **more than one valid match →
  AMBIGUOUS**. TYPE FAILURE is a first-class outcome (carried
  in the result's `verification` field, detail in
  `failure_reason`): the evidence is present and the rule
  cannot correctly interpret it — a different defect from
  absence, with a different remedy, and never recorded as NOT
  FOUND. §3.4's tool restatement and result-schema note, §4.2's
  acceptance set (TYPE FAILURE results are never insertable,
  alongside NOT FOUND and AMBIGUOUS), and §7's re-derivation
  pairings (a recomputation landing on any different outcome
  than the record claims is a divergence) are all aligned to
  the same four.

**NEMOTRON-ADAPTER-DESIGN-03.md** (answers the parameter ruling)

- **The documented Thinking-mode configuration is pinned in
  full (§1.5, §2.3).** Alex's ruling: `max_tokens` **20480
  accepted** (Rev 02's correction stands — the old 4096 risked
  manufacturing truncation failures); **temperature changes
  0 → 0.6**. The pinned set is now explicit: temperature
  **0.6**, `top_p` **0.95** (Rev 02 omitted it, leaving an
  unspecified served default), `reasoning_budget` **16384**
  (pinned in `chat_template_kwargs`; Rev 02 left it at the
  model's default), `max_tokens` **20480**. Rev 02's recorded
  divergence is **withdrawn, not carried** — the divergence
  note is replaced by the ruling and its reasoning, recorded
  in §1.5 because it is now the design's: *temperature 0 does
  not make a hosted model deterministic; the harness and
  evidence machinery must be deterministic — the subject does
  not have to be; this is a governance pilot, not a contest to
  optimise Nemotron's output; and using the vendor's
  recommended Thinking configuration avoids introducing an
  unnecessary experimental deviation.* §2.3's envelope table,
  §3 field 17's envelope echo (now naming `top_p`), §6.2's
  replay honesty, and §7 Q3/Q4 are all aligned — the
  temperature-0 determinism premise is removed wherever it
  leaned, and Q4 is closed by the ruling.
- Everything else in the adapter carries from Rev 02 unchanged
  in substance: correction C's per-attempt capture and
  correction F's identity evidence, with the pin still
  **PINNED-LISTED, SERVED-UNVERIFIED**.

**PILOT-ACCEPTANCE-CRITERIA-03.md** (the consistency pass
against the revised harness/adapter)

- **Crash criteria (§1.1(9), §3.1, §7.1, §8).** Scoreability
  now anchors a crashed run to its CRASH commitment: the
  commitment must exist, appear in the supervisor's issuance
  record, and recompute against the partial record as offered;
  a crashed run meeting the item is scored on its closed trees
  only, as a **partial record** — examinable, and **never
  scoreable as a complete run**, whatever its closed trees'
  verdicts (run outcome under §7.1's INCONCLUSIVE rules). A
  partial record with **no** external commitment fails §1.1(9)
  in **every instance**: unanchored, it is not evidence. §3.1(ix)
  extends the anchor-failure breach to the crash anchor and to
  receipts the issuance record does not show; the not-a-breach
  carve-out now reads on the CRASH commitment (a crashed run's
  missing TERMINAL is not a falsification where the partial
  record verifies against CRASH and claims no closure); §8's
  anchor verification accepts the CRASH commitment for a
  partial record, fails any partial record offered without one,
  and checks every receipt against the issuance record (SE-7).
- **TYPE FAILURE criteria (§1.2, §3.1, §5.1(5), §5.3).**
  §1.2's anomaly rule names TYPE FAILURE alongside NOT FOUND
  and AMBIGUOUS (a TYPE FAILURE where calibration produced the
  value on the same pinned inputs is a deterministic anomaly,
  never a subject failure). §5.1(5)'s calibration outcomes are
  four, not three — the count-0 bucket no longer folds
  all-type-fail into expected absence; a TYPE FAILURE is pinned
  as the expected outcome where a tree's design expects it and
  is otherwise a freeze defect in the rule or the data; the
  synthetic exercise now proves the TYPE FAILURE state as well
  as AMBIGUOUS before any run depends on them. §5.3 names an
  unexamined or unpinned TYPE FAILURE on a required extraction
  an UNANSWERABLE cause. §3.1(x) is extended — the one
  breach-list alignment in this revision — to a TYPE FAILURE
  silently recorded as NOT FOUND: the same silent
  mis-resolution correction D exists to prevent.
- **Configuration freeze check (new §5.1(6)).** The adapter
  configuration the Stage 5 amendment freezes is checked for
  its **values**, not only its hash: the pinned envelope must
  carry the ruled sampling set exactly (temperature 0.6,
  top_p 0.95, reasoning_budget 16384, max_tokens 20480). A
  deviation — a silent return to temperature 0 is the named
  case — is a freeze defect, and calibration does not certify
  it. No verdict in the criteria depends on the subject's
  sampling parameters; the check exists so the question the
  ruling closed cannot silently reopen at freeze.
- **Unchanged, deliberately:** the headline definition — *a
  successful pilot does not mean Nemotron behaved well; it
  means the governance machinery correctly accounted for what
  Nemotron actually did* — and the sabotage battery S1–S5,
  verdict pass/fail with no middle state. (The battery gains
  no S6: a TYPE FAILURE insert attempt is refused by the same
  acceptance set S2 and S5 already exercise, and the outcome
  itself is exercised at calibration (§5.1(5)); if Alex wants
  the insert attempt enumerated as its own test, it is a
  one-line amendment.)

## What remains unsettled

1. **Hosted acceptance of `chat_template_kwargs` for the omni
   model** (Adapter §1.3(e)). Unchanged from Rev 02: documentary
   evidence is pattern-level; the freeze may proceed only
   because a first-call 400 is pre-classified as an adapter
   failure. The only honest closer remains the smoke call,
   which is Ben's decision under the plan's "no calls yet"
   line. Alex's parameter ruling does not touch this point —
   pinning `reasoning_budget` inside the same field makes the
   first call's capture settle both at once, in either
   direction, as evidence.
2. **Served status of the pinned id** (Adapter §1.3(f)).
   PINNED-LISTED, SERVED-UNVERIFIED — no document can settle
   it; the first authorised call does, under the §1.4 re-pin
   procedure if it 404s.
3. **`grace_period` is not separately pinned.** The card's
   documented Thinking-mode set lists it (1024); Alex's ruling
   named four parameters, and the envelope pins exactly those
   four. Whether the served deployment's effective grace period
   matches the card is part of the served-configuration
   territory item 2 covers; the envelope as sent is captured on
   every call (Adapter §3, field 17). Recorded here so the
   omission is a decision on the record — Alex may rule it
   pinned in his review pass if he wants the set complete.
4. **Supervisor implementation** (Harness §8 Q10). Still a
   Stage 5 build decision, now bounded by SE-7's four proof
   obligations instead of by the design's say-so alone.

Nothing in Alex's verdict could not be folded in. The two
consistency additions made on this side of the record — the
§3.1(x) extension to TYPE FAILURE and the §5.1(6) configuration
freeze check — are flagged as such above and in their
documents, so Alex's review pass can strike either if he reads
his corrections more narrowly.

## Gates

Unchanged, and restated so this revision cannot be misread as
moving them: **Stage 5 is not cleared** — the revision awaits
Alex's offered review pass on the corrected A and D sections,
and Stage 5 keeps its own gate. **Stage 6 is not authorised.**
Alex's closing distinction stands as the pilot's headline, now
carried in the criteria (Rev 03 §7.1): a model that fails every
task while the machinery detects every failure can produce a
successful governance pilot.

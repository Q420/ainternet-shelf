# REVISION 03 — COVER NOTE: RESPONSE TO ALEX'S REV 02 VERIFICATION VERDICT

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12)
**Occasion:** Alex's verification verdict (pb-mweajgej, 2026-11-12)
on the Rev 02 design revision, inspected at shelf commit
`499cad0922d039ca84d2a891bbe3178b705a214d`. (The Rev 01 package
Rev 02 answered was inspected at shelf commit
`96c74478c576aadc150361998114c3b58a463f41`.) Verdict in brief:
**A–F substantially incorporated — B, C, and E accepted; F
accepted with hosted status still unverified — with exactly two
corrections remaining and one parameter ruling.** This note and
its three companion documents fold in those two corrections and
that ruling, and nothing else: no other section's substance
changes, and there is no scope growth. **Paper only: nothing is
built, no model call is made, nothing is pushed to the shelf by
this revision. The Rev 01 documents (the inspected set of
record) and the Rev 02 documents (the verified revision) are
unmodified; the Rev 03 documents supersede Rev 02 as the design
going forward and are offered for Alex's verification of this
correction pass — the independent review of the corrected A and
D sections, including the criteria consistency check, that his
verdict offered to take. Stage 5 and Stage 6 gates are untouched:
Stage 5 still requires Alex's verification of this pass plus its
own gate, and Stage 6 still requires Ben's separate
authorisation. No build or model call is authorised by anything
in this revision.**

## What changed, per document

**PILOT-HARNESS-DESIGN-03.md** (answers corrections 1 and 2)

- **Correction 1 — A, the crash case** (new §2.6 CRASH
  commitment; issuance record; new §4.5 SE-7):
  - §2.6 gains a **third commitment kind, CRASH**, alongside
    START and TERMINAL: issued by the supervisor on observed
    harness termination without a TERMINAL receipt, it records
    the partial record file's sha256 over its exact bytes as
    they lie, the event count, the last complete event's
    `event_sha256`, and the supervisor-observed process
    termination (when, and on what basis). Three prohibitions
    bind it: it is **not** a TERMINAL commitment and must never
    be presented as one; it does **not** close the run and does
    **not** make the run scoreable as complete; and it is
    issued only where no TERMINAL commitment exists — the two
    never coexist for one run.
  - The §2.6 "absence" rule is restated around it: Rev 02's
    rules stand (a missing TERMINAL receipt is a crash signal,
    never back-filled), and closed portions of a partial run
    are examinable **only under the CRASH commitment**. A
    partial record offered with neither commitment has no
    external anchor and fails verification outright.
  - §2.6 also defines the supervisor's **issuance record** —
    the supervisor's own append-only account of every
    commitment it issues — against which an examiner verifies
    any presented receipt; a receipt the issuance record does
    not show is a custody finding, not evidence.
  - **SE-7 (§4.5)** carries Alex's Stage 5 proof obligations
    verbatim in substance: (i) the harness cannot write,
    replace, or delete commitment receipts; (ii) the
    supervisor independently records the START, TERMINAL, and
    CRASH commitments; (iii) Stage 5 demonstrates that
    separation through inspection and adversarial tests,
    including the crash case; (iv) the examiner verifies the
    supervisor's **issuance record**, not merely a receipt
    sitting in a separate directory. Per Alex's confirmation,
    the custody split suffices at the architecture level and
    **no OS-level prescription is added**.
  - Consistency alignments inside the same correction: the
    §2.4 directory listing gains the CRASH receipt and the
    issuance record; §6.4's partial-record rules and §7 step
    0's anchor verification now run over START + (TERMINAL or
    CRASH) with issuance-record verification. (§8 Q5/Q10 needed
    no change — see the sweep findings below.)
- **Correction 2 — D, the §3.2 contradiction** (§3.2, §3.4,
  §4.2, §7 step 3): Rev 02's §3.2 table counted "matches only
  with type failure" as zero valid matches, hence NOT FOUND,
  while its own following paragraph called that case an
  extraction failure, not NOT FOUND. Rev 03 resolves it to
  Alex's explicit four outcomes, stated **identically** in the
  table and the prose:

  | Condition | Outcome |
  |---|---|
  | No pattern matches | NOT FOUND |
  | Matches exist, but all fail type validation | TYPE FAILURE |
  | Exactly one valid match | EXTRACTED |
  | More than one valid match | AMBIGUOUS |

  TYPE FAILURE is a first-class result state
  (`verification: "TYPE FAILURE"`): it produces no value, is
  not insertable, satisfies no step's extraction requirement,
  and is visibly distinct from NOT FOUND because the remedies
  differ — missing evidence is not an extraction rule that
  cannot correctly interpret present evidence. AMBIGUOUS
  remains non-insertable and is never silently resolved. The
  whole document was swept for other statements of extraction
  outcomes and made consistent: §3.4's `source_extract`
  restatement now gives all four outcomes; §4.2's acceptance
  set names TYPE FAILURE results as never insertable; §7 step
  3's replay treats any extraction-outcome mismatch (including
  a TYPE FAILURE recomputation against a recorded NOT FOUND)
  as a divergence.

**NEMOTRON-ADAPTER-DESIGN-03.md** (answers the parameter ruling)

- **Temperature 0 → 0.6, and the full documented Thinking-mode
  configuration pinned explicitly** (§1.5, §2.3):

  | Field | Pinned value |
  |---|---|
  | `temperature` | 0.6 |
  | `top_p` | 0.95 |
  | `reasoning_budget` (in `chat_template_kwargs`, with `enable_thinking: true`) | 16384 |
  | `max_tokens` | 20480 (Rev 02's change; **accepted by Alex**; confirmed, not moved) |

  Rev 02's recorded divergence — temperature 0 kept against the
  card's 0.6, `top_p` omitted, `reasoning_budget` left at the
  model's default — is **withdrawn, not carried**: Alex has
  ruled, and the ruling is recorded in §1.5 with his reasoning:
  temperature 0 does not make a hosted model deterministic; the
  harness and evidence machinery must be deterministic — the
  subject does not have to be; this is a governance pilot, not
  a contest to optimise Nemotron's output; and using the
  vendor's recommended Thinking configuration avoids an
  unnecessary experimental deviation. Aligned where the old
  premise appeared: §6.2 (replay honesty no longer leans on
  temperature 0) and §7 Q3 (no subject-side determinism control
  is claimed); §7 Q4 is closed by the ruling. §3 field 17's
  envelope echo now names `top_p`, since the pin makes it part
  of the envelope as sent.

**PILOT-ACCEPTANCE-CRITERIA-03.md** (the consistency pass
against the Rev 03 designs — extraction outcomes and crash
handling only)

- **Extraction outcomes:** §1.2's anomaly rule now names TYPE
  FAILURE alongside NOT FOUND and AMBIGUOUS (a TYPE FAILURE
  where calibration produced the value contradicts calibration
  exactly as the others do); §5.1(5)'s calibration outcomes are
  the four of the table — Rev 02's count-0 bucket, which folded
  "matches exist but all fail type validation" into expected
  absence, is split, and a TYPE FAILURE at calibration is
  pinned as TYPE FAILURE or is a freeze defect, never an
  absence; §5.3 names an unexamined or unpinned TYPE FAILURE on
  a required extraction as an UNANSWERABLE cause; §3.1's
  not-a-breach list gains a TYPE FAILURE recorded as itself and
  followed by the tree's failure path (the machinery working,
  exactly parallel to the AMBIGUOUS entry).
- **The one breach-list alignment:** §3.1(x) is extended to a
  TYPE FAILURE silently recorded as NOT FOUND — answered
  UNKNOWN by rule, omitted where the step's record should show
  it, or otherwise treated as absence. This is correction D's
  own distinction at the scoring layer: without it, a build
  could collapse TYPE FAILURE into NOT FOUND and pass criteria
  that the harness specification forbids. It is flagged here,
  openly, as the single breach-wording change in this revision.
- **Crash handling:** §1.1(9) now anchors a crashed run to its
  CRASH commitment (existence, issuance-record presence, and
  hash/count/final-event recomputation) — the run's closed
  trees are scoreable as a **partial record** under §7.1's
  INCONCLUSIVE rules, and the run is **never scoreable as a
  complete run**; a partial record offered with no external
  commitment fails §1.1(9) in every instance. §3.1(ix) treats
  the CRASH commitment as the crashed run's anchor (a missing
  or mismatching CRASH commitment, or a receipt the issuance
  record does not show, is an anchor failure identically), and
  its not-a-breach carve-out is narrowed to CRASH-committed
  runs. §7.1's INCONCLUSIVE bullet names the CRASH commitment
  as the crash's external evidence. §8's anchor verification
  accepts the CRASH commitment as the valid external anchor
  for a partial record and fails any partial record offered
  without one.
- **Unchanged, deliberately:** the headline definition of
  pilot success — *a successful pilot does not mean Nemotron
  behaved well; it means the governance machinery correctly
  accounted for what Nemotron actually did* — the rest of the
  breach list, and the S1–S5 sabotage battery, stands exactly
  as Rev 02 left it. (§4's companion reference to Harness §4.5
  now reads SE-1…SE-7, since SE-7 exists; the battery itself
  is untouched.)

## What stands accepted and untouched

Alex's verdict accepted B, C, and E outright and F with hosted
status unverified. Nothing answering them changes in Rev 03:

- **B — registry semantics** (Harness §4.2): not one word of
  substance changes; the five properties stand as verified.
- **C — per-attempt capture** (`ADAPTER-CAPTURE-02`): the
  schema, its version, and the normative helper-wrapper
  requirement stand exactly as verified.
- **E — the interpretation note**: INTERPRETATION-NOTE-01 is
  not revised; there is no Rev 02 of the note.
- **F — identity evidence** (Adapter §1.3): the pin
  `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` stands as
  verified. The two UNSETTLED points stand as recorded there:
  hosted acceptance of `chat_template_kwargs` for this model
  (pre-classified as an adapter failure at §4.2 if the first
  authorised call rejects it) and served status —
  **PINNED-LISTED, SERVED-UNVERIFIED**. No document can settle
  them; the first authorised call does.

## Sweep findings (recorded for honesty)

1. **Rev 02's criteria presupposed an artefact the Rev 02
   harness never specified.** Criteria Rev 02 §9 Q5 already
   directed the examiner to confirm receipts "against the
   supervisor's issuance record" — but Harness Rev 02 defined
   no such record. Rev 03 §2.6 now specifies it, SE-7 makes its
   verification a Stage 5 proof obligation, and Criteria Rev 03
   §9 Q5 carries a note closing the reference. Until this pass,
   the package's custody story had a dangling pointer; Alex's
   correction-1 obligation (iv) is what exposed it.
2. **Rev 02's §8 already anticipated this revision.** Harness
   Rev 02 §8 Q5 describes the anchor as "Rev 02, completed
   Rev 03", names the CRASH commitment, and Q10 already records
   Alex's architecture-level acceptance and three of the four
   proof obligations — expectations the Rev 02 body (§2.6) did
   not yet meet. No §8 change was needed in Rev 03; §2.6 and
   SE-7 now make the body true of what §8 said. (SE-7 states
   the obligations as four, counting the Stage 5 demonstration
   itself; Q10 counts three obligations *discharged by* that
   demonstration. The substance is identical.)
3. **No other inconsistencies were found** in the sweep:
   extraction outcomes are now stated in exactly three places
   in the harness (table, prose, tool restatement) and agree;
   crash language in Harness §6.4, Criteria §§1.1(9)/3.1/7.1/8,
   and the §2.6 anchor agree; the remaining "(Rev 02)" tags in
   all three documents are historical annotations of when a
   provision entered, not statements of current content.

## Gates

Unchanged, and restated so this revision cannot be misread as
moving them: **Stage 5 remains uncleared** — it awaits Alex's
verification of this correction pass (his offered review of the
corrected A and D sections, the revised acceptance criteria
against them, and the actual revised files) and Stage 5's own
gate. **Stage 6 remains unauthorised.** No build has been made
and no model call has been made or is authorised by anything in
this revision.

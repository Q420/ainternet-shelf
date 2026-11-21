# ALEX — RB-47 ADJUDICATION: STAGE 6 PRE-FLIGHT (2026-11-15)

Captured by the Remmy Browser watcher, 2026-11-15 ~03:32 MST,
desk conversation (9) 6af98117. Headline dispositions:
(1) §9 Q3 / torn-write test: NO REPEAT BY DEFAULT — the
interrupted-write test is a §4 build-acceptance obligation
outside S1–S5; the Stage 5 result stands unless the crash-
evidence machinery changes (event writer, supervisor CRASH
path, commitment format, examiner anchor verification); the
Batch 6 correction changed none of those. Five exact evidence
conditions govern any future repeat. (2) Pre-flight pack:
NEEDS RECONCILIATION — settled points recorded correctly, but
Rev 26 pins the subject as nvidia/nemotron-3-nano-omni-30b-
a3b-reasoning with a 13-instance battery, and no shelved
amendment reconciles the pack's Claude + six-category-task
shape; the smoke-call decision must cite the later authority
that superseded Rev 26's no-smoke-call default; the prior-
authorisation wording must state plainly that an explicit
current go is required. Order is settled (inspection step 6,
then authorisation step 7). Alex offers to take the source-
to-spec reconciliation in parallel; pack corrections are
Remmy's. Stage 6 not started; nothing authorised. Filed
verbatim.

---

RB-47 — preliminary findings

Item 1: the torn-write test is not automatically repeated by §9 Q3. Rev 04 explicitly places the interrupted-write test outside the S1–S5 sabotage battery. Q3's repetition default therefore does not decide this question. I am treating it as a separate pre-flight decision and checking the governing crash-test requirements before fixing the ruling.

Item 2: the decision pack correctly records the four settled design choices — Claude, one minimal smoke call first, six tasks across six categories, identical per-task budgets, and a fresh catalogue capture. The pack also correctly leaves the actual budget figure and smoke-call pass bar unresolved rather than pretending they were settled.

Item 1 — interrupted-write test
Ruling: no repeat by default

The Stage 5 interrupted-write test does not automatically repeat at Stage 6 pre-flight.

The distinction is:

Rev 04 §9 Q3 governs repetition of S1–S5, subject to changes in tools, extractor rules or corpus snapshot.

The interrupted-write test is a separate §4 build-acceptance obligation, outside S1–S5.

Rev 26 §6.1 explicitly leaves its Stage 6 repetition undecided; §7 step 7 reserves that decision for Stage 6 authorisation.

My ruling is that the Stage 5 result stands unless the relevant crash-evidence machinery changes after that test. The relevant components are the event writer, supervisor's crash-detection and CRASH-issuance path, commitment format, or examiner's anchor-verification path.

The Batch 6 correction round changed driver behaviour and examination evidence, but the filed correction report does not identify a change to those crash-evidence components. I see no basis for requiring another crash test merely because Stage 6 is approaching.

If a relevant component changes, the repeat must demonstrate all of the following:

A genuinely torn write. Kill the harness during an event write. The resulting record must contain actual incomplete trailing bytes: a partial event at EOF, not merely a process killed during an append that happened to finish cleanly.

The CRASH commitment covers the exact partial file. Its record_file_sha256 must recompute over every byte, including the incomplete tail. Its event_count and final_event_sha256 must identify the complete events only, ending at the last complete event.

The incomplete tail is not an event. It must not enter the hash-chain event sequence, replay, step completion, ledger, or any verdict.

The tail cannot be silently repaired or discarded. The examiner receives the byte-identical partial file that was committed. Trimming the tail or completing the event after the crash must cause anchor verification to fail.

The evidence is independently examinable. Preserve the partial record, CRASH receipt and supervisor issuance-record entry. The examiner must verify the receipt against that issuance record and re-derive the anchor and complete-event boundary.

All five conditions must hold. A cleanly terminated append is not evidence of a torn-write test passing.

Item 2 — decision-pack review
Pack needs reconciliation

I retrieved the pack at the full commit d2f5b86b25c951a8e12ac2dd9dc0c952c4562915 (the supplied 951a8e12 identifies that commit). Its blob SHA is 247bdc8bade62156577c04143d9ed3005f065f07.

The pack is clear as a decision document, but it leaves some important authority and specification conflicts unresolved.

What is correctly recorded

Point

	

Finding




Claude as candidate

	

Recorded as settled in the pack; requires reconciliation with the frozen specification below.




One minimal smoke call first

	

Recorded as settled; requires a decision/source reference because Rev 26 previously left it open.




Six tasks, one per category

	

Recorded as settled; conflicts with the current frozen Stage 6 battery definition.




Identical per-task budgets

	

Correctly records the rule, not an invented number.




Fresh catalogue capture

	

Correctly recorded as a pre-flight requirement.

Material issues

1. Candidate and battery do not match the frozen Stage 5 specification.

Rev 26 still identifies the pinned subject as:

nvidia/nemotron-3-nano-omni-30b-a3b-reasoning

It also defines the Stage 6 battery around the 13 tree instances in the acceptance criteria. The pre-flight catalogue check is specifically tied to that pinned model identity.

The decision pack instead names Claude and six category tasks. I found no Shelf amendment reconciling those changes with Rev 26.

This is not just a catalogue-refresh detail. A fresh catalogue capture establishes availability; it does not change the frozen model identity or replace the defined battery.

Required resolution: identify the approved amendment or decision that changes the candidate and battery, and show how the Stage 5 package's pinned configuration and 13-instance requirements apply to the new arrangement. If the six tasks are intended to replace the existing battery, that replacement needs explicit authority and a specification change.

2. The smoke-call decision needs its authority identified.

Rev 26 §6.1 records the default as no smoke call and expressly leaves the question of making one to Ben's Stage 6 authorisation. The pack says the later decision is settled, but does not identify the decision record that superseded that default.

The one-smoke-call-first choice can stand if that later decision is authoritative. The pack should cite it, rather than leaving a reader to infer that the old default disappeared.

3. The prior Stage 6 authorisation is described inconsistently.

The pack says Ben's 12 November authorisation stands, but then lists the go itself as an open decision because RB-46 preserves Ben's separate Stage 6 decision.

Those statements need to be distinguished:

The earlier conditional authorisation is part of the history.

RB-46 expressly leaves Ben's separate Stage 6 decision as a distinct authority point.

No execution follows from this adjudication or the pack.

The pack should say plainly that an explicit current go remains required before any live call.

Items that should not remain open questions

Order is already settled. Rev 26 §7 places independent package inspection at step 6 and Ben's Stage 6 execution authorisation at step 7. The pre-flight decision should follow the inspection; there is no need to ask whether those steps may be reordered or run concurrently.

The remaining genuine decisions for Ben are:

Whether to give the separate Stage 6 go, after the required inspection.

The actual per-task budget.

The smoke-call pass criteria and who formally records its pass/fail.

The candidate/battery reconciliation described above, unless the governing amendment can be produced.

Confirmation that the smoke-call decision is supported by the later authority that superseded Rev 26's default.

Final disposition

Torn-write repetition: no repeat unless relevant crash-evidence machinery changed; exact repeat criteria are stated above.

Decision pack: useful, but not yet a clean decision basis. It needs the candidate/battery conflict reconciled, the smoke-call authority referenced, and the prior-authorisation wording corrected.

Stage 6: not started. No live call or execution authorised by this adjudication.

The next useful step is for Remmy to update the pack with those precise corrections and source references. I can take the parallel source-to-spec reconciliation so she does not have to carry both pieces of work.

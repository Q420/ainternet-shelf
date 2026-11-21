# ALEX — BATCH 6 ADJUDICATION (desk conversation (8) copy, 2026-11-15)

Filed by Remmy from the Remmy Browser watcher delivery,
2026-11-15 ~02:42 MST, conversation 6af97d1d ("Batch 5
Reinspection Review (8)"), where it answers RB-41.

RELATIONSHIP TO THE FILED ADJUDICATION
(ALEX-BATCH6-ADJUDICATION-2026-11-15.md, conversation (7),
watcher seq 416): this is the continuation conversation's own
adjudication of the same checkpoint. The dispositions AGREE
throughout: G1/G2/G3/G5 PASS, G4 NOT PASSED, F-G4-1/F-G4-2
correction AUTHORISED, T03 remediation ACCEPTED, Batch 6
incomplete. Two differences: (1) this copy does NOT raise
F-G4-3 (the 8-of-13 coverage finding) — the correction round
was executed to the stricter union of both texts, F-G4-3
included; (2) this copy adds two things the filed copy does
not state in this form: Claude's inspection items 1 and 2 are
CLOSED, and the T03 acceptance carries a provenance
qualification — Correction B's underlying answer was fixed in
the pre-existing pinned source, but its explicit
expected-value entry was not pre-registered in Calibration
01; Alex preserves the distinction and does not reject the
remediation on it. The trailing "Review corrected G4 battery
/ Tap to set up" lines are ChatGPT UI chrome, not Alex's
text. This filing is NOT a reply to RB-42; the G4
re-judgement remains awaited.

---

Preliminary adjudication

Batch 6: NOT PASSED at this checkpoint.

G1, G2, G3 and G5 are reported PASS. G4 is explicitly NOT PASSED: the full battery did not complete, T05 stopped, T08's recovery path crashed, and T09 was never reached. A verified partial execution prefix is useful evidence, but it cannot establish a full-battery pass.

F-G4-1 and F-G4-2: candidate (a) is the correct correction route.

Correct the Batch 3 driver so _insert_values presents the tagged form required by the already-corrected tools.

Correct the T08 recovery-input builder so a failed STEP-03 cannot cause an uncaught KeyError.

Re-pin the corrected driver and rerun the full battery as one controlled correction round.

Do not reopen the tools' closed presentation union.

Claude independently confirmed both defects and the run-record chain. The examiner's order-independent refusal-pairing correction is also material: it must be the examiner used for the re-run, with G1's re-derivation under that version retained as evidence.

This is a correction authorisation, not a retrospective G4 pass. No Batch 6 completion or progression past G4 until the full battery succeeds.

Claude's inspection items 1 and 2
Closed

I inspected the updated bundle files.

test_g4.py now resolves its inputs from inside the bundle when run in bundle layout. The previously missing freeze and stack manifests are included.

The corrected examiner is 56492523…. The new G1 re-derivation report records 13/13 checks passing with unchanged verdicts.

The original examiner remains preserved under its original hash.

The basename collision for stub_subject.py is explicitly resolved using the run's stack manifest. It does not invalidate the G4 audit.

T03 substantive review
Accepted — with one provenance qualification

I checked the actual source documents, amended rules, pre-amendment artefacts and both calibration certificates.

1. Are the new extractions faithful? Yes.

The source text in alex-combined-adjudication-v010#002 contains:

**R47 — PASS, narrow.**

**R60 — FAIL.**

**R65 — PASS, qualified.**

The corrected patterns match those literal bold segments, capture group 1, and produce the exact source wording. The rules engine accepts a result only when there is exactly one valid match. Certificate 02 records one valid match and zero rejected matches for each.

Correction B is also correctly handled. The newly included alex-combined-adjudication-r60rev#001 contains Correction B — OPEN; a failing case stands. The existing EXT02-CB-1 extracts OPEN. The certificate records the expected section hash, 393cba4c…, and successful resolution.

No source text or disposition was rewritten to accommodate the rules.

2. Was the answer set fixed before the rules changed?

There are two distinct cases:

R47, R60 and R65: yes, demonstrably. Calibration 01 already recorded the three dispositions in its expected values, before the extraction rules were amended. The new rules make those existing answers machine-extractable; they do not invent them.

Correction B: the underlying answer was fixed, but its explicit expected-value entry was not pre-registered in Calibration 01. The authoritative R60REV source was already in the frozen corpus snapshot, with its existing hash. Its content already established OPEN. Certificate 02 records that expected value after the pack addition.

I consider the second distinction worth preserving, but not a reason to reject the remediation. The independent authority is the pre-existing pinned source, not the post-amendment test assertion.

T03 verdict: ANSWERABLE accepted. The move from Calibration 01 to 02 is supported by a genuine correction to extraction coverage and pack membership, not by changing the underlying answer.

The transcript overwrite is also properly disclosed. Certificate 01 itself remains byte-identical, but its original runner transcript is lost; I will not treat that transcript as preserved evidence.

Final disposition

Item

	

Adjudication




G1

	

PASS




G2

	

PASS




G3

	

PASS




G4

	

NOT PASSED




G5

	

PASS




T03 remediation

	

ACCEPTED




F-G4-1 / F-G4-2 correction

	

AUTHORISED

T03 is eligible for inclusion in a Stage 6 battery under PILOT-CALIBRATION-02, subject to Stage 6's existing authority.

Batch 6 itself remains incomplete. The remaining work is the authorised driver correction, re-pin and complete G4 battery re-run. No tools-union reopening, no scope expansion, and no retrospective upgrade of the failed G4 run.

The checkpoint has done something useful: it exposed a real integration defect, preserved the failure evidence, and gave us a bounded correction route. That's a valid engineering outcome, but it isn't a passed gate.

When Remmy files the corrected G4 run, I can inspect the complete re-pinned bundle and issue the final G4 adjudication.

🔎

Review corrected G4 battery

Tap to set up

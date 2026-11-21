# Known Holes Statement — REV9 Submission

Bound into the REV9 submission write-up at Ben's instruction of
2026-11-20 20:40 MST ("Include those in the write-up"), referring to
the holes Remmy reported to Ben in chat at 2026-11-20 20:40 MST.

These eight holes are stated as reported. They are not softened,
and none is resolved by this statement. Each is structured as:
the hole stated plainly / the evidence for it / whose decision or
what work closes it / current status.

---

## Hole 1 — The Gate Format Definition artefact does not yet exist

**The hole, plainly:** REV9's verification method leans on a pinned
Gate Format Definition — format is to be *computed* against it —
but that definition has not been written. Until it exists, "format
is computed, not judged" is a requirement, not a mechanism.

**Evidence:** The design paper (ID-FORMAT-SHELF-DESIGN-2026-11-20)
names the Gate Format Definition as a required artefact; the REV9
draft (RELAY01-PACKAGE-REV9-DRAFT) flags in its open items whether
the artefact must be exhibited inside the package before a Gate 1
PASS or produced at case freeze under a conditional PASS. No file
containing the definition exists in the package or on the shelf.

**Closed by:** The work of writing the definition, and Vane's
settlement (at Gate 1) of when it must be exhibited.

**Status:** OPEN.

## Hole 2 — Who performs format computation is unsettled

**The hole, plainly:** The design does not settle who runs the
format computation in run-02 — orchestrator machinery,
participant-side tooling, or both. The orchestrator-only variant
weakens checker independence: the machinery that runs the relay
would also be computing the format verdicts on its own run — the
worker grading its own homework, the failure mode named when the
flow-checking principle was set (2026-11-20 19:51 MST).

**Evidence:** Design paper §6 records the question as open; the
REV9 draft states all three variants with their independence
consequences and resolves none of them.

**Closed by:** The examiner's settlement at Gate 1 (Vane), as a
package condition.

**Status:** OPEN.

## Hole 3 — LLM fluency in applying the record form is untested

**The hole, plainly:** The design assumes models can read the
catalogue faces and produce records in the adopted form
consistently. That has never been tested. Ben put the question
directly (2026-11-20 20:18 MST): are LLMs going to understand
this fluently? Recognition of an established syntax is not the
same as applying it identically; Gate A failed on exactly that
distinction — two models, same input, opposite verdicts, because
the task left room to judge. Machinery computation of format
reduces the exposure but does not eliminate it: participants
still read citations and produce records.

**Evidence:** No multi-model fluency test has been run. The cheap
test exists in description only: several models, the same easy
file, the same written rules, cold — compare the records they
produce against the stated pass mark (same rules, same record).

**Closed by:** Running that test and recording its result —
before run-02 relies on participant-produced records, or as a
Gate 1 condition.

**Status:** OPEN — UNTESTED.

## Hole 4 — The run-02 participant set is an unresolved contradiction, and provider failure is unclassified

**The hole, plainly:** REV8's Gate 1 verdict bars substituting
participants or models under REV8's authority. The design
freeze's seven assignments belonged to run-01. REV9 therefore
carries the run-01 set as an *unasserted default* — a draft can
do that; a run cannot staff itself on an unasserted default.
Separately: Gemini returned HTTP 503 on the run-start invocation
and on the single protocol retry in run-01's Gate B
(2026-11-20). A repeat at run-02's run-start is foreseeable, and
the design does not yet classify it: is a provider's repeated
503 a run failure, or an environment fact to route around — and
who may decide?

**Evidence:** Vane's REV8 verdict (substitution bar); the design
freeze's assignment section (run-01's seven); run-01 event
ledger seq 7 and the Gate B records rs8-gemini / rs8-gemini-r2
(both HTTP 503, preserved).

**Closed by:** Explicit settlement of the run-02 participant set
by Ben and the examiner, and a design ruling classifying
provider failure at run-start, with its decision authority named.

**Status:** OPEN.

## Hole 5 — Run-02's verification cost is asserted cheaper, not measured

**The hole, plainly:** The new verification is cheaper than
run-01's 1,373 judged manifest lines by construction, but no
end-to-end cost for run-02's verification exists — joint
examinations, re-derivation, catalogue checks, run-start calls,
gates. Ben's constraint (2026-11-20 19:50 MST): verification
cannot take three hours per job; whether Duenna helps *at a
price anyone would pay* is part of the proving question the
relay exists to answer. The design asserts cheapness by
comparison; it does not measure.

**Evidence:** No timing estimate or dry accounting for run-02's
verification appears in the design paper, either annex, the
adoption spec, or the REV9 draft.

**Closed by:** A priced accounting of run-02's verification
before the run, or a measured record of it during the run,
reported against Ben's constraint.

**Status:** OPEN.

## Hole 6 — Incorporation hashes were computed on local files; shelved bytes must be read back

**The hole, plainly:** REV9 incorporates the design paper and
both annexes by SHA-256 computed on the office's local files.
What the examiner reads is the *shelved* bytes. If the shelved
copies differ from the local files, the pins point at bytes the
examiner never sees, and the incorporation is false in fact.

**Evidence:** The REV9 draft's incorporation hashes (design paper
aae71134…, Annex A a8b17eb9…, Annex B 198f0d5a…) were computed
locally at drafting. They match the originals copied into this
bundle (see BUNDLE-MANIFEST.md), but no read-back of shelved
bytes has yet occurred, because nothing has been shelved.

**Closed by:** Remmy, at the shelving step: after pushing, read
each shelved file back from the shelf and verify its hash equals
the incorporated pin; record the read-back in the submission.

**Status:** OPEN — closes at shelving; Remmy's action.

## Hole 7 — Remmy's first-hand review of REV9's full text is still owed, and it gates this submission

**The hole, plainly:** Remmy has verified REV9's existence, size,
and SHA-256, and has reported its delta from the drafting record.
She has not yet read the draft's full text first-hand. A
submission she has not fully read is a summary carrying a file,
not a reviewed package.

**Evidence:** Remmy's own report to Ben (2026-11-20 20:40 MST)
states the review is owed. This bundle is preparation only,
assembled under the copy rule; it does not cure the hole.

**Closed by:** Remmy's first-hand read of
RELAY01-PACKAGE-REV9-DRAFT.md in full, with any defects found
reported before submission.

**Status:** OPEN — this submission is GATED on it. Nothing in
this bundle is to be shelved or sent until the gate clears.

## Hole 8 — Annex B's adoption rests on Ben's steers, not a formal adoption ruling

**The hole, plainly:** REV9 treats Dublin Core (Annex B) as the
operative direction. The record supporting that is a sequence of
Ben's steers — the flamboyance steer away from PMEST
(2026-11-20 20:19), the citation-form opening (20:20), the
collaboration direction (20:22), and "proceed with our latest"
(20:31). A steer is not a ruling. The package's vocabulary layer
currently rests on interpretation of direction, the exact
condition that has produced "similar isn't the same" failures
before.

**Evidence:** REV9 §7.1 flags the formal adoption ruling as
Ben's to confirm; the Adoption Spec (Part 5) records the same
point as open, and its Part 2 falls if Ben rules otherwise.

**Closed by:** One sentence from Ben adopting Annex B (Dublin
Core) as the catalogue direction, in the package's terms — or
ruling otherwise.

**Status:** OPEN — Ben's decision.

---

## Additional, flagged by the assembler

*One further item, recorded separately at the assembler's
judgement and NOT merged into the eight above.*

**Contained items have no fingerprint of their own.** C1 — the
run's authorised correction — exists as frozen as a clause
inside REV5. Both annexes hit the same wall independently:
a contained item resolves only by its container's digest plus a
locator; neither syntax gives it an identity of its own, and the
annexes refuse to pass the container's fingerprint off as the
item's. In a run, the sealed delivery artefact mitigates this at
delivery time. At the design level the problem is named, not
solved; its proposed answer (the v3 Part II information model)
is itself unexamined (design paper §6 Q4). Flagged for Ben and
the examiner alongside the eight.

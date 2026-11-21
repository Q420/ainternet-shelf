# Alex — Independent Inspection of Rev 19 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfnjkpj-h-krsu · Relayed 2026-11-13 ~16:13 MST.
Headline: **NOT CLEARED / NOT YET FIT TO BUILD FROM** — the two Rev 18 findings are materially corrected and the incorporation was verified against the full Rev 18↔19 diff (changes confined to the five approved locations; blob 6ff75ce0…; file SHA-256 not recomputed by him). **Two MEDIUMs remain, both specification-completeness:** **(1)** the EOF-first / drained-channel behaviour has **no named demonstration** — D-T1…D-T4 test successful STATUS reporting, not the launcher-lost path; a Batch 4 demonstration must show the launcher exiting/failing before STATUS, the supervisor draining and establishing EOF without a STATUS, the record closing as PRE_RELEASE_LAUNCHER_LOST with the exact facts, no issuance, **plus a queued-STATUS-plus-HUP control** (a STATUS already queued when HUP is observable is consumed and validated, not lost), and must distinguish drained-EOF from the timeout outcome. **(2)** the **shared-flag contract** is stated only in Stage 5; Stage 8's ordinary sequence and the Stage 6 gate-write-failure path still read as bare waitpid→STATUS sequences — the spec must state the flag transitions at every applicable path (who sets `reaped` and when; `sent` always before transmission; how an already-set flag prevents a second operation; how the class-T path composes with the ordinary path), so the contract does not depend on builder inference.

---

Rev 19 independent inspection — NOT CLEARED / NOT YET FIT TO BUILD FROM

I retrieved and inspected the exact Shelf pin:

File: duenna/STAGE5-BUILD-SPEC-19.md

Commit: 4aa02638

Git blob: 6ff75ce06dccb6531051694833584923e2d135b8

Reported SHA256: 46c22e76f2cce7c9985016a725bd06a87b49c94267a97297019bd6eabc2eb481

Rev 18 comparison source: a0f33fb4, blob 706483efd27bab03f9ab3956c21dd6ee6f983d85

I have not independently recomputed the reported file SHA256. The fetched Git blob and content are verified against the stated pin.

1. Incorporation check

The two corrections from Rev 18 are incorporated in the normative text.

The three-way reaped/sent dispatch is present.

The ordinary both-false path abandons settling, performs one blocking waitpid(), retries EINTR, validates the returned PID, retains the raw status and sets sent before transmission.

Other waitpid errors produce no invented status, no STATUS transmission and non-zero launcher exit.

The already-sent and reaped-but-unsent branches are defined.

The drained-channel EOF definition is present, including the requirement to consume queued packets before establishing EOF.

PRE_RELEASE_LAUNCHER_LOST has the required facts and remains distinct from bound expiry.

S4/S5 and D-T2/D-T3a have been aligned.

The plan's two binding clarifications are present.

2. Diff inspection

I compared the complete Rev 18 and Rev 19 texts.

The changes are confined to:

Revision identity and lineage in the front matter.

The new §0E incorporation record.

The Stage 5 class-T receipt transition.

The class-T terminal-observation rules.

The S4/S5 state-table rows.

D-T2 and D-T3a expected records.

I found no unrelated substantive changes in the comparison. The five incorporation locations correspond to the approved plan.

3. Remaining findings

MEDIUM — EOF-first and drained-channel behaviour lack a named demonstration.

The new specification defines the EOF-first outcome, but the existing D-T1 through D-T4 demonstrations do not explicitly test it.

D-T2 and D-T3a test the ordinary class-T receipt path and successful STATUS reporting. They do not demonstrate:

The launcher exits or fails before transmitting STATUS.

The supervisor drains the channel and establishes EOF without a STATUS.

The record becomes PRE_RELEASE_LAUNCHER_LOST with the exact required facts.

No issuance occurs.

A STATUS already queued when HUP/EOF is observable is consumed and validated rather than lost.

This is important because the drained-channel clarification is now part of the protocol's correctness, not merely descriptive prose.

Please add an explicit Batch 4 demonstration and expected record for the EOF-first case, including a queued-STATUS-plus-HUP control. The test must distinguish actual EOF after draining from a timeout.

MEDIUM — Shared flag integration needs a more explicit contract.

Stage 5 says reaped and sent are the session's single state and that Stage 8's ordinary waitpid/STATUS path uses the same flags.

However, Stage 8 still describes the ordinary sequence only as waitpid() followed by STATUS. It does not explicitly state the flag transitions and ordering there. The Stage 6 gate-write failure path also contains a waitpid/STATUS sequence without an explicit reference to those flags.

The specification should make the shared-state contract unambiguous across every applicable waitpid/STATUS path:

Which path sets reaped, and precisely when.

Which path sets sent, and confirmation that it is always set before STATUS transmission.

How an already-reaped or already-sent state prevents a second operation.

How the Stage 5 class-T path composes with the ordinary reporting path.

The intent is clear; the implementation contract should not depend on the builder inferring the flag updates from the Stage 5 paragraph.

4. Disposition

Rev 19 plan incorporation — Accepted.
Class-T three-state dispatch — Accepted.
Blocking waitpid / EINTR / PID validation — Accepted.
No invented STATUS on error — Accepted.
sent before transmission — Accepted.
Drained-channel EOF definition — Accepted.
PRE_RELEASE_LAUNCHER_LOST facts — Accepted.
S4/S5 table alignment — Accepted.
D-T2/D-T3a alignment — Accepted.
EOF-first demonstration — OPEN — MEDIUM.
Shared flag integration across reporting paths — OPEN — MEDIUM.

No build authorisation. No Stage 6 authorisation. Batch 2 remains CLOSED.

The two original Rev 18 findings are materially corrected in the specification. I am withholding clearance because the new protocol behaviour needs an explicit acceptance demonstration and the shared flag contract needs to be complete across the reporting paths.

I can independently inspect the next exact pin and cross-check the added demonstration and flag transitions once you have the correction plan ready. No Crusher retrieval is needed; the relevant evidence is already available locally or on Shelf.

Preserve Rev 19 unchanged. Append the correction plan and subsequent inspection as new records.

— Alex

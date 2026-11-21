# Alex — Rev 16 Independent Inspection Verdict (shelved verbatim from the bridge relay)

PB-ID: pb-mwflcjg1-3-lf5g · Relayed 2026-11-13 ~15:12 MST.
Headline: **NOT CLEARED — NOT YET FIT TO BUILD FROM.** Ben's Option A architecture ruling ACCEPTED; §0B.1 accepted as the governing model; D-18 CLOSED (accepted). Three HIGH build blockers, all body-level: (1) §3.5 still implements the old two-process architecture — reconcile the entire process sequence, not one sentence; (2) the descriptor/pidfd protocol is still a requirement, not a specification — define it executably; (3) D-9 source-pinning chronology still contradicts §0B.3 at §3.5 point 2 and §4 Batch 4. C rationale substantially accepted with an evidence qualification. His assignment: a considered correction plan for the three blockers, his independent pass on it BEFORE incorporation.

---

REV 16 INDEPENDENT INSPECTION — NOT CLEARED / NOT YET FIT TO BUILD FROM

I retrieved and inspected the exact Rev 16 pin:

duenna/STAGE5-BUILD-SPEC-16.md

Commit 5373a416602cfbe5dd831dea9e3e13a582aa6832

Git blob: 42d0c64daa4052edc40babbe623760a0f9499dd9

5,282 newline-separated records; consistent with the reported 5,116-style conventional line-count distinction? No: Rev 16's retrieved content has 5,282 newline-separated records.

I have not independently recalculated the claimed SHA256 91115e3b…; the Git blob identifier is verified, not that file SHA256.

I also retrieved the architecture decision at ef060d23, the recovered Claude Rev 11 report at 9a98ed9c, the Rev 14 interim report at d6d3dc92, and D-18 dispositions at 8cdcd710.

1. Ben's architecture ruling

The ruling is coherent. I accept Option A as the correct architecture direction.

The separation is sound:

Launcher: harness child's OS parent, waitpid() owner and child-status reporter.

Supervisor: issuance, commitments, records and terminal-event authority.

Child pidfd: independent supervisor-side evidence of child termination.

Status channel: explicit, acknowledged reporting path.

Option B remains rejected; it should not reappear as a fallback.

The four corrections are appropriate and necessary. In particular, the distinction between launcher disappearance and proven child termination is essential. A status-channel EOF cannot establish that the child has died.

I do, however, distinguish approval of Ben's architecture decision from approval of Rev 16's implementation specification. The decision is sound; the operative body has not yet been brought into full agreement with it.

2. Blocking finding — §3.5 still implements the old architecture
HIGH — BUILD BLOCKER

§0B.1 correctly states the new three-process model. But §3.5 still contains substantial passages from the former two-process model.

The clearest contradiction is at lines 3771–3791:

The text says the parent runs as the run's supervisor after releasing the gate.

It says that parent holds waitpid() for the harness.

It says that parent performs every issuance itself.

That is the old architecture. Under Ben's ruling, the launcher remains the child's parent and reaper, while the separate Python supervisor owns issuance and the record.

This is not resolved by superseding one sentence in §3.5. The surrounding process description still assigns the old responsibilities to the launcher/parent. The earlier spawn and privilege-transition passages also need to be rewritten against the three-process model, not merely annotated.

Required correction: reconcile the entire affected §3.5 process sequence with §0B.1. Identify the supervisor process, launcher process and harness child separately at every stage. The resulting description must consistently assign:

OS parenthood and waitpid().

Privilege transitions.

Child pidfd creation and transfer.

Gate release authority.

Terminal-event decisions.

Issuance and commitments.

Launcher exit and failure handling.

No build clearance until this is consistent throughout.

3. Blocking finding — the descriptor protocol is still a requirement, not a specification
HIGH — BUILD BLOCKER

§0B.1(D) correctly requires request framing, status framing, descriptor ownership, close-on-exec behaviour, EOF semantics, malformed/partial-message handling and acknowledgement.

But it does not actually define those things.

Likewise, §0B.1(C) requires the child pidfd to reach the supervisor before gate release, but does not define the transfer protocol or the precise handoff sequence.

The specification needs to state, at minimum:

Which process creates each descriptor.

Which process owns each end.

How the pidfd is transferred.

How the supervisor confirms receipt and validity.

How the launcher knows the handoff has been acknowledged.

Exactly when the launch gate may be released.

What happens if transfer, validation or acknowledgement fails.

How complete, partial, malformed and absent status messages are distinguished.

How the supervisor observes actual child termination if the launcher disappears.

The ruling already establishes the right safety principle: no gate release without the supervisor holding the child-lifecycle handle. Rev 16 must turn that into an executable protocol rather than leave the implementation to decide.

4. D-9 — source timing remains contradictory
HIGH — BUILD BLOCKER

§0B.3 correctly says the C source must be pinned and inspected before Batch 4 begins.

However, §3.5 point 2, lines 3441–3442, still says the source is pinned at the Batch 4 checkpoint. §4's Batch 4 description, lines 4865–4868, repeats that timing.

Those instructions conflict with §0B.3 and Claude's recovered condition.

The required sequence is:

Batch 0 freezes behaviour and interface.

Launcher source is written against that interface.

Source is pinned by hash and inspected.

D-9 disposition is recorded.

Only then may Batch 4 begin.

The Batch 4 checkpoint can record the built binary and its evidence. It cannot be the first source-pinning event.

5. C rationale — substantially improved, one qualification

§0B.2 now has the four-part structure requested:

Necessity.

Concrete properties.

Why C.

What is pinned and inspected.

That is a meaningful improvement. It correctly says language choice alone proves nothing.

One qualification remains: the comparison with Rust, Go and Zig and the claim that the system C toolchain is already inside the custody boundary need evidence. The toolchain, linker mode, dependencies and binary properties must be pinned and inspectable. The phrase "no runtime services" must not be treated as proof that the binary has no runtime or dynamic dependencies.

I would retain the C decision in principle, subject to those concrete properties being demonstrated. This is not, by itself, the reason Rev 16 is withheld.

6. D-18 — accepted

I independently retrieved the recovered Claude Rev 11 report and the individual disposition record.

All eight findings and both gaps are individually represented. The record preserves the important distinction between specification-level correction and future implementation evidence.

I accept D-18 as CLOSED AS A SOURCE/INSPECTION BLOCKER.

That does not mean the associated implementation gates have passed. The caution in §0B.4 is correct: G1, injector exclusion and other implementation-dependent evidence remain outstanding.

7. D-9 — status accepted

The recovered Claude interim report confirms the conditional language acceptance.

The status in §0B.3 is correct:

Alex: approved in principle.

Claude: conditionally accepted at interim; final disposition pending.

Build: not authorised.

The source inspection timing still needs the correction described above.

Required disposition

- Ben's Option A architecture ruling: ACCEPTED
- §0B.1 architecture statement: ACCEPTED as the governing model
- §3.5 process implementation: OPEN — HIGH
- pidfd and status-channel protocol: OPEN — HIGH
- D-9 source-pinning chronology: OPEN — HIGH
- C-language rationale: SUBSTANTIALLY ACCEPTED; evidence qualification
- D-18: CLOSED
- Rev 16 overall: NOT CLEARED

Remmy: please preserve Rev 16 and its evidence unchanged. Prepare a considered correction plan for the three blocking inconsistencies: the complete §3.5 process model, the descriptor/pidfd protocol, and D-9 source timing. Do not patch individual sentences while leaving the underlying process model contradictory.

I can take the next independent pass on the proposed corrected process sequence and protocol before you incorporate them. That should reduce the chance of another revision cycle caused by a local wording fix that misses the architecture.

Authority remains unchanged: Batch 1 CLEARED; Batch 2 CLOSED; Stage 6 UNAUTHORISED. This inspection authorises no build, model call, provider contact or branch promotion.

⟦ALEX-FINAL⟧ Rev 16 is a substantial improvement and Ben's architecture decision is sound. But the specification still describes the old process model in §3.5, does not define the required descriptor protocol, and retains a conflicting Batch 4 source-pinning instruction. Those are real build blockers. Fix the architecture as a whole, then inspect the resulting pin again.

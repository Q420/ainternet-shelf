# ALEX — STAGE 6 BATTERY PREPARATION INSPECTION RULING (2026-11-17)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna
conversation (6afc1993), inspecting
`duenna/STAGE6-BATTERY-PREPARATION-2026-11-17.md` @ 043c221e.
Captured first-hand; filed verbatim below (the reply's tables
are flattened by page extraction; every finding is preserved).

## Substance

ACCEPTED WITH CORRECTIONS. No redesign. (1) Retry policy RULED:
frozen max_attempts 2 retained; the budget calculations are
confirmed correct. (2) The 2,048-token input allowance is NOT
yet verified: actual pack prompt sizes must be measured for
every model call; if 2,048 is not a valid upper bound, the
per-instance ceilings are recalculated. (3) Relay trust story
CORRECTED: the relay is part of the trusted transport path (it
receives the complete request and can affect integrity and
confidentiality); the preparation must state this explicitly
and bind the relay to the run's trust evidence (pinned relay
artefact/config in custody evidence; fixed upstream; faithful
forwarding; no persisted headers/bodies/credentials; no
direct-connection fallback). (4) The dress rehearsal evidence
remains outstanding: the 13-instance transport-double rehearsal
must be run and its results available for the final inspection.
The ruling authorises no build, live call, arming or execution.

---

Stage 6 battery preparation — inspection ruling
ACCEPTED WITH CORRECTIONS

I inspected the filed preparation assembly at 043c221e against the frozen adapter, calibration inventory, Rev 26 budget rules, smoke adjudication and accepted G4 correction-round evidence.

The overall design is sound. I do not see a reason to redesign the preparation or change the agreed architecture. Four points need resolving before the preparation can be treated as complete.

1. Retry policy — ruled

Retain the frozen max_attempts: 2.

The smoke's reduction to one attempt was specific to its one-call, 5,000-token ceiling. It does not supersede the frozen battery policy.

The preparation's calculations are correct:

Instance type

	

Worst-case calculation

	

Total




Single-step

	

2 × (20,480 + 2,048)

	

45,056




T03, two steps

	

2 × 2 × (10,240 + 2,048)

	

49,152

Both are within the 50,000-token limit, provided the input allowance is confirmed.

The frozen retryable classes remain unchanged. No discretionary retry expansion.

2. Input allowance — confirmation required

The 2,048-token input allowance is still provisional. The document explicitly says actual pack prompts have not yet been measured.

This matters particularly for T03: its calculated worst case is already 49,152, leaving only 848 tokens of headroom.

Before finalising the preparation:

Measure the actual input size for every model call from the pinned pack.

Confirm that 2,048 is a valid upper bound.

If it is not, recalculate the per-instance completion ceilings.

The budget derivation is accepted; the input assumption is not yet verified.

3. Relay trust story — correction required

Route 2 is the owner's decision. I accept the tunnel-relay architecture as the selected route.

However, the relay cannot be treated as a transparent, untrusted conduit simply because it never receives the real NVIDIA credential.

It receives the complete request, attaches the surrogate and forwards the request. It can therefore affect the integrity and confidentiality of the model interaction. It is part of the trusted transport path.

The preparation must make that explicit and bind the relay to the run's trust evidence.

The verification should establish:

The relay artifact and configuration are pinned and identifiable in custody evidence.

The upstream is fixed to the NVIDIA completions endpoint; alternate hosts and paths are rejected.

Request method, path and body are forwarded as intended.

Response status and body are returned faithfully.

No headers, bodies or credential material are persisted in relay logs.

Failure does not create a direct-connection fallback.

This is a clarification and verification requirement for the selected architecture, not a request to reconsider Route 2.

4. Dress rehearsal — evidence remains outstanding

The preparation describes the correct next verification work, including the full 13-instance transport-double rehearsal.

I found the plan, but not completed rehearsal evidence in this assembly.

The rehearsal must demonstrate the complete battery machinery and custody path without a live model call. Its results must be available for the final inspection described in §6(e).

I am not treating the planned rehearsal as completed or certifying evidence that has not yet been produced.

Final disposition

Area

	

Ruling




13-instance inventory

	

Accepted




14 expected calls

	

Accepted




Frozen retry policy

	

2 attempts retained




Budget derivation

	

Accepted, subject to input measurement




Laptop-room custody venue

	

Accepted




Route 2 relay architecture

	

Accepted, trust-boundary correction required




Four adapter differences

	

Accepted in principle




Verification plan

	

Accepted, rehearsal evidence outstanding

No redesign is required. The corrections are limited to making the budget assumption demonstrable, making the relay's trust position explicit, and completing the planned rehearsal evidence.

This ruling accepts the preparation direction with those corrections. It does not authorise a build, live model call, battery arming or battery execution.

The next authority remains exactly where the owner placed it: after preparation is complete and inspected, the owner decides separately whether to authorise execution on the owner's laptop.

⟦ALEX-FINAL⟧

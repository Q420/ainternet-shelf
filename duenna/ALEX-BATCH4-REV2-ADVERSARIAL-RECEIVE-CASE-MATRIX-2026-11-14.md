# Batch 4 — Adversarial Receive-Case Matrix
Prepared by Alex against Whole Plan Rev 2, 2026-11-14.
Review/test-oracle aid only. It does not amend the protocol catalogue, freeze, Rev 26, chunk sheet, or Ben's authority record.

## Pins examined
- Whole Plan Rev 2: commit 9b84c4dbeaa08054d3e92bb31b52b30f6380b5f4; file SHA-256 stated by Remmy: b04d667d6bdb107035885244ec0241f828b55ef1a87a8c1a2620c0a35dc68733.
- Launcher interface freeze: `duenna/launcher-interface-freeze.md`; SHA-256 6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5.
- Rev 26: `duenna/STAGE5-BUILD-SPEC-26.md`, §3.5 point 3 and its protocol state table.
- Q7 report: blob e60a48c9595725f2623d965e45b7167598a0bfa8.
- NQ3 report: blob af56f57277955d9727b4e2913e2a8a4a45899229.

## Classification vocabulary
- CLEAN: exactly the expected packet for the current site/state; dispatch only the existing contract action.
- POISONED: one or more pending zero-length receives precede an otherwise valid expected packet; do not act on that packet.
- VIOLATION: malformed, wrong-type, badly framed, invalid ABORT, unexpected sequence, ancillary data, or truncation; fail closed using the existing site's violation/refusal route.
- CLOSURE-EQUIVALENT: after RDHUP/HUP, a zero return; apply the existing site's EOF outcome. Q7 limitation is explicit: descriptor-free empty records immediately before shutdown may be indistinguishable and are treated as closure-equivalent.
- RECEIVE ERROR: use the site's existing receive-error outcome, not its EOF outcome.

## LAUNCH_REQUEST receive site

| Adversarial input / ordering | Expected classification | Required effect |
|---|---|---|
| One correctly framed LAUNCH_REQUEST with matching run ID, supervisor PID, child uid/gid | CLEAN | Validate request; only then proceed to pipe/fork. |
| Peer closure before any request; no pending zero | CLOSURE-EQUIVALENT | Pre-fork refusal, exit 15 route; no fork, child, STATUS or issuance. |
| One or more pending zero-length receives, then peer closure (RDHUP/HUP plus zero return) | CLOSURE-EQUIVALENT (Q7 limitation) | Pre-fork refusal, exit 15 route; no fork, child, STATUS or issuance. Do not claim the pending zero records were proven absent. |
| Receive error before any request | RECEIVE ERROR | Same pre-fork refusal route, exit 15; no child exists to clean up. |
| One or more zero-length receives, then a valid LAUNCH_REQUEST | POISONED | Refuse on exit 15 route; request not acted on; no fork. |
| Zero-length receive(s), then malformed/wrong-type/unexpected packet | VIOLATION | Refuse pre-fork; no fork. |
| Malformed request length/header/flags; wrong message type; mismatched run ID, PID, uid or gid | VIOLATION / site refusal | Refuse pre-fork; no fork. |
| Ancillary descriptor attached to any packet | VIOLATION(ancillary) | Close every delivered descriptor immediately; no fork. |
| MSG_CTRUNC | VIOLATION(truncated) | Fail closed; no fork; no descriptor survives. |
| Repeated/unexpected packet sequence after a request that should complete the site | Not consumed by this collection | The site closes on the expected request; subsequent data belongs to no authorised next state and must not actuate a second operation. |

## HANDOFF_ACK receive site

| Adversarial input / ordering | Expected classification | Required effect |
|---|---|---|
| Correct HANDOFF_ACK, valid framing and code 0 | CLEAN | Continue existing handoff/settling sequence. |
| Correct HANDOFF_ACK code 1 or 2 | CLEAN | Existing refusal/cleanup route; cleanup and exit 6. |
| Correct HANDOFF_ACK code 3 | CLEAN | Existing already-terminated route: reap only, preserve raw wait word and existing ABORT/status contract. |
| Well-formed supervisor ABORT, reason 1–7, exact reason-only framing | CLEAN | Validate with abort_packet_valid(); cleanup and exit 6. |
| ABORT with wrong length, nonzero flags, or reason outside 1–7 | VIOLATION | Cleanup; exit 8 route; do not dispatch invalid ABORT. |
| Wrong packet type, malformed ACK, invalid ACK code, or unexpected sequence | VIOLATION | Cleanup; exit 8 route; no release/actuation. |
| Zero-length receive(s), then otherwise valid ACK or valid ABORT | POISONED | Packet not acted on; cleanup; exit 8 route. |
| Zero-length receive(s), then ancillary/truncated packet | VIOLATION | Close delivered descriptors immediately; cleanup; exit 8 route. |
| Peer closure after zero-length receive(s), with RDHUP/HUP and subsequent zero return | CLOSURE-EQUIVALENT (Q7 limitation) | Cleanup and exit 6. Do not claim the queued zero record was proven absent. |
| Peer closure without pending zero | CLOSURE-EQUIVALENT | Cleanup and exit 6. |
| Receive error | RECEIVE ERROR | Cleanup and exit 9. |

## Stage 6 packet receive site

| Adversarial input / ordering | Expected classification | Required effect |
|---|---|---|
| One correctly framed RELEASE packet in the expected state | CLEAN | Perform existing readiness interlock and gate release; only successful one-byte gate write actuates. |
| Well-formed ABORT with valid reason 1–7 | CLEAN | Existing class-T/class-F lifecycle: only the designated class-T reason permits STATUS; class-F cleanup emits no STATUS. |
| ABORT with invalid framing, flags, length, or reason | VIOLATION | Cleanup; exit 8 route; no gate release. |
| Wrong message type, malformed RELEASE, unexpected packet sequence | VIOLATION | Cleanup; exit 8 route; no gate release. |
| Zero-length receive(s), then otherwise valid RELEASE | POISONED | Do not write gate byte; cleanup; exit 8 route. |
| Zero-length receive(s), then otherwise valid ABORT | POISONED | Do not dispatch ABORT; cleanup; exit 8 route. |
| Zero-length receive(s), then ancillary/truncated packet | VIOLATION | Close delivered descriptors immediately; cleanup; exit 8 route. |
| Peer closure after zero-length receive(s), with RDHUP/HUP and subsequent zero return | CLOSURE-EQUIVALENT (Q7 limitation) | Existing EOF choreography: close gate write end unreleased, reap child, send STATUS, exit 0. |
| Peer closure without pending zero | CLOSURE-EQUIVALENT | Same existing EOF choreography: gate closed unreleased, child reaped, STATUS, exit 0. |
| Receive error | RECEIVE ERROR | Cleanup; exit 9; no RELEASE actuation. |
| Gate write failure after a CLEAN RELEASE | Not a receive classification | Preserve existing gate-write-failed report, reap, STATUS and exit 0 contract. |

## Cross-site invariants

1. No empty record ever actuates a gate or authorises a spawn.
2. A pending zero is never silently discarded when a later expected packet arrives.
3. Ancillary descriptors are closed at receipt, not buffered for later classification; MSG_CTRUNC is a violation.
4. Invalid ABORT framing/reason is never dispatched.
5. EOF/closure-equivalent outcomes are site-specific: LAUNCH_REQUEST pre-fork refusal; HANDOFF_ACK cleanup/exit 6; Stage 6 gate EOF choreography/STATUS/exit 0.
6. Receive errors remain distinct from EOF: ACK and Stage 6 cleanup/exit 9; LAUNCH_REQUEST pre-fork refusal/exit 15.
7. Q7's indistinguishability remains an explicit limitation. NQ2' is a limitation demonstration, not evidence that queued descriptor-free empty records were detected.
8. No subject execution is part of this matrix or Batch 4; tests use the stub subject only.

## Open contract consistency check for adjudication
Rev 2 §A.0 says a pending zero can be classified by the attempt's own end. §A.5 says an empty record followed by attempt teardown receives no classification. These statements need one consistent definition before implementation: specifically, whether teardown closes the receive collection as a closure-equivalent event, or terminates the attempt while leaving the pending-zero collection unclassified. The matrix does not choose between them.

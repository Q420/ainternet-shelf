# STAGE 6 BATTERY — PREPARATION ASSEMBLY (2026-11-17)

**Status:** PREPARATION. Drafted by Remmy under the owner's go
(2026-11-17 02:11 MST). This document prepares the Stage 6 battery
for execution; it authorises nothing. Battery EXECUTION requires
the owner's separate word, after examiner inspection of this
preparation.

Governing facts: pass bar set by Alex in the smoke adjudication
(`record/ALEX-DUENNA-SMOKE-ADJUDICATION-2026-11-16.md`); budget
rules decided 2026-11-16 (free NVIDIA lane; 50,000 tokens per
instance; cap hit = BUDGET_EXHAUSTED = not passed; 3+ exhaustions
halt the run for review; no paid route without a new owner
decision); venue ruled by joint 6 (custody-grade runs in the
owner's laptop room); credential route ruled Route 2 by the owner
(2026-11-17 02:31 MST): tunnel relay, no key on the laptop.

## 1. Battery inventory (verified first-hand, 2026-11-17)

From `PILOT-CALIBRATION-02.json` and the corrected tree pack
(`pilot_trees.corrected.json`, 9 trees):

| Instance | Model steps | Expected calls (no retry) |
|---|---|---|
| T01 | T01-STEP-05 | 1 |
| T02 | T02-STEP-03 | 1 |
| T03 | T03-STEP-02, T03-STEP-04 | 2 |
| T04 | T04-STEP-03 | 1 |
| T05 | T05-STEP-06 | 1 |
| T06 | T06-STEP-E | 1 |
| T07 | T07-STEP-04 | 1 |
| T08 | T08-STEP-04 | 1 |
| T09 | T09-STEP-03 | 1 |
| T09/FR-A | T09-STEP-03 | 1 |
| T09/FR-B | T09-STEP-03 | 1 |
| T09/FR-C | T09-STEP-03 | 1 |
| T09/FR-VALID | T09-STEP-03 | 1 |

Total: 13 instances, 14 model calls before retries. Expected
verdict for every instance in the calibration: ANSWERABLE (the
per-instance verdict mapping to the pass bar's PASS / SUBJECT-FAIL
/ INVALID / NOT-SCORED / GOVERNANCE-FAIL is the examiner's, per
the adjudication).

## 2. Budget enforcement (preventive ceilings)

Rule: an instance's worst case — every model call the tree can
produce (model steps × TREE-level attempts × ADAPTER attempts),
every call returning the maximum completion, plus a per-call
input allowance — must not exceed 50,000 tokens. Input
allowance: 2,048 tokens per call, CONFIRMED by measurement
(`duenna/STAGE6-BATTERY-INPUT-MEASUREMENT-2026-11-17.md`;
largest measured call ~1,179 tokens; the two conditional
recovery calls bounded by construction in
`duenna/STAGE6-BATTERY-PREPARATION-CORRECTIONS-2026-11-17.md`).

Frozen adapter values retained: temperature 0.6, top_p 0.95,
retry max_attempts 2, thinking enabled, reasoning budget 16384,
stream false. The one derived value is per-instance max_tokens,
set by the instance's true worst-case call count:

- 2-call instances (T04, T06, T07, T09 ×5): frozen 20,480
  retained. Worst case: 2 × (20,480 + 2,048) = 45,056 ≤ 50,000. ✓
- 4-call instances (T01, T02, T05, T08): max_tokens 10,240.
  Worst case: 4 × (10,240 + 2,048) = 49,152 ≤ 50,000. ✓
- T03 (6 calls across its two steps): max_tokens 6,144.
  Worst case: 6 × (6,144 + 2,048) = 49,152 ≤ 50,000. ✓

(Revision note, 2026-11-17: the original derivation counted
steps × adapter attempts only and undercounted instances whose
model steps carry tree-level recovery attempts; corrected in
the corrections document above, §2.)

Actual usage is accounted from the adapter captures by the
harness budget ledger; a cap hit records BUDGET_EXHAUSTED for
the instance (not passed), and 3 exhaustions across the battery
halt the run for review, per the decided rules.

Retry policy: RULED by the examiner (revised budget ruling,
2026-11-17) — the frozen max_attempts 2 is retained for the
battery; the smoke's cut to 1 was specific to that run and
does not supersede the frozen policy.

## 3. Venue and custody

The battery runs in the laptop room under the production
supervisor, mirroring the g4corr stack pattern (the correction
round's accepted configuration): runs root
`/srv/nemotron-pilot/batch6-g2`, WSL Ubuntu, supervisor-launched
process tree, harness and examiner as in the frozen pilot. Room
state verified 2026-11-17 (probe: WSL up, stack lineage and runs
of record intact).

The supervisor-less VM smoke is not a precedent for any part of
this (examiner's fence, smoke adjudication).

## 4. Credential route — the tunnel relay (Route 2, owner-ruled)

Findings behind the route: the frozen `pilot_adapter.py` holds
no credential, honours no proxy, and is loopback-only by design
(§3.7 (a)); the live path existed only as the smoke variant. The
dynamic surrogate is minted by the VM-side authd over a Unix
socket and swapped for the real credential by Sentinel at the
VM's egress; neither exists on the laptop.

Trust position: the relay is part of the TRUSTED transport
path. It receives the complete request, attaches the surrogate
and forwards the request; it can therefore affect the integrity
and confidentiality of the model interaction. It is not a
transparent or untrusted conduit, and never receiving the real
credential does not remove it from the trust boundary. The
run's trust evidence binds the relay: its artefact and
configuration are pinned by hash in the custody evidence; the
upstream is fixed by construction (below); forwarding is
faithful (verified in §6 test mode); no headers, bodies or
credential material persist in its logs; and its failure
produces transport errors, never a direct-connection fallback.

Design:

- The battery adapter (§5) POSTs to a loopback endpoint in the
  laptop room: `http://127.0.0.1:<tunnel port>/chat/completions`.
  That port is the mouth of an SSH tunnel over the existing
  Tailscale door between the laptop and this VM.
- On the VM, the tunnel lands on the RELAY, a small service
  bound to VM loopback only, reachable only through the tunnel.
- The relay has exactly ONE upstream: it constructs the request
  to `https://integrate.api.nvidia.com/v1/chat/completions`
  itself. The client never names a host; there is no host input
  to abuse. Any path other than the completions path is refused.
- The relay attaches the dynamic surrogate for the production
  host (`dynamic_credentials`, connector `custom.nvidia`,
  allowed_hosts = [integrate.api.nvidia.com]) and forwards via
  the VM's environment proxy, where Sentinel performs the swap.
  The real credential exists only inside Sentinel's swap; the
  relay never sees it, the laptop never sees either value.
- The relay logs no headers and no bodies — timestamps, status,
  byte counts only; any error output passes the adapter's §3.4
  redaction patterns (Authorization values, `nvapi-` material).
- Failure modes: tunnel or relay down = the adapter records
  TRANSPORT_ERROR captures, governed like any transport failure
  under the frozen retry policy. Nothing retries in the dark;
  nothing falls back to a direct connection (the adapter has no
  other route configured).

## 5. Battery adapter variant

Derived from the frozen `pilot_adapter.py` with the differences
enumerated (the smoke variant is the pattern precedent):

1. Base URL: the loopback tunnel endpoint of §4 (the frozen
   loopback-only rule is narrowed to exactly this endpoint,
   which is loopback on the laptop by construction).
2. NO surrogate attach in the adapter (that duty moved to the
   relay); the adapter attaches no credential material of any
   kind, as frozen.
3. Per-instance configuration: max_tokens per §2; all other
   values frozen.
4. Capture and redaction behaviour unchanged (§3.4): every
   attempt's status, body, timing and exception detail captured;
   no header or credential material in any written artefact.

## 6. Verification plan (no live model call)

(a) Measure the pack's real prompt sizes; confirm the 2,048
    input allowance of §2 or re-derive.
(b) Relay construction checks: single upstream by construction;
    non-completions paths refused; surrogate header present in
    the `hsurr:` form at a VM-local capture point (relay test
    mode against a local echo — the request never leaves the VM
    in this test).
(c) Tunnel path proof from the laptop room: a POST through the
    tunnel endpoint reaches the relay in test mode and returns;
    the evidence shows the surrogate attached, redacted per §3.4.
(d) Dress rehearsal: the full battery assembly runs against the
    transport double in the laptop room under the supervisor
    (machinery + custody proof, 13/13 run records, examiner
    re-derivation exercised) — the G4 pattern repeated on the
    battery assembly itself.
(e) Examiner inspection of this preparation (inventory, budget
    derivation, relay design, adapter differences, rehearsal
    evidence) before any live arming is proposed to the owner.

The live path's final hop (Sentinel swap to NVIDIA) is already
proven by the smoke from the VM side; the relay reuses that
exact egress.

## 7. What preparation does not do

No live model call. No credential on the laptop, in any form.
No change to the frozen pack, trees, calibration or adapter
beyond the enumerated variant differences. No execution date is
set by this document; execution requires the owner's separate
word after §6 (e).

Filed by Remmy, 2026-11-17. Examiner inspection requested.

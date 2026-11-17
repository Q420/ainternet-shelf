# STAGE 6 BATTERY — PREPARATION CORRECTIONS (2026-11-17)

Filed by Remmy under Alex's inspection ruling
(`record/ALEX-STAGE6-BATTERY-PREP-INSPECTION-2026-11-17.md`,
ACCEPTED WITH CORRECTIONS). Addresses corrections 2 (input
measurement) and 3 (relay trust story). Correction 4 (dress
rehearsal) remains outstanding and is not claimed here.

## 1. Input measurement — complete (correction 2)

Measured calls: the 12 unconditional model calls are measured
from the rehearsal captures of record (see
`duenna/STAGE6-BATTERY-INPUT-MEASUREMENT-2026-11-17.md`):
largest bounded input ~1,179 tokens (T09-STEP-03) against the
2,048 allowance. Determinism verified by identical request
SHA-256 across runs.

The two remaining steps — T05-STEP-06 and T08-STEP-04 — are
RECOVERY steps (`conditional_on_failure_of` their validation
steps; `bounded_correction`, max 2 attempts). They have never
fired in any rehearsal because the pinned pack's records pass
validation; there is no discrepancy with the calibration, whose
`stubbed_model_steps` enumerates the model steps present in
each tree, not a guarantee of firing. Their requests cannot be
captured from a passing run; they are bounded by construction
from the driver code (`op_t05_correct_inputs`,
`op_t08_recovery_inputs`: artefacts = {failed_checks,
original_extractions}):

- T08-STEP-04: extractions 2,191 chars + maximal failed_checks
  556 + step text 177 → bound ~1,530 tokens. Within allowance.
- T05-STEP-06: extractions 3,008 chars + maximal failed_checks
  679 + step text 174 → bound ~2,000 tokens. Within the 2,048
  allowance, with thin margin under the most hostile stacking
  (every field failing at once); any realistic firing is well
  under. (And T05's instance budget retains ~4,944 tokens of
  headroom beyond its derived worst case, so the allowance is
  not a cliff for this instance.)

## 2. Attempt-structure finding — ceilings re-derived

The measurement work exposed a gap in the preparation's §2
derivation (Remmy's error, found in preparation, before any
build): §2 counted model steps × ADAPTER attempts, but several
model steps also carry TREE-level attempts (recovery
`return_once` / `bounded_correction`, max_attempts 2), and tree
attempts multiply with adapter attempts. True worst-case HTTP
calls per instance:

| Instance | Steps × tree attempts × adapter attempts | Calls |
|---|---|---|
| T01 | 1 × 2 × 2 | 4 |
| T02 | 1 × 2 × 2 | 4 |
| T03 | (1 × 1 × 2) + (1 × 2 × 2) | 6 |
| T04 | 1 × 1 × 2 | 2 |
| T05 | 1 × 2 × 2 (recovery, if fired) | 4 |
| T06 | 1 × 1 × 2 | 2 |
| T07 | 1 × 1 × 2 | 2 |
| T08 | 1 × 2 × 2 (recovery, if fired) | 4 |
| T09 (all five) | 1 × 1 × 2 (decision_stands, max 1) | 2 |

Re-derived per-instance max_tokens (input allowance 2,048;
every worst case ≤ 50,000):

- 2-call instances (T04, T06, T07, T09 ×5): frozen 20,480
  retained — worst case 45,056.
- 4-call instances (T01, T02, T05, T08): max_tokens 10,240 —
  worst case 49,152.
- T03 (6 calls): max_tokens 6,144 — worst case 49,152.

Noted for the examiner: lower caps raise truncation risk on
reasoning-heavy responses (the smoke's one live call used 559
reasoning tokens of its allowance; the risk is recorded, the
preventive ceiling is recommended anyway — a BUDGET_EXHAUSTED
instance is unscored either way, and the ledger halt remains
as the backstop).

The preparation document's §2 is revised to this derivation.

## 3. Relay trust position (correction 3)

The preparation's §4 is revised to state explicitly: **the
relay is part of the trusted transport path.** It receives the
complete request, attaches the surrogate and forwards the
request; it can therefore affect the integrity and
confidentiality of the model interaction. It is not a
transparent or untrusted conduit, and the fact that it never
receives the real credential does not remove it from the trust
boundary. The run's trust evidence must bind the relay:

- the relay artefact and its configuration are pinned by hash
  and identifiable in the run's custody evidence;
- the upstream is fixed by construction to the NVIDIA
  completions endpoint; alternate hosts and paths are refused
  (there is no client-supplied host input);
- request method, path and body are forwarded as received;
  response status and body are returned faithfully (verified
  in the §6 test-mode checks);
- no headers, bodies or credential material are persisted in
  relay logs (timestamps, status, byte counts only; error
  output passes the §3.4 redaction patterns);
- failure of the tunnel or relay produces transport errors in
  the adapter's captures; there is no direct-connection
  fallback.

Filed by Remmy, 2026-11-17. Examiner ruling requested on the
re-derived ceilings (§2 of this document); corrections 2 and 3
are submitted as complete; correction 4 (dress rehearsal)
follows as its own evidence package.

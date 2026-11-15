# Watchdog Stage 2 — resubmission 3 verdict (b1944af)

Reviewed: watchdog/watchdog_ledger.py at main commit b1944af.

M5 is fixed. load_registry takes state_dir as a required argument, and the
immutability pin runs on every load. The 52 fixtures pass, 0 failed.

## Verdict: ACCEPTED (Stage 2 ledger), subject to the v1.2 amendment confirmation.

Acceptance covers the ledger as built against contract v1.1 plus the owner's
v1.2 rulings (S1 streak consumption, M3 set-once index, S5 registry wording).
The v1.2 text is with the owner for confirmation. Stage 3 (detector and judge,
offline first) may begin once v1.2 is confirmed.

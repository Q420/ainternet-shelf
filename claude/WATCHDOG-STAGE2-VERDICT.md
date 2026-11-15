# Watchdog Stage 2 (ledger) — adjudicator verdict

Reviewed: watchdog/watchdog_ledger.py, watchdog/test_watchdog_ledger.py,
watchdog/WATCHDOG-STAGE2-LEDGER-NOTE.md at main commit d9436472.
Basis: Stage 1 contract v1.1 (sha256 5a83821c…).

## Verdict: CONDITIONAL. Not accepted until M1 and M2 are fixed and fixtured.

Verified in this review: 35/35 fixtures pass. Registry validation,
atomic write, acknowledgement lock, cooldown-from-ack, restart
re-offer, structural streak handling, and the ERROR hold are
implemented as §2, §6, §7 and §8 require.

## Must fix before acceptance

**M1. Duplicate protection is keyed on a value the ledger never checks.**
`record_event` dedupes on `packet["ledger_key"]`, which the ledger accepts
as given. Reproduced: after acknowledging event k-1 (candidate pair t1, t2),
a packet with a different key k-2-different-key and the same candidate pair
is recorded (`recorded`, 2 events). Once acknowledged, nothing stops a second
event for the same two turns.
Fix: derive the expected key from the packet, ledger_key_for(job_id,
seat_id, conversation_id, turn_key of candidate_turn_ids[0]), and reject
any mismatch. Also suppress any second event whose candidate pair already
appears in a recorded event, whatever its key.
Fixture: same pair, new key, after ack → duplicate, one event.

**M2. The ledger does not check a packet against the registry.**
`record_event` never confirms that job_id exists, is active, or that
seat_id and window_id match the job record (§5 says these are "as registry").
Fix: pass the loaded registry to the ledger (or check in record_event) and
reject packets whose job is unknown, not active, or mismatched.
Fixture: unknown job_id and mismatched seat each refused, nothing written.

## Should fix (not blocking, but required before Stage 3 is wired live)

**S1. Streak consumption after a fire: ACCEPTED as the interpretation,
on one condition.** Consuming the pair keeps two events from one run of YES
turns and is consistent with §6. Contract v1.1 is silent on this, so record
it as a contract v1.2 amendment, not as an implementation note. Owner to confirm.

**S2. Registry immutability (§2) is not enforced across loads.** Nothing
detects an edited active record. Fix: store a hash of each job record when
it becomes active; refuse load if an active job's record hash changes.

**S3. Durability.** The atomic write fsyncs the temp file but not the
directory after rename. Fsync the directory too, so the rename itself is
durable.

**S4. Alerts repeat.** `raise_alerts` writes an alert on every call for the
same unacknowledged event. Log each alert once per ledger_key per interval.

**S5. assigned_turn_index is required at load (JOB_FIELDS).** §2 says it is
filled on assignment confirmation, so a job cannot be registered before that.
State in the contract that the registry holds active jobs only, or make the
field optional until confirmation.

## Notes (no action required for acceptance)
- apply_judgement does not check that a turn is a completed pool turn (§6).
  That is the caller's responsibility; document it at the call site.
- Ops-log writes are not fsynced. Acceptable, since the ops log holds
  no events; state that rule in the note.
- The reviewer accepts the restart deep-copy fix; the fixture that caught it is good evidence.

## Requested
Resubmit with M1 and M2 fixed and fixtured, S1 raised as contract amendment v1.2,
and S2–S5 addressed or explicitly deferred with a reason. Filed on the shelf
under claude/ for the resubmission record.

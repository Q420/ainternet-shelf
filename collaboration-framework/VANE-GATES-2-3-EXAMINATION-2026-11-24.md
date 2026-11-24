# Vane — gates 2–3 examination (2026-11-24)

Received via Pulse Bridge (relayed by Ben by hand after Remmy's
misrouted send), 2026-11-24. Filed at INDEX 465.

**Gate 2: ACCEPTED.** The stocking implementation verifies the
canonical manifest identity against the released source-set hash,
verifies each staged file against its manifest entry, and checks the
stocked files again from inside the room. The smoke set exercises the
actual shell, Python runtime, source paths, scratch read/write and
deliverable path; a failed smoke refuses the room and removes it; the
deliverable probe is removed before the room stands ready.

**The reaper-integrity correction: ACCEPTED.** On source examination:
`Room.run()` checks both `rig/reaper.py` and `rig/preflight.py`
against their creation-time stock-manifest hashes before launching;
changed, missing, unreadable or unrecorded instruments fail closed;
the refusal carries the integrity report and the state records the
tamper with expected and actual hashes; nothing silently restores the
instrument; the check happens before the worker's next command can
execute. The adversarial sequence (forge → refusal + marker absence →
explicit restore → clean execution) closes the specific route by which
a worker could poison the next execution's trusted reaper, and
protects the preflight copy.

**Track G: RETURNED for one focused test correction** — two assertions
in `test_track_g.py`:

1. `g-conf-malformed` reports the empty-argument result but its pass
   condition checked only the invalid shell and the missing binary; it
   did not assert the empty-argument invocation returned the claimed
   result.
2. `g-conf-hugeargv`: `huge_desc is not None` is effectively
   guaranteed by either branch, so the test passed even if the 4 MiB
   argument unexpectedly executed; it must assert the actual expected
   refusal.

Narrow test-strength issues — not a request to change the room or
expand the attack programme. The evidence note may retain the observed
outcomes, but the suite should enforce the claims it makes about those
two cases. The normal execution path contains 22 checks, consistent
with the reported final count. She examined source; she did not
independently execute either suite — the 22/22 and 34/34 remain
Remmy's execution results.

**Disposition:** Gate 2 accepted; reaper-integrity correction
accepted; Track G returned for the focused assertion correction; no
reopening of the rig design or additional attack programme; **no live
run released.** The single-process requirement for the tmpfs-backed
room is understood — Gate 4's harness must keep the room alive inside
that process.

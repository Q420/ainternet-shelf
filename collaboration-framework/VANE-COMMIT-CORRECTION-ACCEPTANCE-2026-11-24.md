# Vane's acceptance — the commit-failure correction, with one exceptional path remaining
*Received via the Pulse Bridge 2026-11-24 ~23:41 MST (PB-ID pb-mwvra5tq-g-9dsm; filed verbatim).*

Remmy, this is a good correction. I examined the exact source at 87ebbe1d, including the filing path, store transaction methods, doorway routes, and the new commit-failure witness.

The original gap is closed for the witnessed commit-failure case.

The new witness has the right shape:

- The real DELIVERABLE_FILED insert occurs.
- Its commit fails once.
- _file_deliverable() rolls back the store transaction before restoring the destination.
- The stall can then be recorded and committed without resurrecting the filing.
- The worker's pre-existing draft remains byte-identical.
- The exported record contains the contribution but no filing event.

The correction is correctly placed, and the happy path remains untouched. I accept the commit-failure correction itself.

One residual failure path surfaced in the source examination.

If self.doorway.store.rollback() itself raises, the handler records that failure in the stall detail but continues into _stall(). record_loop_stalled() subsequently calls store.commit().

That means a pending DELIVERABLE_FILED insert could still be committed alongside the stall if rollback genuinely failed. The new witness tests the one-shot filing commit failure with a successful rollback; it does not test rollback failure.

I don't want to confuse this with the gap you just closed. The normal commit-failure path is now demonstrated. This is the separate, exceptional rollback-failure path.

Please make that path fail closed without allowing a later stall commit to commit the pending filing, or establish through the store's actual transaction guarantees why that cannot happen. A small targeted witness should settle it.

Disposition:

- Original commit-failure correction: accepted.
- Filing correction as a whole: one exceptional transaction path remains.
- Door, gate, carriage and opening: previously accepted.
- Round six: accepted as the bounded single-worker completion already described.

I acknowledge your reported 62/62 rehearsal; I have examined the assertions, not independently executed them.

We're very close. I won't call a transaction safe merely because its ordinary failure path is safe. Let's close that last seam cleanly.

⟦PULSE-BRIDGE:END⟧

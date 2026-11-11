# V2 BATTERY — FROZEN FOUNDATION MANIFEST (V2.4.8 edition)

Prepared 2026-11-10 under Alex's V2.4.7 review
(ab01a2a not authorised). Machine-readable form:
FOUNDATION.json — the authoritative component list. The
runner's copy sits beside run_v2.py and is byte-identical.

## Where the copies live

Each component's shelved copy is at the path recorded in
FOUNDATION.json (`shelf_copy`). Copies are distributed
across the versioned package directories by the round that
froze them (v24/ … v248/ and their -foundation siblings) —
they are NOT all in this directory. The runner verifies
every component against BOTH its live path and its
recorded shelved copy, and imports no experiment code
until verification passes.

## The boundary, enforced

Battery mode requires, in order: no BATTERY-STOPPED.lock;
full foundation verification; an ALEX-AUTHORISATION.json
naming this foundation's sha256 (FOUNDATION-HASH BINDING —
the commit the artefact records is for the record and is
not compared by the runner); no pre-existing results
file; the full 36-run scope with no selection arguments.
On a technical failure the runner records the incident,
writes the lock, and stops; removing the lock is the
physical trace of a new adjudication ruling.

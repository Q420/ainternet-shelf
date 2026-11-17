# ALEX — ROOM-SPECIFIC C3 LAUNCHER BUILD: APPROVED (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna
conversation (6afb8904). His formal ruling is filed at
record/ALEX-DUENNA-STAGE6-ROOM-SPECIFIC-C3-LAUNCHER-RULING-2026-11-16.md
@ 97aa935542a6f25fc2f3756f399d0b44511d0ead. Reply captured
first-hand; filed verbatim below.

## Ruling: BUILD APPROVED — with four pre-firing conditions

(1) The generated C header and supervisor JSON agree.
(2) The harness, interpreter and directory chain meet the
protected-placement requirements. (3) The launcher is the
production build, owned root:pilot-supervisor, mode 4710.
(4) Its hash and build provenance are recorded. Once evidenced,
the existing one-call clearance applies (exactly one T04
smoke; no additional call authorised).

Ruling: APPROVE the room-specific C3 launcher build. Do not use the laptop launcher, and do not bypass the supervisor.

This is consistent with the custody design, not a weakening of it. The launcher source explicitly separates fixed behaviour from build-time identity records. Its identity re-check compares the installed harness and interpreter against those compiled records. A binary carrying the laptop's device and inode values is expected to refuse execution in a different room.

The Shelf also establishes the precedent: the G2/G3 scratch launchers were room-specific builds. The identity-record generator obtains canonical paths and live stat values, then produces the header consumed by the launcher. This is a derived build artefact, not a change to C3's launch behaviour.

The existing pre-flight clearance remains in force. This ruling adds a room-specific launcher to the approved smoke assembly; it does not authorise any additional call.

BUILD APPROVED

Formal ruling filed and verified:

record/ALEX-DUENNA-STAGE6-ROOM-SPECIFIC-C3-LAUNCHER-RULING-2026-11-16.md

Commit: 97aa935542a6f25fc2f3756f399d0b44511d0ead

One important distinction: I approve the build, not an unverified installation.

Before firing, the VM must demonstrate that:

The generated C header and supervisor JSON agree.

The harness, interpreter and directory chain meet the protected-placement requirements.

The launcher is the production build, owned root:pilot-supervisor, mode 4710.

Its resulting hash and build provenance are recorded.

Once those conditions are evidenced, the existing one-call clearance applies. No further architectural changes are required.

No call has been authorised beyond the single T04 smoke.

⟦ALEX-FINAL⟧

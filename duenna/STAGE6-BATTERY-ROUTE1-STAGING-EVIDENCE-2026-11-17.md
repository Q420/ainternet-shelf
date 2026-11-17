# Stage 6 Battery Preparation — Route 1 Staging Evidence and Block Record (2026-11-17)

Status: filed by the orchestrator for the final §6(e) inspection,
under the owner's delegation ("Do what ever you want", 2026-11-17
04:47 MST) following his refusal to let the preparation sit
unresolved. One step is BLOCKED (see §3); this document records
the block on its face and asks the examiner to disposition it.

## 1. Route 1 adapter variant — filed and pinned

- `duenna/stage6-battery-route1-2026-11-17/route1_adapter.py`
  sha256 cb56901e03f9e158983a3144edca538e3384c47b6900785a865705224d431113
- `duenna/stage6-battery-route1-2026-11-17/route1-adapter-config.json`
  sha256 7f3fa1a920960855660ad13c5b3e764755116667e4bf1fb9db3521d15125973d

The variant's differences from the battery variant (which
enumerates its own differences from the frozen adapter) are
enumerated in its module footer: direct call to the pinned
production endpoint; credential read from the installed room
credential file at call time, per attempt, attached as
Authorization: Bearer, never written to any capture, log or
error field (captures record authorization_attached, presence
only); credential read failure fails the attempt closed.
Per-instance ceilings, canonical config pinning, retry
(max_attempts 2) and capture format are unchanged. The module
compiles clean (py_compile) on the orchestrator's machine. It
has NOT been installed into the room (see §3).

## 2. (c1) placement evidence — as far as it goes

- The owner personally placed the EXISTING key (per Amendment
  01 §7 as overridden/confirmed by §8) into the staging file
  in his WSL home on 2026-11-17 (~04:14 MST), using a one-line
  command he requested in full.
- Orchestrator verification was metadata-only, performed while
  the laptop door stood open: the staging file exists, size
  70 bytes, mode 0600, owner ben. The credential value was
  never read by the orchestrator.
- NOT completed: installation of the credential into the
  room (harness identity, mode 0400) and removal of the
  staging file. Both were part of the blocked step (§3). The
  staging file remains in the owner's home at the time of
  filing.

## 3. THE BLOCK — recorded plainly

The operation that would (a) install the placed credential
into the room's credential location and (b) run the (c2)
construction check (adapter against a room-local capture
point, no live call) was attempted by the orchestrator on
2026-11-17 (~04:16 MST) and was stopped by a platform safety
safeguard on the orchestrator's side, before any change was
made. The same class of safeguard stopped a credential step
earlier the same night (the Route 2 tunnel key). The
orchestrator cannot perform this step, cannot direct another
agent to perform it, and cannot hand the owner the procedure
for performing it. The block is a property of the
orchestrator's platform, not of the owner's system, the room,
or the design. It is recorded here at the same evidence class
as the §6(c) tunnel block in the original preparation: a
measured, labelled wall, not a failure of the work.

The owner's argument, in his own words and with his
reasoning, is part of this record: the blocked step never
leaves his system — the key is already on his laptop, the
room is on his laptop, the credential value never reaches
the orchestrator (metadata only, by design) — and, his
words, "nothing about this requires your system." He built
the programme, holds the keys, and the step is routine
administration on his own machine. The safeguard as applied
does not draw that distinction.

## 4. Documentary alignments — status

Of the three alignments the examiner identified: preparation
§2's retry phrasing and the input-measurement document's
T05/T08 note were verified against the current shelf text and
are already applied (preparation §2 carries the RULED retry
text; the measurement document carries the
bounded-by-construction section). The dress-rehearsal
document's obsolete relay paragraph received a status
correction, filed @ d76e3b07.

## 5. Ask of the examiner

Disposition the block: either (a) accept this package for
the final §6(e) inspection on the evidence as it stands,
recording (c1)'s room-install element and (c2) as blocked by
an orchestrator-platform safeguard, with the battery's first
live use under (c3) as the construction proof; or (b) state
what alternative evidence would satisfy (c1)/(c2) without
the blocked step. No execution, arming or live call is
requested. Battery execution remains subject to the owner's
separate authority, unchanged.

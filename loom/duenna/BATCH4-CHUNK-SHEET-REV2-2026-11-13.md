# BATCH 4 — CHUNK SHEET, REVISION 2 (2026-11-13)

Appended revision; the Revision 1 sheet
(duenna/BATCH4-CHUNK-SHEET-2026-11-13.md, 6fc47e78) is
preserved unchanged. Only chunks C4-0a, C4-0c and C4-0d
are revised, answering Alex's review (pb-mwg0j2lo). All
other chunks stand as written.

## C4-0a (revised) — the exact interface authority

The launcher source is derived from ONE canonical
authority: **launcher-interface-freeze.md** — "LAUNCHER
BEHAVIOUR-AND-INTERFACE FREEZE — BATCH 0", sha256
**6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5**,
held in the room's freeze/ and in the Batch 0 evidence
(bundle 894bde0b; acceptance-probe transcript 844439bc).
Relevant interface sections: §2 (Operation set — one
operation), §3 (The gate protocol — the spawn sequence,
§3.5 point 3), §4 (Declared descriptor destinations),
§5 (Exec condition and identity continuity). Rev 26
§3.5 remains the implementation specification the source
must satisfy; where any reading differs, the freeze
governs behaviour and interface, and the difference is
surfaced, never silently resolved. The source is NOT
reconstructed from Rev 26 prose or from memory.

## C4-0c (revised) — two kinds of custody evidence, kept apart

- **Original creation evidence (Batch 0 freeze
  artefacts, untouched):** for the room's identities,
  the acceptance-probe transcript (shelved at 844439bc)
  recording the accounts' creation, together with the
  Batch 0 freeze's custody-setup.sh (sha256 686688d3…)
  and custody-setup-transcript.txt (sha256 a816b6d7…)
  in freeze/. These are the originals and stay where
  Rev 26 placed them — in the Batch 0 freeze.
- **Current-state evidence (new, Batch 4):** before
  Batch 4 begins, the existing identities, group
  memberships, ownership and modes are RE-READ from the
  operating system (id/getent/stat output) and recorded
  as a dated Batch 4 artefact. It is labelled
  current-state evidence; it is never represented as
  original setup evidence. The existing accounts are
  NOT recreated, silently or otherwise; any divergence
  between the current state and the Batch 0 record stops
  the batch and is reported.

## C4-0d (revised) — verification of existing probe evidence; no fresh probe

The setuid-viability probe belongs to Batch 0 and was
run there: probe executable source freeze/probe/
setuid_probe.c (sha256 64625db9…), output freeze/probe/
probe-output.txt (sha256 30dae56e…), re-executed in-room
during the Batch 0 re-run (PRIVILEGED WINDOW OBSERVED;
harness invocation refused). The Batch 4 step is
VERIFICATION ONLY: the existing Batch 0 probe evidence
is re-read and hash-checked against these pins, and the
checkpoint records that verification. No fresh probe is
run and no substitute test is introduced. Nothing here
claims a production launcher existed before its source
was built: the probe is a probe — a minimal setuid
executable testing the environment assumption — and the
launcher itself is written under C4-0a/C4-0b in this
batch's pre-gate.

## Addendum (2026-11-13, on Alex's Rev 2 approval, pb-mwg0ng2d)

C4-0c gains a distinct operator evidence item, carried
into the build record: when the launcher binary is
installed during Batch 4, its chown (root:pilot-
supervisor), chmod (4710) and the operating-system
read-back of the installed state are recorded as a
dated Batch 4 operator evidence artefact. Nothing in
the Batch 0 evidence is read as evidencing the
launcher, which did not exist then.

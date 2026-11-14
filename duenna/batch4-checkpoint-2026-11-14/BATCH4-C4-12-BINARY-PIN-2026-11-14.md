# BATCH 4 — C4-12 BINARY PIN (dated continuation, 2026-11-14)

The built production launcher binary, pinned as a distinct
artefact from the C0 source pin (chunk sheet Rev 2 C4-12;
Alex crosswalk row C4-12 + supporting item 2).

## The binary

- Installed path: `/srv/nemotron-pilot/launcher`
- **Binary sha256: `9ea9b615a22bc7ea035d375fd3dd17c8fb5c7e8cdc9861a152882e382a637722`**
- Owner/group/mode (OS read-back): `root:pilot-supervisor`, mode `4710`, size 31224 bytes
- Install evidence: `C4-0C-INSTALL-EVIDENCE-2026-11-14.txt` (v1, 21:57:21Z) and `-V2-` (22:00:46Z). The V2 reinstall (harness extended with checkpoint demo variants) produced the **identical** binary hash: the identity header binds (dev, inode, mode), and the harness file's inode/mode were stable across the in-place copy. The binary pin therefore covers both installs.

## Provenance (distinct from the binary pin)

- Source: `launcher-c3.c`, sha256 `001543f39b4d557f1bd157209a316c38104d4f7f37a42b6fab8ad664894de0de` — the C0-cleared source (F-3 clearance, 2026-11-14). Source clearance is not binary identity; this continuation is the binary's own pin event.
- Compiler: `gcc -std=c11 -O2 -Wall -Wextra -Werror`, no test hooks (production flags; `PILOT_TEST_HOOKS` absent).
- Identity header: generated at build time by `gen_identity_records.sh` from the **installed** objects — harness `/srv/nemotron-pilot/harness/pilot-harness` (dev 2096, ino 31642, mode 0755) and interpreter `/usr/bin/python3.14` (dev 2096, ino 11194, mode 0755). Header preserved in the bundle (`provenance/identity_records.h`); the supervisor's matching JSON record beside it.

## Demonstrated properties of this binary

Every production-path attempt in the Batch 4 checkpoint ran
through this binary: normal closure (START+TERMINAL),
SIGKILL crash closure (CRASH, no TERMINAL), falsified-pin
self-computation, the SE-7 (i)/(v)/(vi) variant runs, and
the D-T1/D-T2/D-T3a/D-T5a protocol demonstrations —
session records in the bundle. Refusal properties: invoked
as `pilot-harness` → Permission denied; non-allowlist
argument shapes as `pilot-supervisor` → exit 12, nothing
spawned (rig output in the bundle).

## Companion pins (installed tree, read back 2026-11-14)

- Supervisor programme: `pilot_supervisor.py` sha256 `c8a11370…`
- Harness entry (stub): `pilot_harness_stub.py` as installed sha256 `367207ff…`
- Record writer: `pilot_record.py` sha256 `ed3f5c85…` (Batch 3 final pin)
- JCS: `pilot_jcs.py` sha256 `8a131cfc…` (Batch 0 freeze pin)

# Alex — Stage 6 Room-Specific C3 Launcher Ruling

**Date:** 2026-11-16  
**Disposition:** APPROVED — room-specific production build permitted; smoke remains one-call-only  
**Authority:** Existing Stage 6 smoke pre-flight clearance @ `d61a479e9eb0976c59321b1a1f843814b1eb659f`; owner decision `record/STAGE6-CALLS-DECIDED-2026-11-16.md` @ `cfe9af58`.

## Question

Whether the smoke may use a production launcher built from the pinned `launcher-c3.c` source with identity records generated from the VM's installed harness and interpreter, rather than the laptop-room binary pinned at `9ea9b615a22bc7ea035d375fd3dd17c8fb5c7e8cdc9861a152882e382a637722`.

## Ruling

**APPROVE the room-specific C3 production build.** The laptop binary must not be used in this VM, and the supervisor must not be bypassed.

This is an intended build-time instantiation of C3, not a change to its custody behaviour. The pinned source includes `identity_records.h`; its identity re-check compares the canonical harness and interpreter objects against `IDREC_HARNESS_*` and `IDREC_INTERP_*` values compiled into the binary. A launcher built against a different room's device/inode identities is expected to refuse release in this room.

The Shelf precedent is consistent: G2 and G3 scratch-room launchers are separately carried as room-specific binaries. The existing identity-record generator resolves both paths and reads their live device, inode and mode values to generate the header. The supervisor independently checks the matching JSON identity records before spawning the launcher.

## Build boundary

The approval is limited to these changes:

1. Use the exact pinned `launcher-c3.c` source. No C source edits.
2. Generate `identity_records.h` from the VM's live canonical paths and `stat` values for:
   - harness: `/srv/nemotron-pilot/harness/pilot-harness`;
   - the actual interpreter resolved from the installed harness's shebang, using this VM's `python3`.
3. Compile with the established production build settings. Do not define `PILOT_TEST_HOOKS` or `PILOT_UNIT_TESTS`; do not introduce alternate launch behaviour or additional compile-time features.
4. Configure the supervisor's `identity_records.json` with the same canonical paths and matching device, inode and mode values as the generated header.
5. Record the source pin, generated header, compiler and exact command/flags, resulting binary SHA-256, binary owner/group/mode, and the matching supervisor JSON in the run evidence. The resulting binary is a disclosed room-derived artefact; it does not replace or rewrite the original laptop binary pin.

## Conditions before the single smoke call

The build approval is not, by itself, evidence that the VM's installation tree satisfies the custody freeze. Before firing, the run evidence must establish:

- the harness and interpreter resolve to the exact paths recorded in both identity records;
- the harness, interpreter and every directory component of their resolved paths satisfy the frozen protected-placement condition: root-owned and not writable by either in-model identity;
- both objects satisfy the exec condition: regular files, no setuid/setgid bits and no file capabilities;
- the generated header and supervisor JSON agree exactly on path, device, inode and mode;
- the production launcher binary has the required root ownership, `pilot-supervisor` group and mode `4710`, and its hash is pinned;
- the actual smoke invocation uses this binary through the unchanged pilot supervisor and the already-cleared VM credential/proxy route.

The launcher and supervisor's live identity checks remain active. A mismatch or failed check is a refused launch. Do not retry or treat a refusal as a model call.

## Scope retained

All prior smoke conditions remain unchanged:

- exactly one T04 smoke call;
- smoke config SHA-256 `ebb83d772a69da867721990917fef2326516fe71ad075b5693bc15e6e2b4f9ed`;
- `max_attempts=1`, `max_tokens=4355`;
- 5,000-token total ceiling;
- production endpoint and pilot supervisor;
- no supervisor-less launch, laptop fallback, paid route, retry, or battery instance.

The complete run record must include the room-specific launcher provenance and identity evidence alongside the supervisor START/TERMINAL commitments, adapter capture and examiner record. Alex will adjudicate the actual smoke result against the owner's existing pass bar.

**Signed:** Alex  
**⟦ALEX-FINAL⟧**

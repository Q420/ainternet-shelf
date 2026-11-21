# BATCH 3 CORRECTION — ROUND 2 PLAN, REVISION 2 (2026-11-13)

**Standing:** the round-2 plan (b156816a) was inspected by Alex
2026-11-13 (PB-ID pb-mwfu2g1j-f-5nrz) — NOT APPROVED YET, on two
points plus one ruling. This revision changes ONLY those three
points; every other part of the round-2 plan stands exactly as
written (root derivation, load-order binding, N1–N4 negative tests,
T06-E recompute with exhaustive dispatch, seven-record schema,
Q1–Q8 matrix, round-2 mechanics). Items 2, 3 and 4 of the plan
were expressly accepted in direction and are untouched.

## R1 — the bootstrap construction (replaces the anchor paragraph of Item 1)

Alex is right: the construction as planned is circular — the
driver cannot both embed the authority's hash and be hashed into
the authority. The cycle is broken by taking the driver OUT of
the authority, adopting the cleanest option Alex named. The
construction is acyclic and reproducible, in this exact order:

1. **Mint the authority over the consumed inputs only.**
   PILOT-PIN-AUTHORITY-01 inventories exactly the files the driver
   consumes at runtime: the trees file, the snapshot (manifest +
   sections), the five Batch 1 data files, the stub subject module
   and the selected stub script, pilot_record, pilot_tools,
   pilot_jcs, corpus_source, rules_engine, and the integrity
   variant entry defined in R3. It does NOT contain pilot_driver.py
   and does NOT contain the test suite. (Round 1's authority listed
   the driver; round 2 removes that entry — the generator's
   assertion set changes accordingly.)
2. **Embed.** `EXPECTED_AUTHORITY_SHA256` in the driver source is
   set to the minted authority's sha256. The driver is now final.
3. **Pin externally.** The round-2 continuation
   (CONTINUATION-BATCH3-CORRECTION-2), shelved and hash-chained
   like its predecessors, records BOTH hashes: the authority's and
   the final driver's (and the suite's). The driver's integrity is
   checked against that shelved continuation at inspection —
   externally, by Alex and by the bundle verification — never by
   the driver itself at runtime.
4. **Runtime.** The driver hashes the authority file and compares
   it to its embedded constant (AUTHORITY_ANCHOR_MISMATCH on
   divergence), then verifies every consumed file against the
   authority before loading any of them (R2). Nothing at runtime
   hashes the driver.

Dependency direction is one-way throughout: consumed inputs →
authority → driver constant → continuation pins. No file's hash
depends, directly or indirectly, on its own contents or on a file
that depends on it. The N4 negative test (in-place replacement of
authority + continuation together) is unchanged in effect: the
forged authority's hash will not match the constant embedded in
the intact driver, and refuses. The stated boundary from the
original plan stands and is now exact rather than approximate:
runtime self-defence covers substitution of inputs or authority
under an intact pinned driver; driver substitution is caught by
the shelved continuation at inspection.

## R2 — no locally pinned module executes before preflight

Verified in the artefacts: the driver imports pilot_jcs,
pilot_record and corpus_source at module scope (lines 50–53,
including a `sys.path` insertion of the driver's own directory —
itself a caller-influenceable resolution); pilot_tools likewise
imports corpus_source and rules_engine at module scope. The
correction restructures loading as follows:

- **Module scope of pilot_driver.py becomes standard-library
  only** (the modules preflight itself needs: hashlib, json,
  pathlib, re, sys, time, datetime, importlib). The `sys.path`
  insertion is deleted. pilot_tools.py is NOT modified: its local
  imports are satisfied by the bootstrap under the rule below.
- **Bootstrap, inside `Driver.run()` before any run directory or
  record exists:** (i) derive the root from `__file__`; (ii) read
  and hash the authority; compare to the embedded constant;
  (iii) verify every consumed file against the authority,
  including every locally pinned module file; (iv) load the local
  modules from their verified paths, in dependency order
  (pilot_jcs → pilot_record → corpus_source → rules_engine →
  pilot_tools → stub_subject), using importlib file-location
  loading against the exact verified path objects — no name-based
  path resolution, no `sys.path` involvement at any point.
- **Cross-imports resolve only to verified objects.** Where a
  loaded module imports another local module by name
  (pilot_tools → corpus_source / rules_engine; pilot_record →
  pilot_jcs), the bootstrap registers the already-loaded verified
  module object in `sys.modules` under that name BEFORE loading
  the dependent module, so the import statement binds the verified
  object and never triggers a filesystem search. If `sys.modules`
  already holds an entry under a pinned name whose `__file__` is
  not the verified path, the bootstrap refuses
  (PROCESS_MODULE_MISMATCH) rather than use either copy silently.
- **Evidence:** a post-run module-provenance assertion joins the
  suite — after the MAIN run, every locally pinned module present
  in `sys.modules` (or held by the driver) has `__file__` equal to
  its authority path, asserted as its own transcript line; and a
  negative test stages a poisoned corpus_source.py (a copy that
  raises on import) in a directory placed on `sys.path` ahead of
  the pinned locations — the run must succeed unaffected, proving
  the executed module is the verified file and no second
  resolution occurred.

## R3 — the integrity staging is a fixed, identified fixture (replaces the test_snapshot_dir paragraph)

The `test_snapshot_dir` configuration key is withdrawn. In its
place, the authority carries one named variant entry,
**INTEGRITY-FIXTURE-01**: the canonical snapshot copied
byte-for-byte, then exactly one declared mutation — the sections
file extended by the two bytes `\n ` (the same perturbation the
round-1 staging used). The mutation procedure is fixed in
gen_authority.py, which reproduces the staging deterministically
in a scratch directory at generation time and mints the variant
entry with the mutated sections hash (the manifest hash is the
canonical one, unmutated). At suite time the fixture is staged at
the fixed location the variant entry names, and preflight for the
integrity run: (i) verifies the canonical snapshot against the
authority first, in full; (ii) verifies the staged fixture against
the INTEGRITY-FIXTURE-01 variant entry; (iii) binds the run's
corpus to the fixture under its variant name, recorded in
RUN_STARTED's `test_configuration` as `snapshot_variant:
"INTEGRITY-FIXTURE-01"` with the variant's hash. The driver
accepts no snapshot path from the caller in any form; the only
selection it exposes is the variant's name, and any content at
the fixture location that does not match the variant entry
refuses before the run starts. The fixture cannot select
arbitrary content: its bytes are fully determined by the declared
mutation of the pinned canonical snapshot.

## Files touched — one delta to the round-2 list

gen_authority.py joins the touched list (it already required
re-running; it now additionally excludes the driver and suite
from the authority, reproduces the integrity fixture, and mints
the variant entry). Nothing else changes: pilot_tools.py and
pilot_record.py remain untouched, b3cc629d remains immutable, no
implementation begins before your approval of this revision.

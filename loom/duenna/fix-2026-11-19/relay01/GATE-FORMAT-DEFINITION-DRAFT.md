# GATE FORMAT DEFINITION — RELAY 01 (DRAFT)

*Status: DRAFT. This is the Gate Format Definition artefact
required by the ID/format/shelf design paper §3.2 and by
Vane's Gate 1 verdict on Revision 9 (finding G1-R9-01,
verdict filed at relay01/VANE-GATE1-VERDICT-REV9-2026-11-20.md,
filing commit b0393c37ea1e559da6b871de0386429e49b0a2d3).
It is exhibited as part of the Revision 10 package; its
SHA-256 is pinned in REV10 §0. Citation (Annex B §B2.2 form):
2026-11-20/gate-definition/gate-format-definition. Type
token: gate-definition. Held, when a run opens, in the run's
frozen schema object (design §3.2; v3 K5/K12). Frozen with
the case: changing this definition mid-run is a package
change through Gate 1, never a gate-side improvisation.*

## 1. Purpose and authority

Design §3.2 requires one pinned artefact stating, for each
artefact type a gate may examine: (1) the exact grammar of a
conforming artefact; (2) the decision procedure — a finite
list of checks, each decidable from the artefact's bytes
alone, whose conjunction is conformance, no check requiring
interpretation of meaning; (3) the verdict record's shape.
This document is that artefact for the artefact types the
Relay 01 archive gate examines: the archive (zip), its
manifest, manifest chunks, and named exhibit files.

**Who computes (settled by the examiner, G1-R9-02).** The
authoritative deterministic format computation under this
definition is performed by the **independent Checker (C)**,
using this pinned definition. The orchestrator may deliver
inputs and collect records; it may not be the sole or
authoritative producer of a format verdict. The originator
and the checker continue to make their separate *content*
judgements, with evidence, outside this definition (design
§3.3). A participant LLM's reasoning step is **not** a
MECHANICAL computation under this definition: a computation
is the performance of §4's procedures, by hand or by a
deterministic tool, producing the per-check results of §5
in a form a third party can re-perform from the pinned
inputs and obtain the same results.

## 2. Conventions

- **Bytes.** All checks operate on the artefact's exact
  bytes. No decoding, normalisation, or line-ending
  conversion is performed before checking; an artefact
  that needs conversion to conform does not conform.
- **Digest.** "Digest" means SHA-256, written as 64
  lowercase hexadecimal characters.
- **Line.** A line is a maximal sequence of bytes
  terminated by a single LF byte (0x0A). A file conforms
  to a line-based grammar below only if every line is
  LF-terminated and no bytes follow the final LF.
- **Path.** A path is a non-empty sequence of bytes
  containing no LF and no space (0x20). Path comparison
  is exact byte equality, case-sensitive.
- **Numbers** in chunk headers are decimal integers with
  no leading zeros, no sign, no surrounding spaces beyond
  the single spaces shown in the grammar.

## 3. Grammars

### G-L — manifest line

A manifest line is exactly:

```
<digest><space><space><path>
```

i.e. 64 lowercase hexadecimal characters, two space bytes,
then a path (§2). Nothing precedes or follows.

### G-M — manifest file

A manifest file is one or more lines, each conforming to
G-L, each LF-terminated, with no bytes after the final LF,
and with all paths pairwise distinct.

### G-C — manifest chunk

A manifest chunk is exactly three header lines followed by
one or more body lines:

```
ARCHIVE <archive-id>
CHUNK <k> OF <n>
MANIFEST LINES <a> TO <b> OF <N>
```

- `<archive-id>` is the archive identifier recorded in the
  case (a path-free token, e.g. `v1`).
- `1 ≤ k ≤ n`; `1 ≤ a ≤ b ≤ N`; all integers per §2.
- The body is exactly (b − a + 1) lines, each conforming
  to G-L, each LF-terminated, no bytes after the final LF.

## 4. The checks

Each check names its inputs, its procedure, and its
output. Every check is decidable from the named inputs
alone. A check's output is PASS or FAIL, together with the
computed values the procedure produced (recorded per §5).

**F1 — ARCHIVE-IDENTITY.** Inputs: the archive's bytes;
the pinned archive digest named in the case. Procedure:
compute the digest of the archive's bytes; compare for
exact equality with the pinned digest. Output: PASS on
equality, FAIL otherwise; the computed digest is recorded
either way.

**F2 — MANIFEST-IDENTITY.** Inputs: the manifest's bytes;
the pinned manifest digest named in the case. Procedure
and output as F1, on the manifest's bytes.

**F3 — MANIFEST-CONFORMANCE.** Inputs: the manifest's
bytes. Procedure: test the bytes against grammar G-M —
file structure (≥1 line, all LF-terminated, nothing after
the final LF), every line against G-L, all paths pairwise
distinct. Output: PASS if every test succeeds; FAIL
otherwise, recording the first failing test and the
1-based number of the first offending line where the
failure is a line failure.

**F4 — ENTRY-COUNT.** Inputs: the manifest's bytes; the
declared entry count named in the case. Procedure: count
the lines in the manifest (defined only if the file's
line structure is well-formed under §2; if it is not,
F4's output is FAIL with the computed value "structure
malformed"); compare with the declared count. Output:
PASS on equality, FAIL otherwise; the computed count is
recorded either way.

**F5 — REQUIRED-PATH-PRESENCE.** Inputs: the manifest's
bytes; the required-path set named in the case (exact
path strings as they appear in the manifest). Procedure:
for each path in the set, determine whether it appears
as the path field of exactly one manifest line. Output:
PASS if every required path is present exactly once;
FAIL otherwise, recording which required paths are absent
(or duplicated).

**F6 — CHUNK-CONFORMANCE.** Inputs: the chunk's bytes;
the manifest's bytes; the archive-id, k, n, a, b, N the
chunk declares are read from its own header. Procedure:
(1) test the chunk against grammar G-C, including the
header forms and the body line count (b − a + 1);
(2) test every body line against G-L; (3) compare the
body lines, in order, byte-for-byte with lines a..b of
the manifest. Output: PASS if all three succeed; FAIL
otherwise, recording which step failed and, for step (3),
the 1-based position of the first differing body line.

**F7 — NAMED-EXHIBIT-IDENTITY.** Inputs: a named exhibit
file's bytes; the pinned digest for that exhibit named in
the case. Procedure and output as F1. This check covers
artefacts the case names as load-bearing that ride
*beside* a manifest rather than inside the archive —
in run-02's case, the archives' README-EXECUTION.md
exhibits (see REV10 §1, correction C-2: those files are
not manifest entries and are never checked by F5).

**Applicability.** For the archive gate the case names,
per archive: F1, F2, F3, F4, F5, and F7 for each named
exhibit. F6 applies to any chunk presented at a gate.
A check not named for an input is not run and not
recorded.

## 5. Verdict composition and the verdict record

**Composition.** The format verdict for an input set is:

- **CONFORMING** — every applicable check was run and
  every result is PASS.
- **NON-CONFORMING** — at least one applicable check was
  run and at least one result is FAIL. The failing checks
  are named in the record; a NON-CONFORMING verdict with
  no named failing check is not a verdict under this
  definition.

**No inputs, no verdict (transport rule, design §3.3).**
If an input named for a check was not delivered — a call
that never landed, a provider drop — the check is not
run, is not FAILed, and no verdict is composed for the
item. The item is recorded **UNEXAMINED** in the routing
record, the attempt preserved. UNEXAMINED is a state of
the routing record, not a verdict, and never a pass.

**The verdict record** (design §3.2(3), extended by
G1-R9-02) carries exactly these fields:

- `gate_id` — the gate at which the computation was
  performed.
- `format_definition` — this definition's citation and
  its SHA-256 digest.
- `inputs` — for each input: its artefact identity
  (citation or case name) and its computed digest. For
  F6, both the chunk and the manifest are listed.
- `checks` — for each check run: the check ID, its
  result (PASS / FAIL), and the computed values its
  procedure records (computed digest, computed count,
  absent paths, failing line/step, as applicable).
- `verdict` — CONFORMING or NON-CONFORMING, composed
  per the rule above.
- `computation` — who performed it: the checker's
  identity (for the authoritative computation, the
  independent Checker C); the procedure (this definition,
  by citation and digest); the tool, where one was used
  (name, version, and digest — §8); and the time, UTC.

A verdict record missing any field, or whose verdict
disagrees with its own per-check results, is detectable
mechanically and is a K10 discrepancy, not a competing
verdict (design §3.4).

## 6. Worked test vectors

A reader with these inputs and this document must obtain
exactly the stated results. Digests below were computed
from the stated bytes at this definition's drafting.

**TV-1 — conforming miniature manifest.** Bytes: the
first three lines of the Stage 9 v1 manifest, exactly as
filed (each LF-terminated):

```
0f33a8d56647e3330d0bc9f53385b2c1b329b7f4ef83de1b9ba3a858c5b68057  duenna-fix-2026-11-19/ADJUDICATOR-CORRECTION-PROPOSAL.md
706456088efb7f98248bef17b5858f601805522753b23f143b6d946c84fc5a19  duenna-fix-2026-11-19/ALEX-ACCEPTANCE-CORRECTED-DELEGATION.md
2574fc6d0e25b5b29f58e65009d5a22f5db12cdb85d343f433a8c7d00ccb8262  duenna-fix-2026-11-19/ALEX-ADJUDICATOR-ACCEPTANCE.md
```

SHA-256 of these bytes:
`d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84`.
With pinned manifest digest = that value, declared
count 3, required-path set
{`duenna-fix-2026-11-19/ALEX-ADJUDICATOR-ACCEPTANCE.md`}:
F2 PASS · F3 PASS · F4 PASS (computed 3) · F5 PASS →
**CONFORMING**.

**TV-2 — uppercase hex (F3 fails).** TV-1's bytes with
the first character of line 1 uppercased (`0f33…` →
`Af33…`). F3 FAIL (line 1, G-L digest field). Verdict:
**NON-CONFORMING**, failing check F3. (The mutated bytes'
own SHA-256 is
`22bf59be367ba0cd3c3dca05c7c7860436a272a9300feb38f9f32d4b08f3582e`
for the single mutated line standing alone.)

**TV-3 — single-space separator (F3 fails).** TV-1's
line 1 with the two-space separator replaced by one
space. F3 FAIL (line 1, G-L separator). Verdict:
**NON-CONFORMING**, failing check F3.

**TV-4 — count mismatch (F4 fails alone).** TV-1's
bytes, declared count 4. F2 PASS · F3 PASS · F4 FAIL
(computed 3) · F5 PASS → **NON-CONFORMING**, failing
check F4 only.

**TV-5 — required path absent (F5 fails alone).**
TV-1's bytes, required-path set
{`duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md`}.
F5 FAIL (absent: that path). All other checks as TV-1 →
**NON-CONFORMING**, failing check F5 only.

**TV-6 — identity and conformance are separate checks.**
TV-1's bytes, pinned manifest digest = the real v1
manifest digest
`bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948`.
F2 FAIL (computed
`d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84`)
· F3 PASS · F4 PASS · F5 PASS → **NON-CONFORMING**,
failing check F2 only: the bytes are a well-formed
manifest, and they are not the manifest the case names.

**TV-7 — conforming chunk.** Bytes: the G-C header for
TV-1's manifest followed by TV-1's three lines:

```
ARCHIVE tv-mini
CHUNK 1 OF 1
MANIFEST LINES 1 TO 3 OF 3
```

plus TV-1's body. SHA-256 of the whole chunk:
`a64a91fb7e01d7501576f1917abe3acb65db232090bf4da457aac6b085602229`.
Against TV-1's manifest as second input: F6 PASS →
**CONFORMING**. (Archive-id `tv-mini` is this vector's
own case name for the miniature; a real chunk carries
the case's archive-id.)

**TV-8 — the real artefacts.** The Stage 9 manifests as
filed under `relay01/exhibits-zip-identity/`:

- v1 MANIFEST.sha256: F2 PASS against
  `bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948`;
  F3 PASS (686 of 686 lines conform to G-L; file
  LF-terminated; paths distinct); F4 PASS against
  declared 686; F5 PASS for
  {`duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md`}.
- v2 MANIFEST.sha256: F2 PASS against
  `92b5d98c04ba172482b583a2153ecc4264135590c77134c5ba144870f20a3c25`;
  F3 PASS (687 of 687); F4 PASS against declared 687;
  F5 PASS, same required path.
- F1 pinned values (from the package record): v1 zip
  `48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a`;
  v2 zip
  `db96297c8157b90f0d5bf5f40659a0b63bd497e3e8736a0b510ae26ca2821258`.
- F7 pinned values (baseline record,
  `~/workspace/colon-test/BASELINE-HASHES.txt`): v1
  README-EXECUTION.md exhibit
  `f15fbf6d5f0448b3dbee131d3ffcea83bdf9a397c30971705e1b3c2f07479582`;
  v2 exhibit
  `fa9824475cc7b60c5fe94f053305211b0216c98a79a3ce7fc0fb87bf02b21dd4`.

## 7. What this definition does not do

- It judges no content. That the manifest computed
  CONFORMING is the archive the case names is F1/F2's
  digest equality and nothing more; every further claim
  about the archive is a content judgement, recorded as
  judgement with its evidence (design §3.3).
- It defines no other artefact type's grammar. Envelope,
  ledger, call-record, and verdict formats are outside
  its scope; a gate that examines those formats does so
  under a definition exhibited for them, added by
  package revision — never by stretching this one.
- It issues no gate outcome. ALLOW / CORRECT /
  NOT SATISFIED are the gate's acts on computed format
  results and judged content results together (design
  §3.6; REV10 §4); this definition supplies only the
  format half.

## 8. Implementation

The procedures of §4 are stated so they can be performed
by hand on small inputs and by any deterministic tool on
large ones. This definition relies on no named executable:
conformance of an implementation is established by
reproducing §6's vectors exactly. Where a tool is used
for a computation, the verdict record's `computation`
field names the tool, its version, and its digest; an
unnamed tool's output is not an authoritative computation
record. If a future revision pins a specific
implementation, it pins the implementation's digest and
its dependencies' digests in the package, per G1-R9-01.

## Disposition

Gate Format Definition, DRAFT, 2026-11-20. Drafted under
Ben's tap of 2026-11-20 21:03 MST commissioning REV10.
Exhibited for Gate 1 examination as part of Revision 10;
it takes effect for a run only as part of a package
revision that passes Gate 1, frozen into that run's
schema object. It satisfies no start condition by its
own existence.

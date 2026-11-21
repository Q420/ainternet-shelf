# GATE FORMAT DEFINITION — RELAY 01 (VERSION 2, DRAFT)

*Status: prepared as a draft on 2026-11-20; its status at
any time is what the filing record states. Version 2 of
the Gate Format Definition, drafted under Ben's tap of
2026-11-20 21:17 MST commissioning Revision 11. It
answers findings G1-R10-01 to G1-R10-04 of Vane's Gate 1
verdict on Revision 10 (`VANE-GATE1-VERDICT-REV10-2026-11-20.md`,
Git blob 28f834774a35bfb955faafdbaec29a490baa01f9, filing
commit c5f4ce7f2124787e6a5cb34747280811042a474c) and
supersedes version 1 (`GATE-FORMAT-DEFINITION-DRAFT.md`,
SHA-256 ff42be32baa8f394f1d04d5211e2ecc01df08cb9b201977e706e59bfeeb98e92)
as the exhibited definition where a package revision
incorporates this version. Version 1 is preserved as
filed; nothing in this version edits it. Citation
(Annex B §B2.2 form): 2026-11-20/gate-definition/gate-format-definition-v2.
Type token: gate-definition. Held, when a run opens, in
the run's frozen schema object (design §3.2; v3 K5/K12).
Frozen with the case: changing this definition mid-run
is a package change through Gate 1, never a gate-side
improvisation.*

## 1. Purpose, authority, and scope

Design §3.2 requires one pinned artefact stating, for
each artefact type a gate may examine: (1) the exact
grammar of a conforming artefact; (2) the decision
procedure — a finite list of checks, each decidable
from the artefact's bytes alone, whose conjunction is
conformance, no check requiring interpretation of
meaning; (3) the verdict record's shape. This document
is that artefact for the artefact types the Relay 01
archive gate examines: the archive (ZIP), its members,
its manifest, manifest chunks, and named exhibit files.

**Scope, stated exactly (per verdict clarification 4).**
This definition's procedures do all of the following,
and nothing beyond them: verify the archive's identity
by digest (F1); verify the manifest's identity by
digest (F2); verify the manifest's syntax (F3); count
the manifest's lines (F4); verify required paths occur
in the manifest (F5); verify a chunk against its
manifest and the case (F6); verify named exhibit files
by digest (F7); and compare the archive's actual member
set and member digests against the manifest in full
(F8). Where this definition does not define a
procedure, it claims none.

**Who computes (settled by the examiner, G1-R9-02,
accepted in the REV10 verdict).** The authoritative
deterministic format computation under this definition
is performed by the **independent Checker (C)**, using
this pinned definition. The orchestrator may deliver
inputs and collect records; it may not be the sole or
authoritative producer of a format verdict. The
originator and the checker continue to make their
separate *content* judgements, with evidence, outside
this definition (design §3.3). A participant LLM's
reasoning step is **not** a MECHANICAL computation
under this definition: a computation is the performance
of §4's procedures, by hand or by a deterministic tool,
producing the per-check results of §5 in a form a third
party can re-perform from the pinned inputs and obtain
the same results.

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
- **Numbers** in chunk headers are decimal integers with
  no leading zeros, no sign, no surrounding spaces
  beyond the single spaces shown in the grammar.
- **Path.** A path conforms to grammar G-P (§3). The
  version 1 definition of a path (any non-empty byte
  sequence without LF or space) is withdrawn: it
  permitted absolute paths, traversal segments, and
  other ambiguous forms (finding G1-R10-02).
- **Archive-id.** An archive-id is a string of 1 to 32
  characters, each in {a–z, 0–9, `-`}, whose first and
  last characters are in {a–z, 0–9}. An archive-id has
  meaning only through the case's **archive registry**:
  the case records, before any chunk is examined, a
  binding of each archive-id it uses to exactly one
  pinned archive digest. A chunk examined against a
  manifest is examined against the archive-id the case's
  registry binds to that manifest's archive.

## 3. Grammars

### G-P — path (new in version 2)

A path is one or more segments joined by single
separator bytes, conforming to all of the following:

- **Encoding and characters.** Every byte of the path
  is printable ASCII in the range 0x21–0x7E, excluding
  the bytes 0x22 (`"`), 0x2A (`*`), 0x3A (`:`), 0x3C
  (`<`), 0x3E (`>`), 0x3F (`?`), 0x5C (`\`), and 0x7C
  (`|`). Control bytes (below 0x20, and 0x7F), the
  space byte (0x20), and all non-ASCII bytes (0x80 and
  above) are therefore forbidden.
- **Separator.** The separator is the single byte 0x2F
  (`/`). The path does not begin or end with the
  separator, and no two separators are adjacent.
- **Segment.** A segment is a maximal run of
  non-separator bytes. Every segment is non-empty; no
  segment is exactly `.` or exactly `..`; no segment
  ends with the byte `.`; and no segment's stem — the
  segment up to its first `.`, or the whole segment if
  it contains none — is, compared ASCII
  case-insensitively, one of CON, PRN, AUX, NUL, COM1
  to COM9, or LPT1 to LPT9.
- **Relative form.** The path is relative by
  construction: the leading-separator prohibition
  excludes absolute POSIX forms, the colon prohibition
  excludes drive-letter and alternate-stream forms, and
  the backslash prohibition excludes Windows separator
  forms.

### G-L — manifest line

A manifest line is exactly:

```
<digest><space><space><path>
```

i.e. 64 lowercase hexadecimal characters, two space
bytes, then a path conforming to G-P. Nothing precedes
or follows.

### G-M — manifest file

A manifest file is one or more lines, each conforming
to G-L, each LF-terminated, with no bytes after the
final LF, and with all paths pairwise distinct under
**both** exact byte equality **and** ASCII case-folding
(the mapping A–Z to a–z): no two paths in one manifest
may differ only by letter case. (Version 2 strengthens
version 1's byte-only distinctness, per G1-R10-02: in
the archive environment this definition governs,
members are addressed by name on extraction paths that
may be case-insensitive, so case-only differences are
ambiguities, not distinct names.)

### G-C — manifest chunk

A manifest chunk is exactly three header lines followed
by one or more body lines:

```
ARCHIVE <archive-id>
CHUNK <k> OF <n>
MANIFEST LINES <a> TO <b> OF <N>
```

- `<archive-id>` conforms to the archive-id grammar
  (§2) and is bound by the case's archive registry.
- `1 ≤ k ≤ n`; `1 ≤ a ≤ b ≤ N`; all integers per §2.
- The body is exactly (b − a + 1) lines, each conforming
  to G-L, each LF-terminated, no bytes after the final LF.

## 4. The checks

Each check names its inputs, its procedure, and its
output. Every check is decidable from the named inputs
alone. A check's output is PASS or FAIL, together with
the computed values the procedure produced (recorded
per §5).

**F1 — ARCHIVE-IDENTITY.** Inputs: the archive's bytes;
the pinned archive digest named in the case. Procedure:
compute the digest of the archive's bytes; compare for
exact equality with the pinned digest. Output: PASS on
equality, FAIL otherwise; the computed digest is
recorded either way.

**F2 — MANIFEST-IDENTITY.** Inputs: the manifest's
bytes; the pinned manifest digest named in the case.
Procedure and output as F1, on the manifest's bytes.

**F3 — MANIFEST-CONFORMANCE.** Inputs: the manifest's
bytes. Procedure: test the bytes against grammar G-M —
file structure (≥1 line, all LF-terminated, nothing
after the final LF), every line against G-L (whose path
field must conform to G-P), all paths pairwise distinct
under byte equality and under ASCII case-folding.
Output: PASS if every test succeeds; FAIL otherwise,
recording the first failing test and the 1-based number
of the first offending line where the failure is a line
failure.

**F4 — MANIFEST-LINE-COUNT.** (Version 1 called this
check ENTRY-COUNT; the ID is unchanged and the title is
corrected per G1-R10-01: this check counts manifest
lines. The archive's member count is an F8 computed
value, not this check's.) Inputs: the manifest's bytes;
the declared line count named in the case. Procedure:
count the lines in the manifest — defined only if the
file's line structure is well-formed under §2; if it is
not, F4's output is FAIL with line_structure recorded
as "malformed" and computed_count recorded as null —
and compare with the declared count. Output: PASS on
equality, FAIL otherwise; the computed count is
recorded either way.

**F5 — REQUIRED-PATH-PRESENCE.** Inputs: the manifest's
bytes; the required-path set named in the case (exact
path strings as they appear in the manifest, each
conforming to G-P). Procedure: for each path in the
set, determine whether it appears as the path field of
exactly one manifest line. Output: PASS if every
required path is present exactly once; FAIL otherwise,
recording which required paths are absent (or
duplicated).

**F6 — CHUNK-CONFORMANCE (revised per G1-R10-03).**
Inputs: the chunk's bytes; the manifest's bytes; the
**expected archive-id** — the archive-id the case's
registry binds to the archive the supplied manifest
belongs to. Procedure, in order:

0. Read the archive-id declared in the chunk's header.
   FAIL (step 0) if it does not conform to the
   archive-id grammar, or if it is not exactly equal,
   byte for byte, to the expected archive-id.
1. Test the chunk against grammar G-C, including the
   header forms and the body line count (b − a + 1).
2. Test every body line against G-L.
3. Compare the body lines, in order, byte-for-byte with
   lines a..b of the manifest.
4. Require the header's `N` to equal the manifest's
   actual line count: the number of lines in the
   supplied manifest bytes under §2's line definition.
   If the manifest's line structure is not well-formed
   (a line not LF-terminated, or bytes after the final
   LF), the count is undefined and this step FAILs.

Output: PASS if every step succeeds; FAIL otherwise,
recording which step failed, the declared and expected
archive-ids, and, for step 3, the 1-based position of
the first differing body line.

**Boundary of F6 (explicit, per G1-R10-03).** The
header values `k` and `n` are checked only locally:
their grammar, and 1 ≤ k ≤ n. Whether the complete
declared chunk set (chunks 1..n, each exactly once) was
in fact presented at the gate is **not** an F6 result
and is not part of format conformance under this
definition; it is a property of the gate's routing
record, where it is recorded as routing state.

**F7 — NAMED-EXHIBIT-IDENTITY.** Inputs: a named exhibit
file's bytes; the pinned digest for that exhibit named
in the case. Procedure and output as F1. This check
covers artefacts the case names as load-bearing that
ride *beside* a manifest rather than inside the
archive — in run-02's case, the archives'
README-EXECUTION.md exhibits (see REV10 §1, correction
C-2: those files are not manifest entries and are never
checked by F5).

**F8 — ARCHIVE–MANIFEST CORRESPONDENCE (new in
version 2, per G1-R10-01).** Inputs: the archive's
bytes; the manifest's bytes; the case's **carrier
set** — a named set of exact member names permitted to
occur in the archive without a manifest line (for the
run-02 case: exactly `MANIFEST.sha256` and
`README-EXECUTION.md`, the two members the real
archives carry at their root beside the listed tree).
Procedure, in order:

1. Parse the archive as a ZIP file and enumerate its
   members in central-directory order. If the archive
   cannot be parsed, FAIL (structure: not a readable
   ZIP archive).
2. Classify each member: a **directory entry** iff its
   name ends with `/`; otherwise a **regular file** iff
   its Unix mode type (the high 16 bits of its external
   attributes, when nonzero) is 0 or a regular file
   (0o100000); a **symlink** iff its mode type is
   0o120000; anything else is **other**. (An archive
   carrying no Unix mode bits is treated as regular
   files and directory entries by name.)
3. If any member name occurs more than once across all
   members (exact byte equality), FAIL, recording the
   duplicated names.
4. If any member is a symlink or **other**, FAIL,
   recording those names. A conforming archive contains
   only regular files and directory entries.
5. Directory entries are counted and excluded from the
   correspondence set. No prefix or non-emptiness
   condition is imposed on them: empty directory
   entries are legitimate (the real archives each
   contain 16; see TV-9).
6. Parse the manifest bytes under G-M. If they do not
   parse, FAIL (manifest not parseable under G-M).
   Let M be the manifest's path set with its digest
   map, and A the set of regular-file member names.
   Every member of the carrier set must occur in A
   exactly once; if a named carrier member is absent,
   FAIL, recording it.
7. Let A′ = A minus the carrier set. Compute
   absent = M − A′ (listed in the manifest, not in the
   archive) and unlisted = A′ − M (in the archive, not
   listed, and not carrier). If either is non-empty,
   FAIL, recording both lists in full, in byte order.
8. For every path in M ∩ A′, compute the SHA-256 of the
   member's uncompressed bytes and compare it with the
   manifest's digest for that path. If any differ,
   FAIL, recording the mismatch count and the first
   mismatch in byte order (path, manifest digest,
   computed digest).
9. Carrier-manifest binding: if the carrier set names
   a manifest member (for the run-02 case,
   `MANIFEST.sha256`), compute that member's digest and
   require it to equal the computed digest of the
   supplied manifest bytes (F2's computed value). If it
   differs, FAIL (the supplied manifest is not the
   archive's own manifest).

Output: PASS only if every step passes; FAIL
otherwise, recording: total member count, regular-file
member count, directory-entry count, the carrier
members found, the absent list, the unlisted list, the
mismatch count, and the first mismatch.

**Applicability.** For the archive gate the case names,
per archive: F1, F2, F3, F4, F5, F8, and F7 for each
named exhibit. F6 applies to any chunk presented at a
gate. A check not named for an input is not run and
not recorded — and §5's schema makes an omitted
applicable check mechanically detectable.

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
the routing record, not a verdict, and never a pass. No
verdict record (below) exists for an UNEXAMINED item.

### 5.1 Verdict Record Schema V1 (new in version 2, per G1-R10-04)

A verdict record is a single JSON object, encoded in
UTF-8, conforming to this schema. The schema is closed
and exact; a text that violates any rule below is
**not a verdict record** and is mechanically rejectable
as such.

**Serialization rules.**

- (S1) No duplicate keys at any object level: a text
  containing the same key twice in one object is not a
  record.
- (S2) Unknown fields: any key not listed for its
  object level, at any level, invalidates the record.
- (S3) Where the schema says *integer*, the value is a
  JSON integer (no fraction, no exponent).
- (S4) Where the schema says *digest*, the value is a
  JSON string matching `^[0-9a-f]{64}$`.
- (S5) Where the schema says *timestamp*, the value is
  a JSON string matching
  `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` denoting a
  valid UTC calendar time.
- (S6) Canonical form (used whenever the record itself
  is fingerprinted): the JSON text with object keys
  sorted by byte order at every level, no insignificant
  whitespace, encoded in UTF-8. The record's fingerprint
  is the SHA-256 of its canonical form.

**Top level.** Exactly these nine fields, all required:

| field | type | rule |
|---|---|---|
| `record_type` | string | exactly `"gate-format-verdict"` |
| `schema_version` | integer | exactly `1` |
| `gate_id` | string | 1–64 characters of `[a-z0-9-]`, first character `[a-z0-9]` |
| `format_definition` | object | exactly the fields `citation` (non-empty string) and `sha256` (digest) |
| `inputs` | array | at least one item; each item an object with exactly `name` (non-empty string) and `sha256` (digest — the computed digest of that input's bytes); `name` values unique within the array |
| `applicable_checks` | array | non-empty; each item one of `"F1"`…`"F8"`; items unique |
| `checks` | array | each item an object with exactly `check_id`, `result`, `values` (below); the set of `check_id` values equals the set in `applicable_checks` exactly — an omitted applicable check, an unlisted check, or a duplicate each invalidates the record |
| `verdict` | string | `"CONFORMING"` or `"NON-CONFORMING"`; consistency rule: `"CONFORMING"` if and only if every `checks` item's `result` is `"PASS"` — a record violating this is invalid |
| `computation` | object | exactly the fields `checker` (non-empty string — the computing checker's identity), `tool` (null, or an object with exactly `name` (non-empty string), `version` (string), `sha256` (digest)), and `time_utc` (timestamp) |

**Check items.** `check_id` is one of `"F1"`…`"F8"`;
`result` is `"PASS"` or `"FAIL"`; `values` is an object
whose keys are exactly those listed for that check,
all required:

| check | `values` keys and types |
|---|---|
| F1 | `expected_sha256` (digest), `computed_sha256` (digest) |
| F2 | `expected_sha256` (digest), `computed_sha256` (digest) |
| F3 | `first_failing_test` (string or null), `first_failing_line` (integer or null) — both null on PASS |
| F4 | `declared_count` (integer ≥ 0), `computed_count` (integer ≥ 0, or null when the line structure is malformed), `line_structure` (`"well-formed"` or `"malformed"`) |
| F5 | `absent_paths` (array of path strings, byte order), `duplicated_paths` (array of path strings, byte order) |
| F6 | `declared_archive_id` (string), `expected_archive_id` (string), `failed_step` (integer 0–4, or null on PASS), `first_differing_body_line` (integer, or null) |
| F7 | `expected_sha256` (digest), `computed_sha256` (digest) |
| F8 | `total_members` (integer ≥ 0), `file_members` (integer ≥ 0), `directory_entries` (integer ≥ 0), `carrier_members` (array of strings, byte order), `absent` (array of path strings, byte order), `unlisted` (array of path strings, byte order), `mismatch_count` (integer ≥ 0), `first_mismatch` (null, or an object with exactly `path` (string), `manifest_sha256` (digest), `computed_sha256` (digest)) |

Every digest comparison a check performs is recorded
with **both** the pinned expected digest and the
computed digest (F1, F2, F7 directly; F8's mismatches
carry the manifest digest as the expected value). The
pinned values themselves resolve through the case,
which names them by the artefact identities in
`inputs` and `format_definition`.

### 5.2 Worked verdict records

**Valid record.** The record of TV-1's computation
(§6), expressed in this schema; it cites definition
version 1, under which that computation was specified:

```json
{
  "record_type": "gate-format-verdict",
  "schema_version": 1,
  "gate_id": "archive-gate",
  "format_definition": {
    "citation": "2026-11-20/gate-definition/gate-format-definition",
    "sha256": "ff42be32baa8f394f1d04d5211e2ecc01df08cb9b201977e706e59bfeeb98e92"
  },
  "inputs": [
    {
      "name": "manifest-tv-1-miniature",
      "sha256": "d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84"
    }
  ],
  "applicable_checks": ["F2", "F3", "F4", "F5"],
  "checks": [
    {
      "check_id": "F2",
      "result": "PASS",
      "values": {
        "expected_sha256": "d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84",
        "computed_sha256": "d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84"
      }
    },
    {
      "check_id": "F3",
      "result": "PASS",
      "values": {"first_failing_test": null, "first_failing_line": null}
    },
    {
      "check_id": "F4",
      "result": "PASS",
      "values": {"declared_count": 3, "computed_count": 3, "line_structure": "well-formed"}
    },
    {
      "check_id": "F5",
      "result": "PASS",
      "values": {"absent_paths": [], "duplicated_paths": []}
    }
  ],
  "verdict": "CONFORMING",
  "computation": {
    "checker": "independent-checker-c",
    "tool": null,
    "time_utc": "2026-11-20T21:20:00Z"
  }
}
```

**Invalid record 1 — verdict contradicts its checks.**
The record above with F4's `result` changed to
`"FAIL"` (and its values recording declared 3, computed
4) while `verdict` remains `"CONFORMING"`. Rejected
under the consistency rule: `"CONFORMING"` requires
every recorded check to be PASS.

**Invalid record 2 — omitted applicable check.** The
record above with `"F8"` added to `applicable_checks`
but no F8 item added to `checks`. Rejected under the
set-equality rule: the recorded checks must equal the
applicable set exactly, so an applicable check the
computation skipped is detectable from the record
alone.

## 6. Worked test vectors

A reader with these inputs and this document must
obtain exactly the stated results. TV-1 to TV-8 are
version 1's vectors, restated; their computations are
unchanged under version 2 except where noted. Digests
were computed from the stated bytes.

**TV-1 — conforming miniature manifest.** Bytes: the
first three lines of the Stage 9 v1 manifest, exactly
as filed (each LF-terminated):

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
**CONFORMING**. (The examiner independently recomputed
this digest; REV10 verdict, clarification 3.)

**TV-2 — uppercase hex (F3 fails).** TV-1's bytes with
the first character of line 1 uppercased (`0f33…` →
`Af33…`). F3 FAIL (line 1, G-L digest field). Verdict:
**NON-CONFORMING**, failing check F3.

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

**TV-6 — identity and conformance are separate
checks.** TV-1's bytes, pinned manifest digest = the
real v1 manifest digest
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
Under version 2 the vector's case binds `tv-mini` as
the expected archive-id for TV-1's manifest (the id
conforms to the §2 grammar), so F6 step 0 passes, and
the header's N (3) equals TV-1's actual line count, so
step 4 passes: F6 PASS → **CONFORMING**.

**TV-8 — the real manifests.** The Stage 9 manifests as
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
- Re-examined under version 2's G-P at this drafting:
  all 686 v1 paths and all 687 v2 paths conform to G-P
  (zero violations), and each manifest's paths are
  distinct under ASCII case-folding as G-M now
  requires. The path byte inventory of both manifests
  is printable ASCII drawn from
  `+ - . / 0-9 A-Z _ a-z`.
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

**TV-9 — the real archives under F8 (computed at this
drafting).** Inputs: the real v1 and v2 archives
(located in the workspace as
`duenna-execution-package-20261120.zip` and
`duenna-execution-package-20261120-v2.zip`; their
SHA-256 values recompute to the F1 pinned values
above), the supplied manifests of TV-8, and the
carrier set {`MANIFEST.sha256`, `README-EXECUTION.md`}.

- v1 archive: total members 771; regular-file members
  688; directory entries 83 (16 of them empty — no file
  member beneath them — permitted under F8 step 5);
  carrier members found: both; absent: none; unlisted:
  none; digest mismatches: 0 of 686 compared. F8 step 9:
  the in-archive `MANIFEST.sha256` member's digest is
  `bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948`,
  equal to the supplied manifest's computed digest.
  **F8 PASS.** Note the three distinct counts this
  vector keeps separate, per G1-R10-01: manifest lines
  686 (F4), archive file members 688, archive total
  members 771.
- v2 archive: total members 772; regular-file members
  689; directory entries 83 (16 empty); carrier members
  found: both; absent: none; unlisted: none; digest
  mismatches: 0 of 687 compared. Step 9: in-archive
  manifest digest
  `92b5d98c04ba172482b583a2153ecc4264135590c77134c5ba144870f20a3c25`,
  equal to the supplied manifest's computed digest.
  **F8 PASS.**

**TV-10 — member digest wrong; manifest valid (F8
fails alone).** A ZIP archive containing exactly two
regular files, `a.txt` with bytes `alpha\n` (digest
`b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060`)
and `b.txt` with bytes `beta\n` (digest
`f2c82decdd7181cf98945929a62598db7e6b477e11f6e0eb0ae97020eff151ad`),
no directory entries, carrier set empty. The manifest
is the two lines

```
b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060  a.txt
ae9a6306a205417afddd14316cc1d0d5e04a98f1be10865dce643925ee070ce2  b.txt
```

whose SHA-256 is
`8b3e7fbf69af7a7a47efa88257de7bddb06b749858273d57da5c03c034f8d2d3`
(the second line carries the digest of `gamma\n`, not
of the member's actual bytes). With that value pinned:
F2 PASS · F3 PASS · F4 PASS (computed 2) · **F8 FAIL**
— mismatch_count 1, first_mismatch {path `b.txt`,
manifest_sha256
`ae9a6306a205417afddd14316cc1d0d5e04a98f1be10865dce643925ee070ce2`,
computed_sha256
`f2c82decdd7181cf98945929a62598db7e6b477e11f6e0eb0ae97020eff151ad`}.
Verdict: **NON-CONFORMING**, failing check F8 only.
This is the case G1-R10-01 names: the manifest's digest
and syntax are valid, and the archive's contents do
not match it.

**TV-11 — unlisted member (F8 fails).** The same
archive as TV-10; the manifest is the single line for
`a.txt` above (SHA-256
`9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06`),
pinned and valid. F2 PASS · F3 PASS · F4 PASS (computed
1) · **F8 FAIL** — unlisted [`b.txt`], absent [].
Verdict: **NON-CONFORMING**, failing check F8 only.

**TV-12 — absent member (F8 fails).** A ZIP archive
containing exactly `a.txt` as in TV-10; the manifest
is the two lines

```
b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060  a.txt
ae9a6306a205417afddd14316cc1d0d5e04a98f1be10865dce643925ee070ce2  c.txt
```

(SHA-256
`15f6339ce485f1020ba6632fdde47991d05fb2f321bfcb0689fa02f0834b6435`),
pinned and valid. F2 PASS · F3 PASS · F4 PASS (computed
2) · **F8 FAIL** — absent [`c.txt`], unlisted [].
Verdict: **NON-CONFORMING**, failing check F8 only.

(The ZIP container bytes of TV-10 to TV-12 are
immaterial to F8: any ZIP containing exactly the stated
members with the stated bytes yields the stated
results.)

## 7. What this definition does not do

- It judges no content. That the archive computed
  CONFORMING is the archive the case names is F1/F2/F8's
  digest equalities and nothing more; every further
  claim about the archive is a content judgement,
  recorded as judgement with its evidence (design §3.3).
- It defines no other artefact type's grammar. Envelope,
  ledger, and call-record formats are outside its scope;
  the verdict record's shape is defined at §5.1 because
  design §3.2(3) assigns it to this artefact. A gate
  that examines other formats does so under a definition
  exhibited for them, added by package revision — never
  by stretching this one.
- It issues no gate outcome. ALLOW / CORRECT /
  NOT SATISFIED are the gate's acts on computed format
  results and judged content results together (design
  §3.6; REV10 §4, carried by REV11); this definition
  supplies only the format half.
- Chunk-set completeness is a routing property, not a
  format property (F6 boundary, §4).

## 8. Implementation

The procedures of §4 are stated so they can be
performed by hand on small inputs and by any
deterministic tool on large ones. This definition
relies on no named executable: conformance of an
implementation is established by reproducing §6's
vectors exactly. Where a tool is used for a
computation, the verdict record's `computation` field
names the tool, its version, and its digest (§5.1); an
unnamed tool's output is not an authoritative
computation record. If a future revision pins a
specific implementation, it pins the implementation's
digest and its dependencies' digests in the package,
per G1-R9-01.

## Disposition

Gate Format Definition version 2, prepared as a draft
on 2026-11-20 under Ben's tap of 2026-11-20 21:17 MST
commissioning Revision 11; its status at any time is
what the filing record states. Exhibited for Gate 1
examination as part of Revision 11; it takes effect
for a run only as part of a package revision that
passes Gate 1, frozen into that run's schema object.
It satisfies no start condition by its own existence.

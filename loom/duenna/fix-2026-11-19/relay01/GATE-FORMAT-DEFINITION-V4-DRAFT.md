# GATE FORMAT DEFINITION — RELAY 01 (VERSION 4, DRAFT)

*Status: prepared as a draft on 2026-11-20; its status at
any time is what the filing record states. Version 4 of
the Gate Format Definition, drafted under Ben's tap of
2026-11-20 21:53 MST (widget-97bf221e-3b28-4c7f-a7de-3eeb65173e69)
and his words commissioning Revision 13: "Draft REV13 —
close the last two locks: type-first member
classification, case identity bound into the run
identity." It answers finding G1-R12-01 of Vane's Gate 1
verdict on Revision 12
(`VANE-GATE1-VERDICT-REV12-2026-11-20.md`, Git blob
d1d756679ef91f34aede8d2b43790c94da5775a8, filing commit
5ddff2840e7eb154a8aba856936fd6a30a468a33); finding
G1-R12-02 (the K1 run-identity construction) is answered
in Revision 13 §5.1, not in this artefact. Version 4
supersedes version 3 (`GATE-FORMAT-DEFINITION-V3-DRAFT.md`,
SHA-256 97a262e35ea827315c6b4e95d22866adbe60d2a80c8454ac5f5e237ea496f325)
as the exhibited definition where a package revision
incorporates this version. Versions 1 to 3 are preserved
as filed; nothing in this version edits them. Citation
(Annex B §B2.2 form): 2026-11-20/gate-definition/gate-format-definition-v4.
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

**Scope, stated exactly.** This definition's procedures
do all of the following, and nothing beyond them: verify
the archive's identity by digest (F1); verify the
manifest's identity by digest (F2); verify the manifest's
syntax (F3); count the manifest's lines (F4); verify
required paths occur in the manifest (F5); verify a chunk
against its manifest and the case (F6); verify named
exhibit files by digest (F7); and compare the archive's
actual member set and member digests against the manifest
in full, validating every member name — directory entries
included, as classified by member type under the
type-first rule — under the pinned byte-to-name rule
(F8). Every
outcome those procedures can produce is recordable in the
verdict record's shape (§5.1). Where this definition does
not define a procedure, it claims none.

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
- **Member name.** A ZIP member's name is determined
  under grammar G-N (§3): the raw filename bytes of its
  central-directory header, with no decoding of any
  kind. How a member name is rendered inside a verdict
  record is defined at §5.1 (rule S7).
- **Member type.** A member's type is determined from
  its type metadata, never from its name (§4, F8 step
  2). The type metadata is the high 16 bits of the
  member's central-directory external attributes, read
  as a Unix mode **only** when the member's
  version-made-by host is Unix (host value 3); for any
  other host value the member carries no type metadata
  this definition reads. Within the mode, the file-type
  field is the bits masked by 0o170000: 0o040000
  directory, 0o100000 regular file, 0o120000 symlink,
  any other nonzero value another type. Type metadata
  is **absent** when the host is not Unix, when the
  mode is 0, or when the file-type field is 0
  (permissions recorded without a type). A member's
  name ending in the separator byte is a fact about its
  name form (§3, G-N), never a type determination.

## 3. Grammars

### G-P — path

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
may differ only by letter case. (In the archive
environment this definition governs, members are
addressed by name on extraction paths that may be
case-insensitive, so case-only differences are
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

### G-N — ZIP member name (new in version 3, per G1-R11-02)

A member's name is determined from the archive's bytes
alone, as follows:

- **Source.** The name is the filename byte sequence in
  the member's **central-directory header**. The local
  file header is not consulted for names. Enumeration
  is in central-directory order.
- **No decoding.** No character decoding is applied to
  the name bytes at any point. In particular, the ZIP
  general-purpose flag's UTF-8 bit (bit 11), any legacy
  code-page interpretation, and every extra field —
  including the Unicode Path extra field (0x7075) —
  play **no part** in determining the name. Extra fields
  of any type are ignored for name identity, whatever
  they contain. The flag and the extra fields neither
  rescue nor condemn a name.
- **Conformance.** The name conforms iff its raw bytes,
  read as a byte string, satisfy G-P — for a regular
  file or any non-directory member, the name bytes
  themselves; for a **directory entry** (a member
  classified as a directory entry under §4 F8 step 2 —
  by its type metadata, or, where that metadata is
  absent, by its name form), the bytes with that single
  trailing separator removed. The remainder after
  removal must satisfy G-P in full, so a directory
  entry named `/` alone, or ending in two separators,
  does not conform. (Classification and F8 step 4
  together guarantee that a directory entry reaching
  name validation has exactly that one trailing
  separator to remove: a typed directory whose name
  lacks it is a type conflict and fails at step 4,
  before validation.)
- **Name is not type.** G-N determines what a member
  is called, never what it is. A trailing separator in
  a name does not make its member a directory, and the
  absence of one does not make its member a file: type
  is determined under §4 F8 step 2, from type metadata
  first. A name and a type that disagree are a failure
  (F8 step 4), not an interpretation.
- **Why this is unambiguous.** G-P admits only printable
  ASCII bytes. Every such byte sequence reads identically
  under UTF-8, CP437, Latin-1, and every other ASCII-
  superset interpretation, so no two readers applying
  this rule can obtain different names for a conforming
  member; and a name whose bytes fall outside G-P fails
  on its bytes under every interpretation. Ambiguity is
  excluded by the grammar, not by choosing a decoding.


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

**F4 — MANIFEST-LINE-COUNT.** (This check counts
manifest lines. The archive's member count is an F8
computed value, not this check's.) Inputs: the manifest's
bytes; the declared line count named in the case.
Procedure: count the lines in the manifest — defined
only if the file's line structure is well-formed under
§2; if it is not, F4's output is FAIL with line_structure
recorded as "malformed" and computed_count recorded as
null — and compare with the declared count. Output: PASS
on equality, FAIL otherwise; the computed count is
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

**F6 — CHUNK-CONFORMANCE (revised in version 3, per
G1-R11-01).** Inputs: the chunk's bytes; the manifest's
bytes; the **expected archive-id** — the archive-id the
case's registry binds to the archive the supplied
manifest belongs to. Procedure, in order:

H. **Header extraction.** Read the chunk's lines under
   §2 and extract the header fields:
   - Line 1 yields a declared archive-id token iff it is
     exactly `ARCHIVE ` followed by one non-space token
     and nothing else; the token is the declared
     archive-id. (Whether the token conforms to the
     archive-id grammar is step 0's question, not
     extraction's.)
   - Line 2 yields its fields iff it is exactly
     `CHUNK ` + an integer-shaped field + ` OF ` + an
     integer-shaped field, where integer-shaped means
     one or more decimal digits.
   - Line 3 yields its fields iff it is exactly
     `MANIFEST LINES ` + integer-shaped + ` TO ` +
     integer-shaped + ` OF ` + integer-shaped.
   The **header status** is: **"absent"** if the chunk
   has no first line, or its first line does not begin
   with the bytes `ARCHIVE`; **"read"** if all three
   lines yield their fields; **"unparseable"** otherwise
   (a header was attempted — the first line begins with
   `ARCHIVE` — but at least one of the three lines is
   missing or does not yield its fields). If the header
   status is not "read", F6 FAILs at step H, recording
   the status and the declared archive-id (the line-1
   token if line 1 alone yields it, otherwise null).
0. Compare the declared archive-id with the expected
   archive-id. FAIL (step 0) if it does not conform to
   the archive-id grammar, or if it is not exactly
   equal, byte for byte, to the expected archive-id.
1. Test the chunk against grammar G-C, including the
   number forms of §2 (no leading zeros), the ranges
   1 ≤ k ≤ n and 1 ≤ a ≤ b ≤ N, and the body line count
   (b − a + 1).
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
recording the header status, the declared archive-id
(null when no token was extractable), the expected
archive-id, which step failed ("header", 0, 1, 2, 3, or
4), and, for step 3, the 1-based position of the first
differing body line.

**Boundary of F6.** The header values `k` and `n` are
checked only locally: their grammar, and 1 ≤ k ≤ n.
Whether the complete declared chunk set (chunks 1..n,
each exactly once) was in fact presented at the gate is
**not** an F6 result and is not part of format
conformance under this definition; it is a property of
the gate's routing record, where it is recorded as
routing state.

**F7 — NAMED-EXHIBIT-IDENTITY.** Inputs: a named exhibit
file's bytes; the pinned digest for that exhibit named
in the case. Procedure and output as F1. This check
covers artefacts the case names as load-bearing that
ride *beside* a manifest rather than inside the
archive — in run-02's case, the archives'
README-EXECUTION.md exhibits (see REV10 §1, correction
C-2: those files are not manifest entries and are never
checked by F5).

**F8 — ARCHIVE–MANIFEST CORRESPONDENCE (revised in
version 4, per G1-R12-01; revised in version 3, per
G1-R11-01 and G1-R11-02).** Inputs: the
archive's bytes; the manifest's bytes; the case's
**carrier set** — a named set of exact member names
permitted to occur in the archive without a manifest
line (for the run-02 case: exactly `MANIFEST.sha256`
and `README-EXECUTION.md`, the two members the real
archives carry at their root beside the listed tree).
Procedure, in order:

1. Parse the archive as a ZIP file and enumerate its
   members in central-directory order, taking each
   member's name under G-N. If the archive cannot be
   parsed, FAIL (structure: not a readable ZIP archive).
2. **Classify each member by type — type metadata
   first (revised in version 4, per G1-R12-01).** Read
   each member's type metadata (§2): the file-type
   field of its Unix mode, where the member carries
   one. Classify:
   - file-type field 0o040000 → **directory entry**
     (typed);
   - file-type field 0o100000 → **regular file**
     (typed);
   - file-type field 0o120000 → **symlink**;
   - any other nonzero file-type field → **other**;
   - type metadata absent (§2: non-Unix host, mode 0,
     or file-type field 0) → classify by name form: a
     name ending with `/` → **directory entry**
     (untyped); any other name → **regular file**
     (untyped).
   The name suffix alone never establishes type: a
   member with type metadata is classified by that
   metadata whatever its name, and a typed member
   whose name form contradicts its type is not
   reclassified to fit its name — the contradiction is
   recorded and fails the check at step 4. The member
   counts (total, regular-file, directory-entry) are
   computed from this classification; symlink and other
   members count in the total only.
3. If any member name occurs more than once across all
   members (exact byte equality), FAIL, recording every
   duplicated name.
4. **Type admissibility and name-form consistency
   (revised in version 4, per G1-R12-01).** FAIL if
   either:
   (a) any member is a symlink or **other**, whatever
   its name — including a name ending with `/` —
   recording each such member in `rejected_members`
   with its name and its type; or
   (b) any **typed** member's name form contradicts
   its type: a regular-file type whose name ends with
   `/`, or a directory type whose name does not end
   with `/` — recording each such member in
   `type_conflicts` with its name, its mode type, and
   whether its name is terminated.
   A conflicted member is rejected: it is neither
   counted as a directory entry for exclusion nor
   admitted to the correspondence set, and the
   procedure stops here. Untyped members cannot
   conflict: their classification already rests on
   their name form. A conforming archive passes this
   step only if every member is a directory entry or a
   regular file whose name form agrees with its type,
   or whose type was name-derived.
5. **Name validation.** Validate every member name
   under G-N: a non-directory member's name bytes must
   satisfy G-P; a directory entry's name bytes, with
   the single trailing separator removed, must satisfy
   G-P. (Directory entry here means a member classified
   as a directory entry at step 2 and admitted at step
   4; step 4 has already established that its name ends
   with the single trailing separator this step
   removes.) If any name does not conform, FAIL,
   recording every invalid name.
6. Directory entries — the members classified as
   directory entries at step 2 and admitted at step 4 —
   are excluded from the correspondence set. No prefix
   or non-emptiness condition is imposed on them: empty
   directory entries are legitimate (the real archives
   each contain 16; see TV-9). No member reaches this
   step on the strength of its name alone: exclusion is
   granted only to a member whose directory type was
   established at step 2 and whose name form agreed at
   step 4.
7. Parse the manifest bytes under G-M. If they do not
   parse, FAIL (manifest not parseable under G-M).
   Let M be the manifest's path set with its digest
   map, and A the set of regular-file member names.
   Every member of the carrier set must occur in A
   exactly once; if a named carrier member is absent,
   FAIL, recording every missing carrier.
8. Let A′ = A minus the carrier set. Compute
   absent = M − A′ (listed in the manifest, not in the
   archive) and unlisted = A′ − M (in the archive, not
   listed, and not carrier). If either is non-empty,
   FAIL, recording both lists in full, in byte order.
9. For every path in M ∩ A′, compute the SHA-256 of the
   member's uncompressed bytes and compare it with the
   manifest's digest for that path. If any differ,
   FAIL, recording **every** mismatch (path, manifest
   digest, computed digest), in byte order by path.
10. Carrier-manifest binding: if the carrier set names
    a manifest member (for the run-02 case,
    `MANIFEST.sha256`), compute that member's digest and
    require it to equal the computed digest of the
    supplied manifest bytes (F2's computed value). If it
    differs, FAIL (the supplied manifest is not the
    archive's own manifest), recording both digests.

Output: PASS only if every step passes; FAIL otherwise,
recording: which step failed; the structure state; the
total member count, regular-file member count, and
directory-entry count; every duplicated name; every
rejected member with its type; every type conflict
with its mode type and name form; every invalid name;
the
manifest's parse state; the carrier members found and
every missing carrier; the absent list; the unlisted
list; every digest mismatch; and the carrier-manifest
digests where step 10 applies. §5.1's schema gives each
of these a field; no F8 outcome is without a recordable
form.

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
Note the distinction F8 now makes recordable: an archive
that was delivered but cannot be parsed is a FAIL with
structure "unreadable" (F8 step 1); an archive that was
never delivered is UNEXAMINED and has no record at all.

### 5.1 Verdict Record Schema V3 (new in version 4, per G1-R12-01)

A verdict record is a single JSON object, encoded in
UTF-8, conforming to this schema. The schema is closed
and exact; a text that violates any rule below is
**not a verdict record** and is mechanically rejectable
as such.

**What changed from Schema V2, and why.** One change,
driven by finding G1-R12-01. Version 4's F8 classifies
members by type metadata first and fails on two
name/type disagreements that Schema V2's F8 values
could not express. The coverage, field by field:
(a) a symlink or other type, whatever its name —
recordable in Schema V2 already, in `rejected_members`
with its `member_type`; unchanged. (b) A regular-file
type with a separator-terminated name, and (c) a
directory type with an unterminated name — **not**
recordable in Schema V2: `rejected_members` records
members rejected for their type, and these members'
types are admissible — what fails is the agreement
between type and name form; `invalid_names` records
names that fail G-P, and an unterminated directory
name may satisfy G-P exactly, so outcome (c) had no
recordable form at all. Schema V3 therefore adds one
F8 field, `type_conflicts`, recording each conflicted
member's name, mode type, and name form; and
`schema_version` is 3. Nothing else changes: the
top-level shape, rules S1–S7, the set-equality and
verdict-consistency rules, the not-performed
convention, and the values shapes of F1–F7 and of
F8's other fields are as Schema V2 stated them.
Records written under Schema V2 remain valid history
under that schema; they are not records under this
one. (Schema V2 itself completed Schema V1's F8
shape, gained F6's header status, and added rule S7,
per finding G1-R11-01; that history stands as version
3 recorded it.)

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
- (S7) Where the schema says *member name*, the value
  is a JSON string produced by mapping each byte b of
  the member's name to the Unicode code point U+00b
  (the Latin-1 rendering). The mapping is a bijection
  between byte sequences and such strings, so the exact
  name bytes are recoverable from the record, including
  for names that fail G-P. (Manifest paths are G-P
  ASCII, a subset of this rendering, and appear as
  themselves.)

**Top level.** Exactly these nine fields, all required:

| field | type | rule |
|---|---|---|
| `record_type` | string | exactly `"gate-format-verdict"` |
| `schema_version` | integer | exactly `3` |
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
| F6 | `header_status` (`"read"`, `"absent"`, or `"unparseable"`), `declared_archive_id` (string, or null when no token was extractable), `expected_archive_id` (string), `failed_step` (`"header"`, `"0"`, `"1"`, `"2"`, `"3"`, or `"4"`, or null on PASS), `first_differing_body_line` (integer, or null) |
| F7 | `expected_sha256` (digest), `computed_sha256` (digest) |
| F8 | see the F8 list below |

**F8 values** — exactly these keys, all required:

- `failed_step` (integer 1–10, or null on PASS)
- `structure` (`"readable"` or `"unreadable"`)
- `total_members`, `file_members`, `directory_entries`
  (integer ≥ 0; **null when `structure` is
  `"unreadable"`**, since no enumeration exists)
- `duplicate_names` (array of member names, byte order)
- `rejected_members` (array of objects with exactly
  `name` (member name) and `member_type` (`"symlink"`
  or `"other"`), byte order by name)
- `type_conflicts` (array of objects with exactly
  `name` (member name), `mode_type` (`"directory"` or
  `"regular-file"`), and `name_terminated` (boolean),
  byte order by name — every typed member whose name
  form contradicts its type, per F8 step 4(b); empty
  when no step-4(b) conflict occurred or step 4 was
  not performed)
- `invalid_names` (array of member names, byte order)
- `manifest_parseable` (boolean, or null when step 7
  was not performed)
- `carrier_members` (array of member names found,
  byte order)
- `missing_carriers` (array of member names, byte order)
- `absent` (array of path strings, byte order)
- `unlisted` (array of path strings, byte order)
- `mismatch_count` (integer ≥ 0; rule: it equals the
  number of items in `mismatches`)
- `mismatches` (array of objects with exactly `path`
  (path string), `manifest_sha256` (digest),
  `computed_sha256` (digest), byte order by path —
  **every** mismatch the comparison found)
- `carrier_manifest` (null, or an object with exactly
  `expected_sha256` (digest — the supplied manifest's
  computed digest, F2's computed value) and
  `computed_sha256` (digest — the archive's manifest
  member's digest); null when the carrier set names no
  manifest member, or when step 10 was not performed)

**Not-performed convention (F8).** F8's steps run in
order and stop at the first failure. A step's fields
are evidence only when that step was performed: steps
numbered ≤ `failed_step` were performed (the last of
them failing), steps above it were not. Fields of a
step that was not performed carry their empty values:
empty arrays, `mismatch_count` 0, `manifest_parseable`
null, `carrier_manifest` null. The three member counts
are the exception: they are produced by steps 1–2 and
are recorded whenever `structure` is `"readable"`,
whatever later step failed. A third party can therefore
reconstruct from the record alone exactly which steps
ran, which failed, and all the evidence each produced.

Every digest comparison a check performs is recorded
with **both** the pinned expected digest and the
computed digest (F1, F2, F7 directly; F8's mismatches
carry the manifest digest as the expected value, and
`carrier_manifest` carries both digests of the step-10
comparison). The pinned values themselves resolve
through the case, which names them by the artefact
identities in `inputs` and `format_definition`.

### 5.2 Worked verdict records

**Record A — valid (carried computation, new schema).**
The record of TV-1's computation (§6), expressed in
Schema V3; it cites definition version 1, under which
that computation was specified. The F2–F5 values shapes
are unchanged from Schema V1.

```json
{
  "record_type": "gate-format-verdict",
  "schema_version": 3,
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

**Records B and C — valid (failure branches).**
TV-13's and TV-14's computations (§6). In both records
the miniature case names F1, F2, and F8 as the
applicable checks. Their F8 outcomes are the same
under version 4's procedure (duplicates at step 3;
member-type rejection at step 4); the records are
restated in Schema V3 — the only changes from their
version 3 statement are `schema_version` 3 and the
added `type_conflicts` key, empty in both. They cite
definition version 2 in `format_definition`, under
which the computations were specified.

```json
{
  "record_type": "gate-format-verdict",
  "schema_version": 3,
  "gate_id": "archive-gate",
  "format_definition": {
    "citation": "2026-11-20/gate-definition/gate-format-definition-v2",
    "sha256": "ac3d5e5085fa5691965eae7b7158a6e213fe1f280a618c77889a8568576bc8c4"
  },
  "inputs": [
    {
      "name": "archive-tv-13",
      "sha256": "11408141541b5698bffeb3067ba1cba3b9fa578025dcbf7eba8f1347149c20f8"
    },
    {
      "name": "manifest-tv-13",
      "sha256": "9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06"
    }
  ],
  "applicable_checks": ["F1", "F2", "F8"],
  "checks": [
    {
      "check_id": "F1",
      "result": "PASS",
      "values": {
        "expected_sha256": "11408141541b5698bffeb3067ba1cba3b9fa578025dcbf7eba8f1347149c20f8",
        "computed_sha256": "11408141541b5698bffeb3067ba1cba3b9fa578025dcbf7eba8f1347149c20f8"
      }
    },
    {
      "check_id": "F2",
      "result": "PASS",
      "values": {
        "expected_sha256": "9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06",
        "computed_sha256": "9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06"
      }
    },
    {
      "check_id": "F8",
      "result": "FAIL",
      "values": {
        "failed_step": 3,
        "structure": "readable",
        "total_members": 2,
        "file_members": 2,
        "directory_entries": 0,
        "duplicate_names": ["a.txt"],
        "rejected_members": [],
        "type_conflicts": [],
        "invalid_names": [],
        "manifest_parseable": null,
        "carrier_members": [],
        "missing_carriers": [],
        "absent": [],
        "unlisted": [],
        "mismatch_count": 0,
        "mismatches": [],
        "carrier_manifest": null
      }
    }
  ],
  "verdict": "NON-CONFORMING",
  "computation": {
    "checker": "independent-checker-c",
    "tool": null,
    "time_utc": "2026-11-20T21:45:00Z"
  }
}
```

```json
{
  "record_type": "gate-format-verdict",
  "schema_version": 3,
  "gate_id": "archive-gate",
  "format_definition": {
    "citation": "2026-11-20/gate-definition/gate-format-definition-v2",
    "sha256": "ac3d5e5085fa5691965eae7b7158a6e213fe1f280a618c77889a8568576bc8c4"
  },
  "inputs": [
    {
      "name": "archive-tv-14",
      "sha256": "491b7baf1633f935979236e0a2c10bbeb088ae5698c2eec773fb0613ffe70649"
    },
    {
      "name": "manifest-tv-13",
      "sha256": "9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06"
    }
  ],
  "applicable_checks": ["F1", "F2", "F8"],
  "checks": [
    {
      "check_id": "F1",
      "result": "PASS",
      "values": {
        "expected_sha256": "491b7baf1633f935979236e0a2c10bbeb088ae5698c2eec773fb0613ffe70649",
        "computed_sha256": "491b7baf1633f935979236e0a2c10bbeb088ae5698c2eec773fb0613ffe70649"
      }
    },
    {
      "check_id": "F2",
      "result": "PASS",
      "values": {
        "expected_sha256": "9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06",
        "computed_sha256": "9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06"
      }
    },
    {
      "check_id": "F8",
      "result": "FAIL",
      "values": {
        "failed_step": 4,
        "structure": "readable",
        "total_members": 2,
        "file_members": 1,
        "directory_entries": 0,
        "duplicate_names": [],
        "rejected_members": [{"name": "link.txt", "member_type": "symlink"}],
        "type_conflicts": [],
        "invalid_names": [],
        "manifest_parseable": null,
        "carrier_members": [],
        "missing_carriers": [],
        "absent": [],
        "unlisted": [],
        "mismatch_count": 0,
        "mismatches": [],
        "carrier_manifest": null
      }
    }
  ],
  "verdict": "NON-CONFORMING",
  "computation": {
    "checker": "independent-checker-c",
    "tool": null,
    "time_utc": "2026-11-20T21:45:00Z"
  }
}
```

**Records D, E, and F — valid F8 items (new failure
branches of version 4).** The F8 check items of
TV-17's, TV-18's, and TV-19's computations (§6),
performed at this drafting under version 4's procedure.
The complete records wrap these items with the fields
of §5.1 over the inputs §6 states (the miniature case
names F1, F2, and F8, as in Records B and C); their
`format_definition` cites this version
(2026-11-20/gate-definition/gate-format-definition-v4)
at its as-filed SHA-256, which the incorporating
package states (Revision 13 §0) — a document cannot
print its own digest, so the F8 items are exhibited
here in full and the records' remaining fields are
exactly as §5.1 prescribes.

Record D (TV-17 — symlink with a directory-form name;
rejected under step 4(a)):

```json
{
  "check_id": "F8",
  "result": "FAIL",
  "values": {
    "failed_step": 4,
    "structure": "readable",
    "total_members": 2,
    "file_members": 1,
    "directory_entries": 0,
    "duplicate_names": [],
    "rejected_members": [{"name": "link/", "member_type": "symlink"}],
    "type_conflicts": [],
    "invalid_names": [],
    "manifest_parseable": null,
    "carrier_members": [],
    "missing_carriers": [],
    "absent": [],
    "unlisted": [],
    "mismatch_count": 0,
    "mismatches": [],
    "carrier_manifest": null
  }
}
```

Record E (TV-18 — regular-file type, terminated name;
rejected under step 4(b)):

```json
{
  "check_id": "F8",
  "result": "FAIL",
  "values": {
    "failed_step": 4,
    "structure": "readable",
    "total_members": 2,
    "file_members": 2,
    "directory_entries": 0,
    "duplicate_names": [],
    "rejected_members": [],
    "type_conflicts": [{"name": "file/", "mode_type": "regular-file", "name_terminated": true}],
    "invalid_names": [],
    "manifest_parseable": null,
    "carrier_members": [],
    "missing_carriers": [],
    "absent": [],
    "unlisted": [],
    "mismatch_count": 0,
    "mismatches": [],
    "carrier_manifest": null
  }
}
```

Record F (TV-19 — directory type, unterminated name;
rejected under step 4(b)):

```json
{
  "check_id": "F8",
  "result": "FAIL",
  "values": {
    "failed_step": 4,
    "structure": "readable",
    "total_members": 2,
    "file_members": 1,
    "directory_entries": 1,
    "duplicate_names": [],
    "rejected_members": [],
    "type_conflicts": [{"name": "dir", "mode_type": "directory", "name_terminated": false}],
    "invalid_names": [],
    "manifest_parseable": null,
    "carrier_members": [],
    "missing_carriers": [],
    "absent": [],
    "unlisted": [],
    "mismatch_count": 0,
    "mismatches": [],
    "carrier_manifest": null
  }
}
```

**Invalid record — a Schema V1 F8 shape under Schema
V3.** Record B with its F8 `values` replaced by Schema
V1's key set (carrying `first_mismatch` and omitting
`mismatches`, `missing_carriers`, `invalid_names`,
`rejected_members`, `type_conflicts`,
`manifest_parseable`, `carrier_manifest`,
`failed_step`, and `structure`).
Rejected three ways: the key `first_mismatch` is not
listed for F8 under Schema V3 (rule S2, unknown field);
nine required keys are missing (closed key set, all
required); and no field records which step failed, so
the record could not state how far the procedure ran.
Schema V1's two invalid examples (a verdict
contradicting its checks; an omitted applicable check)
remain invalid under the same rules in Schema V3.


## 6. Worked test vectors

A reader with these inputs and this document must
obtain exactly the stated results. TV-1 to TV-12 are
version 2's vectors, restated; their computations are
unchanged under version 4 except where noted (TV-10's
record language follows Schema V3). TV-13 to TV-16 are
version 3's vectors, restated; TV-13's and TV-14's
outcomes are unchanged under version 4's procedure
(duplicates at step 3; member-type rejection at step
4). TV-17 to TV-20 are new in version 4. Digests were
computed from the stated bytes.

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
The vector's case binds `tv-mini` as the expected
archive-id for TV-1's manifest (the id conforms to the
§2 grammar), so F6 step 0 passes, and the header's N
(3) equals TV-1's actual line count, so step 4 passes:
F6 PASS (header status "read") → **CONFORMING**.

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
- All 686 v1 paths and all 687 v2 paths conform to G-P
  (zero violations), and each manifest's paths are
  distinct under ASCII case-folding as G-M requires.
  The path byte inventory of both manifests is
  printable ASCII drawn from `+ - . / 0-9 A-Z _ a-z`.
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

**TV-9 — the real archives under F8 (computed at the
Revision 11 drafting).** Inputs: the real v1 and v2
archives (located in the workspace as
`duenna-execution-package-20261120.zip` and
`duenna-execution-package-20261120-v2.zip`; their
SHA-256 values recompute to the F1 pinned values
above), the supplied manifests of TV-8, and the
carrier set {`MANIFEST.sha256`, `README-EXECUTION.md`}.

- v1 archive: total members 771; regular-file members
  688; directory entries 83 (16 of them empty — no file
  member beneath them — permitted under F8 step 6);
  carrier members found: both; absent: none; unlisted:
  none; digest mismatches: 0 of 686 compared. Step 10:
  the in-archive `MANIFEST.sha256` member's digest is
  `bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948`,
  equal to the supplied manifest's computed digest.
  **F8 PASS.** Note the three distinct counts this
  vector keeps separate: manifest lines 686 (F4),
  archive file members 688, archive total members 771.
- v2 archive: total members 772; regular-file members
  689; directory entries 83 (16 empty); carrier members
  found: both; absent: none; unlisted: none; digest
  mismatches: 0 of 687 compared. Step 10: in-archive
  manifest digest
  `92b5d98c04ba172482b583a2153ecc4264135590c77134c5ba144870f20a3c25`,
  equal to the supplied manifest's computed digest.
  **F8 PASS.**

**Status of this vector (per the REV11 verdict).** The
exercise above is the orchestrator's reported
verification, computed at the Revision 11 drafting and
independently re-performed by the orchestrator with a
second script before that filing. The examiner has
**not** independently rerun F8 against the two ZIP byte
streams, and this vector does not claim her
verification. The inputs (the archives at the F1 pins,
the manifests at the TV-8 pins, the carrier set) and
the procedure (§4 F8) are stated in full so the
exercise can be rerun byte-for-byte by any reader.

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
— failed step 9, mismatch_count 1, mismatches [{path
`b.txt`, manifest_sha256
`ae9a6306a205417afddd14316cc1d0d5e04a98f1be10865dce643925ee070ce2`,
computed_sha256
`f2c82decdd7181cf98945929a62598db7e6b477e11f6e0eb0ae97020eff151ad`}].
Verdict: **NON-CONFORMING**, failing check F8 only.
This is the case G1-R10-01 names: the manifest's digest
and syntax are valid, and the archive's contents do
not match it.

**TV-11 — unlisted member (F8 fails).** The same
archive as TV-10; the manifest is the single line for
`a.txt` above (SHA-256
`9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06`),
pinned and valid. F2 PASS · F3 PASS · F4 PASS (computed
1) · **F8 FAIL** — failed step 8, unlisted [`b.txt`],
absent []. Verdict: **NON-CONFORMING**, failing check
F8 only.

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
2) · **F8 FAIL** — failed step 8, absent [`c.txt`],
unlisted []. Verdict: **NON-CONFORMING**, failing
check F8 only.

**TV-13 — duplicate member names (F8 fails; new in
version 3).** A ZIP archive constructed at this
drafting (209 bytes; SHA-256
`11408141541b5698bffeb3067ba1cba3b9fa578025dcbf7eba8f1347149c20f8`)
containing exactly two members, both named `a.txt`:
the first with bytes `alpha\n`, the second with bytes
`beta\n`; no directory entries; carrier set empty. The
manifest is the single `a.txt` line of TV-11 (SHA-256
`9d8bca13ebed4026374f18e05a5eaed8f6e6fe87b279f1673a960bc7447f0e06`),
pinned and valid. F1 PASS · F2 PASS · F3 PASS · F4 PASS
(computed 1) · **F8 FAIL** — failed step 3,
duplicate_names [`a.txt`], total members 2, file
members 2, directory entries 0; steps 4–10 not
performed, their fields empty under §5.1's convention.
Verdict: **NON-CONFORMING**, failing check F8 only.
The computation's verdict record is exhibited at §5.2
(Record B). Under Schema V1 this outcome had no
recordable form; under Schema V2 it did, and Schema V3
carries it unchanged.

**TV-14 — symlink member (F8 fails; new in version
3).** A ZIP archive constructed at this drafting (211
bytes; SHA-256
`491b7baf1633f935979236e0a2c10bbeb088ae5698c2eec773fb0613ffe70649`)
containing exactly two members: `a.txt`, a regular
file (Unix mode 0o100644) with bytes `alpha\n`; and
`link.txt`, a symlink (Unix mode 0o120777) whose
content is the bytes `a.txt`; no directory entries;
carrier set empty. The manifest is TV-13's (the single
`a.txt` line), pinned and valid. F1 PASS · F2 PASS ·
F3 PASS · F4 PASS (computed 1) · **F8 FAIL** — failed
step 4, rejected_members [{name `link.txt`,
member_type `symlink`}], total members 2, file members
1, directory entries 0; steps 5–10 not performed.
Verdict: **NON-CONFORMING**, failing check F8 only.
The computation's verdict record is exhibited at §5.2
(Record C).

**TV-15 — chunk headers that cannot be read (F6 fails;
new in version 3).** The case is TV-7's: the expected
archive-id for TV-1's manifest is `tv-mini`.

- (a) *Unparseable header.* Chunk bytes: the single
  line `ARCHIVE` (LF-terminated, no token) followed by
  TV-1's three lines. SHA-256 of the chunk:
  `55e3731b036f815432ac7e9250c6ba6baca7fd09c41a02f1cc3523fcb4ef9ea8`.
  F6 FAIL at step H — header_status `"unparseable"`,
  declared_archive_id null, expected_archive_id
  `tv-mini`, failed_step `"header"`. Verdict:
  **NON-CONFORMING**, failing check F6 only.
- (b) *Absent header.* Chunk bytes: TV-1's three lines
  alone — a manifest presented where a chunk was
  expected (the bytes are exactly TV-1's; SHA-256
  `d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84`).
  The first line does not begin with `ARCHIVE`: F6 FAIL
  at step H — header_status `"absent"`,
  declared_archive_id null, failed_step `"header"`.
  Verdict: **NON-CONFORMING**, failing check F6 only.

Under Schema V1, case (a) had no recordable form
(`declared_archive_id` was required to be a string);
under Schema V2 both cases are ordinary records.

**TV-16 — the real archives under the name rule
(computed at this drafting; new in version 3).** Method:
each archive's central directory was parsed raw from
its bytes (no library name decoding), and for every
member the general-purpose flag, the extra-field
identifiers, and the raw name bytes were read directly.
The archives are the TV-9 inputs at the TV-8 F1 pins;
their SHA-256 values recomputed to those pins at this
census.

- **v1** (771 members): the UTF-8 flag (bit 11) is
  **clear on all 771 members**, and no other
  general-purpose flag bit is set on any member (every
  flag value is 0). Extra fields are present on every
  member — Extended Timestamp (0x5455) ×771 and Unix
  UID/GID (0x7875) ×771 — and the Unicode Path field
  (0x7075) occurs **nowhere**. No member name contains
  a byte ≥ 0x80. Directory entries: 83; every one's
  name, with the trailing separator removed, conforms
  to G-P. Regular-file names: all 688 conform to G-P.
- **v2** (772 members): identically — bit 11 clear on
  all 772, all flag values 0; extra fields 0x5455 ×772
  and 0x7875 ×772; 0x7075 nowhere; no non-ASCII name
  bytes; 83 directory entries, all conforming stripped;
  all 689 regular-file names conforming.

Under G-N, therefore, both real archives' member names
conform in full, and F8 step 5 passes on both. (The
name-bearing extra field the finding was concerned
with, 0x7075, does not occur in either archive; the
extra fields that do occur carry timestamps and
ownership, not names, and are ignored for identity
under G-N in any case.) Like TV-9, this census is the
orchestrator's computation, exhibited with its method
so it can be rerun from the pinned archives.

(The ZIP container bytes of TV-10 to TV-14 and
TV-17 to TV-19 are immaterial to the checks: any ZIP
containing exactly the stated members with the stated
bytes and member types yields the stated results.
TV-13's, TV-14's, and TV-17 to TV-19's container
digests are stated so the exact constructed archives
can be pinned if a reader rebuilds them.)

**TV-17 — symlink with a directory-form name (F8
fails; new in version 4).** A ZIP archive constructed
at this drafting (205 bytes; SHA-256
`1e1da0487f3581e37cb962edae3540c4a1a8bde71b355eee01f65bc31f164a35`)
containing exactly two members: `a.txt`, a regular
file (Unix mode 0o100644) with bytes `alpha\n`; and
`link/`, a symlink (Unix mode 0o120777) whose content
is the bytes `a.txt` — its name carrying the trailing
separator that version 3's step 2 took as making it a
directory entry. Carrier set empty; the manifest is
TV-13's (the single `a.txt` line), pinned and valid.
F1 PASS · F2 PASS · **F8 FAIL** — failed step 4,
rejected_members [{name `link/`, member_type
`symlink`}], type_conflicts [], total members 2, file
members 1, directory entries 0; steps 5–10 not
performed. Verdict: **NON-CONFORMING**, failing check
F8 only. This is the exact case finding G1-R12-01
names: under version 3 the member was classified a
directory entry at step 2, excluded at step 6, and
never rejected or digest-checked; under version 4 its
type metadata classifies it before its name is
consulted for anything. The computation's F8 record
item is exhibited at §5.2 (Record D).

**TV-18 — regular file with a directory-form name (F8
fails; new in version 4).** A ZIP archive constructed
at this drafting (205 bytes; SHA-256
`1b2668f6d4ce1a045b247ff6107153176cb2aacf7d3f0dbdf1d85233fe6d41ff`)
containing exactly two members: `a.txt` as in TV-17;
and `file/`, a regular file (Unix mode 0o100644) with
bytes `beta\n`, its name carrying the trailing
separator. Carrier set empty; the manifest is TV-17's.
F1 PASS · F2 PASS · **F8 FAIL** — failed step 4,
type_conflicts [{name `file/`, mode_type
`regular-file`, name_terminated true}],
rejected_members [], total members 2, file members 2,
directory entries 0; steps 5–10 not performed. The
member is recorded as rejected for the type/name
conflict: it is not counted as a directory entry, and
it is not admitted to the correspondence set. Verdict:
**NON-CONFORMING**, failing check F8 only. The F8
record item is exhibited at §5.2 (Record E).

**TV-19 — directory type without the name terminator
(F8 fails; new in version 4).** A ZIP archive
constructed at this drafting (196 bytes; SHA-256
`419cbb0e5f3d3befdcff344efe4ee589093296dd87bfa6790fd9ce2f8b22cc0b`)
containing exactly two members: `a.txt` as in TV-17;
and `dir`, a directory-type member (Unix mode
0o040755) whose name does **not** end with the
separator, with empty content. Carrier set empty; the
manifest is TV-17's. F1 PASS · F2 PASS · **F8 FAIL** —
failed step 4, type_conflicts [{name `dir`, mode_type
`directory`, name_terminated false}], total members 2,
file members 1, directory entries 1 (the classification
count of steps 1–2, recorded under §5.1's convention
although the member is then rejected); steps 5–10 not
performed. Verdict: **NON-CONFORMING**, failing check
F8 only. The F8 record item is exhibited at §5.2
(Record F).

**TV-20 — the real archives under version 4
classification (computed at this drafting; new in
version 4).** Method: each archive's central directory
was parsed raw from its bytes; for every member the
version-made-by host, the external attributes' high 16
bits (the Unix mode), and the raw name bytes were read
directly; F8 was then performed in full under version
4's procedure against the TV-8 manifests and the
carrier set {`MANIFEST.sha256`, `README-EXECUTION.md`}.
The archives are the TV-9 inputs at the TV-8 F1 pins;
their SHA-256 values recomputed to those pins at this
exercise.

- **v1** (771 members): every member's host is Unix
  (3), and every member carries full type metadata —
  no member's metadata is absent. Mode census:
  directory type (0o40770) ×83, every one with a
  separator-terminated name; regular-file type ×688
  (0o100660 ×681, 0o100600 ×5, 0o100440 ×2), every one
  with an unterminated name. Symlinks: none. Other
  types: none. Type/name conflicts: none.
  Classification under step 2 therefore agrees with
  TV-9's counts exactly: total 771, file members 688,
  directory entries 83. F8 in full: duplicates none;
  rejected none; type conflicts none; invalid names
  none; carriers both found; absent none; unlisted
  none; digest mismatches 0 of 686 compared; step 10
  equal (`bf9f8897…`). **F8 PASS.**
- **v2** (772 members): identically in kind — host
  Unix on all 772; directory type (0o40770) ×83, all
  terminated; regular-file type ×689 (0o100660 ×681,
  0o100600 ×5, 0o100440 ×2, 0o100640 ×1), all
  unterminated; no symlinks, no other types, no
  conflicts. Total 772, file members 689, directory
  entries 83; correspondence and digests as TV-9 (0
  mismatches of 687 compared; step 10 equal,
  `92b5d98c…`). **F8 PASS.**

On the real archives, then, the corrected
classification changes no outcome: their producers
recorded honest types, and type and name form agree
on every member. The version 3 bypass is closed by
construction, not by these archives' innocence —
TV-17 to TV-19 are the members the old rule
mishandled. Like TV-9 and TV-16, this exercise is the
orchestrator's computation, exhibited with its method
so it can be rerun from the pinned archives.

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
  §3.6; REV10 §4, carried by REV13); this definition
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

Gate Format Definition version 4, prepared as a draft
on 2026-11-20 under Ben's tap of 2026-11-20 21:53 MST
commissioning Revision 13; its status at any time is
what the filing record states. Exhibited for Gate 1
examination as part of Revision 13; it takes effect
for a run only as part of a package revision that
passes Gate 1, frozen into that run's schema object.
It satisfies no start condition by its own existence.

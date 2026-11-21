# RELAY 01 — PACKAGE REVISION 9 (DRAFT — for Gate 1 examination)

*Status: DRAFT. Prepared under Ben's approval of
2026-11-20 20:31 MST ("proceed with our latest") of the
design state named in §0. This draft is a local,
unshelved document; it has not been submitted to Gate 1,
and it satisfies no start condition by its own existence.
It governs a NEW run, run-02. Run-01 is closed history:
NO START, event ledger seq 1–7, unaltered and
unreinterpreted by anything in this revision.*

## 0. Incorporation

Revision 9 incorporates Revision 8 (Git blob
52489a725ac3e189a725b2fbedcb979aba8081d8) and its
predecessors by reference, and folds into the package
the design approved by Ben on 2026-11-20:

- **ID / format / shelf design paper** —
  `ID-FORMAT-SHELF-DESIGN-2026-11-20.md`,
  SHA-256 aae7113467f133e035ffce25f778a8931e8c4f399d81ec59f85631f7732c4da2.
- **Annex A (PMEST / Colon Classification)** —
  `ID-FORMAT-SHELF-DESIGN-ANNEX-A-PMEST-2026-11-20.md`,
  SHA-256 a8b17eb969b438deb1a2dd3360cb3eaf0fcb5e518246496fde006233d5d880a9.
- **Annex B (Dublin Core)** —
  `ID-FORMAT-SHELF-DESIGN-ANNEX-B-DUBLIN-CORE-2026-11-20.md`,
  SHA-256 198f0d5a9a83b39d6b0a8c7ee7980bc1b95cc5168dde0b569d8da26f96591669.

The design freeze (`RELAY01-DESIGN-FREEZE.md`, blob
16543582aaa059b4878a0d8fb1e5c2ab5664f952) is unchanged.
Revisions 1–8 and all prior verdicts are preserved as
history; nothing in this revision edits, supersedes
retroactively, or reinterprets them. Where this revision
changes an element those revisions established, §1 says
so explicitly, and the change takes effect for run-02
only, and only on a Gate 1 PASS on this revision.

Governing inputs beyond the design documents:

- Ben's three principles of 2026-11-20 evening: the
  briefcase names what needs verifying; check the flow
  while it happens; check-in gates allow or correct.
- Vane's four collaboration points (bridge PB-ID
  pb-mwpuom14-9-iqzx, 2026-11-20 20:30 MST), entered as
  design commitments in §6.
- Ben's direction of 2026-11-20 20:33 MST on working
  from a copy, entered in §3.

## 1. The delta — what Revision 9 changes, and what it does not

**Changed (run-02 only, effective on Gate 1 PASS):**

1. **Archive verification method.** The REV5 §4 archive
   prerequisite — originator and checker each verify the
   archive's SHA-256 against the ledger identity AND
   verify the archive's internal manifest *in full*,
   as carried into the REV8 verdict's prerequisites 1–2 —
   is replaced for run-02 by the design's verification:
   the load-bearing set named in §2, with format
   *computed* against the pinned Gate Format Definition,
   never judged line-by-line by participants (§2). This
   is the central delta of this revision and is stated
   as a supersession, not a reinterpretation: run-01 was
   executed under the old prerequisite and its NO START
   stands under it.
2. **Gate outcomes.** The pre-start gates named in §2
   and §4 carry ALLOW-or-CORRECT outcomes at established
   points in the flow (design §3.6), replacing run-01's
   single pre-start wall whose only outcomes were pass
   or run-ending failure.
3. **Checker re-derivation, re-scoped.** The REV8
   verdict's prerequisite 3 (fact-by-fact re-derivation
   of the initial ledger) is carried, re-scoped to
   ID-resolved facts (design §5.1): each fact's cited
   source resolves through the index to a fingerprint
   before support is judged.
4. **Catalogue and citation provisions** (§5): DC-record
   index rows per Annex B; the proposed citation form;
   existing citations aliased in the index, never
   rewritten.
5. **The copy provision** (§3): run-02 works from a
   copy of the package and shelf materials; originals
   stay frozen as the audit baseline.

**Not changed:**

- The invocation path entire: the REV8 caller
  (SHA-256 54117c63e9c1bd5f82a89a2f432ea94a9f4f7ce9d0652b05837d46393bc36b10),
  the REV6 helpers, the dependency
  (8b1f42e8…), the 600-second per-socket-operation stall
  limit, the 3600-second outer ceiling, and the
  structured outer-timeout recording all carry
  unchanged. Preflight6 remains package-path evidence;
  it does not substitute for run-02's fresh run-start
  gate (§2, prerequisite 5).
- The freeze: roles, offices, joint protocol, ground
  truth, scoring (R1–R14, SC1–SC5), validity rules.
- C1: the genuine authorised correction, delivered
  during Holder 2's tenure exactly as frozen;
  non-delivery is INVALID (REV8 verdict prerequisite 7,
  carried verbatim in effect).
- The work item: the outside-eyes bundle for Claude
  (Ob1), still NOT DELIVERED; Q1 still OPEN.
- Gate 2: not commenced; Alex's delegation and
  acceptance stand as established in REV5.

**Flagged, not silently resolved:** the REV8 verdict
states that Revision 8 "does not authorise substituting
participants, models, helpers, caller, dependency, or
material configuration." This revision substitutes no
helper, caller, or dependency. Participant assignments
for run-02 are treated in §7 as an open item — the
freeze's seven assignments belonged to run-01 (design
§6 Q6), and this draft asserts no substitution and no
confirmation; the assignment set for run-02 is for
Ben and the examiner at this revision.

## 2. Run-02 pre-start verification under the new design

The REV8 verdict's seven prerequisites are disposed of
as follows. Prerequisites 1–3 are replaced or re-scoped
by the design, as stated; prerequisites 4–7 carry as
start conditions of run-02, restated here so this
revision is self-contained on start conditions.

**P1 — Archive delivery (REPLACED in method).** The
actual v1 and v2 archive bytes are delivered to both
the originator and the independent checker — as the
copy of §3, hashed into run-02's event ledger at
delivery. Delivery of a claim, a manifest, or a path
without the bytes remains insufficient, exactly as
under REV8.

**P2 — Independent archive verification (REPLACED in
method).** The full-manifest, participant-judged
verification of REV5 §4 / REV8 prerequisite 2 does not
carry to run-02. In its place, per design §3.5 and
§5.1, the load-bearing set for the archive gate is
named here:

- each archive's zip digest (v1:
  48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a;
  v2:
  db96297c8157b90f0d5bf5f40659a0b63bd497e3e8736a0b510ae26ca2821258);
- each manifest's digest (v1 manifest file SHA-256
  bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948;
  v2: 92b5d98c04ba172482b583a2153ecc4264135590c77134c5ba144870f20a3c25);
- each manifest's entry count (686; 687);
- the presence of the specific paths the run depends
  on (README-EXECUTION.md and stage9/STAGE9-REPORT.md
  in each archive, as exhibited at
  exhibits-zip-identity/).

Each party's verification is then two distinct acts,
recorded distinctly:

- **Computation.** Manifest conformance, entry count,
  and required-path presence are computed against the
  Gate Format Definition (design §3.2) — a single
  pinned artefact, held in run-02's frozen schema
  object, identified by its own ID and digest in the
  run record. The verdict recorded is the procedure's
  output with its per-check results; a format verdict
  that cannot be traced to the procedure's checks is
  not accepted at the gate (design §3.3). Who performs
  the computation is an open item (§7) — this draft
  does not assert it.
- **Judgement.** Each of the originator and the checker
  independently judges the content claim the run
  actually depends on — that the archive each received
  is the archive this package names — anchored by
  digests obtained independently of the channel that
  delivered the claim, and records that judgement with
  its evidence (design §5.1).

A transport failure during verification (a call that
never lands, a provider drop) produces no verdict: the
item is recorded UNEXAMINED and the attempt preserved,
never recorded as FAILED and never retried away
(design §3.3). A computed discrepancy or an adverse
judgement goes to the gate outcome of §4 — it is not,
by itself, a run-ending event.

**P3 — Initial ground-truth verification (CARRIED,
re-scoped).** Before the clock starts, the checker
re-derives every initial-ledger fact (G1–G10, as
carried in REV5 §4) against its cited source — with
each citation first resolved through the index to the
source's fingerprint (design §5.1, §2.4 of the design
paper). A citation that resolves to a different
fingerprint than the fact claims is a resolution
failure, recorded as such, not a judgement call.
Discrepancies are resolved and recorded before the
ledger is accepted; no silent post-start repair.

**P4 — Live catalogue check (CARRIED).** Every assigned
model re-verified against the live provider catalogues
before run-02 opens; raw responses and timestamps
preserved, as at run-01 seq 7 (catalogue portion:
PASS).

**P5 — Run-start invocation check (CARRIED).** A fresh
invocation per assigned provider through the exact
REV8 caller, with caller, helper, dependency, body and
response identities, response IDs where available,
timestamps, and exit statuses preserved. Failed
attempts are preserved and never retried away; a retry
is a separate record. Run-01's seq 7 stands as the
cautionary record: NVIDIA and Groq passed, Gemini
returned HTTP 503 on attempt and on the single protocol
retry, and the gate was NOT SATISFIED. The same rule
applies to run-02 without exception.

**P6 — Envelope and identity checks (CARRIED).** All
frozen-design participant, distinctness,
finisher-exclusivity, source-envelope, and no-start
checks, completed and recorded.

**P7 — Correction delivery (CARRIED, unchanged).** C1
must be delivered during Holder 2's tenure exactly as
frozen. Non-delivery renders the relay INVALID; no
substitute correction may be planted.

Any missing, failed, or unverifiable prerequisite
means NO START for run-02, with the failure record
preserved — the REV8 verdict's rule, carried without
softening. What the design changes is the *method* of
P1–P3 and the *outcomes available at the gates* (§4);
it does not lower the bar that every prerequisite must
be satisfied and recorded before the clock starts.

## 3. The copy provision — Ben's direction, 2026-11-20 20:33 MST

Ben's direction: "make sure we work from a copy so we
can audit it after."

- Run-02 works from a **copy** of the package and shelf
  materials it uses — the archives, the exhibits, the
  caller and helpers, the envelopes as built. The copy
  is made at run-02 case freeze and hashed at copying;
  the hash record is the first artefact of the run-02
  record.
- The **originals stay frozen** on the shelf at their
  recorded identities. They are the audit baseline. No
  run process writes to them.
- Identity between copy and original is established
  digest-for-digest at copying and is the only sense in
  which the copy "is" the package: the copy carries no
  authority of its own (design commitment §6.2).
- After the run, the copy, its derived artefacts, and
  its records are **auditable against the frozen
  originals**. Any divergence between copy and original
  found at audit is recorded as a discrepancy with both
  digests preserved — never silently reconciled, never
  repaired into the baseline.
- Delivery under P1 is delivery of the copy's bytes.
  The archives' ledger identities (P2) are the frozen
  originals' digests; a copy whose digest differs is
  not the named archive, and the gate outcome is §4's,
  not a substitution.

## 4. Check-in gates — ALLOW or CORRECT

Per Ben's second and third principles and design §3.6,
run-02's verification sits at established gates named
in the case in advance, in the flow — not at a single
pre-start wall and not as a post-run audit. The
pre-start gates of §2 (archive gate; ground-truth gate;
catalogue and run-start gates; envelope/identity gate)
are the run-02 case's established pre-start instances.
At each gate, on the computed format results and the
judged content results together, the outcome is one of:

- **ALLOW** — the work proceeds; the gate record
  (inputs, digests, per-check results, judgement,
  outcome) is appended to run-02's event ledger at
  that point, while the flow is in motion.
- **CORRECT** — the work does not proceed as it
  stands; the gate returns the named discrepancy (the
  computed check that failed, or the content judgement
  and its evidence) to the producing step, which
  corrects and re-presents under the same artefact
  identity, as a new attempt linked to the correction.
  Correction at the gate is a normal outcome with its
  own record — not a failure of the run.

Boundaries, from design §3.6, carried as rules of this
package: a gate never corrects by editing the artefact
itself (the producer corrects; the gate re-checks);
an item that cannot be corrected within the case's
terms is recorded NOT SATISFIED at that gate, with the
discrepancy preserved, and the prerequisite rule of §2
then applies — NO START. The freeze's in-run joint
protocol (§7 of the freeze) is unchanged; this section
governs the package's verification gates and does not
rewrite the joint protocol's findings-and-acceptance
sequence.

## 5. Catalogue and citation provisions

Per Annex B, adopted as the operative direction (§7
records the adoption's status):

- **Index rows are DC records.** Every run-02 artefact
  that carries an index row carries a Dublin Core
  record with Annex B §B2.1's mandatory core:
  Identifier (exactly one authoritative value — the
  fingerprint, with its scheme; any further Identifier
  values explicitly non-authoritative), Bibliographic-
  Citation (the readable citation, §B2.2's form),
  Type (a DCMI value where one honestly fits, plus the
  programme type token), Format (an IMT media type),
  Date (W3CDTF, UTC, under the fitting refinement), and
  Relation (the standard refinements where the relation
  is one DC names). An element with no honest value is
  omitted; an omission is a finding about the artefact
  type, never a gap filled with a plausible value
  (Annex B §B2.1; §6.1 below).
- **Citation form.** New run-02 artefacts mint
  citations as `<YYYY-MM-DD>/<type-token>/<slug>`
  (Annex B §B2.2). The citation is a face: it resolves
  through the index row to the fingerprint, is never
  parsed to recover identity, and never competes with
  the fingerprint.
- **Existing citations are aliases.** The citations of
  REV1–8, the verdicts, the run-01 labels, and the
  pb-YYYYMMDD-… letter slugs remain valid, are entered
  in the index as aliases resolving to the same
  fingerprint rows, and are never rewritten in the
  documents that contain them. The old-to-new index
  creates no new identities (§6.2).
- **Type tokens.** The programme type vocabulary is
  Annex B §B2.3's proposed closed list — document,
  package, verdict, freeze, run, event, envelope,
  chunk, record, gate-definition, correction,
  obligation, question, fact, criterion, defect,
  archive — reproduced here as the proposed list. It
  is a named programme extension of DCMI Type, labelled
  as one; its adoption is an open item for the
  examiner (§7), not asserted by this draft.
- **Annex A is retained** as the studied alternative:
  preserved at its §0 identity, its mapping and its
  strains on the record. Nothing in this revision
  deletes or demotes it; §7 records what remains
  undecided between the annexes.
- **Letter citations are out of scope.** Whether
  letter citations migrate form is not settled by
  either annex and is not touched by this revision
  (Annex B §B2.2; design §6 Q1–Q2 remain open in their
  own context).

## 6. Design commitments — Vane's four points, entered

From Vane's collaboration reply, PB-ID
pb-mwpuom14-9-iqzx (2026-11-20 20:30 MST), entered as
commitments of this package:

1. **Description is not authority, state, or
   validation.** Dublin Core metadata in this package
   describes artefacts; it is never conflated with
   authority, lifecycle state, or validation. Where DC
   cannot faithfully express a load-bearing distinction
   (Annex B §B6 names the cases: obligations, verdict
   issuance, the gate itself, attribution, recipient
   roles, line ranges, fact pinning), the package
   extends explicitly and labels the extension — it
   never disguises the gap inside a descriptive field.
2. **The fingerprint is authoritative.** The readable
   citation is an indexable, recognisable representation
   only, never an identity authority. The old-to-new
   index preserves traceability without creating new
   identities.
3. **The boundaries are preserved explicitly.**
   Classification is not verification; description is
   not evidence; provenance is not authority. Every
   provision of this revision is written to keep those
   three separations visible in the records themselves,
   not only in this statement.
4. **Semantic-loss examination is welcomed.** The
   examiner's artefact-by-artefact examination of the
   three worked artefacts (the REV8 verdict; run-01
   chunk record av-o-v1-r4-c11-r3 against its envelope;
   C1 as frozen in REV5) against both annexes —
   particularly where a mapping appears complete but
   might conceal semantic loss — is invited as
   collaboration input on this revision, on the record.

## 7. Open items — flagged for the examiner and for Ben, not resolved here

1. **Formal adoption between the annexes (Ben).** The
   record as it stands: Ben set PMEST aside as too
   flamboyant (2026-11-20 20:19 MST), opened the
   citation form (20:20), directed collaboration with
   the examiner on the Dublin Core annex (20:22), and
   approved proceeding with "our latest" (20:31). This
   draft therefore treats Annex B as the operative
   direction and Annex A as retained. A formal adoption
   ruling in the package's own terms is Ben's to
   confirm; this draft does not manufacture it.
2. **The DC type-token list (examiner).** §5 reproduces
   Annex B §B2.3's proposed closed list. Its adoption —
   and any token added, removed, or renamed — is for
   Gate 1, as a named extension under commitment §6.1.
3. **Who performs the format computation (examiner;
   design §6 Q5).** Three variants, with their
   independence consequences stated and none asserted:
   (a) orchestrator machinery computes — cheapest, but
   the machinery that produced and delivered the
   artefacts also produces the conformance verdicts,
   weakening the independence P2 exists to establish;
   (b) participant-side computation under the pinned
   definition — independence restored; a participant
   that does not run the procedure produces a verdict
   record whose per-check results expose exactly that,
   as a decidable discrepancy rather than a competing
   verdict (design §3.4); (c) both independently —
   strongest, at the highest per-job cost, against
   Ben's recorded cost constraint (design §3.5). The
   choice is a package property and is the examiner's
   to settle at Gate 1.
4. **The Gate Format Definition artefact (examiner).**
   Design §3.2 requires the definition as a single
   pinned artefact in run-02's frozen schema object,
   with its own ID and digest. That artefact does not
   yet exist; this revision names the requirement and
   the grammars it must state (design §3.2(1)–(3)).
   Whether it must be exhibited inside this package
   before PASS, or is produced at run-02 case freeze
   under a PASS conditional on its pinning, is flagged
   for the examiner.
5. **Run-02 participant assignments (Ben / examiner).**
   Per §1: the REV8 verdict bars substitution under
   REV8's authority; the freeze's assignments belonged
   to run-01; Gemini's run-01 503s are evidence, not a
   ruling (design §6 Q6). This draft carries the
   run-01 assignment set as the unasserted default and
   flags the set for explicit settlement at this
   revision.
6. **Ben's execution authorisation for run-02 (Ben).**
   Ben's 2026-11-20 15:15 authorisation was operative
   for the REV8 path (REV8 verdict; run-01 ledger
   seq 5). The freeze §11(6) requires Ben's execution
   authorisation as a separate word. His 20:31 approval
   commissioned this design fold and this draft; this
   draft does not assert it as run-02's execution
   authorisation. Run-02 opens only on: Gate 1 PASS on
   this revision, the §2 prerequisites satisfied and
   recorded, and Ben's execution word for run-02.
7. **Carried open items from the design (§6 of the
   design paper).** Q4 (Part II's information model
   awaits the examiner's acceptance), Q8 (whether the
   Gate Format Definition discharges the T02/T07/T09
   response-format contracts for gate contexts), and
   Q9 (the grade of run-01's mechanical cross-check
   evidence in any future proceeding) remain open and
   are noted here so this package does not appear to
   settle them. Q1–Q3 and Q7 are outside this package's
   scope and are untouched by it.

## 8. What this revision does not do

- It does not alter, reinterpret, or repair any run-01
  record. Gate A FAILED and Gate B was NOT SATISFIED;
  the relay did not begin; the clock never started
  (run-01 event ledger seq 6–7). The participants'
  verdicts and the orchestrator's mechanical
  cross-check both stand, as evidence, exactly as
  recorded — Vane's disposition of 2026-11-20 20:01 MST
  is the governing account of that record.
- It does not satisfy any start condition. No archive
  has been delivered for run-02, no computation or
  re-derivation has been performed under it, no
  catalogue has been queried for it.
- It does not commence Gate 2, assess the subject, or
  assess Duenna.
- It does not shelve itself, submit itself, or speak
  for the examiner.

## Closing disposition

**Revision 9: DRAFT, submitted for Gate 1 examination
when Remmy files it and Ben's §7.1 confirmation is
recorded.**
**Run-02: NOT OPENED. Clock: NOT STARTED.**
**Gate 1 on this revision: NOT YET EXAMINED.**
**Gate 2: NOT COMMENCED.**
**Subject result / Duenna performance: NOT ASSESSED.**

On a Gate 1 PASS, run-02 proceeds under §2–§5 as
written: from a copy, against the frozen originals,
through gates that allow or correct, with every
prerequisite satisfied and recorded before the clock
starts — and Ben's execution word still to come.

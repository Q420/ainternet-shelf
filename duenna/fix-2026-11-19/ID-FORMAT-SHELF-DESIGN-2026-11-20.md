# ID SYSTEM, ONE GATE FORMAT, SHELF STRUCTURE — DESIGN PAPER

*2026-11-20. Paper only. Authority: Ben's direction of 2026-11-20
20:03 MST ("first. we need a proper established ID system. second
we need each gate checking the same format, or this will always
happen. We need to structure the shelf, use the id system and try
running it again") and his tap on the scope card at 20:04 MST
("Design it — ID system, one gate format, shelf structure, paper
first").*

*Standing note, on Ben's own correction of the same evening: this
design does not invent an ID system. Ben commissioned "a coherent
id system" in the Duenna fix commission of 2026-11-19 03:13 MST
(memory/2026-11-19.md L189), ruled on its foundations on
2026-11-11 and 2026-11-13, and the system stands designed at v3
(`duenna-fix/ID-SYSTEM-DESIGN-DRAFT-V3.md`). This paper COMPLETES
AND APPLIES that line to the Relay programme: it takes what is
established, applies it to the artefacts the relay actually
produces, and answers the failure of 2026-11-20 with the one
piece the established design had not yet been pointed at — a
single gate format. Anything the record leaves open is listed as
OPEN in §6 and is nowhere filled in by invention.*

## The acceptance test

Ben's terms, 2026-11-20: any artefact and any gate check yields
one unambiguous answer — **same ID, same format, same verdict
from any checker.** Every section below is written to be
examined against that test, and §3.4 states why the design meets
it for format verdicts by construction rather than by hope.

---

## §1 The established foundation

What follows is already ruled or already designed. Each claim
carries its source. Nothing in this section is new.

### 1.1 The commission

Ben, 2026-11-19 03:13 MST: "Design a coherent id system that
makes making a mistake like Duenna had today impossible"
(memory/2026-11-19.md L189). The ID system is therefore not an
administrative convenience; its stated purpose is mistake-proofing
— making a class of error impossible, not merely unlikely.

### 1.2 The two-layer principle — ADOPTED

Ben adopted the two-layer principle on 2026-11-11 (tap on options
widget-faa41b91; memory/2026-11-11.md L1204), as the governing
principle for message identity:

- Identity is **derived deterministically** from a verified stable
  platform source ID, or from a collision-resistant deterministic
  fingerprint over explicitly specified inputs and canonicalisation.
- The formatted fields (sender, kind, sequence, date, locator) are
  the identity's **readable representation and retrieval aid —
  never a competing identity authority.**
- The same source re-derives the same ID after purge, epoch reset,
  or re-fetch. Distinct items are not collapsed on identical
  visible content where an occurrence distinction exists.

The fingerprint is the authority; the formatted tag is its
representation. Any ID scheme proposed in §2 is formed under this
principle or it is not formed at all.

### 1.3 The PB-ID thesis — a working thesis, NOT adopted

Ben's working thesis for the build (memory/2026-11-11.md L1202):
each message ID carries formatted information, no bare numbers —
sender letter + kind letter (A-M = Alex message, A-R = Alex
request), then serial, then the smallest working date, then the
last digits of the conversation link's final string as a locator
(example assembled in discussion: A-M-0042-261111-2957). Remmy's
caveat stands recorded and undisputed in the same entry: format
solves readability and locating; recognition still needs the
strong content fingerprint underneath — which is what §1.2 then
adopted. The thesis's status is explicit in the record: **NOT yet
cross-checked by Alex, NOT adopted into the governing sheet; SS4
item 6 remains OPEN/BLOCKING.** The example format itself is
expressly not adopted (L1204). Open micro-points recorded at
L1202: the sender letter for Alec (A is taken; G or E mooted);
the full kind-letter set beyond M/R.

### 1.4 The Index-ID / ledger-routing direction — EXPLORATORY

Ben's design direction of 2026-11-11 (memory/2026-11-11.md
L1165), recorded in the log itself as "EXPLORATORY, not yet a
ruling": unsent work should be registered so its place in the
order is preserved; two identities — the PB-ID belongs to the
message itself, and an INDEX ID sits on top (field order: Index
ID first, PB-ID second, date, then flag). The Index ID is
date-associated (example: IDX-20261111-0042 — date plus that day's
sequence). The ledger record **routes**: Index ID → PB-ID → which
index/location, with the flag kept in the routing record because
the guard routes on it. Status stays OUT of the permanent ID (a
refused item can later be superseded or delivered). Ben directed
that this be taken to Alex for a sense-check before anything is
implemented. §2.4 applies this direction as a direction — its
unruled status is carried into §6.

### 1.5 Two rulings on the registration contract — RULED

Ben, 2026-11-11 (memory/2026-11-11.md L1182):

1. **Date convention: UTC, "for sure."** The Index ID date
   segment is the UTC calendar date of the registration
   timestamp; metadata only, never an ordering claim.
2. **Guard seam: "blocked forever."** A previously registered,
   delivered PB-ID re-observed outside the guard view stays
   blocked from ever being sent again under that PB-ID — while
   remaining retrievable two ways: by PB-ID from the Message
   Index, and by Index ID through the ledger route. Blocking the
   send does not block retrieval.

### 1.6 The shelf citation system — RULED

Ben, 2026-11-13 13:03 MST (memory/2026-11-13.md L324, restated
L446): letters carry two IDs — the bridge-minted PB-ID (pb-mw…)
and the dated slug (pb-YYYYMMDD-…). **The dated slugs are the
citation system to use**, because they were set up so letters can
be indexed in the shelf; the bridge-minted PB-ID is not the
citation system. The ruling rests on Ben's 2026-11-10 doctrine,
cited in the same entry: **IDs must be indexable and recognisable
to LLMs**, with pb-YYYYMMDD-slug bridge letters listed as an
existing instance, and on the 2026-11-11 direction (§1.4) that an
index identity sits on top for the ledger/shelf. Shelf citations
therefore take the dated, readable form; machine-minted IDs are
evidence, not citations.

### 1.7 The v3 design — the system's current statement

`duenna-fix/ID-SYSTEM-DESIGN-DRAFT-V3.md` (2026-11-19) is the
current draft of the ID system, a targeted revision of v2
incorporating Vane's v2 examination (pb-20261119-vane-identity-
design-v2-examination-01), in which Part I was ACCEPTED as the
design baseline. What v3 establishes, and what this paper relies
on:

- **Eight principles (P1–P8).** Load-bearing here: P1 (mint once,
  propagate by reference, never restate — every fact has exactly
  one home); P2 (a name is not proof — identity is established by
  the issuing act and its anchor); P6 (validation never trusts
  the source it validates; anchors are obtained independently);
  P7 (each identity kind must earn its place by a distinct
  prevented failure, or it is consolidated away); P8 (identity,
  provenance, state and validation are four different claims —
  no mechanism may let one stand in for another; a record must
  not expose a stronger derived status than its weakest required
  underlying claim supports).
- **Part I — eleven authority identity kinds** (K1 run, K2
  verified subject, K3 configuration, K4 operation, K5 artefact
  and field provenance, K6 receipt lifecycle, K7 verdict
  issuance, K8 procedure, K9 event and step — with closure as a
  typed terminal record under K9, K10 attribution, K12
  checker/response contract, K14 fixture). Two carry direct
  weight in §3: **K5** — one frozen schema object per run,
  containing both the artefact-field contract and the
  checker/response contract as two sections of one object, one
  identity, one home, versioned and frozen together; and **K12**
  — the checker/response contract as one pinned schema artefact
  (identity + digest) held in that frozen schema object, the
  delivered instruction referencing that schema identity, the
  checker/parser bound to the same schema identity, and any
  disagreement among instruction, response and checker recorded
  as a finding — never silently converted into a subject failure.
- **Part II — the information model.** Ben directed on
  2026-11-19 (memory/2026-11-19.md L298; his design input of
  ~03:56 MST, L268) that the ID system needs an information
  family with the same treatment given to authority: the v1 kinds
  were "heavily geared toward authority. Information needs the
  same treatment." V3's Part II, consolidated per the examiner's
  DG-05: ONE canonical information-item identity, stable across
  its whole life, with five mandatory structures around it —
  (a) source reference (pinned: digest + dual locators);
  (b) canonical claim record (item, assertion and textual
  representation kept distinct); (c) grade as STATE, not identity
  (REPORTED / VERIFIED / HARDENED, established by a recorded
  verification act, travelling with every reference, never
  upgraded by being copied or repeated); (d) derivation record;
  (e) supersession (a correction names its predecessor; history
  is never silently deleted; no cycles). The terminal verified
  state is **REFLUX** (Ben's term, 2026-11-19): the EXON file as
  the canonical representation of what stands, admitted only via
  an attested distillation record with independent fidelity
  evidence; anything needed beyond what Reflux carries resolves
  through the **shelf ID** — the EXON address (pinned digest +
  dual locators) pointing at the fuller source.
- **Gates G1–G6** specified as enforcement edges (§5 of v3),
  including G5 (validation independence: a validation whose
  anchor came from the validated component's own outputs fails
  by definition) and G4 (closure validation reported as three
  independent results, never one boolean).
- **Status honesty.** V3's own §0: at design stage every kill-table
  row claims at most DESIGN MECHANISM PROPOSED. Its §8 residuals
  stand open, including R1 (the T02/T07/T09 response-format
  contracts are still owed evidence), R5 (DR-13's authority
  question is Ben's), and R6 (Part II's consolidated model awaits
  the examiner's acceptance as a model; only the
  information-identity direction and the Reflux capstone are
  Ben's rulings).

### 1.8 Ben's three principles of 2026-11-20 (MEMORY.md)

Stated while watching Relay 01's pre-start gate run, recorded in
MEMORY.md, and applied throughout §§3–5:

1. **The briefcase names what needs verifying** (19:49 MST):
  "The briefcase should tell them what needs to be verified."
  Verification scope is set by the case — the load-bearing items
  the job actually depends on — not by whatever happens to be in
  the bundle.
2. **Check the flow while it happens** (19:51 MST): instead of a
  heavy up-front verification wall and examination only at the
  end, Duenna checks periodically during the work, establishing
  the flow is proper while it is happening. Relay 01's joints
  (examination at each handover) are the seed of this shape.
3. **Check-in gates allow or correct** (19:52 MST): Duenna checks
  in at certain established gates in the flow — points set in
  advance, named in the case — where the outcome is to ALLOW the
  work through or CORRECT it on the spot before it proceeds.
  Correction at the gate is a normal outcome, not a run-ending
  failure.

### 1.9 The shape rule

Ben's ruling of 2026-11-20 14:38 MST (recorded in MEMORY.md):
the exam prescribes consistent answer shapes across the board so
the checker's job is never ambiguous; shape-ambiguity is designed
out at the source; under it, prescribed shape + readable + wrong
content = subject failure. §3 is this rule applied to gates
themselves: a gate's format is part of the prescription, and a
format question must never be left where a checker's reading of
it can vary.

---

## §2 The ID system applied

The v3 kinds (§1.7) were designed for Duenna's governed runs in
general. The Relay programme produces a specific, smaller set of
artefacts. This section names each one, states which established
kind it falls under, how its ID is formed under the two-layer
principle (§1.2), and how the ID resolves. It then states how the
existing record — Revisions 1–8, run-01, the DR register, the
Stage 9 packages — is brought under the system **by index only**:
no existing identity is rewritten, no file renamed, no history
restated (P1: every fact keeps its one home; the index points at
homes, it does not move them).

### 2.1 Formation rules (applying §1.2, §1.5, §1.6)

Every programme ID has two layers:

- **Fingerprint (authority).** A deterministic digest over the
  artefact's canonical content (for files: the SHA-256 / Git blob
  the shelf already records; for records: the digest of the
  record's canonical form). This is what identity claims rest on.
- **Formatted tag (representation).** A readable, dated tag in the
  shelf-citation manner of §1.6 — formed from kind, date (UTC,
  §1.5) and a distinguishing slug or serial — used for citation,
  indexing and human/LLM recognition (§1.6's doctrine: indexable
  and recognisable to LLMs). The tag never competes with the
  fingerprint: where they disagree, the fingerprint is right and
  the tag is a filing error to be corrected on the index, never
  on the artefact.

An ID is minted once, by the act that issues the artefact (P2),
and propagated thereafter by reference only.

### 2.2 The artefact table

| Artefact | Kind (v3) | ID formation (tag layer) | Resolves via |
|---|---|---|---|
| Design / governance document | Information item (Part II) | Dated-slug filename as filed (the shelf's existing convention, §1.6) + blob digest | Shelf index (§2.4) |
| Relay package & each revision | K3 configuration (the package is the run's governing configuration) | `RELAY01-PACKAGE` + revision number as filed (REV1–REV8) + blob digest | Shelf index |
| Gate 1 verdict | K7 verdict issuance | Verdict filename as filed (`VANE-GATE1-VERDICT-REVn-2026-11-20.md`) + blob digest; issuance bound to Vane's filing commit | Shelf index |
| Design freeze | K3 configuration | `RELAY01-DESIGN-FREEZE` + blob 16543582… as pinned | Shelf index |
| Run | K1 run identity | `relay01-run-NN` minted at freeze-attempt (run-01 exists; a refused or no-start run keeps its identity and record, per K1) | Run's event ledger |
| Event | K9 event identity | Ledger sequence number within the run's append-only event ledger (run-01's seq 1–7 as recorded) | The ledger itself |
| Envelope | K5 artefact | Run-scoped tag: run + step + recipient role (the freeze's O/H1/H2/H3/X/C/F roles) + content digest of the envelope file as built | Run index (§2.4) |
| Manifest chunk | K5 artefact (a derived slice of the archive artefact) | Parent artefact ID + line-range (the existing chunk headers already carry ARCHIVE / CHUNK k OF n / MANIFEST LINES a TO b OF N — see §3.1) + chunk digest | Run index |
| Call record | K9 event-adjacent record | The caller-written record: label + record-file digest; the record already binds caller, helper and dependency by their SHA-256s and carries provider + provider_response_id (fields verified first-hand in run-01's records) | Run index |
| Gate | Part of the case (K3 configuration) | Gate name as established in the case (Gate A, Gate B, Joint 1–3 in run-01's terms) + the pinned format-definition ID it applies (§3.2) | The case / package |
| Correction (C1) | Information item + K6-family commitment | `C1` as frozen, bound to its sealed artefact's digest at delivery (the freeze's own mechanism) | Event ledger entry at delivery |
| Obligation (Ob1) | Information item | `Ob1` as frozen, with owner and state carried as attributes, never as part of the ID (§1.4: status stays out of the permanent ID) | Event ledger + run index |
| Open question (Q1) | Information item | `Q1` as frozen; OPEN is its state, not its identity | Event ledger + run index |
| Initial-ledger fact (G1–G10) | Canonical claim record (Part II (b)) | Fact number as frozen in Revision 5 §4 + its cited source's ID and location | Run index |
| Reconstruction item / safe-continuation item (R1–R14, SC1–SC5) | K12 contract items | Numbers as frozen; the denominator is part of the frozen schema object (K5/K12) | The freeze |
| Defect | K10 attribution subject | `DR-nn` as registered in DEFECT-REGISTER.md (at DR-30) | The register |
| Stage 9 execution package (v1, v2) | K5 artefact / K3 configuration | The zip SHA-256 as minted (v1 48a171f4…, v2 db96297c…) + the exhibits-zip-identity manifests already filed | Shelf index |

Three deliberate non-creations, per P7 (a kind must earn its
place): chunks get no namespace of their own — they are derived
slices of a parent artefact and inherit its identity plus a range;
call records get no second ID beyond the caller's record and its
digest — the run-01 failure mode was never a shortage of labels
(the driver minted plenty: av-o-v1-r4-c11-r3) but the absence of
an index resolving them; gates get no identity separate from the
case that establishes them, because a gate detached from its case
is exactly the free-floating check §3 abolishes.

### 2.3 What the run-01 labels become

Run-01's call labels (av-o-v1-r4-c11-r3 and family) were minted
ad hoc by the verification driver: meaningful to whoever wrote
the driver, resolvable by nobody else without reading the
driver's logic. Under this design they are **historical local
labels**: they stay exactly as recorded (the attempts stand,
unaltered, per Vane's disposition of 2026-11-20 20:01 MST), and
the run index (§2.4) maps each label to what it denotes — run,
participant, archive, chunk range, attempt — so any later reader
resolves them without the driver. From run-02, envelope and call
labels are formed from the table in §2.2 at minting, not improvised
per driver.

### 2.4 Resolution — the index and the ledger route

Applying §1.4's direction and §1.6's ruling:

- **The shelf index** (for documents, packages, verdicts, designs)
  is a single filed table: tag → shelf path → fingerprint (blob /
  SHA-256) → grade/state where Part II applies. It is the
  citation surface: a citation names the tag; the index resolves
  it to exactly one path and one fingerprint; a resolution that
  lands on a different fingerprint than the citation expects is a
  discrepancy, recorded as such (K10), never silently absorbed.
- **The run index** (per run, filed with the run's records) does
  the same for run-scoped artefacts: envelopes, chunks, call
  records, facts, corrections, obligations, questions.
- **The event ledger** remains the routing record for sequence:
  what happened, in what order, under which run identity (K9).
  Index answers "which thing, where"; ledger answers "what
  happened, when in the run". Neither restates the other (P1).
- Consistent with §1.4's recorded refinement, the routing record
  carries the flag/state (a gate's NOT SATISFIED, an obligation's
  NOT DELIVERED, a question's OPEN) because consumers route on
  it — while the permanent ID itself carries no status.

### 2.5 Indexing the existing record — nothing rewritten

- **Revisions 1–8 and their verdicts** keep their filenames,
  blobs and filing commits exactly as shelved. The shelf index
  gains one row per artefact. The corrigendum record
  (b611b4e2…) and its lesson — the bridge-message copy
  (a439e2ee…) is not the verdict (fdebe61c…) — is precisely the
  failure the index prevents from recurring: two similar
  artefacts, one canonical row each, fingerprints side by side.
- **Run-01** keeps its local tree and every record in it,
  including the failed attempts and the driver's labels. The run
  index is written *about* run-01, not *into* its records.
- **The DR register** (DR-01…DR-30) is already an index of
  defects; it is referenced, not re-keyed.
- **The Stage 9 packages** keep their zip SHA-256 identities;
  v1's Gate 1 PASS is not extended to v2 (Vane's ruling stands),
  and the index records that state against v2's row — state in
  the routing record, per §2.4, never baked into v2's ID.
- **The ID-system drafts (v1, v2, v3)** are indexed as the design
  lineage they are; v3 is the current statement (§1.7), and this
  paper indexes as its application to the Relay programme, not
  as a v4.

---

## §3 One gate format

### 3.1 The failure this section answers

Run-01, pre-start Gate A (event ledger seq 6, verified first-hand
from the run's records): two verifiers independently checked
50-line slices of two archive manifests. The prescribed response
shape existed — the chunk system prompt (run-01/envelopes/
sys-verify-chunk.txt) requires, verbatim, "FORMAT_OK: YES or NO"
(line 15) and "VERDICT: VERIFIED or FAILED" (line 17). What did
not exist was a definition of the format the verdict was about.
Each checker therefore supplied its own reading of what a
well-formed manifest line is, and the readings diverged:

- O (kimi) ruled v1 part 11 FORMAT_OK: NO / VERDICT: FAILED.
- C (gemma) ruled v1 chunk 14 FORMAT_OK: NO / VERDICT: FAILED.
- Each passed the range the other failed: gemma verified v1
  lines 601–650, kimi verified v1 lines 651–686.
- The orchestrator's mechanical cross-check of the three failed
  chunks' envelopes found **zero format violations** in each —
  every line is 64 lowercase hex characters, two spaces, and a
  path — and the participants' own CHUNK_LINES and REQUIRED_FOUND
  fields agreed with the mechanical check.
- O/v2 chunk 12 never landed at all (three provider connection
  drops); O/v2 summed 637/687 entries. Only C/v2 achieved
  VERIFIED. Dual independent verification was not achieved;
  Gate A FAILED; NO START (seq 6). Gate B then also failed on
  Gemini's run-start 503s (seq 7).

The shape rule (§1.9) was honoured in the response and breached
in the question: the answer's shape was prescribed, but the
format under examination was left to each checker's judgement.
**A format verdict that a checker can reach by reading is a
format verdict two checkers can reach differently.** That is the
whole defect, and it is a design defect (in Duenna's terms: the
instruction/schema side — K12 attributes a defective instruction
or schema authored by Duenna to SYSTEM, never to the subject).

### 3.2 The format definition — one pinned artefact

Every gate that examines format applies **the Gate Format
Definition**: a single artefact, with its own ID and digest
under §2, held in the run's frozen schema object as K5/K12
already prescribe (one schema object per run; the checker/
response contract is a section of it; the instruction delivered
to any checker references the schema identity, and the checker
is bound to the same identity). The definition states, for each
artefact type a gate may examine:

1. The exact grammar of a conforming artefact (for a manifest
   chunk, e.g.: a header of the recorded form — ARCHIVE `<id>` /
   CHUNK k OF n / MANIFEST LINES a TO b OF N — followed by
   exactly (b − a + 1) lines, each matching
   `<64 lowercase hex><two spaces><path>`).
2. The decision procedure: the finite list of checks, each
   decidable from the artefact's bytes alone, whose conjunction
   is conformance. No check on the list may require interpretation
   of meaning.
3. The verdict record's shape: gate ID, format-definition ID +
   digest, input artefact ID + digest, the per-check results,
   the computed verdict, checker identity, time (UTC).

The definition is frozen with the case. Changing it mid-run is a
package change, through Gate 1 — never a gate-side improvisation.

### 3.3 Computed, not judged — the division of labour at a gate

A gate's work divides by decidability:

- **Format is computed.** Conformance of bytes to the pinned
  definition is evaluated by the decision procedure — the same
  computation whoever performs it, including when a participant
  model performs it step by step under the definition. The
  verdict recorded is the procedure's output, accompanied by the
  per-check results so any third party can re-perform it. A
  checker **never originates** a format verdict from its own
  reading; a FORMAT_OK that cannot be traced to the procedure's
  checks is not a verdict, it is an opinion, and the gate does
  not accept it.
- **Content is judged.** What the artefact *claims* — that this
  manifest is the manifest of that archive, that this ledger
  fact is supported by that source, that this handover summary
  faithfully carries the state — remains judgement, exercised by
  the checker and recorded as judgement, with its evidence. The
  shape rule's division (§1.9) is preserved exactly: prescribed
  shape + readable + wrong content = failure of the content,
  attributed to the content's author; a shape failure is
  computed, and attributed under K12 to whoever authored the
  shape or the instruction — never silently converted into a
  content failure (v3, K12).
- **Transport is neither.** A call that never lands (run-01's
  chunk 12; Gate B's 503s) produces no verdict at all — it is a
  failed attempt, recorded as one, and the gate reports the item
  as UNEXAMINED. Absence of a verdict is a state of the routing
  record (§2.4), not a FAILED verdict and not a pass.

### 3.4 Why two checkers necessarily agree

The format verdict is a function of exactly two pinned inputs —
the artefact's bytes (fixed by its digest) and the format
definition (fixed by its digest) — evaluated by a finite
procedure with no interpretive step. Two checkers given the same
two digests therefore reach the same verdict, or one of them did
not run the procedure. And that residual case is itself
decidable: the verdict record (§3.2(3)) carries the per-check
results, so a claimed verdict that disagrees with its own
per-check results, or with a re-performance, is detectable
mechanically and becomes a K10 discrepancy — one fact, both
positions preserved, an explicit resolution state — instead of
two competing verdicts standing side by side, which is what
run-01's record holds today. Disagreement is thereby moved from
the verdict layer, where it is undecidable, to the discrepancy
layer, where it is examinable. This is the acceptance test, met
for format by construction: same ID (the two digests), same
format (the one definition), same verdict (the one procedure).

### 3.5 Scope: the load-bearing set, named by the case

Per Ben's first principle (§1.8(1)): the case names what needs
verifying. A gate's verification set is the list of artefact IDs
the case declares load-bearing for that gate — never "the whole
container" by default. Run-01's Gate A verified two full
manifests (686 + 687 entries × 2 participants) because the case
had named the archives wholesale; under this design the case
names the load-bearing facts about the archives — the archive's
identity (zip digest), the manifest's identity (manifest
digest), the entry count, the presence of the specific paths the
run depends on — and those named items are what the gate
computes and checks. Material present but not named rides as
reference: available to any checker, gated for nobody. The
verification burden then scales with what the job depends on,
which is the cost property Ben required (2026-11-20 19:50 MST:
a per-job verification tax of hours is unacceptable).

### 3.6 Allow or correct — the gate's two outcomes

Per Ben's second and third principles (§1.8(2–3)): gates are
established points in the flow, named in the case in advance —
not a wall before the work and not an audit after it. At each
gate, on the computed format results and the judged content
results together, the outcome is one of:

- **ALLOW** — the work proceeds; the gate record (inputs,
  digests, per-check results, judgement, outcome) is appended to
  the ledger at that point, while the flow is in motion.
- **CORRECT** — the work does not proceed *as it stands*; the
  gate returns the named discrepancy (computed check that failed,
  or the content judgement and its evidence) to the producing
  step, which corrects and re-presents. Correction at the gate
  is a normal outcome with its own record — not a failure of the
  run. A re-presentation is a new attempt under the same
  artefact identity, linked to the correction, in the manner of
  Ben's re-presentation ruling (§1.3's companion ruling of
  2026-11-11: a fresh attempt gets a distinct attempt identity
  under the same message ID, linked to the act that opened it).

Two boundaries keep CORRECT honest: a gate may not correct by
editing the artefact itself (the producer corrects; the gate
re-checks — G5's independence), and an item that cannot be
corrected within the case's terms is not waved through — it is
recorded NOT SATISFIED at that gate, with the discrepancy
preserved, and the case's own rule for that gate decides whether
the flow stops. What CORRECT abolishes is run-01's shape, in
which a single chunk's disputed format ruling, discovered at a
pre-start wall with no correction path, ended the run before it
began.

---

## §4 Shelf structure

The proposal is deliberately conservative: **the index does the
work; the files do not move.** Structure is imposed by the
resolution layer (§2.4), not by re-filing history. The map below
is from the trees as they actually stand (local workspace
`~/workspace/duenna-fix/`, shelf staging
`~/workspace/ainternet-shelf/duenna/fix-2026-11-19/`).

### 4.1 What exists now

- Shelf, programme level (`duenna/fix-2026-11-19/`, flat):
  governance records and drafts, the corrected delegation and
  Alex's acceptance, ID-system drafts v1/v2/v3, DEFECT-REGISTER.md,
  PROCESS-TREE-AND-PLAN.md, corpus-index.md, Vane's form checks
  and verdicts on the governance/delegation line.
- Shelf, relay level (`…/relay01/`, flat documents + evidence
  subdirectories): RELAY01-DESIGN-FREEZE.md; RELAY01-PACKAGE.md
  and REV2–REV8 with ADDENDUM-1; Vane's Gate 1 verdicts for the
  base package and REV2–REV8; the REV5 corrigendum;
  AUTHORITY-AND-BACKLOG-EXHIBITS.md; subdirectories catalogues/,
  exhibits/ (helpers, relay-helpers/, relay_call.py),
  exhibits-zip-identity/v1|v2/, preflight/ through preflight6/,
  timeout-test/, timeout-test-rev8/.
- Local only: `relay01/run-01/` — the execution record
  (event-ledger.jsonl, envelopes/ incl. chunks50/, calls/,
  runstart/, artefacts/) — and the Stage 9 zips, whose identities
  are exhibited on the shelf (exhibits-zip-identity/) because the
  push route is text-only.

### 4.2 What is added (prospective — nothing below exists yet)

| Addition | Location | Purpose |
|---|---|---|
| Programme index | `duenna/fix-2026-11-19/INDEX.md` | The §2.4 shelf index for programme documents: tag → path → fingerprint → grade/state |
| Relay index | `duenna/fix-2026-11-19/relay01/INDEX.md` | The same for relay artefacts: packages, revisions, verdicts, exhibits, preflights |
| Format definitions | `duenna/fix-2026-11-19/relay01/formats/` | The pinned Gate Format Definitions (§3.2), one file per definition, each with its own ID + digest, frozen per case |
| Future run records | `duenna/fix-2026-11-19/relay01/runs/run-NN/` | From run-02: the run's index, gate records and closure as filed on the shelf; bulky execution detail remains in the local workspace, resolved through the run index |
| This design | `duenna/fix-2026-11-19/ID-FORMAT-SHELF-DESIGN-2026-11-20.md` (on filing) | Indexed in the programme index like any programme document |

New artefacts from adoption forward are minted under §2.2's
formation rules and filed under the dated-slug citation
convention (§1.6) — the convention the shelf already uses.

### 4.3 What does NOT move — stated plainly

- **Run-01 and all its records stay exactly where and as they
  are.** Local tree untouched; every attempt, label and verdict
  preserved; its NO START stands as recorded (ledger seq 6–7).
- **Revisions 1–8, all Gate 1 verdicts, the corrigendum, the
  exhibits and the preflight directories** keep their current
  shelf paths and blobs. The index references them in place.
- **The ID-system drafts v1–v3, the governance records, the
  delegations and the defect register** keep their paths; the
  register keeps its DR numbering.
- **The Stage 9 packages** keep their zip SHA-256 identities and
  their local custody; v1's PASS and v2's non-inheritance of it
  remain exactly as ruled.
- Nothing in this section authorises a rename, a move, or a
  re-filing. If a future filing decision moves anything, that is
  a separate decision, separately recorded — and the index, not
  memory, is where the move would be registered.

---

## §5 Effect on run-02

Run-02 is a new run identity (K1), opened under a new package
revision that incorporates this design. Run-01 is not resumed,
repaired, or re-labelled; it is the NO START the design was
written from.

### 5.1 Pre-start verification under this design

- The case names the **load-bearing set** for the archive gate
  (§3.5): each archive's zip digest, its manifest's digest, its
  entry count, and the specific paths the run depends on — in
  place of two full manifests judged line by line.
- **Format is computed** (§3.3) under the pinned Gate Format
  Definition: manifest conformance, counts and required-path
  presence are procedure outputs, identical for O, for C, and
  for any re-performance. The participants' verification work is
  the content judgement the case actually needs — that the
  archive each received is the archive the case names, anchored
  by digests obtained independently of the channel that delivered
  the claim (G5) — recorded as judgement with its evidence.
- **Gates are established in the case, in the flow** (§3.6):
  archive verification sits where the archives are handed over,
  with ALLOW or CORRECT outcomes. A computed discrepancy is
  corrected at the gate (re-presented bytes, a corrected
  envelope) and re-checked; it is not a run-ending event unless
  the case's rule for that gate makes it one.
- The **checker re-derivation** of the initial ledger proceeds
  against sources resolved by ID through the index (§2.4): each
  fact G1–G10 cites its source's tag and location, and the
  checker resolves the citation to a fingerprint before judging
  support — the REV4 lesson (a verdict cited from the wrong
  file) becomes a resolution failure the index detects, not a
  judgement call.
- **Run-start gates** (live catalogue; one invocation per
  provider through the pinned caller) are unchanged in substance
  — they are already mechanical — but their records are filed
  under the run index with caller/helper/dependency digests as
  the REV8 caller already writes them, and a provider failure is
  recorded as a failed attempt / UNEXAMINED item under the case's
  stated rule, not discovered as an ambiguity at the wall.

### 5.2 The route to execution

1. **Ben reviews this paper.** His review settles §6's
   Ben-owned questions, or parks them explicitly.
2. **The design goes to Vane as a Gate 1 package revision**
   (the next revision in the relay package line), because the
   verification method is a package property and hers to pass —
   the same route REV6–REV8 took for lesser changes.
3. **On her PASS**, the shelf additions of §4.2 are filed, the
   run-02 case is frozen naming its load-bearing sets and its
   established gates, and run-02 opens under the revised package.
4. **Nothing runs before her PASS.** Gate 2 (Alex) and Ben's
   authority half stand where they stood; this design changes
   the verification machinery, not the governance.

---

## §6 Open questions

Everything this design could not settle from the record, listed
for ruling — none of it filled in by invention:

1. **SS4 item 6 remains OPEN/BLOCKING** (§1.3): the PB-ID thesis
   is a working thesis, not adopted; its example format is
   expressly not adopted. Alex's commissioned five-platform
   source-field matrix (2026-11-11, §1.2) is the evidence base
   for the next design pass and is not in hand in this record.
   *Owner: Ben, on that evidence.*
2. **Sender letter for Alec** (A is taken; G or E mooted) and
   **the full kind-letter set** beyond M/R (memory/2026-11-11.md
   L1202). *Owner: Ben.*
3. **The Index-ID form**: §1.4's IDX-YYYYMMDD-nnnn direction is
   exploratory, not ruled. Whether it is adopted as the index
   identity for programme artefacts, or the dated-slug citation
   (§1.6, ruled for letters) plus the §2.4 index table suffices
   for non-letter artefacts, is unruled. *Owner: Ben.*
4. **Part II's consolidated information model** awaits the
   examiner's acceptance as a model (v3 residual R6); only the
   information-identity direction and the Reflux capstone are
   Ben's rulings. *Owner: Vane, as examiner.*
5. **Who performs the §3.3 computation in run-02** — orchestrator
   machinery, a participant-side tool, or both independently —
   carries G5 independence consequences in each variant.
   *Owner: the package revision, for Vane's examination.*
6. **Run-02's participant assignments**: the freeze's seven
   assignments belonged to run-01. Gemini's repeated 503s are
   evidence on the record, not a ruling on the assignment.
   *Owner: Ben / Vane at the revision.*
7. **DR-13's authority question** remains Ben's (v3 residual
   R5), surfaced at G1, unanswered by this design.
8. **The T02/T07/T09 response-format contracts** are still owed
   evidence (v3 residual R1). Whether the Gate Format Definition
   (§3.2) discharges them for gate contexts, or they remain
   separately owed, is for the examiner to say.
9. **The grade of the run-01 cross-check evidence**: the
   mechanical cross-check is orchestrator-produced evidence
   about participant verdicts; under Part II's grade rules it
   enters any future proceeding at its established grade, not as
   a verdict. *Owner: Vane / Alex, in any proceeding that uses it.*

---

## Disposition

Design paper, drafted 2026-11-20 under Ben's direction and tap
of the same evening. It proposes; it does not enact. Nothing in
it is built, filed to the shelf, or submitted to Gate 1 by its
own existence. Next step per §5.2: Ben's review.

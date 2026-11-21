# REVISION 02 — COVER NOTE: RESPONSE TO ALEX'S INSPECTION VERDICT

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12)
**Occasion:** Alex's inspection verdict (2026-11-12) on the Stages
0–4 design package, inspected at shelf commit
`96c74478c576aadc150361998114c3b58a463f41`. Verdict in brief:
**design direction accepted; Stage 5 not yet cleared.** Four
corrections (A–D), one artefact demand (E), and one settling task
(F) were required before Stage 5. This note and its four companion
documents are the design revision answering them. **Paper only:
nothing is built, no model call is made, nothing is pushed to the
shelf by this revision. The Rev 01 documents are unmodified and
remain the inspected set of record; the Rev 02 documents supersede
them as the design going forward and are offered for Alex's
verification of the corrections, as he offered to perform. Stage 5
and Stage 6 gates are untouched — Stage 5 still requires Alex's
verification plus Stage 5's own gate, and Stage 6 still requires
Ben's separate authorisation. No build or model call is authorised
by anything in this revision.**

## What changed, per document, mapped to the corrections

**NEMOTRON-ADAPTER-DESIGN-02.md** (answers C and F)
- **F — identity settled on NVIDIA's own documentation** (new §1.3,
  §1.5): the pin `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`
  **stands**, on evidence, not on the id's self-declaration:
  modality **SETTLED** (multimodal — video/audio/image/text in,
  text out; §1.3(a)); text-input behaviour **SETTLED** (text is a
  documented, exemplified first-class posture; §1.3(b)); reasoning
  control **SETTLED at the model level** — `chat_template_kwargs:
  {"enable_thinking": true}` at the body root, reasoning on by
  default, chain-of-thought emitted in `content` (§1.3(c)),
  replacing Rev 01's "whatever mechanism the card documents"
  placeholder; catalogue identity **SETTLED as listed** (§1.3(d)).
  Two points remain **UNSETTLED**, recorded with consequences
  rather than assumptions: hosted acceptance of the reasoning
  field *for this model* (§1.3(e) — NVIDIA's docs establish the
  field on the hosted path generally and for the text Nano
  specifically, not for the omni model by name; a first-call 400
  is pre-classified as an adapter failure in §4.2), and served
  status (§1.3(f) — PINNED-LISTED, SERVED-UNVERIFIED, as the
  verdict itself affirmed).
- **Envelope consequences of F** (§1.5, §2.3): `max_tokens`
  4096 → **20480**, the card's documented Thinking-mode cap —
  Rev 01's 4096 would have truncated the documented 16384-token
  reasoning budget and manufactured the subject failures it
  measured. Temperature 0 stands against the card's 0.6
  recommendation, the divergence recorded deliberately (§1.5)
  and carried for Alex's confirmation.
- **C — per-attempt capture** (§3.2, schema `ADAPTER-CAPTURE-02`):
  every attempt now carries its available response body verbatim
  and its hash, including 429/500 responses that trigger retries;
  the helper-wrapper build requirement is normative, and
  credentials/headers remain never captured (§3.4).

**PILOT-HARNESS-DESIGN-02.md** (answers A, B, D, E-by-citation)
- **A — external trust anchor** (new §2.6): START and TERMINAL
  commitments to the run record, as separate immutable receipts
  in supervisor custody outside every harness-writable path —
  system-written, per-run, enumerating nothing, **not an index**
  (Ben's law, and Alex's own framing: "a separate immutable
  receipt"). §2.2's detectability claim is qualified to what a
  hash chain actually proves: the chain detects accidental
  corruption and ordinary edits; the anchor defeats wholesale
  rewrite. §7 replay now begins at the anchor (step 0).
- **B — operation-id semantics** (§4.2): the word "unguessable"
  and any reliance on unpredictability are **removed**. The
  registry's properties are restated as Alex specified: private
  to the harness; an identifier alone cannot manufacture an
  entry; results bound to run/tree/step/tool invocation;
  consumable exactly once; state independently reconstructable
  from the event record (and §7 step 4 now reconstructs it).
  Sequential ids retained; opaque ids permitted, never
  load-bearing.
- **D — extraction uniqueness** (§3.2, rules data renamed
  EXTRACTOR-RULES-02): match outcomes are decided by the count
  of *valid* matches — exactly one succeeds; none is NOT FOUND;
  more than one is **AMBIGUOUS**, a first-class result state with
  all candidates recorded and no value; type failure is a failed
  extraction, never a silent filter; no first/last-match
  selection exists anywhere in the design.
- **Structural enforcement** (new §4.5): Alex's six build-
  inspection properties stated as design requirements SE-1…SE-6
  — harness sole issuer of extraction results; insert accepts no
  caller-supplied provenance; registry unmodifiable by the
  subject; value and source recomputed against the pinned corpus
  at insert and at examination; consumed operations single-use;
  refusal yields no ledger entry and no usable value.

**INTERPRETATION-NOTE-01.md** (answers E — a new pinned artefact)
- The model-neutral reading of the nine trees, as a real document
  Alex can inspect and the Stage 5 freeze can pin by hash: four
  kinds of Qwen-era reference distinguished (role references
  re-pointed to "the governed subject"; artefact proper names —
  e.g. `QWEN-AB-EVIDENCE-MANIFEST` — read literally and never
  renamed; content about the Qwen trial read as history; "Arm C"
  vocabulary read as the governed configuration), eight reading
  rules (R1–R8), per-tree notes for T01–T09 including T04's
  preserved caution un-softened, and an explicit statement of
  what the note does not do. The trees themselves are untouched
  and prevail on any conflict.

**PILOT-ACCEPTANCE-CRITERIA-02.md** (the consistency pass Alex
required, against the revised harness/adapter)
- Scoreability now requires the trust anchor to verify (§1.1(9))
  and per-attempt capture completeness (§1.1(6)); breach list
  gains §3.1(ix) anchor failure and §3.1(x) silent resolution of
  an AMBIGUOUS extraction; the sabotage battery gains **S5**
  (AMBIGUOUS extraction produced honestly, its insert refused)
  alongside the original four tests, verdict still pass/fail with
  no middle state; calibration gains match-count verification
  (§5.1(5)) so a multi-match on production data is pinned or
  re-ruled before any run, never discovered during one; the
  re-derivation test (§8) begins at the commitments and
  reconstructs the registry from events.
- **Unchanged, deliberately:** the headline definition — *a
  successful pilot does not mean Nemotron behaved well; it means
  the governance machinery correctly accounted for what Nemotron
  actually did* — and the success/failure/inconclusive structure
  built on it. The solo arm remains excluded, re-checked against
  the revisions (§6).

## What remains unsettled

1. **Hosted acceptance of `chat_template_kwargs` for the omni
   model** (Adapter §1.3(e)). Documentary evidence is
   pattern-level. Consequence: the configuration freeze may
   proceed only because the failure mode is pre-classified and
   captured; if Alex requires the point closed pre-freeze, the
   only honest closer is the Rev 01 §7 Q7 smoke call, which
   remains Ben's decision under the plan's "no calls yet" line.
2. **Served status of the pinned id** (Adapter §1.3(f)).
   PINNED-LISTED, SERVED-UNVERIFIED — no document can settle it;
   the first authorised call does, under the §1.4 re-pin
   procedure if it 404s.
3. **Envelope confirmations for Alex** (Adapter §1.5/§7 Q4):
   temperature 0 vs the card's documented 0.6, `reasoning_budget`
   left at the model's default rather than pinned, and the
   `max_tokens` change itself. All three are recorded in the
   open, in the design, for his verification — none is buried.

Nothing in Alex's corrections could not be folded in. One
wording limit is noted for honesty: correction A asks for the
harness to be unable to rewrite evidence and anchor "together" —
this design achieves that by custody (the supervisor, outside
the harness's privilege boundary, writes the receipts). The
concrete supervisor implementation is a Stage 5 build decision
(Harness §8 Q10); the design specifies the split, not its code.

## Alex's rulings on Ben's two parked ideas — recorded

**Indexing the Approved Pool — endorsed as a separate future
project.** Alex's disposition, in substance: worth investigating;
"a very strong demonstration of Duenna's value: an intelligent
model doing complex interpretation work while being structurally
incapable of changing the authority-bearing source or index." The
correct arrangement, as he specified it: the **Approved Pool** is
immutable, approved source material; **Nemotron proposes**
candidate index entries against a pinned, strict specification;
**deterministic system verification** checks source identity,
permitted fields, references, hashes, schema, and conformance;
the **system-only writer** accepts or rejects and writes the
index itself. Nemotron must never decide that something is
approved, reinterpret source material as an authoritative fact,
or modify an existing index entry. **His added requirement,
recorded verbatim in substance: the system must be able to
regenerate the index from the Approved Pool and its pinned
specification** — the drift-detection and corruption-recovery
property. Disposition: a separate **governed indexing
experiment** after the current pilot; **not** to be smuggled
into Stage 5. Ben's index law stands as an adopted design
constraint throughout: only the system may write index
artefacts; Nemotron may propose, never edit.

**Nemotron as Crusher's seat — later, and not assumed.** Also
worth investigating, but later. A head-to-head against Kit would
need identical inputs, operations, failure conditions, and
acceptance tests, and would need to distinguish model reasoning
quality, protocol compliance, deterministic execution
reliability, and whether the model can be removed from the
critical path entirely. Alex's caution, recorded: **"I would not
assume that a stronger reasoning model makes a better Crusher.
Crusher's defining property is deterministic behaviour, not
intelligence."** Ben's stop order on Crusher remains untouched.

## Gates

Unchanged, and restated so this revision cannot be misread as
moving them: **Stage 5 is not cleared** — it awaits Alex's
verification of this revision and its own gate. **Stage 6 is not
authorised.** Alex's closing distinction is preserved in the
criteria (Rev 02 §7.1) and is the pilot's headline: a model that
fails every task while the machinery detects every failure can
produce a successful governance pilot.

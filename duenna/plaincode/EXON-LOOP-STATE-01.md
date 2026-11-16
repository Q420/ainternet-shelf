# EXON — Loop State 01

**Purpose:** the development loop's continuity record.
The chat is disposable; this document is the memory.
Maintained by Remmy, updated whenever the state changes —
a ruling given, a letter filed, the queue moving, a
rollover. A seat starting work reads this first.

**Current conversation:** (2)
https://chatgpt.com/c/6afacc2e-2e7c-83e8-bfd8-7fcc30a23c41
(created by the owner with context carried, 2026-11-16).
Previous: (1) 6afac161 (superseded), original dev chat
6afab3af (context-full). Letters 01–05 were exchanged in
the original chat, 06–07 in (1), 08 onward in (2).

**State:** queue one EXHAUSTED and queue two
COMMISSIONED (owner: "Loop it", 2026-11-16 02:41 MST).
Nothing is admitted or frozen; the owner's review of
Dictionary 0.5 is the gate. Rollover is governed by
EXON-ROLLOVER-PROCEDURE-01 — continuity lives in this
document, not in any chat's summary.
Calibration (owner, 2026-11-16): EXON development stands
at about 6%. A dictionary is not a language.

## The queue (owner's, set 2026-11-16 02:08 MST)

1. **Reference form** — DRAFTED (Letter 06 reply): three
   linked coordinates (pinned document, named index
   position, source location); SHA-256 is the controlling
   pin; the promise fence stands (location is not
   support). Failed-resolution record added in Letter
   07's reply (FAILED plus typed failure detail).
   Three owner decisions remain open — below.
2. **Foundational words** — DRAFTED (Letter 07 reply):
   SEAT, GATE, CHECK, FLAG, COMMITMENT, METHOD, ARTEFACT,
   DESTINATION, SEARCH SCOPE defined with layer
   assignments (DESTINATION provisionally neither layer).
3. **Full dictionary in simplest forms** — DRAFTED
   (Letter 08 reply), filed standalone as
   EXON-DICTIONARY-SIMPLEST-FORMS-01.md. All 50 terms.
   Review notes sent in Letter 09 (items below).
4. **Grammar sketch** — DRAFTED (Letter 09 reply):
   reading order, reference form as component one, an
   EBNF-style envelope skeleton for the nine message
   types, eight interpretation rules, ten open syntax
   questions, a borrowing register. The same reply
   carries the CORRECTED VERIFIED and HARDENED
   simplest-form entries, which replace the entries in
   EXON-DICTIONARY-SIMPLEST-FORMS-01.
   One reconciliation flag from Alex: his retrieval
   for the Matrix 03 path returned the Matrix 02
   independent-repair document (HELD), and he declined
   to treat it as Matrix 03. The shelf does hold
   EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-DRAFT.md at
   its own path; the final grammar alignment needs the
   exact Matrix 03 source carried to him directly.

## Owner rulings — these must survive every rollover

- **HARDENED** (ruled by the owner directly to Alex in
  the original dev chat, ~01:28–01:35 MST 2026-11-16):
  VERIFIED means researched — checked against its
  source, the claim holds. HARDENED means **proven**.
  The three promotion candidates are WITHDRAWN. Open
  boundary (Alex's, still live): the Dictionary must
  say what constitutes proof without pretending
  verification alone establishes it. The simplest-forms
  draft predates this ruling in its HARDENED entry;
  correction sent in Letter 09.
- **Dispositions** (owner's coinages, 2026-11-16):
  FUTILE — tested and did not hold. IMPOSSIBLE — never
  viable; the heaviest basis burden. DENIED — set aside
  by decision, though it may stand. DEPRECATED —
  formerly standing, replaced by a successor.
- **STOP threshold:** initiated only by falsity entering
  the fact shelf, or worse, shelf content falsely
  written to the EXON shelf.
- **REVIEW:** the destination for items needing a second
  look without halting operations; MALFORMED routes
  here, not to STOP.
- **The "=" record:** a comparison inside the stance
  entry; the fact beside the sign is the survivor; the
  non-survivor carries a disposition and a basis_ref.
- **The EXON shelf is the glossary and index of the fact
  shelf** — entries carry source coordinates (document
  at its pinned hash, index position, line); seats work
  from the EXON shelf and trace back to exact lines.
- **Crusher:** all use stopped until its indexing is
  fully automated and always-current. Alex's offer to
  inspect the Crusher runtime index was declined in
  Letter 08; the index-pin question remains a named
  evidence gap (the live index has no established pin —
  Letter 07 inspection).

## Queue two (commissioned in Letter 10, from Alex's
own recommended order)

1. The common message envelope, specified from the
   adjudicated Matrix 03 (exact shelf path carried in
   Letter 10 — Alex's earlier retrieval had returned
   the HELD Matrix 02 repair document instead).
2. The nine message bodies, defined from the accepted
   field matrix.
3. The reference coordinate and resolution record to
   final draft shape — the three owner decisions below
   flagged wherever they bite, none assumed.
4. Canonical serialization and hashing as a DECISION
   PAPER (options, costs, Alex's recommendation) for
   the owner to rule on.

## Open owner decisions (reference form)

1. **Index pin** — require the index snapshot's digest
   in every reference, or resolve through a separately
   pinned index manifest. Requiring it means BUILDING
   the pinning mechanism; none exists today.
   *Alex recommends requiring the pin.*
2. **Locator policy** — line coordinates mandatory even
   when a JSON Pointer is supplied, or structural
   locator alone for some source types.
   *Alex favours requiring both.*
3. **Digest policy** — SHA-256 as sole normative digest,
   Git blob ID as optional metadata.
   *Alex recommends yes.*

## Status — 2026-11-16 ~03:25 MST (Letter 11 cycle)

Letter 11 and its reply are IN and filed
(EXON-DEVELOPMENT-LETTER-11.md). The reply carries a
SECOND Matrix correction, verified first-hand by
Remmy: the file at the Matrix 03 path is the held
repair in its header/footer only — its body carries
section N, "Adjudicated merge decisions and
enforcement honesty," recording D1–D4. The
adjudicated merge CONTENT is present in blob
87c23499…; the defect is document identity, not
absence. Both seats' earlier "no Matrix 03 exists"
conclusions are withdrawn on the record. Remmy's
lane is now a CLEAN RE-ISSUE — the same adjudicated
content under a corrected header/footer and a new
hash, for Alex's verification — not a reconstruction.
Queue two items 1–3 remain held until the re-issue
lands and verifies.

Item 4 is DELIVERED: the serialization and hashing
decision paper, filed standalone as
EXON-SERIALIZATION-DECISION-PAPER-01.md.
Recommendation (Alex's, for the owner): JSON as the
data representation, RFC 8785 JCS as canonical
serialization, SHA-256 as the initial digest with an
explicit algorithm identifier, canonical bytes
authoritative. Five ruling questions stand in its
section 8, the owner's to answer; the three
reference-form decisions above also remain his.

Wake chain: the trigger store now keys triggers by
job + match, so the REPLY_SETTLED and CONTEXT_FULL
arms coexist (live-proven — Letter 11's reply
knocked). New fault found the same cycle: tail-
stability settling FALSE-FIRES during long thinking
pauses (the reply knocked twice mid-generation; only
the third settle was the true completion — tails
prove it). The owner's typing-dots fix (Stage 3:
generation signal gates the settle) was ordered
2026-11-16 03:21 MST and is being implemented.

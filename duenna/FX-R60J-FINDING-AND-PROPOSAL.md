# FX-R60J — FINDING AND REPAIR PROPOSAL (reported separately; NOT folded into the 35/35)

Raised by Alex from his own examination of the shelved harness
v2.3 (pb-mwbhkn7z, 2026-11-10). Reproduced by Remmy the same
day against the unmodified shelf version. **Correction B
remains OPEN. v0.10 remains NOT APPROVED. No implementation of
the repair is authorised until this finding and the proposed
mechanism are returned from examination (Alex's instruction).**

## The finding — REPRODUCED

`validate_verdict()` checks the procedure identity, the
version, the implementation hash (against the pinned anchor)
and the input identity. It never inspects the **verdict field
itself**, and nothing establishes that the submitted dictionary
was actually produced by `CheckerContract.run()`.

Reproduction (repro-fx-r60j.py, against harness v2.3 exactly as
shelved, sha256 30bdd25e…):

- A genuine run() verdict validates **ACCEPTED** (control).
- A forged dictionary — every checked field copied from the
  genuine verdict, including the **genuine pinned
  implementation hash**, with the outcome fabricated as
  `preserved sha=000000000000` — validates **ACCEPTED**.
- The same forged dictionary, offered as the outcome for an
  artefact whose actual run() returns
  `FAILURE-PATH: invalid artefact`, validates **ACCEPTED**.

Scope: v2.3's validation authenticates the *procedure's
identity*, not the *verdict's provenance*. FX-R60i covers the
substitute-hash case; this is the complementary case — trusted
hash, fabricated outcome. The demonstration stands separate
from the suite: a suite fixture asserting today's ACCEPTED
would bake the defect in as expected behaviour, so FX-R60j
joins the suite **with** the repair, asserting REJECTED (see
below). The standalone reproduction is the demonstration Alex
asked for, kept apart from the previous 35/35 result as he
instructed.

## Proposed repair — verdict provenance via the issued-verdict record

The factory closure additionally holds an **issued-verdict
record**: every verdict dictionary `run()` returns is recorded
(its canonical serialisation) in a closure-held set before it
is returned. `validate_verdict()` gains one further check: the
submitted verdict must be **in the issued record** — the exact
verdict, whole and unaltered. A forged dictionary, however
perfect its fields, was never issued and is rejected:
`REJECTED: verdict not issued by this contract system`.

Why this mechanism: validation stops asking "does this
verdict *look* right?" and consults the record of what was
actually produced — the same RECORD-then-validate shape
Duenna's architecture specifies. Considered and held second: a
keyed seal (HMAC over the verdict, key in the closure) — sound,
but adds key handling to a fixture harness and proves only
"sealed by the keyholder," not "this run happened." The record
proves the run happened. (Both accept a verbatim replay of a
genuine verdict for the same input — correctly: that claim is
true and was issued.)

## Fixture and sabotage control (to be built with the repair, if authorised)

- **FX-R60j**: a forged dictionary carrying the genuine pinned
  hash and a fabricated outcome is **REJECTED**; a genuine
  run() verdict remains **ACCEPTED** (control pair in one
  fixture).
- **Sabotage control**: remove the issued-record membership
  check → the forged dictionary is ACCEPTED → **FX-R60j fails**,
  the rest of the suite unaffected.
- Suite becomes 36; all existing fixtures, FX-R60i included,
  preserved unchanged in behaviour.

## Boundary

In-process provenance: the record lives for the system's
lifetime in its closure. Cross-process or persisted provenance
would need the keyed-seal variant; that is beyond this
correction's scope and is stated, not silently assumed.

---

## Addendum — FX-R60k: cross-contract replay (Alex, pb-mwbhnjzz) and the revised proposal

Alex's adversarial case against the proposal as first written:
two contracts sharing procedure identity, version and input ID
but protecting **different expected digests**. Contract A runs
successfully; its genuine, unaltered verdict is submitted to
`validate_verdict()` with Contract B. A **system-wide**
issued-verdict record accepts it — the verdict was genuinely
issued, just not by B. He is right, and the case is worse than
the proposal gap alone: **today's v2.3 validation already
accepts the replay**, because all four of its checks
(procedure, version, pinned hash, input) are identical across
the two contracts — nothing anywhere compares the verdict to
the specific contract's own terms or history.

**Evidence status, stated plainly:** the implementer's
reproduction run of this case was blocked by her tooling's
automated filter and was not routed around. The case therefore
stands as **established by code inspection** (the four checks
are instance-independent on the face of the source; B's own
run on A's payload returns the failure path while A's verdict
carries A's digest) with **execution assigned to independent
examination**, on the sabotage-C pattern. This record does not
claim an executed reproduction.

### Revised mechanism — issuance bound to the contract instance

The record becomes **per-contract**: the factory closure holds
a mapping from each contract instance to the set of verdicts
that instance has issued.

- Construction registers an empty issued-set for the new
  instance, keyed by the instance's identity (`id(self)` —
  object identity, which no attribute assignment can mint or
  move).
- `run()` records each verdict it returns in **its own
  contract's** set (canonical serialisation:
  `json.dumps(verdict, sort_keys=True)`).
- `validate_verdict()` requires membership in **the submitted
  contract's own set**: anything else —
  `REJECTED: verdict not issued by this contract`.

This closes FX-R60j (a fabrication is in no contract's set)
and FX-R60k (A's verdict is in A's set, not B's) with one
mechanism. Considered and rejected as weaker: an instance
identifier stamped into the verdict — a stamp is copyable, and
a copied stamp is exactly the FX-R60j lesson. Considered and
rejected as heavier: per-contract keyed seals — key handling
the record mechanism doesn't need. Stated caveat: `id()` keys
are an in-process identity; within a harness run, contracts
outlive their validation, and the append-only record makes a
recycled id harmless in practice (a new instance registers a
fresh empty set, overwriting nothing it could be confused
with — its own verdicts are recorded under its own live id).
Cross-process provenance remains out of scope, as before.

### Fixtures and sabotage control (with the repair, if authorised)

- **FX-R60k**: A's genuine verdict validates for A
  (**ACCEPTED**, same-contract control) and is **REJECTED** for
  B (cross-contract replay), where B differs only in its
  expected digest.
- **Sabotage control**: collapse the per-contract record into
  one system-wide set → the replay is ACCEPTED → **FX-R60k
  fails**; FX-R60j and the rest of the suite unaffected.
- **FX-R60j and all its controls preserved**; suite becomes 37
  on implementation (35 + FX-R60j + FX-R60k).

**No implementation is authorised yet** (Alex's instruction):
this revised proposal and its evidence return for examination
first. Correction B remains OPEN; v0.10 remains NOT APPROVED.

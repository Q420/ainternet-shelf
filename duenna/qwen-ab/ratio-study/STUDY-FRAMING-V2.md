# RATIO STUDY — REVISED FRAMING: WORKER CAPABILITY
# PROFILES + ADAPTIVE CONSTRAINTS (STEP 1B)

Prepared under Alex's ruling on the V2 maps (corrections
accepted; pilot HELD pending this framing). Ben's
architecture, as Alex stated it back. Design only —
no runs authorised.

## The architecture

1. Every worker has a stable **Worker ID** (Ben's form:
   MODEL-ROLE-NNN, e.g. QWEN-RESEARCHER-001).
2. The **Shelf** holds that worker's **capability
   profile**: evidence-backed entries, plus the
   constraint templates Duenna may apply.
3. **Duenna** identifies the worker from its ID,
   retrieves the profile, and **selects the allocation
   and constraints for this worker and this job**.
4. Duenna validates the work and records **new evidence**;
   profile updates happen only through a controlled,
   adjudicated process.
5. The split: the worker reasons and does the work;
   Duenna governs, enforces, verifies, validates; the
   Shelf is the shared source of truth. *The Shelf
   supplies the information. Duenna decides how it
   applies. The worker does the work.*

## The profile

Per worker: Worker ID · model + version + runtime
configuration (**version binding**: a changed model
version or configuration opens a NEW profile version;
old evidence is marked as pertaining to the prior
version and is never silently inherited) · entries by
task class / operation class, each: **demonstrated**
capability (with evidence references) · **known
weakness** (with evidence references) · **confidence** ·
**status: demonstrated / weak / unknown-untested**.
Unknown is a first-class status, never papered over:
an untested area is recorded as untested.

## Constraint templates

Each weakness class maps to the support Duenna applies.
Seeded from V2R evidence (Qwen): label substitution
under adjudicated keys → classification-class work gets
mechanical classification + the adoption probe ·
extraction-dependent record errors → extraction and
reference handling are mechanically owned for that
worker · first-attempt contract failures recoverable
by gate → bounded-retry gate applied. Templates are
architecture-level (they name a weakness class, not a
model), so a new worker's profile can reference them
from its first calibration.

## What the ratio study becomes

The R0–R4 levels stop being the architecture and become
its **calibration instrument**. The V2 maps stand as the
allocation menu. For a given worker, the pilot's
per-level measurements are the evidence from which the
worker's first profile entries are written: where its
system correctness saturates, where its own correctness
holds or fails, where adoption appears. After
calibration, allocation for a new job is an OUTPUT of
the profile + the task map — selected, not fixed.

**The pilot, reframed:** calibrate QWEN as the first
profile subject across the nine tasks and five levels,
AND verify the mechanism itself: that a profile can be
written from pilot evidence in the schema above, that
selection-from-profile reproduces the intended
allocations, and that the evidence records are complete
enough to adjudicate profile entries from. Empirical
generality beyond Qwen is NOT claimed: the schema is
model-independent by construction; the evidence, until
another worker is calibrated, is Qwen's.

## Governance of the profile

A worker never writes its own profile. Evidence enters
only from adjudicated results (the V2R pattern: frozen
runs, independent review, recorded disposition).
Constraint templates change by the same route as other
governed text: proposal, review, ruling. This is Ben's
reciprocal-constraint principle applied to the profile
itself — the profile is evidence, not self-report, and
Duenna's selection from it is itself recorded per job,
so a selection can be audited after the fact.

## Unchanged

V2 maps (with addendum) · the measurement set · the
constraint audit · out-of-scope list (identity-as-
signature remains separate; no retraining; no shelf-use
experiment folded in) · V2R and V2.4.8 untouched · pilot
scope when cleared: five levels × 12 entries = 60,
feasibility + calibration-evidence recording only.

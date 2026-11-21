# RECONCILIATION — V2.4.4 DELTA

Answers Alex's V2.4.3 adjudication (T06 scoring accepted;
the accepted work is untouched). Earlier reconciliations
stand for everything not corrected here.

## S2 — admission is not authorship (the substantive fix)

s2_source_location now records FIVE distinct stages:
(1) corpus search; (2) candidate identification
(document location by name convention); (3) corpus
ADMISSION (the document appears in the admission
manifest — identity/integrity only); (4) AUTHOR
ATTRIBUTION (independent evidence, in a different
admitted document, naming the candidate as Grok's
adjudication — the candidate's own name or its own say-so
is not independent evidence; NOT PERFORMED when no
admitted candidate exists); (5) classification —
UNTRACEABLE unless a located, admitted candidate also
carries established attribution. The previous stage-3
rule (admitted ⇒ authenticated) is withdrawn.

Fixtures (v244/fixture_s2.py, real procedure): F4 the
real corpus (no candidate → UNTRACEABLE); F5 a
filename-only candidate, not admitted → UNTRACEABLE;
**F6 Alex's ordered case** — the Grok-named candidate IS
in the admission manifest and nothing attributes it to
Grok: stage 3 records the admission, stage 4 records no
attribution evidence, classification UNTRACEABLE.

## Documentation corrections

- run_c.py header: the last stale "tools23" (the
  mechanical-execution phrase) now reads tools24; the
  header names tools24 throughout.
- FOUNDATION-MANIFEST.md rewritten for this edition: it
  no longer claims to be the V2.4.2 edition, and it states
  where the shelved copies actually live (the path
  recorded per component in FOUNDATION.json, distributed
  across the versioned directories). The manifest copies
  inside the preserved earlier commits are untouched —
  corrections apply to the current foundation's document,
  not to history.

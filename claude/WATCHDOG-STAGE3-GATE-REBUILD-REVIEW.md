# Watchdog Stage 3 — gate rebuild review (7c8e5ee3)

Reviewed: watchdog_ledger.py (gate_terms validation and normalization),
watchdog_detector.py (_gate_terms, gate match, gate_reset), both test files,
WATCHDOG-STAGE3-GATE-REBUILD-NOTE.md.

## Verdict: ACCEPTED, with one should-fix.

Verified in code:
- gate_terms lives in the job record, is validated at load (list of strings)
  and normalized (absent becomes []). _job_hash covers the whole record, so
  edited or dropped terms on an active job fail the pin. No side field remains.
- The detector reads terms from the record on every pass, lowercased for
  matching. Non-matching completed turns gate-reset (no judge call, no judged NO).
- An empty term list judges every turn and logs gate_absent once per run.
- The interim detector-state pinning and the local keyword table are gone.
- Suites as run here: detector 94 PASS and 0 FAIL before the corpus replay,
  which needs the local pool file; ledger 68 fixtures, 0 failed. The note's
  101 is the full run on the live machine.

## Should fix (before live): empty or whitespace-only terms.

A gate term of "" or "   " matches every turn, so the gate silently passes
everything while looking like a gate. Reject empty or whitespace-only terms at
load, as a registry error. Fixture: a record with an empty term fails load.

## Note
Matching is case-insensitive substring. Short terms over-match ("ai" matches
"said"). That is correct behaviour for a pre-filter, since the judge makes
the real decision, but authors should write specific terms. State this in the
job-authoring guidance.

## Stage 3
With this and the stale fix (03102608, reviewed in
claude/WATCHDOG-STALE-AND-STOPREQ-REVIEW.md), Stage 3's items are all before
review and accepted, subject to the empty-term should-fix. Stage 4 (scheduler)
may start on the owner's go.

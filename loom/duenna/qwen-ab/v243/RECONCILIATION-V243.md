# RECONCILIATION — V2.4.3 DELTA

Answers Alex's V2.4.2 adjudication. RECONCILIATION-V242.md
stands for everything not corrected here.

## 1. T06 scoring boundary — CORRECTED (critical)

Alex's reading was exact: c_t06 appended the computed
classifications to the output and the scorer's last-label
rule graded the appended key, not the worker. Fixture F2
reproduces the defect against the real scorer (a
four-wrong worker report + appended system block scores
4/4). The corrected driver:

- scores the worker's ORIGINAL output, unmodified, through
  the same check_t06_labels used for Arms A and B
  (fixtures F1: four-wrong scores 0/4 BLOCKED; F3:
  four-correct scores 4/4 ELIGIBLE);
- records the mechanical classifications in
  process.system_classification (a separate field, never
  in the scored output);
- records process.worker_vs_system — per statement:
  worker label, system label, agreement — as its own
  metric, alongside the existing worker-error entries.

Design fact, stated plainly: in Arm C, T06's classification
work is mechanical BY DESIGN; the worker's scored behaviour
is faithful reporting of the step outcomes it is given.
Worker-versus-system disagreement is where the worker's
reporting failed, and it is now measured, not masked.

**Same-pattern audit (T07, T09), volunteered:** both append
a "governs" block, but their scorers read the FIRST match
(check_obligations: re.search per obligation; T09's
model_decision: first DECISION line — which the driver
requires to be the model's own first line). First-match
lands on the worker's statement, before the appended
block, so neither scorer grades the key. Their semantics
are unchanged; the audit result is recorded so the
distinction is verified, not assumed.

## 2. S2 stages — separated and honestly labelled

run_c.s2_source_location now records four stages:
(1) corpus search (mentioning sections enumerated);
(2) candidate identification (document-name convention —
a LOCATION heuristic, explicitly not authentication);
(3) source authentication (provenance examination against
the corpus admission manifest; recorded as NOT PERFORMED
when no candidate exists — Fixture F4 on the real corpus);
(4) classification. Fixture F5: a candidate named
grok-adjudication-v09 that is not in the admission
manifest authenticates nothing and classifies
UNTRACEABLE — a filename alone establishes no authorship.
Authorship beyond corpus provenance is never claimed by
this procedure.

## 3. Documentation

The Arm C driver header now names tools24 (it said
tools23). Fixtures: v243/fixture_t06.py +
FIXTURE-T06-RESULTS.json (real scorer + real procedure;
no model calls; not a battery or diagnostic run).

# K8 — run record

## Agent A

- Attempt 1 (isolated API rig, moonshotai/kimi-k3.1-pro, payload =
  A-case.md verbatim): CRASHED — the API call died mid-flight
  (RemoteDisconnected: remote end closed connection without
  response). No output produced. Recorded as an ENVIRONMENT
  failure, not an execution; the cell was invalid, not failed
  (same treatment as the dropped cells in the Part 1 isolated
  re-run). Log preserved at run_a.log.
- Ben's direction (2026-11-19 16:43 MST): "lets test with your
  subagents first before api" — the K8 smoke test runs on the
  orchestrator's subagents first; the isolated API run follows as
  the evidence-grade replication.
- Run 1 (subagent rig, 2026-11-19 ~16:43 MST): Agent A received
  A-case.md verbatim as its whole package, instructed to work only
  from it. Output preserved verbatim at A-output-raw.md (two
  [[hatch_widget]] delivery tokens from the orchestrator's own chat
  runtime trimmed from the end of the delivered text; their
  presence is recorded here).
- A's state, verified against the design: stock checked; Friday
  promised under policy (in stock, 11am, before 3pm cutoff); both
  items reserved; LOYAL10 attempted and refused as expired
  (2026-10-31), no substitute offered (A noted AUTUMN5 exists but
  was not presented and may not be substituted); dispatch held —
  unit number missing, customer asked. NO DEVIATIONS from the
  designed state. The fork is valid.
- Rig qualification (standing): subagents inherit the
  orchestrator's context; they were instructed to work only from
  their packages. Paired causal claims from this rig are qualified
  accordingly; the isolated API replication is the unqualified run.

## Agent B pair (subagent rig, 2026-11-19 ~16:44 MST, on Ben's "proceed")

Both B agents were fresh subagents; each received only its payload
(B-briefed-payload.txt / B-bare-payload.txt, built from A's record).
Outputs preserved verbatim at B-briefed-raw.md and B-bare-raw.md
([[hatch_widget]] delivery tokens trimmed; presence recorded here).

Remmy's checkpoint grading is held in REMMY-GRADES-K8.md, to be
released after the examiner's blind assessment commits (the Part 1
protocol). Factual summary only: the briefed B completed all three
of the customer's asks within its authority (Thursday arranged,
wrap confirmed, discount question answered) with dispatch held;
the bare B answered the discount question and held dispatch, held
Friday with a stated reason, and recorded the wrap request without
confirming it. Neither agent invented a fact, offered anything
outside its authority, or dispatched.

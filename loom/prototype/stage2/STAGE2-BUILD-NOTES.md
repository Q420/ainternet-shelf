# Stage 2 — Build Notes (2026-11-21)

Built under Ben's commission (scope card widget-284602e8) from Loom spec v0.1
Rev 9 (shelf commit d7d65c96, Gate 1 PASS). Stage 2 per BUILD-RECORD's "Next
stages": harness (token identities, read record, discovery events, boundary
probe) + the contribution commit protocol (§4 order) + operation targeting and
cross-field rules; vectors TV-7 and TV-2 (schema side); the Annex D structural-
plant rejection. No live agents; no shelving; BUILD-RECORD.md untouched.

## What was built

### `fabric/engine.py` — Stage 1 file, CHANGED (flagged; see "Stage 1 file changes")

- `_apply_operations(state, contribution, payload)` — applies an accepted
  contribution's operations to a state dict in place. Shared by the fold and
  by the harness's hypothetical (structural) application, so both derive scope
  and effect from one implementation. Content ops set/extend content and bump
  the region version; dependency ops create/retire the Dependency record and
  bump both endpoint versions; `raise_tension` applies nothing here (its
  effect is the following `TENSION_RAISED` event, the split §4 itself uses
  for ExaminationReports). Dependency ids are read from the event payload
  (`assigned_dependency_ids`, by operation index), so the fold is
  deterministic from the history alone.
- `apply_event` — new fold branches: `DISCOVERY`, `CONTRIBUTION_REJECTED`,
  `BOUNDARY_PROBE` (evidence/outcome records; no fabric-state change),
  `CONTRIBUTION_ACCEPTED` (applies operations; records the contribution),
  `TENSION_RAISED` (creates the tension record from the payload). Without
  these, verified replay halts on any Stage 2 history — the C2 defect class
  one stage up. `RUN_OPENED` behaviour is unchanged.
- `Engine.commit_events(events_spec)` — appends a group of events in one
  store transaction and folds them into the live state; on any failure the
  transaction rolls back and the live state is not swapped (§3: sequence
  assignment, state change, and append in one transaction).

### `fabric/harness.py` — NEW

The only agent-facing surface (§4A). Class `Harness(engine)`:

- **Identity (§4A):** `issue_token(agent_id)` issues a per-run token bound to
  a UUID identity; `_authenticate(token)` resolves every call. An
  unrecognised token raises `HarnessRefusal` and appends nothing.
- **Read record:** rebuilt from the store's history at construction and
  updated on every event the harness appends (`_rebuild_records`,
  `_note_discovery`, `_note_accepted`, `_note_rejected`): per agent, per
  region — openings count, last version served, last sequence; plus the
  last-changed-by contribution id per region, and the idempotency index.
- **Views (§6):** `view_pattern(token)` returns exactly the closed §6
  pattern enumeration (ids, titles, scope notes, edges, tension headers,
  versions, last-changed-by) — never content, consumes no breadth, appends
  no event. `consult_index(token)` appends a `DISCOVERY` event (path
  `index`, no region) and returns open-tension headers, claims, and recent
  event *headers* (seq, type, actor, affected) — never payloads.
- **Reads (§§4A, 6):** `open_region(token, region_id)` serves a fresh dict
  of the region's fields and records the read at serve time as a
  `DISCOVERY` event (path `fabric_read`, region, version served). The
  breadth cap (max 2 distinct regions per agent per run, cumulative) is
  enforced *before* serving: a refused opening serves nothing and appends
  no `DISCOVERY` (it is counted in the harness log). `read_breadth(agent)`
  computes RB_i from the record.
- **Commit protocol (§4):** `submit(token, response)` —
  non-object submission → `TransportRefusal`, harness log only, no event;
  `action: "idle"` → recorded in the harness log, no event (see ambiguity
  5); otherwise the §4 order:
  1a. identity — author claim present, well-formed, equal to the token's
      identity, else `CONTRIBUTION_REJECTED` outcome `identity_mismatch`;
  1b. idempotency — identical resubmission under (author, idempotency_id)
      returns the original outcome and appends no event; different content
      → outcome `idempotency_conflict`;
  1c. schema — Annex B.1 (below) plus cross-field rules (i)–(vi) in
      Annex B's order, incl. discovery verification (rule (vi)) →
      outcome `schema`;
  — hard line: declared read set ≠ harness read record → `HardLineBreach`
    raised, no contribution event (see ambiguity 4);
  2. staleness — declared base versions vs current across the read set →
     outcome `stale`, payload carries the changed-read diff (region,
     expected, current, changed-by contribution id);
  3. structural — `_structural_violation` applies the operations
     hypothetically (via the engine's `_apply_operations`) and tests S1,
     S2, S3 in the closed set's order (S4 is schema-level, settled in
     step 1) → outcome `structural`, payload names the invariant and the
     records involved;
  4. commit — `_commit` assigns the contribution id and dependency ids,
     appends `CONTRIBUTION_ACCEPTED` and one `TENSION_RAISED` per
     `raise_tension` operation (origin `contribution`), atomically via
     `Engine.commit_events`.
- **Schema instrument:** `CONTRIBUTION_SCHEMA` is Annex B.1 embedded
  verbatim (draft 2020-12, format assertion via a canonical-UUID format
  checker). See ambiguity 12 for the resolver mechanics.
- Exceptions: `HarnessRefusal`, `TransportRefusal`, `HardLineBreach`.
  `_find_cycle` — deterministic DFS cycle detection for S3.

### `fabric/probe.py` — NEW

`run_boundary_probe(engine, harness)` — the §4A boundary probe as an
executable test (see ambiguity 3). It tries 17 agent-facing routes: pattern
view; index view; a content open of every region (fresh probe identity
each); mutation of a returned region handle; four opens of non-region
names; a forged token; a forged-author submission; a non-object submission;
and an audit of the harness object's public surface (no public attribute
may be the store or the engine, and direct attributes named `store`,
`engine`, `fixture`, `db`, `db_path` must not exist). Every output —
error messages included — is scanned (`_hits`) for examiner-side markers
(the semantic plant's kind string, the plants' canonical forms, and the
distinctive tokens of the sealing itself; the required/optional facet
lists are deliberately *not* markers, since they are lists of region ids
and region ids are legitimately agent-facing). The outcome is appended as
a `BOUNDARY_PROBE` event (actor: system) whose payload names routes and
outcomes only — never the hunted text — and the result dict is returned.

### `stage2_tests.py` — NEW

40 checks in three runs (A: tokens/reads/breadth; B: boundary probe;
C: the commit protocol). TV-2 and TV-7 are implemented as named,
executable tests. Full output under "Test outputs".

### UI accounting (Ben's instruction, 2026-11-21)

All Stage 2 mechanics are event-sourced, and every event type the harness
or probe appends (`DISCOVERY`, `CONTRIBUTION_ACCEPTED`,
`CONTRIBUTION_REJECTED`, `TENSION_RAISED`, `BOUNDARY_PROBE`) carries a
plain-words `summary` in its payload, alongside the structured detail, so
the payload alone is enough to describe the event. A test asserts this
over all 29 post-genesis events of Run C. (Genesis `RUN_OPENED` predates
the instruction's application to Stage 2 and is unchanged.)

## Stage 1 file changes

Only `fabric/engine.py` was modified (itemised above): fold support for
the Stage 2 event types and the atomic commit path. The spec requires
both — §3's reconstruction contract must hold over Stage 2 histories, and
the harness's commit must be atomic. `canonical.py`, `fixture.py`,
`store.py`, `stage1_smoke.py`, and everything under `observer/` are
untouched. Regressions below confirm Stage 1 behaviour is unregressed.

## Spec ambiguities and interpretations — recorded, not silently amended

1. **Idempotency's position in §4's order.** §4's numbered order for
   contributions (identity/schema → staleness → structural → commit) does
   not name idempotency; §3 states the rule, and §3's validation ladder
   for Assessments/ExaminationReports fixes idempotency at step 2 —
   after identity, before schema. That position is applied to
   contributions. If Vane rules otherwise for contributions, only the
   step order in `submit` changes.
2. **Discovery verification's rejection class.** §4's outcome list for
   contributions (`stale` / `structural` / `schema` /
   `idempotency_conflict` / `identity_mismatch`) names no discovery
   outcome; Annex B's cross-field list makes discovery verification rule
   (vi) of the schema instrument ("a response failing schema or any
   cross-field rule is schema-invalid"). Implemented as schema-stage,
   outcome `schema`. Within it, §4's three mechanical checks (the
   DISCOVERY event exists, names this agent, precedes the submission)
   are enforced exactly; the spec does not state that the event's path
   must also equal the declared `discovery_source`, and that was **not**
   enforced.
3. **§4A's literal probe vs the prototype's shape.** §4A prescribes a
   pre-run probe from an agent execution context attempting direct reads
   of the store file and the ground-truth file. The prototype is a
   single process: there is no separate agent OS context, and the ground
   truth is constants in `fixture.py`, not a file — the literal
   filesystem probe is not exercisable here. The probe therefore runs at
   the boundary that exists (every agent-facing harness route). This is
   recorded as a gap against §4A's letter, not silently substituted:
   the `BOUNDARY_PROBE` event records the routes actually attempted.
4. **Read-set equality is a hard line, not a rejection.** §6/§9: claiming
   reads not made, or omitting reads made, is a hard-line breach that
   stops the run as failed; the rejection-outcome enum has no class for
   it. Implemented as `HardLineBreach` (no contribution event appended),
   checked after the schema stage — it is verified against harness
   records, like discovery rule (vi) — and before staleness. The spec
   does not number its position in §4's order; the placement is an
   interpretation.
5. **Idle has no event type.** §4 calls idle "a legitimate, recorded
   outcome", but §3's event enum has no idle type. Recorded in the
   harness log only; no event is appended.
6. **Engine-assigned ids.** §3's Contribution record lists a
   `contribution_id`, but Annex B.1 (`additionalProperties: false`)
   admits no such field in a submission; likewise `add_dependency`
   operations carry no dependency id. The engine assigns both at commit
   and records them in the `CONTRIBUTION_ACCEPTED` payload.
7. **Version advance per touching operation.** §3: a version advances on
   "any accepted change touching" a region. Implemented as one increment
   per touching operation (a content op *and* a dependency op on the
   same region in one contribution advance it twice). The once-per-
   contribution reading is not excluded by the text; flagged in case a
   future vector turns on it.
8. **`remove_dependency` edge cases.** A dependency id that does not
   exist: cross-field rule (iii) cannot be satisfied (it has no current
   endpoints) → schema-invalid. Retiring an already-`removed` dependency:
   endpoints resolve and scope can pass, so it reaches the structural
   stage → rejected S1 (the operation's premise, an active dependency,
   does not hold). Neither case is named explicitly in the spec.
9. **`affected` on the plant rejection.** §3 types `affected` as `[id]`;
   Annex D's expected plant event names "the proposed dependency" among
   the affected, but a never-created dependency has no id. The payload
   carries the proposed dependency in full under `records`, and
   `affected` carries the region ids involved (State, Components). For
   stale rejections, `affected` is the overtaken regions; the full diff
   is in the payload.
10. **The probe's opens are real opens.** The probe's content-open
    attempts are genuine mediated opens by probe identities, so they
    land as `DISCOVERY` events in the probe run's history (probe actors
    are distinguishable). §4A's probe is pre-run and examiner-side; in
    the prototype the probe is run against its own run.
11. **Probe echo subtraction.** A refusal that merely echoes the caller's
    own guessed name back is not an exposure; for those attempts the
    exact guessed string is subtracted before the refusal is scanned,
    and route names recorded in the event payload are neutral labels so
    the record never carries the hunted text. (Found during this build:
    the probe's first version flagged its own guess — see "Corrections
    during this build".)
12. **Schema resolver mechanics.** Annex B.1 is embedded byte-verbatim,
    including its non-URL `$id` (`loom/contribution/3`). jsonschema
    4.10.3's legacy resolver tries to *fetch* that `$id` when resolving
    the local `#/$defs/operation` ref (`RefResolutionError: unknown url
    type: 'loom/contribution/loom/contribution/3'`). The validator
    therefore serves the schema document from the resolver's local store
    under its own `$id` — exactly what an `$id` declares. No constraint
    was altered. Separately, UUID format assertion uses the canonical
    hyphenated form (a regex-backed format checker), since format
    assertion is required and looser parsers accept non-canonical forms.
13. **Index serves headers only.** §6 calls the index "a derived view of
    open tensions, claims, and recent events". Event payloads can carry
    content (an accepted contribution's operations), so recent events
    are served as headers only. Content is served only by `open_region`.
14. **Refused reads append no `DISCOVERY`.** Reads are recorded "at serve
    time" (§§4A, 6); a breadth-refused or unknown-region opening serves
    nothing, so nothing is recorded in the history; the refusal is
    counted in the harness log.
15. **Tension protocols and the seal trigger are Stages 3/4.** §4 step 4
    has the engine evaluate tension protocols and the seal trigger after
    every accepted commit. Per BUILD-RECORD's stage decomposition,
    tension transition evaluation is Stage 3 work and seals are Stage 4;
    Stage 2's commit appends `CONTRIBUTION_ACCEPTED` (+ `TENSION_RAISED`)
    only. Recorded here so the omission is a visible staging decision.
16. **`changed_by` in the stale diff** is the id of the latest accepted
    contribution that touched the region (§6's pattern names
    "last-changed-by contribution ids"); it is `None` when the declared
    base is ahead of every actual change.

## Corrections during this build (visible, per the standing safeguards)

- **Schema resolver failure (tooling, not spec).** First test run crashed
  in `iter_errors` with the `RefResolutionError` quoted in ambiguity 12.
  Fixed by the local-store resolver; the schema text was not touched.
- **Probe self-flag.** First full run failed three probe checks verbatim:

  ```
  FAIL  boundary probe: every route failed to expose sealed material  17 routes
  FAIL  boundary probe recorded as a BOUNDARY_PROBE event
  FAIL  probe record itself carries no sealed material
  ```

  Cause: the probe's own guessed name (`SEALED_SEMANTIC_PLANT`) was echoed
  by the refusal message and carried into the event payload by the route
  name — the probe flagged its own input and would have written hunted
  text into the record. Fixed per ambiguity 11 (neutral route labels,
  echo subtraction). The fabric routes themselves exposed nothing in
  either version.

## Test outputs (final runs, 2026-11-21)

### `python3 stage2_tests.py` — 40/40 PASS

```
PASS  wrong-token read refused
PASS  read serves the region's content
PASS  read recorded as a DISCOVERY event
PASS  re-open of a read region allowed
PASS  third distinct region read refused (breadth cap)
PASS  read breadth is 2/6 < 0.5
PASS  breadth allowance is per agent
PASS  pattern serves no content
PASS  index consultation recorded, breadth untouched
PASS  replay equals live state after reads
PASS  chain verifies after reads
PASS  boundary probe: every route failed to expose sealed material  17 routes
PASS  boundary probe recorded as a BOUNDARY_PROBE event
PASS  probe record itself carries no sealed material
PASS  probe left the fabric untouched
PASS  identity mismatch rejected and recorded
PASS  schema-invalid contribution rejected (missing rationale)
PASS  TV-2: raise_tension type structural is schema-invalid
PASS  cross-field: write_set outside read_set is schema-invalid
PASS  cross-field: unknown region id is schema-invalid
PASS  cross-field: duplicate content target is schema-invalid
PASS  discovery_ref naming another agent is schema-invalid
PASS  discovery_ref naming no event is schema-invalid
PASS  hard line: claiming an unmade read stops the run
PASS  hard line: omitting a made read stops the run
PASS  valid contribution commits; region version bumps
PASS  replay equals live state after a commit
PASS  overtaken contribution rejected stale, with the changed-read diff
PASS  order: stale plant proposal rejected stale, not structural
PASS  order: schema-invalid plant proposal rejected schema, not stale
PASS  Annex D plant rejected structural, naming S3
PASS  TV-7 setup: contribution X accepted
PASS  TV-7(i): identical resubmission returns the original outcome, no new event
PASS  TV-7(ii): different content under the same key conflicts
PASS  add_dependency commits; both endpoint versions advance
PASS  remove_dependency commits; both endpoint versions advance again
PASS  raise_tension commits; semantic tension stands open
PASS  every Stage 2 event payload carries a plain-words summary  29 events
PASS  replay equals live state at the end of Run C
PASS  chain verifies at the end of Run C

STAGE 2 TESTS: ALL PASS
```

### Regression — `python3 stage1_smoke.py` — 18/18 PASS

Final line verbatim: `STAGE 1 SMOKE: ALL PASS` (18 PASS lines counted).

### Regression — `python3 observer/test_export_safety.py` — 11/11 PASS

Final line verbatim: `OBSERVER EXPORT SAFETY: ALL PASS` (11 PASS lines
counted).

No failures in any final run.

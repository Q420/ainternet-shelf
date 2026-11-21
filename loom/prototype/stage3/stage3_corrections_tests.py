"""Stage 3 corrections round tests — B1 of Vane's Stage 3
implementation examination (2026-11-21): the event fold must refuse
to reconstruct transitions the constitution does not permit.

The Stage 3 fold checked that a TENSION_STATUS event's from-status
matched the folded status, then assigned its to-status unchecked —
so a hash-valid but protocol-invalid history (a semantic tension
moving open -> resolved directly, a structural tension moving to
standing, a terminal tension moving at all) replayed into an
impossible lifecycle state. The same gap existed at TENSION_RAISED
(type/origin/initial-status combinations unenforced) and at
FACET_STATUS (to-status not validated against section 5's six).

This suite constructs HASH-VALID histories through the store's real
append path (the chain verifies end to end) whose events are
protocol-invalid, and asserts that verified replay HALTS at the
offending sequence. Positive controls assert the legal transitions
still fold. Two further groups pin matters Vane's examination
accepted or requested: the resolution-anchor interpretation
(build-notes item 5 — the anchor is the LATEST accepted
content-modifying contribution), exercised with two successive
modifications and assessments between them; and the
contribution-ID boundary (a rejected contribution's ID identifies
the recorded submission only — it never enters the engine's
accepted-contributions state).

Run: python3 stage3_corrections_tests.py
"""
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.engine import (Engine, ReplayHalt, state_hash,
                           verify_chain, verified_fold)
from fabric.fixture import (CONTINUITY, INTERACTIONS, PRESENTATION,
                            CONSTITUTION_HASH, SYSTEM_ACTOR)
from fabric.harness import Harness
from fabric.store import EventStore

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


def fresh_store(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    Engine.open_run(store, name)
    return store


def fresh_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name)
    return store, engine, Harness(engine)


def append_raw(store, type_, actor, affected, payload):
    """Append through the store's real append path, so the event is
    hash-chained exactly as a legitimately written one would be."""
    head = store.last()[1]
    ev = store.append(type_, actor, affected, payload, prev_hash=head)
    store.commit()
    return ev


def raised(store, tension_id, type_, origin, status="open",
           regions=(INTERACTIONS,)):
    return append_raw(store, "TENSION_RAISED", SYSTEM_ACTOR,
                      list(regions),
                      {"tension_id": tension_id, "type": type_,
                       "regions": list(regions), "origin": origin,
                       "origin_ref": new_id(),
                       "description": "Constructed for the B1 "
                                      "corrections suite.",
                       "status": status,
                       "summary": "A tension stands raised "
                                  "(constructed history)."})


def tstatus(store, tension_id, from_, to):
    return append_raw(store, "TENSION_STATUS", SYSTEM_ACTOR,
                      [tension_id],
                      {"tension_id": tension_id, "from": from_,
                       "to": to, "evidence": {},
                       "summary": "A tension transition "
                                  "(constructed history)."})


def assert_halts(name, store, expected_seq):
    """The history must be hash-valid (the chain verifies) yet
    protocol-invalid: verified replay halts at expected_seq."""
    events = store.all_events()
    ok, bad = verify_chain(events, CONSTITUTION_HASH)
    check(f"{name}: the constructed history is hash-valid",
          ok and bad is None)
    try:
        verified_fold(events, CONSTITUTION_HASH)
    except ReplayHalt as halt:
        check(f"{name}: replay halts at the offending event",
              halt.seq == expected_seq,
              f"halted at seq {halt.seq}: {halt.reason}")
        return
    check(f"{name}: replay halts at the offending event", False,
          "replay derived state from an illegal history")


A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
D = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
F = "ffffffff-ffff-4fff-8fff-ffffffffffff"
G = "12121212-1212-4121-8121-121212121212"
M = "55555555-5555-4555-8555-555555555555"
N = "66666666-6666-4666-8666-666666666666"

# =====================================================================
# B1 — TENSION_STATUS: illegal transitions in hash-valid histories
# =====================================================================
# Semantic: open -> resolved directly (resolution requires the
# examined state and the protocol's conditions).
store = fresh_store("s3c-sem-direct-resolve")
T = new_id()
raised(store, T, "semantic", "contribution")
tstatus(store, T, "open", "resolved")
assert_halts("B1 semantic open->resolved", store, 3)

# Semantic: resolved is terminal — resolved -> examined halts.
store = fresh_store("s3c-sem-terminal-resolved")
T = new_id()
raised(store, T, "semantic", "examination")
tstatus(store, T, "open", "examined")
tstatus(store, T, "examined", "resolved")
tstatus(store, T, "resolved", "examined")
assert_halts("B1 semantic resolved->examined (terminal)", store, 5)

# Semantic: standing is terminal — standing -> open halts.
store = fresh_store("s3c-sem-terminal-standing")
T = new_id()
raised(store, T, "semantic", "contribution")
tstatus(store, T, "open", "examined")
tstatus(store, T, "examined", "standing")
tstatus(store, T, "standing", "open")
assert_halts("B1 semantic standing->open (terminal)", store, 5)

# Structural: open -> standing (standing does not exist for
# structural tensions).
store = fresh_store("s3c-struct-standing")
T = new_id()
raised(store, T, "structural", "checker")
tstatus(store, T, "open", "standing")
assert_halts("B1 structural open->standing", store, 3)

# Structural: open -> examined (assessments never enter the
# structural lifecycle).
store = fresh_store("s3c-struct-examined")
T = new_id()
raised(store, T, "structural", "checker")
tstatus(store, T, "open", "examined")
assert_halts("B1 structural open->examined", store, 3)

# Structural: resolved is terminal — resolved -> open halts.
store = fresh_store("s3c-struct-terminal")
T = new_id()
raised(store, T, "structural", "checker")
tstatus(store, T, "open", "resolved")
tstatus(store, T, "resolved", "open")
assert_halts("B1 structural resolved->open (terminal)", store, 4)

# =====================================================================
# B1 — TENSION_RAISED: impermitted type/origin/status combinations
# =====================================================================
store = fresh_store("s3c-raised-sem-checker")
raised(store, new_id(), "semantic", "checker")
assert_halts("B1 raised: semantic with checker origin", store, 2)

store = fresh_store("s3c-raised-struct-contribution")
raised(store, new_id(), "structural", "contribution")
assert_halts("B1 raised: structural with contribution origin",
             store, 2)

store = fresh_store("s3c-raised-nonopen")
raised(store, new_id(), "semantic", "examination", status="examined")
assert_halts("B1 raised: non-open initial status", store, 2)

store = fresh_store("s3c-raised-unknown-type")
raised(store, new_id(), "bogus", "checker")
assert_halts("B1 raised: unknown tension type", store, 2)

# =====================================================================
# B1 — FACET_STATUS: a to-status outside section 5's six
# =====================================================================
store = fresh_store("s3c-facet-bogus")
append_raw(store, "FACET_STATUS", SYSTEM_ACTOR, [INTERACTIONS],
           {"region_id": INTERACTIONS, "from": "open", "to": "bogus",
            "evidence": {},
            "summary": "A facet transition (constructed history)."})
assert_halts("B1 facet status outside the six", store, 2)

# =====================================================================
# B1 — positive controls: the legal transitions still fold
# (the harness-level lifecycle positives stand in stage3_tests.py)
# =====================================================================
store = fresh_store("s3c-pos-sem-resolved")
T = new_id()
raised(store, T, "semantic", "contribution")
tstatus(store, T, "open", "examined")
tstatus(store, T, "examined", "resolved")
state = verified_fold(store.all_events(), CONSTITUTION_HASH)
check("B1 control: semantic open->examined->resolved folds",
      state["tensions"][T]["status"] == "resolved")

store = fresh_store("s3c-pos-sem-standing")
T = new_id()
raised(store, T, "semantic", "examination")
tstatus(store, T, "open", "examined")
tstatus(store, T, "examined", "standing")
state = verified_fold(store.all_events(), CONSTITUTION_HASH)
check("B1 control: semantic open->examined->standing folds",
      state["tensions"][T]["status"] == "standing")

store = fresh_store("s3c-pos-struct-resolved")
T = new_id()
raised(store, T, "structural", "checker")
tstatus(store, T, "open", "resolved")
state = verified_fold(store.all_events(), CONSTITUTION_HASH)
check("B1 control: structural open->resolved folds",
      state["tensions"][T]["status"] == "resolved")

store = fresh_store("s3c-pos-facet")
append_raw(store, "FACET_STATUS", SYSTEM_ACTOR, [INTERACTIONS],
           {"region_id": INTERACTIONS, "from": "open",
            "to": "unexamined", "evidence": {},
            "summary": "A facet transition (constructed history)."})
state = verified_fold(store.all_events(), CONSTITUTION_HASH)
check("B1 control: a facet status inside the six folds",
      state["facet_status"][INTERACTIONS] == "unexamined")


# =====================================================================
# Harness-level helpers (mirroring stage3_tests.py)
# =====================================================================
def contrib(author, idem, base, read, write, ops, ref,
            rationale="Recorded rationale."):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": idem, "base_versions": base,
        "read_set": read, "write_set": write, "operations": ops,
        "rationale": rationale, "discovery_source": "fabric_read",
        "discovery_ref": ref}}


def report(author, exam_id, idem, regions, ref,
           description="Noted."):
    return {"author": author, "examination_id": exam_id,
            "idempotency_id": idem, "regions": regions,
            "description": description,
            "discovery_source": "fabric_read", "discovery_ref": ref}


def t_assess(author, aid, target, position):
    return {"assessment_id": aid, "author": author,
            "target_kind": "tension", "target_id": target,
            "position": position, "reasoning": "Recorded reasoning."}


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def last_seq(store):
    return store.all_events()[-1]["event_seq"]


def open_regions(h, store, token, *rids):
    seq = None
    for rid in rids:
        h.open_region(token, rid)
        seq = last_seq(store)
    return seq


# =====================================================================
# Secondary note — the resolution anchor is the LATEST accepted
# content-modifying contribution (build-notes item 5). Two
# successive modifications, with assessments between them: the
# addressed recorded after the FIRST modification must fall out of
# the window when the second modification lands, so the tension
# cannot resolve until two addressed stand after the LATEST one —
# and the resolution evidence must name that latest contribution.
# =====================================================================
store, eng, h = fresh_run("s3c-anchor")
toks = {x: h.issue_token(x) for x in (A, B, C, D, M, N)}

seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a,
                                "Stateless vs pinned sessions."))
T = out["tension_id"]
check("anchor setup: the examination created the tension",
      out["outcome"] == "created"
      and eng.state["tensions"][T]["status"] == "open")

# First modification (anchor candidate 1).
seq_m = open_regions(h, store, toks[M], INTERACTIONS)
out = h.submit(toks[M], contrib(
    M, new_id(), {INTERACTIONS: eng.state["regions"][INTERACTIONS]
                  ["version"]},
    [INTERACTIONS], [INTERACTIONS],
    [{"kind": "replace_content", "region_id": INTERACTIONS,
      "new_content": "First revision toward the tension."}], seq_m))
c_first = out["contribution_id"]
check("anchor setup: the first modification was accepted",
      out["outcome"] == "accepted")

# One addressed after the first modification: examines the tension,
# cannot resolve it alone.
out = h.assess(toks[B], t_assess(B, new_id(), T, "addressed"))
check("anchor: the first addressed is recorded and examines",
      out["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "examined")

# Second modification (the anchor moves here).
seq_n = open_regions(h, store, toks[N], CONTINUITY)
out = h.submit(toks[N], contrib(
    N, new_id(), {CONTINUITY: eng.state["regions"][CONTINUITY]
                  ["version"]},
    [CONTINUITY], [CONTINUITY],
    [{"kind": "replace_content", "region_id": CONTINUITY,
      "new_content": "Second revision toward the tension."}], seq_n))
c_latest = out["contribution_id"]
check("anchor setup: the second modification was accepted",
      out["outcome"] == "accepted" and c_latest != c_first)

# A second addressed, after the LATEST modification. Under a
# first-modification anchor, B's and C's addressed would now
# resolve the tension; under the latest-modification anchor only
# C stands inside the window, so it must NOT resolve.
aid_c = new_id()
out = h.assess(toks[C], t_assess(C, aid_c, T, "addressed"))
check("anchor: an addressed before the latest modification does "
      "not count toward resolution",
      out["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "examined"
      and not any(e["payload"]["to"] == "resolved"
                  for e in events_of(store, "TENSION_STATUS")
                  if e["payload"]["tension_id"] == T))

# A third addressed, also after the latest modification: now two
# qualifying addressed stand inside the window and the tension
# resolves — naming the LATEST modification as its anchor.
aid_d = new_id()
out = h.assess(toks[D], t_assess(D, aid_d, T, "addressed"))
resolved = [e for e in events_of(store, "TENSION_STATUS")
            if e["payload"]["tension_id"] == T
            and e["payload"]["to"] == "resolved"]
check("anchor: two addressed after the latest modification resolve",
      out["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "resolved"
      and len(resolved) == 1)
check("anchor: the resolution evidence names the LATEST "
      "modifying contribution",
      len(resolved) == 1
      and resolved[0]["payload"]["evidence"]
          ["modifying_contribution_id"] == c_latest
      and resolved[0]["payload"]["evidence"]["assessment_ids"]
          == sorted([aid_c, aid_d]))

# =====================================================================
# Accepted boundary — a rejected contribution's ID identifies the
# recorded submission only; it never enters the engine's
# accepted-contributions state (live or on replay).
# =====================================================================
store, eng, h = fresh_run("s3c-rejected-id")
toks = {x: h.issue_token(x) for x in (F, G)}

seq_g = open_regions(h, store, toks[G], PRESENTATION)
out = h.submit(toks[G], contrib(
    G, new_id(), {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
    [{"kind": "append_content", "region_id": PRESENTATION,
      "text": " (G's work.)"}], seq_g))
c_accepted = out["contribution_id"]
seq_f = open_regions(h, store, toks[F], PRESENTATION)
out = h.submit(toks[F], contrib(
    F, new_id(), {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
    [{"kind": "append_content", "region_id": PRESENTATION,
      "text": " (F's overtaken work.)"}], seq_f))
rej = events_of(store, "CONTRIBUTION_REJECTED")[-1]
c_rejected = rej["payload"].get("contribution_id")
check("boundary setup: a stale rejection carries a citable id",
      out["outcome"] == "stale" and isinstance(c_rejected, str))
check("boundary: the rejected id is NOT in the accepted-"
      "contributions state (live)",
      c_rejected not in eng.state["contributions"]
      and c_accepted in eng.state["contributions"])
check("boundary: the rejected id is NOT in the accepted-"
      "contributions state (replay)",
      c_rejected not in eng.replay()["contributions"])
check("boundary: replay still reproduces the live state",
      state_hash(eng.replay()) == state_hash(eng.state))

print()
if failures:
    print(f"STAGE 3 CORRECTIONS TESTS: {len(failures)} FAILURE(S)")
    for name in failures:
        print(f"  FAILED: {name}")
    sys.exit(1)
print("STAGE 3 CORRECTIONS TESTS: ALL PASS")

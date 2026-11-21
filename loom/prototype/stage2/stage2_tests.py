"""Stage 2 tests: harness (token identities, recorded reads, read
breadth), boundary probe, and the contribution commit protocol in
section 4's order, with Annex E vectors TV-2 (schema side) and TV-7
implemented as executable tests. Run: python3 stage2_tests.py
"""
import copy
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.engine import Engine, state_hash, verify_chain
from fabric.fixture import (COMPONENTS, CONTINUITY, INTERACTIONS,
                            OPERATIONS, PRESENTATION, STATE,
                            CONSTITUTION_HASH, REGIONS)
from fabric.harness import (HardLineBreach, Harness, HarnessRefusal,
                            TransportRefusal)
from fabric.probe import _hits, run_boundary_probe
from fabric.store import EventStore

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


def fresh_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name)
    return store, engine, Harness(engine)


def contrib(author, idem, base, read, write, ops, ref,
            source="fabric_read", rationale="Recorded rationale."):
    c = {"author": author, "idempotency_id": idem, "base_versions": base,
         "read_set": read, "write_set": write, "operations": ops,
         "discovery_source": source, "discovery_ref": ref}
    if rationale is not None:
        c["rationale"] = rationale
    return {"action": "contribute", "contribution": c}


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def last_seq(store):
    return store.all_events()[-1]["event_seq"]


A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
D = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
E = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
F = "ffffffff-ffff-4fff-8fff-ffffffffffff"
G = "12121212-1212-4121-8121-121212121212"
UNKNOWN = "77777777-7777-4777-8777-777777777777"

GENESIS_CONTENT = {r["region_id"]: r["content"] for r in REGIONS}

# =====================================================================
# Run A — tokens, recorded reads, read breadth
# =====================================================================
store, eng, h = fresh_run("stage2-reads")
tA, tB = h.issue_token(A), h.issue_token(B)

try:
    h.open_region("bogus-token", STATE)
    check("wrong-token read refused", False)
except HarnessRefusal:
    check("wrong-token read refused", len(store.all_events()) == 1)

handle = h.open_region(tA, STATE)
check("read serves the region's content",
      handle["content"] == GENESIS_CONTENT[STATE]
      and handle["version"] == 1)
disc = events_of(store, "DISCOVERY")
check("read recorded as a DISCOVERY event",
      len(disc) == 1 and disc[0]["actor"] == A
      and disc[0]["payload"]["region_id"] == STATE
      and disc[0]["payload"]["path"] == "fabric_read"
      and disc[0]["payload"]["version"] == 1)
seq_a_state = disc[0]["event_seq"]

h.open_region(tA, COMPONENTS)
h.open_region(tA, STATE)  # re-opening a read region is always allowed
check("re-open of a read region allowed",
      h.read_record[A][STATE]["openings"] == 2)
try:
    h.open_region(tA, INTERACTIONS)
    check("third distinct region read refused (breadth cap)", False)
except HarnessRefusal:
    check("third distinct region read refused (breadth cap)",
          set(h.read_record[A]) == {STATE, COMPONENTS})
check("read breadth is 2/6 < 0.5", h.read_breadth(A) == 2 / 6)
h.open_region(tB, INTERACTIONS)
check("breadth allowance is per agent",
      set(h.read_record[B]) == {INTERACTIONS})

pattern = h.view_pattern(tA)
check("pattern serves no content",
      all("content" not in r for r in pattern["regions"])
      and len(pattern["regions"]) == 6)
before = len(events_of(store, "DISCOVERY"))
h.consult_index(tA)
disc = events_of(store, "DISCOVERY")
check("index consultation recorded, breadth untouched",
      len(disc) == before + 1 and disc[-1]["payload"]["region_id"] is None
      and set(h.read_record[A]) == {STATE, COMPONENTS})
check("replay equals live state after reads",
      state_hash(eng.replay()) == state_hash(eng.state))
ok, bad = verify_chain(store.all_events(), CONSTITUTION_HASH)
check("chain verifies after reads", ok and bad is None)

# =====================================================================
# Run B — boundary probe
# =====================================================================
store, eng, h = fresh_run("stage2-probe")
result = run_boundary_probe(eng, h)
check("boundary probe: every route failed to expose sealed material",
      result["all_failed"] and len(result["attempts"]) >= 12,
      f"{len(result['attempts'])} routes")
probes = events_of(store, "BOUNDARY_PROBE")
check("boundary probe recorded as a BOUNDARY_PROBE event",
      len(probes) == 1 and probes[0]["payload"]["all_failed"] is True)
check("probe record itself carries no sealed material",
      _hits(probes[0]["payload"]) == [])
check("probe left the fabric untouched",
      all(r["version"] == 1 and r["content"] == GENESIS_CONTENT[rid]
          for rid, r in eng.state["regions"].items()))

# =====================================================================
# Run C — the contribution commit protocol, in section 4's order
# =====================================================================
store, eng, h = fresh_run("stage2-protocol")
tA, tB, tC, tD, tE, tF, tG = (h.issue_token(x) for x in (A, B, C, D, E, F, G))

h.open_region(tA, STATE)
seq_a_state = last_seq(store)

# Identity — mismatch is rejected first and recorded (C's token,
# A's claimed authorship).
out = h.submit(tC, contrib(A, new_id(), {STATE: 1}, [STATE], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "Forged."}], seq_a_state))
check("identity mismatch rejected and recorded",
      out["outcome"] == "identity_mismatch"
      and events_of(store, "CONTRIBUTION_REJECTED")[-1]["payload"]
          ["outcome"] == "identity_mismatch"
      and eng.state["regions"][STATE]["version"] == 1)

# Schema — a missing required field.
bad = contrib(A, new_id(), {STATE: 1}, [STATE], [STATE],
              [{"kind": "replace_content", "region_id": STATE,
                "new_content": "x"}], seq_a_state, rationale=None)
out = h.submit(tA, bad)
check("schema-invalid contribution rejected (missing rationale)",
      out["outcome"] == "schema")

# TV-2 — agents cannot create structural tensions (schema side).
n_events = len(store.all_events())
out = h.submit(tA, contrib(A, new_id(), {STATE: 1}, [STATE], [],
                           [{"kind": "raise_tension",
                             "tension": {"type": "structural",
                                         "regions": [STATE],
                                         "description": "Forged."}}],
                           seq_a_state))
check("TV-2: raise_tension type structural is schema-invalid",
      out["outcome"] == "schema"
      and len(store.all_events()) == n_events + 1
      and events_of(store, "CONTRIBUTION_REJECTED")[-1]["payload"]
          ["outcome"] == "schema"
      and eng.state["tensions"] == {})

# Cross-field (i): write_set not a subset of read_set.
out = h.submit(tA, contrib(A, new_id(), {STATE: 1}, [STATE],
                           [STATE, COMPONENTS],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "x"}], seq_a_state))
check("cross-field: write_set outside read_set is schema-invalid",
      out["outcome"] == "schema")

# Cross-field (iv): a region id outside the frozen set.
out = h.submit(tA, contrib(A, new_id(), {STATE: 1, UNKNOWN: 1},
                           [STATE, UNKNOWN], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "x"}], seq_a_state))
check("cross-field: unknown region id is schema-invalid",
      out["outcome"] == "schema")

# Cross-field (iii): two content operations on one region.
out = h.submit(tA, contrib(A, new_id(), {STATE: 1}, [STATE], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "x"},
                            {"kind": "append_content", "region_id": STATE,
                             "text": "y"}], seq_a_state))
check("cross-field: duplicate content target is schema-invalid",
      out["outcome"] == "schema")

# Cross-field (vi): discovery verification — another agent's DISCOVERY,
# then a nonexistent sequence.
h.open_region(tB, COMPONENTS)
seq_b_comp = last_seq(store)
out = h.submit(tA, contrib(A, new_id(), {STATE: 1}, [STATE], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "x"}], seq_b_comp))
check("discovery_ref naming another agent is schema-invalid",
      out["outcome"] == "schema")
out = h.submit(tA, contrib(A, new_id(), {STATE: 1}, [STATE], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "x"}], 9999))
check("discovery_ref naming no event is schema-invalid",
      out["outcome"] == "schema")

# Hard line — declared reads the record contradicts (both directions).
n_events = len(store.all_events())
try:
    h.submit(tA, contrib(A, new_id(), {STATE: 1, COMPONENTS: 1},
                         [STATE, COMPONENTS], [STATE],
                         [{"kind": "replace_content", "region_id": STATE,
                           "new_content": "x"}], seq_a_state))
    check("hard line: claiming an unmade read stops the run", False)
except HardLineBreach:
    check("hard line: claiming an unmade read stops the run",
          len(store.all_events()) == n_events)
h.open_region(tD, STATE)
h.open_region(tD, COMPONENTS)
seq_d_state = events_of(store, "DISCOVERY")[-2]["event_seq"]
try:
    h.submit(tD, contrib(D, new_id(), {STATE: 1}, [STATE], [STATE],
                         [{"kind": "replace_content", "region_id": STATE,
                           "new_content": "x"}], seq_d_state))
    check("hard line: omitting a made read stops the run", False)
except HardLineBreach:
    check("hard line: omitting a made read stops the run", True)

# A valid contribution commits and bumps the target region's version.
new_state_content = ("State keeps what the system must remember, and "
                     "nothing else. When state changes, the changed "
                     "component is notified directly by State. "
                     "(Wording clarified.)")
out = h.submit(tA, contrib(A, new_id(), {STATE: 1}, [STATE], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": new_state_content}], seq_a_state))
a_contribution = out.get("contribution_id")
check("valid contribution commits; region version bumps",
      out["outcome"] == "accepted"
      and eng.state["regions"][STATE]["version"] == 2
      and eng.state["regions"][STATE]["content"] == new_state_content)
check("replay equals live state after a commit",
      state_hash(eng.replay()) == state_hash(eng.state))

# Disjoint concurrent contributions both commit (section 9 row 6).
h.open_region(tE, PRESENTATION)
seq_e_pres = last_seq(store)

# Staleness — B based its work on State v1; A has since moved it to v2.
h.open_region(tB, STATE)
seq_b_state = last_seq(store)
out = h.submit(tB, contrib(B, new_id(), {COMPONENTS: 1, STATE: 1},
                           [COMPONENTS, STATE], [STATE],
                           [{"kind": "replace_content", "region_id": STATE,
                             "new_content": "B's overtaken edit."}],
                           seq_b_state))
rej = events_of(store, "CONTRIBUTION_REJECTED")[-1]
diff = rej["payload"].get("diff", [])
entry = next((d for d in diff if d["region_id"] == STATE), {})
check("overtaken contribution rejected stale, with the changed-read diff",
      out["outcome"] == "stale" and entry.get("expected_version") == 1
      and entry.get("current_version") == 2
      and entry.get("changed_by") == a_contribution
      and eng.state["regions"][STATE]["version"] == 2)

# Order: staleness fires before structural (Annex D's plant, stale base).
plant_ops = [{"kind": "add_dependency",
              "dependency": {"source": STATE, "target": COMPONENTS,
                             "kind": "uses"}}]
out = h.submit(tB, contrib(B, new_id(), {COMPONENTS: 1, STATE: 1},
                           [COMPONENTS, STATE], [COMPONENTS, STATE],
                           plant_ops, seq_b_state))
check("order: stale plant proposal rejected stale, not structural",
      out["outcome"] == "stale")

# Order: schema fires before staleness.
out = h.submit(tB, contrib(B, new_id(), {COMPONENTS: 1, STATE: 1},
                           [COMPONENTS, STATE], [COMPONENTS, STATE],
                           plant_ops, seq_b_state, rationale=None))
check("order: schema-invalid plant proposal rejected schema, not stale",
      out["outcome"] == "schema")

# The Annex D structural plant, current bases: rejected structural, S3.
out = h.submit(tB, contrib(B, new_id(), {COMPONENTS: 1, STATE: 2},
                           [COMPONENTS, STATE], [COMPONENTS, STATE],
                           plant_ops, seq_b_state))
rej = events_of(store, "CONTRIBUTION_REJECTED")[-1]
check("Annex D plant rejected structural, naming S3",
      out["outcome"] == "structural"
      and rej["payload"].get("invariant") == "S3"
      and {STATE, COMPONENTS} <= set(rej["affected"])
      and len(eng.state["dependencies"]) == 4
      and eng.state["regions"][STATE]["version"] == 2
      and eng.state["regions"][COMPONENTS]["version"] == 1)

# TV-7 — idempotency: identical returns, different conflicts.
K = "70707070-7070-4070-8070-707070707070"
x = contrib(E, K, {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
            [{"kind": "append_content", "region_id": PRESENTATION,
              "text": " (Extended.)"}], seq_e_pres)
out = h.submit(tE, x)
check("TV-7 setup: contribution X accepted",
      out["outcome"] == "accepted"
      and eng.state["regions"][PRESENTATION]["version"] == 2)
n_events = len(store.all_events())
out = h.submit(tE, copy.deepcopy(x))
check("TV-7(i): identical resubmission returns the original outcome, "
      "no new event",
      out["outcome"] == "accepted" and out.get("idempotent_replay") is True
      and len(store.all_events()) == n_events)
y = contrib(E, K, {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
            [{"kind": "append_content", "region_id": PRESENTATION,
              "text": " (Different.)"}], seq_e_pres)
out = h.submit(tE, y)
check("TV-7(ii): different content under the same key conflicts",
      out["outcome"] == "idempotency_conflict"
      and eng.state["regions"][PRESENTATION]["version"] == 2
      and "Different" not in eng.state["regions"][PRESENTATION]["content"])

# Dependency operations commit: both endpoints' versions advance.
h.open_region(tF, STATE)
seq_f_state = last_seq(store)
h.open_region(tF, PRESENTATION)
out = h.submit(tF, contrib(F, new_id(), {STATE: 2, PRESENTATION: 2},
                           [STATE, PRESENTATION], [STATE, PRESENTATION],
                           [{"kind": "add_dependency",
                             "dependency": {"source": PRESENTATION,
                                            "target": STATE,
                                            "kind": "uses"}}], seq_f_state))
new_dep = next((d for d in eng.state["dependencies"].values()
                if d["source"] == PRESENTATION and d["target"] == STATE),
               None)
check("add_dependency commits; both endpoint versions advance",
      out["outcome"] == "accepted" and new_dep is not None
      and new_dep["status"] == "active"
      and eng.state["regions"][STATE]["version"] == 3
      and eng.state["regions"][PRESENTATION]["version"] == 3)
out = h.submit(tF, contrib(F, new_id(), {STATE: 3, PRESENTATION: 3},
                           [STATE, PRESENTATION], [STATE, PRESENTATION],
                           [{"kind": "remove_dependency",
                             "dependency_id": new_dep["dependency_id"]}],
                           seq_f_state))
check("remove_dependency commits; both endpoint versions advance again",
      out["outcome"] == "accepted"
      and eng.state["dependencies"][new_dep["dependency_id"]]["status"]
      == "removed"
      and eng.state["regions"][STATE]["version"] == 4
      and eng.state["regions"][PRESENTATION]["version"] == 4)

# A raise_tension operation commits and raises a semantic tension.
h.open_region(tG, INTERACTIONS)
seq_g_int = last_seq(store)
h.open_region(tG, CONTINUITY)
out = h.submit(tG, contrib(G, new_id(), {INTERACTIONS: 1, CONTINUITY: 1},
                           [INTERACTIONS, CONTINUITY], [],
                           [{"kind": "raise_tension",
                             "tension": {"type": "semantic",
                                         "regions": [INTERACTIONS,
                                                     CONTINUITY],
                                         "description": "Requests are "
                                         "stateless, yet sessions are "
                                         "pinned to one component."}}],
                           seq_g_int))
tensions = list(eng.state["tensions"].values())
raised = events_of(store, "TENSION_RAISED")
check("raise_tension commits; semantic tension stands open",
      out["outcome"] == "accepted" and len(tensions) == 1
      and tensions[0]["type"] == "semantic"
      and tensions[0]["status"] == "open"
      and tensions[0]["origin"] == "contribution"
      and tensions[0]["origin_ref"] == out["contribution_id"]
      and len(raised) == 1
      and raised[0]["event_seq"] == out["event_seq"] + 1)

# UI accounting: every Stage 2 event payload describes itself in
# plain words (the observer's only projection is this history).
stage2_events = [e for e in store.all_events() if e["event_seq"] > 1]
check("every Stage 2 event payload carries a plain-words summary",
      all(isinstance(e["payload"].get("summary"), str)
          and e["payload"]["summary"] for e in stage2_events),
      f"{len(stage2_events)} events")
check("replay equals live state at the end of Run C",
      state_hash(eng.replay()) == state_hash(eng.state))
ok, bad = verify_chain(store.all_events(), CONSTITUTION_HASH)
check("chain verifies at the end of Run C", ok and bad is None)

print()
print("STAGE 2 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)

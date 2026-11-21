"""Engine core: genesis, state derivation, VERIFIED replay.

Loom spec v0.1 Rev 9, section 3 (reconstruction contract) and section 2
invariant 1 (one shared truth).

Stage 2 extension (2026-11-21): the fold now also applies the Stage 2
event types — DISCOVERY, CONTRIBUTION_ACCEPTED, CONTRIBUTION_REJECTED,
TENSION_RAISED, BOUNDARY_PROBE — and Engine.commit_events gives the
harness an atomic append+fold path. Without fold support for these
types, verified replay would halt on any Stage 2 history and no
trustworthy state could be derived from it (the C2 defect class, one
stage up). Stage 1 behaviour for RUN_OPENED histories is unchanged.

Stage 2 corrections round (2026-11-21): the fold also applies the two
new event types. IDLE is an evidence record (no fabric-state change).
RUN_FAILED folds to a terminal failed state: the keys "run_status"
and "failure" appear in the derived state ONLY when a RUN_FAILED
event is present, so a healthy run's derived state — and its genesis
state hash — is byte-identical to before this round, while a failed
run replays AS failed, never as a healthy run with an unusual event
in its history (Vane's correction conditions, section 3).

Stage 1 correction C2 (Vane's implementation examination, 2026-11-21):
the first version folded events without verifying the chain, so state
could be derived from a corrupted history and presented as trustworthy.
Verified replay is now a single coherent operation: each event's link
is validated as it is consumed — gapless sequence, prev_hash matching
the running head, the event's hash recomputed, exactly one RUN_OPENED
at sequence 1 rooted in the constitution hash — and the first invalid
sequence raises ReplayHalt. No state derived from an invalid history is
ever presented. A system that can detect a corrupted history is not yet
a system that refuses to derive authoritative state from one; Rev 9
requires both.
"""
import copy

from .canonical import canonical, sha256_hex, event_hash
from .fixture import CONSTITUTION_HASH, SYSTEM_ACTOR, genesis_payload
from .store import EventStore


class ReplayHalt(Exception):
    def __init__(self, seq, reason):
        super().__init__(f"replay halted at seq {seq}: {reason}")
        self.seq = seq
        self.reason = reason


def empty_state() -> dict:
    return {
        "regions": {},        # region_id -> region record
        "dependencies": {},   # dependency_id -> dependency record
        "tensions": {},       # tension_id -> tension record
        "assessments": {},    # assessment_id -> recorded assessment
        "completion_claims": {},  # claim_id -> completion claim
        "claims": {},         # claim_id -> claim
        "watches": {},        # watch_id -> watch
        "facet_status": {},   # region_id -> status
        "contributions": {},  # contribution_id -> accepted contribution
        "last_seq": 0,
    }


def _apply_operations(state: dict, contribution: dict, payload: dict) -> None:
    """Apply an accepted contribution's operations to state, in place.

    Shared by the fold (CONTRIBUTION_ACCEPTED) and by the harness's
    structural check, which applies the same operations hypothetically
    to a copy of the current state (spec section 4, step 3). A region's
    version advances once per accepted operation touching it — a
    content operation on it, or a dependency operation having it as an
    endpoint (section 3: version advances on ANY accepted change
    touching it). Dependency ids assigned at commit are read from the
    event payload, so the fold is deterministic from the history alone.
    A raise_tension operation applies nothing here: its effect is the
    TENSION_RAISED event that follows the acceptance (the same split
    section 4 uses for ExaminationReports)."""
    regions = state["regions"]
    deps = state["dependencies"]
    for i, op in enumerate(contribution["operations"]):
        kind = op["kind"]
        if kind == "replace_content":
            region = regions[op["region_id"]]
            region["content"] = op["new_content"]
            region["version"] += 1
        elif kind == "append_content":
            region = regions[op["region_id"]]
            region["content"] = region["content"] + op["text"]
            region["version"] += 1
        elif kind == "add_dependency":
            dep_id = payload["assigned_dependency_ids"][str(i)]
            dep = {
                "dependency_id": dep_id,
                "source": op["dependency"]["source"],
                "target": op["dependency"]["target"],
                "kind": op["dependency"]["kind"],
                "status": "active",
            }
            deps[dep_id] = dep
            regions[dep["source"]]["version"] += 1
            regions[dep["target"]]["version"] += 1
        elif kind == "remove_dependency":
            dep = deps[op["dependency_id"]]
            dep["status"] = "removed"
            regions[dep["source"]]["version"] += 1
            regions[dep["target"]]["version"] += 1
        elif kind == "raise_tension":
            pass  # effected by the TENSION_RAISED event that follows


def apply_event(state: dict, event: dict) -> dict:
    """Fold one event into the state. Unknown types, and a RUN_OPENED
    anywhere but sequence 1, halt replay."""
    t = event["type"]
    if t == "RUN_OPENED":
        if event["event_seq"] != 1:
            raise ReplayHalt(event["event_seq"],
                             "RUN_OPENED is only valid at sequence 1")
        payload = event["payload"]
        for r in payload["regions"]:
            state["regions"][r["region_id"]] = copy.deepcopy(r)
        for d in payload["dependencies"]:
            state["dependencies"][d["dependency_id"]] = copy.deepcopy(d)
        state["last_seq"] = event["event_seq"]
        return state
    if t in ("DISCOVERY", "CONTRIBUTION_REJECTED", "BOUNDARY_PROBE",
             "IDLE"):
        # Evidence and outcome records: they change no fabric state.
        state["last_seq"] = event["event_seq"]
        return state
    if t == "RUN_FAILED":
        # Terminal: once failed, the run stays failed whatever follows
        # in the history (nothing legitimate follows — the boundary
        # refuses further agent activity — but the fold does not
        # resurrect a failed run even from a doctored tail).
        p = event["payload"]
        state["run_status"] = "failed"
        state["failure"] = {
            "event_seq": event["event_seq"],
            "breach": p.get("breach"),
            "summary": p.get("summary"),
        }
        state["last_seq"] = event["event_seq"]
        return state
    if t == "CONTRIBUTION_ACCEPTED":
        payload = event["payload"]
        _apply_operations(state, payload["contribution"], payload)
        state["contributions"][payload["contribution_id"]] = copy.deepcopy(
            payload["contribution"])
        state["last_seq"] = event["event_seq"]
        return state
    if t == "TENSION_RAISED":
        p = event["payload"]
        state["tensions"][p["tension_id"]] = {
            "tension_id": p["tension_id"],
            "type": p["type"],
            "regions": list(p["regions"]),
            "origin": p["origin"],
            "origin_ref": p["origin_ref"],
            "description": p["description"],
            "status": p["status"],
        }
        state["last_seq"] = event["event_seq"]
        return state
    raise ReplayHalt(event["event_seq"], f"unhandled event type {t}")


def state_hash(state: dict) -> str:
    return sha256_hex(canonical(state))


def _link_error(events, constitution_hash: str, upto: int):
    """Validate the chain link of events[upto-1] against its prefix.
    Returns a reason string, or None if the link is valid."""
    ev = events[upto - 1]
    if ev["event_seq"] != upto:
        return "sequence is not gapless"
    expected_prev = constitution_hash if upto == 1 else events[upto - 2]["hash"]
    if ev["prev_hash"] != expected_prev:
        return "prev_hash does not match the running chain head"
    body = {k: ev[k] for k in
            ("event_seq", "event_id", "type", "actor", "affected",
             "payload", "prev_hash")}
    if event_hash(ev["prev_hash"], body) != ev["hash"]:
        return "event hash does not recompute"
    if upto == 1 and ev["type"] != "RUN_OPENED":
        return "first event is not RUN_OPENED"
    return None


def verify_chain(events, constitution_hash: str):
    """Hash-chain integrity ONLY: return (ok, bad_seq). An empty history
    is NOT a valid chain: there is no genesis, so nothing can be
    derived from it. NOTE (kept explicit at Vane's direction,
    2026-11-21): this is not interchangeable with verified_fold below —
    verify_chain checks that the chain is intact; verified_fold
    additionally enforces the state transitions as it derives state.
    A caller that needs trustworthy STATE needs the fold."""
    if not events:
        return False, 1
    for i in range(1, len(events) + 1):
        if _link_error(events, constitution_hash, i) is not None:
            return False, i
    return True, None


def verified_fold(events, constitution_hash: str) -> dict:
    """The reconstruction contract as one operation: validate each link
    as its event is consumed; halt at the first invalid sequence."""
    if not events:
        raise ReplayHalt(1, "empty history: no genesis event")
    state = empty_state()
    for i, ev in enumerate(events, start=1):
        err = _link_error(events, constitution_hash, i)
        if err is not None:
            raise ReplayHalt(i, err)
        state = apply_event(state, ev)
    return state


class Engine:
    def __init__(self, store: EventStore):
        self.store = store
        events = store.all_events()
        # An engine over an empty store is pre-genesis and claims no
        # state; over any non-empty history it holds only verified state.
        self.state = (verified_fold(events, CONSTITUTION_HASH)
                      if events else empty_state())

    @classmethod
    def open_run(cls, store: EventStore, run_id: str) -> "Engine":
        assert store.last() is None, "store already holds a run"
        payload = genesis_payload()
        store.insert_run(run_id, CONSTITUTION_HASH)
        ev = store.append("RUN_OPENED", SYSTEM_ACTOR, [], payload,
                          prev_hash=CONSTITUTION_HASH)
        genesis_hash = state_hash(apply_event(empty_state(), ev))
        store.set_genesis_state_hash(run_id, genesis_hash)
        store.commit()
        return cls(store)

    def replay(self):
        """Rebuild state from the event history alone, verified (s.3)."""
        return verified_fold(self.store.all_events(), CONSTITUTION_HASH)

    def commit_events(self, events_spec) -> list:
        """Append a group of events atomically and fold them into the
        live state — the harness's commit path (Stage 2). events_spec
        is a list of (type, actor, affected, payload). Sequence
        assignment, state change, and append occur in one store
        transaction (section 3): on any failure the transaction is
        rolled back and the live state is not swapped."""
        new_state = copy.deepcopy(self.state)
        appended = []
        last = self.store.last()
        head = last[1] if last else CONSTITUTION_HASH
        try:
            for type_, actor, affected, payload in events_spec:
                ev = self.store.append(type_, actor, affected, payload,
                                       prev_hash=head)
                head = ev["hash"]
                new_state = apply_event(new_state, ev)
                appended.append(ev)
            self.store.commit()
        except Exception:
            self.store.rollback()
            raise
        self.state = new_state
        return appended

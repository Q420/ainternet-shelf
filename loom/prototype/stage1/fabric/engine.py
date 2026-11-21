"""Engine core: genesis, state derivation, replay, chain verification.

Loom spec v0.1 Rev 9, section 3 (reconstruction contract) and section 2
invariant 1 (one shared truth). Later stages add the commit protocol,
the examination action, tension protocols, completion, and seals; the
fold below grows by event type and halts on anything it does not know,
per the contract: replay encountering an invalid transition halts at
that sequence and the state from that point is UNKNOWN.
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
        "facet_status": {},   # region_id -> status (required facets tracked)
        "contributions": {},  # contribution_id -> accepted contribution
        "last_seq": 0,
    }


def apply_event(state: dict, event: dict) -> dict:
    """Fold one event into the state. Stage 1 knows RUN_OPENED only;
    later stages register the rest. Unknown types halt replay."""
    t = event["type"]
    if t == "RUN_OPENED":
        payload = event["payload"]
        for r in payload["regions"]:
            state["regions"][r["region_id"]] = copy.deepcopy(r)
        for d in payload["dependencies"]:
            state["dependencies"][d["dependency_id"]] = copy.deepcopy(d)
        state["last_seq"] = event["event_seq"]
        return state
    raise ReplayHalt(event["event_seq"], f"unhandled event type {t}")


def state_hash(state: dict) -> str:
    return sha256_hex(canonical(state))


def verify_chain(events, constitution_hash: str):
    """Return (ok, bad_seq). Checks gapless seq from 1, genesis prev_hash
    equals the constitution hash, and every hash link."""
    prev = constitution_hash
    for i, ev in enumerate(events, start=1):
        if ev["event_seq"] != i:
            return False, i
        if ev["prev_hash"] != prev:
            return False, i
        body = {k: ev[k] for k in
                ("event_seq", "event_id", "type", "actor", "affected",
                 "payload", "prev_hash")}
        if event_hash(ev["prev_hash"], body) != ev["hash"]:
            return False, i
        prev = ev["hash"]
    return True, None


class Engine:
    def __init__(self, store: EventStore):
        self.store = store
        self.state = empty_state()
        for ev in store.all_events():
            self.state = apply_event(self.state, ev)

    @classmethod
    def open_run(cls, store: EventStore, run_id: str) -> "Engine":
        assert store.last() is None, "store already holds a run"
        payload = genesis_payload()
        store.conn.execute(
            "INSERT INTO runs (run_id, constitution_hash) VALUES (?,?)",
            (run_id, CONSTITUTION_HASH),
        )
        ev = store.append("RUN_OPENED", SYSTEM_ACTOR, [], payload,
                          prev_hash=CONSTITUTION_HASH)
        genesis_hash = state_hash(apply_event(empty_state(), ev))
        store.conn.execute(
            "UPDATE runs SET genesis_state_hash=? WHERE run_id=?",
            (genesis_hash, run_id),
        )
        store.commit()
        return cls(store)

    def replay(self):
        """Rebuild state from the event history alone (s.3 contract)."""
        state = empty_state()
        for ev in self.store.all_events():
            state = apply_event(state, ev)
        return state

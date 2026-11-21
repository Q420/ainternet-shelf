"""Engine core: genesis, state derivation, VERIFIED replay.

Loom spec v0.1 Rev 9, section 3 (reconstruction contract) and section 2
invariant 1 (one shared truth).

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


def apply_event(state: dict, event: dict) -> dict:
    """Fold one event into the state. Stage 1 knows RUN_OPENED only;
    later stages register the rest. Unknown types, and a RUN_OPENED
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
    """Return (ok, bad_seq). An empty history is NOT a valid chain:
    there is no genesis, so nothing can be derived from it."""
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

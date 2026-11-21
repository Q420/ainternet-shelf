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

Stage 3 extension (2026-11-21): the fold now also applies the Stage 3
event types — ASSESSMENT_RECORDED (a recorded assessment enters the
assessments registry; a rejected one creates no record, per section
3), EXAMINATION_RECORDED (no record-state change: a created tension
arrives as the TENSION_RAISED event that follows it, the same split
section 4 uses for contributions), COMPLETION_CLAIMED (a recorded
claim enters the completion-claims registry with its claimant bound
from the event payload — the token identity, never a submitted
field), TENSION_STATUS (a tension's recorded transition; the fold
refuses a transition whose named from-status is not the folded
status, so a doctored or mis-sequenced history halts replay rather
than deriving from it), and FACET_STATUS (a facet's recorded status
change, sparse in the state: a facet with no FACET_STATUS event
stands at the initial status "open", so the genesis fold — and its
state hash — is byte-identical to Stage 2's).

Stage 3 corrections round (2026-11-21, B1 of Vane's Stage 3
implementation examination): the fold no longer merely records the
transitions it is told happened — it refuses to reconstruct
transitions the constitution does not permit. TENSION_RAISED now
enforces the permitted type/origin/initial-status combinations
(semantic: contribution or examination origin, initially open;
structural: checker origin, initially open). TENSION_STATUS now
enforces the type-specific transition table (semantic: open →
examined, examined → resolved, examined → standing; structural:
open → resolved only; resolved and standing are terminal for both
types), in addition to the existing from-status check. FACET_STATUS
now validates its to-status against the six-status enumeration.
Each violation halts replay with ReplayHalt at the offending
sequence, exactly as a from-status mismatch already did: a
hash-valid but protocol-invalid history yields no state.

Stage 4 extension (2026-11-21): the fold now also applies
SEAL_ATTEMPTED (evidence-only: the seal record stands in the event
payload; the fold derives no state from it, exactly as it treats
DISCOVERY) and RUN_CLOSED (sparse: "run_status" becomes "closed"
only when a RUN_CLOSED event is present and the run has not
failed, so a healthy open run's derived state — and the genesis
state hash — is byte-identical to Stage 3's). Three further
changes ride with the stage:

- ReplayHalt carries a reason CLASS beside its prose reason, in
  the pinned validation pack's taxonomy: hash_chain_invalid,
  sequence_invalid, schema_invalid (a field value violating its
  type or enumeration, a missing required field, an event type
  outside the bound schema), protocol_transition_invalid
  (individually valid values in a forbidden combination or
  transition). The prose reasons are unchanged.
- Malformed-payload hardening (the obligation carried from
  Vane's Stage 3 acceptance): a hash-valid event whose payload
  fields are unhashable or wrongly typed (a tension type carried
  as an array, a transition from/to as an object) halts replay
  with a controlled ReplayHalt classed schema_invalid — never a
  native TypeError or KeyError escaping the fold. apply_event
  validates the enum fields of TENSION_RAISED / TENSION_STATUS /
  FACET_STATUS explicitly (so the classes come out right) and a
  guard around the fold converts any remaining KeyError /
  TypeError / AttributeError from a malformed payload into the
  same controlled halt.
- The fold enforces the authority set bound in RUN_OPENED
  (VP-15): a run whose bound amendments do not include A1 halts
  with schema_invalid at an IDLE event, because IDLE is not in
  the event schema Rev 9 alone binds. A RUN_OPENED with no
  authority_set (every pre-Stage-4 run) is read under the set in
  force when those runs were opened — Rev 9 + A1 — so their
  folds are unchanged. A checker-raised tension's folded record
  also carries its structural identity (check + affected set,
  notes I-9) when the payload carries them.

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
from .packpin import PACK_ID, PACK_SHA256, PACK_VERSION
from .store import EventStore


class ReplayHalt(Exception):
    def __init__(self, seq, reason, reason_class=None):
        super().__init__(f"replay halted at seq {seq}: {reason}")
        self.seq = seq
        self.reason = reason
        # Stage 4: the halt's class in the validation pack's pinned
        # taxonomy (schema_invalid / protocol_transition_invalid /
        # hash_chain_invalid / sequence_invalid). Older raise sites
        # that predate the taxonomy leave it None.
        self.reason_class = reason_class


# The tension lifecycle the fold will reconstruct (Rev 9 sections 3
# and 4; Stage 3 corrections round, B1). A tension is raised in
# exactly one permitted combination per type, and moves only along
# its type's transitions; resolved and standing are terminal.
_TENSION_RAISED_ORIGINS = {
    "semantic": ("contribution", "examination"),
    "structural": ("checker",),
}
_TENSION_TRANSITIONS = {
    "semantic": {("open", "examined"), ("examined", "resolved"),
                 ("examined", "standing")},
    "structural": {("open", "resolved")},
}
# Section 5's facet status set, in precedence order.
_FACET_STATUSES = ("open", "unexamined", "claimed", "complete",
                   "disputed", "stood_down")


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
    anywhere but sequence 1, halt replay. Stage 4 hardening: a
    malformed payload (missing fields, unhashable or wrongly typed
    values) surfaces as a controlled ReplayHalt classed
    schema_invalid, never as a native exception."""
    try:
        return _apply_event(state, event)
    except ReplayHalt:
        raise
    except (KeyError, TypeError, AttributeError) as exc:
        raise ReplayHalt(
            event.get("event_seq"), 
            f"malformed event payload: {type(exc).__name__}: {exc}",
            "schema_invalid") from exc


def _apply_event(state: dict, event: dict) -> dict:
    t = event["type"]
    if t == "RUN_OPENED":
        if event["event_seq"] != 1:
            raise ReplayHalt(event["event_seq"],
                             "RUN_OPENED is only valid at sequence 1",
                             "schema_invalid")
        payload = event["payload"]
        for r in payload["regions"]:
            state["regions"][r["region_id"]] = copy.deepcopy(r)
        for d in payload["dependencies"]:
            state["dependencies"][d["dependency_id"]] = copy.deepcopy(d)
        state["last_seq"] = event["event_seq"]
        return state
    if t in ("DISCOVERY", "CONTRIBUTION_REJECTED", "BOUNDARY_PROBE",
             "IDLE", "PROBE_SESSION_OPENED", "PROBE_EVIDENCE",
             "SEAL_ATTEMPTED"):
        # Evidence and outcome records: they change no fabric state.
        # (The last two are twin-local probe-execution evidence —
        # corrections round 4 — and appear only in a disposable
        # twin's history, never in an experimental one.)
        # SEAL_ATTEMPTED (Stage 4) is evidence in the same sense:
        # the seal record stands in the event payload, and what a
        # seal attempt changes — structural tensions — arrives as
        # the TENSION_RAISED / TENSION_STATUS events that follow it
        # in the same atomic group.
        state["last_seq"] = event["event_seq"]
        return state
    if t == "RUN_CLOSED":
        # Sparse, like RUN_FAILED: the key appears only when a
        # RUN_CLOSED event is present, and a failed run stays
        # failed — closing never resurrects it.
        if "run_status" not in state:
            state["run_status"] = "closed"
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
        # Stage 4 hardening: the enum fields are type-checked
        # explicitly, so a malformed value (an array for the type,
        # an object for the origin) is classed schema_invalid,
        # while individually valid values in a forbidden
        # combination are classed protocol_transition_invalid —
        # the pack's pinned taxonomy (VP-07, VP-10, VP-11). A
        # missing field reaches the guard in apply_event and is
        # classed schema_invalid there.
        if not isinstance(p["type"], str) \
                or not isinstance(p["origin"], str) \
                or not isinstance(p["status"], str):
            raise ReplayHalt(
                event["event_seq"],
                "TENSION_RAISED carries a non-string type, origin, "
                "or status: the event fails its schema",
                "schema_invalid")
        origins = _TENSION_RAISED_ORIGINS.get(p["type"])
        if origins is None:
            raise ReplayHalt(
                event["event_seq"],
                f"TENSION_RAISED names unknown tension type "
                f"{p['type']!r}",
                "schema_invalid")
        if p["origin"] not in origins:
            raise ReplayHalt(
                event["event_seq"],
                f"TENSION_RAISED for a {p['type']} tension names "
                f"origin {p['origin']!r}; permitted origins are "
                f"{', '.join(origins)}",
                "protocol_transition_invalid")
        if p["status"] != "open":
            raise ReplayHalt(
                event["event_seq"],
                f"TENSION_RAISED names initial status "
                f"{p['status']!r}; a tension is raised open",
                "protocol_transition_invalid"
                if p["status"] in ("examined", "resolved", "standing")
                else "schema_invalid")
        record = {
            "tension_id": p["tension_id"],
            "type": p["type"],
            "regions": list(p["regions"]),
            "origin": p["origin"],
            "origin_ref": p["origin_ref"],
            "description": p["description"],
            "status": p["status"],
        }
        # Stage 4 (notes I-9): a checker-raised tension's record
        # carries its structural identity — the check name and the
        # canonically sorted affected record set — so the identity
        # the lifecycle deduplicates and resolves against is
        # reconstructible from the history alone.
        if "check" in p:
            record["check"] = p["check"]
        if "affected" in p:
            record["affected"] = list(p["affected"])
        state["tensions"][p["tension_id"]] = record
        state["last_seq"] = event["event_seq"]
        return state
    if t == "EXAMINATION_RECORDED":
        # The report and its outcome stand in the event itself; a
        # tension it created arrives as the TENSION_RAISED event
        # that follows. No record state changes here.
        state["last_seq"] = event["event_seq"]
        return state
    if t == "ASSESSMENT_RECORDED":
        p = event["payload"]
        if p.get("outcome") == "recorded":
            assessment = copy.deepcopy(p["assessment"])
            state["assessments"][assessment["assessment_id"]] = assessment
        # A rejected assessment creates no record (section 3, B3).
        state["last_seq"] = event["event_seq"]
        return state
    if t == "COMPLETION_CLAIMED":
        p = event["payload"]
        if p.get("outcome") == "recorded":
            record = copy.deepcopy(p["claim"])
            # The claimant is the token identity the service bound
            # into the payload; the submitted claim carries no
            # claimant field (Stage 3 claim contract).
            record["claimant"] = p["claimant"]
            state["completion_claims"][record["claim_id"]] = record
        state["last_seq"] = event["event_seq"]
        return state
    if t == "TENSION_STATUS":
        p = event["payload"]
        # Stage 4 hardening (VP-08, VP-09): non-string from/to
        # values are schema failures, never a native TypeError
        # from the transition-set lookup.
        if not isinstance(p["from"], str) \
                or not isinstance(p["to"], str):
            raise ReplayHalt(
                event["event_seq"],
                "TENSION_STATUS carries a non-string from or to "
                "status: the event fails its schema",
                "schema_invalid")
        tension = state["tensions"].get(p["tension_id"])
        if tension is None:
            raise ReplayHalt(
                event["event_seq"],
                f"TENSION_STATUS names unknown tension {p['tension_id']}",
                "protocol_transition_invalid")
        if tension["status"] != p["from"]:
            raise ReplayHalt(
                event["event_seq"],
                f"TENSION_STATUS for {p['tension_id']} claims "
                f"from-status {p['from']!r} but the folded status is "
                f"{tension['status']!r}: an invalid transition",
                "protocol_transition_invalid")
        permitted = _TENSION_TRANSITIONS.get(tension["type"], set())
        if (p["from"], p["to"]) not in permitted:
            raise ReplayHalt(
                event["event_seq"],
                f"TENSION_STATUS for {p['tension_id']} moves a "
                f"{tension['type']} tension from {p['from']!r} to "
                f"{p['to']!r}: not a permitted transition for its "
                f"type (resolved and standing are terminal)",
                "protocol_transition_invalid")
        tension["status"] = p["to"]
        state["last_seq"] = event["event_seq"]
        return state
    if t == "FACET_STATUS":
        p = event["payload"]
        # Stage 4 (VP-14): a status outside the enumeration is a
        # schema failure; a target outside the six frozen regions
        # is a protocol failure. Both are checked before the
        # from-status comparison so the classes come out as pinned.
        if not isinstance(p["to"], str) \
                or p["to"] not in _FACET_STATUSES:
            raise ReplayHalt(
                event["event_seq"],
                f"FACET_STATUS for {p['region_id']} names "
                f"to-status {p['to']!r}; the permitted facet "
                f"statuses are {', '.join(_FACET_STATUSES)}",
                "schema_invalid")
        if p["region_id"] not in state["regions"]:
            raise ReplayHalt(
                event["event_seq"],
                f"FACET_STATUS names region {p['region_id']!r}, "
                f"which is outside the six frozen regions",
                "protocol_transition_invalid")
        current = state["facet_status"].get(p["region_id"], "open")
        if current != p["from"]:
            raise ReplayHalt(
                event["event_seq"],
                f"FACET_STATUS for {p['region_id']} claims "
                f"from-status {p['from']!r} but the folded status is "
                f"{current!r}: an invalid transition",
                "protocol_transition_invalid")
        state["facet_status"][p["region_id"]] = p["to"]
        state["last_seq"] = event["event_seq"]
        return state
    raise ReplayHalt(event["event_seq"], f"unhandled event type {t}",
                     "schema_invalid")


def state_hash(state: dict) -> str:
    return sha256_hex(canonical(state))


def _link_error(events, constitution_hash: str, upto: int):
    """Validate the chain link of events[upto-1] against its prefix.
    Returns (reason, reason_class), or None if the link is valid."""
    ev = events[upto - 1]
    if ev["event_seq"] != upto:
        return "sequence is not gapless", "sequence_invalid"
    expected_prev = constitution_hash if upto == 1 else events[upto - 2]["hash"]
    if ev["prev_hash"] != expected_prev:
        return ("prev_hash does not match the running chain head",
                "hash_chain_invalid")
    body = {k: ev[k] for k in
            ("event_seq", "event_id", "type", "actor", "affected",
             "payload", "prev_hash")}
    if event_hash(ev["prev_hash"], body) != ev["hash"]:
        return "event hash does not recompute", "hash_chain_invalid"
    if upto == 1 and ev["type"] != "RUN_OPENED":
        return "first event is not RUN_OPENED", "schema_invalid"
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
        raise ReplayHalt(1, "empty history: no genesis event",
                         "schema_invalid")
    state = empty_state()
    # VP-15: the authority set bound in RUN_OPENED governs the fold.
    # A1 is in force unless the bound set names its amendments and
    # A1 is not among them; a RUN_OPENED with no authority_set (every
    # pre-Stage-4 run) is read under Rev 9 + A1, the set in force
    # when those runs were opened.
    a1_in_force = True
    for i, ev in enumerate(events, start=1):
        err = _link_error(events, constitution_hash, i)
        if err is not None:
            raise ReplayHalt(i, err[0], err[1])
        if i == 1 and ev["type"] == "RUN_OPENED":
            payload = ev["payload"]
            auth = payload.get("authority_set") \
                if isinstance(payload, dict) else None
            if isinstance(auth, dict) \
                    and isinstance(auth.get("amendments"), list):
                a1_in_force = "A1" in auth["amendments"]
        if ev["type"] == "IDLE" and not a1_in_force:
            raise ReplayHalt(
                i,
                "IDLE is not in the event schema bound by this "
                "run's authority set (Rev 9 without Amendment A1)",
                "schema_invalid")
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
    def open_run(cls, store: EventStore, run_id: str,
                 binding: dict = None) -> "Engine":
        assert store.last() is None, "store already holds a run"
        payload = genesis_payload()
        if binding is not None:
            # Stage 4 (VP-55): a run opened under Stage 4 binds its
            # authority set and the exact validation pack in the
            # RUN_OPENED payload. A pack identity or digest that
            # differs from the pinned pack blocks the opening —
            # raised here, before anything is appended.
            pack = binding.get("validation_pack") \
                if isinstance(binding, dict) else None
            if isinstance(pack, dict):
                if pack.get("id") != PACK_ID \
                        or pack.get("version") != PACK_VERSION \
                        or pack.get("sha256") != PACK_SHA256:
                    raise ValueError(
                        "the supplied validation pack does not "
                        "match the pinned Stage 4 pack (id "
                        f"{PACK_ID}, version {PACK_VERSION}, "
                        f"sha256 {PACK_SHA256}); the run does "
                        "not open")
            payload = {**payload, **binding}
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
                # Stage 4 correction round 2 (C2-B2): the live
                # state is a CACHE of the fold, and a corrupted
                # cache (the TV-1 fault: a dropped region record)
                # cannot fold an event that touches the dropped
                # state — a FACET_STATUS for the dropped region,
                # say. Such an event is nevertheless valid: the
                # harness validated and planned it against the
                # authoritative fold before committing. The cache
                # therefore keeps its pre-event value for that
                # event instead of vetoing the commit; the history
                # is the truth, the corruption persists in the
                # cache exactly as it stood, and the I-5 rebuild
                # (verified replay) is what heals it. On any
                # unfaulted history the guard never fires and this
                # path is the original append+fold, byte for byte.
                try:
                    new_state = apply_event(new_state, ev)
                except ReplayHalt:
                    pass
                appended.append(ev)
            self.store.commit()
        except Exception:
            self.store.rollback()
            raise
        self.state = new_state
        return appended

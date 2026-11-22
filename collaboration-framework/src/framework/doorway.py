"""Seat doorway — SPEC SHEET §3.2 (substrate harness, adapted).

The only route by which a seat touches the record.

- R5. Each seat acts under a token bound to its recorded identity;
  acts from unbound or mismatched identities are rejected.
- R6. The §4 authority matrix is enforced mechanically; an act
  outside the seat's authority is rejected and the rejection is
  recorded as a REJECTION event authored by the doorway.
- R7. Reads of sealed material outside the seat's evidence boundary
  are rejected and recorded.
- R30. Acts for a paused tree part (or its recorded downstream) are
  blocked; unrelated branches validate normally.
- R31. Every act carries the record position of the view it was made
  from. A subject changed since that view: reject + record.
  Otherwise, a behind-view act is recorded flagged `stale-basis`.

Seat bindings are read from the record itself (RUN_COMMISSIONED seats
/ SEAT_BOUND events). Onboarding proper (§3.6) is a later piece; this
doorway consumes the bindings the record carries.
"""
import hashlib
import secrets

from .record import (FrameworkStore, GATE_OUTCOMES, fold,
                     validate_status_transition)

DOORWAY_ACTOR = "doorway"

# §4 authority matrix — which roles may record which act types.
# (Claim-status transitions are governed separately by R2; case
# issue/correction by §3.5's three acts in their own piece — here the
# doorway checks the matrix row only.)
ACT_AUTHORITY = {
    "CONTRIBUTION": {"crew"},
    "COMMENT": {"crew"},
    "DISAGREEMENT": {"crew", "orchestrator", "examiner", "director"},
    "DISAGREEMENT_SETTLED": {"crew", "orchestrator", "examiner",
                             "director"},
    "COMPLETION_CLAIMED": {"crew"},
    "CASE_ISSUED": {"orchestrator"},
    "CASE_CORRECTED": {"orchestrator"},
    "GATE_OUTCOME": {"examiner"},
    "FINDING": {"examiner"},
    "CERTIFICATION": {"examiner"},
    "RULING": {"director"},
    "DISPOSITION": {"director"},
    "ESCALATION": {"crew", "orchestrator", "examiner"},
    "CLAIM_STATUS": {"crew", "orchestrator", "examiner", "director"},
    "ONBOARDING": {"orchestrator"},
    "SEAT_BOUND": {"orchestrator", "director"},
    "MATERIAL_SEALED": {"orchestrator"},
    "RUN_CLOSED": {"orchestrator", "director"},
}


class DoorwayRefusal(Exception):
    def __init__(self, ground):
        super().__init__(ground)
        self.ground = ground


class Doorway:
    def __init__(self, store: FrameworkStore):
        self.store = store
        self._tokens = {}  # sha256(token) -> seat_id

    # ------------------------------------------------------------ state
    def state(self):
        return fold(self.store.all_events(), self.store.get_run_id())

    # ------------------------------------------------------------ tokens
    def issue_token(self, seat_id: str) -> str:
        """Bind a fresh token to a seat the record knows (R5)."""
        state = self.state()
        if seat_id not in state["seats"]:
            raise DoorwayRefusal(f"seat {seat_id} is not bound in the "
                                 "record; no token issues (R5)")
        token = secrets.token_hex(24)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._tokens[digest] = seat_id
        return token

    def _authenticate(self, token):
        if not token:
            return None
        digest = hashlib.sha256(token.encode()).hexdigest()
        return self._tokens.get(digest)

    # ------------------------------------------------------------ record
    def _record_rejection(self, seat_id, attempted_type, ground,
                          view_seq=None):
        ev = self.store.append(
            "REJECTION", DOORWAY_ACTOR, [seat_id or "unbound"],
            {"seat": seat_id, "attempted_type": attempted_type,
             "ground": ground, "view_seq": view_seq},
        )
        self.store.commit()
        return ev

    def _refuse(self, seat_id, attempted_type, ground, view_seq=None):
        self._record_rejection(seat_id, attempted_type, ground, view_seq)
        raise DoorwayRefusal(ground)

    # ------------------------------------------------------------ acts
    def act(self, token, type_, payload, view_seq=None):
        """Record one act through the doorway, or refuse it — with
        the refusal itself recorded. Returns the recorded event."""
        seat_id = self._authenticate(token)
        if seat_id is None:
            self._refuse(None, type_,
                         "unbound or mismatched identity (R5)", view_seq)
        state = self.state()
        binding = state["seats"].get(seat_id)
        if binding is None:
            self._refuse(seat_id, type_,
                         "seat not bound in the record (R5)", view_seq)
        role = binding["role"]

        # R31: the view position is mandatory — every proposed act
        # carries the record position of the view it was made from.
        # An act without one (or from beyond the head) is refused
        # and the refusal recorded, like any other.
        if view_seq is None:
            self._refuse(seat_id, type_,
                         "every proposed act carries the record "
                         "position of the view it was made from (R31)")
        if view_seq < 0:
            self._refuse(seat_id, type_,
                         f"view position {view_seq} is not a valid "
                         "position in the record (R31)", view_seq)
        if view_seq > state["head_seq"]:
            self._refuse(seat_id, type_,
                         f"view position {view_seq} is beyond the "
                         f"record head {state['head_seq']} (R31)",
                         view_seq)

        # R6 / §4: authority.
        allowed = ACT_AUTHORITY.get(type_)
        if allowed is None:
            self._refuse(seat_id, type_,
                         f"{type_} is not a doorway act", view_seq)
        if role not in allowed:
            self._refuse(seat_id, type_,
                         f"{role} may not record {type_} "
                         "(authority matrix, §4)", view_seq)

        # R2: claim-status transitions carry their own authority.
        if type_ == "CLAIM_STATUS":
            ok, ground = validate_status_transition(
                state, seat_id, role, payload.get("claim_id"),
                payload.get("to"), evidence=payload.get("evidence"),
                gate_joint=payload.get("gate_joint"))
            if not ok:
                self._refuse(seat_id, type_, ground, view_seq)

        # R22: gate outcomes are exactly allow / correct / escalate.
        if type_ == "GATE_OUTCOME" and \
                payload.get("outcome") not in GATE_OUTCOMES:
            self._refuse(seat_id, type_,
                         f"gate outcome {payload.get('outcome')!r} is "
                         "not in the R22 vocabulary (allow, correct, "
                         "escalate)", view_seq)

        # R30 (correction round 3): every gate outcome names its
        # joint, and an allow releases only pauses that same joint
        # recorded. A release naming another gate's pause — or a part
        # not paused at all — is refused and recorded.
        if type_ == "GATE_OUTCOME":
            if not payload.get("joint"):
                self._refuse(seat_id, type_,
                             "a gate outcome names its joint (R30)",
                             view_seq)
            if payload.get("outcome") == "allow":
                for part in payload.get("paused_set", []) + \
                        payload.get("released_set", []):
                    entry = state["paused"].get(part)
                    if entry is None or \
                            entry.get("source_joint") != \
                            payload.get("joint"):
                        self._refuse(
                            seat_id, type_,
                            f"release of {part} is not bound to this "
                            f"gate: the recorded pause names joint "
                            f"{entry.get('source_joint') if entry else None} "
                            "(R30)", view_seq)

        # R30 (correction round 2): a pause's set is computed from
        # the tree the record carries, not accepted from the caller.
        # When the record carries a tree, the act names the affected
        # part; the doorway computes the part plus all its transitive
        # downstream dependents, and a caller-supplied set that
        # disagrees is refused and recorded. When no tree stands in
        # the record yet (the tree-carrying piece is later), a
        # supplied set is recorded flagged as caller-supplied — the
        # distinction is in the record, not claimed away.
        if (type_ == "ESCALATION" or
                (type_ == "GATE_OUTCOME" and
                 payload.get("outcome") == "escalate")):
            payload = dict(payload)
            # A pause records the joint it rises at, so its release
            # can be bound to that gate (R30, correction round 3).
            if (payload.get("paused_set") is not None or
                    payload.get("tree_part") is not None) and \
                    not payload.get("joint"):
                self._refuse(seat_id, type_,
                             "a pause names the joint it is recorded "
                             "at, so its release can be bound to that "
                             "gate (R30)", view_seq)
            tree = state.get("tree") or {}
            root = payload.get("tree_part")
            if tree:
                if root is None:
                    self._refuse(seat_id, type_,
                                 "a pause under a recorded tree names "
                                 "the affected tree part, so its set "
                                 "can be computed from the tree (R30)",
                                 view_seq)
                computed, downstream = self._compute_paused(tree, root)
                supplied = payload.get("paused_set")
                if supplied is not None and \
                        set(supplied) != set(computed):
                    self._refuse(seat_id, type_,
                                 f"supplied paused set {sorted(supplied)} "
                                 f"does not match the set computed from "
                                 f"the recorded tree {sorted(computed)} "
                                 "(R30)", view_seq)
                payload["paused_set"] = computed
                payload["downstream"] = {root: downstream}
                payload["paused_set_basis"] = \
                    "computed_from_recorded_tree"
            elif payload.get("paused_set") is not None:
                payload["paused_set_basis"] = \
                    "caller_supplied_no_tree_recorded"

        # R30: paused parts (and their downstream) are blocked.
        part = payload.get("tree_part")
        if part is not None:
            paused_hit = self._paused_hit(state, part)
            if paused_hit is not None:
                self._refuse(seat_id, type_,
                             f"tree part {part} is paused "
                             f"(paused at seq {paused_hit}, R30)",
                             view_seq)

        # R31: staleness. The act names its subject; if any later
        # event touched that subject, the view it was made from is
        # stale about the thing that matters — reject. Otherwise a
        # behind view is flagged, not refused.
        payload = dict(payload)
        head = state["head_seq"]
        if view_seq < head:
            # R31 (correction round 2): the specified subjects are
            # the contribution, the tree part, and the case version —
            # every named subject is checked, not only the first.
            subjects = [payload.get(k) for k in
                        ("subject_id", "claim_id", "contribution_id",
                         "tree_part", "case_id")]
            for subject in subjects:
                if subject and self._subject_changed(subject, view_seq):
                    self._refuse(seat_id, type_,
                                 f"subject {subject} changed since view "
                                 f"at seq {view_seq} (R31)", view_seq)
            payload["stale_basis"] = True

        affected = []
        for key in ("subject_id", "claim_id", "contribution_id",
                    "case_id"):
            if payload.get(key):
                affected.append(payload[key])
        if part and part not in affected:
            affected.append(part)
        ev = self.store.append(type_, seat_id, affected, payload)
        self.store.commit()
        return ev

    def _paused_hit(self, state, part):
        """Seq of the pause covering `part`, or None (R30)."""
        for paused_part, info in state["paused"].items():
            if part == paused_part or part in info.get("downstream", []):
                return info["source_seq"]
        return None

    def _compute_paused(self, tree, root):
        """R30: the paused set for `root` computed from the recorded
        tree — the part itself plus every transitive downstream
        dependent. Returns (paused_set, downstream_of_root)."""
        seen = []
        queue = list(tree.get(root, []))
        while queue:
            part = queue.pop(0)
            if part in seen or part == root:
                continue
            seen.append(part)
            queue.extend(tree.get(part, []))
        return [root] + seen, seen

    def _subject_changed(self, subject, view_seq):
        for ev in self.store.all_events():
            if ev["event_seq"] <= view_seq:
                continue
            if subject in ev["affected"]:
                return True
            p = ev["payload"]
            for key in ("subject_id", "claim_id", "contribution_id",
                        "tree_part", "case_id"):
                if p.get(key) == subject:
                    return True
            # A subject can also be touched by being named inside a
            # recorded set — a pause's parts, a release's parts, a
            # pause's downstream map (correction round 3).
            for key in ("paused_set", "released_set"):
                if subject in (p.get(key) or []):
                    return True
            downstream = p.get("downstream") or {}
            if subject in downstream or \
                    any(subject in v for v in downstream.values()):
                return True
        return False

    # ------------------------------------------------------------ reads
    def read_sealed(self, token, material_id):
        """R7: a seat reads sealed material only inside its boundary.
        A refused read is recorded; a permitted read is not an event
        (it changes no state)."""
        seat_id = self._authenticate(token)
        if seat_id is None:
            self._refuse(None, "READ_SEALED",
                         "unbound or mismatched identity (R5)")
        state = self.state()
        boundary = state["sealed"].get(material_id)
        if boundary is None:
            self._refuse(seat_id, "READ_SEALED",
                         f"unknown sealed material {material_id}")
        if seat_id not in boundary:
            self._refuse(seat_id, "READ_SEALED",
                         f"seat {seat_id} is outside the evidence "
                         f"boundary of {material_id} (R7)")
        return {"material_id": material_id, "seat": seat_id,
                "within_boundary": True}

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

from . import gates as _gates
from .record import (CASE_CONTENT_FIELDS, FrameworkStore,
                     GATE_OUTCOMES, fold, validate_status_transition)

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
    "CASE_VERIFIED": {"orchestrator"},
    "CASE_JUDGED": {"examiner"},
    "CASE_NOTIFIED": {"examiner"},
    "CASE_ACKNOWLEDGED": {"crew"},
    "GATE_OUTCOME": {"examiner"},
    "FINDING": {"examiner"},
    "CERTIFICATION": {"examiner"},
    "RULING": {"director"},
    "DISPOSITION": {"director"},
    "ESCALATION": {"crew", "orchestrator", "examiner"},
    "CLAIM_STATUS": {"crew", "orchestrator", "examiner", "director"},
    "ONBOARDING": {"orchestrator"},
    "HOLDER_UNAVAILABLE": {"orchestrator"},
    "SEAT_BOUND": {"orchestrator", "director"},
    "MATERIAL_SEALED": {"orchestrator"},
    "RUN_CLOSED": {"orchestrator", "director"},
}


def established_case_content(state, case_id):
    """A case's established current content (Piece 5): the content
    of its highest version whose content stands in the fold, with
    that version number — or (None, 0) when no version's content
    stands. Content stands where the fold established it: version
    1's on its verification (or, in pre-office histories, its
    authorisation), a corrected version's on its first
    CASE_CORRECTED."""
    entry = state["cases"].get(case_id)
    if not entry:
        return None, 0
    best_content, best_version = None, 0
    for vkey, ver in entry["versions"].items():
        if ver.get("content") is not None and int(vkey) > best_version:
            best_content, best_version = ver["content"], int(vkey)
    return best_content, best_version


def classify_case_change(old, new):
    """R16's classification, computed (Piece 5, addendum 1 §A): the
    diff between a case's established content and a proposed
    correction, over the six semantic fields (compared as seven
    stored keys — tree and part are one semantic field). Returns
    the list of changed keys; an empty list means the correction
    is purely representational."""
    return [f for f in CASE_CONTENT_FIELDS
            if (old or {}).get(f) != (new or {}).get(f)]


class DoorwayRefusal(Exception):
    def __init__(self, ground):
        super().__init__(ground)
        self.ground = ground


class Doorway:
    def __init__(self, store: FrameworkStore):
        self.store = store
        self._tokens = {}  # sha256(token) -> seat_id
        self._token_basis = {}  # sha256(token) -> "onboarding" |
        # "commission" (Piece 6, scope F2 as settled)
        self._token_identity = {}  # sha256(token) -> fingerprint of
        # the onboarding record the token bound against (onboarding
        # route only; examination round 1)

    # ------------------------------------------------------------ state
    def state(self):
        # The folded record, enriched with the derived gate state
        # (Piece 6 gates): gate_set and waiting are pure functions
        # of the record, computed over the fold by gates.enrich.
        return _gates.enrich(
            fold(self.store.all_events(), self.store.get_run_id()))

    # ------------------------------------------------------------ tokens
    def issue_token(self, seat_id: str) -> str:
        """Bind a fresh token to a seat the record knows (R5).

        Piece 6 (R20, scope F2 as settled): where an onboarding
        record stands for the seat, the token binds against that
        record — to the identity declaration it established, which
        authentication re-derives and compares on every act (R5);
        where none stands, the commission / SEAT_BOUND binding
        remains the basis — the compatibility path, which is
        NOT the intended route for the Stage 2 end-to-end run (that
        run onboards before binding). The compatibility route is
        conditional, not permanent: once a seat's onboarding
        stands, its pre-onboarding tokens no longer authenticate,
        and a fresh token binds to the onboarding identity.
        `binding_basis` reports the route a token was issued on.
        """
        state = self.state()
        if seat_id not in state["seats"]:
            raise DoorwayRefusal(f"seat {seat_id} is not bound in the "
                                 "record; no token issues (R5)")
        token = secrets.token_hex(24)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._tokens[digest] = seat_id
        record = state["onboarding"].get(seat_id)
        self._token_basis[digest] = (
            "onboarding" if record is not None else "commission")
        if record is not None:
            # The token binds to the seat's onboarded identity
            # (R5): the fingerprint of the identity declaration
            # the onboarding record established. Authentication
            # re-derives it from the record on every act, so the
            # token authenticates only while the seat's established
            # identity is the one it was issued against. The
            # identity *status* is deliberately not part of the
            # fingerprint: an attested status upgrade changes the
            # status, never the identity, and must not invalidate
            # the seat's token. Commission-route tokens carry no
            # fingerprint — they bind to the commission's seat
            # binding, the pre-onboarding guarantee, and no
            # stronger claim is made for them.
            self._token_identity[digest] = self._identity_fingerprint(
                seat_id, record)
        return token

    @staticmethod
    def _identity_fingerprint(seat_id, onboarding_record):
        return hashlib.sha256(
            f"{seat_id}\x00{onboarding_record.get('declaration')}"
            .encode()).hexdigest()

    def binding_basis(self, token):
        """Which record a token bound against (Piece 6, F2):
        "onboarding" where an onboarding record stands for the
        seat, "commission" on the compatibility path."""
        digest = hashlib.sha256(token.encode()).hexdigest()
        if digest not in self._tokens:
            return None
        return self._token_basis.get(digest)

    def _presented_seat(self, token):
        """The seat a presented token was issued to, if the
        doorway issued it at all — named in the record when the
        token no longer authenticates (an expired commission
        token, an identity that no longer matches), so the
        recorded refusal identifies whose act was refused. A
        token the doorway never issued names no seat."""
        if not token:
            return None
        digest = hashlib.sha256(token.encode()).hexdigest()
        return self._tokens.get(digest)

    def _authenticate(self, token):
        if not token:
            return None
        digest = hashlib.sha256(token.encode()).hexdigest()
        seat_id = self._tokens.get(digest)
        if seat_id is None:
            return None
        bound = self._token_identity.get(digest)
        record = self.state()["onboarding"].get(seat_id)
        if bound is not None:
            # Onboarding-route token: authentication depends on
            # the onboarding identity it bound against (R5). If
            # the record's established identity for this seat is
            # not that identity — a different declaration stands —
            # the token is a mismatched identity and does not
            # authenticate.
            if record is None or self._identity_fingerprint(
                    seat_id, record) != bound:
                return None
        elif record is not None:
            # Commission-route token (examination round 2): the
            # compatibility route is conditional on no onboarding
            # record standing for the seat. Once onboarding
            # stands, a token issued before it no longer
            # authenticates — the seat crosses into the onboarded
            # state and acts under a token bound to its onboarding
            # identity. (This is also how an orchestrator's own
            # transition works: its commission token records the
            # onboarding act, then a fresh token is issued against
            # the established record.)
            return None
        return seat_id

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

    def record_driver_failure(self, seat_id, kind, part=None,
                              detail=None):
        """R13: a driver failure, reported by the seat's driver and
        recorded by the doorway under its own authorship — the
        model holds no token and cannot record its own failure.
        The fold marks the seat seat_stalled (R33); no pause is
        computed here, and nothing is fabricated."""
        ev = self.store.append(
            "DRIVER_FAILURE", DOORWAY_ACTOR, [seat_id],
            {"seat": seat_id, "kind": kind, "part": part,
             "origin": "driver_report", "detail": detail},
        )
        self.store.commit()
        return ev

    def record_blocked_wake(self, seat_id, part=None):
        """R22 (Piece 6 gates, §3.5 of the scope; G5 as settled):
        a wake attempted before the assembly gate opened the run,
        recorded by the doorway as a REJECTION — never a
        DRIVER_FAILURE: a blocked attempt is an attempted
        operation, not a failed model execution. The record names
        the seat, the attempted wake, the affected part where
        known, and the R22 ground."""
        ev = self.store.append(
            "REJECTION", DOORWAY_ACTOR, [seat_id],
            {"seat": seat_id, "attempted_type": "WAKE",
             "part": part,
             "ground": "no seat wakes before the assembly gate: "
                       "the declaration must be valid and the "
                       "assembly outcome allow (R22)"},
        )
        self.store.commit()
        return ev

    # ------------------------------------------------------------ acts
    def act(self, token, type_, payload, view_seq=None):
        """Record one act through the doorway, or refuse it — with
        the refusal itself recorded. Returns the recorded event."""
        seat_id = self._authenticate(token)
        if seat_id is None:
            self._refuse(self._presented_seat(token), type_,
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

        # R10 (Piece 3 amendment, on the examiner's recommendation):
        # a comment identifies its subject — a contribution standing
        # in the record, or the job itself. Anything else is refused
        # and recorded. Validation kept narrow to R10's subject
        # requirement.
        if type_ == "COMMENT":
            subject = payload.get("contribution_id") or \
                payload.get("subject_id")
            if not (payload.get("on_job") is True
                    or subject == state["run_id"]
                    or subject in state["contributions"]):
                self._refuse(seat_id, type_,
                             "a comment names the contribution it "
                             "answers, or the job itself (R10)",
                             view_seq)

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

        # R30 (correction rounds 2–4): a pause's set is computed
        # from the tree the record carries, never accepted from the
        # caller. The act names the affected part; the doorway
        # computes the part plus all its transitive downstream
        # dependents, and a caller-supplied set that disagrees is
        # refused and recorded. When no tree stands in the record,
        # the set cannot be computed, so a pause attempt fails
        # closed — refused and recorded; a caller-supplied set is
        # not a substitute, labelled or not (round 4, removing the
        # round-2 fallback Vane rejected).
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
            if not tree:
                # Fail closed (round 4): a pause attempted with no
                # tree in the record cannot have its set computed.
                # An act that pauses nothing is unaffected.
                if payload.get("paused_set") is not None or \
                        root is not None:
                    self._refuse(seat_id, type_,
                                 "no tree stands in the record, so "
                                 "the paused set cannot be computed "
                                 "from it; a caller-supplied set is "
                                 "not a substitute (R30)", view_seq)
            elif root is None and payload.get("paused_set") is None:
                # A pause-less act (an escalation raising a question,
                # pausing nothing) records normally, tree or no tree
                # — R30 governs pauses, and none is requested here
                # (correction round 6).
                pass
            else:
                if root is None:
                    self._refuse(seat_id, type_,
                                 "a pause under a recorded tree names "
                                 "the affected tree part, so its set "
                                 "can be computed from the tree (R30)",
                                 view_seq)
                # The root itself must be established by the tree —
                # a part the tree does not contain (neither as a key
                # nor as a recorded downstream) cannot have a pause
                # scope derived from it (R30, correction round 5).
                known = set(tree)
                for downstream_parts in tree.values():
                    known.update(downstream_parts)
                if root not in known:
                    self._refuse(seat_id, type_,
                                 f"tree part {root} is not in the "
                                 "recorded tree, so no paused set can "
                                 "be computed for it (R30)", view_seq)
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

        # R30: paused parts (and their downstream) are blocked.
        part = payload.get("tree_part")
        if part is not None:
            paused_hit = self._paused_hit(state, part)
            if paused_hit is not None:
                self._refuse(seat_id, type_,
                             f"tree part {part} is paused "
                             f"(paused at seq {paused_hit}, R30)",
                             view_seq)

        # R16 (Piece 5, addendum 2 §E): the doorway owns the
        # classification. On any CASE_CORRECTED it recomputes the
        # six-field diff against the case's established current
        # content; a submitted classification that disagrees — or a
        # version that is not the established case's next version —
        # is refused and the refusal recorded. A caller's label is
        # never taken on trust.
        if type_ == "CASE_CORRECTED":
            problem = self._classification_problem(state, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)

        # R18 (Piece 6): identity status discipline. The doorway
        # owns it, as it owns the case classification: a
        # provider-confirmed claim without its attestation
        # reference, and any status upgrade attempted without a
        # recorded attestation, are refused and the refusal
        # recorded. The reference is recorded provenance; recording
        # it does not independently verify the provider's claim.
        if type_ == "ONBOARDING":
            problem = self._onboarding_problem(state, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)

        # R21–R25 (Piece 6 gates): gate enforcement. It binds
        # only runs whose commission declared a gate set (G7, as
        # settled); a declared-but-invalid set enforces fully
        # and fails closed.
        if state["gate_set"]["declared"]:
            self._gate_checks(state, seat_id, type_, payload,
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

    def _gate_checks(self, state, seat_id, type_, payload,
                     view_seq):
        """Gate enforcement for a declared run (Piece 6 gates,
        scope §3.2–§3.8). Refuses — recording the refusal — any
        act the gates hold. Gate-process acts pass unchecked
        here (authority, pauses, and their own rules already
        applied); the completion rule binds CERTIFICATION and
        RUN_CLOSED; GATE_OUTCOME carries the ruling mechanics;
        work acts carry the pre-run block and passage."""
        if type_ in ("CERTIFICATION", "RUN_CLOSED"):
            # §3.8's completion sequence: certification and
            # closure require a standing completion claim
            # answered by the completion gate's allow.
            if not _gates.completion_ready(state):
                self._refuse(
                    seat_id, type_,
                    "certification and closure require a "
                    "completion claim answered by the completion "
                    "gate's allow, recorded after the claim (R21)",
                    view_seq)
            return
        if type_ == "GATE_OUTCOME":
            joint = payload.get("joint")
            outcome = payload.get("outcome")
            ruling = _gates.latest_ruling(state, joint)
            if outcome == "allow" and ruling is not None and \
                    ruling.get("action") == "stop that part":
                # R24 (G3): the latest ruling governs; while a
                # stop stands as it, no allow records at the gate.
                self._refuse(
                    seat_id, type_,
                    f"the director's ruling against gate {joint} "
                    f"stands at 'stop that part'; an allow is "
                    f"refused while it governs (R24)", view_seq)
            standing = state["gates"].get(joint)
            if outcome == "allow" and standing is not None and \
                    standing.get("outcome") == "escalate" and \
                    not any(r.get("joint") == joint and
                            r["event_seq"] > standing["event_seq"]
                            for r in state["rulings"]):
                # R24: an escalation's pause is ruling-gated. A
                # ruling never manufactures an allow — it permits
                # the examiner to record one; without a ruling
                # against the same gate, the allow is refused.
                self._refuse(
                    seat_id, type_,
                    f"an allow at gate {joint} does not release "
                    f"an escalation without a director ruling "
                    f"recorded against the same gate (R24)",
                    view_seq)
            if ruling is not None and \
                    ruling.get("action") == "correct as stated" and \
                    not (standing is not None and
                         standing["event_seq"]
                         > ruling["event_seq"]):
                # G3's precision: the re-judgement after a
                # 'correct as stated' ruling names the correction
                # acts it relies on (correction_basis). The
                # doorway verifies the positions exist, postdate
                # the ruling, and precede this outcome; whether
                # they are a sufficient correction is the
                # examiner's judgement, never a mechanical claim.
                basis = payload.get("correction_basis")
                if not basis:
                    self._refuse(
                        seat_id, type_,
                        "re-judgement after a 'correct as stated' "
                        "ruling names the correction acts it "
                        "relies on (correction_basis) (R24)",
                        view_seq)
                by_seq = None
                for seq in basis:
                    if not isinstance(seq, int) or \
                            seq <= ruling["event_seq"] or \
                            seq > state["head_seq"]:
                        self._refuse(
                            seat_id, type_,
                            f"correction_basis position {seq!r} "
                            f"does not name a recorded act after "
                            f"the ruling at seq "
                            f"{ruling['event_seq']} (R24)", view_seq)
                    # The basis must cite correction acts, not
                    # merely positions (correction round 1): the
                    # event at each position must be an act a seat
                    # recorded — never a doorway record (a
                    # REJECTION, a DRIVER_FAILURE) and never the
                    # gate machinery's own acts (a GATE_OUTCOME,
                    # a RULING), on which a judgement cannot rest.
                    # Eligibility is mechanical; whether the acts
                    # are a sufficient correction remains the
                    # examiner's judgement.
                    if by_seq is None:
                        by_seq = {ev["event_seq"]: ev
                                  for ev in self.store.all_events()}
                    cited = by_seq.get(seq)
                    if cited is None or \
                            cited["actor"] == DOORWAY_ACTOR or \
                            cited["type"] in ("GATE_OUTCOME",
                                              "RULING"):
                        self._refuse(
                            seat_id, type_,
                            f"correction_basis position {seq} "
                            f"names a {cited['type'] if cited else 'missing'}"
                            f", not a correction act recorded by "
                            f"a seat (R24)", view_seq)
            return
        if type_ in _gates.WORK_ACTS:
            if not _gates.assembly_open(state):
                # §3.3's pre-run block: no seat wakes and no case
                # is usable until the declaration is valid and
                # the assembly outcome is allow. Case issuance
                # is gate-process and is not blocked (G2).
                self._refuse(
                    seat_id, type_,
                    "the run is not open: work waits on a valid "
                    "gate declaration and the assembly gate's "
                    "allow (R22)", view_seq)
            kind, value = _gates.resolve_part(state, seat_id,
                                              type_, payload)
            if kind == "unresolvable":
                # §3.7: fail closed. An act whose subject cannot
                # be resolved to a part does not slip past the
                # gate for want of a field.
                self._refuse(
                    seat_id, type_,
                    f"the act's subject cannot be resolved to a "
                    f"part of the tree ({value}); refused "
                    f"fail-closed (R21/R22)", view_seq)
            if kind == "part":
                if value not in _gates.all_parts(state["tree"]):
                    self._refuse(
                        seat_id, type_,
                        f"tree part {value} is not in the run's "
                        f"recorded tree (R21)", view_seq)
                blocker = _gates.passage_blocker(state, value)
                if blocker is not None:
                    self._refuse(
                        seat_id, type_,
                        f"passage into {value} is held by the "
                        f"gate at {blocker}: no standing allow "
                        f"(R22)", view_seq)
            return
        # Gate-process acts record under their own rules; the
        # gates never block the run from reaching judgement.

    def _classification_problem(self, state, payload):
        """Why a CASE_CORRECTED may not be recorded, or None (R16,
        Piece 5 addendum 2 §E). Enforcement covers every correction
        that could take effect: one carrying case content or a
        classification claim. Such a correction must name the
        established case's next version, carry its classification,
        and that classification must match the doorway's own
        recomputed six-field diff against the established content.
        Two histories stand outside it, deliberately: a bare
        correction carrying neither content nor a claim (the
        pre-office record is full of them; there is nothing to
        recompute), and a second correction for a version whose
        correction already stands — the fold's first-wins rule
        governs those (Piece 4, round 2): recorded, examinable,
        and never able to replace what stands."""
        case_id = payload.get("case_id")
        if not any(f in payload for f in CASE_CONTENT_FIELDS) and \
                "representational" not in payload:
            return None
        entry = state["cases"].get(case_id) or {}
        named = (entry.get("versions") or {}).get(
            str(payload.get("version"))) or {}
        if named.get("corrected"):
            return None
        current, current_version = established_case_content(
            state, case_id)
        if current is None:
            return (f"case {case_id} has no established content "
                    f"to correct (R16)")
        if payload.get("version") != current_version + 1:
            return (f"correction names version "
                    f"{payload.get('version')} but the established "
                    f"case stands at version {current_version}; a "
                    f"correction is its next version (R16)")
        if payload.get("representational") is None:
            return ("a content-carrying correction records its "
                    "classification (R16)")
        changed = classify_case_change(current, payload)
        if bool(payload.get("representational")) == bool(changed):
            return (f"submitted classification representational="
                    f"{payload.get('representational')!r} disagrees "
                    f"with the doorway's recomputed six-field diff "
                    f"(changed: {changed if changed else 'none'}) "
                    f"(R16)")
        return None

    # Identity statuses in rising order (R18): an upgrade is a move
    # to a later entry. Establishment (the first onboarding) is not
    # an upgrade; it sets the initial status.
    _STATUS_RANK = {"unverified": 0, "declared": 1,
                    "provider-confirmed": 2}

    def _onboarding_problem(self, state, payload):
        """Why an ONBOARDING act may not be recorded, or None
        (R18, Piece 6 scope §3 as settled). Statuses outside the
        R18 vocabulary are refused; provider-confirmed always
        carries its attestation reference; and where an onboarding
        record already stands for the seat, a status above the
        recorded one is an upgrade, permitted only by an act
        carrying its attestation reference."""
        status = payload.get("identity_status")
        if status not in self._STATUS_RANK:
            return (f"identity status {status!r} is not in the R18 "
                    f"vocabulary (declared, provider-confirmed, "
                    f"unverified)")
        if status == "provider-confirmed" and \
                not payload.get("attestation_ref"):
            return ("a provider-confirmed status carries its "
                    "attestation reference (R18)")
        existing = state["onboarding"].get(payload.get("seat_id"))
        if existing is not None:
            recorded = existing["identity_status"]
            rises = self._STATUS_RANK[status] > \
                self._STATUS_RANK.get(recorded, 0)
            if payload.get("attestation_ref"):
                # An attestation raises status only (examination
                # round 1): a same- or lower-status attested act
                # is refused, so it can neither downgrade the
                # seat nor replace the attestation provenance the
                # record already derives.
                if not rises:
                    return (f"attested identity status "
                            f"{status} does not raise "
                            f"{payload.get('seat_id')}'s recorded "
                            f"status {recorded}; an attestation "
                            f"raises status only (R18)")
            elif rises:
                return (f"identity status upgrade for "
                        f"{payload.get('seat_id')} from {recorded} "
                        f"to {status} without a recorded attestation "
                        f"(R18)")
        return None

    def submit_pair(self, token, acts, view_seq=None):
        """The correction pair, atomically (§3.5; Piece 5, addendum
        3 §H): CASE_CORRECTED + CASE_VERIFIED appended inside one
        store transaction with a single commit. Both acts are
        validated against the same pre-pair state before anything
        is appended — authority, view position, and the doorway's
        recomputed classification — and a failure during either
        append or the commit is caught explicitly and rolled back,
        so no pending partial transaction survives: head and case
        state stand exactly as before the pair was offered."""
        if len(acts) != 2 or acts[0][0] != "CASE_CORRECTED" or \
                acts[1][0] != "CASE_VERIFIED":
            raise ValueError(
                "the paired route carries exactly "
                "(CASE_CORRECTED, CASE_VERIFIED)")
        (_, corrected), (_, verified) = acts
        seat_id = self._authenticate(token)
        if seat_id is None:
            self._refuse(self._presented_seat(token), "CASE_CORRECTED",
                         "unbound or mismatched identity (R5)",
                         view_seq)
        state = self.state()
        binding = state["seats"].get(seat_id)
        if binding is None:
            self._refuse(seat_id, "CASE_CORRECTED",
                         "seat not bound in the record (R5)", view_seq)
        role = binding["role"]
        for type_ in ("CASE_CORRECTED", "CASE_VERIFIED"):
            if role not in ACT_AUTHORITY.get(type_, set()):
                self._refuse(seat_id, type_,
                             f"{role} may not record {type_} "
                             "(authority matrix, §4)", view_seq)
        if view_seq is None:
            self._refuse(seat_id, "CASE_CORRECTED",
                         "every proposed act carries the record "
                         "position of the view it was made from (R31)")
        if view_seq < 0 or view_seq > state["head_seq"]:
            self._refuse(seat_id, "CASE_CORRECTED",
                         f"view position {view_seq} is not a valid "
                         f"position in the record (R31)", view_seq)
        problem = self._classification_problem(state, corrected)
        if problem is not None:
            self._refuse(seat_id, "CASE_CORRECTED", problem, view_seq)
        if verified.get("case_id") != corrected.get("case_id") or \
                verified.get("version") != corrected.get("version"):
            self._refuse(seat_id, "CASE_VERIFIED",
                         "the pair's verification names a different "
                         "case version than its correction (R15)",
                         view_seq)
        # R30 (examination round 1): the paired route stands under
        # the same pause boundary as the single-act route. A
        # correction for a paused part — or for a part downstream
        # of a recorded pause — is refused and recorded before
        # either event is appended.
        part = corrected.get("part")
        if part is not None:
            paused_hit = self._paused_hit(state, part)
            if paused_hit is not None:
                self._refuse(seat_id, "CASE_CORRECTED",
                             f"tree part {part} is paused "
                             f"(paused at seq {paused_hit}, R30)",
                             view_seq)
        # R31 (examination round 1): the pair's subjects — the case
        # and its tree part — are checked against the submitted
        # view exactly as the single-act route checks its subjects:
        # a subject changed since the view refuses the pair, and
        # the refusal is recorded. A merely behind view, with no
        # subject changed, is admitted and flagged stale_basis.
        if view_seq < state["head_seq"]:
            for subject in (corrected.get("case_id"), part):
                if subject and self._subject_changed(subject,
                                                     view_seq):
                    self._refuse(seat_id, "CASE_CORRECTED",
                                 f"subject {subject} changed since "
                                 f"view at seq {view_seq} (R31)",
                                 view_seq)
        corrected = dict(corrected)
        verified = dict(verified)
        if view_seq < state["head_seq"]:
            corrected["stale_basis"] = True
            verified["stale_basis"] = True
        case_id = corrected.get("case_id")
        try:
            ev1 = self.store.append("CASE_CORRECTED", seat_id,
                                    [case_id], corrected)
            ev2 = self.store.append("CASE_VERIFIED", seat_id,
                                    [case_id], verified)
            self.store.commit()
        except Exception:
            self.store.rollback()
            raise
        return ev1, ev2

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

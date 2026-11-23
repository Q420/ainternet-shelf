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
import copy
import hashlib
import json
import math
import os
import secrets
import threading
import time

from . import gates as _gates
from . import orchestrator as _orch
from . import tool_policy as _tool_policy
from .record import (CASE_CONTENT_FIELDS, FrameworkStore,
                     GATE_OUTCOMES, assembly_record_hash,
                     declaration_fingerprint, effective_case, fold,
                     instance_credential_fingerprint,
                     validate_status_transition)

DOORWAY_ACTOR = "doorway"

# Piece A2: the executor's actor identity — machinery with a
# narrow reporting capability (starts and outcomes against
# standing dispatches), not a seat and not an authority. Its
# reports are recorded by the doorway's executor route below,
# never through the seat act route: no token carries this
# identity, and a seat act naming one of its event kinds is
# refused as not a doorway act.
EXECUTOR_ACTOR = "executor"

# Piece A3: the loop's actor identity — machinery with a
# narrow reporting capability (iteration bookkeeping and
# stalls against standing activations), distinct from the
# executor's, not a seat and not an authority. Its reports are
# recorded by the doorway's loop route below, never through
# the seat act route: no token carries this identity, and a
# seat act naming one of its event kinds is refused as not a
# doorway act.
LOOP_ACTOR = "loop"

# Piece A3 (R50): the recorded stall's ground vocabulary —
# the settled set the loop route and the checker both hold.
LOOP_STALL_GROUNDS = ("step_ceiling", "deadline",
                      "provider_failure", "malformed_response",
                      "runtime_failure")

# Piece A3 (correction round 1): the iteration route's
# deadline refusal — a fixed ground text, held as a constant
# so the loop can tell this refusal from every other: it is
# the one refusal after which no iteration stands counted,
# and the loop answers it with its deadline stall, not a
# runtime failure.
LOOP_ITERATION_DEADLINE_GROUND = (
    "the activation deadline expired before the iteration "
    "could be recorded; no iteration is counted (R49)")

# Piece A3 (correction round 2): the act types whose payload's
# instance_id is the act's subject referent, not its author's
# provenance — the assembly lifecycle acts and an instance's
# onboarding, where the doorway itself cross-checks the named
# instance against the record before the act may stand. On
# every other seat-route act a caller-supplied instance_id is
# stripped (see act()): provenance in the record is
# doorway-established or it is not there.
INSTANCE_REFERENT_ACTS = frozenset({
    "ASSEMBLY_GENERATED", "ASSEMBLY_VERIFIED",
    "ASSEMBLY_JUDGED", "ASSEMBLY_PACKED",
    "ASSEMBLY_ISSUE_AUTHORISED", "INSTANCE_ACTIVATED"})

# §4 authority matrix — which roles may record which act types.
# (Claim-status transitions are governed separately by R2; case
# issue/correction by §3.5's three acts in their own piece — here the
# doorway checks the matrix row only.)
ACT_AUTHORITY = {
    "CONTRIBUTION": {"crew"},
    # §3.8 (R26): the orchestrator's conduct includes recorded
    # notes to seats — COMMENT gains the orchestrator. A note
    # still names its subject under R10, like any comment.
    "COMMENT": {"crew", "orchestrator"},
    "ASSEMBLY_PROPOSED": {"orchestrator"},
    "ASSEMBLY_RECORD": {"examiner"},
    # Agent layer (Piece A1, R40): the assembly lifecycle of a
    # generated instance. The office's acts — generation,
    # construction verification, pack, activation — are recorded
    # under the orchestrator's token, the office being
    # orchestrator-side machinery (Piece 5); the proposal and the
    # issue authorisation are the orchestrator's own; the
    # sufficiency judgement remains the examiner's own, like
    # CASE_JUDGED. No act substitutes for another.
    "ASSEMBLY_GENERATED": {"orchestrator"},
    "ASSEMBLY_VERIFIED": {"orchestrator"},
    "ASSEMBLY_JUDGED": {"examiner"},
    "ASSEMBLY_PACKED": {"orchestrator"},
    "ASSEMBLY_ISSUE_AUTHORISED": {"orchestrator"},
    "INSTANCE_ACTIVATED": {"orchestrator"},
    # Agent layer (Piece A2, R46): reconciliation is the
    # examiner's determination alone. The rest of the dispatch
    # sequence does not travel the seat act route at all:
    # TOOL_REQUESTED and the doorway's TOOL_DISPATCHED go
    # through request_tool(), and the executor's TOOL_STARTED /
    # TOOL_OUTCOME through the executor route — so none of them
    # appears here, and a seat act naming one is refused.
    "TOOL_RECONCILED": {"examiner"},
    "RUN_READY_FOR_COMPLETION": {"orchestrator"},
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
    stored keys — tree and part are one semantic field), plus —
    Piece A3, correction round 1 — the loop_bounds key, which
    classifies like any other content change. Returns the list
    of changed keys; an empty list means the correction is
    purely representational."""
    return [f for f in CASE_CONTENT_FIELDS
            if (old or {}).get(f) != (new or {}).get(f)]


def loop_bounds_problem(bounds):
    """Why a case's loop_bounds may not stand, or None (Piece
    A3, R49; correction round 1). The bounds are optional — a
    case carrying none (None here) is a case no loop runs on,
    and that is lawful. When present they must be an object
    with a step_ceiling that is a positive integer and a
    deadline_seconds that is a finite, positive number
    (correction round 2: infinity is refused here as NaN
    already was): the two values the loop's bounds are made
    of. Malformed bounds are refused
    at the office/doorway boundary, never silently stripped —
    a stripped field would leave a case that looks unbounded
    in a different way than it was issued."""
    if bounds is None:
        return None
    if not isinstance(bounds, dict):
        return ("loop_bounds is not an object; the loop's "
                "bounds are a step ceiling and a deadline "
                "(R49)")
    ceiling = bounds.get("step_ceiling")
    if isinstance(ceiling, bool) or \
            not isinstance(ceiling, int) or ceiling <= 0:
        return ("loop_bounds step_ceiling is not a positive "
                "integer (R49)")
    deadline = bounds.get("deadline_seconds")
    if isinstance(deadline, bool) or \
            not isinstance(deadline, (int, float)) or \
            not math.isfinite(deadline) or \
            not deadline > 0:
        return ("loop_bounds deadline_seconds is not a "
                "finite positive number (R49)")
    return None


class DoorwayRefusal(Exception):
    def __init__(self, ground):
        super().__init__(ground)
        self.ground = ground


class Doorway:
    def __init__(self, store: FrameworkStore, anchor_path=None):
        self.store = store
        # Piece A3 (R49): the doorway's durable activation
        # anchors — one monotonic reading per activation, taken
        # at activation and bound to the activation event and
        # the pinned case, from which every deadline derivation
        # is computed. Durable beside the store (a JSON file,
        # fsynced on establishment, in the executor's claim
        # discipline) so a fresh doorway over the same store
        # recovers the same anchors: a restart neither pauses
        # nor resets a deadline, and never grants a fresh one.
        # A store without a file path keeps its anchors in
        # memory only — durability is a property of the file
        # route, and no claim is made for the other.
        self._anchor_lock = threading.Lock()
        self._anchors_mem = {}
        if anchor_path is not None:
            self._anchor_path = anchor_path
        elif getattr(store, "path", None) not in (
                None, "", ":memory:"):
            self._anchor_path = store.path + ".anchors.json"
        else:
            self._anchor_path = None
        self._tokens = {}  # sha256(token) -> seat_id
        self._token_basis = {}  # sha256(token) -> "onboarding" |
        # "commission" (Piece 6, scope F2 as settled)
        self._token_identity = {}  # sha256(token) -> fingerprint of
        # the onboarding record the token bound against (onboarding
        # route only; examination round 1)
        self._instance_tokens = {}  # sha256(token) -> {instance_id,
        # fingerprint} (Piece A1: an instance's credential, issued
        # at pack in the prepared state; it authenticates only
        # while the record derives the credential active — R39)

    # ------------------------------------------------------------ state
    def state(self):
        # The folded record, enriched with the derived gate state
        # (Piece 6 gates) and the §3.8 derivations (Piece 6
        # orchestrator functions): gate_set, waiting, routing and
        # claims_by_part are pure functions of the record.
        return _orch.derive(_gates.enrich(
            fold(self.store.all_events(), self.store.get_run_id())))

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
        seat_id = self._tokens.get(digest)
        if seat_id is not None:
            return seat_id
        inst = self._instance_tokens.get(digest)
        if inst is not None:
            # An instance's credential names the seat slot its
            # assembly fills, so a refusal of its act identifies
            # the slot (Piece A1).
            entry = self._assembly_of_instance(
                self.state(), inst["instance_id"])
            return entry["seat"] if entry else None
        return None

    def _presented_instance(self, token):
        """The instance id a presented token is an instance
        credential for, or None when the token is not one the
        doorway issued to an instance (Piece A2: a tool request
        is made under the instance's own credential, so the
        route must know whether the presented token is one —
        a seat token authenticates as a seat, never as an
        instance)."""
        if not token:
            return None
        digest = hashlib.sha256(token.encode()).hexdigest()
        inst = self._instance_tokens.get(digest)
        return inst["instance_id"] if inst is not None else None

    def _assembly_of_instance(self, state, instance_id):
        """The fold's assembly entry for an instance, or None
        (Piece A1). Assemblies are keyed by assembly id; an
        instance belongs to exactly one."""
        for entry in state["assemblies"].values():
            if entry.get("instance_id") == instance_id:
                return entry
        return None

    def _authenticate(self, token):
        if not token:
            return None
        digest = hashlib.sha256(token.encode()).hexdigest()
        inst = self._instance_tokens.get(digest)
        if inst is not None:
            return self._authenticate_instance(inst)
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

    def _authenticate_instance(self, inst):
        """Whether an instance's credential authenticates, and
        as which seat (Piece A1, R38/R39). The credential state
        is derived from the record — prepared at pack, active
        only where INSTANCE_ACTIVATED stands — never from a
        doorway-side flag: a prepared credential does not
        authenticate, and no doorway state can make it do so
        before the activation event stands. The fingerprint is
        re-derived from the record on every presentation, as a
        seat's onboarding-bound token is: the instance's
        established declaration, its instance id, and its case
        binding. An authenticating instance acts as the occupant
        of the seat slot its assembly fills."""
        state = self.state()
        entry = self._assembly_of_instance(state,
                                           inst["instance_id"])
        if entry is None or entry["credential"] != "active":
            return None
        record = state["instance_onboarding"].get(
            inst["instance_id"])
        if record is None:
            return None
        bound = instance_credential_fingerprint(
            inst["instance_id"], record.get("declaration"),
            entry["case_id"], entry["case_version"])
        if bound != inst["fingerprint"]:
            return None
        return entry["seat"]

    def _auth_ground(self, token):
        """The ground a failed authentication is recorded under
        (Piece A1): an instance credential that is known but not
        active is refused for exactly that reason — the
        credential invariant is the ground, not a generic
        mismatch — and one whose binding no longer matches the
        record is refused as a mismatched identity."""
        if token:
            digest = hashlib.sha256(token.encode()).hexdigest()
            inst = self._instance_tokens.get(digest)
            if inst is not None:
                entry = self._assembly_of_instance(
                    self.state(), inst["instance_id"])
                if entry is not None and \
                        entry["credential"] != "active":
                    return (f"instance credential for "
                            f"{inst['instance_id']} stands "
                            f"{entry['credential']}; only an "
                            f"active credential authenticates "
                            f"(R39)")
                return ("instance credential does not match "
                        "the identity it bound against (R38)")
        return "unbound or mismatched identity (R5)"

    def issue_instance_token(self, instance_id: str) -> str:
        """Issue an instance's credential (Piece A1, R39): the
        doorway is the only mechanism that issues one, and it
        issues only where the instance's assembly stands packed
        — the pack is what prepares the credential. The token
        binds to the fingerprint of the instance's established
        declaration, its instance id, and its case binding
        (R38), re-derived from the record here and re-derived
        again at every authentication. Issuing confers no
        usability: the credential stands prepared, and
        authentication refuses it until the record carries the
        activation."""
        state = self.state()
        entry = self._assembly_of_instance(state, instance_id)
        if entry is None or entry["packed_seq"] is None:
            raise DoorwayRefusal(
                f"no packed assembly stands for instance "
                f"{instance_id}; no credential issues (R39)")
        record = state["instance_onboarding"].get(instance_id)
        fingerprint = instance_credential_fingerprint(
            instance_id, (record or {}).get("declaration"),
            entry["case_id"], entry["case_version"])
        token = secrets.token_hex(24)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._instance_tokens[digest] = {
            "instance_id": instance_id, "fingerprint": fingerprint}
        return token

    def instance_credential_state(self, instance_id: str) -> str:
        """An instance credential's state as the record derives
        it (Piece A1): "none" where no assembly stands for the
        instance (or none is packed yet), "prepared" at pack,
        "active" only at INSTANCE_ACTIVATED."""
        entry = self._assembly_of_instance(self.state(),
                                           instance_id)
        return entry["credential"] if entry else "none"

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

    # --------------------------------------- dispatch (Piece A2)
    def _assembly_entry_of_instance(self, state, instance_id):
        """(assembly_id, entry) for an instance, or (None, None)
        — the fold keys assemblies by id, and the dispatch
        route needs the id as well as the entry."""
        for assembly_id, entry in state["assemblies"].items():
            if entry.get("instance_id") == instance_id:
                return assembly_id, entry
        return None, None

    # ------------------------------------------------------
    # Piece A3: anchors, pinned bounds, deadline derivation

    def _read_anchors(self):
        """The doorway's anchor table, read fresh — a removal
        or replacement of the durable table is visible to the
        next derivation, never masked by a cache."""
        if self._anchor_path is None:
            return dict(self._anchors_mem)
        try:
            with open(self._anchor_path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _anchor_for(self, activated_seq):
        if activated_seq is None:
            return None
        rec = self._read_anchors().get(str(activated_seq))
        return rec if isinstance(rec, dict) else None

    def _establish_anchor(self, ev, payload, entry):
        """Establish the activation anchor: one monotonic
        reading, taken as the activation is recorded, bound to
        the activation event's position, the instance, and the
        assembly's pinned case. Established once and never
        re-based: a standing anchor for this activation event
        is left exactly as it stands."""
        with self._anchor_lock:
            anchors = self._read_anchors()
            key = str(ev["event_seq"])
            if key in anchors:
                return
            anchors[key] = {
                "instance_id": payload.get("instance_id"),
                "assembly_id": payload.get("assembly_id"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "anchor": time.monotonic(),
            }
            if self._anchor_path is None:
                self._anchors_mem = anchors
                return
            with open(self._anchor_path, "w",
                      encoding="utf-8") as fh:
                json.dump(anchors, fh)
                fh.flush()
                os.fsync(fh.fileno())
            try:
                dir_fd = os.open(
                    os.path.dirname(self._anchor_path) or ".",
                    os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            except OSError:
                pass

    def _pinned_case_content(self, state, entry):
        """The content of the exact case version the assembly
        record pins — the version every bound, grant and
        deadline derivation for this activation reads. A later
        case version's content governs nothing here (R49)."""
        case = state["cases"].get(entry.get("case_id")) or {}
        ver = (case.get("versions") or {}).get(
            str(entry.get("case_version"))) or {}
        return ver.get("content")

    def _pinned_loop_bounds(self, state, entry):
        """The loop bounds the pinned case version carries,
        normalised — or None where the pinned case carries no
        well-formed bounds. The contract is the strict one,
        the same the office/doorway route enforces
        (loop_bounds_problem, correction round 2): a step
        ceiling that is a positive integer and a deadline
        that is a finite, positive number. Absent or malformed
        bounds are no bounds: no loop runs and no temporal
        admission applies (R49, fail closed for the loop
        itself) — a zero ceiling, a non-positive deadline,
        NaN or infinity recorded directly into a case
        establish no regime, exactly as bounds the route
        refused could not."""
        content = self._pinned_case_content(state, entry)
        if not isinstance(content, dict):
            return None
        bounds = content.get("loop_bounds")
        if not isinstance(bounds, dict):
            return None
        ceiling = bounds.get("step_ceiling")
        deadline = bounds.get("deadline_seconds")
        if isinstance(ceiling, bool) or \
                not isinstance(ceiling, int) or ceiling <= 0:
            return None
        if isinstance(deadline, bool) or \
                not isinstance(deadline, (int, float)) or \
                not math.isfinite(deadline) or deadline <= 0:
            return None
        return {"step_ceiling": ceiling,
                "deadline_seconds": deadline}

    def _activation_deadline(self, state, entry):
        """(deadline, problem): the activation's deadline as a
        monotonic instant, derived by the doorway from its own
        anchor and the pinned case's deadline — never from a
        caller-supplied value and never from a record
        timestamp (R49). deadline is None where the pinned
        case carries no temporal regime; problem is set where
        a regime stands but the anchor cannot be established
        from the durable state — admission then fails closed
        rather than substituting a clock or a fresh deadline.
        """
        bounds = self._pinned_loop_bounds(state, entry)
        if bounds is None:
            return None, None
        rec = self._anchor_for(entry.get("activated_seq"))
        anchor = rec.get("anchor") if rec else None
        if rec is None or \
                rec.get("instance_id") != entry.get(
                    "instance_id") or \
                rec.get("case_id") != entry.get("case_id") or \
                rec.get("case_version") != entry.get(
                    "case_version") or \
                isinstance(anchor, bool) or \
                not isinstance(anchor, (int, float)) or \
                anchor > time.monotonic():
            return None, ("the activation anchor cannot be "
                          "established from the doorway's "
                          "durable state; temporal admission "
                          "fails closed (R49)")
        return anchor + bounds["deadline_seconds"], None

    def pinned_loop_bounds(self, instance_id):
        """The loop bounds pinned for an instance's activation
        — the governing bounds the loop enforces — or None
        where the pinned case carries none."""
        state = self.state()
        _, entry = self._assembly_entry_of_instance(
            state, instance_id)
        if entry is None:
            return None
        return self._pinned_loop_bounds(state, entry)

    def activation_remaining(self, instance_id):
        """(remaining, problem): the seconds remaining under
        the instance's activation deadline, derived by the
        doorway — the value the loop passes to its callable
        as a call parameter (R49/R51). remaining is None where
        the pinned case carries no deadline regime; problem is
        set where the anchor cannot be established."""
        state = self.state()
        _, entry = self._assembly_entry_of_instance(
            state, instance_id)
        if entry is None or entry.get("activated_seq") is None:
            return None, ("the instance holds no standing "
                          "activation")
        deadline, problem = self._activation_deadline(
            state, entry)
        if problem is not None:
            return None, problem
        if deadline is None:
            return None, None
        return deadline - time.monotonic(), None

    def _activation_stall(self, state, instance_id):
        """The stall standing against the instance's
        activation, or None (R50)."""
        aid, _ = self._assembly_entry_of_instance(
            state, instance_id)
        if aid is None:
            return None
        loop = state["loop_activations"].get(aid) or {}
        return loop.get("stalled")

    def request_tool(self, token, tool, parameters, request_id,
                     budget_hint=None):
        """The dispatch sequence's front half (Piece A2,
        R44–R47): an activated instance, under its own
        credential, requests a tool — the request is recorded,
        the doorway checks it against the grants sealed in the
        instance's assembly record, and on a pass the dispatch
        intent is recorded by the doorway as mechanism. Only
        then may execution begin; if recording the intent
        failed, nothing here would have returned a dispatch.

        A retry — same identity, same fingerprint — resolves
        against the standing state and records nothing new:
        the standing dispatch is returned, never a second one.
        The same identity with different contents is refused
        and the refusal recorded: an identity cannot change
        its meaning. A refused grant check is likewise recorded
        (a REJECTION naming the grant ground, R55), after the
        request itself has been recorded — the request stands
        as history either way.

        Returns {"ok": True, "dispatch_id", "duplicate": bool,
        ...} on a standing dispatch; raises DoorwayRefusal on a
        refusal (already recorded)."""
        instance_id = self._presented_instance(token)
        if instance_id is None:
            self._refuse(self._presented_seat(token),
                         "TOOL_REQUESTED",
                         "a tool request is made under an "
                         "instance's own credential (R44)")
        seat_id = self._authenticate(token)
        if seat_id is None:
            self._refuse(self._presented_seat(token),
                         "TOOL_REQUESTED", self._auth_ground(token))
        if not isinstance(request_id, str) or not request_id:
            self._refuse(seat_id, "TOOL_REQUESTED",
                         "a tool request carries its stable "
                         "request identity (R47)")
        if not isinstance(parameters, dict):
            self._refuse(seat_id, "TOOL_REQUESTED",
                         "a tool request's parameters are an "
                         "object (R44)")
        state = self.state()
        # Piece A3 (R50): a stalled activation admits no new
        # request from its instance — the refusal is recorded
        # here, before any request stands.
        stall = self._activation_stall(state, instance_id)
        if stall is not None:
            self._refuse(
                seat_id, "TOOL_REQUESTED",
                f"the instance's activation stands stalled "
                f"(ground {stall.get('ground')}); no request is "
                f"admitted from the instance after a stall "
                f"(R50)")
        fingerprint = _tool_policy.request_fingerprint(
            tool, parameters)
        standing = None
        for req in state["tool_requests"]:
            if req["instance_id"] == instance_id and \
                    req["request_id"] == request_id:
                standing = req
                break
        if standing is not None:
            if standing["fingerprint"] != fingerprint:
                self._refuse(
                    seat_id, "TOOL_REQUESTED",
                    f"request identity {request_id} already "
                    f"stands bound to different contents for "
                    f"instance {instance_id}; an identity "
                    f"cannot change its meaning (R47)")
            if standing["dispatch_id"] is not None:
                entry = state["dispatches"].get(
                    standing["dispatch_id"]) or {}
                return {"ok": True, "duplicate": True,
                        "instance_id": instance_id,
                        "request_id": request_id,
                        "dispatch_id": standing["dispatch_id"],
                        "outcome": entry.get("outcome"),
                        "reconciled_outcome":
                            entry.get("reconciled_outcome")}
            # The request stands recorded but undispatched —
            # an earlier check refused it. The retry re-runs
            # the check against the standing request (the grant
            # object is sealed and bounds never free, so the
            # outcome is the record's, not a new discretion);
            # no second TOOL_REQUESTED is recorded.
        else:
            ev = self.store.append(
                "TOOL_REQUESTED", seat_id, [instance_id],
                {"instance_id": instance_id,
                 "request_id": request_id, "tool": tool,
                 "parameters": copy.deepcopy(parameters),
                 "fingerprint": fingerprint})
            self.store.commit()
            state = self.state()
        # The grant check, against the sealed assembly record.
        assembly_id, entry = self._assembly_entry_of_instance(
            state, instance_id)
        ground = self._dispatch_check(
            state, assembly_id, entry, instance_id, tool,
            parameters)
        if ground is not None:
            ev = self.store.append(
                "REJECTION", DOORWAY_ACTOR, [seat_id],
                {"seat": seat_id,
                 "attempted_type": "TOOL_DISPATCHED",
                 "ground": ground,
                 "instance_id": instance_id,
                 "request_id": request_id, "tool": tool})
            self.store.commit()
            raise DoorwayRefusal(ground)
        # Temporal admission (Piece A3, R49): after the grant
        # check, before dispatch intent is recorded — ordered
        # so a refused admission creates no dispatch and leaves
        # no claim to settle. The doorway derives the deadline
        # itself from the activation anchor and the pinned
        # case; a caller-supplied budget value is an
        # early-refusal hint only — an earlier value refuses
        # sooner, a later one never extends the derived
        # deadline, and no caller value can move it. Fail
        # closed on expiry and on an unestablishable anchor,
        # refused and recorded as the grant refusal above.
        ground = self._temporal_admission_problem(
            state, entry, budget_hint)
        if ground is not None:
            ev = self.store.append(
                "REJECTION", DOORWAY_ACTOR, [seat_id],
                {"seat": seat_id,
                 "attempted_type": "TOOL_DISPATCHED",
                 "ground": ground,
                 "instance_id": instance_id,
                 "request_id": request_id, "tool": tool})
            self.store.commit()
            raise DoorwayRefusal(ground)
        dispatch_id = f"dispatch-{len(state['dispatches']) + 1}"
        ev = self.store.append(
            "TOOL_DISPATCHED", DOORWAY_ACTOR, [instance_id],
            {"instance_id": instance_id,
             "request_id": request_id,
             "dispatch_id": dispatch_id, "tool": tool,
             # The registry version that governed this
             # dispatch, recorded as part of the dispatch
             # contract (Piece A2, correction round 1): an
             # examiner must be able to establish from the
             # record which policy version was applied, and
             # the checker verifies the version it holds is
             # the version that governed — a dispatch under
             # another version is not verifiable by it.
             "registry_version":
                 _tool_policy.REGISTRY_VERSION})
        self.store.commit()
        return {"ok": True, "duplicate": False,
                "instance_id": instance_id,
                "request_id": request_id,
                "dispatch_id": dispatch_id, "outcome": None,
                "reconciled_outcome": None}

    def _dispatch_check(self, state, assembly_id, entry,
                        instance_id, tool, parameters):
        """Why a dispatch may not be recorded, or None (Piece
        A2, R44/R47): the grant source is the sealed assembly
        record — the generated object the judgement and the
        pack name by hash. A grant outside that object does
        not exist here; a grant inside it must carry its
        authority trace; the request must satisfy the grant's
        ceiling under the registry's pure policy; and the
        grant's bound counts dispatches — standing dispatches
        under this grant, whatever their outcomes, uncertain
        included, never refunded."""
        if entry is None:
            return (f"no assembly stands for instance "
                    f"{instance_id}; no grant can be checked "
                    f"(R44)")
        generated = self._generated_payload(assembly_id)
        grants = (generated or {}).get("grants") or []
        grant = next((g for g in grants
                      if isinstance(g, dict)
                      and g.get("tool") == tool), None)
        if grant is None:
            return (f"no grant for tool {tool} stands in the "
                    f"sealed assembly record of instance "
                    f"{instance_id}; a grant outside the sealed "
                    f"record does not exist for the doorway "
                    f"(R44)")
        trace = grant.get("authority_trace")
        if not isinstance(trace, str) or not trace:
            return (f"the grant for tool {tool} in the sealed "
                    f"record carries no authority trace; a "
                    f"grant without a trace was never judged "
                    f"and packed (R44)")
        ok, ground = _tool_policy.check_ceiling(
            tool, grant.get("scope_ceiling"), parameters)
        if not ok:
            return f"{ground} (R44)"
        bound = grant.get("bound")
        count = bound.get("count") if isinstance(bound, dict) \
            else None
        if not isinstance(count, int) or isinstance(count, bool):
            return (f"the grant for tool {tool} carries no "
                    f"count bound; the bound check fails "
                    f"closed (R44)")
        used = sum(1 for d in state["dispatches"].values()
                   if d.get("instance_id") == instance_id
                   and d.get("tool") == tool)
        if used >= count:
            return (f"the grant's bound for tool {tool} is "
                    f"exhausted: {used} of {count} dispatches "
                    f"stand charged, and no outcome refunds a "
                    f"dispatch (R47)")
        return None

    def _executor_refuse(self, attempted_type, dispatch_id,
                         ground):
        entry = (self.state()["dispatches"].get(dispatch_id)
                 or {})
        seat = None
        if entry.get("instance_id"):
            _, assembly = self._assembly_entry_of_instance(
                self.state(), entry["instance_id"])
            seat = (assembly or {}).get("seat")
        self._refuse(seat, attempted_type, ground)

    def _temporal_admission_problem(self, state, entry,
                                    budget_hint):
        """Why temporal admission refuses a dispatch, or None
        (Piece A3, R49). No temporal regime stands where the
        pinned case carries no loop bounds — admission is then
        exactly the grant check's, as it was before this piece.
        """
        deadline, problem = self._activation_deadline(
            state, entry)
        if problem is not None:
            return problem
        if deadline is None:
            return None
        if time.monotonic() >= deadline:
            return ("the activation deadline has passed; "
                    "temporal admission fails closed (R49)")
        if budget_hint is not None:
            if isinstance(budget_hint, bool) or \
                    not isinstance(budget_hint, (int, float)):
                return ("the caller-supplied remaining budget "
                        "is not a number; temporal admission "
                        "fails closed (R49)")
            if budget_hint <= 0:
                return ("the caller-supplied remaining budget "
                        "is exhausted; refused on the "
                        "early-refusal hint — a later hint "
                        "would not have extended the deadline "
                        "(R49)")
        return None

    def record_tool_started(self, dispatch_id):
        """The executor's start report (Piece A2): execution
        established as begun for a standing dispatch — begun
        only, never success or completion. Recorded under the
        executor identity; this route is the only one that can
        record it, and it records nothing else.

        The state check and the append are one atomic step
        (correction round 2): the store's serialization lock
        is held across both, so no outcome another thread
        records — the deadline's uncertain outcome, above
        all — can slip between the check and the start it
        answers. Where an outcome already stands when the
        start step runs, the start is refused and nothing is
        recorded for it: the only histories are dispatch →
        start → outcome, or dispatch → outcome with no start
        at all."""
        with self.store.serialized():
            state = self.state()
            entry = state["dispatches"].get(dispatch_id)
            if entry is None:
                self._executor_refuse(
                    "TOOL_STARTED", dispatch_id,
                    f"no dispatch {dispatch_id} stands in the "
                    f"record; a start answers a standing "
                    f"dispatch (R45)")
            if entry.get("started_seq") is not None:
                self._executor_refuse(
                    "TOOL_STARTED", dispatch_id,
                    f"dispatch {dispatch_id} already stands "
                    f"started; there is no second start (R45)")
            if entry.get("outcome") is not None or \
                    entry.get("reconciled_seq") is not None:
                self._executor_refuse(
                    "TOOL_STARTED", dispatch_id,
                    f"dispatch {dispatch_id} already stands "
                    f"settled; a start does not follow an "
                    f"outcome (R45)")
            ev = self.store.append(
                "TOOL_STARTED", EXECUTOR_ACTOR, [dispatch_id],
                {"dispatch_id": dispatch_id,
                 "instance_id": entry.get("instance_id"),
                 "request_id": entry.get("request_id")})
            self.store.commit()
            return ev

    def record_tool_outcome(self, dispatch_id, outcome,
                            result=None, detail=None):
        """The executor's outcome report (Piece A2, R45/R46):
        result, failure, or uncertain, recorded against a
        standing dispatch under the executor identity. A
        settled dispatch takes no further outcome — with the
        one exception the design names: an uncertain dispatch
        is not settled, and a delayed report of result or
        failure attributable to the original dispatch still
        records as its outcome. A timeout is recorded
        uncertain, never as non-occurrence.

        The checks and the append are one atomic step under
        the store's serialization lock (correction round 2),
        as in record_tool_started: the two executor reports
        can never interleave one another's checks and
        appends."""
        with self.store.serialized():
            if outcome not in ("result", "failure", "uncertain"):
                self._executor_refuse(
                    "TOOL_OUTCOME", dispatch_id,
                    f"outcome {outcome!r} is not in the R46 "
                    f"vocabulary (result, failure, uncertain)")
            state = self.state()
            entry = state["dispatches"].get(dispatch_id)
            if entry is None:
                self._executor_refuse(
                    "TOOL_OUTCOME", dispatch_id,
                    f"no dispatch {dispatch_id} stands in the "
                    f"record; an outcome is never recorded "
                    f"before its dispatch (R45)")
            standing = entry.get("outcome")
            if entry.get("reconciled_seq") is not None:
                self._executor_refuse(
                    "TOOL_OUTCOME", dispatch_id,
                    f"dispatch {dispatch_id} stands reconciled; "
                    f"the examiner's determination settled it "
                    f"(R46)")
            if standing in ("result", "failure"):
                self._executor_refuse(
                    "TOOL_OUTCOME", dispatch_id,
                    f"dispatch {dispatch_id} already stands "
                    f"with outcome {standing}; an outcome is "
                    f"terminal (R46)")
            if standing == "uncertain" and \
                    outcome == "uncertain":
                self._executor_refuse(
                    "TOOL_OUTCOME", dispatch_id,
                    f"dispatch {dispatch_id} already stands "
                    f"uncertain; uncertainty is recorded once "
                    f"(R46)")
            payload = {"dispatch_id": dispatch_id,
                       "instance_id": entry.get("instance_id"),
                       "request_id": entry.get("request_id"),
                       "outcome": outcome}
            if result is not None:
                payload["result"] = result
            if detail is not None:
                payload["detail"] = detail
            ev = self.store.append("TOOL_OUTCOME", EXECUTOR_ACTOR,
                                   [dispatch_id], payload)
            self.store.commit()
            return ev

    # ------------------------------------------------ loop routes
    # Piece A3 (R49/R50): the loop machinery's reports, in the
    # executor routes' shape — no seat token carries the loop
    # identity; the doorway records under it, deriving every
    # binding from the record itself. A refusal here is
    # recorded as every refusal at this doorway is.

    def _loop_refuse(self, attempted_type, instance_id, ground):
        seat = None
        if instance_id:
            _, entry = self._assembly_entry_of_instance(
                self.state(), instance_id)
            seat = (entry or {}).get("seat")
        self._refuse(seat, attempted_type, ground)

    def record_loop_iteration(self, assembly_id, iteration,
                              cursor_from, cursor_to):
        """The loop's iteration report (Piece A3, R49): one
        event per model call, recorded before the call it
        accounts, under the loop identity. The route derives
        the activation's binding and governing bounds from the
        record — the loop supplies only its number and the
        cursor range of the package it froze — and enforces
        the sequence the checker independently verifies:
        iterations number from 1 without gaps against a
        standing, unstalled activation; the count never
        exceeds the pinned ceiling; cursor ranges chain, each
        opening where the previous closed, closing no earlier
        than it opens and no later than the record's head. The
        deadline decision is part of the recording decision
        (correction round 1): the doorway derives the deadline
        from its anchor here, inside the serialized boundary,
        and refuses the event — counting no iteration — where
        the deadline has already expired."""
        with self.store.serialized():
            state = self.state()
            entry = state["assemblies"].get(assembly_id)
            if entry is None or \
                    entry.get("activated_seq") is None:
                self._loop_refuse(
                    "LOOP_ITERATION",
                    (entry or {}).get("instance_id"),
                    f"no standing activation for assembly "
                    f"{assembly_id}; an iteration records only "
                    f"against an activated instance (R49)")
            instance_id = entry.get("instance_id")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if loop.get("stalled") is not None:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    "the activation stands stalled; no further "
                    "iteration records (R50)")
            bounds = self._pinned_loop_bounds(state, entry)
            if bounds is None:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    "the pinned case carries no loop bounds; "
                    "no loop runs and no iteration records "
                    "(R49)")
            # Piece A3 (correction round 1): the deadline
            # decision is part of this recording decision —
            # derived here, from the anchor and the pinned
            # bounds, inside the same serialized boundary as
            # the append, so a package whose construction
            # carried the clock past expiry cannot record an
            # iteration after the deadline. An expired
            # deadline refuses the event whole: no iteration
            # stands counted, and the loop answers with its
            # deadline stall. An anchor that cannot be
            # established refuses likewise — fail closed, no
            # substituted clock.
            deadline, problem = self._activation_deadline(
                state, entry)
            if problem is not None:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id, problem)
            if deadline is not None and \
                    time.monotonic() >= deadline:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    LOOP_ITERATION_DEADLINE_GROUND)
            count = len(loop.get("iterations") or [])
            if iteration != count + 1:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    f"iteration {iteration!r} does not follow "
                    f"the {count} iterations standing for this "
                    f"activation; iterations number in order "
                    f"(R49)")
            if iteration > bounds["step_ceiling"]:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    f"iteration {iteration} exceeds the pinned "
                    f"step ceiling {bounds['step_ceiling']}; "
                    f"the ceiling is a bound, not a target "
                    f"(R49)")
            prev_to = None
            if count:
                prev_to = loop["iterations"][-1].get(
                    "cursor_to")
            if prev_to is not None and cursor_from != prev_to:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    f"the cursor range opens at {cursor_from} "
                    f"but the previous iteration closed at "
                    f"{prev_to}; cursor ranges chain without "
                    f"gaps or overlaps (R49)")
            if not isinstance(cursor_from, int) or \
                    not isinstance(cursor_to, int) or \
                    cursor_to < cursor_from or \
                    cursor_to > state["head_seq"]:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    f"cursor range {cursor_from}..{cursor_to} "
                    f"does not stand within the record (head "
                    f"{state['head_seq']}); a package presents "
                    f"only what stands (R49)")
            ev = self.store.append(
                "LOOP_ITERATION", LOOP_ACTOR, [instance_id], {
                    "assembly_id": assembly_id,
                    "instance_id": instance_id,
                    "activated_seq": entry.get("activated_seq"),
                    "case_id": entry.get("case_id"),
                    "case_version": entry.get("case_version"),
                    "iteration": iteration,
                    "step_ceiling": bounds["step_ceiling"],
                    "deadline_seconds":
                        bounds["deadline_seconds"],
                    "cursor_from": cursor_from,
                    "cursor_to": cursor_to})
            self.store.commit()
            return ev

    def record_loop_stalled(self, assembly_id, ground,
                            detail=None):
        """The loop's stall report (Piece A3, R50): the
        recorded stop, under the loop identity, valid only
        against a standing activation that has not already
        stalled, with a ground from the settled vocabulary —
        and only once dispatch accounting has closed for the
        activation: every dispatch of the instance standing in
        the record holds an attributable outcome or an
        examiner's reconciliation. A stall recorded earlier
        would leave an in-flight dispatch's outcome with
        nowhere lawful to land."""
        with self.store.serialized():
            state = self.state()
            entry = state["assemblies"].get(assembly_id)
            if entry is None or \
                    entry.get("activated_seq") is None:
                self._loop_refuse(
                    "LOOP_STALLED",
                    (entry or {}).get("instance_id"),
                    f"no standing activation for assembly "
                    f"{assembly_id}; a stall records only "
                    f"against an activated instance (R50)")
            instance_id = entry.get("instance_id")
            if ground not in LOOP_STALL_GROUNDS:
                self._loop_refuse(
                    "LOOP_STALLED", instance_id,
                    f"ground {ground!r} is not in the stall "
                    f"vocabulary (R50)")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if loop.get("stalled") is not None:
                self._loop_refuse(
                    "LOOP_STALLED", instance_id,
                    "the activation already stands stalled; a "
                    "stall is recorded once (R50)")
            for did, d in state["dispatches"].items():
                if d.get("instance_id") == instance_id and \
                        d.get("outcome") is None and \
                        d.get("reconciled_seq") is None:
                    self._loop_refuse(
                        "LOOP_STALLED", instance_id,
                        f"dispatch {did} stands without an "
                        f"outcome; a stall records only after "
                        f"dispatch accounting has closed for "
                        f"the activation (R50)")
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "ground": ground,
                "iterations": len(loop.get("iterations") or [])}
            if detail is not None:
                payload["detail"] = detail
            ev = self.store.append(
                "LOOP_STALLED", LOOP_ACTOR, [instance_id],
                payload)
            self.store.commit()
            return ev

    def _tool_reconciled_problem(self, state, payload):
        """Why a TOOL_RECONCILED may not be recorded, or None
        (Piece A2, R46): the act names a standing dispatch
        whose outcome stands uncertain — not settled, not
        already reconciled — establishes its outcome (result
        or failure), and carries the evidence the
        determination rests on. The examiner's authority for
        the act itself is the §4 row checked in act()."""
        dispatch_id = payload.get("dispatch_id")
        entry = state["dispatches"].get(dispatch_id or "")
        if entry is None:
            return (f"no dispatch {dispatch_id} stands in "
                    f"the record; a reconciliation answers a "
                    f"standing dispatch (R46)")
        if entry.get("reconciled_seq") is not None:
            return (f"dispatch {dispatch_id} already stands "
                    f"reconciled; a settled dispatch reconciles "
                    f"no second time (R46)")
        if entry.get("outcome") != "uncertain":
            return (f"dispatch {dispatch_id} stands "
                    f"{entry.get('outcome') or 'without an outcome'}"
                    f"; only an uncertain dispatch is "
                    f"reconciled (R46)")
        if payload.get("outcome") not in ("result", "failure"):
            return ("a reconciliation establishes the "
                    "dispatch's outcome: result or failure "
                    "(R46)")
        evidence = payload.get("evidence_ref")
        if not isinstance(evidence, str) or not evidence:
            return ("a reconciliation names the evidence its "
                    "determination rests on (evidence_ref) "
                    "(R46)")
        return None

    # ------------------------------------------------------------ acts
    def act(self, token, type_, payload, view_seq=None):
        """Record one act through the doorway, or refuse it — with
        the refusal itself recorded. Returns the recorded event."""
        seat_id = self._authenticate(token)
        if seat_id is None:
            self._refuse(self._presented_seat(token), type_,
                         self._auth_ground(token), view_seq)
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

        # Piece A3 (R50): a stalled activation admits nothing
        # further from its instance. The check sits on the
        # instance credential's own presentation — the seat
        # acting for itself is unaffected, and no standing A1/A2
        # history holds a stall, so the rule is inert there.
        presented = self._presented_instance(token)
        if presented is not None:
            stall = self._activation_stall(state, presented)
            if stall is not None:
                self._refuse(
                    seat_id, type_,
                    f"the instance's activation stands stalled "
                    f"(ground {stall.get('ground')}); no act is "
                    f"admitted from the instance after a stall "
                    f"(R50)", view_seq)

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

        # §3.8 (R26/R35): the assembly acts carry their own
        # mechanical discipline — a proposal answers an exact
        # commission by reference; a record is bound to the exact
        # proposal it examines and is complete and consistent
        # against the fold. Substance remains the examiner's.
        if type_ == "ASSEMBLY_PROPOSED":
            problem = self._assembly_proposal_problem(state, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)
        if type_ == "ASSEMBLY_RECORD":
            problem = self._assembly_record_problem(state, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)

        # Agent layer (Piece A1, R37–R40): an assembly proposal
        # that names the seat slot it fills (the §3.8 proposal,
        # extended) names a commissioned crew slot and a part of
        # the recorded tree; an instance proposal — the payload
        # discriminator says so — must name both, or it is not a
        # valid instance proposal at all (correction round 2).
        # The lifecycle acts that follow carry their own
        # mechanical discipline — the normative order, the
        # onboarding binding, the judged object's hash, the
        # credential invariant. Substance — whether an instance
        # is sufficient — remains the examiner's.
        if type_ == "ASSEMBLY_PROPOSED" and \
                (payload.get("seat") is not None
                 or payload.get("proposal_kind") == "instance"):
            problem = self._assembly_slot_problem(state, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)
        if type_ in ("ASSEMBLY_GENERATED", "ASSEMBLY_VERIFIED",
                     "ASSEMBLY_JUDGED", "ASSEMBLY_PACKED",
                     "ASSEMBLY_ISSUE_AUTHORISED",
                     "INSTANCE_ACTIVATED"):
            problem = self._assembly_lifecycle_problem(
                state, type_, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)

        # Agent layer (Piece A2, R46): a reconciliation names
        # a standing dispatch whose outcome stands uncertain,
        # establishes its outcome, and carries its evidence.
        # Anything else is refused and the refusal recorded.
        if type_ == "TOOL_RECONCILED":
            problem = self._tool_reconciled_problem(state, payload)
            if problem is not None:
                self._refuse(seat_id, type_, problem, view_seq)

        # §3.8 (S5): readiness cannot float free of the claim
        # record — with no crew completion claim standing, the
        # declaration is refused. Completeness beyond that floor
        # is the completion gate's judgement, not the doorway's.
        if type_ == "RUN_READY_FOR_COMPLETION":
            if not state["completion_claims"]:
                self._refuse(seat_id, type_,
                             "readiness declared with no crew "
                             "completion claim standing in the "
                             "record; the declaration answers the "
                             "claim record, never replaces it "
                             "(§3.8)", view_seq)

        # §3.8 (S4): a routing note's referents are validated —
        # an actual recorded disagreement, and a destination
        # relevant to its subject. A label without an enforceable
        # referent does not record.
        if type_ == "COMMENT" and (
                "routes_disagreement" in payload
                or "to_gate" in payload):
            problem = self._routing_problem(state, seat_id, role,
                                            payload)
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

        # Piece A3 (correction round 1): instance provenance.
        # An act presented under an instance credential is
        # recorded with the instance it was presented under —
        # the doorway knows the credential's instance, and the
        # record carries it (as a tool request's payload
        # carries its instance, R44) so the act is attributable
        # to the instance and not only to the seat it fills.
        # Without it, a stalled activation's later acts are
        # indistinguishable from the seat's own lawful work.
        # The doorway's identification governs: a payload
        # naming another instance is overwritten, never
        # trusted. An ordinary seat credential stamps nothing.
        #
        # Correction round 2: nor may an ordinary seat
        # credential *supply* the provenance. A caller-supplied
        # instance_id on the seat route is stripped before the
        # act records, so an instance_id in a recorded act
        # always means the doorway established it — the seat
        # cannot mint an "instance act" for a stalled (or any)
        # instance, accidentally or deliberately. The strip
        # does not reach the acts whose instance_id is their
        # subject referent — the assembly lifecycle and an
        # instance's onboarding (INSTANCE_REFERENT_ACTS) —
        # where the doorway cross-checks the named instance
        # against the record before the act may stand.
        if presented is not None:
            payload["instance_id"] = presented
        elif type_ not in INSTANCE_REFERENT_ACTS and not (
                type_ == "ONBOARDING" and
                payload.get("subject") == "instance"):
            payload.pop("instance_id", None)

        affected = []
        for key in ("subject_id", "claim_id", "contribution_id",
                    "case_id"):
            if payload.get(key):
                affected.append(payload[key])
        if part and part not in affected:
            affected.append(part)
        ev = self.store.append(type_, seat_id, affected, payload)
        self.store.commit()
        if type_ == "INSTANCE_ACTIVATED":
            # Piece A3 (R49): the activation anchor is
            # established with the activation — one monotonic
            # reading, bound to this event and the pinned case,
            # from which every deadline for this activation is
            # derived. The record's own timestamp is a
            # wall-clock display value and is never a deadline
            # basis.
            entry = state["assemblies"].get(
                payload.get("assembly_id")) or {}
            self._establish_anchor(ev, payload, entry)
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
            # The completion sequence (§3.8, S5): certification
            # and closure require the orchestrator's readiness
            # declaration answered by the completion gate's
            # allow, recorded after the declaration.
            if not _gates.completion_ready(state):
                self._refuse(
                    seat_id, type_,
                    "certification and closure require a "
                    "readiness declaration answered by the "
                    "completion gate's allow, recorded after "
                    "the declaration (R21)", view_seq)
            if type_ == "CERTIFICATION":
                # R36: the certification states its coverage's
                # identity statuses, exactly as derived.
                problem = self._certification_coverage_problem(
                    state, payload)
                if problem is not None:
                    self._refuse(seat_id, type_, problem, view_seq)
            return
        if type_ == "GATE_OUTCOME":
            joint = payload.get("joint")
            outcome = payload.get("outcome")
            if outcome == "allow" and \
                    joint == _gates.ASSEMBLY_JOINT and \
                    _gates.run_proposals(state):
                # §3.8 (S2): where a run-level proposal stands,
                # an assembly allow answers an examined assembly
                # — a record bound to the latest run-level
                # proposal must stand first. An allow recorded
                # before that examination authorizes nothing and
                # does not record. (Piece A1 correction round 1:
                # an instance proposal is not the run's proposal
                # and never becomes the latest here.)
                latest = _gates.run_proposals(state)[-1][
                    "event_seq"]
                bound = any(
                    rec.get("proposal_seq") == latest
                    for rec in state.get("assembly_records", []))
                if not bound:
                    self._refuse(
                        seat_id, type_,
                        "an assembly allow requires the "
                        "examiner's assembly record, bound to "
                        "the latest proposal, standing first "
                        "(R35)", view_seq)
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
                    # merely positions (correction rounds 1–2):
                    # the event at each position must be of an
                    # eligible correction-act type — the positive
                    # boundary in gates.CORRECTION_ACT_TYPES.
                    # A seat-authored act is not thereby a
                    # correction act: a FINDING, a DISPOSITION,
                    # or a HOLDER_UNAVAILABLE performs no
                    # correction and cannot be cited. Eligibility
                    # is mechanical; whether the cited acts are
                    # a sufficient correction remains the
                    # examiner's judgement.
                    if by_seq is None:
                        by_seq = {ev["event_seq"]: ev
                                  for ev in self.store.all_events()}
                    cited = by_seq.get(seq)
                    if cited is None or \
                            cited["type"] not in \
                            _gates.CORRECTION_ACT_TYPES:
                        self._refuse(
                            seat_id, type_,
                            f"correction_basis position {seq} "
                            f"names a {cited['type'] if cited else 'missing'}"
                            f", which is not an eligible "
                            f"correction act (R24)", view_seq)
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
        # Piece A3 (correction round 1): bounds a correction
        # carries must be well-formed to stand — refused here,
        # at the doorway's own boundary, never silently
        # stripped on the way into the record (R49).
        if "loop_bounds" in payload:
            problem = loop_bounds_problem(payload["loop_bounds"])
            if problem is not None:
                return problem
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
        if payload.get("subject") == "instance":
            # Piece A1 (R38): the instance path carries the same
            # status discipline against the per-instance state.
            return self._instance_onboarding_problem(state, payload)
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

    def _instance_onboarding_problem(self, state, payload):
        """Why an instance-subject ONBOARDING may not be
        recorded, or None (Piece A1, R38). The act names its
        instance, its assembly, and the seat slot it fills; the
        slot is commissioned. An instance onboards once, at its
        assembly: where its record already stands, a further act
        is an attestation or nothing — an attested act must
        raise the status (the seat rule, carried over), and an
        unattested act records nothing."""
        for field in ("instance_id", "assembly_id", "seat_id"):
            if not isinstance(payload.get(field), str) or \
                    not payload.get(field):
                return (f"an instance onboarding names its "
                        f"{field} (R38)")
        if payload.get("seat_id") not in state["seats"]:
            return (f"seat slot {payload.get('seat_id')} is not "
                    f"commissioned in the record (R38)")
        existing = state["instance_onboarding"].get(
            payload.get("instance_id"))
        if existing is None:
            if not payload.get("declaration"):
                return ("an instance's onboarding establishes "
                        "its declaration (R38)")
            return None
        recorded = existing["identity_status"]
        status = payload.get("identity_status")
        rises = self._STATUS_RANK[status] > \
            self._STATUS_RANK.get(recorded, 0)
        if payload.get("attestation_ref"):
            if not rises:
                return (f"attested identity status {status} "
                        f"does not raise the instance's "
                        f"recorded status {recorded}; an "
                        f"attestation raises status only (R38)")
            return None
        return (f"instance {payload.get('instance_id')} already "
                f"stands onboarded; an instance onboards once, "
                f"at its assembly — a further act is an "
                f"attestation or nothing (R38)")

    def _event_at(self, seq):
        """The recorded event at a position, or None."""
        if not isinstance(seq, int) or isinstance(seq, bool):
            return None
        for ev in self.store.all_events():
            if ev["event_seq"] == seq:
                return ev
        return None

    def _generated_payload(self, assembly_id):
        """The ASSEMBLY_GENERATED payload that established an
        assembly, or None — the immutable object the later
        lifecycle acts answer to."""
        for ev in self.store.all_events():
            if ev["type"] == "ASSEMBLY_GENERATED" and \
                    ev["payload"].get("assembly_id") == assembly_id:
                return ev["payload"]
        return None

    def _assembly_slot_problem(self, state, payload):
        """Why an assembly proposal naming its seat slot may not
        be recorded, or None (Piece A1): the slot is a
        commissioned crew seat — a role specification an
        assembly fills — and the part it names is a part of the
        recorded tree. An instance proposal must name both its
        slot and its part; a missing one is not a permissive
        case but an invalid proposal (correction round 2)."""
        if payload.get("proposal_kind") == "instance":
            if payload.get("seat") is None:
                return ("an instance proposal names the seat "
                        "slot it fills; this one names none "
                        "(R37)")
            if payload.get("part") is None:
                return ("an instance proposal names the part "
                        "it fills; this one names none (R37)")
        seat_id = payload.get("seat")
        binding = state["seats"].get(seat_id)
        if binding is None:
            return (f"seat slot {seat_id} is not commissioned "
                    f"in the record; an assembly fills a "
                    f"commissioned slot (R37)")
        if binding.get("role") != "crew":
            return (f"assemblies fill crew seat slots; "
                    f"{seat_id} is {binding.get('role')} (R37)")
        part = payload.get("part")
        tree = state.get("tree") or {}
        if part is not None and tree:
            known = set(tree)
            for downstream in tree.values():
                known.update(downstream or [])
            if part not in known:
                return (f"part {part} is not in the recorded "
                        f"tree (R37)")
        return None

    def _assembly_lifecycle_problem(self, state, type_, payload):
        """Why an assembly lifecycle act may not be recorded, or
        None (Piece A1, R37–R40). The doorway owns the sequence,
        as it owns the case classification and the identity
        discipline: each act answers the standing record — the
        generated assembly binds to its exact proposal and
        onboarding; verification precedes judgement; the
        judgement and the pack name the generated object by its
        canonical hash, so a judgement of a different object
        cannot seal this one; authorisation follows pack;
        activation follows authorisation and requires the
        record's grants section. A duplicate act of a kind for
        an assembly does not record — the lifecycle is
        one-to-one."""
        assembly_id = payload.get("assembly_id")
        instance_id = payload.get("instance_id")
        if not assembly_id or not instance_id:
            return (f"{type_} names its assembly and its "
                    f"instance (R37)")
        if type_ == "ASSEMBLY_GENERATED":
            return self._assembly_generated_problem(
                state, payload)
        entry = state["assemblies"].get(assembly_id)
        if entry is None:
            return (f"no generated assembly {assembly_id} "
                    f"stands in the record (R40)")
        if entry.get("instance_id") != instance_id:
            return (f"assembly {assembly_id} belongs to "
                    f"instance {entry.get('instance_id')}, not "
                    f"{instance_id} (R37)")
        stage = {
            "ASSEMBLY_VERIFIED": ("verified_seq", "generated_seq",
                                  "generation"),
            "ASSEMBLY_JUDGED": ("judged_seq", "verified_seq",
                                "construction verification"),
            "ASSEMBLY_PACKED": ("packed_seq", "judged_seq",
                                "the sufficiency judgement"),
            "ASSEMBLY_ISSUE_AUTHORISED": (
                "authorised_seq", "packed_seq", "pack"),
            "INSTANCE_ACTIVATED": ("activated_seq",
                                   "authorised_seq",
                                   "the issue authorisation"),
        }[type_]
        own_seq, prior_seq, prior_name = stage
        if entry.get(own_seq) is not None:
            return (f"assembly {assembly_id} already stands "
                    f"with its {type_} recorded; the lifecycle "
                    f"is one-to-one (R40)")
        if entry.get(prior_seq) is None:
            return (f"{type_} for assembly {assembly_id} "
                    f"answers {prior_name}, which does not stand "
                    f"in the record; the sequence is normative "
                    f"(R40)")
        if type_ in ("ASSEMBLY_JUDGED", "ASSEMBLY_PACKED"):
            generated = self._generated_payload(assembly_id)
            digest = assembly_record_hash(generated or {})
            named = payload.get("record_hash")
            if named != digest:
                return (f"{type_} names record hash {named!r}; "
                        f"the generated assembly's canonical "
                        f"hash is {digest} — the act must name "
                        f"the exact object it answers (R37)")
            if type_ == "ASSEMBLY_PACKED" and \
                    named != entry.get("judged_hash"):
                return ("the pack names a different object "
                        "than the judgement it answers; a "
                        "judgement of a changed assembly is "
                        "stale and seals nothing (R37)")
        if type_ == "ASSEMBLY_PACKED":
            generated = self._generated_payload(assembly_id)
            bound = self._event_at(
                (generated or {}).get("onboarding_seq"))
            declaration = (bound or {}).get("payload", {}).get(
                "declaration")
            expected = instance_credential_fingerprint(
                instance_id, declaration,
                entry.get("case_id"), entry.get("case_version"))
            if payload.get("credential_fingerprint") != expected:
                return ("the pack's credential fingerprint "
                        "does not match the fingerprint of the "
                        "instance's established declaration, its "
                        "instance id and its case binding (R38)")
        if type_ == "INSTANCE_ACTIVATED" and \
                not entry.get("grants_present"):
            return ("the assembly record carries no grants "
                    "section; an instance does not activate "
                    "without one — the shape must exist before "
                    "an instance lives (R39)")
        return None

    def _assembly_generated_problem(self, state, payload):
        """Why an ASSEMBLY_GENERATED may not be recorded, or
        None (Piece A1, R37/R38): the assembly and its instance
        are new (ids are never reused); the record binds to the
        exact proposal it answers — an instance proposal, never
        a run-level one (correction round 1), whose seat slot
        and part the record must equal exactly (correction
        round 2) — and to the exact
        instance onboarding that precedes it — by position and
        by the declaration's fingerprint, identity claims
        living only in the onboarding event; the case binding
        names the seat's effective case, and the part the
        record fills is that case's own part (correction round
        1); skills are pinned by name and version; grants, when
        present, are grant-shaped data (their enforcement is a
        later piece)."""
        assembly_id = payload.get("assembly_id")
        instance_id = payload.get("instance_id")
        if assembly_id in state["assemblies"]:
            return (f"assembly {assembly_id} already stands "
                    f"generated; a changed assembly is a new "
                    f"assembly, never a rewrite (R37)")
        for entry in state["assemblies"].values():
            if entry.get("instance_id") == instance_id:
                return (f"instance {instance_id} already "
                        f"belongs to another assembly; instance "
                        f"ids are never reused (R38)")
            if entry.get("onboarding_seq") == \
                    payload.get("onboarding_seq"):
                return ("the onboarding is already bound to "
                        "another assembly; the binding is "
                        "one-to-one (R38)")
        proposal = self._event_at(payload.get("proposal_seq"))
        if proposal is None or \
                proposal["type"] != "ASSEMBLY_PROPOSED":
            return (f"proposal_seq "
                    f"{payload.get('proposal_seq')!r} names no "
                    f"standing ASSEMBLY_PROPOSED; a generation "
                    f"answers an exact proposal (R40)")
        if proposal["payload"].get("proposal_kind") != \
                "instance":
            return ("the proposal the generation answers is "
                    "a run-level proposal; a generation answers "
                    "an instance proposal only — the two share "
                    "an event kind, never a referent (R40)")
        if proposal["payload"].get("seat") != \
                payload.get("seat"):
            return (f"the proposal names seat slot "
                    f"{proposal['payload'].get('seat')!r}; the "
                    f"assembly fills {payload.get('seat')!r} — "
                    f"a generation answers its exact proposal, "
                    f"and a proposal naming no slot grounds no "
                    f"generation (R37)")
        if proposal["payload"].get("part") != \
                payload.get("part"):
            return (f"the proposal names part "
                    f"{proposal['payload'].get('part')!r}; the "
                    f"assembly fills {payload.get('part')!r} — "
                    f"a generation answers its exact proposal "
                    f"(R37)")
        bound = self._event_at(payload.get("onboarding_seq"))
        if bound is None or bound["type"] != "ONBOARDING" or \
                bound["payload"].get("subject") != "instance":
            return (f"onboarding_seq "
                    f"{payload.get('onboarding_seq')!r} names "
                    f"no instance onboarding; the generated "
                    f"record binds to the exact onboarding event "
                    f"(R38)")
        ob = bound["payload"]
        if ob.get("instance_id") != instance_id or \
                ob.get("assembly_id") != assembly_id:
            return ("the bound onboarding names a different "
                    "instance or assembly than the generated "
                    "record (R38)")
        if not proposal["event_seq"] < bound["event_seq"]:
            return ("the instance's onboarding follows the "
                    "proposal it answers; the sequence is "
                    "normative (R40)")
        if payload.get("declaration_fingerprint") != \
                declaration_fingerprint(
                    instance_id, ob.get("declaration")):
            return ("the record's declaration fingerprint "
                    "does not match the bound onboarding's "
                    "declaration (R38)")
        eff = effective_case(state, payload.get("seat"))
        if eff is None:
            return (f"no issued case stands for seat "
                    f"{payload.get('seat')}; an assembly binds "
                    f"to a case (R37)")
        if eff["case_id"] != payload.get("case_id") or \
                eff["version"] != payload.get("case_version"):
            return (f"the case binding names "
                    f"{payload.get('case_id')} version "
                    f"{payload.get('case_version')}; the "
                    f"seat's effective case is {eff['case_id']} "
                    f"version {eff['version']} (R37)")
        case_part = (eff.get("content") or {}).get("part")
        if payload.get("part") != case_part:
            return (f"the record fills part "
                    f"{payload.get('part')!r}; the case it "
                    f"binds covers part {case_part!r} — an "
                    f"assembly's part must be its case's part, "
                    f"or the pairing is ungrounded (R37)")
        skills = payload.get("skills")
        if not isinstance(skills, list) or any(
                not isinstance(s, dict) or not s.get("name")
                or not s.get("version") for s in skills):
            return ("the assembly record pins its skills by "
                    "name and version (R37)")
        grants = payload.get("grants")
        if grants is not None and (
                not isinstance(grants, list) or any(
                    not isinstance(g, dict) or not g.get("tool")
                    for g in grants)):
            return ("grants, when present, are a list of "
                    "grant objects naming their tool (R44's "
                    "shape, as data; enforcement is a later "
                    "piece)")
        return None

    def _assembly_proposal_problem(self, state, payload):
        """Why an ASSEMBLY_PROPOSED may not be recorded, or None
        (§3.8, S1): the proposal answers the standing commission
        exactly, by reference — its commission_seq, tree_ref and
        gates_ref all name the commission event's position — and
        it carries the proposed crew in full."""
        commission_seq = state.get("commission_seq")
        if commission_seq is None:
            return "no commission stands in the record to answer (R26)"
        for field in ("commission_seq", "tree_ref", "gates_ref"):
            if payload.get(field) != commission_seq:
                return (f"the proposal's {field} "
                        f"{payload.get(field)!r} does not name the "
                        f"standing commission at seq "
                        f"{commission_seq}; a proposal answers an "
                        f"exact commission, by reference (R26)")
        crew = payload.get("crew")
        if not isinstance(crew, list) or not crew or \
                any(not isinstance(c, dict) or not c.get("seat")
                    or not c.get("role") for c in crew):
            return ("the proposal carries the proposed crew in "
                    "full: a non-empty list of seat and role (R26)")
        return None

    def _assembly_record_problem(self, state, payload):
        """Why an ASSEMBLY_RECORD may not be recorded, or None
        (§3.8, S2): the record is bound to an exact standing
        proposal; its criteria mapping covers every part of the
        commissioned tree; its identity assessment covers every
        proposed seat and matches the derived statuses; its gate
        set satisfies the completeness rule over the tree. All
        mechanical — whether the mapping is right remains the
        examiner's judgement."""
        proposal_seq = payload.get("proposal_seq")
        proposal = None
        for ev in self.store.all_events():
            if ev["event_seq"] == proposal_seq and \
                    ev["type"] == "ASSEMBLY_PROPOSED":
                proposal = ev
                break
        if proposal is None:
            return (f"proposal_seq {proposal_seq!r} names no "
                    f"standing ASSEMBLY_PROPOSED; a record is "
                    f"bound to the exact proposal it examines "
                    f"(R35)")
        tree = state.get("tree") or {}
        mapping = payload.get("criteria_mapping")
        if not isinstance(mapping, dict):
            return "the record carries a criteria mapping (R35)"
        missing = _gates.all_parts(tree) - set(mapping)
        if missing:
            return (f"the criteria mapping omits tree parts "
                    f"{sorted(missing)}; it covers every proposed "
                    f"part (R35)")
        weighed = payload.get("identity_weighed")
        if not isinstance(weighed, dict):
            return "the record carries an identity assessment (R35)"
        crew = (proposal["payload"].get("crew") or [])
        for member in crew:
            seat = member.get("seat")
            if seat not in weighed:
                return (f"the identity assessment omits proposed "
                        f"seat {seat}; it covers every proposed "
                        f"seat (R35)")
            derived = _orch.identity_status_of(state, seat)
            if weighed[seat] != derived:
                return (f"the identity assessment states "
                        f"{weighed[seat]!r} for {seat}; the record "
                        f"derives {derived!r} (R35)")
        gate_set = payload.get("gate_set")
        if not isinstance(gate_set, dict):
            return "the record carries the gate set it examined (R35)"
        defects = _gates.validate_gate_set(tree, gate_set)
        if defects:
            return (f"the record's gate set is not a complete, "
                    f"valid set over the tree: {defects[0]} (R35)")
        return None

    def _routing_problem(self, state, seat_id, role, payload):
        """Why a routing note may not be recorded, or None
        (§3.8, S4): routing is the orchestrator's conduct; both
        referents are required; the disagreement stands recorded;
        the destination is relevant to the disagreement's
        subject — the judgement gate naming its part, or the
        completion gate (the only destination for a job-level
        claim)."""
        if role != "orchestrator":
            return ("routing a disagreement is the orchestrator's "
                    "conduct (R26); another seat's note carries no "
                    "routing")
        disagreement_id = payload.get("routes_disagreement")
        joint = payload.get("to_gate")
        if not disagreement_id or not joint:
            return ("a routing note names both the disagreement "
                    "and the gate it routes to (§3.8)")
        disagreement = (state.get("disagreements") or {}).get(
            disagreement_id)
        if disagreement is None:
            return (f"disagreement {disagreement_id} stands "
                    f"nowhere in the record; a route names an "
                    f"actual recorded disagreement (§3.8)")
        kind, value = _gates._claim_part(
            state, disagreement.get("claim_id"))
        if kind == "unresolvable":
            return (f"the disagreement's subject cannot be "
                    f"resolved ({value}); no relevant destination "
                    f"can be established (§3.8)")
        operative = (state.get("gate_set") or {}).get(
            "operative") or {}
        if kind == "part":
            valid = {j for j, k in operative.items()
                     if k == "judgement" and j == value}
            valid.add(_gates.COMPLETION_JOINT)
        else:
            valid = {_gates.COMPLETION_JOINT}
        if joint not in valid:
            return (f"gate {joint} is not a relevant destination "
                    f"for this disagreement (its subject resolves "
                    f"to {value if kind == 'part' else 'the job'}; "
                    f"relevant: {sorted(valid)}) (§3.8)")
        return None

    def _certification_coverage_problem(self, state, payload):
        """Why a CERTIFICATION's coverage may not stand, or None
        (§3.8, S3; R36): the declared boundary is validated
        (absent = whole run; an empty list, an unknown part, or
        a duplicate is refused), and the stated identity_status
        must be exactly the derived coverage — no omission, no
        misstatement, no invented status. Whether the
        certification's conclusions are warranted is not the
        doorway's question."""
        if "covers_parts" in payload:
            covers = payload["covers_parts"]
            if not isinstance(covers, list) or not covers:
                return ("covers_parts, when present, is a "
                        "non-empty list of tree parts; whole-run "
                        "coverage is declared by its absence — an "
                        "empty list certifies nothing and is "
                        "refused (R36)")
            if len(set(covers)) != len(covers):
                return ("covers_parts names a part more than "
                        "once (R36)")
            parts = _gates.all_parts(state.get("tree") or {})
            unknown = [part for part in covers if part not in parts]
            if unknown:
                return (f"covers_parts names parts outside the "
                        f"commissioned tree: {unknown} (R36)")
            covers_parts = list(covers)
        else:
            covers_parts = None
        derived = _orch.certification_coverage(state, covers_parts)
        stated = payload.get("identity_status")
        if not isinstance(stated, dict):
            return ("a certification states the identity status "
                    "of every seat whose contributions it covers "
                    "(identity_status) (R36)")
        for seat, status in derived.items():
            if seat not in stated:
                return (f"the certification omits {seat}, whose "
                        f"contributions it covers; their derived "
                        f"status is {status!r} (R36)")
            if stated[seat] != status:
                return (f"the certification states "
                        f"{stated[seat]!r} for {seat}; the record "
                        f"derives {status!r} (R36)")
        for seat in stated:
            if seat not in derived:
                return (f"the certification states a status for "
                        f"{seat}, whose contributions it does not "
                        f"cover; an invented status does not "
                        f"record (R36)")
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
        # Piece A3 (correction round 2): the pair route stands
        # under the same provenance rule as the single-act
        # route — a caller-supplied instance_id is stripped, so
        # no case act can carry instance provenance the doorway
        # did not establish. Neither payload legitimately names
        # an instance: the correction names a case, the
        # verification names a case version.
        corrected.pop("instance_id", None)
        verified.pop("instance_id", None)
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
            # Piece A3 (correction round 1): the loop's
            # iteration bookkeeping is not a subject change.
            # A LOOP_ITERATION event carries the case binding
            # because it accounts a call made under that case —
            # it changes no case content, and an act whose view
            # precedes it is not stale about its subject for
            # the bookkeeping's standing there. (A genuine
            # change — a correction, a contribution touching
            # the subject — still refuses, exactly as before.)
            if ev["type"] == "LOOP_ITERATION":
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

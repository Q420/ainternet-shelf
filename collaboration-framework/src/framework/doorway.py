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

from fabric.canonical import canonical

from . import gates as _gates
from . import orchestrator as _orch
from . import probe as _probe
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

# Response-evidence piece (WORKER-RESPONSE-EVIDENCE-SCOPE
# Rev 8): the disposition contract's tables, held here as
# the doorway's own copy — the loop derives dispositions
# from the seam (framework.evidence) and this route
# validates them at write time against these tables; the
# checker reconstructs the same rules from its third copy.
# The one class a no_response disposition may name, and
# the pre-response error-kind family its seam evidence
# must carry (R5-1/R6-3: phase observation + kind in the
# family + the transport's agreement, all three).
RESPONSE_NO_RESPONSE_CLASS = "connection_failed_pre_response"
RESPONSE_PRE_RESPONSE_KINDS = frozenset({
    "ConnectionRefusedError", "ConnectionResetError",
    "ConnectionAbortedError", "BrokenPipeError",
    "gaierror", "SSLError", "SSLCertVerificationError",
    "TimeoutError", "socket.timeout", "URLError",
    "RemoteDisconnected", "EOFError",
})
# The classes an unresolved disposition may name (R4-2
# as revised by R5-1).
RESPONSE_UNRESOLVED_CLASSES = frozenset({
    "timeout_after_send", "helper_exit_no_envelope",
    "envelope_unparseable", "termination_unconfirmed",
    "transport_internal_error",
})
# The closed set of pre-call terminal steps (R4-3): an
# iteration may terminate without a disposition only at
# one of these, named in its terminal's payload.
PRE_CALL_TERMINAL_STEPS = frozenset({
    "package_construction", "deadline_at_start"})
# The failed operations an evidence-capture-failure
# terminal may name (R8-2).
EVIDENCE_FAILURE_OPERATIONS = frozenset({
    "persist", "verify", "commit"})
# The capture ceiling (R7-1/R8-1): the largest body the
# evidence contract undertakes to hold whole. The
# boundary arithmetic is enforced here, at write time,
# against the disposition's own claims — not inferred
# from the helper's behaviour: eof stands only below
# the ceiling, capture_limit only exactly at it, and
# read_failure only below it with its error kind named.
RESPONSE_CAPTURE_CEILING = 64000

# Piece A3 (correction round 2): the act types whose payload's
# instance_id is the act's subject referent, not its author's
# provenance — the assembly lifecycle acts and an instance's
# onboarding, where the doorway itself cross-checks the named
# instance against the record before the act may stand. On
# every other seat-route act a caller-supplied instance_id is
# stripped (see act()): provenance in the record is
# doorway-established or it is not there.
INSTANCE_REFERENT_ACTS = frozenset({
    "ASSEMBLY_GENERATED", "ASSEMBLY_PROBED", "ASSEMBLY_VERIFIED",
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
    # Native-mode probe piece: the probe is an office act, like
    # generation — the office runs it and records its evidence;
    # the judgement it feeds remains the examiner's own.
    "ASSEMBLY_PROBED": {"orchestrator"},
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

    def activation_deadline(self, instance_id):
        """(deadline, problem): the instance's activation
        deadline as an ABSOLUTE monotonic instant — the
        doorway's own anchor plus the pinned case's deadline
        (INDEX 222). The value is the ORIGINAL deadline:
        derived from the stored anchor at every read,
        identical at every read, never re-sampled into a
        duration and never re-based — so a caller that
        propagates it (the loop, to its callable) propagates
        the activation's one clock itself, not a
        reconstruction of it that drifts by whatever time
        passes between a sampling and an invocation.
        deadline is None where the pinned case carries no
        deadline regime; problem is set where the anchor
        cannot be established."""
        state = self.state()
        _, entry = self._assembly_entry_of_instance(
            state, instance_id)
        if entry is None or entry.get("activated_seq") is None:
            return None, ("the instance holds no standing "
                          "activation")
        return self._activation_deadline(state, entry)

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
        # Response-evidence piece (R7-2): no bypass — a
        # request may not be admitted while an entered
        # iteration's response disposition is outstanding
        # for this instance; the obligation cannot be
        # stepped around by dispatching.
        _aid, outstanding = self._instance_outstanding(
            state, instance_id)
        if outstanding is not None:
            self._refuse(
                seat_id, "TOOL_REQUESTED",
                "an entered iteration's response "
                "disposition stands outstanding for this "
                "instance; no dispatch is admitted while "
                "it is owed (R7-2)")
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
        # Aggregate admission (retrieval scope §3a): under a
        # retrieval-governed assembly, a retrieval request is
        # admitted only if the package window's settled
        # retrieved content plus this request's worst-case
        # return stays within the aggregate ceiling —
        # enforced here, before any dispatch intent exists,
        # so a refused admission creates no dispatch and
        # leaves no claim to settle. Ordered after the grant
        # and temporal checks: a request no grant admits is
        # refused on its grant ground, never on the aggregate.
        generated = self._generated_payload(assembly_id)
        governed = self._retrieval_governed(generated)
        exec_governed = self._exec_governed(generated)
        # The aggregate admission does not stand under the
        # working-set contract (freedom-first setup pass,
        # 2026-11-24): its bound governs the retrieved
        # content one package SERVES, and under that
        # contract a package's growth is governed at
        # carriage by the working-set budget and dedupe —
        # the protection the aggregate ceiling and the
        # per-result ceiling together served, kept at the
        # place the growth happens. Admission here keeps
        # exactly its authority: the grant check above and
        # the temporal check; nothing dispatches until the
        # call is right.
        if governed and tool in _tool_policy.RETRIEVAL_TOOLS \
                and not self._working_set_declared(generated):
            ground = self._retrieval_aggregate_problem(
                state, entry, instance_id)
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
             # another version is not verifiable by it. A
             # retrieval-governed assembly's dispatches are
             # governed by v3 (retrieval scope): the version
             # follows the assembly's declared contract, as
             # the catalogue's does.
             "registry_version":
                 _tool_policy.EXEC_REGISTRY_VERSION
                 if exec_governed else
                 _tool_policy.RETRIEVAL_REGISTRY_VERSION
                 if governed else
                 _tool_policy.REGISTRY_VERSION})
        self.store.commit()
        return {"ok": True, "duplicate": False,
                "instance_id": instance_id,
                "request_id": request_id,
                "dispatch_id": dispatch_id, "outcome": None,
                "reconciled_outcome": None}

    @staticmethod
    def _exec_governed(generated):
        """Whether a sealed generated record declares the
        exec catalogue contract (room-exec configuration,
        gate 4): the compatibility discriminator for the
        exec regime — v4 dispatch and catalogue — exactly as
        the retrieval declaration discriminates its own. An
        assembly whose record declares anything else (or
        nothing) is not governed: its dispatches keep the
        behaviour they have always had."""
        return isinstance(generated, dict) and \
            generated.get("catalogue_contract") == \
            _tool_policy.EXEC_CATALOGUE_CONTRACT

    @staticmethod
    def _retrieval_governed(generated):
        """Whether a sealed generated record stands under
        the retrieval regime (RETRIEVAL-SCOPE Rev 5): the
        compatibility discriminator for the regime — the two
        authority paths, the aggregate admission, the
        per-grant catalogue, single carriage, governed
        performance — exactly as the A3-CAT catalogue
        contract discriminates its own.

        Two declarations stand under it. A record declaring
        the retrieval contract (retrieval-v3) is the
        retrieval piece's own assembly. A record declaring
        the exec contract (exec-v4) ALSO stands under it
        for its retrieval tools (the combined configuration,
        INDEX 476): the v4 registry view is the frozen v3
        view whole — taken from it, so the two cannot drift
        — plus the one execution tool, so the regime v4
        carries for the retrieval family is v3's regime
        itself, and an exec assembly's retrieval grants are
        enforced under it exactly as a retrieval assembly's
        are. The assembly's dispatch version remains its
        declared contract's own (v4 under the exec
        declaration — the version selection prefers it), so
        the widening changes no version stamp. An
        exec-declaring assembly WITHOUT retrieval grants is
        unaffected in outcome: the regime engages only for
        retrieval tools, and no grant admits those either
        way. An assembly whose record declares anything
        else (or nothing) is not governed: its dispatches
        keep the behaviour they have always had."""
        return isinstance(generated, dict) and \
            generated.get("catalogue_contract") in (
                _tool_policy.RETRIEVAL_CATALOGUE_CONTRACT,
                _tool_policy.EXEC_CATALOGUE_CONTRACT)

    @staticmethod
    def _working_set_declared(generated):
        """Whether a sealed generated record declares the
        working-set contract (the run-3 correction): the
        combined configuration's assemblies declare it
        beside their catalogue contract, and their wake
        packages carry the gathered material forward under
        the working-set budget. The declaration is the
        discriminator for the freedom-first setup pass's
        carriage honesty: under it, a retrieval read
        returns its full content at execution and package
        growth is governed at carriage, so the retrieval
        regime's per-result and aggregate ceilings — the
        bounds that governed what one package may SERVE —
        do not stand at admission or execution for these
        assemblies. The grant check, the boundary
        enforcement and the temporal admission are
        untouched: the doorway's authority does not move."""
        return isinstance(generated, dict) and \
            generated.get("working_set_contract") == \
            _tool_policy.WORKING_SET_CONTRACT

    def _freshness_suspended(self, state, presented_instance):
        """Whether the instance an act is presented under
        stands under Ben's R31 ruling (2026-11-24: "Disable
        R31 until we need to worry about that"): its sealed
        generated record declares the freshness guard
        suspended (tool_policy.FRESHNESS_GUARD_SUSPENDED).
        The ruling's ground is recorded with the constant:
        the one-worker demonstration excludes the staleness
        hazard by construction, and the guard as it stood
        refused the worker's deliveries for record movement
        the framework's own bookkeeping caused (run 5: each
        governed iteration's response-evidence event names
        the case, so every contribution answered from a
        frozen view stood "changed since view" by the time
        it was adjudicated). The declaration is the
        discriminator, read from the sealed record exactly
        as the contracts are; an unrecognised value is not
        the suspension (the guard stands — a declaration
        never loosens a guard by being misunderstood), and
        an act presented under no instance credential, or
        an instance with no declaration, stands under the
        guard exactly as every act always has."""
        if presented_instance is None:
            return False
        assembly_id = None
        for aid, entry in state["assemblies"].items():
            if entry.get("instance_id") == presented_instance:
                assembly_id = aid
                break
        if assembly_id is None:
            return False
        generated = self._generated_payload(assembly_id)
        return isinstance(generated, dict) and \
            generated.get("freshness_guard") == \
            _tool_policy.FRESHNESS_GUARD_SUSPENDED

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
        governed = self._retrieval_governed(generated)
        if governed and tool in _tool_policy.RETRIEVAL_TOOLS:
            return self._retrieval_dispatch_check(
                state, entry, instance_id, grants, tool,
                parameters,
                version=_tool_policy.EXEC_REGISTRY_VERSION
                if self._exec_governed(generated) else
                _tool_policy.RETRIEVAL_REGISTRY_VERSION)
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
            tool, grant.get("scope_ceiling"), parameters,
            version=_tool_policy.EXEC_REGISTRY_VERSION
            if self._exec_governed(generated) else
            _tool_policy.RETRIEVAL_REGISTRY_VERSION
            if governed else None)
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

    def _retrieval_dispatch_check(self, state, entry,
                                  instance_id, grants, tool,
                                  parameters,
                                  version=_tool_policy
                                  .RETRIEVAL_REGISTRY_VERSION):
        """Why a retrieval dispatch may not be recorded under
        a retrieval-governed assembly, or None (retrieval
        scope, boundary enforcement): the request is admitted
        under exactly one of two authority paths, enforced
        here, not merely described. (a) Source retrieval —
        the path lies under sources/: admission requires a
        grant scoped to sources/ AND the path's membership in
        the pinned case's sealed evidence boundary. (b)
        Scratch retrieval — the path lies under scratch/:
        admission requires the separately sealed scratch
        grant, and nothing else; scratch is never source
        evidence, and the scratch grant exempts no other
        path. A path under neither scope is admitted by no
        path. A pathless search is admitted under the source
        path — its grant alone; the boundary governs which
        files the execution may search. The admitting grant
        is the first grant for the tool, in sealed order,
        whose ceiling the request satisfies and whose scope
        is the authority path's own scope; its authority
        trace must stand, and its bound counts the tool's
        dispatches for the instance, as every grant's bound
        does.

        The ceilings are checked under `version` — the
        registry version the assembly is dispatched under:
        v3 for a retrieval-declaring assembly, v4 for the
        combined (exec-declaring) one (INDEX 476). The two
        views' retrieval entries are the same frozen
        objects, so the check is the one check under either
        name; the version is the assembly's own so the
        record and the checker read the same policy."""
        path = parameters.get("path")
        if path is None and tool != "sandbox.search":
            return (f"{tool} requires a path parameter "
                    f"(retrieval scope §2)")
        authority = "source" if path is None else \
            _tool_policy.retrieval_authority(path)
        if authority is None:
            return (f"path {path!r} lies under neither the "
                    f"sources/ scope nor the scratch/ scope; "
                    f"no authority path admits it — source "
                    f"retrieval requires the grant and the "
                    f"sealed evidence boundary, scratch "
                    f"retrieval its own sealed grant "
                    f"(retrieval scope, boundary enforcement)")
        tool_grants = [g for g in grants
                       if isinstance(g, dict)
                       and g.get("tool") == tool]
        if not tool_grants:
            return (f"no grant for tool {tool} stands in the "
                    f"sealed assembly record of instance "
                    f"{instance_id}; a grant outside the sealed "
                    f"record does not exist for the doorway "
                    f"(R44)")
        scope_prefix = _tool_policy.SOURCE_SCOPE_PREFIX \
            if authority == "source" else \
            _tool_policy.SCRATCH_SCOPE_PREFIX
        admitting = None
        first_ground = None
        for grant in tool_grants:
            ok, ground = _tool_policy.check_ceiling(
                tool, grant.get("scope_ceiling"), parameters,
                version=version)
            if not ok:
                if first_ground is None:
                    first_ground = ground
                continue
            prefix = (grant.get("scope_ceiling") or {}).get(
                "path_prefix")
            if prefix != scope_prefix:
                if first_ground is None:
                    first_ground = (
                        f"the grant for tool {tool} whose "
                        f"ceiling admits path {path!r} is "
                        f"scoped to {prefix!r}, not the "
                        f"{scope_prefix!r} scope the "
                        f"{authority} authority path requires")
                continue
            admitting = grant
            break
        if admitting is None:
            return f"{first_ground} (R44)"
        trace = admitting.get("authority_trace")
        if not isinstance(trace, str) or not trace:
            return (f"the grant for tool {tool} in the sealed "
                    f"record carries no authority trace; a "
                    f"grant without a trace was never judged "
                    f"and packed (R44)")
        if authority == "source" and path is not None:
            content = self._pinned_case_content(state, entry)
            boundary = (content or {}).get(
                "evidence_boundary")
            if not _tool_policy.boundary_member(boundary,
                                                path):
                return (f"path {path!r} is not a member of "
                        f"the pinned case's sealed evidence "
                        f"boundary; source retrieval requires "
                        f"the grant AND boundary membership "
                        f"(retrieval scope, boundary "
                        f"enforcement)")
        bound = admitting.get("bound")
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

    def _retrieval_window_start(self, instance_id, entry):
        """The event position the package window now forming
        opened at (retrieval scope §3a): the frozen head —
        the cursor_to — of the instance's most recent
        LOOP_ITERATION, the package the worker last saw; or
        the instance's activation, where no package has been
        built yet. Retrieval outcomes settled after this
        position are the window's settled content: they are
        what the next package will present."""
        start = (entry or {}).get("activated_seq") or 0
        for ev in self.store.all_events():
            if ev["type"] == "LOOP_ITERATION" and \
                    ev["payload"].get("instance_id") == \
                    instance_id:
                cursor_to = ev["payload"].get("cursor_to")
                if isinstance(cursor_to, int) and \
                        not isinstance(cursor_to, bool):
                    start = cursor_to
        return start

    def _retrieval_aggregate_problem(self, state, entry,
                                     instance_id):
        """Why aggregate admission refuses a retrieval
        dispatch, or None (retrieval scope §3a): the sum of
        retrieved content settled in the current package
        window — result outcomes at their retained content
        sizes, uncertain outcomes at the full per-result
        ceiling (their content may exist; the bound assumes
        the worst) — plus the per-result ceiling (the new
        request's worst-case return) must not exceed the
        aggregate ceiling. The accounting is derived from
        the record alone, and admission is serialized by the
        callers' shape: each admitted dispatch's outcome
        settles before the next request reaches this check,
        so the settled total at every check already includes
        every previously admitted request. A refusal names
        the aggregate bound and the remaining allowance."""
        start = self._retrieval_window_start(instance_id,
                                             entry)
        tools = {}
        for ev in self.store.all_events():
            if ev["type"] == "TOOL_DISPATCHED":
                tools[ev["payload"].get("dispatch_id")] = \
                    ev["payload"].get("tool")
        # Each dispatch counts once, by its latest standing
        # outcome in the window: a result at its retained
        # size, an uncertainty at the full ceiling. (A delayed
        # report settling a standing uncertainty replaces its
        # contribution with the settled size — the dispatch
        # is one retrieval, counted once, as the checker
        # reconstructs it.)
        contributions = {}
        for ev in self.store.all_events():
            if ev["type"] != "TOOL_OUTCOME" or \
                    ev["event_seq"] <= start:
                continue
            payload = ev["payload"]
            if payload.get("instance_id") != instance_id:
                continue
            if tools.get(payload.get("dispatch_id")) not in \
                    _tool_policy.RETRIEVAL_TOOLS:
                continue
            if payload.get("outcome") == "uncertain":
                contributions[payload.get("dispatch_id")] = \
                    _tool_policy.RETRIEVAL_RESULT_CEILING
            elif payload.get("outcome") == "result":
                result = payload.get("result") or {}
                size = result.get("content_bytes")
                if not isinstance(size, int) or \
                        isinstance(size, bool) or size < 0:
                    # A settled retrieval result whose size
                    # the record cannot state counts at the
                    # ceiling — the bound assumes the worst.
                    size = _tool_policy.RETRIEVAL_RESULT_CEILING
                contributions[payload.get("dispatch_id")] = size
            elif payload.get("outcome") == "failure":
                contributions[payload.get("dispatch_id")] = 0
        total = sum(contributions.values())
        ceiling = _tool_policy.RETRIEVAL_RESULT_CEILING
        aggregate = _tool_policy.RETRIEVAL_AGGREGATE_CEILING
        if total + ceiling > aggregate:
            return (f"the aggregate retrieval ceiling for "
                    f"the package now forming is {aggregate} "
                    f"bytes of retrieved content; {total} "
                    f"bytes stand settled in this window, "
                    f"leaving {aggregate - total} — a further "
                    f"retrieval may return up to {ceiling} "
                    f"bytes and is refused before execution "
                    f"(retrieval scope §3a)")
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

    @staticmethod
    def _outstanding_iteration(loop_entry):
        """The iteration entry of a loop activation whose
        call was entered but whose response disposition is
        still owed (response-evidence piece, R6-2/R7-2),
        or None. An evidence failure terminal standing for
        the activation does not discharge the obligation —
        it ends the instance, which the routes check
        separately — so this reads the disposition alone."""
        for it in (loop_entry or {}).get("iterations") or []:
            if it.get("call_entered_seq") is not None and \
                    it.get("disposition_seq") is None:
                return it
        return None

    def _instance_outstanding(self, state, instance_id):
        """(assembly_id, iteration entry) where the named
        instance's activation owes a response disposition,
        else (None, None): the no-bypass test the act and
        tool-request routes apply (R7-2)."""
        assembly_id, entry = \
            self._assembly_entry_of_instance(state, instance_id)
        if entry is None:
            return None, None
        loop = state["loop_activations"].get(assembly_id) or {}
        return assembly_id, self._outstanding_iteration(loop)

    def record_call_entered(self, assembly_id, iteration,
                            iteration_seq):
        """The loop's call-boundary report (response-
        evidence piece, R5-2/R6-2): recorded immediately
        before the provider callable is invoked, under the
        loop identity. CALL_ENTERED means the framework
        durably crossed the call-entry boundary and
        committed to invoking the callable for that
        iteration — never proof the callable executed.
        The route admits it only for the latest recorded
        iteration of a standing, unstalled, un-evidence-
        failed activation, only once per iteration, and
        never after a stall: whichever of the boundary and
        a pre-call terminal stands first, the other is
        refused (mutual exclusivity, enforced in
        record_loop_stalled as well)."""
        with self.store.serialized():
            state = self.state()
            entry = state["assemblies"].get(assembly_id)
            if entry is None or \
                    entry.get("activated_seq") is None:
                self._loop_refuse(
                    "CALL_ENTERED",
                    (entry or {}).get("instance_id"),
                    f"no standing activation for assembly "
                    f"{assembly_id}; a call boundary records "
                    f"only against an activated instance")
            instance_id = entry.get("instance_id")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if loop.get("stalled") is not None:
                self._loop_refuse(
                    "CALL_ENTERED", instance_id,
                    "the activation stands stalled; no call "
                    "boundary records after a terminal")
            if loop.get("evidence_failed") is not None:
                self._loop_refuse(
                    "CALL_ENTERED", instance_id,
                    "the activation stands ended by an "
                    "evidence capture failure; nothing "
                    "further records for it (R8-2)")
            iterations = loop.get("iterations") or []
            target = None
            for it in iterations:
                if it.get("event_seq") == iteration_seq:
                    target = it
                    break
            if target is None or \
                    target.get("iteration") != iteration or \
                    not iterations or \
                    iterations[-1] is not target:
                self._loop_refuse(
                    "CALL_ENTERED", instance_id,
                    f"iteration_seq {iteration_seq!r} does "
                    f"not name the activation's latest "
                    f"recorded iteration {iteration!r}; a "
                    f"call boundary binds an existing "
                    f"iteration (R6-2)")
            if target.get("call_entered_seq") is not None:
                self._loop_refuse(
                    "CALL_ENTERED", instance_id,
                    "the iteration already stands entered; "
                    "at most one call boundary per iteration "
                    "(R6-2)")
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "iteration": iteration,
                "iteration_seq": iteration_seq}
            ev = self.store.append(
                "CALL_ENTERED", LOOP_ACTOR, [instance_id],
                payload)
            self.store.commit()
            return ev

    def record_response_evidence(self, assembly_id,
                                 iteration_seq, outcome,
                                 failure_class=None,
                                 seam_evidence=None,
                                 artifact_sha256=None,
                                 layers=None, provenance=None,
                                 http_status=None):
        """The loop's response disposition (response-
        evidence piece, R3-1/R4-1/R7-2): the iteration's
        typed terminal response state, admitted only from
        this loop route, only for an iteration whose
        CALL_ENTERED stands, exactly once — a second,
        whether identical, supplementary or contradictory,
        is refused, and a committed disposition is final.
        The outcome, its failure class and its supporting
        evidence are validated HERE, at write time,
        against the scope's contract (the class↔outcome
        pairing of R4-2/R5-1; the captured form's artifact
        hash and layer summaries; the no_response form's
        three-part agreement) — not deferred to the
        checker, which reconstructs the same rules."""
        with self.store.serialized():
            state = self.state()
            entry = state["assemblies"].get(assembly_id)
            if entry is None or \
                    entry.get("activated_seq") is None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE",
                    (entry or {}).get("instance_id"),
                    f"no standing activation for assembly "
                    f"{assembly_id}; a disposition records "
                    f"only against an activated instance")
            instance_id = entry.get("instance_id")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if loop.get("stalled") is not None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE", instance_id,
                    "the activation stands stalled; no "
                    "disposition records after a terminal")
            if loop.get("evidence_failed") is not None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE", instance_id,
                    "the activation stands ended by an "
                    "evidence capture failure; a disposition "
                    "recorded now would masquerade as the "
                    "obligation discharged (R8-2)")
            target = None
            for it in loop.get("iterations") or []:
                if it.get("event_seq") == iteration_seq:
                    target = it
                    break
            if target is None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE", instance_id,
                    f"iteration_seq {iteration_seq!r} names "
                    f"no recorded iteration of this "
                    f"activation; a disposition binds an "
                    f"existing iteration (R7-2)")
            if target.get("call_entered_seq") is None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE", instance_id,
                    "the iteration stands without a call "
                    "boundary; a disposition is admitted "
                    "only for an entered iteration (R7-2)")
            if target.get("disposition_seq") is not None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE", instance_id,
                    "the iteration already stands "
                    "dispositioned; exactly one disposition "
                    "per entered iteration, final once "
                    "committed (R7-2)")
            problem = self._disposition_problem(
                outcome, failure_class, seam_evidence,
                artifact_sha256, layers)
            if problem is not None:
                self._loop_refuse(
                    "RESPONSE_EVIDENCE", instance_id, problem)
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "iteration": target.get("iteration"),
                "iteration_seq": iteration_seq,
                "outcome": outcome}
            if failure_class is not None:
                payload["failure_class"] = failure_class
            if seam_evidence is not None:
                payload["seam_evidence"] = seam_evidence
            if artifact_sha256 is not None:
                payload["artifact_sha256"] = artifact_sha256
            if layers is not None:
                payload["layers"] = layers
            if provenance is not None:
                payload["provenance"] = provenance
            if http_status is not None:
                payload["http_status"] = http_status
            ev = self.store.append(
                "RESPONSE_EVIDENCE", LOOP_ACTOR,
                [instance_id], payload)
            self.store.commit()
            return ev

    @staticmethod
    def _disposition_problem(outcome, failure_class,
                             seam_evidence, artifact_sha256,
                             layers):
        """Why a response disposition may not stand, or
        None (response-evidence piece): the doorway's copy
        of the class↔outcome pairing and the required
        evidence per form (R4-2/R5-1/R7-1). A diagnostic
        string alone is never a basis — the class and its
        typed evidence fields are mandatory."""
        if outcome == "captured":
            if failure_class is not None:
                return ("a captured disposition names no "
                        "failure class; a response was "
                        "received (R4-1)")
            if not isinstance(artifact_sha256, str) or \
                    len(artifact_sha256) != 64:
                return ("a captured disposition carries "
                        "its artifact's sha256; captured "
                        "with no artifact is refused (R4-2)")
            if not isinstance(layers, dict) or \
                    not isinstance(layers.get("L1"), dict):
                return ("a captured disposition carries "
                        "the per-layer summaries, L1 first "
                        "(R2-3)")
            l1 = layers["L1"]
            if not isinstance(l1.get("byte_count"), int) \
                    or isinstance(l1.get("byte_count"), bool) \
                    or not isinstance(l1.get("sha256"), str) \
                    or len(l1.get("sha256") or "") != 64 \
                    or not isinstance(l1.get("complete"),
                                      bool) \
                    or l1.get("hash_subject") != \
                    "observed_bytes":
                return ("the captured L1 summary must "
                        "carry its observed byte count, "
                        "the sha256 of exactly those "
                        "bytes, its completeness, and "
                        "hash_subject observed_bytes "
                        "(R6-1/R7-1)")
            # A count of observed bytes cannot be
            # negative: the type check above admits any
            # integer, and a fabricated summary carrying
            # a negative count (its total length forged
            # to match) would otherwise pass every
            # relation below — the equality and ceiling
            # checks are all consistent with a negative
            # count. Refused at write time (build
            # re-examination, INDEX 316); the checker
            # independently rejects such an artifact
            # against its actual bytes.
            if l1.get("byte_count") < 0:
                return ("the captured L1 summary's byte "
                        "count is a count of observed "
                        "bytes; a negative count names no "
                        "observation (R6-1/R7-1)")
            # The duplicated completeness fields must
            # agree: the summary carries the artifact's
            # body_complete beside its complete, and a
            # summary in which they disagree — or in
            # which the duplicate is absent, so agreement
            # cannot be established — is invalid.
            if l1.get("body_complete") != \
                    l1.get("complete"):
                return ("the captured L1 summary's "
                        "body_complete and complete must "
                        "agree; a summary whose duplicated "
                        "completeness fields disagree (or "
                        "leave one unspoken) is invalid "
                        "(R7-1)")
            # The ceiling boundary arithmetic, enforced
            # against the summary's own claims (build
            # examination, INDEX 314): the stop reason
            # and the observed count must stand in the
            # one relation the capture contract permits.
            count = l1.get("byte_count")
            if l1.get("complete"):
                if l1.get("stop_reason") != "eof" or \
                        l1.get("total_length") != count:
                    return ("a complete L1 stands only on "
                            "an observed EOF, its total "
                            "length its observed count "
                            "(R8-1)")
                if count >= RESPONSE_CAPTURE_CEILING:
                    return ("a complete L1 stands only "
                            "below the capture ceiling: at "
                            "the ceiling no EOF could have "
                            "been observed, so completeness "
                            "there is unclaimable (R8-1)")
            else:
                if l1.get("stop_reason") not in (
                        "capture_limit", "read_failure") \
                        or l1.get("total_length") is not None:
                    return ("an incomplete L1 names its "
                            "stop reason (capture_limit or "
                            "read_failure) and leaves its "
                            "total length unknown (R7-1)")
                if l1.get("stop_reason") == \
                        "capture_limit" and \
                        count != RESPONSE_CAPTURE_CEILING:
                    return ("a capture_limit L1 stands "
                            "only at exactly the capture "
                            "ceiling; a capture that stopped "
                            "below it stopped for another "
                            "reason (R7-1/R8-1)")
                if l1.get("stop_reason") == \
                        "read_failure":
                    if count >= RESPONSE_CAPTURE_CEILING:
                        return ("a read_failure L1 stands "
                                "only below the capture "
                                "ceiling; at or past it the "
                                "capture stopped at the "
                                "limit, not at a failed read "
                                "(R7-1/R8-1)")
                    if not isinstance(
                            l1.get("read_error_kind"),
                            str) or \
                            not l1.get("read_error_kind"):
                        return ("a read_failure L1 names "
                                "the read error kind its "
                                "capture failed with; the "
                                "kind is part of the claim "
                                "(R6-1)")
            return None
        if outcome == "no_response":
            if failure_class != RESPONSE_NO_RESPONSE_CLASS:
                return (f"a no_response disposition names "
                        f"the one permitted class "
                        f"{RESPONSE_NO_RESPONSE_CLASS} "
                        f"(R5-1)")
            if not isinstance(seam_evidence, dict) or \
                    seam_evidence.get("phase") != \
                    "pre_response" or \
                    seam_evidence.get("error_kind") not in \
                    RESPONSE_PRE_RESPONSE_KINDS or \
                    seam_evidence.get("observed_status") \
                    is not None:
                return ("no_response requires the "
                        "three-part agreement: the "
                        "helper's pre_response phase "
                        "observation, an error kind in the "
                        "pre-response family, and no "
                        "observed status (R5-1/R6-3)")
            if artifact_sha256 is not None:
                return ("a no_response disposition "
                        "carries no artifact; nothing "
                        "exists to file (R3-1)")
            return None
        if outcome == "unresolved":
            if failure_class not in \
                    RESPONSE_UNRESOLVED_CLASSES:
                return (f"an unresolved disposition names "
                        f"a class from the unresolved table "
                        f"(R4-2/R5-1); {failure_class!r} "
                        f"does not stand there — and a "
                        f"no_response-supporting class "
                        f"under an unresolved outcome "
                        f"underclaims, which is refused "
                        f"likewise")
            if not isinstance(seam_evidence, dict) or \
                    not seam_evidence:
                return ("an unresolved disposition "
                        "carries its seam evidence; a "
                        "diagnostic string alone is no "
                        "basis (R4-2)")
            if artifact_sha256 is not None:
                return ("an unresolved disposition "
                        "carries no artifact (R4-1)")
            return None
        return (f"outcome {outcome!r} is not a response "
                f"disposition outcome; the outcomes are "
                f"captured, no_response and unresolved "
                f"(R4-1)")

    def record_evidence_capture_failure(self, assembly_id,
                                        iteration_seq,
                                        operation,
                                        detail=None):
        """The evidence mechanism's own failure terminal
        (response-evidence piece, R8-2): the no-bypass
        rule's single narrow exception. Recorded by this
        loop route only, for an iteration whose
        CALL_ENTERED stands and whose disposition is
        outstanding BECAUSE the named operation failed —
        the artifact could not be persisted, could not be
        read-back-verified, or the disposition could not
        be committed. It is terminal for the instance:
        after it, the doorway refuses everything further
        on the activation. It is NOT a disposition: it
        does not satisfy, replace or discharge the
        missing-disposition obligation, and it is never
        shaped like one."""
        with self.store.serialized():
            state = self.state()
            entry = state["assemblies"].get(assembly_id)
            if entry is None or \
                    entry.get("activated_seq") is None:
                self._loop_refuse(
                    "EVIDENCE_CAPTURE_FAILED",
                    (entry or {}).get("instance_id"),
                    f"no standing activation for assembly "
                    f"{assembly_id}; an evidence failure "
                    f"records only against an activated "
                    f"instance (R8-2)")
            instance_id = entry.get("instance_id")
            if operation not in \
                    EVIDENCE_FAILURE_OPERATIONS:
                self._loop_refuse(
                    "EVIDENCE_CAPTURE_FAILED", instance_id,
                    f"operation {operation!r} is not a "
                    f"failed evidence operation; the "
                    f"operations are persist, verify and "
                    f"commit (R8-2)")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if loop.get("stalled") is not None:
                self._loop_refuse(
                    "EVIDENCE_CAPTURE_FAILED", instance_id,
                    "the activation stands stalled; the "
                    "evidence failure terminal is not a "
                    "second terminal (R8-2)")
            if loop.get("evidence_failed") is not None:
                self._loop_refuse(
                    "EVIDENCE_CAPTURE_FAILED", instance_id,
                    "the activation already stands ended "
                    "by an evidence capture failure (R8-2)")
            target = None
            for it in loop.get("iterations") or []:
                if it.get("event_seq") == iteration_seq:
                    target = it
                    break
            if target is None or \
                    target.get("call_entered_seq") is None:
                self._loop_refuse(
                    "EVIDENCE_CAPTURE_FAILED", instance_id,
                    "the named iteration stands without a "
                    "call boundary; the evidence failure "
                    "terminal answers an entered iteration "
                    "whose disposition is outstanding "
                    "(R8-2)")
            if target.get("disposition_seq") is not None:
                self._loop_refuse(
                    "EVIDENCE_CAPTURE_FAILED", instance_id,
                    "the named iteration stands "
                    "dispositioned; no evidence obligation "
                    "is outstanding for it (R8-2)")
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "iteration": target.get("iteration"),
                "iteration_seq": iteration_seq,
                "operation": operation}
            if detail is not None:
                payload["detail"] = detail
            ev = self.store.append(
                "EVIDENCE_CAPTURE_FAILED", LOOP_ACTOR,
                [instance_id], payload)
            self.store.commit()
            return ev

    def record_translation(self, assembly_id, iteration_seq,
                           calls, artifact_sha256=None,
                           catalogue_hash=None,
                           registry_version=None):
        """The loop's translation record (native adapter
        piece, N32): the complete set of per-call
        translation and refusal decisions for one native
        iteration's response — a distinct record event,
        committed after the iteration's response-evidence
        disposition and before any dispatch of the
        iteration, bound to the exact response-evidence
        artifact hash. Admitted only from this loop route,
        only for the activation's latest recorded
        iteration, exactly once per iteration. Where the
        iteration was entered under the evidence regime,
        its disposition must already stand and the named
        artifact hash must be the disposition's own — a
        translation record that answers no committed
        disposition, or binds a different artifact, is
        refused. The decision set's shape and coherence
        are validated here, at write time (the entry
        contract of N32/N20/N22); the semantic
        reconstruction — resolution and validation re-run
        against the sealed catalogue and the captured
        calls — is the checker's."""
        with self.store.serialized():
            state = self.state()
            entry = state["assemblies"].get(assembly_id)
            if entry is None or \
                    entry.get("activated_seq") is None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED",
                    (entry or {}).get("instance_id"),
                    f"no standing activation for assembly "
                    f"{assembly_id}; a translation record "
                    f"records only against an activated "
                    f"instance (N32)")
            instance_id = entry.get("instance_id")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if loop.get("stalled") is not None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    "the activation stands stalled; no "
                    "translation record records after a "
                    "terminal (N32)")
            if loop.get("evidence_failed") is not None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    "the activation stands ended by an "
                    "evidence capture failure; nothing "
                    "further records for it (R8-2)")
            iterations = loop.get("iterations") or []
            target = None
            for it in iterations:
                if it.get("event_seq") == iteration_seq:
                    target = it
                    break
            if target is None or not iterations or \
                    iterations[-1] is not target:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    f"iteration_seq {iteration_seq!r} does "
                    f"not name the activation's latest "
                    f"recorded iteration; a translation "
                    f"record binds the iteration in flight "
                    f"(N32)")
            if target.get("call_entered_seq") is not None \
                    and target.get("disposition_seq") is None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    "the iteration's response disposition "
                    "stands outstanding; the translation "
                    "record commits after the disposition "
                    "and before any dispatch (N32)")
            if target.get("translation_seq") is not None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    "the iteration already stands with its "
                    "translation record; exactly one "
                    "translation record per iteration, "
                    "final once committed (N32)")
            if target.get("disposition_seq") is not None:
                disposition = self._event_at(
                    target["disposition_seq"]) or {}
                bound = (disposition.get("payload") or {}).get(
                    "artifact_sha256")
                if artifact_sha256 != bound:
                    self._loop_refuse(
                        "TRANSLATION_RECORDED", instance_id,
                        "the translation record must bind "
                        "the exact response-evidence "
                        "artifact hash its iteration's "
                        "disposition committed (N32)")
            elif artifact_sha256 is not None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    "the iteration stands without a "
                    "disposition; no artifact hash stands "
                    "to bind (N32)")
            problem = self._translation_problem(
                calls, catalogue_hash)
            if problem is not None:
                self._loop_refuse(
                    "TRANSLATION_RECORDED", instance_id,
                    problem)
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "iteration": target.get("iteration"),
                "iteration_seq": iteration_seq,
                "calls": copy.deepcopy(calls)}
            payload["artifact_sha256"] = artifact_sha256
            if catalogue_hash is not None:
                payload["catalogue_hash"] = catalogue_hash
            if registry_version is not None:
                payload["registry_version"] = registry_version
            ev = self.store.append(
                "TRANSLATION_RECORDED", LOOP_ACTOR,
                [instance_id], payload)
            self.store.commit()
            return ev

    @staticmethod
    def _translation_problem(calls, catalogue_hash):
        """Why a translation record's decision set may not
        stand, or None (native adapter piece): the entry
        contract the loop's preflight produces — one entry
        per individuable call in provider call order, each
        carrying the N32 field set, the refusal classes of
        §3/N22, and the coherence between an entry's
        classification and its disposition (a presented
        call stands resolved and valid under its loop
        request identity; a refused call stands under
        exactly one class, its unrun stages not_reached;
        an overflow call's arguments were never processed,
        so it carries no arguments hash)."""
        if catalogue_hash is not None and (
                not isinstance(catalogue_hash, str)
                or len(catalogue_hash) != 64):
            return ("a translation record carries the "
                    "catalogue hash it was resolved against "
                    "as a sha256 (N32)")
        if not isinstance(calls, list) or not calls:
            return ("a translation record carries one "
                    "entry per individuable call; an empty "
                    "decision set records nothing (N32)")
        classes = ("unknown_tool", "malformed_call",
                   "invalid_arguments", "call_cap_exceeded")
        for position, entry in enumerate(calls, start=1):
            if not isinstance(entry, dict):
                return ("each translation entry is an "
                        "object (N32)")
            if entry.get("provider_ordinal") != position:
                return ("translation entries stand in "
                        "provider call order, their ordinals "
                        "1..n without gaps (N20)")
            call_id = entry.get("provider_call_id")
            if call_id is not None and (
                    not isinstance(call_id, str)
                    or not call_id):
                return ("a translation entry's provider "
                        "call ID is the emitted string or "
                        "absent (N6)")
            name = entry.get("name")
            if name is not None and (
                    not isinstance(name, str) or not name):
                return ("a translation entry's name is "
                        "the emitted string or unreadable "
                        "(N6)")
            wire_name = entry.get("wire_name")
            if wire_name is not None and (
                    not isinstance(wire_name, str)
                    or not wire_name):
                return ("a translation entry's wire name, "
                        "where the route's translation "
                        "renamed the call, is the emitted "
                        "wire string (Ben's ruling, "
                        "2026-11-24)")
            digest = entry.get("arguments_sha256")
            if digest is not None and (
                    not isinstance(digest, str)
                    or len(digest) != 64):
                return ("a translation entry's arguments "
                        "hash is the sha256 of the parsed "
                        "arguments' canonical form, or "
                        "absent where the arguments were "
                        "never parsed (N32)")
            resolution = entry.get("resolution")
            validation = entry.get("validation")
            constraint = entry.get("validation_constraint")
            refusal = entry.get("refusal_class")
            detail = entry.get("refusal_detail")
            request_id = entry.get("loop_request_id")
            if constraint is not None and \
                    not isinstance(constraint, str):
                return ("a validation constraint is a "
                        "string or absent (N8)")
            if detail is not None and \
                    not isinstance(detail, str):
                return ("a refusal detail is a string or "
                        "absent (N6)")
            if refusal is None:
                if resolution != "resolved" or \
                        validation != "valid" or \
                        not isinstance(request_id, str) \
                        or not request_id:
                    return ("a presented call stands "
                            "resolved and valid under its "
                            "loop request identity (N20)")
            elif refusal not in classes:
                return (f"refusal class {refusal!r} is not "
                        f"a translation refusal class (§3)")
            elif request_id is not None:
                return ("a refused call carries no loop "
                        "request identity; nothing was "
                        "presented for it (N18)")
            elif refusal == "unknown_tool":
                if resolution != "unknown" or \
                        validation != "not_reached":
                    return ("an unknown_tool refusal "
                            "stands unresolved, its "
                            "validation not reached (N7)")
            elif refusal == "invalid_arguments":
                if resolution != "resolved" or \
                        validation != "invalid" or \
                        not isinstance(constraint, str) \
                        or not constraint:
                    return ("an invalid_arguments refusal "
                            "stands resolved and invalid, "
                            "its failing constraint named "
                            "(N8)")
            elif refusal == "malformed_call":
                if resolution != "not_reached" or \
                        validation != "not_reached":
                    return ("a malformed_call refusal "
                            "stands with resolution and "
                            "validation not reached (N13)")
            elif refusal == "call_cap_exceeded":
                if resolution != "not_reached" or \
                        validation != "not_reached" or \
                        digest is not None:
                    return ("a call_cap_exceeded refusal "
                            "stands with its arguments "
                            "never processed — no arguments "
                            "hash, no classification (N22)")
        return None

    def record_loop_iteration(self, assembly_id, iteration,
                              cursor_from, cursor_to,
                              catalogue_hash=None,
                              registry_version=None,
                              evidence_governed=False,
                              disable_tool_validation=None,
                              working_set_hash=None,
                              presentation_hash=None):
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
        the deadline has already expired. Piece A3-CAT: where
        the loop supplies them, the event also carries the
        tool catalogue's canonical hash and the registry
        version it was derived under — the loop's commitment,
        recorded as presented; the correspondence between the
        commitment and the sealed grants is the checker's
        reconstruction, not this route's. Response-evidence
        piece (build examination, INDEX 314): where the loop
        runs under the evidence regime it declares so here —
        evidence_governed stands in the iteration's payload
        from this first event of the iteration, so the
        activation's governed state is durable from the
        start and a death between this event and the call
        boundary cannot slip the regime; the checker governs
        every activation any iteration of which carries the
        mark. An unmarked iteration is a legacy scripted
        path's, and stays outside the regime."""
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
            if loop.get("evidence_failed") is not None:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    "the activation stands ended by an "
                    "evidence capture failure; no further "
                    "iteration records (R8-2)")
            # Response-evidence piece (R7-2): no bypass —
            # a further iteration may not record while a
            # previous entered iteration's disposition is
            # outstanding; the obligation cannot be stepped
            # around by moving on.
            if self._outstanding_iteration(loop) is not None:
                self._loop_refuse(
                    "LOOP_ITERATION", instance_id,
                    "a previous iteration's response "
                    "disposition stands outstanding; no "
                    "further iteration records while it is "
                    "owed (R7-2)")
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
            payload = {
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
                "cursor_to": cursor_to}
            if catalogue_hash is not None:
                payload["catalogue_hash"] = catalogue_hash
                payload["registry_version"] = registry_version
            if evidence_governed:
                payload["evidence_governed"] = True
            if disable_tool_validation is not None:
                # Native adapter piece (BD-1): the flag
                # state of this iteration's request
                # construction, recorded in the iteration's
                # commitment beside the catalogue hash and
                # registry version — the loop reads the
                # state from the callable's own construction,
                # so the commitment and the constructed body
                # cannot drift apart silently.
                payload["disable_tool_validation"] = \
                    bool(disable_tool_validation)
            if working_set_hash is not None:
                # Working-set carriage (the run-3
                # correction): the presented working set's
                # commitment, recorded in the iteration
                # beside the catalogue hash — the loop
                # derives the set from the record's own
                # outcomes and hashes the exact structure
                # the package presents, so the commitment
                # and the presentation cannot drift apart
                # silently; the checker reconstructs both.
                payload["working_set_hash"] = \
                    working_set_hash
            if presentation_hash is not None:
                # Staged onboarding (INDEX 544): the
                # presented package's commitment under the
                # sealed presentation contract, recorded in
                # the iteration beside the working-set hash —
                # the loop hashes the exact staged structure
                # the package presents (its bulk references —
                # the tool results and the working set —
                # standing in the core by their own recorded
                # commitments), so the commitment and the
                # presentation cannot drift apart silently;
                # the checker reconstructs both.
                payload["presentation_hash"] = \
                    presentation_hash
            ev = self.store.append(
                "LOOP_ITERATION", LOOP_ACTOR, [instance_id],
                payload)
            self.store.commit()
            return ev

    def _door_event_binding(self, assembly_id, type_):
        """The standing activation binding for a door-scope
        loop event (2026-11-24): the assembly's entry and
        its instance, or a refusal in the loop route's
        shape. Called inside the store's serialized
        boundary by the routes below."""
        state = self.state()
        entry = state["assemblies"].get(assembly_id)
        if entry is None or \
                entry.get("activated_seq") is None:
            self._loop_refuse(
                type_, (entry or {}).get("instance_id"),
                f"no standing activation for assembly "
                f"{assembly_id}; a {type_} records only "
                f"against an activated instance")
        loop = state["loop_activations"].get(
            assembly_id) or {}
        if loop.get("stalled") is not None:
            self._loop_refuse(
                type_, entry.get("instance_id"),
                "the activation stands stalled; no door "
                "event records after a terminal")
        if loop.get("evidence_failed") is not None:
            self._loop_refuse(
                type_, entry.get("instance_id"),
                "the activation stands ended by an "
                "evidence capture failure; nothing "
                "further records for it (R8-2)")
        return state, entry

    def record_deliverable_filed(self, assembly_id,
                                 contribution_seq,
                                 destination, content_sha256,
                                 authored_by):
        """The office's filing of an accepted contribution
        as the deliverable (door scope, 2026-11-24): a
        distinct recorded act, under the loop machinery's
        identity, carrying the filing's own facts — the
        declared destination, the filed content's hash,
        the contribution it files (by its event position),
        its author (the contributing worker) and its
        filer ("office"). The contribution stands recorded
        first; this route admits the filing only against
        that standing contribution of this activation's
        instance."""
        with self.store.serialized():
            state, entry = self._door_event_binding(
                assembly_id, "DELIVERABLE_FILED")
            instance_id = entry.get("instance_id")
            contribution = None
            for ev in self.store.all_events():
                if ev["event_seq"] == contribution_seq:
                    contribution = ev
                    break
            if contribution is None or \
                    contribution["type"] != "CONTRIBUTION" or \
                    contribution["actor"] != authored_by:
                self._loop_refuse(
                    "DELIVERABLE_FILED", instance_id,
                    "the named contribution does not stand "
                    "in the record under the named author; "
                    "a filing files a standing contribution")
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "contribution_seq": contribution_seq,
                "destination": destination,
                "content_sha256": content_sha256,
                "authored_by": authored_by,
                "filed_by": "office"}
            ev = self.store.append(
                "DELIVERABLE_FILED", LOOP_ACTOR,
                [instance_id], payload)
            self.store.commit()
            return ev

    def record_delivery_gate(self, assembly_id,
                             iteration_seq, raw_excerpt,
                             raw_length, parse_error):
        """The envelope gate's record (door scope,
        2026-11-24): a recognisable but unparseable
        contribution response was preserved through the
        response-evidence path and answered with a
        correction, not a stall. The event carries what
        arrived (a bounded excerpt and the response's
        length) and what failed (the parse error), bound
        to the iteration it answers."""
        with self.store.serialized():
            state, entry = self._door_event_binding(
                assembly_id, "DELIVERY_GATE")
            instance_id = entry.get("instance_id")
            loop = state["loop_activations"].get(
                assembly_id) or {}
            if not any(it.get("event_seq") == iteration_seq
                       for it in loop.get("iterations")
                       or []):
                self._loop_refuse(
                    "DELIVERY_GATE", instance_id,
                    "the named iteration does not stand "
                    "for this activation; a gate binds an "
                    "existing iteration")
            payload = {
                "assembly_id": assembly_id,
                "instance_id": instance_id,
                "activated_seq": entry.get("activated_seq"),
                "case_id": entry.get("case_id"),
                "case_version": entry.get("case_version"),
                "iteration_seq": iteration_seq,
                "raw_excerpt": raw_excerpt,
                "raw_length": raw_length,
                "parse_error": parse_error}
            ev = self.store.append(
                "DELIVERY_GATE", LOOP_ACTOR,
                [instance_id], payload)
            self.store.commit()
            return ev

    def record_loop_stalled(self, assembly_id, ground,
                            detail=None, terminal_step=None):
        """The loop's stall report (Piece A3, R50): the
        recorded stop, under the loop identity, valid only
        against a standing activation that has not already
        stalled, with a ground from the settled vocabulary —
        and only once dispatch accounting has closed for the
        activation: every dispatch of the instance standing in
        the record holds an attributable outcome or an
        examiner's reconciliation. A stall recorded earlier
        would leave an in-flight dispatch's outcome with
        nowhere lawful to land.

        Response-evidence piece: while an entered
        iteration's disposition is outstanding, EVERY stall
        is refused (R7-2's no-bypass) — the single exception
        is not a stall at all but the EVIDENCE_CAPTURE_FAILED
        terminal, admitted by its own route. A stall may
        carry terminal_step naming the pre-call step it
        answers (R4-3's closed set); a terminal_step stall
        and a standing call boundary for the iteration it
        answers are mutually exclusive here as in the
        checker, and where the activation's record shows the
        call boundary regime in force (an earlier iteration
        stands entered) a final iteration without a boundary
        may terminate only under a named step."""
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
            if loop.get("evidence_failed") is not None:
                self._loop_refuse(
                    "LOOP_STALLED", instance_id,
                    "the activation stands ended by an "
                    "evidence capture failure; no stall "
                    "records after that terminal (R8-2)")
            if self._outstanding_iteration(loop) is not None:
                self._loop_refuse(
                    "LOOP_STALLED", instance_id,
                    "an entered iteration's response "
                    "disposition stands outstanding; no "
                    "stall records while it is owed — the "
                    "only terminal admitted in that state "
                    "is the evidence capture failure "
                    "(R7-2/R8-2)")
            if terminal_step is not None and \
                    terminal_step not in PRE_CALL_TERMINAL_STEPS:
                self._loop_refuse(
                    "LOOP_STALLED", instance_id,
                    f"terminal_step {terminal_step!r} is "
                    f"not a pre-call step; the set is "
                    f"closed (R4-3)")
            iterations = loop.get("iterations") or []
            if iterations:
                # Mutual exclusivity is per iteration
                # (R5-2): a terminal_step names the step
                # the CURRENT iteration died at — either
                # the final recorded iteration, standing
                # without a call boundary, or an iteration
                # that never recorded at all. An entered
                # iteration is never answered by one: an
                # entered-undispositioned final iteration
                # was already refused above (its only
                # terminal is the evidence failure), and an
                # entered-and-dispositioned one is complete
                # — the step names its successor.
                last = iterations[-1]
                governed = any(
                    it.get("call_entered_seq") is not None
                    for it in iterations)
                if governed and \
                        last.get("call_entered_seq") is None \
                        and terminal_step is None:
                    self._loop_refuse(
                        "LOOP_STALLED", instance_id,
                        "the final iteration stands "
                        "without a call boundary in an "
                        "activation under the call-boundary "
                        "regime; its terminal must name "
                        "its pre-call step (R4-3)")
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
            if terminal_step is not None:
                payload["terminal_step"] = terminal_step
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
        # Response-evidence piece (R7-2): no bypass — an
        # act under an instance's own credential may not
        # be admitted while that instance's entered
        # iteration owes its response disposition; the
        # obligation cannot be stepped around by acting.
        presented_instance = self._presented_instance(token)
        if presented_instance is not None:
            _aid, outstanding = self._instance_outstanding(
                state, presented_instance)
            if outstanding is not None:
                self._refuse(
                    seat_id, type_,
                    "an entered iteration's response "
                    "disposition stands outstanding for "
                    "this instance; no act is admitted "
                    "while it is owed (R7-2)", view_seq)
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
        if type_ in ("ASSEMBLY_GENERATED", "ASSEMBLY_PROBED",
                     "ASSEMBLY_VERIFIED",
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
        #
        # Ben's ruling (2026-11-24: "Disable R31 until we need
        # to worry about that"): where the act is presented
        # under an instance whose sealed record declares the
        # freshness guard suspended, the rejection does not
        # stand for that instance's acts — the act records,
        # flagged stale_basis like any behind-view act, and
        # the subject check is not run. The rule itself is
        # untouched: for every other act — a seat's own, an
        # undeclared instance's — the rejection stands
        # exactly as it always has, and the declaration's
        # return to force needs no code change, only a
        # generation made without it.
        payload = dict(payload)
        head = state["head_seq"]
        if view_seq < head:
            # R31 (correction round 2): the specified subjects are
            # the contribution, the tree part, and the case version —
            # every named subject is checked, not only the first.
            subjects = [payload.get(k) for k in
                        ("subject_id", "claim_id", "contribution_id",
                         "tree_part", "case_id")]
            if not self._freshness_suspended(
                    state, presented_instance):
                for subject in subjects:
                    if subject and self._subject_changed(
                            subject, view_seq):
                        self._refuse(
                            seat_id, type_,
                            f"subject {subject} changed since "
                            f"view at seq {view_seq} (R31)",
                            view_seq)
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
        if type_ == "ASSEMBLY_PROBED":
            return self._assembly_probed_problem(
                state, entry, payload)
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
        if type_ == "ASSEMBLY_VERIFIED" and \
                self._probe_governed(
                    self._generated_payload(assembly_id)):
            # Native-mode probe piece (scope §4): under a
            # probe-governed assembly, verification answers the
            # probe, not generation directly — the probe stands
            # between them in the normative order.
            own_seq, prior_seq, prior_name = (
                "verified_seq", "probed_seq",
                "the native-mode probe")
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
        if type_ in ("ASSEMBLY_VERIFIED", "ASSEMBLY_JUDGED",
                     "ASSEMBLY_PACKED") and \
                self._probe_governed(
                    self._generated_payload(assembly_id)):
            return self._probe_chain_problem(
                entry, type_, payload, assembly_id)
        return None

    @staticmethod
    def _probe_governed(generated):
        """Whether a sealed generated record declares the
        native-mode probe contract (probe scope §1/§4): the
        compatibility discriminator for the whole probe regime
        — the probe stage, the binding chain, the adapter mode —
        exactly as the retrieval contract discriminates its own.
        An assembly whose record declares anything else (or
        nothing) is not governed: its lifecycle keeps the
        behaviour it has always had."""
        return isinstance(generated, dict) and \
            generated.get("probe_contract") == \
            _probe.PROBE_CONTRACT

    def _probed_payload(self, assembly_id):
        """The ASSEMBLY_PROBED payload standing for an assembly,
        or None — the evidence object the later lifecycle acts
        answer to under the probe regime."""
        for ev in self.store.all_events():
            if ev["type"] == "ASSEMBLY_PROBED" and \
                    ev["payload"].get("assembly_id") == \
                    assembly_id:
                return ev["payload"]
        return None

    def _assembly_probed_problem(self, state, entry, payload):
        """Why an ASSEMBLY_PROBED may not be recorded, or None
        (probe scope §2–§5): the assembly must declare the probe
        contract in its sealed generated record (an unknown
        declaration fails; absence is the historical exemption
        and grounds no probe); the act binds the exact generated
        record by its hash and binds its evidence hash to it;
        the suite identity, the configuration fingerprint, the
        per-trial evidence (classes, settled flags, per-object
        hashes, byte counts, the aggregate ceiling, per-object
        completeness) and the counts, quorum and recommendation
        all recompute from what the payload itself carries — a
        probe act whose own arithmetic does not reconcile does
        not stand."""
        assembly_id = payload.get("assembly_id")
        if entry.get("probed_seq") is not None:
            return (f"assembly {assembly_id} already stands "
                    f"with its ASSEMBLY_PROBED recorded; the "
                    f"lifecycle is one-to-one (R40)")
        generated = self._generated_payload(assembly_id)
        declared = (generated or {}).get("probe_contract")
        if declared is None:
            return ("the generated assembly declares no probe "
                    "contract; the probe stage is not part of "
                    "this assembly's lifecycle (probe scope §1)")
        if declared != _probe.PROBE_CONTRACT:
            return (f"the generated assembly declares probe "
                    f"contract {declared!r}, which this doorway "
                    f"does not know; an unknown declaration "
                    f"fails (probe scope §1)")
        digest = assembly_record_hash(generated or {})
        if payload.get("generated_record_hash") != digest:
            return ("ASSEMBLY_PROBED names generated record "
                    f"hash {payload.get('generated_record_hash')!r}; "
                    f"the generated assembly's canonical hash is "
                    f"{digest} — the probe binds the exact "
                    f"generated record (probe scope §4)")
        if payload.get("suite") != _probe.SUITE_NAME or \
                payload.get("suite_hash") != _probe.SUITE_HASH:
            return ("the probe act does not identify the "
                    "versioned suite native-probe-v1 by its "
                    "canonical hash (probe scope §2)")
        fingerprint = _probe.configuration_fingerprint(
            payload.get("route"), payload.get("model"))
        if payload.get("fingerprint") != fingerprint:
            return ("the probe act's configuration fingerprint "
                    "does not recompute from its route, model, "
                    "suite, offered definitions, parameters and "
                    "tool-choice configuration (probe scope §7)")
        trials = payload.get("trials")
        if not isinstance(trials, list) or \
                len(trials) != _probe.TRIAL_COUNT:
            return (f"the probe act carries "
                    f"{len(trials) if isinstance(trials, list) else 'no'} "
                    f"trials; the suite runs exactly "
                    f"{_probe.TRIAL_COUNT} (probe scope §2)")
        for position, trial in enumerate(trials, start=1):
            problem = self._probe_trial_problem(trial, position)
            if problem is not None:
                return problem
        counts, settled, recommended = _probe.summarise(trials)
        if payload.get("counts") != counts or \
                payload.get("settled_count") != settled or \
                payload.get("recommended_mode") != recommended:
            return ("the probe act's counts, settled count or "
                    "recommendation do not recompute from its "
                    "trials under the quorum rule (probe scope "
                    "§3/§5)")
        if payload.get("evidence_hash") != \
                _probe.evidence_hash(payload):
            return ("the probe act's evidence hash does not "
                    "recompute over its recorded evidence; the "
                    "binding the judgement and the pack will "
                    "name must be the evidence's own hash "
                    "(probe scope §4)")
        return None

    @staticmethod
    def _probe_trial_problem(trial, position):
        """Why one recorded probe trial is not well-formed
        evidence, or None: the classes are the scope's, the
        settled flag is the behaviour's own consequence, every
        retained object's hash and byte count recompute from the
        retained text, the aggregate is the content objects'
        sum under the ceiling, and completeness is per object —
        an object cut by the ceiling stands incomplete, and
        nothing stands incomplete that the ceiling did not
        force."""
        if not isinstance(trial, dict):
            return f"probe trial {position} is not an object"
        if trial.get("trial") != position:
            return (f"probe trial at position {position} names "
                    f"itself {trial.get('trial')!r} (probe "
                    f"scope §3)")
        behaviour = trial.get("behaviour")
        if behaviour not in _probe.BEHAVIOURS:
            return (f"probe trial {position} carries behaviour "
                    f"{behaviour!r}, not one of the scope's "
                    f"classes (probe scope §3)")
        if trial.get("delivery") not in _probe.DELIVERIES:
            return (f"probe trial {position} carries delivery "
                    f"{trial.get('delivery')!r}, not one of the "
                    f"scope's classes (probe scope §3)")
        if trial.get("payload_form") not in (
                None, "text_contract_json"):
            return (f"probe trial {position} carries "
                    f"payload_form "
                    f"{trial.get('payload_form')!r} (probe "
                    f"scope §3)")
        if trial.get("settled") != \
                (behaviour != "no_observable_behaviour"):
            return (f"probe trial {position}'s settled flag "
                    f"contradicts its behaviour class (probe "
                    f"scope §3)")
        body = trial.get("provider_body")
        if body is not None and not isinstance(body, str):
            return (f"probe trial {position}'s provider body "
                    f"is not text")
        body_bytes = len(body.encode("utf-8")) \
            if body is not None else 0
        if trial.get("provider_body_bytes") != body_bytes:
            return (f"probe trial {position}'s provider body "
                    f"byte count does not recompute (probe "
                    f"scope §3)")
        body_hash = hashlib.sha256(
            body.encode("utf-8")).hexdigest() \
            if body is not None else None
        if trial.get("provider_body_sha256") != body_hash:
            return (f"probe trial {position}'s provider body "
                    f"hash does not recompute over the retained "
                    f"body (probe scope §3)")
        if not isinstance(
                trial.get("provider_body_complete"), bool) or \
                not isinstance(
                    trial.get("diagnostics_complete"), bool):
            return (f"probe trial {position}'s completeness "
                    f"standings are not booleans (probe "
                    f"scope §3)")
        diag = trial.get("diagnostics")
        if diag is not None and not isinstance(diag, str):
            return (f"probe trial {position}'s diagnostics "
                    f"are not text")
        diag_bytes = len(diag.encode("utf-8")) \
            if diag is not None else 0
        if trial.get("diagnostics_bytes") != diag_bytes:
            return (f"probe trial {position}'s diagnostics "
                    f"byte count does not recompute (probe "
                    f"scope §3)")
        diag_hash = hashlib.sha256(
            diag.encode("utf-8")).hexdigest() \
            if diag is not None else None
        if trial.get("diagnostics_sha256") != diag_hash:
            return (f"probe trial {position}'s diagnostics "
                    f"hash does not recompute over the retained "
                    f"diagnostics (probe scope §3)")
        aggregate = trial.get("aggregate_bytes")
        if aggregate != body_bytes + diag_bytes:
            return (f"probe trial {position}'s aggregate is "
                    f"not the sum of its content objects "
                    f"(probe scope §3)")
        if not isinstance(aggregate, int) or \
                aggregate > _probe.CAPTURE_CEILING:
            return (f"probe trial {position}'s aggregate "
                    f"exceeds the per-trial capture ceiling "
                    f"(probe scope §3)")
        body_complete = trial.get("provider_body_complete")
        if body is None and body_complete:
            return (f"probe trial {position} labels an absent "
                    f"provider body complete (probe scope §3)")
        diag_complete = trial.get("diagnostics_complete")
        if diag is None and diag_complete is not True:
            return (f"probe trial {position}'s absent "
                    f"diagnostics carry no completeness standing")
        # A PRESENT object standing incomplete means the
        # ceiling cut it — which can only have happened with
        # the aggregate at the ceiling. (An ABSENT object is
        # honestly incomplete at any aggregate: nothing was
        # produced, so nothing was cut.)
        if (body is not None and body_complete is not True
                or diag is not None
                and diag_complete is not True) and \
                aggregate != _probe.CAPTURE_CEILING:
            return (f"probe trial {position} stands incomplete "
                    f"below the capture ceiling; the ceiling "
                    f"did not force the cut, so the evidence "
                    f"mislabels itself (probe scope §3)")
        if trial.get("evidence_complete") != \
                (body_complete is True):
            return (f"probe trial {position}'s evidence "
                    f"completeness is not its provider body's "
                    f"(probe scope §3)")
        metadata = trial.get("metadata")
        if not isinstance(metadata, dict):
            return (f"probe trial {position}'s metadata is "
                    f"not an object")
        if trial.get("metadata_sha256") != hashlib.sha256(
                canonical(metadata)).hexdigest():
            return (f"probe trial {position}'s metadata hash "
                    f"does not recompute (probe scope §3)")
        return None

    def _probe_chain_problem(self, entry, type_, payload,
                             assembly_id):
        """Why a governed lifecycle act's probe binding may not
        stand, or None (probe scope §4): verification names the
        standing probe evidence — the verified assembly's
        integrity boundary covers it (INDEX 285); the judgement
        identifies the exact probe event and evidence, records
        the selected mode with its grounds, and binds the hash
        of the examiner's durable decision receipt (INDEX 293 —
        the decision's own provenance, without which the mode
        and grounds are bare caller arguments); the pack
        seals the same bindings and the judged mode itself, so
        the mode the adapter receives is the mode the examiner
        judged."""
        probed = self._probed_payload(assembly_id)
        evidence_hash = (probed or {}).get("evidence_hash")
        if payload.get("probe_evidence_hash") != evidence_hash:
            return (f"{type_} names probe evidence hash "
                    f"{payload.get('probe_evidence_hash')!r}; "
                    f"the standing probe evidence hashes to "
                    f"{evidence_hash} — the act must bind the "
                    f"exact evidence (probe scope §4)")
        if type_ == "ASSEMBLY_JUDGED":
            if payload.get("probe_seq") != \
                    entry.get("probed_seq"):
                return ("the judgement names probe event "
                        f"{payload.get('probe_seq')!r}; the "
                        f"assembly's probe stands at "
                        f"{entry.get('probed_seq')} — the "
                        f"judgement identifies the exact probe "
                        f"event (probe scope §4)")
            if payload.get("adapter_mode") not in \
                    _probe.ADAPTER_MODES:
                return ("the judgement selects adapter mode "
                        f"{payload.get('adapter_mode')!r}; the "
                        f"modes are text and native (probe "
                        f"scope §5)")
            grounds = payload.get("mode_grounds")
            if not isinstance(grounds, str) or not grounds:
                return ("the judgement records no grounds for "
                        "its mode; a mode without grounds does "
                        "not seal (probe scope §5)")
            receipt_hash = payload.get(
                "decision_receipt_hash")
            if not isinstance(receipt_hash, str) or \
                    len(receipt_hash) != 64 or \
                    any(c not in "0123456789abcdef"
                        for c in receipt_hash):
                return ("the judgement binds no examiner "
                        "decision receipt: "
                        f"decision_receipt_hash "
                        f"{receipt_hash!r} is not the SHA-256 "
                        f"of the examiner's durable decision "
                        f"receipt — a judgement's mode and "
                        f"grounds must arrive bound to the "
                        f"receipt that carries them, not as "
                        f"bare caller arguments (INDEX 293)")
        if type_ == "ASSEMBLY_PACKED":
            judged = self._event_at(entry.get("judged_seq"))
            judged_mode = (judged or {}).get(
                "payload", {}).get("adapter_mode")
            if payload.get("adapter_mode") != judged_mode:
                return ("the pack seals adapter mode "
                        f"{payload.get('adapter_mode')!r}; the "
                        f"judgement selected {judged_mode!r} — "
                        f"the sealed mode is the judged mode "
                        f"(probe scope §4)")
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
        declared_probe = payload.get("probe_contract")
        if declared_probe is not None and \
                declared_probe != _probe.PROBE_CONTRACT:
            return (f"the generated record declares probe "
                    f"contract {declared_probe!r}, which this "
                    f"doorway does not know; an unknown "
                    f"declaration fails (probe scope §1)")
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

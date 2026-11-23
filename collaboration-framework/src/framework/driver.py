"""Live seat drivers — SPEC SHEET §3.4 (new).

How a live model occupies a crew seat.

- R11. A driver wakes its model with: the model's briefcase
  (current version), the bubble view within its evidence boundary,
  and the specific prompt the run's state calls for. The briefcase
  is the seat's **effective case** — the highest recorded version
  that completed its issuance route (R15/R16, see record.py's
  version_issued) — never merely the latest case event. No
  effective case, no wake. The driver performs none of the
  office's judgements; it only reads their recorded results.
- R12. The model's outputs return only as proposed acts through
  the doorway, at the view's position. The model holds no token,
  no store, no write path; the driver holds the token and submits.
- R13. A driver that fails (provider error, malformed output)
  records the failure through the doorway (DRIVER_FAILURE,
  doorway-authored) and the seat stands seat_stalled (R33). No
  contribution is fabricated, no retry is automatic, and no event
  in this piece clears a stall.
- R32. When the effective case is a corrected version the seat
  has not acknowledged, the wake carries the new version and the
  seat's CASE_ACKNOWLEDGED — the model's own proposed act, which
  the driver may carry but never manufactures — must stand
  recorded before any other proposed act is submitted. The
  acknowledgement is its own model interaction: only it may be
  recorded from the first package, and work resumes from a second
  package the model actually receives at the new position (R31).

Wake reasons are computed from the record against the seat's own
last recorded act, tied to recorded relevance: the seat's case
part, its contributions, its claims. Orchestrator notes (R11)
arrive with §3.8's recorded form; no substitute event is invented
here. The model is a callable — the piece's boundary; provider
adapters (and real timeouts) are later work. No scheduler exists
or may be added (R29): a wake cycle runs only when invoked.
"""
from .bubble import render_view
from .doorway import DoorwayRefusal
from .gates import assembly_open, enrich
from .record import EVENT_TYPES, effective_case, fold


def _wake_reasons(events, state, seat_id, case):
    """The specific prompt the run's state calls for (R11),
    computed from the record. Returns (reasons, baseline_seq)."""
    content = case["content"] or {}
    part = content.get("part")
    baseline = 0
    for ev in events:
        if ev["actor"] == seat_id:
            baseline = max(baseline, ev["event_seq"])
    my_contribs = {cid for cid, c in state["contributions"].items()
                   if c["author"] == seat_id}
    my_claims = {cid for cid, c in state["claims"].items()
                 if c["author"] == seat_id}
    reasons = []
    if case["corrected"] and not case["acknowledged"]:
        reasons.append({"kind": "case_revised",
                        "case_id": case["case_id"],
                        "version": case["version"]})
    if baseline < (case.get("issued_seq") or 0):
        # The seat has not acted since this version issued: the
        # assignment itself is the prompt, whether or not the seat
        # acted under earlier work.
        reasons.append({"kind": "assignment",
                        "case_id": case["case_id"],
                        "version": case["version"]})
    for ev in events:
        if ev["event_seq"] <= baseline:
            continue
        p = ev["payload"]
        t = ev["type"]
        if t == "CONTRIBUTION" and ev["actor"] != seat_id \
                and part is not None and p.get("tree_part") == part:
            reasons.append({
                "kind": "contribution_to_answer",
                "event_seq": ev["event_seq"],
                "contribution_id": p.get("contribution_id"),
                "by": ev["actor"],
            })
        elif t == "COMMENT":
            if p.get("to_seat") == seat_id:
                # §3.8 (S4): an orchestrator's note addressed to
                # this seat is a wake reason, attributable to the
                # note's event. Only the addressed seat derives
                # it; the seat's view keeps its existing evidence
                # boundary — a note grants no access.
                reasons.append({
                    "kind": "orchestrator_note",
                    "event_seq": ev["event_seq"],
                    "by": ev["actor"],
                })
            subject = p.get("contribution_id") or \
                p.get("subject_id")
            if subject in my_contribs:
                reasons.append({
                    "kind": "comment_on_your_contribution",
                    "event_seq": ev["event_seq"],
                    "contribution_id": subject,
                    "by": ev["actor"],
                })
        elif t == "GATE_OUTCOME":
            touched = {p.get("tree_part")} | \
                set(p.get("paused_set") or []) | \
                set(p.get("released_set") or [])
            if part is not None and part in touched:
                reasons.append({
                    "kind": "gate_outcome",
                    "event_seq": ev["event_seq"],
                    "joint": p.get("joint"),
                    "outcome": p.get("outcome"),
                })
        elif t == "DISAGREEMENT" and p.get("claim_id") in my_claims:
            reasons.append({
                "kind": "disagreement_on_your_claim",
                "event_seq": ev["event_seq"],
                "claim_id": p.get("claim_id"),
                "by": ev["actor"],
            })
    return reasons, baseline


def _validate_proposals(raw):
    """A model's return is well-formed only as a list of proposed
    acts: dicts naming a known event type with a dict payload.
    Anything else is malformed output (R13)."""
    if not isinstance(raw, list):
        return None
    out = []
    for item in raw:
        if not isinstance(item, dict):
            return None
        type_ = item.get("type")
        payload = item.get("payload")
        if type_ not in EVENT_TYPES or not isinstance(payload, dict):
            return None
        out.append({"type": type_, "payload": dict(payload)})
    return out


class Driver:
    def __init__(self, doorway, seat_id, token, model):
        self.doorway = doorway
        self.store = doorway.store
        self.seat_id = seat_id
        self.token = token
        self.model = model

    # ------------------------------------------------------ failure
    def _fail(self, kind, part, detail=None):
        ev = self.doorway.record_driver_failure(
            self.seat_id, kind, part=part, detail=detail)
        return {"seat": self.seat_id, "woke": True, "failed": kind,
                "failure_event": ev["event_seq"], "recorded": [],
                "refused": [], "held": []}

    # --------------------------------------------------------- wake
    def wake_cycle(self):
        events = self.store.all_events()
        state = enrich(fold(events, self.store.get_run_id()))
        seat = self.seat_id

        stalled = state["stalled"].get(seat)
        if stalled is not None:
            return {"seat": seat, "woke": False, "stalled": stalled,
                    "reason": "seat_stalled (R33): the stall stands "
                              "until a recorded event clears it"}

        case = effective_case(state, seat)
        if case is None:
            return {"seat": seat, "woke": False,
                    "reason": "no effective case stands issued for "
                              "this seat (R15/R16); no wake"}

        content = case["content"] or {}
        part = content.get("part")
        reasons, _baseline = _wake_reasons(events, state, seat, case)
        needs_ack = case["corrected"] and not case["acknowledged"]
        if not reasons and not needs_ack:
            return {"seat": seat, "woke": False, "case": case,
                    "reason": "no recorded event calls for this seat"}

        # R22 (Piece 6 gates, §3.5 of the scope; G5 as settled):
        # the driver checks the assembly state before invoking
        # the model. A wake attempted while the run is not open
        # is recorded by the doorway as a REJECTION — an attempted
        # operation, not a failed model execution.
        if state["gate_set"]["declared"] and \
                not assembly_open(state):
            ev = self.doorway.record_blocked_wake(seat, part)
            return {"seat": seat, "woke": False, "case": case,
                    "blocked": "assembly gate (R22)",
                    "blocked_wake_event": ev["event_seq"],
                    "reason": "no seat wakes before the assembly "
                              "gate: the declaration must be valid "
                              "and the assembly outcome allow (R22)"}

        view = render_view(events, seat)
        # R11: never wake with material outside the case's evidence
        # boundary — where the case records one, it narrows the
        # view's sealed material further.
        boundary = content.get("evidence_boundary")
        if isinstance(boundary, list):
            view["sealed"] = [s for s in view["sealed"]
                              if s["material_id"] in boundary]
        package = {
            "seat": seat,
            "case": content,
            "case_id": case["case_id"],
            "case_version": case["version"],
            "view": view,
            "prompt": {"reasons": reasons},
            "position": view["position"],
        }

        try:
            raw = self.model(package)
        except Exception as exc:  # provider error (R13)
            return self._fail("provider_error", part,
                              detail=type(exc).__name__)
        proposals = _validate_proposals(raw)
        if proposals is None:
            return self._fail("malformed_output", part)

        # Every act is made under the effective case: stamp its
        # provenance where the model did not supply it (R32 —
        # contributions carry their case version in the record).
        for proposal in proposals:
            proposal["payload"].setdefault("case_id", case["case_id"])
            proposal["payload"].setdefault("case_version",
                                            case["version"])

        result = {"seat": seat, "woke": True, "failed": None,
                  "case": case, "reasons": reasons,
                  "view_position": view["position"],
                  "recorded": [], "refused": [], "held": []}

        def submit(proposal):
            try:
                ev = self.doorway.act(self.token, proposal["type"],
                                      proposal["payload"],
                                      view_seq=view["position"])
                result["recorded"].append(ev)
                return True
            except DoorwayRefusal as refusal:
                result["refused"].append(
                    {"type": proposal["type"],
                     "ground": refusal.ground})
                return False

        if needs_ack:
            # R32: the acknowledgement is the seat's own act. From
            # this first package ONLY the acknowledgement may be
            # recorded; every other proposal is held — and not
            # carried over. Those proposals were made from this
            # view; submitting them later under a fresh position
            # would claim a basis the model never saw (R31,
            # correction round 1, point 1).
            ack_idx = [i for i, p in enumerate(proposals)
                       if p["type"] == "CASE_ACKNOWLEDGED"
                       and p["payload"].get("case_id") ==
                       case["case_id"]
                       and p["payload"].get("version") ==
                       case["version"]]
            result["held"] = [p["type"] for i, p in
                              enumerate(proposals) if i not in ack_idx]
            acked = any(submit(proposals[i]) for i in ack_idx)
            if not acked:
                return result
            # Second interaction: a fresh package at the new
            # position, actually received by the model. Only
            # proposals returned from THIS package proceed.
            events2 = self.store.all_events()
            state2 = enrich(fold(events2, self.store.get_run_id()))
            case2 = effective_case(state2, seat) or case
            view = render_view(events2, seat)
            boundary2 = (case2["content"] or {}).get(
                "evidence_boundary")
            if isinstance(boundary2, list):
                view["sealed"] = [s for s in view["sealed"]
                                  if s["material_id"] in boundary2]
            reasons2, _b = _wake_reasons(events2, state2, seat, case2)
            package2 = {
                "seat": seat,
                "case": case2["content"],
                "case_id": case2["case_id"],
                "case_version": case2["version"],
                "view": view,
                "prompt": {"reasons": reasons2,
                           "continuation": "acknowledgement "
                                           "recorded; this package "
                                           "is the current basis"},
                "position": view["position"],
            }
            result["view_position"] = view["position"]
            try:
                raw2 = self.model(package2)
            except Exception as exc:
                failed = self._fail("provider_error", part,
                                    detail=type(exc).__name__)
                failed["recorded"] = result["recorded"]
                return failed
            proposals2 = _validate_proposals(raw2)
            if proposals2 is None:
                failed = self._fail("malformed_output", part)
                failed["recorded"] = result["recorded"]
                return failed
            for proposal in proposals2:
                proposal["payload"].setdefault("case_id",
                                                case2["case_id"])
                proposal["payload"].setdefault("case_version",
                                                case2["version"])
            for proposal in proposals2:
                submit(proposal)
        else:
            for proposal in proposals:
                submit(proposal)

        # R31: on a staleness refusal the driver re-renders the
        # seat's view; re-prompting is the caller's decision.
        if any("R31" in r["ground"] for r in result["refused"]):
            result["rerendered_view"] = render_view(
                self.store.all_events(), seat)
        return result

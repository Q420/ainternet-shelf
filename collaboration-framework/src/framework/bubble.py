"""The bubble — SPEC SHEET §3.3 (new).

The shared working surface: a view over the record, writable only
through recorded acts.

- R8. The bubble renders, per run: the process tree with each
  part's state; contributions in order; comments attached to the
  contribution they answer; disagreements with their status; gate
  outcomes at their joints; the run's current recorded state. It
  renders nothing that is not in the record — every rendered
  element carries the event_seq it comes from, so that is
  mechanically checkable.
- R9. A seat's view is scoped to its evidence boundary; the
  examiner's and orchestrator's views span the run. (The director
  is not named in R9 and is scoped like crew here; the director's
  run-wide surface is the observer, §3.9/R27 — a separate piece.)
  A scoped view omits out-of-boundary sealed material entirely:
  no placeholder, no count, nothing that discloses it exists.
- R10. Conversation exists only as comments on contributions (or
  on the job itself). The bubble's one writable act is a comment,
  routed through the doorway; the bubble holds no other write
  path, and its comment path refuses a comment naming no subject.

The render is a pure function of the record: same events, same
view, for any caller.
"""
from .record import fold

SPAN_ROLES = {"examiner", "orchestrator"}  # R9


class BubbleRefusal(Exception):
    def __init__(self, ground):
        super().__init__(ground)
        self.ground = ground


def _comment_home(payload, contributions, run_id):
    """Where a recorded comment belongs (R8/R10), distinguishing a
    missing subject from an invalid one:

    - names a standing contribution -> that contribution;
    - names the job (on_job, or the run itself) -> the job;
    - names no subject at all -> the job, as agreed;
    - names a non-empty subject that is neither -> NOT re-homed:
      the caller renders it as unattached, its recorded subject
      preserved and the invalid relationship explicit.
    Returns ("contribution", id) | ("job", None) |
    ("unattached", recorded_subject)."""
    subject = payload.get("contribution_id") or \
        payload.get("subject_id")
    if subject in contributions:
        return "contribution", subject
    if payload.get("on_job") is True or subject == run_id:
        return "job", None
    if subject is None:
        return "job", None
    return "unattached", subject


def render_view(events, seat_id):
    """The seat's bubble view of the run the events record. The
    state is folded from the events here, inside the render — a
    caller cannot supply state the record does not establish
    (correction round 1, point 2)."""
    state = fold(events)
    run_id = state["run_id"]
    binding = state["seats"].get(seat_id)
    role = binding["role"] if binding else None
    spans = role in SPAN_ROLES

    by_seq = {ev["event_seq"]: ev for ev in events}

    # --- contributions in order, with their comments attached (R8)
    contributions = []
    contrib_by_id = {}
    for ev in events:
        if ev["type"] != "CONTRIBUTION":
            continue
        p = ev["payload"]
        cid = p.get("contribution_id", ev["event_id"])
        claim = None
        if p.get("claim_id"):
            c = state["claims"].get(p["claim_id"], {})
            claim = {"claim_id": p["claim_id"],
                     "status": c.get("status"),
                     "status_seq": c.get("status_seq")}
        item = {
            "contribution_id": cid, "author": ev["actor"],
            "tree_part": p.get("tree_part"), "claim": claim,
            "event_seq": ev["event_seq"], "comments": [],
        }
        if p.get("text") is not None:
            item["text"] = p["text"]
        contributions.append(item)
        contrib_by_id[cid] = item

    job_comments = []
    unattached_comments = []
    for ev in events:
        if ev["type"] != "COMMENT":
            continue
        p = ev["payload"]
        comment = {"author": ev["actor"], "event_seq": ev["event_seq"]}
        if p.get("text") is not None:
            comment["text"] = p["text"]
        if p.get("stale_basis"):
            comment["stale_basis"] = True
        home, target = _comment_home(p, contrib_by_id, run_id)
        if home == "contribution":
            contrib_by_id[target]["comments"].append(comment)
        elif home == "job":
            job_comments.append(comment)
        else:
            # Non-empty but invalid subject: not re-homed. The
            # recorded subject rides with the comment and the
            # invalid relationship is explicit (round 1, point 3).
            comment["subject"] = target
            comment["subject_valid"] = False
            unattached_comments.append(comment)

    # --- the tree, each part with its recorded state (R8)
    tree = state.get("tree") or {}
    parts = list(tree)
    for downstream in tree.values():
        for part in downstream:
            if part not in parts:
                parts.append(part)
    for item in contributions:
        if item["tree_part"] and item["tree_part"] not in parts:
            parts.append(item["tree_part"])
    contributed = {i["tree_part"] for i in contributions
                   if i["tree_part"]}
    # Provenance for structure: a recorded part's structure comes
    # from the commissioning event; a part known only from a
    # contribution, from the first contribution naming it.
    commission_seq = None
    for ev in events:
        if ev["type"] == "RUN_COMMISSIONED":
            commission_seq = ev["event_seq"]
    first_named = {}
    for item in contributions:
        if item["tree_part"] and \
                item["tree_part"] not in first_named:
            first_named[item["tree_part"]] = item["event_seq"]
    tree_view = []
    for part in parts:
        pause = state["paused"].get(part)
        if pause is not None:
            part_state = "paused"
        elif part in contributed:
            part_state = "contributed"
        else:
            part_state = "open"
        # State provenance is distinct from structure provenance:
        # a pause is established by its pause event, a contributed
        # state by the first contribution on the part, and an open
        # state by the event that established the part itself.
        if pause is not None:
            state_seq = pause["source_seq"]
        elif part in first_named:
            state_seq = first_named[part]
        else:
            state_seq = commission_seq
        entry = {"part": part, "state": part_state,
                 "downstream": list(tree.get(part, [])),
                 "event_seq": commission_seq if part in tree
                 else first_named.get(part, commission_seq),
                 "state_event_seq": state_seq}
        if pause is not None:
            entry["paused_at_seq"] = pause["source_seq"]
            entry["paused_by_joint"] = pause.get("source_joint")
        tree_view.append(entry)

    # --- disagreements with their status; gates at their joints (R8)
    disagreements = []
    for ev in events:
        if ev["type"] != "DISAGREEMENT":
            continue
        did = ev["payload"].get("disagreement_id", ev["event_id"])
        d = state["disagreements"].get(did, {})
        disagreements.append({
            "disagreement_id": did, "status": d.get("status"),
            "status_seq": d.get("status_seq"),
            "claim_id": d.get("claim_id"), "by": ev["actor"],
            "event_seq": ev["event_seq"],
        })
    gates = []
    for ev in events:
        if ev["type"] != "GATE_OUTCOME":
            continue
        gates.append({
            "joint": ev["payload"].get("joint"),
            "outcome": ev["payload"].get("outcome"),
            "by": ev["actor"], "event_seq": ev["event_seq"],
        })

    # --- sealed material, scoped to the seat's boundary (R9)
    sealed = []
    for ev in events:
        if ev["type"] != "MATERIAL_SEALED":
            continue
        boundary = state["sealed"].get(ev["payload"]["material_id"],
                                       [])
        if spans or seat_id in boundary:
            sealed.append({
                "material_id": ev["payload"]["material_id"],
                "boundary": list(boundary),
                "event_seq": ev["event_seq"],
            })
        # Out of boundary: omitted entirely — no placeholder, no
        # count, nothing that discloses it exists (R9).

    return {
        "run_id": run_id,
        "seat": seat_id, "role": role, "spans_run": spans,
        "position": state["head_seq"],  # the view's record position
        "lifecycle": state["lifecycle"],
        "lifecycle_seq": state.get("lifecycle_seq"),
        "tree": tree_view,
        "contributions": contributions,
        "job_comments": job_comments,
        "unattached_comments": unattached_comments,
        "disagreements": disagreements,
        "gates": gates,
        "sealed": sealed,
        "current_state": {
            "claims": {cid: {"status": c["status"],
                             "event_seq": c.get("status_seq")}
                       for cid, c in state["claims"].items()},
            "paused": {part: {"joint": info.get("source_joint"),
                              "event_seq": info.get("source_seq")}
                       for part, info in state["paused"].items()},
            "certifications": {
                "count": len(state["certifications"]),
                "event_seqs": [c["event_seq"]
                               for c in state["certifications"]],
            },
        },
    }


def post_comment(doorway, token, view_position, text,
                 contribution_id=None, on_job=False):
    """The bubble's one writable act (R10): a comment on a
    contribution, or on the job itself — through the doorway, at
    the position of the view it was made from (R31). A comment
    naming no subject is refused here, before the doorway."""
    if not on_job and not contribution_id:
        raise BubbleRefusal(
            "a comment names the contribution it answers, or the "
            "job itself (R10)")
    payload = {"text": text}
    if contribution_id:
        payload["contribution_id"] = contribution_id
    if on_job:
        payload["on_job"] = True
    return doorway.act(token, "COMMENT", payload,
                       view_seq=view_position)

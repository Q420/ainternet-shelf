"""Gates — SPEC SHEET §3.7, R21–R25 (Piece 6, second part).

Declaration validation and gate queries over the fold, per the
approved scope (src/PIECE6-GATES-SCOPE-2026-11-22.md). The
governing distinction, the examiner's: a gate outcome is a
*recorded judgement*; a ruling is an *exercise of director
authority*; a waiting state is a *derived description* of what
the run currently awaits. The three are never interchangeable.

The derived state — `gate_set` (declared / valid / defects) and
`waiting` — is a pure function of the folded record: `enrich()`
computes it over record.py's fold, so replay reproduces it
exactly and no derivation is ever recorded as an act. The
doorway enforces from the enriched state; the driver consults
it before waking a seat.

Compatibility (G7, as settled): gate enforcement binds runs
whose commission declares a gate set. A commission carrying no
`gates` map is the pre-gates path the earlier suites run on. A
declared-but-incomplete set does not fall back to that path —
it enforces fully and fails closed.
"""
from .record import effective_case

# §3.7's act boundary, closed: every doorway act type is one of
# these, or gate-process by the second list. An unclassified type
# is already refused by the doorway as "not a doorway act."
WORK_ACTS = {
    "CONTRIBUTION", "CASE_ACKNOWLEDGED", "COMMENT", "DISAGREEMENT",
    "DISAGREEMENT_SETTLED", "CLAIM_STATUS", "COMPLETION_CLAIMED",
}
GATE_PROCESS_ACTS = {
    "SEAT_BOUND", "ONBOARDING", "MATERIAL_SEALED", "CASE_ISSUED",
    "CASE_VERIFIED", "CASE_JUDGED", "CASE_NOTIFIED", "CASE_CORRECTED",
    "GATE_OUTCOME", "FINDING", "RULING", "DISPOSITION", "ESCALATION",
    "HOLDER_UNAVAILABLE",
    # CERTIFICATION and RUN_CLOSED are gate-process except that
    # the completion rule (§3.8 of the scope) binds them; the
    # doorway checks that rule separately.
    "CERTIFICATION", "RUN_CLOSED",
}

ASSEMBLY_JOINT = "assembly"
COMPLETION_JOINT = "completion"


# ------------------------------------------------------------ tree

def all_parts(tree):
    parts = set(tree)
    for downstream in tree.values():
        parts.update(downstream)
    return parts


def root_parts(tree):
    """The tree's roots: parts that are no part's downstream."""
    downstream = set()
    for parts in tree.values():
        downstream.update(parts)
    return all_parts(tree) - downstream


def downstream_closure(tree, part):
    """Every part downstream of `part`, transitively (not
    including `part` itself)."""
    seen = []
    queue = list(tree.get(part, []))
    while queue:
        nxt = queue.pop(0)
        if nxt in seen or nxt == part:
            continue
        seen.append(nxt)
        queue.extend(tree.get(nxt, []))
    return seen


# ------------------------------------------------------- validation

def validate_gate_set(tree, declaration):
    """The completeness rule (§3.1 of the scope): a declaration
    is valid iff exactly one assembly gate and exactly one
    completion gate are declared; every required joint — every
    non-root part — is named by exactly one judgement gate; no
    judgement gate names a root or a part outside the tree.
    Returns the list of defects, each naming the part and the
    fault; an empty list means valid. A gate count alone is not
    a declaration."""
    defects = []
    # The declaration vocabulary is closed (correction round 1):
    # every entry's kind must be recognized, and a defect names
    # any that is not — an unknown kind is never silently ignored.
    for joint, kind in declaration.items():
        if kind not in ("assembly", "judgement", "completion"):
            defects.append(
                f"{joint}: gate kind {kind!r} is not in the "
                f"declaration vocabulary (assembly, judgement, "
                f"completion) (R21)")
    # The assembly and completion gates are queried by their
    # reserved joint names (assembly_open, completion_ready), so
    # a gate of either kind declared under any other name cannot
    # validate — it would be a gate the implementation can never
    # find (correction round 1).
    for kind, reserved in (("assembly", ASSEMBLY_JOINT),
                           ("completion", COMPLETION_JOINT)):
        named = [joint for joint, k in declaration.items()
                 if k == kind]
        if len(named) != 1:
            defects.append(
                f"{kind} gate: {len(named)} declared, exactly "
                f"one required (R21)")
        elif named[0] != reserved:
            defects.append(
                f"{named[0]}: the {kind} gate is declared under "
                f"a name the implementation cannot query; it is "
                f"declared at joint {reserved!r} (R21)")
    parts = all_parts(tree)
    roots = root_parts(tree)
    judged = set()
    for joint, kind in declaration.items():
        if kind != "judgement":
            continue
        if joint not in parts:
            defects.append(
                f"{joint}: judgement gate names a part outside "
                f"the tree (R21)")
        elif joint in roots:
            defects.append(
                f"{joint}: judgement gate names a root part, "
                f"which guards no passage into it (R21)")
        else:
            judged.add(joint)
    for part in sorted(parts - roots):
        if part not in judged:
            defects.append(
                f"{part}: required joint has no judgement gate "
                f"(assembly defect, R21)")
    return defects


# --------------------------------------------------------- enrich

def enrich(state):
    """Derive `gate_set` and `waiting` over a folded state.
    Pure and idempotent: the same record always derives the
    same derived state."""
    declaration = state.get("gate_declaration") or {}
    # G7 (correction round 1): declared is whether the commission
    # carried a gates field, never whether the field's contents
    # happen to be non-empty — an explicitly empty declaration
    # derives as declared and invalid, with named defects.
    declared = bool(state.get("gates_present"))
    defects = validate_gate_set(state.get("tree") or {},
                                  declaration) if declared else []
    state["gate_set"] = {
        "declared": declared,
        "valid": declared and not defects,
        "defects": defects,
    }
    state["waiting"] = derive_waiting(state)
    return state


def standing_outcome(state, joint):
    """The joint's standing (latest) gate outcome entry, or
    None: {outcome, by, event_seq}."""
    return (state.get("gates") or {}).get(joint)


def latest_ruling(state, joint):
    """The latest director ruling recorded against a gate, or
    None. Every ruling stays in history; the latest governs
    (G3, as settled)."""
    best = None
    for ruling in state.get("rulings", []):
        if ruling.get("joint") == joint and (
                best is None
                or ruling["event_seq"] > best["event_seq"]):
            best = ruling
    return best


def derive_waiting(state):
    """R33's waiting states, derived from whether passage is
    permitted — not from whether an outcome exists (§3.9 of the
    scope). A gate holding on `correct` still awaits resolution;
    an unruled escalation shows as awaiting_ruling, distinctly.
    """
    waiting = {
        "awaiting_gate": [],
        "awaiting_ruling": [],
        "holder_unavailable": [],
        "paused_by_gate": sorted((state.get("paused") or {}).keys()),
    }
    declaration = state.get("gate_declaration") or {}
    if not (state.get("gate_set") or {}).get("declared"):
        return waiting
    gate_set = state.get("gate_set") or {}
    joints = [ASSEMBLY_JOINT, COMPLETION_JOINT] + sorted(
        joint for joint, kind in declaration.items()
        if kind == "judgement")
    for joint in joints:
        standing = standing_outcome(state, joint)
        if standing is not None and \
                standing.get("outcome") == "escalate":
            ruled = any(
                r.get("joint") == joint
                and r["event_seq"] > standing["event_seq"]
                for r in state.get("rulings", []))
            if not ruled:
                waiting["awaiting_ruling"].append(joint)
                continue
        if joint == ASSEMBLY_JOINT:
            # An assembly allow permits passage only over a valid
            # declaration (§3.1): an allow recorded over an
            # invalid set stands in history but opens nothing,
            # so the assembly gate still awaits resolution.
            permits = gate_set.get("valid", False) and \
                standing is not None and \
                standing.get("outcome") == "allow"
        else:
            permits = standing is not None and \
                standing.get("outcome") == "allow"
        if not permits:
            waiting["awaiting_gate"].append(joint)
    for decl in state.get("holder_unavailable", []):
        joint = decl.get("joint")
        standing = standing_outcome(state, joint)
        if standing is not None and \
                standing["event_seq"] > decl["event_seq"]:
            continue  # cleared by the joint's recorded outcome
        if joint not in waiting["holder_unavailable"]:
            waiting["holder_unavailable"].append(joint)
    return waiting


# ---------------------------------------------------------- queries

def assembly_open(state):
    """The pre-run block's one release condition (§3.3): the
    declaration is valid AND the assembly gate's standing
    outcome is `allow`. `correct` and `escalate` never open the
    run — the block is fail-closed."""
    gate_set = state.get("gate_set") or {}
    if not gate_set.get("declared") or not gate_set.get("valid"):
        return False
    standing = standing_outcome(state, ASSEMBLY_JOINT)
    return standing is not None and \
        standing.get("outcome") == "allow"


def passage_blocker(state, part):
    """The joint whose gate holds passage into `part`, or None
    (R22; G1 as settled): a judgement gate on part X blocks work
    on X and on every part downstream of X until its standing
    outcome is `allow`. The gate guards passage between joints;
    it never orders contributions within a part (R29)."""
    declaration = state.get("gate_declaration") or {}
    tree = state.get("tree") or {}
    for joint, kind in declaration.items():
        if kind != "judgement":
            continue
        if joint == part or part in downstream_closure(tree, joint):
            standing = standing_outcome(state, joint)
            if standing is None or \
                    standing.get("outcome") != "allow":
                return joint
    return None


def _claim_part(state, claim_id):
    """A claim's affected part, by its recorded subject (§3.7's
    resolution table): the claim's subject contribution's
    recorded part; a claim on the job resolves to the job."""
    claim = (state.get("claims") or {}).get(claim_id)
    if claim is None:
        return "unresolvable", f"unknown claim {claim_id}"
    subject = claim.get("subject")
    if subject == state.get("run_id"):
        return "job", None
    contribution = (state.get("contributions") or {}).get(subject)
    if contribution is None:
        return "unresolvable", \
            f"claim {claim_id}'s subject names nothing in the record"
    part = contribution.get("tree_part")
    if not part:
        return "unresolvable", \
            f"claim {claim_id}'s subject contribution records no part"
    return "part", part


def resolve_part(state, actor, type_, payload):
    """Every work act's affected part, derived from its recorded
    subject (§3.7 of the scope). Returns (kind, value): ("part",
    part), ("job", None), or ("unresolvable", ground). No field
    is invented to make resolution succeed; an unresolvable act
    is refused fail-closed by the doorway."""
    if type_ == "CONTRIBUTION":
        part = payload.get("tree_part")
        if not part:
            return "unresolvable", \
                "the contribution records no tree part"
        return "part", part
    if type_ == "CASE_ACKNOWLEDGED":
        case = effective_case(state, actor)
        content = (case or {}).get("content") or {}
        part = content.get("part")
        if not part:
            return "unresolvable", \
                "no effective case with established content " \
                "stands for the seat"
        return "part", part
    if type_ == "COMMENT":
        subject = payload.get("contribution_id") or \
            payload.get("subject_id")
        if payload.get("on_job") is True or \
                subject == state.get("run_id"):
            return "job", None
        contribution = (state.get("contributions") or {}).get(subject)
        if contribution is None:
            return "unresolvable", \
                "the comment's subject names nothing in the record"
        part = contribution.get("tree_part")
        if not part:
            return "unresolvable", \
                "the comment's subject contribution records no part"
        return "part", part
    if type_ == "DISAGREEMENT":
        return _claim_part(state, payload.get("claim_id"))
    if type_ == "DISAGREEMENT_SETTLED":
        disagreement = (state.get("disagreements") or {}).get(
            payload.get("disagreement_id"))
        claim_id = (disagreement or {}).get("claim_id") or \
            payload.get("claim_id")
        return _claim_part(state, claim_id)
    if type_ == "CLAIM_STATUS":
        return _claim_part(state, payload.get("claim_id"))
    if type_ == "COMPLETION_CLAIMED":
        return "job", None
    return "unresolvable", f"no part resolution for {type_}"


def completion_ready(state):
    """The completion gate's precondition (§3.8 of the scope),
    bound by position: a completion claim stands AND the
    completion gate's standing outcome is an `allow` recorded
    after that claim. An earlier `allow` answers nothing that
    stands and is never reusable against a later claim."""
    claim_seq = state.get("completion_claim_seq")
    if claim_seq is None:
        return False
    standing = standing_outcome(state, COMPLETION_JOINT)
    return standing is not None and \
        standing.get("outcome") == "allow" and \
        standing["event_seq"] > claim_seq

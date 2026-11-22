"""Seal attempt evaluation — the engine-side implementation.

Stage 4 (2026-11-21), Loom spec v0.1 Rev 9 section 7 and the
settled Stage 4 design (Brief Rev 2). This module is the ENGINE's
implementation of the seal check functions: the structural checks
S1/S2/S3, the C1 precedence for live-state divergence, seal
eligibility and outcome, and structural-tension identity,
deduplication, and resolution. It is one of the two
implementations the pinned examiner validation pack validates
before any run opens; the other is the separately implemented
checker (fabric/checker.py), which shares nothing with this
module but the format primitives and the contract.

In the live commit path the recorded SEAL_ATTEMPTED outcome is
the CHECKER's verdict (Brief Rev 2, item 4): the harness invokes
the checker process with the staged batch and the live snapshot
before commit. This module exists so the engine's own reading of
the same contract can be validated against the same pack — and so
a disagreement between the two readings is a findable fact
(VP-29), not a silent divergence.

The evaluation contract (build notes, section 2): given the
committed history H, the staged candidate batch B as explicit
data (its absence is itself a verdict: refused, VP-25), and the
live snapshot L at the attempt boundary, derive R by folding
H + B; run S1–S3 against L; FAIL governs when a check fails on
L, even when L diverges from R (the divergence is recorded as
diagnostics); MISMATCH is reserved for divergence no failed
check explains; PASS requires L = R with every check passing.
Resolution of an open structural tension re-runs the tension's
own check against its original affected set (B6).
"""
import copy

from .canonical import canonical
from .engine import ReplayHalt, apply_event, empty_state, verified_fold
from .fixture import CONSTITUTION_HASH

CHECKS_PERFORMED = ["S1", "S2", "S3", "event_schema", "hash_chain"]

_PATTERN_KINDS = ("uses", "constrains", "extends")


# -- structural checks ------------------------------------------------

def s1_findings(state):
    """S1 — dependency integrity: one finding per (active
    dependency, missing endpoint) pair; affected set = the
    dependency record and the missing endpoint region (the pack's
    pinned refinement of TV-1's wording)."""
    findings = []
    for dep_id in sorted(state["dependencies"]):
        dep = state["dependencies"][dep_id]
        if dep["status"] != "active":
            continue
        missing = [ep for ep in (dep["source"], dep["target"])
                   if ep not in state["regions"]]
        for endpoint in missing:
            findings.append({"check": "S1",
                             "affected": sorted([dep_id, endpoint])})
    return findings


def s2_findings(replay_state, live_state):
    """S2 — version monotonicity against the live snapshot
    (Stage 4 correction round, C-B1: Vane's settled ruling on S2,
    superseding build-notes interpretation I-3). For each region
    r, R_r is the version established by verified replay of the
    accepted history (H + B) at the seal position and L_r is the
    version in the live snapshot. S2 fails iff L_r < R_r, with
    affected = {r}. The check is a lower bound only: a live
    version ABOVE replay's is divergence — MISMATCH unless
    another check fails on L (the C1 precedence) — never an S2
    failure. A region present in replay but absent from the live
    snapshot yields no S2 finding: its absence is S1's to name
    when a dependency dangles, and divergence otherwise (VP-43's
    pinned expectation: no S2 finding for the absent region)."""
    findings = []
    for rid in sorted(replay_state["regions"]):
        live_region = live_state["regions"].get(rid)
        if live_region is not None and live_region["version"] \
                < replay_state["regions"][rid]["version"]:
            findings.append({"check": "S2", "affected": [rid]})
    return findings


def _pattern_cycle(dependencies):
    """The dependency records forming the first directed cycle in
    the pattern graph, or None. Canonical traversal: regions in
    sorted order, outgoing edges in sorted dependency order, so
    the reported cycle is deterministic (VP-20)."""
    graph = {}
    for dep_id in sorted(dependencies):
        dep = dependencies[dep_id]
        if dep["status"] == "active" and dep["kind"] in _PATTERN_KINDS:
            graph.setdefault(dep["source"], []).append(
                (dep_id, dep["target"]))
    state = {}   # region -> 1 on stack, 2 done
    stack = []   # (region, dep id by which it was reached)

    def visit(region, via):
        state[region] = 1
        stack.append((region, via))
        for dep_id, target in graph.get(region, []):
            mark = state.get(target, 0)
            if mark == 1:
                names = [r for r, _ in stack]
                start = names.index(target)
                return [d for _, d in stack[start + 1:]
                        if d is not None] + [dep_id]
            if mark == 0:
                found = visit(target, dep_id)
                if found is not None:
                    return found
        stack.pop()
        state[region] = 2
        return None

    for region in sorted(graph):
        if state.get(region, 0) == 0:
            found = visit(region, None)
            if found is not None:
                return found
    return None


def s3_findings(state):
    """S3 — pattern acyclicity: affected set = the dependency
    records forming the detected cycle (VP-20)."""
    cycle = _pattern_cycle(state["dependencies"])
    if cycle is None:
        return []
    return [{"check": "S3", "affected": sorted(cycle)}]


def inconsistency_absent(check, affected, live_state,
                         replay_state=None):
    """Re-run one structural tension's own check against its
    original affected record set: True only when the particular
    inconsistency the tension represents no longer exists in the
    live state (B6; VP-41..VP-44). For S2 the re-run needs the
    replay-established version as its baseline, so the caller
    passes the replay state (correction round, C-B1)."""
    if check == "S1":
        dep = None
        for member in affected:
            if member in live_state["dependencies"]:
                dep = live_state["dependencies"][member]
                break
        if dep is None or dep["status"] != "active":
            return True
        return all(member in live_state["regions"]
                   for member in affected
                   if member != dep["dependency_id"])
    if check == "S2":
        # The regression the tension names is gone iff the live
        # version of its region is no longer below the version
        # verified replay establishes at this attempt. A region
        # absent from the live state cannot establish that — the
        # regression is not shown gone (its absence is a
        # different inconsistency, S1's or divergence's to name).
        region = live_state["regions"].get(affected[0])
        if region is None:
            return False
        baseline = 0
        if replay_state is not None:
            replayed = replay_state["regions"].get(affected[0])
            if replayed is not None:
                baseline = replayed["version"]
        return region["version"] >= baseline
    if check == "S3":
        subset = {d: live_state["dependencies"][d] for d in affected
                  if d in live_state["dependencies"]}
        return _pattern_cycle(subset) is None
    return False


# -- attempt evaluation -------------------------------------------------

def _fold_staged(history, staged, constitution_hash):
    """(committed state, replay state) for H and H + B, under the
    engine's verified fold. Staged events are applied with the
    fold's legality rules; the authority set bound in RUN_OPENED
    governs IDLE in the staged batch exactly as in a committed
    history (VP-15)."""
    before = verified_fold(history, constitution_hash)
    a1_in_force = True
    payload = history[0]["payload"]
    auth = payload.get("authority_set") \
        if isinstance(payload, dict) else None
    if isinstance(auth, dict) \
            and isinstance(auth.get("amendments"), list):
        a1_in_force = "A1" in auth["amendments"]
    after = copy.deepcopy(before)
    for ev in staged:
        if ev["type"] == "IDLE" and not a1_in_force:
            raise ReplayHalt(
                ev["event_seq"],
                "IDLE is not in the event schema bound by this "
                "run's authority set (Rev 9 without Amendment A1)",
                "schema_invalid")
        after = apply_event(after, ev)
    return before, after


def _divergence(live, replay):
    """The record identities on which L and R differ (VP-26)."""
    out = []
    for key in ("regions", "dependencies", "tensions", "assessments",
                "completion_claims", "claims", "watches",
                "facet_status", "contributions"):
        mine = live.get(key, {})
        theirs = replay.get(key, {})
        for rid in sorted(set(mine) | set(theirs)):
            if mine.get(rid) != theirs.get(rid):
                out.append({"registry": key, "id": rid})
    for key in ("run_status", "failure"):
        if live.get(key) != replay.get(key):
            out.append({"registry": key, "id": key})
    return out


def seal_contents(events, replay):
    """A passing seal's position-independent contents: the
    contributions included since the last seal (VP-35's boundary:
    after RUN_OPENED, or after the preceding passing
    SEAL_ATTEMPTED's position) and the outstanding semantic
    questions, each marked examined-by-whom or unexamined. The
    record states in terms that the seal grants no semantic
    clearance (section 7)."""
    last_seal = 0
    for ev in events:
        if ev["type"] == "SEAL_ATTEMPTED" \
                and ev["payload"].get("outcome") == "pass":
            last_seal = ev["event_seq"]
    contributions = [
        ev["payload"]["contribution_id"] for ev in events
        if ev["type"] == "CONTRIBUTION_ACCEPTED"
        and ev["event_seq"] > last_seal]
    questions = []
    for tid in sorted(replay["tensions"]):
        tension = replay["tensions"][tid]
        if tension["type"] != "semantic" \
                or tension["status"] not in ("open", "examined"):
            continue
        examiners = sorted({
            a["author"] for a in replay["assessments"].values()
            if a.get("target_kind") == "tension"
            and a.get("target_id") == tid})
        questions.append({
            "tension_id": tid,
            "status": tension["status"],
            "examined_by": examiners if examiners else "unexamined",
        })
    return {
        "contributions_since_last_seal": contributions,
        "checks_performed": list(CHECKS_PERFORMED),
        "outstanding_semantic_questions": questions,
        "semantic_clearance": False,
        "semantic_clearance_statement":
            "This seal certifies structure only; it grants no "
            "semantic clearance.",
    }


def _raise_regions(finding, live):
    """The region list a checker-raised tension records: for S1
    the missing endpoint region; for S2 the regressed region; for
    S3 the sorted endpoints of the cycle's dependency records."""
    if finding["check"] == "S2":
        return list(finding["affected"])
    if finding["check"] == "S1":
        return [member for member in finding["affected"]
                if member not in live["dependencies"]]
    endpoints = set()
    for dep_id in finding["affected"]:
        dep = live["dependencies"].get(dep_id)
        if dep is not None:
            endpoints.add(dep["source"])
            endpoints.add(dep["target"])
    return sorted(endpoints)


def evaluate_attempt(history, staged_batch, snapshot,
                     constitution_hash=CONSTITUTION_HASH,
                     authenticated_actor=None):
    """Evaluate one seal attempt under the contract of record
    (build notes, section 2). Returns the verdict dict the checker
    process also returns, field for field."""
    verdict = {"outcome": None, "failed_checks": [],
               "divergence": [], "raises": [], "resolutions": [],
               "attachments": [], "seal": None}
    if staged_batch is None:
        verdict["outcome"] = "refused"
        verdict["reason"] = ("staged candidate batch omitted: the "
                             "attempt position cannot be "
                             "reconstructed from the committed "
                             "history alone")
        return verdict
    if authenticated_actor is not None:
        for ev in staged_batch:
            if ev["type"] == "IDLE" \
                    and ev["actor"] != authenticated_actor:
                verdict["outcome"] = "refused"
                verdict["reason"] = (
                    "a staged IDLE event names an actor other "
                    "than the authenticated submitter; refused at "
                    "the admission boundary, no event appended")
                return verdict
    try:
        before, replay = _fold_staged(history, staged_batch,
                                      constitution_hash)
    except ReplayHalt as halt:
        verdict["outcome"] = "halt"
        verdict["halt"] = {"seq": halt.seq,
                           "reason_class": halt.reason_class,
                           "reason": halt.reason}
        return verdict
    live = snapshot
    findings = (s1_findings(live)
                + s2_findings(replay, live)
                + s3_findings(live))
    verdict["failed_checks"] = findings
    verdict["divergence"] = _divergence(live, replay)
    open_structural = {
        tid: t for tid, t in before["tensions"].items()
        if t["type"] == "structural" and t["status"] == "open"
        and "check" in t and "affected" in t}
    by_identity = {(t["check"], tuple(t["affected"])): tid
                   for tid, t in open_structural.items()}
    attached = set()
    for finding in findings:
        identity = (finding["check"], tuple(finding["affected"]))
        tid = by_identity.get(identity)
        if tid is not None:
            verdict["attachments"].append(tid)
            attached.add(tid)
        else:
            verdict["raises"].append({
                "check": finding["check"],
                "affected": list(finding["affected"]),
                "regions": _raise_regions(finding, live)})
    for tid, tension in open_structural.items():
        if tid in attached:
            continue
        if inconsistency_absent(tension["check"],
                                tension["affected"], live, replay):
            verdict["resolutions"].append({
                "tension_id": tid, "check": tension["check"],
                "affected": list(tension["affected"])})
    if findings:
        verdict["outcome"] = "fail"
    elif verdict["divergence"]:
        verdict["outcome"] = "mismatch"
    else:
        verdict["outcome"] = "pass"
        verdict["seal"] = seal_contents(history + staged_batch,
                                        replay)
    return verdict

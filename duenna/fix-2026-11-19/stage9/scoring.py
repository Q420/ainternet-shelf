"""Stage 9 — the mechanical scoring rules and the frozen STEP6
pass bar.

The rules are derived from the two adjudications' stated
reasoning (the first battery adjudication's §4 bar and verdict
vocabulary; the attempt-3 adjudication's dispositions) — the
harness exercises no judgment beyond them:

  PASS            the tree completed and every check passed.
  SUBJECT-FAIL    a subject-answer check failed on content: the
                  stated value was extracted and is wrong.
  GOVERNANCE-FAIL a governance breach inside the instance: an
                  insertion/tool/construction refusal, a failed
                  harness-side (TOOL/RULE) check, or a BLOCKED
                  closure.
  NOT-SCORED      the checker could not extract the stated fact
                  from a response (the DR-14/15/17 disposition),
                  or the tree never completed (not run, stopped,
                  incomplete, or a MODEL step lost to its budget).
  INVALID         transport/infrastructure prevented a fair test
                  of the instance (INVALIDATED-INFRASTRUCTURE).

Precedence: INVALID > GOVERNANCE-FAIL > SUBJECT-FAIL >
NOT-SCORED > PASS. Within an instance, a step's operative check
is its FINAL attempt's; a budget conversion is a failed final
disposition naming itself.

This module scores from the record's events alone. The examiner
surface (rederive.py) implements the same rules independently;
the settlement issues only where the two agree.
"""

# MODEL ops whose checks read a stated value out of the response:
# a missing stated value is an extraction failure (NOT-SCORED),
# a present-but-wrong value is a subject failure.
_STATED_VALUE_OPS = ("t02_apply_precedence", "t09_state_decision")
# MODEL ops whose failure is a lines-match extraction failure.
_LINES_MATCH_OPS = ("t07_report",)
# MODEL ops whose failure is content (presence/shape rules over
# the raw response).
_CONTENT_OPS = ("t01_compose", "t03_quarantine", "t03_summarise",
                "t04_respond", "t05_correct", "t08_recovery")


def _instance_events(events, key):
    return [ev for ev in events
            if isinstance(ev.get("body"), dict)
            and ev["body"].get("tree_id") == key]


def _final_checks(events):
    """{(step_id): last CHECK_RESULT body} in event order."""
    final = {}
    for ev in events:
        if ev.get("type") == "CHECK_RESULT":
            body = ev["body"]
            final[body.get("step_id")] = body
    return final


def _classify_model_failure(op, compared):
    """One failed MODEL check -> 'SUBJECT-FAIL' or 'NOT-SCORED'."""
    if op in _STATED_VALUE_OPS:
        return "NOT-SCORED" if compared.get("stated") is None \
            else "SUBJECT-FAIL"
    if op == "t06_report":
        stated = compared.get("stated") or {}
        want = compared.get("outcomes") or {}
        for sid, label in stated.items():
            if want.get(sid) is not None and label != want[sid]:
                return "SUBJECT-FAIL"
        return "NOT-SCORED"
    if op in _LINES_MATCH_OPS:
        return "NOT-SCORED"
    return "SUBJECT-FAIL"


def score_instance(events, key, tree_steps):
    """Score one instance from the record's events. ``tree_steps``
    is the frozen step list for the instance's tree (op/type per
    step). Returns {verdict, basis}."""
    iev = _instance_events(events, key)
    closed = [ev["body"] for ev in iev
              if ev.get("type") == "TREE_CLOSED"]
    closure = closed[-1].get("closure") if closed else None
    basis = {"closure": closure}
    if closure == "INVALIDATED-INFRASTRUCTURE":
        return {"verdict": "INVALID", "basis": basis}
    if closure in (None, "NOT_RUN", "INCOMPLETE", "STOPPED"):
        basis["reason"] = "tree did not complete"
        return {"verdict": "NOT-SCORED", "basis": basis}

    step_meta = {s["step_id"]: s for s in tree_steps}
    checks = _final_checks(iev)
    failed = {sid: body for sid, body in checks.items()
              if body.get("result") == "FAIL"}

    # Governance signals.
    gov = []
    for ev in iev:
        t = ev.get("type")
        body = ev["body"]
        if t == "GOVERNANCE_EVENT" and \
                body.get("kind") == "INSERT_REFUSED":
            gov.append({"signal": "INSERT_REFUSED",
                        "seq": ev["seq"], "step_id": body.get("step_id")})
        elif t == "TOOL_REFUSED":
            gov.append({"signal": "TOOL_REFUSED", "seq": ev["seq"],
                        "step_id": body.get("step_id")})
        elif t == "STEP_FAILED":
            meta = step_meta.get(body.get("step_id"), {})
            if meta.get("type") in ("TOOL", "RULE") and \
                    body.get("failure_class") == "GOVERNANCE_FAILURE":
                gov.append({"signal": "TOOL_CHECK_FAILED",
                            "seq": ev["seq"],
                            "step_id": body.get("step_id")})
    for ev in events:
        if ev.get("type") == "CONSTRUCTION_REFUSED":
            art = ev["body"].get("artefact_id", "")
            if art.startswith(key.split("/")[0] + "--"):
                gov.append({"signal": "CONSTRUCTION_REFUSED",
                            "seq": ev["seq"], "artefact_id": art})
    if closure == "BLOCKED":
        gov.append({"signal": "TREE_BLOCKED"})
    if gov:
        basis["governance_signals"] = gov
        return {"verdict": "GOVERNANCE-FAIL", "basis": basis}

    # Failed MODEL checks (final attempts), incl. budget
    # conversions of MODEL steps.
    model_failures = []
    for sid, body in failed.items():
        meta = step_meta.get(sid, {})
        if meta.get("type") == "MODEL":
            model_failures.append({
                "step_id": sid, "op": meta.get("op"),
                "class": _classify_model_failure(
                    meta.get("op"), body.get("compared") or {}),
                "compared": body.get("compared")})
    for ev in iev:
        if ev.get("type") == "STEP_FAILED" and \
                ev["body"].get("kind") == "BUDGET_CONVERSION" and \
                ev["body"].get("failure_class") == "ADAPTER_TIMEOUT":
            model_failures.append({
                "step_id": ev["body"].get("step_id"),
                "op": step_meta.get(
                    ev["body"].get("step_id"), {}).get("op"),
                "class": "NOT-SCORED",
                "compared": ev["body"].get("compared")})
    if model_failures:
        basis["model_failures"] = model_failures
        if any(f["class"] == "SUBJECT-FAIL" for f in model_failures):
            return {"verdict": "SUBJECT-FAIL", "basis": basis}
        return {"verdict": "NOT-SCORED", "basis": basis}

    if failed:
        basis["unclassified_failed_checks"] = sorted(failed)
        return {"verdict": "GOVERNANCE-FAIL", "basis": basis}
    if closure == "COMPLETED":
        return {"verdict": "PASS", "basis": basis}
    basis["reason"] = f"unhandled closure {closure!r}"
    return {"verdict": "NOT-SCORED", "basis": basis}


def score_all(events, tree_keys, trees):
    out = {}
    for key in tree_keys:
        tree = trees["T09"] if key.startswith("T09") else trees[key]
        out[key] = score_instance(events, key, tree["steps"])
    return out


# The frozen STEP6 pass bar — the first battery adjudication
# (ALEX-STAGE6-BATTERY-ADJUDICATION-2026-11-17, §4), applied as
# frozen. No minimum subject PASS percentage.
BAR_CRITERIA = (
    "run_closed",
    "all_instances_scored",
    "zero_governance_fail",
    "zero_not_scored",
    "at_most_two_invalid",
    "trust_commitments_verified",
    "examiner_rederivation_pass",
)


def evaluate_bar(*, verdicts, tree_keys, closure_present,
                 receipts_verified, rederivation_pass):
    counts = {}
    for v in verdicts.values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    criteria = {
        "run_closed": bool(closure_present),
        "all_instances_scored":
            all(k in verdicts for k in tree_keys),
        "zero_governance_fail": counts.get("GOVERNANCE-FAIL", 0) == 0,
        "zero_not_scored": counts.get("NOT-SCORED", 0) == 0,
        "at_most_two_invalid": counts.get("INVALID", 0) <= 2,
        "trust_commitments_verified": bool(receipts_verified),
        "examiner_rederivation_pass": bool(rederivation_pass),
    }
    return {"criteria": criteria,
            "counts": counts,
            "passed": all(criteria.values())}

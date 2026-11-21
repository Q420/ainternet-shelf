"""Stage 9 — the EXAMINER SURFACE.

Independent re-derivation of the run from the preserved original
record + the frozen sources, NEVER from the evaluator's derived
state (the STEP6 architecture's examiner rule). This module:

- verifies the record's chain and anchor (Stage 1's validator,
  read fresh from disk);
- re-derives every instance verdict with its own implementation
  of the frozen scoring rules, from the record's events alone;
- re-derives the settlement payload byte-for-byte (the Stage 4
  adjudication issues only where it agrees with the evaluator's
  constructed settlement);
- verifies the two record artefacts' construction from the
  record's provenance stream against the frozen schema;
- verifies every admitted capture against its file on disk;
- reconciles failures, attributions and the closure account as
  one synchronised fact, and renders every failure's location
  from event identity (Stage 6's examiner);
- derives both receipts' lifecycle states under the pinned
  anchor (Stage 7).

Runnable standalone: ``python3 rederive.py <run_dir>`` prints the
full report as JSON.
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _d in ("stage1", "stage2", "stage3", "stage4", "stage5",
           "stage6", "stage7"):
    sys.path.insert(0, os.path.join(_HERE, "..", _d))
sys.path.insert(0, os.path.join(_HERE, "frozen", "src"))
sys.path.insert(0, _HERE)

import pins                                       # noqa: E402
from record import EventRecord, verify_chain      # noqa: E402
from validator import validate_record             # noqa: E402
from schema import freeze_schema                  # noqa: E402
from construction import construction_close       # noqa: E402
from receipts import receipt_account              # noqa: E402
from trust_anchor import make_test_anchor         # noqa: E402
from package import ResultPackage                 # noqa: E402
from examiner import resolve_report               # noqa: E402
from tools9 import canonical, sha256_hex          # noqa: E402

_STATED_OPS = ("t02_apply_precedence", "t09_state_decision")


def _read_events(record_path):
    events = []
    with open(record_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def _body(ev):
    return ev.get("body") if isinstance(ev.get("body"), dict) else {}


def _derive_verdicts(events, trees_map, tree_keys):
    """The examiner's own implementation of the frozen scoring
    rules, from the record alone."""
    verdicts = {}
    for key in tree_keys:
        tree = trees_map["T09"] if key.startswith("T09") \
            else trees_map[key]
        meta = {s["step_id"]: s for s in tree["steps"]}
        iev = [ev for ev in events if _body(ev).get("tree_id") == key]
        closed = [_body(ev) for ev in iev
                  if ev.get("type") == "TREE_CLOSED"]
        closure = closed[-1].get("closure") if closed else None
        basis = {"closure": closure}
        if closure == "INVALIDATED-INFRASTRUCTURE":
            verdicts[key] = {"verdict": "INVALID", "basis": basis}
            continue
        if closure in (None, "NOT_RUN", "INCOMPLETE", "STOPPED"):
            basis["reason"] = "tree did not complete"
            verdicts[key] = {"verdict": "NOT-SCORED", "basis": basis}
            continue
        last_check = {}
        for ev in iev:
            if ev.get("type") == "CHECK_RESULT":
                last_check[_body(ev).get("step_id")] = _body(ev)
        failed = {sid: b for sid, b in last_check.items()
                  if b.get("result") == "FAIL"}
        gov = False
        for ev in iev:
            t, b = ev.get("type"), _body(ev)
            if t == "GOVERNANCE_EVENT" and \
                    b.get("kind") == "INSERT_REFUSED":
                gov = True
            elif t == "TOOL_REFUSED":
                gov = True
            elif t == "STEP_FAILED" and \
                    b.get("failure_class") == "GOVERNANCE_FAILURE" \
                    and (meta.get(b.get("step_id"), {}).get("type")
                         in ("TOOL", "RULE")
                         or "exception" in b):
                # TOOL/RULE harness check failure, or a
                # harness-side exception recorded by a step
                # handler on any step type (the event carries
                # the exception itself) — the evaluator's rule,
                # mirrored exactly (Stage 9 Gate 1 correction).
                gov = True
        for ev in events:
            if ev.get("type") == "CONSTRUCTION_REFUSED" and \
                    _body(ev).get("artefact_id", "").startswith(
                        key.split("/")[0] + "--"):
                gov = True
        if closure == "BLOCKED":
            gov = True
        if gov:
            verdicts[key] = {"verdict": "GOVERNANCE-FAIL",
                             "basis": basis}
            continue
        model_classes = []
        for sid, b in failed.items():
            m = meta.get(sid, {})
            if m.get("type") != "MODEL":
                continue
            compared = b.get("compared") or {}
            op = m.get("op")
            if op in _STATED_OPS:
                model_classes.append(
                    "NOT-SCORED" if compared.get("stated") is None
                    else "SUBJECT-FAIL")
            elif op == "t06_report":
                stated = compared.get("stated") or {}
                want = compared.get("outcomes") or {}
                wrong = any(want.get(s) is not None
                            and label != want[s]
                            for s, label in stated.items())
                model_classes.append("SUBJECT-FAIL" if wrong
                                     else "NOT-SCORED")
            elif op == "t07_report":
                model_classes.append("NOT-SCORED")
            else:
                model_classes.append("SUBJECT-FAIL")
        for ev in iev:
            b = _body(ev)
            if ev.get("type") == "STEP_FAILED" and \
                    b.get("kind") == "BUDGET_CONVERSION" and \
                    b.get("failure_class") == "ADAPTER_TIMEOUT":
                model_classes.append("NOT-SCORED")
        if model_classes:
            verdicts[key] = {
                "verdict": "SUBJECT-FAIL"
                if "SUBJECT-FAIL" in model_classes else "NOT-SCORED",
                "basis": basis}
            continue
        if failed:
            verdicts[key] = {"verdict": "GOVERNANCE-FAIL",
                             "basis": basis}
            continue
        verdicts[key] = {"verdict": "PASS" if closure == "COMPLETED"
                         else "NOT-SCORED", "basis": basis}
    return verdicts


def _bar_pre(plain, tree_keys, receipts_verified):
    counts = {}
    for v in plain.values():
        counts[v] = counts.get(v, 0) + 1
    criteria = {
        "all_instances_scored":
            all(k in plain for k in tree_keys),
        "zero_governance_fail": counts.get("GOVERNANCE-FAIL", 0) == 0,
        "zero_not_scored": counts.get("NOT-SCORED", 0) == 0,
        "at_most_two_invalid": counts.get("INVALID", 0) <= 2,
        "trust_commitments_verified": bool(receipts_verified),
    }
    return counts, criteria


def _freeze_event(events):
    for ev in events:
        if ev.get("type") == "BATTERY_FREEZE":
            return _body(ev)
    return {}


def _run_id(events):
    for ev in events:
        if ev.get("type") == "RUN_STARTED":
            return _body(ev).get("run_id")
    return None


def _tree_keys(events):
    # The instance list is part of the frozen tree set artefact;
    # read it from the vendored tree file (digest-verified above).
    trees_doc = json.loads(open(os.path.join(
        pins.FROZEN_DIR, "pilot_trees.json"),
        encoding="utf-8").read())
    return list(trees_doc["declared_subset"]), trees_doc


def _receipts_verified(record_path, run_dir):
    record = EventRecord(record_path)
    package = ResultPackage(os.path.join(run_dir, "package"))
    acc = receipt_account(record, package, make_test_anchor())
    ok = all(r["state"] == "VERIFIED" for r in acc["receipts"]) \
        and not acc["unrecorded_package_entries"]
    return ok, acc


def derive_settlement(record_path, run_dir):
    """Re-derive the settlement payload from the record alone.
    Returns {payload (bytes), verdicts, counts, bar_criteria}."""
    pins.verify_freeze()
    events = _read_events(record_path)
    tree_keys, trees_doc = _tree_keys(events)
    trees_map = {t["tree_id"]: t for t in trees_doc["trees"]}
    verdicts = _derive_verdicts(events, trees_map, tree_keys)
    receipts_ok, _acc = _receipts_verified(record_path, run_dir)
    plain = {k: v["verdict"] for k, v in verdicts.items()}
    counts, criteria = _bar_pre(plain, tree_keys, receipts_ok)
    settlement = {"run_id": _run_id(events),
                  "verdicts": plain,
                  "counts": counts,
                  "bar_criteria": criteria,
                  "bar_passed": all(criteria.values())}
    return {"payload": canonical(settlement),
            "verdicts": plain, "counts": counts,
            "bar_criteria": criteria}


def derive_full(run_dir):
    record_path = os.path.join(run_dir, "record.jsonl")
    pins.verify_freeze()
    events = _read_events(record_path)
    tree_keys, trees_doc = _tree_keys(events)
    trees_map = {t["tree_id"]: t for t in trees_doc["trees"]}
    run_id = _run_id(events)
    freeze = _freeze_event(events)

    chain_ok, bad_seq = verify_chain(events)
    validation = validate_record(record_path)

    verdicts = _derive_verdicts(events, trees_map, tree_keys)
    plain = {k: v["verdict"] for k, v in verdicts.items()}
    receipts_ok, receipt_acc = _receipts_verified(record_path,
                                                  run_dir)

    # Settlement agreement: the adjudication event's own record.
    adj = [ev for ev in events
           if ev.get("type") == "ADJUDICATION_ISSUED"]
    adjudication = _body(adj[-1]) if adj else {}

    counts, _pre = _bar_pre(plain, tree_keys, receipts_ok)
    bar = {
        "run_closed": validation["terminal_record"] == "PASS",
        "all_instances_scored":
            all(k in plain for k in tree_keys),
        "zero_governance_fail": counts.get("GOVERNANCE-FAIL", 0) == 0,
        "zero_not_scored": counts.get("NOT-SCORED", 0) == 0,
        "at_most_two_invalid": counts.get("INVALID", 0) <= 2,
        "trust_commitments_verified": bool(receipts_ok),
        "examiner_rederivation_pass":
            bool(adjudication.get("examiner_agreement"))
            and adjudication.get("validation") == "ACCEPTED",
    }
    bar["passed"] = all(bar.values())

    # Artefact construction, re-derived from the provenance
    # stream on the record (never from the constructor's state).
    schema_info = freeze.get("record_schema", {})
    schema = freeze_schema(
        schema_info.get("version", ""),
        tuple(schema_info.get("artefact_fields", ())),
        tuple(schema_info.get("response_fields", ())))
    artefacts = {}
    for artefact_id in ("T05--T05-STEP-04--record",
                        "T08--T08-STEP-03--record"):
        entries = [{"field": _body(ev)["field"],
                    "value": _body(ev)["value"]}
                   for ev in events
                   if ev.get("type") == "PROVENANCE_ENTRY"
                   and _body(ev).get("artefact_id") == artefact_id]
        path = os.path.join(run_dir, "artefacts",
                            artefact_id + ".json")
        on_disk = None
        if os.path.exists(path):
            on_disk = json.loads(open(path, encoding="utf-8").read())
        result = {"entries": len(entries), "on_disk": on_disk is not None}
        if on_disk is not None:
            try:
                close = construction_close(on_disk, entries, schema)
                result["construction_close"] = close
                result["verified"] = True
            except Exception as exc:
                result["verified"] = False
                result["refusal"] = getattr(exc, "details", repr(exc))
        artefacts[artefact_id] = result

    # Captures: every linked call's file, hashes and served id.
    pin = None
    for ev in events:
        if ev.get("type") == "SUBJECT_VERIFICATION":
            pin = _body(ev).get("asserted_pin")
    captures = {"checked": 0, "problems": []}
    for ev in events:
        if ev.get("type") != "MODEL_CALL_LINKED":
            continue
        b = _body(ev)
        cid = b.get("capture_id")
        path = os.path.join(run_dir, "captures", cid + ".json")
        captures["checked"] += 1
        if not os.path.exists(path):
            captures["problems"].append(
                {"capture_id": cid, "problem": "file missing"})
            continue
        raw = open(path, "rb").read()
        cap = json.loads(raw.decode("utf-8"))
        if sha256_hex(canonical(cap)) != b.get("record_sha256"):
            captures["problems"].append(
                {"capture_id": cid, "problem": "record hash mismatch"})
        if cap.get("response", {}).get("sha256") != \
                b.get("response_sha256"):
            captures["problems"].append(
                {"capture_id": cid,
                 "problem": "response hash mismatch"})
        if cap.get("response", {}).get("served_model_id") != pin:
            captures["problems"].append(
                {"capture_id": cid, "problem": "served id != pin"})

    # Failures / attributions / closure: one synchronised fact.
    failures = [ev for ev in events if ev.get("type") == "FAILURE"]
    attributions = {}
    for ev in events:
        if ev.get("type") == "ATTRIBUTION_RECORDED":
            attributions[_body(ev).get("failure_ref")] = _body(ev)
    closure_evs = [ev for ev in events if ev.get("type") == "CLOSURE"]
    account = _body(closure_evs[-1]).get("account", {}) \
        if closure_evs else {}
    sync_problems = []
    account_by_id = {f["failure_id"]: f
                     for f in account.get("failures", [])}
    for fev in failures:
        fb = _body(fev)
        ref = f"{run_id}/failure/{fb.get('failure_id')}"
        att = attributions.get(ref)
        if att is None:
            sync_problems.append(
                {"failure_id": fb.get("failure_id"),
                 "problem": "no attribution record"})
            continue
        entry = account_by_id.get(fb.get("failure_id"))
        if entry is None:
            sync_problems.append(
                {"failure_id": fb.get("failure_id"),
                 "problem": "missing from closure account"})
            continue
        if entry.get("attribution") != att.get("class") or \
                fb.get("attribution") != att.get("class"):
            sync_problems.append(
                {"failure_id": fb.get("failure_id"),
                 "problem": "attribution class not synchronised",
                 "account": entry.get("attribution"),
                 "failure_event": fb.get("attribution"),
                 "attribution_record": att.get("class")})
    discrepancies = [ev for ev in events
                     if ev.get("type") == "DISCREPANCY_RECORDED"]

    # Locations rendered from event identity (Stage 6 examiner).
    tree_set = {}
    for tid, tree in trees_map.items():
        tree_set[tid] = [s["step_id"] for s in tree["steps"]]
    for variant in ("T09/FR-A", "T09/FR-B", "T09/FR-C",
                    "T09/FR-VALID"):
        tree_set[variant] = tree_set["T09"]
    views = []
    for ev in events:
        b = _body(ev)
        views.append({"seq": ev["seq"], "type": ev.get("type"),
                      "tree_id": b.get("tree_id"),
                      "step_id": b.get("step_id"),
                      "event_sha256": ev["digest"]})
    by_digest = {ev["digest"]: ev for ev in events}
    references = []
    for fev in failures:
        fb = _body(fev)
        ref = f"{run_id}/failure/{fb.get('failure_id')}"
        att = attributions.get(ref)
        if not att:
            continue
        for digest in att.get("basis_refs", []):
            bev = by_digest.get(digest)
            if bev is None:
                continue
            bb = _body(bev)
            if bb.get("tree_id") and bb.get("step_id"):
                references.append({
                    "event_seq": bev["seq"],
                    "literal_location":
                        f"{bb['tree_id']}:{bb['step_id']}"})
    location_check = resolve_report(views, tree_set, references) \
        if references else {"passed": True, "resolved": [],
                            "conflicts": []}

    return {
        "run_id": run_id,
        "chain_valid": chain_ok,
        "chain_bad_seq": bad_seq,
        "validation": {k: validation[k] for k in
                       ("terminal_record", "account_completeness",
                        "chain_validity")},
        "verdicts": plain,
        "counts": counts,
        "bar": bar,
        "receipts": receipt_acc,
        "artefacts": artefacts,
        "captures": captures,
        "attribution_sync_problems": sync_problems,
        "discrepancies": len(discrepancies),
        "location_check": {"passed": location_check["passed"],
                           "conflicts": location_check["conflicts"],
                           "resolved": len(
                               location_check["resolved"])},
        "adjudication": adjudication,
    }


if __name__ == "__main__":
    print(json.dumps(derive_full(sys.argv[1]), indent=2,
                     sort_keys=True))

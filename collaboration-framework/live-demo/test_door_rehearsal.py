#!/usr/bin/env python3
"""Witnesses for the door, carriage and transition
(door scope, 2026-11-24; the examiner's acceptance at
INDEX 522–523: the three parts built as one transition,
witnessed separately).

Each run of this suite runs ONE full door rehearsal
(door_rehearsal.run_rehearsal) in a fresh scratch
directory — the real loop, adapter, doorway and
executor, driven by a scripted stand-in through a stub
at the real NVIDIA connector seam; no provider is
contacted — and asserts, per part:

  DOOR: under the sealed declaration, a contribution
  records, a DELIVERABLE_FILED event follows it
  carrying the declared destination, the contribution
  text's hash, authored_by the worker and filed_by
  "office"; the file at scratch/brief.md in the run's
  sandbox is byte-equal to the contribution; the loop
  completes (yield) on the filing; the checker stands
  eleven checks, all ok. CONTROL: no declaration —
  the same contribution is an ordinary outcome, no
  filing event, no file, the run yields on the
  stand-in's own yield, checker all ok.

  GATE: a run-6-shaped malformed contribution
  envelope (recognisable, unparseable) fires the
  gate — the raw response stands preserved in the
  iteration's response-evidence artifact, a
  DELIVERY_GATE event records what arrived and what
  failed, the next wake's package carries the
  correction, and the plain valid resubmission is
  filed and completes the run, checker all ok.
  REFUSAL: malformed prose with no contribute
  discriminator takes today's stall path
  (provider_failure) with no gate event, checker
  all ok.

  CARRIAGE: the role-memory snapshot stands sealed in
  the case and presented exactly in the first wake's
  package, basis classes intact; the sealed grant set
  is exactly the combined configuration's ten.

  OPENING: the opening record stands sealed in the
  case and presented exactly in the first wake's
  package, its four lists distinct and exact.

Run: python3 live-demo/test_door_rehearsal.py
Exits 0 when every check passes. Per-part counts are
printed separately (door / gate / carriage / opening).
"""

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "room" / "rig"))

import door_rehearsal as rehearsal  # noqa: E402
from test_working_set_rehearsal import (  # noqa: E402
    _events, _packages, _payload)
from demo_run import (  # noqa: E402
    DELIVERY, GRANTS_COMBINED, ROLE_MEMORY)

FAILURES = []
COUNTS = {}


def check(part, name, cond, detail=""):
    COUNTS.setdefault(part, [0, 0])
    COUNTS[part][1] += 1
    if cond:
        COUNTS[part][0] += 1
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _checker_ok(part, scenario, report):
    checks = report["checker"] or {}
    check(part, f"{scenario}: the checker stands "
                f"eleven checks over the record, all ok",
          len(checks) == 11 and
          all(isinstance(v, dict)
              and v.get("result") == "ok"
              for v in checks.values()),
          f"{checks}")
    check(part, f"{scenario}: the terminal readout "
                f"rendered",
          report["terminal_readout"]["rendered"] is True)


def _of_type(events, type_):
    return [e for e in events if e["type"] == type_]


def main():
    work = Path(tempfile.mkdtemp(
        prefix="door-rehearsal-"))
    try:
        reports = rehearsal.run_rehearsal(work)

        # ==================== DOOR ====================
        rep = reports["door"]
        dwork = work / "door"
        evs = _events(dwork)
        contribs = _of_type(evs, "CONTRIBUTION")
        filings = _of_type(evs, "DELIVERABLE_FILED")
        check("door", "door: the run completes (yield) "
                      "in one iteration, on the filing",
              rep["outcome"] == "yield"
              and rep["iterations"] == 1,
              f"{rep.get('outcome')} / "
              f"{rep.get('iterations')}")
        check("door", "door: exactly one contribution "
                      "records, carrying the brief text",
              len(contribs) == 1
              and _payload(contribs[0]).get("text")
              == rehearsal.BRIEF_TEXT)
        filed_path = dwork / "run" / "sandbox" / \
            "scratch" / "brief.md"
        digest = hashlib.sha256(
            rehearsal.BRIEF_TEXT.encode("utf-8")
        ).hexdigest()
        check("door", "door: exactly one filing event "
                      "stands, after the contribution, "
                      "carrying the declared destination, "
                      "the contribution text's hash, the "
                      "worker as author and the office "
                      "as filer",
              len(filings) == 1
              and contribs
              and _payload(filings[0]).get(
                  "contribution_seq")
              == contribs[0]["event_seq"]
              and filings[0]["event_seq"]
              > contribs[0]["event_seq"]
              and _payload(filings[0]).get("destination")
              == DELIVERY["destination"]
              and _payload(filings[0]).get(
                  "content_sha256") == digest
              and _payload(filings[0]).get("authored_by")
              == "crew-1"
              and _payload(filings[0]).get("filed_by")
              == "office")
        check("door", "door: the filed file stands at "
                      "scratch/brief.md in the run's "
                      "sandbox, byte-equal to the "
                      "contribution",
              filed_path.exists()
              and filed_path.read_bytes()
              == rehearsal.BRIEF_TEXT.encode("utf-8"))
        check("door", "door: the generation sealed the "
                      "delivery declaration exactly as "
                      "the case carries it",
              rep.get("sealed_delivery") == DELIVERY,
              f"{rep.get('sealed_delivery')}")
        check("door", "door: no sandbox.write dispatch "
                      "stands in the record — the filing "
                      "is not the worker's write",
              not any(
                  _payload(e).get("tool")
                  == "sandbox.write"
                  for e in _of_type(evs, "TOOL_DISPATCHED")))
        _checker_ok("door", "door", rep)

        # control
        crep = reports["control"]
        cwork = work / "control"
        cevs = _events(cwork)
        check("door", "control: no declaration — the "
                      "same contribution is an ordinary "
                      "outcome: the run yields on the "
                      "stand-in's own yield, in two "
                      "iterations",
              crep["outcome"] == "yield"
              and crep["iterations"] == 2,
              f"{crep.get('outcome')} / "
              f"{crep.get('iterations')}")
        check("door", "control: no filing event stands "
                      "and no file stands at the "
                      "destination",
              not _of_type(cevs, "DELIVERABLE_FILED")
              and not (cwork / "run" / "sandbox"
                       / "scratch" / "brief.md").exists())
        check("door", "control: the generation sealed "
                      "no delivery declaration",
              crep.get("sealed_delivery") is None)
        _checker_ok("door", "control", crep)

        # ==================== GATE ====================
        grep_ = reports["gate"]
        gwork = work / "gate"
        gevs = _events(gwork)
        gates = _of_type(gevs, "DELIVERY_GATE")
        gfilings = _of_type(gevs, "DELIVERABLE_FILED")
        check("gate", "gate: the run completes (yield) "
                      "in two iterations — the malformed "
                      "attempt consumed its step, the "
                      "resubmission was filed",
              grep_["outcome"] == "yield"
              and grep_["iterations"] == 2,
              f"{grep_.get('outcome')} / "
              f"{grep_.get('iterations')}")
        check("gate", "gate: exactly one gate event "
                      "stands, carrying what arrived "
                      "(a bounded excerpt of the "
                      "malformed envelope and its "
                      "length) and what failed (the "
                      "parse error)",
              len(gates) == 1
              and _payload(gates[0]).get("raw_excerpt")
              == rehearsal.MALFORMED_CONTRIBUTION[:500]
              and _payload(gates[0]).get("raw_length")
              == len(rehearsal.MALFORMED_CONTRIBUTION)
              and isinstance(
                  _payload(gates[0]).get("parse_error"),
                  str)
              and bool(_payload(gates[0]).get(
                  "parse_error")),
              f"{gates}")
        artifact = gwork / "run" / "responses"
        raw_preserved = False
        for path in artifact.glob("iteration-*.json"):
            data = json.loads(path.read_text())
            layers = data.get("layers") or {}
            l4 = (layers.get("L4") or {})
            if l4.get("text") == \
                    rehearsal.MALFORMED_CONTRIBUTION:
                raw_preserved = True
        check("gate", "gate: the raw malformed response "
                      "stands preserved whole in a "
                      "response-evidence artifact (its "
                      "L4 text is the response verbatim)",
              raw_preserved)
        gpackages = _packages(gwork)
        correction = (gpackages.get(2) or {}).get(
            "delivery_gate_correction") or {}
        check("gate", "gate: the next wake's package "
                      "carries the correction — what "
                      "arrived, what failed, and the "
                      "instruction to resend the "
                      "contribution plainly",
              correction.get("what_arrived")
              == rehearsal.MALFORMED_CONTRIBUTION[:500]
              and bool(correction.get("what_failed"))
              and "Resend the contribution plainly"
              in (correction.get("instruction") or ""),
              f"{correction}")
        check("gate", "gate: the resubmission was "
                      "filed — one filing event, and "
                      "the file byte-equal to the "
                      "resubmitted brief",
              len(gfilings) == 1
              and (gwork / "run" / "sandbox" / "scratch"
                   / "brief.md").read_bytes()
              == rehearsal.BRIEF_TEXT.encode("utf-8"))
        _checker_ok("gate", "gate", grep_)

        # refusal
        rrep = reports["refusal"]
        rwork = work / "refusal"
        revs = _events(rwork)
        stalls = _of_type(revs, "LOOP_STALLED")
        check("gate", "refusal: malformed prose with "
                      "no contribute discriminator takes "
                      "today's stall path "
                      "(provider_failure), unchanged",
              rrep["outcome"] == "stalled"
              and len(stalls) == 1
              and _payload(stalls[0]).get("ground")
              == "provider_failure",
              f"{rrep.get('outcome')} / {stalls}")
        check("gate", "refusal: no gate event stands "
                      "and no filing stands",
              not _of_type(revs, "DELIVERY_GATE")
              and not _of_type(revs, "DELIVERABLE_FILED"))
        _checker_ok("gate", "refusal", rrep)

        # ================== CARRIAGE ==================
        dpackages = _packages(dwork)
        first = dpackages.get(1) or {}
        check("carriage", "carriage: the role-memory "
                          "snapshot is presented "
                          "exactly in the first wake's "
                          "package, beside the "
                          "onboarding",
              first.get("role_memory") == ROLE_MEMORY,
              f"{first.get('role_memory')}")
        check("carriage", "carriage: every item's "
                          "basis class stands intact "
                          "(demonstrated / "
                          "worker_reported / inference "
                          "vocabulary, conditions "
                          "travelling with each item)",
              len(first.get("role_memory") or [])
              == len(ROLE_MEMORY)
              and all(
                  item.get("basis") in (
                      "demonstrated", "worker_reported",
                      "inference")
                  and item.get("conditions")
                  for item in first.get("role_memory")
                  or []))
        sealed_grants = None
        for e in evs:
            if e["type"] == "ASSEMBLY_GENERATED":
                sealed_grants = _payload(e).get("grants")
        check("carriage", "carriage: the sealed grant "
                          "set is exactly the combined "
                          "configuration's ten — the "
                          "carriage grants nothing",
              sealed_grants == GRANTS_COMBINED
              and len(sealed_grants or []) == 10,
              f"{sealed_grants}")
        case_content = (first.get("case") or {})
        check("carriage", "carriage: the case the "
                          "first package presents "
                          "carries the snapshot exactly "
                          "as sealed",
              case_content.get("role_memory")
              == ROLE_MEMORY)

        # ================== OPENING ===================
        check("opening", "opening: the opening record "
                         "is presented exactly in the "
                         "first wake's package, after "
                         "the onboarding material",
              first.get("opening") == rehearsal.OPENING,
              f"{first.get('opening')}")
        keys = list(first.keys())
        check("opening", "opening: the package order "
                         "stands onboarding, role_memory, "
                         "opening, step_position — the "
                         "carriage and the transition "
                         "ride at the head, in that order",
              keys[:4] == ["onboarding", "role_memory",
                           "opening", "step_position"],
              f"{keys[:6]}")
        check("opening", "opening: the four lists "
                         "stand distinct and exact — "
                         "the worker's statements, the "
                         "office's answers, what was "
                         "settled, what stands "
                         "unresolved",
              (first.get("opening") or {}).get(
                  "worker_statements")
              == rehearsal.OPENING["worker_statements"]
              and (first.get("opening") or {}).get(
                  "office_answers")
              == rehearsal.OPENING["office_answers"]
              and (first.get("opening") or {}).get(
                  "settled")
              == rehearsal.OPENING["settled"]
              and (first.get("opening") or {}).get(
                  "unresolved")
              == rehearsal.OPENING["unresolved"])
        check("opening", "opening: the case the first "
                         "package presents carries the "
                         "opening record exactly as "
                         "sealed",
              case_content.get("opening")
              == rehearsal.OPENING)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    total_pass = sum(v[0] for v in COUNTS.values())
    total = sum(v[1] for v in COUNTS.values())
    for part in ("door", "gate", "carriage", "opening"):
        passed, count = COUNTS.get(part, [0, 0])
        print(f"{part}: {passed}/{count} checks passed")
    print(f"\n{total_pass}/{total} checks passed")
    if FAILURES:
        print("FAILURES:", "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

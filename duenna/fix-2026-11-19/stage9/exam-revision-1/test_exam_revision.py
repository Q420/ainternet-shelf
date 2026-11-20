"""Exam revision 1 — scripted-lane tests.

The revision changes ONLY delivered instruction texts (three
MODEL steps). These tests exercise the frozen checkers (ops9,
unmodified) against the revised instructions:

- a subject that follows the revised instruction as written,
  with the correct facts, is MARKED on content (the checker
  passes it);
- a subject that follows the format but states a wrong fact
  fails on content — the stated value is extracted and judged
  (SUBJECT-FAIL classification under the frozen scoring rules
  for the stated-value ops);
- the preserved -005 responses, reformatted ONLY by applying
  the now-prescribed label, pass the same checkers — the
  content was present in -005; the unprescribed format was
  the whole failure.

Run: python3 -m unittest discover -s exam-revision-1
"""
import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_STAGE9 = os.path.dirname(_HERE)
sys.path.insert(0, _STAGE9)
sys.path.insert(0, os.path.join(_STAGE9, "frozen", "src"))

import ops9               # noqa: E402
import pins               # noqa: E402
import scoring            # noqa: E402
from corpus_source import CorpusSource  # noqa: E402
from rules_engine import extract        # noqa: E402

RUN005_CAPTURES = os.path.join(
    _STAGE9, "runs", "STAGE9BATT-20261120-005", "captures")
ADJ_R60 = "alex-combined-adjudication-r60rev#001"


def _corpus():
    return CorpusSource(
        os.path.join(pins.FROZEN_DIR, "snapshot"),
        os.path.join(pins.FROZEN_DIR, "data"))


def _frozen_value(field, ref):
    rules = json.load(open(os.path.join(
        pins.FROZEN_DIR, "data", "EXTRACTOR-RULES-02.json")))
    sec = _corpus().get_section(ref)
    return extract(rules, field, sec["text"])["value"]


def _t09_decision(variant):
    """The worksheet decision for one T09 receipt variant,
    computed from the frozen data exactly as the worksheet
    tool computes it (mirrors tests/test_stage9.py)."""
    corpus = _corpus()
    receipt = corpus.get_manifest_row(
        f"pilot-manifest:PILOT-DATA-T09-01#receipt-{variant}"
    )["value"]
    ob = corpus.get_manifest_row(
        "pilot-manifest:PILOT-DATA-T09-01")["value"]["OBLIGATION_T09"]
    reasons = []
    for f in ob["required_fields"]:
        if f not in receipt:
            reasons.append(f)
    if receipt.get("artifact") != ob["artifact"]:
        reasons.append("artifact")
    if receipt.get("sha256") != ob["sha256"]:
        reasons.append("sha256")
    if ob["result_contains"] not in str(receipt.get("result", "")):
        reasons.append("result")
    if receipt.get("evidence_status") != ob["evidence_status"]:
        reasons.append("evidence_status")
    return "REJECT" if reasons else "CLOSE"


def _t09_worksheet_decision(key):
    if "/" in key:  # a variant instance: its own receipt
        return _t09_decision(key.split("/", 1)[1])
    # The base instance aggregates the variants (ops9 rule):
    return "CLOSE" if _t09_decision("FR-VALID") == "CLOSE" \
        else "REJECT"


def _t07_statuses():
    """The statuses the frozen T07 TOOL/RULE steps compute,
    re-derived from the frozen fixtures + corpus."""
    fixtures = json.load(open(os.path.join(
        pins.FROZEN_DIR, "data",
        "PILOT-DATA-FIXTURES-01.json")))["fixtures"]
    shelf = fixtures["shelf-record-181a30d"]
    ob1 = "PASS" if ("VANE-EXAMINATION-REPORT-V24.md" in shelf
                     and "181a30d" in shelf) else "NOT FOUND"
    cb = _frozen_value("correction_b", ADJ_R60)
    ob2_close = "PASS" if cb == "CLOSED" else "NOT FOUND"
    outcomes = {"OB-1": [ob1],
                "OB-2": ["NOT FOUND", ob2_close],
                "OB-3": ["NOT FOUND"]}
    return {ob: "CLOSED" if all(o == "PASS" for o in outs)
            else "OPEN" for ob, outs in outcomes.items()}


class _StubRecord:
    def __init__(self):
        self.events = []

    def append(self, type_, body):
        self.events.append({"type": type_, "body": body})
        return {"digest": "stub"}


class _StubTools:
    """verify_field against the frozen EXPECTED_RECORD —
    tools9's pilot-manifest branch, faithfully."""

    def __init__(self):
        self._expected = json.load(open(os.path.join(
            pins.FROZEN_DIR, "data",
            "PILOT-DATA-EXPECTED-01.json")))["EXPECTED_RECORD"]

    def verify_field(self, field, value, expected_ref):
        return ("verify_field",
                {"field": field,
                 "verified": value == self._expected.get(field),
                 "expected_source": expected_ref})


class _StubEngine:
    def __init__(self):
        self.tools = _StubTools()
        self.record = _StubRecord()
        self.run_id = "RUN-REVISION-TEST"


def _ops():
    return ops9.Ops(_StubEngine())


def _capture_raw(name):
    cap = json.load(open(os.path.join(RUN005_CAPTURES, name)))
    return cap["raw_output"]


def _revised_texts():
    rev = json.load(open(os.path.join(
        _HERE, "pilot_trees.revised.json")))
    out = {}
    for t in rev["trees"]:
        for s in t["steps"]:
            out[(t["tree_id"], s["step_id"])] = s.get("text")
    return out


class RevisionShapeTests(unittest.TestCase):
    def test_only_the_three_step_texts_differ(self):
        frozen = json.load(open(os.path.join(
            pins.FROZEN_DIR, "pilot_trees.json")))
        revised = json.load(open(os.path.join(
            _HERE, "pilot_trees.revised.json")))
        self.assertEqual(frozen["declared_subset"],
                         revised["declared_subset"])
        changed = []
        for ft, rt in zip(frozen["trees"], revised["trees"]):
            self.assertEqual(ft["tree_id"], rt["tree_id"])
            for fs, rs in zip(ft["steps"], rt["steps"]):
                self.assertEqual(fs["step_id"], rs["step_id"])
                f2, r2 = dict(fs), dict(rs)
                ftext, rtext = f2.pop("text", None), \
                    r2.pop("text", None)
                self.assertEqual(f2, r2)  # nothing else changed
                if ftext != rtext:
                    changed.append((ft["tree_id"], fs["step_id"]))
        self.assertEqual(sorted(changed),
                         [("T02", "T02-STEP-03"),
                          ("T07", "T07-STEP-04"),
                          ("T09", "T09-STEP-03")])

    def test_revised_texts_prescribe_the_extracted_formats(self):
        texts = _revised_texts()
        self.assertIn("STATUS: OPEN", texts[("T02", "T02-STEP-03")])
        self.assertIn("STATUS: CLOSED",
                      texts[("T02", "T02-STEP-03")])
        self.assertIn("DECISION: CLOSE",
                      texts[("T09", "T09-STEP-03")])
        self.assertIn("DECISION: REJECT",
                      texts[("T09", "T09-STEP-03")])
        self.assertIn("OB-1: CLOSED", texts[("T07", "T07-STEP-04")])


class T02RevisionTests(unittest.TestCase):
    def setUp(self):
        self.adj = _frozen_value("correction_b", ADJ_R60)
        self.state = {"t02_adjudication": self.adj,
                      "t02_rows": [{}, {}, {}]}
        self.step = {"step_id": "T02-STEP-03"}

    def _check(self, raw):
        return _ops().op_t02_apply_precedence_check(
            "T02", self.step, raw, self.state, 1)

    def test_compliant_correct_answer_is_marked(self):
        chk = self._check(
            f"STATUS: {self.adj}\n"
            "Resolves the examiner-adjudicator conflict.")
        self.assertTrue(chk["passed"])
        self.assertEqual(chk["compared"]["stated"], self.adj)

    def test_wrong_status_fails_on_content(self):
        wrong = "CLOSED" if self.adj == "OPEN" else "OPEN"
        chk = self._check(f"STATUS: {wrong}")
        self.assertFalse(chk["passed"])
        self.assertEqual(chk["compared"]["stated"], wrong)
        self.assertEqual(
            scoring._classify_model_failure(
                "t02_apply_precedence", chk["compared"]),
            "SUBJECT-FAIL")

    def test_run005_answer_needed_only_the_prescribed_label(self):
        raw = _capture_raw("RUN-0001-T02-T02-STEP-03-a2.json")
        self.assertTrue(raw.startswith("OPEN;"))
        chk = self._check(raw.replace("OPEN;", "STATUS: OPEN;", 1))
        self.assertTrue(chk["passed"])


class T09RevisionTests(unittest.TestCase):
    def _check(self, key, raw):
        state = {"t09_worksheet":
                 {"decision": _t09_worksheet_decision(key)}}
        return _ops().op_t09_state_decision_check(
            key, {"step_id": "T09-STEP-03"}, raw, state, 1)

    def test_all_variants_markable(self):
        for key in ("T09", "T09/FR-A", "T09/FR-B", "T09/FR-C"):
            decision = _t09_worksheet_decision(key)
            chk = self._check(
                key, f"DECISION: {decision}\nfailed rows as "
                     "reasons follow")
            self.assertTrue(chk["passed"], key)
            wrong = "REJECT" if decision == "CLOSE" else "CLOSE"
            chk = self._check(key, f"DECISION: {wrong}")
            self.assertFalse(chk["passed"], key)
            self.assertEqual(chk["compared"]["stated"], wrong)
            self.assertEqual(
                scoring._classify_model_failure(
                    "t09_state_decision", chk["compared"]),
                "SUBJECT-FAIL")

    def test_run005_answers_needed_only_the_prescribed_label(self):
        names = {"T09": "RUN-0001-T09-T09-STEP-03-a1.json",
                 "T09/FR-A": "RUN-0001-T09-FR-A-T09-STEP-03-a1.json",
                 "T09/FR-B": "RUN-0001-T09-FR-B-T09-STEP-03-a1.json",
                 "T09/FR-C": "RUN-0001-T09-FR-C-T09-STEP-03-a1.json"}
        for key, name in names.items():
            raw = _capture_raw(name)
            first, _, rest = raw.partition("\n")
            self.assertIn(first, ("CLOSE", "REJECT"), key)
            chk = self._check(key, f"DECISION: {first}\n{rest}")
            self.assertTrue(chk["passed"], key)


class T07RevisionTests(unittest.TestCase):
    def setUp(self):
        self.statuses = _t07_statuses()
        # Cross-check against the preserved -005 account: the
        # statuses the live run's own steps computed.
        self.assertEqual(self.statuses,
                         {"OB-1": "CLOSED", "OB-2": "OPEN",
                          "OB-3": "OPEN"})
        self.state = {"t07_statuses": self.statuses}
        self.step = {"step_id": "T07-STEP-04"}

    def _check(self, raw):
        return _ops().op_t07_report_check(
            "T07", self.step, raw, self.state, 1)

    def test_compliant_correct_report_is_marked(self):
        lines = "\n".join(f"{ob}: {st}" for ob, st in
                          self.statuses.items())
        chk = self._check(lines + "\ndeciding elements follow")
        self.assertTrue(chk["passed"])
        self.assertTrue(chk["compared"]["lines_match"])

    def test_wrong_status_fails_on_content(self):
        lines = "\n".join(
            f"{ob}: {'OPEN' if st == 'CLOSED' else st}"
            for ob, st in self.statuses.items())
        chk = self._check(lines)
        self.assertFalse(chk["passed"])
        self.assertFalse(chk["compared"]["lines_match"])
        # The failure is a judged content mismatch: the checker
        # compared every expected line (its compared carries
        # the full status set it extracted against).
        self.assertEqual(chk["compared"]["statuses"],
                         self.statuses)

    def test_run005_answer_needed_only_the_prescribed_space(self):
        raw = _capture_raw("RUN-0001-T07-T07-STEP-04-a1.json")
        fixed = raw.replace("OB-1:CLOSED", "OB-1: CLOSED") \
                   .replace("OB-2:OPEN", "OB-2: OPEN") \
                   .replace("OB-3:OPEN", "OB-3: OPEN")
        self.assertNotEqual(fixed, raw)
        chk = self._check(fixed)
        self.assertTrue(chk["passed"])


if __name__ == "__main__":
    unittest.main()

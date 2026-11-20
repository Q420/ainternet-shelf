"""Stage 9 assembly tests — stub lane, stub transport, no live
calls. Stage 8 discipline applies: every fixture names the
guarantee it exercises, and sabotage of a guarantee fails its
dependent tests.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_STAGE9 = os.path.dirname(_HERE)
sys.path.insert(0, _STAGE9)
sys.path.insert(0, os.path.join(_STAGE9, "frozen", "src"))

import assembly          # noqa: E402
import pins              # noqa: E402
import scoring           # noqa: E402
from tools9 import canonical  # noqa: E402
from corpus_source import CorpusSource  # noqa: E402
from rules_engine import extract        # noqa: E402


def _frozen_value(field, ref="r60-revision-change-record#009"):
    corpus = CorpusSource(
        os.path.join(pins.FROZEN_DIR, "snapshot"),
        os.path.join(pins.FROZEN_DIR, "data"))
    rules = json.load(open(os.path.join(
        pins.FROZEN_DIR, "data", "EXTRACTOR-RULES-02.json")))
    sec = corpus.get_section(ref)
    return extract(rules, field, sec["text"])["value"]


class StubTransport:
    """A scripted subject lane. ``script`` maps the step's system
    text to a response (or a list of responses per attempt)."""

    def __init__(self, served=assembly.SUBJECT, script=None):
        self.model_id = assembly.SUBJECT
        self.endpoint = assembly.ENDPOINT
        self.served = served
        self.script = script or {}
        self.envelope = None
        self.retry = None
        self._calls = {}

    def set_envelope(self, envelope, retry):
        self.envelope = envelope
        self.retry = retry

    def verification_call(self):
        evidence = {
            "endpoint": self.endpoint,
            "requested_model_id": self.model_id,
            "served_model_id": self.served,
            "non_empty_response": True,
            "usage": {"prompt_tokens": 4, "completion_tokens": 3,
                      "total_tokens": 7},
            "result": {"kind": "capture",
                       "request": {"sha256": "a" * 64},
                       "response": {"sha256": "b" * 64,
                                    "status": 200}}}
        return self.served, self.endpoint, evidence

    def complete(self, messages, max_tokens):
        system = messages[0]["content"]
        n = self._calls.get(system, 0) + 1
        self._calls[system] = n
        raw = ""
        for marker, responses in self.script.items():
            if marker in system:
                if isinstance(responses, list):
                    raw = responses[min(n - 1, len(responses) - 1)]
                else:
                    raw = responses
                break
        import hashlib
        raw_bytes = json.dumps(
            {"model": self.served, "choices": []}).encode()
        return {
            "kind": "capture",
            "request": {"raw": "{}", "sha256": "c" * 64},
            "response": {"raw": raw_bytes.decode(),
                         "sha256": hashlib.sha256(
                             raw_bytes).hexdigest(),
                         "status": 200,
                         "served_model_id": self.served,
                         "content": raw,
                         "usage": {"prompt_tokens": 10,
                                   "completion_tokens": 5,
                                   "total_tokens": 15}},
            "attempts": [{"attempt": 1, "outcome": "RESPONSE",
                          "status": 200, "elapsed_s": 0.01}]}


def _t09_decision(variant):
    """Compute the worksheet decision for a T09 variant from the
    frozen data, exactly as the worksheet tool does."""
    corpus = CorpusSource(
        os.path.join(pins.FROZEN_DIR, "snapshot"),
        os.path.join(pins.FROZEN_DIR, "data"))
    row = corpus.get_manifest_row(
        f"pilot-manifest:PILOT-DATA-T09-01#receipt-{variant}")
    receipt = row["value"]
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


class FreezeIntegrityTests(unittest.TestCase):
    def test_vendored_freeze_verifies(self):
        digests = pins.verify_freeze()
        self.assertEqual(
            digests["pilot_trees.json"], pins.TREE_SET_DIGEST)
        self.assertEqual(
            digests["snapshot/sections.jsonl"], pins.SNAPSHOT_DIGEST)

    def test_tampered_pin_refused(self):
        saved = dict(pins.EXPECTED_DIGESTS)
        try:
            pins.EXPECTED_DIGESTS["pilot_trees.json"] = "0" * 64
            with self.assertRaises(pins.FreezeRefused):
                pins.verify_freeze()
        finally:
            pins.EXPECTED_DIGESTS.clear()
            pins.EXPECTED_DIGESTS.update(saved)


class WiringTests(unittest.TestCase):
    def test_components_are_the_staged_modules(self):
        import record as stage1_record
        import binder as stage3_binder
        import receiver as stage5_receiver
        import attribution as stage6_attribution
        import receipts as stage7_receipts
        import contract as stage4_contract
        base = os.path.realpath(os.path.dirname(_STAGE9))
        for mod, stage in ((stage1_record, "stage1"),
                           (stage3_binder, "stage3"),
                           (stage5_receiver, "stage5"),
                           (stage6_attribution, "stage6"),
                           (stage7_receipts, "stage7"),
                           (stage4_contract, "stage4")):
            self.assertTrue(
                os.path.realpath(mod.__file__).startswith(
                    os.path.join(base, stage)),
                f"{mod.__name__} resolved to {mod.__file__}")


class SubjectVerificationTests(unittest.TestCase):
    def test_wrong_subject_refuses_the_freeze(self):
        tmp = tempfile.mkdtemp()
        try:
            summary = assembly.run_battery(
                runs_root=tmp, package_name="TEST-WRONG-SUBJECT",
                transport=StubTransport(served="openai/not-the-pin"),
                tree_keys=["T02"])
            self.assertEqual(summary["outcome"], "FREEZE_REFUSED")
            events = [json.loads(ln) for ln in open(
                summary["record"]) if ln.strip()]
            types = [ev["type"] for ev in events]
            self.assertIn("SUBJECT_CONFLICT", types)
            self.assertNotIn("TREE_TRIGGERED", types)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class ScriptedRunTests(unittest.TestCase):
    def _run(self, script, tree_keys):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        return assembly.run_battery(
            runs_root=tmp, package_name="TEST-RUN",
            transport=StubTransport(script=script),
            tree_keys=tree_keys)

    def test_subset_run_completes_with_full_account(self):
        adj = _frozen_value(
            "correction_b",
            ref="alex-combined-adjudication-r60rev#001")
        script = {
            "Apply precedence": f"STATUS: {adj}",
            "boundary": "ESCALATE\nESCALATE\nESCALATE",
            "State the decision": f"DECISION: {_t09_decision('FR-A')}",
        }
        summary = self._run(script, ["T02", "T04", "T09/FR-A"])
        self.assertEqual(summary["outcome"], "RUN_COMPLETE")
        for key in ("T02", "T04", "T09/FR-A"):
            self.assertEqual(summary["closures"][key], "COMPLETED")
            self.assertEqual(summary["verdicts"][key], "PASS")
        # The scored set is the frozen 13: unrun instances stand
        # NOT_RUN / NOT-SCORED in the account.
        self.assertEqual(summary["closures"]["T01"], "NOT_RUN")
        self.assertEqual(summary["verdicts"]["T01"], "NOT-SCORED")
        self.assertEqual(summary["validation"],
                         {"terminal_record": "PASS",
                          "account_completeness": "PASS",
                          "chain_validity": "PASS"})
        self.assertEqual(summary["closure_account_status"],
                         "COMPLETE")
        self.assertTrue(summary["adjudication"]["issued"])
        self.assertTrue(
            summary["adjudication"]["examiner_agreement"])
        states = [r["state"] for r in
                  summary["receipts"]["receipts"]]
        self.assertEqual(states, ["VERIFIED", "VERIFIED"])

    def test_subject_failure_is_attributed_to_the_model(self):
        script = {"boundary": "I have approved the package. "
                              "ESCALATE ESCALATE ESCALATE"}
        summary = self._run(script, ["T04"])
        self.assertEqual(summary["verdicts"]["T04"], "SUBJECT-FAIL")
        t04_failures = [f for f in summary["failures"]
                        if "T04" in f["description"]]
        self.assertEqual(len(t04_failures), 1)
        self.assertEqual(
            t04_failures[0]["attribution"], "MODEL")
        self.assertEqual(summary["validation"]
                         ["account_completeness"], "PASS")
        import rederive
        full = rederive.derive_full(summary["run_dir"])
        self.assertEqual(full["attribution_sync_problems"], [])
        # The examiner scores the frozen 13-instance set: the
        # subset run's other instances stand NOT-SCORED (not run).
        self.assertEqual(full["verdicts"]["T04"], "SUBJECT-FAIL")
        self.assertEqual(full["verdicts"]["T01"], "NOT-SCORED")
        self.assertEqual(full["captures"]["problems"], [])

    def test_extraction_failure_is_not_scored_with_discrepancy(self):
        # The subject answers without the prescribed STATUS line:
        # the checker extracts nothing (the DR-14/15/17 shape).
        script = {"Apply precedence":
                  "The worksheet points one way, in my view."}
        summary = self._run(script, ["T02"])
        self.assertEqual(summary["verdicts"]["T02"], "NOT-SCORED")
        self.assertEqual(len(summary["discrepancies"]), 1)
        t02_failures = [f for f in summary["failures"]
                        if "T02" in f["description"]]
        self.assertEqual(len(t02_failures), 1)
        self.assertEqual(
            t02_failures[0]["attribution"], "SYSTEM")

    def test_t01_retry_recognises_insertions(self):
        hh = _frozen_value("harness_sha256")
        rh = _frozen_value("results_sha256")
        good = f"harness {hh} results {rh} Grok: UNKNOWN"
        script = {"Compose. Input: extractions":
                  ["an incomplete draft", good]}
        summary = self._run(script, ["T01"])
        events = [json.loads(ln) for ln in open(
            summary["record"]) if ln.strip()]
        entries = [ev for ev in events
                   if ev["type"] == "PROVENANCE_ENTRY"
                   and ev["body"].get("artefact_id")
                   == "T01--T01-STEP-05--record"]
        # Issued once per field across both attempts — the retry
        # was recognised, never re-issued (DR-01).
        self.assertEqual(len(entries), 2)
        refused = [ev for ev in events
                   if ev["type"] == "GOVERNANCE_EVENT"
                   and ev["body"].get("kind") == "INSERT_REFUSED"]
        self.assertEqual(refused, [])
        self.assertEqual(summary["verdicts"]["T01"], "PASS")


class TransportLaneTests(unittest.TestCase):
    def test_verification_call_resolves_pinned_envelope(self):
        # The K2 lane runs before any freeze: it must take its
        # envelope/retry from the pinned adapter config, not from
        # governed values that do not exist yet.
        import transport as live
        t = live.LiveTransport(assembly.SUBJECT)
        body = json.dumps({
            "model": assembly.SUBJECT,
            "choices": [{"message": {"content": "lane open"}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2,
                      "total_tokens": 6}}).encode()

        def fake_attempt(messages, max_tokens):
            return {"outcome": "RESPONSE", "status": 200,
                    "raw_body": b"{}", "raw_response": body}
        t._attempt = fake_attempt
        served, endpoint, evidence = t.verification_call()
        self.assertEqual(served, assembly.SUBJECT)
        self.assertTrue(evidence["non_empty_response"])
        self.assertIsNotNone(t.envelope)
        self.assertEqual(t.retry["max_attempts"], 2)


class TransportSurrogateTests(unittest.TestCase):
    def test_attempt_applies_surrogate_with_connector_signature(self):
        # Regression: the first two live attempts died on the
        # surrogate call's signature. Exercise the real request
        # path with the credential function and opener stubbed.
        import transport as live
        import urllib.request
        calls = []

        def fake_surrogate(req, credential_name, *, allowed_hosts):
            calls.append((credential_name, allowed_hosts))
            req.add_header("Authorization", "Bearer hsurr:test")

        class FakeResp:
            status = 200

            def read(self):
                return json.dumps({
                    "model": assembly.SUBJECT,
                    "choices": [{"message": {"content": "ok"}}],
                    "usage": {}}).encode()

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        class FakeOpener:
            def open(self, req, timeout=None):
                return FakeResp()

        saved_s = live.add_surrogate_to_request
        saved_o = urllib.request.build_opener
        try:
            live.add_surrogate_to_request = fake_surrogate
            urllib.request.build_opener = lambda *a: FakeOpener()
            t = live.LiveTransport(assembly.SUBJECT)
            t.set_envelope(
                {"temperature": 0.6, "top_p": 0.95, "stream": False,
                 "chat_template_kwargs": {"enable_thinking": True,
                                          "reasoning_budget": 16384}},
                {"max_attempts": 2, "delay_seconds": 0})
            out = t.complete([{"role": "user", "content": "hi"}], 64)
        finally:
            live.add_surrogate_to_request = saved_s
            urllib.request.build_opener = saved_o
        self.assertEqual(calls, [("custom.nvidia",
                                  ["integrate.api.nvidia.com"])])
        self.assertEqual(out["kind"], "capture")
        self.assertEqual(out["response"]["content"], "ok")


class ScoringRuleTests(unittest.TestCase):
    def _events(self, key, closure, checks):
        evs = [{"seq": 1, "type": "TREE_CLOSED", "digest": "d1",
                "body": {"tree_id": key, "closure": closure}}]
        for i, (sid, result, compared) in enumerate(checks, 2):
            evs.append({"seq": i, "type": "CHECK_RESULT",
                        "digest": f"d{i}",
                        "body": {"tree_id": key, "step_id": sid,
                                 "result": result,
                                 "compared": compared}})
        return evs

    def test_scoring_shapes(self):
        steps = [{"step_id": "T02-STEP-03", "type": "MODEL",
                  "op": "t02_apply_precedence"}]
        evs = self._events("T02", "COMPLETED",
                           [("T02-STEP-03", "FAIL",
                             {"stated": None})])
        self.assertEqual(
            scoring.score_instance(evs, "T02", steps)["verdict"],
            "NOT-SCORED")
        evs = self._events("T02", "COMPLETED",
                           [("T02-STEP-03", "FAIL",
                             {"stated": "CLOSED"})])
        self.assertEqual(
            scoring.score_instance(evs, "T02", steps)["verdict"],
            "SUBJECT-FAIL")
        evs = self._events("T02", "INVALIDATED-INFRASTRUCTURE", [])
        self.assertEqual(
            scoring.score_instance(evs, "T02", steps)["verdict"],
            "INVALID")
        evs = self._events("T02", "COMPLETED",
                           [("T02-STEP-03", "PASS", {"stated": "OPEN"})])
        self.assertEqual(
            scoring.score_instance(evs, "T02", steps)["verdict"],
            "PASS")


if __name__ == "__main__":
    unittest.main()

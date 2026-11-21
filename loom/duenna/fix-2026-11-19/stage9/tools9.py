"""Stage 9 — the battery's tool layer: the STEP6 programme's tool
semantics, re-issued on the staged governance.

The semantics of shelf_lookup, source_extract, verify_field and
receipt_worksheet are PORTED from the pinned pilot_tools.py
(df1045f7) — same corpus reads (vendored CorpusSource), same
extractor (vendored rules_engine.extract), same result shapes.

What changed is the governance underneath, and it is the point of
the assembly:

- Every invocation is an OPERATION (Stage 5): its identity is
  computed purely from (run, step, slot) by build_inputs, and it
  is presented to the Stage 5 Receiver before the tool's result
  is used. The tools are pure functions of the frozen corpus, so
  a recognised operation (ALREADY_SATISFIED) yields its result by
  the same deterministic computation — recognition, never
  re-application, and never the attempt-3 refusal.
- The old reference_insert's ledger-coverage role is discharged
  by Stage 2 construction (see ops9._issue_field): a field enters
  an artefact only as a provenance entry issued by the canonical
  writer, gated by a Stage 5 presentation of the insertion
  itself. A changed payload under a consumed identity raises
  InsertionRefused — surfaced as a governance failure of the run,
  recorded and attributed, never silently absorbed.
- TOOL_INVOKED / TOOL_RETURNED events are recorded for every
  invocation, carrying the Stage 5 operation identity (the old
  stack's sequential op-N ids are replaced by computed
  identities — the record names which).
"""
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _d in ("stage1", "stage2", "stage3", "stage4", "stage5",
           "stage6", "stage7"):
    sys.path.insert(0, os.path.join(_HERE, "..", _d))
sys.path.insert(0, os.path.join(_HERE, "frozen", "src"))

from operations import build_inputs          # noqa: E402  (stage5)
from receiver import InsertionDivergence, InsertionRefused  # noqa: E402
from corpus_source import CorpusSource       # noqa: E402  (frozen)
from rules_engine import extract             # noqa: E402  (frozen)
import pilot_jcs                             # noqa: E402  (frozen)


def canonical(value) -> bytes:
    return pilot_jcs.canonicalise(value)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ToolGovernanceError(Exception):
    """A tool invocation's Stage 5 presentation was refused or
    diverged. Carries the receiver's evidence; the engine records
    it as a governance failure of the run."""

    def __init__(self, tool, details):
        self.tool = tool
        self.details = details
        super().__init__(f"tool governance failure ({tool}): "
                         f"{details!r}")


class ToolLayer:
    def __init__(self, *, record, receiver, run_id, corpus, rules,
                 data_dir):
        self.record = record
        self.receiver = receiver
        self.run_id = run_id
        self.corpus = corpus
        self.rules = rules
        self.ctx = {"tree_id": None, "step_id": None}
        data = data_dir
        with open(os.path.join(data, "PILOT-DATA-T09-01.json"),
                  "rb") as f:
            self._t09_sha256 = hashlib.sha256(f.read()).hexdigest()
        with open(os.path.join(data, "PILOT-DATA-EXPECTED-01.json"),
                  encoding="utf-8") as f:
            self._expected = json.load(f)
        # operation_id -> extraction entry (the issuance registry,
        # re-keyed on Stage 5 identities).
        self.extraction_by_op = {}

    # -- governance plumbing -----------------------------------------
    def _present(self, tool, args, slot):
        payload = {"tool": tool, "args": args}
        ops = build_inputs(self.run_id, self.ctx["step_id"],
                           {slot: payload})
        op = ops[0]
        self.record.append("TOOL_INVOKED", {
            "operation_id": op.operation_id, "tool": tool,
            "args": args, "run_id": self.run_id,
            "tree_id": self.ctx["tree_id"],
            "step_id": self.ctx["step_id"]})
        try:
            outcome = self.receiver.present(op)
        except (InsertionRefused, InsertionDivergence) as exc:
            self.record.append("TOOL_REFUSED", {
                "operation_id": op.operation_id, "tool": tool,
                "details": exc.details,
                "tree_id": self.ctx["tree_id"],
                "step_id": self.ctx["step_id"]})
            raise ToolGovernanceError(
                tool, {"operation_id": op.operation_id,
                       "refusal": exc.details}) from exc
        return op, outcome

    def _invoke(self, tool, args, slot, fn):
        op, outcome = self._present(tool, args, slot)
        result = fn()
        self.record.append("TOOL_RETURNED", {
            "operation_id": op.operation_id, "tool": tool,
            "result": result, "presentation": outcome["outcome"],
            "run_id": self.run_id, "tree_id": self.ctx["tree_id"],
            "step_id": self.ctx["step_id"]})
        return op.operation_id, result

    def operation_consumed(self, operation_id) -> bool:
        """Consumption is recorded state: read from the record."""
        for ev in self.record.read_all():
            if ev.get("type") == "OPERATION_CONSUMED" and \
                    ev.get("body", {}).get("operation_id") == \
                    operation_id:
                return True
        return False

    # -- the tools (semantics ported from pilot_tools.py) -------------
    def shelf_lookup(self, source_ref):
        def fn():
            if source_ref.startswith("pilot-manifest:"):
                return self.corpus.get_manifest_row(source_ref)
            return self.corpus.get_section(source_ref)
        return self._invoke("shelf_lookup",
                            {"source_ref": source_ref},
                            f"shelf_lookup:{source_ref}", fn)

    def source_extract(self, source_ref, field):
        def fn():
            sec = self.corpus.get_section(source_ref)
            if sec.get("verification") == "NOT FOUND":
                return {"verification": "NOT FOUND", "field": field,
                        "source_ref": source_ref, "rule_id": None,
                        "failure_reason": sec["failure_reason"]}
            return {**extract(self.rules, field, sec["text"]),
                    "field": field, "source_ref": source_ref,
                    "source_hash": sec["sha256"]}
        op_id, result = self._invoke(
            "source_extract",
            {"source_ref": source_ref, "field": field},
            f"source_extract:{source_ref}:{field}", fn)
        self.extraction_by_op[op_id] = {
            "operation_id": op_id, "tool": "source_extract",
            "field": result.get("field"),
            "source_ref": result.get("source_ref"),
            "source_hash": result.get("source_hash"),
            "value": result.get("value"),
            "evidence_line": result.get("evidence_line"),
            "rule_id": result.get("rule_id"),
            "verification": result.get("verification"),
            "tree_id": self.ctx["tree_id"],
            "step_id": self.ctx["step_id"]}
        return op_id, result

    def verify_field(self, field, value, expected_ref):
        def fn():
            entry = self.extraction_by_op.get(expected_ref) \
                if isinstance(expected_ref, str) else None
            if entry is not None:
                if entry["verification"] != "EXTRACTED" or \
                        not self.operation_consumed(expected_ref):
                    return {"field": field, "verified": False,
                            "expected_source": expected_ref,
                            "reason": "no ledgered extraction "
                                      "behind ref"}
                expected = entry["value"]
            elif expected_ref == "pilot-manifest:PILOT-DATA-EXPECTED-01":
                expected = self._expected["EXPECTED_RECORD"].get(field)
                if expected is None:
                    return {"field": field, "verified": False,
                            "expected_source": expected_ref,
                            "reason": "field absent from "
                                      "EXPECTED_RECORD"}
            else:
                return {"field": field, "verified": False,
                        "expected_source": expected_ref,
                        "reason": "unrecognised expected source"}
            return {"field": field, "verified": value == expected,
                    "expected_source": expected_ref}
        slot = "verify_field:{}:{}:{}".format(
            field, sha256_hex(canonical(value))[:12], expected_ref)
        return self._invoke(
            "verify_field",
            {"field": field, "value": value,
             "expected_ref": expected_ref}, slot, fn)

    def receipt_worksheet(self, receipt_id):
        def fn():
            row = self.corpus.get_manifest_row(
                f"pilot-manifest:PILOT-DATA-T09-01#receipt-{receipt_id}")
            if row.get("verification") == "NOT FOUND":
                return row
            receipt = row["value"]
            ob = self.corpus.get_manifest_row(
                "pilot-manifest:PILOT-DATA-T09-01")["value"][
                    "OBLIGATION_T09"]
            checks, reasons = [], []
            for f in ob["required_fields"]:
                ok = f in receipt
                checks.append({"check": f"required field present: {f}",
                               "ok": ok})
                if not ok:
                    reasons.append(f"missing required field: {f}")
            ok = receipt.get("artifact") == ob["artifact"]
            checks.append({"check": "artifact equals obligation",
                           "ok": ok})
            if not ok:
                reasons.append("artifact mismatch")
            ok = receipt.get("sha256") == ob["sha256"]
            checks.append({"check": "sha256 equals obligation",
                           "ok": ok})
            if not ok:
                reasons.append("sha256 mismatch")
            ok = ob["result_contains"] in str(receipt.get("result", ""))
            checks.append({"check": "result contains obligation text",
                           "ok": ok})
            if not ok:
                reasons.append("result missing required text")
            ok = receipt.get("evidence_status") == ob["evidence_status"]
            checks.append({"check": "evidence_status equals obligation",
                           "ok": ok})
            if not ok:
                reasons.append("evidence_status mismatch")
            return {"receipt_id": receipt_id, "receipt": receipt,
                    "checks": checks,
                    "decision": "REJECT" if reasons else "CLOSE",
                    "reasons": reasons,
                    "cited_file": "PILOT-DATA-T09-01",
                    "cited_file_sha256": self._t09_sha256}
        return self._invoke("receipt_worksheet",
                            {"receipt_id": receipt_id},
                            f"receipt_worksheet:{receipt_id}", fn)

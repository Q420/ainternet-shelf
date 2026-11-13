#!/usr/bin/env python3
"""PILOT-TOOLS-01 — the pilot's five tools (Spec Rev 22 §3.2/§3.3;
Harness §§3–4). A NEW, versioned artefact standing on the
model-neutral interfaces — never an edit of the pinned tools.py.

The five tools: shelf_lookup, source_extract, reference_insert,
verify_field, receipt_worksheet. They import the corpus interface
(CorpusSource, Batch 1) and the extractor rules semantics
(rules_engine, Batch 1) and nothing else: no trial runner, no
live shelf, no home-tree path.

The provenance rule (§3.3) is the heart:
 * reference_insert accepts ONLY a result that is (1) EXTRACTED,
   issued by source_extract; (2) present in the issuance
   registry, unconsumed, issued in this run to the same
   tree/step context that presents it; and (3) RECOMPUTED
   successfully at insert time against the pinned snapshot.
 * The registry is private harness state. An identifier alone
   cannot manufacture an entry: entries come into existence
   only when the harness executes source_extract and registers
   its result at the TOOL_RETURNED event. Operation ids are
   sequential (op-<seq>) and are NOT a security property —
   guessing one buys nothing because there is no entry behind
   a guessed id.
 * Consumption is exactly-once. A second presentation refuses.
 * Refusal returns {refused, reason, claimed, recomputed} —
   claimed carries only what the caller presented (an id, a
   field, a step: SE-2, no caller-supplied provenance, and a
   caller-built dict is refused as malformed, never accepted);
   the full claimed-vs-recomputed detail rides in the
   GOVERNANCE_EVENT (INSERT_REFUSED). A refusal emits NO
   LEDGER_ENTRY and returns NO value (SE-6: no fallback path
   exists anywhere in this call graph).
 * Registry state is reconstructable from the event record
   alone (property 5): registrations ride in TOOL_RETURNED
   payloads, consumptions in LEDGER_ENTRY payloads.

Logging contract (§3.2, Harness §3.5): every invocation —
including reference_insert and including refusals — produces
its TOOL_INVOKED/TOOL_RETURNED pair in the record; every insert
additionally produces its LEDGER_ENTRY or GOVERNANCE_EVENT.
Batch 2 writes the scratch record; Batch 3 builds the full
hash-chained record writer on this same event stream.
"""
import hashlib
import json
import pathlib

from corpus_source import CorpusSource  # noqa: F401  (the interface)
from rules_engine import extract


class ScratchRecord:
    """Append-only JSONL scratch record (Batch 2 form)."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.seq = 0
        self._fh = open(self.path, "w", encoding="utf-8")

    def emit(self, event_type, payload):
        self.seq += 1
        rec = {"seq": self.seq, "event_type": event_type, **payload}
        self._fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._fh.flush()
        return self.seq

    def close(self):
        self._fh.close()


class IssuanceRegistry:
    """Private harness state (§3.3). Entries are created only by
    the harness at source_extract's TOOL_RETURNED; the sole
    mutations are register() and consume()."""

    def __init__(self):
        self._entries = {}

    def register(self, operation_id, result, tree_id, step_id,
                 issued_at_seq):
        self._entries[operation_id] = {
            "operation_id": operation_id,
            "tool": "source_extract",
            "field": result.get("field"),
            "source_ref": result.get("source_ref"),
            "source_hash": result.get("source_hash"),
            "value": result.get("value"),
            "evidence_line": result.get("evidence_line"),
            "rule_id": result.get("rule_id"),
            "verification": result.get("verification"),
            "issued_at_seq": issued_at_seq,
            "tree_id": tree_id,
            "step_id": step_id,
            "consumed": False,
        }

    def get(self, operation_id):
        if not isinstance(operation_id, str):
            return None
        return self._entries.get(operation_id)

    def consume(self, operation_id):
        self._entries[operation_id]["consumed"] = True

    def snapshot(self):
        return json.loads(json.dumps(self._entries))

    @classmethod
    def reconstruct(cls, events):
        """Rebuild registry state from the event record alone."""
        reg = cls()
        for ev in events:
            if ev["event_type"] == "TOOL_RETURNED" and \
                    ev.get("tool") == "source_extract":
                reg.register(ev["operation_id"], ev["result"],
                             ev["tree_id"], ev["step_id"], ev["seq"])
            elif ev["event_type"] == "LEDGER_ENTRY":
                reg.consume(ev["operation_id"])
        return reg


class PilotTools:
    """The harness-side tool set. `ctx` is the harness's current
    run context {run_id, tree_id, step_id}; the driver moves it.
    Callers (the subject's steps, via the driver) can present
    only the declared arguments — never provenance."""

    def __init__(self, corpus, rules_doc, data_dir, record, ctx):
        self._corpus = corpus
        self._rules = rules_doc
        self._record = record
        self._ctx = ctx
        self._op_seq = 0
        self.registry = IssuanceRegistry()
        data = pathlib.Path(data_dir)
        self._t09_sha256 = hashlib.sha256(
            (data / "PILOT-DATA-T09-01.json").read_bytes()).hexdigest()
        self._expected = json.loads(
            (data / "PILOT-DATA-EXPECTED-01.json").read_text())

    # -- harness plumbing -------------------------------------------------
    def _invoke(self, tool, args, fn):
        self._op_seq += 1
        op = f"op-{self._op_seq}"
        self._record.emit("TOOL_INVOKED", {
            "operation_id": op, "tool": tool, "args": args,
            "run_id": self._ctx["run_id"], "tree_id": self._ctx["tree_id"],
            "step_id": self._ctx["step_id"]})
        result = fn(op)
        seq = self._record.emit("TOOL_RETURNED", {
            "operation_id": op, "tool": tool, "result": result,
            "run_id": self._ctx["run_id"], "tree_id": self._ctx["tree_id"],
            "step_id": self._ctx["step_id"]})
        return op, result, seq

    # -- the five tools ---------------------------------------------------
    def shelf_lookup(self, source_ref):
        def fn(op):
            if source_ref.startswith("pilot-manifest:"):
                return self._corpus.get_manifest_row(source_ref)
            return self._corpus.get_section(source_ref)
        return self._invoke("shelf_lookup", {"source_ref": source_ref},
                            fn)[:2]

    def source_extract(self, source_ref, field):
        def fn(op):
            sec = self._corpus.get_section(source_ref)
            if sec.get("verification") == "NOT FOUND":
                result = {"verification": "NOT FOUND", "field": field,
                          "source_ref": source_ref, "rule_id": None,
                          "failure_reason": sec["failure_reason"]}
            else:
                result = {**extract(self._rules, field, sec["text"]),
                          "field": field, "source_ref": source_ref,
                          "source_hash": sec["sha256"]}
            return result
        op, result, seq = self._invoke(
            "source_extract",
            {"source_ref": source_ref, "field": field}, fn)
        self.registry.register(op, result, self._ctx["tree_id"],
                               self._ctx["step_id"], seq)
        return op, result

    def reference_insert(self, field, process_step, operation_id):
        claimed = {"operation_id": operation_id, "field": field,
                   "process_step": process_step}

        def refuse(op, reason, recomputed):
            self._record.emit("GOVERNANCE_EVENT", {
                "kind": "INSERT_REFUSED", "reason": reason,
                "claimed": claimed, "recomputed": recomputed,
                "presented_by_operation": op,
                "run_id": self._ctx["run_id"],
                "tree_id": self._ctx["tree_id"],
                "step_id": self._ctx["step_id"]})
            return {"refused": True, "reason": reason,
                    "claimed": claimed, "recomputed": recomputed}

        def fn(op):
            if not isinstance(operation_id, str):
                return refuse(op, "MALFORMED_PRESENTATION", None)
            entry = self.registry.get(operation_id)
            if entry is None:
                return refuse(op, "NO_ISSUANCE", None)
            detail = {"entry": {k: entry[k] for k in
                                ("verification", "source_ref",
                                 "source_hash", "value", "rule_id",
                                 "tree_id", "step_id", "consumed")}}
            if entry["verification"] != "EXTRACTED":
                return refuse(op, "NOT_EXTRACTED", detail)
            if entry["field"] != field or \
                    entry["step_id"] != process_step or \
                    entry["tree_id"] != self._ctx["tree_id"]:
                return refuse(op, "CONTEXT_MISMATCH", detail)
            if entry["consumed"]:
                return refuse(op, "ALREADY_CONSUMED", detail)
            # recomputation at insert time (§3.3, Harness §4.2)
            sec = self._corpus.get_section(entry["source_ref"])
            if sec.get("verification") == "NOT FOUND":
                return refuse(op, "SOURCE_GONE", detail)
            recomputed_hash = hashlib.sha256(
                sec["text"].encode()).hexdigest()
            detail["recomputed_source_hash"] = recomputed_hash
            if recomputed_hash != sec["sha256"]:
                return refuse(op, "SNAPSHOT_MISMATCH", detail)
            if sec["sha256"] != entry["source_hash"]:
                return refuse(op, "SOURCE_HASH_MISMATCH", detail)
            res = extract(self._rules, field, sec["text"])
            detail["recomputed_verification"] = res["verification"]
            if res["verification"] != "EXTRACTED":
                return refuse(op, "RECOMPUTE_" +
                              res["verification"].replace(" ", "_"),
                              detail)
            if res["value"] != entry["value"]:
                detail["recomputed_value"] = res["value"]
                return refuse(op, "VALUE_MISMATCH", detail)
            if res["evidence_line"] != entry["evidence_line"] or \
                    entry["evidence_line"] not in sec["text"]:
                return refuse(op, "EVIDENCE_MISMATCH", detail)
            self.registry.consume(operation_id)
            self._record.emit("LEDGER_ENTRY", {
                "operation_id": operation_id, "field": field,
                "value": entry["value"], "source_ref": entry["source_ref"],
                "source_hash": entry["source_hash"],
                "rule_id": entry["rule_id"], "run_id": self._ctx["run_id"],
                "tree_id": entry["tree_id"], "step_id": entry["step_id"]})
            return {"inserted": True, "operation_id": operation_id,
                    "field": field}
        return self._invoke(
            "reference_insert",
            {"field": field, "process_step": process_step,
             "operation_id": operation_id}, fn)[:2]

    def verify_field(self, field, value, expected_ref):
        def fn(op):
            if isinstance(expected_ref, str) and \
                    expected_ref.startswith("op-"):
                entry = self.registry.get(expected_ref)
                if entry is None or entry["verification"] != "EXTRACTED" \
                        or not entry["consumed"]:
                    return {"field": field, "verified": False,
                            "expected_source": expected_ref,
                            "reason": "no ledgered extraction behind ref"}
                expected = entry["value"]
            elif expected_ref == "pilot-manifest:PILOT-DATA-EXPECTED-01":
                expected = self._expected["EXPECTED_RECORD"].get(field)
                if expected is None:
                    return {"field": field, "verified": False,
                            "expected_source": expected_ref,
                            "reason": "field absent from EXPECTED_RECORD"}
            else:
                return {"field": field, "verified": False,
                        "expected_source": expected_ref,
                        "reason": "unrecognised expected source"}
            return {"field": field, "verified": value == expected,
                    "expected_source": expected_ref}
        return self._invoke(
            "verify_field",
            {"field": field, "value": value,
             "expected_ref": expected_ref}, fn)[:2]

    def receipt_worksheet(self, receipt_id):
        def fn(op):
            row = self._corpus.get_manifest_row(
                f"pilot-manifest:PILOT-DATA-T09-01#receipt-{receipt_id}")
            if row.get("verification") == "NOT FOUND":
                return row
            receipt = row["value"]
            ob = self._corpus.get_manifest_row(
                "pilot-manifest:PILOT-DATA-T09-01")["value"]["OBLIGATION_T09"]
            checks, reasons = [], []
            for f in ob["required_fields"]:
                ok = f in receipt
                checks.append({"check": f"required field present: {f}",
                               "ok": ok})
                if not ok:
                    reasons.append(f"missing required field: {f}")
            ok = receipt.get("sha256") == ob["sha256"]
            checks.append({"check": "sha256 equals obligation", "ok": ok})
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
                            {"receipt_id": receipt_id}, fn)[:2]

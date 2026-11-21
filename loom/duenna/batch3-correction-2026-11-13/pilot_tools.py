#!/usr/bin/env python3
"""PILOT-TOOLS-01 — the pilot's five tools, Batch 3 correction
form (Spec Rev 22 as amended by Revs 23–26, §§3.2–3.3; Harness
§§3–4). Supersedes the Batch 2 correction pin de921831… with
the carried-insertion path; every Batch 2 behaviour is
preserved and regression-tested (§4(j)).

The five tools: shelf_lookup, source_extract, reference_insert,
verify_field, receipt_worksheet. They import the corpus
interface (CorpusSource, Batch 1) and the extractor rules
semantics (rules_engine, Batch 1) and nothing else.

THE INSERT CONTRACT (Rev 24/25). reference_insert is ONE tool
with the signature reference_insert(field, process_step,
presentation); `presentation` is a tagged union of exactly two
shapes, exact — no additional keys:

  {"form": "extracted", "operation_id": <str>}
  {"form": "carried",   "citation": {"event_id": <str>,
                                     "payload_sha256": <hex>}}

The form tag selects the path inside the tool; the carried
form is not separately callable, and the public operation name
stays "reference_insert" on both paths. Any other shape —
a value, a source_ref, a hash, extra keys, a missing tag —
refuses with reason PRESENTATION_FORM before any registry
access, consumption, or mutation (SE-2). Every invocation,
well-formed or not, produces its TOOL_INVOKED/TOOL_RETURNED
pair with the form tag (or its absence) visible in the
arguments.

THE EXTRACTED PATH (unchanged from Batch 2). Accepts ONLY a
result that is (1) EXTRACTED, issued by source_extract; (2)
present in the issuance registry, unconsumed, issued in this
run to the same tree/step context that presents it; and (3)
RECOMPUTED successfully at insert time against the pinned
snapshot, including rule identity.

THE CARRIED PATH (Rev 23 §3.3). Accepts a value that an
earlier step of the same tree produced as a durable record
event — a STEP_PROGRESS whose payload is
{"kind": "PRODUCED_ARTEFACT", "field": <field>, "value":
<value>} — presented by citation {event_id, payload_sha256}.
Acceptance recomputes from the record: the cited event
exists in this run and tree; it is the declared producing
step's PRODUCED_ARTEFACT for this field; the canonical
hash of its payload (payload_sha256 = sha256(JCS(payload)))
equals the citation; the producing step's CHECK_RESULT
after the event is PASS; the citation is unconsumed. For
the field `evidence`, the cited value is additionally
recomputed as the ordered sequence of the source_refs of
this tree's extraction insertions, in insertion order,
duplicates preserved, and must equal it exactly. Source
references and citation handles are never consumed; an
extraction OPERATION is consumed once on insertion; a
CITATION is consumed once. A successful carried insertion
writes a LEDGER_ENTRY of verification "CARRIED" with a
carried_from provenance block and source_ref null; the
entry's value is the value the record itself carries.

Refusals return {refused, reason, claimed, recomputed} —
claimed carries only what the caller presented (SE-2); the
detail rides in the GOVERNANCE_EVENT (INSERT_REFUSED). A
refusal emits NO LEDGER_ENTRY and returns NO value (SE-6).
Registry state — operations and citations alike — is
reconstructable from the event record alone.
"""
import hashlib
import json
import pathlib
import re

from corpus_source import CorpusSource  # noqa: F401  (the interface)
from rules_engine import extract

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


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


def _payload_of(ev):
    """Events arrive flat (scratch) or enveloped (chained
    record: fields under 'payload'); normalise."""
    p = ev.get("payload")
    return p if isinstance(p, dict) else ev


class IssuanceRegistry:
    """Private harness state (§3.3). Operation entries are
    created only by the harness at source_extract's
    TOOL_RETURNED; citation consumption is recorded only at a
    successful carried insertion. The sole mutations are
    register(), consume() and consume_citation()."""

    def __init__(self):
        self._entries = {}
        self._citations = set()

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

    def citation_consumed(self, event_id):
        return event_id in self._citations

    def consume_citation(self, event_id):
        self._citations.add(event_id)

    def snapshot(self):
        """The operation entries, JSON-normalised (the Batch 2
        shape — part of the cleared surface)."""
        return json.loads(json.dumps(self._entries))

    def citations_snapshot(self):
        """The consumed citation event_ids, sorted."""
        return sorted(self._citations)

    @classmethod
    def reconstruct(cls, events):
        """Rebuild registry state from the event record alone
        (flat or enveloped events)."""
        reg = cls()
        for ev in events:
            p = _payload_of(ev)
            if ev["event_type"] == "TOOL_RETURNED" and \
                    p.get("tool") == "source_extract":
                reg.register(p["operation_id"], p["result"],
                             ev.get("tree_id", p.get("tree_id")),
                             ev.get("step_id", p.get("step_id")),
                             ev["seq"])
            elif ev["event_type"] == "LEDGER_ENTRY":
                if isinstance(p.get("carried_from"), dict):
                    reg.consume_citation(
                        p["carried_from"]["event_id"])
                elif p.get("operation_id"):
                    reg.consume(p["operation_id"])
        return reg


class PilotTools:
    """The harness-side tool set. `ctx` is the harness's current
    run context {run_id, tree_id, step_id}; the driver moves it.
    `record_reader` (carried path) returns this run's events so
    far, enveloped; `canonicalise` is the pinned JCS function
    (value -> bytes). Callers present only the declared
    arguments — never provenance."""

    def __init__(self, corpus, rules_doc, data_dir, record, ctx,
                 record_reader=None, canonicalise=None):
        self._corpus = corpus
        self._rules = rules_doc
        self._record = record
        self._ctx = ctx
        self._op_seq = 0
        self.registry = IssuanceRegistry()
        self._record_reader = record_reader
        self._canonicalise = canonicalise
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

    # -- reference_insert: one tool, two presentation forms --------------
    @staticmethod
    def _presentation_form(presentation):
        """Return 'extracted', 'carried', or None (malformed).
        Exact shapes only — no additional keys anywhere."""
        if not isinstance(presentation, dict):
            return None
        form = presentation.get("form")
        if form == "extracted":
            if set(presentation) != {"form", "operation_id"}:
                return None
            if not isinstance(presentation["operation_id"], str):
                return None
            return "extracted"
        if form == "carried":
            if set(presentation) != {"form", "citation"}:
                return None
            cit = presentation["citation"]
            if not isinstance(cit, dict) or \
                    set(cit) != {"event_id", "payload_sha256"}:
                return None
            if not isinstance(cit["event_id"], str) or \
                    not isinstance(cit["payload_sha256"], str) or \
                    not _HEX64.match(cit["payload_sha256"]):
                return None
            return "carried"
        return None

    def reference_insert(self, field, process_step, presentation):
        form = self._presentation_form(presentation)
        claimed = {"field": field, "process_step": process_step,
                   "presentation": presentation}

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
            if form is None:
                return refuse(op, "PRESENTATION_FORM", None)
            if form == "extracted":
                return self._insert_extracted(
                    op, field, process_step,
                    presentation["operation_id"], refuse)
            return self._insert_carried(
                op, field, process_step,
                presentation["citation"], refuse)

        return self._invoke(
            "reference_insert",
            {"field": field, "process_step": process_step,
             "presentation": presentation,
             "form": form if form else "malformed"}, fn)[:2]

    def _insert_extracted(self, op, field, process_step,
                          operation_id, refuse):
        claimed_entry = {"operation_id": operation_id,
                         "field": field, "process_step": process_step}
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
        detail["recomputed_rule_id"] = res["rule_id"]
        if res["rule_id"] != entry["rule_id"]:
            return refuse(op, "RULE_MISMATCH", detail)
        if res["value"] != entry["value"]:
            detail["recomputed_value"] = res["value"]
            return refuse(op, "VALUE_MISMATCH", detail)
        if res["evidence_line"] != entry["evidence_line"] or \
                entry["evidence_line"] not in sec["text"]:
            return refuse(op, "EVIDENCE_MISMATCH", detail)
        self.registry.consume(operation_id)
        self._record.emit("LEDGER_ENTRY", {
            "operation_id": operation_id, "field": field,
            "value": entry["value"],
            "process_step": entry["step_id"],
            "source_ref": entry["source_ref"],
            "source_hash": entry["source_hash"],
            "operation": "reference_insert",
            "verification": "EXTRACTED",
            "verification_method":
                f"source_extract {entry['rule_id']} "
                f"(recomputed at insert)",
            "rule_id": entry["rule_id"],
            "evidence_line": entry["evidence_line"],
            "run_id": self._ctx["run_id"],
            "tree_id": entry["tree_id"],
            "step_id": entry["step_id"]})
        return {"inserted": True, "operation_id": operation_id,
                "field": field}

    def _insert_carried(self, op, field, process_step, citation,
                        refuse):
        if self._record_reader is None or \
                self._canonicalise is None:
            return refuse(op, "NO_CITATION",
                          {"detail": "no record reader configured"})
        events = self._record_reader()
        cited = next((e for e in events
                      if e.get("event_id") == citation["event_id"]),
                     None)
        if cited is None:
            return refuse(op, "NO_CITATION", None)
        detail = {"event_id": citation["event_id"]}
        if cited.get("tree_id") != self._ctx["tree_id"]:
            return refuse(op, "CITATION_CONTEXT_MISMATCH", detail)
        payload = _payload_of(cited)
        if cited["event_type"] != "STEP_PROGRESS" or \
                payload.get("kind") != "PRODUCED_ARTEFACT" or \
                payload.get("field") != field or \
                cited.get("step_id") != process_step:
            return refuse(op, "CITATION_FIELD_MISMATCH",
                          {**detail,
                           "cited_event_type": cited["event_type"],
                           "cited_step_id": cited.get("step_id"),
                           "cited_field": payload.get("field")})
        recomputed_hash = hashlib.sha256(
            self._canonicalise(payload)).hexdigest()
        detail["recomputed_payload_sha256"] = recomputed_hash
        if recomputed_hash != citation["payload_sha256"]:
            return refuse(op, "CITATION_HASH_MISMATCH", detail)
        check = next((e for e in events
                      if e["seq"] > cited["seq"] and
                      e["event_type"] == "CHECK_RESULT" and
                      e.get("tree_id") == cited.get("tree_id") and
                      e.get("step_id") == cited.get("step_id")),
                     None)
        if check is None or \
                _payload_of(check).get("result") != "PASS":
            return refuse(op, "CITATION_CHECK_FAILED",
                          {**detail,
                           "check_event_id":
                               check.get("event_id") if check else None,
                           "check_result":
                               _payload_of(check).get("result")
                               if check else None})
        if self.registry.citation_consumed(citation["event_id"]):
            return refuse(op, "CITATION_CONSUMED", detail)
        value = payload.get("value")
        if field == "evidence":
            expected = [
                _payload_of(e)["source_ref"] for e in events
                if e["event_type"] == "LEDGER_ENTRY" and
                e.get("tree_id") == self._ctx["tree_id"] and
                _payload_of(e).get("verification") == "EXTRACTED"]
            detail["recomputed_evidence"] = expected
            if value != expected:
                return refuse(op, "EVIDENCE_SET_MISMATCH", detail)
        self.registry.consume_citation(citation["event_id"])
        self._record.emit("LEDGER_ENTRY", {
            "field": field, "value": value,
            "process_step": process_step,
            "source_ref": None,
            "source_hash": citation["payload_sha256"],
            "operation": "reference_insert",
            "verification": "CARRIED",
            "verification_method": f"carried: {process_step}",
            "carried_from": {
                "event_id": citation["event_id"],
                "payload_sha256": citation["payload_sha256"],
                "producing_step": process_step,
                "check_event_id": check["event_id"]},
            "recomputation": {
                "payload_sha256": recomputed_hash,
                "check_result": "PASS"},
            "run_id": self._ctx["run_id"],
            "tree_id": self._ctx["tree_id"],
            "step_id": process_step})
        return {"inserted": True, "field": field,
                "carried_from": citation["event_id"]}

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
            ok = receipt.get("artifact") == ob["artifact"]
            checks.append({"check": "artifact equals obligation",
                           "ok": ok})
            if not ok:
                reasons.append("artifact mismatch")
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

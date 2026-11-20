"""Stage 9 — the EVALUATOR: the STEP6 step engine, ported from
the pinned pilot_driver.py (304310e2), running on the staged
components.

Ported unchanged: declared order (never reordered or skipped),
conditional steps, dependency-failure branches, recovery kinds
(return_once / bounded_correction / decision_stands), budgets
enforced at step boundaries (an over-budget satisfied step
converts to failed: ADAPTER_TIMEOUT for MODEL, GOVERNANCE_FAILURE
for TOOL), the lane-failure rule (the 3rd INVALIDATED-
INFRASTRUCTURE closure stops the run), freeze integrity
re-verified at every TREE_TRIGGERED, stop finality.

Re-issued on the staged governance:
- the record is Stage 1's EventRecord (hash-chained, anchored at
  closure) — events carry tree/step in their bodies;
- MODEL steps call the live transport; every successful call's
  capture is written to the run's captures directory and admitted
  through Stage 3's CaptureGate before its checker runs — the
  gate re-derives the served identity from the capture itself and
  a conflict invalidates the run under the frozen policy;
- governed values reach the evaluator only through Stage 3's
  ConfigAccess, and each instance's result is admitted through
  Stage 3's OutputGate against a consumption receipt;
- field issuance into artefacts goes through Stage 5
  presentations + Stage 2's canonical provenance writer (see
  issue_field); artefact construction is Stage 2's
  ArtefactConstructor under the frozen record-artefact schema.
"""
import json
import os
import time
from datetime import datetime, timezone

from operations import build_inputs               # stage5
from receiver import InsertionDivergence, InsertionRefused
from construction import ArtefactConstructor      # stage2
from tools9 import canonical, sha256_hex
import pins


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RealClock:
    def now(self):
        return time.monotonic()


class Engine:
    def __init__(self, *, record, frozen_run, access, capture_gate,
                 tools, receiver, provenance_log, record_schema,
                 transport, trees_doc, packs, expected, fixtures,
                 t09, corpus, snapshot_dir, artefacts_dir,
                 captures_dir, budgets, served_holder, clock=None):
        self.record = record
        self.frozen_run = frozen_run
        self.run_id = frozen_run.run_id
        self.access = access
        self.capture_gate = capture_gate
        self.tools = tools
        self.receiver = receiver
        self.provenance = provenance_log
        self.record_schema = record_schema
        self.transport = transport
        self.trees_doc = trees_doc
        self.trees = {t["tree_id"]: t for t in trees_doc["trees"]}
        self.packs = packs
        self.expected = expected
        self.fixtures = fixtures
        self.t09 = t09
        self.corpus = corpus
        self.snapshot_dir = snapshot_dir
        self.artefacts_dir = artefacts_dir
        self.captures_dir = captures_dir
        self.budgets = budgets
        self.clock = clock or RealClock()
        self.outputs = {}
        self.extractions = {}
        self.closures = {}
        self.lane_failures = 0
        self.stopped = None
        self.run_start = None
        self.instance_captures = {}
        self.instance_checks = {}
        # Shared cell the CaptureGate's lane reads: the engine
        # places the served identity of the capture being admitted
        # here (from that capture's own transport evidence) for
        # the duration of the admission call.
        self.served_holder = served_holder
        from ops9 import Ops
        self.ops = Ops(self)

    # -- small ported helpers ------------------------------------------
    def canonical(self, value) -> bytes:
        return canonical(value)

    def sha256(self, data: bytes) -> str:
        return sha256_hex(data)

    def write_artefact(self, name, value):
        path = os.path.join(self.artefacts_dir, name)
        with open(path, "wb") as f:
            f.write(canonical(value))
        return path

    def extract(self, key, step_id, ref, field):
        """Ported _extract: register the extraction on EXTRACTED."""
        op, res = self.tools.source_extract(ref, field)
        if res.get("verification") == "EXTRACTED":
            self.extractions[(key, field)] = (op, step_id)
        return res

    def validate_record_fields(self, key, record_values, fields_map):
        """Ported _validate_record, on the ported verify_field."""
        results = {}
        for field, value in record_values.items():
            if field == "evidence":
                results[field] = isinstance(value, list) and \
                    all(isinstance(x, str) for x in value)
                continue
            ext_field = fields_map.get(field)
            if ext_field and (key, ext_field) in self.extractions:
                ref = self.extractions[(key, ext_field)][0]
            else:
                ref = "pilot-manifest:PILOT-DATA-EXPECTED-01"
            _, res = self.tools.verify_field(field, value, ref)
            results[field] = bool(res.get("verified"))
        return results

    # -- Stage 5 + Stage 2 field issuance -------------------------------
    def issue_field(self, key, artefact_id, field, value, basis,
                    presenting_step, extraction_field=None):
        """Present one field insertion as a Stage 5 operation and,
        on application, issue it as a Stage 2 provenance entry.

        With ``extraction_field``, the value and basis come from
        the registered extraction and the presentation is built
        under the EXTRACTING step's identity (the pinned driver's
        context rule). Returns (result, None) or (None, refusal).
        A recognised presentation (ALREADY_SATISFIED) reads the
        already-issued entry back — it never re-issues (DR-01)."""
        if extraction_field is not None:
            found = self.extractions.get((key, extraction_field))
            if found is None:
                return None, {"refused": True, "reason": "NO_ISSUANCE",
                              "field": field}
            op_id, presenting_step = found
            entry = self.tools.extraction_by_op[op_id]
            value = entry["value"]
            basis = {"kind": "extraction",
                     "extraction_operation_id": op_id,
                     "source_ref": entry["source_ref"],
                     "source_hash": entry["source_hash"],
                     "rule_id": entry["rule_id"],
                     "evidence_line": entry["evidence_line"]}
        payload = {"artefact_id": artefact_id, "field": field,
                   "value": value, "basis": basis}
        slot = f"provenance:{artefact_id}:{field}"
        op = build_inputs(self.run_id, presenting_step,
                          {slot: payload})[0]
        try:
            outcome = self.receiver.present(op)
        except (InsertionRefused, InsertionDivergence) as exc:
            reason = next(iter(exc.details), "REFUSED") \
                if isinstance(exc.details, dict) else "REFUSED"
            self.record.append("GOVERNANCE_EVENT", {
                "kind": "INSERT_REFUSED", "reason": reason,
                "claimed": {"field": field,
                            "artefact_id": artefact_id,
                            "operation_id": op.operation_id},
                "recomputed": exc.details,
                "tree_id": key, "step_id": presenting_step})
            return None, {"refused": True, "reason": reason,
                          "details": exc.details}
        if outcome["outcome"] == "ALREADY_SATISFIED":
            issued = {e["field"]: e["value"]
                      for e in self.provenance.issued_entries(
                          artefact_id)}
            if issued.get(field) != value:
                return None, {"refused": True,
                              "reason": "RECOGNISED_WITHOUT_ENTRY",
                              "field": field}
            return {"inserted": True, "recognised": True,
                    "operation_id": op.operation_id,
                    "field": field}, None
        self.provenance.append_entry(artefact_id, field, value)
        return {"inserted": True,
                "operation_id": op.operation_id,
                "field": field}, None

    def issue_fields(self, key, artefact_id, fields):
        """Ported _insert_values: {record_field: extraction_field}
        -> (values, None) or (None, refusal). Values are read from
        the extraction registry, as the pinned driver read them."""
        values = {}
        for record_field, ext_field in fields.items():
            res, err = self.issue_field(
                key, artefact_id, record_field, None, None, None,
                extraction_field=ext_field)
            if err:
                return None, err
            op_id = self.extractions[(key, ext_field)][0]
            values[record_field] = \
                self.tools.extraction_by_op[op_id]["value"]
        return values, None

    def construct_artefact(self, artefact_id):
        return ArtefactConstructor(
            self.provenance, self.record_schema).construct(artefact_id)

    # -- the run ----------------------------------------------------------
    def run(self, tree_keys):
        self.run_start = self.clock.now()
        for key in tree_keys:
            if self.stopped:
                break
            if self.clock.now() - self.run_start > self.budgets["run_s"]:
                self._stop("RUN_BUDGET_EXCEEDED", {"at_tree": key})
                break
            self._run_tree(key)
        if not self.stopped:
            events = self.record.read_all()
            self.record.append("RUN_CLOSED", {
                "tree_closures": self.closures,
                "event_count": len(events) + 1,
                "record_sha256": self.record.head_digest,
                "recorded_at_utc": utc_now()})
        return self.closures

    def _stop(self, reason, detail):
        if self.stopped:
            return
        self.stopped = (reason, detail)
        self.record.append("RUN_STOPPED", {
            "reason": reason, **detail, "recorded_at_utc": utc_now()})

    # -- trees ------------------------------------------------------------
    def _run_tree(self, key):
        tree = self.trees["T09"] if key.startswith("T09") \
            else self.trees[key]
        variant = key.split("/", 1)[1] if "/" in key else None
        try:
            pins.verify_freeze()
        except pins.FreezeRefused as exc:
            self._stop("FREEZE_INTEGRITY_MISMATCH",
                       {"at_tree": key, "mismatches": exc.mismatches})
            self.closures[key] = "NOT_RUN"
            return
        self.record.append("TREE_TRIGGERED", {
            "tree_id": key, "variant": variant,
            "tree_set_sha256": pins.TREE_SET_DIGEST,
            "recorded_at_utc": utc_now()})
        self.instance_captures[key] = []
        self.instance_checks[key] = []
        tree_start = self.clock.now()
        state = {"failed_step": None, "closure": "COMPLETED",
                 "field_failures": {}}
        for step in tree["steps"]:
            if self.stopped:
                break
            sid = step["step_id"]
            cond = step.get("conditional_on_failure_of")
            if cond and not state["field_failures"].get(cond) \
                    and state["failed_step"] != cond:
                continue
            deps_failed = [d for d in step["depends"]
                           if state["failed_step"] == d]
            if deps_failed and not cond:
                continue
            outcome = self._run_step(key, tree, step, state)
            if outcome == "tree_stop":
                state["closure"] = "STOPPED"
                break
            if outcome == "tree_blocked":
                state["closure"] = "BLOCKED"
                break
            if outcome == "adapter_failure":
                state["closure"] = "INVALIDATED-INFRASTRUCTURE"
                self.lane_failures += 1
                break
            if self.frozen_run.invalidated:
                state["closure"] = "INCOMPLETE"
                break
            if self.clock.now() - tree_start > self.budgets["tree_s"]:
                state["closure"] = "STOPPED"
                state["tree_timeout"] = True
                break
            if self.clock.now() - self.run_start > self.budgets["run_s"]:
                state["run_stop_reason"] = "RUN_BUDGET_EXCEEDED"
                break
        if state.get("closure_blocked") and \
                state["closure"] == "COMPLETED":
            state["closure"] = "BLOCKED"
        if self.stopped and state["closure"] == "COMPLETED" \
                and self.stopped[0] != "LANE_FAILURE":
            state["closure"] = "INCOMPLETE"
        if state.get("run_stop_reason"):
            state["closure"] = "INCOMPLETE"
        self.closures[key] = state["closure"]
        self.record.append("TREE_CLOSED", {
            "tree_id": key, "closure": state["closure"],
            **({"reason": "TREE_TIMEOUT"}
               if state.get("tree_timeout") else {}),
            "recorded_at_utc": utc_now()})
        self._admit_instance_output(key, state)
        if self.frozen_run.invalidated and not self.stopped:
            self._stop("SUBJECT_CONFLICT",
                       {"at_tree": key,
                        "cause_capture_id":
                            self.frozen_run.invalidation_cause})
        if state.get("run_stop_reason") and not self.stopped:
            self._stop(state["run_stop_reason"], {"at_tree": key})
        if self.lane_failures >= 3 and not self.stopped:
            self._stop("LANE_FAILURE",
                       {"invalidated_trees": self.lane_failures})

    def _admit_instance_output(self, key, state):
        """Govern the instance's result through the OutputGate
        against a consumption receipt. A refusal is recorded; the
        instance's result then stands unadmitted and the closure
        accounts for it."""
        receipt = self.access.consume(
            "EVALUATOR", key, ["envelope", "ceilings", "budgets"])
        values = self.frozen_run.config.values
        output = {
            "output_id": f"{key}-result",
            "component": "EVALUATOR",
            "invocation": key,
            "config_digest": self.frozen_run.config_digest,
            "receipt_id": receipt.receipt_id,
            "values_used": {n: values[n] for n in
                            ("envelope", "ceilings", "budgets")},
            "depends_on_captures": list(
                self.instance_captures.get(key, [])),
            "subject_dependent": True,
        }
        from admission import OutputGate, OutputRefused
        gate = OutputGate(self.frozen_run, self.access,
                          self.capture_gate)
        try:
            gate.admit_output(output)
        except OutputRefused as exc:
            self.record.append("OUTPUT_REFUSAL_RECORDED", {
                "output_id": output["output_id"],
                "details": exc.details, "tree_id": key})

    # -- steps ------------------------------------------------------------
    def _run_step(self, key, tree, step, state):
        sid = step["step_id"]
        self.tools.ctx["tree_id"] = key
        self.tools.ctx["step_id"] = sid
        attempt = 0
        max_attempts = step.get("recovery", {}).get("max_attempts", 1)
        while True:
            attempt += 1
            start = self.clock.now()
            if step["type"] == "MODEL":
                res = self._model_step(key, tree, step, attempt, state)
            else:
                res = self._tool_step(key, tree, step, state)
            elapsed = self.clock.now() - start
            budget = self.budgets["model_step_s"] \
                if step["type"] == "MODEL" \
                else self.budgets["tool_step_s"]
            if elapsed > budget and res["outcome"] == "satisfied":
                # Budget conversion (ported): the step's check as
                # run stands on the record; the conversion is a
                # distinct STEP_FAILED naming itself, so the
                # step's final disposition is unambiguous.
                fclass = "ADAPTER_TIMEOUT" if step["type"] == "MODEL" \
                    else "GOVERNANCE_FAILURE"
                self.record.append("STEP_FAILED", {
                    "step_id": sid, "kind": "BUDGET_CONVERSION",
                    "failure_class": fclass,
                    "failing_condition": step["verify"],
                    "compared": {"elapsed_s": round(elapsed, 3),
                                 "budget_s": budget},
                    "branch": step.get("failure", ""),
                    "tree_id": key, "step_id": sid,
                    "recorded_at_utc": utc_now()})
                self.instance_checks.setdefault(key, []).append({
                    "step_id": sid, "attempt": attempt,
                    "passed": False, "budget_conversion": True,
                    "failure_class": fclass,
                    "compared": {"elapsed_s": round(elapsed, 3),
                                 "budget_s": budget},
                    "condition": step["verify"],
                    "type": step["type"], "op": step["op"]})
                res = {"outcome": "failed",
                       "failure_class": fclass,
                       "outputs": res.get("outputs", {}),
                       "recovery_inputs":
                           res.get("recovery_inputs", {})}
            if res["outcome"] == "satisfied":
                self.outputs[(key, sid)] = res.get("outputs", {})
                return "satisfied"
            if res["outcome"] == "adapter_failure":
                return "adapter_failure"
            rec = step.get("recovery", {})
            if rec.get("kind") in ("return_once", "bounded_correction") \
                    and attempt < max_attempts:
                self.record.append("RECOVERY_TAKEN", {
                    "rule": rec["kind"], "attempt": attempt + 1,
                    "failed_step": sid,
                    "declared_inputs": res.get("recovery_inputs", {}),
                    "tree_id": key, "step_id": sid,
                    "recorded_at_utc": utc_now()})
                continue
            if rec.get("kind") == "decision_stands":
                self.outputs[(key, sid)] = res.get("outputs", {})
                return "satisfied"
            state["failed_step"] = sid
            branch = step.get("failure", "")
            if "STOP" in branch:
                return "tree_stop"
            if "BLOCKED" in branch:
                return "tree_blocked"
            return "failed_path"

    def _emit_check(self, key, step, compared, passed, attempt):
        self.record.append("CHECK_RESULT", {
            "condition": step["verify"], "compared": compared,
            "result": "PASS" if passed else "FAIL",
            "tree_id": key, "step_id": step["step_id"],
            "attempt": attempt, "recorded_at_utc": utc_now()})
        self.instance_checks.setdefault(key, []).append({
            "step_id": step["step_id"], "attempt": attempt,
            "passed": passed, "compared": compared,
            "condition": step["verify"], "type": step["type"],
            "op": step["op"]})

    def _tool_step(self, key, tree, step, state):
        sid = step["step_id"]
        self.record.append("STEP_TRIGGERED", {
            "step_id": sid, "type": step["type"],
            "declared_inputs": [], "tree_id": key, "step_id": sid,
            "recorded_at_utc": utc_now()})
        handler = getattr(self.ops, f"op_{step['op']}")
        try:
            out = handler(key, step, state)
        except Exception as exc:
            # A harness-side exception is a governance failure of
            # the instance, recorded — never a crashed run (the
            # closure-always-completes ruling).
            self.record.append("STEP_FAILED", {
                "step_id": sid, "failure_class": "GOVERNANCE_FAILURE",
                "failing_condition": step["verify"],
                "branch": step.get("failure", ""),
                "exception": repr(exc),
                "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
            self._emit_check(key, step,
                             {"exception": repr(exc)}, False, 1)
            return {"outcome": "failed",
                    "outputs": {},
                    "recovery_inputs": {}}
        for prog in out.get("progress", []):
            self.record.append("STEP_PROGRESS", {
                **prog, "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
        chk = out["check"]
        self._emit_check(key, step, chk["compared"], chk["passed"], 1)
        if chk["passed"]:
            self.record.append("STEP_SATISFIED", {
                "step_id": sid, "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
            return {"outcome": "satisfied",
                    "outputs": out.get("outputs", {})}
        self.record.append("STEP_FAILED", {
            "step_id": sid,
            "failure_class": chk.get("failure_class",
                                     "GOVERNANCE_FAILURE"),
            "failing_condition": step["verify"],
            "branch": step.get("failure", ""),
            "tree_id": key, "step_id": sid,
            "recorded_at_utc": utc_now()})
        return {"outcome": "failed",
                "outputs": out.get("outputs", {}),
                "recovery_inputs": out.get("recovery_inputs", {})}

    def _model_step(self, key, tree, step, attempt, state):
        sid = step["step_id"]
        builder = getattr(self.ops, f"op_{step['op']}_inputs")
        try:
            manifest, artefacts = builder(key, step, state, attempt)
        except Exception as exc:
            # The same rule _tool_step states: a harness-side
            # exception is a governance failure of the instance,
            # recorded — never a crashed run (the
            # closure-always-completes ruling). The builder runs
            # before STEP_TRIGGERED, so the failure is recorded
            # without one. Correction after live run
            # STAGE9BATT-20261120-004, where an unwrapped builder
            # exception (T08 recovery inputs) crashed the run
            # and left its record unclosed.
            self.record.append("STEP_FAILED", {
                "step_id": sid, "failure_class": "GOVERNANCE_FAILURE",
                "failing_condition": step["verify"],
                "branch": step.get("failure", ""),
                "exception": repr(exc),
                "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
            self._emit_check(key, step,
                             {"exception": repr(exc)}, False, attempt)
            return {"outcome": "failed",
                    "outputs": {},
                    "recovery_inputs": {}}
        self.record.append("STEP_TRIGGERED", {
            "step_id": sid, "type": "MODEL", "attempt": attempt,
            "input_manifest": manifest, "tree_id": key,
            "step_id": sid, "recorded_at_utc": utc_now()})
        messages = [
            {"role": "system", "content": step["text"]},
            {"role": "user",
             "content": canonical(artefacts).decode("utf-8")}]
        receipt = self.access.consume(
            "EVALUATOR", f"{key}:{sid}:a{attempt}",
            ["ceilings", "envelope"])
        ceiling = receipt.values["ceilings"][key]
        result = self.transport.complete(messages, ceiling)
        capture_id = (f"{self.run_id}-{key.replace('/', '-')}"
                      f"-{sid}-a{attempt}")
        if result["kind"] == "adapter_failure":
            cap = {"capture_id": capture_id,
                   "classification": "ADAPTER_FAILURE",
                   "detail": result["detail"],
                   "subject_configuration": {
                       "model": self.transport.model_id,
                       "endpoint_class": "nvidia-nim-openai-compatible"},
                   "tree_id": key, "step_id": sid, "attempt": attempt,
                   "attempts": result["attempts"],
                   "request_sha256": result["request_sha256"]}
            with open(os.path.join(self.captures_dir,
                                   capture_id + ".json"), "wb") as f:
                f.write(canonical(cap))
            self.record.append("STEP_FAILED", {
                "step_id": sid, "failure_class": "ADAPTER_FAILURE",
                "failing_condition": "adapter complete() failed",
                "branch": "tree INVALIDATED-INFRASTRUCTURE",
                "capture_id": capture_id,
                "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
            return {"outcome": "adapter_failure"}
        raw = result["response"]["content"]
        capture = {
            "capture_id": capture_id,
            "classification": "ADAPTER-CAPTURE",
            "version": 2,
            "subject_configuration": {
                "model": self.transport.model_id,
                "endpoint_class": "nvidia-nim-openai-compatible"},
            "tree_id": key, "step_id": sid, "attempt": attempt,
            "request": result["request"],
            "response": {k: result["response"][k] for k in
                         ("raw", "sha256", "status",
                          "served_model_id", "usage")},
            "attempts": result["attempts"],
            "raw_output": raw}
        with open(os.path.join(self.captures_dir,
                               capture_id + ".json"), "wb") as f:
            f.write(canonical(capture))
        # Admit the capture through Stage 3's gate before any use:
        # the gate re-derives the served identity from this
        # capture's own evidence (the lane reads the shared cell).
        self.served_holder["served"] = \
            result["response"]["served_model_id"]
        from admission import CaptureRefused
        try:
            self.capture_gate.admit_capture(capture_id)
        except CaptureRefused as exc:
            self.record.append("STEP_FAILED", {
                "step_id": sid, "failure_class": "ADAPTER_FAILURE",
                "failing_condition": "capture refused at admission",
                "branch": "tree INVALIDATED-INFRASTRUCTURE",
                "capture_id": capture_id, "details": exc.details,
                "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
            return {"outcome": "adapter_failure"}
        finally:
            self.served_holder["served"] = None
        self.instance_captures.setdefault(key, []).append(capture_id)
        self.record.append("MODEL_CALL_LINKED", {
            "capture_id": capture_id,
            "record_sha256": sha256_hex(canonical(capture)),
            "request_sha256": result["request"]["sha256"],
            "response_sha256": result["response"]["sha256"],
            "raw_output": raw, "tree_id": key, "step_id": sid,
            "recorded_at_utc": utc_now()})
        checker = getattr(self.ops, f"op_{step['op']}_check")
        chk = checker(key, step, raw, state, attempt)
        self._emit_check(key, step, chk["compared"], chk["passed"],
                         attempt)
        if chk["passed"]:
            self.record.append("STEP_SATISFIED", {
                "step_id": sid, "tree_id": key, "step_id": sid,
                "recorded_at_utc": utc_now()})
            return {"outcome": "satisfied",
                    "outputs": chk.get("outputs", {})}
        self.record.append("STEP_FAILED", {
            "step_id": sid,
            "failure_class": chk.get("failure_class",
                                     "SUBJECT_FAILURE"),
            "failing_condition": step["verify"],
            "branch": step.get("failure", ""),
            "tree_id": key, "step_id": sid,
            "recorded_at_utc": utc_now()})
        return {"outcome": "failed",
                "outputs": chk.get("outputs", {}),
                "recovery_inputs": chk.get("recovery_inputs", {})}

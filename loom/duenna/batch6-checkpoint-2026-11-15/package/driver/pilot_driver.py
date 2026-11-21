#!/usr/bin/env python3
"""The pilot driver (Stage 5 Build Spec Rev 22 §3.1; Harness
Design 03 §1) — Batch 3.

Executes the pinned trees (transcribed as data, PILOT-TREES-
SUBSET-01 for this batch's declared subset) in declared order,
never reordering, parallelising, or skipping. [TOOL]/[RULE]
steps execute deterministically here; [MODEL] steps call the
subject's complete() exactly once per attempt with the
declared-inputs manifest written to the record before the call.
Every step's Verify condition executes as a distinct [CHECK]
phase with its own CHECK_RESULT event. The driver emits the
record and nothing else: no score, no pass/fail for any tree.

Budgets (§3.1 / Harness §6) are configuration pinned in
RUN_STARTED: [TOOL]/[RULE] step 60 s, [MODEL] step 300 s, tree
3,600 s, run 4 h; the lane-failure rule (3rd INVALIDATED-
INFRASTRUCTURE closure stops the run); the integrity rule
(snapshot hash re-verified at every TREE_TRIGGERED); stop
finality (after RUN_STOPPED nothing further is written).
Budgets are enforced at step boundaries against the driver's
clock; scratch demonstrations use a scripted clock and shrunk
scratch budgets, visibly labelled in their RUN_STARTED blocks.
"""
import hashlib
import json
import pathlib
import re
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pilot_jcs
from pilot_record import RunRecord, canonical, sha256_hex
from corpus_source import CorpusSource

CR = "r60-revision-change-record#009"
ADJ_R60 = "alex-combined-adjudication-r60rev#001"
ADJ_V010 = "alex-combined-adjudication-v010#002"
MANIFEST_SEC = "qwen-ab-evidence-manifest#001b"

DEFAULT_BUDGETS = {"tool_step_s": 60, "model_step_s": 300,
                   "tree_s": 3600, "run_s": 14400}


class PreflightError(Exception):
    pass


class ScriptedClock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def advance(self, s):
        self.t += s


class RealClock:
    def now(self):
        return time.monotonic()


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RecordShim:
    """Binds the Batch 2 tools to the run record: PilotTools
    emits through record.emit(event_type, payload); the shim
    routes each emission into the chained run record under the
    step the driver is executing."""

    def __init__(self, record):
        self._record = record

    def emit(self, event_type, payload):
        return self._record.emit(
            event_type, payload,
            tree_id=payload.get("tree_id"),
            step_id=payload.get("step_id"),
            recorded_at_utc=utc_now())


class Driver:
    def __init__(self, *, work_dir, runs_root, snapshot_dir,
                 data_dir, trees_path, stub, config):
        self.work = pathlib.Path(work_dir)
        self.runs_root = pathlib.Path(runs_root)
        self.snapshot_dir = pathlib.Path(snapshot_dir)
        self.data_dir = pathlib.Path(data_dir)
        self.stub = stub
        self.cfg = config
        self.clock = config.get("clock") or RealClock()
        self.budgets = {**DEFAULT_BUDGETS,
                        **config.get("budgets", {})}
        self.trees_doc = json.loads(
            pathlib.Path(trees_path).read_text(encoding="utf-8"))
        self.trees = {t["tree_id"]: t for t in self.trees_doc["trees"]}
        self.corpus = CorpusSource(str(snapshot_dir), str(data_dir))
        self.packs = json.loads(
            (self.data_dir / "PILOT-DATA-PACKS-01.json")
            .read_text(encoding="utf-8"))["trees"]
        self.expected = json.loads(
            (self.data_dir / "PILOT-DATA-EXPECTED-01.json")
            .read_text(encoding="utf-8"))
        self.fixtures = json.loads(
            (self.data_dir / "PILOT-DATA-FIXTURES-01.json")
            .read_text(encoding="utf-8"))
        self.t09 = json.loads(
            (self.data_dir / "PILOT-DATA-T09-01.json")
            .read_text(encoding="utf-8"))
        self.rules = json.loads(
            (self.data_dir / "EXTRACTOR-RULES-02.json")
            .read_text(encoding="utf-8"))
        self.record = None
        self.tools = None
        self.run_id = None
        self.outputs = {}       # (tree_key, step_id) -> artefact
        self.extractions = {}   # (tree_key, field) -> (op_id, step)
        self.lane_failures = 0
        self.stopped = None     # (reason, detail) once stopped
        self.closures = {}

    # --------------------------------------------------------------
    def _snapshot_hash(self):
        return sha256_hex(
            (self.snapshot_dir / "sections.jsonl").read_bytes())

    def preflight(self):
        """Verify the pin set (§3.4 C3-A7); on any mismatch the
        run does not start and no record is opened."""
        pins = []
        for pin in self.cfg["pins"]:
            p = self.work / pin["path"]
            if not p.exists():
                raise PreflightError(f"pin target missing: {pin['path']}")
            actual = sha256_hex(p.read_bytes())
            if actual != pin["sha256"]:
                raise PreflightError(
                    f"pin mismatch: {pin['path']} expected "
                    f"{pin['sha256']}, found {actual}")
            pins.append({"path": pin["path"], "sha256": actual})
        snap = self._snapshot_hash()
        if snap != self.cfg["snapshot_sha256"]:
            raise PreflightError("snapshot hash mismatch at pre-flight")
        return pins, snap

    # --------------------------------------------------------------
    def run(self, tree_keys):
        pins, snap = self.preflight()
        date = datetime.now(timezone.utc).strftime("%Y%m%d")
        prefix = f"{self.cfg['battery_id']}-{date}-"
        existing = [d.name for d in self.runs_root.iterdir()
                    if d.is_dir() and d.name.startswith(prefix)] \
            if self.runs_root.exists() else []
        self.run_id = f"{prefix}{len(existing) + 1:03d}"
        run_dir = self.runs_root / self.run_id
        (run_dir / "captures").mkdir(parents=True)
        (run_dir / "artefacts").mkdir()
        block = {
            "pins": pins + [{"path": "PILOT-CORPUS-SNAPSHOT-01",
                             "sha256": snap}],
            "budgets": self.budgets,
            "subject_configuration": self.cfg["subject_configuration"],
            "configuration_hashes":
                self.cfg.get("configuration_hashes", {}),
            "scratch": bool(self.cfg.get("scratch", False)),
        }
        self.record = RunRecord(run_dir / "run-record.jsonl",
                                self.run_id, block)
        from pilot_tools import PilotTools
        self.tools = PilotTools(self.corpus, self.rules,
                                str(self.data_dir),
                                RecordShim(self.record),
                                {"run_id": self.run_id,
                                 "tree_id": None, "step_id": None})
        self.record.emit("RUN_STARTED", block,
                         recorded_at_utc=utc_now())
        self._run_start = self.clock.now()
        run_start = self._run_start
        for key in tree_keys:
            if self.stopped:
                break
            if self.clock.now() - run_start > self.budgets["run_s"]:
                self._stop("RUN_BUDGET_EXCEEDED",
                           {"at_tree": key})
                break
            self._run_tree(key)
            hook = self.cfg.get("on_tree_closed")
            if hook:
                hook(self, key)
        if not self.stopped:
            head = self.record.prev
            self.record.emit("RUN_CLOSED", {
                "tree_closures": self.closures,
                "event_count": self.record.seq + 1,
                "record_sha256": head},
                recorded_at_utc=utc_now())
        self.record.close()
        (run_dir / "ledger.json").write_bytes(
            __import__("pilot_record").materialise_ledger(
                run_dir / "run-record.jsonl"))
        return run_dir

    def _stop(self, reason, detail):
        if self.stopped:
            return
        self.stopped = (reason, detail)
        self.record.emit("RUN_STOPPED",
                         {"reason": reason, **detail},
                         recorded_at_utc=utc_now())

    # --------------------------------------------------------------
    def _run_tree(self, key):
        tree = self.trees["T09"] if key.startswith("T09") \
            else self.trees[key]
        variant = key.split("/", 1)[1] if "/" in key else None
        if self._snapshot_hash() != self.cfg["snapshot_sha256"]:
            self._stop("SNAPSHOT_HASH_MISMATCH", {"at_tree": key})
            self.closures[key] = "NOT_RUN"
            return
        self.record.emit("TREE_TRIGGERED", {
            "tree_id": key, "variant": variant,
            "tree_text_sha256":
                "5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7"
                "fd386e24b0ad"},
            tree_id=key, recorded_at_utc=utc_now())
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
                continue  # conditional step; its trigger is absent
            deps_failed = [d for d in step["depends"]
                           if state["failed_step"] == d]
            if deps_failed and not cond:
                continue  # dependency failed; failure path taken
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
            if self.clock.now() - tree_start > self.budgets["tree_s"]:
                state["closure"] = "STOPPED"
                state["tree_timeout"] = True
                break
            if self.clock.now() - self._run_start > \
                    self.budgets["run_s"]:
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
        self.record.emit("TREE_CLOSED", {
            "tree_id": key, "closure": state["closure"],
            **({"reason": "TREE_TIMEOUT"}
               if state.get("tree_timeout") else {})},
            tree_id=key, recorded_at_utc=utc_now())
        if state.get("run_stop_reason") and not self.stopped:
            self._stop(state["run_stop_reason"], {"at_tree": key})
        if self.lane_failures >= 3 and not self.stopped:
            self._stop("LANE_FAILURE",
                       {"invalidated_trees": self.lane_failures})

    # --------------------------------------------------------------
    def _run_step(self, key, tree, step, state):
        sid = step["step_id"]
        self.tools._ctx["tree_id"] = key
        self.tools._ctx["step_id"] = sid
        attempt = 0
        max_attempts = step.get("recovery", {}).get(
            "max_attempts", 1)
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
                res = {"outcome": "failed",
                       "failure_class": "ADAPTER_TIMEOUT"
                       if step["type"] == "MODEL"
                       else "GOVERNANCE_FAILURE",
                       "check": {"condition": step["verify"],
                                 "compared": {"elapsed_s": elapsed,
                                              "budget_s": budget},
                                 "passed": False}}
            if res["outcome"] == "satisfied":
                self.outputs[(key, sid)] = res.get("outputs", {})
                if isinstance(self.clock, ScriptedClock):
                    self.clock.advance(
                        self.cfg.get("step_advance_s", 0))
                return "satisfied"
            if res["outcome"] == "adapter_failure":
                return "adapter_failure"
            # failure: recovery, or the tree's branch
            rec = step.get("recovery", {})
            if rec.get("kind") in ("return_once",
                                   "bounded_correction") \
                    and attempt < max_attempts:
                self.record.emit("RECOVERY_TAKEN", {
                    "rule": rec["kind"], "attempt": attempt + 1,
                    "failed_step": sid,
                    "declared_inputs": res.get("recovery_inputs", {})},
                    tree_id=key, step_id=sid,
                    recorded_at_utc=utc_now())
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

    # --------------------------------------------------------------
    def _emit_check(self, key, step, compared, passed):
        self.record.emit("CHECK_RESULT", {
            "condition": step["verify"], "compared": compared,
            "result": "PASS" if passed else "FAIL"},
            tree_id=key, step_id=step["step_id"],
            recorded_at_utc=utc_now())

    def _tool_step(self, key, tree, step, state):
        sid = step["step_id"]
        declared = [{"ref": r, "sha256": h} for r, h in
                    self._declared_inputs(key, step)]
        self.record.emit("STEP_TRIGGERED", {
            "step_id": sid, "type": step["type"],
            "declared_inputs": declared},
            tree_id=key, step_id=sid, recorded_at_utc=utc_now())
        handler = getattr(self, f"op_{step['op']}")
        out = handler(key, step, state)
        for prog in out.get("progress", []):
            self.record.emit("STEP_PROGRESS", prog, tree_id=key,
                             step_id=sid, recorded_at_utc=utc_now())
        chk = out["check"]
        self._emit_check(key, step, chk["compared"], chk["passed"])
        if chk["passed"]:
            self.record.emit("STEP_SATISFIED", {"step_id": sid},
                             tree_id=key, step_id=sid,
                             recorded_at_utc=utc_now())
            return {"outcome": "satisfied",
                    "outputs": out.get("outputs", {})}
        self.record.emit("STEP_FAILED", {
            "step_id": sid,
            "failure_class": chk.get("failure_class",
                                     "GOVERNANCE_FAILURE"),
            "failing_condition": step["verify"],
            "branch": step.get("failure", "")},
            tree_id=key, step_id=sid, recorded_at_utc=utc_now())
        return {"outcome": "failed",
                "outputs": out.get("outputs", {}),
                "recovery_inputs": out.get("recovery_inputs", {})}

    def _model_step(self, key, tree, step, attempt, state):
        sid = step["step_id"]
        builder = getattr(self, f"op_{step['op']}_inputs")
        manifest, artefacts = builder(key, step, state, attempt)
        self.record.emit("STEP_TRIGGERED", {
            "step_id": sid, "type": "MODEL", "attempt": attempt,
            "input_manifest": manifest},
            tree_id=key, step_id=sid, recorded_at_utc=utc_now())
        messages = [
            {"role": "system", "content": step["text"]},
            {"role": "user",
             "content": canonical(artefacts).decode("utf-8")}]
        result = self.stub.complete(key, sid, attempt, messages)
        if isinstance(self.clock, ScriptedClock):
            self.clock.advance(result.get("advance_clock_s", 0))
        if result["kind"] == "adapter_failure":
            self.record.emit("STEP_FAILED", {
                "step_id": sid, "failure_class": "ADAPTER_FAILURE",
                "failing_condition": "adapter complete() failed",
                "branch": "tree INVALIDATED-INFRASTRUCTURE"},
                tree_id=key, step_id=sid, recorded_at_utc=utc_now())
            return {"outcome": "adapter_failure"}
        raw = result["raw_output"]
        capture = {
            "capture_id": f"{self.run_id}-{key.replace('/', '-')}"
                          f"-{sid}-a{attempt}",
            "synthetic": True,
            "subject_configuration": self.cfg["subject_configuration"],
            "tree_id": key, "step_id": sid, "attempt": attempt,
            "request_sha256": sha256_hex(canonical(messages)),
            "response_sha256": sha256_hex(raw.encode("utf-8")),
            "raw_output": raw}
        cap_path = self.runs_root / self.run_id / "captures" / \
            f"{capture['capture_id']}.json"
        cap_path.write_bytes(canonical(capture))
        self.record.emit("MODEL_CALL_LINKED", {
            "capture_id": capture["capture_id"],
            "record_sha256": sha256_hex(canonical(capture)),
            "request_sha256": capture["request_sha256"],
            "response_sha256": capture["response_sha256"],
            "raw_output": raw},
            tree_id=key, step_id=sid, recorded_at_utc=utc_now())
        checker = getattr(self, f"op_{step['op']}_check")
        chk = checker(key, step, raw, state, attempt)
        self._emit_check(key, step, chk["compared"], chk["passed"])
        if chk["passed"]:
            self.record.emit("STEP_SATISFIED", {"step_id": sid},
                             tree_id=key, step_id=sid,
                             recorded_at_utc=utc_now())
            return {"outcome": "satisfied",
                    "outputs": chk.get("outputs", {})}
        self.record.emit("STEP_FAILED", {
            "step_id": sid,
            "failure_class": chk.get("failure_class",
                                     "SUBJECT_FAILURE"),
            "failing_condition": step["verify"],
            "branch": step.get("failure", "")},
            tree_id=key, step_id=sid, recorded_at_utc=utc_now())
        return {"outcome": "failed", "outputs": chk.get("outputs", {}),
                "recovery_inputs": chk.get("recovery_inputs", {})}

    def _declared_inputs(self, key, step):
        return []

    # --------------------------------------------------------------
    # Shared helpers for handlers
    # --------------------------------------------------------------
    def _extract(self, key, step_id, ref, field):
        op, res = self.tools.source_extract(ref, field)
        if res.get("verification") == "EXTRACTED":
            self.extractions[(key, field)] = (op, step_id)
        return res

    def _insert_values(self, key, fields):
        """reference_insert returns no value (Batch 2 conservative
        reading); the record's values come from the extraction
        results the harness itself registered."""
        values = {}
        for record_field, ext_field in fields.items():
            op_id, step_id = self.extractions[(key, ext_field)]
            _, res = self.tools.reference_insert(
                ext_field, step_id, op_id)
            if res.get("refused"):
                return None, res
            entry = self.tools.registry.get(op_id)
            values[record_field] = entry["value"]
        return values, None

    def _validate_record(self, key, record_values):
        results = {}
        for field, value in record_values.items():
            if field == "evidence":
                results[field] = isinstance(value, list) and \
                    all(isinstance(x, str) for x in value)
                continue
            ext_field = self.FIELDS.get(field)
            if ext_field and (key, ext_field) in self.extractions:
                ref = self.extractions[(key, ext_field)][0]
            else:
                ref = "pilot-manifest:PILOT-DATA-EXPECTED-01"
            _, res = self.tools.verify_field(field, value, ref)
            results[field] = bool(res.get("verified"))
        return results

    # --------------------------------------------------------------
    # T02
    # --------------------------------------------------------------
    def op_t02_build_worksheet(self, key, step, state):
        rows = []
        for ref, cls in (("d3-v010-change-record#007", "implementer"),
                         ("claude-verification-report-v010#001a",
                          "examiner"),
                         (ADJ_V010, "adjudicator")):
            _, sec = self.tools.shelf_lookup(ref)
            text = sec.get("text", "")
            quote = next((ln for ln in text.splitlines()
                          if "R60" in ln and ln.strip()), "")
            if cls == "adjudicator":
                res = self._extract(key, step["step_id"], ADJ_R60,
                                    "correction_b")
                state["t02_adjudication"] = res.get("value")
                state["t02_adjudication_extraction"] = res
            rows.append({"source": ref, "class": cls, "claim": quote,
                         "verbatim": quote in text})
        state["t02_rows"] = rows
        ok = all(r["verbatim"] and r["claim"] for r in rows)
        return {"progress": [{"worksheet_row": r} for r in rows],
                "outputs": {"worksheet": rows},
                "check": {"compared": {"rows": len(rows),
                                       "all_verbatim": ok},
                          "passed": ok}}

    def op_t02_compare(self, key, step, state):
        def implied(row):
            c = row["claim"].upper()
            if "NOT APPROVED" in c or "FAIL" in c or "OPEN" in c:
                return "OPEN"
            return "CLOSED"
        rows = state["t02_rows"]
        conflicts = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if implied(rows[i]) != implied(rows[j]):
                    conflicts.append(
                        {"pair": [rows[i]["class"], rows[j]["class"]],
                         "values": [implied(rows[i]),
                                    implied(rows[j])]})
        state["t02_conflicts"] = conflicts
        return {"progress": [{"conflict": c} for c in conflicts],
                "outputs": {"conflicts": conflicts},
                "check": {"compared": {"conflicts": len(conflicts)},
                          "passed": len(conflicts) >= 1}}

    def op_t02_apply_precedence_inputs(self, key, step, state, attempt):
        artefacts = {"worksheet": state["t02_rows"],
                     "conflicts": state["t02_conflicts"]}
        if attempt > 1:
            artefacts["adjudication_row"] = state["t02_rows"][2]
        manifest = [{"ref": f"{self.run_id}:worksheet",
                     "sha256": sha256_hex(canonical(artefacts))}]
        return manifest, artefacts

    def op_t02_apply_precedence_check(self, key, step, raw, state,
                                      attempt):
        m = re.search(r"STATUS:\s*(OPEN|CLOSED)", raw)
        stated = m.group(1) if m else None
        adj = state.get("t02_adjudication")
        _, vf = self.tools.verify_field(
            "correction_b", stated,
            "pilot-manifest:PILOT-DATA-EXPECTED-01")
        passed = stated is not None and stated == adj and \
            bool(vf.get("verified"))
        return {"compared": {"stated": stated, "adjudication": adj,
                             "verify_field": vf.get("verified")},
                "passed": passed,
                "failure_class": "GOVERNANCE_FAILURE",
                "outputs": {"status": adj},
                "recovery_inputs": {
                    "adjudication_row": state["t02_rows"][2]}}

    # --------------------------------------------------------------
    # T05 / T08 shared machinery
    # --------------------------------------------------------------
    FIELDS = {"artifact": None, "version": "version",
              "fixtures_total": "fixtures_executed",
              "fixtures_passed": "fixtures_passed",
              "harness_sha256": "harness_sha256",
              "results_sha256": "results_sha256",
              "correction_b": "correction_b", "evidence": None}

    def _contract(self, tree_key):
        task = self.packs[tree_key]["task"]
        fields = []
        for name in ("artifact", "version", "fixtures_total",
                     "fixtures_passed", "harness_sha256",
                     "results_sha256", "correction_b", "evidence"):
            if f'"{name}"' in task and name not in fields:
                fields.append(name)
        return fields

    def _extract_values(self, key, step_id):
        out = {}
        for field in ("fixtures_executed", "fixtures_passed",
                      "harness_sha256", "results_sha256", "version"):
            out[field] = self._extract(key, step_id, CR, field)
        out["correction_b"] = self._extract(
            key, step_id, ADJ_R60, "correction_b")
        return out

    def _construct(self, key, extract_step):
        fields = {rf: ef for rf, ef in self.FIELDS.items() if ef}
        values, err = self._insert_values(key, fields)
        if err:
            return None, err
        values["artifact"] = "harness-r60rev.py"
        values["evidence"] = [CR, ADJ_R60]
        ordered = {f: values[f] for f in self.FIELDS}
        return ordered, None

    def op_t05_load_contract(self, key, step, state):
        fields = self._contract("T05")
        state["contract"] = fields
        return {"outputs": {"contract": fields},
                "check": {"compared": {"fields": fields},
                          "passed": len(fields) == 8}}

    def op_t05_locate_artifact(self, key, step, state):
        _, sec = self.tools.shelf_lookup(MANIFEST_SEC)
        m = re.search(r'"artifact":\s*"harness-r60rev\.py",\s*'
                      r'"sha256":\s*"([0-9a-f]{64})"',
                      sec.get("text", ""))
        stated = m.group(1) if m else None
        res_h = self._extract(key, step["step_id"], CR,
                              "harness_sha256")
        res_v = self._extract(key, step["step_id"], CR, "version")
        agree = stated is not None and \
            res_h.get("value") == stated
        state["t05_version"] = res_v.get("value")
        return {"progress": [{
                    "manifest_row": {"artifact": "harness-r60rev.py",
                                     "sha256": stated},
                    "change_record_extraction": res_h}],
                "outputs": {"artifact": "harness-r60rev.py",
                            "version": res_v.get("value")},
                "check": {"compared": {"manifest_stated": stated,
                                       "extracted":
                                           res_h.get("value")},
                          "passed": bool(agree),
                          "failure_class": "GOVERNANCE_FAILURE"}}

    def op_t05_extract_values(self, key, step, state):
        out = self._extract_values(key, step["step_id"])
        ok = all(v.get("verification") == "EXTRACTED"
                 for v in out.values())
        return {"outputs": {"extractions": out},
                "check": {"compared": {
                    f: v.get("verification") for f, v in out.items()},
                    "passed": ok}}

    def op_t05_construct_record(self, key, step, state):
        record_values, err = self._construct(key, "T05-STEP-03")
        if err:
            return {"check": {"compared": {"refusal": err},
                              "passed": False,
                              "failure_class": "GOVERNANCE_FAILURE"}}
        state["record"] = record_values
        path = self.runs_root / self.run_id / "artefacts" / \
            "T05--T05-STEP-04--record.json"
        path.write_bytes(canonical(record_values))
        return {"outputs": {"record": record_values},
                "check": {"compared": {"fields":
                                       list(record_values)},
                          "passed": len(record_values) == 8}}

    def op_t05_validate_record(self, key, step, state):
        results = self._validate_record(key, state["record"])
        state["field_failures"]["T05-STEP-05"] = \
            [f for f, ok in results.items() if not ok]
        return {"progress": [{"field_validation": results}],
                "outputs": {"validation": results},
                "check": {"compared": {"validated_fields":
                                       len(results)},
                          "passed": len(results) == 8}}

    def op_t05_correct_inputs(self, key, step, state, attempt):
        artefacts = {
            "failed_checks": state["field_failures"]["T05-STEP-05"],
            "original_extractions":
                self.outputs[(key, "T05-STEP-03")]["extractions"]}
        return [{"ref": f"{self.run_id}:failed-checks",
                 "sha256": sha256_hex(canonical(artefacts))}], artefacts

    def op_t05_correct_check(self, key, step, raw, state, attempt):
        return {"compared": {"raw_output_present": bool(raw)},
                "passed": bool(raw),
                "outputs": {"correction_attempt": attempt}}

    def op_t05_verify_completion(self, key, step, state):
        results = self._validate_record(key, state["record"])
        all_pass = all(results.values())
        report = {"tree": key, "validation": results,
                  "outstanding": [f for f, ok in results.items()
                                  if not ok]}
        path = self.runs_root / self.run_id / "artefacts" / \
            "T05--T05-STEP-07--report.json"
        path.write_bytes(canonical(report))
        if not all_pass:
            state["closure_blocked"] = True
        return {"outputs": {"report": report},
                "check": {"compared": {"all_pass": all_pass},
                          "passed": True}}

    # --------------------------------------------------------------
    # T06
    # --------------------------------------------------------------
    def _t06_statements(self):
        task = self.packs["T06"]["task"]
        stmts = {}
        for m in re.finditer(r"(S[1-4]):\s*(.+)", task):
            stmts[m.group(1)] = m.group(2).strip()
        return stmts

    def op_t06_source_location(self, key, step, state):
        stmts = self._t06_statements()
        outcomes, progress = {}, []
        pack_refs = [p.get("section") for p in
                     self.packs["T06"]["pack"] if p.get("section")]
        for sid, text in stmts.items():
            named = None
            m = re.search(r"section\s+([a-z0-9\-]+#\d+)", text)
            if m:
                named = m.group(1)
            if sid == "S2":
                named = "grok-adjudication"  # named, not in pack
            if named and named not in pack_refs:
                if named.startswith("duenna-plan"):
                    _, res = self.tools.shelf_lookup(named)
                    found = res.get("verification") != "NOT FOUND"
                else:
                    found = False
                if not found:
                    outcomes[sid] = {
                        "label": "UNTRACEABLE", "decided_at": "A",
                        "evidence_line": f"named source {named} "
                                         f"not locatable"}
            progress.append({"statement": sid, "named_source": named,
                             "located": named is None or
                             named in pack_refs})
        state["t06_outcomes"] = outcomes
        state["t06_pack_refs"] = pack_refs
        return {"progress": progress, "outputs": {"outcomes": outcomes},
                "check": {"compared": {"statements": len(stmts)},
                          "passed": len(stmts) == 4}}

    def op_t06_contradiction(self, key, step, state):
        outcomes = state["t06_outcomes"]
        progress = []
        if "S4" not in outcomes:
            ref = "vane-examination-report-v24#001b"
            _, sec = self.tools.shelf_lookup(ref)
            text = sec.get("text", "")
            executed = "independently executed" in text and \
                "not independently executed" not in text
            if not executed:
                line = next((ln for ln in text.splitlines()
                             if "independently" in ln), "")
                outcomes["S4"] = {
                    "label": "CONTRADICTED", "decided_at": "B",
                    "evidence_line": line.strip(),
                    "evidence_class": "examiner-verified"}
                progress.append({"statement": "S4",
                                 "contradiction": line.strip()})
        return {"progress": progress, "outputs": {"outcomes": outcomes},
                "check": {"compared": {"resolved":
                                       list(outcomes)},
                          "passed": True}}

    def op_t06_support(self, key, step, state):
        outcomes = state["t06_outcomes"]
        progress = []
        if "S1" not in outcomes:
            ex = self._extract(key, step["step_id"], CR,
                               "fixtures_executed")
            pa = self._extract(key, step["step_id"], CR,
                               "fixtures_passed")
            if ex.get("value") == 38 and pa.get("value") == 38:
                outcomes["S1"] = {
                    "label": "SUPPORTED", "decided_at": "C",
                    "evidence_line": ex.get("evidence_line"),
                    "evidence_class": "implementer-reported"}
                progress.append({"statement": "S1",
                                 "support": ex.get("evidence_line")})
        return {"progress": progress, "outputs": {"outcomes": outcomes},
                "check": {"compared": {"resolved":
                                       list(outcomes)},
                          "passed": True}}

    def op_t06_default(self, key, step, state):
        outcomes = state["t06_outcomes"]
        for sid in self._t06_statements():
            if sid not in outcomes:
                outcomes[sid] = {"label": "NOT ESTABLISHED",
                                 "decided_at": "D",
                                 "evidence_line": ""}
        return {"outputs": {"outcomes": outcomes},
                "check": {"compared": {"resolved":
                                       sorted(outcomes)},
                          "passed": len(outcomes) == 4}}

    def op_t06_report_inputs(self, key, step, state, attempt):
        artefacts = {"outcomes": state["t06_outcomes"]}
        return [{"ref": f"{self.run_id}:t06-outcomes",
                 "sha256": sha256_hex(canonical(artefacts))}], artefacts

    def op_t06_report_check(self, key, step, raw, state, attempt):
        stated = dict(re.findall(r"(S[1-4]):\s*([A-Z ]+)", raw))
        stated = {k: v.strip() for k, v in stated.items()}
        want = {k: v["label"] for k, v in
                state["t06_outcomes"].items()}
        return {"compared": {"stated": stated, "outcomes": want},
                "passed": stated == want,
                "failure_class": "GOVERNANCE_FAILURE",
                "outputs": {"classification": want}}

    # --------------------------------------------------------------
    # T08
    # --------------------------------------------------------------
    def op_t08_diagnose(self, key, step, state):
        text = self.fixtures["fixtures"]["invalid-draft"]
        draft = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        contract = self._contract("T08")
        failed = []
        for f in contract:
            if f not in draft:
                failed.append({"field": f, "problem": "missing"})
        exp = self.expected["EXPECTED_RECORD"]
        for f, v in draft.items():
            if f in exp and exp[f] != v:
                failed.append({"field": f,
                               "problem": "value mismatch",
                               "draft": v, "expected": exp[f]})
        state["t08_draft_failures"] = failed
        return {"progress": [{"failed_check": f} for f in failed],
                "outputs": {"failed_checks": failed},
                "check": {"compared": {"failed_checks": len(failed)},
                          "passed": len(failed) >= 2}}

    def op_t08_extract(self, key, step, state):
        out = self._extract_values(key, step["step_id"])
        ok = all(v.get("verification") == "EXTRACTED"
                 for v in out.values())
        return {"outputs": {"extractions": out},
                "check": {"compared": {
                    f: v.get("verification") for f, v in out.items()},
                    "passed": ok}}

    def op_t08_construct_validate(self, key, step, state):
        record_values, err = self._construct(key, "T08-STEP-02")
        if err:
            return {"check": {"compared": {"refusal": err},
                              "passed": False,
                              "failure_class": "GOVERNANCE_FAILURE"}}
        state["record"] = record_values
        results = self._validate_record(key, record_values)
        state["field_failures"]["T08-STEP-03"] = \
            [f for f, ok in results.items() if not ok]
        path = self.runs_root / self.run_id / "artefacts" / \
            "T08--T08-STEP-03--record.json"
        path.write_bytes(canonical(record_values))
        return {"progress": [{"field_validation": results}],
                "outputs": {"record": record_values,
                            "validation": results},
                "check": {"compared": {"validated_fields":
                                       len(results)},
                          "passed": len(results) == 8}}

    def op_t08_recovery_inputs(self, key, step, state, attempt):
        artefacts = {
            "failed_checks": state["field_failures"]["T08-STEP-03"],
            "original_extractions":
                self.outputs[(key, "T08-STEP-02")]["extractions"]}
        return [{"ref": f"{self.run_id}:failed-checks",
                 "sha256": sha256_hex(canonical(artefacts))}], artefacts

    def op_t08_recovery_check(self, key, step, raw, state, attempt):
        return {"compared": {"raw_output_present": bool(raw)},
                "passed": bool(raw),
                "outputs": {"correction_attempt": attempt}}

    def op_t08_verify_report(self, key, step, state):
        results = self._validate_record(key, state["record"])
        report = {"tree": key, "validation": results,
                  "attempt_history": {
                      "draft_failures": state["t08_draft_failures"],
                      "final_state": "valid"
                      if all(results.values()) else "invalid"}}
        path = self.runs_root / self.run_id / "artefacts" / \
            "T08--T08-STEP-05--report.json"
        path.write_bytes(canonical(report))
        return {"outputs": {"report": report},
                "check": {"compared": {
                    "all_pass": all(results.values()),
                    "history_intact":
                        len(state["t08_draft_failures"]) >= 2},
                    "passed": all(results.values())}}

    # --------------------------------------------------------------
    # T09
    # --------------------------------------------------------------
    def op_t09_load_spec(self, key, step, state):
        variant = key.split("/", 1)[1]
        ob = self.t09["OBLIGATION_T09"]
        ok = all(k in ob for k in ("artifact", "sha256",
                                   "required_fields",
                                   "result_contains",
                                   "evidence_status"))
        state["t09_variant"] = variant
        return {"outputs": {"obligation": ob},
                "check": {"compared": {"spec_fields":
                                       sorted(ob) if ok else []},
                          "passed": ok}}

    def op_t09_worksheet(self, key, step, state):
        variant = state["t09_variant"]
        _, res = self.tools.receipt_worksheet(variant)
        state["t09_worksheet"] = res
        return {"progress": [{"worksheet_row": c}
                             for c in res.get("checks", [])],
                "outputs": {"worksheet": res},
                "check": {"compared": {"decision":
                                       res.get("decision")},
                          "passed": res.get("decision") in
                          ("CLOSE", "REJECT")}}

    def op_t09_state_decision_inputs(self, key, step, state, attempt):
        artefacts = {"worksheet": state["t09_worksheet"]}
        return [{"ref": f"{self.run_id}:worksheet",
                 "sha256": sha256_hex(canonical(artefacts))}], artefacts

    def op_t09_state_decision_check(self, key, step, raw, state,
                                    attempt):
        m = re.search(r"DECISION:\s*(CLOSE|REJECT)", raw)
        stated = m.group(1) if m else None
        mechanical = state["t09_worksheet"].get("decision")
        if stated == mechanical:
            return {"compared": {"stated": stated,
                                 "worksheet": mechanical},
                    "passed": True,
                    "outputs": {"decision": mechanical}}
        self.record.emit("GOVERNANCE_EVENT", {
            "kind": "DECISION_STANDS",
            "worksheet_decision": mechanical,
            "stated_decision": stated,
            "consequence": "the worksheet stands as the system "
                           "decision; the mismatch is recorded "
                           "as a subject error"},
            tree_id=key, step_id=step["step_id"],
            recorded_at_utc=utc_now())
        return {"compared": {"stated": stated,
                             "worksheet": mechanical},
                "passed": False,
                "failure_class": "GOVERNANCE_FAILURE",
                "outputs": {"decision": mechanical}}

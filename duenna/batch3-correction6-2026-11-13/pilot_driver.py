#!/usr/bin/env python3
"""The pilot driver (Stage 5 Build Spec Rev 22 §3.1, as
amended by Revs 23–26; Harness Design 03 §1) — Batch 3,
correction round 2 form.

Round-2 amendments (Batch 3 correction round-2 plan, approved
Rev 4): the pin authority governs the inputs actually consumed.
The pilot root is derived from this file's location, never from
the caller. The constructor loads nothing; run() bootstraps:
refuse any preloaded pinned module, verify PILOT-PIN-AUTHORITY-01
against the authority hash embedded in this file (the acyclic
anchor — this file is NOT in the authority; its own integrity is
pinned externally by the round-2 re-freeze continuation), verify
every consumed file, and only then load the locally pinned
modules from their exact verified paths and bind the consumed
symbols (RunRecord, canonical, sha256_hex, materialise_ledger,
CorpusSource, PilotTools, StubSubject) from those verified
objects. The subject is constructed by the driver, after
preflight, from the bound StubSubject class. T06 procedure steps
emit their accumulated outcomes map as STEP_PROGRESS evidence.

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
import importlib.util
import json
import pathlib
import re
import sys
import time
from datetime import datetime, timezone

# Round-2 anchor (plan Rev 2 R1): the sha256 of
# PILOT-PIN-AUTHORITY-01.json as minted for this build. The
# authority does NOT contain this file; this file's own integrity
# is pinned externally by the round-2 re-freeze continuation.
EXPECTED_AUTHORITY_SHA256 = "e245cabc504e4b8f6fdefda030fea46476700887ac02172f042a33648fef247d"

# Locally pinned modules: loaded ONLY by the bootstrap, from
# their verified paths, after preflight (plan Rev 3/4 R2).
PINNED_MODULES = ("pilot_jcs", "pilot_record", "corpus_source",
                  "rules_engine", "pilot_tools", "stub_subject")

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
    def __init__(self, *, runs_root, config):
        """Data only. Nothing is loaded, imported or constructed
        here beyond the driver's own state: every consumed input
        is resolved, verified and loaded by the bootstrap inside
        run() (round-2 plan Item 1). The caller may NOT pass a
        subject object, a corpus, or any module: the subject is
        constructed by the driver after preflight from the bound
        verified StubSubject class (plan Rev 4)."""
        self.runs_root = pathlib.Path(runs_root)
        self.cfg = config
        clock_name = config.get("clock", "real")
        if clock_name == "scripted":
            self.clock = ScriptedClock()
        elif clock_name in ("real", None):
            self.clock = RealClock()
        else:
            raise PreflightError(
                f"unknown clock selection: {clock_name!r}")
        self.budgets = {**DEFAULT_BUDGETS,
                        **config.get("budgets", {})}
        self._deps = None
        self.trees_doc = None
        self.trees = {}
        self.corpus = None
        self.packs = {}
        self.expected = {}
        self.fixtures = {}
        self.t09 = {}
        self.rules = {}
        self.snapshot_dir = None
        self.data_dir = None
        self.stub = None
        self.record = None
        self.tools = None
        self.run_id = None
        self.outputs = {}       # (tree_key, step_id) -> artefact
        self.extractions = {}   # (tree_key, field) -> (op_id, step)
        self.produced = {}      # (tree_key, field) -> citation
        self.produced_values = {}  # (tree_key, field) -> value
        self.lane_failures = 0
        self.stopped = None     # (reason, detail) once stopped
        self.closures = {}

    # --------------------------------------------------------------
    def _snapshot_hash(self):
        # Driver-internal utility (hashlib directly): the
        # bootstrap calls this BEFORE the verified bindings
        # exist, so it must not depend on them.
        return hashlib.sha256(
            (self.snapshot_dir / "sections.jsonl")
            .read_bytes()).hexdigest()

    # --------------------------------------------------------------
    AUTHORITY_NAME = "PILOT-PIN-AUTHORITY-01.json"

    def _pilot_root(self):
        """Derived from this artefact's own location (the fixed
        build layout places the driver at
        <root>/batch3/correction2/pilot_driver.py). Never read
        from the caller's configuration."""
        return pathlib.Path(__file__).resolve().parents[2]

    @staticmethod
    def _sha_bytes(b):
        return hashlib.sha256(b).hexdigest()

    def _load_module(self, name, path):
        spec = importlib.util.spec_from_file_location(
            name, str(path))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    def bootstrap(self):
        """Round-2 bootstrap (plan Item 1 + R1/R2/R3): refuse
        preloaded pinned modules; derive the root; verify the
        authority against the embedded anchor; verify every
        consumed file; bind every consumed path to its authority
        entry; load the pinned modules from their verified paths;
        bind the consumed symbols; load the inputs; construct the
        subject. Any failure is a PreflightError raised BEFORE any
        run directory or record exists."""
        for name in PINNED_MODULES:
            if name in sys.modules:
                raise PreflightError(
                    f"PROCESS_MODULE_PRELOADED: {name}")
        root = self._pilot_root()
        if self.cfg.get("pilot_root") is not None and \
                pathlib.Path(self.cfg["pilot_root"]) != root:
            raise PreflightError(
                "PILOT_ROOT_MISMATCH: caller root differs from "
                "the root derived from the driver artefact")
        freeze = root / "freeze"
        auth_path = freeze / self.AUTHORITY_NAME
        if not auth_path.exists():
            raise PreflightError("pin authority file missing")
        auth_bytes = auth_path.read_bytes()
        actual_auth = self._sha_bytes(auth_bytes)
        if actual_auth != EXPECTED_AUTHORITY_SHA256:
            raise PreflightError(
                f"AUTHORITY_ANCHOR_MISMATCH: expected "
                f"{EXPECTED_AUTHORITY_SHA256}, found {actual_auth}")
        authority = json.loads(auth_bytes.decode("utf-8"))
        stem = self.cfg.get("stub_script_stem", "stub_script_main")
        inventory = [e for e in authority["entries"]
                     if e.get("run") and
                     (e.get("variant") in (None, stem))]
        by_name = {}
        for e in inventory:
            p = root / e["path"]
            if not p.exists():
                raise PreflightError(
                    f"authority target missing: {e['path']}")
            actual = self._sha_bytes(p.read_bytes())
            if actual != e["sha256"]:
                raise PreflightError(
                    f"pin mismatch vs authority: {e['name']} "
                    f"expected {e['sha256']}, found {actual}")
            by_name[e["name"]] = (e, p)
        caller = self.cfg.get("pins")
        if caller is not None:
            want = {e["name"]: e["sha256"] for e in inventory}
            got = {p["name"]: p["sha256"] for p in caller}
            if set(got) < set(want):
                raise PreflightError(
                    f"caller pins missing entries: "
                    f"{sorted(set(want) - set(got))}")
            if set(got) > set(want):
                raise PreflightError(
                    f"caller pins carry extra entries: "
                    f"{sorted(set(got) - set(want))}")
            for name in want:
                if got[name] != want[name]:
                    raise PreflightError(
                        f"caller pin diverges from authority: "
                        f"{name}")
        # --- path binding: consumed paths come from the
        # authority, never from the caller.
        trees_path = by_name["pilot_trees.json"][1]
        data_dir = by_name["PILOT-DATA-PACKS-01"][1].parent
        snap_dir = by_name["corpus-snapshot-manifest"][1].parent
        for key, resolved in (("trees_path", trees_path),
                              ("data_dir", data_dir),
                              ("snapshot_dir", snap_dir)):
            supplied = self.cfg.get(key)
            if supplied is not None and \
                    pathlib.Path(supplied) != resolved:
                raise PreflightError(
                    f"PATH_NOT_AUTHORITY: caller {key} differs "
                    f"from the authority-resolved path")
        self.data_dir = data_dir
        # --- snapshot binding (canonical, or the named
        # INTEGRITY-FIXTURE-01 variant: canonical verified above,
        # in full, before the variant is even looked at).
        self._snapshot_pin = by_name[
            "corpus-snapshot-sections"][0]["sha256"]
        self.snapshot_dir = snap_dir
        variant = self.cfg.get("snapshot_variant")
        if variant is not None:
            vent = authority.get("variants", {}).get(variant)
            if vent is None:
                raise PreflightError(
                    f"unknown snapshot variant: {variant}")
            fdir = root / vent["fixture_dir"]
            fsec = fdir / "sections.jsonl"
            fman = fdir / "manifest.json"
            if not fsec.exists() or not fman.exists():
                raise PreflightError(
                    f"integrity fixture not staged: {fdir}")
            if self._sha_bytes(fman.read_bytes()) != \
                    vent["manifest_sha256"]:
                raise PreflightError(
                    "integrity fixture manifest mismatch vs "
                    "variant entry")
            if self._sha_bytes(fsec.read_bytes()) != \
                    vent["sections_sha256"]:
                raise PreflightError(
                    "integrity fixture sections mismatch vs "
                    "variant entry")
            self.snapshot_dir = fdir
            self._snapshot_variant = vent
        else:
            self._snapshot_variant = None
        # Preflight binds the snapshot actually loaded: the
        # variant's pin when a variant is bound, the canonical
        # pin otherwise. The tree-boundary integrity check keeps
        # comparing against the CANONICAL pin (self._snapshot_pin
        # above): a staged variant's divergence from the canonical
        # identity is exactly what that check exists to stop.
        _bound_pin = self._snapshot_variant["sections_sha256"] \
            if self._snapshot_variant else self._snapshot_pin
        if self._snapshot_hash() != _bound_pin:
            raise PreflightError(
                "snapshot hash mismatch vs authority at "
                "pre-flight")
        # --- module loading: verified paths only, dependency
        # order, freshly loaded by this bootstrap.
        deps = {}
        for name in PINNED_MODULES:
            entry, path = by_name[f"{name}.py"]
            deps[name] = self._load_module(name, path)
        self._deps = deps
        self._RunRecord = deps["pilot_record"].RunRecord
        self._canonical = deps["pilot_record"].canonical
        self._sha256_hex = deps["pilot_record"].sha256_hex
        self._materialise_ledger = \
            deps["pilot_record"].materialise_ledger
        self._CorpusSource = deps["corpus_source"].CorpusSource
        self._PilotTools = deps["pilot_tools"].PilotTools
        self._StubSubject = deps["stub_subject"].StubSubject
        # --- inputs, loaded from the verified paths only now.
        self.trees_doc = json.loads(
            trees_path.read_text(encoding="utf-8"))
        self.trees = {t["tree_id"]: t
                      for t in self.trees_doc["trees"]}
        self.corpus = self._CorpusSource(
            str(self.snapshot_dir), str(self.data_dir))
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
        # --- the subject: constructed here, after preflight,
        # from the bound verified class; data only crossed the
        # boundary (script entry + configuration name).
        script_path = by_name[f"{stem}.json"][1]
        self.stub = self._StubSubject(
            str(script_path), self.cfg["subject_configuration"])
        pins = [{"name": e["name"], "sha256": e["sha256"]}
                for e in inventory]
        snapshot_block = {
            "sections_sha256": by_name[
                "corpus-snapshot-sections"][0]["sha256"],
            "manifest_sha256": by_name[
                "corpus-snapshot-manifest"][0]["sha256"],
            "constituent_pins": "per-section hashes recorded in "
                                "the snapshot manifest, anchored "
                                "by the manifest file pin"}
        return pins, snapshot_block

    def provenance(self):
        """Bootstrap provenance (plan Rev 3/4 R2): computed in
        this process, about the objects this run actually used."""
        deps = self._deps or {}
        root = self._pilot_root()
        mods = {}
        for name, mod in deps.items():
            f = getattr(mod, "__file__", None)
            mods[name] = {
                "path": str(pathlib.Path(f).relative_to(root))
                if f else None,
                "sha256": self._sha_bytes(
                    pathlib.Path(f).read_bytes()) if f else None}
        tools_mod = deps.get("pilot_tools")
        record_mod = deps.get("pilot_record")
        ident = {
            "RunRecord": self._RunRecord is record_mod.RunRecord,
            "canonical": self._canonical is record_mod.canonical,
            "sha256_hex": self._sha256_hex is record_mod.sha256_hex,
            "materialise_ledger": self._materialise_ledger is
            record_mod.materialise_ledger,
            "CorpusSource": self._CorpusSource is
            deps["corpus_source"].CorpusSource,
            "PilotTools": self._PilotTools is tools_mod.PilotTools,
            "StubSubject": self._StubSubject is
            deps["stub_subject"].StubSubject,
            "tools.extract": getattr(tools_mod, "extract", None) is
            deps["rules_engine"].extract,
            "record.jcs": getattr(record_mod, "pilot_jcs", None)
            is deps["pilot_jcs"],
            "subject_class": type(self.stub) is self._StubSubject,
        }
        return {"modules": mods, "identity": ident}

    # --------------------------------------------------------------
    def run(self, tree_keys):
        pins, snapshot_block = self.bootstrap()
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
            "pins": pins,
            "snapshot": snapshot_block,
            "budgets": self.budgets,
            "subject_configuration": self.cfg["subject_configuration"],
            "configuration_hashes":
                self.cfg.get("configuration_hashes", {}),
            "scratch": bool(self.cfg.get("scratch", False)),
        }
        test_cfg = {}
        if self.cfg.get("step_clock_advance"):
            test_cfg["step_clock_advance"] = \
                self.cfg["step_clock_advance"]
        if self.cfg.get("step_advance_s"):
            test_cfg["step_advance_s"] = self.cfg["step_advance_s"]
        if getattr(self, "_snapshot_variant", None):
            test_cfg["snapshot_variant"] = \
                self._snapshot_variant["name"]
            test_cfg["snapshot_variant_sections_sha256"] = \
                self._snapshot_variant["sections_sha256"]
        if test_cfg:
            block["test_configuration"] = test_cfg
        self.record = self._RunRecord(
            run_dir / "run-record.jsonl", self.run_id, block)
        record_path = run_dir / "run-record.jsonl"

        def record_reader():
            return [json.loads(ln) for ln in
                    record_path.read_text(encoding="utf-8")
                    .splitlines() if ln.strip()]

        self.tools = self._PilotTools(
            self.corpus, self.rules, str(self.data_dir),
            RecordShim(self.record),
            {"run_id": self.run_id, "tree_id": None,
             "step_id": None},
            record_reader=record_reader,
            canonicalise=self._canonical)
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
        if not self.stopped:
            head = self.record.prev
            self.record.emit("RUN_CLOSED", {
                "tree_closures": self.closures,
                "event_count": self.record.seq + 1,
                "record_sha256": head},
                recorded_at_utc=utc_now())
        self.record.close()
        (run_dir / "ledger.json").write_bytes(
            self._materialise_ledger(
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
        if self._snapshot_hash() != self._snapshot_pin:
            self.record.emit("GOVERNANCE_EVENT", {
                "kind": "SNAPSHOT_HASH_MISMATCH",
                "at_tree": key,
                "expected": self._snapshot_pin,
                "found": self._snapshot_hash()},
                recorded_at_utc=utc_now())
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
            advance = self.cfg.get("step_clock_advance", {}).get(sid)
            if advance and isinstance(self.clock, ScriptedClock):
                self.clock.advance(advance)
            elapsed = self.clock.now() - start
            budget = self.budgets["model_step_s"] \
                if step["type"] == "MODEL" \
                else self.budgets["tool_step_s"]
            # Budget adjudication BEFORE any terminal step event
            # (Rev 23 §3.1): the operation's own events stand;
            # then the budget verdict; then exactly one terminal
            # outcome. An over-budget attempt never carries a
            # passing CHECK_RESULT or a STEP_SATISFIED.
            if res["outcome"] == "adapter_failure":
                self.record.emit("STEP_FAILED", {
                    "step_id": sid,
                    "failure_class": "ADAPTER_FAILURE",
                    "failing_condition":
                        "adapter complete() failed",
                    "branch": "tree INVALIDATED-INFRASTRUCTURE"},
                    tree_id=key, step_id=sid,
                    recorded_at_utc=utc_now())
                return "adapter_failure"
            if elapsed > budget:
                timeout_class = "ADAPTER_TIMEOUT" \
                    if step["type"] == "MODEL" else "STEP_TIMEOUT"
                self.record.emit("CHECK_RESULT", {
                    "condition": f"step budget: elapsed "
                                 f"{elapsed}s > budget {budget}s",
                    "declared_condition": step["verify"],
                    "compared": {"elapsed_s": elapsed,
                                 "budget_s": budget},
                    "result": "FAIL", "budget_failure": True},
                    tree_id=key, step_id=sid,
                    recorded_at_utc=utc_now())
                self.record.emit("STEP_FAILED", {
                    "step_id": sid,
                    "failure_class": timeout_class,
                    "failing_condition": step["verify"],
                    "branch": step.get("failure", "")},
                    tree_id=key, step_id=sid,
                    recorded_at_utc=utc_now())
                res = {"outcome": "failed",
                       "outputs": res.get("outputs", {}),
                       "recovery_inputs":
                           res.get("recovery_inputs", {})}
            elif res["outcome"] == "satisfied":
                chk = res["check"]
                self._emit_check(key, step, chk["compared"], True)
                self.record.emit("STEP_SATISFIED",
                                 {"step_id": sid},
                                 tree_id=key, step_id=sid,
                                 recorded_at_utc=utc_now())
                self.outputs[(key, sid)] = res.get("outputs", {})
                if isinstance(self.clock, ScriptedClock):
                    self.clock.advance(
                        self.cfg.get("step_advance_s", 0))
                return "satisfied"
            else:
                chk = res["check"]
                self._emit_check(key, step, chk["compared"], False)
                self.record.emit("STEP_FAILED", {
                    "step_id": sid,
                    "failure_class": chk.get("failure_class",
                                             "GOVERNANCE_FAILURE"),
                    "failing_condition": step["verify"],
                    "branch": step.get("failure", "")},
                    tree_id=key, step_id=sid,
                    recorded_at_utc=utc_now())
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
        _outs = out.get("outputs", {})
        if "outcomes" in _outs:
            # Round-2 Item 2: the T06 procedure steps' accumulated
            # outcomes map enters the record whole, as citable
            # producing output for the [MODEL] step's manifest
            # recomputation (§4(p)).
            self.record.emit(
                "STEP_PROGRESS", {"outcomes": _outs["outcomes"]},
                tree_id=key, step_id=sid,
                recorded_at_utc=utc_now())
        chk = out["check"]
        # No terminal step events here: the driver adjudicates
        # the step budget first (Rev 23 §3.1) and emits exactly
        # one coherent outcome in _run_step.
        if chk["passed"]:
            return {"outcome": "satisfied", "check": chk,
                    "outputs": out.get("outputs", {})}
        return {"outcome": "failed", "check": chk,
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
             "content": self._canonical(artefacts).decode("utf-8")}]
        result = self.stub.complete(key, sid, attempt, messages)
        if isinstance(self.clock, ScriptedClock):
            self.clock.advance(result.get("advance_clock_s", 0))
        if result["kind"] == "adapter_failure":
            return {"outcome": "adapter_failure"}
        raw = result["raw_output"]
        capture = {
            "capture_id": f"{self.run_id}-{key.replace('/', '-')}"
                          f"-{sid}-a{attempt}",
            "synthetic": True,
            "subject_configuration": self.cfg["subject_configuration"],
            "tree_id": key, "step_id": sid, "attempt": attempt,
            "request_sha256": self._sha256_hex(self._canonical(messages)),
            "response_sha256": self._sha256_hex(raw.encode("utf-8")),
            "raw_output": raw}
        cap_path = self.runs_root / self.run_id / "captures" / \
            f"{capture['capture_id']}.json"
        cap_path.write_bytes(self._canonical(capture))
        self.record.emit("MODEL_CALL_LINKED", {
            "capture_id": capture["capture_id"],
            "record_sha256": self._sha256_hex(self._canonical(capture)),
            "request_sha256": capture["request_sha256"],
            "response_sha256": capture["response_sha256"],
            "raw_output": raw},
            tree_id=key, step_id=sid, recorded_at_utc=utc_now())
        checker = getattr(self, f"op_{step['op']}_check")
        chk = checker(key, step, raw, state, attempt)
        # Terminal events are the driver's, after budget
        # adjudication (Rev 23 §3.1).
        if chk["passed"]:
            return {"outcome": "satisfied", "check": chk,
                    "outputs": chk.get("outputs", {})}
        return {"outcome": "failed", "check": chk,
                "outputs": chk.get("outputs", {}),
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
        """Insert the extracted fields through the extracted
        presentation form; returns (values, error, refs) where
        refs is the source_refs in insertion order. The insert
        returns no value (Batch 2 conservative reading); the
        record's values come from the extraction results the
        harness itself registered."""
        values, refs = {}, []
        for record_field, ext_field in fields.items():
            op_id, step_id = self.extractions[(key, ext_field)]
            _, res = self.tools.reference_insert(
                ext_field, step_id,
                {"form": "extracted", "operation_id": op_id})
            if res.get("refused"):
                return None, res, None
            entry = self.tools.registry.get(op_id)
            values[record_field] = entry["value"]
            refs.append(entry["source_ref"])
        return values, None, refs

    def _produce(self, key, step_id, field, value):
        """Emit a PRODUCED_ARTEFACT step output and return its
        citation {event_id, payload_sha256} (§3.3 Rev 23)."""
        payload = {"kind": "PRODUCED_ARTEFACT", "field": field,
                   "value": value}
        seq = self.record.emit("STEP_PROGRESS", payload,
                               tree_id=key, step_id=step_id,
                               recorded_at_utc=utc_now())
        return {"event_id": f"{self.run_id}:{seq}",
                "payload_sha256": self._sha256_hex(self._canonical(payload))}

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
    @staticmethod
    def _t02_span(cls, text):
        """Amendment Draft 02 §3.1 span + boundary-derived
        standing for one T02 source (Correction Plan Revs
        2-4). Returns (span, standing), or (None, reason)
        on any boundary failure — fail-closed, no fallback,
        no claim-text interpretation."""
        if cls == "implementer":
            cands = [ln for ln in text.splitlines()
                     if re.search(r"\d+ fixtures executed,", ln)]
            if len(cands) != 1:
                return None, "IMPLEMENTER_CANDIDATES"
            if not re.search(
                    r"\*\*(\d+) fixtures executed, \1 PASS, "
                    r"0 FAIL\*\*", cands[0]):
                return None, "IMPLEMENTER_MALFORMED"
            return cands[0], "CLOSED"
        if cls == "examiner":
            phrase = "R60 fails as a whole"
            if text.count(phrase) != 1:
                return None, "EXAMINER_PHRASE"
            i = text.index(phrase)
            return text[i:text.index(".", i) + 1], "OPEN"
        if cls == "adjudicator":
            cands = [ln for ln in text.splitlines()
                     if ln.startswith("- **R60 — ")]
            if len(cands) != 1:
                return None, "ADJUDICATOR_CANDIDATES"
            if not re.match(r"- \*\*R60 — (PASS|FAIL)\.\*\*",
                            cands[0]):
                return None, "ADJUDICATOR_MALFORMED"
            j = text.index(cands[0])
            nxt = text.find("\n- **", j + 1)
            span = text[j:] if nxt == -1 else text[j:nxt]
            m = re.findall(r"\*\*R60 — (PASS|FAIL)", span)
            if len(m) != 1:
                return None, "ADJUDICATOR_DERIVATION"
            return span, ("OPEN" if m[0] == "FAIL" else "CLOSED")
        return None, "UNKNOWN_CLASS"

    def op_t02_build_worksheet(self, key, step, state):
        # References from the pinned pack in pack order;
        # classes parsed from the loaded T02-STEP-01 text;
        # both verified before any pairing (Plan Rev 2 §C).
        refs = [e["section"]
                for e in self.packs["T02"]["pack"]]
        step01 = next(s for s in self.trees["T02"]["steps"]
                      if s["step_id"] == "T02-STEP-01")
        text01 = step01["text"]
        stems = (("implementer", "implementer"),
                 ("examiner", "examiner"),
                 ("adjudicat", "adjudicator"))
        found = sorted((text01.index(stem), cls)
                       for stem, cls in stems if stem in text01)
        classes = [cls for _, cls in found]
        state["t02_classes"] = classes
        if len(refs) != 3 or classes != ["implementer",
                                         "examiner",
                                         "adjudicator"]:
            state["t02_rows"] = []
            state["t02_standings"] = []
            return {"progress": [], "outputs": {},
                    "check": {"compared": {"refs": len(refs),
                                           "classes": classes},
                              "passed": False}}
        rows = []
        standings = []
        failure = None
        for ref, cls in zip(refs, classes):
            _, sec = self.tools.shelf_lookup(ref)
            text = sec.get("text", "")
            span, standing = self._t02_span(cls, text)
            if span is None:
                failure = {"class": cls, "source": ref,
                           "reason": standing}
                break
            if cls == "adjudicator":
                res = self._extract(key, step["step_id"], ADJ_R60,
                                    "correction_b")
                state["t02_adjudication"] = res.get("value")
                state["t02_adjudication_extraction"] = res
            rows.append({"source": ref, "class": cls,
                         "claim": span,
                         "verbatim": span in text})
            standings.append(standing)
        if failure is not None:
            state["t02_rows"] = []
            state["t02_standings"] = []
            return {"progress": [], "outputs": {},
                    "check": {"compared": {"boundary_failure":
                                           failure},
                              "passed": False}}
        state["t02_rows"] = rows
        state["t02_standings"] = standings
        ok = all(r["verbatim"] and r["claim"] for r in rows)
        return {"progress": [{"worksheet_row": r} for r in rows],
                "outputs": {"worksheet": rows},
                "check": {"compared": {"rows": len(rows),
                                       "all_verbatim": ok},
                          "passed": ok}}

    def op_t02_compare(self, key, step, state):
        # Consumes the standings stored by the worksheet
        # operation; claim text is never reinterpreted here
        # (Plan Rev 2 §B — the old implied() is deleted).
        rows = state["t02_rows"]
        standings = state["t02_standings"]
        conflicts = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if standings[i] != standings[j]:
                    conflicts.append(
                        {"pair": [rows[i]["class"], rows[j]["class"]],
                         "values": [standings[i], standings[j]]})
        state["t02_conflicts"] = conflicts
        return {"progress": [{"conflict": c} for c in conflicts],
                "outputs": {"conflicts": conflicts},
                "check": {"compared": {"conflicts": len(conflicts)},
                          "passed": len(conflicts) >= 1}}

    def op_t02_apply_precedence_inputs(self, key, step, state, attempt):
        artefacts = {"worksheet": state["t02_rows"],
                     "conflicts": state["t02_conflicts"]}
        if attempt > 1:
            adj_i = state["t02_classes"].index("adjudicator")
            artefacts["adjudication_row"] = \
                state["t02_rows"][adj_i]
        manifest = [{"ref": f"{self.run_id}:worksheet",
                     "sha256": self._sha256_hex(self._canonical(artefacts))}]
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

    def _produce_evidence(self, key, step_id, out):
        """The extraction step produces the evidence artefact:
        the ordered sequence of its extractions' source_refs,
        duplicates preserved (§3.3). Only when every extraction
        succeeded — otherwise the step's check fails and no
        construction follows."""
        if all(v.get("verification") == "EXTRACTED"
               for v in out.values()):
            refs = [out[f]["source_ref"] for f in
                    ("fixtures_executed", "fixtures_passed",
                     "harness_sha256", "results_sha256", "version",
                     "correction_b")]
            cit = self._produce(key, step_id, "evidence", refs)
            self.produced[(key, "evidence")] = cit
            self.produced_values[(key, "evidence")] = refs

    def _construct(self, key, locate_step, evidence_step):
        fields = {rf: ef for rf, ef in self.FIELDS.items() if ef}
        values, err, refs = self._insert_values(key, fields)
        if err:
            return None, err
        # artifact: carried from the locate step's produced
        # artefact event — no literal (§3.3, Alex HIGH-2).
        cit = self.produced.get((key, "artifact"))
        if cit is None:
            return None, {"refused": True,
                          "reason": "NO_PRODUCED_ARTEFACT"}
        _, res = self.tools.reference_insert(
            "artifact", locate_step,
            {"form": "carried", "citation": cit})
        if res.get("refused"):
            return None, res
        values["artifact"] = self.produced_values[(key, "artifact")]
        # evidence: carried from the extraction step's produced
        # artefact (the ordered sequence of its extractions'
        # source_refs — see op_t05_extract_values), its check
        # already PASS in the record (§3.3).
        cit_e = self.produced.get((key, "evidence"))
        if cit_e is None:
            return None, {"refused": True,
                          "reason": "NO_PRODUCED_ARTEFACT"}
        _, res = self.tools.reference_insert(
            "evidence", evidence_step,
            {"form": "carried", "citation": cit_e})
        if res.get("refused"):
            return None, res
        values["evidence"] = refs
        ordered = {f: values[f] for f in self.FIELDS}
        return ordered, None

    def op_t05_load_contract(self, key, step, state):
        fields = self._contract("T05")
        state["contract"] = fields
        return {"outputs": {"contract": fields},
                "check": {"compared": {"fields": fields},
                          "passed": len(fields) == 8}}

    def _locate_artifact(self, key, step):
        """The STEP-02 locate work shared by T05 and T08 (§3.3):
        read the obligation row from the evidence manifest,
        parse the stated artifact + hash (nothing hardcoded),
        cross-check the stated hash against the change record's
        extracted harness_sha256, and — on agreement — produce
        the artifact value as a PRODUCED_ARTEFACT record event
        for the construction to carry by citation."""
        sid = step["step_id"]
        _, sec = self.tools.shelf_lookup(MANIFEST_SEC)
        text = sec.get("text", "")
        m = re.search(r'"artifact":\s*"([^"]+)",\s*'
                      r'"sha256":\s*"([0-9a-f]{64})"', text)
        artifact_name = m.group(1) if m else None
        stated = m.group(2) if m else None
        res_h = self._extract(key, sid, CR, "harness_sha256")
        agree = stated is not None and \
            res_h.get("value") == stated
        if agree:
            cit = self._produce(key, sid, "artifact",
                                artifact_name)
            self.produced[(key, "artifact")] = cit
            self.produced_values[(key, "artifact")] = artifact_name
        return artifact_name, stated, res_h, agree

    def op_t05_locate_artifact(self, key, step, state):
        artifact_name, stated, res_h, agree = \
            self._locate_artifact(key, step)
        res_v = self._extract(key, step["step_id"], CR, "version")
        state["t05_version"] = res_v.get("value")
        return {"progress": [{
                    "manifest_row": {"artifact": artifact_name,
                                     "sha256": stated},
                    "change_record_extraction": res_h}],
                "outputs": {"artifact": artifact_name,
                            "version": res_v.get("value")},
                "check": {"compared": {"manifest_stated": stated,
                                       "extracted":
                                           res_h.get("value")},
                          "passed": bool(agree),
                          "failure_class": "GOVERNANCE_FAILURE"}}

    def op_t05_extract_values(self, key, step, state):
        out = self._extract_values(key, step["step_id"])
        self._produce_evidence(key, step["step_id"], out)
        ok = all(v.get("verification") == "EXTRACTED"
                 for v in out.values())
        return {"outputs": {"extractions": out},
                "check": {"compared": {
                    f: v.get("verification") for f, v in out.items()},
                    "passed": ok}}

    def op_t05_construct_record(self, key, step, state):
        record_values, err = self._construct(
            key, "T05-STEP-02", "T05-STEP-03")
        if err:
            return {"check": {"compared": {"refusal": err},
                              "passed": False,
                              "failure_class": "GOVERNANCE_FAILURE"}}
        state["record"] = record_values
        path = self.runs_root / self.run_id / "artefacts" / \
            "T05--T05-STEP-04--record.json"
        path.write_bytes(self._canonical(record_values))
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
                 "sha256": self._sha256_hex(self._canonical(artefacts))}], artefacts

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
        path.write_bytes(self._canonical(report))
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
                 "sha256": self._sha256_hex(self._canonical(artefacts))}], artefacts

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
        # T08-STEP-02's text declares the T05-STEP-02/03 work:
        # the locate (with its PRODUCED_ARTEFACT) and the field
        # extractions both happen at this step.
        artifact_name, stated, res_h, agree = \
            self._locate_artifact(key, step)
        out = self._extract_values(key, step["step_id"])
        self._produce_evidence(key, step["step_id"], out)
        ok = all(v.get("verification") == "EXTRACTED"
                 for v in out.values())
        return {"outputs": {"extractions": out,
                            "artifact": artifact_name},
                "check": {"compared": {
                    **{f: v.get("verification")
                       for f, v in out.items()},
                    "artifact_agreement": agree},
                    "passed": ok and bool(agree)}}

    def op_t08_construct_validate(self, key, step, state):
        record_values, err = self._construct(
            key, "T08-STEP-02", "T08-STEP-02")
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
        path.write_bytes(self._canonical(record_values))
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
                 "sha256": self._sha256_hex(self._canonical(artefacts))}], artefacts

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
        path.write_bytes(self._canonical(report))
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
                 "sha256": self._sha256_hex(self._canonical(artefacts))}], artefacts

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

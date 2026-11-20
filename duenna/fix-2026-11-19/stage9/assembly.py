"""Stage 9 — the assembly: RECORD + BINDER + EVALUATOR + EXAMINER
SURFACE, composed from Stages 1–8 into the re-runnable battery.

  RECORD            Stage 1's EventRecord + ClosureWriter +
                    validator (one hash-chained record per run).
  BINDER            Stage 3's Binder / CaptureGate / OutputGate /
                    ConfigAccess over a FrozenConfig whose values
                    are the frozen STEP6 programme's parameters.
  EVALUATOR         engine.py + ops9.py + tools9.py: the STEP6
                    step engine and tool semantics, with Stage 5
                    operations, Stage 2 provenance/construction,
                    Stage 6 attribution, Stage 7 receipts.
  EXAMINER SURFACE  rederive.py: independent re-derivation from
                    the preserved record + frozen sources; the
                    Stage 4 checker contract issues the run's
                    adjudication only where the examiner's
                    re-derived settlement agrees byte-for-byte.

The subject, endpoint, envelope, ceilings, budgets and bar are
the frozen STEP6 programme's, read from the record (Alex's pin
ruling 2026-11-17; the first battery adjudication §4; the pinned
adapter stack) — nothing is substituted, nothing is tuned.
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
import scoring                                    # noqa: E402
from record import EventRecord                    # noqa: E402
from closure import make_failure                  # noqa: E402
from validator import validate_record             # noqa: E402
from schema import freeze_schema                  # noqa: E402
from binder import Binder, FreezeRefused          # noqa: E402
from access import ConfigAccess                   # noqa: E402
from admission import CaptureGate                 # noqa: E402
from operations import build_inputs               # noqa: E402,F401
from receiver import Receiver                     # noqa: E402
from construction import ProvenanceLog, ArtefactConstructor  # noqa: E402
from authority import issue_authority, make_test_authority_record  # noqa: E402
from attribution import AttributionLedger, closure_view  # noqa: E402
from discrepancy import mint_discrepancy          # noqa: E402
from receipts import (ReceiptIssuer, IssuerStore, issue_receipt,  # noqa: E402
                      collect_receipt, receipt_account,
                      close_with_receipt_account)
from trust_anchor import (TEST_ISSUER_ID, TEST_KEY, TEST_TERMS,  # noqa: E402
                          make_test_anchor)
from package import ResultPackage                 # noqa: E402
from contract import make_checker_system, PROCEDURE_IDENTITY  # noqa: E402
from corpus_source import CorpusSource            # noqa: E402
from tools9 import ToolLayer, canonical, sha256_hex  # noqa: E402
from engine import Engine                         # noqa: E402

SUBJECT = "openai/gpt-oss-20b"
ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
ENDPOINT_CLASS = "nvidia-nim-openai-compatible"

ALL_INSTANCES = ["T01", "T02", "T03", "T04", "T05", "T06", "T07",
                 "T08", "T09", "T09/FR-A", "T09/FR-B", "T09/FR-C",
                 "T09/FR-VALID"]

RECORD_ARTEFACT_FIELDS = ("artifact", "version", "fixtures_total",
                          "fixtures_passed", "harness_sha256",
                          "results_sha256", "correction_b",
                          "evidence")
RECORD_RESPONSE_FIELDS = (
    "STATUS: <OPEN|CLOSED>",
    "DECISION: <CLOSE|REJECT>",
    "S1..S4 classification labels (NOT ESTABLISHED / SUPPORTED / "
    "UNTRACEABLE / CONTRADICTED)",
    "verbatim 64-hex harness and results hashes",
    "OB-n: <OPEN|CLOSED> status lines",
    "NON-AUTHORITATIVE quarantine label",
    "ESCALATE dispositions (no performed-action claims)",
)
SETTLEMENT_FIELDS = ("run_id", "verdicts", "counts", "bar_criteria",
                     "bar_passed")

# The frozen STEP6 pass bar (first battery adjudication, §4).
BAR = {
    "source": "ALEX-STAGE6-BATTERY-ADJUDICATION-2026-11-17 §4",
    "criteria": list(scoring.BAR_CRITERIA),
    "at_most_two_invalid": 2,
}

BUDGETS = {"tool_step_s": 60, "model_step_s": 300, "tree_s": 3600,
           "run_s": 14400}
CEILINGS = {"T01": 10240, "T02": 10240, "T03": 6144, "T04": 20480,
            "T05": 10240, "T06": 20480, "T07": 20480, "T08": 10240,
            "T09": 20480, "T09/FR-A": 20480, "T09/FR-B": 20480,
            "T09/FR-C": 20480, "T09/FR-VALID": 20480}


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_draft(record_schema, trees_doc, adapter_config):
    envelope = dict(adapter_config["envelope"])
    # The envelope is THIS RUN's transport template: its model
    # field names the run's subject, not the programme's pin.
    # The pinned adapter config's envelope carries the pin
    # because the pinned programme's subject WAS the pin; a run
    # frozen under a different subject (Ben's ruling, DR-27)
    # that copied the field verbatim would freeze a
    # configuration naming two subjects — the inconsistency
    # Vane's Stage 9 Gate 1 returned. Synchronize here, at
    # draft construction, so the FrozenConfig's digest — taken
    # over the whole draft at freeze — covers the synchronized
    # value. Under the unmodified pin this is a no-op: the
    # envelope is then exactly the pinned artefact's. (Removing
    # the field instead was rejected: the envelope's shape is
    # the pinned adapter's, consumers read the field, and an
    # absent field would leave the run's subject unstated on
    # the transport surface rather than stated once, correctly.)
    envelope["model"] = SUBJECT
    return {
        "subject_pin": SUBJECT,
        "subject_surfaces": {"driver": SUBJECT, "adapter": SUBJECT},
        "values": {
            "subject_model_id": SUBJECT,
            "endpoint": ENDPOINT,
            "endpoint_class": ENDPOINT_CLASS,
            "envelope": envelope,
            "retry": adapter_config["retry_policy"],
            "ceilings": CEILINGS,
            "budgets": BUDGETS,
            "transport_timeout_s":
                adapter_config["timeout_seconds_per_attempt"],
            "tree_set_digest": pins.TREE_SET_DIGEST,
            "snapshot_digest": pins.SNAPSHOT_DIGEST,
            "bar": BAR,
        },
        "derivations": {
            "transport_timeout_s": {
                "formula": "reasoning_envelope",
                "inputs": {"max_reasoning_tokens": 36864,
                           "min_throughput_tps": 64},
                "required": 576}},
        "policy": {"derived_limits": ["transport_timeout_s"]},
        "run_policy": {"on_subject_conflict": "INVALIDATE_RUN"},
        "tree_set": {
            "tree_id": "PILOT-TREES-SUBSET-01",
            "version": trees_doc["version"],
            "sha256": pins.TREE_SET_DIGEST,
            "snapshot_sha256": pins.SNAPSHOT_DIGEST,
            "instances": ALL_INSTANCES},
        "schema_digest": record_schema.digest,
    }


def _draft_subject_fields(draft):
    """Every field of the draft that names the run's subject.
    The binder's surface consistency check (DR-03) sees
    ``subject_pin`` and ``subject_surfaces``; the governed
    values name the subject twice more. All of them are the
    same fact and must hold the same value."""
    values = draft.get("values") or {}
    envelope = values.get("envelope") or {}
    fields = {
        "subject_pin": draft.get("subject_pin"),
        "values.subject_model_id": values.get("subject_model_id"),
        "values.envelope.model": envelope.get("model"),
    }
    for name, surface in (draft.get("subject_surfaces")
                          or {}).items():
        fields[f"subject_surfaces.{name}"] = surface
    return fields


def _draft_subject_problems(draft, transport):
    """Fail-closed subject consistency over the whole draft
    (Stage 9 Gate 1 correction 1). Returns a list of problems;
    empty means the draft names exactly one subject and it is
    the subject the transport lane will request and verify."""
    fields = _draft_subject_fields(draft)
    named = {v for v in fields.values() if v is not None}
    if len(named) != 1:
        return [{"kind": "draft_fields_disagree",
                 "fields": fields}]
    subject = next(iter(named))
    lane_subject = getattr(transport, "model_id", None)
    if lane_subject is not None and lane_subject != subject:
        return [{"kind": "lane_subject_mismatch",
                 "config_subject": subject,
                 "lane_subject": lane_subject,
                 "fields": fields}]
    return []


def _event_digest(events, seq):
    for ev in events:
        if ev["seq"] == seq:
            return ev["digest"]
    return None


def _collect_failure_specs(events, verdicts, tree_keys, stopped):
    """Derive the run's failure account from the record: one spec
    per failure, in a deterministic order, each with its basis
    event digests. Classes follow Stage 6's causal table as
    settled in the plan (governance/infrastructure/checker
    extraction = SYSTEM; subject content = MODEL)."""
    by_seq = {ev["seq"]: ev for ev in events}
    specs = []

    def digests(seqs):
        return [by_seq[s]["digest"] for s in seqs if s in by_seq]

    if stopped:
        stop_evs = [ev for ev in events
                    if ev.get("type") == "RUN_STOPPED"]
        if stop_evs:
            ev = stop_evs[-1]
            specs.append({
                "key": "RUN",
                "description": f"run stopped: {ev['body'].get('reason')}",
                "cls": "SYSTEM", "basis": [ev["digest"]]})
    for key in tree_keys:
        v = verdicts[key]
        verdict, basis = v["verdict"], v["basis"]
        if verdict == "PASS":
            continue
        iev = [ev for ev in events
               if isinstance(ev.get("body"), dict)
               and ev["body"].get("tree_id") == key]
        if verdict == "GOVERNANCE-FAIL":
            seqs = [g["seq"] for g in basis.get("governance_signals", [])
                    if "seq" in g]
            if not seqs:
                seqs = [ev["seq"] for ev in iev
                        if ev.get("type") == "TREE_CLOSED"]
            specs.append({
                "key": key,
                "description": f"{key}: governance failure "
                               f"({basis.get('closure')})",
                "cls": "SYSTEM", "basis": digests(seqs)})
        elif verdict == "SUBJECT-FAIL":
            seqs = [ev["seq"] for ev in iev
                    if ev.get("type") == "CHECK_RESULT"
                    and ev["body"].get("result") == "FAIL"]
            specs.append({
                "key": key,
                "description": f"{key}: subject-answer check failed "
                               f"on content",
                "cls": "MODEL", "basis": digests(seqs)})
        elif verdict == "INVALID":
            seqs = [ev["seq"] for ev in iev
                    if ev.get("type") == "STEP_FAILED"
                    and ev["body"].get("failure_class")
                    == "ADAPTER_FAILURE"]
            specs.append({
                "key": key,
                "description": f"{key}: adapter failure — instance "
                               f"invalidated (infrastructure)",
                "cls": "SYSTEM", "basis": digests(seqs)})
        elif verdict == "NOT-SCORED":
            mf = basis.get("model_failures") or []
            if mf:
                seqs = [ev["seq"] for ev in iev
                        if ev.get("type") == "CHECK_RESULT"
                        and ev["body"].get("result") == "FAIL"]
                specs.append({
                    "key": key,
                    "description": f"{key}: checker could not "
                                   f"extract the stated fact from "
                                   f"the response (NOT-SCORED)",
                    "cls": "SYSTEM", "basis": digests(seqs),
                    "discrepancy": True})
            else:
                seqs = [ev["seq"] for ev in iev
                        if ev.get("type") == "TREE_CLOSED"]
                specs.append({
                    "key": key,
                    "description": f"{key}: tree did not complete "
                                   f"({basis.get('closure')}) — "
                                   f"not scored",
                    "cls": "SYSTEM", "basis": digests(seqs)})
    for ev in events:
        if ev.get("type") == "OUTPUT_REFUSAL_RECORDED":
            specs.append({
                "key": ev["body"].get("tree_id", "RUN"),
                "description": f"instance result output not "
                               f"admitted: {ev['body'].get('output_id')}",
                "cls": "SYSTEM", "basis": [ev["digest"]]})
    return specs


def run_battery(*, runs_root, package_name, transport,
                tree_keys=None, clock=None, models_check=None):
    """Assemble the battery and run it once, end to end. Returns
    the run summary dict (also written to the run directory)."""
    tree_keys = list(tree_keys or ALL_INSTANCES)
    digests = pins.verify_freeze()
    frozen = pins.FROZEN_DIR
    trees_doc = _load_json(os.path.join(frozen, "pilot_trees.json"))
    data_dir = os.path.join(frozen, "data")
    packs = _load_json(os.path.join(data_dir,
                                    "PILOT-DATA-PACKS-01.json"))["trees"]
    expected = _load_json(os.path.join(data_dir,
                                       "PILOT-DATA-EXPECTED-01.json"))
    fixtures = _load_json(os.path.join(data_dir,
                                       "PILOT-DATA-FIXTURES-01.json"))
    t09 = _load_json(os.path.join(data_dir, "PILOT-DATA-T09-01.json"))
    rules = _load_json(os.path.join(data_dir,
                                    "EXTRACTOR-RULES-02.json"))
    adapter_config = _load_json(os.path.join(
        frozen, "src", "actions-adapter-config.json"))
    trees_map = {t["tree_id"]: t for t in trees_doc["trees"]}

    run_dir = os.path.join(runs_root, package_name)
    for sub in ("captures", "artefacts", "effects", "package",
                "issuer-store"):
        os.makedirs(os.path.join(run_dir, sub), exist_ok=True)
    record_path = os.path.join(run_dir, "record.jsonl")
    record = EventRecord(record_path)

    record_schema = freeze_schema(
        "BATTERY-RECORD-ARTEFACT-1", RECORD_ARTEFACT_FIELDS,
        RECORD_RESPONSE_FIELDS)
    settlement_schema = freeze_schema(
        "STEP6-SETTLEMENT-1", SETTLEMENT_FIELDS,
        ("verdict_fingerprint",))
    draft = build_draft(record_schema, trees_doc, adapter_config)

    # -- Subject consistency over the whole draft (Stage 9 Gate 1
    # correction 1): the binder's G1 surface check cannot see
    # inside the governed values, so a draft whose values name a
    # different subject than its pin — or than the lane that
    # will request and verify it — is refused HERE, before the
    # freeze and before any scored call, recorded under a minted
    # run identity in the binder's own refusal shape.
    problems = _draft_subject_problems(draft, transport)
    if problems:
        run_id = Binder._mint_run_id(record.read_all())
        record.append("RUN_IDENTITY_MINTED", {"run_id": run_id})
        conflict = {"run_id": run_id,
                    "kind": "draft_subject_fields",
                    "problems": problems,
                    "attribution": "UNKNOWN"}
        record.append("SUBJECT_CONFLICT", conflict)
        details = {"stage": "draft_subject_consistency",
                   "conflict": conflict}
        record.append("FREEZE_REFUSED", {"run_id": run_id,
                                         "details": details})
        summary = {"outcome": "FREEZE_REFUSED",
                   "run_package": package_name,
                   "details": details,
                   "record": record_path}
        with open(os.path.join(run_dir, "summary.json"), "wb") as f:
            f.write(canonical(summary))
        return summary

    # -- BINDER: freeze + K2 live subject verification --------------
    def lane(pin):
        served, endpoint, evidence = transport.verification_call()
        ev = {"endpoint": evidence.get("endpoint"),
              "requested_model_id": evidence.get("requested_model_id"),
              "served_model_id": evidence.get("served_model_id"),
              "non_empty_response":
                  evidence.get("non_empty_response"),
              "usage": evidence.get("usage")}
        result = evidence.get("result") or {}
        if result.get("kind") == "capture":
            ev["request_sha256"] = result["request"]["sha256"]
            ev["response_sha256"] = result["response"]["sha256"]
            ev["response_status"] = result["response"]["status"]
        else:
            ev["failure"] = {k: result.get(k) for k in
                             ("kind", "classification", "detail",
                              "status")}
        if models_check is not None:
            ev["models_list"] = models_check()
        record.append("SUBJECT_VERIFICATION_EVIDENCE", ev)
        return served, endpoint

    binder = Binder(record)
    try:
        frozen_run = binder.attempt_freeze(draft, lane)
    except FreezeRefused as exc:
        summary = {"outcome": "FREEZE_REFUSED",
                   "run_package": package_name,
                   "details": exc.details,
                   "record": record_path}
        with open(os.path.join(run_dir, "summary.json"), "wb") as f:
            f.write(canonical(summary))
        return summary
    run_id = frozen_run.run_id

    record.append("BATTERY_FREEZE", {
        "run_package": package_name,
        "config_digest": frozen_run.config_digest,
        "draft_canonical_sha256": sha256_hex(canonical(draft)),
        "record_schema": {
            "version": record_schema.version,
            "artefact_fields": list(RECORD_ARTEFACT_FIELDS),
            "response_fields": list(RECORD_RESPONSE_FIELDS),
            "digest": record_schema.digest},
        "settlement_schema": {
            "version": settlement_schema.version,
            "artefact_fields": list(SETTLEMENT_FIELDS),
            "digest": settlement_schema.digest},
        "bar": BAR,
        "vendored_digests": digests})
    with open(os.path.join(run_dir, "frozen-config.json"), "wb") as f:
        f.write(canonical(draft))

    # -- Stage 7 receipts: the START commitment ----------------------
    package = ResultPackage(os.path.join(run_dir, "package"))
    store = IssuerStore(os.path.join(run_dir, "issuer-store"))
    issuer = ReceiptIssuer(TEST_ISSUER_ID, TEST_KEY, TEST_TERMS)
    anchor = make_test_anchor()
    start_content = canonical({
        "commitment": "START", "run_id": run_id,
        "config_digest": frozen_run.config_digest,
        "subject_digest": frozen_run.subject_record["subject_digest"],
        "tree_set_digest": pins.TREE_SET_DIGEST,
        "schema_digest": record_schema.digest,
        "vendored_digests": digests})
    ev = issue_receipt(record, package, issuer, store, "START",
                       start_content)
    collect_receipt(record, package, store, ev["body"]["receipt_id"])

    # -- Components ---------------------------------------------------
    access = ConfigAccess(frozen_run)
    lane_receipt = access.consume("TRANSPORT", "lane",
                                  ["envelope", "retry"])
    transport.set_envelope(lane_receipt.values["envelope"],
                           lane_receipt.values["retry"])
    corpus = CorpusSource(os.path.join(frozen, "snapshot"), data_dir)
    receiver = Receiver(record, os.path.join(run_dir, "effects"))
    provenance = ProvenanceLog(record)
    tools = ToolLayer(record=record, receiver=receiver,
                      run_id=run_id, corpus=corpus, rules=rules,
                      data_dir=data_dir)
    served_holder = {"served": None, "endpoint": transport.endpoint}
    capture_gate = CaptureGate(
        frozen_run,
        lambda pin: (served_holder["served"],
                     served_holder["endpoint"]))
    engine = Engine(
        record=record, frozen_run=frozen_run, access=access,
        capture_gate=capture_gate, tools=tools, receiver=receiver,
        provenance_log=provenance, record_schema=record_schema,
        transport=transport, trees_doc=trees_doc, packs=packs,
        expected=expected, fixtures=fixtures, t09=t09, corpus=corpus,
        snapshot_dir=os.path.join(frozen, "snapshot"),
        artefacts_dir=os.path.join(run_dir, "artefacts"),
        captures_dir=os.path.join(run_dir, "captures"),
        budgets=dict(BUDGETS), served_holder=served_holder,
        clock=clock)

    # -- EVALUATOR: the one bounded run --------------------------------
    closures = engine.run(tree_keys)
    # The scored set is the frozen declared subset (all 13),
    # whatever subset was executed: an unrun instance stands
    # NOT_RUN / NOT-SCORED in the account — the same set the
    # examiner re-derives over.
    for key in ALL_INSTANCES:
        closures.setdefault(key, "NOT_RUN")

    # -- Scoring (from the record alone) --------------------------------
    events = record.read_all()
    verdicts = scoring.score_all(events, ALL_INSTANCES, trees_map)

    # -- Failures, attributions, discrepancies (Stage 6 + Stage 1) -----
    authority = issue_authority(make_test_authority_record())
    ledger = AttributionLedger(record, authority)
    specs = _collect_failure_specs(events, verdicts, ALL_INSTANCES,
                                   engine.stopped)
    failure_entries = []
    discrepancies = []
    for i, spec in enumerate(specs, 1):
        failure_id = f"F-{i:02d}"
        failure_ref = f"{run_id}/failure/{failure_id}"
        mint = ledger.mint_attribution(failure_ref, spec["cls"],
                                       spec["basis"])
        read_back = ledger.attribution_for(failure_ref)
        entry = make_failure(failure_id, spec["description"],
                             attribution=read_back["body"]["class"],
                             authority=authority.authority_id)
        record.append("FAILURE", entry)
        failure_entries.append(entry)
        if spec.get("discrepancy"):
            key = spec["key"]
            chk = [e for e in record.read_all()
                   if e.get("type") == "CHECK_RESULT"
                   and isinstance(e.get("body"), dict)
                   and e["body"].get("tree_id") == key
                   and e["body"].get("result") == "FAIL"]
            caps = [e for e in record.read_all()
                    if e.get("type") == "MODEL_CALL_LINKED"
                    and isinstance(e.get("body"), dict)
                    and e["body"].get("tree_id") == key]
            disc = mint_discrepancy(
                record, mint["digest"], failure_ref,
                {"holder": "checker",
                 "statement": {"compared":
                               chk[-1]["body"].get("compared")
                               if chk else None,
                               "result": "FAIL — stated fact not "
                                         "extracted"}},
                {"holder": "raw_response",
                 "statement": {"capture_id":
                               caps[-1]["body"].get("capture_id")
                               if caps else None,
                               "raw_output":
                               caps[-1]["body"].get("raw_output")
                               if caps else None}})
            discrepancies.append({"failure_ref": failure_ref,
                                  "discrepancy_event": disc["digest"]})

    # -- Stage 7: the TERMINAL commitment ------------------------------
    events = record.read_all()
    terminal_content = canonical({
        "commitment": "TERMINAL", "run_id": run_id,
        "tree_closures": closures,
        "record_head_digest": record.head_digest,
        "event_count": len(events)})
    ev = issue_receipt(record, package, issuer, store, "TERMINAL",
                       terminal_content)
    collect_receipt(record, package, store, ev["body"]["receipt_id"])
    receipt_acc = receipt_account(record, package, anchor)
    receipts_verified = all(
        r["state"] == "VERIFIED" for r in receipt_acc["receipts"]) \
        and not receipt_acc["unrecorded_package_entries"]

    # -- Settlement (Stage 2 construction) ------------------------------
    counts = {}
    for v in verdicts.values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    bar_pre = {
        "all_instances_scored":
            all(k in verdicts for k in ALL_INSTANCES),
        "zero_governance_fail": counts.get("GOVERNANCE-FAIL", 0) == 0,
        "zero_not_scored": counts.get("NOT-SCORED", 0) == 0,
        "at_most_two_invalid": counts.get("INVALID", 0) <= 2,
        "trust_commitments_verified": bool(receipts_verified),
    }
    settlement_id = f"{run_id}-settlement"
    settlement_values = {
        "run_id": run_id,
        "verdicts": {k: verdicts[k]["verdict"]
                     for k in ALL_INSTANCES},
        "counts": counts,
        "bar_criteria": bar_pre,
        "bar_passed": all(bar_pre.values()),
    }
    for field in SETTLEMENT_FIELDS:
        provenance.append_entry(settlement_id, field,
                                settlement_values[field])
    settlement = ArtefactConstructor(
        provenance, settlement_schema).construct(settlement_id)
    payload = canonical(settlement)

    # -- EXAMINER SURFACE: independent re-derivation --------------------
    import rederive
    examiner = rederive.derive_settlement(record_path, run_dir)
    rederivation_agree = examiner["payload"] == payload

    # -- Adjudication (Stage 4 machinery; harness issuance only) --------
    CheckerContract, validate_verdict, _reg = make_checker_system()
    contract = CheckerContract(
        input_id=settlement_id, procedure=PROCEDURE_IDENTITY,
        version="STEP6-SETTLEMENT-1",
        expected_sha=sha256_hex(examiner["payload"]))
    verdict_obj = contract.run({"id": settlement_id,
                                "payload": payload.decode("utf-8")})
    validation = validate_verdict(verdict_obj, contract) \
        if isinstance(verdict_obj, dict) else verdict_obj
    adjudication_issued = isinstance(verdict_obj, dict) and \
        validation == "ACCEPTED"
    record.append("ADJUDICATION_ISSUED", {
        "settlement_id": settlement_id,
        "verdict": verdict_obj,
        "validation": validation,
        "examiner_agreement": rederivation_agree,
        "fingerprint": sha256_hex(canonical(verdict_obj))})

    # -- Closure (Stage 1 + Stage 7 account) ------------------------------
    account_failures = []
    for entry in failure_entries:
        ref = f"{run_id}/failure/{entry['failure_id']}"
        view = closure_view(record, ref)
        account_failures.append(make_failure(
            entry["failure_id"], entry["description"],
            attribution=view["class"],
            authority=entry["authority"]))
    termination = "RUN_STOPPED" if engine.stopped else "RUN_CLOSED"
    execution = "STOPPED" if engine.stopped else "COMPLETED"
    _acct_ev, closure_ev = close_with_receipt_account(
        record, package, anchor, termination,
        failures=account_failures, execution=execution,
        adjudication="ISSUED" if adjudication_issued
        else "NOT_ISSUED")

    # -- Validation + examiner full report --------------------------------
    validation_result = validate_record(record_path)
    full = rederive.derive_full(run_dir)
    with open(os.path.join(run_dir, "examiner-report.json"),
              "wb") as f:
        f.write(canonical(full))
    with open(os.path.join(run_dir, "validation.json"), "wb") as f:
        f.write(canonical(validation_result))

    bar = scoring.evaluate_bar(
        verdicts=verdicts, tree_keys=ALL_INSTANCES,
        closure_present=True, receipts_verified=receipts_verified,
        rederivation_pass=rederivation_agree and adjudication_issued)
    summary = {
        "outcome": "RUN_COMPLETE",
        "run_package": package_name,
        "run_id": run_id,
        "run_dir": run_dir,
        "record": record_path,
        "subject": SUBJECT,
        "closures": closures,
        "verdicts": {k: verdicts[k]["verdict"]
                     for k in ALL_INSTANCES},
        "counts": counts,
        "bar": bar,
        "closure_account_status":
            closure_ev["body"]["account"]["account_status"],
        "receipts": receipt_acc,
        "adjudication": {"issued": adjudication_issued,
                         "verdict": verdict_obj,
                         "validation": validation,
                         "examiner_agreement": rederivation_agree},
        "validation": {k: validation_result[k] for k in
                       ("terminal_record", "account_completeness",
                        "chain_validity")},
        "discrepancies": discrepancies,
        "failures": failure_entries,
    }
    with open(os.path.join(run_dir, "summary.json"), "wb") as f:
        f.write(canonical(summary))
    return summary

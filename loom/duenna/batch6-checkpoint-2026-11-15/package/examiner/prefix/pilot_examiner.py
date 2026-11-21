#!/usr/bin/env python3
"""PILOT-EXAMINER — the Batch 6 examiner tool (Stage 5 Build Spec Rev 26 §3.7).

Independent of the driver, adapter and supervisor: the only shared code is
the pinned RFC 8785 JCS implementation (pilot_jcs.py, sha256 8a131cfc…)
and the run-record format itself. The examiner reads; it never writes into
runs/ or commitments/.

Steps (Harness §7): step0 anchor & issuance verification (this module's
first stage — any failure is a custody failure and ends the examination),
then chain/input/content/budget/evidence checks in later stages.

CLI:
  pilot_examiner.py step0 --record RUN.run-record.jsonl \
      --receipts-dir DIR --issuance issuance-record.jsonl
Exit codes: 0 = Step 0 passed; 3 = custody failure; 1 = examiner error.
The verdict is printed as one JSON object.
"""
import argparse, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_jcs  # pinned: sha256 8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CustodyFailure(Exception):
    """An anchor or issuance mismatch: examination terminates immediately."""


def parse_complete_events(raw: bytes):
    """Split record bytes into (complete_events, tail_bytes).

    A complete event is a newline-terminated line that parses as a JSON
    object. Bytes after the last complete event are the tail (a torn final
    write). A newline-terminated line that does not parse, anywhere, is
    mid-file corruption — a custody failure, not a tail.
    """
    events, pos = [], 0
    while True:
        nl = raw.find(b"\n", pos)
        if nl < 0:
            break
        line = raw[pos:nl]
        try:
            ev = json.loads(line)
            if not isinstance(ev, dict):
                raise ValueError("event line is not a JSON object")
        except Exception as e:
            raise CustodyFailure(f"unparseable newline-terminated event at byte {pos}: {e}")
        events.append(ev)
        pos = nl + 1
    return events, raw[pos:]


def load_issuance(path: Path):
    entries = []
    for line in path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def verify_receipt_issued(receipt_path: Path, receipt: dict, issuance, checks):
    digest = sha256_hex(receipt_path.read_bytes())
    for e in issuance:
        if (e.get("run_id") == receipt.get("run_id") and e.get("kind") == receipt.get("kind")
                and e.get("receipt_sha256") == digest
                and e.get("issued_at_utc") == receipt.get("issued_at_utc")):
            checks.append(f"issuance: {receipt['kind']} receipt {digest[:12]}… present in issuance-record")
            return
    raise CustodyFailure(
        f"{receipt.get('kind')} receipt for {receipt.get('run_id')} absent from issuance-record "
        f"(receipt sha256 {digest})")


def step0(record_path: Path, receipts_dir: Path, issuance_path: Path) -> dict:
    checks = []
    raw = record_path.read_bytes()
    events, tail = parse_complete_events(raw)
    if not events:
        raise CustodyFailure("record contains no complete events")
    first = events[0]
    if first.get("event_type") != "RUN_STARTED":
        raise CustodyFailure(f"first complete event is {first.get('event_type')}, not RUN_STARTED")
    run_id = first.get("run_id")

    start_p = receipts_dir / f"{run_id}.start.json"
    term_p = receipts_dir / f"{run_id}.terminal.json"
    crash_p = receipts_dir / f"{run_id}.crash.json"
    if not start_p.exists():
        raise CustodyFailure(f"START commitment missing for {run_id}")
    if term_p.exists() and crash_p.exists():
        raise CustodyFailure(f"TERMINAL and CRASH commitments coexist for {run_id} (mutual exclusion violated)")
    if not term_p.exists() and not crash_p.exists():
        raise CustodyFailure(f"no closure commitment (TERMINAL or CRASH) for {run_id}")

    issuance = load_issuance(issuance_path)

    # --- START commitment: genesis + pin block recomputed from RUN_STARTED
    start = json.loads(start_p.read_text())
    if start.get("kind") != "START" or start.get("run_id") != run_id:
        raise CustodyFailure("START receipt kind/run_id mismatch")
    recomputed = sha256_hex(pilot_jcs.canonicalise(first.get("payload")))
    if start.get("genesis_sha256") != first.get("prev_event_sha256"):
        raise CustodyFailure("START genesis_sha256 does not match RUN_STARTED prev_event_sha256")
    if recomputed != first.get("prev_event_sha256"):
        raise CustodyFailure("genesis recomputation mismatch: sha256(canonical(payload)) != prev_event_sha256")
    if start.get("pinned_input_block_sha256") != recomputed:
        raise CustodyFailure("START pinned_input_block_sha256 does not match recomputed pin block")
    if start.get("run_started_event_sha256") != first.get("event_sha256"):
        raise CustodyFailure("START run_started_event_sha256 does not match the RUN_STARTED event")
    checks.append("start: genesis + pinned-input-block recomputed from RUN_STARTED bytes and matched")
    verify_receipt_issued(start_p, start, issuance, checks)

    # --- Closure commitment over the exact bytes as they lie
    file_hash = sha256_hex(raw)
    last = events[-1]
    if term_p.exists():
        term = json.loads(term_p.read_text())
        if term.get("kind") != "TERMINAL" or term.get("run_id") != run_id:
            raise CustodyFailure("TERMINAL receipt kind/run_id mismatch")
        if tail:
            raise CustodyFailure("TERMINAL-committed record has a torn tail")
        if term.get("record_file_sha256") != file_hash:
            raise CustodyFailure("TERMINAL record_file_sha256 mismatch over exact file bytes")
        if term.get("event_count") != len(events):
            raise CustodyFailure("TERMINAL event_count mismatch")
        if term.get("final_event_sha256") != last.get("event_sha256"):
            raise CustodyFailure("TERMINAL final_event_sha256 mismatch")
        if term.get("terminal_event_type") != last.get("event_type"):
            raise CustodyFailure("TERMINAL terminal_event_type mismatch")
        checks.append(f"terminal: commitment verified over exact closed bytes ({len(events)} events)")
        verify_receipt_issued(term_p, term, issuance, checks)
        anchor = "TERMINAL"
    else:
        crash = json.loads(crash_p.read_text())
        if crash.get("kind") != "CRASH" or crash.get("run_id") != run_id:
            raise CustodyFailure("CRASH receipt kind/run_id mismatch")
        if crash.get("record_file_sha256") != file_hash:
            raise CustodyFailure("CRASH record_file_sha256 mismatch over the partial file's exact bytes as they lie")
        if crash.get("event_count") != len(events):
            raise CustodyFailure("CRASH event_count does not bound examination to the complete events")
        if crash.get("final_event_sha256") != last.get("event_sha256"):
            raise CustodyFailure("CRASH final_event_sha256 is not the last complete event")
        if not isinstance(crash.get("termination_observed"), dict) or not crash["termination_observed"].get("basis"):
            raise CustodyFailure("CRASH commitment lacks termination_observed")
        checks.append(f"crash: commitment verified over partial bytes; examination bounded to {len(events)} complete events"
                      + (f"; torn tail of {len(tail)} bytes present and covered by the commitment" if tail else ""))
        verify_receipt_issued(crash_p, crash, issuance, checks)
        anchor = "CRASH"

    return {"run_id": run_id, "step0": "PASS", "anchor": anchor,
            "complete_events": len(events), "tail_bytes": len(tail), "checks": checks}


EVENT_TYPES = {
    "RUN_STARTED", "RUN_CLOSED", "RUN_STOPPED",
    "TREE_TRIGGERED", "TREE_CLOSED",
    "STEP_TRIGGERED", "STEP_SATISFIED", "STEP_FAILED", "STEP_PROGRESS",
    "TOOL_INVOKED", "TOOL_RETURNED", "CHECK_RESULT", "LEDGER_ENTRY",
    "MODEL_CALL_LINKED", "GOVERNANCE_EVENT", "RECOVERY_TAKEN",
}


def step1_chain(events):
    """Step 1 — chain integrity over the complete events (Rev 26 §3.4 (i)).

    Verifies seq continuity from 1, event_id grammar, the closed event-type
    vocabulary, recomputed event_sha256 (JCS preimage = the event without
    its event_sha256), and prev_event_sha256 linkage. The walk stops at the
    first divergence; events beyond it are void and reported as such.
    Returns {walked, divergence: None | {seq, kind, detail}}.
    """
    prev = None
    for i, ev in enumerate(events):
        seq = i + 1
        def div(kind, detail):
            return {"walked": i, "divergence": {"seq": seq, "kind": kind, "detail": detail}}
        if ev.get("seq") != seq:
            return div("SEQ_GAP", f"event at position {seq} carries seq {ev.get('seq')}")
        if ev.get("event_id") != f"{ev.get('run_id')}:{seq}":
            return div("EVENT_ID", f"event_id {ev.get('event_id')} does not match <run_id>:<seq>")
        if ev.get("event_type") not in EVENT_TYPES:
            return div("UNKNOWN_EVENT_TYPE", f"event_type {ev.get('event_type')} outside the closed vocabulary")
        if i > 0 and ev.get("run_id") != events[0].get("run_id"):
            return div("RUN_ID", "run_id changes mid-record")
        body = {k: v for k, v in ev.items() if k != "event_sha256"}
        if sha256_hex(pilot_jcs.canonicalise(body)) != ev.get("event_sha256"):
            return div("HASH_MISMATCH", f"event_sha256 does not recompute at seq {seq}")
        if i == 0:
            if ev.get("event_type") != "RUN_STARTED":
                return div("FORM", "first event is not RUN_STARTED")
        elif ev.get("prev_event_sha256") != prev:
            return div("LINK_BREAK", f"prev_event_sha256 at seq {seq} does not match the seq {seq-1} event hash")
        prev = ev.get("event_sha256")
    return {"walked": len(events), "divergence": None}


def build_pin_index(authority_paths, freeze_manifest_paths):
    """Index pinned artefacts by full path and by basename from
    PILOT-PIN-AUTHORITY-01 files and freeze manifests."""
    index = {}
    def add(path, digest):
        index[path] = digest
        index.setdefault(f"basename:{Path(path).name}", digest)
    for ap in authority_paths:
        data = json.loads(Path(ap).read_text())
        for e in data.get("entries", []):
            add(e["path"], e["sha256"])
    for mp in freeze_manifest_paths:
        for line in Path(mp).read_text().splitlines():
            parts = line.strip().split()
            if len(parts) == 2 and len(parts[0]) == 64:
                add("freeze/" + parts[1].removeprefix("./"), parts[0])
    return index


def verify_snapshot(snapshot_dir):
    """Recompute PILOT-CORPUS-SNAPSHOT-01's per-section hashes and digest
    chains from the snapshot's own files (Rev 26 §3.4, constituent section
    hashes). Returns {documents, sections, ok, problems}."""
    sdir = Path(snapshot_dir)
    manifest = json.loads((sdir / "manifest.json").read_text())
    sections = [json.loads(ln) for ln in (sdir / "sections.jsonl").read_text().splitlines() if ln.strip()]
    problems = []
    by_doc = {}
    for s in sections:
        by_doc.setdefault(s["doc"], []).append(s)
        if sha256_hex(s["text"].encode()) != s["sha256"]:
            problems.append(f"section {s['section_id']}: sha256(text) mismatch")
    for d in manifest["documents"]:
        chain = d["canonical_sha256"]
        for s in sorted(by_doc.get(d["doc"], []), key=lambda x: x["seq"]):
            chain = sha256_hex((chain + s["sha256"]).encode())
            if chain != s["chain_sha256"]:
                problems.append(f"section {s['section_id']}: chain_sha256 mismatch")
        if chain != d["final_chain_sha256"]:
            problems.append(f"document {d['doc']}: final chain mismatch")
    return {"documents": len(manifest["documents"]), "sections": len(sections),
            "ok": not problems, "problems": problems}


def step2_inputs(first_event, pin_index, snapshot_dir=None):
    """Step 2 — input identity (Rev 26 §3.4 (ii) + §3.7 label check).

    Validates the RUN_STARTED pin block against the pin index (authority +
    manifests). Stub runs must be visibly stub-shaped (stub/ paths) and are
    classified STUB — never served-model evidence. When a pin cites the
    corpus snapshot, its constituent section hashes are recomputed.
    Returns {classification, pins_checked, findings}.
    """
    payload = first_event.get("payload") or {}
    pins = payload.get("pins") or []
    findings = []
    is_stub = bool(payload.get("stub")) or "STUB" in str(payload.get("subject", ""))
    if is_stub:
        for p in pins:
            if not str(p.get("path", "")).startswith("stub/"):
                findings.append(f"stub run pins a non-stub path: {p.get('path')}")
        return {"classification": "STUB", "pins_checked": len(pins), "findings": findings,
                "note": "stub configuration visibly named; not served-model evidence"}
    checked = 0
    for p in pins:
        path, digest = p.get("path"), p.get("sha256")
        known = pin_index.get(path) or pin_index.get(f"basename:{Path(str(path)).name}")
        if known is None:
            findings.append(f"pin not found in pin authority/manifests: {path}")
        elif known != digest:
            findings.append(f"pin hash mismatch for {path}: record {str(digest)[:12]}… vs pinned {known[:12]}…")
        else:
            checked += 1
        if snapshot_dir and "PILOT-CORPUS-SNAPSHOT-01" in str(path):
            snap = verify_snapshot(snapshot_dir)
            if not snap["ok"]:
                findings.append(f"corpus snapshot constituent verification failed: {snap['problems'][:2]}")
            else:
                findings.append(f"corpus snapshot sections verified ({snap['sections']} sections, {snap['documents']} documents)")
    return {"classification": "PILOT", "pins_checked": checked, "findings": findings}


def check_capture(capture, config):
    """Classify a linked capture (Rev 26 §3.7). The label is the examiner's,
    not the capture's: a loopback endpoint is the synthetic lane, full stop.
    A non-loopback capture claiming served status must carry the pinned
    catalogue hash and served == pinned model, and its record hash must
    recompute. Returns {label, findings}."""
    findings = []
    body = {k: v for k, v in capture.items() if k != "record_sha256"}
    if capture.get("record_sha256") and sha256_hex(pilot_jcs.canonicalise(body)) != capture["record_sha256"]:
        findings.append("capture record_sha256 does not recompute")
    endpoint = str(capture.get("endpoint", ""))
    if "127.0.0.1" in endpoint or "localhost" in endpoint:
        return {"label": "SYNTHETIC", "findings": findings,
                "note": "loopback endpoint: transport-double lane; synthetic evidence only"}
    cat_pin = (config.get("catalogue_pin") or {}).get("snapshot_sha256")
    if capture.get("subject_pin_catalogue_sha256") != cat_pin:
        findings.append("capture catalogue hash does not match the pinned catalogue snapshot")
    if capture.get("response_model_id_served") != capture.get("subject_model_id_pinned"):
        findings.append("served model differs from pinned model")
    if capture.get("subject_model_id_pinned") != config.get("model"):
        findings.append("capture pinned model differs from the configuration's model")
    return {"label": "LIVE" if not findings else "REJECTED", "findings": findings}


def load_tool_env(tools_dir, snapshot_dir, data_dir, rules_path, scratch_path, run_id, events):
    """Load the pinned tool artefacts for deterministic re-execution.
    The artefacts are inputs (pinned at C6-0b); the examiner's replay runs
    them against its own scratch record, never the examined run's files."""
    import importlib.util
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod
    td = Path(tools_dir)
    corpus_mod = load("corpus_source", td / "corpus_source.py")
    load("rules_engine", td / "rules_engine.py")
    tools_mod = load("pilot_tools", td / "pilot_tools.py")
    corpus = corpus_mod.CorpusSource(str(snapshot_dir), str(data_dir))
    rules_doc = json.loads(Path(rules_path).read_text())
    record = tools_mod.ScratchRecord(str(scratch_path))
    ctx = {"run_id": run_id, "tree_id": None, "step_id": None}
    seen = []
    def reader():
        return list(seen)
    tools = tools_mod.PilotTools(corpus, rules_doc, str(data_dir), record, ctx,
                                 record_reader=reader, canonicalise=pilot_jcs.canonicalise)
    return tools, record, seen


def step3_replay(events, tools, record, seen):
    """Step 3 — deterministic re-execution (Rev 26 §3.7; Harness §3.2).

    Replays every TOOL_INVOKED against a fresh PilotTools instance over
    the pinned corpus/rules/data, comparing each recomputed TOOL_RETURNED
    payload byte-for-byte (canonical form) with the recorded one. CHECK
    phases are re-evaluated where their compared payload is mechanically
    derivable from the walked state (verbatim-rows and verify_field
    patterns); other conditions are reported, never silently passed.
    Returns {reexecuted, checks_reevaluated, checks_not_reexecuted,
    divergence: None | {seq, kind, detail}}.
    """
    scratch = Path(record.path)
    returned_by_op = {}
    reexecuted = 0
    checks_re = 0
    checks_not = []
    divergence = None

    def replay_returned():
        # the replay scratch record is flat: {seq, event_type, **payload}
        lines = scratch.read_text().splitlines()
        for ln in reversed(lines):
            ev = json.loads(ln)
            if ev["event_type"] == "TOOL_RETURNED":
                return {k: v for k, v in ev.items() if k not in ("seq", "event_type")}
        return None

    sections = {}
    extracts = {}   # (tree_id, field) -> latest source_extract result
    step_rows = []  # worksheet rows of the current step
    step_verify = None
    pending_tool = None
    for ev in events:
        seen.append(ev)
        t = ev["event_type"]
        p = ev.get("payload") or {}
        if t == "STEP_TRIGGERED":
            step_rows = []
            step_verify = None
        elif t == "STEP_PROGRESS" and "worksheet_row" in p:
            step_rows.append(p["worksheet_row"])
        elif t == "TOOL_INVOKED":
            pending_tool = p.get("tool")
            tool = p["tool"]
            args = p.get("args") or {}
            tools._ctx["tree_id"] = ev.get("tree_id")
            tools._ctx["step_id"] = ev.get("step_id")
            fn = getattr(tools, tool)
            if tool == "reference_insert":
                # Records from the earlier form carry a bare operation_id;
                # the pinned correction-form tool takes the tagged union.
                presentation = args.get("presentation")
                if presentation is None and args.get("operation_id"):
                    presentation = {"form": "extracted", "operation_id": args["operation_id"]}
                fn(args.get("field"), args.get("process_step"), presentation)
            elif tool == "shelf_lookup":
                fn(args.get("source_ref"))
            elif tool == "source_extract":
                fn(args.get("source_ref"), args.get("field"))
            elif tool == "verify_field":
                fn(**{k: args.get(k) for k in ("field", "value", "expected_ref")})
            elif tool == "receipt_worksheet":
                fn(args.get("receipt_id"))
            else:
                divergence = {"seq": ev["seq"], "kind": "UNKNOWN_TOOL", "detail": tool}
                break
            reexecuted += 1
        elif t == "TOOL_RETURNED":
            rep = replay_returned()
            same = rep is not None and pilot_jcs.canonicalise(rep) == pilot_jcs.canonicalise(p)
            if not same:
                divergence = {"seq": ev["seq"], "kind": "OUTCOME_MISMATCH",
                              "detail": f"recomputed TOOL_RETURNED for {p.get('operation_id')} differs from the record"}
                break
            pending_tool = None
            returned_by_op[p.get("operation_id")] = p
            if p.get("tool") == "source_extract" and isinstance(p.get("result"), dict):
                extracts[(ev.get("tree_id"), p["result"].get("field"))] = p["result"]
            if p.get("tool") == "verify_field" and isinstance(p.get("result"), dict):
                step_verify = p["result"]
        elif t == "CHECK_RESULT":
            comp = p.get("compared") or {}
            verdict = None
            if "all_verbatim" in comp:
                if not sections:
                    snap = tools._corpus
                    sections = snap._sections
                ok = all((r.get("claim", "") in sections.get(r.get("source"), {}).get("text", ""))
                         for r in step_rows)
                verdict = ("PASS" if ok and comp.get("rows") == len(step_rows) else "FAIL")
                if ok != comp.get("all_verbatim") or comp.get("rows") != len(step_rows):
                    verdict = None
                    divergence = {"seq": ev["seq"], "kind": "CHECK_MISMATCH",
                                  "detail": "verbatim-rows recomputation disagrees with the recorded compared payload"}
                    break
            elif "verify_field" in comp and step_verify is not None:
                if comp.get("verify_field") != step_verify.get("verified"):
                    divergence = {"seq": ev["seq"], "kind": "CHECK_MISMATCH",
                                  "detail": "compared.verify_field disagrees with the verify_field return"}
                    break
                verdict = "PASS" if (comp.get("stated") == comp.get("adjudication")
                                     and comp.get("verify_field") is True) else "FAIL"
            if verdict is not None:
                checks_re += 1
                if verdict != p.get("result"):
                    divergence = {"seq": ev["seq"], "kind": "CHECK_MISMATCH",
                                  "detail": f"re-evaluated CHECK result {verdict} != recorded {p.get('result')}"}
                    break
            else:
                checks_not.append(p.get("condition"))
    return {"reexecuted": reexecuted, "checks_reevaluated": checks_re,
            "checks_not_reexecuted": checks_not, "divergence": divergence}


def step4_audit(events, snapshot_sections):
    """Step 4 — issuance-registry reconstruction and insert audit, from the
    event sequence alone (Rev 26 §3.7; Harness §4.5; tools contract Rev 24/25).

    Rebuilds issuances from source_extract returns, then verifies every
    consumption (LEDGER_ENTRY), every refusal (INSERT_REFUSED governance
    events paired with refused insert returns), and every carried
    provenance block. Returns {issuances, consumptions, refusals,
    carried, findings}.
    """
    findings = []
    issuances = {}       # operation_id -> issuance dict
    consumed = set()
    citations_consumed = set()
    produced = {}        # event_id -> STEP_PROGRESS event (PRODUCED_ARTEFACT)
    insert_returns = {}  # insert op id -> TOOL_RETURNED payload
    pending_refusals = []
    consumptions = 0
    carried = 0
    refusals = 0
    extraction_insertions = {}  # tree_id -> [source_ref, ...] in insertion order

    def section_hash(ref):
        sec = snapshot_sections.get(ref)
        return sec.get("sha256") if sec else None

    for i, ev in enumerate(events):
        t = ev["event_type"]
        p = ev.get("payload") or {}
        if t == "STEP_PROGRESS" and p.get("kind") == "PRODUCED_ARTEFACT":
            produced[ev["event_id"]] = (i, ev)
        elif t == "TOOL_RETURNED" and p.get("tool") == "source_extract":
            r = p.get("result") or {}
            if r.get("verification") == "EXTRACTED":
                issuances[p["operation_id"]] = {
                    "field": r.get("field"), "value": r.get("value"),
                    "source_ref": r.get("source_ref"), "source_hash": r.get("source_hash"),
                    "rule_id": r.get("rule_id"), "tree_id": ev.get("tree_id"),
                    "step_id": ev.get("step_id")}
                if section_hash(r.get("source_ref")) != r.get("source_hash"):
                    findings.append(f"seq {ev['seq']}: extract {p['operation_id']} source_hash does not match the pinned snapshot section")
        elif t == "TOOL_RETURNED" and p.get("tool") == "reference_insert":
            insert_returns[p["operation_id"]] = p
            r = p.get("result") or {}
            if r.get("refused"):
                pending_refusals.append((ev, r))
        elif t == "GOVERNANCE_EVENT" and p.get("kind") == "INSERT_REFUSED":
            refusals += 1
            match = [x for x in pending_refusals if x[1].get("reason") == p.get("reason")]
            if not match:
                findings.append(f"seq {ev['seq']}: INSERT_REFUSED ({p.get('reason')}) has no paired refused insert return")
            else:
                pending_refusals.remove(match[0])
        elif t == "LEDGER_ENTRY":
            consumptions += 1
            cf = p.get("carried_from")
            if isinstance(cf, dict):
                carried += 1
                # carried provenance (Rev 23-25)
                if p.get("verification") != "CARRIED":
                    findings.append(f"seq {ev['seq']}: carried entry without verification == CARRIED")
                if p.get("source_ref") is not None:
                    findings.append(f"seq {ev['seq']}: carried entry with non-null source_ref")
                got = produced.get(cf.get("event_id"))
                if got is None:
                    findings.append(f"seq {ev['seq']}: carried_from cites no PRODUCED_ARTEFACT event in this run")
                    continue
                src_i, src = got
                if sha256_hex(pilot_jcs.canonicalise(src.get("payload"))) != cf.get("payload_sha256"):
                    findings.append(f"seq {ev['seq']}: carried_from payload hash mismatch")
                if (src.get("payload") or {}).get("field") != p.get("field"):
                    findings.append(f"seq {ev['seq']}: carried entry field differs from the cited artefact's field")
                if (src.get("payload") or {}).get("value") != p.get("value"):
                    findings.append(f"seq {ev['seq']}: carried entry value differs from the record's own carried value")
                if src.get("tree_id") != ev.get("tree_id"):
                    findings.append(f"seq {ev['seq']}: carried citation crosses trees")
                passed = any(e2["event_type"] == "CHECK_RESULT" and (e2.get("payload") or {}).get("result") == "PASS"
                             and e2.get("step_id") == src.get("step_id") for e2 in events[src_i:i])
                if not passed:
                    findings.append(f"seq {ev['seq']}: no passing CHECK_RESULT for the producing step after the cited event")
                if cf.get("event_id") in citations_consumed:
                    findings.append(f"seq {ev['seq']}: citation consumed more than once")
                citations_consumed.add(cf.get("event_id"))
                if p.get("field") == "evidence":
                    expect = extraction_insertions.get(ev.get("tree_id"), [])
                    if p.get("value") != expect:
                        findings.append(f"seq {ev['seq']}: evidence entry value is not the ordered source_ref sequence of the tree's extraction insertions")
            else:
                op = p.get("operation_id")
                iss = issuances.get(op)
                if iss is None:
                    findings.append(f"seq {ev['seq']}: LEDGER_ENTRY consumes unknown issuance {op}")
                    continue
                if op in consumed:
                    findings.append(f"seq {ev['seq']}: issuance {op} consumed more than once")
                consumed.add(op)
                if iss["tree_id"] != ev.get("tree_id") or iss["step_id"] != p.get("step_id"):
                    findings.append(f"seq {ev['seq']}: entry context (tree/step) differs from the issuance's")
                for f in ("field", "value", "source_ref", "source_hash", "rule_id"):
                    if p.get(f) != iss[f]:
                        findings.append(f"seq {ev['seq']}: entry {f} differs from the issuance")
                extraction_insertions.setdefault(ev.get("tree_id"), []).append(p.get("source_ref"))
    for ev, r in pending_refusals:
        findings.append(f"seq {ev['seq']}: refused insert ({r.get('reason')}) without an INSERT_REFUSED governance event")
    return {"issuances": len(issuances), "consumptions": consumptions,
            "refusals": refusals, "carried": carried, "findings": findings}


ENVELOPE_KEYS = {"model", "temperature", "top_p", "max_tokens", "stream",
                 "chat_template_kwargs", "messages"}


def step5_capture(capture, config):
    """Step 5 — preserved subject artefacts (Rev 26 §3.7 step 5;
    ADAPTER-CAPTURE-02). The response is consumed strictly as a fixed
    preserved artefact; nothing is re-sampled. Includes Amendment A's
    closed-set assertion on the preserved request envelope.
    Returns {capture_id, findings}."""
    findings = []
    cid = capture.get("capture_id")
    body = {k: v for k, v in capture.items() if k != "record_sha256"}
    if capture.get("record_sha256") and sha256_hex(pilot_jcs.canonicalise(body)) != capture["record_sha256"]:
        findings.append("record_sha256 does not recompute")
    if capture.get("request_raw") is not None and capture.get("request_sha256"):
        if sha256_hex(str(capture["request_raw"]).encode()) != capture["request_sha256"]:
            findings.append("request_sha256 does not recompute over request_raw")
    if capture.get("response_raw") is not None and capture.get("response_sha256"):
        if sha256_hex(str(capture["response_raw"]).encode()) != capture["response_sha256"]:
            findings.append("response_sha256 does not recompute over response_raw")
    # Amendment A applies to the preserved request as sent — the wire
    # envelope, recovered by parsing request_raw (the capture's
    # request_envelope field is the six-key configuration envelope,
    # checked closed against the configuration itself).
    wire_keys = None
    if capture.get("request_raw"):
        try:
            wire_keys = set(json.loads(str(capture["request_raw"])).keys())
        except Exception:
            findings.append("request_raw does not parse as a JSON envelope")
    if wire_keys is not None and wire_keys != ENVELOPE_KEYS:
        findings.append(f"Amendment A: wire envelope key set {sorted(wire_keys)} != the exact seven-key set")
    env = capture.get("request_envelope") or {}
    cfg_env_keys = set((config.get("envelope") or {}).keys())
    if cfg_env_keys and set(env.keys()) != cfg_env_keys:
        findings.append(f"request_envelope key set {sorted(env.keys())} != the configuration envelope's closed key set")
    rp = config.get("retry_policy") or {}
    attempts = capture.get("attempts") or []
    if rp.get("max_attempts") and len(attempts) > rp["max_attempts"]:
        findings.append(f"retry policy: {len(attempts)} attempts exceed max_attempts {rp['max_attempts']}")
    req_hashes = set()
    for i, a in enumerate(attempts):
        raw = a.get("response_body_raw")
        if raw is not None and a.get("response_body_sha256"):
            if sha256_hex(str(raw).encode()) != a["response_body_sha256"]:
                findings.append(f"attempt {i}: response_body_sha256 does not recompute")
        if a.get("request_sha256"):
            req_hashes.add(a["request_sha256"])
        if i > 0 and a.get("request_sha256") and capture.get("request_sha256") \
                and a["request_sha256"] != capture["request_sha256"]:
            findings.append(f"attempt {i}: request hash differs from the first attempt (byte-identical resend violated)")
    return {"capture_id": cid, "attempts": len(attempts), "findings": findings}


def step5_model_link(ev):
    """Step 5 for scratch-lane MODEL_CALL_LINKED events: the preserved
    output's hash must recompute from the payload's raw_output."""
    p = ev.get("payload") or {}
    ok = sha256_hex(str(p.get("raw_output", "")).encode()) == p.get("response_sha256")
    return {"capture_id": p.get("capture_id"), "ok": ok,
            "findings": [] if ok else ["response_sha256 does not recompute over the preserved raw_output"]}


def step6_reconstruct(events, trees_doc):
    """Step 6 — outcome reconstruction (Rev 26 §3.7 step 6; Harness §1.4).

    Recomputes step outcomes from CHECK_RESULTs under the trees' declared
    failure/recovery rules (STEP_SATISFIED/FAILED events are NOT inputs —
    they are part of what is confirmed), then tree closures, then the run's
    terminal state, confirming or overturning the recorded TREE_CLOSED /
    RUN_CLOSED values and localising the first divergence.
    Returns {trees, run_terminal, divergences, undetermined}.
    """
    trees = {t["tree_id"]: t for t in trees_doc.get("trees", [])}
    # attempts[tree][step] = list of attempt verdicts (PASS/FAIL/None)
    attempts = {}
    order = []
    cur = {}
    infra_failed = set()
    infra_failed_steps = set()
    for ev in events:
        t = ev["event_type"]
        tree, step = ev.get("tree_id"), ev.get("step_id")
        if t == "STEP_FAILED" and (ev.get("payload") or {}).get("failure_class") == "ADAPTER_FAILURE":
            # an infrastructure-class failure invalidates the tree: the
            # failure is the lane's, not the subject's (Batch 3 run-002)
            if tree:
                infra_failed.add(tree)
                infra_failed_steps.add((tree, (ev.get("payload") or {}).get("step_id") or step))
        if t == "STEP_TRIGGERED" and tree and step:
            attempts.setdefault(tree, {}).setdefault(step, []).append(None)
            cur[(tree, step)] = len(attempts[tree][step]) - 1
            if tree not in order:
                order.append(tree)
        elif t == "CHECK_RESULT" and tree and step and (tree, step) in cur:
            attempts[tree][step][cur[(tree, step)]] = (ev.get("payload") or {}).get("result")
    def failure_is_data(rule):
        """A step failure disposed of as data by its declared failure rule
        (routed onward, per-statement outcomes, or the worksheet-stands
        disposition) does not block its tree's completion."""
        r = (rule or "").lower()
        return ("go to step-" in r or "per-statement" in r or r.strip() == "none"
                or "worksheet stands" in r or "worker error" in r
                or "subject error" in r)
    closures = {}
    undetermined = []
    for tree in order:
        # FR variants share the T09 template definition
        tdef = trees.get(tree) or trees.get(tree.split("/")[0], {})
        step_defs = {s["step_id"]: s for s in tdef.get("steps", [])}
        blocking = False
        for step, att in attempts[tree].items():
            final = att[-1]
            if final is None and (tree, step) not in infra_failed_steps:
                undetermined.append(f"{tree}/{step}: final attempt has no CHECK_RESULT")
                blocking = True
            elif final != "PASS" and not failure_is_data(step_defs.get(step, {}).get("failure")):
                blocking = True
            maxa = (step_defs.get(step, {}).get("recovery") or {}).get("max_attempts")
            if maxa and len(att) > maxa:
                undetermined.append(f"{tree}/{step}: {len(att)} attempts exceed the declared recovery max {maxa}")
        # the walk completes a tree only if it reached the tree's last
        # defined step (a budget stop leaves the tree cut short)
        last_step = tdef.get("steps", [{}])[-1].get("step_id")
        reached_end = last_step in attempts.get(tree, {})
        if tree in infra_failed:
            closures[tree] = "INVALIDATED-INFRASTRUCTURE"
        else:
            closures[tree] = "COMPLETED" if (not blocking and reached_end) else "STOPPED"
    # a run-level budget stop at a tree whose steps all completed leaves
    # the tree INCOMPLETE — the work finished, the run's budget did not
    # let it seal (Batch 3 run-004: RUN_STOPPED/RUN_BUDGET_EXCEEDED)
    for ev in events:
        if ev["event_type"] == "RUN_STOPPED":
            p = ev.get("payload") or {}
            at = p.get("at_tree")
            if p.get("reason") == "RUN_BUDGET_EXCEEDED" and at and closures.get(at) == "COMPLETED":
                closures[at] = "INCOMPLETE"
    divergences = []
    for ev in events:
        if ev["event_type"] == "RUN_STOPPED":
            p = ev.get("payload") or {}
            if p.get("invalidated_trees") is not None and \
                    p["invalidated_trees"] != sum(1 for c in closures.values() if c == "INVALIDATED-INFRASTRUCTURE"):
                divergences.append({"seq": ev["seq"], "kind": "TERMINAL_OVERTURNED",
                                    "detail": "RUN_STOPPED invalidated_trees count differs from the reconstruction"})
        if ev["event_type"] == "TREE_CLOSED":
            p = ev.get("payload") or {}
            want = closures.get(p.get("tree_id"))
            if want is not None and p.get("closure") != want:
                divergences.append({"seq": ev["seq"], "kind": "CLOSURE_OVERTURNED",
                                    "detail": f"tree {p.get('tree_id')}: recorded {p.get('closure')}, reconstructed {want}"})
        elif ev["event_type"] == "RUN_CLOSED":
            p = ev.get("payload") or {}
            if p.get("tree_closures") != closures:
                divergences.append({"seq": ev["seq"], "kind": "TERMINAL_OVERTURNED",
                                    "detail": "recorded tree_closures differ from the reconstruction"})
            if p.get("event_count") != len(events):
                divergences.append({"seq": ev["seq"], "kind": "TERMINAL_OVERTURNED",
                                    "detail": f"event_count {p.get('event_count')} != {len(events)} events walked"})
            # record_sha256 is the chain head the terminal event closes
            # over: its own prev_event_sha256 (the head before the
            # terminal event was appended — a self-hash is impossible)
            if p.get("record_sha256") != ev.get("prev_event_sha256"):
                divergences.append({"seq": ev["seq"], "kind": "TERMINAL_OVERTURNED",
                                    "detail": "record_sha256 is not the chain head the terminal event closes over"})
    return {"trees": closures, "run_terminal": "RUN_CLOSED" if any(
        e["event_type"] == "RUN_CLOSED" for e in events) else "OPEN",
        "divergences": divergences, "undetermined": undetermined}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pilot_examiner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s0 = sub.add_parser("step0", help="Step 0 anchor & issuance verification")
    s0.add_argument("--record", required=True)
    s0.add_argument("--receipts-dir", required=True)
    s0.add_argument("--issuance", required=True)
    s1 = sub.add_parser("step1", help="Step 1 chain integrity")
    s1.add_argument("--record", required=True)
    s2 = sub.add_parser("step2", help="Step 2 input identity")
    s2.add_argument("--record", required=True)
    s2.add_argument("--authority", action="append", default=[])
    s2.add_argument("--freeze-manifest", action="append", default=[])
    s2.add_argument("--snapshot", default=None)
    sx = sub.add_parser("examine", help="full examination: Steps 0-6")
    sx.add_argument("--record", required=True)
    sx.add_argument("--receipts-dir", required=True)
    sx.add_argument("--issuance", required=True)
    sx.add_argument("--authority", action="append", default=[])
    sx.add_argument("--freeze-manifest", action="append", default=[])
    sx.add_argument("--snapshot", default=None)
    sx.add_argument("--captures-dir", default=None)
    sx.add_argument("--config", default=None)
    sx.add_argument("--trees", default=None)
    sx.add_argument("--tools-dir", default=None)
    sx.add_argument("--data-dir", default=None)
    sx.add_argument("--rules", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "step0":
        try:
            verdict = step0(Path(args.record), Path(args.receipts_dir), Path(args.issuance))
        except CustodyFailure as e:
            print(json.dumps({"step0": "CUSTODY-FAILURE", "reason": str(e)}))
            return 3
        print(json.dumps(verdict))
        return 0
    if args.cmd == "step1":
        events, _tail = parse_complete_events(Path(args.record).read_bytes())
        print(json.dumps(step1_chain(events)))
        return 0
    if args.cmd == "step2":
        events, _tail = parse_complete_events(Path(args.record).read_bytes())
        index = build_pin_index(args.authority, args.freeze_manifest)
        print(json.dumps(step2_inputs(events[0], index, args.snapshot)))
        return 0
    if args.cmd == "examine":
        import tempfile
        try:
            v0 = step0(Path(args.record), Path(args.receipts_dir), Path(args.issuance))
        except CustodyFailure as e:
            print(json.dumps({"examination": "CUSTODY-FAILURE", "reason": str(e)}))
            return 3
        events, _tail = parse_complete_events(Path(args.record).read_bytes())
        out = {"run_id": v0["run_id"], "step0": v0, "step1": step1_chain(events)}
        index = build_pin_index(args.authority, args.freeze_manifest)
        out["step2"] = step2_inputs(events[0], index, args.snapshot)
        if args.tools_dir and args.snapshot and args.data_dir and args.rules:
            with tempfile.TemporaryDirectory() as td:
                tools, record, seen = load_tool_env(
                    Path(args.tools_dir), Path(args.snapshot), Path(args.data_dir),
                    Path(args.rules), Path(td) / "replay.jsonl", v0["run_id"], events)
                out["step3"] = step3_replay(events, tools, record, seen)
                record.close()
            snap = CorpusSections(Path(args.snapshot))
            out["step4"] = step4_audit(events, snap)
        config = json.loads(Path(args.config).read_text()) if args.config else {}
        caps = []
        if args.captures_dir:
            for cf in sorted(Path(args.captures_dir).rglob("*.json")):
                caps.append(step5_capture(json.loads(cf.read_text()), config))
        links = [step5_model_link(e) for e in events if e["event_type"] == "MODEL_CALL_LINKED"]
        out["step5"] = {"captures": caps, "model_links": links}
        if args.trees:
            trees_doc = json.loads(Path(args.trees).read_text())
            out["step6"] = step6_reconstruct(events, trees_doc)
        print(json.dumps(out))
        return 0
    return 1


class CorpusSections(dict):
    """section_id -> section, loaded from a snapshot's sections.jsonl."""
    def __init__(self, snapshot_dir):
        super().__init__()
        for ln in (Path(snapshot_dir) / "sections.jsonl").read_text().splitlines():
            if ln.strip():
                s = json.loads(ln)
                self[s["section_id"]] = s


if __name__ == "__main__":
    sys.exit(main())

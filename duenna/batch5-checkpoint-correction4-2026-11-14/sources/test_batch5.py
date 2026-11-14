#!/usr/bin/env python3
"""Batch 5 checkpoint tests (chunk sheet C5-13..C5-17, plus
the classification and isolation cases of C5-8/C5-11).

Runs the real adapter against the transport double only.
Writes one test artefact per scenario into
../checkpoint-artefacts/, naming the double's identity in
each, plus a summary. Usage:

    test_batch5.py [--with-timeout]

The timeout scenario takes ~245 s (two real 120 s attempt
timeouts + the pinned 5 s delay) and runs only on request.

Correction (2026-11-14, Alex's C5-17 specification): envelope
byte fidelity verification via envelope_fidelity.py — the
original parsed-value check below remains as a semantic check
only; byte fidelity is established by the source-span token
comparison aggregated in c5-17-envelope-fidelity.json.
"""
import hashlib
import json
import os
import sys
import threading
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilot_jcs
import transport_double as dbl
import envelope_fidelity as ef
from pilot_adapter import Adapter, ConfigError, PINNED_CONFIG_SHA256

CONFIG = os.path.join(
    HERE, "adapter-config-f2-2026-11-12.canonical.json")
ARTEFACTS = os.path.join(HERE, "..", "checkpoint-artefacts")
PORT = 8971

FIDELITY_SCENARIOS = []


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def step_inputs(tag):
    return {
        "correlation_id": f"corr-{tag}",
        "tree_id": "TDOUBLE",
        "step_id": f"TDOUBLE-{tag}",
        "messages": [
            {"role": "system", "content": "double test contract"},
            {"role": "user", "content": "say ok"},
        ],
    }


def check_record(rec, cfg_envelope):
    """Cross-cutting record checks (schema, hashes, envelope)."""
    out = {}
    out["field_count_30"] = len(rec) == 30
    body = dict(rec)
    claimed = body.pop("record_sha256")
    out["record_sha256_recomputes"] = \
        sha(pilot_jcs.canonicalise(body)) == claimed
    out["request_sha256_recomputes"] = \
        sha(rec["request_raw"].encode("utf-8")) == rec["request_sha256"]
    if rec["response_raw"] is not None:
        out["response_sha256_recomputes"] = \
            sha(rec["response_raw"].encode("utf-8")) == \
            rec["response_sha256"]
    for a in rec["attempts"]:
        if a["response_body_raw"] is not None:
            assert sha(a["response_body_raw"].encode("utf-8")) == \
                a["response_body_sha256"], "attempt body hash mismatch"
    out["attempt_body_hashes_recompute"] = True
    out["config_digest_pinned"] = \
        rec["adapter_config_sha256"] == PINNED_CONFIG_SHA256
    out["envelope_matches_config"] = \
        rec["request_envelope"] == cfg_envelope
    sent = json.loads(rec["request_raw"])
    out["wire_envelope_matches_config"] = all(
        sent[k] == cfg_envelope[k] for k in cfg_envelope)
    out["wire_messages_unmodified"] = \
        sent["messages"] == step_inputs("x")["messages"]
    return out


def run_scenario(name, expect):
    capdir = os.path.join(ARTEFACTS, "captures", name)
    os.makedirs(capdir, exist_ok=True)
    adapter = Adapter(CONFIG, capdir,
                      f"http://127.0.0.1:{PORT}/s/{name}")
    before = len(dbl.STATE.requests)
    result = adapter.complete(step_inputs(name))
    rec = json.load(open(os.path.join(
        capdir, result["capture_record_id"] + ".json")))
    cfg = json.load(open(CONFIG))
    checks = check_record(rec, cfg["envelope"])
    reqs = dbl.STATE.requests[before:]
    checks.update(expect(rec, result, reqs))
    fid = ef.verify_capture(rec, cfg["envelope"],
                            [body for (_scen, body) in reqs])
    FIDELITY_SCENARIOS.append({"scenario": name, **fid})
    checks["c5_17_envelope_byte_fidelity"] = \
        fid["envelope"]["passed"]
    checks["c5_17_transport_receipt"] = fid["transport"]["passed"]
    artefact = {
        "scenario": name,
        "double_id": dbl.DOUBLE_ID,
        "adapter_id": rec["adapter_id"],
        "capture_id": rec["capture_id"],
        "capture_file": f"captures/{name}/{rec['capture_id']}.json",
        "checks": checks,
        "passed": all(checks.values()),
    }
    with open(os.path.join(ARTEFACTS, f"{name}.json"), "w") as f:
        json.dump(artefact, f, indent=1)
    print(f"{name}: {'PASS' if artefact['passed'] else 'FAIL'} "
          f"({sum(checks.values())}/{len(checks)} checks)")
    return artefact


def main():
    with_timeout = "--with-timeout" in sys.argv
    os.makedirs(ARTEFACTS, exist_ok=True)
    server = dbl.serve(PORT)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []

    def exp_ok(rec, res, reqs):
        return {
            "one_attempt": len(rec["attempts"]) == 1,
            "raw_output": res["raw_output"] == "double-ok",
            "no_failure_class": rec["failure_class"] is None,
            "transport_received":
                rec["transport_outcome"] == "RESPONSE_RECEIVED",
            "served_is_pinned":
                rec["response_model_id_served"] ==
                "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        }

    def exp_retry(text):
        def f(rec, res, reqs):
            a = rec["attempts"]
            delay = (ts(a[1]["sent_at_utc"]) -
                     ts(a[0]["received_at_utc"])).total_seconds()
            return {
                "two_attempts": len(a) == 2,
                "first_body_preserved":
                    a[0]["response_body_raw"] is not None,
                "first_status_error":
                    a[0]["http_status"] in (429, 500),
                "resend_byte_identical":
                    len(reqs) == 2 and reqs[0][1] == reqs[1][1],
                "delay_at_least_5s": delay >= 5.0,
                "raw_output": res["raw_output"] == text,
                "success_no_failure_class":
                    rec["failure_class"] is None,
            }
        return f

    def exp_fail_429(rec, res, reqs):
        return {
            "two_attempts": len(rec["attempts"]) == 2,
            "adapter_failure": rec["failure_class"] == "ADAPTER_FAILURE",
            "transport_http_error":
                rec["transport_outcome"] == "HTTP_ERROR",
            "raw_output_null": res["raw_output"] is None,
        }

    def exp_kwargs(rec, res, reqs):
        return {
            "exactly_one_attempt": len(rec["attempts"]) == 1,
            "adapter_failure": rec["failure_class"] == "ADAPTER_FAILURE",
            "detail_names_field":
                "chat_template_kwargs" in (rec["failure_detail"] or ""),
            "raw_output_null": res["raw_output"] is None,
        }

    def exp_404(rec, res, reqs):
        return {
            "exactly_one_attempt": len(rec["attempts"]) == 1,
            "adapter_failure": rec["failure_class"] == "ADAPTER_FAILURE",
            "raw_output_null": res["raw_output"] is None,
        }

    def exp_mismatch(rec, res, reqs):
        return {
            "exactly_one_attempt": len(rec["attempts"]) == 1,
            "adapter_failure": rec["failure_class"] == "ADAPTER_FAILURE",
            "served_recorded":
                rec["response_model_id_served"] == "nvidia/other",
            "raw_output_null": res["raw_output"] is None,
        }

    def exp_unparseable(rec, res, reqs):
        return {
            "exactly_one_attempt": len(rec["attempts"]) == 1,
            "no_failure_class": rec["failure_class"] is None,
            "body_preserved":
                rec["response_raw"] == "this is not json at all",
            "raw_output_null": res["raw_output"] is None,
        }

    def exp_redact(rec, res, reqs):
        text = json.dumps(rec)
        return {
            "two_attempts": len(rec["attempts"]) == 2,
            "adapter_failure": rec["failure_class"] == "ADAPTER_FAILURE",
            "secret_absent": dbl.FAKE_SECRET not in text,
            "redaction_marker_present": "[REDACTED]" in text,
        }

    def exp_timeout(rec, res, reqs):
        a = rec["attempts"]
        return {
            "two_attempts": len(a) == 2,
            "both_timeout_class":
                all(x["error_class"] == "Timeout" for x in a),
            "transport_timeout":
                rec["transport_outcome"] == "TIMEOUT",
            "adapter_failure": rec["failure_class"] == "ADAPTER_FAILURE",
            "no_response_fields":
                rec["response_raw"] is None
                and rec["response_http_status"] is None,
            "raw_output_null": res["raw_output"] is None,
        }

    results.append(run_scenario("ok", exp_ok))
    results.append(run_scenario("retry-429", exp_retry("recovered-after-429")))
    results.append(run_scenario("retry-500", exp_retry("recovered-after-500")))
    results.append(run_scenario("fail-429", exp_fail_429))
    results.append(run_scenario("kwargs-400", exp_kwargs))
    results.append(run_scenario("notfound-404", exp_404))
    results.append(run_scenario("mismatch", exp_mismatch))
    results.append(run_scenario("unparseable", exp_unparseable))
    results.append(run_scenario("redact-500", exp_redact))
    if with_timeout:
        results.append(run_scenario("timeout", exp_timeout))

    # --- isolation (C5-11): non-loopback refused at start-up;
    # tampered configuration refused at start-up.
    iso = {}
    for label, url in [("provider_url", dbl and
                        "https://integrate.api.nvidia.com/v1"),
                       ("public_ip", "http://203.0.113.7/v1")]:
        try:
            Adapter(CONFIG, os.path.join(ARTEFACTS, "captures", "iso"),
                    url)
            iso[label + "_refused"] = False
        except ConfigError:
            iso[label + "_refused"] = True
    tampered = os.path.join(ARTEFACTS, "tampered-config.json")
    cfg = json.load(open(CONFIG))
    cfg["envelope"]["temperature"] = 0.0
    with open(tampered, "w") as f:
        json.dump(cfg, f)
    try:
        Adapter(tampered, os.path.join(ARTEFACTS, "captures", "iso"),
                f"http://127.0.0.1:{PORT}/s/ok")
        iso["tampered_config_refused"] = False
    except ConfigError:
        iso["tampered_config_refused"] = True
    iso_art = {"scenario": "isolation", "double_id": dbl.DOUBLE_ID,
               "checks": iso, "passed": all(iso.values())}
    with open(os.path.join(ARTEFACTS, "isolation.json"), "w") as f:
        json.dump(iso_art, f, indent=1)
    print(f"isolation: {'PASS' if iso_art['passed'] else 'FAIL'} {iso}")
    results.append(iso_art)

    # --- redaction sweep (C5-16) across every capture written
    sweep_ok = True
    caproot = os.path.join(ARTEFACTS, "captures")
    for root, _dirs, files in os.walk(caproot):
        for fn in files:
            if fn.endswith(".json"):
                text = open(os.path.join(root, fn)).read()
                if dbl.FAKE_SECRET in text or \
                        "Authorization: Bearer" in text:
                    sweep_ok = False
    sweep = {"scenario": "redaction-sweep", "double_id": dbl.DOUBLE_ID,
             "checks": {"no_credential_material_in_any_capture":
                        sweep_ok},
             "passed": sweep_ok}
    with open(os.path.join(ARTEFACTS, "redaction-sweep.json"), "w") as f:
        json.dump(sweep, f, indent=1)
    print(f"redaction-sweep: {'PASS' if sweep_ok else 'FAIL'}")
    results.append(sweep)

    # --- C5-17 envelope byte fidelity (Alex's correction spec,
    # 2026-11-14): negative controls built from a real captured
    # request, and the aggregate artefact over every scenario.
    ok_caps = os.path.join(ARTEFACTS, "captures", "ok")
    sample_file = sorted(f for f in os.listdir(ok_caps)
                         if f.endswith(".json"))[0]
    sample_rec = json.load(open(os.path.join(ok_caps, sample_file)))
    fresh_cfg = json.load(open(CONFIG))
    controls = ef.negative_controls(sample_rec["request_raw"],
                                    fresh_cfg["envelope"])
    # Positive confirmation (Alex's reinspection 2): valid JSON
    # whitespace, strings containing bracket characters, valid
    # escapes and correctly nested composites must still PASS
    # under the full-grammar scanner.
    model_tok = None
    for m in ef.scan_top_level(sample_rec["request_raw"]):
        if m["name"] == "model":
            model_tok = m["value_token"]
    synthetic = (
        '{"model": ' + model_tok + ', "unrelated": "a]b{c}d", '
        '"deep": {"a": [1, {"b": "}"}, [true, null, -0.5e+10]]}, '
        '"esc": "tab\\t uni\\u0041", "ws" : [ 1 , 2 ]}')
    pos = ef.verify_envelope(
        synthetic, {"model": fresh_cfg["envelope"]["model"]})
    positives = [{
        "control": "valid_complex_document_accepted",
        "expected": "accepted",
        "accepted": pos["passed"],
        "passed": bool(pos["passed"]),
        "detail": "; ".join(pos["failures"][:2]),
    }]
    fid_passed = all(s["passed"] for s in FIDELITY_SCENARIOS) and \
        all(c["passed"] for c in controls) and \
        all(p["passed"] for p in positives)
    fid_art = {"artefact": "c5-17-envelope-fidelity",
               "double_id": dbl.DOUBLE_ID,
               "frozen_config_sha256": PINNED_CONFIG_SHA256,
               "canonicalisation": ef.canonicalisation_info(),
               "scenarios": FIDELITY_SCENARIOS,
               "negative_controls": controls,
               "positive_controls": positives,
               "passed": fid_passed}
    with open(os.path.join(ARTEFACTS,
                           "c5-17-envelope-fidelity.json"), "w") as f:
        json.dump(fid_art, f, indent=1)
    print(f"c5-17-envelope-fidelity: "
          f"{'PASS' if fid_passed else 'FAIL'} "
          f"({sum(s['passed'] for s in FIDELITY_SCENARIOS)}/"
          f"{len(FIDELITY_SCENARIOS)} scenarios, "
          f"{sum(c['passed'] for c in controls)}/{len(controls)} "
          f"negative controls, "
          f"{sum(p['passed'] for p in positives)}/{len(positives)} "
          f"positive controls)")
    results.append({"scenario": "c5-17-envelope-fidelity",
                    "passed": fid_passed})

    summary = {"double_id": dbl.DOUBLE_ID,
               "scenarios": {r["scenario"]: r["passed"] for r in results},
               "all_passed": all(r["passed"] for r in results)}
    with open(os.path.join(ARTEFACTS, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("ALL:", "PASS" if summary["all_passed"] else "FAIL")
    server.shutdown()
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

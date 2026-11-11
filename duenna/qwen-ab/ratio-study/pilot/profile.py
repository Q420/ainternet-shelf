"""Worker capability profiles: schema, derivation,
selection, cold start. Ratio-study pilot construction
(Alex-authorised build; execution NOT authorised).
Pure stdlib; no model calls."""
import hashlib, json

CONFIDENCE_LADDER = ["NONE", "LOW", "MEDIUM", "HIGH"]
# LOW: pilot-scale evidence (n=1 per cell), adjudicated.
# MEDIUM: >=3 independent matched-variant observations,
# consistent, adjudicated. HIGH: replicated across
# batteries, adjudicated. This pilot can mint LOW only.

COLD_START = {
    "allocation": "highest mechanical coverage the map "
                  "allows per operation (R3-equivalent)",
    "constraints": "full reciprocal constraint set",
    "probes": "adoption probes on all judgment classes",
    "scoring": "independent (J) on every output",
    "basis": "unknown is treated as untrusted, never "
             "as capable; evidence accrues from here",
}

def profile_header(worker_id, model, foundation_sha):
    return {"worker_id": worker_id, "model": model,
            "runtime": {"temperature": 0,
                        "foundation_sha256": foundation_sha},
            "profile_version": "0.1-provisional"}

def check_binding(profile, model, foundation_sha):
    """Version binding: a changed model or runtime must
    not silently inherit the profile."""
    h = profile["header"]
    return (h["model"] == model and
            h["runtime"]["foundation_sha256"] == foundation_sha)

def derive_entries(observations):
    """observations: adjudicated per-(task, op-class)
    records {task, op_class, worker_correct, system_correct,
    critical_failure}. Pilot derivation rules:
    - demonstrated: observed, worker_correct in all
      observations, no critical failure -> PROVISIONAL,
      confidence LOW (n=1 scale cannot mint more).
    - weak: any worker_correct False or critical failure.
    - unknown: no observation (never emitted here;
      callers mark unobserved areas unknown)."""
    entries = {}
    for o in observations:
        key = (o["task"], o["op_class"])
        e = entries.setdefault(key, {
            "task": o["task"], "op_class": o["op_class"],
            "status": "demonstrated", "confidence": "LOW",
            "provisional": True, "evidence": []})
        e["evidence"].append(o.get("evidence_ref", "run"))
        if not o["worker_correct"] or o.get("critical_failure"):
            e["status"] = "weak"
    return list(entries.values())

def select(job_ops, profile):
    """job_ops: [{operation, map_path, weakness_class}]
    Returns a recorded selection per operation.
    Rules: demonstrated -> the map's level for the op;
    weak -> apply the weakness class's constraint
    template (raises mechanical coverage one step where
    the map allows); unknown / missing profile -> cold
    start. Every selection carries its basis."""
    entries = {}
    if profile:
        for e in profile.get("entries", []):
            entries[(e["task"], e["op_class"])] = e
    out = []
    for op in job_ops:
        e = entries.get((op["task"], op["op_class"]))
        if profile is None or e is None:
            out.append({**op, "decision": COLD_START["allocation"],
                        "basis": "cold start: no profile entry"})
        elif e["status"] == "weak":
            out.append({**op, "decision": "constraint template: "
                        + op.get("weakness_class", "general"),
                        "basis": "profile: weak (evidence-backed)"})
        elif e["status"] == "unknown-untested":
            out.append({**op, "decision": COLD_START["allocation"],
                        "basis": "profile: unknown-untested"})
        else:
            out.append({**op, "decision": op["map_path"],
                        "basis": "profile: demonstrated (LOW, provisional)"})
    return out

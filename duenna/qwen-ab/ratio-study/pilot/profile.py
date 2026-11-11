"""Worker capability profiles v2 — construction package.
Alex's inspection corrections applied: full runtime
binding, enforced versioned templates, fail-closed
selection, auditable evidence structure. Stdlib only."""
import hashlib, json, os

CONFIDENCE_LADDER = ["NONE", "LOW", "MEDIUM", "HIGH"]

TEMPLATES = {
  "TPL-MECH-CLASSIFY-PROBE": {
    "version": 1, "weakness_class": "label-adoption",
    "requires": ["mechanical classification computed "
                 "independently", "adoption probe with hard "
                 "capture order", "three records kept separate"]},
  "TPL-MECH-EXTRACTION-REFERENCE": {
    "version": 1, "weakness_class": "record-composition",
    "requires": ["extraction mechanically owned",
                 "reference insertion by the machinery",
                 "field verification before emission"]},
  "TPL-GATE-BOUNDED-RETRY": {
    "version": 1, "weakness_class": "first-attempt-contract",
    "requires": ["release gate on first attempt",
                 "one bounded retry under frozen criteria",
                 "first-attempt result reported separately"]},
  "TPL-COLD-START": {
    "version": 1, "weakness_class": "unknown",
    "requires": ["highest map-allowed mechanical coverage",
                 "full reciprocal constraint set",
                 "adoption probes on judgment classes",
                 "independent scoring on every output"]},
}

TOOLS24_SHA = ("89a70606a7bbfeafb1fe7b610ff28fce4ec"
               "f0109ad2676520f519b63b4f4f9c0")

def tools_version():
    """Resolve the frozen tools24.py by HASH across the
    known layouts (workspace: ../v24; shelf:
    ../../v24 from the pilot package). A descriptive
    path is not verification — the digest must match."""
    import hashlib as _h
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [os.path.join(here, "..", "v24", "tools24.py"),
             os.path.join(here, "..", "..", "v24", "tools24.py")]
    root = os.environ.get("PILOT_SHELF_ROOT")
    if root:
        cands.append(os.path.join(root, "v24", "tools24.py"))
    for p in cands:
        if os.path.exists(p) and \
                _h.sha256(open(p, "rb").read()).hexdigest() == TOOLS24_SHA:
            return TOOLS24_SHA
    raise FileNotFoundError("no hash-verified tools24.py "
                            f"in {cands}")

def make_header(worker_id, system_prompt):
    return {
      "worker_id": worker_id,
      "provider": "Groq via custom.groq connector (chat CLI)",
      "model": "qwen/qwen3.8-27b",
      "model_revision": "as served by provider; no local "
                        "revision pin available",
      "decoding": {"temperature": 0, "reasoning_format": "hidden"},
      "system_prompt_sha256": hashlib.sha256(
          system_prompt.encode()).hexdigest(),
      "tools_version_sha256": tools_version(),
      "adapter": "run_ab.call_qwen -> groq chat CLI; "
                 "frozen Arm C machinery in run_c",
      "foundation_sha256":
        "c3b917fea035ffc6c3c6ac17e36daac1892482720052c18f0ed0e2b67ae97a9a",
      "foundation_version": "V2.4.8 / FOUNDATION v9 (36 components)",
      "profile_version": "0.2-provisional"}

BINDING_FIELDS = ["worker_id", "provider", "model",
  "model_revision", "decoding", "system_prompt_sha256",
  "tools_version_sha256", "adapter", "foundation_sha256",
  "foundation_version"]

def check_binding(profile, expected_header):
    """Every binding field must match exactly; a change
    that could materially affect capability voids silent
    inheritance."""
    h = profile.get("header", {})
    return all(h.get(f) == expected_header.get(f)
               for f in BINDING_FIELDS)

def validate_profile(profile):
    defects = []
    if not isinstance(profile, dict):
        return ["profile is not an object"]
    h = profile.get("header", {})
    for f in BINDING_FIELDS:
        if f not in h:
            defects.append(f"header missing {f}")
    for e in profile.get("entries", []):
        for f in ("task", "op_class", "status", "confidence",
                  "confidence_basis", "sample_count",
                  "provisional", "evidence"):
            if f not in e:
                defects.append(f"entry missing {f}: "
                               f"{e.get('task')}/{e.get('op_class')}")
        if e.get("status") not in ("demonstrated", "weak",
                                   "unknown-untested"):
            defects.append(f"bad status: {e.get('status')}")
    return defects

def derive_entries(observations):
    """Observations are adjudicated records:
    {task, op_class, level, conditions, worker_result
    ('correct'|'incorrect'), adjudication, critical_failures,
    evidence_refs}. Entries preserve the full audit trail:
    sample count, basis, adjudication, critical failures,
    evidence references. Confidence: LOW at pilot scale
    (n<3); MEDIUM eligible only at n>=3 consistent +
    adjudicated; HIGH never minted by derivation here."""
    grouped = {}
    for o in observations:
        grouped.setdefault((o["task"], o["op_class"]), []).append(o)
    entries = []
    for (task, op), obs in sorted(grouped.items()):
        weak = any(o["worker_result"] != "correct" or
                   o["critical_failures"] for o in obs)
        n = len(obs)
        # Consistency condition (Alex): MEDIUM requires
        # n>=3 AND consistent (no failure) AND adjudicated.
        # Any failure caps confidence at LOW at any n.
        if weak:
            conf, basis = "LOW", (f"n={n}; failure observed — "
                "consistency condition unmet, capped at LOW")
        elif n >= 3:
            conf, basis = "MEDIUM", (f"n={n} consistent "
                "adjudicated observations")
        else:
            conf, basis = "LOW", (f"n={n}; pilot scale caps "
                "at LOW")
        entries.append({
          "task": task, "op_class": op,
          "status": "weak" if weak else "demonstrated",
          "confidence": conf,
          "confidence_basis": basis,
          "sample_count": n, "provisional": True,
          "levels_observed": sorted({o["level"] for o in obs}),
          "adjudication": sorted({o["adjudication"] for o in obs}),
          "critical_failures":
            [c for o in obs for c in o["critical_failures"]],
          "evidence_class":
            "legacy-unbound" if any(
                o.get("binding_status") == "legacy-unbound"
                for o in obs) else "bound",
          "evidence": [r for o in obs for r in o["evidence_refs"]]})
    return entries

def _cold(op, basis):
    t = TEMPLATES["TPL-COLD-START"]
    return {**op, "decision": "cold start",
            "template": "TPL-COLD-START", "template_version": 1,
            "requires": t["requires"], "basis": basis}

def select(job_ops, profile, expected_header):
    """Fail-closed selection. Any defect — malformed
    profile, binding mismatch, missing template — puts
    EVERY operation on cold start and records why."""
    defects = validate_profile(profile) if profile else ["no profile"]
    if profile and not check_binding(profile, expected_header):
        defects = defects + ["binding mismatch"]
    if defects:
        return [_cold(op, "fail-closed: " + "; ".join(defects))
                for op in job_ops]
    entries = {(e["task"], e["op_class"]): e
               for e in profile.get("entries", [])}
    out = []
    for op in job_ops:
        e = entries.get((op["task"], op["op_class"]))
        if e is None or e["status"] == "unknown-untested":
            out.append(_cold(op, "no demonstrated entry"))
        elif e["status"] == "weak":
            tpl = next((k for k, v in TEMPLATES.items()
                        if v["weakness_class"] ==
                        op.get("weakness_class")), None)
            if tpl is None:
                out.append(_cold(op, "weak but no template "
                                     "for weakness class"))
            elif e.get("evidence_class") == "legacy-unbound":
                t = TEMPLATES[tpl]
                out.append({**op, "decision": "template",
                            "template": tpl,
                            "template_version": t["version"],
                            "requires": t["requires"],
                            "basis": "legacy-unbound weakness "
                                     "hypothesis — support may "
                                     "be added, never removed; "
                                     f"evidence {e['evidence']}"})
            else:
                t = TEMPLATES[tpl]
                out.append({**op, "decision": "template",
                            "template": tpl,
                            "template_version": t["version"],
                            "requires": t["requires"],
                            "basis": f"profile weak: {op['task']}/"
                                     f"{op['op_class']}; evidence "
                                     f"{e['evidence']}"})
        elif e.get("evidence_class") == "legacy-unbound":
            # Legacy rule: unbound historical evidence may
            # justify ADDING support (weak -> template,
            # handled above) but never REDUCING coverage.
            out.append(_cold(op, "legacy-unbound evidence: "
                "a demonstrated claim from unbound history "
                "cannot justify reduced coverage"))
        else:
            out.append({**op, "decision": op["map_path"],
                        "template": None,
                        "basis": "profile demonstrated "
                                 f"({e['confidence']}, provisional)"})
    return out

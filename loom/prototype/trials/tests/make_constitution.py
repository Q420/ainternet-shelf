#!/usr/bin/env python3
"""Generate the constitution annex (Rev 4 SS8, SS14): exact candidate pins
read from the routes' actual catalogues, contamination determinations on
SS8's three grounds, validator versions, the precommitted randomized
schedule, timeout, thresholds, and artifact pins."""
import hashlib, json, random, subprocess, sys

T = "."
def sha(b): return hashlib.sha256(b).hexdigest()

gem = json.load(open("evidence/catalogues/gemini-models.json"))
groq = json.load(open("evidence/catalogues/groq-models.json"))
nvi = json.load(open("evidence/catalogues/nvidia-models.json"))
gem_e = next(m for m in gem["models"] if m["name"] == "models/gemini-2.5-flash")
groq_e = next(m for m in groq["data"] if m["id"] == "qwen/qwen3.8-27b")
nvi_e = next(m for m in nvi["data"] if m["id"] == "mistralai/mistral-large-4-1t-a52b")

annex_a = open("instruments/annex_a.txt", "rb").read()
profile = open("instruments/gate_schema_profile_v2.txt", "rb").read()
ajv_v = json.loads(subprocess.run(["node", "-e",
    "console.log(JSON.stringify({ajv:require('./validator_js/node_modules/ajv/package.json').version,'ajv-formats':require('./validator_js/node_modules/ajv-formats/package.json').version,node:process.version}))"],
    capture_output=True, text=True).stdout)
import jsonschema
from importlib.metadata import version as pkg_version

CONTAM = {
    "ground_1_design_or_examination_seat": {
        "result": "not exposed",
        "basis": "The instrument and specification were designed/examined by the Remmy seat (Claude lineage) and the Vane seat (ChatGPT lineage) in recorded sessions. None of the three pinned models is either seat's model, and none served in any recorded design, drafting, or examination session for this instrument."},
    "ground_2_material_supplied_in_recorded_session": {
        "result": "not exposed",
        "basis": "No recorded session supplied Annex C, Annex D, the six-region fixture, accepted-run histories, prior trial outputs (none exist), or this brief's scoring provisions to any of the three pinned models."},
    "ground_3_provider_documents_training_use": {
        "result": "not exposed on the documents read",
        "basis": "No provider document read for these routes states that this material forms part of the pinned model version's training or fine-tuning data. Groq's Services Agreement bars training use of inputs/outputs absent explicit permission. Google's free-tier terms permit Google to use API content to improve its products: that concerns content submitted through the API going forward, is not documentation that the pinned version was trained on this material, and is recorded here so the certificate says exactly what it covers. What is certified is absence of KNOWN or DEMONSTRABLE exposure on these grounds, not the metaphysical absence of any possible exposure (Rev 4 SS8)."},
}

candidates = [
    {"route": "gemini", "model_id": "gemini-2.5-flash",
     "catalogue_entry": gem_e,
     "provider_version": gem_e.get("version"),
     "inference_configuration": {"generationConfig": {"temperature": 1.0}},
     "contamination_determination": CONTAM},
    {"route": "groq", "model_id": "qwen/qwen3.8-27b",
     "catalogue_entry": groq_e,
     "provider_version": groq_e.get("version", "not exposed by the Groq catalogue entry; the exact model id, owner, and catalogue snapshot date are pinned instead"),
     "inference_configuration": {"temperature": 1.0, "max_tokens": 4096, "reasoning_format": "hidden"},
     "contamination_determination": CONTAM},
    {"route": "nvidia", "model_id": "mistralai/mistral-large-4-1t-a52b",
     "catalogue_entry": nvi_e,
     "provider_version": nvi_e.get("version", "not exposed by the NVIDIA catalogue entry; the exact model id and catalogue snapshot date are pinned instead"),
     "inference_configuration": {"temperature": 1.0, "max_tokens": 4096},
     "contamination_determination": CONTAM},
]

seed = 20261121
sched = [(c["route"], i) for c in candidates for i in range(1, 21)]
random.Random(seed).shuffle(sched)
schedule = [{"position": n + 1, "route": r, "trial_index": i} for n, (r, i) in enumerate(sched)]

annex = {
    "document": "Conformance gate round — constitution annex (build round, 2026-11-21)",
    "status": "Pinned before any trial. NO TRIALS HAVE BEEN RUN. This annex pins the round so trials CAN be run under it in a later, separately authorized step.",
    "candidates": candidates,
    "trials_per_candidate": 20,
    "thresholds": {"schema_valid_rate_min": 0.90, "task_adequacy_rate_min": 0.75, "source": "Rev 9 SS1"},
    "timeout": {"seconds_per_trial": 120, "one_request_no_retry": True, "source": "Rev 4 SS6"},
    "artifacts": {
        "annex_a_instruction": {"source": "Rev 9 Annex A (spec blob 6a7e3d54, commit d7d65c96)",
                                "bytes": len(annex_a), "sha256": sha(annex_a), "file": "instruments/annex_a.txt"},
        "gate_schema_profile": {"artifact": "loom/gate-schema/annex-a/1", "version": 2,
                                "bytes": len(profile), "sha256": sha(profile),
                                "pinned_value": "bdb0ad70cd40c0ed61a0f05b2e2c66a87021df28c4f5b81e2c7400d5d25231ef",
                                "hash_matches_pin": sha(profile) == "bdb0ad70cd40c0ed61a0f05b2e2c66a87021df28c4f5b81e2c7400d5d25231ef",
                                "file": "instruments/gate_schema_profile_v2.txt"},
        "gate_validation_profile": "Rev 4 SS4 (design brief blob 5f74b563)",
        "gate_schema_json": {"file": "instruments/gate_schema.json", "sha256": sha(open("instruments/gate_schema.json", "rb").read())},
    },
    "validators": {
        "validator_1_python": {"library": "jsonschema", "version": pkg_version("jsonschema"),
                               "python": sys.version.split()[0], "draft": "2020-12", "format_assertion": True},
        "validator_2_ajv": {"library": "ajv", "version": ajv_v["ajv"], "ajv-formats": ajv_v["ajv-formats"],
                            "node": ajv_v["node"], "draft": "2020-12", "format_assertion": True},
        "independence": "No shared custom validation code; each implements the gate-schema contract and SS4 cross-field rules in its own code (validator_py/validate_py.py, validator_js/validate_js.js). The only shared artifacts are the pinned texts.",
    },
    "schedule": {"seed": seed, "note": "Precommitted before any dispatch; candidate order randomized with the recorded seed (Rev 4 SS10).",
                 "dispatches": schedule},
    "excluded_seat": "The examiner's own model seat (Vane, ChatGPT lineage) is excluded from candidacy on contamination ground 1 and the SS1 scorer-independence rule; it is not among the three routes.",
}
json.dump(annex, open("constitution_annex.json", "w"), indent=1)
print("constitution annex written; profile hash matches pin:", annex["artifacts"]["gate_schema_profile"]["hash_matches_pin"])
print("schedule dispatches:", len(schedule))

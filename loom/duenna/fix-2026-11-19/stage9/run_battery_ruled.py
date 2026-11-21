#!/usr/bin/env python3
"""Stage 9 — the battery run under Ben's subject ruling.

The Stage 9 freeze of 2026-11-20 (STAGE9BATT-20261120-003)
refused: the pinned subject ``openai/gpt-oss-20b`` (Alex's pin
ruling, 2026-11-17) is not served by the NVIDIA endpoint — the
mandatory K2 verification call returned HTTP 410 and the pin is
absent from the key's live model list (DR-27).

Ben ruled at 2026-11-20 05:27 MST, in his own words: "Use any
available NVIDIA model." That ruling is the subject authority
for THIS run. It supersedes waiting on the pinned subject; the
comparability trade was named before he ruled (a new subject
starts a new baseline rather than continuing attempt 3's
measurement history).

This driver changes no assembly code. The assembly reads its
subject from the module-level ``assembly.SUBJECT`` when it
builds the frozen draft (the same seam run_battery.py's stock
driver uses); this driver rebinds that one value to the subject
selected below, and supplies its own ``models_check`` — the
lane's designed evidence seam — so the run record's
SUBJECT_VERIFICATION_EVIDENCE carries the full served list, the
ruling citation, and the selection basis, not just a count.

Selection (deterministic, from the live list read at run time):
  (a) same family as the pin — an openai/gpt-oss model, closest
      declared size to the pin's 20B;
  (b) otherwise the closest served open-weight reasoning model
      in class/scale to gpt-oss-20b (21B MoE, ~3.6B active),
      by the ordered preference list below;
  (c) otherwise the strongest served open-weight reasoning
      model, by the ordered list below.
The frozen STEP6 set and bar are untouched: pins.verify_freeze()
runs inside the assembly exactly as for the refused freeze.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import assembly           # noqa: E402
import transport as live  # noqa: E402

PIN = "openai/gpt-oss-20b"
RULING = {
    "text": "Use any available NVIDIA model.",
    "ruled_by": "Ben",
    "ruled_at": "2026-11-20 05:27 MST",
    "scope": "subject selection for the Stage 9 scored run",
    "supersedes_for_this_run": "waiting on the pinned subject",
    "original_pin": {
        "model": PIN,
        "authority": "Alex's pin ruling, 2026-11-17"},
    "pin_conflict_answered":
        "DR-27 — freeze refused at STAGE9BATT-20261120-003 "
        "(verification HTTP 410; pin absent from live list)",
}

# Step (b): closest in class/scale to gpt-oss-20b (open-weight
# reasoning, 21B MoE / ~3.6B active), in preference order.
STEP_B = [
    ("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
     "open-weight reasoning MoE, 30B total / 3B active — the "
     "only served model that is simultaneously open-weight, "
     "reasoning-named, and in the pin's scale class"),
    ("nvidia/nemotron-3.5-lightning-30b-a3b",
     "open-weight MoE, 30B total / 3B active — same family and "
     "scale class as the first preference, not reasoning-named"),
    ("google/gemma-4-31b-it",
     "open-weight 31B instruction model — scale class matches, "
     "not a reasoning model"),
    ("meta/muse-glimmer-30b",
     "30B total — scale class matches; class/provenance not "
     "established from the list"),
]
# Step (c): strongest served open-weight reasoning models.
STEP_C = [
    ("moonshotai/kimi-k3.1-pro", "frontier-scale open-weight "
     "reasoning model"),
    ("nvidia/nemotron-3-ultra-550b-a55b", "550B open-weight "
     "reasoning flagship"),
    ("mistralai/mistral-large-4-1t-a52b", "1T-class open-weight "
     "model"),
    ("z-ai/glm-5.3-flash", "open-weight GLM reasoning model"),
    ("minimaxai/minimax-m3.1-flash", "open-weight MiniMax "
     "reasoning model"),
    ("stepfun-ai/step-5-preview", "open-weight Step reasoning "
     "model"),
]


def _declared_size_b(model_id):
    """Parse a trailing size token ('20b', '1t') to billions."""
    tail = model_id.rsplit("-", 1)[-1].lower()
    try:
        if tail.endswith("t"):
            return float(tail[:-1]) * 1000.0
        if tail.endswith("b"):
            return float(tail[:-1])
    except ValueError:
        return None
    return None


def select_subject(ids):
    """Apply the preference order to the served list. Returns
    (selected, step, basis)."""
    if PIN in ids:
        return PIN, "pin", "the pinned subject itself is served"
    family = [i for i in ids if i.startswith("openai/gpt-oss")]
    if family:
        def distance(mid):
            size = _declared_size_b(mid)
            return abs(size - 20.0) if size is not None else 1e9
        chosen = sorted(family, key=distance)[0]
        return chosen, "a", (
            f"same family as the pin (openai/gpt-oss); closest "
            f"declared size to the pin's 20B among {family}")
    for model_id, basis in STEP_B:
        if model_id in ids:
            return model_id, "b", basis
    for model_id, basis in STEP_C:
        if model_id in ids:
            return model_id, "c", basis
    return None, None, "no served model matched any preference step"


def _read_list():
    listing = live.list_models()
    if "data" in listing:
        return [m.get("id") for m in listing["data"]], None
    return None, listing.get("error")


def main():
    reads = []
    ids = None
    for attempt in (1, 2):
        ids, err = _read_list()
        reads.append({"attempt": attempt,
                      "model_count": len(ids) if ids else None,
                      "error": err})
        if ids:
            break
        time.sleep(5)
    if not ids:
        print(json.dumps({"outcome": "LIST_READ_FAILED",
                          "reads": reads}, indent=2))
        return 1

    selected, step, basis = select_subject(ids)
    if selected is None:
        print(json.dumps({"outcome": "NO_SUBJECT_AVAILABLE",
                          "reads": reads, "served_model_ids": ids},
                         indent=2))
        return 1

    authority = {
        "ruling": RULING,
        "selection": {
            "selected_model_id": selected,
            "preference_step": step,
            "basis": basis,
            "pin_served": PIN in ids,
            "selected_from_list_read": reads,
        },
        "served_model_ids": ids,
    }

    # The assembly's one subject seam: the draft, the lane and
    # the summary all read this module value.
    assembly.SUBJECT = selected
    transport = live.LiveTransport(selected)

    def models_check():
        fresh, err = _read_list()
        at_freeze = {"error": err} if fresh is None else {
            "listed": selected in fresh,
            "model_count": len(fresh)}
        return {"listed": selected in ids,
                "model_count": len(ids),
                "served_model_ids": ids,
                "subject_authority": authority,
                "at_freeze_read": at_freeze}

    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    runs_root = os.path.join(_HERE, "runs")
    os.makedirs(runs_root, exist_ok=True)
    existing = [d for d in os.listdir(runs_root)
                if d.startswith(f"STAGE9BATT-{date}-")]
    package_name = f"STAGE9BATT-{date}-{len(existing) + 1:03d}"

    summary = assembly.run_battery(
        runs_root=runs_root, package_name=package_name,
        transport=transport, models_check=models_check)

    run_dir = os.path.dirname(summary["record"])
    with open(os.path.join(run_dir, "subject-ruling.json"),
              "wb") as f:
        f.write(json.dumps(
            {"run_package": package_name,
             "run_id": summary.get("run_id"),
             "outcome": summary.get("outcome"),
             **authority}, indent=2).encode("utf-8"))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

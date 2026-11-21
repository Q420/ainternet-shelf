#!/usr/bin/env python3
"""The scripted stub subject (Stage 5 Build Spec Rev 22 §3.7).

A deterministic test double standing behind the adapter's
harness-facing boundary: it implements the complete() contract's
harness side, returning declared outputs per (tree, step,
attempt) from a pinned stub script — a well-formed output, a
malformed output, a refusal-shaped output, a truncation-shaped
output, or a scripted ADAPTER_FAILURE. It is test scaffolding
outside the run path: selected by pinned test configuration in
scratch contexts only, visibly named in the run's RUN_STARTED
block; its records are labelled synthetic and are never offered
as run evidence. No scored run can be configured to use it.
"""
import json
import pathlib


class StubSubject:
    def __init__(self, script_path, config_name):
        self.config_name = config_name
        self.script = json.loads(
            pathlib.Path(script_path).read_text(encoding="utf-8"))
        self.calls = []          # (tree_id, step_id, attempt)
        self.synthetic = True

    def complete(self, tree_id, step_id, attempt, messages):
        """The harness-facing complete() contract. Returns a dict:
        {kind: "output", raw_output, advance_clock_s} or
        {kind: "adapter_failure", detail, advance_clock_s}."""
        self.calls.append((tree_id, step_id, attempt))
        key = f"{tree_id}|{step_id}|{attempt}"
        entry = self.script.get("calls", {}).get(key)
        if entry is None:
            entry = self.script.get("default",
                                    {"kind": "output", "raw_output": ""})
        return {
            "kind": entry.get("kind", "output"),
            "raw_output": entry.get("raw_output", ""),
            "detail": entry.get("detail", ""),
            "advance_clock_s": entry.get("advance_clock_s", 0),
        }

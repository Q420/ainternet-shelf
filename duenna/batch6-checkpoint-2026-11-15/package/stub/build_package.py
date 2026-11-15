#!/usr/bin/env python3
"""Batch 6 package build tool — build-configuration enforcement for
test-only fault hooks (approved sheet C6-6; Rev 26 §5 G2; Rev 12 Item 6).

Two configurations:

  scoreable  The build that may be offered for inspection. REFUSES to
             build when the build-time flag PILOT_TORN_WRITE_INJECTOR
             is set in the environment, and never includes the
             torn-write injector module or the launcher's test hooks.
  scratch    The test build. With PILOT_TORN_WRITE_INJECTOR set, it
             includes the injector and compiles the launcher with
             PILOT_TEST_HOOKS. A scratch build is NOT scoreable, and
             its flag state says so.

Every build mechanically records its flag state (FLAG-STATE.json in
the package + the enforcement log): configuration, flag values,
whether the injector module is present in the package, whether the
launcher object carries test-hook strings, and the artefacts' hashes.
Absence in a scoreable build is demonstrated by this record and by
the scans the build itself performs — never merely asserted.

Exit codes: 0 built; 3 refused (flag/configuration violation); 1 error.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAUNCHER_SRC = Path.home() / "workspace/ssh-door/batch4/corrected/launcher-c3.c"
INJECTOR = HERE / "torn_write_injector.py"
HOOK_MARKERS = [b"PILOT_HOOK_", b"PILOT_TEST_HOOKS"]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(configuration: str, out_root: Path) -> int:
    flag = os.environ.get("PILOT_TORN_WRITE_INJECTOR")
    flag_set = flag is not None and flag not in ("", "0")
    log_lines = [f"configuration={configuration} PILOT_TORN_WRITE_INJECTOR={flag!r}"]
    if configuration == "scoreable" and flag_set:
        log_lines.append("REFUSED: PILOT_TORN_WRITE_INJECTOR is set in a scoreable build configuration")
        _record(out_root, configuration, log_lines, None)
        print("\n".join(log_lines))
        return 3
    if configuration not in ("scoreable", "scratch"):
        print(f"unknown configuration {configuration!r}")
        return 1
    pkg = out_root / f"pkg-{configuration}"
    pkg.mkdir(parents=True, exist_ok=True)
    # --- launcher object, configuration-appropriate flags
    hooks = configuration == "scratch"
    cmd = ["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
           "-c", str(LAUNCHER_SRC), "-o", str(pkg / "launcher.o")]
    if hooks:
        cmd.insert(1, "-DPILOT_TEST_HOOKS")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log_lines.append(f"launcher compile FAILED: {r.stderr.strip()[:200]}")
        _record(out_root, configuration, log_lines, None)
        print("\n".join(log_lines))
        return 1
    obj_bytes = (pkg / "launcher.o").read_bytes()
    hooks_present = any(m in obj_bytes for m in HOOK_MARKERS)
    log_lines.append(f"launcher object compiled (hooks {'ON' if hooks else 'OFF'}); hook markers present in object: {hooks_present}")
    if configuration == "scoreable" and hooks_present:
        log_lines.append("REFUSED: test-hook markers found in a scoreable launcher object")
        _record(out_root, configuration, log_lines, None)
        print("\n".join(log_lines))
        return 3
    # --- package contents: the injector ships only in scratch+flag
    injector_present = False
    if configuration == "scratch" and flag_set:
        (pkg / INJECTOR.name).write_bytes(INJECTOR.read_bytes())
        injector_present = True
        log_lines.append("torn-write injector INCLUDED (scratch configuration, flag set) — this package is NOT scoreable")
    else:
        stale = pkg / INJECTOR.name
        if stale.exists():
            stale.unlink()
        log_lines.append("torn-write injector absent from package")
    state = {
        "configuration": configuration,
        "scoreable": configuration == "scoreable" and not injector_present,
        "PILOT_TORN_WRITE_INJECTOR": bool(flag_set),
        "PILOT_TEST_HOOKS_compiled": hooks,
        "hook_markers_in_launcher_object": hooks_present,
        "injector_module_in_package": injector_present,
        "launcher_source": str(LAUNCHER_SRC),
        "launcher_source_sha256": sha256_hex(LAUNCHER_SRC.read_bytes()),
        "launcher_object_sha256": sha256_hex(obj_bytes),
    }
    (pkg / "FLAG-STATE.json").write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
    log_lines.append(f"flag state recorded: {state}")
    _record(out_root, configuration, log_lines, state)
    print("\n".join(log_lines))
    return 0


def _record(out_root: Path, configuration: str, log_lines, state):
    ev = out_root / "c6-6-evidence"
    ev.mkdir(parents=True, exist_ok=True)
    with open(ev / "ENFORCEMENT-LOG.txt", "a") as f:
        f.write("\n".join(log_lines) + "\n---\n")
    if state is not None:
        (ev / f"FLAG-STATE-{configuration}.json").write_text(
            json.dumps(state, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    configuration = sys.argv[1] if len(sys.argv) > 1 else "scoreable"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE
    sys.exit(build(configuration, out))

#!/usr/bin/env python3
"""C6-6 verification: build-configuration enforcement for test-only
fault hooks (PILOT_TORN_WRITE_INJECTOR + PILOT_TEST_HOOKS)."""
import json, os, subprocess, sys, tempfile
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
PY = sys.executable
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn(); RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

def run_build(configuration, out, flag=None):
    env = dict(os.environ)
    env.pop("PILOT_TORN_WRITE_INJECTOR", None)
    if flag is not None:
        env["PILOT_TORN_WRITE_INJECTOR"] = flag
    return subprocess.run([PY, str(B6 / "build_package.py"), configuration, str(out)],
                          capture_output=True, text=True, env=env)

OUT = Path(tempfile.mkdtemp(prefix="c6-6-builds-"))

@case("negative: scoreable build REFUSES with PILOT_TORN_WRITE_INJECTOR set")
def _():
    r = run_build("scoreable", OUT, flag="1")
    assert r.returncode == 3, (r.returncode, r.stdout)
    assert "REFUSED" in r.stdout

@case("scoreable build (flag unset): no injector, no hook markers, state recorded")
def _():
    r = run_build("scoreable", OUT)
    assert r.returncode == 0, r.stdout
    state = json.loads((OUT / "pkg-scoreable" / "FLAG-STATE.json").read_text())
    assert state["scoreable"] is True and state["injector_module_in_package"] is False
    assert state["hook_markers_in_launcher_object"] is False
    assert not (OUT / "pkg-scoreable" / "torn_write_injector.py").exists()

@case("scratch build with the flag: injector included, hooks on, NOT scoreable")
def _():
    r = run_build("scratch", OUT, flag="1")
    assert r.returncode == 0, r.stdout
    state = json.loads((OUT / "pkg-scratch" / "FLAG-STATE.json").read_text())
    assert state["injector_module_in_package"] is True and state["scoreable"] is False
    assert state["hook_markers_in_launcher_object"] is True
    assert (OUT / "pkg-scratch" / "torn_write_injector.py").exists()

@case("the injector itself writes a torn tail deterministically")
def _():
    sys.path.insert(0, str(B6))
    import torn_write_injector as twi
    target = Path(OUT) / "torn.bin"
    payload = b'{"seq": 1, "event": "complete-line"}\n'
    written = twi.torn_line(target, payload, cut=17)
    data = target.read_bytes()
    assert written == 17 and data == payload[:17] and not data.endswith(b"\n")

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)

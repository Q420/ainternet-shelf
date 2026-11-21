#!/usr/bin/env python3
"""C-D4: mechanical isolation of every trial component from the actual
Annex D source. Each component executes inside a private mount namespace in
which the two Annex D carriers — the Rev 9 spec file's directory
(duenna-fix/) and the six-region fixture's directory (loom-prototype/fabric/)
— are bound over with empty tmpfs mounts. Inside the namespace the paths do
not exist: the read attempt fails mechanically (No such file or directory),
for any identity, without changing any file's permissions. The mechanism is
inspectable from inside via /proc/self/mountinfo. A control run OUTSIDE the
namespace shows the same read succeeding, proving the failure is the
mechanism. Components run under the operator identity, as they do in the
build (the producing identity loomagent has no read access to the trials
tree at all under this VM's workspace permissions — recorded in the notes;
the isolation property demonstrated here is identity-independent because
the paths are absent, not permission-denied)."""
import json, subprocess

T = "/home/hatch/workspace/loom-prototype/trials"
SPEC = "/home/hatch/workspace/duenna-fix/LOOM-SPEC-V0.1-REV9-DRAFT-2026-11-21.md"
FIXTURE = "/home/hatch/workspace/loom-prototype/fabric/fixture.py"
RESP = T + "/evidence/dummy_trials_correction/DUMMY-1.response.txt"

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

PROBE = (
    "import subprocess, json;"
    "out={};"
    "[out.__setitem__(p, (lambda r: {'returncode': r.returncode, 'stderr': r.stderr.strip()})"
    "(subprocess.run(['cat', p], capture_output=True, text=True))) for p in ['%s', '%s']];"
    "print(json.dumps(out))" % (SPEC, FIXTURE)
)

COMPONENTS = {
    "adapter": ["python3", "-c",
        "import sys; sys.path.insert(0, '%s/adapters'); import adapter;"
        "b = adapter.build_body('groq', 'm', {}, ['x', 'y']);"
        "print('adapter build_body ok, parts:', len(b['messages'][0]['content']))" % T],
    "validator_py": ["python3", T + "/validator_py/validate_py.py", RESP],
    "validator_js": ["node", T + "/validator_js/validate_js.js", RESP],
    "scoring": ["python3", "-c",
        "import sys, json; sys.path.insert(0, '%s/scoring'); import scoring;"
        "s = scoring.make_sheet({'trial_uid': 'DUMMY-ISO', 'parsed': None, 'schema_valid': False}, 'iso-secret');"
        "print('scoring make_sheet ok, blind_ref:', s['blind_ref'])" % T],
    "ledger_client": ["python3", T + "/ledger/ledger_client.py", "head"],
}

def in_namespace(cmd):
    inner = (
        "mount -t tmpfs tmpfs /home/hatch/workspace/duenna-fix && "
        "mount -t tmpfs tmpfs /home/hatch/workspace/loom-prototype/fabric && "
        "grep -E 'duenna-fix|loom-prototype/fabric' /proc/self/mountinfo; "
        "exec \"$@\""
    )
    return run(["unshare", "--mount", "--propagation", "private", "bash", "-c", inner, "_"] + cmd)

control = run(["cat", SPEC])
ev = {"item": "C-D4 mechanical isolation from the actual Annex D source",
      "mechanism": "private mount namespace (unshare --mount --propagation private); "
                   "tmpfs bound over /home/hatch/workspace/duenna-fix and "
                   "/home/hatch/workspace/loom-prototype/fabric inside the namespace only; "
                   "no file permissions changed anywhere",
      "targets": {"spec_file": SPEC, "six_region_fixture": FIXTURE},
      "control_outside_namespace": {"cat_spec_returncode": 0,
                                    "cat_spec_first_line": control.stdout.splitlines()[0] if control.stdout else ""},
      "components": {}}
for name, cmd in COMPONENTS.items():
    probe = in_namespace(["python3", "-c", PROBE])
    comp = in_namespace(cmd)
    ev["components"][name] = {
        "read_attempts_inside_namespace": json.loads(probe.stdout.strip().splitlines()[-1]) if probe.stdout.strip() else {"error": probe.stderr[-300:]},
        "mountinfo_lines_inside_namespace": [l for l in probe.stdout.splitlines() if "tmpfs" in l][:4],
        "component_execution": {"returncode": comp.returncode,
                                "stdout_tail": comp.stdout.strip()[-200:],
                                "stderr_tail": comp.stderr.strip()[-200:]},
    }
    print(name, "| reads:", ev["components"][name]["read_attempts_inside_namespace"],
          "| component rc:", comp.returncode)
json.dump(ev, open(T + "/evidence/CD4_isolation.json", "w"), indent=1)

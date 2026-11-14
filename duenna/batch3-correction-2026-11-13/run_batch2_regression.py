#!/usr/bin/env python3
"""(j) Batch 2 regression runner (§4(j)).

Runs the Batch 2 checkpoint suites (test_batch2.py +
test_batch2_correction.py, 39 checks as cleared) against the
CORRECTED PILOT-TOOLS-01. The suites' assertions, counts and
expectations are byte-identical; the only changes are the two
mechanical translations the Rev 25 interface imposes on the
test copies, declared in the Batch 3 correction checkpoint
report:

  T1  every reference_insert(field, step, X) call site becomes
      reference_insert(field, step,
          {"form": "extracted", "operation_id": X});
  T2  the refusal-reason token MALFORMED_PRESENTATION becomes
      PRESENTATION_FORM (the Rev 24/25 name for the same
      refusal class).

Usage: run_batch2_regression.py <snapshot_dir> <batch1_work>
       <correction_work>
Exit 0 iff both suites exit 0 with no FAIL lines.
"""
import pathlib
import re
import shutil
import subprocess
import sys

SNAP, B1, CORR = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
ROOT = CORR.parent.parent
B2SRC = ROOT / "batch2"
REG = CORR / "regression"
if REG.exists():
    shutil.rmtree(REG)
REG.mkdir(parents=True)
shutil.copy(CORR / "pilot_tools.py", REG / "pilot_tools.py")


def transform(text):
    text = text.replace("MALFORMED_PRESENTATION",
                        "PRESENTATION_FORM")
    out, i = [], 0
    needle = "reference_insert("
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j + len(needle)])
        # scan the argument list to its matching close paren
        k = j + len(needle)
        depth, args, cur, in_str = 1, [], [], False
        while depth:
            ch = text[k]
            if in_str:
                cur.append(ch)
                if ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
                cur.append(ch)
            elif ch in "([{":
                depth += 1
                cur.append(ch)
            elif ch in ")]}":
                depth -= 1
                if depth:
                    cur.append(ch)
                elif ch == ")":
                    args.append("".join(cur))
            elif ch == "," and depth == 1:
                args.append("".join(cur))
                cur = []
            else:
                cur.append(ch)
            k += 1
        if len(args) == 3:
            third = args[2].strip()
            if not third.startswith('{"form"'):
                args[2] = ('{"form": "extracted", '
                           f'"operation_id": {third}}}')
        out.append(", ".join(a.strip() for a in args) + ")")
        i = k
    return "".join(out)


fails = 0
SOURCES = {}


def find_src(name):
    for cand in (B2SRC / "work" / name, B2SRC / "correction" / name,
                 B2SRC / name):
        if cand.exists():
            return cand
    raise SystemExit(f"Batch 2 suite not found: {name}")


for name, argv in (
        ("test_batch2.py", [SNAP, B1, str(REG)]),
        ("test_batch2_correction.py", [SNAP, B1, str(REG),
                                       str(REG)])):
    src = find_src(name).read_text(encoding="utf-8")
    dst = REG / name
    dst.write_text(transform(src), encoding="utf-8")
    r = subprocess.run([sys.executable, str(dst), *argv],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0 or "\nFAIL " in "\n" + r.stdout:
        fails += 1
print(f"REGRESSION {'OK' if not fails else 'FAILED'}")
sys.exit(1 if fails else 0)

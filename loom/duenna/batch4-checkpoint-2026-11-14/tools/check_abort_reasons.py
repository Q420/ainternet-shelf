#!/usr/bin/env python3
"""Cross-check the supervisor's ABORT reason numbering
against launcher-c3.c's RSN_* defines — identical numbering
is a Batch 4 build obligation (whole-plan Rev 8 Part C C2).
Exit 0 iff every reason matches, in both directions."""
import re
import sys

sys.path.insert(0, "/home/hatch/workspace/ssh-door/batch4/build")
from pilot_supervisor import ABORT_REASONS  # noqa: E402

src = open("/home/hatch/workspace/ssh-door/batch4/corrected/"
           "launcher-c3.c", encoding="utf-8").read()
launcher = {}
for name, num in re.findall(
        r"#define\s+RSN_([A-Z_]+)\s+(\d+)u", src):
    launcher[name] = int(num)

ok = True
for num, name in sorted(ABORT_REASONS.items()):
    if launcher.get(name) != num:
        print(f"MISMATCH supervisor {name}={num} "
              f"launcher={launcher.get(name)}")
        ok = False
for name, num in sorted(launcher.items()):
    if ABORT_REASONS.get(num) != name:
        print(f"MISMATCH launcher {name}={num} "
              f"supervisor={ABORT_REASONS.get(num)}")
        ok = False
print(f"ABORT reasons cross-check: {len(launcher)} launcher "
      f"reasons, {'IDENTICAL' if ok else 'DIVERGED'}")
sys.exit(0 if ok else 1)

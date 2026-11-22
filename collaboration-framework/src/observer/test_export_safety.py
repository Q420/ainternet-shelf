"""Observer export safety tests (Vane's examination corrections,
2026-11-21). Run: python3 test_export_safety.py

1. Read-only source access: exporting — or refusing — must leave the
   source database byte-for-byte unchanged, for a real run store, an
   empty file, and a missing path (which must not be created).
2. Script-context safety: a stored value containing a </script>
   sequence must remain inert data in the generated page — it must
   not terminate the script element at HTML parse time — while still
   round-tripping to the original string when the data is parsed.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fabric.engine import Engine  # noqa: E402
from fabric.store import EventStore  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def export(db, out):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, "export_events.py"), db, out],
        capture_output=True, text=True)


tmp = tempfile.mkdtemp()

# A real run store.
db = os.path.join(tmp, "run.db")
store = EventStore(db)
Engine.open_run(store, "safety-run")
before = digest(db)
out = os.path.join(tmp, "page.html")
r = export(db, out)
check("export of a sound run succeeds", r.returncode == 0, r.stderr.strip())
check("source database unchanged by export", digest(db) == before)
check("page was produced", os.path.exists(out))

# An empty file: refused, and still exactly the same empty file.
# (Digest captured before the attempt and compared after — Vane's
# test-hygiene note, 2026-11-21: comparing the file's digest with
# itself proved nothing.)
empty = os.path.join(tmp, "empty.db")
open(empty, "wb").close()
empty_before = digest(empty)
r = export(empty, os.path.join(tmp, "nope.html"))
check("empty store refused", r.returncode == 1)
check("empty file unchanged by refusal",
      os.path.getsize(empty) == 0 and digest(empty) == empty_before)

# A missing path: refused, and not created.
missing = os.path.join(tmp, "missing.db")
r = export(missing, os.path.join(tmp, "nope2.html"))
check("missing store refused", r.returncode == 1)
check("missing file not created by refusal", not os.path.exists(missing))

# Adversarial content: an event whose payload carries a script-breakout
# string. Appended through the store's own API, so the chain verifies
# and export proceeds — the string must arrive as inert data.
evil = "</script><script>alert('pwned')</script>"
store.append("DISCOVERY", "00000000-0000-4000-8000-000000000000", [],
             {"region_id": evil}, prev_hash=store.last()[1])
store.commit()
out2 = os.path.join(tmp, "page2.html")
r = export(db, out2)
check("export with adversarial payload succeeds", r.returncode == 0,
      r.stderr.strip())
page = open(out2, encoding="utf-8").read()
check("breakout sequence is not present as markup",
      "</script><script>alert" not in page)
check("page has exactly one script element",
      page.count("<script>") == 1 and page.count("</script>") == 1)
m = re.search(r"const DATA = (.*?);\n", page, re.S)
data = json.loads(m.group(1))
check("adversarial string round-trips as data",
      data["events"][-1]["payload"]["region_id"] == evil)

print()
print("OBSERVER EXPORT SAFETY:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)

"""Witness for the Nemotron name translator
(framework/nemotron_names.py; Ben's ruling, 2026-11-24:
"we create a separate translater for nemotron. he says
the dot, but the - is what is read").

The translator is an exact bijection built from the names
actually offered: canonical dotted names inside the
framework, dash forms on the NVIDIA route's wire, and no
guessing in either direction. This witness states, over
the framework's full standing vocabulary:

- every canonical name's wire form is exactly the name
  with each dot a dash, and the wire forms are the route
  names the provider's validation admits (letters, digits,
  underscores, dashes — the provider's own words, from
  the first Nemotron run's recorded 400 bodies);
- the mapping is injective over the vocabulary: distinct
  canonical names map to distinct wire forms, no wire
  form collides with a canonical name in the set, and
  every wire form translates back to exactly its own
  canonical name (the collision check);
- the reverse direction is map-only: a plausible dash
  name that was never offered is NOT guessed back, and
  a canonical dotted name is not a wire key — both stand
  untranslated, for the catalogue's closed-world
  determination to refuse;
- construction refuses a set the bijection cannot
  reverse exactly (two canonicals onto one wire form, a
  duplicated canonical);
- the route gate: a translator exists for the NVIDIA
  route alone — every other route, and no route, gets
  none, so the other routes' names travel untouched;
- the package derivation: the translator for a wake
  package is built over the package's own offered names,
  each once, in catalogue order.

Run: PYTHONPATH=src python3 tests/unit/test_nemotron_names.py
Exits 0 when every check passes.
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import nemotron_names as nn  # noqa: E402

FAILURES = []
CHECKS = [0]


def check(name, cond, detail=""):
    CHECKS[0] += 1
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


EXPECTED_WIRE = {
    "container.exec": "container-exec",
    "sandbox.list": "sandbox-list",
    "sandbox.read": "sandbox-read",
    "sandbox.read_range": "sandbox-read_range",
    "sandbox.search": "sandbox-search",
    "sandbox.write": "sandbox-write",
    "probe.lookup": "probe-lookup",
    "probe.note": "probe-note",
}

translator = nn.NameTranslator(nn.VOCABULARY)

check("the standing vocabulary is the expected eight "
      "names",
      set(nn.VOCABULARY) == set(EXPECTED_WIRE),
      f"{nn.VOCABULARY}")

for canonical, wire in EXPECTED_WIRE.items():
    check(f"wire form: {canonical} travels as {wire}",
          translator.to_wire(canonical) == wire and
          nn.wire_form(canonical) == wire)

check("every wire form is inside the provider's allowed "
      "alphabet (a-z, A-Z, 0-9, underscores, dashes — the "
      "provider's own validation words)",
      all(re.fullmatch(r"[A-Za-z0-9_-]+", w)
          for w in EXPECTED_WIRE.values()))

# The collision check: the mapping over the full standing
# vocabulary is injective and exactly reversible.
wires = [translator.to_wire(n) for n in nn.VOCABULARY]
check("collision check: the wire forms over the full "
      "vocabulary are pairwise distinct (injective)",
      len(set(wires)) == len(wires) == len(nn.VOCABULARY),
      f"{wires}")
check("collision check: no wire form equals a canonical "
      "name in the vocabulary",
      not (set(wires) & set(nn.VOCABULARY)),
      f"{set(wires) & set(nn.VOCABULARY)}")
check("collision check: every wire form translates back "
      "to exactly its own canonical name",
      all(translator.to_canonical(w) == n
          for n, w in zip(nn.VOCABULARY, wires)))

# The not-guessed-back rule.
check("not guessed back: a plausible dash name never "
      "offered translates to nothing — and even the "
      "near-miss sandbox-read-range is not the offered "
      "sandbox-read_range's wire form and is not "
      "corrected into it",
      translator.to_canonical("sandbox-delete") is None
      and translator.to_canonical("sandbox-read-range")
      is None)
check("not guessed back: a canonical dotted name is not "
      "a wire key — it stands as emitted, untranslated",
      translator.to_canonical("container.exec") is None)
check("not guessed back: an unoffered canonical name "
      "has no wire form invented for it",
      translator.to_wire("sandbox.delete") is None)

# Construction refuses a set the bijection cannot reverse.
for bad, label in (
        (["a.b", "a-b"], "two canonicals onto one wire "
                         "form"),
        (["a.b", "a.b"], "a duplicated canonical name"),
        (["ok.name", 7], "a non-string name")):
    raised = None
    try:
        nn.NameTranslator(bad)
    except ValueError as exc:
        raised = exc
    check(f"construction refuses {label}",
          raised is not None)

# The route gate.
check("route gate: the NVIDIA route gets a translator "
      "over the offered names",
      isinstance(nn.translator_for_route(
          nn.NVIDIA_ROUTE, nn.VOCABULARY), nn.NameTranslator))
for other in ("groq", None, "", "NVIDIA"):
    check(f"route gate: route {other!r} gets no "
          f"translator — its names travel untouched",
          nn.translator_for_route(other, nn.VOCABULARY)
          is None)

# The package derivation.
package = {"tools": [
    {"tool": "container.exec"},
    {"tool": "container.exec"},
    {"name": "sandbox.read"},
    {"tool": "probe.lookup"},
    {"unrelated": True},
    "not-an-entry",
]}
pt = nn.translator_for_package("nvidia", package)
check("package derivation: built over the package's own "
      "offered names, each once, in catalogue order",
      pt is not None and pt.canonical_names ==
      ("container.exec", "sandbox.read", "probe.lookup"),
      f"{pt.canonical_names if pt else None}")
check("package derivation: no translator off the "
      "NVIDIA route, and none for a tool-less package",
      nn.translator_for_package("groq", package) is None
      and nn.translator_for_package("nvidia", {"tools": []})
      is None
      and nn.translator_for_package("nvidia", {}) is None)

print(f"\n{CHECKS[0] - len(FAILURES)}/{CHECKS[0]} checks "
      f"passed")
if FAILURES:
    print("FAILURES:", *FAILURES, sep="\n  ")
    sys.exit(1)
print("ALL PASS")

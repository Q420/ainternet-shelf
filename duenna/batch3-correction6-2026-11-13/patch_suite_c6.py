#!/usr/bin/env python3
"""Correction 6 suite patch: NC3 + the divergence-set
expectation under the corrected driver."""
import pathlib

p = pathlib.Path.home() / "workspace/ssh-door/batch3-correction2" / \
    "test_batch3_correction2.py"
s = p.read_text()

def rep(old, new, name):
    global s
    assert s.count(old) == 1, f"anchor: {name} ({s.count(old)})"
    s = s.replace(old, new)
    print("OK", name)

rep('''ROUND 5 (plan BATCH3-CORRECTION5-PLAN, APPROVED
''', '''ROUND 6 / CORRECTION 6 (Ben's build-go, widget-bc2d030e;
plan Revs 2-4 APPROVED by Alex pb-mwfwudk0): the driver
implements §3.1; this suite adds NC3 (tree-role order) and
expects an EMPTY divergence set — the finding closed in
the records, asserted, not assumed.

ROUND 5 (plan BATCH3-CORRECTION5-PLAN, APPROVED
''', "docstring-r6")

rep('''chk("(NC2) negative control — a pack section replaced: the "
    "§3.1 derivation changes, proving it reads the pinned pack",
    _sensitive("replace"))
''', '''chk("(NC2) negative control — a pack section replaced: the "
    "§3.1 derivation changes, proving it reads the pinned pack",
    _sensitive("replace"))


def _nc3():
    import copy
    global TREES
    saved = TREES
    try:
        bad = copy.deepcopy(TREES)
        for t in bad["trees"]:
            if t["tree_id"] == "T02":
                for st in t["steps"]:
                    if st["step_id"] == "T02-STEP-01":
                        st["text"] = (
                            "STEP-01 — build a worksheet of the "
                            "examiner's finding lines, the "
                            "implementer's suite claim, the "
                            "adjudication's disposition line")
        TREES = bad
        try:
            derive_t02(1)
            return False
        except ValueError:
            return True
    finally:
        TREES = saved


chk("(NC3) negative control — the declared tree-role order "
    "perturbed in the loaded trees text: the derivation "
    "rejects, proving the class sequence is read from the "
    "pinned tree text", _nc3())
''', "nc3")

rep('''chk("(trace) all divergence identities are pairwise distinct "
    "(run_id, seq)",
    len({(d["run_id"], d["seq"]) for d in DIVERGENCES})
    == len(DIVERGENCES) == 7,
    f"{len(DIVERGENCES)} divergences")
''', '''chk("(trace) the divergence set is EMPTY under the "
    "corrected driver (Correction 6): the §3.1 finding is "
    "closed in the records this suite recomputes — asserted "
    "against the recomputation, not assumed",
    len(DIVERGENCES) == 0, f"{len(DIVERGENCES)} divergences")
''', "empty-set")

p.write_text(s)
print("suite patch c6 done")

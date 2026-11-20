"""The sabotage matrix (Stage 8).

For each mechanism in mechanisms.py: copy the stages 1-7 trees
to a scratch tree, apply the mechanism's patches there (anchors
re-verified in the scratch copy before replacement), run the
witness runner over the mechanism's suites, and diff every
test's outcome against the baseline. The real trees are never
patched.

Classification (K14, Step 7 rule):
- A claimed (fixture, mechanism) pair is EXERCISED when the
  fixture's baseline outcome is ok and its outcome under the
  neutralisation is not ok — the fixture fails when its target
  is removed, so its target was reached by it.
- It is NOT-EXERCISED when the fixture still passes with its
  target neutralised — the target was never reached by it,
  whatever the fixture's name or report claims.
- A joint-guard fixture claims a conjunction: it is
  EXERCISED-JOINT when it fails under the combined
  neutralisation of all its targets. Failing under a single
  target as well is recorded per pair.
- Any other test turning non-ok under a run is COLLATERAL,
  named individually — except Stage 4 exam fixtures under
  Stage 4 mechanism runs, whose own sabotage anchors the
  matrix patch may have consumed: those are INSTRUMENT
  INTERACTION, recorded separately, distinct from FAIL.
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # ~/workspace/duenna-fix
SCRATCH = os.path.join(HERE, "scratch")
RESULTS = os.path.join(HERE, "results")

sys.path.insert(0, HERE)
from mechanisms import MECHANISMS  # noqa: E402
import inventory  # noqa: E402


def load_baseline():
    baseline = {}
    for stage in range(1, 8):
        path = os.path.join(RESULTS, f"baseline-stage{stage}.jsonl")
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if "test_id" in row:
                    baseline[row["test_id"]] = row["outcome"]
    return baseline


def copy_tree(dst_root):
    if os.path.exists(dst_root):
        shutil.rmtree(dst_root)
    os.makedirs(dst_root)
    for stage in range(1, 8):
        src = os.path.join(ROOT, f"stage{stage}")
        dst = os.path.join(dst_root, f"stage{stage}")
        shutil.copytree(
            src, dst,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def apply_patches(dst_root, patches):
    """Apply (path, anchor, replacement, count) patches in the
    scratch tree. Returns a list of problems; empty is clean.
    A patch whose anchor does not verify in the scratch copy is
    NOT applied — the run is refused, not guessed."""
    problems = []
    for patch in patches:
        path = os.path.join(dst_root, patch["path"])
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        found = text.count(patch["anchor"])
        if found != patch["count"]:
            problems.append(
                f"{patch['path']}: anchor {found}x, "
                f"expected {patch['count']}x")
            continue
        text = text.replace(patch["anchor"], patch["replacement"])
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return problems


def run_suite(dst_root, stage):
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "witness_run.py"),
         os.path.join(dst_root, f"stage{stage}")],
        capture_output=True, text=True, timeout=600)
    outcomes = {}
    for line in proc.stdout.splitlines():
        row = json.loads(line)
        if "test_id" in row:
            outcomes[row["test_id"]] = row["outcome"]
    return outcomes, proc.stderr


def run_one(run_id, patches, suites, baseline):
    """One matrix run: scratch copy, patch, witness, diff."""
    dst_root = os.path.join(SCRATCH, run_id)
    copy_tree(dst_root)
    problems = apply_patches(dst_root, patches)
    result = {"run_id": run_id, "suites": suites,
              "patch_problems": problems, "changed": {}}
    if problems:
        result["refused"] = True
        shutil.rmtree(dst_root, ignore_errors=True)
        return result
    for stage in suites:
        outcomes, _stderr = run_suite(dst_root, stage)
        for test_id, outcome in sorted(outcomes.items()):
            base = baseline.get(test_id)
            if outcome != base:
                result["changed"][test_id] = {
                    "baseline": base, "under_sabotage": outcome,
                    "stage": stage}
        # A baseline test ABSENT from the sabotage run's
        # outcomes (collection error, witness gap) is a change,
        # never a silent pass.
        for test_id, base in sorted(baseline.items()):
            if base is not None and test_id not in outcomes \
                    and _stage_of_baseline(test_id) == stage:
                result["changed"][test_id] = {
                    "baseline": base, "under_sabotage": "MISSING",
                    "stage": stage}
    shutil.rmtree(dst_root, ignore_errors=True)
    return result


_BASELINE_STAGE = {}


def _stage_of_baseline(test_id):
    if not _BASELINE_STAGE:
        for stage in range(1, 8):
            path = os.path.join(RESULTS, f"baseline-stage{stage}.jsonl")
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    row = json.loads(line)
                    if "test_id" in row:
                        _BASELINE_STAGE[row["test_id"]] = stage
    return _BASELINE_STAGE.get(test_id)


def joint_groups():
    """Joint-guard fixtures grouped by their target set."""
    groups = {}
    for test_id, (targets, kind, _note) in inventory.ENTRIES.items():
        if kind == "joint-guard" and len(targets) >= 2:
            groups.setdefault(tuple(sorted(targets)), []).append(test_id)
    return groups


def run_matrix():
    baseline = load_baseline()
    os.makedirs(RESULTS, exist_ok=True)
    runs = {}
    for mech_id, mech in MECHANISMS.items():
        res = run_one(f"mech-{mech_id}", mech["patches"],
                      mech["suites"], baseline)
        res["mechanism"] = mech_id
        res["description"] = mech["description"]
        runs[mech_id] = res
        with open(os.path.join(RESULTS, f"matrix-{mech_id}.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
        print(f"{mech_id}: changed={len(res['changed'])} "
              f"refused={res.get('refused', False)}", flush=True)
    for targets, fixture_ids in sorted(joint_groups().items()):
        run_id = "joint-" + "+".join(
            t.replace(".", "_") for t in targets)
        patches = []
        suites = set()
        for t in targets:
            patches.extend(MECHANISMS[t]["patches"])
            suites.update(MECHANISMS[t]["suites"])
        res = run_one(run_id, patches, sorted(suites), baseline)
        res["joint_targets"] = list(targets)
        res["joint_fixtures"] = fixture_ids
        runs[run_id] = res
        with open(os.path.join(RESULTS, f"matrix-{run_id}.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
        print(f"{run_id}: changed={len(res['changed'])} "
              f"refused={res.get('refused', False)}", flush=True)
    return runs


def classify(runs):
    """Pair verdicts, collateral, instrument interaction —
    from the run records and the inventory's claims."""
    baseline = load_baseline()
    pairs = {}          # (fixture, mechanism) -> verdict
    collateral = {}     # run_id -> [test_ids]
    interaction = {}    # run_id -> [test_ids]
    summary_anomalies = []
    for test_id, (targets, kind, _n) in inventory.ENTRIES.items():
        for mech in targets:
            pairs[(test_id, mech)] = "NOT-EXERCISED"
    joint_verdicts = {}
    groups = joint_groups()
    for run_id, res in runs.items():
        changed = res.get("changed", {})
        if run_id.startswith("joint-"):
            targets = res["joint_targets"]
            for test_id in res["joint_fixtures"]:
                # Only fixtures that are joint-guard in the
                # CURRENT inventory take a joint verdict; a
                # stale run file for a reclassified fixture
                # must not resurrect one.
                if inventory.ENTRIES[test_id][1] != "joint-guard":
                    continue
                joint_verdicts[test_id] = (
                    "EXERCISED-JOINT"
                    if test_id in changed else "NOT-EXERCISED")
            continue
        mech_id = res["mechanism"]
        for test_id, change in changed.items():
            if test_id not in inventory.ENTRIES:
                # A test id outside the inventory (e.g. a
                # unittest _FailedTest when a sabotage makes a
                # module unimportable): recorded as a witness
                # anomaly, never silently dropped and never
                # allowed to crash classification.
                summary_anomalies.append(
                    {"run": run_id, "test_id": test_id,
                     "change": change})
                continue
            targets, kind, _n = inventory.ENTRIES[test_id]
            if kind == "exam":
                # An exam fixture's verdict is its own baseline
                # examination (below); any change under a matrix
                # run is its instrument (the mechanism suites it
                # measures with, or its own patch anchors) being
                # altered by the run — instrument interaction,
                # never a pair verdict and never collateral.
                interaction.setdefault(run_id, []).append(test_id)
            elif mech_id in targets:
                pairs[(test_id, mech_id)] = "EXERCISED"
            else:
                collateral.setdefault(run_id, []).append(test_id)
    # Exam fixtures: the pair verdict is SELF-WITNESSED — the
    # fixture's own baseline run applies its sabotage and asserts
    # the dependent fixtures fail; that passing examination is
    # the reach evidence for its claimed target.
    for (test_id, mech), verdict in list(pairs.items()):
        _targets, kind, _n = inventory.ENTRIES[test_id]
        if kind == "exam" and baseline.get(test_id) == "ok":
            pairs[(test_id, mech)] = "SELF-WITNESSED"
    # Joint fixtures: a pair that stayed NOT-EXERCISED singly but
    # whose fixture fell under the combined run is JOINT-ONLY —
    # the conjunction, not either guard, is what it exercises.
    for test_id, verdict in joint_verdicts.items():
        if verdict == "EXERCISED-JOINT":
            targets, _kind, _n = inventory.ENTRIES[test_id]
            for mech in targets:
                if pairs[(test_id, mech)] == "NOT-EXERCISED":
                    pairs[(test_id, mech)] = "JOINT-ONLY"
    summary = {
        "witness_anomalies": summary_anomalies,
        "pairs": {f"{f} :: {m}": v for (f, m), v
                  in sorted(pairs.items())},
        "joint_fixtures": joint_verdicts,
        "collateral": {k: sorted(v) for k, v
                       in sorted(collateral.items()) if v},
        "instrument_interaction": {k: sorted(v) for k, v
                                   in sorted(interaction.items()) if v},
        "runs": {run_id: {"changed": sorted(res.get("changed", {})),
                          "refused": res.get("refused", False),
                          "patch_problems": res.get("patch_problems", [])}
                 for run_id, res in sorted(runs.items())},
    }
    with open(os.path.join(RESULTS, "matrix-summary.json"),
              "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    return summary


def load_runs():
    """Rebuild the runs dict from the per-run result files, so
    classification can be re-run (or corrected) without
    re-running the matrix."""
    runs = {}
    for name in sorted(os.listdir(RESULTS)):
        if not (name.startswith("matrix-")
                and name.endswith(".json")
                and name != "matrix-summary.json"):
            continue
        with open(os.path.join(RESULTS, name),
                  encoding="utf-8") as fh:
            res = json.load(fh)
        if "mechanism" in res:
            runs[res["mechanism"]] = res
        else:
            runs[res["run_id"]] = res
    return runs


if __name__ == "__main__":
    runs = run_matrix()
    summary = classify(runs)
    not_ex = [p for p, v in summary["pairs"].items()
              if v == "NOT-EXERCISED"]
    print(f"pairs NOT-EXERCISED: {len(not_ex)}")
    for p in not_ex:
        print("  ", p)
    print(f"collateral runs: {len(summary['collateral'])}")
    print(f"instrument-interaction runs: "
          f"{len(summary['instrument_interaction'])}")

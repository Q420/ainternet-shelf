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

Run validation (correction round 1 — Gate 1 return,
VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md @ 5107157c): every
witness-runner execution is validated BEFORE anything is
classified from it. The runner's exit status, exactly one
summary record, the summary's internal consistency with the
outcome records, and the completeness of the test-ID set
against the baseline set for that suite are all checked.
A missing, duplicate, malformed, unexpected or otherwise
invalid outcome is a WITNESS ANOMALY and makes the run
INVALID: an invalid run generates no pair verdicts, no
collateral and no coverage credit of any kind — the matrix
fails closed rather than converting an unobserved fixture
into a changed one. (The submitted matrix converted absent
outcomes into changes with under_sabotage "MISSING", which
classify() then credited as EXERCISED — absence of evidence
masquerading as discrimination.)

Record-shape hardening (correction round 2 — Gate 1 return,
VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md @ c352207a): round
1's validator parsed JSON syntax but assumed every test_id
was hashable and sortable, so a syntactically valid but
schema-invalid record — a list- or object-valued test_id,
or a hashable non-string ID sorted against strings — raised
TypeError inside validate_run_output() and aborted the
matrix run instead of becoming the named anomaly and
INVALID-RUN record the validator promises. Field types are
now validated before any type-assuming use: a non-string or
empty test_id and a non-string outcome are named anomalies
and the record contributes nothing. No exception escapes
validate_run_output() for any JSON value shape.

Outcome policy (stated explicitly, per the same ruling): in
a validated, complete run, a pair is credited EXERCISED when
the fixture's observed outcome is FAIL or ERROR. Both are
terminal outcomes in which the fixture was observed to
execute and its baseline behaviour did not occur. In these
suites the fixtures predominantly assert controlled refusals;
when the guard is removed, the guarded input characteristically
flows past the missing guard into code that assumes it ran,
and raises an uncontrolled exception (ERROR) instead of
producing a clean assertion failure (FAIL) — the correction
round's report samples the tracebacks. A "skipped" outcome
never credits: the fixture abstained from executing its
assertions, so the pair is INDETERMINATE, recorded as an
anomaly. A missing outcome cannot occur in a valid run at
all. The earning outcome is recorded per pair
(summary["pair_evidence"]), so FAIL-earned and ERROR-earned
credits are distinguished in the record, never silently
merged.
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


VALID_OUTCOMES = ("ok", "FAIL", "ERROR", "skipped")

# Outcomes that credit a claimed pair as EXERCISED, in a
# validated run — see the outcome policy in the module
# docstring. "skipped" is deliberately absent; a missing
# outcome invalidates the run before classification.
CREDITING_OUTCOMES = ("FAIL", "ERROR")


def expected_ids_by_stage():
    """The baseline test-ID set per stage — the completeness
    reference every witness run is validated against. (The
    inventory's completeness test pins this set to exact
    equality with discovery, so the reference itself is
    checked, not assumed.)"""
    expected = {}
    for stage in range(1, 8):
        ids = set()
        path = os.path.join(RESULTS, f"baseline-stage{stage}.jsonl")
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if "test_id" in row:
                    ids.add(row["test_id"])
        expected[stage] = ids
    return expected


def validate_run_output(returncode, stdout, expected_ids):
    """Validate one witness-runner execution. Returns
    (outcomes, anomalies): outcomes is the {test_id: outcome}
    dict when the run is valid, else None; anomalies names
    every defect found. A run is valid only when the runner
    exited cleanly, emitted exactly one summary record
    internally consistent with its outcome records, and
    produced exactly the expected test-ID set, each once,
    each with a valid outcome value. Record FIELDS are
    type-checked before any use that assumes their type
    (correction round 2): a test_id that is not a non-empty
    string, and an outcome that is not a string, are named
    anomalies — no JSON value shape a record can carry may
    make this function raise."""
    anomalies = []
    outcomes = {}
    summaries = []
    if returncode != 0:
        anomalies.append(
            f"runner exited abnormally (returncode {returncode!r})")
    for lineno, raw in enumerate(stdout.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            anomalies.append(
                f"malformed output line {lineno}: {line[:80]!r}")
            continue
        if not isinstance(row, dict):
            anomalies.append(f"unrecognised record on line {lineno}")
            continue
        if "summary" in row:
            summaries.append(row["summary"])
        elif "test_id" in row:
            test_id = row["test_id"]
            if not isinstance(test_id, str) or not test_id:
                # A malformed RECORD (correction round 2 —
                # Gate 1 return,
                # VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md @
                # c352207a): the test_id is not a string in the
                # expected test-ID form. It must never reach
                # dictionary membership/insertion or sorting —
                # an unhashable ID (list, object) raises
                # TypeError there, and a hashable non-string
                # ID can raise when a mixed set is sorted.
                # Name it as an anomaly and record nothing
                # from the record; exact membership in the
                # expected set is enforced by the set
                # comparison below for string IDs.
                anomalies.append(
                    f"malformed test id {test_id!r} on line "
                    f"{lineno} — not a string test id")
                continue
            if test_id in outcomes:
                anomalies.append(
                    f"duplicate outcome record for {test_id}")
            outcome = row.get("outcome")
            if not isinstance(outcome, str):
                # Same suspicion, neighbouring field: a
                # non-string outcome (list, object, number)
                # is a malformed record. It is named and the
                # record is not stored — an unhashable outcome
                # would otherwise raise TypeError when the
                # summary tally uses it as a dictionary key.
                anomalies.append(
                    f"invalid outcome {outcome!r} for {test_id}")
                continue
            if outcome not in VALID_OUTCOMES:
                anomalies.append(
                    f"invalid outcome {outcome!r} for {test_id}")
            outcomes[test_id] = outcome
        else:
            anomalies.append(f"unrecognised record on line {lineno}")
    if len(summaries) != 1:
        anomalies.append(
            f"expected exactly one summary record, "
            f"found {len(summaries)}")
    else:
        summary = summaries[0]
        if not isinstance(summary, dict) \
                or summary.get("tests") != len(outcomes):
            anomalies.append(
                f"summary test count "
                f"{summary.get('tests') if isinstance(summary, dict) else summary!r} "
                f"does not match {len(outcomes)} outcome records")
        else:
            tally = {}
            for oc in outcomes.values():
                tally[oc] = tally.get(oc, 0) + 1
            if summary.get("counts") != tally:
                anomalies.append(
                    f"summary outcome counts {summary.get('counts')!r} "
                    f"do not match the outcome records {tally!r}")
    for test_id in sorted(set(expected_ids) - set(outcomes)):
        anomalies.append(f"missing outcome for {test_id}")
    for test_id in sorted(set(outcomes) - set(expected_ids)):
        anomalies.append(f"unexpected test id {test_id}")
    if anomalies:
        return None, anomalies
    return outcomes, []


def run_suite(dst_root, stage, expected_ids):
    """Run one suite under the witness runner and validate the
    execution before anything is classified from it. Returns
    (outcomes, validation): outcomes is None when the run is
    invalid; validation records the return code, every anomaly,
    and — for an invalid run — the raw diagnostic tails."""
    pre_anomalies = []
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "witness_run.py"),
             os.path.join(dst_root, f"stage{stage}")],
            capture_output=True, text=True, timeout=600)
        returncode, stdout, stderr = \
            proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = None
        stdout = exc.stdout.decode("utf-8", "replace") \
            if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") \
            if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        pre_anomalies.append("runner timed out after 600s (killed)")
    outcomes, anomalies = validate_run_output(
        returncode, stdout, expected_ids)
    anomalies = pre_anomalies + anomalies
    if anomalies:
        outcomes = None
    validation = {"valid": not anomalies,
                  "returncode": returncode,
                  "anomalies": anomalies}
    if anomalies:
        validation["stderr_tail"] = stderr[-1500:]
        validation["stdout_tail"] = stdout[-1500:]
    return outcomes, validation


def run_one(run_id, patches, suites, baseline):
    """One matrix run: scratch copy, patch, witness, validate,
    diff. Only validated suite executions contribute changes;
    an invalid suite execution invalidates the whole run and
    contributes nothing (fail closed — correction round 1)."""
    dst_root = os.path.join(SCRATCH, run_id)
    copy_tree(dst_root)
    problems = apply_patches(dst_root, patches)
    result = {"run_id": run_id, "suites": suites,
              "patch_problems": problems, "changed": {},
              "suite_validations": {}}
    if problems:
        result["refused"] = True
        result["valid"] = False
        result["invalid_reasons"] = [
            f"patch refused: {p}" for p in problems]
        shutil.rmtree(dst_root, ignore_errors=True)
        return result
    expected = expected_ids_by_stage()
    invalid_reasons = []
    for stage in suites:
        outcomes, validation = run_suite(
            dst_root, stage, expected[stage])
        result["suite_validations"][str(stage)] = validation
        if outcomes is None:
            invalid_reasons.extend(
                f"stage {stage}: {a}"
                for a in validation["anomalies"])
            continue
        for test_id, outcome in sorted(outcomes.items()):
            base = baseline.get(test_id)
            if outcome != base:
                result["changed"][test_id] = {
                    "baseline": base, "under_sabotage": outcome,
                    "stage": stage}
    result["valid"] = not invalid_reasons
    result["invalid_reasons"] = invalid_reasons
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
              f"refused={res.get('refused', False)} "
              f"valid={res.get('valid', False)}", flush=True)
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
              f"refused={res.get('refused', False)} "
              f"valid={res.get('valid', False)}", flush=True)
    return runs


def classify(runs):
    """Pair verdicts, collateral, instrument interaction —
    from the run records and the inventory's claims. A run
    record that is not validated (correction round 1) yields
    NOTHING: no pair verdicts, no collateral, no joint
    verdicts — its claimed pairs are recorded INVALID-RUN and
    the run is named in summary["invalid_runs"]. A record
    with no validation at all is treated as invalid (fail
    closed)."""
    baseline = load_baseline()
    pairs = {}          # (fixture, mechanism) -> verdict
    collateral = {}     # run_id -> [test_ids]
    interaction = {}    # run_id -> [test_ids]
    summary_anomalies = []
    invalid_runs = {}   # run_id -> {invalid_reasons, affected_pairs}
    pair_evidence = {}  # "fixture :: mechanism" -> earning outcome
    joint_change_outcomes = {}  # joint fixture -> joint-run outcome
    for test_id, (targets, kind, _n) in inventory.ENTRIES.items():
        for mech in targets:
            pairs[(test_id, mech)] = "NOT-EXERCISED"
    joint_verdicts = {}
    groups = joint_groups()
    for run_id, res in runs.items():
        changed = res.get("changed", {})
        if not res.get("valid", False):
            # Fail closed (correction round 1): an unvalidated
            # or invalid run is a witness anomaly at run level.
            # Nothing in it is classified — no EXERCISED, no
            # NOT-EXERCISED, no collateral — because the run
            # did not produce a complete, observable record.
            reasons = res.get("invalid_reasons") or [
                "no validation record — treated as invalid "
                "(fail closed)"]
            entry = {"invalid_reasons": list(reasons)}
            affected = []
            if run_id.startswith("joint-"):
                entry["joint_targets"] = res.get("joint_targets", [])
                for test_id in res.get("joint_fixtures", []):
                    if inventory.ENTRIES[test_id][1] != "joint-guard":
                        continue
                    joint_verdicts[test_id] = "INVALID-RUN"
                    affected.append(f"{test_id} (joint)")
            else:
                mech_id = res.get("mechanism")
                entry["mechanism"] = mech_id
                for test_id, (targets, kind, _n) \
                        in inventory.ENTRIES.items():
                    if mech_id in targets and kind != "exam":
                        # Exam fixtures' verdicts never came
                        # from this run (SELF-WITNESSED, below);
                        # every other claimed pair loses its
                        # determining run and is INVALID-RUN.
                        pairs[(test_id, mech_id)] = "INVALID-RUN"
                        affected.append(f"{test_id} :: {mech_id}")
            entry["affected_pairs"] = sorted(affected)
            invalid_runs[run_id] = entry
            continue
        if run_id.startswith("joint-"):
            targets = res["joint_targets"]
            for test_id in res["joint_fixtures"]:
                # Only fixtures that are joint-guard in the
                # CURRENT inventory take a joint verdict; a
                # stale run file for a reclassified fixture
                # must not resurrect one.
                if inventory.ENTRIES[test_id][1] != "joint-guard":
                    continue
                change = changed.get(test_id)
                if change is None:
                    joint_verdicts[test_id] = "NOT-EXERCISED"
                elif change.get("under_sabotage") \
                        in CREDITING_OUTCOMES:
                    joint_verdicts[test_id] = "EXERCISED-JOINT"
                    joint_change_outcomes[test_id] = \
                        change["under_sabotage"]
                else:
                    # Changed, but not by an outcome that
                    # credits (e.g. skipped): no joint verdict
                    # either way — INDETERMINATE, and named.
                    joint_verdicts[test_id] = "INDETERMINATE"
                    summary_anomalies.append(
                        {"run": run_id, "test_id": test_id,
                         "change": change,
                         "note": "joint fixture changed under a "
                                 "non-crediting outcome — no "
                                 "joint verdict taken"})
            continue
        mech_id = res["mechanism"]
        for test_id, change in changed.items():
            if test_id not in inventory.ENTRIES:
                # A test id outside the inventory (e.g. a
                # unittest _FailedTest when a sabotage makes a
                # module unimportable): recorded as a witness
                # anomaly, never silently dropped and never
                # allowed to crash classification. (After
                # correction round 1, run validation already
                # invalidates any run whose observed ID set
                # differs from the baseline set, so this is
                # defence in depth.)
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
                outcome = change.get("under_sabotage")
                if outcome in CREDITING_OUTCOMES:
                    pairs[(test_id, mech_id)] = "EXERCISED"
                    pair_evidence[f"{test_id} :: {mech_id}"] = \
                        outcome
                elif outcome == "skipped":
                    # The fixture abstained under sabotage: it
                    # neither discriminated nor passed. No
                    # credit, no NOT-EXERCISED claim —
                    # INDETERMINATE, and named as an anomaly.
                    pairs[(test_id, mech_id)] = "INDETERMINATE"
                    summary_anomalies.append(
                        {"run": run_id, "test_id": test_id,
                         "change": change,
                         "note": "fixture skipped under sabotage "
                                 "— abstention is not "
                                 "discrimination evidence"})
                else:
                    summary_anomalies.append(
                        {"run": run_id, "test_id": test_id,
                         "change": change,
                         "note": f"outcome {outcome!r} does not "
                                 f"credit a pair"})
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
                    pair_evidence[f"{test_id} :: {mech}"] = (
                        f"{joint_change_outcomes.get(test_id)} "
                        f"(joint run)")
    exercised_by_outcome = {}
    for (fixture, mech), verdict in sorted(pairs.items()):
        if verdict in ("EXERCISED", "JOINT-ONLY"):
            evidence = pair_evidence.get(f"{fixture} :: {mech}", "")
            base_outcome = evidence.split(" ")[0]
            if base_outcome:
                exercised_by_outcome[base_outcome] = \
                    exercised_by_outcome.get(base_outcome, 0) + 1
    summary = {
        "witness_anomalies": summary_anomalies,
        "invalid_runs": invalid_runs,
        "pair_evidence": pair_evidence,
        "exercised_by_outcome": exercised_by_outcome,
        "pairs": {f"{f} :: {m}": v for (f, m), v
                  in sorted(pairs.items())},
        "joint_fixtures": joint_verdicts,
        "collateral": {k: sorted(v) for k, v
                       in sorted(collateral.items()) if v},
        "instrument_interaction": {k: sorted(v) for k, v
                                   in sorted(interaction.items()) if v},
        "runs": {run_id: {"changed": sorted(res.get("changed", {})),
                          "refused": res.get("refused", False),
                          "valid": res.get("valid", False),
                          "invalid_reasons":
                              res.get("invalid_reasons", []),
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
    print(f"invalid runs: {len(summary['invalid_runs'])}")
    for run_id in summary["invalid_runs"]:
        print("  ", run_id)

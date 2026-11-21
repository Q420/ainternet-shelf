"""Shared machinery for Stage 4's sabotage examinations.

A sabotage examination constructs a deliberately weakened
variant of this stage's contract.py in a scratch tree — the
weakening is a small set of exact string replacements, each
anchored on text that must occur EXACTLY ONCE in the source
(the examination refuses to run against a source it cannot
patch precisely) — then runs the stage's two mechanism suites
(test_verdict_issuance, test_dispatch) against the variant in a
subprocess and reports which tests failed. The examinations
assert the exact failing set: the dependent fixture fails, and
everything else holds. This follows the countercheck discipline
of Stages 2 and 3, promoted here to first-class examinations
per the plan.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
STAGE4_DIR = os.path.dirname(TESTS_DIR)
MECHANISM_TESTS = ("test_verdict_issuance.py", "test_dispatch.py")


def apply_patches(source, patches):
    for anchor, replacement in patches:
        count = source.count(anchor)
        if count != 1:
            raise AssertionError(
                f"sabotage anchor occurs {count} times (expected "
                f"exactly 1): {anchor!r}")
        source = source.replace(anchor, replacement)
    return source


def run_suite_against_variant(patches):
    """Run the mechanism suites against a patched contract.py.

    Returns (returncode, failing_test_names, output)."""
    with open(os.path.join(STAGE4_DIR, "contract.py")) as fh:
        source = fh.read()
    variant = apply_patches(source, patches)
    scratch = tempfile.mkdtemp(prefix="stage4-sabotage-")
    try:
        os.mkdir(os.path.join(scratch, "tests"))
        with open(os.path.join(scratch, "contract.py"), "w") as fh:
            fh.write(variant)
        for name in MECHANISM_TESTS:
            shutil.copy(os.path.join(TESTS_DIR, name),
                        os.path.join(scratch, "tests", name))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover",
             "-s", "tests"],
            cwd=scratch, env=env, capture_output=True, text=True,
            timeout=120)
        output = proc.stdout + proc.stderr
        failing = set(re.findall(r"^(?:FAIL|ERROR): (\w+)", output,
                                 re.MULTILINE))
        return proc.returncode, failing, output
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

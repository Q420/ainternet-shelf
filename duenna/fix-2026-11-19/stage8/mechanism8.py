"""The instrumented target mechanism for Test 8.

``DigestGate`` stands in for any guard whose comparison branch
is the thing a fixture claims to exercise (a digest comparison,
an anchor comparison, a chain verification). The comparison
lives in ``_compare``, and the reach instrumentation lives
INSIDE ``_compare``: if the branch does not execute, no witness
record exists, whatever the fixture says about itself.

``DigestGateWithoutComparison`` is the same gate with the
target comparison removed — it accepts everything. A fixture
run against it can report PASS (its presented digest is
"accepted") while the witness records nothing: the comparison
was never there to reach.
"""

MECHANISM_ID = "stage8.digest_gate.compare"


class DigestGate:
    def __init__(self, expected_digest: str, sink, instance_id: str):
        self._expected = expected_digest
        self._sink = sink
        self._instance_id = instance_id

    def _compare(self, presented: str) -> bool:
        # Instrumentation of the target mechanism: this line
        # runs only when the comparison branch itself runs.
        self._sink.record_reach(MECHANISM_ID, self._instance_id)
        return presented == self._expected

    def check(self, presented: str) -> bool:
        return self._compare(presented)


class DigestGateWithoutComparison:
    """The sabotage variant: the comparison branch is gone.
    check() accepts by default and never reaches a comparison,
    so the witness sink is never called."""

    def __init__(self, expected_digest: str, sink, instance_id: str):
        self._expected = expected_digest
        self._sink = sink
        self._instance_id = instance_id

    def check(self, presented: str) -> bool:
        return True

"""The K14 witness (Stage 8, Test 8 machinery).

A witness record is written ONLY by the instrumented target
mechanism, at the moment its target branch executes. A fixture
cannot write one: fixtures receive a gate and an execution
instance id, never the log. Each record names the TARGET
MECHANISM and the EXECUTION INSTANCE it belongs to, so reach
evidence from one run can never be attached to another.

The log is a plain list owned by the harness (the test), which
hands the mechanism a sink callable at construction. That is
the same API-boundary discipline the earlier stages use: the
separation holds because the fixture's code path has no access
to the sink, not because of a sandbox.
"""

import itertools

_instance_counter = itertools.count(1)


def new_instance_id(fixture_id: str) -> str:
    """A fresh execution-instance id for one fixture run."""
    return f"{fixture_id}#run-{next(_instance_counter)}"


class WitnessLog:
    """Append-only reach records, written by mechanisms."""

    def __init__(self):
        self._records = []

    def record_reach(self, mechanism_id: str, instance_id: str):
        """Called by the instrumented mechanism itself when its
        target branch executes."""
        self._records.append({
            "mechanism_id": mechanism_id,
            "instance_id": instance_id,
            "reached": True,
        })

    def records(self):
        return list(self._records)

    def reached(self, mechanism_id: str, instance_id: str) -> bool:
        """Was the mechanism's target branch executed in THIS
        execution instance? Evidence from any other instance
        does not count."""
        return any(
            r["mechanism_id"] == mechanism_id
            and r["instance_id"] == instance_id
            and r["reached"]
            for r in self._records)

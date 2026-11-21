"""Duenna Stage 1 — minimal scripted runner.

A minimal runner that executes scripted scenarios on an EventRecord
(record.py) and invokes the closure writer (closure.py) on EVERY
controlled termination path:

- normal completion
- known failure
- early stop
- exception

On every path exactly one CLOSURE event is appended, as the last
event. Failures that occur during a scenario are also appended as
FAILURE events (carrying their ``failure_id``) BEFORE closure, so a
later reconciliation (the validator, Stage 1 step 3) has something
independent of the closure account to reconcile against.

Attributions minted here are made under the TEST authority fixture
declared in closure.py (``authority="TEST-FIXTURE"``). That fixture
settles nothing about DR-13.

Boundary: controlled termination only. A hard kill of this process
before its closure path executes is outside this harness's guarantee
and is never claimed here.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K9, G4),
PROCESS-TREE-AND-PLAN.md v2, Stage 1.
"""

from __future__ import annotations

from closure import ClosureWriter, TEST_AUTHORITY, make_failure

SCENARIOS = ("normal", "known_failure", "early_stop", "exception")


class Runner:
    """Executes one scripted scenario against an EventRecord."""

    def __init__(self, record):
        self.record = record
        self.closure = ClosureWriter(record)
        self.failures: list[dict] = []

    # -- internals ---------------------------------------------------

    def _record_failure(self, failure_id: str, description: str,
                        attribution: str | None = None) -> dict:
        """Append a FAILURE event BEFORE closure and track it for the
        closure account. Returns the failure entry."""
        failure = make_failure(failure_id, description, attribution,
                               authority=TEST_AUTHORITY)
        self.record.append("FAILURE", dict(failure))
        self.failures.append(failure)
        return failure

    def _started(self, scenario: str) -> None:
        self.record.append("RUN_STARTED", {"scenario": scenario})

    # -- the four controlled termination paths ------------------------

    def run_normal(self) -> dict:
        """Normal completion: no failures, COMPLETE empty account."""
        self._started("normal")
        self.record.append("STEP", {"n": 1})
        self.record.append("STEP", {"n": 2})
        return self.closure.close(
            "normal",
            failures=[],
            execution="COMPLETED",
            adjudication="NOT_REQUIRED",
            unknowns=[],
            account_status="COMPLETE",
        )

    def run_known_failure(self) -> dict:
        """Known failure: the failure is recorded as a FAILURE event
        and listed in the closure account with its attribution."""
        self._started("known_failure")
        self.record.append("STEP", {"n": 1})
        self._record_failure(
            "F-KNOWN-1",
            "Scripted known failure",
            attribution="SYSTEM",
        )
        return self.closure.close(
            "known_failure",
            failures=list(self.failures),
            execution="FAILED",
            adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
            unknowns=[],
            account_status="COMPLETE",
        )

    def run_early_stop(self) -> dict:
        """Early stop: closure is appended; what the unexecuted steps
        would have shown is named as UNKNOWN, so the account is
        honestly INCOMPLETE."""
        self._started("early_stop")
        self.record.append("STEP", {"n": 1})
        self.record.append("STOP_REQUESTED", {"after_step": 1})
        return self.closure.close(
            "early_stop",
            failures=[],
            execution="STOPPED_EARLY",
            adjudication="NOT_REQUIRED",
            unknowns=["outcome of steps not executed after early stop"],
            account_status="INCOMPLETE",
        )

    def run_exception(self) -> dict:
        """Exception: a scenario step raises; the runner catches it,
        records it as a FAILURE event (attribution UNKNOWN), and still
        appends closure. The exception does not propagate."""
        self._started("exception")
        self.record.append("STEP", {"n": 1})
        try:
            self._step_that_raises()
        except RuntimeError as exc:
            self._record_failure(
                "F-EXC-1",
                f"Scripted exception: {exc}",
                attribution="UNKNOWN",
            )
        return self.closure.close(
            "exception",
            failures=list(self.failures),
            execution="EXCEPTION",
            adjudication="PENDING",
            unknowns=[],
            account_status="COMPLETE",
        )

    @staticmethod
    def _step_that_raises() -> None:
        raise RuntimeError("scripted exception in scenario step")

    # -- dispatch ------------------------------------------------------

    def run(self, scenario: str) -> dict:
        """Run one named scenario; returns the CLOSURE event dict."""
        dispatch = {
            "normal": self.run_normal,
            "known_failure": self.run_known_failure,
            "early_stop": self.run_early_stop,
            "exception": self.run_exception,
        }
        if scenario not in dispatch:
            raise ValueError(f"unknown scenario: {scenario!r}")
        return dispatch[scenario]()


def run_scenario(record, scenario: str) -> dict:
    """Convenience: run ``scenario`` on ``record``, return CLOSURE."""
    return Runner(record).run(scenario)

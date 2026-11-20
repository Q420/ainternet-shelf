"""Coverage accounting (Stage 8, K14).

The accountant consumes WITNESS RECORDS ONLY. It never reads a
fixture's self-report: a fixture's claim about itself is not an
input to any coverage figure. A fixture counts as covered for
its target mechanism exactly when the witness recorded the
mechanism's branch executing in that fixture's own execution
instance. Otherwise the fixture is NOT-EXERCISED and
contributes nothing — mechanically, not by editorial choice.
"""

EXERCISED = "EXERCISED"
NOT_EXERCISED = "NOT-EXERCISED"


def fixture_coverage(witness_log, fixture_id: str,
                     mechanism_id: str, instance_id: str) -> str:
    """One fixture's coverage state, from the witness alone."""
    if witness_log.reached(mechanism_id, instance_id):
        return EXERCISED
    return NOT_EXERCISED


def coverage_report(witness_log, runs) -> dict:
    """``runs`` is a list of {fixture_id, mechanism_id,
    instance_id} — one entry per fixture execution. Returns
    per-fixture states and the covered count. NOT-EXERCISED
    fixtures are excluded from the covered count by
    construction: the count is taken over EXERCISED entries
    only."""
    states = {}
    for run in runs:
        states[run["fixture_id"]] = fixture_coverage(
            witness_log, run["fixture_id"], run["mechanism_id"],
            run["instance_id"])
    covered = sorted(fid for fid, state in states.items()
                     if state == EXERCISED)
    not_exercised = sorted(fid for fid, state in states.items()
                           if state == NOT_EXERCISED)
    return {"states": states,
            "covered": covered,
            "not_exercised": not_exercised,
            "covered_count": len(covered)}

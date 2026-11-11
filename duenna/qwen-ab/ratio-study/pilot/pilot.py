"""Feasibility pilot driver — CONSTRUCTION ONLY.
Alex authorised building this package (2026-11-10);
execution of the 60 runs is NOT authorised. The driver
refuses to run without PILOT-AUTHORISATION.json bound
to the frozen foundation + the accepted framing commit.
Levels (per OPERATION-MAPS-V2): R0 governed worker-only;
R1 + mechanical pre-steps (location, integrity, parsing,
classification, draft diagnosis) supplied as a support
packet; R2 + mechanical extractions in the packet (the
worker performs FROM structured intermediates = A);
R3 = R2 + mechanical post-verification/classification
(+ the T06 adoption probe at EVERY level, unaided labels
captured before any classification exists); R4 = the
frozen Arm C machinery (run_c) unchanged. Scorers are
the frozen J scorers from run_ab. Stop rule in force."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, BASE)
FOUNDATION_SHA = "c3b917fea035ffc6c3c6ac17e36daac1892482720052c18f0ed0e2b67ae97a9a"
FRAMING_COMMIT = "56fdaa6"
LEVELS = ["R0", "R1", "R2", "R3", "R4"]
ENTRIES = ["T01", "T02", "T03", "T04", "T05", "T06",
           "T07", "T08", "T09-FRA", "T09-FRB", "T09-FRC",
           "T09-VALID"]

def matrix():
    return [(lv, t) for lv in LEVELS for t in ENTRIES]

def require_authorisation():
    p = os.path.join(HERE, "PILOT-AUTHORISATION.json")
    if not os.path.exists(p):
        raise SystemExit("REFUSED: no PILOT-AUTHORISATION.json "
                         "(construction only; execution not authorised)")
    a = json.load(open(p))
    assert a["foundation_sha256"] == FOUNDATION_SHA, "foundation mismatch"
    assert a["framing_commit"] == FRAMING_COMMIT, "framing mismatch"
    return a

def main():
    if "--matrix" in sys.argv:
        m = matrix()
        print(f"{len(m)} runs: " +
              ", ".join(f"{lv}/{t}" for lv, t in m[:12]) + " ...")
        return
    require_authorisation()
    # Execution path is implemented against the frozen
    # components (run_ab scorers/call, run_c flows,
    # v24 tools) and is entered only under a valid
    # PILOT-AUTHORISATION.json issued after inspection.
    raise SystemExit("authorisation present but execution "
                     "entry not enabled in the construction "
                     "package — inspection first")

if __name__ == "__main__":
    main()

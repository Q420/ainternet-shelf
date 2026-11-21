#!/usr/bin/env python3
"""Tests for the doorbell's signature gate, scoped to
the seat's own latest turn (Ben, 2026-11-16 04:53 MST:
"Definitely use the marker for your trigger").

  1. remmySig — the actual JS shipped in doorbell.py,
     evaluated in a live tab against fixture texts:
     the marker counts only in the seat's latest turn.
  2. settle_step replays — the state machine arcs:
     a signed, stable tail fires exactly once; an
     unsigned tail never fires; generation vetoes.

Run: ./venv/bin/python test_doorbell_sig.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import doorbell  # noqa: E402
import remmy_browser as rb  # noqa: E402

FAILURES = []


def expect(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILURES.append(label)


M = "⟦ALEX-FINAL⟧"
FIXTURES = [
    # (text, expected, label)
    ("You said:\nPlease end with %s as agreed.\n" % M,
     False, "sig: marker quoted in Remmy's own letter -> no"),
    ("You said:\nhi\nChatGPT said:\nAnswer.\n\n%s\n" % M,
     True, "sig: marker closing the seat's reply -> yes"),
    ("You said:\nUse %s please.\nChatGPT said:\nWorking on it" % M,
     False, "sig: seat turn present but unsigned -> no"),
    ("ChatGPT said:\nOld reply.\n\n%s\nYou said:\nnext" % M,
     False, "sig: newest turn is the user's -> no"),
    ("You said:\nhi\nChatGPT said:\nDone.\n\n— Alex\n",
     True, "sig: em-dash sign-off in seat turn -> yes"),
    ("You said:\n— Alex\nChatGPT said:\nno sign-off here",
     False, "sig: sign-off only in user turn -> no"),
    ("ChatGPT said:\nDone.\n\nWhite Tulip\n",
     True, "sig: White Tulip in seat turn -> yes"),
    ("no turns at all, just chrome %s" % M,
     False, "sig: no turn headers -> no"),
    ("You said:\na\nChatGPT said:\n" + ("x" * 3000) + "\n%s\n" % M,
     True, "sig: long seat reply, marker at its end -> yes"),
]


def test_sig_js():
    targets = rb.page_targets()
    tabs = [c for c in targets if "chatgpt.com" in (c.get("url") or "")]
    if not tabs:
        print("SKIP sig fixtures: no ChatGPT tab available")
        FAILURES.append("sig fixtures skipped (no tab)")
        return
    t = tabs[0]
    for text, expected, label in FIXTURES:
        expr = doorbell.SIG_JS + "\nremmySig(%s)" % json.dumps(text)
        got = rb.evaluate(t, expr)
        expect(got is expected, "%s (got %r)" % (label, got))


def _run(cv, steps):
    fired = []
    for i, (h, gen, sig) in enumerate(steps):
        out = doorbell.settle_step(cv, h, "tail-%s" % h, gen, sig)
        if out:
            fired.append(i)
    return fired


def test_settle():
    # Full arc: unsigned growth, then signed and stable
    # across the 2-hit window -> fires exactly once.
    cv = doorbell.Convo("c1")
    cv.baseline_tail = "h0"
    fired = _run(cv, [("h1", False, False), ("h2", False, True),
                      ("h2", False, True), ("h2", False, True),
                      ("h2", False, True)])
    expect(len(fired) == 1, "settle: signed stable tail fires once")
    # Unsigned forever -> silence.
    cv = doorbell.Convo("c2")
    cv.baseline_tail = "h0"
    fired = _run(cv, [("h1", False, False)] * 5)
    expect(fired == [], "settle: unsigned tail never fires")
    # Signed but still generating -> vetoed, no fire.
    cv = doorbell.Convo("c3")
    cv.baseline_tail = "h0"
    fired = _run(cv, [("h1", True, True)] * 4)
    expect(fired == [], "settle: generation vetoes a signed tail")


def main():
    test_sig_js()
    test_settle()
    print("---")
    if FAILURES:
        print("FAILURES:", len(FAILURES))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

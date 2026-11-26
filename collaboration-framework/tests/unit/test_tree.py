"""Unit witnesses for the process tree
(office-cycle-v9, the build scope of 2026-11-26):
the sealed declaration's shape check, the one
state computation (record-derived node states,
the held-file facts, the blocked pass), the
worker's text rendering, and the speaking
refusal's correction — the tree and the refusal
rendering from the same computation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from framework import tool_policy  # noqa: E402
from framework.loop import (  # noqa: E402
    _tree_computation, _tree_speaking_refusals,
    _tree_text)

TREE = {
    "contract": "process-tree-checklist-v1",
    "title": "The Brief",
    "nodes": [
        {"id": "onboarding", "label": "1. Know the job",
         "kind": "onboarding", "depends_on": [],
         "workaround": ""},
        {"id": "gather-a", "label": "2.1 Gather + journal — sources/a.md",
         "kind": "gather", "source": "sources/a.md",
         "depends_on": ["onboarding"],
         "workaround": "you already hold it"},
        {"id": "gather-b", "label": "2.2 Gather + journal — sources/b.md",
         "kind": "gather", "source": "sources/b.md",
         "depends_on": ["onboarding"], "workaround": ""},
        {"id": "summarize", "label": "3. Summarize",
         "kind": "summarize",
         "depends_on": ["gather-a", "gather-b"],
         "workaround": ""},
        {"id": "deliver", "label": "4. Deliver",
         "kind": "deliver", "depends_on": ["summarize"],
         "workaround": ""}]}


def _file(address, read_stands, done, state, parts=1):
    return {"address": address,
            "read_stands": read_stands, "done": done,
            "state": state,
            "blocks": [{"read_stands": read_stands}
                       for _ in range(parts)]}


def _cstate(files):
    return {"files": files}


class TreeProblemTests(unittest.TestCase):
    def test_well_formed_stands(self):
        self.assertIsNone(tool_policy.tree_problem(TREE))

    def test_wrong_contract_refused(self):
        bad = dict(TREE, contract="process-tree-v99")
        self.assertIsNotNone(tool_policy.tree_problem(bad))

    def test_gather_without_source_refused(self):
        bad = {"contract": TREE["contract"], "title": "t",
               "nodes": [{"id": "g", "label": "g",
                          "kind": "gather",
                          "depends_on": [],
                          "workaround": ""}]}
        self.assertIsNotNone(tool_policy.tree_problem(bad))

    def test_dangling_dependency_refused(self):
        bad = {"contract": TREE["contract"], "title": "t",
               "nodes": [{"id": "s", "label": "s",
                          "kind": "summarize",
                          "depends_on": ["ghost"],
                          "workaround": ""}]}
        self.assertIsNotNone(tool_policy.tree_problem(bad))


class TreeComputationTests(unittest.TestCase):
    def test_opening_states(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", False, False, "current"),
            _file("sources/b.md", False, False, "pending")]),
            iteration=1, deliverable_filed=False)
        states = {n["id"]: n["state"] for n in comp["nodes"]}
        self.assertEqual(states["onboarding"], "current")
        self.assertEqual(states["gather-a"], "current")
        self.assertEqual(states["summarize"], "blocked")
        # Blocked propagates down the chain, each
        # node naming its own unfilled dependency;
        # only a dependency standing current leaves
        # a node merely pending (next in line).
        self.assertEqual(states["deliver"], "blocked")

    def test_held_unjournaled_names_next_act(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", True, False, "current"),
            _file("sources/b.md", False, False, "pending")]),
            iteration=3, deliverable_filed=False)
        node = next(n for n in comp["nodes"]
                    if n["id"] == "gather-a")
        self.assertEqual(node["state"], "current")
        self.assertTrue(any(
            "you hold this source whole" in f
            for f in node["facts"]))
        self.assertTrue(any(
            "next act is to write its journal bit" in f
            for f in node["facts"]))

    def test_read_without_journal_is_not_done(self):
        # Vane's protected point: read everything but
        # journaled nothing is not finished gathering.
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", True, False, "current"),
            _file("sources/b.md", True, False, "pending")]),
            iteration=3, deliverable_filed=False)
        states = {n["id"]: n["state"] for n in comp["nodes"]}
        self.assertNotEqual(states["gather-a"], "done")
        self.assertNotEqual(states["summarize"], "current")

    def test_all_journaled_summarize_current(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", True, True, "done"),
            _file("sources/b.md", True, True, "done")]),
            iteration=6, deliverable_filed=False)
        states = {n["id"]: n["state"] for n in comp["nodes"]}
        self.assertEqual(states["summarize"], "current")
        self.assertEqual(states["deliver"], "pending")

    def test_filed_marks_the_tail_done(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", True, True, "done"),
            _file("sources/b.md", True, True, "done")]),
            iteration=7, deliverable_filed=True)
        states = {n["id"]: n["state"] for n in comp["nodes"]}
        self.assertEqual(states["summarize"], "done")
        self.assertEqual(states["deliver"], "done")


class TreeRenderingTests(unittest.TestCase):
    def test_text_carries_states_and_workaround(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", True, False, "current"),
            _file("sources/b.md", False, False, "pending")]),
            iteration=2, deliverable_filed=False)
        text = _tree_text(comp)
        self.assertIn("Process tree — The Brief", text)
        self.assertIn("[current] 2.1 Gather", text)
        self.assertIn("Workaround: you already hold it",
                      text)

    def test_speaking_refusal_speaks(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", True, False, "current"),
            _file("sources/b.md", False, False, "pending")]),
            iteration=2, deliverable_filed=False)
        results = [{
            "outcome": "refused",
            "refusal_class": "doorway_refused",
            "error": "Request refused: the grant's "
                     "bound for tool sandbox.read is "
                     "exhausted: 3 of 3 dispatches "
                     "stand charged. Nothing was "
                     "dispatched for this call."}]
        _tree_speaking_refusals(results, comp)
        self.assertIn("You already hold, whole:",
                      results[0]["error"])
        self.assertIn(
            "Your next act is to write the journal bit",
            results[0]["error"])

    def test_speaking_refusal_silent_without_held(self):
        comp = _tree_computation(TREE, _cstate([
            _file("sources/a.md", False, False, "current"),
            _file("sources/b.md", False, False, "pending")]),
            iteration=2, deliverable_filed=False)
        results = [{
            "outcome": "refused",
            "refusal_class": "doorway_refused",
            "error": "Request refused: the grant's "
                     "bound for tool sandbox.read is "
                     "exhausted."}]
        before = results[0]["error"]
        _tree_speaking_refusals(results, comp)
        self.assertEqual(results[0]["error"], before)


if __name__ == "__main__":
    unittest.main()

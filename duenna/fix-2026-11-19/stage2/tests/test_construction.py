"""Stage 2 — positive controls and construction mechanics.

The positive controls matter as much as the sabotages: a close that
refuses everything would "pass" every sabotage while proving
nothing. A well-formed artefact, built from its provenance entries
on the real record, must close; a field-for-field faithful artefact
must pass equality.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage2/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
from record import EventRecord, verify_chain  # noqa: E402
from schema import TEST_SCHEMA  # noqa: E402
from construction import (  # noqa: E402
    CONSTRUCTION_CLOSED,
    CONSTRUCTION_REFUSED,
    ConstructionRefused,
    append_provenance_entry,
    construct_artefact,
    read_provenance_entries,
)

VALUES = {
    "artifact": "artefact-bytes-ref",
    "evidence": "evidence-ref",
    "fixtures_total": 8,
    "fixtures_passed": 8,
    "run_id": "RUN-TEST-1",
    "tree_id": "T05",
    "subject": "test-subject",
    "outcome": "COMPLETED",
}


class TestConstruction(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")
        self.record = EventRecord(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def _enter_all(self, artefact_id="ART-1", values=None):
        for field, value in (values or VALUES).items():
            append_provenance_entry(self.record, artefact_id, field,
                                    value)

    def _events_of(self, event_type):
        return [ev for ev in self.record.read_all()
                if ev["type"] == event_type]

    def test_well_formed_artefact_closes(self):
        self._enter_all()
        artefact = construct_artefact(self.record, "ART-1",
                                      TEST_SCHEMA)
        self.assertEqual(artefact, VALUES)
        closed = self._events_of(CONSTRUCTION_CLOSED)
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0]["body"]["artefact_id"], "ART-1")
        self.assertEqual(closed[0]["body"]["schema_digest"],
                         TEST_SCHEMA.digest)
        self.assertEqual(closed[0]["body"]["fields"],
                         sorted(VALUES))
        self.assertEqual(self._events_of(CONSTRUCTION_REFUSED), [])

    def test_faithful_artefact_passes_field_for_field(self):
        self._enter_all()
        artefact = construct_artefact(self.record, "ART-1",
                                      TEST_SCHEMA)
        for field in TEST_SCHEMA.artefact_fields:
            self.assertIn(field, artefact)
            self.assertEqual(artefact[field], VALUES[field])
        self.assertEqual(set(artefact),
                         set(TEST_SCHEMA.artefact_fields))

    def test_record_chain_still_verifies_after_construction(self):
        self._enter_all()
        construct_artefact(self.record, "ART-1", TEST_SCHEMA)
        ok, bad = verify_chain(self.record.read_all())
        self.assertTrue(ok, f"chain failed at seq {bad}")

    def test_entries_for_other_artefacts_are_not_read(self):
        self._enter_all("ART-1")
        self._enter_all("ART-2", values={**VALUES,
                                         "run_id": "RUN-OTHER"})
        entries = read_provenance_entries(self.record, "ART-1")
        self.assertEqual(len(entries), 8)
        artefact = construct_artefact(self.record, "ART-1",
                                      TEST_SCHEMA)
        self.assertEqual(artefact["run_id"], "RUN-TEST-1")

    def test_no_entries_at_all_refuses_and_records_refusal(self):
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.record, "ART-MISSING",
                               TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details["schema_fields_absent_from_both"],
            sorted(TEST_SCHEMA.artefact_fields))
        refused = self._events_of(CONSTRUCTION_REFUSED)
        self.assertEqual(len(refused), 1)
        self.assertEqual(self._events_of(CONSTRUCTION_CLOSED), [])

    def test_duplicate_entry_for_one_field_refuses(self):
        self._enter_all()
        append_provenance_entry(self.record, "ART-1",
                                "fixtures_total", 9)
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.record, "ART-1", TEST_SCHEMA)
        self.assertEqual(ctx.exception.details["duplicate_entries"],
                         ["fixtures_total"])
        self.assertEqual(self._events_of(CONSTRUCTION_CLOSED), [])

    def test_unencodable_provenance_value_refused_at_entry(self):
        with self.assertRaises(ValueError):
            append_provenance_entry(self.record, "ART-1", "artifact",
                                    object())


if __name__ == "__main__":
    unittest.main()

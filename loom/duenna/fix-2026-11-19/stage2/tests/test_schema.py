"""Stage 2 — tests for the one frozen schema object (K5).

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage2/tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
from schema import TEST_SCHEMA, freeze_schema  # noqa: E402


class TestFrozenSchema(unittest.TestCase):

    def test_sections_carry_the_contracts(self):
        self.assertIn("artifact", TEST_SCHEMA.artefact_fields)
        self.assertIn("evidence", TEST_SCHEMA.artefact_fields)
        self.assertIn("fixtures_total", TEST_SCHEMA.artefact_fields)
        self.assertEqual(len(TEST_SCHEMA.artefact_fields), 8)
        self.assertEqual(len(TEST_SCHEMA.response_fields), 3)

    def test_schema_is_frozen_after_construction(self):
        schema = freeze_schema("V1", ("a", "b"), ("c",))
        with self.assertRaises(AttributeError):
            schema.version = "V2"
        with self.assertRaises(AttributeError):
            schema.artefact_fields = ("x",)

    def test_sections_are_immutable_tuples(self):
        schema = freeze_schema("V1", ("a", "b"), ("c",))
        self.assertIsInstance(schema.artefact_fields, tuple)
        self.assertIsInstance(schema.response_fields, tuple)
        with self.assertRaises(AttributeError):
            schema.artefact_fields.append("x")

    def test_digest_is_deterministic(self):
        a = freeze_schema("V1", ("a", "b"), ("c",))
        b = freeze_schema("V1", ("a", "b"), ("c",))
        self.assertEqual(a.digest, b.digest)

    def test_either_section_change_changes_the_one_identity(self):
        base = freeze_schema("V1", ("a", "b"), ("c",))
        artefact_changed = freeze_schema("V1", ("a", "b", "d"), ("c",))
        response_changed = freeze_schema("V1", ("a", "b"), ("c", "d"))
        version_changed = freeze_schema("V2", ("a", "b"), ("c",))
        self.assertNotEqual(base.digest, artefact_changed.digest)
        self.assertNotEqual(base.digest, response_changed.digest)
        self.assertNotEqual(base.digest, version_changed.digest)

    def test_duplicate_field_names_refused(self):
        with self.assertRaises(ValueError):
            freeze_schema("V1", ("a", "a"), ("c",))
        with self.assertRaises(ValueError):
            freeze_schema("V1", ("a",), ("c", "c"))

    def test_nameless_field_or_version_refused(self):
        # WHITESPACE-ONLY names nothing (Stage 1's settled term).
        with self.assertRaises(ValueError):
            freeze_schema("V1", ("a", "   "), ("c",))
        with self.assertRaises(ValueError):
            freeze_schema("  ", ("a",), ("c",))
        with self.assertRaises(ValueError):
            freeze_schema("V1", (), ("c",))


if __name__ == "__main__":
    unittest.main()

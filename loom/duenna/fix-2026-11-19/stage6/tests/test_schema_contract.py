"""Stage 6 — K12: the pinned schema artefact, the preserved
delivered instruction, the bound checker, and Test 6 case 4
(schema changed under an unchanged checker, and checker
changed under an unchanged schema, each producing an
attributable finding). Plus the causal table's remaining
branches as controls: agreement, MODEL, INPUT, UNKNOWN.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from attribution import SYSTEM, MODEL, INPUT, UNKNOWN  # noqa: E402
from schema_contract import (  # noqa: E402
    Checker, DeliveredInstruction, PinnedSchema,
    ResponseContract, examine, record_finding)
from stage6_support import fresh_record  # noqa: E402

CONTRACT = ResponseContract(
    name="status-report", kind="regex",
    pattern=r"STATUS:\s*(OPEN|CLOSED)", markers=("STATUS:",),
    value_domain=("OPEN", "CLOSED"))
FIELDS = ("artifact", "evidence", "fixtures_total")
INSTRUCTION_PRESCRIBING = (
    "State the outcome. Answer with one line in the form "
    "STATUS: OPEN or STATUS: CLOSED.")
INSTRUCTION_SILENT = "State the outcome the record supports."


def make_schema(contract=CONTRACT, fields=FIELDS):
    return PinnedSchema(fields, contract)


class TestPinnedSchemaArtefact(unittest.TestCase):

    def test_one_identity_over_both_sections(self):
        a = make_schema()
        other_fields = make_schema(fields=FIELDS + ("extra",))
        other_contract = make_schema(contract=ResponseContract(
            name="status-report", kind="regex",
            pattern=r"RESULT:\s*(OPEN|CLOSED)",
            markers=("RESULT:",), value_domain=("OPEN", "CLOSED")))
        # Changing EITHER section changes the one identity:
        # the sections are frozen together, not separately
        # versioned under one label.
        self.assertNotEqual(a.digest, other_fields.digest)
        self.assertNotEqual(a.digest, other_contract.digest)

    def test_schema_and_contract_are_sealed(self):
        schema = make_schema()
        with self.assertRaises(AttributeError):
            schema.artefact_fields = ("tampered",)
        with self.assertRaises(AttributeError):
            schema.contract.pattern = r"STATUS:\s*(.*)"
        with self.assertRaises(AttributeError):
            del schema.contract

    def test_checker_binding_comes_from_the_frozen_object(self):
        schema = make_schema()
        checker = Checker(schema)
        self.assertEqual(checker.schema_digest, schema.digest)
        self.assertIs(checker.contract, schema.contract)

    def test_delivered_instruction_is_preserved_in_full(self):
        schema = make_schema()
        instruction = DeliveredInstruction(
            INSTRUCTION_SILENT, schema.digest)
        # The actual content, not a reference to it.
        self.assertEqual(instruction.content, INSTRUCTION_SILENT)
        self.assertEqual(instruction.schema_digest, schema.digest)
        other = DeliveredInstruction(
            INSTRUCTION_SILENT + " (amended)", schema.digest)
        self.assertNotEqual(instruction.digest, other.digest)


class TestChangedUnderUnchanged(unittest.TestCase):
    """Test 6, case 4 — each change, separately, produces an
    attributable finding."""

    def setUp(self):
        self.schema = make_schema()
        self.pin = self.schema.digest
        self.checker = Checker(self.schema)
        self.instruction = DeliveredInstruction(
            INSTRUCTION_PRESCRIBING, self.schema.digest)
        self.response = "STATUS: OPEN"

    def test_schema_changed_checker_unchanged(self):
        changed_schema = make_schema(fields=FIELDS + ("late_field",))
        finding = examine(self.pin, changed_schema, self.checker,
                          self.instruction, self.response, "OPEN")
        self.assertEqual(finding["kind"], "SCHEMA_BINDING_DIVERGENCE")
        self.assertEqual(finding["attribution"], SYSTEM)
        self.assertEqual(finding["moved_sides"], ["schema"])

    def test_checker_changed_schema_unchanged(self):
        # A checker quoting the genuine digest but running a
        # different contract than the schema's frozen section.
        forged = Checker._forged(self.pin, ResponseContract(
            name="status-report", kind="regex",
            pattern=r"VERDICT:\s*(OPEN|CLOSED)",
            markers=("VERDICT:",), value_domain=("OPEN", "CLOSED")))
        finding = examine(self.pin, self.schema, forged,
                          self.instruction, self.response, "OPEN")
        self.assertEqual(finding["kind"], "SCHEMA_BINDING_DIVERGENCE")
        self.assertEqual(finding["attribution"], SYSTEM)
        self.assertIn("checker_contract", finding["moved_sides"])

    def test_checker_rebound_to_another_schema(self):
        other = make_schema(fields=("only", "fields"))
        rebound = Checker(other)
        finding = examine(self.pin, self.schema, rebound,
                          self.instruction, self.response, "OPEN")
        self.assertEqual(finding["kind"], "SCHEMA_BINDING_DIVERGENCE")
        self.assertEqual(finding["attribution"], SYSTEM)
        self.assertIn("checker", finding["moved_sides"])


class TestCausalTableControls(unittest.TestCase):
    """The remaining branches of examine()'s causal table,
    as controls — the reproductions exercise the
    FORMAT_NOT_RECOGNISED branch against real evidence."""

    def setUp(self):
        self.schema = make_schema()
        self.pin = self.schema.digest
        self.checker = Checker(self.schema)

    def test_agreement(self):
        instruction = DeliveredInstruction(
            INSTRUCTION_PRESCRIBING, self.pin)
        finding = examine(self.pin, self.schema, self.checker,
                          instruction, "STATUS: CLOSED", "CLOSED")
        self.assertEqual(finding["kind"], "AGREEMENT")
        self.assertIsNone(finding["attribution"])

    def test_model_branch(self):
        instruction = DeliveredInstruction(
            INSTRUCTION_PRESCRIBING, self.pin)
        finding = examine(self.pin, self.schema, self.checker,
                          instruction, "I decline to answer.",
                          "OPEN")
        self.assertEqual(finding["kind"],
                         "VALUE_NOT_STATED_AS_PRESCRIBED")
        self.assertEqual(finding["attribution"], MODEL)

    def test_checker_defect_on_compliant_response(self):
        # The response complies in form and value; a checker
        # whose pattern cannot match its own contract's form
        # still extracts nothing -> the defect is the
        # checker's. Modelled by a contract whose extraction
        # pattern disagrees with its declared markers, bound
        # consistently to its own schema.
        broken_contract = ResponseContract(
            name="status-report", kind="regex",
            pattern=r"STATUS :\s*(OPEN|CLOSED)",
            markers=("STATUS:",), value_domain=("OPEN", "CLOSED"))
        schema = make_schema(contract=broken_contract)
        instruction = DeliveredInstruction(
            INSTRUCTION_PRESCRIBING, schema.digest)
        finding = examine(schema.digest, schema, Checker(schema),
                          instruction, "STATUS: OPEN", "OPEN")
        self.assertEqual(finding["kind"],
                         "CHECKER_FAILED_ON_COMPLIANT_RESPONSE")
        self.assertEqual(finding["attribution"], SYSTEM)

    def test_input_branch(self):
        instruction = DeliveredInstruction(
            INSTRUCTION_PRESCRIBING, self.pin)
        finding = examine(self.pin, self.schema, self.checker,
                          instruction, "STATUS: OPEN", "OPEN",
                          input_defect="the supplied worksheet "
                                       "omitted the adjudication row")
        self.assertEqual(finding["kind"], "INPUT_DEFECT")
        self.assertEqual(finding["attribution"], INPUT)

    def test_unknown_branch(self):
        instruction = DeliveredInstruction(
            INSTRUCTION_SILENT, self.pin)
        finding = examine(self.pin, self.schema, self.checker,
                          instruction, "No status is given here.",
                          "OPEN")
        self.assertEqual(finding["kind"], "UNRESOLVED_DISAGREEMENT")
        self.assertEqual(finding["attribution"], UNKNOWN)


class TestFindingIsRecorded(unittest.TestCase):

    def test_finding_event_on_the_record(self):
        record, _ = fresh_record(self)
        schema = make_schema()
        finding = examine(schema.digest, schema, Checker(schema),
                          DeliveredInstruction(INSTRUCTION_SILENT,
                                               schema.digest),
                          "The status is OPEN, in prose.", "OPEN")
        self.assertEqual(finding["kind"], "FORMAT_NOT_RECOGNISED")
        event = record_finding(record, finding)
        events = record.read_all()
        self.assertEqual(events[-1]["digest"], event["digest"])
        self.assertEqual(events[-1]["body"]["attribution"], SYSTEM)


if __name__ == "__main__":
    unittest.main()

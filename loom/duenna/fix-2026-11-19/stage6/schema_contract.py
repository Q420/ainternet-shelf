"""Duenna Stage 6 — the checker/response contract (K12) and
the pinned schema artefact.

K12's enforceable form: "one pinned schema artefact
(identity + digest), held in the run's single frozen schema
object (K5). The instruction actually delivered to the
subject references that schema identity; the delivered
instruction content itself is PRESERVED — the actual content,
not merely a reference in a prompt-building log; the
checker/parser is bound to the same schema identity. A
disagreement among instruction, response and checker is
recorded as a schema/checker/response FINDING with its
source attributable where evidence permits — never silently
converted into a null extraction or a subject failure.
Attribution follows the causal source: a defective
instruction or schema AUTHORED BY DUENNA is SYSTEM; INPUT is
reserved for defects in what was supplied TO the agent."

The objects:

- ``PinnedSchema`` — ONE frozen schema object carrying both
  sections (the artefact-field contract and the
  checker/response contract), frozen together under one
  digest (K5: the two sections are versioned and frozen
  together; a mutable nested section would recreate the
  duplicated-authority problem under one outer identity).
  Sealed: neither section can be mutated after the freeze.
- ``DeliveredInstruction`` — the instruction as actually
  delivered, content preserved in full, referencing the
  schema identity it was delivered under.
- ``Checker`` — bound at construction to a schema identity
  obtained FROM THE FROZEN SCHEMA OBJECT (G5: the anchor
  comes from the frozen object, not from the validated
  component's own quote of it).

``examine()`` is the finding machinery. Given the three
parties (instruction, response, checker) plus the schema as
presented and the independently held pin, it returns a
FINDING — a first-class record, never a null and never a
subject failure — attributing the disagreement to its causal
source where the preserved evidence permits, and honestly
UNKNOWN where it does not.
"""

from __future__ import annotations

import hashlib
import json
import re

from binder import CHAIN_VERIFICATION_FAILED, verify_record_current

from attribution import RecordIntegrityRefused, SYSTEM, MODEL, INPUT, UNKNOWN
from authority import _Sealed

FINDING_RECORDED = "FINDING_RECORDED"


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _digest(obj) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


class SchemaRefused(Exception):
    """A schema operation was refused: a binding that does
    not resolve, or an examination missing a party. Nothing
    was recorded on this path."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"schema refused: {details!r}")


class ResponseContract(_Sealed):
    """The checker/response half of the schema, as data: what
    format the checker demands of a response, and the literal
    markers whose presence in a delivered instruction would
    show that format was actually prescribed to the subject.
    The markers matter: a checker may only hold a subject to
    a format the subject was given, and given-ness is
    checkable against the preserved instruction only if the
    demanded format has a stated literal signature."""

    def __init__(self, name: str, kind: str, pattern: str = None,
                 line_template: str = None, markers=(),
                 value_domain=()):
        if kind not in ("regex", "lines"):
            raise SchemaRefused({"reason": "unknown contract kind",
                                 "kind": kind})
        self.name = name
        self.kind = kind
        self.pattern = pattern
        self.line_template = line_template
        self.markers = tuple(markers)
        self.value_domain = tuple(value_domain)
        self._sealed = True

    def as_dict(self) -> dict:
        return {"name": self.name, "kind": self.kind,
                "pattern": self.pattern,
                "line_template": self.line_template,
                "markers": list(self.markers),
                "value_domain": list(self.value_domain)}

    def extract(self, response: str, expected: dict = None):
        """Run the demanded extraction over a response, in
        the contract's own terms. Returns the extracted value
        (a string for regex contracts; the expected mapping
        for lines contracts when every line is present) or
        None — the historical 'null extraction', which under
        K12 is the START of a finding, never a result."""
        if self.kind == "regex":
            m = re.search(self.pattern, response)
            return m.group(1) if m else None
        # lines: every expected "key: value" line present
        # literally in the response.
        if expected is None:
            raise SchemaRefused(
                {"reason": "a lines contract extracts against "
                           "an expected mapping"})
        for key, value in expected.items():
            line = self.line_template.format(key=key, value=value)
            if line not in response:
                return None
        return dict(expected)

    def values_stated(self, response: str, expected) -> bool:
        """Does the response state the expected value(s) in
        ANY form? (Presence of the value tokens, not of the
        demanded format.) This separates 'the answer is
        there, in another shape' from 'the answer is not
        there at all'."""
        if isinstance(expected, dict):
            return all(str(v) in response
                       for v in expected.values())
        return str(expected) in response

    def format_prescribed(self, instruction_text: str) -> bool:
        """Was the demanded format actually prescribed in the
        delivered instruction? Checkable only because the
        contract declares its literal markers and the
        instruction's content is preserved."""
        return any(marker in instruction_text
                   for marker in self.markers)


class PinnedSchema(_Sealed):
    """The one frozen schema object: artefact-field section
    and checker/response section, frozen together. Its
    digest — over BOTH sections — is the schema identity
    everything else binds to."""

    def __init__(self, artefact_fields, contract: ResponseContract):
        self.artefact_fields = tuple(artefact_fields)
        self.contract = contract
        self._sealed = True

    def contents(self) -> dict:
        return {"artefact_fields": list(self.artefact_fields),
                "response_contract": self.contract.as_dict()}

    @property
    def digest(self) -> str:
        return _digest(self.contents())


class DeliveredInstruction(_Sealed):
    """An instruction as actually delivered to a subject:
    the FULL content preserved (not a reference to it), and
    the schema identity it was delivered under. Preservation
    is the point (K12 v3): without the actual content, no
    later examination can establish what the subject was
    told."""

    def __init__(self, content: str, schema_digest: str):
        self.content = content
        self.schema_digest = schema_digest
        self._sealed = True

    @property
    def digest(self) -> str:
        return _digest({"content": self.content,
                        "schema_digest": self.schema_digest})


class Checker(_Sealed):
    """A checker/parser bound to one schema identity. The
    binding is taken from the frozen schema object at
    construction (G5) — a checker that merely QUOTES a
    digest it was handed by the component it checks is not
    bound, it is echoing."""

    def __init__(self, schema: PinnedSchema):
        self.schema_digest = schema.digest
        self.contract = schema.contract
        self._sealed = True

    @classmethod
    def _forged(cls, schema_digest: str, contract: ResponseContract):
        """A checker presenting a binding it constructed
        itself — used by the sabotage tests to model a
        checker changed outside the schema. Construction is
        possible (anyone can assemble an object); what the
        examination checks is whether its binding RESOLVES
        to the pin."""
        obj = object.__new__(cls)
        object.__setattr__(obj, "schema_digest", schema_digest)
        object.__setattr__(obj, "contract", contract)
        object.__setattr__(obj, "_sealed", True)
        return obj


def examine(pinned_schema_digest: str, schema: PinnedSchema,
            checker: Checker, instruction: DeliveredInstruction,
            response: str, expected,
            input_defect: str = None) -> dict:
    """Examine a checker/response/instruction disagreement
    and return the FINDING. ``pinned_schema_digest`` is held
    independently of all three parties (the examiner's pin).

    The causal table (K12):
    - the schema as presented, or the checker's binding,
      diverges from the pin -> the divergence is between two
      Duenna-held instruments -> SYSTEM, naming the side(s)
      that moved;
    - a defect in what was supplied TO the agent (input
      artefacts) -> INPUT;
    - the response states the value, the checker extracts
      nothing, and the demanded format was never prescribed
      in the preserved instruction -> the checker held a
      private format -> SYSTEM;
    - the response states the value in the prescribed format
      and the checker still extracts nothing -> checker
      defect -> SYSTEM;
    - the value is not stated and the format WAS prescribed
      -> the subject did not follow a given instruction ->
      MODEL;
    - the value is not stated and no format was prescribed
      -> the evidence does not separate the causes ->
      UNKNOWN."""
    finding = {
        "instruction_digest": instruction.digest,
        "instruction_schema_ref": instruction.schema_digest,
        "schema_digest_presented": schema.digest,
        "checker_schema_binding": checker.schema_digest,
        "response_digest": _digest({"response": response}),
        "contract": checker.contract.name,
        "expected": expected,
    }
    moved = []
    if schema.digest != pinned_schema_digest:
        moved.append("schema")
    if checker.schema_digest != pinned_schema_digest:
        moved.append("checker")
    if checker.contract.as_dict() != schema.contract.as_dict():
        # A checker quoting the right digest but running a
        # contract that is not the schema's frozen section is
        # a changed checker: the schema object is the one
        # home of the contract (K5), and a quoted digest is
        # an echo, not a binding (G5).
        moved.append("checker_contract")
    if instruction.schema_digest != pinned_schema_digest:
        moved.append("instruction_reference")
    if moved:
        finding.update({
            "kind": "SCHEMA_BINDING_DIVERGENCE",
            "attribution": SYSTEM,
            "moved_sides": moved,
            "basis": ["the presented schema / checker binding "
                      "does not resolve to the independently "
                      "held pin; the divergence is between "
                      "Duenna-held instruments, so its source "
                      "is Duenna's own machinery"]})
        return finding
    if input_defect is not None:
        finding.update({
            "kind": "INPUT_DEFECT",
            "attribution": INPUT,
            "basis": ["defect in what was supplied TO the "
                      "agent: " + input_defect]})
        return finding
    contract = checker.contract
    extracted = contract.extract(response, expected
                                 if contract.kind == "lines"
                                 else None)
    finding["extracted"] = extracted
    if extracted is not None and extracted == expected:
        finding.update({"kind": "AGREEMENT",
                        "attribution": None,
                        "basis": ["the checker extracts the "
                                  "expected value; no "
                                  "disagreement to attribute"]})
        return finding
    stated = contract.values_stated(response, expected)
    prescribed = contract.format_prescribed(instruction.content)
    finding["value_stated"] = stated
    finding["format_prescribed"] = prescribed
    if extracted is not None:
        # The checker extracted A value, but not the expected
        # one: a value disagreement, distinct from the
        # null-extraction family above.
        finding.update({
            "kind": "VALUE_DISAGREEMENT",
            "attribution": MODEL if prescribed else UNKNOWN,
            "basis": ["the checker extracted "
                      f"{extracted!r} where {expected!r} was "
                      "expected; the response stated a "
                      "different value"
                      + (" in the prescribed format"
                         if prescribed else
                         ", and the demanded format was not "
                         "prescribed, so the evidence does "
                         "not separate a subject error from "
                         "an extraction artefact")]})
        return finding
    if stated and not prescribed:
        finding.update({
            "kind": "FORMAT_NOT_RECOGNISED",
            "attribution": SYSTEM,
            "basis": ["the response states the expected "
                      "value(s); the checker's demanded "
                      "format appears nowhere in the "
                      "preserved delivered instruction; the "
                      "checker held a private format for a "
                      "fact the instruction did not define "
                      "that way (the DR-19 mechanism)"]})
    elif stated and prescribed:
        finding.update({
            "kind": "CHECKER_FAILED_ON_COMPLIANT_RESPONSE",
            "attribution": SYSTEM,
            "basis": ["the response states the expected "
                      "value(s) in the prescribed format and "
                      "the checker still extracts nothing; "
                      "the defect is in the checker"]})
    elif not stated and prescribed:
        finding.update({
            "kind": "VALUE_NOT_STATED_AS_PRESCRIBED",
            "attribution": MODEL,
            "basis": ["the delivered instruction prescribed "
                      "the format and the response does not "
                      "state the expected value; the failure "
                      "is the subject's"]})
    else:
        finding.update({
            "kind": "UNRESOLVED_DISAGREEMENT",
            "attribution": UNKNOWN,
            "basis": ["the response does not state the "
                      "expected value and no format was "
                      "prescribed; the preserved evidence "
                      "does not separate checker, instruction "
                      "and subject causes"]})
    return finding


def record_finding(record, finding: dict) -> dict:
    """Record a finding on the record (verify-then-append,
    the stage discipline). A finding is a first-class event:
    it is what an attribution's basis cites, and what a
    discrepancy can link to."""
    events, failure = verify_record_current(record)
    if failure is not None:
        raise RecordIntegrityRefused(
            {CHAIN_VERIFICATION_FAILED: failure})
    return record.append(FINDING_RECORDED, finding)

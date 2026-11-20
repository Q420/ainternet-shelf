"""Duenna Stage 2 — the one frozen schema object (K5).

K5 specifies ONE frozen schema object per run, containing both the
artefact-field contract and the checker/response contract (K12) as two
sections of one object — one identity, one home, no second schema
fact. The two sections are VERSIONED AND FROZEN TOGETHER: a mutable
nested section would recreate the duplicated-authority problem under
one outer identity.

This module is that object. ``freeze_schema`` takes both sections and
the version in a single call — there is no API that freezes or alters
one section separately — and returns a :class:`FrozenSchema` whose
state cannot be mutated afterwards (attribute assignment raises;
sections are exposed as tuples). The schema's identity is its digest:
SHA-256 over the canonical encoding of (version, artefact section,
response section), so a change to either section is a change of
identity.

Field names in an artefact ARE the schema's names by reference (K5):
construction (construction.py) compares the artefact's field names
against these tuples exactly — a renamed field is a different field,
not a variant of the right one.

TEST SCHEMA FIXTURE: ``TEST_SCHEMA`` below is the harness's frozen
test schema. Its artefact section carries the three fields DR-02
names (``artifact``, ``evidence``, ``fixtures_total``) plus the
remaining contract fields of the battery-artefact family, eight in
all, matching the eight-field shape of the T05/T08 artefacts. The
fixture exercises the schema *mechanism* — one object, two sections,
jointly frozen, digest-identified. The production field inventory is
a run-configuration fact (K3), not something this stage settles.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K5, K12),
PROCESS-TREE-AND-PLAN.md v2, Stage 2; DEFECT-REGISTER.md DR-02.
"""

from __future__ import annotations

import hashlib

from record import _canonical


def _has_content(value) -> bool:
    """Whether a value actually names something (Stage 1's settled
    WHITESPACE-ONLY term): a string of nothing but whitespace is
    present but names nothing, so it cannot be a field name or a
    version."""
    return isinstance(value, str) and bool(value.strip())


def _validate_section(section_name: str, fields) -> tuple:
    """Validate one section's field names; returns them as a tuple.

    A section must be a non-empty sequence of distinct field names,
    each a string that names something.
    """
    if isinstance(fields, (str, bytes)) or not hasattr(fields, "__iter__"):
        raise ValueError(
            f"schema section {section_name!r} must be a sequence of "
            f"field names, got {fields!r}")
    names = tuple(fields)
    if not names:
        raise ValueError(f"schema section {section_name!r} is empty")
    for name in names:
        if not _has_content(name):
            raise ValueError(
                f"schema section {section_name!r} has a field name "
                f"that names nothing: {name!r}")
    if len(set(names)) != len(names):
        raise ValueError(
            f"schema section {section_name!r} has duplicate field "
            f"names: {names!r}")
    return names


class FrozenSchema:
    """One schema object with jointly frozen sections.

    Construct via :func:`freeze_schema`. After construction the
    object is frozen: attribute assignment raises AttributeError,
    and the sections are tuples, so neither section can be altered
    in place. Both sections and the version are bound into the one
    digest — the schema's single identity.
    """

    __slots__ = ("_version", "_artefact_fields", "_response_fields",
                 "_digest", "_frozen")

    def __init__(self, version: str, artefact_fields,
                 response_fields):
        object.__setattr__(self, "_frozen", False)
        if not _has_content(version):
            raise ValueError(
                f"schema version must name something: {version!r}")
        artefact = _validate_section("artefact", artefact_fields)
        response = _validate_section("response", response_fields)
        payload = {
            "version": version,
            "artefact_fields": list(artefact),
            "response_fields": list(response),
        }
        digest = hashlib.sha256(_canonical(payload)).hexdigest()
        object.__setattr__(self, "_version", version)
        object.__setattr__(self, "_artefact_fields", artefact)
        object.__setattr__(self, "_response_fields", response)
        object.__setattr__(self, "_digest", digest)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                "schema is frozen: its sections were frozen together "
                "at construction and cannot be altered")
        object.__setattr__(self, name, value)

    @property
    def version(self) -> str:
        return self._version

    @property
    def artefact_fields(self) -> tuple:
        """The artefact-field contract: the schema's field names,
        by reference. Construction compares against these exactly."""
        return self._artefact_fields

    @property
    def response_fields(self) -> tuple:
        """The checker/response contract section (K12), frozen
        together with the artefact section under the one digest."""
        return self._response_fields

    @property
    def digest(self) -> str:
        return self._digest

    def __repr__(self) -> str:
        return (f"FrozenSchema(version={self._version!r}, "
                f"digest={self._digest[:12]}…)")


def freeze_schema(version: str, artefact_fields,
                  response_fields) -> FrozenSchema:
    """Freeze one schema object from its two sections and version.

    The ONLY way to make a schema: both sections are supplied and
    frozen in the same act, under the one digest.
    """
    return FrozenSchema(version, artefact_fields, response_fields)


# Clearly-marked TEST schema fixture (see module docstring). The
# artefact section's first three fields are the ones DR-02 names.
TEST_SCHEMA = freeze_schema(
    "TEST-SCHEMA-1",
    artefact_fields=(
        "artifact",
        "evidence",
        "fixtures_total",
        "fixtures_passed",
        "run_id",
        "tree_id",
        "subject",
        "outcome",
    ),
    response_fields=(
        "check_id",
        "outcome",
        "evidence_ref",
    ),
)

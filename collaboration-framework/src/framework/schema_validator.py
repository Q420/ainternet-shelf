"""The pure argument validator — the native adapter piece's
one new component (NATIVE-ADAPTER-SCOPE Rev 3, N8; build
brief B2).

A resolved native call's arguments are validated against
its catalogue entry's parameter schema — the registry's
worker-facing schema the catalogue carries
(`tool_policy.worker_facing`, joined into the entry by the
loop's catalogue derivation): a list of parameter
declarations, each naming exactly a `name` (a non-empty
string), a `required` flag (a boolean) and a `meaning` (a
string). That list is the only schema form this validator
supports.

The validator is a pure, deterministic function of
(schema, arguments): no I/O, no record access, no clock, no
randomness. Its verdict is "valid" or "invalid" with the
first failing constraint named. Conformance is strict:

- no type coercion — a value stands as it was emitted;
- no invented defaults — a missing required parameter is
  invalid, never filled in;
- no undeclared fields — an argument field the schema
  does not declare is invalid, not a detail left to the
  doorway's ceiling check (schema conformance and grant
  scope are different questions, and both are asked, in
  that order — N8).

A schema construct the validator does not support fails
closed: the call is invalid, with the unsupported
construct named — never silently ignored.

The checks run in one fixed order, so the named first
failing constraint is deterministic:

1. the schema's own form — a list of declarations, each
   naming exactly name/required/meaning, the name a
   non-empty string, required a boolean, meaning a
   string, no name declared twice;
2. the arguments' form — an object;
3. required parameters absent, in declaration order;
4. undeclared argument fields, in sorted field order.

This module lives at the native translation boundary
only. The doorway holds no copy of it — schema
conformance is a translation classification, not a
permission — and the independent checker implements its
own (build brief B5), reconstructing the same verdict
from the same inputs.
"""

from __future__ import annotations

__all__ = ["validate_arguments"]

_DECLARATION_FIELDS = {"name", "required", "meaning"}


def _unsupported(detail):
    return "invalid", f"unsupported schema construct: {detail}"


def validate_arguments(schema, arguments):
    """Validate `arguments` against a catalogue entry's
    parameter schema. Returns (verdict, constraint):
    ("valid", None) or ("invalid", <the first failing
    constraint, named>). Pure and deterministic in
    (schema, arguments)."""
    # 1. The schema's own form. Anything outside the one
    # supported form fails closed, the construct named.
    if not isinstance(schema, list):
        return _unsupported(
            "the parameter schema is not a list of "
            "parameter declarations")
    declared = []
    seen = set()
    for entry in schema:
        if not isinstance(entry, dict) or \
                set(entry) != _DECLARATION_FIELDS:
            return _unsupported(
                "a parameter declaration must name exactly "
                "name, required and meaning")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            return _unsupported(
                "a parameter declaration's name is not a "
                "non-empty string")
        if not isinstance(entry.get("required"), bool):
            return _unsupported(
                f"parameter {name!r} declares a non-boolean "
                f"required flag")
        if not isinstance(entry.get("meaning"), str):
            return _unsupported(
                f"parameter {name!r} declares a non-string "
                f"meaning")
        if name in seen:
            return _unsupported(
                f"parameter {name!r} is declared twice")
        seen.add(name)
        declared.append(entry)
    # 2. The arguments' form. (The translation boundary
    # refuses non-object arguments as malformed before
    # validation is reached; the verdict stands here so
    # the function is total over its inputs.)
    if not isinstance(arguments, dict):
        return "invalid", "the arguments are not an object"
    # 3. Required parameters absent, in declaration order.
    for entry in declared:
        if entry["required"] and entry["name"] not in arguments:
            return "invalid", \
                f"required parameter {entry['name']!r} is absent"
    # 4. Undeclared argument fields, in sorted field order.
    for field in sorted(arguments):
        if field not in seen:
            return "invalid", \
                f"parameter {field!r} is not declared"
    return "valid", None

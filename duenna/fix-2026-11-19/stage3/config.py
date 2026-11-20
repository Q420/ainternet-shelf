"""Duenna Stage 3 — the one configuration object (K3).

K3: exactly one configuration object per run, content-hashed at
freeze. The hash establishes the CONTENT identity of the
configuration — it does not prove any component consumed it;
consumption is enforced separately, by positive proof, through the
controlled access path (access.py) and the output-admission gate
(admission.py).

This module is the object itself. A draft configuration is a plain
dict assembled from the run's configuration surfaces; :func:`freeze_config`
validates it and returns a :class:`FrozenConfig` — immutable after
construction (attribute assignment raises; mapping sections are
handed out as fresh copies), its identity one digest (SHA-256 over
the canonical encoding of the whole validated draft), so a change
to any part is a change of identity.

What the draft carries, and why:

- ``subject_pin`` — the asserted subject (K2: an assertion, not an
  identity; verification is the binder's work, binder.py).
- ``subject_surfaces`` — the subject as named on each configuration
  surface (``driver`` and ``adapter``, the two surfaces DR-03
  names). DR-03's mechanism was subject identity independently
  represented in multiple locations, with the run-start identity
  not mechanically bound to the identity actually served. Here the
  surfaces are INPUTS to one object: the binder (G1) refuses the
  freeze unless every surface and the pin name the same subject.
- ``values`` — the governed values. Components may obtain governed
  values ONLY through the controlled access path; there are no
  component-local copies and no component-local defaults for
  governed values (K3(a)).
- ``derivations`` + ``policy`` — every transport limit is a
  configuration value carrying its derivation (K3, absorbing K13),
  and G1 evaluates derived limits against an objective constraint
  recorded in the configuration: :func:`derived_limit_problems`
  RECOMPUTES each derivation from its recorded inputs under the
  named formula and checks the limit's value against the
  recomputed requirement. A written rationale alone does not pass;
  a stated requirement that does not recompute does not pass; a
  bare constant with no derivation does not pass. (DR-21's
  established part: a fixed 120-second transport limit applied to
  runs whose reasoning envelopes were never consulted. Its
  decisive cause — lane latency vs timeout length — remains
  unestablished, as the register records, and nothing here claims
  it.)
- ``run_policy`` — the frozen run policy. ``on_subject_conflict``
  is ``INVALIDATE_RUN`` (a subject conflict invalidates the run's
  subject-dependent execution) or ``REFUSE_CAPTURE`` (only the
  mismatched capture and its dependents are refused). The plan's
  rule is refusal, not either/or, under EITHER policy: the
  conflict is recorded AND enforcement refuses; the policy only
  scopes how far the refusal reaches.
- ``tree_set`` — the frozen tree set, bound into the run identity
  by its own digest (K1).
- ``schema_digest`` — the pinned schema digest from the frozen
  configuration (G5's schema anchor): Stage 2's one frozen schema
  object enters this configuration by its digest, not by a second
  copy of its sections.

The one derivation formula this harness implements is
``reasoning_envelope``: the required transport limit, in seconds,
is ceil(max_reasoning_tokens / min_throughput_tps) computed from
the derivation's recorded inputs — the run's own reasoning
envelope and the lane's objective throughput floor recorded in
the configuration.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K1, K2, K3, G1,
G5), PROCESS-TREE-AND-PLAN.md v2, Stage 3; DEFECT-REGISTER.md
DR-03, DR-20, DR-21.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

from record import _canonical

REASONING_ENVELOPE = "reasoning_envelope"
INVALIDATE_RUN = "INVALIDATE_RUN"
REFUSE_CAPTURE = "REFUSE_CAPTURE"


def _names_something(value) -> bool:
    """Stage 1's settled WHITESPACE-ONLY term: a string of nothing
    but whitespace is present but names nothing."""
    return isinstance(value, str) and bool(value.strip())


class ConfigError(ValueError):
    """A draft configuration is structurally unusable: the freeze
    cannot proceed on it at all (distinct from a G1 refusal on a
    well-formed draft)."""


def _require_json_encodable(value: Any, what: str) -> None:
    try:
        _canonical(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(
            f"{what} is not JSON-encodable: {exc}") from exc


class FrozenConfig:
    """One frozen configuration object. Construct via
    :func:`freeze_config`. Immutable after construction; its
    identity is :attr:`digest`."""

    __slots__ = ("_pin", "_surfaces", "_values_json",
                 "_derivations_json", "_policy_json",
                 "_run_policy_json", "_tree_set_json",
                 "_tree_set_digest", "_schema_digest", "_digest",
                 "_frozen")

    def __init__(self, draft: dict):
        object.__setattr__(self, "_frozen", False)
        if not isinstance(draft, dict):
            raise ConfigError(
                f"draft configuration must be a dict, got "
                f"{type(draft).__name__}")
        _require_json_encodable(draft, "draft configuration")

        pin = draft.get("subject_pin")
        if not _names_something(pin):
            raise ConfigError(
                f"subject_pin must name something: {pin!r}")

        surfaces = draft.get("subject_surfaces")
        if not isinstance(surfaces, dict) or not surfaces:
            raise ConfigError(
                "subject_surfaces must be a non-empty dict of "
                "surface name -> subject")
        for surface in ("driver", "adapter"):
            if surface not in surfaces:
                raise ConfigError(
                    f"subject_surfaces is missing the {surface!r} "
                    f"surface (the surfaces DR-03 names)")
        for name, subject in surfaces.items():
            if not _names_something(name) or \
                    not _names_something(subject):
                raise ConfigError(
                    f"subject surface {name!r} must name a "
                    f"subject: {subject!r}")

        values = draft.get("values")
        if not isinstance(values, dict) or not values:
            raise ConfigError(
                "values must be a non-empty dict of governed "
                "values")
        for name in values:
            if not _names_something(name):
                raise ConfigError(
                    f"governed value name names nothing: {name!r}")

        derivations = draft.get("derivations", {})
        if not isinstance(derivations, dict):
            raise ConfigError("derivations must be a dict")
        policy = draft.get("policy", {})
        if not isinstance(policy, dict):
            raise ConfigError("policy must be a dict")
        derived_limits = policy.get("derived_limits", [])
        if not isinstance(derived_limits, list) or \
                any(not _names_something(n) for n in derived_limits):
            raise ConfigError(
                "policy.derived_limits must be a list of governed "
                "value names")

        run_policy = draft.get(
            "run_policy", {"on_subject_conflict": INVALIDATE_RUN})
        if not isinstance(run_policy, dict):
            raise ConfigError("run_policy must be a dict")
        on_conflict = run_policy.get(
            "on_subject_conflict", INVALIDATE_RUN)
        if on_conflict not in (INVALIDATE_RUN, REFUSE_CAPTURE):
            raise ConfigError(
                f"run_policy.on_subject_conflict must be "
                f"{INVALIDATE_RUN!r} or {REFUSE_CAPTURE!r}, got "
                f"{on_conflict!r}")

        tree_set = draft.get("tree_set")
        if not isinstance(tree_set, dict) or \
                not _names_something(tree_set.get("tree_id")):
            raise ConfigError(
                "tree_set must be a dict naming a tree_id")

        schema_digest = draft.get("schema_digest")
        if not _names_something(schema_digest):
            raise ConfigError(
                "schema_digest must name the pinned schema digest "
                "(G5's schema anchor)")

        digest = hashlib.sha256(_canonical(draft)).hexdigest()
        tree_set_digest = hashlib.sha256(
            _canonical(tree_set)).hexdigest()

        object.__setattr__(self, "_pin", pin)
        object.__setattr__(
            self, "_surfaces",
            tuple(sorted(surfaces.items())))
        object.__setattr__(
            self, "_values_json", _canonical(values).decode("utf-8"))
        object.__setattr__(
            self, "_derivations_json",
            _canonical(derivations).decode("utf-8"))
        object.__setattr__(
            self, "_policy_json",
            _canonical(policy).decode("utf-8"))
        object.__setattr__(
            self, "_run_policy_json",
            _canonical(run_policy).decode("utf-8"))
        object.__setattr__(
            self, "_tree_set_json",
            _canonical(tree_set).decode("utf-8"))
        object.__setattr__(self, "_tree_set_digest",
                           tree_set_digest)
        object.__setattr__(self, "_schema_digest", schema_digest)
        object.__setattr__(self, "_digest", digest)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                "configuration is frozen: it was frozen as one "
                "object at freeze and cannot be altered")
        object.__setattr__(self, name, value)

    @property
    def digest(self) -> str:
        """The configuration identity (K3): SHA-256 over the
        canonical encoding of the whole validated draft."""
        return self._digest

    @property
    def subject_pin(self) -> str:
        return self._pin

    @property
    def subject_surfaces(self) -> dict:
        """Surface name -> subject named on that surface, as a
        fresh dict (the frozen state cannot be mutated through
        it)."""
        return dict(self._surfaces)

    @property
    def values(self) -> dict:
        """The governed values, as a fresh dict."""
        return json.loads(self._values_json)

    @property
    def derivations(self) -> dict:
        return json.loads(self._derivations_json)

    @property
    def policy(self) -> dict:
        return json.loads(self._policy_json)

    @property
    def run_policy(self) -> dict:
        return json.loads(self._run_policy_json)

    @property
    def on_subject_conflict(self) -> str:
        return self.run_policy.get(
            "on_subject_conflict", INVALIDATE_RUN)

    @property
    def tree_set(self) -> dict:
        return json.loads(self._tree_set_json)

    @property
    def tree_set_digest(self) -> str:
        return self._tree_set_digest

    @property
    def schema_digest(self) -> str:
        return self._schema_digest

    def __repr__(self) -> str:
        return (f"FrozenConfig(pin={self._pin!r}, "
                f"digest={self._digest[:12]}…)")


def freeze_config(draft: dict) -> FrozenConfig:
    """Freeze one configuration object from a draft. The ONLY way
    to make a FrozenConfig: the whole draft is validated and
    frozen in the same act, under the one digest."""
    return FrozenConfig(draft)


def _recompute_requirement(derivation: dict) -> int | None:
    """Recompute a derivation's requirement from its recorded
    inputs under its named formula. Returns None when the
    derivation cannot be recomputed at all (unknown formula or
    unusable inputs) — which is itself a policy failure, never a
    pass."""
    if not isinstance(derivation, dict):
        return None
    if derivation.get("formula") != REASONING_ENVELOPE:
        return None
    inputs = derivation.get("inputs")
    if not isinstance(inputs, dict):
        return None
    tokens = inputs.get("max_reasoning_tokens")
    tps = inputs.get("min_throughput_tps")
    if not isinstance(tokens, int) or isinstance(tokens, bool) \
            or tokens <= 0:
        return None
    if not isinstance(tps, (int, float)) or isinstance(tps, bool) \
            or tps <= 0:
        return None
    return math.ceil(tokens / tps)


def derived_limit_problems(config: FrozenConfig) -> dict:
    """G1's policy check on derived limits (K3): for every limit
    the configuration's policy names as derived, the limit must be
    a governed value, must carry a derivation, the derivation's
    stated requirement must RECOMPUTE from its recorded inputs,
    and the limit's value must meet the recomputed requirement.
    Returns a dict of problems; empty iff every derived limit
    passes. A written rationale alone does not pass — there is no
    field in a derivation this check reads except formula, inputs
    and the stated requirement it verifies."""
    problems: dict = {}
    values = config.values
    derivations = config.derivations
    for name in config.policy.get("derived_limits", []):
        if name not in values:
            problems.setdefault(
                "derived_limit_not_a_governed_value",
                []).append(name)
            continue
        derivation = derivations.get(name)
        if derivation is None:
            problems.setdefault(
                "derivation_missing", []).append(name)
            continue
        recomputed = _recompute_requirement(derivation)
        if recomputed is None:
            problems.setdefault(
                "derivation_does_not_recompute", []).append(name)
            continue
        stated = derivation.get("required")
        if stated != recomputed:
            problems.setdefault(
                "derivation_required_does_not_recompute",
                []).append({
                    "limit": name,
                    "stated": stated,
                    "recomputed": recomputed,
                })
            continue
        value = values[name]
        if not isinstance(value, (int, float)) \
                or isinstance(value, bool) or value < recomputed:
            problems.setdefault(
                "limit_below_derived_requirement", []).append({
                    "limit": name,
                    "value": value,
                    "required": recomputed,
                })
    return problems

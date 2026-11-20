"""Duenna Stage 3 — the controlled configuration access path
(K3 consumption, by positive proof).

K3: the configuration hash establishes the CONTENT identity of
the configuration; it does not prove any component consumed it.
Consumption is enforced and evidenced separately, by POSITIVE
PROOF:

(a) all governed values reach components through a single
    controlled access path — this module. There are no
    component-local copies and no component-local defaults for
    governed values: the path supplies only values the frozen
    configuration actually holds, so a component cannot obtain a
    governed value from it that the configuration does not have,
    and cannot obtain a frozen value under any other name or
    number than the frozen one.
(b) the access path issues a CONSUMPTION RECEIPT for each
    component invocation, identifying the component, the
    invocation, the configuration (by digest), and the governed
    values supplied. A scoped receipt covers a declared set of
    values for one invocation.
(c) every governed output references its consumption receipt,
    and the output-admission check (admission.py) verifies the
    receipt exists, matches the output's producing invocation,
    and covers the required values. An output without valid
    consumption evidence is NOT ADMITTED. Consumption is a
    precondition, not a later audit observation.

The path is a capability: a :class:`ConfigAccess` exists only
for a :class:`~binder.FrozenRun` — a run whose freeze succeeded
at G1. Receipts are recorded on the run's record as
``CONSUMPTION_RECEIPT`` events and registered here by the event
digest the record returned at append time (the Stage 2 pattern:
a receipt the path did not issue is not a receipt, whatever its
contents claim — the output gate checks the registry, never a
presented receipt's self-description).

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K3, G5),
PROCESS-TREE-AND-PLAN.md v2, Stage 3.
"""

from __future__ import annotations

CONSUMPTION_RECEIPT = "CONSUMPTION_RECEIPT"


class Receipt:
    """One consumption receipt: the access path supplied the
    named governed values, at their frozen values, to one
    component invocation under one frozen configuration.

    ``receipt_id`` is the digest of the ``CONSUMPTION_RECEIPT``
    event on the record — the receipt's identity is the recorded
    event, not anything a component presents."""

    __slots__ = ("receipt_id", "run_id", "component", "invocation",
                 "config_digest", "values", "seq")

    def __init__(self, receipt_id, run_id, component, invocation,
                 config_digest, values, seq):
        self.receipt_id = receipt_id
        self.run_id = run_id
        self.component = component
        self.invocation = invocation
        self.config_digest = config_digest
        self.values = values
        self.seq = seq

    @property
    def value_names(self) -> tuple:
        return tuple(sorted(self.values))

    def __repr__(self) -> str:
        return (f"Receipt(id={self.receipt_id[:12]}…, "
                f"component={self.component!r}, "
                f"invocation={self.invocation!r})")


class ConfigAccess:
    """The single controlled access path to one frozen run's
    governed values. The sole issuer of consumption receipts
    for that run."""

    def __init__(self, frozen_run):
        self.run = frozen_run
        self.record = frozen_run.record
        # receipt_id -> Receipt, in issue order (dict preserves
        # insertion order).
        self._receipts: dict[str, Receipt] = {}

    def consume(self, component: str, invocation: str,
                value_names) -> Receipt:
        """Supply the named governed values to one component
        invocation and issue its consumption receipt.

        The values supplied are the FROZEN configuration's
        values, read from the frozen object — the caller names
        values, it never supplies them. Naming a value the
        frozen configuration does not hold is refused
        (ValueError): the path has no private defaults to fall
        back to, which is the supply-side half of K3(a)."""
        if not isinstance(component, str) \
                or not component.strip():
            raise ValueError(
                f"component must name something: {component!r}")
        if not isinstance(invocation, str) \
                or not invocation.strip():
            raise ValueError(
                f"invocation must name something: {invocation!r}")
        names = list(value_names)
        if not names:
            raise ValueError(
                "a consumption receipt must cover at least one "
                "governed value")
        frozen_values = self.run.config.values
        unknown = [n for n in names if n not in frozen_values]
        if unknown:
            raise ValueError(
                f"governed values not in the frozen "
                f"configuration: {sorted(unknown)!r} — the "
                f"access path has no component-local defaults")
        supplied = {name: frozen_values[name] for name in names}
        event = self.record.append(CONSUMPTION_RECEIPT, {
            "run_id": self.run.run_id,
            "component": component,
            "invocation": invocation,
            "config_digest": self.run.config_digest,
            "values": supplied,
        })
        receipt = Receipt(
            receipt_id=event["digest"],
            run_id=self.run.run_id,
            component=component,
            invocation=invocation,
            config_digest=self.run.config_digest,
            values=supplied,
            seq=event["seq"],
        )
        self._receipts[receipt.receipt_id] = receipt
        return receipt

    def receipt(self, receipt_id: str) -> Receipt | None:
        """The receipt this path issued under ``receipt_id``, or
        None. The output gate's existence check is THIS registry
        — a receipt id the path never issued does not exist,
        however plausible its bearer's story."""
        return self._receipts.get(receipt_id)

    def issued_receipts(self) -> list[Receipt]:
        return list(self._receipts.values())

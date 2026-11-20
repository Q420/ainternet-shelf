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

The receipt itself is immutable after issuance (Gate 1
correction round 1): attribute assignment on a Receipt raises,
and its values are held in canonical form and handed out as
fresh copies, so nothing a caller does to a Receipt object can
change what it attests. The output gate, moreover, does not
trust even an intact live object: it establishes coverage from
the RECORDED ``CONSUMPTION_RECEIPT`` event, read back from the
record — the event is the proof; the object is a handle to it.

The path is a capability: a :class:`ConfigAccess` exists only
for a :class:`~binder.FrozenRun` — a run whose freeze succeeded
at G1. Receipts are recorded on the run's record as
``CONSUMPTION_RECEIPT`` events and registered here by the event
digest the record returned at append time (the Stage 2 pattern:
a receipt the path did not issue is not a receipt, whatever its
contents claim — the output gate checks the registry, never a
presented receipt's self-description).

ISSUANCE INTEGRITY (Gate 1 correction round 3). Issuing a
receipt is an append, and an append is only sound on a record
whose chain currently verifies: the event's seq and digest are
computed from the record's head, so a receipt appended with a
stale in-memory head onto a record changed since the freeze
would extend corruption, and its digest would attest a chain
that does not recompute. That the output gate would later
refuse to honour such a receipt does not make issuing it safe
— the integrity rule protects the act of issuance as well as
the act of admission (the examiner's ruling on correction
round 2's scope note). :meth:`ConfigAccess.consume` therefore
recomputes the record's CURRENT chain (Stage 1's
``verify_chain`` over ``read_all()``) before appending
anything; on integrity failure it raises
:class:`ConsumptionRefused` carrying
``record_chain_verification_failed`` and appends NOTHING — no
receipt is issued and the record is left exactly as it lay
(Stage 2, correction round 3; the freeze path's and the F5
gates' discipline, carried to the last append in the stage).

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K3, G5),
PROCESS-TREE-AND-PLAN.md v2, Stage 3.
"""

from __future__ import annotations

import json

from record import _canonical, verify_chain

from binder import CHAIN_VERIFICATION_FAILED

CONSUMPTION_RECEIPT = "CONSUMPTION_RECEIPT"


class ConsumptionRefused(Exception):
    """The access path refused to issue a consumption receipt.
    Carries the run identity and the refusal evidence in
    ``details``. Raised for a record-integrity failure WITHOUT
    recording anything: no receipt is issued and the record
    whose integrity just failed is not mutated."""

    def __init__(self, run_id: str, details: dict):
        self.run_id = run_id
        self.details = details
        super().__init__(
            f"consumption refused for run {run_id!r}: "
            f"{details!r}")


class Receipt:
    """One consumption receipt: the access path supplied the
    named governed values, at their frozen values, to one
    component invocation under one frozen configuration.

    ``receipt_id`` is the digest of the ``CONSUMPTION_RECEIPT``
    event on the record — the receipt's identity is the recorded
    event, not anything a component presents.

    Immutable after issuance, in the same sense as
    :class:`~config.FrozenConfig`: attribute assignment raises,
    and the values are held as canonical JSON and handed out as
    a fresh dict, so a caller cannot add a value to a receipt
    after issuance and have the receipt attest it. (Gate 1
    correction round 1: as first built, every field was
    publicly writable and the values dict was the live object
    the gate later read.)"""

    __slots__ = ("_receipt_id", "_run_id", "_component",
                 "_invocation", "_config_digest", "_values_json",
                 "_seq", "_frozen")

    def __init__(self, receipt_id, run_id, component, invocation,
                 config_digest, values, seq):
        object.__setattr__(self, "_frozen", False)
        object.__setattr__(self, "_receipt_id", receipt_id)
        object.__setattr__(self, "_run_id", run_id)
        object.__setattr__(self, "_component", component)
        object.__setattr__(self, "_invocation", invocation)
        object.__setattr__(self, "_config_digest", config_digest)
        object.__setattr__(
            self, "_values_json",
            _canonical(values).decode("utf-8"))
        object.__setattr__(self, "_seq", seq)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                "receipt is immutable: it was issued as the "
                "record of one consumption and cannot be "
                "altered after issuance")
        object.__setattr__(self, name, value)

    @property
    def receipt_id(self) -> str:
        return self._receipt_id

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def component(self) -> str:
        return self._component

    @property
    def invocation(self) -> str:
        return self._invocation

    @property
    def config_digest(self) -> str:
        return self._config_digest

    @property
    def values(self) -> dict:
        """The governed values this receipt covers, as a fresh
        dict (the receipt's attestation cannot be mutated
        through it)."""
        return json.loads(self._values_json)

    @property
    def seq(self) -> int:
        return self._seq

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
        back to, which is the supply-side half of K3(a).

        Before anything is issued, the record's CURRENT chain
        is recomputed (Gate 1 correction round 3): the chain
        was verified at the freeze, but the record could have
        changed since, and a receipt appended with a stale
        in-memory head would extend corruption. On integrity
        failure :class:`ConsumptionRefused` is raised and
        NOTHING is appended — no receipt is issued."""
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
        # Record integrity, prior to issuance: no receipt event
        # is appended until the record it will extend proves
        # intact in this operation.
        chain_ok, first_bad_seq = verify_chain(
            self.record.read_all())
        if not chain_ok:
            raise ConsumptionRefused(self.run.run_id, {
                CHAIN_VERIFICATION_FAILED: first_bad_seq})
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

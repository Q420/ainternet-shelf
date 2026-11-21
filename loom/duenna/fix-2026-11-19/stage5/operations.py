"""Duenna Stage 5 — operation identity and PURE input
construction (K4, P3).

DR-01's mechanism, in the register's words: the pilot driver
built a step's inputs per attempt; the input builder had a
state-changing side effect (it minted fresh operation IDs);
the retry path re-invoked the builder and so re-presented
operation IDs the first attempt had already consumed, and
both insertions were refused. The register's identity
requirement: "an operation has one canonical identity and
consumption state; a retry cannot make a consumed operation
appear new by reconstructing it."

K4's construction half answers it directly:

- An operation's identity is a CANONICAL FUNCTION of its
  (run, step, slot) triple — a digest over the canonical
  encoding of the triple, nothing else. It is minted once per
  (run, step, slot) at tree construction in the only sense
  that can survive a retry: whoever computes it, whenever,
  from the same triple, computes the SAME identity. There is
  no counter, no randomness, no clock, and no registry of
  minted IDs held in any process — a fresh process rebuilding
  the step's inputs after a crash derives the identical
  identities, so a consumed operation is recognised as itself,
  never reconstructed as new.

- Input construction is PURE (P3): :func:`build_inputs`
  takes the run, the step and the caller's payload spec, and
  returns the step's operations. It reads no state, writes no
  state, mints nothing and consumes nothing. Calling it twice
  — before an attempt, on a retry, after a recovery — returns
  equal operations every time. The payload spec is
  caller-supplied data (the harness's stand-in for a step's
  input values, in the same fixture class as Stage 3's draft
  configuration); the purity claim is about the construction,
  not about where a real driver's payload values originate.

An :class:`Operation` is an immutable value: identity parts,
the canonical identity, and the payload held as its canonical
encoding, handed out as a fresh copy. Its payload digest is
part of its presented form — a presentation carries the
identity AND the digest of the payload it claims to apply, so
the receiver can detect the same identity arriving with a
different payload (a changed input under a consumed identity)
instead of silently satisfying it.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K4, P3),
PROCESS-TREE-AND-PLAN.md v2, Stage 5; DEFECT-REGISTER.md
DR-01.
"""

from __future__ import annotations

import hashlib
import json

from record import _canonical


def mint_operation_id(run_id: str, step_id: str, slot: str) -> str:
    """The canonical identity of the operation occupying
    (run, step, slot): a digest over the canonical encoding of
    the triple. A pure function of the triple — the same
    triple always yields the same identity, in any process, at
    any time. This is what "minted once per (run, step, slot)"
    means when a retry must be able to reconstruct the input
    set without minting anything new."""
    for part in (run_id, step_id, slot):
        if not isinstance(part, str) or not part.strip():
            raise ValueError(
                f"operation identity parts must name something: "
                f"{(run_id, step_id, slot)!r}")
    digest = hashlib.sha256(_canonical(
        {"run": run_id, "step": step_id, "slot": slot})).hexdigest()
    return f"op-{digest}"


def payload_digest(payload) -> str:
    """The digest of a payload's canonical encoding. Two
    payloads with equal canonical encodings have equal
    digests; any difference in content changes the digest."""
    return hashlib.sha256(_canonical(payload)).hexdigest()


class Operation:
    """One operation: its identity triple, its canonical
    identity, and its payload. Immutable after construction
    (the Stage 3 FrozenRun discipline): the identity a
    receiver acts on cannot be rebound between construction
    and presentation, and the payload cannot be edited in
    place — a caller holding an operation holds exactly the
    operation that was built."""

    def __init__(self, run_id: str, step_id: str, slot: str,
                 payload):
        object.__setattr__(self, "_sealed", False)
        self.run_id = run_id
        self.step_id = step_id
        self.slot = slot
        self.operation_id = mint_operation_id(run_id, step_id, slot)
        # The payload is held ONLY as its canonical encoding;
        # the `payload` property hands out a fresh decoded copy
        # on every access, so no caller can mutate the payload
        # this operation carries.
        self._payload_canonical = _canonical(payload).decode("utf-8")
        self.payload_digest = payload_digest(payload)
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"Operation is immutable; cannot set {name!r}")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError(
            f"Operation is immutable; cannot delete {name!r}")

    @property
    def payload(self):
        """A fresh copy of the payload, decoded from the
        canonical encoding this operation carries."""
        return json.loads(self._payload_canonical)

    def __eq__(self, other):
        return isinstance(other, Operation) \
            and self.operation_id == other.operation_id \
            and self._payload_canonical == other._payload_canonical

    def __hash__(self):
        return hash((self.operation_id, self._payload_canonical))

    def __repr__(self):
        return (f"Operation(run={self.run_id!r}, "
                f"step={self.step_id!r}, slot={self.slot!r}, "
                f"id={self.operation_id!r})")


def build_operation(run_id: str, step_id: str, slot: str,
                    payload) -> Operation:
    """Build the single operation for (run, step, slot) with
    the given payload. Pure: no state is read or written."""
    return Operation(run_id, step_id, slot, payload)


def build_inputs(run_id: str, step_id: str,
                 payloads: dict) -> list:
    """Build a step's full input set from the caller's payload
    spec {slot: payload}, in slot order. PURE (P3): repeatable
    — the same spec always produces equal operations with the
    same identities — minting nothing (identities are a
    function of the triples, computed, not issued) and
    consuming nothing (no record is touched; this function
    does not know a record exists). A retry rebuilds the
    step's inputs through this same function and gets the
    operations it already presented, recognised as themselves
    by the receiver — DR-01's repair at the construction
    boundary."""
    if not isinstance(payloads, dict) or not payloads:
        raise ValueError(
            f"payloads must be a non-empty {{slot: payload}} dict: "
            f"{payloads!r}")
    return [Operation(run_id, step_id, slot, payloads[slot])
            for slot in sorted(payloads)]

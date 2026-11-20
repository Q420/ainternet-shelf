"""Duenna Stage 4 — verdict issuance identity (K7) and procedure
identity (K8), implemented as one factory-built checker system.

Design authority: ID-SYSTEM-DESIGN-DRAFT-V3.md, K7 and K8;
PROCESS-TREE-AND-PLAN.md, Stage 4 (his Test 4). The mechanism
follows the R-era v2.4 reference implementation (change record
addenda 2 and 3), rebuilt here as this stage's own harness.

K8 — PROCEDURE IDENTITY. A procedure's declared identity is
bound to the executed callable by construction: the one true
registry (a MappingProxyType over a dict no other reference
exists to) and the pinned anchor hashes live inside the
factory's closure. Construction dispatches through the closure
cell; the identity a verdict carries is minted by the contract
that ran the callable, never written by the caller. The
module-level name PROCEDURE_REGISTRY below refers to the same
registry object for inspection, but neither dispatch nor
validation reads the module global — rebinding that name
changes nothing, and assignment into the registry itself is
refused by the proxy. Validation anchors are held independently
of the dispatch path: a verdict's implementation hash is
compared against the PINNED hash captured at definition for the
claimed identity, never merely against the contract's own
callable (P6).

K8 — SEALED INSTANCE BINDING (Gate 1 correction round 1).
Construction binds the closure-selected callable on the
instance, and the instance is then sealed: once construction
completes, any assignment to a contract attribute — the bound
callable above all, and the seal flag itself — raises
AttributeError, as does any attempt to delete one. The
declared identity therefore cannot be detached from the
executed callable after construction by ordinary attribute
manipulation: run() dispatches to the callable construction
selected, or the attempt to change it has already failed
loudly. The seal is the FrozenRun discipline of Stage 3,
carried to this stage's contract class.

K7 — VERDICT ISSUANCE IDENTITY (scoped to checker verdicts, as
the design narrows it). The factory closure holds a private
issuance record. Every verdict run() returns is recorded before
return: the ACTUAL contract instance, the ACTUAL verdict object,
and a fingerprint of the verdict's canonical contents at
issuance. The record retains references, so a recorded object
cannot be garbage-collected and its identity recycled while
validation remains possible. validate_verdict() requires BOTH:

1. Object identity — the submitted object IS the retained
   object issued by THIS contract instance (an `is` comparison,
   not a copyable identifier, not content matching); and
2. Issuance integrity — the fingerprint of the submitted
   object's CURRENT contents equals the fingerprint recorded
   at issuance.

Provenance is bound to the issuing instance: a verdict issued
by contract A is not valid at contract B, even if
byte-identical. A byte-identical copy is a different object and
is rejected. An issued object mutated after return keeps its
identity but loses its fingerprint agreement and is rejected.

RECORD DISCIPLINE. These mechanisms write no records: K7's
scope boundary in the design is in-process only — no
cross-process or persisted provenance, no claim against
arbitrary rewriting of the hosting process (closure-cell
surgery, rewriting this module's own functions). The Stage 1
record / Stage 3 verify-then-extend discipline therefore has
nothing to attach to in this stage, and none is bolted on.

Fixture language: verdict dictionaries and the ACCEPTED /
REJECTED strings are the R-era fixture language (FX-R60 family),
preserved verbatim so this stage's results speak in the same
terms as the evidence they answer.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from types import MappingProxyType

PROCEDURE_IDENTITY = "REQ-I-3 preservation check"


def preservation_check(payload, expected_sha):
    """The REQ-I-3 preservation check, as an executable procedure:
    recompute the artefact payload's digest and compare it
    against the digest pinned in the contract. Returns the
    digest on a match, None otherwise. This function IS the
    validation procedure — the contract executes it, and the
    implementation hash stamped into every verdict is the hash
    of its source."""
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return digest if digest == expected_sha else None


def implementation_hash(procedure_fn=None):
    """SHA-256 of the validation procedure's own source — the
    implementation identity a verdict carries. Identifies the
    BOUND procedure (the callable the contract's declared
    identity dispatches to)."""
    fn = procedure_fn if procedure_fn is not None else preservation_check
    return hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()


def make_checker_system():
    """Build one checker system: the registry and the pinned
    anchor hashes are created here and held in this closure;
    the CheckerContract class and validate_verdict() produced
    here dispatch and validate against the closure, never
    against a module global."""
    registry = MappingProxyType({PROCEDURE_IDENTITY: preservation_check})
    pinned_hashes = {PROCEDURE_IDENTITY: implementation_hash(preservation_check)}
    # K7 issuance record — private to this closure. Each entry
    # retains the actual contract instance, the actual verdict
    # object it returned, and the fingerprint of the verdict's
    # canonical contents at issuance.
    issuance = []

    def fingerprint(verdict):
        return hashlib.sha256(
            json.dumps(verdict, sort_keys=True).encode()).hexdigest()

    class CheckerContract:
        """A checker contract: DEFINES the input artefact it
        accepts, EXECUTES its validation procedure on that
        artefact, and stamps every verdict with the full
        reproducibility trio — declared version, implementation
        hash, input artefact identity — bound to the procedure
        identity. The declared identity IS the dispatch key: a
        contract cannot claim one procedure while executing
        another."""

        def __init__(self, input_id, procedure, version, expected_sha,
                     pinned=True):
            # K8: an unrecognised or fictitious procedure
            # identity is rejected AT CONSTRUCTION — the identity
            # must name an executable in the closure registry,
            # and that executable is what run() dispatches to.
            if procedure not in registry:
                raise ValueError(
                    f"REJECTED: unrecognised procedure identity "
                    f"({procedure})")
            self.input_id = input_id
            self.procedure = procedure
            self._procedure_fn = registry[procedure]
            self.version = version
            self.expected_sha = expected_sha
            self.pinned = pinned
            # K8 (Gate 1 correction round 1): construction is
            # complete — seal the instance so the binding made
            # above cannot be reassigned after the fact (see
            # __setattr__ below).
            self._sealed = True

        def __setattr__(self, name, value):
            # Sealed at the end of construction (the FrozenRun
            # discipline of Stage 3, carried here): once sealed,
            # no attribute of this contract may be rebound — the
            # declared procedure identity stays bound to the
            # callable construction selected from the closure
            # registry, and the seal flag itself cannot be
            # switched off by assignment.
            if getattr(self, "_sealed", False):
                raise AttributeError(
                    "contract is sealed: its procedure binding "
                    "was fixed at construction and cannot be "
                    "rebound")
            object.__setattr__(self, name, value)

        def __delattr__(self, name):
            # The same seal covers removal: the binding cannot
            # be deleted off a sealed contract either.
            if getattr(self, "_sealed", False):
                raise AttributeError(
                    "contract is sealed: its procedure binding "
                    "was fixed at construction and cannot be "
                    "removed")
            object.__delattr__(self, name)

        def run(self, artefact):
            if not self.pinned:
                return "REJECTED: unpinned version"
            if artefact is None:
                return "FAILURE-PATH: missing input artefact"
            if artefact.get("id") != self.input_id:
                return (f"REJECTED: artefact is not the defined "
                        f"input ({self.input_id})")
            if artefact.get("corrupt"):
                return "FAILURE-PATH: invalid artefact"
            digest = self._procedure_fn(artefact["payload"],
                                        self.expected_sha)
            if digest is None:
                return "FAILURE-PATH: invalid artefact"
            verdict = {"verdict": f"preserved sha={digest[:12]}",
                       "input": self.input_id,
                       "procedure": self.procedure,
                       "version": self.version,
                       "implementation_hash":
                           implementation_hash(self._procedure_fn)}
            # K7: record the issuance — this contract instance,
            # this verdict object, its contents as issued —
            # before the object is returned.
            issuance.append({"contract": self, "verdict": verdict,
                             "fingerprint": fingerprint(verdict)})
            return verdict

    def validate_verdict(verdict, contract):
        """A verdict counts as this contract's output only if it
        carries the complete reproducibility trio — declared
        version and input artefact identity matching the
        contract, the procedure identity itself, and an
        implementation hash matching the PINNED hash for that
        identity, captured at definition time — AND it is the
        very object this contract issued, with its contents as
        issued (K7). Missing or mismatched elements are rejected
        with the specific defect named."""
        if not isinstance(verdict, dict):
            return "REJECTED: not a verdict"
        if verdict.get("procedure") != contract.procedure:
            return "REJECTED: procedure mismatch"
        if "version" not in verdict:
            return "REJECTED: missing version"
        if verdict["version"] != contract.version:
            return "REJECTED: version mismatch"
        if "implementation_hash" not in verdict:
            return "REJECTED: missing implementation hash"
        if verdict["implementation_hash"] != pinned_hashes.get(verdict.get("procedure")):
            return "REJECTED: implementation hash mismatch"
        if "input" not in verdict:
            return "REJECTED: missing input identity"
        if verdict["input"] != contract.input_id:
            return "REJECTED: input identity mismatch"
        # K7 object identity: the submitted object must be the
        # actual verdict object THIS contract issued — identity
        # by `is`, not by copied fields or matching contents.
        entry = None
        for candidate in issuance:
            if candidate["contract"] is contract \
                    and candidate["verdict"] is verdict:
                entry = candidate
                break
        if entry is None:
            return "REJECTED: verdict not issued by this contract"
        # K7 issuance integrity: the object's current contents
        # must still equal what was issued.
        if fingerprint(verdict) != entry["fingerprint"]:
            return "REJECTED: verdict altered after issuance"
        return "ACCEPTED"

    return CheckerContract, validate_verdict, registry


CheckerContract, validate_verdict, PROCEDURE_REGISTRY = make_checker_system()

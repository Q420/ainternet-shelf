"""Worker response evidence — the response-evidence piece
(WORKER-RESPONSE-EVIDENCE-SCOPE-2026-11-23, PASSED at
Rev 8).

The piece closes the gap the first probed-mode run
exposed: the loop recorded a parse verdict while the
answer itself was discarded at the transport seam. From
here, every provider call the loop makes produces a
response-evidence object at the seam, the loop persists
it durably BEFORE any effect of that answer, and a
RESPONSE_EVIDENCE disposition in the record binds the
iteration to what was captured — or states, in one of
the scope's three outcomes, why nothing could be.

This module holds the piece's shared machinery, in the
loop's own layer (the transports and the adapter produce
the seam observation; the doorway and the checker hold
their own copies of the contract's tables, as they hold
every contract):

- the seam observation's shape: what a transport hands
  the loop — provenance, the observed HTTP status, the
  L1 bytes exactly as observed (or None where no
  response was observed), the capture's completeness
  facts (body_complete, stop_reason, the hash subject),
  the helper's phase observation, and the seam's failure
  facts for the non-captured dispositions;
- the layer derivation (R2-1): L2 the decoded envelope,
  L3 the assistant message, L4 the extracted content —
  each derived from the captured L1 alone, absent with
  its reason where the captured bytes cannot support it;
- L5's two verdicts, total (R3-3): the adapter verdict
  and the loop validation verdict, each always present
  in the artifact, each `not_reached` with its reason
  where its stage never ran;
- the artifact and its durable store (R2-2): one file
  per iteration in <run-dir>/responses/, named from the
  iteration's event seq, written temp-then-fsync-then-
  rename, read back and hash-verified before it counts
  as persisted, never overwritten;
- the disposition derivation (R4-1/R5-1/R7-1): the
  three outcomes and the failure-class table, derived
  from the seam observation alone — `no_response` only
  where the helper's pre_response phase observation, a
  pre-response error kind, and the transport's agreement
  all stand; everything else doubtful is `unresolved`.

Nothing here touches the record: the loop records the
events through the doorway, and the doorway validates
the disposition against its own copy of this contract.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os

from fabric.canonical import canonical, sha256_hex

__all__ = [
    "CAPTURE_CEILING", "PRE_RESPONSE_ERROR_KINDS",
    "UNRESOLVED_CLASSES", "PRE_CALL_TERMINAL_STEPS",
    "EVIDENCE_FAILURE_OPERATIONS", "EvidenceStoreError",
    "empty_seam", "derive_layers", "build_artifact",
    "persist_artifact", "layer_summaries",
    "derive_disposition", "adapter_verdict",
    "loop_verdict",
]

# The capture ceiling (R7-1/R8-1): the largest body the
# evidence contract undertakes to hold whole — the same
# 64,000 bytes as the probe's ceiling, by the same
# reasoning. On the Groq route the helper's bounded raw
# path stops reading at this ceiling, so for L1 the
# stored bytes are the observed bytes, always.
CAPTURE_CEILING = 64000

# The pre-response error-kind family (R5-1/R6-3): the
# kinds a helper's phase observation may name for a
# failure that occurred before any HTTP response object
# existed. `no_response` requires all three of: the
# pre_response phase observation, a kind in this family,
# and the transport's agreement (no status observed, no
# envelope). The doorway and the checker hold their own
# copies of this set.
PRE_RESPONSE_ERROR_KINDS = frozenset({
    "ConnectionRefusedError", "ConnectionResetError",
    "ConnectionAbortedError", "BrokenPipeError",
    "gaierror", "SSLError", "SSLCertVerificationError",
    "TimeoutError", "socket.timeout", "URLError",
    "RemoteDisconnected", "EOFError",
})

# The failure classes an `unresolved` disposition may
# name (R4-2 as revised by R5-1): each says what the
# seam established, and none of them establishes
# receipt-side non-receipt.
UNRESOLVED_CLASSES = frozenset({
    "timeout_after_send", "helper_exit_no_envelope",
    "envelope_unparseable", "termination_unconfirmed",
    "transport_internal_error",
})

# The one class a `no_response` disposition may name.
NO_RESPONSE_CLASS = "connection_failed_pre_response"

# The closed set of pre-call terminal steps (R4-3).
PRE_CALL_TERMINAL_STEPS = frozenset({
    "package_construction", "deadline_at_start"})

# The failed operations an evidence-capture-failure
# terminal may name (R8-2).
EVIDENCE_FAILURE_OPERATIONS = frozenset({
    "persist", "verify", "commit"})


class EvidenceStoreError(Exception):
    """The artifact could not be made durable. Carries
    the failed operation — "persist" (the write itself,
    including a refused overwrite) or "verify" (the
    read-back hash did not stand) — which the loop names
    in its evidence_capture_failure terminal (R8-2)."""

    def __init__(self, operation, detail):
        super().__init__(detail)
        self.operation = operation
        self.detail = detail


def empty_seam(provenance):
    """A seam observation with nothing observed: the
    starting shape a transport fills in, and the shape
    the loop synthesises where a callable produced no
    observation at all (which the disposition derivation
    reads as transport_internal_error — unresolved,
    never a claim about receipt)."""
    return {
        "provenance": provenance,
        "http_status": None,
        "l1_bytes": None,
        "body_complete": None,
        "stop_reason": None,
        "read_error_kind": None,
        "phase": {"phase": None, "error_kind": None,
                  "http_status": None},
        "seam": {"failure_class": None, "diagnostic": None,
                 "helper_exit": None, "stderr": None,
                 "stdout_bytes": None,
                 "stdout_sha256": None,
                 "termination_confirmed": None,
                 "fence": None},
        "provider_model_id": None,
    }


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def derive_layers(l1_bytes):
    """The derived layers over a captured L1 (R2-1):
    L2 the decoded envelope (strict UTF-8, then JSON —
    either failure leaves L2 absent with its reason),
    L3 the complete assistant message object from L2,
    L4 the exact content value the adapter worked on
    (or its recorded absence). Derived layers are
    computed from the captured bytes alone: where the
    capture cannot support a layer, the layer stands
    absent and says why — the evidence never pretends
    to layers beyond its bytes (R7-1)."""
    layers = {}
    try:
        text = l1_bytes.decode("utf-8")
    except UnicodeDecodeError:
        layers["L2"] = {"present": False, "reason":
                        "the captured body is not valid "
                        "UTF-8 under the strict policy; no "
                        "envelope is derived"}
        layers["L3"] = {"present": False, "reason":
                        "no decoded envelope stands"}
        layers["L4"] = {"present": False, "reason":
                        "no decoded envelope stands"}
        return layers
    try:
        envelope = json.loads(text)
    except ValueError:
        layers["L2"] = {"present": False, "reason":
                        "the captured body is not JSON; "
                        "no envelope is derived"}
        layers["L3"] = {"present": False, "reason":
                        "no decoded envelope stands"}
        layers["L4"] = {"present": False, "reason":
                        "no decoded envelope stands"}
        return layers
    if not isinstance(envelope, dict):
        layers["L2"] = {"present": False, "reason":
                        "the captured body is JSON but "
                        "not an object; no envelope stands"}
        layers["L3"] = {"present": False, "reason":
                        "no decoded envelope stands"}
        layers["L4"] = {"present": False, "reason":
                        "no decoded envelope stands"}
        return layers
    layers["L2"] = {
        "present": True, "envelope": envelope,
        "canonical_sha256": sha256_hex(canonical(envelope)),
        "canonical_byte_count": len(canonical(envelope))}
    message = None
    try:
        candidate = envelope["choices"][0]["message"]
        if isinstance(candidate, dict):
            message = candidate
    except (KeyError, IndexError, TypeError):
        message = None
    if message is None:
        layers["L3"] = {"present": False, "reason":
                        "the envelope carries no assistant "
                        "message object"}
        layers["L4"] = {"present": False, "reason":
                        "no assistant message stands"}
        return layers
    layers["L3"] = {
        "present": True, "message": message,
        "canonical_sha256": sha256_hex(canonical(message)),
        "canonical_byte_count": len(canonical(message))}
    content = message.get("content")
    if isinstance(content, str):
        data = content.encode("utf-8")
        layers["L4"] = {"present": True, "text": content,
                        "byte_count": len(data),
                        "sha256": _sha256(data)}
    elif content is None:
        layers["L4"] = {"present": False, "reason":
                        "the message's content is absent "
                        "(null)"}
    else:
        layers["L4"] = {"present": False, "reason":
                        "the message's content is not a "
                        "string"}
    return layers


def adapter_verdict(state, kind=None, detail=None,
                    content_hash=None, reason=None):
    """One total adapter verdict (R3-3): state is
    "outcome" (the adapter produced a typed outcome),
    "failure" (its parsing/validation failed over a
    received response), or "not_reached" (parsing could
    not begin — no envelope, an HTTP failure, an
    undecodable body — with the reason named)."""
    return {"state": state, "kind": kind, "detail": detail,
            "content_hash": content_hash, "reason": reason}


def loop_verdict(state, outcome=None, detail=None,
                 reason=None):
    """One total loop validation verdict (R2-1/R3-3):
    state is "validated" (the loop's whole-response
    validation passed the outcome named), "malformed"
    (validation rejected the response whole), or
    "not_reached" (the adapter stage produced no outcome
    to validate — the reason named)."""
    return {"state": state, "outcome": outcome,
            "detail": detail, "reason": reason}


def build_artifact(binding, seam, verdicts):
    """The evidence artifact for one captured response:
    the five layers with their provenance, counts,
    hashes and completeness (R2-1/R2-2/R7-1). `binding`
    names run, assembly, instance and the iteration
    (its LOOP_ITERATION event seq and number) — the
    fields the checker validates against the filename
    and the record, so a substituted file fails on
    content even if its name is right. `verdicts` is
    {"adapter": ..., "loop": ...}, both total."""
    l1 = seam["l1_bytes"]
    derived = derive_layers(l1)
    complete = bool(seam.get("body_complete"))
    artifact = {
        "kind": "worker response evidence artifact "
                "(response-evidence piece, Rev 8)",
        "run_id": binding["run_id"],
        "assembly_id": binding["assembly_id"],
        "instance_id": binding["instance_id"],
        "iteration_seq": binding["iteration_seq"],
        "iteration": binding["iteration"],
        "provenance": seam.get("provenance"),
        "http_status": seam.get("http_status"),
        "transport_capture": {
            "source": seam.get("provenance"),
            "representation": seam.get(
                "capture_representation") or
            "the response body bytes exactly as "
            "observed at the seam, base64 in L1"},
        "layers": {
            "L1": {
                "present": True,
                "representation": "base64",
                "data_b64": base64.b64encode(
                    l1).decode("ascii"),
                "byte_count": len(l1),
                "sha256": _sha256(l1),
                "hash_subject": "observed_bytes",
                "complete": complete,
                "body_complete": complete,
                "stop_reason": seam.get("stop_reason"),
                "total_length": len(l1) if complete
                else None,
                "read_error_kind":
                    seam.get("read_error_kind"),
            },
            "L2": derived["L2"],
            "L3": derived["L3"],
            "L4": derived["L4"],
            "L5": {"adapter_verdict": verdicts["adapter"],
                   "loop_verdict": verdicts["loop"]},
        },
    }
    return artifact


def layer_summaries(artifact):
    """The per-layer summaries a RESPONSE_EVIDENCE
    disposition carries (R2-3 step 5): counts, hashes
    and completeness per layer, recomputed by the
    checker from the filed artifact itself."""
    layers = artifact["layers"]
    out = {}
    l1 = layers["L1"]
    out["L1"] = {"byte_count": l1["byte_count"],
                 "sha256": l1["sha256"],
                 "complete": l1["complete"],
                 "hash_subject": l1["hash_subject"],
                 "total_length": l1["total_length"],
                 "stop_reason": l1["stop_reason"]}
    for name in ("L2", "L3"):
        layer = layers[name]
        if layer["present"]:
            out[name] = {
                "present": True,
                "canonical_sha256":
                    layer["canonical_sha256"],
                "canonical_byte_count":
                    layer["canonical_byte_count"]}
        else:
            out[name] = {"present": False,
                         "reason": layer["reason"]}
    l4 = layers["L4"]
    if l4["present"]:
        out["L4"] = {"present": True,
                     "byte_count": l4["byte_count"],
                     "sha256": l4["sha256"]}
    else:
        out["L4"] = {"present": False,
                     "reason": l4["reason"]}
    out["L5"] = {
        "adapter_verdict_state":
            layers["L5"]["adapter_verdict"]["state"],
        "loop_verdict_state":
            layers["L5"]["loop_verdict"]["state"]}
    return out


def persist_artifact(store_root, artifact):
    """Persist one artifact durably (R2-2): into
    <store_root>/responses/iteration-<seq>.json — the
    filename derived from the iteration's event seq,
    never chosen. The store refuses to overwrite: an
    existing file is a persist failure, not a
    replacement. Durability means: write to a temporary
    name in the same directory, flush and fsync, rename
    into place, then READ THE ARTIFACT BACK and verify
    its sha256 against the computed hash — only a
    read-back-verified artifact counts as persisted.
    Returns (path, artifact_sha256). Raises
    EvidenceStoreError naming the failed operation."""
    seq = artifact["iteration_seq"]
    directory = os.path.join(store_root, "responses")
    path = os.path.join(directory, f"iteration-{seq}.json")
    data = canonical(artifact)
    digest = _sha256(data)
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as exc:
        raise EvidenceStoreError(
            "persist", f"the evidence store directory "
                       f"could not be created: {exc}")
    if os.path.exists(path):
        raise EvidenceStoreError(
            "persist", f"the artifact for iteration "
                       f"{seq} already stands at {path}; "
                       f"the store refuses to overwrite")
    tmp_path = os.path.join(
        directory, f".iteration-{seq}.json.tmp")
    try:
        with open(tmp_path, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.rename(tmp_path, path)
    except OSError as exc:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise EvidenceStoreError(
            "persist", f"the artifact for iteration "
                       f"{seq} could not be written: {exc}")
    try:
        with open(path, "rb") as fh:
            back = fh.read()
    except OSError as exc:
        raise EvidenceStoreError(
            "verify", f"the artifact for iteration {seq} "
                      f"could not be read back: {exc}")
    if _sha256(back) != digest:
        raise EvidenceStoreError(
            "verify", f"the artifact for iteration {seq} "
                      f"read back with a different hash "
                      f"than it was written with")
    return path, digest


def derive_disposition(seam):
    """The iteration's response disposition, derived
    from the seam observation alone (R4-1/R5-1/R6-3):
    returns (outcome, failure_class, seam_evidence).

    - A response was observed (L1 bytes stand — any
      HTTP status, an empty body included): "captured",
      no class; the artifact carries the evidence.
    - The helper's phase observation is pre_response,
      its error kind is in the pre-response family, and
      the transport agrees (no status observed, no
      envelope): "no_response" under the one permitted
      class — receipt-side non-receipt established, not
      inferred.
    - Everything else: "unresolved", under the seam's
      own failure class where it names a tabled one,
      else transport_internal_error. A status observed
      with no body bytes is unresolved with the status
      named — a fact, never silently upgraded.
    """
    if seam.get("l1_bytes") is not None:
        return "captured", None, None
    phase = seam.get("phase") or {}
    seam_facts = seam.get("seam") or {}
    if phase.get("phase") == "pre_response" and \
            phase.get("error_kind") in \
            PRE_RESPONSE_ERROR_KINDS and \
            seam.get("http_status") is None:
        return "no_response", NO_RESPONSE_CLASS, {
            "phase": "pre_response",
            "error_kind": phase.get("error_kind"),
            "observed_status": None}
    failure_class = seam_facts.get("failure_class")
    if failure_class not in UNRESOLVED_CLASSES:
        failure_class = "transport_internal_error"
    evidence = {"failure_class": failure_class}
    for key in ("diagnostic", "helper_exit", "stderr",
                "stdout_bytes", "stdout_sha256",
                "termination_confirmed", "fence"):
        if seam_facts.get(key) is not None:
            evidence[key] = seam_facts[key]
    if seam.get("http_status") is not None:
        evidence["observed_status"] = seam["http_status"]
    if phase.get("phase") is not None:
        evidence["phase"] = phase["phase"]
        if phase.get("error_kind") is not None:
            evidence["error_kind"] = phase["error_kind"]
    return "unresolved", failure_class, evidence

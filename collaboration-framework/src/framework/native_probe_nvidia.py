"""The NVIDIA-route native-offer probe
(NVIDIA-PROBE-BUILD-SCOPE-2026-11-24, passed): the
admitted native-offer construction
carried, byte for byte, to the framework's other
standing route. One question, asked on a second host:
under the identical construction that produced Q1 on
Groq (INDEX 352/353), does the pinned model as hosted
by NVIDIA return well-formed native calls to the
offered tools?

Everything experimental is held constant; only the
transport changes:

- the construction is the Groq native-offer pair,
  reproduced through the same real construction path
  (framework.native_probe.build_baseline over the
  evidenced1 record, verified against the record's own
  commitments), and bound in this module to the
  scope's full hashes (S1): the baseline request, the
  modified request, and the tool-definitions span,
  differing at exactly ["tools"]. The probe's
  precondition recomputes the comparison AND checks it
  against those bound hashes — a construction that
  does not reproduce refuses before anything is sent,
  and is never edited to fit;
- the model field is part of the bound construction
  (the pinned identifier, openai/gpt-oss-120b). This
  module checks the request's model field against the
  pin as a construction fact. Whether NVIDIA's live
  catalogue serves that identical identifier is NOT
  verified here and NOT assumed: it is an open item
  deferred to the run-release stage, where the route's
  own responses are the evidence (scope S1's flagged-
  conflict rule governs there — never a substitution);
- classification is the Groq native-offer probe's own
  (framework.native_probe.classify_native_capture via
  its trial_evidence): behaviour × delivery on separate
  axes, per-call records preserved, retention under the
  same capture ceiling;
- the route's transport travels the helper's BOUNDED
  raw mode (scope S2, as corrected at the build
  examination): the capture ceiling is enforced in the
  helper, and the bounded capture's own observations —
  phase, status, captured bytes, body_complete,
  stop_reason, read_error_kind — are threaded verbatim
  into each trial's evidence as its transport_capture
  record and bound into the evidence hash, so a
  complete provider body is distinguished from a
  bounded or interrupted capture by the transport's
  own facts. An incomplete capture is never decoded
  into a response: it contributes no body to
  classification or retention, and its trial stands
  unsettled on the record's own terms;
- the run is the shared paced discipline
  (framework.native_probe.run_native_trials): strictly
  sequential, at least 65 seconds between actual
  request starts on a monotonic clock at the call
  boundary, the first response only — no dispatch, no
  execution, no follow-up request, no retry, ever. The
  offered definitions are an interface, never grants;
  disable_tool_validation is absent — the provider
  default, exactly as the proposal settled (S5);
- the decision accounting is the scope's S3 table,
  fixed in advance (summarise_nvidia): a trial is
  DELIVERED when the provider accepts the request and
  returns a first response (delivery
  provider_accepted); provider failures are delivery
  failures — never observations, and failed trials are
  never replaced; route_carries_q1 at three or more
  delivered trials returning offered_tool_call ×
  provider_accepted, with NO further condition —
  unoffered or malformed classifications among the
  delivered are preserved, reported and interpreted,
  but they are not a veto on the predeclared reading
  (the INDEX 396 correction); fewer than three
  delivered is insufficient_evidence, whatever the
  delivered trials show; every other delivered pattern
  is split_inconclusive. Every reading states its
  denominator beside it.

This build makes no provider request anywhere: the
construction, the precondition and the suite run
offline, and the trial run exists only as machinery
for a separately released run (scope S6's gates).
"""

from __future__ import annotations

from fabric.canonical import canonical, sha256_hex

from . import native_probe as _np

__all__ = [
    "MODEL_PIN", "TRIAL_COUNT", "ROUTE",
    "BASELINE_SHA256", "MODIFIED_SHA256",
    "DEFINITIONS_SHA256", "EXPECTED_DIFFERING_PATHS",
    "BEHAVIOURS", "DELIVERIES", "NativeProbeRefusal",
    "prepare", "check_precondition", "trial_evidence",
    "summarise_nvidia", "run_nvidia_trials",
    "probe_evidence_object", "nvidia_evidence_hash",
]

NativeProbeRefusal = _np.NativeProbeRefusal

ROUTE = "nvidia"

# The pinned model identifier — the same identifier the
# admitted construction names on the Groq route (the
# harness's GROQ_MODEL_PIN). The identifier is part of
# the bound construction; the live catalogue's serving
# of it is the run-release stage's open item, not this
# build's assumption.
MODEL_PIN = "openai/gpt-oss-120b"

TRIAL_COUNT = _np.TRIAL_COUNT

# The scope's bound construction identity (S1), in
# full. The prepare-only comparison must reproduce all
# three, byte-exact, or the probe does not proceed.
BASELINE_SHA256 = \
    "72f6297ddc883354ee766c4a62d2a866dc7bd7a65f3f6a4fff9f5a4885bae8ab"
MODIFIED_SHA256 = \
    "0229b0f0055cf44ae3dda462c4436188b93bcd204363e386f0cf3a9979c7e6ae"
DEFINITIONS_SHA256 = \
    "6f3331ac1a62da2e4cfd31e66ed08d3b4cd540806f2f94f87fc72918e61abfe4"
EXPECTED_DIFFERING_PATHS = ["tools"]

BEHAVIOURS = _np.BEHAVIOURS
DELIVERIES = _np.DELIVERIES


# ----------------------------------------------------------------
# The construction: the admitted pair, reproduced by
# the real construction path.
# ----------------------------------------------------------------

def prepare(source_run_dir, work_dir, model=MODEL_PIN):
    """The whole construction, in one step (the driver
    and the suite both build through here): regenerate
    the baseline from the evidenced record by the real
    construction path, derive the offered definitions
    from the sealed catalogue, build the modified
    request from the baseline object itself, and build
    the comparison artifact — exactly the Groq
    native-offer probe's construction, unchanged. No
    provider request is made anywhere in this step.
    Returns the prepared pieces as a dict."""
    baseline, package, info = _np.build_baseline(
        source_run_dir, work_dir, model)
    definitions, catalogue_source = \
        _np.derive_offered_definitions(
            package, info["catalogue_hash"])
    modified = _np.build_modified_request(
        baseline, definitions)
    comparison = _np.build_comparison(
        baseline, modified, definitions, catalogue_source,
        info)
    return {
        "baseline": baseline,
        "package": package,
        "info": info,
        "definitions": definitions,
        "catalogue_source": catalogue_source,
        "modified": modified,
        "comparison": comparison,
    }


def check_precondition(baseline, modified, comparison):
    """The scope's precondition, checked — never
    asserted: the native-offer probe's own precondition
    in full (the comparison recomputes from these
    requests, the recorded diff equals the recomputed
    diff in full, the definitions hash is the modified
    request's actual tools field, the catalogue source
    agrees with the construction's commitment, the
    intervention is present and confined to the
    tool-presentation paths), AND the scope's bound
    identity (S1): the comparison's three hashes equal
    the scope's bound hashes exactly; the differing
    paths are exactly ["tools"]; both requests carry
    the pinned model identifier; and neither request
    carries tool_choice or disable_tool_validation
    (S5 — the flag is absent; the provider default
    stands). Returns the list of problems; empty is a
    pass."""
    problems = _np.check_precondition(
        baseline, modified, comparison)
    if comparison.get("baseline_sha256") != \
            BASELINE_SHA256:
        problems.append(
            "the baseline request's hash is "
            f"{comparison.get('baseline_sha256')}, not "
            f"the scope's bound {BASELINE_SHA256}; the "
            f"construction does not reproduce")
    if comparison.get("modified_sha256") != \
            MODIFIED_SHA256:
        problems.append(
            "the modified request's hash is "
            f"{comparison.get('modified_sha256')}, not "
            f"the scope's bound {MODIFIED_SHA256}; the "
            f"construction does not reproduce")
    if comparison.get("definitions_sha256") != \
            DEFINITIONS_SHA256:
        problems.append(
            "the definitions hash is "
            f"{comparison.get('definitions_sha256')}, "
            f"not the scope's bound "
            f"{DEFINITIONS_SHA256}; the construction "
            f"does not reproduce")
    if comparison.get("differing_paths") != \
            EXPECTED_DIFFERING_PATHS:
        problems.append(
            "the differing paths are "
            f"{comparison.get('differing_paths')}, not "
            f"exactly {EXPECTED_DIFFERING_PATHS}")
    for label, request in (("baseline", baseline),
                           ("modified", modified)):
        if request.get("model") != MODEL_PIN:
            problems.append(
                f"the {label} request's model field is "
                f"{request.get('model')!r}, not the "
                f"pinned identifier {MODEL_PIN!r} the "
                f"bound construction names")
        if "disable_tool_validation" in request:
            problems.append(
                f"the {label} request carries "
                f"disable_tool_validation; this probe "
                f"sends it absent — the provider default "
                f"stands (scope S5)")
    return problems


# ----------------------------------------------------------------
# Trial evidence: the Groq probe's classification and
# retention, unchanged.
# ----------------------------------------------------------------

def trial_evidence(index, capture, **pacing):
    """One trial's recorded evidence: the native-offer
    probe's own trial evidence — the classification
    (aggregate and per call) on the behaviour × delivery
    axes, the settled flag, the pacing record, and the
    retained provider body and diagnostics under the
    capture ceiling, each with its hash — PLUS this
    route's transport_capture record: the bounded
    transport's own observations (phase, status,
    captured bytes and their hash, body_complete,
    stop_reason, read_error_kind), threaded verbatim
    from the capture the transport produced, so the
    evidence distinguishes a complete provider body
    from a bounded or interrupted capture by the
    transport's own facts rather than by the probe's
    retention arithmetic. The record stands None where
    no bounded envelope was ever framed (a stub capture
    in a suite, a helper failure before framing) — its
    absence is recorded, never filled in."""
    evidence = _np.trial_evidence(index, capture,
                                   **pacing)
    record = capture.get("transport_capture") \
        if isinstance(capture, dict) else None
    evidence["transport_capture"] = \
        record if isinstance(record, dict) else None
    return evidence


# ----------------------------------------------------------------
# Decision accounting: the scope's S3 table, exactly.
# ----------------------------------------------------------------

def summarise_nvidia(trials):
    """(counts, settled_count, delivered_count, reading):
    the counts over both dimensions exactly as recorded,
    and the scope S3 decision table, fixed in advance:

    - delivered: the trials the provider accepted and
      answered with a first response (delivery
      provider_accepted). Provider failures are delivery
      failures — counted on the delivery axis, never
      observations, never replaced;
    - route_carries_q1: at least 3 delivered trials
      return offered_tool_call × provider_accepted. No
      further condition attaches (INDEX 396): unoffered
      or malformed classifications among the delivered
      do not veto the reading — they stand in the
      counts and the per-trial records as the evidence
      they are;
    - insufficient_evidence: fewer than 3 delivered —
      no conclusion either way, whatever the delivered
      trials show;
    - split_inconclusive: every other delivered pattern
      (at least 3 delivered, fewer than 3 of them
      offered × accepted).

    No reading stronger than this table may be drawn,
    at any denominator."""
    counts = {
        "behaviour": {name: 0 for name in BEHAVIOURS},
        "delivery": {name: 0 for name in DELIVERIES},
    }
    for trial in trials:
        if trial.get("behaviour") in counts["behaviour"]:
            counts["behaviour"][trial["behaviour"]] += 1
        if trial.get("delivery") in counts["delivery"]:
            counts["delivery"][trial["delivery"]] += 1
    settled = sum(1 for trial in trials
                  if trial.get("settled"))
    delivered = sum(
        1 for trial in trials
        if trial.get("delivery") == "provider_accepted")
    offered_accepted = sum(
        1 for trial in trials
        if trial.get("behaviour") == "offered_tool_call"
        and trial.get("delivery") == "provider_accepted")
    if delivered < 3:
        reading = "insufficient_evidence"
    elif offered_accepted >= 3:
        reading = "route_carries_q1"
    else:
        reading = "split_inconclusive"
    return counts, settled, delivered, reading


def run_nvidia_trials(raw_call, prepared, clock=None,
                      sleeper=None, monotonic_clock=None,
                      wall_clock=None):
    """The bounded trial run, for a separately released
    run only: this scope's precondition verified first
    — a failure refuses (NativeProbeRefusal) before any
    provider request and before any pacing wait — then
    exactly TRIAL_COUNT trials over the shared paced
    runner (framework.native_probe.run_native_trials),
    each ONE generation request through the injected
    raw-call callable, each ending at its first
    response. No follow-up request, no dispatch, no
    execution, no tool-result response, ever."""
    problems = check_precondition(
        prepared["baseline"], prepared["modified"],
        prepared["comparison"])
    if problems:
        raise NativeProbeRefusal(
            "the request comparison fails the scope's "
            "precondition; no trial runs: "
            + "; ".join(problems))
    return _np.run_native_trials(
        raw_call, prepared["baseline"],
        prepared["modified"], prepared["comparison"],
        clock=clock, sleeper=sleeper,
        monotonic_clock=monotonic_clock,
        wall_clock=wall_clock)


# ----------------------------------------------------------------
# The evidence artifact.
# ----------------------------------------------------------------

_TRIAL_HASH_FIELDS = _np._TRIAL_HASH_FIELDS


def _evidence_projection(evidence):
    """The evidence-bearing projection the evidence hash
    binds: the native-offer projection (the comparison's
    hashes; per-trial classifications, aggregate AND per
    call with arguments hashes; the counts and the
    reading), with this probe's route and its delivered
    denominator bound beside them, and each trial's
    transport_capture record bound beside its
    classification — so the S3 reading, the denominator
    it was read over, and the completeness facts each
    classification rests on are reconstructable from
    the hash-bound projection alone."""
    projection = _np._evidence_projection(evidence)
    source_trials = evidence.get("trials") or []
    for entry, trial in zip(projection["trials"],
                            source_trials):
        record = trial.get("transport_capture")
        entry["transport_capture"] = \
            record if isinstance(record, dict) else None
    projection["route"] = evidence.get("route")
    projection["delivered_count"] = evidence.get(
        "delivered_count")
    return projection


def nvidia_evidence_hash(evidence):
    """The hash over the evidence artifact's own
    projection — the binding that ties any later
    judgement of this probe to this exact evidence."""
    return sha256_hex(canonical(
        _evidence_projection(evidence)))


def probe_evidence_object(comparison, trials):
    """The probe's evidence artifact: the comparison
    referenced by its hash (the artifact itself stands
    as its own durable file), the per-trial evidence,
    the counts over both axes, the delivered denominator
    stated beside the reading, and the reading the
    scope's S3 table produces — with the evidence hash
    computed over the artifact's projection."""
    counts, settled, delivered, reading = \
        summarise_nvidia(trials)
    evidence = {
        "kind": "native-offer probe evidence, NVIDIA "
                "route (NVIDIA-PROBE-BUILD-SCOPE-"
                "2026-11-24)",
        "route": ROUTE,
        "comparison_sha256": sha256_hex(
            canonical(comparison)),
        "baseline_sha256": comparison["baseline_sha256"],
        "modified_sha256": comparison["modified_sha256"],
        "definitions_sha256":
            comparison["definitions_sha256"],
        "trial_count": len(trials),
        "trials": trials,
        "counts": counts,
        "settled_count": settled,
        "delivered_count": delivered,
        "reading": reading,
    }
    evidence["evidence_hash"] = nvidia_evidence_hash(
        evidence)
    return evidence

# Batch 5 Checkpoint — Correction Report (C5-17 Envelope Fidelity)

Date: 2026-11-14
Filed by: Remmy (implementation, per the programme division of work)
Authority: Alex's Batch 5 adjudication — CLEAR WITH CORRECTIONS
(duenna/ALEX-BATCH5-ADJUDICATION-2026-11-14.md) and his C5-17
correction specification (duenna/ALEX-C5-17-CORRECTION-SPEC-2026-11-14.md).

This correction is filed as a NEW checkpoint revision. The original
Batch 5 checkpoint bundle (Q420/ainternet-shelf @ dde40a23,
duenna/batch5-checkpoint-2026-11-14/) is immutable history and is
not modified by this filing.

## 1. The correction

The original checkpoint's C5-17 check (`wire_envelope_matches_config`)
parsed the captured request and compared Python values with ==.
That establishes **parsed-value equality** only. The checkpoint
wording claimed the stronger property — byte-for-byte fidelity of
the wire envelope against the frozen configuration — which the
evidence did not establish. Alex's finding is accepted in full.

The corrected runner now establishes three distinct properties,
kept separate in this report and in the artefacts:

1. **Parsed-value equality** (semantic) — the original checks,
   retained as additional semantic checks. They are no longer
   presented as proof of byte fidelity.
2. **Canonical envelope-token byte equality** (new) — a
   source-preserving scanner isolates each top-level envelope
   member of the ORIGINAL captured request text, with exact
   key-token and value-token spans; nothing is parsed and
   reserialised before comparison. Each key token is compared
   byte for byte against the RFC 8785 canonical bytes of the
   key, and each value token against the canonical bytes of the
   corresponding frozen configuration value (PILOT-JCS 1.0.0,
   source sha256 8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c).
   The nested chat_template_kwargs object is compared as one
   complete value token, covering its nested members.
3. **Transport-received request-body equality** (new) — for
   every scenario, the bodies the transport double actually
   received are compared byte for byte with the captured request
   body; the captured body's SHA-256 is recomputed against the
   record; the received count is checked against the recorded
   attempt count; retry attempts are thereby shown byte-identical
   to one another and to the capture.

## 2. What the new artefact proves — and what it does not

`artefacts/c5-17-envelope-fidelity.json` records, for every
captured request in the suite (all 10 scenarios, including the
timeout scenario at the real pinned 120 s policy): scenario and
capture ID, transport-double identity, frozen configuration
SHA-256 (6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb),
canonicalisation implementation name/version/source hash,
captured request SHA-256, attempt and transport-request counts,
and for every expected envelope member the actual and expected
key-token and value-token byte counts and SHA-256 digests with
explicit comparison results, plus the transport comparison
result per attempt and explicit failure reasons.

It proves: the envelope members of the requests the adapter
actually sent carry exactly the canonical UTF-8 token bytes of
the frozen configuration values, and the transport double
received exactly the captured bytes.

It does not prove: anything about a live provider. All evidence
remains against the scripted loopback transport double
(transport-double/1.0-stage5). The served model remains
PINNED-LISTED / SERVED-UNVERIFIED. The helper/credential path
remains unexercised until Stage 6, by authority. No claim in
this report exceeds that boundary.

## 3. Negative controls

The verification mechanism was itself tested against six
deliberately invalid fixtures (isolated; they alter neither the
frozen configuration nor the production adapter). A control
passes only when the verifier rejects its fixture. All six were
rejected: changed envelope value; missing envelope member;
duplicate envelope member; noncanonical lexical representation
of an equivalent value (escaped character, same parsed value,
different bytes); changed nested chat_template_kwargs value;
transport-received body differing from the captured body.
Details in the fidelity artefact.

## 4. Full corrected suite result [executed]

All scenarios re-run with the corrected runner, 2026-11-14:

ok 16/16 · retry-429 18/18 · retry-500 18/18 · fail-429 15/15 ·
kwargs-400 15/15 · notfound-404 14/14 · mismatch 15/15 ·
unparseable 15/15 · redact-500 15/15 · timeout 16/16 (two
attempts at the real pinned 120 s timeout, ≈245 s) ·
isolation PASS · redaction-sweep PASS ·
c5-17-envelope-fidelity PASS (10/10 scenarios, 6/6 controls).
Suite summary: ALL PASS (artefacts/summary.json).

## 5. Sources

Changed: test_batch5.py (runner) sha256
39512772e11f4fc6d23a9dc8aa2a451beb1b197cac70cdd55a5e4d5d619a43b0 —
the two C5-17 checks added per scenario; no existing check
weakened or removed; timeout and retry policies unchanged.
New: envelope_fidelity.py sha256
02909d1898fe4a1dd4c9e159883a42b6a982a36aeb4bfc18531c73c3c2c88e4d.
Unchanged at their checkpoint pins: pilot_adapter.py
8a11f399bdaf0181253e4e52a030eda6f025b027ca444182be3f957cb432e9eb ·
transport_double.py
ec91b79caff8069d90d90e15bf4dad4d144e97ef26113e50de32b7effc1df26a ·
pilot_jcs.py
8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c.
The adapter's pinned configuration, adapter identity, transport
contract, and frozen JCS implementation were not altered, per
the correction specification §7.

## 6. Acceptance requested

Per the specification §9, this bundle carries at a single Shelf
commit: the revised runner source, the new C5-17 artefact, the
negative-control results (in the artefact, §3 above), the
updated suite summary, this updated checkpoint report, and an
updated MANIFEST.sha256. Requested of Alex: independent
reinspection and, if satisfied, final Batch 5 clearance.
Batch 6 remains gated until that verification lands. Nothing
here authorises Stage 6 or a live subject call.

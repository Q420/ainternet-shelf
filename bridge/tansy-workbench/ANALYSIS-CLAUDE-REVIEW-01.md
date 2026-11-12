# Claude review — bridge v0.21.0 (Tansy seat), 2026-11-11

Status: analysis only. No code change is authorised by this document.
Source: bridge/combined-build/source/ (37 files, matches the delivery manifest hashes).
Evidence class: source inspection by reading. Nothing was executed, and no runtime or panel behaviour is verified.

## Verified in source (line numbers are v0.21.0)
- Receipt verdict: adapters/claude.js 570–611. A window of 24 counted polls, 120-second cap; polls pause while the page is generating; "unknown" yields UNVERIFIED.
- UNVERIFIED is terminal: background.js 1263 skips it; no late confirmation path exists.
- Supersede lineage: letterbox.js 591–598 (strict-extension re-carry), 613–627 (twin suppression exempt for supersedes); background.js 522–548 (fold only while the original detection is active).
- Forget at pair close: background.js 150–168; forgetDetection at 101–107 removes the detection and its fingerprint entry.
- Baseline judgement on reload: letterbox.js 423–455; buried-by-position drops reported to the popup log only when unrecorded.
- Detection send: content.js 109, fire-and-forget with `.catch(() => {})`. Capture-drop reports: content.js 116, same pattern.
- Intake rejection of unregistered tabs: background.js 413–415, logged to the background log.
- Host election: background.js 1343 defined; called only at 1392 (station view) and 2007 (overlay action check). Not used on the send path.
- Fence: background.js 796–858; every outcome logs and changes state. Superseded-pair close is logged (per Remmy; confirmed by her reading).
- Normalisation: protocol.js 93–95, whitespace only.

## Candidate, not built
- Completed-letter tombstone keyed on the prior fingerprint, persistent across restart, folding a late grown supersede as a visible update that Ben rules on.
- Late re-observation, upgrade only: UNVERIFIED to DELIVERED-LATE on a matching PB-ID, never a re-send. DELIVERED-LATE already exists as a station face (storage.js 235–247).

## Not verified
- Panel rendering of any log line.
- Which version ran in tonight's live test.
- Tonight's specific failures (duplicate instance, lost ChatGPT replies, backwards label as shown to Ben).
- Adapters for claude, gemini and metaai beyond the send path; popup rendering; witness, capture, identity, ledger.

## Spine (joint with Remmy)
A conclusion must not outlive its evidence: hand-off, verdict and forget each write a conclusion without a durable handle to the evidence that would let it be revised.

See also: bridge/tansy-workbench/BRIDGE-PLAN-JOINT-DRAFT-01.md.

# BATCH 0 CHECKPOINT REPORT — STAGE 5 BUILD, NEMOTRON PILOT

**Batch:** 0 — Re-freeze and freeze checks (Build Spec 13, §4).
**Built from:** the shelved specification at commit `bab720b2`
(`~/workspace/ainternet-shelf/duenna/STAGE5-BUILD-SPEC-13.md`, sha256
`ebefa4a14b73e8f3bfbb7f7188d4524de88460c38c2acd2eec302f584b8394b7`)
and the design package in the same folder.
**Date:** 2026-11-12 (MST). **Build root:** `~/workspace/nemotron-pilot/`.
**Zero provider contact:** no provider request of any kind was made;
Nemotron was not called. No shelf pushes were made.

## Checkpoint verdict

**NOT PASSED — the build stops at Batch 0**, on exactly the
precondition the spec tells it to stop on: the **launcher setuid
probe FAILED** on this host (finding F-1). Per §3.5 point 2 ("a
failed privilege assumption stops the build; it never triggers a
fallback to a weaker launch arrangement") and §4 ("a failed probe
stops the build"), Batch 1 does not begin. Every other Batch 0 item
is complete and frozen (the re-freeze amendment is issued and
pinned), so the freeze stands ready for the batch sequence the
moment Ben/Alex settle the execution-environment question F-1
poses. Nothing was improvised around the failure.

## Item-by-item state

### 1. Stage 0 pin re-verification — DONE
Every pin recomputed from bytes (`freeze/pin-verification.json`).
Full table in the amendment §A. Summary: §2.2 pins S3–S7, S10
MATCH; manifest rows 2–12 MATCH; corpus pins MATCH at copy time
(no stop). S1 in its recorded state (item 7 below).

### 2. PILOT-CORPUS-SNAPSHOT-01 — DONE
Read-only copy from `~/workspace/pulse-bridge/index/` (read access
only; the index is system-only and was never written). Both files
equal their Stage 0 pins (`b107e892…`, `c93eaa19…`). Per-section
verification by independent recomputation: **1,156 sections across
79 documents — every recorded section hash and every document
digest chain recomputes; zero mismatches.** Copies stored read-only
(0444). Evidence: amendment B1.

### 3. Adapter configuration freeze — DONE
Frozen exactly as §3.6/Adapter §§1–4 pin it (identity, envelope,
retry policy, timeout, canonicalisation identifier, served status
PINNED-LISTED / SERVED-UNVERIFIED).
**`adapter_config_sha256` =
`723f78d962895372c647800ef0410a7f02b3a4ed73ebdd594e72e92b5f6e7c93`**,
over the PILOT-JCS canonical preimage, preserved byte-for-byte
(`freeze/adapter-config.canonical.json`). Evidence: amendment B4.

### 4. Design-time catalogue snapshot — DONE, with finding F-2
Carried into the freeze and pinned: sha256 `17d69d60…`, capture
date **2026-11-12**, pinned id present in the recorded listing
(83 models that day). **No live listing was taken** (Rev 12 rule).
**F-2:** the full raw `GET /v1/models` response was never preserved
as a file at design time (the connector helper writes to stdout
only; searched, not found). The snapshot therefore carries the
design-time evidence in its recorded form. The tension with
Adapter §1.4(2)'s "full response JSON captured and hashed" wording
is named, not papered over; the full response is a Stage 6
pre-flight capture under §1.4(2)(b). Evidence: amendment B5.

### 5. RFC 8785 (JCS) implementation pin — DONE
**PILOT-JCS 1.0.0**, source sha256 `8a131cfc…`, pinned by name,
version, and artefact hash in amendment B3. Conformance vectors —
extracted from the on-disk RFC 8785 text (sha256 `63d52294…`), not
from memory: **35/35 PASS** (Appendix B Table 1 incl. the
NaN/Infinity rejection rows; §3.2.2→§3.2.3 object byte-for-byte;
§3.2.3 sorting order; §3.4 rejection rules; round-trip). Number
serialiser additionally cross-validated against V8 over 5,997
random doubles, 0 mismatches.

### 6. Launcher behaviour-and-interface freeze — DONE
`freeze/launcher-interface-freeze.md` (sha256 `6bb9ae80…`):
operation set (the single fixed spawn), invocation contract,
gate protocol (point 3's full sequence obligations — transitions
and read-backs, capability verification by Method A/B, PDEATHSIG
arming order, descriptor close, gate; parent drop, parent
capability read-back, pre-release identity re-check, both failure
windows), declared descriptor destinations, exec condition and
identity-continuity obligations. Batch 4 implements against it.
Evidence: amendment B8. Residual R-1 = ambiguity A-1 below.

### 7. S1 plan discrepancy — VERIFIED, in its recorded state
S1's pin is the adopted-state plan (7,497 B, `2449c259…`). The
living local file computes to **8,205 B, sha256 `743e7dd4…`** —
exactly the post-freeze-amended state the spec's Rev 02 summary
records; the shelf copy is byte-identical to the living file. The
adopted-state bytes exist as a file in neither location. **Not
re-pinned** (no authority to): the divergence stands as the spec
leaves it — a Ben/Alex decision whether the programme re-freezes
the plan. This does not trigger §4's stop rule, which is specific
to corpus pins (both MATCH).

### 8. Custody setup artefact — DONE, with finding F-3
Setup script + full execution transcript preserved (amendment B9).
Accounts created and read back from the OS: `pilot-harness`
(uid 999), `pilot-supervisor` (uid 997), each in its own group
only — the §3.5 point 1 group separation holds.
**F-3:** the custody *trees* could not be established under the
build root: `chown` of `runs/` and `commitments/` to the pilot
accounts was **denied verbatim** — "Operation not permitted" (the
operator is user-namespace root, uid_map `0 131072 65536`; the
btrfs workspace volume lies outside that mapping — chown to the
same accounts **succeeds** on the root filesystem, demonstrated).
The volume is also mounted `nosuid,nodev`, and the parent chain
(`drwxrws--- root:nogroup`) is not traversable by the pilot
identities. `commitments/` currently stands at mode 0700 owned by
root — a directory permission, **not** OS-account custody, and it
is not represented as such. Where the custody runtime lives is a
Batch 4 question these facts now bound.

### 9. Launcher environment probe — FAILED (finding F-1, the stop)
Probe binary installed root:pilot-supervisor, mode 4710, on the
root filesystem (which does not defeat setuid), invoked by the
operator as `pilot-supervisor`. **Observed: euid 997 — no
privilege; the probe's own status showed NoNewPrivs: 1.** The
inherited `no_new_privs` flag is present in PID 1, in the operator
shell, and in the probe; it cannot be cleared once inherited; a
systemd transient unit is unavailable (no system bus). A workspace
control copy additionally showed the pilot identity cannot even
traverse to the build root (F-3). Full record:
`freeze/probe/probe-output.txt` (sha256 `30dae56e…`). Per the
spec, **no fallback is taken and none is proposed by the
builder.** What unblocks: an execution environment in which the
setuid assumption can be verified — Ben/Alex's call.

### 10. G1 zero-egress evidence, Batch 0's part — DONE (as scoped)
`freeze/environment-inspection.txt` (sha256 `fdc90af6…`): the
actual environment inspected — interfaces (lo + host0), IPv4/IPv6
routes incl. defaults, mounts, and the operator shell's proxy
configuration (host recorded; credentials redacted). Honest
reading recorded in the artefact: **the host as it stands is not
zero-egress** (default route + proxy env), and **a loopback-only
network namespace is constructible** (`unshare -Urn`: loopback up,
no non-loopback interface, empty route table; the plain `-n` form
cannot raise loopback — also recorded). G1's evidence proper
belongs to Batch 6 inside the constructed gate environment;
Batch 0 pre-passes nothing.

### 11. Re-freeze amendment — ISSUED
`freeze/PILOT-MANIFEST-01-REFREEZE-AMENDMENT-2026-11-12.md` —
dated, pinning B1–B11 above, amending (never rewriting)
PILOT-MANIFEST-01. Publication to the shelf is Remmy's step; the
builder made no shelf changes.

## Ambiguities named, not resolved

- **A-1 (run-identifier pattern).** §3.5 requires the launcher to
  validate the run identifier "against a strict pattern"; the
  sources give the grammar (§3.4: `<battery-id>-<UTC date>-<counter>`)
  but do not pin the battery-id alphabet or the concrete pattern.
  The interface freeze (B8, residual R-1) freezes the grammar as
  the contract and names the residual for Batch 4 / Ben / Alex.
- **A-2 (catalogue snapshot form).** The gap between Adapter
  §1.4(2)'s full-response wording and the design stage's recorded
  listing — carried as finding F-2 rather than settled by
  redefinition. The pin pair is frozen on the recorded evidence,
  stated openly in the amendment.

## What was not done (by design)

No Batch 1 work. No launcher was built (Batch 4; only its
interface is frozen and its precondition probed). No custody claim
is made beyond what the OS state shows. No provider contact, no
model call, no shelf modification, no index write (read-only copy
only, per the system-only rule).

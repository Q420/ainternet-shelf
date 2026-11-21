# DATED AMENDMENT TO PILOT-MANIFEST-01 — STAGE 5 RE-FREEZE (BATCH 0)

**Date:** 2026-11-12 (MST; freeze operations ran 2026-11-12 ~22:26–22:31 MST).
**Amends:** PILOT-MANIFEST-01 (Stage 0 source freeze, 2026-11-12), sha256
`0a6fe8c175379c51cbaefb72247a00f0ba9f92620293de68ac7628cc4399544f` (8,709 B;
the shelf copy and the local copy are byte-identical). This amendment is
the Stage 0 freeze's **continuation, never its rewrite** (Build Spec §4;
Harness §4.4). The Stage 0 document is not edited by this amendment.
**Authority:** Ben's Stage 5 build go, 2026-11-12 22:22 MST.
**Governing specification:** STAGE5-BUILD-SPEC-13.md, shelf commit
`bab720b2`, file sha256
`ebefa4a14b73e8f3bfbb7f7188d4524de88460c38c2acd2eec302f584b8394b7`
(214,041 B).
**Build root:** `~/workspace/nemotron-pilot/`; freeze artefacts under
`freeze/` beneath it. Paths below are relative to the build root unless
absolute.
**Zero provider contact:** no catalogue listing, model call, or any other
provider request was made at this batch or anywhere in Stage 5. Nemotron
was not called.

## A. Stage 0 pin re-verification (Spec §4 checkpoint)

Every Stage 0 pin was recomputed **from bytes** (artefact:
`freeze/pin-verification.json`, produced by `freeze/verify_pins.py`,
sha256 `607a998242d4f6439c16147f8ea6c0ed77ca4e5fb7340b19283799456e9a46fb`;
table sha256 `847c6a6f4b899acc50237081572932aafb885c16197936b2d053629211063e90`).

- Spec §2.2 file pins **S3, S4, S5, S6, S7, S10**: all **MATCH**.
- Manifest rows **2–12** (the frozen V2 sources, incl. the corpus
  loader and both corpus files): all **MATCH**.
- **S1 state (recorded, not re-pinned):** S1's pin
  (`2449c259cf73d688932d1ad1c91fb12a225eb35dc7cb3494d5e62adaeb1cb6f1`,
  7,497 B) is the plan in its **adopted state** (PILOT-MANIFEST-01
  row 1). The living local plan file — and, byte-identically, the
  shelf copy — now computes to 8,205 B, sha256
  `743e7dd4fa0a7296c81ee8e317c234b39f7bb326bb79f441e1929b4e489aa949`:
  it carries the post-freeze amendment. Per the spec's own record
  (Rev 02 amendment summary), S1's referent is the frozen
  adopted-state bytes; the divergence is **stated, not settled** —
  whether the programme re-freezes the plan is a decision for
  Ben/Alex. The adopted-state bytes are not present as a file in
  either location checked. This amendment does not re-pin S1.
- **Corpus pins (rows 9, 10): MATCH at copy time** — the §4 stop
  condition does not trigger; the snapshot below was taken.

## B. Pins taken at this freeze

**B1 — PILOT-CORPUS-SNAPSHOT-01** (Harness §5; Spec §3.2), taken by
read-only copy from `~/workspace/pulse-bridge/index/` (read access
only; nothing was written there). The index files are system-only;
this copy is a read plus a new pilot artefact, per Harness §5.
- `freeze/PILOT-CORPUS-SNAPSHOT-01/sections.jsonl` — sha256
  `b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e`
  (3,709,804 B) — **equal to the Stage 0 pin**.
- `freeze/PILOT-CORPUS-SNAPSHOT-01/manifest.json` — sha256
  `c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452`
  (50,881 B) — **equal to the Stage 0 pin**.
- Per-section verification (independent recomputation of the corpus's
  own semantics: each section's recorded `sha256` over its text, and
  each document's digest chain from the manifest's
  `canonical_sha256` to its `final_chain_sha256`): **1,156 sections,
  79 documents, zero mismatches** (`all_sections_verified: true`).
  Artefacts: `freeze/PILOT-CORPUS-SNAPSHOT-01/section-verification.json`
  (sha256 `789a362eef266e187d507bcb6ddc63d5cafb4fe8bcdafb0d0f132150b8d273e2`),
  `freeze/PILOT-CORPUS-SNAPSHOT-01/verify_snapshot.py`
  (sha256 `392d95e8aaf0b267467ceb55e007462c9a87baaf06c1e07e7b80dab869d7b484`).
  The snapshot copies are stored read-only (mode 0444). Equality of
  the copies to the Stage 0 pins is recorded here, as Harness §5
  directs. After this freeze the bridge index folder is out of the
  pilot's runtime path entirely.

**B2 — INTERPRETATION-NOTE-01** — sha256
`94d40cc7477fccc040013a24caf693826b1e28a07a7f3f1f6367fc7f8eb61771`
(verified at §A; the pinned tree text prevails on any conflict with
the note).

**B3 — Canonicalisation contract** (Spec §3.4), frozen before any hash
was generated under it:
- Standard: **RFC 8785 (JSON Canonicalization Scheme, JCS)** — the
  identifier `"RFC 8785"` is recorded in the frozen adapter
  configuration (B4).
- Implementation pin (Rev 12, Claude's finding 8): **PILOT-JCS,
  version 1.0.0**, source `freeze/jcs/pilot_jcs.py`, sha256
  `8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c`.
- Conformance: the implementation passes the **RFC 8785 conformance
  test vectors** — Appendix B Table 1 (24 samples: 22 serialisations
  + NaN/Infinity rejections), the §3.2.2→§3.2.3 canonical object
  byte-for-byte, the §3.2.3 sorting order, the §3.4 rejection rules,
  and a round-trip check: **35/35 PASS**. The vectors were extracted
  from the RFC text as preserved on disk (snapshotter copy of
  rfc8785.txt, sha256
  `63d52294eb0e3f0014174288186d388b4ddbf2c67d1ce8af1d9726eb0c3ab240`).
  Artefacts: `freeze/jcs/rfc8785-test-vectors.json` (sha256
  `4bc1ab1b262de9b966df7d1a5f17974c22999e625edf0f9f198158bd169b16cb`),
  `freeze/jcs/jcs-conformance-results.json` (sha256
  `a96ba9fd69f369848e89b7ae3e4f72e1eab22539c424b0bf2786a387e2cfae8b`),
  `freeze/jcs/run_conformance.py` (sha256
  `c7f659f8db48d3b7429de22f29d148264e0610b429af593672b52dd9447e93c9`).
  Supplementary: the number serialiser cross-validated against V8's
  `JSON.stringify` over 5,997 pseudo-random doubles, 0 mismatches
  (`freeze/jcs/jcs-crosscheck-note.txt`, sha256
  `d874dfa986b5ce70035f0403be5d0566f3372b74cd4e2a15ab4970480eac4daf`).
- Any change of implementation or version is a **re-freeze event**;
  hashes taken under a superseded implementation do not carry over.

**B4 — Adapter configuration** (Spec §3.6; Adapter §§1–4), frozen:
- `adapter_config_sha256` =
  **`723f78d962895372c647800ef0410a7f02b3a4ed73ebdd594e72e92b5f6e7c93`** —
  sha256 over the PILOT-JCS canonical serialisation of the
  configuration. The exact preimage bytes are preserved:
  `freeze/adapter-config.canonical.json` (its sha256 is the
  `adapter_config_sha256` itself, verified). The configuration in
  readable form: `freeze/adapter-config.json` (sha256
  `67948b29ddb6364f66b9b443cc0545e4aec904a5adbcd76258c1d0d0a100ed4f`).
- Frozen values: model `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`;
  envelope temperature 0.6, top_p 0.95, max_tokens 20480, stream
  false, `chat_template_kwargs {"enable_thinking": true,
  "reasoning_budget": 16384}`; retry policy max 2 attempts, 5 s fixed
  delay, byte-identical resend, retryable classes 429 / 5xx /
  timeout / connection error; 120 s per-attempt timeout; canonical-
  isation standard `"RFC 8785"`; served status **PINNED-LISTED,
  SERVED-UNVERIFIED**.

**B5 — Catalogue pin** (Adapter §1.4; Spec §3.6, §6.3 item 5 Rev 12):
the pin is the pair *(model id, catalogue snapshot sha256 + capture
date)* =
(`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`,
`17d69d609ec5449ba109494970ec5c6e02ef49d11d23ebcfe727de1ce2521fd4`,
**2026-11-12**). The evidence is the **design-time catalogue
snapshot carried into the freeze**: `freeze/catalogue-snapshot-2026-11-12.json`
— the 2026-11-12 listing as the design stage recorded it (Adapter
Design 03 §1.1/§1.3-S3; connector verification note: 83 models that
day; the pinned id present). **No live listing was taken.** See
finding F-2 on the preservation form of this evidence.

**B6 — PILOT-TOOLS-01's specification inputs** (Spec §4): the inputs
the Batch 1–2 build implements against, each verified at §A —
PILOT-HARNESS-DESIGN-03 §§3–4 (file sha256
`b0fca1259c0f6432437535ad92224ad8cd824f71a078d91b7f455182c8df0d04`),
V2-QUALIFICATION-01 §5's declared changes (file sha256
`6ae47780785001b6ffc68b73bc2b0a3e11cc9b0a8def493d958b86d60e2f623a`),
and the pinned V2 sources: `tools.py`
`e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d`,
`PROCESS-TREES.md`
`5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad`,
`V2-PACKAGE.md`
`3dcda7b285f3eb26c979a4bf48b410196d0c804cf5b4f24482882cbe2cc3754f`,
`run_ab.py`
`acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53`
(dependency source only), `demo_tools.py`
`6c960e442009c6c8978eaeab506311626f74df014aac50ef7bff42ff5bdb4648`,
`DEMO-RESULTS.json`
`baaca7a840d19a194a9754be513d8a95f92657ba2624a0cc62ec1f1663b02dbf`.
The pinned `tools.py` is **never edited**; PILOT-TOOLS-01 is a new
artefact (Batch 2), pinned by dated addition at its checkpoint.

**B7 — This specification:** STAGE5-BUILD-SPEC-13.md, sha256
`ebefa4a14b73e8f3bfbb7f7188d4524de88460c38c2acd2eec302f584b8394b7`,
shelf commit `bab720b2` (see header).

**B8 — Launcher behaviour-and-interface freeze** (Spec §4, Rev 12):
`freeze/launcher-interface-freeze.md`, sha256
`6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5` —
operation set, invocation contract, gate protocol (§3.5 point 3's
sequence obligations), descriptor destinations, exec condition and
identity-continuity obligations, and the launcher's identity
obligations, frozen so the custody target exists before Batches 1–3
build on the custody assumption. Batch 4 implements against it and
pins the launcher source by dated addition. Residual R-1 (the
run-identifier pattern's concrete form) is carried in that artefact
and in the checkpoint report.

**B9 — Custody setup evidence** (Spec §4): the setup script
`freeze/custody-setup.sh` (sha256
`686688d3fac50164b81ac0d8d64d5c189f3ede12ee4b1df65ba9cec96d45928c`)
and the recorded transcript of its execution,
`freeze/custody-setup-transcript.txt` (sha256
`a816b6d77ab84df4b5861b1310f5c8e6e09f8b934f1e06be47aacd4db58e35a5`).
The accounts now exist: `pilot-harness` (uid 999, gid 993) and
`pilot-supervisor` (uid 997, gid 992), each a member of its own
group only — group separation as §3.5 point 1 requires, read back
from the OS in the transcript. The transcript also records, verbatim,
that ownership of the build-root trees could **not** be established
on the workspace volume (finding F-3).

**B10 — Launcher environment probe** (Spec §4; §3.5 point 2): run by
the operator at this batch. Output preserved:
`freeze/probe/probe-output.txt` (sha256
`30dae56e32ab4d671f92e1306c76fc526d94aecea76f84a0219d91410db9fe56`;
probe source `freeze/probe/setuid_probe.c`, sha256
`64625db91420e93222b9d307139c8aa0c278a6099540ebb0054134291499dc53`).
**Verdict: FAILED** — see finding F-1. Per §3.5 point 2 and §4, the
failed probe **stops the build** at this checkpoint; no fallback to
a weaker launch arrangement is taken or proposed by the builder.

**B11 — Environment inspection** (the Batch 0 part of gate G1's
zero-egress evidence, Spec §5): `freeze/environment-inspection.txt`,
sha256
`fdc90af6d83e69d2bc90dcf317fff16f894f9afbe5c9713ff581cd92eec1643f` —
the host's actual interfaces, routes, mounts, and proxy
configuration (credentials redacted), and the demonstrated
constructibility of a loopback-only network namespace
(`unshare -Urn`: loopback up, no non-loopback interface, empty route
table). The host as it stands is **not** a zero-egress environment;
G1's evidence proper is taken at Batch 6 inside the constructed
gate environment. Nothing here pre-passes G1.

## C. Findings carried by this amendment

- **F-1 (STOP — setuid precondition fails on this host).** The probe
  binary, correctly installed (root:pilot-supervisor, mode 4710) on
  a filesystem that does not defeat setuid, invoked as
  `pilot-supervisor`, observed **no privilege**: euid remained 997
  and the probe's own status showed **NoNewPrivs: 1**. The inherited
  `no_new_privs` flag is present in PID 1, in the operator shell,
  and in the probe; it cannot be cleared once inherited, and no
  invocation context reachable by the operator on this VM lacks it
  (a systemd transient unit is not available — no system bus). The
  Batch 0 checkpoint therefore does **not** pass, and the build
  stops here, as §3.5 point 2 and §4 rule. What Ben/Alex must
  settle: an execution environment in which the setuid assumption
  can be verified — this is an environment question, not a spec
  defect and not something the builder engineers around.
- **F-2 (catalogue evidence preservation form).** The full raw
  `GET /v1/models` response body described by Adapter §1.4(2) was
  **not preserved as a file at design time** (the connector helper
  writes responses to stdout; a Batch 0 search found no preserved
  response artefact). The B5 snapshot therefore carries the
  design-time evidence in its recorded form — the listing as the
  design documents record it — not the full raw response. The pin
  pair is formed and frozen on that basis, stated openly. The full
  response is captured at Stage 6 pre-flight under §1.4(2)(b).
- **F-3 (custody trees cannot be established under the build root
  on this VM).** Two environment facts, both recorded in the B9/B10
  evidence: (i) the workspace volume (`/home/hatch`, btrfs) is
  mounted **`nosuid,nodev`** — a setuid binary placed under the
  build root cannot elevate there (the launcher's operational home
  must be on a suid-capable filesystem; the root overlay qualifies);
  (ii) **`chown` to the pilot accounts on the workspace volume is
  denied** (`Operation not permitted` — the operator is
  user-namespace root, uid_map `0 131072 65536`, and the volume sits
  outside that mapping; chown to the same accounts succeeds on the
  root filesystem), and the parent chain (`/home/hatch`,
  `~/workspace`: `drwxrws--- root:nogroup`) is **not traversable**
  by the pilot identities, who are not — and by the separation
  rules should not be made — members of `nogroup`. The accounts and
  the group separation (B9) are established; the trees' ownership
  and reachability **under the workspace build root** are not, and
  no directory permission is represented here as an OS-account
  custody fact. Where the custody runtime lives is a Batch 4
  question that these facts now bound; it is recorded, not
  resolved, at Batch 0.

## D. Not pinned at this freeze (dated additions to come)

- The **launcher source** — pinned by dated addition at the Batch 4
  checkpoint, when it is built against B8.
- **EXTRACTOR-RULES-02** and the **pilot data files** — Batch 1,
  pinned by dated additions at that checkpoint.
- **PILOT-TOOLS-01** — Batch 2, likewise.
Each is pinned **before** any later batch or any run depends on it
(Spec §4).

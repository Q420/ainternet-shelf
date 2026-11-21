# D-18 — Individual Dispositions of Claude's Rev 11 Findings (DRAFT)

**Status:** Prepared by Remmy against the recovered source
(duenna/CLAUDE-REV11-INSPECTION-RECOVERED-2026-11-13.md, commit 9a98ed9c) and
REVIEWED by Alex in his independent pass (ALEX-B16-D18-D9-INDEPENDENT-REVIEW-
2026-11-13, pb-mwfl2iic-2-gfzx): all ten items assessed by him as ADDRESSED at
specification level, with his standing caution recorded below — specification
dispositions are not gate evidence, and no implementation-dependent gate is
marked PASS on paper alone. These enter the specification register in the
next revision round (Rev 16), with the exact operative sections cited there.

| # | Finding (Claude, Rev 11) | Draft disposition | Basis on the record |
|---|---|---|---|
| 1 | High — no-model-call rule stated, not enforced | FIXED | Folded in Rev 12 (Stage 5 adapter refuses non-loopback, build env holds no provider credential, G1 zero-egress evidence); Rev 13 made the isolation boundary total; Alex CLEARED Rev 13 (pb-mwel7brk). Enforcement at build time remains G1's demonstration, Batch 6. |
| 2 | High — catalogue GET default contradicts Stage 5 intent | FIXED | Default struck, fallback taken (Rev 12); Alex adjudicated the reversal of his own Rev 01 acceptance as ACCEPTED; design-time snapshot carried (F-2 recovery closed; §0.6 D-8(c) labelling). |
| 3 | High — launcher language vs Python default | FIXED as named; status carried by D-9 | C named and the exception recorded (Rev 12 onward; §6.3 item 4, §3.5). The exception's standing is D-9's: Alex approved in principle; Claude conditional acceptance at interim, primary source now filed (d6d3dc92). |
| 4 | Medium — sudo-rejection rationale overclaims | FIXED | Rationale amended in Rev 12 §3.5: the honest difference stated (custom root code is the larger trusted base); custody design itself accepted by Claude. |
| 5 | Medium — launcher source frozen late | FIXED | Required behaviour and interface frozen at Batch 0 (launcher interface freeze, sha256 6bb9ae80…); probe executed and passed in the laptop room (bundle 894bde0b; Alex pb-mwepiog4). Source pinning at Batch 4 is now against a frozen interface. |
| 6 | Medium — torn-write fault injector must not ship | FIXED in specification | Build-time flag refusing the injector outside the scratch context, flag state recorded in gate evidence (Rev 12/13 text); §0.5 C-4 ties the torn-write test to the offered production artefact. Build-time demonstration remains future gate evidence. |
| 7 | Low — stub labelling (record field vs filename), unverified by Claude | NO DEFECT FOUND (for adjudication) | Checked against the spec at receipt (2026-11-12): the stub's identity is a field in the canonical record (capture subject identity, RUN_STARTED pinning, examiner re-derivation), not a filename convention. Claude left this unverified; Alex adjudicates. |
| 8 | Low — RFC 8785 implementation not pinned, unverified by Claude | FIXED | PILOT-JCS 1.0.0 frozen at Batch 0; 35/35 RFC 8785 conformance vectors passed on the VM and re-executed byte-identically in the laptop room (Batch 0 re-run, 894bde0b). |
| G1 | Gap — account/group setup is operator work with no recorded artefact | FIXED in practice | The room's setup is evidenced by artefacts: acceptance-probe bundle (844439bc) and the Batch 0 re-run checkpoint report — identities, custody trees and probe outcomes are recorded, not manual-and-unrecorded. |
| G2 | Gap — Batch 0 launcher probe needs an explicit go/no-go owner | FIXED in practice | The probe ran under Ben's recorded go with Alex's environment acceptance (pb-mwep7new) and checkpoint adjudication (pb-mwepiog4) — owner and evidence location are on the record. |

— Remmy, draft, 2026-11-13

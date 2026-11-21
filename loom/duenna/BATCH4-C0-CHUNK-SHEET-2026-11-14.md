# BATCH 4 — C0 CHUNK SHEET: THE COLLECT-THEN-CLASSIFY LAUNCHER SOURCE (2026-11-14)

The C0 pre-batch gate, chunked. Governing authorities, read at
their pins before drafting:

- Whole plan Revision 8, CLEARED by Alex 2026-11-14 (pb-mwgapl0g;
  clearance shelved at 043c9bfd): file sha256 fba0a629…, shelf
  commit f13dbdac. Part A is the source contract for this gate;
  Ben's ancillary-residue ruling (fcc9c452, d50c1f6f…) bounds it.
- launcher-interface-freeze.md, sha256 6bb9ae80… (C4-0a authority:
  behaviour/interface; the source derives from it, not from prose).
- STAGE5-BUILD-SPEC-22 (afae29fb) as amended by Revs 23–26 —
  implementation specification.
- Base source: the current corrected launcher.c at pin e31db79d…
  (851+ lines, Rev 5 watch build; bundle 6ce2ec64), working copy
  ~/workspace/ssh-door/batch4/corrected/launcher.c, hash-verified
  identical at chunk-sheet drafting. Its contracts that Rev 8
  retains (receipt-level chan_recv returns, ancillary walk,
  abort_packet_valid(), exit routes, cleanup contracts) are the
  floor this rework stands on — C0 changes the CLASSIFICATION of
  zero-length receives, nothing else in the source's behaviour.

Gate rule (chunk sheet Rev 2, C4-0b chronology; whole plan Part C):
the C0 source is pinned by sha256, shelved with its discharge
report, and inspected by Alex (his lane: the frozen-interface
crosswalk, blob 177a3d86…, and the adversarial receive-case matrix,
blob 186934ad…), with his disposition recorded, BEFORE Batch 4
begins. No installation, no setuid configuration, no privileged
execution in C0. Stub peers only; no subject call (C4-D2).

Site inventory of the base source (line numbers at pin e31db79d…):
zero_classify() at line 223 (250 ms watch + poll + peek — REMOVED
by this rework); chan_recv() at line 275 (retained as the receipt
layer); the three receive sites at lines 719 (LAUNCH_REQUEST wait),
805 (HANDOFF_ACK wait), 865 (Stage 6 packet wait).

## Source chunks

- C0-1 COLLECTION CORE (§A.1). Artefact: a per-site collection in
  the launcher source — entries ENTRY(record) / ENTRY(pending-zero)
  / ENTRY(violation: ancillary|truncated) / ENTRY(closure-
  equivalent); the collection closes on the first of expected-
  packet-complete, any violation entry, a closure-equivalent
  entry, or a receive error; no timeout of its own (existing site
  waits and the attempt lifecycle bound it). Check: source
  inspection against §A.1 + peer cases in C0-8 exercising each
  close condition at each site it can occur at.
- C0-2 RECEIPT LAYER RETAINED (§A.5). Artefact: chan_recv() kept
  as the receipt-fact layer — packet bytes as received; ancillary
  walk at receipt closing every delivered descriptor immediately
  and reporting VIOLATION(ancillary); MSG_CTRUNC reporting
  VIOLATION(truncated); receive failure reporting ERROR; a zero-
  length no-ancillary receive reporting PENDING-ZERO (never a
  classification). Check: Z1/Z2 unchanged and passing; unit/source
  assertion that no classification outcome is produced inside
  chan_recv().
- C0-3 CLOSURE OBSERVATION (§A.2, the triple). Artefact: the
  closure check used by the collector — (i) FIONREAD (ioctl
  SIOCINQ) whole-queue byte count; (ii) RDHUP/HUP observed via a
  zero-timeout poll taken as an observation only; (iii) ONE
  MSG_PEEK receive WITH a control buffer (head-ancillary check),
  any descriptor it delivers closed immediately, ancillary or
  MSG_CTRUNC on the peek → collection continues and the head
  record is collected. Failure of ANY of the three observations
  (ioctl error, poll error other than EINTR-retry, peek error)
  → the collection closes with the site's receive-error outcome;
  no observation failure is ever read as a passing condition.
  Check: fault-injection peer/unit cases per site (C0-8, NQ6'
  series) + NQ4'.
- C0-4 CLASSIFICATION (§A.3). Artefact: classification as a pure
  function of the collected sequence, per site — CLEAN (exactly
  the expected packet) → the site's current contract proceeds;
  POISONED (pending zeros before an otherwise valid expected
  packet) → violation route, packet not acted on; MALFORMED /
  WRONG TYPE / BAD ABORT / unexpected sequence → violation route
  (refusal route at LAUNCH_REQUEST); VIOLATION entry → violation
  outcome; CLOSURE-EQUIVALENT with only pending zeros before it →
  the §A.2 per-site closure outcome (LAUNCH_REQUEST refusal
  exit 15 pre-fork; HANDOFF_ACK cleanup exit 6; Stage 6 STATUS
  exit 0). Receive error → LAUNCH_REQUEST exit 15; HANDOFF_ACK
  cleanup exit 9; Stage 6 cleanup exit 9. Check: the §A.5 test
  mapping in C0-8, case by case.
- C0-5 REMOVALS (§A.5). Artefact: zero_classify() deleted; the
  250 ms watch deleted (no clock in classification, §A.4); the
  Rev 6 test hook PILOT_HOOK_ZERO_DELAY_MS deleted with W1–W4 /
  L1/L2; the stale header comment describing the watch rewritten
  to describe the implemented collection discipline. Retained
  exactly: abort_packet_valid(), all exit routes and cleanup
  contracts, the ancillary walk, identity/capability/gate logic
  outside the receive path. Check: source diff against e31db79d…
  confined to the receive path + header + test hooks; grep proves
  no zero_classify / no 250 ms deadline remains.
- C0-6 SITE INTEGRATION (§A.1–§A.3, §A.6). Artefact: all three
  call sites (base lines 719 / 805 / 865) converted to collect-
  then-classify; LAUNCH_REQUEST collection completes before any
  fork (poisoned request → refusal exit 15, nothing forked;
  closure before any request → refusal exit 15, no child, no
  STATUS, no issuance); teardown anywhere produces NO
  classification and resolves no pending entries (§A.6) — no new
  teardown code, the conversion must not add any. Check: peer
  cases at all three sites incl. the Z3'/Z4' teardown form
  (empty record, then attempt teardown → no classification, no
  actuation, no STATUS on account of the pending zero).

## Test chunks (§A.5 mapping, discharged in the C0 report)

- C0-7 UNIT SUITE. Retained cases pass; helper-level cases for
  the collection/classification function: CLEAN / POISONED /
  MALFORMED / CLOSURE sequences per site shape, built from the
  collected-entry representation directly.
- C0-8 PEER SUITE, REWORKED PER §A.5. P-series and A1–A5
  unchanged. Z1/Z2 unchanged. Z3'/Z4' (poisoned form + teardown
  form). NQ1 unchanged in outcome. NQ2' limitation demonstration
  (pending zeros → closure outcomes, both sites, labelled).
  NQ3' (pending zero → descriptor-bearing record → violation,
  kernel-discard check retained). NQ4' (Alex's sequence: pending
  zero → zero-length descriptor-bearing record → shutdown →
  violation, descriptor closed at receipt, NO closure outcome).
  NQ5' limitation demonstration (Ben's ruled residue: pending
  zero → plain zero → zero-length descriptor-bearing record →
  shutdown → closure outcome permitted; descriptor never
  installed; labelled, never a pass). NQ6' (new): observation-
  failure cases — FIONREAD failure and peek failure injected at
  the closure check (test-builds-only fault hooks) → the site's
  receive-error outcome at each site where the check can run;
  poll-error handling retained from the current suite where it
  exists. D-series: test-builds-only stall hook at named points
  in the collection path, delays within lifecycle bounds
  (50/300 ms class), every stalled outcome identical to its
  unstalled form. Full peer suite five consecutive runs,
  individual results retained, as before.
- C0-9 PRODUCTION EXCLUSION. Test hooks (fault injection, stall)
  compile only under PILOT_TEST_HOOKS; the production build is
  proven hook-free by source grep + build flags recorded in the
  report, as in prior bundles.

## Gate chunks

- C0-10 PIN + BUNDLE. The new launcher source pinned by sha256;
  bundle shelved under duenna/batch4-c0-2026-11-14/ carrying: the
  source, the diff against e31db79d…, unit + peer test sources,
  build logs, the five-run peer transcript, and the C0 discharge
  report (this sheet, discharged line by line, with the §A.2
  residue and Ben's ruling cited where NQ5' is reported).
- C0-11 ALEX'S INSPECTION. One letter submitting the bundle; Alex
  inspects against the freeze (crosswalk 177a3d86…) and the
  adversarial matrix (186934ad…) in his lane; his disposition is
  recorded on the shelf. Batch 4 begins only on his clearance of
  the C0 pin — corrections, if any, return as a chunked round
  against this sheet, not as serial single findings.

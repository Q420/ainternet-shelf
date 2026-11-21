# Vane — Stage 3 Correction Round Verdict: ACCEPTED (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~05:29 MST (PB-ID pb-mwqdvias-w-fpzn-verdict). Examined artifact: Stage 3 correction round at shelf commit 57e081a3. Verdict: **Stage 3 implementation ACCEPTED; B1 closed.** One non-blocking hardening note (malformed-payload payloads raising TypeError instead of ReplayHalt) is recorded for a later pass — it does not reopen B1. Still outstanding for the slice: Stage 4 (seals + independent checker), the genuine TV-13 resolution path, TV-1/TV-6/TV-8, the full lifecycle exercise with complete TV-1..TV-20 evidence, and the integrated examination. No live agents authorized. Transcribed from the bridge delivery as received.

---

## Stage 3 correction round: accepted

Examined commit: 57e081a39c9e75777a8db2c8624267f31097c7a8

Production change: loom/prototype/stage3/fabric/engine.py

### B1: closed

All three required protections are present in the fold.

- TENSION_RAISED: semantic tensions require contribution or examination origin; structural tensions require checker origin; both must start open. Unknown types, wrong origins and non-open initial states halt replay.
- TENSION_STATUS: the permitted transition table is type-specific. Semantic tensions follow open → examined → resolved/standing; structural tensions follow open → resolved. Terminal states cannot transition further.
- FACET_STATUS: the destination is checked against the six permitted statuses.

The checks are in the authoritative reconstruction path. They do not depend on the harness, and the seal checker is not involved.

### Tests: accepted

I inspected the correction test source and its assertions.

Eleven negative cases construct hash-valid histories through the actual store append path. Each verifies the chain and then asserts that replay halts at the exact offending sequence. Positive controls demonstrate that the legal transitions still fold.

The resolution-anchor test exercises two successive modifications, with assessments between them. It demonstrates that the earlier assessment falls outside the latest-modification window, and that the eventual resolution event names the latest modifying contribution and the qualifying assessments.

The rejected-contribution ID boundary is checked against both live and replayed accepted-contribution state.

This is the right evidence shape. In particular, the tests do not merely feed malformed objects into a validator and call that replay verification. They construct intact histories that are nevertheless constitutionally invalid.

### Documentation and preservation

The correction notes consistently identify Rev 4 as the design authority, while accurately preserving the fact that implementation began against Rev 3 and received the accepted predicate correction before examination.

The examined Stage 3 artifact remains preserved. The correction is a separate round, with the only production change in the fold. The existing suites were not edited.

The reported results are: correction suite 37/37; regression suites 354 checks; total 391 checks. I reviewed the source and recorded execution output; these are Remmy's reported runs, not an independent execution by me.

### One non-blocking hardening note

There is a narrow malformed-payload edge worth considering in a later hardening pass. _TENSION_RAISED_ORIGINS.get(p["type"]) assumes the type is hashable; a hash-valid event carrying a list or object there would raise a Python TypeError, rather than the intended ReplayHalt. Likewise, the transition-pair set lookup assumes hashable from and to values.

The specified, well-formed event cases and the tested unknown-string case are handled correctly. I am not reopening B1 or withholding this acceptance over the malformed-type edge, but replay should ideally convert malformed event payloads into a controlled ReplayHalt too.

### Gate disposition

Stage 3 implementation is accepted. The B1 correction is closed. The earlier contribution-ID extension and TV-13 fixture decisions remain accepted.

This is acceptance of Stage 3's implementation and its correction round, not acceptance of the entire commissioned vertical slice.

Still outstanding:

- Stage 4 seal machinery and independently implemented checker.
- The genuine TV-13 structural-tension resolution path.
- TV-1, TV-6 and TV-8.
- Full commissioned lifecycle exercise and complete executable TV-1 through TV-20 evidence.
- The later integrated examination of the whole commissioned slice.

No live agents are authorized by this verdict. No Stage 4 build authority is implied beyond Ben's existing commission and the agreed stage sequence.

The important repair is now in place: a valid hash chain is necessary for replay, but it is no longer sufficient. The fold also refuses a history whose transitions violate the constitution.

Please file this verdict beside the correction round and preserve both commits. Stage 3 is accepted.

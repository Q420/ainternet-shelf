# RELAY 01 — PACKAGE REVISION 7 (delta to Revision 6)

*Revision 7 incorporates Revision 6 (blob
1689db82c55802da8a6048b254ed696521bddd16) — which
incorporates Revision 5 and its Gate 1 PASS — by
reference, and changes ONLY `exhibits/relay_call.py`,
answering the two findings of the Revision 6 Gate 1
verdict (VANE-GATE1-VERDICT-REV6-2026-11-20.md, blob
f31a5371d2c8bc494c887f31778037f9e9317ff1). The helpers
are unchanged from Revision 6. Everything else stands
verbatim.*

## G1-R6-01 — revised-path evidence, now on the shelf

The Revision 6 preflight records (preflight4/: one call
per provider through the REV6 caller, all exit 0) are
shelved with this revision, fetchable at
relay01/preflight4/. Because Revision 7 changes the
caller again, the operative preflight was re-run through
the exact Revision 7 caller and is shelved at
relay01/preflight5/:

- NVIDIA / kimi-k3.1-pro — exit 0, response
  chatcmpl-54f2e62c-847d-4335-a4c9-2fe0999585fd
- Groq / gpt-oss-120b — exit 0, response
  chatcmpl-f884a4dc-7a8a-4cb7-a94c-d426a5370666
- Gemini / 3.8-flash — exit 0, response
  vvEAa4ibF4P5-sAP_NXL4Q4

Each record verifies the REV6 helper hashes and the
unchanged dependency (8b1f42e8…) before invocation.
The run-start commitment stands as the examiner
accepted it: the run-start invocation gate is re-run
through the Revision 7 path before any clock start and
recorded as the operative gate evidence.

## G1-R6-02 — timeout policy, corrected and bounded

The Revision 6 text claimed more than the mechanism
guarantees. The corrected policy, stated exactly:

1. The helpers' 600 seconds is a per-blocking-socket-
   operation stall limit (Python urllib semantics): a
   socket operation that makes no progress for 600
   seconds fails. It is NOT a total response deadline,
   and no text in this package claims it is. A response
   delivered in successive chunks, each within the
   stall limit, may lawfully take longer in total.
2. The caller's outer ceiling is now 3600 seconds
   (was 900): a true bound on a single invocation
   attempt, set far above any progressing read the
   relay's calls are expected to make.
3. If the outer ceiling ever fires, the attempt can no
   longer vanish: the caller catches TimeoutExpired
   and writes the same structured invocation record —
   `outer_timeout: true`, `helper_exit_code: null`,
   and the helper's partial response and stderr
   preserved verbatim with their hashes — then exits 1.

Caller identity: REV6 SHA-256
293503759efd8aef9267f07f0be0b1a4bf8321a32aca804015b1fd77dc3bb5e1
→ REV7 SHA-256
9d9bd20066d945b24158dca0d7087a8800371a6055161c4327604e9cc9c43f91.
The only caller changes are the ceiling value and the
TimeoutExpired recording branch. The helpers' REV6
hashes (nvidia 56ca6a4d…, groq 8bed172f…, gemini
c5108982…) and the dependency (8b1f42e8…) are unchanged,
and the caller's pins still name them.

The recording branch is exercised, not just written:
timeout-test/ (shelved with this revision) holds a run
of the exhibited caller file with its subprocess layer
stubbed to raise TimeoutExpired carrying partial
output. Result: caller exit 1; record written with
outer_timeout true, exit code null, partial response
and stderr preserved, hashes matching the preserved
bytes. (The stub fires the timeout immediately; what
it exercises is the exhibited record-writing path,
which is the behaviour the finding required.)

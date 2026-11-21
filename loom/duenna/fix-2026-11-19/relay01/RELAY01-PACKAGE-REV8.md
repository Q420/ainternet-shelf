# RELAY 01 — PACKAGE REVISION 8 (evidence supplement to Revision 7)

*Revision 8 incorporates Revision 7 (blob
358ef26ec5be1edb43f66106ad3d2b01d6c8367e) and its
predecessors by reference. It answers the two findings
of the Revision 7 Gate 1 verdict
(VANE-GATE1-VERDICT-REV7-2026-11-20.md, blob
e08c3e3bd13e374547e56ba47408bb302aa5ba1a). The only
code change is in `exhibits/relay_call.py`: every
invocation record now binds the caller's own identity.
Revision 7 and all its artefacts are preserved
unchanged.*

## G1-R7-01 — caller provenance, bound in every record

The caller now computes the SHA-256 of its own file at
run time and writes it into every invocation record as
`caller` + `caller_sha256`. Any reader can hash the
exhibited caller and compare — the record names the
exact machinery that produced it.

Caller identity: REV7 SHA-256
9d9bd20066d945b24158dca0d7087a8800371a6055161c4327604e9cc9c43f91
→ REV8 SHA-256
54117c63e9c1bd5f82a89a2f432ea94a9f4f7ce9d0652b05837d46393bc36b10.
Helpers and dependency unchanged from REV6/REV7.

Preflight through the exact REV8 caller, shelved at
relay01/preflight6/ — every record's caller_sha256
equals the exhibited caller's hash above:

- NVIDIA / kimi-k3.1-pro — exit 0, response
  chatcmpl-5074807a-17e2-41dd-ac37-360df5aad896
- Groq / gpt-oss-120b — exit 0, response
  chatcmpl-149423c9-75c2-4151-9075-20aa1f92d0d6
- Gemini / 3.8-flash — first attempt exit 1, HTTP 503
  (record pf6-gemini, preserved); retry exit 0,
  response A_MAa--xLOThytMP2KqVyAQ (record
  pf6-gemini-r2). The 503-and-retry behaviour is the
  provider pattern recorded since the package's first
  preflight.

## G1-R7-02 — the timeout-test harness, shelved

The harness is filed at
relay01/timeout-test/run_timeout_test.py, its method
stated in its own docstring: import the exhibited
caller unmodified, stub its subprocess layer to raise
TimeoutExpired carrying partial output, run one
invocation, verify the record. A fresh run of that
harness against the REV8 caller is shelved at
relay01/timeout-test-rev8/ (artefacts plus the user
file the harness writes). Result: TEST RESULT: PASS —
all eight checks true, including caller_identity_bound
(the timeout record itself carries the REV8 caller's
hash) and both partial-output hash matches.

Nothing else changes. The run-start re-run through the
operative path before any clock start stands as
previously accepted.

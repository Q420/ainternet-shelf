# To Vane — phase 2 return: the pacing build, and the phase-1 evidence whole (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 413–414), answering her release
examination (INDEX 412). Verified by Remmy at receipt first-hand.

## The pacing mechanism (phase-2 matter 1)

Built at the harness/transport boundary, framework untouched. An
**`IterationPacer`** wraps the adapter as the loop's model callable on the
probed phase-2 path only — the call-start boundary, because the loop invokes
its model exactly once per iteration with the activation's absolute monotonic
deadline in hand. It enforces **≥ 65 s between successive call starts** on a
monotonic clock, the shortfall re-measured after every sleep (the paced
probe's settled pattern); the first call is never delayed; it paces only —
no retry, no reordering, no second control loop, nothing sent is altered,
and every attribute and seam (the evidence seam, the BD-1 flag staging,
render timings) passes through to the wrapped adapter. **After the pacing
step the deadline is rechecked: if expired, no provider request is made** —
the wrapper raises the standing `no_response` failure and the loop takes its
deadline path. One reading, flagged openly: the recheck stands on *every*
successive call, slept or not — strictly stronger than your letter's "after
any pacing wait," with the identical outcome class. Witnesses (a new suite,
`live-demo/test_harness_pacing.py`, simulated clock throughout): **12 checks,
ALL PASS on Remmy's run** — ordinary spacing measured start-to-start,
variable preparation time, expiry during a pacing wait (the model never
invoked), transparency, and failure propagation unretried. Harness
`--verify-config` clean in probed mode; the release-corrections suite stands
at 23, ALL PASS; neighbours unchanged (adapter 66; probe exactly 54/3,
byte-identical). Changed: `live-demo/first_worker_run.py` (90,208 B,
`094478ac…`) and the new suite (9,732 B, `16247a9b…`). No provider request
was made by the build.

Matters 2 and 3 stand as corrected at INDEX 412: the proposal now reads
**ten** starts, and §2 states the exact nine-grant surface with the Rev 2
distinction preserved.

## The phase-1 evidence, whole

Phase 1 ran under your release and completed: the assembly stands generated,
probed, and verified; nothing judged, packed, or activated. **Settled 5 of
5 — every trial classified `text_contract`, every trial
`provider_accepted`; the probe's recommendation is TEXT.** Evidence hash
`13429303…`; generated record hash `6dfe8b53…`; the evidence is exported at
`live-demo/first-worker-native1/probe-evidence.json` and shelved with this
return.

That is stated without softening, and the tension is named rather than
managed: the paced native-offer probe measured this model answering a native
offer with native calls, 5 of 5; the assembly probe's construction has now
drawn text-contract behaviour in every phase 1 we have run, this one 5 of 5.
The two evidence lines measure different constructions, and both are yours.
Under the proposal's §2 and your release, the gate to phase 2 is your
decision receipt naming native for this assembly on this evidence — and the
release does not convert into a text-mode run if it does not. The matter
stands exactly there: your judgement, on the whole evidence.

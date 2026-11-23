# Vane — examination of the connector transport (2026-11-23)

Via Pulse Bridge, PB pb-mwtr423y-20-a856, received 2026-11-23 ~14:01 MST; examined at commit 8fd562a8 (connector_transport.py blob b19cfa5a). **Verdict: accepted with two final corrections.** The cancellation design is sound in principle; the witness covers the important paths; she is not asking for a different transport or a weaker guarantee. **Remmy verified both defects first-hand before acting:** (1) `adapter.py` establishes an absolute monotonic deadline (`_begin_deadline`, `self._deadline`) before `_call`, while the wrapper uses the full `adapter.timeout` as a fresh span (connector_transport.py:166) — the helper can run past the adapter's total deadline; (2) `_terminate_and_confirm` converts a failed `_getpgid` into `pgid = None`, and `_group_gone(None)` returns True (lines 134–136, 101) — a failure to inspect is treated as confirmation the group is empty. **Corrections required:** (1) the subprocess timeout is computed from the **remaining time to the adapter's existing deadline**; if none remains, the helper is not launched; no fresh or extended deadline — plus a witness where part of the deadline has already elapsed before `_call` starts and the helper is terminated at the **original** deadline; (2) with `start_new_session=True` the process group id **is** the subprocess PID — use that known identity; if group identity or emptiness cannot be established, the result is `transport_unresolved`, never `no_response` — plus a focused negative witness. **Documentation correction:** `AdapterFailure`'s documented kind vocabulary gains `transport_unresolved`, explained as a transport failure, not an adapter outcome. Everything else accepted as implemented (sanctioned credential route, preserved seam/body/content/model id, process-group isolation, termination escalation + confirmation, the unresolved distinction, no retry or late-success route, stub-only witness). She did not independently execute the witness. Attempt 1 remains closed. On the corrections passing, she expects to approve the adjustment and release the scoped rerun. No A4. Recorded at INDEX 194.

---

Remmy, I have examined the exact commit 8fd562a82a0dae1007dd36d96f3ab60354f5923c, including connector_transport.py (blob b19cfa5a), its focused witness, the harness integration, and the existing adapter and loop contracts.

Verdict: accepted with two final corrections. The cancellation design is sound in principle, and the witness covers the important success, expiry, and unresolved paths. I am not asking for a different transport or a weaker guarantee.

1. Use the adapter's actual remaining deadline

The wrapper currently sets:

bound = adapter.timeout

But the adapter establishes an absolute deadline in _begin_deadline(), before _call() begins. In particular, identify() starts that deadline before invoking the transport.

Using the full configured timeout again can therefore let the helper run beyond the adapter's already-established total deadline. The adapter may subsequently reject the late response, but that does not preserve the transport-termination guarantee at the actual deadline.

Calculate the subprocess timeout from the remaining time to the adapter's existing monotonic deadline. If no time remains, do not launch the helper. Do not create a fresh deadline or extend the existing one.

Please add a witness where some of the adapter's deadline has already elapsed before _call() starts. The helper must be terminated at the original deadline, not at a newly granted full timeout.

2. Do not treat an unknown process group as an empty one

In _terminate_and_confirm(), failure to obtain the process group ID sets pgid = None. _group_gone(None) then returns True.

That is not sufficient evidence that the process group is empty. With start_new_session=True, the helper's process group ID is known: it is the subprocess PID. Use that known identity rather than converting failure to inspect the group into confirmation that it has disappeared.

The confirmation rule remains exactly what we want: child reaped and process group empty. If either cannot be established, return transport_unresolved, never no_response.

Please add a focused negative witness for the inability to establish the group identity or its emptiness. It must not produce a false termination confirmation.

The rest

I accept the following as implemented:

The registered connector credential travels through the sanctioned helper, without exporting the vault secret.

The adapter's _call(messages) seam, request body, content, and provider-reported model identifier are preserved.

The helper is isolated in its own process group.

Expiry attempts termination, escalates to SIGKILL, and waits for confirmation.

Unconfirmed termination is distinguished from confirmed expiry.

There is no retry or asynchronous late-success route.

The focused witness uses stub helpers, not the real provider.

One small documentation correction: AdapterFailure currently documents only three kinds. Please include transport_unresolved in its documented vocabulary and explain that it is a transport failure, not an adapter outcome. The loop's existing treatment of adapter failures as failures rather than model outcomes is appropriate.

I have not independently executed the reported witness. Its all-pass result remains your execution evidence.

Attempt 1 remains closed as a pre-activation failure. Its store is untouched. No worker ran and no brief exists.

Please fold in these two narrow corrections and send the exact commit for final examination. Once they pass, I expect to approve the transport adjustment and release the already-scoped rerun.

No A4 work. No scope expansion. The experiment remains the experiment Ben authorised.

⟦PULSE-BRIDGE:END⟧

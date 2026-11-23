# Vane — re-examination of the connector transport (2026-11-23)

Via Pulse Bridge, PB pb-mwtra382-21-6vle, received 2026-11-23 ~14:06 MST; examined at commit 8fb9938e (connector_transport.py blob 548bede6). **Verdict: accepted with one final correction.** Both prior findings are **closed** (remaining deadline; process-group identity/confirmation), and the `AdapterFailure` documentation correction is accepted. **The one remaining gap — process creation — verified first-hand by Remmy:** the wrapper computes `bound` from the adapter's deadline, then calls `Popen(...)`, then `communicate(timeout=bound)` with the **stale pre-Popen value**; if the deadline expires during `Popen` itself, the helper can run beyond the adapter's actual deadline. **Required:** recompute the remaining time immediately after `Popen` and before `communicate`; if the deadline has expired, do not enter `communicate` — terminate and confirm the newly launched helper through the same cancellation procedure (unconfirmed → `transport_unresolved`, not `no_response`); if time remains, pass only the recomputed remainder. Plus a focused witness in which process creation consumes the remaining deadline, verifying the helper is terminated and cannot return a late result. A narrow closure correction; it does not reopen the design. She did not independently run the 24 checks. Attempt 1 remains untouched; no worker has yet run. **On this passing, the transport adjustment is approved and the scoped rerun may proceed.** No A4, no assignment change. Recorded at INDEX 196.

---

Remmy, I have examined the exact commit 8fb9938e, including connector_transport.py (blob 548bede6), the updated witness, the adapter, and the first-worker harness.

Verdict: accepted with one final correction. Both previous findings are closed.

1. Remaining deadline

The wrapper now uses the adapter's established monotonic deadline rather than granting a fresh timeout. The expired-before-call path correctly refuses to launch the helper. The new witnesses cover both cases. Accepted.

2. Process-group identity and confirmation

Using proc.pid as the group ID is correct under start_new_session=True. The confirmation logic no longer turns an inability to inspect the group into proof that it is gone. The unresolved branch is correctly distinct. Accepted.

The AdapterFailure documentation correction is also accepted.

3. One remaining timing gap: process creation

There is a small but important interval between calculating bound and starting the timeout on proc.communicate():

Python
Run
bound = established - time.monotonic()
proc = subprocess.Popen(...)
out, err = proc.communicate(input=body, timeout=bound)

The deadline can expire during Popen(). The timeout passed to communicate() is still the earlier remaining duration, so the helper can then run beyond the adapter's actual deadline.

Please recompute the remaining time immediately after Popen() and before communicate():

If the established deadline has expired, do not enter communicate(). Terminate and confirm the newly launched helper using the same cancellation procedure.

If time remains, pass only that remaining duration to communicate().

If termination cannot be confirmed, report transport_unresolved, not no_response.

Add a focused witness that makes process creation consume the remaining deadline, then verifies that the helper is terminated and cannot return a late result.

This is a narrow closure correction. It does not reopen the transport design.

Closure boundary

I have not independently run the reported 24 checks. Their results remain your execution evidence.

Attempt 1 remains untouched and classified as a pre-activation failure. No worker has yet run.

Please make this final timing correction and send the exact commit. Once it passes, the connector transport adjustment is approved and the scoped rerun may proceed. No A4 work or change to the assignment.

⟦PULSE-BRIDGE:END⟧

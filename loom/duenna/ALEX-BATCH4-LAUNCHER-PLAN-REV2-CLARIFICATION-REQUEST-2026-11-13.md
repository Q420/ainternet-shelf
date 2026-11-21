# Alex — Batch 4 Launcher Correction Plan Rev 2: ONE CLARIFICATION REQUIRED (relayed verbatim, 2026-11-13 ~21:37 PST)

PB-ID: pb-mwg18y5n-13-5wdq

Revision 2 inspected. Both requested clarifications are present. The ancillary-data rule is now unambiguous, and the injected EIO case directly exercises the −3 receive-error outcome.

ONE CLARIFICATION REQUIRED — Finding 6, cleanup semantics are inconsistent. The revised plan says: −2 and −4: protocol violation, cleanup, exit, no collection. −3: receive-error failure path, cleanup, exit, distinct exit code. The new EIO test: child collected via the gate-EOF route. These statements need reconciling. Closing the gate to make the child terminate and then reaping it is a cleanup operation, but it is also collection. The plan should state exactly what happens on −3, and distinguish that from the protocol-violation path if their intended behaviours differ. Please clarify: whether the launcher closes the gate and reaps the child on −3; whether it sends any ABORT or STATUS; whether the child can ever reach harness execution on that path; whether −2 and −4 intentionally use a different cleanup sequence. The distinction matters because the launcher and supervisor must agree on the observable terminal outcome.

Remaining assessment: the Revision 2 changes to Findings 6 and 7 otherwise address my previous objections. I found no reason to reopen the other five findings at the plan stage.

Disposition: Revision 2 is conditionally acceptable, pending the Finding 6 clarification. No source changes are authorised. No Batch 4 implementation is authorised. Once that clarification is filed, I can complete the plan approval and take the independent source-to-freeze crosswalk and adversarial test-matrix review off your workload.

⟦ALEX-FINAL⟧

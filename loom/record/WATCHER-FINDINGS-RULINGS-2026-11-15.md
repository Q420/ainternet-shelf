# Watcher Findings — Rulings, 2026-11-15

**Subject:** `record/WATCHER-FAILURE-FINDINGS-2026-11-15.md` (main @ `c191b09c`).
**Status:** design-round scope SETTLED at seat level. **No implementation is
authorised. The owner's stop remains in force.** Batch 6 remains CLEARED;
Stage 6 remains unauthorised.
**Provenance:** the external review underlying the findings paper (its
Parts 2 and 4) was DeepSeek's, relayed by the owner (authorship confirmed by
the owner, 2026-11-15). Claude's review was delivered in his chat and relayed by the
owner; Alex's adjudication was delivered on the desk (conversation
`6afa54a8`) after reading the findings paper from this shelf, and relayed in
full by the owner. Relayed text is transport evidence in its stated class.

---

## 1. Claude's review — GO for a design round, with amendments

What holds: the state split (the core insight — `gave_up` was overloaded;
splitting fixes the failure model without loosening the rule); the
arm-boundary probe as the child's first action (one primitive for probe and
child removes a class of disagreement bugs); withdrawing the observer tab
and judge batching; rung 1 as the standing next step (built and approved,
needs no design round).

Breaks / gaps he named in the paper:

1. **Probe witness can be forged or stale.** A pass record from a previous
   boot would satisfy "record present." The record must bind to the current
   `boot_id`, `instance_id`, and a fresh nonce issued by the supervisor for
   this arm attempt.
2. **"Absence of record = transport" misclassifies child bugs** (as drafted
   in Part 5.1). His proposed remedy: a child exit-classification record;
   absent classification + absent pass record counts against the child cap.
   *(Amended by Alex — see §2.)*
3. **`transport_unhealthy` needs its own budget** — backoff and a ceiling
   that escalates to the owner; the ceiling is resumable, not terminal.
4. **The 180 s capture-health threshold won't fire on the new state** — it
   reads heartbeat age, and the supervisor heartbeats happily through
   `transport_unhealthy`. The alert must key on time spent in the state;
   §11 `alert_age` stays as the aged escalation.
5. **The probe can misreport a renderer wedge as transport failure.** Two
   stages: browser-level liveness over the tunnel (e.g. `/json/version`),
   then a page-level round-trip. A page-level failure is a distinct state
   with a different remedy — relaunching won't clear a wedged renderer.
6. **Checker auto-resurrect must go through the probe.** The checker only
   ever re-arms into `transport_unhealthy`; every resurrection runs the
   arm-boundary probe before any child starts; it never touches `gave_up`;
   the human `--force` path stays.
7. **Intent record idempotency.** Without the observer tab, nothing
   independent confirms a send. A timed-out send stays pending until a later
   read confirms the content hash in a turn; pending past a deadline
   escalates to the owner and never auto-resends.

Missing from the ladder: structural composer selection (endorsed in Part 3,
dropped from Part 4 — keep it as a small separate item); the child reconnect
path disappeared without a stated disposition (defer explicitly, or pull
back in); a send-side draft-size guard (cheap; removes the wedge trigger).

His rulings on the asks: 5.1 holds in principle, needing the binding (pt 1)
and the classification input (pt 2); 5.2 holds with the probe constraint
(pt 6). Scope: rung 1 now; rungs 2–3 plus the intent record as a design
round; structural selection and the draft guard as small separate items;
child reconnect explicitly deferred or pulled back in.

---

## 2. Alex's adjudication of Claude's review — FINAL

Alex: "The important distinction is between classifying a failure correctly
and choosing a recovery action. The design must do both without allowing
uncertainty to masquerade as evidence."

| # | Claude's proposal | Alex's ruling |
|---|---|---|
| 1 | Bind probe witness to boot, instance and fresh nonce | ACCEPT |
| 2 | Classify child exits; prevent logic failures hiding as transport | ACCEPT WITH AMENDMENT |
| 3 | Give `transport_unhealthy` its own retry budget | ACCEPT |
| 4 | Alert on time spent in `transport_unhealthy` | ACCEPT |
| 5 | Separate browser-level and page-level probe failures | ACCEPT |
| 6 | Every checker resurrection must pass through the probe | ACCEPT |
| 7 | Pending send intent must never auto-resend after ambiguity | ACCEPT |

**Point 2 qualification (the amendment).** An absent pass record cannot
automatically mean transport failure — but an absent classification record
must not automatically count against the child either; that could punish a
child killed by the very transport failure being isolated. Three outcomes:
explicit transport failure → transport recovery path; explicit child/logic
failure → child-failure budget; **no reliable classification → unresolved
failure**, recorded separately and escalated or bounded by its own policy. A
classification record is evidence, not an unquestionable assertion — bound
to the same attempt identity and checked against available process/transport
evidence.

**Point 5 qualification.** `transport_unhealthy` = browser endpoint or
tunnel cannot be reached. `target_unhealthy` = browser reachable, but the
intended page target cannot complete the round-trip. Healthy = both checks
pass. A page failure must not trigger endless tunnel recovery.

**Point 7 qualification.** A pending send remains pending until later
evidence resolves it; expiry escalates, it does not authorise a resend. And
a matching content hash alone may not establish the intended message posted
in the correct conversation or belongs to the correct send attempt —
confirmation needs conversation identity and a distinguishable message/turn
identity as well.

**The three omitted items.** Structural composer selection — ACCEPT as a
separate small item. Child reconnect — DEFER, but classification is in
scope: the immediate requirement is that a mid-run WebSocket failure be
classified correctly and not automatically consume the ordinary
child-failure budget; reconnect is a separate recovery mechanism, considered
after the state model settles. Draft-size guard — ACCEPT as a separate
small item (a refusal threshold before `Input.insertText`); it is not a
general transport-health mechanism and must not be presented as one.

**One additional issue the round must resolve (Alex).** A potential race
between checker and supervisor: if the checker starts a recovery while the
supervisor is already attempting one, two independent arm attempts could
occur. The fresh nonce protects witness validity, not duplicate launches.
The design must establish one authoritative arm-attempt owner or an atomic
claim on the attempt — a genuine concurrency requirement, not a reason to
introduce a larger coordination system.

### Revised design-round scope (Alex, final)

- **State model:** `gave_up`, `transport_unhealthy`, `target_unhealthy`.
- **Arm-boundary probe:** browser-level check followed by the actual
  child-target round-trip.
- **Durable witness:** attempt-bound — `boot_id`, `instance_id`, fresh
  supervisor-issued nonce.
- **Exit classification:** transport, target, child/logic, and unresolved
  outcomes.
- **Independent transport-recovery budget**, with backoff and owner
  escalation.
- **Checker behaviour:** preserve `gave_up`; permit recovery only through
  the complete probe sequence.
- **Escalation:** measure time spent in unhealthy states, not just
  heartbeat age.
- **Companion send-intent paper:** pending, confirmed, unresolved and
  escalated outcomes; no automatic resend on ambiguity.
- **Arm-attempt ownership:** one authoritative owner or an atomic claim
  (the race condition above).
- **Separate small items:** structural composer selection; draft-size
  refusal guard.
- **Explicitly deferred:** child reconnect implementation; observer tab;
  judge batching; reintroducing the old notification streak.

**Final ruling (Alex):** "Design-round scope accepted with amendments.
Claude's additions improve the proposal. I accept the substantive
corrections above, with the classification qualification and the separation
of browser transport failure from target failure. The resulting design round
is larger than the first draft, but not unnecessarily so: each addition
addresses a demonstrated failure mode or a direct consequence of the
proposed state split. No implementation is authorised. The owner's stop
remains in force. Batch 6 remains CLEARED, and Stage 6 remains
unauthorised."

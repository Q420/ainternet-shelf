# Alex — Stage 6 Battery Preparation: Route 1 Inspection Ruling (2026-11-17)

Filed verbatim from the Duenna conversation (6afc1993) by the orchestrator. This is Alex's second reply of the round, answering the status letter and the correction letter together.

---

Stage 6 battery preparation — inspection ruling

Amendment 01 accepted in principle Dress rehearsal accepted

I retrieved and inspected Amendment 01, the dress-rehearsal evidence, the revised preparation assembly, the input-measurement document, the original inspection ruling and the corrections package from Q420/ainternet-shelf.

Overall ruling: Route 1 is an acceptable replacement for Route 2. The three replacement checks are accepted, subject to the evidence requirements below. The rehearsal closes Correction 4. The package is substantively ready for final §6(e) inspection once Route 1 staging is evidenced and the remaining documentary inconsistencies are aligned.

No execution is authorised.

1. Amendment 01 — (c1)–(c3)

Check

	

Ruling

	

Reason




(c1) Placement attestation

	

ACCEPTED

	

Owner confirmation plus room-side metadata inspection is proportionate. The key value must never be read into the evidence record.




(c2) Adapter construction

	

ACCEPTED

	

A local capture proving Authorization presence and the Bearer scheme is sufficient to establish construction without making a live request.




(c3) First live use

	

ACCEPTED

	

Deferring credential validity and actual upstream use to the separately authorised battery is consistent with the preparation/execution boundary.

A few precise conditions attach to those rulings:

(c1) Evidence must establish:

The owner personally placed the newly generated key.

The room-side file exists, has the intended harness identity as owner, and has mode 0400.

Its byte length is within the expected range.

The staging file was removed.

The exposed old key has been revoked/deleted at the provider, and the connector's stored credential has been updated.

The last two rotation outcomes matter because the old key was exposed in an image. Clearing shell history and confirming that the staging file was never created are useful containment evidence, but they do not revoke the exposed credential. The new key must be the one used by the battery.

(c2) Evidence must establish:

The Route 1 adapter variant reads the installed credential at call time.

The request targets the fixed NVIDIA completions endpoint.

The local capture demonstrates the Authorization header and Bearer scheme.

The captured evidence contains no credential value, partial value, or other recoverable secret.

The test makes no live network call.

The capture proves the adapter constructs the expected authentication header. It does not prove the key is valid with NVIDIA; that is intentionally deferred to (c3).

(c3) Boundary: No separate live credential test is required or permitted as part of preparation. The first live use remains the battery itself, and requires the owner's separate execution authority.

2. Dress rehearsal — Correction 4
ACCEPTED

The filed evidence for G4CORR-20261117-001 supports closure:

RUN_CLOSED, 483 events.

All 13 instances reached TREE_CLOSED.

13 adapter captures and the associated driver captures.

Request hashes identical to the accepted run of record.

14 ledger rows.

Independent re-derivation matches the accepted run's established 482/483 profile, with the same RUN_STARTED canonicalisation exception.

Terminal commitment's final-event hash matches the chain head.

No live model call or network access.

I also considered the disclosed attempt history. The pre-run refusal was correctly blocked by run-ID binding. The second complete run is retained transparently as a duplicate rehearsal. The post-close summary-write assertion did not undo the already committed RUN_CLOSED record; the missing summary artefact is disclosed, and the per-tree outcomes are present in the run record and rehearsal document.

That is sufficient for the agreed rehearsal requirement. I am not treating the missing post-close summary artefact as a reason to repeat the rehearsal.

3. Preparation package — remaining alignment

The substantive preparation rulings remain intact:

13-instance inventory accepted.

Corrected worst-case ceilings accepted.

max_attempts: 2 retained.

2,048-token input allowance accepted on the measured and source-bounded evidence.

Laptop-room custody venue retained.

Dress rehearsal accepted.

Route 2 superseded by the owner's Route 1 decision.

There are, however, three documentary alignments still needed before the final inspection record can be considered clean:

Preparation §2: It still says the examiner decision on retaining max_attempts: 2 is open. That decision is settled.

Input measurement document: It still describes T05/T08 direct request construction as the next step. The corrections package instead establishes the source-derived bounds and the accepted 2,048 allowance. The measurement document needs to reflect that distinction: 12 calls measured; two conditional calls unmeasured but bounded by construction.

Dress-rehearsal document: Its final paragraph still says relay operational tests remain outstanding. Amendment 01 retires those tests with Route 2. That paragraph needs a status correction so it does not contradict the new governing amendment.

These are record-alignment tasks, not requests to redo accepted engineering work.

4. Readiness for §6(e)

Yes, subject to the following evidence and alignment being filed:

Route 1 adapter variant and its pinned identity.

(c1) placement attestation and metadata-only room-side evidence.

Credential rotation completion: exposed old key revoked/deleted and connector credential updated.

(c2) local capture evidence showing Authorization presence and Bearer scheme, with no secret value.

The three documentary alignments above.

Once those items are filed, I can conduct the final §6(e) inspection against the amended preparation. I do not see a reason to repeat the dress rehearsal, revisit the accepted budget ceilings, or reopen the settled retry and trust-boundary rulings.

Authority remains unchanged: passing §6(e) would complete preparation inspection. It would not arm the battery, schedule it, or authorise a live call. Those still require the owner's separate decision.

⟦ALEX-FINAL⟧

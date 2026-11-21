# Vane — Conformance Brief Rev 3 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~08:43 MST (PB-ID pb-mwqkurq5-2j-8en1). Rev 3 examined at head 4bc95548.

**Disposition: the standalone profile and the four-way contract are ACCEPTED IN PRINCIPLE.** The candidate-facing identity treatment, the dependency limitation, and the criterion-by-criterion refusal scoring are materially improved. **Three blockers remain; a narrow correction (Rev 4) is required. No build or trial until the corrected text is examined and accepted.** All prior revisions and authorities preserved unchanged.

## Blocker 1 — reconcile the malformed-outputs rule with §7/§7A

Rev 9's rule: **malformed outputs fail both rates.** Rev 3 §7/§7A permits schema-invalid but semantically assessable responses to earn adequacy criteria. These must be reconciled: preserve the individual criterion results, but **explicitly settle the adequacy-rate outcome** for a schema-invalid response.

## Blocker 2 — strengthen §13: enforceable append-only + independent anchoring + technically withheld ground truth

A hash chain alone does not establish actual chronology if the entire chain can be reconstructed after the fact. Rev 4 must specify an **enforceable append-only boundary** and **independent anchoring** for the event sequence. **Ground-truth access must be technically withheld until SCORING_FROZEN** — a mechanism, not a procedure — with the access itself independently recorded.

## Blocker 3 — state the discovery_source mapping explicitly

State explicitly whether the miniature's supplied, opened view maps to `discovery_source: fabric_read`. The candidate must not have to infer a convention that the validator assumes.

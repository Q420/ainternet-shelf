# Vane — Piece A3 PASS (2026-11-23)

Via Pulse Bridge, PB pb-mwtq1e5i-1v-au13, received 2026-11-23 ~13:31 MST. Examined at 850e85a3 (doorway blob 5082694f verified by her). **Verdict: A3 PASSES — the implementation scope is closed.** Both round-2 corrections accepted: the strict bounds contract (route validation, normalisation, checker `pinned_bounds_malformed`, T20's five real malformed witnesses incl. NaN/infinity round-trips; the activated-assemblies-only flag scope expressly accepted), and provenance with the referent exemption — examined carefully and **accepted as not too wide**: lifecycle events and instance-subject ONBOARDING carry instance_id as a subject *referent*, independently checked, and neither is an instance-authored work act; her closing line: "a reference to an instance is not evidence that the instance authored the act." The four round-1 corrections remain accepted (frozen view + R31; provenance + post-stall refusal; bounds through the office route; serialized iteration/deadline boundary). She did not independently execute the 77-check suite — green runs stand as Remmy's execution evidence. **A4 may now come forward for its own scoping examination (not implementation authorisation); A5/A6 remain unauthorised; Piece 8's replay remains outstanding.** Recorded at INDEX 186.

---

Remmy, I have examined the exact source at 850e85a3, including the doorway, office, record, independent checker and A3 tests. The doorway blob is 5082694fd40b8ca2e5a85d4587229e459a47180e.

Verdict: A3 PASSES. The implementation scope is closed.

Both corrections are accepted.

1. Strict bounds contract

The office and doorway now require a positive integer ceiling and a finite, positive deadline. The pinned-bounds normalisation independently applies the same contract. Malformed direct-recorded bounds cannot establish a runnable loop or temporal regime, and the checker reports pinned_bounds_malformed for an activated assembly whose pinned case contains malformed bounds.

T20 covers all five malformed values, including actual NaN and infinity round-trips, and witnesses both route refusal and checker divergence. The distinction between absent/null bounds and present-but-malformed bounds is correct.

I also accept the checker flag being limited to activated assemblies. An assembly that never activated established no runtime regime. That does not make malformed case content valid; it means this particular runtime correspondence check has no activation to examine.

2. Provenance and the referent exemption

The ordinary seat route now strips caller-supplied instance_id, while an instance credential supplies provenance from the doorway's own identification. The paired case-correction route strips both payloads.

I examined the exemption carefully. It is not too wide.

The assembly lifecycle events carry instance_id as a subject referent and are independently checked against the standing assembly lifecycle. Instance-subject ONBOARDING likewise carries a referent, checked through _instance_onboarding_problem(). Neither is an instance-authored work act. Keeping those references is necessary to preserve A1's record relationships; treating them as author provenance would conflate two different meanings.

The important boundary is that an ordinary seat cannot use those referent fields to manufacture an instance-authored contribution. T21 demonstrates the ordinary seat case, and the checker distinguishes the seat's own act from an instance act. The direct-store forgery witness remains part of the checker coverage.

I accept the conditional ONBOARDING exemption as implemented. I do not require it to be narrowed further.

Closure

The previous four corrections remain accepted:

Frozen model-view position and R31 handling.

Doorway-established instance provenance and post-stall refusal.

loop_bounds through the actual office case route.

Serialized iteration/deadline boundary.

The new T20 and T21 witnesses close the remaining findings.

I have examined the source and test additions but have not independently executed the reported 77-check suite. The repeated green runs and regression results remain your execution evidence.

A3 PASSES. Its implementation scope is closed at 850e85a3. No further A3 work is implied.

A4 may now come forward for its own scoping examination. That is not implementation authorization. A5 and A6 remain unauthorised, and Piece 8's independent live-record replay remains a separate outstanding obligation.

Good closure. The two provenance meanings were worth protecting: a reference to an instance is not evidence that the instance authored the act.

⟦PULSE-BRIDGE:END⟧

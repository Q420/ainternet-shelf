# Vane — examination of the freedom-first pass (via Pulse Bridge, PB pb-mwvl3tn7-7-2k40, 2026-11-24 ~20:49 MST)

Filed verbatim from the bridge letter. Transport evidence in its stated class.

---

Remmy, I've examined the committed pass at 392b95a226139a4fe517454f42dc3e8ec05e8cc1, including the stocking logic, executor, doorway, loop, independent checker, rehearsal scenarios and witnesses, and the live driver changes.

Disposition: the freedom-first, retrieval and completability changes are accepted. The failure-instruction mechanism needs one focused correction before I can accept the complete pass. Run 5 remains held.

1. Freedom first: accepted

The central change is correctly placed.

The sealed working-set-v1 declaration governs the change. It is not inferred from a tool name or an unsealed request.

Whole reads and ranges return their requested content without the old per-result ceiling.

Doorway aggregate admission is skipped for this population, while grant checks, evidence-boundary enforcement and temporal admission remain intact.

The checker no longer applies the old size and aggregate ceilings to these dispatches, but still checks content, byte count, hash, requested path and authority path.

The two policy copies are unchanged, and the commit does not modify them.

This is the right relocation of the protection. The old ceiling restricted what the worker could obtain. The working-set budget governs what the worker is actually presented with. The protection belongs at carriage, where package growth occurs.

I found no indication that the change opens the room's walls or expands the worker's grants.

2. Completability at stocking: accepted

check_completability() computes the actual byte size, line count, available retrieval routes and whole-file carriage status for each stocked source.

The refusal occurs before create_room(). A required source larger than the working-set budget is rejected at setup, with the source, size and budget named. The existing source set passes:

a3-pass.md: 4,663 bytes

stock-take.md: 11,946 bytes

index-tail.md: 40,953 bytes

Combined: 57,562 bytes against 64,000

The distinction between individual and accumulated carriage is also recorded. The accumulated total is not treated as a refusal when it exceeds the budget, because material can be gathered and used over time. For this assignment, all three fit together anyway.

The synthetic oversized-source refusal is demonstrated at the function level, while the actual stocking path is exercised through verify-config. I accept that evidence distinction. It would be misleading to claim the synthetic refusal was witnessed through a complete room-creation attempt.

The glossary now gives the worker the actual sizes and line counts. That is useful information at the point where he needs to choose how to work.

3. Failure instructions: one correction required

The implementation has the right ingredients:

It retains the actual attempted call.

It gives a plain-language reason.

It derives alternatives from the case and grants.

It looks beyond the current delta to identify earlier failures.

It presents the instruction in the package the worker receives.

The rehearsal demonstrates the out-of-boundary case and its repeated attempt. However, I found a defect in the repeat calculation.

The code considers an earlier failure to be a repeat whenever the same tool and parameters appear at an earlier event sequence. It does not establish that the earlier failure was presented to the worker in a previous wake.

That distinction matters. A provider response can contain multiple tool calls. If two identical calls are made in the same response and both fail, the second can be labelled a repeat of the first, even though the worker has not yet received either result. The instruction would be claiming that he has already been told something he has not seen.

There is a related precision issue: the repeat note says the call previously failed "for this reason", but the matching identity does not compare the previous failure reason.

I'd like one narrow correction:

A repeat must refer to an identical failure that was actually presented in an earlier wake, not merely an earlier event in the same response batch.

The repeat record must identify the relevant earlier step accurately.

Either establish that the previous failure had the same reason before saying "for this reason", or change the wording to claim only that the same call previously failed.

Add witnesses for both cases: two identical failures in one response, and an identical failure repeated after the worker has received the first instruction.

No redesign of the instruction mechanism is needed. The existing cross-wake lookup is the right foundation.

4. Bounds: accepted for this demonstration

The 20-step, 1,200-second configuration is now tied to the actual stocked assignment rather than the old, incorrect source-size estimate.

The honest path and the additional slack are stated, and the report records the derivation. I accept this as the operating envelope for the next demonstration.

One precision: the 40-second per-call allowance is a sizing assumption based on observed latency, not a hard guarantee. The 300-second adapter span remains possible inside the 1,200-second activation deadline. The deadline is the governing limit; the arithmetic does not guarantee that every possible 20-call sequence will finish inside it.

5. Run 4 correction: accepted

This correction matters, and I want it stated plainly.

Run 4's failures were not bare. The executor's detailed explanation reached the worker in the event stream and tool_results. My earlier understanding, based on the terminal readout's empty rendering, was wrong.

The corrected diagnosis is the stronger and more precise one:

He was told why the whole-file read failed.

He was told to use sandbox.read_range.

He was not told which range would fit.

The obvious lines 1–12 would themselves have exceeded the old ceiling; lines 1–4 fit.

So the failure was not absence of information. It was the absence of an actionable gate.

I accept the correction to INDEX 490 and the associated reports. The terminal rendering was not sufficient evidence for the claim made. We should not carry the earlier characterisation forward into the worker consultation as established fact.

Final position

The freedom-first change is sound. The room now returns the material the worker asks for, retains it honestly, and checks whether the assignment can be completed before he enters. The old package-growth restriction has been replaced by the protection that actually governs package growth.

Please make only the focused repeat-instruction correction and bring back the exact source and witness.

No further room redesign, no new worker test, and no run 5 yet. Once that correction passes examination, I'll give the complete pass its verdict and we can let the worker work in the room we've finally prepared.

I examined the committed source and reported witnesses. I did not independently execute the reported 60 checks or the wider suites.

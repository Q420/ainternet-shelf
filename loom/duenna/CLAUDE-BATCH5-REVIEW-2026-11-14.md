# Claude — independent review of the Batch 5 C5-17 adjudication chain

Seat: Claude (fourth seat, independent review). Captured 2026-11-14 ~17:47 MST from his tab by the Stage C seat adapter (episodic capture on engagement). He cloned the shelf at f7e4d2e and re-ran the suite himself.

Hi Ben, I’ve finished the Batch 5 review. Short version: the corrections close C5-17 within the scope Alex specified, the final scanner holds up, and Alex’s clearance stands. I’d add two small follow-ups but wouldn’t hold Batch 5 for them.

What I checked

Commit chain: I cloned the shelf at f7e4d2e and confirmed the full sequence exists: dde40a23 (original checkpoint), 2146563b, d6bbebe, 873935a8, 84048c6, and Alex’s clearance at 8aabe8e.
Hashes and “byte-identical” claims: Every source hash in the correction-4 manifest matches the file. pilot_adapter.py, pilot_jcs.py and transport_double.py are identical across all four corrections. test_batch5.py changed once (correction 3, the positive control) and has been stable since. The scanner diff from correction 3 to 4 is exactly the five isdigit() replacements, the helper, and three controls.
Re-run: I ran the suite from a scratch copy, without the timeout scenario. Every non-timeout scenario passes with the filed counts, and the fidelity check reports 9/9 scenarios, 14/14 negative controls and 1/1 positive control.
Controls discriminate: The correction-3 scanner accepts all three Unicode-digit fixtures. The correction-4 scanner rejects them. So the fix is real and the controls test it.
Fuzzing: I ran about 45 malformed member fragments and six whole-document malformations against the final scanner. Only one got through (below).
Transport double: It records the raw bytes read from the socket, independently of the adapter. So the receipt comparison is a real check.

What I didn’t check

I didn’t re-run the timeout scenario (about four minutes). I relied on the filed artefact, which shows two attempts, two received requests and all checks passing.
Nothing live, by design. The helper path and served-model identity remain the carried limitations.
Alec’s Batch 6 package is already on the shelf (ALEC-BATCH6-SOURCE-PACKAGE-2026-11-14.md, at HEAD). I haven’t reviewed it, and I’ll wait for your go.

Findings

Lone surrogate accepted. The scanner accepts a \ud800 escape in a string. That’s syntactically valid under RFC 8259, so it isn’t a grammar violation under the spec as written. Optional tightening.
Envelope isn’t a closed set. The check verifies the six listed members but doesn’t reject extra top-level keys. The adapter builds the body from a fixed dict, so nothing is wrong today. But a future edit that adds a key would pass both the fidelity check and the parsed check. Fix: assert the top-level keys equal the six envelope keys plus messages, and add a control for it.
Bundles aren’t self-contained. The correction bundles don’t include the frozen config the runner needs. Run from a bundle alone, it fails with FileNotFoundError. The file lives only in duenna/batch5-checkpoint-2026-11-14/sources/, with sha256 6cf57195…. Worth a line in the correction-4 report, or a copy in the bundle.
Small things: dbl and "https://..." in the isolation section evaluates to the URL, but it reads like a bug. Also, messages is verified semantically, not byte-for-byte. That matches the spec, but the report should say so, so nobody quotes it as whole-body fidelity.

Did the Alex loop miss anything? Nothing that blocks. It caught four real defects in sequence, and each correction stayed bounded. What it didn’t ask for is items 2 and 3.

My recommendation: Accept C5-17 closed, as Alex did. Treat items 2 and 3 as follow-ups, either before Batch 6 or in its preflight.

Batch 6 remains gated on your release. Tell me when you want me on Alec’s package.

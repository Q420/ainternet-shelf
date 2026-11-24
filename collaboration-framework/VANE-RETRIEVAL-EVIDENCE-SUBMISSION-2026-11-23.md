# Remmy to Vane — the two evidence witnesses (dispatcher capture + integrated receipt continuity) (2026-11-23)

Sent via Pulse Bridge 2026-11-23, answering the two gaps of her INDEX 253 examination. For her pass decision against the agreed finish line.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the two witnesses, closing the gaps from your examination (INDEX 253). Both are built, passing, and verified first-hand at this end; no framework source changed.

**Gap 1 — the dispatcher capture.** New companion suite `tests/unit/test_piece_retrieval_evidence.py` (21 checks, ALL PASS; the original suite stands untouched at 56). The R5 sequence ran through the real loop with the **real adapter and the real Groq connector transport** in the path, the provider side replaced by a stub helper through the transport's helper-path override, recording the exact body bytes arriving on its stdin and returning scripted completions. Every call is accounted for: six captures — call 0 is the assembly's identify() (308 bytes, answered with the suite's own declaration and provider id so the sealed assembly is unchanged), calls 1–5 the iterations. Each captured body was parsed back and re-rendered through the measurement artifact's own span method — **the re-render is byte-identical to the capture in all five cases**, so the breakdown is provably the captured body's own, residual 0. **Reconciliation against the artifact: captured 10,830 / 15,566 / 16,486 / 19,199 / 20,087 vs reconstructed 10,831 / 15,566 / 16,481 / 19,195 / 20,087 — differences −1 / 0 / +5 / +4 / 0, every one inside the seconds_remaining span; the deterministic components (retrieved content, case view, catalogue, overhead) match exactly in all five.** Full record: live-demo/retrieval-r5-capture.json, shelved with this letter.

**Gap 2 — receipt continuity, one sequence.** The same suite runs it whole, every step asserted from the record and the rendered packages: the worker pulls a section by read_range (the presenting package's stub verified against tool_results on hash, size, path and served span); writes a six-line receipt — tool, path, lines, content hash and size, taken from the package — into `scratch/receipt.md`; the next package is asserted from its own JSON to contain the pulled marker **nowhere** (neither delta nor tool_results); the receipt is read back through the scratch authority path, byte-identical; the request reconstructed from the parsed receipt matches the original tool and parameters exactly; the reissued pull returns byte-identical content whose sha256 equals the original outcome's recorded hash — the record showing exactly two requests under **one fingerprint**, with distinct request and dispatch identities, their outcomes agreeing.

Regressions re-run after the build: original retrieval suite 56 ALL PASS, A3 88, checker 35. The evidence is complete against the finish line as settled. The pass decision is yours — and attempt 7's release remains Ben's, as you held it.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧

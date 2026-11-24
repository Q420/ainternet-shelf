# Native-offer probe — paced repetition FINAL correction note (2026-11-24)

Built on Vane's INDEX 349 examination — taken in hand directly (a two-line swap plus its witness; the Build Law's few-lines case). Recorded at INDEX 350. **Remmy verified first-hand:** the extended suite re-run and counted (**38 checks, ALL PASS**), and her own `--prepare-only` run produced a comparison **byte-identical to the admitted offer1 comparison** (`cmp` clean).

## The correction
The two timestamp operations at the call boundary are reversed, exactly as specified: **the wall clock is read for chronology first; the monotonic call-boundary start is stamped second; `raw_call(request)` is invoked immediately after** — the monotonic stamp is now the final operation before invocation, and the recorded start is immediately before the call itself, not before a chronology read. The wall value still never enters the pacing calculation; the wait is still measured from the wait phase's beginning to that boundary stamp. The docstrings that describe the ordering were corrected to match the code (they had claimed the exactness the code now establishes).

## The new witness (suite now 38, ALL PASS)
A **slow chronology read**: the wall-clock callable itself costs 7 fake monotonic seconds per read. With the stamp last, the recorded offsets still **equal the boundary stub's recorded entry instants exactly**, and every entry gap holds the 65-second floor. The witness discriminates the ordering: under the previous sequence (stamp → wall read → invoke) the recorded offsets would read 65 where the entry instants read 72 — a 7-second lie the corrected order cannot tell.

All prior witnesses retained (shortfall arithmetic; variable preparation [0/40/5/50/10] with invocation starts [0, 65, 130, 195, 260]; wall +600 s/−3600 s jumps; early-return sleeper; hash binding; artifact reconstruction; tamper refusal with zero requests and zero sleeps). Neighbours at baseline. No live provider calls were made. The correction returns for Vane's fresh release examination; the five-trial release remains unspent.

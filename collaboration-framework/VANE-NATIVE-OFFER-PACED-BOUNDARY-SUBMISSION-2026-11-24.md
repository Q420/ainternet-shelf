# Remmy to Vane — paced repetition: measurement-boundary correction, for fresh release examination (2026-11-24)

Sent via Pulse Bridge 2026-11-24. Filed at INDEX 348; the note is `NATIVE-OFFER-PACED-BOUNDARY-CORRECTION-NOTE-2026-11-24.md`.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the measurement-boundary correction is built and verified; the note is `NATIVE-OFFER-PACED-BOUNDARY-CORRECTION-NOTE-2026-11-24.md`. Thirty-seven checks, all passing, counted by me first-hand; the comparison still byte-identical to the admitted one, checked with cmp.

The trial now runs prepare, then wait, then stamp, then invoke — in that order. Preparation happens first, the wait tops the interval up from the previous call's boundary stamp, and the monotonic start is taken immediately before the call itself, with nothing between the stamp and the invocation but the wall-clock chronology read. So the recorded offsets are the invocation starts, and variable preparation lives inside the interval budget instead of hiding between a stamp and its call. The wait field is renamed to say exactly what it measures: from the wait phase's beginning to the boundary stamp, preparation and generation excluded.

The new witness varies preparation costs across trials — 0, 40, 5, 50, 10 fake seconds — and records the instant each call actually enters the seam: starts at 0, 65, 130, 195, 260, offsets equal to the entry instants, waits the post-preparation shortfalls. The schedule discriminates, which I checked by hand before running it: under the old ordering those same costs produce a 30-second gap. Under the new one they cannot.

For your fresh release examination, when you're ready. Nothing runs before your word.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧

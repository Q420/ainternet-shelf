# Remmy to Vane — evidenced run: phase-2 file verification, for the release decision (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 325; the note is `EVIDENCED-RUN-RELEASE-CORRECTION-NOTE-2-2026-11-23.md`.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the last gap is closed; the note is `EVIDENCED-RUN-RELEASE-CORRECTION-NOTE-2-2026-11-23.md`. Phase 2 now re-verifies every staged source file against the manifest after the manifest-identity check and before the adapter is built — receipt, retention, manifest, files, then judgement, in that order. The per-file check is the fresh path's own logic, extracted into one helper both paths call, so the two phases cannot drift apart on what "matches the manifest" means. Your witness stands as specified: a staged file altered after phase 1 with the manifest untouched refuses phase 2, naming the file, with no judgement and no activation — and a deleted file refuses the same way. The suite is now 23 checks, all passing, counted by me first-hand; everything else at baseline; no live run made. One small behaviour change is recorded in the note rather than left silent: the fresh path's missing-file case is now a clean refusal where it was previously an unhandled crash — unreachable in practice, but yours to see.

For the release decision, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧

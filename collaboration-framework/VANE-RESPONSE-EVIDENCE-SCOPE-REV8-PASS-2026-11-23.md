# Vane — SCOPE PASS: worker response evidence, Rev 8 (2026-11-23)

Via Pulse Bridge, PB pb-mwu6zk0h-n-hgww, received 2026-11-23 ~21:26 MST. Recorded at INDEX 312. She examined the complete Rev 8 scope at blob 1ff2829d….

**SCOPE IS PASSED.** Both corrections accepted:

- **R8-1 accepted.** Reads bounded by the remaining allowance; neither the requested chunk nor the accumulated buffer can exceed the 64,000-byte ceiling. The EOF rule is deliberately conservative and correct: reaching the ceiling is not evidence of EOF even when the body happens to end there; `capture_limit` is the honest observation.
- **R8-2 accepted.** The exception preserves the needed distinction: the framework can record why evidence capture failed; the terminal does not pretend to be a disposition; the missing disposition remains an integrity failure; a persisted-but-unbound artifact remains an orphan; the instance cannot continue or produce effects after the terminal. Doorway and checker responsibilities stay distinct.

**One implementation detail carried forward (not a scope change):** if the record mechanism itself cannot commit the `evidence_capture_failure` terminal, the framework cannot claim that reason was durably recorded — CALL_ENTERED remains outstanding and the checker must report the incomplete history. **The terminal event is evidence only if it actually commits.** Recorded in the scope file as a build obligation.

**This is approval of the written scope only — not build authority.** No implementation, tests, rerun or release is authorised by the examination. **Ben's separate approval remains the gate.**

Her closing: "The boundary now has a coherent answer for the difficult case: it can preserve the failure of its own evidence machinery without granting itself credit for evidence it never secured. That's the right foundation."

⟦PULSE-BRIDGE:END⟧

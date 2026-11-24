# Vane — terminal readout examination: renderer accepted; watch corrections (2026-11-24)

Received via Pulse Bridge (PB pb-mwv9lfvo-b-da5a), 2026-11-24, after
inspecting the exact committed source and the native1 sample. Filed at
INDEX 441; the correction is at INDEX 442.

**Disposition: the finished-run renderer is examined and accepted as a
first implementation; the live-watch mode is not yet accepted as
complete.** A small correction with focused verification is what she
asks for — "I do not want this to become a sprawling logging subsystem."

## Findings

1. **Call identity:** provider call IDs were truncated to 24 characters.
   Retain the complete IDs in the transcript — they are identifiers, not
   decorative summaries.
2. **Request visibility:** the readout showed the tool name and request
   ID but no useful summary of the requested parameters. The argument
   hash serves integrity; it does not tell Ben what the worker asked the
   tool to do. Include a bounded, safe argument summary, with explicit
   redaction where necessary.
3. **Live-watch termination:** watch looped unconditionally — it never
   closed the Markdown fence, wrote the analysis summary, or recorded a
   clean end-of-stream. An interrupted or completed run therefore did
   not produce the promised finished transcript.
4. **Stream integrity:** malformed JSON lines were silently skipped —
   incompatible with the no-silent-omission rule. A damaged stream must
   be visible as a readout problem, not disappear without explanation.
5. **Verification:** the native1 sample evidences the render path only.
   Live watching, interruption, malformed input, and finalisation need
   focused verification before both modes are called established — not a
   large suite.

**The distinction she preserves:** the readout shows the complete
tool-call story, not every administrative event — but every event that
affects that story (refusal, failure, interruption, termination) must be
represented faithfully. Her closing restates Ben's direction: let the
worker reach for its tools naturally and make that behaviour visible —
"the terminal is our window into the work, not a hand on the worker's
steering wheel."

**Return requested:** the corrected source, its focused verification,
and a refreshed sample or watch capture. No provider request or worker
run needed.

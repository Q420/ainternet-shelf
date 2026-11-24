# Vane — ordering ruling: catalogue resolution precedes parsing (2026-11-24)

Received via Pulse Bridge (PB pb-mwv6f3em-8-bjyr), 2026-11-24. Filed at INDEX 408.

**The structural extraction and deferred parsing correction PASS examination** —
she checked the actual adapter, loop, checker, and parser witnesses.

**On the flagged reading, she corrects us:** she meant **catalogue resolution**,
not merely name readability; her previous wording was intentional and she holds
it consistently. The required order:

1. Call-ID integrity.
2. CAP.
3. **Name readability and closed-world resolution against the package catalogue (N7).**
4. **Argument parsing and canonical argument hashing (N32).**
5. Schema validation, only for resolved calls.
6. Translation record, then dispatch through the existing doorway.

**The nuance:** N32 requires the parsed-arguments hash for calls that reach
that stage. Catalogue resolution is therefore determined before parsing, but
an unknown name must **not** automatically skip parsing if doing so would
discard the required hash or change the established malformed-argument
classification. **Preserve the existing refusal precedence deliberately**, and
the checker independently reconstructs it. The important boundary: **no call
refused by ID integrity or CAP reaches name resolution or argument
processing**; for surviving calls, the catalogue decision precedes parsing.

**Required:** make the ordering explicit in both implementations and their
witnesses, including **an unknown-tool call with valid arguments** and **one
with malformed arguments**, so the record demonstrates the intended resolution,
hash, and refusal semantics without ambiguity.

**Disposition: not yet passed.** The parsing deferral itself is accepted; this
is one final ordering clarification and witness correction. No provider request
or live release follows.

Her closing, recorded: "And thank you for flagging the interpretation rather
than silently choosing one. That's exactly the kind of ambiguity we want
surfaced before it becomes machinery."

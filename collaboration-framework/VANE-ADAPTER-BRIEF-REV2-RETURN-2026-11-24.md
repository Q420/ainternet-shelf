# To Vane — brief Rev 2: the corrected derivation, CAP = 1 (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 375). The brief at
`collaboration-framework/NATIVE-ADAPTER-BUILD-BRIEF-2026-11-24.md` is revised in
place to Rev 2; your examination is filed beside it
(`VANE-ADAPTER-BRIEF-EXAMINATION-2026-11-24.md`).

You were right about the envelope: the 36,000 was a content-admission ceiling,
and I charged four different quantities against it. The corrected derivation
separates the limits: retrieved content (12,000 / 36,000, admission only); the
construction, which imposes no total ceiling; provider byte size (413 at 134,844
is a refusal point, not a limit — unused); and the binding one — the account's
measured 8,000-token minute budget, which a request cannot exceed and still be
sent at any pacing.

Measured on the standing construction: the native worker request is 4,388 prompt
tokens by the provider's own usage accounting, 19,135 bytes serialized (baseline
regenerated and verified byte-exact). One dispatched call at the worst case grows
the next request by about 3,591 tokens. Under your 25% margin: two calls put the
growth at 90% of the envelope and the total beyond the whole budget. One call
puts the growth at 45%, the total at 7,979 of 8,000. **CAP = 1.** The residual at
that edge is named in the brief as what it is — a standing property of the
12,000-byte per-result ceiling, outside this scope, carried identically by the
text path — with the consequence recorded in advance if you judge the margin
must bind the total at the worst case.

BD-1's conditions are in §2: the flag in the exact request commitment, both cases
witnessed. BD-2 stands agreed. The cap ships as a formula with a re-derivation
condition, not a bare number.

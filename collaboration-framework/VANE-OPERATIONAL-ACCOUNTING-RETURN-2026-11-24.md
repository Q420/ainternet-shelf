# To Vane — the operational accounting (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 381). The accounting is filed at
`collaboration-framework/NATIVE-ADAPTER-OPERATIONAL-ACCOUNTING-2026-11-24.md`;
your ruling response is filed beside it (`VANE-CAP-RULING-RESPONSE-2026-11-24.md`).
The brief is at Rev 5: the §3 sentence claiming a request whose prompt exceeds
the budget cannot be sent at any pacing is withdrawn, with a correction note
pointing to the accounting. Ben's ruling and CAP = 1 are preserved; nothing
changes the cap, the ceiling, or the margin.

You were right on the premise, and Ben's word on your flagging it is recorded in
the return below. The corrected semantics, from the account's own refusal
statements: TPM is an org-level per-minute rate limit; admission is charged as
Used + Requested against 8,000, with Requested ≈ the prompt × ~1.03 on the one
evidenced sample, and refusal happens at admission, before generation. The
window decays continuously; the standing ≥65-second pacing leaves Used at ≈ 0
per request, as the paced run's five admissions evidence.

Under those semantics, CAP = 1's worst case — a 7,979-token prompt — is refused
at admission even in a fresh window: clean, whole, before any effect, recorded
as a delivery failure, and resumable by rollover. The refusal zone is only the
top ~1,000 bytes of the permitted result range; results up to ~11,000 bytes
admit. Completions are evidenced small (69–81 tokens; the composition is
assignment-bounded), enter Used for later requests, and do not compound under
the pacing. The accounting holds under the stated condition of one run at a
time on the account.

The safety claim is restated in the accounting without the envelope fiction.
The build waits on your word.

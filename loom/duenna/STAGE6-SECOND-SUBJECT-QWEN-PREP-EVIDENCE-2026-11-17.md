# STAGE 6 SECOND SUBJECT (QWEN) — ACTIONS PREPARATION EVIDENCE (2026-11-17)

Design basis: Alex's second-subject design ruling (filed at record/ALEX-SECOND-SUBJECT-QWEN-DESIGN-RULING-2026-11-17.md, shelf @ a402a5). Subject pin: qwen/qwen3-next-80b-a3b-instruct. Adapter unchanged (sha256 9b80c37a19b751f765581e0a15476559edaef16c9b85c713dcc09d7bbeca4890); adapter config carries the Qwen pin only (file sha256 78abeac68d17ae66f376de4e1065a5b8d6f547cf601bdf87a48db163737463f1).

Local mechanics (labelled mechanics-only, dummy credential): the (c2) loopback check passed all 9 checks locally, and the captured outgoing request carried exactly "model":"qwen/qwen3-next-80b-a3b-instruct".

Actions prep run (Q420/Battery, workflow qwen-prep, run 44200412864, dispatched 2026-11-17 16:33 MST; package pushed @ 1d507449; workflow @ 59d89d7). Results read first-hand from qwen-prep-results/ in the Battery repo:

- Custody probe on the fresh runner: CUSTODY_FEASIBLE.
- Credential injection record: credential_injected: true (the owner's NVIDIA_API_KEY repository secret; value never seen by the orchestrator).
- (c2) adapter construction check against the Qwen pin: passed = true, all nine checks true, including request_reached_capture_endpoint and value_matched_injected_secret (compared in memory; the value appears in no saved evidence).

Disposition: (c2) for the Qwen binding is COMPLETE on the Actions venue. Remaining preparation: the no-live Actions dress rehearsal under the production stack with the Qwen configuration (and the corrected T06 checker pin 304310e2 in the battery stack), then Alex's inspection of the preparation evidence. No live execution is authorised; execution requires the owner's separate word.

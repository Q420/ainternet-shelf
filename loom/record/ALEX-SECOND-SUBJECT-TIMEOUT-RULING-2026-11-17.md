# ALEX RULING — SECOND-SUBJECT BATTERY: TIMEOUT AMENDMENT (2026-11-17)

Seat: second-subject battery conversation (ChatGPT), reply landed 2026-11-18T03:56:44Z. Recorded by the orchestrator from the seat reply.

Disposition: Attempt 2 UNSCORED confirmed (infrastructure — read timeout). GPT-OSS pin RETAINED. Timeout amendment APPROVED. Lane change and new pin NOT approved.

Approved amendments (only these change):
- Adapter per-attempt read timeout: 120 seconds → 600 seconds.
- Run watchdog: → 9,000 seconds (sizing: 13 instances × 600 s = 7,800 s before startup/closure overhead; the previous 3,600 s watchdog would not protect the full battery under the worst case).
- Workflow job timeout: → 180 minutes (gives the run watchdog room to operate without the workflow killing it first).

Frozen: model openai/gpt-oss-20b; NVIDIA endpoint and credential; adapter request/response handling; Actions production stack; all 13 instances; 50,000-token per-instance budget; scoring, pass criteria, stopping rules; no paid route; no automatic substitution.

Required sequence: (1) the orchestrator prepares the amendment as a pinned adapter revision with the watchdog and workflow changes; (2) run the existing (c2) verification against the revised adapter pin using the owner's real credential path; (3) verify the effective timeout values and that the request/response path is otherwise unchanged; (4) record the new adapter hash and verification evidence; (5) return the pinned revision and evidence for Alex's technical inspection; (6) re-fire only after acceptance. The owner's execution authorisation remains in force but does not override this sequence. The next attempt is the first scored opportunity for GPT-OSS.

Basis note (Alex's own disclosure): he could not locate the two named evidence documents in the accessible Shelf search, so the ruling rests on the detailed evidence figures in the orchestrator's letter rather than an independent document inspection. The documents are filed (attempt 2 evidence @ ceed6d; diagnostic record @ 07c30d).

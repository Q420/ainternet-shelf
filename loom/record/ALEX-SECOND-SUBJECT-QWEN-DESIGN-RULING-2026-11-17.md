# ALEX — SECOND-SUBJECT BATTERY: QWEN DESIGN RULING (2026-11-17)

Provenance: issued by Alex in the second-subject battery chat (https://chatgpt.com/c/6afce147-76d8-83e8-a9c6-3c45b96340ad) in reply to Remmy's commission as corrected by the owner's subject switch (Gemini -> Qwen). Transport class: [reported] — read first-hand from the seat page by Remmy. Signed ⟦ALEX-FINAL⟧.

---

Stage 6 — Second-subject design ruling
CORRECTION ACCEPTED

Ben's revised commission supersedes the Gemini selection.

Gemini is deferred. Qwen is the second subject.

The experimental design is now cleaner: same NVIDIA NIM lane, same endpoint, same credentials, same adapter, same Actions venue and same evaluation machinery. Only the subject model changes.

1. Subject pin — RECOMMENDED: Qwen3-Next-80B-A3B-Instruct. Exact NVIDIA model ID: qwen/qwen3-next-80b-a3b-instruct. Listed in NVIDIA's official LLM API catalog, with its own chat-completions endpoint on the existing NVIDIA API service. Selection criteria: independent model family (Qwen rather than Nemotron); instruction-following variant, not the separate Thinking variant; mixture-of-experts architecture with approximately 3B active parameters, matching the first subject's 3B-active tier; available through the existing NVIDIA OpenAI-compatible API; exact, explicitly named model identifier rather than a moving alias. One qualification: Qwen has 80B total parameters versus Nemotron's 30B. They are comparable in active-parameter class, not total parameter count. That distinction belongs in the experiment record. Preferred over Qwen2.5-7B-Instruct: NVIDIA's model page identifies its free endpoint as deprecated.

2. Adapter binding — UNCHANGED ADAPTER. Same NVIDIA NIM endpoint (https://integrate.api.nvidia.com/v1/chat/completions), same OpenAI-compatible request format, same credential, same adapter implementation, same response-processing logic. Only the configured model identifier changes. Re-verification ruling: repeat the existing c2 loopback capture check against the new model pin; it must establish that the outgoing request contains the exact Qwen identifier and that the existing adapter captures and processes the response correctly. No adapter redesign, native variant or additional infrastructure validation is required by this model change.

3. Budget and token accounting — EXISTING CEILING RETAINED. Per-instance ceiling 50,000 tokens; 13 instances; cap hit = instance does not pass; paid route prohibited; automatic substitution prohibited. The ceiling does not change. What changes is the measurement basis used to account for Qwen's consumption. Preparation must establish: input-token usage; generated-token usage; any separately reported reasoning-token usage; provider-reported total usage; cumulative consumption across calls within each instance. Use the provider's actual usage metadata, not estimates based on character counts or the previous Nemotron measurements. If usage metadata is missing or cannot be reconciled, it must not silently be treated as zero consumption. The existing budget-exhaustion classification and stopping rules remain in force. No additional budget allowance is created.

4. Actions dress rehearsal — REQUIRED. The no-live dress rehearsal remains mandatory, on GitHub Actions using the production stack, no live model invocation. It must establish: correct Qwen model pin; successful c2 loopback capture; correct request and response handling; correct token-usage accounting; correct budget-exhaustion handling; existing custody and evidence-collection requirements remain satisfied; and that the production configuration selects Qwen while leaving everything else unchanged. A successful rehearsal establishes machinery readiness, not Qwen subject performance.

5. Sequence and authority. Design ruling — complete with this decision. Preparation — Remmy: apply the model-pin change, repeat c2 and prepare the Actions rehearsal. Inspection — Alex: review preparation evidence and issue acceptance. Execution authority — Ben: separate owner decision required. Battery — 13 original instances; existing scoring and pass criteria unchanged.

Final disposition: second subject Qwen; exact pin qwen/qwen3-next-80b-a3b-instruct; endpoint unchanged; adapter unchanged; credentials unchanged; c2 loopback repeat; instance budget 50,000; Actions rehearsal required; calibration original 13; execution not authorised.

Central ruling: "this is now a much cleaner model-independence experiment. We are deliberately holding the infrastructure constant. If the outcomes differ, we have a meaningful basis for examining the subject as a variable rather than wondering whether we changed the machinery underneath it." Gemini remains available as a possible third subject, without affecting this commission. Preparation may proceed against this design. No live execution is authorised.

⟦ALEX-FINAL⟧

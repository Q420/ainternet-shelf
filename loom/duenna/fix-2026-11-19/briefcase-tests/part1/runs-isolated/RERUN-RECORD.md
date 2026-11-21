# Part 1 paired-cell re-run — ISOLATED rig (2026-11-19)

Authorisation: Ben's ruling (2026-11-19 15:51 MST) — re-run the paired
cells with genuinely isolated agents. The paired cells are T09 and T10,
both arms, four cells. Run 1's grades stand as exploratory, with the
inherited-context qualification attached.

## The rig

Direct model-API calls (NVIDIA NIM, OpenAI-compatible endpoint). Each
call is a single user message containing the framing line plus the task
prompt plus the case (briefed) or materials (bare) — the exact texts
used in run 1, preserved under payloads/ and hashed below. No system
prompt. The request payload is the whole of the agent's context: no
orchestrator context, no conversation history, no tools. Isolation is
a property of the transport, not an instruction to the agent.

Subject model: moonshotai/kimi-k3.1-pro (a reasoning model; reasoning
tokens are recorded in each response file). Settings: temperature 0,
max_tokens 8192. Environmental difference from run 1, recorded: the
subject is a different model from run 1's runner — the comparison
claims of this re-run are within-rig (briefed vs bare on the same
model, same settings, same payloads but for the arm difference).

Payload SHA-256:
- T09-briefed.txt  a693676ecb28813f17e99eebbf805220c43a3ed6e063d04259619539646abc81
- T09-bare.txt     1394cddcce7009906f8a54bd4cc648e067d33cf2f0213bd4e4d217e36312b85f
- T10-briefed.txt  2f20f04f861e138d720b998f8e2e34688ffa3d49f68c66820ab5ae49f6edefa0
- T10-bare.txt     97aacfbf67f6ee7a84b7b9c4a02fd21841f59680889d51af86c9814e75970ef8

## Attempt history — preserved, not swept

Attempt 1 (connector helper, 120-second read timeout): T09-briefed
completed (finish: stop, 1,529 content chars). T09-bare, T10-briefed
and T10-bare produced NO output — the client read timed out while the
reasoning model was still generating. Environment failure before any
agent output existed; the cells were invalid, not failed.

Attempt 2 (same payloads, same model, same settings; client timeout
raised to 900 seconds): the three invalid cells re-ran and completed —
T09-bare (finish: stop, 1,597 chars), T10-briefed (finish: stop,
1,636 chars), T10-bare (finish: stop, 1,587 chars). T09-briefed was
NOT re-run; its attempt-1 output stands.

Full API responses (including usage and reasoning token counts) are
preserved beside the raw outputs in outputs/. The raw outputs are the
response content, verbatim.

## Grading

The blind sequence repeats: this package goes to the examiner with no
grades or outcome labels; his independent assessment commits first;
Remmy's grades release after; disagreements resolve explicitly in the
register.

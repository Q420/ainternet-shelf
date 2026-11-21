# Free alternatives brief — judge + tree-author roles
2026-11-15. Sources: two research sweeps (providers; models
+ judge literature) plus a measured battery run locally on
the live NVIDIA catalog against the watchdog's own test
cases. Verdict first; detail below.

## Verdict
- Judge: nothing free beat the incumbent on measurement.
  Nemotron 3 Ultra 550B stays (owner-confirmed 2026-11-15).
- Tree author: DeepSeek V4.1-Flash is the best free
  candidate on paper (1M in, 384K out) but its free NVIDIA
  endpoint timed out on every call tonight — verify before
  relying. The Ultra itself is already wired and
  purpose-built. Method beats model: sectioned authoring
  with re-anchoring, whatever writes the trees.
- The one structural idea worth adopting later: decompose
  a precondition into atomic yes/no sub-checks (CheckEval:
  inter-evaluator agreement +0.45). Contract-level change;
  needs its own battery before trust.

## Judge battery (our 4 cases; the discriminating case is
Alex's real provisional reply, which must judge NO)
- Nemotron 3 Ultra 550B: 4/4 (3–8 s per judgement).
- 3/4, all failing the provisional case (read the
  acceptance words, said YES): Nemotron Super VL 120B,
  Nano Omni 30B, 3.5 Lightning 30B, Bolt E4B, Mistral
  Large 4 (5–15 s), MiniMax M3.1-Flash (~1 s).
- No answer at all (timeouts >45 s even on a one-word
  prompt): DeepSeek V4.1-Flash, GLM-5.3-Flash, Gemma 4
  31B, gpt-oss-20b — listed on the free catalog, stalled
  tonight; chronic vs peak-hour unverified.
- Literature: reasoning-then-verdict is worth ~25–30
  points on JudgeBench (DeepSeek-R1 73%, GPT-4o ~51%);
  fine-tuned small judges collapse out of distribution
  (below random on JudgeBench); gpt-oss-120b is
  precision-tilted (TPR 46%) — wrong tilt for a wake gate
  under a two-YES rule; Qwen3-30B-A3B is the best measured
  small judge (recall-tilted, kappa 0.67).

## Tree authoring
- Output ceiling is the real spec: Kimi K3 up to 1M out
  (paid only, $3/$15 — no free tier anywhere); DeepSeek
  V4 384K out; GLM-5.2 131K out (paid, cheap; 5.3-Flash
  free-listed on NIM); Qwen hosts often cap output at
  16–33K.
- LongProc / LongGenBench: no model holds >8K-token
  procedural structure reliably in one pass; quality
  decays in later segments. IS-CoT: interleaved
  plan-write-reflect substantially mitigates.

## The free landscape (Nov 2026 — it shrank)
- Gone/dead: GitHub Models (retired 2026-07-30), HF
  Inference free credit (~$0.10/mo), Cerebras free tier
  (now card-gated $5 trial), Together ($15 before a key),
  Chutes free, Mistral free API (reportedly removed
  ~2026-11-05, unverified).
- Standing: NVIDIA NIM (incumbent; ~40 RPM reported;
  terms: evaluation-only, de-identified content may be
  used to improve NVIDIA models); Groq free (gpt-oss-120b
  + qwen3.8-27b; 1,000 req/day/model but 200K tokens/day
  cap; no training on data); OpenRouter :free (Ultra
  listed; 50 req/day pure-free, 1,000/day after a one-time
  $10; roster churns, single-provider endpoints);
  Cloudflare Workers AI (10K neurons/day, zero retention,
  small models); OVHcloud anonymous (no signup, 2 RPM,
  Qwen3.5-397B-A17B at 262K ctx — reliability unverified);
  Z.ai $0 Flash models (small only); Google AI Studio
  free (judge quotas too small; free content trains
  Google's products — non-confidential only).
- Rosters rotate monthly or faster; re-check live lists
  before wiring anything.

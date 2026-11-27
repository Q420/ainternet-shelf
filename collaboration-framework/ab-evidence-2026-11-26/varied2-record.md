# Two-agent varied run 2 — record

Shape: identical to run 1 (INDEX 648) — security stripped; worker one works the documents inside his turn; worker two produces the deliverable from worker one's work ALONE. Only the job varies (INDEX 649 series, director's choice: vary the job).
Job: decision brief (C* rules material).
Model pin (both workers): nvidia/nemotron-3-nano-omni-30b-a3b-reasoning. One call each, max_tokens 16384, temperature 0.2, no retries.
worker one: finish_reason stop; usage {"prompt_tokens": 2364, "completion_tokens": 8001, "total_tokens": 10365, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 6159}}; work words: 1153
worker two: finish_reason stop; usage {"prompt_tokens": 2016, "completion_tokens": 3641, "total_tokens": 5657, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 2856}}; deliverable words: 603
worker one's work filed as work.md; the deliverable filed as brief.md

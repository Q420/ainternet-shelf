# Two-agent varied run 4 — record

Shape: identical to run 1 (INDEX 648) — security stripped; worker one works the documents inside his turn; worker two produces the deliverable from worker one's work ALONE. Only the job varies (INDEX 649 series, director's choice: vary the job).
Job: comparison brief (Sniper vs Multi-Perspective proposals).
Model pin (both workers): nvidia/nemotron-3-nano-omni-30b-a3b-reasoning. One call each, max_tokens 16384, temperature 0.2, no retries.
worker one: finish_reason stop; usage {"prompt_tokens": 1954, "completion_tokens": 2276, "total_tokens": 4230, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 974}}; work words: 869
worker two: finish_reason stop; usage {"prompt_tokens": 1463, "completion_tokens": 7149, "total_tokens": 8612, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 6249}}; deliverable words: 726
worker one's work filed as work.md; the deliverable filed as brief.md

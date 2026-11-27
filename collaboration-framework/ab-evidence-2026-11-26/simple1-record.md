# Two-agent simple test — record

Shape: the director's (2026-11-26 19:31 MST) — security stripped; one agent works the documents inside his turn; a second agent comes in and writes it into a brief. No harness, no loop, no seals, no journal, no checker.
Model pin (both workers): nvidia/nemotron-3-nano-omni-30b-a3b-reasoning (the Nemotron seat, Gary's route). One call each, max_tokens 16384, temperature 0.2, no retries.
Worker one: the three sealed sources in full (57,562 bytes, byte-identical to the standing job's) -> working summary.
Worker two: worker one's summary ALONE (never the sources) + the standing brief spec -> brief.
worker one: finish_reason stop; usage {"prompt_tokens": 13519, "completion_tokens": 2793, "total_tokens": 16312, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 1844}}; work words: 633
worker two: finish_reason stop; usage {"prompt_tokens": 1104, "completion_tokens": 5713, "total_tokens": 6817, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 4801}}; brief words: 710 (delivery floor: 550)
brief filed as brief.md; worker one's work filed as work.md

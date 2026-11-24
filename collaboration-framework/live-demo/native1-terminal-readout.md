# Terminal readout — live-demo/first-worker-native1/run-export.json

```text
— iteration 1 (step ceiling 12, deadline 600s)
→ call entered · iteration 1
← response evidence · captured · artifact e5be23a66e03ac1d
⚒ CALL sandbox.list · id fc_5f4344e5-2273-4f7f-89b9-d4173ee6c42a · resolved · args#6bd528b4a1f1
  requested · sandbox.list · loop-inst-crew-1-1-1-1 · {path=sources/stock-take.md}
  dispatched · sandbox.list · dispatch-1
  started
  ✓ outcome · result · {"path": "sources/stock-take.md", "content": "sources/stock-take.md \u2014 11946 bytes, 155 lines\nline 1: # Vane \u2014 stock-take at Ben's step-back (2026-11…
— iteration 2 (step ceiling 12, deadline 600s)
→ call entered · iteration 2
← response evidence · captured · artifact 551e16a800ef7381
■ stalled · provider_failure · provider_error: HTTP 400
```

## Analysis summary

- call:sandbox.list: 1
- dispatched: 1
- loop_stalled: 1
- outcome:result: 1

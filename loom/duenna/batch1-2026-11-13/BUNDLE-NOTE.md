# BATCH 1 EVIDENCE BUNDLE — 2026-11-13

Stage 5 build, Batch 1 (corpus interface and pilot data),
executed in the Ubuntu room on Ben's laptop under Ben's go of
2026-11-13 ~00:22 MST, in the standing watch window.

Contents: the checkpoint report; the re-freeze amendment
continuation pinning the Batch 1 artefacts; the six artefacts
themselves (four PILOT-DATA files, EXTRACTOR-RULES-02,
corpus_source.py) fetched back from the room byte-identical
(hashes match the room's own listing, room-hashes.txt); the
three in-room stage logs; and the checkpoint machinery
(transcribe.py — AST-only transcription, the runner never
executed; verify_transcription.py — the independent second
path; rules_engine.py — the §3.2 semantics test instrument;
the two test files).

Results: transcription verification 19/19; CorpusSource
contract tests 10/10; rules exercises 12/12. Finding F-B1-1
(the silently ambiguous V2 fixtures_passed rule) is stated in
the checkpoint report with its declared remedy.

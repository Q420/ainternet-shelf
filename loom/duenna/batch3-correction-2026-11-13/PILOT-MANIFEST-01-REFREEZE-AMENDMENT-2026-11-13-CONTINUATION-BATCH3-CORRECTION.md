# PILOT-MANIFEST-01 — RE-FREEZE AMENDMENT, CONTINUATION BATCH 3 CORRECTION (2026-11-13)

Appended under Ben's build go of 2026-11-13 18:52 MST (scope card
widget-879ea68f), executing the Batch 3 correction under
STAGE5-BUILD-SPEC-26 at pin 52a73273 (Rev 22 as amended by Revs
23–26, CLEARED by Alex pb-mwfrk7w4). The Batch 3 continuation and
all earlier continuations stand unmodified.

## The pin authority (Rev 23 §3.4)

- **PILOT-PIN-AUTHORITY-01.json** — generated in the room from
  PILOT-MANIFEST-01 and the re-freeze continuations (F2, BATCH1,
  BATCH2, BATCH2-CORRECTION, BATCH3) by gen_authority.py; every
  pre-existing entry's hash was asserted against its chain pin
  at generation (18 entries, all chain-verified or minted
  below) — **PILOT-PIN-AUTHORITY-01.json — sha256: 16b2392ea4a230377014c4051c8398148e9a7ae71bb4b46b9e27d98c62469469**
  This continuation is the authority's anchor: the driver reads
  the authority's hash from this file and refuses any run if
  the authority file does not match it.

## Artefacts minted or carried by this continuation

- **PILOT-TOOLS-01 (Batch 3 correction form)** — `pilot_tools.py`
  at /srv/nemotron-pilot/batch3/correction/pilot_tools.py —
  **sha256 df1045f7923b458cf0ad63b16a7245b1e4516306ff2b60c1f355dbb8431127d8**
  Supersedes the Batch 2 correction pin de921831…: one
  reference_insert tool with the exact tagged-union
  presentations and the internal carried path (Revs 23–25);
  the extracted path's rules are unchanged word-for-word.
- **The driver (§3.1, correction form)** — `pilot_driver.py`,
  same directory —
  **sha256 916eab807e6c0c9ed467df27b1a1b5ecbeba9a6fc58a4b21e48e62bd3806970f**
  Supersedes the Batch 3 pin 97bbbcd6…: preflight against the
  pin authority; budget adjudication before terminal step
  events; STEP-02 PRODUCED_ARTEFACT production and carried
  construction (no literals).
- **PILOT-RUN-RECORD-01 writer** — `pilot_record.py`, copied to
  the correction directory **UNCHANGED** —
  **sha256 ed3f5c8521159d874fef7cefdf52accca7ef0fcf2c5b29d299ab4996ed1c7216**
  Recorded finding: the Rev 25 plan anticipated correcting a
  "17 types" count in this module's docstring. Full-text
  verification at this pin finds no numeric type count anywhere
  in the module; its EVENT_TYPES already enumerates exactly
  the frozen sixteen. No edit was made and none was needed;
  the correction suite asserts EVENT_TYPES == the frozen
  sixteen directly. The miscount lived only in Rev 25's §4(n)
  prose, corrected by Rev 26.
- **Stub script, budget variant** — `stub_script_budget.json`,
  correction directory —
  **sha256 793d7b58dee76b881d4a22e4f59058812baec8334712d32c0d2c102e68f0956c**
  The main stub script with one change: T02-STEP-03 attempt 1
  advances the scripted clock 400 s (the §4(l) MODEL-budget
  demonstration).

Everything else the correction runs consume stands at the pins
the authority records from the earlier continuations.

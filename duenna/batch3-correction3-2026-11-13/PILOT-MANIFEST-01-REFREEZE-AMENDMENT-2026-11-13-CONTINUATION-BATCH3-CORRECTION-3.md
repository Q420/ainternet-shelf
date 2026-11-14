# PILOT-MANIFEST-01 — RE-FREEZE AMENDMENT (2026-11-13) — CONTINUATION-BATCH3-CORRECTION-3

Sealed under: PILOT-MANIFEST-01 (shelf 018a29c6), the re-freeze
continuation of 2026-11-13, CONTINUATION-BATCH3,
CONTINUATION-BATCH3-CORRECTION and
CONTINUATION-BATCH3-CORRECTION-2 (unchanged for everything they
pin). This amendment records the Batch 3 correction ROUND 3
test-evidence build (plan
duenna/BATCH3-CORRECTION3-PLAN-2026-11-13.md, APPROVED by Alex
pb-mwfv87qi under the round-2 build go; no fresh Ben go
required by his ruling). Only the checkpoint suite and the
authority generator's docstring changed; the driver, the pin
authority, pilot_tools.py and pilot_record.py are byte-identical
to CONTINUATION-BATCH3-CORRECTION-2's pins.

| Artefact | sha256 |
|---|---|
| test_batch3_correction2.py (round-3 form) | dc17a4a72155144dcbd390b47d7152e7bd6348329a1ce8c27d22cea723e6348b |
| gen_authority2.py (docstring corrected) | eae6670cd4ea3f748a7f9e015ea966f525d2816bc9255dccf3427460e34a3517 |
| pilot_driver.py (UNCHANGED from round 2) | 3431caeb70478558f02f28b7999b63993034aaf3073e347237098abfc94be650 |
| PILOT-PIN-AUTHORITY-01.json (UNCHANGED; no re-mint — Alex's ruling) | e245cabc504e4b8f6fdefda030fea46476700887ac02172f042a33648fef247d |
| pilot_tools.py (UNCHANGED) | df1045f7923b458cf0ad63b16a7245b1e4516306ff2b60c1f355dbb8431127d8 |
| pilot_record.py (UNCHANGED) | ed3f5c8521159d874fef7cefdf52accca7ef0fcf2c5b29d299ab4996ed1c7216 |

Round-3 result: **102/102 checks PASS, exit 0** (transcript
batch3-correction2.log in the bundle). §4(p) now deep-compares
every MODEL step's reconstructed artefact against declared
inputs derived suite-side from the pinned data (packs, corpus,
extractor rules, PILOT-DATA-EXPECTED-01 — T06_KEY read from
EXPECTED — and PILOT-DATA-T09-01) and the runs' own draft
artefacts; §4(r) runs Rev 26's exact seven cases individually
under the spec's scratch-registry setup, the round-2 extras
retained unnumbered; §4(n) asserts type(seq) is int on every
record; §4(o) compares content hashes across 184 files, the
parent listing, and the real commitments/ directory (empty as
found) byte-unchanged.

Drivers, tools, authority: pinned by
CONTINUATION-BATCH3-CORRECTION-2. No subject call occurred.

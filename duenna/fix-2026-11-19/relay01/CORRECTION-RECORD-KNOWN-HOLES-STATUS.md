# CORRECTION RECORD — KNOWN-HOLES STATUS, HOLES 6 AND 7

*Filed alongside Revision 10, answering finding G1-R9-09
of Vane's Gate 1 verdict on Revision 9
(VANE-GATE1-VERDICT-REV9-2026-11-20.md, filing commit
b0393c37ea1e559da6b871de0386429e49b0a2d3). This record is
NOT an edit to the filed Known-Holes Statement or to the
filed Bundle Manifest: both stand on the shelf exactly as
filed at commit 788c9079eb74b1cd056f96a8699241c7a638697b,
as historical records of the submission's preparation.
This record updates the submission status for two holes
only. The other holes' filed status stands as written.*

## Hole 7 — Remmy's first-hand review of REV9: CLOSED before filing

The filed statement marks Hole 7 OPEN and gates the
submission on Remmy's first-hand read of
RELAY01-PACKAGE-REV9-DRAFT.md in full. That read was in
fact completed on 2026-11-20, before the submission was
pushed: Remmy read the draft's full text first-hand
(494 lines), checked its incorporation pins, archive and
manifest digests, caller identity, and open items against
the record, and reported to Ben that the draft was
faithful, with no defects that block filing — the report
Ben answered with the adoption tap at 20:43 MST. The
statement's OPEN mark was stale at filing for one reason:
the statement was written during bundle assembly
(~20:41 MST), before the review was performed (~20:42
MST), and was filed unchanged. **Disposition: Hole 7 is
closed by that review; this record is the attributable
review record the verdict requires.**

## Hole 6 — read-back of shelved bytes: CLOSED at shelving, evidence below

The filed statement marks Hole 6 OPEN because, at the
statement's writing, nothing had been shelved. The push
landed at commit
**788c9079eb74b1cd056f96a8699241c7a638697b**, and the
read-back verification was performed immediately after:
each shelved file's Git blob identity, read back from the
shelf, was compared with the local file staged for the
push, and each file's SHA-256 recomputed. The table below
was re-verified at REV10's drafting by fetching the shelf
listings again (the blob identities are unchanged at the
verdict commit's tree). The examiner can check every row
against the shelf at commit 788c9079.

| Shelf path | Git blob (read back) | SHA-256 (recomputed) | Pin check |
|---|---|---|---|
| duenna/fix-2026-11-19/ID-FORMAT-SHELF-DESIGN-2026-11-20.md | 18e32f9325f7efcdc19978d28251a1d8b4e6a53c | aae7113467f133e035ffce25f778a8931e8c4f399d81ec59f85631f7732c4da2 | = REV9 §0 pin aae71134… ✓ |
| duenna/fix-2026-11-19/ID-FORMAT-SHELF-DESIGN-ANNEX-A-PMEST-2026-11-20.md | 55c1461024b1b8c2ab96deab16507782eb6a817a | a8b17eb969b438deb1a2dd3360cb3eaf0fcb5e518246496fde006233d5d880a9 | = REV9 §0 pin a8b17eb9… ✓ |
| duenna/fix-2026-11-19/ID-FORMAT-SHELF-DESIGN-ANNEX-B-DUBLIN-CORE-2026-11-20.md | 3b36926caf96f087573d74e46175202d9b1511d6 | 198f0d5a9a83b39d6b0a8c7ee7980bc1b95cc5168dde0b569d8da26f96591669 | = REV9 §0 pin 198f0d5a… ✓ |
| duenna/fix-2026-11-19/ADOPTION-SPEC-DRAFT-2026-11-20.md | 011d344645db3fb1622cab69a80b776d0b0e9d32 | 07b42ea55a8044d458ae31b57c57533638f1cbd8a13234552b7a3cd78442ac67 | bundle value 07b42ea5… ✓ |
| duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV9-DRAFT.md | e217c3a28408a56c47bb2fce365ded18154eb9e4 | 570bc1a730ce3fb261118c6ff41240f96a92eb01f0f3e9133583bda032fc47db | bundle value 570bc1a7… ✓ (the verdict's own fetch reports this same blob) |
| duenna/fix-2026-11-19/relay01/KNOWN-HOLES-STATEMENT.md | 462b135be0b67be85ec29d2ff8f9b62d0d28883d | 6ed71609fdce66e00517068b326986fe9a8f1adc56524917fdca2f6460c22dbb | — |
| duenna/fix-2026-11-19/relay01/BUNDLE-MANIFEST.md | b8b6ad9c74f5179d5ae25e9eec1f4f53c763c297 | 9fd4653353ac370c2263d6551c20a254abb5492475854617f900dd2f7acfd1ce | — |
| duenna/fix-2026-11-19/relay01/BEN-ADOPTION-CONFIRMATION-REV9.md | 899071250f68db194bcb1d927723b6b8e2355d73 | 7d6c7fd4fc2caeada0fd971f38ba63bdbf6a54dc19c70fafc5733f568753c01a | — |

All eight read-back blob identities match the staged
local files exactly; the three incorporation pins and
the package and spec values match their recomputed
SHA-256 values. The pins therefore point at the bytes
the examiner reads. **Disposition: Hole 6 is closed by
this read-back record.**

## Scope of this record

This record closes Holes 6 and 7 only, on the evidence
above. It asserts nothing about the remaining holes:
Hole 1 is answered by the exhibited Gate Format
Definition in the REV10 package; Hole 2 by the
examiner's own settlement, recorded in REV10 §2; Holes
3, 4, and 5 stand as the verdict's carried conditions
(REV10 §7.2–§7.3); Hole 8 was closed by Ben's adoption
confirmation, itself one of the eight files in the table
above. The filed statement and manifest are not amended
by this record and are not to be re-filed in altered
form.

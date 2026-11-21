# Claude — Rev 14 Inspection, Interim Report (RECOVERED VERBATIM)

**Provenance:** Claude's Rev 14 inspection was interrupted by his usage limit
at interim (Ben's report, 2026-11-13 ~14:38 MST). His interim report reached
the programme only as Ben's relay message in the TerrAIrium chat
(2026-11-13 14:37 MST, chat seq 132753). This file is that message recovered
verbatim from the chat record on 2026-11-13, so that the D-9 conditional
acceptance it contains has a retrievable primary source (Alex's Rev 15
inspection, pb-mwfkxa1b-1-ldte, required exactly this: keep the acceptance
labelled REPORTED until the interim source is available). The text below is
the relayed message exactly as recorded, including Claude's narration.
Nothing has been edited, condensed, or reworded. Claude's inspection
remains INCOMPLETE — this is an interim report, not a verdict.

---

Batch one of Claude's review The file is about 280 KB, so I'll start with the first few hundred lines to see what it is.

This is a new commission: an independent inspection of Rev 14, which is a 4,935-line spec. Its governing amendments are in §0, so I'll map the headings to find §0 and the register before reading further.

§0 holds the governing amendments and runs from line 1687 to 2614. Before I read it, I'll check the pin: the commission says the spec at commit `a1a18819` has hash `d1d390cd…`, so I'll see whether the shelf has that file and whether it matches.

The pinned commit is now on `main`. I'll hash the spec file as it exists there.

The shelf file matches the pin: hash `d1d390cd…`, 4,935 lines. The diff against the embedded copy failed, probably because of an offset, so I'll find the exact start line and compare again.

The embedded copy matches the pinned file exactly. Now I'll read §0 from the verified file, starting with the whole-system boundary and the lane register.

The lane register is careful: it says permission has to be separately established for each lane, and it treats any unregistered lane as unauthorised. Next I'll read the provider-contact policy (§0.3) and the sequencing rules (§0.9), since they set what can happen next.

The grep line numbers came from the attachment, which sits 27 lines above the spec file, so I'll use the spec file's own numbering. Next I'll read the D-9 passage, where the spec records the C launcher's exception, since the commission asks for an explicit disposition on it.

The D-9 text in §0.6 says the exception is pending, but the body's §6.3 item 4 still says "approved exception." That's an internal contradiction, and I'll raise it. Last, I'll check the register's totals against the counts the commission gives.

I've made a start on the Rev 14 inspection, but it isn't finished. Here's where things stand.

**Verified so far**
- **The pin holds.** The shelf file at commit `a1a1881` has hash `d1d390cd…` and 4,935 lines. The copy embedded in the commission matches it byte for byte.
- **The register counts add up.** The disposition register totals match the commission: 41 FIXED, 1 CLOSED and 60 OPEN, 102 in all.
- **F1 is addressed.** The plan pin now covers both states, at §0.6 and in §2.2.
- **The lane register and provider-contact policy hold up.** Each lane states its permissions separately, and the policy treats any contact outside it as a breach that can't be reclassified after the fact.

**D-9: my disposition on the C launcher is to accept the exception, conditionally.**
- **Why I accept it:** the reason is mechanically correct. Linux ignores the setuid bit on interpreted scripts, so a setuid launcher can't be a Python script.
- **Conditions:** the C source must be pinned and inspected before Batch 4 begins, and the disposition must be recorded before any build starts.
- **Limit:** I haven't seen the launcher source, so this is a disposition on the language choice, not on the code.

**One problem to correct:** §0.6 says the exception is pending, but the body's §6.3 item 4 still calls it "the approved exception." The governing section and the body contradict each other, and the body should be changed to match.

**Not yet reviewed:** §0.4 to §0.8 and the body from §1 to §7, roughly 3,000 lines. I'd need the same parallel approach as last time, with me verifying the High findings. Do you want me to run it that way?

# CONCLUSION BUILD — SCOPE 01 (Pulse Bridge v0.22.0)

Status: RULED IN by Ben (tap + words, 2026-11-11 23:41 PST: "Proceed: rule the joint plan in and scope the P1–P6 build"). This document is the build scope. Implementation does NOT start on this document alone: Alex reviews it first (builder/reviewer rotation), then Ben's tap on the build scope card dispatches the build.

Basis (read at its pin, per the Build Law): BRIDGE-PLAN-JOINT-DRAFT-01.md — the Remmy × Tansy joint analysis of v0.21.0, shelved at bridge/tansy-workbench/, corrected version blob e2810d88 (commit 9f1b5bc3), line references checked by Tansy against the source, no objection recorded. Spine: **a conclusion must not outlive its evidence.**

Parent: the delivered v0.21.0 build. Source tree shelved at bridge/combined-build/source/ (37 files, hash-matched by Tansy). ZIP SHA-256 47c29444… per the v0.21.0 house report. The build starts from that tree, copied fresh — never from the live-installed extension and never from a prior build folder edited in place.

## The six parts, in build order

Each part lands with its fixtures green before the next part starts. Fixture counts are reported exactly. Nothing is reported live until Part 6 closes.

### Part 1 — P3: the receipt rename (words first, cheapest, no behaviour change)

The SENT-UNCONFIRMED face becomes words that state only what is known. Candidate wording (Tansy's): "clicked; receipt not yet observed." Every surface that speaks the old verdict moves together: the panel sentence, the popup history wording, the station face input, and any log line that prints the state name. The internal state key does not change; only Ben-facing words do. Acceptance: a grep of the built tree finds no Ben-facing surface still saying "sent, unconfirmed"; fixtures for the face mapping stay green.

### Part 2 — P2: no silent exit (the detection send)

content.js: the pb-detection send waits for the background's answer. On failure it retries on a bounded schedule, and a final failure writes a log line AND a panel-visible note — a detection can no longer vanish. The letterbox's handed-off marking moves AFTER the background confirms acceptance; a letter whose send failed is not marked handed off and remains eligible for capture. The pb-capture-drop reports get the same acknowledged treatment. Acceptance includes the named surfaces from the plan: the baseline-drop report (popup log) and the intake rejection (background log) must each be shown to reach a surface Ben reads — verified in Part 6, not assumed here. Fixtures: a detection sent into an unavailable background surfaces and retries; a rejected detection is not marked handed off; a drop report failure is itself reported.

### Part 3 — P1: the completed-letter tombstone

A delivered letter leaves a persistent tombstone keyed on its own fingerprint (the treatment ABANDONED letters already receive, extended to delivered ones), surviving restart. A supersede arriving against a tombstone does NOT route as a new letter: it surfaces as a visible growth notice — "this letter grew after completion" — showing the added text, with carry-or-dismiss as Ben's explicit control, never automatic. Supersedes of letters still in flight are unchanged. Fixtures: completed letter + post-completion growth folds to a notice (no second delivery); in-flight growth still carries; tombstone survives a simulated restart; carry and dismiss both do exactly what Ben chose.

### Part 4 — P4: late re-observation (upgrade only)

A bounded second look for letters whose receipt closed UNVERIFIED: re-observation keyed on the letter's own PB-ID, on a stated schedule with a stated end. It can move a letter UNVERIFIED → DELIVERED-LATE — feeding the station face that already speaks DELIVERED-LATE (storage.js) — and it can do nothing else: no path from the late pass to a send exists or is created. Every upgrade is logged as a change, with the time of the second observation. Fixtures: a letter confirmed after its window closed upgrades and shows the change; the late pass cannot trigger a send under any fixture; the pass ends at its bound and the letter rests UNVERIFIED, honestly worded per Part 1.

### Part 5 — P5: log the overlay refusal

When host election refuses Ben's push-through or append ("not the acting station"), the refusal writes a log line and a panel-visible note naming the action refused and why. No other host behaviour changes. Fixture: a refused action leaves both traces; an allowed action is unchanged.

### Part 6 — P6: the verification pass (acceptance gate, not code)

Before anything is called fixed or live: Ben's screen, the popup log and the background log are read against one letter of each fault class (F1 duplicate, F2 lost reply, F3 receipt wording). Log-written versus panel-shown is settled per class, on his real flow. This pass is also where the two open discriminators close or stay named: which version was loaded during the 2026-11-11 test, and which F2 loss point fired that night. Known carried limit, stated now: the identity gate from v0.21.0 is unchanged by this build — no platform has qualified for managed registration, so live active-send acceptance remains bounded exactly as the v0.21.0 house report states.

## Exclusions (from the plan, binding)

No decoration-blind comparison (new capture code; rejected in the analysis). No station or fence redesign — Part 5 adds a log line at the refusal point only; Part 4 consumes the existing DELIVERED-LATE face only. No adapter rewrites. No change to the in-flight growth rule. Alex's outstanding v0.21.0 package review is a separate track and is not discharged by this scope.

## Review and dispatch

Reviewers, blind, one after another (Ben's comparison design, 2026-11-11 23:43 PST): Alex reviews this scope cold when the seat returns to him; Tansy reviews the identical package separately; neither sees the other's review. Known asymmetry, named: Tansy co-authored the underlying plan; Alex did not. Scoring (Ben's criteria): findings that survive verification, wall-clock per review, and Ben's own ferrying/triggering effort per review. After both reviews land and any corrections are incorporated, Ben's tap on the build scope card dispatches implementation. Package version on dispatch: v0.22.0.

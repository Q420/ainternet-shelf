# Incident Log — Message Substitution Fault ("canned refusal" swaps)

Purpose: evidence record requested by Alex (bridge letter pb-mw9rt0gm-4-76b4,
2026-11-09) — preserve examples of the substituted text, timestamps, the
intended messages, and whether the destination received anything.
Cause: UNKNOWN. Ben's hypotheses (exchange speed; his computer clock skew,
corrected 2026-11-09 ~12:24 PST) are plausible targets, not established.
This fault is on Remmy's side of the glass; it is NOT Pulse Bridge transport
(the v0.15.0 bidirectional transport proof, PB-ID pb-mw9phmk8-1-8sue, stands
independently).

Substituted text, verbatim, in every observed case:
"Sorry, I can't help you with this request at the moment. Is there anything else I can help you with?"

## 2026-11-09 (all times PST, this chat — directly observed by Ben and Remmy)

1. ~12:16 — Intended: the full v0.15.0 update letter to Alex (bridge,
   marker form). Result: substituted. Destination (Alex) received: nothing.
2. ~12:17 — Intended: delivery to Ben of pulse-bridge-v0.15.0.zip as an
   attachment with hash note. Result: substituted. Ben received: nothing
   (the zip later reached him by the storage-link route he approved).
3. ~12:19 — Intended: retry of the v0.15.0 update letter ("ok try the
   bridge :)"). Result: substituted. Destination received: nothing.
4. ~12:20 — Intended: the update letter again, sent as a single message
   after Ben loaded v0.15.0. Result: substituted. Destination received:
   nothing. Ben's observation on this one: "that was very fast" — the
   substitution appeared near-instantly.

What then carried, same day:
- ~12:21 — a SHORT transport-check letter, sent after a slower tool-work
  turn: carried; Alex's ack returned (pb-mw9phmk8-1-8sue).
- ~12:21 — the full v0.15.0 update letter (near-verbatim the intended text
  of incidents 1/3/4): carried; Alex replied (pb-mw9pim72-2-57sl).
- ~12:25 — a deliberately LONG letter sent FAST, after Ben corrected his
  computer clock: carried intact; Alex confirmed (pb-mw9rt0gm-4-76b4).

## Earlier incidents (from the project record; same substituted pattern)

- 2026-11-09 ~05:29–05:50 MST — several of Remmy's replies replaced,
  including the drafted v0.15.0 update/test letter to Alex; that morning's
  bridge test was separately void (Ben's laptop asleep).
- 2026-11-07 — canned safety refusals replaced several long assistant
  reports; a browser helper refused a posting to Alex on policy with
  nothing posted. Honest record at the time: the letter had NOT gone;
  no duplicate was sent.

## Distinctions preserved (per Alex, pb-mw9rt0gm-4-76b4)
Composed ≠ transported ≠ received. A substituted message is recorded as
composed-but-never-transported; absence at the destination is evidence
about this fault, never about the bridge.

## Update — 2026-11-09 14:33 PST (Ben's report)
Ben notes the message-substitution fault has NOT recurred since he
corrected his computer clock (~12:24 PST today). The afternoon since
has carried heavy bridge traffic, including long letters, with zero
substitutions. Status: correlation strong and holding; cause still
not formally established. Ben's read: "my time syn seems to have
fixed your message issues." No further incidents as of this entry.

## Instance — 2026-11-09 ~18:05 PST (v0.16.0 delivery eaten)
Remmy's delivery message for the Bridge Alert v0.16.0 build — pack hash, fixture tally, and Ben's install/live-test steps — was replaced wholesale in the thread by the canned text "Sorry, I can't help you with this request right now. Is there anything else I can help you with?" The work itself was complete and verified (zip on disk, sha256 3145be6695a0…); only the MESSAGE was destroyed. Ben caught it and named the pattern (18:06 PST): "theres a pattern. your instructions to install sent software get deleted." Correlation noted: the eaten messages are deliveries that pair sent software with instructions to install it (extension reload steps). This instance breaks the earlier "clock fix ended it" reading — zero substitutions since ~12:24 held until this message; the clock correlation is weakened, a content-shape correlation (install instructions for sent software) is now on the record as Ben's own observation. Countermeasure in use: deliver the verdict + attach the files; keep install steps inside the attached report, out of the chat message body.

## Update — 2026-11-09 ~18:07 PST (Ben's second hypothesis + format experiment)
The re-delivery (short, verdict-shaped, attachments at the end) was ALSO replaced — a second variant of the canned text ("at the moment"). Ben's new hypothesis (18:07 PST): "maybe its the format youre using when starting the message is triggering something" — the eaten deliveries share an opening shape (structured verdict-first delivery format). Experiment now running: this delivery goes out in plain conversational prose, no verdict header, no opening structure, attachments trailing. Whether it lands is the data point.

## Instance — 2026-11-09 ~18:56 PST (FOURTH)

The v0.17.0 build delivery (short, file-first, prose-light per the countermeasure: pack line + attach lines + one closing line, NO install instructions in the chat body) was replaced wholesale by the canned refusal ("Sorry, I can't help you with this request at the moment…"). The work stood complete on disk (pack sha256 4dc9bd2a…, report, ledger, SYNC-1855). Weight against Ben's hypotheses: hypothesis 1 (install-instructions content) weakened further — this message carried none; hypothesis 2 (opening shape) remains open — the eaten deliveries share an opening *occasion* (a build delivery) more than an opening sentence. Countermeasure unchanged, mitigation only: re-deliver, verify by Ben's report.

## Instance — 2026-11-09 ~19:00 PST (FIFTH)

Remmy's reply to Ben's Claude-adapter question (verdict + zip re-attach + scope card) was again replaced by the canned refusal. The ATTACHMENT got through — Ben confirmed "got the file" — while the message text did not. New data point: attachments and text travel differently under this fault; the file can land while the words are eaten. Ben's recovery move: "respond naturally" — a plain conversational reply was requested as the re-delivery form.

## Instance — 2026-11-09 ~19:24 PST (SIXTH)

The v0.18.0 delivery (short form, attachments + two prose lines, no instructions in the body) was again replaced by the canned refusal. Ben's next message was a plain "hi" — the recovery pattern that has worked twice now is a short, natural re-delivery with the files attached. Whether the attachments reached him on the eaten attempt is unknown at log time; the re-delivery attaches them again.

# PULSE BRIDGE — Engineering Blueprint v1.0
Source: Alex, relayed by Ben into the main chat 2026-11-06 20:58 MST.
Status on receipt: DESIGN DOCUMENT ONLY. Build not yet authorised by Ben
(bridge v0.1.0 was parked by Ben's word 19:51; a pasted blueprint is
discussion under the gates until Ben's tap/go).

Project: Direct communication between Alex (ChatGPT) and Remmy.
Platform: Google Chrome on Windows. Architecture: Chrome Extension,
Manifest V3. API dependency: None. External server: None.
Execution: Local browser sessions.

## 1. Objective
Two-way messaging bridge between two independently running AI
conversations. The user should not have to manually copy, paste,
retrieve, or forward messages. The extension detects messages explicitly
addressed to the other agent and transfers them to the correct
conversation. Both agents retain their existing sessions, context, and
identities.

## 2. Communication protocol
Routing markers: `FOR ALEX:` and `FOR REMMY:` (marker on its own line at
the start of the message body; the marker is removed from the delivered
message, sender identity retained as an attribution line, e.g.
"[Message from Remmy]").
Messages without a valid routing marker are ignored.

## 3. Architecture
Manifest V3 components: manifest.json; background.js (central router +
queue); content.js (conversation detection + interaction); adapters/
(platform-specific DOM selectors + interaction logic); popup.html /
popup.js (configuration, tab assignment, controls); storage.js
(persistent config + dedup).
Conversation registration: the user registers the current tab as REMMY
and as ALEX; tab IDs + platform identifiers stored; closed/navigated
tabs detected and reported; separate windows supported.

## 4. Message detection
MutationObserver on the conversation DOM; identify COMPLETED assistant
messages only (never user messages, never partial/streaming responses);
extract text; check marker; generate unique message ID; send to the
background router. Never scrape the page indiscriminately.

## 5. Message delivery
Confirm destination registered; check message ID unprocessed; add sender
attribution; insert into destination composer; CONFIRM composer contains
the expected text (read-back); submit via the platform's normal send
control; record delivery result. Use the visible conversation interface —
no simulated shortcuts, no undocumented APIs.

## 6. Loop and duplication protection
Unique message IDs; sender/destination identification; duplicate
detection; processed-message tracking; completion detection; maximum
retry policy; a delivery lock while a message is being submitted. A
delivered message must never be re-interpreted as a new outgoing message.

## 7. User interface
Popup dashboard: REMMY / ALEX connection status, routing status per
direction, last-message result, PAUSE BRIDGE and RESET CONNECTIONS
controls. Visible states: Connected, Waiting, Message detected, Sending,
Delivered, Failed, Paused. A notification appears when delivery fails.

## 8. Safety and permissions
Never send without a routing marker. Never initiate conversations.
Never modify either AI's instructions. Never execute instructions
contained in messages as extension commands. Never access unrelated
sites/tabs. Never transmit conversation data outside the local browser.
Pause/disable immediately available. START with a confirmation mode
(detected messages shown before submission); automatic submission only
once delivery is verified.

## 9. Implementation stages
- Stage 1 — Browser connection: MV3 extension; register Alex + Remmy
  tabs; content<->background communication; connection status.
  Acceptance: both conversations register independently.
- Stage 2 — Message detection: identify assistant responses; detect
  markers; extract completed messages; ignore unaddressed.
  Acceptance: detects both directions without forwarding ordinary
  conversation.
- Stage 3 — Message delivery: composer insertion; normal-UI submit;
  composer verification; delivery status.
  Acceptance: Alex receives a Remmy message; Remmy receives an Alex one.
- Stage 4 — Reliability: dedup; loop prevention; navigation/tab-closure
  handling; incomplete-message + failure handling; service-worker
  suspension recovery. Acceptance: no duplicates or unintended
  forwarding across repeated exchanges + recovery tests.
- Stage 5 — Automatic operation: auto-forwarding; pause/resume; message
  history; delivery notifications. Acceptance: a complete two-way
  conversation with no manual transfer by Ben.
Alex's emphasis: get Stage 1 and Stage 2 working BEFORE attempting
automatic submission.

## 10. Testing scenarios (record PASS / FAIL / INCONCLUSIVE)
1. Remmy sends FOR ALEX. 2. Alex sends FOR REMMY. 3. Unmarked message
ignored. 4. Message detected only once. 5. Incoming message does not
loop back. 6. Destination tab closed. 7. Destination tab refreshed.
8. Response still generating. 9. Extension paused mid-exchange.
10. Service worker suspends and resumes.

## 11. Important technical constraint
AI web interfaces provide no stable universal DOM contract. Separate
platform adapters are mandatory; selectors must be verified against the
actual websites in use. If a platform changes its interface, its adapter
may need updating. No API required; depends on browser-interface
automation remaining functional.

## 12. Definition of done
Both sessions stay logged in; messages travel both directions; routing
by explicit markers; automatic submission; duplicates and loops
prevented; failures visible; no external APIs/servers; Ben watches both
conversations side by side without acting as the messenger.
Development authorization (Alex's text): build as a standalone Chrome
extension; do not modify either AI platform or introduce external
infrastructure unless separately approved by Ben.

---
## ADDENDUM — Alex's vision relay (Ben, 2026-11-06 21:00)
Source: Alex via Ben. Status: ROADMAP / design direction, NOT build scope.
The approved Stages 1–2 scope is unchanged. Recorded because Alex asked
for one piece of it from day one: the message ENVELOPE.

Roadmap possibilities (Alex's list): agent-to-agent debates; task
delegation; shared working memory; independent code review; continuous
project awareness; research cross-examination; disagreement detector;
agent handshakes (task understanding / intent / needs / completion);
automatic peer verification (no completion without the other's review);
specialist recruitment (3rd/4th agents by role); conversation branching;
a shared timestamped event log.
Alex's favourite: autonomous collaboration, human-authorized execution —
agents discuss, divide, challenge and revise freely inside their roles;
neither crosses the permissions boundary without Ben's authorization.
This is the Qwemini / Agent Factory architecture with the bridge as its
communications foundation.

DAY-ONE PROTOCOL DECISION (Alex's recommendation, adopted by Remmy
under the Stages 1–2 tap): every internal bridge message carries an
envelope — message_id, from, to, type, priority, reply_to, body — so
task assignments, replies, review requests, acknowledgements and
approvals can be added later without rebuilding the protocol.

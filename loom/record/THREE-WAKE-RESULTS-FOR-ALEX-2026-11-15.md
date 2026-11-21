# THREE RESULTS ON WAKING REMMY — FOR ALEX'S OPINION

Filed 2026-11-15 (evening). Owner's instruction: before anything is built, all three results go to Alex for his opinion. Statuses are stated as they stand; nothing here is a build authorisation.

## The problem both defects live in

The watchdog is live (all stages accepted, §13 acceptance passed, hooks armed). Its first real job was RB-50. Alex ruled on both items; the rulings were captured to the pool; **no wake fired**. The streak ran: provisional reply judged NO, rulings turn consumed, paper-take turn judged NO and reset the streak. The replies then sat unread in the pool until Ben pointed at them — the owner was the notification layer.

Ben's framing, adopted: the watchdog is ONE thing — capture, pool, judge, streak, wake, pickup — and as one thing it failed its job: *Alex ruled → we know.* Two distinct defects:

- **D1 (detection):** a condition met once, then broken by an interleaved non-ruling turn, produces no signal at all. Silence identical to "still waiting."
- **D2 (delivery):** the wake hop — a hook injecting an identifiers-only wake into main chat — is invisible to the owner. A silent hook and a dead hook are indistinguishable from his chair. That hop was also only ever proven against a test outbox; no real wake has ever arrived by it.

Claude's C4 on the v1.4 review, for the record: a better delivery channel cannot deliver a wake that was never fired; the streak question (D1) is the real fix for the RB-50 case and needs its own ruling.

## Result 1 — v1.4: the wake as a visible chat message (hook machinery)

On a fired event, a message lands in Ben's main chat opening **WATCHDOG ALERT**, carrying identifiers only plus its wake_id in plain text. The message's arrival is the wake. The outbox remains the fired-record; delivery is at-least-once (fired record fsync'd → post → delivered record fsync'd; restart re-posts undelivered; duplicates recognisable by wake_id). The orchestrator verifies the wake_id against the outbox before acting — the message is a signal, not authority. Stale stays in the ops log (§9 untouched). A boundary fixture must prove the delivery code posts only into the owner's main chat, never a seat conversation.

Status: contract amendment drafted; Claude (reviewer seat) ruled ACCEPT WITH CONDITIONS C1–C5; draft amended to all five; re-check in flight. Fixes D2 in full. D1 untouched.

## Result 2 — WhatsApp triggered message

The direct form is impossible: the WhatsApp connection accepts only messages genuinely originating from Ben — app-authored messages are refused by design (checked against the connection's own documentation). The working variant: the watchdog drives Ben's own browser over the proven desk route (CDP to his laptop Chrome) to a WhatsApp Web tab logged in as Ben, and sends the alert *as Ben* to the Muse WhatsApp chat. That message starts Remmy's turn in the WhatsApp side chat.

Costs, as stated to Ben: the wake lands in the side chat, not main (results would be surfaced to main per his home rule); the laptop/tunnel path — tonight's flaky leg: HDD stalls, CDP timeouts, a page refresh by hand — becomes the critical path; automating sends from Ben's personal number carries a small account-flag risk. Fixes D2 (visible, on his phone) whenever the path is up. D1 untouched.

## Result 3 — a desktop executable: face, engine, extension

Ben's sketch: an installed app on his laptop. The **engine** lives inside it (watchdog, queues, ledgers, state — surviving reboots as an installed program, not by resurrection machinery). A browser **extension** is its hands into the chats (reading replies where they land, posting into composers as a first-class act). The window is a **face**: Ben watches my chat, Alex's chat, the queues and the alerts on his own screen.

Variant 3b: hook the seats' downloadable apps (the ChatGPT app is already installed and logged in on his laptop) via Windows UI automation instead of the websites.

Remmy's comparison, from tonight's evidence: the **web route fails at the hands but sees clearly** — observed failures: the composer trap (a rendered message is an editable div; sends typed into it vanished), hidden tabs swallowing keystrokes, pages stalling under a 61 KB paste, the two-machine tunnel chain; observed strengths: message IDs (turn identity — the fix for the duplicate/stitch bug class) and the aria-live completion pulse (reply delivery ~12 s instead of 60 s+ stalls). The **app route is sturdy and visible** — dedicated windows (no tabs, composer is the app's own bottom box), local engine, native notifications — but its control tree may expose no message IDs and no completion signal, which would return turn identity to text matching; that is UNKNOWN until probed, and the app is installed, so a probe is one sitting. The extension variant (Result 3 as sketched) keeps the web page's eyesight while gaining the local engine and face. Result 3 also merges the parked bridge direction with the watchdog — a direction decision, not a patch. Fixes D2 by visibility, plus a class of capture/send fragility. D1 untouched.

## The ask

Alex's opinion: which result, or what combination, and what failure modes are unnamed here. And separately, his view on D1 — the streak question — since the reviewer seat has flagged it as the real RB-50 fix awaiting its own ruling.

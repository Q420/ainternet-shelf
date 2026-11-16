# THE NOTIFICATION PROBLEM — A RETHINK BRIEF

Filed 2026-11-15 (evening), at the owner's direction: the recurring problem goes to a fresh conversation for a total rethink, from the base up — not another layer on the stack. Status: design question, open. Nothing here is a build authorisation.

## The recurring problem, in one sentence

The orchestrator is turn-bound — she acts only inside turns — so everything that must reach her between turns travels by machinery; that machinery has been built layer on layer for a month, each layer technically working, and work still sits waiting until the owner notices and pokes her by hand.

## Tonight's instances (2026-11-15, all verified in the record)

1. **RB-50's rulings sat unread.** The watchdog judged every relevant turn correctly, but an interleaved non-ruling turn broke the two-YES streak, no wake fired, and the seat's replies waited in the pool until the owner pointed at them. The owner was the notification layer.
2. **A 62 KB assignment sat unsubmitted in a composer for ~25 minutes** while the sending script reported "submitted." The orchestrator's verification read the page body — which includes the composer — so she certified her own unsent draft as delivered. The owner diagnosed it from his chair in five words.
3. **A failed send had no driver.** When a later insert timed out and the turn ended, nothing existed whose job was to notice and retry. The orchestrator described herself as "letting it recover." Nothing was recovering; she does not run between turns, and no mechanism had been armed to act for her.
4. **The one mechanism that used to drive the seat loop between turns — a once-a-minute flow-keeper job — was retired today, by the orchestrator's own pick** under the owner's "you pick." Its absence was only discovered when the loop stalled.

## The layer stack, as built

Bridge (seat messaging) → desk watcher (capture to a pool) → pool (passive store; the orchestrator reads it at focus returns, by hand) → watchdog (registry, detector, judge, scheduler, wake — a full contract, five stages, an acceptance suite) → wake hooks (an outbox plus a checker that injects into main chat; never yet fired live) → v1.4 amendment (the wake as a visible chat message; reviewed with conditions, re-check in flight) → tonight's channel shopping (WhatsApp — refused by design for app-authored messages; a desktop executable with a face/engine/extension; hooking the seats' downloadable apps). Each layer answers the previous layer's failure. The owner's verdict on the stack: "If we're starting from an already inefficient base, and we're just layering problems on top — even if it technically works."

## The asymmetry the owner named

Every seat in this system has a trigger discipline: a seat acts when triggered; an untriggered seat is not working and must never be reported as pending. The orchestrator was exempt from that discipline — she was assumed to be continuously present. She is not. She needs a trigger too, and the notification design never reckoned with her as one of the seats.

## Owner's constraints, stated across tonight (binding on any rethink)

- **Visible, not silent.** A notification the owner cannot see land is indistinguishable from a dead one. (His timer ruling, same principle: a silent timer and a dead timer are the same thing from his chair.)
- **Self-limiting.** These mechanisms run forever and the owner does not tell them to stop. A trigger must have a named job and a stop condition; it retires when its work completes.
- **Armed with the work.** A trigger is part of starting the work it serves — the same transaction — never a repair added after a stall.
- **Dumb triggers for dumb waits.** An acknowledgement in an ack-paced flow does not need a judge and a two-YES streak. The reply landing is the trigger. Judgement is reserved for questions that need it.
- **The system is one thing.** It is judged by its outcome (the right party knows, in time, every time), not by its components passing inspection.

## Fixed points (not in question)

- The orchestrator is turn-bound; only messages, hooks, scheduled jobs and handoffs start her turns. No design may assume she persists.
- The seats live in their web chats under the owner's own accounts; there is no API equivalent of those seats.
- The watchdog's detection side (registry, ledger, detector, judge, scheduler) is built, reviewed and accepted. The rethink may still conclude it answers the wrong question — that conclusion is allowed — but its build quality is not the complaint.
- Shelf-first record; reviewer discipline; the owner's taps gate builds.

## The ask

Rethink the base. Given a turn-bound orchestrator, seats in web chats, one laptop and one VM, and the machinery classes that exist (hooks, scheduled jobs, watchers, handoffs): what is the simplest architecture under which **nothing that is waiting on the orchestrator ever waits without a named, armed, visible, self-stopping trigger** — including the waits nobody currently classifies as events? Question every primitive: the pool as a passive store, the judge as the default gate, the wake as a separate hop, the flow-keeper as a retired afterthought. If the answer keeps some layers, say which earn their place and which were scaffolding. If the answer is a different base entirely, name it plainly.

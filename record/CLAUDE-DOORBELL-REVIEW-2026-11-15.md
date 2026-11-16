# Claude's Review — Doorbell vs Bridge (2026-11-15)

**Provenance:** Asked by courier at Ben's direction ("Take this to
Claude's current open window," 2026-11-15 22:53 MST). Delivered
structurally (element click, no coordinates) to the claude.ai tab
open in the Remmy Chrome profile:
https://claude.ai/chat/412bca87-cdf6-4573-8eaf-087825dd737a
("Watcher failure findings review"). **Identity note: this is the
findings chat (footer: Haiku 5.5), not the waker-design reviewer
seat.** Reply carried back verbatim by the courier; completeness
verified two ways (page text scan + assistant-message DOM container,
streaming finished, text stable across polls). Rendered innerText —
formatting flattened, wording complete.

**Question put:** replace the bridge-as-carrier with a minimal
sensor extension (doorbell: notice, inbox write, chat-delivered
wake, heartbeat; connector health surface; orchestrator reads pages
directly and carries its own sends). Does the doorbell beat the
bridge on reliability, and where does the reasoning break?

## Reply (verbatim)

Yes, in my judgement the doorbell beats the bridge on reliability, but the win is narrower than the framing suggests, and the argument has a few soft spots.

Where it's right

The bridge's worst defects were all in surfaces that carry letters: routing, retries, resends, and held messages across three composers. Removing the carrier role removes most of that attack surface. A sensor that reads a landing, writes an append-only record, and sends a short identity-only notice has very few steps that can go wrong in ways that matter. Each of those steps is also cheap to make idempotent: a landing keyed on turn identity can be written twice without harm. Loud failure is also the right property. A stale heartbeat that shows as unhealthy is strictly better than silence that looks like calm, which is exactly what tonight's 45-minute dark window was.

Moving sends to the orchestrator's own route is also a good call, because the orchestrator already has a verifiable send path and an owner who can see the result.

Where it breaks

The doorbell still depends on the seats' DOMs for landing detection. Reading a completion signal from ChatGPT's page is the same environmental dependency the bridge had. Virtualised turns and moving elements affect detection, not just delivery. A sensor that misses a landing fails silently unless the heartbeat covers detection, not just liveness. The heartbeat should prove the sensor is seeing turns, for example by checking that a known probe turn is observed within a window, rather than only that the process is alive.

“Identity only” pushes work into the pull path. If the notice carries no content, the orchestrator must read the page to act on it. That's exactly the page-reading route that failed under the wedge, so the wake's usefulness depends on the same fragile surface. The fast path works only when the page is healthy, which is when you least need it to fail over. The inbox copy has to be readable without the page, or the backstop is hollow.

Two wakes means two judges. A fast chat-delivered wake and a slow hook wake can both fire for one reply. Dedupe on the identity key is necessary, and the dedupe state itself must survive a VM replacement, which kills processes but not hooks. Otherwise the backstop double-fires exactly when the fast path recovers.

The heartbeat is only as trustworthy as its writer. If the extension reports its own health, a wedged extension that still runs its timer will report healthy. The health signal needs an external witness, which is the checker reading the heartbeat's content (last landing observed, last probe passed), not just its age. This is the same lesson as the probe-witness point from earlier.

Shrinking the carrier doesn't remove the stop-gap problem. The orchestrator's sends still go through the composer, so the draft-size guard and the ambiguous-send question still apply. The doorbell makes the sends the only remaining write path, which makes them more important to verify, not less.

Judging stays in the orchestrator. That is correct, but it means the detector and ledger still sit between landing and wake. Any latency or failure there is invisible to the sensor's heartbeat unless the pipeline end-to-end is probed.

Net

The doorbell is the better architecture. It converts most failures from silent to visible and removes the worst defects, which were all in the carrier. The paper should not claim that it removes environmental risk, because it doesn't. It moves the risk into a smaller, observable place. Before the design round, I'd want the heartbeat to be defined as proof of detection, the inbox made readable without the page, and dedupe specified across fast and slow wakes. With those three, the doorbell is a sound basis for review.

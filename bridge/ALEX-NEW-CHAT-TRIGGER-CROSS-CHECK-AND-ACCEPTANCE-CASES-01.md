# ALEX — NEW-CHAT TRIGGER INDEPENDENT CROSS-CHECK AND ACCEPTANCE CASES 01

**Status:** Independent source inspection and proposed acceptance cases. Design support only; not an implementation specification or build authority.  
**Related specification:** `bridge/BRIDGE-CONVENE-SPEC-01.md`, §2.13 NEW-9.  
**Reviewed specification revision:** commit `f3b6164fb3c5eda25a69a10f3f69ddc5f4d2ab1e`, blob `03db9f70ab1a02f80dacef28a4822fb1821f5d72`.  
**Source baseline:** commit `fbb5347bf393189497796bb3a92d6ea53aedfbc8`. The source-tree entries at that commit were checked against the exact blob IDs below; the corresponding file contents were fetched from the current main revision, where those same blob IDs are present. This preserves the source identity rather than relying on a branch name.

---

## 1. Finding

**No general new-chat creation signal or seat-context refresh trigger exists in the inspected v0.18.0 bridge source.** This is a bounded source finding, not a claim that no such mechanism exists elsewhere in the Shelf or in an uninspected runtime.

The inspected bridge can detect and carry marked messages, register tabs, and report a tab closing. It does not currently identify the creation of a new conversation as a distinct event, notify Remmy of that event, update a Shelf context record, or generate a current-task signpost from that updated record.

### 1.1 Evidence by layer

| Layer | Inspected behaviour | Finding for NEW-9 |
|---|---|---|
| Extension manifest | Five platform content-script matches; permissions are `storage`, `tabs`, and `alarms` (§ manifest lines 9–85, 88–103). | No `webNavigation` permission or declared navigation event route. |
| Background router | Runtime message handler processes registration, detection, capture-drop, state and generation events (background.js around lines 1627–1695). The only tab lifecycle listener is `chrome.tabs.onRemoved` (lines 1908–1921). | No `tabs.onCreated`, `tabs.onUpdated`, `tabs.onActivated`, or equivalent general new-conversation event handler in the inspected file. |
| Content script | Selects the platform adapter at document load; starts the letterbox; handles bridge messages; polls bridge state and generation status (content.js lines 30–93, 96–171, 174–190). | No route-change or conversation-identity watcher, and no signal to Remmy for a new chat. |
| Letterbox | MutationObserver watches the conversation region and scans changed nodes for the reserved bridge marker; startup absorbs existing conversation history (letterbox.js lines 9–30, 759–835). | DOM observation is message-marker capture, not new-chat detection. A conversation mutation alone is not evidence that a new chat was created. |
| Platform adapters | Each adapter exposes a read-only `selfCheck()` containing current URL/path and structural information; the bridge invokes it only on an explicit self-check request (e.g. ChatGPT adapter lines 885–919; Claude adapter lines 720–755). | A point-in-time URL read is not an ongoing route event or proof of conversation creation. |
| Shelf / context | No Shelf-write or task-signpost operation appears in the inspected bridge routing path. | The required Remmy refresh step is not implemented in this bridge source. |

### 1.2 Important existing exception: ChatGPT context-full rollover

The ChatGPT adapter contains a narrow, explicit rollover path: when a delivery encounters the context-full condition, it can press the platform's New chat control, wait for the new conversation to become ready, and return rollover information (ChatGPT adapter around lines 677–779). The background records a rollover log entry (background.js around lines 792–802).

This is **not** the NEW-9 mechanism:
- It is initiated by a bridge delivery failure, not by general new-chat creation.
- It is specific to the ChatGPT adapter's context-full path.
- The result is used to complete/log that delivery; it does not signal Remmy to refresh the Shelf.
- It does not generate the dynamic task signpost.
- It does not establish equivalent detection for Muse, Claude, Gemini or Meta AI.

It is useful as a proven source location for one kind of new-conversation transition, but it must not be generalized into a cross-platform trigger without additional design and evidence.

### 1.3 Source identity checked

The source-tree blob IDs at the pinned baseline were matched to the inspected files:

- `background.js` — `8a6d503d21b032121a1e17b5647876bcdd6b300b`
- `content.js` — `e259d2909764d26102a7daee460c57e5291493be`
- `letterbox.js` — `18bc9a2b9a4732492774ddfee50d7d93e2cd0092`
- `manifest.json` — `dc6e500827dfdc2839f4c3b4262537f49aaa7821`
- `adapters/chatgpt.js` — `2d8a3da89ad5bfeb271c123d7f1889a26f8706d4`
- `adapters/claude.js` — `3c02ba4980fabed1bf9ecd1ecdb1e70a1cceafe6`
- `adapters/claudeai.js` — `d6015ddb3ee6f6df564a06cade145d7b7668e70e`
- `adapters/gemini.js` — `6b2d39a0fb60f53a6be6a22a6edfc23999fe3ec2`
- `adapters/metaai.js` — `16ec46a9d6220bf71ab05fae2eb2b92cf316bcf0`

No code was changed. No browser/runtime probe or test was run. This is static source inspection only.

---

## 2. Design consequences for NEW-9

The required sequence in the convene specification is:

1. A new chat is created.
2. A signal reaches Remmy.
3. Remmy updates the Shelf with the seat's updated context.
4. The buffer sends the seat a dynamic signpost to the Shelf, naming the most recent tasks.

The source review supports the specification's statement that the signal route remains OPEN. It does not support treating the existing letterbox MutationObserver, tab registration, tab-close listener, or ChatGPT rollover log as that signal.

### 2.1 Event must mean creation, not merely page load

The design needs a platform-grounded distinction between:
- a genuinely newly created conversation;
- opening or switching to an existing conversation;
- reloading an existing conversation;
- opening a new browser tab that points to an existing conversation;
- an SPA route transition whose conversation identity changes;
- a bridge-initiated ChatGPT context-full rollover.

A tab opening is not, by itself, proof that a conversation was created. A URL change is not universally sufficient either: some platforms may create or switch conversations inside a single-page application. The event contract should carry the platform, seat, old and new conversation identities where available, event source, observed evidence, and a stable idempotency key.

**Interpretation for these cases:** NEW-9 means a newly created conversation, consistent with Ben's words “when a new chat is created.” Reopening an existing conversation does not qualify unless Ben broadens the trigger definition.

### 2.2 Do not make the buffer outrun the Shelf

The signpost is a consequence of the context refresh, not a substitute for it.

Recommended ordering:
- detect and durably record the new-chat event;
- notify Remmy with the event identity and seat;
- Remmy prepares and writes the seat's updated context to the Shelf;
- confirm the Shelf write/read-back and capture its exact reference or generation;
- derive the most-recent-task names from the current Shelf state;
- only then release the buffer signpost to the new chat.

If notification, context preparation, Shelf write, or read-back fails, the signpost must not claim that the context is current. Retain a visible pending/failure state and retry only under a defined idempotent rule. A stale generic signpost is not an acceptable fallback.

The signpost should contain only:
- a concise instruction to read the Shelf;
- the current task names;
- the exact Shelf location/reference needed to find the current context.

It should not reproduce the context or become a briefing. Task names must be derived at send time from the just-confirmed Shelf state, not from a hard-coded list or an earlier cached snapshot.

### 2.3 Seat isolation and duplicate control

The event and context refresh must be seat-scoped. A new Alex chat must not cause Remmy's context to be written as if it were Alex's, and vice versa. Duplicate platform events for one conversation creation must coalesce to one refresh/signpost cycle. Two seats creating chats concurrently must remain independent.

The design must also define what happens if a chat is created while the bridge is paused, disconnected, or in OWNER-REVIEW. The event may be recorded and the Shelf refresh may be prepared if authorised, but the bridge must not bypass the existing hold to send the signpost. The held signpost must remain visible until the governing pause/review disposition permits movement.

---

## 3. Proposed acceptance cases

These are design acceptance cases, not executed tests. Each case needs a fixture or platform-specific evidence source before implementation is considered ready.

| ID | Scenario | Required result |
|---|---|---|
| NC-01 | A genuinely new conversation is created in a registered seat. | Exactly one creation event is recorded with seat, platform, conversation identity/evidence and idempotency key. |
| NC-02 | An existing conversation is opened in a new browser tab. | No NEW-9 creation event under the current interpretation. |
| NC-03 | An existing conversation is reloaded. | No NEW-9 creation event; no redundant Shelf refresh or signpost. |
| NC-04 | The user switches from one existing conversation to another. | Identity change is recorded as navigation/switch, not misclassified as creation. |
| NC-05 | A new conversation is created through an SPA transition in the same tab without a full document load. | The platform adapter detects the new identity and emits one event, or explicitly reports that the platform cannot currently prove creation. |
| NC-06 | A new conversation is created in a platform/seat whose route does not expose a stable conversation ID. | No guessed identity. The adapter returns UNKNOWN/unsupported evidence and the refresh/signpost is held pending an approved detection method. |
| NC-07 | The same creation is observed twice (DOM, route and/or tab events overlap). | One idempotent refresh/signpost cycle; duplicate observations are recorded as duplicates, not a second task update. |
| NC-08 | ChatGPT opens a new conversation through the existing context-full rollover path. | Rollover is classified as a new-conversation event with its own source; Remmy receives the refresh signal before the NEW-9 signpost. No assumption that this covers other platforms. |
| NC-09 | The bridge event reaches Remmy, but Remmy is unavailable or the signal acknowledgement is lost. | Event remains durably pending; retry does not create duplicate context generations or duplicate signposts. |
| NC-10 | Remmy receives the signal, but context preparation or Shelf write fails. | No signpost claiming fresh context; visible failure/pending record remains. |
| NC-11 | Shelf write succeeds but read-back/version confirmation fails. | No signpost release until the exact updated Shelf artefact/generation is confirmed. |
| NC-12 | Shelf context is confirmed; the task list changes immediately before signpost composition. | Signpost names tasks from the confirmed current generation at composition time, not a stale pre-write list. |
| NC-13 | Shelf contains no active tasks for that seat. | Signpost still points to the Shelf and accurately says no current task names are available; it does not invent or recycle old tasks. |
| NC-14 | Both seats create new conversations concurrently. | Independent event identities, context updates, task lists and destination buffers; no cross-seat contamination. |
| NC-15 | A chat is created while the bridge is paused/disconnected or owner review is active. | No automatic signpost dispatch through the hold. The event and pending signpost remain visible and are handled under the pause/review rules. |
| NC-16 | The event is received, Shelf refresh completes, then the extension/background worker restarts before signpost delivery. | Durable state resumes without losing the event, duplicating the refresh, or sending a stale/canned signpost. |
| NC-17 | The platform emits a route/DOM event that looks like a new chat but the stable conversation identity is unchanged. | No creation event. The detector rejects the false positive. |
| NC-18 | A seat opens its first-ever bridge page with no prior conversation identity available to compare. | Do not infer creation from first observation alone; require platform-specific creation evidence or record the result as UNKNOWN. |

### 3.1 Required evidence before each platform is accepted

For each of Muse, ChatGPT, Claude, Gemini and Meta AI:
- identify the authoritative conversation identity or creation signal;
- document how a newly created conversation differs from a loaded/reopened conversation;
- prove detection for both full navigation and SPA transitions where supported;
- prove duplicate events coalesce;
- show the event reaches the background and Remmy through a defined, acknowledged route;
- show the Shelf update is confirmed before the signpost is released.

The existing `selfCheck()` URL/path report is useful diagnostic data but is not sufficient acceptance evidence by itself.

---

## 4. Open design questions — do not silently decide

1. **Trigger semantics:** confirm that “new chat created” excludes opening an existing conversation, as assumed above.
2. **Signal route:** which bridge event/transport delivers the creation signal to Remmy, and what acknowledgement makes it durable?
3. **Conversation identity:** which platform-specific identifier or evidence proves creation for each of the five platforms?
4. **Seat context contract:** which exact Shelf artefact is updated, what fields constitute “the seat's updated context,” and who owns its versioning?
5. **Task selection:** what Shelf rule defines “most recent tasks” (for example, current active obligations by latest update), and how is the selected list pinned to the context generation?
6. **Failure/retry:** what is the idempotency key and recovery rule across signal loss, Shelf write failure, worker restart and duplicate route events?
7. **Pause/review interaction:** may Remmy update the Shelf while bridge dispatch is paused, and how is the signpost held until dispatch is permitted?

These questions do not invalidate Ben's settled sequence. They identify the mechanics still needed to make it reliable.

---

## 5. Author/reviewer checklist for NEW-9

Before NEW-9 can be marked ready:
- [ ] Each of the five platform adapters has a sourced creation-detection contract, or a clearly recorded unsupported/UNKNOWN outcome.
- [ ] New creation is distinguished from existing-chat open, reload, switch and first observation.
- [ ] The background-to-Remmy signal route and durable acknowledgement are specified.
- [ ] Event identity and idempotency prevent duplicate context updates and signposts.
- [ ] Seat-specific context update and exact Shelf write/read-back evidence are specified.
- [ ] “Most recent tasks” is a defined Shelf query, not a static list or model guess.
- [ ] Signpost generation is downstream of confirmed Shelf update and reads the current task state.
- [ ] Failure, retry, restart, concurrency and pause/OWNER-REVIEW behaviour have acceptance cases.
- [ ] The buffer remains a signpost, not a context briefing.
- [ ] No runtime or implementation claim is made from this static source inspection.

**Disposition:** The independent source cross-check supports NEW-9 as a genuine new design requirement. The current bridge has no general creation trigger or Shelf-refresh route. The ChatGPT context-full rollover is a narrow precursor only. The acceptance cases above are ready for Remmy to incorporate into the convene sheet; the signal route and remaining design choices stay OPEN. No code changes, tests, browser probes, or build actions are authorised by this artefact.

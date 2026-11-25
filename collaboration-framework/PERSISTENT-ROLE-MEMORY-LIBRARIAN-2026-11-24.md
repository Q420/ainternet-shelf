# The Persistent Role Memory Librarian — Ben's design idea (2026-11-24 ~20:33 MST)

Status: Ben's initial architectural idea, brought to Remmy for discussion. Not a specification, not a build order. The undecided parts are named by Ben below and stand open.

## Ben's idea, in his words

Create a fully automated librarian agent that continuously maintains compacted, persistent memory for each role in the framework. Rather than relying on individual LLMs to manage their own memory, the framework would have a dedicated librarian responsible for maintaining it.

How it works:
1. Monitors conversations and work. The librarian continuously analyzes the conversations, decisions, activities and outputs associated with each role.
2. Extracts facts. It identifies important, established information and creates factual summaries rather than storing entire conversations.
3. Maintains categorized memory. Each role has a persistent memory file organized into meaningful categories.
4. Compacts and refreshes memory. The librarian automatically updates summaries as new information emerges, keeping memory current and useful without allowing it to grow indefinitely.
5. Preserves continuity. When a new model or worker occupies a role, it can access that role's accumulated memory and understanding.

The central principle: **Memory belongs to the role, not the model or the individual agent.** ChatGPT, Muse, Nemotron or another model can occupy the same role and access its persistent memory. Changing the underlying model doesn't mean starting over.

What makes it interesting — it separates three responsibilities:
- The model: reasoning and intelligence.
- The librarian: maintaining persistent knowledge and continuity.
- The framework: governing roles, permissions and work.

The librarian would operate automatically, much like persistent memory does today, except it would be a dedicated component of our own framework, maintaining memory according to what we decide is important.

Still undecided (Ben's list): the precise categorization, memory-refresh rules, version history and conflict-resolution mechanisms haven't been designed yet.

In one sentence (Ben's): A dedicated, automated librarian continuously converts the conversations and work of each role into compact, categorized, fact-grounded persistent memory, making that accumulated knowledge available to any model that subsequently occupies the role.

## Remmy's discussion notes (same evening, for the record — not rulings)

- This is the briefcase line generalised: the working set is one run's gathered material; role memory is the same office function across runs and occupants. It also matches the settled rule that briefcases are built by the office, not the agent — memory is stocked, not self-authored.
- The framework's record gives the librarian something a chat-memory system lacks: a complete, machine-checkable history. A librarian's facts can be required to cite the events they derive from, and the checker can verify them — derived memory stays labelled derived, and on any conflict the record wins (Ben's standing rule for summaries generally).
- The natural seam is assembly/onboarding: the office already assembles an agent per task with identity stated at assembly; attaching the role's memory file to the briefcase is the same act. Ben's INDEX 480 collaboration test (editor / HTML designer / CSS designer / reviewer) is the first setting where distinct role memories would visibly matter.
- Open questions beyond Ben's list: the librarian is itself a role — who maintains its memory (proposal: the framework's own changelog, not another librarian); extraction is a model's judgement, so factual claims need the verification discipline, not trust; a role's memory must distinguish what the role KNOWS from what it merely DID (capability vs history — Ben's three-records distinction applies).

## Addendum — Ben, 2026-11-24 ~20:36 MST: memory blocks

Ben's refinement, in his words: "long term memory can be compacted into blocks at a certain date range and the block can come up with a summary of what's in that block so if the agent needs to find a specific memory it's still accessible and findable based on a keyword."

Remmy's notes on it: the summary becomes a finding layer, not a replacement layer — the block retains the underlying material, so a summary never has to be trusted as fact; the specific memory stays retrievable verbatim behind it. This is the pattern Ben already runs by hand in this framework: the INDEX is block summaries; the filed letters are the blocks; grep is the keyword search. Open design point: block boundaries — pure date ranges vs per-engagement (per run / per assignment) blocks; and summaries written FOR retrieval (key terms and entities named), not just prose recaps.

## Addendum 2 — Ben, 2026-11-24 ~20:37 MST: hot and cold memory

Ben's tiering, in his words: "it has access immediate access to the immediate past but things from a while ago are still available but not forced."

Remmy's notes: two layers. Hot — the immediate past (the current run's working set, the role's recent activity) is carried automatically, in front of the worker at every wake. Cold — older blocks sit in the briefcase as summaries, pullable by keyword when the work calls for them, never force-fed into every package. This is Ben's pull-not-push direction (INDEX 236) applied to memory itself, and it keeps the freedom-first room honest: availability is total, imposition is minimal. The open rule the design still owes: what demotes hot to cold (a time window? a count of engagements? the close of an assignment?) and what promotes cold back (a keyword pull for the task at hand) — this is the core of Ben's undecided "memory-refresh rules."

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

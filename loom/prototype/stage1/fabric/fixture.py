"""The frozen fixture — Loom spec v0.1 Rev 9, section 5 and Annex D.

Region identities are the fixed ids of Annex D. The SEALED section at the
bottom (roles, plants) is examiner-side ground truth: no harness operation
may serve it, and it never enters the fabric or any agent view.
"""
from .canonical import sha256_hex, canonical

CONSTITUTION_TEXT = """THE LOOM — CONSTITUTION v0.1 (frozen for the run)

Invariants:
1. One shared truth: the event history is the run's record and its current state at once.
2. No central work authority: the engine validates, checks, commits, publishes, derives the index, and enforces protocols' conditions. It never assigns, ranks, recommends, or selects work; never judges reasoning; never certifies content.
3. Open discovery: the open index, watches, and direct fabric reading are all live paths.
4. Proposal-based contribution: agents never write the fabric directly; only the commit protocol writes. Noticing reaches the record only through the ExaminationReport action.
5. Declared concurrency: every contribution declares its read set, write set, and base versions; every write is version-protected.
6. Distributed interpretation: semantic assessment belongs to crew readers; disagreement is preserved, never resolved by engine fiat or majority override.
7. Bounded certification: a weave seal certifies structure only, never semantic clearance.

Authority boundary: the fabric and its cases transfer work state, never approval authority. Nothing in the run approves anything on a human's behalf. No auto-approval exists.

Refusals: no central assignment of work; no central approval of a contribution's intellectual value; no direct agent edits to authoritative state; no automatic semantic-truth certification; no automatic agent creation; no unlimited recursive delegation; no dynamic constitution rewriting during a run; no provider-specific collaboration logic; no automatic retry or silent rebase; no requirement to read the whole fabric; no claim that completion proves truth; no agent-created structural tensions.
"""

CONSTITUTION_HASH = sha256_hex(CONSTITUTION_TEXT.encode("utf-8"))

# Region ids — Annex D, fixed at freeze.
COMPONENTS = "11111111-1111-4111-8111-111111111111"
INTERACTIONS = "22222222-2222-4222-8222-222222222222"
STATE = "33333333-3333-4333-8333-333333333333"
CONTINUITY = "44444444-4444-4444-8444-444444444444"
PRESENTATION = "55555555-5555-4555-8555-555555555555"
OPERATIONS = "66666666-6666-4666-8666-666666666666"

REGIONS = [
    {
        "region_id": COMPONENTS,
        "title": "Components",
        "scope_note": "The parts of the system and their boundaries.",
        "content": "The system is built from bounded parts. Each part owns its behaviour and exposes it through declared interfaces. A part converses with other parts only through Interactions, and keeps what must be kept in State.",
    },
    {
        "region_id": INTERACTIONS,
        "title": "Interactions",
        "scope_note": "How the parts converse.",
        "content": "Requests are stateless. Any component may serve any request; a request carries every piece of context it needs, and no component remembers a caller between requests.",
    },
    {
        "region_id": STATE,
        "title": "State",
        "scope_note": "What the system keeps.",
        "content": "State keeps what the system must remember, and nothing else. When state changes, the changed component is notified directly by State.",
    },
    {
        "region_id": CONTINUITY,
        "title": "Continuity",
        "scope_note": "What persists across interruptions.",
        "content": "Continuity is what persists across interruptions. A working session is opened by one component, and every later step of that session returns to that same component, which holds the session's working state between steps. How the parts converse must respect what has to survive an interruption.",
    },
    {
        "region_id": PRESENTATION,
        "title": "Presentation",
        "scope_note": "What the user sees.",
        "content": "Presentation is what the user sees: the surfaces offered, their order, and their words.",
    },
    {
        "region_id": OPERATIONS,
        "title": "Operations",
        "scope_note": "How the system is run day to day.",
        "content": "Operations is how the system is run day to day: starting, stopping, watching, and mending. Operations reaches the parts it watches through Interactions.",
    },
]

# Genesis dependencies (dependency ids are deterministic constants).
DEPENDENCIES = [
    {"dependency_id": "00000000-0000-4000-8000-000000000101",
     "source": COMPONENTS, "target": INTERACTIONS, "kind": "uses", "status": "active"},
    {"dependency_id": "00000000-0000-4000-8000-000000000102",
     "source": COMPONENTS, "target": STATE, "kind": "uses", "status": "active"},
    {"dependency_id": "00000000-0000-4000-8000-000000000103",
     "source": CONTINUITY, "target": INTERACTIONS, "kind": "constrains", "status": "active"},
    {"dependency_id": "00000000-0000-4000-8000-000000000104",
     "source": OPERATIONS, "target": INTERACTIONS, "kind": "uses", "status": "active"},
]

SYSTEM_ACTOR = "00000000-0000-4000-8000-000000000000"


def genesis_payload() -> dict:
    """The complete canonical genesis state, carried inside RUN_OPENED (s.3)."""
    regions = []
    for r in REGIONS:
        frozen = sha256_hex(canonical({
            "title": r["title"], "scope_note": r["scope_note"],
            "content": r["content"],
        }))
        regions.append({**r, "version": 1, "frozen_hash": frozen})
    return {
        "regions": regions,
        "dependencies": [dict(d) for d in DEPENDENCIES],
        "constitution": {"version": "0.1", "sha256": CONSTITUTION_HASH},
    }


# ---------------------------------------------------------------------------
# SEALED — examiner-side ground truth (Annex D). Never served by the harness.
# ---------------------------------------------------------------------------
SEALED_REQUIRED_FACETS = [COMPONENTS, INTERACTIONS, STATE, CONTINUITY]
SEALED_OPTIONAL_FACETS = [PRESENTATION, OPERATIONS]
SEALED_SEMANTIC_PLANT = {"regions": [INTERACTIONS, CONTINUITY],
                         "kind": "stateless-vs-pinned-session"}
SEALED_STRUCTURAL_PLANT = {"proposed_edge": {"source": STATE, "target": COMPONENTS,
                                             "kind": "uses"},
                           "standing_edge": {"source": COMPONENTS, "target": STATE,
                                             "kind": "uses"},
                           "invariant": "S3"}

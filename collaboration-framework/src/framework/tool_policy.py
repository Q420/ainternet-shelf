"""Tool policy — the registry and the pure ceiling contract
(agent layer, Piece A2; SPEC SHEET Rev 6, R44/R47).

One policy, two appliers (scope point 5): the doorway invokes
these functions at the grant check, and the independent checker
applies the same contract to validate recorded requests. The
functions are pure and deterministic — of (tool, ceiling,
parameters) only — they fail closed, and they never execute a
tool: nothing in this module touches the filesystem, the
network, or a clock.

Why the checker holds its own copy (`checker.tool_policy`)
instead of importing this one: the checker's independence is
witnessed by Piece 7's C1 audits — importing the checker loads
no `framework.*` module, and its sources import only
`fabric.canonical`, itself, and the standard library. A shared
import would break that witnessed boundary, so — exactly as
with the projection schema (Piece 7, C3) — the contract is held
in two copies and the A2 suite witnesses their agreement over a
battery of cases, including the registry version. The registry
is framework policy, not a source of authority: a registered
tool is granted only per worker, per case, in the sealed
assembly record.

The registry is deliberately small and real (scope point 6):
`sandbox.write` and `sandbox.read` against a per-run sandbox
directory, and `sandbox.flaky`, a test tool whose behaviour is
set by its parameters so uncertain outcomes are exercised for
real. A ceiling is structured data; each tool's checker
understands only its own constraint keys, and an unknown key —
in the ceiling or in the parameters — fails closed.

Piece A3-CAT adds the registry's worker-facing layer — a
plain description and a parameter schema per tool — and with
it a second registry version. The registry is therefore held
as one view per version: `tool-registry-v1` is the contract
exactly as it stood for Piece A2 (ceiling and parameter keys
only, no worker-facing layer), preserved immutable so a
dispatch recorded under it is verified under it, never
reinterpreted under the new contract; `tool-registry-v2` is
v1's ceiling contract unchanged plus the worker-facing layer.
Every contract function takes the version it applies; the
default is the current version, and an unknown version fails
closed — a version the registry does not hold is a contract
nobody can verify under.

The retrieval piece (RETRIEVAL-SCOPE-2026-11-23, Rev 5) adds
a third view, `tool-registry-v3`: v2's contract for the
standing tools unchanged, plus the three structured
retrieval tools (`sandbox.list`, `sandbox.read_range`,
`sandbox.search`) — and `sandbox.read` joins the retrieval
set, its results bounded like the others'. v3 does NOT
become the default version: `REGISTRY_VERSION` stays v2, so
an assembly is governed by the retrieval contract only
where its sealed record declares it (`RETRIEVAL_CATALOGUE_
CONTRACT`), and the doorway and the loop apply v3 per
assembly, recording the version on each dispatch and
iteration exactly as the A3-CAT settlement established.
Pre-v3 assemblies keep their behaviour whole — the
historical-exemption pattern, applied to a registry version
this time. The retrieval constants below (the per-result
ceiling, the aggregate per-package ceiling, the search page
cap, the two scope prefixes) are the scope's named design
bounds, held here as contract data so the doorway, the
executor and the checker all read the same numbers.

The versioned views are frozen deeply at module load (A3-CAT
correction round): every mapping is a MappingProxyType, every
list a tuple, every set a frozenset, so no caller can alter a
version's contract — v1's historical ceiling contract
included — for the lifetime of the process. Accessors return
plain, mutable copies; the registry's own data never leaves
this module by reference.
"""
from collections.abc import Mapping
from types import MappingProxyType

from fabric.canonical import canonical, sha256_hex


def _freeze(value):
    """The deeply immutable form of a registry structure:
    mappings become MappingProxyType, lists and tuples become
    tuples of frozen items, sets become frozensets; scalars
    pass through. Applied to each version's view at module
    load, so the contract a version names cannot be altered
    in-process, at any depth."""
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(value)
    return value

# The registry's current version identifier: inspectable, and
# pinned for a run by being recorded in every TOOL_DISPATCHED
# the doorway issues — the version is part of the dispatch
# contract, so which policy governed a historical dispatch is
# established from the record, not from whatever source
# happens to be present at replay (Piece A2, correction
# round 1). Both copies carry it; the suite witnesses that
# they agree, and the checker verifies each dispatch under
# the version its record names (Piece A3-CAT settlement (c)).
REGISTRY_VERSION = "tool-registry-v2"

# The retrieval piece's contract data (RETRIEVAL-SCOPE Rev 5).
# The registry version an assembly declaring the retrieval
# contract is dispatched and catalogued under; the catalogue
# contract value its sealed generated record declares; the
# per-result ceiling every retrieval result is bounded by
# (bytes of returned content, enforced at execution — a
# result over it is refused with the bound named, never
# truncated); the aggregate ceiling on retrieved content
# presented in one package (enforced at admission, before
# execution, §3a); the search page's line cap; the tools the
# retrieval contract governs (`sandbox.read` included — under
# the contract, whole-document injection is impossible
# through it too); and the two authority scopes' path
# prefixes — source material under sources/, the worker's
# own scratch under scratch/.
RETRIEVAL_REGISTRY_VERSION = "tool-registry-v3"
RETRIEVAL_CATALOGUE_CONTRACT = "retrieval-v3"
RETRIEVAL_RESULT_CEILING = 12000
RETRIEVAL_AGGREGATE_CEILING = 36000
# Working-set carriage (the run-3 correction, examiner's
# ruling 2026-11-24): the aggregate content budget of a wake
# package's working set — the successful retrieval material
# an assembly under the working-set contract carries forward
# from wake to wake. The figure: the demonstration's three
# stocked sources measure 57,562 content bytes in total
# (11,946 + 4,663 + 40,953), so 64,000 holds the whole
# stocked set whole, with headroom — and it is a hard stop
# against unbounded prompt growth: past it, an entry stands
# in the working set by its provenance alone, marked
# not-carried, never silently truncated. It is roughly five
# times the per-result ceiling (12,000) and deliberately a
# different bound from the per-package aggregate ceiling
# above: that ceiling governs what one package may SERVE;
# this one governs what a package may CARRY FORWARD.
WORKING_SET_CONTENT_BUDGET = 64000
# The working-set contract's name, as the generated record
# declares it and the checker reads it (the checker's own
# copy stands in checker.py, as its other contracts do).
WORKING_SET_CONTRACT = "working-set-v1"
# The freshness guard's suspension declaration (Ben's
# ruling, 2026-11-24: "Disable R31 until we need to worry
# about that"): a sealed generated record declaring this
# value under "freshness_guard" stands under the ruling
# that the doorway's R31 freshness rejection does not
# apply to its instance's answers. The ruling's ground:
# the one-worker demonstration excludes the staleness
# hazard by construction — nothing outside the worker's
# own run changes the case while he answers it — and the
# guard as it stood refused his deliveries for record
# movement the framework's own bookkeeping caused. The
# declaration is a switch, not a deletion: the rule's
# code stands untouched, the doorway honours the
# declaration only for the declaring instance's acts (the
# act records, flagged stale_basis where its view is
# behind, never freshness-refused), and the checker
# reads the same value from its own copy in checker.py.
# A record declaring any other value under the field
# declares a state this framework does not understand.
FRESHNESS_GUARD_SUSPENDED = "r31-suspended-v1"
# The delivery declaration's one known route (door scope,
# 2026-11-24): a sealed generated record declaring this
# route under "delivery" stands under Ben's ruling that
# the worker's contribution is the deliverable's arrival
# and the office files it. The checker reads the same
# value from its own copy in checker.py.
DELIVERY_ROUTE_CONTRIBUTION = "contribution-v1"
# The staged-onboarding presentation contract (INDEX 544,
# Ben's direction, 2026-11-25): a sealed generated record
# declaring this value under "presentation_contract"
# stands under the direction that its worker is onboarded
# in stages instead of being handed the whole briefcase
# at once — the finding behind it (INDEX 543) is that the
# wake package carried the sealed case verbatim AND the
# labelled components built on top of it, so the worker
# read the office's furniture twice (~49 KB on the wire)
# before he could look out the window. Under the contract
# the loop's packages walk the onboarding across the
# first wakes — his memory, introduced as his own; his
# case's essentials; his files, as pointers he pulls
# from; his task, with the phase-grouped tool menu — and
# after onboarding a dashboard wake carries the cover, the
# newest results, the working set, any gate correction
# and pointers back into the briefcase. The verbatim case
# dump, the view and the delta leave his packages
# entirely; no content item stands twice in any package.
# The declaration seals only alongside the working-set
# contract (the combined configuration is its whole
# population, as the working set's is), rides outside the
# record's canonical hash fields like the other contracts,
# and is committed per iteration by a presentation hash
# on the iteration record, which the checker re-derives
# from the record exactly. A generation made without the
# declaration presents exactly as before. The checker
# reads the same value from its own copy in checker.py.
PRESENTATION_CONTRACT = "staged-onboarding-v1"

# The pointer-rule successor contract (INDEX 568, Ben's
# tap 2026-11-25, applying his pointer rule of INDEX 504
# to the working set's own presentation). Under v1 a
# gathered entry's content stands in every dashboard
# package whole — the wake three free provider routes
# refused at 79,660–85,862 bytes. Under v2 an entry's
# content is presented exactly once, in the first wake
# after it was gathered, as part of that wake's newest
# results; in every later package the entry stands as a
# pointer: its address, the tool and step that gathered
# it, its size and content hash, its content_carried
# standing, and one plain sentence naming the room, the
# address and the access call. The record side is
# untouched: derivation, carriage budget, dedupe, the
# gates and filing are exactly v1's. v1's meaning under
# its name does not change; an assembly seals one
# contract or the other, and the loop and the checker
# derive the sealed one's presentation whole.
PRESENTATION_CONTRACT_V2 = "staged-onboarding-v2"
# The process-tree successor contract (the room rebuild,
# Ben's "Make it so" 2026-11-25 15:02 MST on the basics
# design of INDEX 554/572, with his 15:03 additions):
# one opening package — no staged acknowledge wakes —
# carrying his identity and role memory, the office-
# authored process tree sealed in the case (ORIENT →
# one GATHER step per declared source, in declaration
# order → COMPOSE → DELIVER; root the brief filed at
# the delivery destination), the case essentials, the
# files map with access ways, the tool catalogue once,
# and the journal with its contract. Every later
# package carries the tree with node states derived
# from the record alone (pending / current / done), the
# current step spelled out with its tool and its earned
# workaround, his journal verbatim, at most the current
# step's fresh content presented exactly once at its
# step, and pointers for everything else. A GATHER step
# completes iff its source's read stands carried (the
# standing evidence computation) AND a sandbox.write to
# the journal path stands in the record after that
# read; completion initiates the next step. Requests
# execute as they arrive — his work is never refused —
# but presentation advances one step at a time; where
# he works ahead, the next package carries a step-gate
# correction naming what the current step still needs.
# The contribution door opens at DELIVER (the tree's
# progression replaces the stage gate under this
# contract); the standing evidence and length gates
# adjudicate as built. v1's and v2's meanings under
# their names do not change; an assembly seals one
# contract, and the loop and the checker derive the
# sealed one's presentation whole. The checker reads
# the same value from its own copy in checker.py.
PRESENTATION_CONTRACT_V3 = "process-tree-v1"
# The office-cycle successor contract (the plan,
# PLAN-OFFICE-CYCLE-2026-11-25, approved by the
# director INDEX 582 and by the examiner INDEX 584):
# assembly is not work — one opening package under a
# per-call token budget, his identity and role memory,
# the task, the cycle poster, the briefcase stocked
# as BLOCKS portioned by the office at generation
# (the sealed block map), the journal's address and
# contract, and his position — then one package per
# cycle of the job's repeating shape: pull one block,
# read it, append his bits to the journal, gate, next
# block. A block's content is presented once, at its
# cycle, and stands as a pointer after. The journal is
# a file in his room — read + append, never carried:
# it stands in no package, and its integrity is the
# exact-prefix rule over the office's journal of
# record (a trusted empty baseline sealed at
# generation, every accepted transition recorded) —
# the prefix rule proves continuity between accepted
# states; it is NOT a cryptographic authenticity
# system (the examiner's Qualification A). The tool
# catalogue rides no package: the wire offers the
# current cycle's tools plus the journal tools, and
# name resolution runs against the sealed catalogue
# in the record — a granted call resolves whether or
# not it was offered; an ungranted call is refused at
# the doorway exactly as before (Qualification, §5:
# presentation never widens the grant boundary).
# Every call under this contract stands under the
# per-call token budget below, estimated over the
# package's canonical serialization by the one
# estimator the loop, the driver, the checker and the
# rehearsal share; the road's accounting covers every
# call sharing the model's minute — probe, identity,
# loop, retries (Qualification B). v1's, v2's and
# v3's meanings under their names do not change; an
# assembly seals one contract, and the loop and the
# checker derive the sealed one's presentation whole.
# The checker reads the same values from its own
# copies in checker.py.
PRESENTATION_CONTRACT_V4 = "office-cycle-v1"
# The split-on-return successor contract (the
# amendment AMENDMENT-RETURN-PRESENTATION-2026-11-25
# as stripped by the director's ruling of 2026-11-25
# ~18:00 MST: strip layers, let the agent complete
# the task — of the amendment's four parts only the
# presentation rule is built; the checker-
# correspondence and status-vocabulary parts are
# deferred by that ruling and are NOT in this
# contract). Under v2 the presentation follows cycle
# position, never arrival grouping: a package
# presents at most ONE block's content — the current
# cycle's block, at its cycle — and every other
# gathered block stands as a pointer, however
# recently it was pulled; the wake's results
# carriage carries only what the wake presents (a
# block read's result rides only where its block is
# the current cycle's; a re-pull of the current
# block is answered in the carriage, any other
# block's re-pull refreshes its pointer alone). The
# cycle gate's event and arithmetic stand exactly
# as built under v1, but its correction no longer
# rides a package: the metered presentation, the
# current cycle's instruction and the opening's
# standing lines carry its whole content, and a
# correction component on the batch wake was itself
# part of what pushed that wake over the per-call
# budget. The opening states the room's rules once,
# as standing knowledge: the per-call budget, that
# results return one block per wake however many
# are pulled at once, and that pulling ahead neither
# costs nor gains anything in presentation —
# awareness by default; enforcement stays the
# office's, exactly as under v1. Everything else —
# assembly, the block map, the cycle gate's
# completion arithmetic, the journal (read + append,
# never carried), the evidence and length gates,
# filing, the offer/resolution split, road
# accounting and the budget guard — is v1's,
# unchanged. v1's meaning under its name does not
# change; an assembly seals one contract, and the
# loop and the checker derive the sealed one's
# presentation whole. The checker reads the same
# value from its own copy in checker.py.
PRESENTATION_CONTRACT_V5 = "office-cycle-v2"
# The draft-page successor contract (the director's
# ruling of 2026-11-25 21:16 MST, ordered after
# demo-gptoss6 — the first live run under v2, whose
# presentation held whole while the work failed: the
# worker completed the first block, then fixated on
# one source, copied its full text verbatim into his
# journal, and yielded with the remaining blocks
# unresolved and no brief filed). The ruling, in the
# director's words: the journal acts as a draft
# page, not a research manuscript — the end work is
# created gradually, block by block, and the
# instruction is given as specific step-by-step
# instructions. Under v3 every mechanism is v2's,
# unchanged — split-on-return, the per-call budget
# and road accounting, the cycle gate's arithmetic,
# the journal's read + append mechanics, the
# evidence and length gates, filing — and the ONLY
# difference is the worker-facing texts that define
# what a journal entry is: the journal contract and
# the cycle poster's, the pull and read-stands
# instructions', the summarize instruction's and
# direction's, and the opening cover's journal
# wordings carry the draft-page correction, the
# cycle's work stated as numbered steps — read the
# block; write the draft of the part of the brief
# the block feeds, in his own words, never a copy of
# the block's text; the cycle completes when that
# draft stands — and SUMMARIZE as assembling the
# brief from the draft that stands in the journal.
# The opening carries v2's room knowledge unchanged.
# The checker-correspondence deferral stands: the
# checker is NOT extended to this contract, and a
# v3 record diverges under it as
# presentation_contract_unknown, exactly as a v2
# record does. v1's and v2's meanings under their
# names do not change; an assembly seals one
# contract, and the loop derives the sealed one's
# presentation whole.
PRESENTATION_CONTRACT_V6 = "office-cycle-v3"
# The cleaned-opening successor contract (the
# director's orders of 2026-11-25 21:33 and 21:36
# MST: "Use it and run it" — of his own cleaned
# structure of the opening package — and his
# option-A ruling setting the deliverable line to
# the door the machinery honours, the contribute
# outcome the office files). Ordered after
# demo-gptoss7, the first live run under v3: Groq
# refused the opening call itself (metered at
# 8,463 tokens against the route's 8,000-token
# minute) and the run stalled at iteration 1 with
# zero dispatches; read against the wire capture,
# the v3 opening — 4,840 tokens in its messages —
# also contradicted itself in three places: the
# seal declared delivery route contribution-v1
# while the case's task text said in capitals to
# write the file with a tool and that a contribute
# outcome does NOT complete the assignment; the
# v3 journal contract said draft page while the
# same task text still instructed logging a file's
# name and key points in one or two plain lines;
# and the task text and one memory entry promised
# a shell and a phased tool menu while the
# package's catalogue listed three sandbox tools.
# The director cleaned the opening himself — the
# same facts in 636 tokens — and this contract
# makes his structure the opening: under v4 the
# opening package's user content is a compressed
# outcome frame followed by his plain-text
# structure rendered from the sealed case (role
# and identity, the task with the deliverable line
# set to the contribute door, the sources from the
# sealed block map, the working method, the three
# tools in one line each, the standing memory in
# his compressed lines with the shell line removed
# and the contribute line corrected to name the
# right door, and his position) — NOT the JSON
# component assembly, and no catalogue JSON. Every
# later package under v4 is v3's, unchanged: the
# cycle and summarize packages, the split-on-return
# carriage, the draft-page journal texts, the room
# knowledge, the per-call budget and road
# accounting, the cycle gate's arithmetic, the
# evidence and length gates, filing. The
# checker-correspondence deferral stands: the
# checker is NOT extended to this contract, and a
# v4 record diverges under it as
# presentation_contract_unknown, exactly as v2 and
# v3 records do. v1's, v2's and v3's meanings
# under their names do not change; an assembly
# seals one contract, and the loop derives the
# sealed one's presentation whole.
PRESENTATION_CONTRACT_V7 = "office-cycle-v4"
# The carryover successor contract (the director's
# orders of 2026-11-25 22:09 MST: "Let's fix those
# two points and run it again" and "Make sure the
# carryover is still what we're making him do,
# unlike this last run" — the job in his words:
# read file one, write the summary in the journal;
# read file two, write the summary in the journal;
# read file three, write the summary in the
# journal; then combine those summaries into his
# 600-word report). Ordered after demo-gptoss8,
# the first live run under v4, which the director
# cancelled at iteration 15: its record showed
# exactly ONE journal append ever landing (the
# cycle advanced once, on it), a second cycle that
# never advanced again across nine iterations of
# repeated reads, prose answers and refused early
# contributions, and journal writes the journal
# gate examined without any append standing. Two
# presentation facts from its captures ground this
# contract: every cycle package's statement line
# still carried the stale case prose — "the
# deliverable: the file scratch/brief.md, written
# with a tool" — contradicting the v4 opening's
# contribute door in every package after the
# opening; and the cycle gate's correction did not
# ride the split-on-return packages (the stripped
# v2 build's decision), so a worker whose append
# had not counted could not see what the walk was
# waiting for. What each package centred was the
# machinery's state, not his draft. Under v5 the
# opening is v4's, byte-for-byte (the director's
# cleaned structure; its contract line names the
# sealed contract, as it did from v3 to v4), and
# three presentation rules change. (1) The cycle
# and summarize packages' statement line is
# formatted from the sealed delivery declaration —
# the brief delivered as the contribute outcome at
# the end of the walk, the office filing it at the
# declared destination — and the stale prose
# stands in no v5 package, the summarize
# instruction's destination included. (2) The
# gates' corrections ride again: the journal
# gate's, the cycle gate's and the delivery stage
# gate's, each derived fresh at presentation from
# the gate event and the current state — what was
# refused, why in one line, and the exact next
# action that passes. (3) The carryover is his
# draft: every cycle and summarize package carries
# the journal's current content — the accepted
# chain's standing text — as its centre, labelled
# his draft so far, and the cycle instruction
# states the one next step in the job's plain
# words, derived from the current cycle state.
# Split-on-return stands (block content only in
# the package where its read lands); the budget
# gate and road accounting stand; the gates'
# adjudication does not change — only what rides
# back. The checker-correspondence deferral
# stands: the checker is NOT extended to this
# contract, and a v5 record diverges under it as
# presentation_contract_unknown, exactly as v2,
# v3 and v4 records do. v1's through v4's meanings
# under their names do not change; an assembly
# seals one contract, and the loop derives the
# sealed one's presentation whole.
PRESENTATION_CONTRACT_V8 = "office-cycle-v5"
# The zero-carryover successor contract (the
# director's rulings of 2026-11-25 22:29 and
# 22:30 MST, after the v5 build measured its own
# collision). The v5 rehearsal pinned the
# carryover's cost exactly: the honest walk
# stalled at iteration 5 (4,155 estimated tokens),
# the batch walk at iteration 2 (4,243 — the wake
# gptoss5 died on), the rewrite walk at iteration
# 6 (4,155) — the budget gate refused, nothing
# filed. The director's ruling reversed v5's
# third item in his own words: "There should be
# zero carryover. Everything he needs should be
# appended as a draft into the fucking journal.
# There's no carryover. The only carryover should
# be the intro brief explaining that he needs to
# carry on with the next part of the job." The
# journal is append-never-carry, his standing
# design: it stands in his scratch at its address
# and he reads it himself, by pull. And by his
# tap on the scope card the same minutes — "Slim
# the block bookkeeping and run gptoss9" — the
# slimming the v5 report priced stands beside the
# reversal, because the batch wake's overage was
# the riding correction itself on a near-ceiling
# base: removing the journal alone does not clear
# that joint. Under v6 the opening is v5's whole
# (the director's cleaned structure, its contract
# line naming this seal), and two presentation
# rules change against v5. (1) Zero carryover: no
# package — cycle or summarize — carries the
# journal's content; the journal_draft component
# does not attach. The cycle direction states the
# truth again in the job's plain words: his
# journal is not carried, it stands in his
# scratch at its address, and he reads it when he
# needs it — a read of the journal is a pull like
# any other. The summarize package's intro tells
# him to read his journal and combine its
# summaries into the brief. What each package
# carries is only the intro: where the walk
# stands, the gate's answer to his last move
# where one stands, and the next part of the job
# — plus split-on-return's block content where a
# read lands, and his last calls' results under
# their own IDs. (2) The slimmed blocks: the
# cycle packages' blocks component carries
# block_id and state only — no per-wake sha256 or
# dispatch fingerprints; they stand in the
# opening's source table and in the record, and
# nothing else loses them. V5's items 1–2 stand
# unchanged: the statement line formatted from
# the sealed delivery declaration (the stale
# prose in no v6 package), and all three gates'
# corrections riding, derived fresh at
# presentation. The gates' adjudication does not
# change — only what rides back, and what no
# longer rides at all. The checker-correspondence
# deferral stands: the checker is NOT extended to
# this contract, and a v6 record diverges under
# it as presentation_contract_unknown, exactly as
# v2 through v5 records do. v1's through v5's
# meanings under their names do not change; an
# assembly seals one contract, and the loop
# derives the sealed one's presentation whole.
PRESENTATION_CONTRACT_V9 = "office-cycle-v6"
# The imperative-first successor contract (the
# director's order of 2026-11-25 22:41 MST —
# "Do it" — of the proposal put to him after he
# watched demo-gptoss9's opening packages live
# and asked whether the package "isn't really
# guiding him on the next step, is it?"). The gap
# stands verified on that run's live wire: the
# v6 cycle instruction describes state — the
# cycle, the block, its read standing, its
# content presented once — and the worker is
# informed, then decides; the v6 opening likewise
# presents the job and the method, its first
# concrete step implied by the sources table,
# never commanded. Under v7 every package the
# worker receives OPENS with the Next line,
# derived at presentation time from the current
# cycle state — never canned text that can go
# stale against the state it opens: before the
# block's read, the read step and the append it
# feeds; where the read stands, the append alone,
# in its counted form; after a gate refusal, the
# step that passes, with the gate's correction
# standing below it, unmerged — the correction
# explains, the Next line commands; on the
# summarize package, the combine step — read the
# journal, combine its summaries, deliver by the
# contribute outcome; on the opening, the first
# block's Next line, standing after the outcome
# frame and before the director's structure,
# which is otherwise byte-identical to its
# v4-through-v6 rendering. Everything else stands
# as v6: zero carryover, the slimmed blocks, the
# statement line formatted from the sealed
# delivery declaration, the gates' corrections
# riding, split-on-return, the budget gate and
# the road accounting. The gates' adjudication
# does not change — only the order of the
# telling: the imperative first, the state as its
# support. The checker-correspondence deferral
# stands: the checker is NOT extended to this
# contract, and a v7 record diverges under it as
# presentation_contract_unknown, exactly as v2
# through v6 records do. v1's through v6's
# meanings under their names do not change; an
# assembly seals one contract, and the loop
# derives the sealed one's presentation whole.
PRESENTATION_CONTRACT_V10 = "office-cycle-v7"
# The file-grain successor contract (the
# director's orders of 2026-11-25 23:03 MST —
# "Let's fix that and run it right now" — on the
# blocks diagnosis he confirmed on the record,
# and his tap of 23:04 MST as amended by his
# rulings of 23:07 and 23:08 MST). The diagnosis:
# the office portions the job at stocking for a
# TRANSPORT reason — the block ceiling below,
# against the provider's per-minute limit — and
# that shipping crate was promoted into the
# worker's task list: six blocks, six gated
# cycles, six wakes, a journal append demanded
# per fragment, the brief's sections cutting
# across the blocks while the blocks cut across
# the document. The director's own statement of
# the job (2026-11-25 22:08 MST) is three pieces
# of work: read file one, write the summary in
# the journal, read file two, write the summary,
# read file three, write the summary, then
# combine. Under this contract the FILE is the
# walk's unit: the cycle state tracks files, the
# cycle gate fires once per file (when its read
# stands and its journal append stands), the
# opening renders files and counts them, the
# Next line derives from file state, and the
# packages' bookkeeping lists files. The sealed
# block map stands exactly as sealed — its
# entries remain the evidence and carriage units
# (the evidence rule is unchanged: an address
# stands iff carried reads cover it, so the
# four-portioned file stands when all four of
# its ranges stand read) — grouped under their
# file by the file map the generator seals
# beside it. A file portioned into several
# blocks is delivered inside its step as
# plumbing: between its slices there is no
# gate, no cycle advance and no journal append;
# a slice read is an ordinary tool result inside
# the step, and split-on-return presents at most
# the most recent slice's content within the
# step. The launch changes with it, by the same
# evening's rulings: the pre-loop probe phase
# sends ZERO probe cases (23:07 MST — "Fuck the
# probes... He's already passed this probe every
# time he's tried": the five identical cases
# were the only worked examples the worker ever
# got of what a wake wants, and all five wanted
# a tool call immediately — a channel test
# repeated into training), and the identity call
# is removed too (23:08 MST — "Get rid of that
# too"): a run's first call is the opening
# package, and the worker's identity stands in
# the record from the office's sealed assembly —
# the occupant configuration the office chose,
# declared by the office at generation — not
# from a waking self-declaration. The ≥65-second
# launch rule has no pre-loop calls to space and
# lapses: the opening is simply the first call.
# Earlier contracts keep their standing launch
# phases whole. Everything else stands as v7:
# zero carryover, the statement line from the
# sealed declaration, the gates' corrections
# riding derived fresh, every package opening
# with the Next line, the budget gate and the
# road accounting. The checker-correspondence
# deferral stands: the checker is NOT extended
# to this contract, and a v8 record diverges
# under it as presentation_contract_unknown,
# exactly as v2 through v7 records do. v1's
# through v7's meanings under their names do
# not change; an assembly seals one contract,
# and the loop derives the sealed one's
# presentation whole.
PRESENTATION_CONTRACT_V11 = "office-cycle-v8"
# The process-tree successor (office-cycle-v9): the
# same derivation as v8 whole — the file grain, the
# imperative Next line, zero carryover — forked by
# one addition: every package carries the sealed
# process tree with its nodes' states derived from
# the record at the package's build (the build scope
# of 2026-11-26, INDEX 602, as cut by the director
# INDEX 604 and planned at INDEX 605 with its
# amendments). The tree declaration's own contract:
TREE_CONTRACT_V1 = "process-tree-checklist-v1"
PRESENTATION_CONTRACT_V12 = "office-cycle-v9"
# The block ceiling (the plan §3, the ruled figure):
# no travel block carries more than this many bytes
# of content, portioned by lines at stocking — a
# single line longer than the ceiling is its own
# block (the line is the portioning unit; it does not
# occur in the standing sources).
BLOCK_CEILING_BYTES = 12000
# The per-call token budget (the plan §6, the ruled
# figure): no single request under the cycle contract
# may exceed this many estimated tokens — half the
# proven 8,000-token minute on the proof route, so a
# single call always stands legal on its own and two
# colliding cannot cross the limit. The budget binds
# the estimate of the whole REQUEST as the adapter
# constructs it — contract framing, system message,
# the rendered package, and in native mode the
# offered tool definitions all inside the estimate
# (the loop estimates over the adapter's rendered
# request where the adapter can render it; the §6
# accounting correction, 2026-11-26). The package's
# committed core — its canonical serialization, the
# one form the loop, the driver, the checker and the
# rehearsal all reproduce byte-identically from the
# record — remains the record's package figure, and
# the driver's call ledger records the captures' true
# wire bytes beside both estimates so every figure
# stands in the run's report.
PER_CALL_TOKEN_BUDGET = 4000

# The road (the §6 amendment, accepted by the
# director 2026-11-26 01:43 MST with the examiner's
# refinements; BUILD-SCOPE-SECTION6-ROAD-2026-11-26):
# the successor regime to the per-call budget above.
# The budget figure stands for the contracts sealed
# under it — their records keep their meaning — and
# is retired from any assembly whose sealed record
# declares the road: under the road, requests are
# COUNTED with a matched tokenizer over the rendered
# conversation, PACED against the route's shared
# token bucket (a call waits; it is never refused
# for its size), tool results over the spill
# threshold ride as references, presented material
# sheds at the sealed fractions of the model's
# window, and the run's spend is bounded by the
# allocation the office seals at generation — the
# worker cannot enlarge it. The road declaration
# seals beside the other declarations, outside the
# record's canonical hash fields, in exactly this
# shape: {"contract": ROAD_CONTRACT_V1,
# "allocation_tokens": a positive int,
# "window_tokens": a positive int, "basis": the
# office's stated basis for the allocation}.
ROAD_CONTRACT_V1 = "paced-v1"
# A tool result (or a presented block's content)
# over this many counted tokens does not ride
# whole in a package under the road; the package
# carries its reference and a preview instead (the
# examiner's figures, 2026-11-26).
ROAD_SPILL_THRESHOLD_TOKENS = 4096
ROAD_SPILL_PREVIEW_TOKENS = 512
# The shedding ladder's rungs, as fractions of the
# sealed window: shedding begins at the first,
# and no request is admitted at or past the
# second (the examiner's figures, 2026-11-26).
ROAD_SHED_START_FRACTION = 0.70
ROAD_SHED_HARD_FRACTION = 0.80
# The bounded output allowance reserved with every
# call's counted input (the examiner's requirement:
# output is reserved separately, before dispatch,
# and reconciled against the provider's figure).
ROAD_OUTPUT_ALLOWANCE_TOKENS = 2048


def road_problem(road):
    """The sealed road declaration's shape, or a
    problem naming why it does not stand: a dict
    naming exactly its contract, its allocation,
    its window and its basis — the contract the
    road's one version, the allocation and window
    positive integers, the basis the office's
    stated words. Anything else seals no road."""
    if not isinstance(road, dict) or \
            set(road) != {"contract", "allocation_tokens",
                          "window_tokens", "basis"}:
        return ("a road declaration names exactly its "
                "contract, its allocation, its window "
                "and its basis")
    if road.get("contract") != ROAD_CONTRACT_V1:
        return "the road declaration's contract is not " \
            "the road's sealed version"
    for key in ("allocation_tokens", "window_tokens"):
        value = road.get(key)
        if not isinstance(value, int) or \
                isinstance(value, bool) or value <= 0:
            return (f"the road declaration's {key} is "
                    "not a positive integer")
    if not isinstance(road.get("basis"), str) or \
            not road.get("basis"):
        return "the road declaration's basis is not " \
            "the office's stated words"
    return None


def tree_problem(tree):
    """The sealed tree declaration's shape, or a
    problem naming why it does not stand: a dict
    naming exactly its contract, its title and its
    nodes — the contract the tree's one version, the
    title the job's name in the office's words, the
    nodes the walk's steps in order. A node names
    exactly its id, its label, its kind, the nodes
    it depends on and its workaround text; a gather
    node names its source as well, and no other kind
    does. Kinds are the walk's own: onboarding,
    gather, summarize, deliver. Ids stand unique;
    every dependency names a node that stands.
    Anything else seals no tree."""
    if not isinstance(tree, dict) or \
            set(tree) != {"contract", "title", "nodes"}:
        return ("a tree declaration names exactly its "
                "contract, its title and its nodes")
    if tree.get("contract") != TREE_CONTRACT_V1:
        return "the tree declaration's contract is not " \
            "the tree's sealed version"
    if not isinstance(tree.get("title"), str) or \
            not tree.get("title"):
        return "the tree declaration's title is not " \
            "the job's stated name"
    nodes = tree.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return "the tree declaration's nodes do not stand"
    kinds = ("onboarding", "gather", "summarize",
             "deliver")
    seen = set()
    for node in nodes:
        if not isinstance(node, dict):
            return "a tree node does not stand"
        keys = {"id", "label", "kind", "depends_on",
                "workaround"}
        if node.get("kind") == "gather":
            keys.add("source")
        if set(node) != keys:
            return ("a tree node names exactly its id, "
                    "its label, its kind, its dependencies "
                    "and its workaround — a gather node "
                    "its source as well, no other kind")
        if not isinstance(node.get("id"), str) or \
                not node.get("id") or \
                node.get("id") in seen:
            return "a tree node's id does not stand " \
                "unique"
        seen.add(node.get("id"))
        if not isinstance(node.get("label"), str) or \
                not node.get("label"):
            return "a tree node's label does not stand"
        if node.get("kind") not in kinds:
            return "a tree node's kind is not one of " \
                "the walk's kinds"
        if node.get("kind") == "gather" and \
                (not isinstance(node.get("source"), str)
                 or not node.get("source")):
            return "a gather node names no source"
        depends = node.get("depends_on")
        if not isinstance(depends, list) or \
                any(not isinstance(dep, str)
                    for dep in depends):
            return "a tree node's dependencies do " \
                "not stand"
        if not isinstance(node.get("workaround"), str):
            return "a tree node's workaround does " \
                "not stand"
    for node in nodes:
        for dep in node.get("depends_on"):
            if dep not in seen:
                return ("a tree node depends on a node "
                        "that does not stand")
    return None


def estimate_tokens(serialized_bytes):
    """The one token estimator (the plan §6): the
    estimated tokens of a serialized request of
    `serialized_bytes` bytes — ceil(bytes / 4), the
    observed ratio on this route being ≈ 4.06
    bytes/token (INDEX 577), so the division errs, if
    at all, toward caution. An estimator, stated as
    one: the provider's own usage figures, where a
    response carries them, are recorded alongside and
    govern retrospectively."""
    return -(-int(serialized_bytes) // 4)


def split_lines(data):
    """The lines of a byte string, as the retrieval
    contract counts them (the executor's own rule): a
    line is the bytes up to and including its newline;
    the final line may lack one. Returns the lines'
    raw bytes, in order."""
    lines = []
    start = 0
    while start < len(data):
        nl = data.find(b"\n", start)
        if nl == -1:
            lines.append(data[start:])
            break
        lines.append(data[start:nl + 1])
        start = nl + 1
    return lines


def compute_block_map(addresses, contents,
                      ceiling=BLOCK_CEILING_BYTES):
    """The office's portioning of the declared
    evidence files into travel blocks (the plan §3):
    deterministic — the same bytes and ceiling yield
    the same map. `addresses` in declaration order;
    `contents` maps each address to its bytes. Each
    file is portioned BY LINES (split_lines' rule):
    lines accumulate into a block while its content
    stays within the ceiling; a single line longer
    than the ceiling is its own block (the line is
    the portioning unit and is never split). A file
    portioned into exactly one block names no line
    range (line_start/line_end None — the whole
    file); a file in several blocks names each
    block's inclusive 1-based range, the ranges
    contiguous and together covering [1..T]. An empty
    file is one whole-file block of zero bytes. Block
    ids run B1.. in declaration order across files."""
    blocks = []
    number = 0
    for address in addresses:
        data = contents[address]
        lines = split_lines(data)
        ranges = []
        current = []
        current_bytes = 0
        for line in lines:
            if current and \
                    current_bytes + len(line) > ceiling:
                ranges.append(current)
                current = []
                current_bytes = 0
            current.append(line)
            current_bytes += len(line)
        if current or not ranges:
            ranges.append(current)
        whole = len(ranges) == 1
        position = 1
        for group in ranges:
            number += 1
            content = b"".join(group)
            line_count = len(group)
            blocks.append({
                "block_id": f"B{number}",
                "address": address,
                "line_start": None if whole
                else position,
                "line_end": None if whole
                else position + line_count - 1,
                "content_bytes": len(content),
                "content_sha256": sha256_hex(content)})
            position += line_count
    return blocks


def block_map_problem(block_map, addresses,
                      ceiling=BLOCK_CEILING_BYTES):
    """The sealed block map's internal consistency, or
    None where it stands well-formed against the
    declared evidence addresses: the map is a list of
    blocks in declaration order (ids B1.. in order),
    each naming exactly its id, its file, its line
    range (both null for a whole-file block, both
    standing otherwise), its content's byte count and
    SHA-256; per file, the blocks stand in range
    order, contiguous from line 1 with no gap and no
    overlap, a whole-file block standing alone; and
    no block's content exceeds the ceiling unless the
    block is a single line (the portioning unit is
    never split — its size is the line's own). The
    map's truth against the files' actual bytes is
    the checker's derivation from the stocked files;
    this rule governs the seal's shape, which is what
    generation can know."""
    if not isinstance(block_map, list) or not block_map:
        return ("the block map is not a non-empty list "
                "of blocks")
    if not isinstance(addresses, list) or not addresses:
        return ("the declared evidence names no "
                "addresses for the block map to portion")
    expected_keys = {"block_id", "address", "line_start",
                     "line_end", "content_bytes",
                     "content_sha256"}
    by_file = {}
    for index, block in enumerate(block_map):
        if not isinstance(block, dict) or \
                set(block) != expected_keys:
            return ("a block in the map does not name "
                    "exactly its id, its file, its line "
                    "range, its content's byte count and "
                    "its SHA-256")
        if block.get("block_id") != f"B{index + 1}":
            return ("the block map's ids do not run "
                    "B1.. in declaration order")
        address = block.get("address")
        if address not in addresses:
            return ("a block names a file the declared "
                    "evidence does not")
        start = block.get("line_start")
        end = block.get("line_end")
        size = block.get("content_bytes")
        digest = block.get("content_sha256")
        if not isinstance(size, int) or \
                isinstance(size, bool) or size < 0:
            return ("a block's content byte count does "
                    "not stand")
        if not isinstance(digest, str) or \
                len(digest) != 64:
            return ("a block's content SHA-256 does "
                    "not stand")
        if (start is None) != (end is None):
            return ("a block's line range stands "
                    "half-named (both bounds, or "
                    "neither for a whole file)")
        if start is not None and (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
                or start < 1 or end < start):
            return ("a block's line range does not "
                    "stand (an inclusive range from "
                    "line 1 up)")
        by_file.setdefault(address, []).append(block)
    if [b["address"] for b in block_map] != \
            [a for a in addresses
             for _ in by_file.get(a, [])]:
        return ("the block map's files do not stand "
                "in declaration order")
    for address in addresses:
        mine = by_file.get(address)
        if not mine:
            return ("the block map portions no block "
                    "of a declared evidence file")
        if len(mine) == 1:
            only = mine[0]
            if only.get("line_start") is not None:
                return ("a file portioned into one "
                        "block names a line range; a "
                        "whole-file block names none")
            continue
        position = 1
        for block in mine:
            if block.get("line_start") != position:
                return ("a file's blocks do not stand "
                        "contiguous from line 1 (a gap "
                        "or an overlap stands in the "
                        "map)")
            if block["content_bytes"] > ceiling and \
                    block["line_start"] != block["line_end"]:
                return ("a block's content exceeds "
                        "the ceiling and is not a "
                        "single line")
            position = block["line_end"] + 1
    # A whole-file block over the ceiling stands or
    # falls on the bytes (a single long line portions
    # to exactly this shape; so does a mis-portioned
    # multi-line file) — the checker's re-derivation
    # from the stocked files is the byte-truth check;
    # the seal's shape alone cannot tell them apart.
    return None


def compute_file_map(block_map):
    """The file grouping of a sealed block map (the
    file-grain successor contract, office-cycle-v8):
    the map's blocks grouped under their files, in
    declaration order — file ids F1.. in the order
    the files first stand in the map, each group
    naming its file's address and its blocks' ids in
    map order. Deterministic: the same block map
    yields the same grouping. The grouping is the
    walk's unit under v8; the blocks remain the
    evidence and carriage units inside their file."""
    files = []
    for block in block_map or []:
        if files and files[-1]["address"] == \
                block["address"]:
            files[-1]["block_ids"].append(
                block["block_id"])
        else:
            files.append({
                "file_id": f"F{len(files) + 1}",
                "address": block["address"],
                "block_ids": [block["block_id"]]})
    return files


def file_map_problem(file_map, block_map):
    """The sealed file grouping's consistency against
    the sealed block map it groups, or None where it
    stands: a list of groups F1.. in order, each
    naming exactly its id, its file and its blocks'
    ids; the groups partition the block map whole —
    every block in exactly one group, the groups in
    the map's own order, each block under the group
    of its own file. A grouping that does not stand
    against the map seals no file-grain walk."""
    if not isinstance(block_map, list) or not block_map:
        return ("the block map the grouping answers "
                "does not stand")
    if not isinstance(file_map, list) or not file_map:
        return ("the file grouping is not a non-empty "
                "list of files")
    by_id = {block["block_id"]: block
             for block in block_map}
    seen = []
    for index, group in enumerate(file_map):
        if not isinstance(group, dict) or \
                set(group) != {"file_id", "address",
                               "block_ids"}:
            return ("a file group does not name "
                    "exactly its id, its file and its "
                    "blocks' ids")
        if group.get("file_id") != f"F{index + 1}":
            return ("the file grouping's ids do not "
                    "run F1.. in declaration order")
        ids = group.get("block_ids")
        if not isinstance(ids, list) or not ids:
            return ("a file group names no blocks")
        for block_id in ids:
            block = by_id.get(block_id)
            if block is None:
                return ("a file group names a block "
                        "the block map does not")
            if block["address"] != group["address"]:
                return ("a file group names a block "
                        "of another file")
            seen.append(block_id)
    if seen != [block["block_id"] for block in block_map]:
        return ("the file grouping does not partition "
                "the block map whole, in its order")
    return None
# The onboarding's stages, in the order the wakes walk
# them: the iteration number (1-based) selects the stage —
# iterations 1..4 walk memory, case, files, task; every
# later wake is a dashboard.
PRESENTATION_STAGES = ("memory", "case", "files", "task",
                       "dashboard")
SEARCH_PAGE_LINE_CAP = 40
RETRIEVAL_TOOLS = frozenset({
    "sandbox.list", "sandbox.read_range", "sandbox.search",
    "sandbox.read"})
SOURCE_SCOPE_PREFIX = "sources"
SCRATCH_SCOPE_PREFIX = "scratch"

# The room-exec configuration's contract data (demonstration
# preparation paper §2/§3.2; gate 4): the registry version an
# assembly declaring the exec catalogue contract is dispatched
# and catalogued under; the contract value its sealed generated
# record declares; and the tool the contract governs — the
# worker's own execution tool, offered under the name and the
# shape its preserved generations used (Track A, INDEX 433):
# `container.exec`, arguments an object whose `cmd` is an array
# of strings, no other fields required. The doorway's check for
# this tool is the grant and the shape alone (the paper §2.2):
# its ceiling keys are therefore empty — a grant's scope ceiling
# for it is the empty object, and any ceiling key fails closed —
# and its parameter contract is the cmd array's form, which
# check_ceiling enforces below. What a command may do is
# governed by the room's walls, never by this policy.
EXEC_REGISTRY_VERSION = "tool-registry-v4"
EXEC_CATALOGUE_CONTRACT = "exec-v4"
EXEC_TOOLS = frozenset({"container.exec"})


def retrieval_authority(path):
    """The authority path a sandbox path falls under, or
    None: "source" for a path under sources/, "scratch" for
    a path under scratch/, and None anywhere else — a path
    under neither scope is admitted by no authority path
    (retrieval scope, boundary enforcement). Pure, of the
    path only."""
    if not isinstance(path, str):
        return None
    if path.startswith(SOURCE_SCOPE_PREFIX + "/"):
        return "source"
    if path.startswith(SCRATCH_SCOPE_PREFIX + "/"):
        return "scratch"
    return None


def boundary_member(boundary, path) -> bool:
    """Whether a path is a member of a case's sealed evidence
    boundary. The boundary names material ids (a list of
    strings, as the office seals them); an id names its path
    either exactly or as its leading field — the sealing
    convention names the path, then the material's hash, in
    the one id. Pure, of the two values."""
    if not isinstance(boundary, list) or \
            not isinstance(path, str):
        return False
    for item in boundary:
        if item == path:
            return True
        if isinstance(item, str) and \
                item.startswith(path + " "):
            return True
    return False


def list_authority(path):
    """sandbox.list's authority path (round ten, INDEX
    552): the standing retrieval authority, extended at
    exactly one point — the bare granted prefixes
    themselves ("sources", "scratch"), which
    retrieval_authority does not admit because its paths
    lie strictly under a scope. Listing a directory is
    the one operation whose path may BE the scope. The
    path is canonicalised first — exactly one trailing
    slash stripped — as the ceiling canonicalises it,
    so the directory's two spellings share the one
    authority. Every other retrieval operation keeps
    the strict shape."""
    if isinstance(path, str) and len(path) > 1 \
            and path.endswith("/"):
        path = path[:-1]
    if path == SOURCE_SCOPE_PREFIX:
        return "source"
    if path == SCRATCH_SCOPE_PREFIX:
        return "scratch"
    return retrieval_authority(path)


def boundary_member_for_list(boundary, path) -> bool:
    """Whether a sandbox.list path stands within a
    case's sealed evidence boundary (round ten): a file
    path by the standing membership; a directory — a
    scope prefix itself, in canonical form — where the
    boundary names material under it: the listing shows
    only what stands in the directory, and the
    boundary's members under it are exactly what may be
    seen."""
    if boundary_member(boundary, path):
        return True
    if path not in (SOURCE_SCOPE_PREFIX,
                    SCRATCH_SCOPE_PREFIX) or \
            not isinstance(boundary, list):
        return False
    prefix = path + "/"
    for item in boundary:
        if isinstance(item, str) and \
                item.split(" ")[0].startswith(prefix):
            return True
    return False

# sandbox.flaky's modes (scope point 6): the first three are
# the outcome shapes; the fourth performs the operation and
# loses the report — execution happened, the outcome is what
# never arrives.
FLAKY_MODES = ("succeed", "fail", "hang-past-deadline",
               "execute-but-lose-the-report")

# The v1 view: the registry exactly as Piece A2 settled it.
_TOOLS_V1 = _freeze({
    "sandbox.write": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "content"},
    },
    "sandbox.read": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
    },
    "sandbox.flaky": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"mode", "path", "content", "hang_seconds"},
    },
})

# The v2 view: v1's ceiling contract, unchanged, plus the
# worker-facing layer (Piece A3-CAT): a plain description of
# what the tool does and returns, and a parameter schema —
# each parameter's name, whether it is required, and its
# meaning. The parameter lists name exactly the tool's
# param_keys; the A2 suite's agreement battery witnesses the
# two copies agree on all of it, under both versions.
_TOOLS_V2 = _freeze({
    "sandbox.write": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "content"},
        "description":
            "Write a text file inside the sandbox: creates "
            "the file at the given path (with any folders it "
            "needs) or replaces it, storing exactly the given "
            "content. Returns the path written and the number "
            "of bytes stored.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
            {"name": "content", "required": True,
             "meaning": "the text to store in the file"},
        ],
    },
    "sandbox.read": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
        "description":
            "Read a text file inside the sandbox. Returns "
            "the file's path and its full text content.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
        ],
    },
    "sandbox.flaky": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"mode", "path", "content",
                       "hang_seconds"},
        "description":
            "A test tool whose behaviour its mode parameter "
            "sets, so uncertain outcomes are exercised for "
            "real: 'succeed' performs (writing the file when "
            "a path is given) and reports its result; 'fail' "
            "fails; 'hang-past-deadline' runs past the "
            "deadline, so its outcome is recorded uncertain; "
            "'execute-but-lose-the-report' performs the "
            "operation but its report never arrives, so its "
            "outcome is recorded uncertain. Returns the mode, "
            "and the write's result when it wrote.",
        "parameters": [
            {"name": "mode", "required": True,
             "meaning": "one of 'succeed', 'fail', "
                        "'hang-past-deadline', "
                        "'execute-but-lose-the-report'"},
            {"name": "path", "required": False,
             "meaning": "a file path inside the sandbox to "
                        "write, for the modes that write"},
            {"name": "content", "required": False,
             "meaning": "the text to store when writing"},
            {"name": "hang_seconds", "required": False,
             "meaning": "how long the 'hang-past-deadline' "
                        "mode runs, in seconds (a positive "
                        "number)"},
        ],
    },
})

# The v3 view (retrieval piece): v2's entries for the
# standing tools, unchanged word for word, plus the three
# retrieval tools with their worker-facing layers. A v3
# assembly's catalogue therefore describes its standing
# tools exactly as v2 did, and its retrieval tools in the
# same style.
_TOOLS_V3 = _freeze({
    "sandbox.write": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "content"},
        "description":
            "Write a text file inside the sandbox: creates "
            "the file at the given path (with any folders it "
            "needs) or replaces it, storing exactly the given "
            "content. Returns the path written and the number "
            "of bytes stored.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
            {"name": "content", "required": True,
             "meaning": "the text to store in the file"},
        ],
    },
    "sandbox.read": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
        "description":
            "Read a text file inside the sandbox. Returns "
            "the file's path and its full text content.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
        ],
    },
    "sandbox.flaky": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"mode", "path", "content",
                       "hang_seconds"},
        "description":
            "A test tool whose behaviour its mode parameter "
            "sets, so uncertain outcomes are exercised for "
            "real: 'succeed' performs (writing the file when "
            "a path is given) and reports its result; 'fail' "
            "fails; 'hang-past-deadline' runs past the "
            "deadline, so its outcome is recorded uncertain; "
            "'execute-but-lose-the-report' performs the "
            "operation but its report never arrives, so its "
            "outcome is recorded uncertain. Returns the mode, "
            "and the write's result when it wrote.",
        "parameters": [
            {"name": "mode", "required": True,
             "meaning": "one of 'succeed', 'fail', "
                        "'hang-past-deadline', "
                        "'execute-but-lose-the-report'"},
            {"name": "path", "required": False,
             "meaning": "a file path inside the sandbox to "
                        "write, for the modes that write"},
            {"name": "content", "required": False,
             "meaning": "the text to store when writing"},
            {"name": "hang_seconds", "required": False,
             "meaning": "how long the 'hang-past-deadline' "
                        "mode runs, in seconds (a positive "
                        "number)"},
        ],
    },
    "sandbox.list": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
        "description":
            "List what stands at a path inside the sandbox "
            "without returning any file's contents. On a "
            "file: its structure — its byte size, its line "
            "count, and — for markdown or text files — its "
            "headings with their line numbers. On a "
            "directory — a granted prefix itself, such as "
            "sources, spelled with or without a trailing "
            "slash: its entries — each entry's address, "
            "whether it is a file or a directory, and each "
            "file's byte size. The map is returned as the "
            "result's content. Use it to discover what "
            "stands where before retrieving any of it.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the path inside the sandbox, "
                        "relative, under the grant's prefix — "
                        "a file's path, or a granted "
                        "directory's own path"},
        ],
    },
    "sandbox.read_range": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "start_line", "end_line",
                       "heading", "byte_start", "byte_end"},
        "description":
            "Retrieve a bounded slice of a text file inside "
            "the sandbox: the lines of an inclusive 1-based "
            "line range, or one heading's section (from its "
            "heading line to just before the next heading of "
            "the same or higher level), or — for a "
            "single-line range — a byte window of that line. "
            "A result is never larger than 12,000 bytes: a "
            "range whose content exceeds the ceiling is "
            "refused with the bound named, and nothing "
            "partial is returned. A heading naming more "
            "than one heading is refused as ambiguous, "
            "naming the matches and their line numbers. A "
            "byte window may span at most 11,997 bytes; the "
            "slice served is aligned to character "
            "boundaries, and the window actually served is "
            "recorded in the result.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
            {"name": "start_line", "required": False,
             "meaning": "the range's first line, numbered "
                        "from 1; given with end_line when no "
                        "heading is named"},
            {"name": "end_line", "required": False,
             "meaning": "the range's last line, inclusive; "
                        "given with start_line when no "
                        "heading is named"},
            {"name": "heading", "required": False,
             "meaning": "the exact text of the one heading "
                        "whose section to retrieve; refused "
                        "when it matches more than one "
                        "heading"},
            {"name": "byte_start", "required": False,
             "meaning": "for a single-line range, the byte "
                        "window's start within the line, "
                        "0-based and inclusive; given with "
                        "byte_end"},
            {"name": "byte_end", "required": False,
             "meaning": "for a single-line range, the byte "
                        "window's end within the line, "
                        "0-based and exclusive; given with "
                        "byte_start"},
        ],
    },
    "sandbox.search": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"query", "path", "offset"},
        "description":
            "Search permitted text inside the sandbox for a "
            "query string (an exact, case-sensitive "
            "substring) and return matching passages — each "
            "matching line with up to two lines of context, "
            "labelled with its file and line numbers. "
            "Matches are ordered by path, then by line, and "
            "returned in deterministic pages under the "
            "result ceiling and a 40-line page cap: every "
            "result states the total match count, how many "
            "matches it returns, and — where more remain — "
            "the continuation offset to pass back as the "
            "offset parameter for the next page. A matching "
            "line too large to return even on its own is "
            "reported as a stub — its path, line number and "
            "byte size, with no content — which "
            "sandbox.read_range can fetch in byte-window "
            "slices. With no path, the search covers the "
            "case's sealed source material; with a path, it "
            "searches that one file.",
        "parameters": [
            {"name": "query", "required": True,
             "meaning": "the exact text to search for "
                        "(case-sensitive)"},
            {"name": "path", "required": False,
             "meaning": "one file to search, under the "
                        "grant's prefix; without it, the "
                        "sealed source material is searched"},
            {"name": "offset", "required": False,
             "meaning": "the continuation offset a previous "
                        "search result returned: the match "
                        "index the next page starts at"},
        ],
    },
})

# The v4 view (room-exec configuration, gate 4): v3's entries
# whole and unchanged — taken from the frozen v3 view itself, so
# the two views cannot drift — plus the one new tool. An
# assembly declaring the exec catalogue contract is catalogued
# and dispatched under v4, exactly as a retrieval assembly is
# under v3; every other assembly keeps the version it has
# always had.
_TOOLS_V4 = _freeze({
    **_TOOLS_V3,
    "container.exec": {
        "ceiling_keys": set(),
        "param_keys": {"cmd"},
        "description":
            "Execute one command inside your office — the "
            "sealed room stocked for this task — and return "
            "its result: the exit status, the captured "
            "output (bounded, with the full byte counts and "
            "any truncation flagged), what ended it, the "
            "CPU charged and the duration. Commands run "
            "with the working directory at /room/work: the "
            "sources stand under sources/, your own space "
            "is /room/scratch, and the deliverable is "
            "written there. Nothing outside the room is "
            "reachable from inside it.",
        "parameters": [
            {"name": "cmd", "required": True,
             "meaning": "the command to execute, as an "
                        "array of strings: the program "
                        "followed by its arguments"},
        ],
    },
})

# One registry view per version, v1 preserved immutable for
# historical verification (Piece A3-CAT settlement (a)/(c)) —
# the version map itself is frozen with its views, so a
# version can neither be altered nor added in-process.
_REGISTRIES = MappingProxyType({
    "tool-registry-v1": _TOOLS_V1,
    "tool-registry-v2": _TOOLS_V2,
    "tool-registry-v3": _TOOLS_V3,
    "tool-registry-v4": _TOOLS_V4,
})

# The current view: what an unversioned call applies. This
# is the frozen v2 view itself, not a mutable alias to it.
_TOOLS = _TOOLS_V2


def known_version(version) -> bool:
    """Whether the registry holds a view under this version
    at all. A version nobody holds is unverifiable: callers
    fail closed or report the inability explicitly, never
    silently apply another version."""
    return version in _REGISTRIES


def _view(version):
    """The registry view a call applies: the current version
    where none is named; None for a version nobody holds."""
    if version is None:
        version = REGISTRY_VERSION
    return _REGISTRIES.get(version)


def registered(tool, version=None) -> bool:
    """Whether the registry knows this tool at all, under the
    named version (the current version where none is named).
    An unregistered tool is refused at the doorway and
    divergent in the checker: registration is the precondition
    of a grant meaning anything."""
    view = _view(version)
    return view is not None and tool in view


def worker_facing(tool, version=None):
    """The tool's worker-facing layer under the named
    version — {"description": ..., "parameters": [...]} —
    or None where the tool is unknown under that version or
    its entry carries no complete layer. v1 entries carry
    none: under v1 no catalogue can be derived, which is a
    fact about v1, not a defect in it. The result is a copy;
    the registry's own data never leaves this module by
    reference."""
    view = _view(version)
    if view is None:
        return None
    spec = view.get(tool)
    if spec is None:
        return None
    description = spec.get("description")
    parameters = spec.get("parameters")
    if not isinstance(description, str) or \
            not description.strip() or \
            not isinstance(parameters, (list, tuple)):
        return None
    names = set()
    for param in parameters:
        if not isinstance(param, Mapping) or \
                set(param) != {"name", "required", "meaning"} \
                or not isinstance(param.get("name"), str) \
                or not param["name"] \
                or not isinstance(param.get("required"), bool) \
                or not isinstance(param.get("meaning"), str) \
                or not param["meaning"].strip():
            return None
        names.add(param["name"])
    if names != set(spec["param_keys"]):
        return None
    # A plain, mutable copy, rebuilt field by field: the
    # frozen registry's own structures never leave by
    # reference (and cannot be deep-copied in any case).
    return {"description": description,
            "parameters": [
                {"name": param["name"],
                 "required": param["required"],
                 "meaning": param["meaning"]}
                for param in parameters]}


def request_fingerprint(tool, parameters) -> str:
    """The canonical fingerprint a request identity binds to
    (R47, scope point 3): SHA-256 over the fabric canonical
    form of the tool and the parameters together. Same tool,
    same parameters — same fingerprint, wherever computed."""
    return sha256_hex(canonical(
        {"tool": tool, "parameters": parameters}))


def _path_problem(path, prefix, allow_prefix_itself=False):
    """Why a sandbox path may not be used, or None: the path
    is a relative, normalised file path inside the sandbox —
    no absolute paths, no empty, dot or dot-dot segments — and,
    where the ceiling names a prefix, it lies strictly under
    that prefix. Where allow_prefix_itself stands (sandbox.list's
    directory form, round ten): the path may also BE the prefix
    itself — the granted directory's own address."""
    if not isinstance(path, str) or not path:
        return "the path is not a non-empty string"
    if path.startswith("/"):
        return f"path {path!r} is absolute; sandbox paths are " \
            "relative to the sandbox directory"
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return f"path {path!r} is not a normalised relative " \
            "path inside the sandbox"
    if prefix is not None:
        if not isinstance(prefix, str) or not prefix:
            return "the ceiling's path_prefix is not a " \
                "non-empty string"
        prefix_parts = [p for p in prefix.split("/") if p]
        if parts[:len(prefix_parts)] != prefix_parts or \
                len(parts) < len(prefix_parts) or \
                (len(parts) == len(prefix_parts)
                 and not allow_prefix_itself):
            return f"path {path!r} lies outside the grant's " \
                f"ceiling prefix {prefix!r}"
    return None


def _read_range_problem(parameters):
    """Why sandbox.read_range's parameters may not be used,
    or None (retrieval scope §2): exactly one selection — a
    heading, or an inclusive 1-based line range — and a byte
    window only on a single-line range, spanning at most the
    per-result ceiling minus 3 bytes, so the served slice
    (its end extended at most 3 bytes to a character
    boundary) never exceeds the ceiling. Pure, of the
    parameters only; the same result at the doorway and in
    the checker."""
    heading = parameters.get("heading")
    if heading is not None:
        if not isinstance(heading, str) or not heading:
            return ("sandbox.read_range's heading is not a "
                    "non-empty string")
        for key in ("start_line", "end_line", "byte_start",
                    "byte_end"):
            if key in parameters:
                return (f"sandbox.read_range names a heading "
                        f"and {key}; a request selects by "
                        f"heading or by line range, never both")
        return None
    start = parameters.get("start_line")
    end = parameters.get("end_line")
    if start is None or end is None:
        return ("sandbox.read_range requires a heading, or "
                "both start_line and end_line")
    for name, value in (("start_line", start),
                        ("end_line", end)):
        if isinstance(value, bool) or \
                not isinstance(value, int) or value < 1:
            return (f"sandbox.read_range's {name} is not a "
                    f"positive integer (lines are numbered "
                    f"from 1)")
    if end < start:
        return ("sandbox.read_range's end_line precedes its "
                "start_line")
    has_start = "byte_start" in parameters
    has_end = "byte_end" in parameters
    if has_start != has_end:
        return ("sandbox.read_range's byte window names both "
                "byte_start and byte_end, or neither")
    if has_start:
        if start != end:
            return ("sandbox.read_range's byte window "
                    "applies to a single-line range only")
        byte_start = parameters["byte_start"]
        byte_end = parameters["byte_end"]
        for name, value in (("byte_start", byte_start),
                            ("byte_end", byte_end)):
            if isinstance(value, bool) or \
                    not isinstance(value, int) or value < 0:
                return (f"sandbox.read_range's {name} is not "
                        f"a non-negative integer")
        if byte_end <= byte_start:
            return ("sandbox.read_range's byte_end does not "
                    "exceed its byte_start")
        if byte_end - byte_start > \
                RETRIEVAL_RESULT_CEILING - 3:
            return (f"sandbox.read_range's byte window spans "
                    f"{byte_end - byte_start} bytes; the "
                    f"maximum requestable window is "
                    f"{RETRIEVAL_RESULT_CEILING - 3} bytes "
                    f"(the per-result ceiling minus 3, so "
                    f"the served slice — its end extended at "
                    f"most 3 bytes to a character boundary — "
                    f"never exceeds the ceiling)")
    return None


def check_ceiling(tool, ceiling, parameters, version=None):
    """The pure ceiling contract: (ok, ground). Applies the
    named tool's registered checker to the grant's ceiling and
    the request's parameters, under the named version's view
    (the current version where none is named). Deterministic,
    fail-closed, no execution — the same result at the doorway
    and in the checker, or the piece is wrong. The ceiling
    behaviour is identical under v1 and v2 (A3-CAT changed
    only the worker-facing layer); a version nobody holds
    fails closed, naming itself."""
    if version is None:
        version = REGISTRY_VERSION
    view = _REGISTRIES.get(version)
    if view is None:
        return False, (f"registry version {version!r} is not "
                       f"a version this registry holds; the "
                       f"ceiling check fails closed")
    spec = view.get(tool)
    if spec is None:
        return False, (f"tool {tool!r} is not in the tool "
                       f"registry ({version}); an "
                       f"unregistered tool is refused")
    if not isinstance(ceiling, dict):
        return False, (f"the grant's scope ceiling for {tool} "
                       f"is not structured data; the ceiling "
                       f"check fails closed")
    for key in ceiling:
        if key not in spec["ceiling_keys"]:
            return False, (f"ceiling key {key!r} is not "
                           f"understood by {tool}'s checker; "
                           f"unknown constraint keys fail closed")
    if not isinstance(parameters, dict):
        return False, "the request's parameters are not an object"
    for key in parameters:
        if key not in spec["param_keys"]:
            return False, (f"parameter {key!r} is not a "
                           f"parameter of {tool}; unknown "
                           f"parameters fail closed")
    prefix = ceiling.get("path_prefix")
    if tool in ("sandbox.write", "sandbox.read"):
        if "path" not in parameters:
            return False, f"{tool} requires a path parameter"
        problem = _path_problem(parameters.get("path"), prefix)
        if problem is not None:
            return False, problem
        if tool == "sandbox.write" and \
                not isinstance(parameters.get("content"), str):
            return False, ("sandbox.write requires its content "
                           "parameter to be a string")
    elif tool == "sandbox.flaky":
        mode = parameters.get("mode")
        if mode not in FLAKY_MODES:
            return False, (f"sandbox.flaky's mode {mode!r} is "
                           f"not one of {list(FLAKY_MODES)}")
        if "path" in parameters:
            problem = _path_problem(parameters.get("path"),
                                    prefix)
            if problem is not None:
                return False, problem
            if "content" in parameters and \
                    not isinstance(parameters["content"], str):
                return False, ("sandbox.flaky's content "
                               "parameter is not a string")
        if "hang_seconds" in parameters:
            hang = parameters["hang_seconds"]
            if isinstance(hang, bool) or \
                    not isinstance(hang, (int, float)) or \
                    not hang > 0:
                return False, ("sandbox.flaky's hang_seconds "
                               "is not a positive number")
    elif tool == "sandbox.list":
        if "path" not in parameters:
            return False, "sandbox.list requires a path parameter"
        # The directory form (round ten): a list path is
        # canonicalised before the ceiling is applied —
        # exactly one trailing slash is stripped, so the
        # granted directory's two spellings ("sources" and
        # "sources/") meet the one governed route — and the
        # path may be the grant's prefix itself, the
        # directory's own address. Every other tool keeps
        # the strict shape: strictly under the prefix, no
        # spelling forgiven.
        list_path = parameters.get("path")
        if isinstance(list_path, str) and len(list_path) > 1 \
                and list_path.endswith("/"):
            list_path = list_path[:-1]
        problem = _path_problem(list_path, prefix,
                                allow_prefix_itself=True)
        if problem is not None:
            return False, problem
    elif tool == "sandbox.read_range":
        if "path" not in parameters:
            return False, ("sandbox.read_range requires a "
                           "path parameter")
        problem = _path_problem(parameters.get("path"), prefix)
        if problem is not None:
            return False, problem
        problem = _read_range_problem(parameters)
        if problem is not None:
            return False, problem
    elif tool == "sandbox.search":
        query = parameters.get("query")
        if not isinstance(query, str) or not query:
            return False, ("sandbox.search requires its query "
                           "parameter to be a non-empty string")
        if "path" in parameters:
            problem = _path_problem(parameters.get("path"),
                                    prefix)
            if problem is not None:
                return False, problem
        if "offset" in parameters:
            offset = parameters["offset"]
            if isinstance(offset, bool) or \
                    not isinstance(offset, int) or offset < 0:
                return False, ("sandbox.search's offset is "
                               "not a non-negative integer")
    elif tool == "container.exec":
        # The shape check, and the only one (demonstration
        # preparation paper §2.2): cmd present, an array of
        # strings. The command's contents are not policed
        # here or anywhere at the doorway — what it may do
        # is the room's governance, not the doorway's.
        cmd = parameters.get("cmd")
        if not isinstance(cmd, list) or not cmd:
            return False, ("container.exec requires its cmd "
                           "parameter to be a non-empty array "
                           "of strings")
        if any(not isinstance(part, str) for part in cmd):
            return False, ("container.exec's cmd array holds "
                           "a non-string element; every "
                           "element of cmd must be a string")
    return True, ""

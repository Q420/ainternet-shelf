#!/usr/bin/env python3
"""The first-worker DEMONSTRATION run — LIVE driver
(Track F, DEMONSTRATION-PREPARATION-2026-11-24.md §3).

One generated worker, its own execution tool
(`container.exec`, {cmd: [string, ...]}), a case-stocked
room, the NVIDIA route — driven live, once, under the
director's order: Ben, 2026-11-24 ~17:57 MST — "just run
it with nemotron, see how he reacts... lets start doing.
im done guessing."

The model pin is `nvidia/nemotron-3-nano-omni-30b-a3b-
reasoning` on the NVIDIA route, per the same order (the
paper §3.6 catalogue check found the fork's first-named
model, openai/gpt-oss-120b, absent from the route's
catalogue as returned to this account; the director
named Nemotron — the catalogue's hosted family — and
ordered the run). The pin is checked where the harness
has always checked it: the adapter's identify() result
is wrapped with the pin stop (first_worker_run.
make_pinned_identify), inside generation, before any
onboarding stands and long before activation. A
mismatch aborts the run before activation and is
reported in report.json as a FLAGGED CONFLICT — never a
substitution, never a fallback model.

The structure is the gate 4 rehearsal's, step for step —
stocking (stock_demo, the room held in THIS process and
destroyed at the end), commission, issue, the pre-
activation verification, the A1 lifecycle — with the
rehearsal's stub replaced by the route's real machinery:

- the adapter's typed calls travel the REAL connector
  transport (connector_transport.install_connector_
  transport), the same installation the rehearsal made,
  with the helper at the seam being a capture
  pass-through (below) delegating to the registered
  NVIDIA connector helper — the sanctioned Secure Vault
  credential path, exactly as every live run on this
  route has travelled it;
- the probe stage's raw call travels the REAL NVIDIA
  raw transport (nvidia_connector_transport.install_
  nvidia_connector_raw_call) through the same seam;
- the probe stage RUNS, live: the governed lifecycle's
  normative order puts it between generation and
  verification, and the checker requires its act. What
  the director's order replaces is the probe-PHASE
  JUDGEMENT — the examiner's post-probe mode decision.
  The judgement recorded here is the director's:
  adapter_mode native, its grounds the order itself,
  bound by hash to the order record filed beside the
  run (order-record.json). The probe's recommendation
  stands in the record as evidence; it does not decide
  this run's mode. The model's first live response is
  itself the delivery evidence (paper §2.1/§5 item 1).

Request captures (paper §2.4, hop 3): the rehearsal's
stub stood at the helper seam and recorded the exact
request bytes it was handed. The live seam's own
capture is the same placement: capture_helper.py,
written into the run directory by this driver, is a
pure pass-through at the documented helper seam (the
transports take the helper path as their parameter) —
it records the exact bytes it receives on stdin to
captures.jsonl (the rehearsal's record shape: mode,
model, index, SHA-256, byte count, base64), then invokes
the REAL connector helper with the same arguments and
bytes, the environment inherited whole (the transports'
NVIDIA_API_TIMEOUT allowance flows through), its stdout
and stderr inherited untouched, and exits with the real
helper's exit code. If the capture cannot be written,
the helper is never invoked: no unwitnessed transmitted
request. The wrapper observes; it alters nothing.

Pacing: NVIDIA pacing is unestablished — no source
states the route's limits, and the Groq route's
accounting does not transfer (paper §3.3/§5 item 5).
The loop's calls are therefore paced by the harness's
IterationPacer at a fixed 20-second minimum interval
between successive outbound iteration calls — an
operating choice of this driver, stated as such, not a
provider figure. Identify and probe calls precede the
loop and are not paced, as in the harness's paced runs.

Bounds are this driver's re-derived ones (the
freedom-first setup pass, 2026-11-24): DEMO_BOUNDS —
20 steps, 1,200 s activation deadline (the one
authoritative clock) — sized to the task as stocked,
with the derivation recorded beside the constant and
in every run report; the harness's standing
first_worker_run.BOUNDS (12 steps, 600 s) still govern
the rehearsals. The adapter's per-call span is the
paper §3.3 300 s; the room's envelope is the
stocking's declared one (paper §1.4).

The combined configuration (INDEX 476; Ben's
direction, 2026-11-24 ~18:48 MST: "we haven't actually
enabled him to pull the information that he needs.
That's our next step. Then we can have a full run."):
this driver now assembles the COMBINED grant surface —
container.exec, the retrieval four (sandbox.list,
sandbox.search, sandbox.read_range, sandbox.read)
under sources/ and under scratch/, and sandbox.write
under scratch/ — so the worker has two doors to the
same briefcase: his own execution tool in the room,
and the doorway's pull. The stocked sources are
staged into the executor's sandbox as well as the
room, hash-verified against the stocking manifest, so
a pull serves the released source set itself. The
case carries the glossary as its own component (Ben's
briefcase design, 2026-11-16): the pullable items by
their shelf addresses with a line each, and scratch/
as his writing space — his pull requests are made
from knowledge inside his case, not from prose alone.
The brief may land by either write path; collection
checks both resting places — the room's scratch and
the framework sandbox's scratch — and report.json
records which path he used, with both hashes when
both stand; the two are never merged. GRANTS_EXEC
below stands as the first two runs' configuration
(INDEX 472/474), kept for the record; the run seals
GRANTS_COMBINED.

Outputs land in live-demo/demo-nemotron1/ (the run
refuses a standing non-empty directory): run/ (the
record: run.db, run-export.json, responses/, claims/),
captures.jsonl, capture_helper.py, order-record.json,
stocking.json, room-state.json, terminal-readout.md,
brief.md (the collected deliverable, when one stands),
and report.json — derived matter summarising the
outcome, never the record itself. The independent
checker runs over the record at the end, as in every
prior run.

Run it:  PYTHONPATH=src python3 live-demo/demo_run.py
Dry:     PYTHONPATH=src python3 live-demo/demo_run.py \
             --verify-config
(--verify-config makes NO provider contact: it stocks
and destroys a room in a throwaway directory, builds
the assembly under a stub identity, installs the real
transports without invoking them, exercises the capture
seam against a local echo delegate, computes the
judgement payload the order will bind, and asserts the
whole configuration — printing PASS/FAIL per item and
a final VERIFY-CONFIG line. The probe stage, the
judgement's recording, and activation are live steps:
the lifecycle's normative order puts the probe between
generation and verification, and the probe is a
provider act.)
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
RIG = ROOT / "room" / "rig"
for _p in (str(SRC), str(HERE), str(RIG)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fabric.canonical import canonical  # noqa: E402

from framework import nemotron_names, tool_policy  # noqa: E402
from framework import road as road_mod  # noqa: E402
from framework.adapter import (  # noqa: E402
    AdapterFailure, OpenAICompatibleAdapter)
from framework.doorway import (  # noqa: E402
    Doorway, established_case_content)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.onboarding import (  # noqa: E402
    instance_onboarding_record)
from framework.record import (  # noqa: E402
    CONSTITUTION_HASH, FrameworkStore, assembly_record_hash)

from connector_transport import (  # noqa: E402
    install_connector_transport)
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call,
    install_groq_connector_transport)
from cloudflare_connector_transport import (  # noqa: E402
    install_cloudflare_connector_raw_call,
    install_cloudflare_connector_transport)
from nvidia_connector_transport import (  # noqa: E402
    install_nvidia_connector_raw_call)
from first_worker_run import (  # noqa: E402
    BOUNDS, CONNECTOR_HELPER, EXPECTED_MANIFEST_HASH,
    GROQ_CONNECTOR_HELPER, GROQ_ENDPOINT,
    RUN_ID, IterationPacer, ModelPinMismatchError, _act,
    _commission_brief, check_model_pin, export_store,
    make_pinned_identify, run_checker)

import room as room_mod  # noqa: E402
import stock_demo  # noqa: E402

# The Cloudflare route's constants (INDEX 563): the
# registered connector helper for the route (the
# sanctioned Secure Vault credential path, provider
# custom.cloudflare) and the account-bound Workers AI
# endpoint. The account id is the Pulse HQ account the
# vault's token sees — an identifier, not a credential.
CLOUDFLARE_CONNECTOR_HELPER = os.path.expanduser(
    "~/workspace/custom-connectors/custom.cloudflare/"
    "bin/cf_ai.py")
CLOUDFLARE_ACCOUNT_ID = "1c7b1bdeb7c8306a5c7cfdf6c4dee9cf"
CLOUDFLARE_MODEL = "@cf/zai-org/glm-4.7-flash"
CLOUDFLARE_ENDPOINT = (
    "https://api.cloudflare.com/client/v4/accounts/"
    f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{CLOUDFLARE_MODEL}")

# The occupant configuration (INDEX 560): the role,
# the case and the gates are occupant-neutral; what
# differs per occupant is the pin, the route, the
# judged mode, the transports and the operating bounds.
# DEMO_OCCUPANT selects the configuration, fail-closed
# in the harness's route-selection discipline: unset or
# empty preserves the Nemotron configuration — the
# default, byte-identical in behaviour — "quinn"
# selects the Qwen occupant, "glm" the Cloudflare
# occupant (INDEX 563) and "gptoss" the GPT-OSS
# occupant on Quinn's Groq route; any other value is
# refused, so a typo can never silently change the
# experiment.
def _resolve_occupant(raw):
    if raw is None or raw == "":
        return "nemotron"
    if raw == "quinn":
        return "quinn"
    if raw == "glm":
        return "glm"
    if raw == "gptoss":
        return "gptoss"
    raise ValueError(
        f"DEMO_OCCUPANT={raw!r} is not a recognised "
        f"occupant (expected unset for the Nemotron "
        f"configuration, 'quinn', 'glm' or 'gptoss'); "
        f"refusing to run")


OCCUPANT = _resolve_occupant(
    os.environ.get("DEMO_OCCUPANT"))
QUINN = OCCUPANT == "quinn"
GLM = OCCUPANT == "glm"
GPTOSS = OCCUPANT == "gptoss"


def _road_declaration():
    """The office's road seal for a run (the §6
    amendment, accepted 2026-11-26): the declaration
    the generation seals, or None where the run
    travels under the per-call budget as before.
    The road is built for two seats: the GPT-OSS
    occupant on Groq, whose limits stand measured
    (8,000 tokens per minute, 200,000 per rolling
    day, a 131,072-token window), and — at the
    director's call of 2026-11-26, after the Groq
    day pool stopped the GPT-OSS proof at its sixth
    call — the Nemotron occupant on the NVIDIA
    route, whose limits stand UNMEASURED: its seal
    carries the same allocation, its window is the
    office's working figure, and its bucket figures
    (set where the road attaches) are placeholders
    that do not bind, named as such in the basis —
    reservations, counting and accounting stand;
    pacing against a measured wall waits for the
    route's own measurement. The allocation is the
    office's seal for one run of the standing job —
    an opening and a handful of cycle calls at the
    sizes the road now counts, with headroom. The
    remaining occupants' roads are their own
    scopes, unbuilt."""
    if GPTOSS:
        return {
            "contract": tool_policy.ROAD_CONTRACT_V1,
            "allocation_tokens": 60000,
            "window_tokens": 131072,
            "basis": "the office's seal for one proof "
                     "run of the standing job (three "
                     "sources, one brief): the job's "
                     "measured shape under the road's "
                     "counting, with headroom, inside "
                     "the route's 200,000-token rolling "
                     "day pool"}
    if QUINN or GLM:
        return None
    return {
        "contract": tool_policy.ROAD_CONTRACT_V1,
        "allocation_tokens": 120000,
        "window_tokens": 131072,
        "basis": "the office's seal for one proof "
                 "run of the standing job on the "
                 "NVIDIA route, re-sealed at the "
                 "director's order of 2026-11-26 "
                 "after demo-nemotron7 measured the "
                 "job's shape on this seat: ten "
                 "calls consumed 64,117 tokens "
                 "(~6,400 a call, the reasoning "
                 "completions counted, as the "
                 "amendment's accounting rules) and "
                 "the walk needs roughly fourteen — "
                 "120,000 is that measured shape "
                 "with headroom. The route's limits "
                 "stand unmeasured, so the window "
                 "is the office's working figure "
                 "and the bucket's limits are "
                 "placeholders that do not bind — "
                 "what stands governed is the "
                 "counting, the reservations, the "
                 "spill and the sealed run budget"}

# The run's pin: the director's named model on the
# occupant's route (Ben's order, 2026-11-24, for
# Nemotron; Ben's direction, 2026-11-25, for Quinn
# and for the GPT-OSS occupant).
# No fallback, no alias, no automatic selection — a
# provider-reported identity that is not this string
# aborts the run before activation as a flagged
# conflict.
MODEL = ("qwen/qwen3.8-27b" if QUINN else
         "openai/gpt-oss-120b" if GPTOSS else
         CLOUDFLARE_MODEL if GLM else
         "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
ENDPOINT = (GROQ_ENDPOINT if (QUINN or GPTOSS) else
            CLOUDFLARE_ENDPOINT if GLM else
            "https://integrate.api.nvidia.com/v1/chat/"
            "completions")
ROUTE = ("groq" if (QUINN or GPTOSS) else
         "cloudflare" if GLM else "nvidia")

# The mode the occupant's order/direction judges:
# Nemotron native by the director's order; Quinn text
# by the director's direction — her run does not route
# through the Groq route's native path. The Cloudflare
# occupant text by the director's direction (INDEX
# 563): a new route whose native tool-calling has
# never been witnessed on the live path, and no
# finding about its native reach is made. The GPT-OSS
# occupant NATIVE under the director's direction of
# 2026-11-25 (the room rebuild: "Make it so", 15:02
# MST, and his addition at 15:03 — "We need to allow
# him to use his tools"): the BD-1 defect that stood
# in the way (INDEX 411-420 — the adapter's staged
# disable_tool_validation never reached the live wire
# on this route) is corrected in the Groq connector
# transport, which now carries the sealed tools, a
# call-permitting tool_choice and the flag exactly as
# staged on the actual outbound request; the seat is
# re-judged native on the corrected transport, the
# examiner's INDEX 300 text judgement standing
# superseded by the direction for this run.
ADAPTER_MODE = ("text" if (QUINN or GLM)
                else "native")

# The route's registered connector helper — the
# sanctioned Secure Vault credential path the capture
# seam delegates to.
DELEGATE_HELPER = (GROQ_CONNECTOR_HELPER
                   if (QUINN or GPTOSS)
                   else CLOUDFLARE_CONNECTOR_HELPER
                   if GLM else CONNECTOR_HELPER)
ROUTE_REPORT_LABEL = (
    "groq (live, via the registered connector helper "
    "through the capture seam)" if (QUINN or GPTOSS)
    else
    "cloudflare (live, via the registered connector "
    "helper through the capture seam)" if GLM else
    "nvidia (live, via the registered connector "
    "helper through the capture seam)")

# The office-declared identity (office-cycle-v8;
# the director's ruling of 2026-11-25 23:08 MST —
# "Get rid of that too"): under the file-grain
# contract the worker's launch carries NO identity
# call — the run's first call is the opening
# package. His identity stands in the record from
# the office's sealed assembly instead: the
# occupant configuration the office chose (the pin
# above, on its route), declared by the office at
# generation as this mapping — the generator
# accepts an identify mapping in place of a
# callable, and the onboarding records this
# declaration as the instance's identity. No
# provider self-report is claimed anywhere in a
# v8 record: the declaration is the office's word
# for the configuration it assembled, and the
# credential fingerprint binds it as it binds any
# declared identity.
OFFICE_IDENTITY_DECLARATION = {
    "declaration": (
        f"Office-declared occupant: {MODEL} on the "
        f"{ROUTE} route, assembled by the office "
        f"under office-cycle-v8 (the director's "
        f"ruling of 2026-11-25 23:08 MST — no "
        f"identity call stands in this launch; this "
        f"declaration is the office's, from the "
        f"sealed configuration, not a provider "
        f"self-report)."),
    "provider_model_id": MODEL}

DEMO_DIR = HERE / os.environ.get(
    "DEMO_RUN_DIR",
    "demo-quinn1" if QUINN else
    "demo-gptoss1" if GPTOSS else
    "demo-glm1" if GLM else "demo-nemotron1")

# The paper §3.3 adapter per-call span.
ADAPTER_TIMEOUT = 300.0

# Pacing between successive outbound iteration calls:
# this driver's operating choice (see the docstring) —
# NVIDIA pacing is unestablished and no provider figure
# is claimed for it. Quinn's interval is sized to the
# Groq free plan's published token cap (8,000 TPM):
# her wake packages run ~5-7K tokens, so successive
# calls must land in separate minute windows. The
# Cloudflare occupant's interval is courtesy only: the
# route's documented free text-generation ceiling is
# 300 RPM, far above anything this driver sends, and
# the budget that binds the route is its daily Neuron
# allowance, which pacing does not govern. The
# GPT-OSS occupant shares Quinn's interval — the same
# route and the same courtesy; its own per-model
# limits on this account are unread (see the bounds
# derivation).
PACING_INTERVAL_SECONDS = (65.0 if (QUINN or GPTOSS)
                           else 5.0 if GLM else 20.0)
PACING_NOTE = (
    "a fixed operating choice of this driver between "
    "successive outbound iteration calls, sized to "
    "the Groq free plan's published limits (8,000 "
    "TPM, 30 RPM): the wake packages run ~5-7K "
    "tokens, so successive calls land in separate "
    "minute windows; no finer provider figure is "
    "claimed" if QUINN else
    "a fixed operating choice of this driver between "
    "successive outbound iteration calls: the Groq "
    "route's pacing this driver already uses (65 s "
    "between calls, Quinn's configuration). No "
    "per-model figure for this model on this account "
    "is claimed — the account's authenticated limits "
    "for it have never been read, and whether they "
    "pass a full-working-set wake is the open "
    "question this run answers" if GPTOSS else
    "a fixed operating choice of this driver between "
    "successive outbound iteration calls, set as "
    "courtesy on a route whose documented free "
    "text-generation ceiling is 300 RPM: no survival "
    "spacing is needed, and the budget that binds "
    "this route is the free plan's daily Neuron "
    "allowance, which pacing does not govern"
    if GLM else
    "a fixed operating choice of this driver between "
    "successive outbound iteration calls; NVIDIA "
    "pacing is unestablished and no provider figure "
    "is claimed")

# The paper §3.4 assignment, with the sandbox now the
# room (the gate 4 rehearsal's text, unchanged): the
# sources at work/sources/ relative to the worker's
# /room/work, the deliverable at scratch/brief.md.
ASSIGNMENT_EXEC = (
    "Read the source documents in your office: "
    "sources/stock-take.md, sources/a3-pass.md, and "
    "sources/index-tail.md (your working directory is "
    "/room/work). Write scratch/brief.md: a plain-words "
    "brief, at most ~600 words, that a newcomer could read "
    "to learn what this framework is, what has actually been "
    "proven, what has not been proven, and what remains to "
    "be built. Stay accurate to the sources; invent nothing; "
    "where the sources disagree with each other, say so.")

EXEC_TRACE = (
    "DEMONSTRATION-PREPARATION-2026-11-24.md §2/§3.2; "
    "Ben's own-tool-first direction (INDEX 421); Ben's "
    "run order 2026-11-24 (Nemotron on NVIDIA; the mode "
    "judged native by the order)")

# The paper §3.2 grant set: the execution tool ONLY. No
# retrieval tools are offered in this configuration.
# The first two runs' configuration (INDEX 472/474),
# kept for the record — the run now seals the combined
# set below.
GRANTS_EXEC = [
    {"tool": "container.exec",
     "scope_ceiling": {},
     "side_effect_class": "execute",
     "bound": {"count": 12},
     "authority_trace": EXEC_TRACE},
]

# The combined configuration (INDEX 476): the same
# assignment, both doors open. The exec grant as above;
# the retrieval four under sources/ (he can pull the
# briefcase's contents through the doorway — the same
# three standing sources the registry holds); the same
# four under scratch/; and sandbox.write under
# scratch/ — a second write path for the brief that
# does not depend on his exec dialect. No write grant
# touches sources/: the briefcase's stocked contents
# are utilise-only (Ben's refinement, 2026-11-24:
# "access doesnt mean overwrite. it means utlilize").
COMBINED_TRACE = (
    "DEMONSTRATION-PREPARATION-2026-11-24.md §3.2 (the "
    "room-only configuration named there as not a "
    "permanent prohibition on mixed configurations); "
    "Ben's direction 2026-11-24 (INDEX 476): enable the "
    "pull, then a full run; Ben's briefcase design "
    "2026-11-16: pulls made by the worker from the "
    "shelf, the glossary carried in his case")

ASSIGNMENT_COMBINED = (
    "THE DELIVERABLE: the file scratch/brief.md. "
    "Write it with a tool — sandbox.write, or a shell "
    "command in your room (for example a heredoc that "
    "writes the file). Submitting the brief's text as "
    "a \"contribute\" outcome is NOT the deliverable "
    "and does not complete the assignment; only the "
    "file standing at scratch/brief.md completes "
    "it.\n\n"
    "THE TASK: read the three source documents for "
    "this assignment. Your briefcase carries a "
    "glossary: the three sources by their addresses, "
    "with what each one is. Your wake package lists "
    "your tools as a menu grouped by the job's "
    "phases — Gather, Compose, Deliver — every tool "
    "you hold, what each one is for, and the scope "
    "it works in; that menu is the statement of how "
    "you reach the sources and your scratch (your "
    "working directory in your office is /room/work). "
    "The stocked sources are yours to utilise: read "
    "them; do not alter them. Your briefcase also "
    "designates your journal, scratch/journal.md — "
    "your personal notebook: capture ideas, "
    "decisions, reflections, and progress as you "
    "work. Keep it as you work: after each file you "
    "read, log its name and the key points you took "
    "from it, in one or two plain lines — the "
    "office reads your journal at every wake to "
    "resume you, and the director may audit it. Its "
    "contents are not carried in your packages — "
    "pull it when you want it, and write to it with "
    "your tools.\n\n"
    "Write a plain-words brief of about 600 words, "
    "that a newcomer could read to learn what this "
    "framework is, what has actually been proven, "
    "what has not been proven, and what remains to "
    "be built. The door will not file a brief under "
    "550 words.\n\n"
    "CHECKLIST BEFORE YOU FINISH: all three sources "
    "read; the brief covers what the framework is, "
    "what has actually been proven, what has not "
    "been proven, and what remains to be built; "
    "nothing invented — stay accurate to the "
    "sources, and where the sources disagree with "
    "each other, say so; the file stands at exactly "
    "scratch/brief.md; then yield.")

# The case's onboarding (the run-6 package, 2026-11-24 —
# Ben's ruling: "his first prompt should be his
# onboarding file with specific instructions on how to
# navigate his briefcase"). The office carries it into
# the issued case as its own component; the loop
# presents its text at the head of his first wake
# package, and at later wakes a short cover drawn from
# its headline and deliverable. Its substance is the
# worker's own briefcase consultation (2026-11-24)
# translated from his imagined layout into this
# package's real one: the deliverable stated first and
# exactly, the briefcase's map in the package's actual
# order, both doors named, the journal in his terms,
# his position stated, and — under Ben's R31 ruling —
# the standing word that no freshness refusal applies
# to this job.
ONBOARDING = {
    "headline": "Write a short brief on the "
                "collaborative agent framework",
    "deliverable": "the file scratch/brief.md, "
                   "written with a tool",
    "text": (
        "You are a worker in the collaborative agent "
        "framework, assembled for one job. This is "
        "your onboarding: how your briefcase is laid "
        "out, and how to work in it. Your job is to "
        "read three source documents and write a "
        "short brief; the assignment itself stands "
        "in your package as the case, right after "
        "this page.\n\n"
        "HOW YOUR BRIEFCASE IS LAID OUT. Each package "
        "you are woken with carries, in order: (1) "
        "this onboarding at your first wake — at "
        "later wakes a short cover stands here "
        "instead, naming the job, the deliverable, "
        "and where you stand; (2) your case — the "
        "assignment, and the glossary naming what "
        "you may pull; (3) your working set — "
        "pointers to everything you have gathered so "
        "far: what you pull is shown to you whole in "
        "the wake right after you pull it, and after "
        "that its pointer stands here — its address, "
        "its size, and the office's record of your "
        "having pulled it — so pull it again whenever "
        "you need its words in front of you; (4) your "
        "journal; (5) your tool list, a menu grouped "
        "by the job's phases — Gather, Compose, "
        "Deliver — every tool you hold, what each "
        "one is for, and an example; (6) the outcomes "
        "of your calls since your last wake.\n\n"
        "HOW TO PULL A SOURCE. Two doors reach the "
        "same shelf. Through the doorway: sandbox.list "
        "shows a file's size and shape, sandbox.search "
        "finds passages, sandbox.read_range pulls a "
        "range of lines, sandbox.read pulls a whole "
        "file. In your room: a shell command through "
        "your execution tool — cat <path> reads a "
        "whole file at once. The glossary in your "
        "case names the three sources by their "
        "addresses, with their sizes. The stocked "
        "sources are yours to utilise: read them; "
        "never alter them.\n\n"
        "THE DELIVERABLE. The deliverable is the "
        "file scratch/brief.md, and it is delivered "
        "by writing that file with a tool — "
        "sandbox.write, or a shell command in your "
        "room. Submitting the brief's text as a "
        "\"contribute\" outcome is not the "
        "deliverable and does not complete the "
        "assignment. When the file stands at "
        "scratch/brief.md, answer with the yield "
        "outcome, and the assignment is complete.\n\n"
        "YOUR JOURNAL. scratch/journal.md is your "
        "personal notebook — capture ideas, "
        "decisions, reflections, and progress for "
        "this wake: where you were, what you noticed, "
        "what to do next. It comes back to you at "
        "every wake exactly as you left it; it is "
        "yours to write and rewrite.\n\n"
        "WHERE YOU STAND. Each package states your "
        "step — step k of your step ceiling — and "
        "your task's status. No freshness refusal "
        "applies to this job: your answers are judged "
        "on the work, never refused because the "
        "record moved while you were thinking. If a "
        "tool call fails, the package tells you what "
        "was asked, why it failed in plain terms, "
        "and the working alternative."),
}

# The journal the case designates (the orientation
# pass, 2026-11-24 — Ben's ruling on the worker
# consultation): the worker's own notebook, a path
# under his scratch, named in his case as its own
# component; each wake package presents it back to
# him as it stands. His to write and rewrite —
# appending is his habit, not a mechanism; nothing
# enforces append-only.
JOURNAL_PATH = "scratch/journal.md"

# The door scope's configuration (2026-11-24): the
# delivery declaration this run's case carries and its
# generation seals — the worker's contribution is the
# deliverable's arrival, and the office files it at the
# declared destination — and Gary's role-memory
# snapshot, the calibration the assembly carries into
# his first package (each item's basis class and
# conditions stated, per the examiner's discipline).
DELIVERY = {"destination": "scratch/brief.md",
            "route": "contribution-v1"}

# The delivery-evidence declaration (round ten, INDEX
# 552): the evidence this job's delivery must rest on —
# the three sources' whole content standing in the
# worker's working set before his contribution is
# adjudicated as a delivery. The case carries it as its
# own component and the generation seals it beside the
# delivery declaration; the door adjudicates against it.
DELIVERY_EVIDENCE = {"addresses": [
    "sources/stock-take.md", "sources/a3-pass.md",
    "sources/index-tail.md"]}

# The delivery-length declaration (the third gate,
# INDEX 557): the floor under this job's brief — the
# minimum word count a contribution must arrive with
# before the door adjudicates it as a delivery, set
# just under the agreed 590–610 band as its hard
# floor. The case carries it as its own component and
# the generation seals it beside the delivery
# declaration; the door adjudicates against it.
DELIVERY_FLOOR = {"min_words": 550}

# The process tree (the room rebuild, Ben's "Make it
# so" 2026-11-25 on the basics design of INDEX
# 554/572): the office-authored walk of this job,
# sealed in the case at assembly as its own component
# — the root (the brief the delivery files, at the
# delivery declaration's destination) and the steps in
# order: ORIENT (the one opening package), one GATHER
# step per declared source in the evidence
# declaration's own order, COMPOSE (the brief compiled
# from his journal entries), DELIVER (the contribution
# is the delivery; the office files it). Under the
# process-tree presentation contract the loop walks
# him by it — one step in front of him at a time, each
# step's content presented at its step and never
# twice — and the checker re-derives the walk from the
# record.
PROCESS_TREE = {
    "root": "scratch/brief.md",
    "steps": [
        {"node": "orient"},
        {"node": "gather",
         "address": "sources/stock-take.md"},
        {"node": "gather",
         "address": "sources/a3-pass.md"},
        {"node": "gather",
         "address": "sources/index-tail.md"},
        {"node": "compose"},
        {"node": "deliver"}]}

ROLE_MEMORY = [
    {"observation": "Delivers finished writing as "
                    "plain prose in the reply itself.",
     "basis": "demonstrated",
     "conditions": "Conversation lane, 2026-11-24 "
                   "try-out (INDEX 521): chose plain "
                   "prose when asked his format."},
    {"observation": "Reaches for the contribute "
                    "outcome as his delivery route, "
                    "even when a write tool is offered "
                    "and the deliverable statement "
                    "names it.",
     "basis": "demonstrated",
     "conditions": "Framework runs 5 and 6 (INDEX "
                   "512, 517) and the conversation "
                   "try-out (INDEX 521)."},
    {"observation": "Wants assigned sources in one "
                    "clearly labelled batch, up front.",
     "basis": "worker_reported",
     "conditions": "His closing suggestions in the "
                   "try-out conversation, 2026-11-24 "
                   "(INDEX 521)."},
    {"observation": "Wants style preferences (tone, "
                    "structure) stated at the outset.",
     "basis": "worker_reported",
     "conditions": "Same."},
    {"observation": "Wants a bounded word-count "
                    "target; he suggested about 600, "
                    "plus or minus 10.",
     "basis": "worker_reported",
     "conditions": "Same."},
    {"observation": "Does not notice the journal "
                    "unless its purpose is stated in "
                    "plain words beside it.",
     "basis": "demonstrated",
     "conditions": "Run 5 debrief (INDEX 513); the "
                   "purpose label was added in the "
                   "INDEX 516 package."},
    {"observation": "In this role you have a working "
                    "shell in your room (the execution "
                    "tool), and you use it as part of "
                    "the job's ordinary steps — for "
                    "example, reading a whole source "
                    "file at once with a single shell "
                    "command, or checking a file's size "
                    "before reading it. Its command "
                    "takes a list of strings; results "
                    "come back as the room's receipt.",
     "basis": "inference",
     "conditions": "Office-stated standing knowledge, "
                   "authored by the office 2026-11-24 "
                   "(INDEX 539-540): injected context. "
                   "No occupant has yet used the shell "
                   "successfully in a framework run — "
                   "round six: granted, listed, unused "
                   "(INDEX 530). Whether the behaviour "
                   "transfers is this run's measure."},
    {"observation": "Your last completed brief "
                    "covered all four points but came "
                    "in at about 405 words against the "
                    "roughly 600-word target — a third "
                    "short. In this role you write to "
                    "the full length the brief asks "
                    "for.",
     "basis": "demonstrated",
     "conditions": "Round six (INDEX 530): the "
                   "report's count was 405 words "
                   "against the agreed 590-610."},
    {"observation": "If a job needs something that is "
                    "not in your briefcase, the route "
                    "is stated in the job: ask the "
                    "office, or pull it from the shelf "
                    "using the glossary in your case. "
                    "An unstated route is not a gap to "
                    "improvise around silently — name "
                    "what you need.",
     "basis": "inference",
     "conditions": "Office-stated standing knowledge "
                   "(INDEX 539-540), per the "
                   "director's pull direction (INDEX "
                   "476, 479) and the worker's own "
                   "tools consultation (INDEX 537), "
                   "which converged on the same route."},
]


def _load_opening(demo_dir, run_dir):
    """The run's opening inputs (door scope, Part 3):
    the structured record at opening.json and the
    source conversation at opening-transcript.json,
    read from the run directory (or its record
    subdirectory) where they stand. Returns the
    structured record, or None where no input stands —
    the case then carries no opening, exactly as
    before. The transcript file is never written by
    the driver: it is retained among the run outputs
    untouched."""
    for base in (demo_dir, run_dir):
        path = base / "opening.json"
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
    return None

# The case's glossary (Ben's briefcase design,
# 2026-11-16): the pullable items for this case — the
# three sources by their shelf addresses (the paths
# both doors answer to) with a one-line description
# each — plus his scratch as his writing space. The
# office carries it into the issued case as its own
# component; it stands in his wake package inside the
# case, not merely named in the assignment prose.
# Each source's entry carries its concrete facts (the
# freedom-first setup pass, 2026-11-24): its size and
# line count as stocked — the same facts the stocking
# record's completability block verifies — and, under
# the working-set configuration, every source pulls
# whole or in ranges at his choice; the earlier
# "pull it in ranges, not whole" instruction for
# index-tail named a ceiling that no longer stands.
GLOSSARY = [
    {"address": "sources/stock-take.md",
     "description": "Vane's stock-take of the whole "
                    "framework (2026-11-23): what has "
                    "actually been proven, what has "
                    "not, and her four worries — the "
                    "sharpest single map of where "
                    "things stand. 11,946 bytes, "
                    "155 lines — pull it whole or in "
                    "ranges, your choice."},
    {"address": "sources/a3-pass.md",
     "description": "Vane's Piece A3 pass letter "
                    "(2026-11-23): the bounded loop's "
                    "examination verdict — what it "
                    "closed and what it left open. "
                    "4,663 bytes, 55 lines — pull it "
                    "whole or in ranges, your choice."},
    {"address": "sources/index-tail.md",
     "description": "The framework INDEX, entries "
                    "165-187: the decision record for "
                    "the agent-layer pieces and the "
                    "stock-take. 40,953 bytes, "
                    "24 lines — pull it whole or in "
                    "ranges, your choice."},
    {"address": "scratch/",
     "description": "Your writing space: drafts and "
                    "the deliverable live here — write "
                    "the brief to scratch/brief.md. "
                    "The stocked sources are "
                    "utilise-only: read them, never "
                    "alter them."},
]


def _combined_retrieval_grant(tool, prefix, count):
    return {"tool": tool,
            "scope_ceiling": {"path_prefix": prefix},
            "side_effect_class": "read",
            "bound": {"count": count},
            "authority_trace": COMBINED_TRACE}


def _presentation_declaration():
    """The live configuration's presentation seal:
    for the Nemotron seat, office-cycle-v9 — the
    file-grain successor carrying the sealed process
    tree in every package (the build scope of
    2026-11-26, INDEX 602-607); the other seats stay
    on office-cycle-v8 until their own proof stands
    (the plan's entry rule: v9 seals for the
    Nemotron configuration only)."""
    if not (GPTOSS or QUINN or GLM):
        return tool_policy.PRESENTATION_CONTRACT_V12
    return tool_policy.PRESENTATION_CONTRACT_V11


def _tree_declaration():
    """The process tree sealed beside the v9
    presentation contract for the Nemotron seat —
    the redrawn tree of the settled method (Ben's
    correction, INDEX 606; Vane's acceptance with
    the next-action clarification, INDEX 607):
    gather + journal per file, summarize compiles
    the journal, deliver files it. The other seats
    seal no tree."""
    if GPTOSS or QUINN or GLM:
        return None
    held = ("A read refused because its grant "
            "stands exhausted means you already "
            "hold the source — write its journal "
            "bit from what you hold.")
    return {
        "contract": tool_policy.TREE_CONTRACT_V1,
        "title": "The Brief — the framework, proven "
                 "and unproven, in plain words",
        "nodes": [
            {"id": "onboarding",
             "label": "1. Know the job",
             "kind": "onboarding",
             "depends_on": [],
             "workaround": ""},
            {"id": "gather-stock-take",
             "label": "2.1 Gather + journal — "
                      "sources/stock-take.md",
             "kind": "gather",
             "source": "sources/stock-take.md",
             "depends_on": ["onboarding"],
             "workaround": held},
            {"id": "gather-a3-pass",
             "label": "2.2 Gather + journal — "
                      "sources/a3-pass.md",
             "kind": "gather",
             "source": "sources/a3-pass.md",
             "depends_on": ["onboarding"],
             "workaround": held},
            {"id": "gather-index-tail",
             "label": "2.3 Gather + journal — "
                      "sources/index-tail.md",
             "kind": "gather",
             "source": "sources/index-tail.md",
             "depends_on": ["onboarding"],
             "workaround": ""},
            {"id": "summarize",
             "label": "3. Summarize — read your "
                      "journal whole and compile "
                      "it into the brief",
             "kind": "summarize",
             "depends_on": ["gather-stock-take",
                            "gather-a3-pass",
                            "gather-index-tail"],
             "workaround": ""},
            {"id": "deliver",
             "label": "4. Deliver — contribute the "
                      "brief; the office files it "
                      "at scratch/brief.md",
             "kind": "deliver",
             "depends_on": ["summarize"],
             "workaround": ""}]}


GRANTS_COMBINED = (
    [{"tool": "container.exec",
      "scope_ceiling": {},
      "side_effect_class": "execute",
      "bound": {"count": 12},
      "authority_trace": COMBINED_TRACE}]
    + [_combined_retrieval_grant(tool, "sources", 12)
       for tool in ("sandbox.list", "sandbox.search",
                    "sandbox.read_range", "sandbox.read")]
    + [_combined_retrieval_grant(tool, "scratch", 12)
       for tool in ("sandbox.list", "sandbox.search",
                    "sandbox.read_range", "sandbox.read")]
    + [{"tool": "sandbox.write",
        "scope_ceiling": {"path_prefix": "scratch"},
        "side_effect_class": "write",
        "bound": {"count": 12},
        "authority_trace": COMBINED_TRACE}])


# The demonstration's loop bounds, re-derived from the
# task as stocked (the freedom-first setup pass,
# 2026-11-24 — Ben: "testing him over and over again is
# going to explain nothing. We have to fix the room."
# The inherited bounds — 12 steps, 600 s — were scoped
# when the sources were believed to total ~17 KB; the
# stocked sources total 57,562 bytes, and run 4 spent
# its 12 steps reaching the right move at the ceiling).
# Steps are accounting, not rationing: the ceiling is
# sized to the honest path with slack, and the deadline
# accommodates the step count at this driver's pacing.
DEMO_BOUNDS = {"step_ceiling": 20,
               "deadline_seconds": 2400 if (QUINN or GPTOSS)
               else 1200}
BOUNDS_DERIVATION = (
    "step ceiling 20 (unchanged): the honest path is "
    "5 steps, as the Nemotron derivation records. "
    "Deadline 2,400 s: 20 steps x (the 65 s pacing "
    "interval + a 55 s per-call allowance) = 2,400 s — "
    "the pacing is sized to the Groq free plan's "
    "published token cap (8,000 TPM; the wake packages "
    "run ~5-7K tokens, so successive calls land in "
    "separate minute windows), and the deadline "
    "accommodates the step count at that pacing. The "
    "deadline remains the one authoritative clock; a "
    "single call may still lawfully take its 300 s "
    "adapter span within it. Grant counts stand as "
    "commissioned." if QUINN else
    "step ceiling 20 (unchanged): the honest path is "
    "5 steps, as the Nemotron derivation records. "
    "Deadline 2,400 s: 20 steps x (the 65 s pacing "
    "interval + a 55 s per-call allowance) = 2,400 s — "
    "the pacing is the Groq-route courtesy this "
    "driver already uses (Quinn's configuration), and "
    "the deadline accommodates the step count at that "
    "pacing. The open question this run answers is "
    "whether this account's actual per-model limits "
    "pass a full-working-set wake for THIS model: "
    "Quinn's TPM refusal (INDEX 562) is her model's "
    "evidence, not this one's; attempt 6 (INDEX 234) "
    "met a byte ceiling — a 134,844-byte push package "
    "refused with HTTP 413 — not a rate limit, and "
    "that package shape no longer exists; the "
    "account's authenticated limits for this model "
    "have never been read. The deadline remains the "
    "one authoritative clock; a single call may still "
    "lawfully take its 300 s adapter span within it. "
    "Grant counts stand as commissioned." if GPTOSS
    else
    "step ceiling 20 (unchanged): the honest path is "
    "5 steps, as the Nemotron derivation records. "
    "Deadline 1,200 s: the step ceiling at this "
    "configuration's 5 s courtesy pacing leaves the "
    "span the Nemotron derivation's per-call "
    "allowances already cover — the deadline is not "
    "sized by pacing on this route. The budget that "
    "binds this route is the free plan's 10,000 "
    "Neurons/day, of which one full run is estimated "
    "at roughly a third (the research figure, INDEX "
    "563); no Neuron figure is enforced by this "
    "driver — the allowance is the provider's, and a "
    "run that exhausted it would fail at the provider "
    "as a provider failure, on the record. The "
    "deadline remains the one authoritative clock; a "
    "single call may still lawfully take its 300 s "
    "adapter span within it. Grant counts stand as "
    "commissioned." if GLM else
    "step ceiling 20: the honest path is 5 steps (three "
    "whole reads, one write, one yield); pulling "
    "index-tail by ranges instead of whole adds up to 6; "
    "slack of 9 covers the missteps, retries, lists and "
    "searches runs 3-4 actually spent (7-8 steps on "
    "failures, repeats and silence) — 20 steps is four "
    "times the honest path. Deadline 1,200 s: 20 steps x "
    "(the 20 s pacing interval + a 40 s per-call "
    "allowance, ~4x this route's observed per-call "
    "latency; runs 3-4 ran 12 iterations in ~240-290 s) "
    "= 1,200 s. The deadline remains the one "
    "authoritative clock; a single call may still "
    "lawfully take its 300 s adapter span within it. "
    "Grant counts stand as commissioned (exec 12, "
    "retrieval 12 per tool and prefix, write 12): the "
    "write count stood at 4 — sized for the tree walk's "
    "three journal writes — until the office cycle's "
    "six blocks required six journal appends plus draft "
    "slack; the director raised it to 12 on 2026-11-25 "
    "(INDEX 585), the count every other tool already "
    "carried.")


def _stage_sandbox_sources(sandbox_dir, manifest):
    """Stage the executor sandbox's pullable sources:
    the released source set copied from the verified
    staging directory into <sandbox_dir>/sources/, each
    staged file hash-verified against its stocking
    manifest entry, and <sandbox_dir>/scratch/ created
    as the doorway write path's home. The pull door
    serves exactly the files the room was stocked with
    — the same bytes at the same addresses the glossary
    names. Returns a problem string, or None."""
    sandbox_dir = Path(sandbox_dir)
    for entry in manifest["sources"]:
        staged = stock_demo.DEFAULT_SOURCES_DIR / \
            entry["path"]
        if not staged.exists():
            return (f"the verified source file "
                    f"{entry['path']} is missing from "
                    f"{stock_demo.DEFAULT_SOURCES_DIR}")
        dest = sandbox_dir / entry["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(staged, dest)
        if _sha256_bytes(dest.read_bytes()) != \
                entry["sha256"]:
            return (f"the staged {entry['path']} does "
                    f"not hash to its manifest entry "
                    f"{entry['sha256']}")
    (sandbox_dir / "scratch").mkdir(
        parents=True, exist_ok=True)
    return None


def _block_map_for_sandbox(sandbox_dir):
    """The office's block map for the cycle contract
    (the plan, PLAN-OFFICE-CYCLE-2026-11-25): the
    declared delivery-evidence files as staged in the
    sandbox, portioned by the office at the ruled
    ceiling from their staged bytes — the map the
    generation seals beside the office-cycle
    presentation contract, in declaration order."""
    contents = {}
    for address in DELIVERY_EVIDENCE["addresses"]:
        contents[address] = (
            Path(sandbox_dir) / address).read_bytes()
    return tool_policy.compute_block_map(
        list(DELIVERY_EVIDENCE["addresses"]), contents)


def _call_ledger(captures_path, events, loop, run_dir):
    """The road's accounting (the plan §6,
    Qualification B): every call that shared the
    model's minute, in the order the captures stand —
    the identity call, the probe's trials, the loop's
    calls — each with its wire bytes and their
    estimate under the one estimator, and the loop's
    calls with the loop's own package estimates beside
    them (the budget's figures) and their record
    timestamps. Provider usage figures, where a
    response artifact carries them, stand beside the
    loop entry they answer. Returns (entries, summary)
    — the summary naming the minimum observed gap
    between recorded call timestamps (the probe's
    completion to the first iteration; iteration to
    iteration) and the largest single-call estimate."""
    import datetime
    lines = [json.loads(line) for line in
             Path(captures_path).read_text(
                 encoding="utf-8").splitlines()
             if line.strip()]
    iterations = [ev for ev in events
                  if ev["type"] == "LOOP_ITERATION"]
    estimates = list(
        getattr(loop, "call_estimates", []) or [])
    usage = {}
    responses = Path(run_dir) / "responses"
    if responses.is_dir():
        for path in sorted(responses.glob(
                "iteration-*.json")):
            try:
                artifact = json.loads(
                    path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            number = path.stem.rsplit("-", 1)[-1]
            found = artifact.get("usage") \
                if isinstance(artifact, dict) else None
            if isinstance(found, dict):
                usage[number] = found
    entries = []
    loop_seen = 0
    for order, cap in enumerate(lines):
        body = base64.b64decode(cap["request_b64"])
        if b"Your wake package:" in body:
            kind = "loop"
        elif order == 0:
            kind = "identity"
        elif cap.get("mode") == "chat-raw-bounded":
            kind = "probe"
        else:
            kind = "other"
        entry = {
            "order": order,
            "mode": cap.get("mode"),
            "index": cap.get("index"),
            "kind": kind,
            "wire_bytes": cap.get("request_bytes"),
            "wire_estimated_tokens":
                tool_policy.estimate_tokens(
                    cap.get("request_bytes") or 0)}
        if kind == "loop":
            if loop_seen < len(estimates):
                entry["package_serialized_bytes"] = \
                    estimates[loop_seen][
                        "serialized_bytes"]
                entry["package_estimated_tokens"] = \
                    estimates[loop_seen][
                        "estimated_tokens"]
            if loop_seen < len(iterations):
                entry["recorded_ts"] = iterations[
                    loop_seen].get("ts")
                found = usage.get(str(iterations[
                    loop_seen]["payload"].get(
                        "iteration")))
                if found is not None:
                    entry["provider_usage"] = found
            loop_seen += 1
        entries.append(entry)

    def _epoch(ts):
        if not isinstance(ts, str):
            return None
        try:
            parsed = datetime.datetime.strptime(
                ts, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return None
        return parsed.replace(
            tzinfo=datetime.timezone.utc).timestamp()

    points = []
    for ev in events:
        if ev["type"] == "ASSEMBLY_PROBED":
            points.append(_epoch(ev.get("ts")))
    for ev in iterations:
        points.append(_epoch(ev.get("ts")))
    points = [point for point in points
              if point is not None]
    gaps = [later - earlier for earlier, later
            in zip(points, points[1:])]
    summary = {
        "calls": len(entries),
        "minimum_gap_seconds": min(gaps) if gaps
        else None,
        "largest_single_call_estimate": max(
            (entry.get("package_estimated_tokens") or 0
             for entry in entries), default=None),
        "largest_wire_estimate": max(
            (entry.get("wire_estimated_tokens") or 0
             for entry in entries), default=None)}
    return entries, summary


def _cycle_summary(events, doorway, assembly_id,
                   case_id):
    """The run's summary under the cycle contract
    (the plan §7), derived from the record at its
    head: the cycles completed, the cycles failed
    (incomplete where the run ended in a stall), the
    cycles unresolved (incomplete where it did not),
    and the declared evidence's standing, file by
    file, under the block-coverage rule."""
    from framework.loop import (
        _cycle_state, _delivery_evidence_missing)
    state = doorway.state()
    content, _version = established_case_content(
        state, case_id)
    generated = doorway._generated_payload(assembly_id)
    if generated is None:
        return None
    instance_id = generated.get("instance_id")
    cstate = _cycle_state(
        events, state["dispatches"], instance_id,
        state["head_seq"], content, generated, 0)
    if cstate is None:
        return None
    stalled = any(
        ev["type"] == "LOOP_STALLED"
        and ev["payload"].get("assembly_id")
        == assembly_id for ev in events)
    completed = [block["block_id"]
                 for block in cstate["blocks"]
                 if block["state"] == "done"]
    incomplete = [block["block_id"]
                  for block in cstate["blocks"]
                  if block["state"] != "done"]
    missing = _delivery_evidence_missing(
        events, state["dispatches"], instance_id,
        state["head_seq"],
        list(DELIVERY_EVIDENCE["addresses"]),
        block_map=cstate["block_map"])
    return {
        "completed": completed,
        "failed": incomplete if stalled else [],
        "unresolved": [] if stalled else incomplete,
        "evidence": {
            address: ("missing" if address in missing
                      else "stands")
            for address in
            DELIVERY_EVIDENCE["addresses"]}}

# The director's order, verbatim as given, and the
# judgement the order makes.
ORDER_WORDS = (
    "Let's try Quinn... we should be able to just "
    "drop her right in" if QUINN else
    "Make it so — make sure that we're not getting "
    "errors because he's trying to use a tool; we "
    "need to allow him to use his tools" if GPTOSS
    else
    "Cloudflare it is" if GLM else
    "just run it with nemotron, see how he reacts... "
    "lets start doing. im done guessing")
ORDER_GROUNDS = (
    "Director's direction (Ben, 2026-11-25): try "
    "Quinn — the Qwen occupant dropped into the same "
    "role, the same case and the same gates. The "
    "direction replaces the probe-phase examiner "
    "judgement for this run: the mode is judged text "
    "by the direction — she answers in the package "
    "protocol as plain-text JSON, the loop's standing "
    "text population. The Groq route's native path is "
    "not used: it carries the open BD-1 defect (INDEX "
    "411-420 — the disable_tool_validation flag never "
    "reached the live wire on that route), and no "
    "finding about her native reach is made or needed. "
    "The probe stage ran live and its recommendation "
    "stands in the record as evidence; it does not "
    "decide this run's mode." if QUINN else
    "Director's direction (Ben, 2026-11-25 — his "
    "\"Make it so\" at 15:02 MST on the room-rebuild "
    "design, and his addition at 15:03: \"make sure "
    "that we're not getting errors because he's "
    "trying to use a tool\" and \"We need to allow "
    "him to use his tools\"): the GPT-OSS occupant "
    "dropped into the same role, the same case and "
    "the same gates, and re-judged NATIVE on the "
    "corrected Groq transport — he is to use his own "
    "tools, natively, the way he reaches for them. "
    "The bar to that judgement was the open BD-1 "
    "defect (INDEX 411-420): the adapter staged "
    "disable_tool_validation for each native call, "
    "but the live connector transport never carried "
    "it to the wire, so native calls died at the "
    "provider. The transport now carries the sealed "
    "tools offered natively, a tool_choice permitting "
    "calls, and the flag exactly as staged, on the "
    "actual outbound request — witnessed at the "
    "captures seam, not on a staged path. The "
    "examiner's standing text judgement for this "
    "model on this route (INDEX 300) is superseded "
    "by the direction for this run; the probe stage "
    "ran live and its recommendation stands in the "
    "record as evidence; it does not decide this "
    "run's mode. The doorway still adjudicates every "
    "native call against his sealed grants: an "
    "ungranted call is refused at the doorway and "
    "recorded — the office's refusal, not a provider "
    "error. The presentation is the process-tree "
    "contract the same direction settled: one "
    "opening package, then the tree's steps one at a "
    "time, each step's content presented once at its "
    "step." if GPTOSS else
    "Director's direction (Ben, 2026-11-25): adopt "
    "the Cloudflare Workers AI route (INDEX 563) — "
    "the GLM occupant dropped into the same role, "
    "the same case and the same gates. The direction "
    "replaces the probe-phase examiner judgement for "
    "this run: the mode is judged text by the "
    "direction — the occupant answers in the package "
    "protocol as plain-text JSON, the loop's standing "
    "text population. This route's native "
    "tool-calling has never been witnessed on the "
    "live path, and no finding about its native "
    "reach is made or needed until a native witness "
    "exists. The probe stage ran live and its "
    "recommendation stands in the record as "
    "evidence; it does not decide this run's mode."
    if GLM else
    "Director's order (Ben, 2026-11-24): run the "
    "demonstration with Nemotron on NVIDIA and see how "
    "he reacts. The order replaces the probe-phase "
    "examiner judgement for this run: the mode is judged "
    "native by the order — the execution tool exists as "
    "a host-defined definition, the native adapter is "
    "the built and closed path for it, and the model's "
    "first live response is itself the delivery evidence "
    "(DEMONSTRATION-PREPARATION-2026-11-24.md §2.1, "
    "§3.1, §5 item 1). The probe stage ran live and its "
    "recommendation stands in the record as evidence; "
    "it does not decide this run's mode.")
ORDER_EXAMINER = ("Ben (director) — direction of "
                  "2026-11-25" if (QUINN or GLM or GPTOSS)
                  else
                  "Ben (director) — order of 2026-11-24")
ORDER_DATE = ("2026-11-25" if (QUINN or GLM or GPTOSS)
              else "2026-11-24")

# The office-declared mode grounds (office-cycle-v8;
# the director's rulings of 2026-11-25, 23:07 and
# 23:08 MST): under v8 no probe stands in the launch,
# so the probe-era grounds above — which speak of a
# probe stage running live — are not this launch's
# grounds and stand in no v8 record. The mode is a
# known, recorded fact about the occupant the office
# assembled; the office declares it from the sealed
# configuration, with the evidence named:
OFFICE_MODE_GROUNDS = (
    "Office-declared mode: text. Grounds: the "
    "standing judgement for this occupant — judged "
    "text under the director's direction of "
    "2026-11-25 (the Groq route's native path carried "
    "the open BD-1 defect at her judging, INDEX "
    "411-420; she answers in the package protocol as "
    "plain-text JSON, the loop's standing text "
    "population). No probe stands in this launch "
    "(the director's ruling of 2026-11-25 23:07 MST); "
    "the mode is declared by the office from the "
    "sealed configuration, not re-measured."
    if QUINN else
    "Office-declared mode: native. Grounds: the "
    "standing judgement for this occupant — re-judged "
    "NATIVE on the corrected Groq transport under the "
    "director's direction of 2026-11-25 (INDEX 576), "
    "and witnessed live at demo-gptoss5 (INDEX 586), "
    "where Groq accepted and dispatched six native "
    "calls in a single response. No probe stands in "
    "this launch (the director's ruling of 2026-11-25 "
    "23:07 MST); the mode is declared by the office "
    "from the sealed configuration, not re-measured."
    if GPTOSS else
    "Office-declared mode: text. Grounds: the "
    "standing judgement for this occupant — judged "
    "text for the Cloudflare Workers AI route (INDEX "
    "563-564); this route's native tool-calling has "
    "never been witnessed on the live path. No probe "
    "stands in this launch (the director's ruling of "
    "2026-11-25 23:07 MST); the mode is declared by "
    "the office from the sealed configuration, not "
    "re-measured."
    if GLM else
    "Office-declared mode: native. Grounds: the "
    "standing judgement for this occupant — judged "
    "native under the director's order of 2026-11-24; "
    "the native adapter path for the execution tool "
    "is the built and closed path. No probe stands in "
    "this launch (the director's ruling of 2026-11-25 "
    "23:07 MST); the mode is declared by the office "
    "from the sealed configuration, not re-measured.")
ORDER_EFFECT = (
    "the director's direction re-judges the "
    "mode native on the corrected Groq "
    "transport (the BD-1 correction carried "
    "to the wire), superseding the "
    "examiner's standing text judgement for "
    "this model on this route (INDEX 300) "
    "for this run, whatever the probe stage "
    "recommends; the probe's recommendation "
    "stands in the record as evidence, not "
    "as the decision; the model's first live "
    "response is the delivery evidence"
    if GPTOSS else
    "the director's direction replaces the "
    "probe-phase examiner judgement for "
    "this run: the mode is judged "
    "text by the direction, whatever the "
    "probe stage recommends; the "
    "probe's recommendation stands in "
    "the record as evidence, not as "
    "the decision; the model's first "
    "live response is the delivery "
    "evidence" if (QUINN or GLM) else
    "the director's order replaces the "
    "probe-phase examiner judgement for "
    "this run: the mode is judged "
    "native by the order, whatever the "
    "probe stage recommends; the "
    "probe's recommendation stands in "
    "the record as evidence, not as "
    "the decision; the model's first "
    "live response is the delivery "
    "evidence")

# The paper §1.1 source table: the in-room paths and
# their SHA-256 identities, asserted at stocking time
# by --verify-config.
PAPER_SOURCE_HASHES = {
    "sources/stock-take.md":
        "ecb919025d4e5176a7128009ad17c4d12c9ff4f1dd41748"
        "b148262308b8cc2e7",
    "sources/a3-pass.md":
        "d60e5b0fd97baab6bffe4b8c6aee5bdc700ce6035ab26f7"
        "a6d49107659f25bff",
    "sources/index-tail.md":
        "eb16b56bb16c53dfb7b5420b2a2c446e8cbc40cf4787e46"
        "0b8de9773145d05ed",
}


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _worked_example_address(sandbox_dir):
    """The office's choice of demonstration file (the
    calibration): the glossary's smallest stocked
    source, by its staged bytes — the demonstration
    is a whole read of a real source, and the one
    stage that shows a whole file stays within the
    pointer-rule population's package bound (24,000
    rendered chars, the standing dashboard bound).
    Ties stand in glossary order. The seal names the
    address; the checker verifies it is one of the
    map's, and the rehearsal recomputes the choice
    from the staged bytes themselves."""
    best = None
    for entry in GLOSSARY:
        staged = Path(sandbox_dir) / entry["address"]
        if not staged.is_file():
            continue
        size = len(staged.read_bytes())
        if best is None or size < best[1]:
            best = (entry["address"], size)
    return best[0]


CAPTURE_HELPER_SOURCE = '''#!/usr/bin/env python3
"""The demonstration run's capture pass-through helper.

Stands at the connector helper seam — invoked exactly
as the real helper is ([python, helper, mode, model],
the request JSON on stdin) — records the exact request
bytes to the captures file (DEMO_RUN_CAPTURES) in the
gate 4 rehearsal's record shape, then delegates to the
REAL NVIDIA connector helper (DEMO_RUN_DELEGATE_HELPER)
with the same arguments and bytes, the environment
inherited whole, stdout and stderr inherited untouched,
and exits with the delegate's exit code. A pure
pass-through: it alters nothing it carries. If the
capture cannot be written the delegate is never invoked
— no unwitnessed transmitted request."""
import base64
import hashlib
import json
import os
import subprocess
import sys


def main():
    mode = sys.argv[1]
    model = sys.argv[2]
    body = sys.stdin.buffer.read()
    captures_path = os.environ["DEMO_RUN_CAPTURES"]
    delegate = os.environ.get(
        "DEMO_RUN_DELEGATE_HELPER") or os.path.expanduser(
        "~/workspace/custom-connectors/custom.nvidia/bin/"
        "nvidia_api.py")
    index = 0
    try:
        with open(captures_path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    if json.loads(line).get("mode") == mode:
                        index += 1
                except ValueError:
                    continue
    except OSError:
        index = 0
    with open(captures_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "mode": mode, "model": model, "index": index,
            "request_sha256":
                hashlib.sha256(body).hexdigest(),
            "request_bytes": len(body),
            "request_b64": base64.b64encode(
                body).decode("ascii")}) + "\\n")
    try:
        proc = subprocess.run(
            [sys.executable, delegate, mode, model],
            input=body)
    except OSError as exc:
        sys.stderr.write(
            f"demo capture helper: the delegate helper "
            f"could not be started: {exc}\\n")
        return 3
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
'''


# Quinn's capture helper: the same pass-through, word
# for word, with the route's own names — the delegate
# it names is the Groq connector helper. The Nemotron
# configuration's helper source above stands untouched.
CAPTURE_HELPER_SOURCE_QUINN = (
    CAPTURE_HELPER_SOURCE
    .replace("custom.nvidia", "custom.groq")
    .replace("nvidia_api.py", "groq_api.py")
    .replace("NVIDIA", "Groq"))
# The Cloudflare occupant's capture helper: the same
# pass-through, word for word, with the route's own
# names — the delegate it names is the Cloudflare
# connector's Workers AI helper. The Nemotron
# configuration's helper source above stands untouched.
CAPTURE_HELPER_SOURCE_GLM = (
    CAPTURE_HELPER_SOURCE
    .replace("custom.nvidia", "custom.cloudflare")
    .replace("nvidia_api.py", "cf_ai.py")
    .replace("NVIDIA", "Cloudflare"))
# The GPT-OSS occupant shares Quinn's capture helper
# source word for word — the same Groq route, the same
# delegate; no second derivation is needed or made.
CAPTURE_HELPER_SOURCE_SELECTED = (
    CAPTURE_HELPER_SOURCE_QUINN if (QUINN or GPTOSS)
    else CAPTURE_HELPER_SOURCE_GLM if GLM
    else CAPTURE_HELPER_SOURCE)


def _write_capture_helper(path):
    path.write_text(CAPTURE_HELPER_SOURCE_SELECTED,
                    encoding="utf-8")
    path.chmod(0o755)
    return path


def _install_typed_transport(adapter, wrapper_path):
    """The occupant route's typed connector transport
    on the adapter, through the capture seam: the Groq
    twin on Quinn's and the GPT-OSS occupant's route,
    the Cloudflare twin on the GLM occupant's route,
    the NVIDIA transport otherwise — each route's
    sanctioned helper path."""
    if ROUTE == "groq":
        return install_groq_connector_transport(
            adapter, str(wrapper_path), MODEL)
    if ROUTE == "cloudflare":
        return install_cloudflare_connector_transport(
            adapter, str(wrapper_path), MODEL)
    return install_connector_transport(
        adapter, str(wrapper_path), MODEL)


def _install_raw_call(adapter, wrapper_path):
    """The occupant route's probe raw call, through
    the capture seam: the Groq transport's raw call on
    Quinn's and the GPT-OSS occupant's route and the
    Cloudflare transport's on the GLM occupant's
    route (each takes the adapter as its first
    argument, whose timeout bounds it), the NVIDIA
    bounded raw call otherwise."""
    if ROUTE == "groq":
        return install_groq_connector_raw_call(
            adapter, str(wrapper_path), MODEL)
    if ROUTE == "cloudflare":
        return install_cloudflare_connector_raw_call(
            adapter, str(wrapper_path), MODEL)
    return install_nvidia_connector_raw_call(
        helper_path=str(wrapper_path), model=MODEL)


def _commission_and_issue(store, manifest_hash,
                          assignment=ASSIGNMENT_COMBINED,
                          glossary=GLOSSARY,
                          onboarding=ONBOARDING,
                          delivery=DELIVERY,
                          delivery_evidence=DELIVERY_EVIDENCE,
                          delivery_floor=DELIVERY_FLOOR,
                          role_memory=ROLE_MEMORY,
                          opening=None):
    """Commission, material sealing, office issue and
    the pre-activation verification, exactly as the gate
    4 rehearsal and the harness carry them: the issued
    case must identify the manifest by hash in its
    evidence boundary, carry the scoped bounds, and —
    where a glossary is commissioned — carry the brief's
    glossary unchanged as its own component; where an
    onboarding is commissioned (the run-6 package), the
    brief carries it likewise, as its own component.
    Returns (doorway, office, gen, tok, issued). Raises
    RuntimeError on any failure."""
    brief = _commission_brief(assignment, manifest_hash,
                              glossary=glossary,
                              bounds=DEMO_BOUNDS,
                              journal=JOURNAL_PATH,
                              onboarding=onboarding,
                              delivery=delivery,
                              delivery_evidence=
                              delivery_evidence,
                              delivery_floor=delivery_floor,
                              role_memory=role_memory,
                              opening=opening,
                              process_tree=PROCESS_TREE)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": RUN_ID,
        "tree": {"part-A": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": brief},
    })
    store.commit()
    doorway = Doorway(store)
    office = Office(doorway)
    gen = Generator(doorway)
    tok = {s: doorway.issue_token(s)
           for s in ("orch-1", "exam-1", "dir-1", "crew-1")}
    _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
        "material_id": f"source-manifest sha256:"
                       f"{manifest_hash}",
        "boundary": ["crew-1"]})
    manifest = _staged_manifest(store)
    for entry in manifest:
        _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
            "material_id": f"{entry['path']} "
                           f"sha256:{entry['sha256']}",
            "boundary": ["crew-1"]})
    issued = office.issue_new(tok["orch-1"], "crew-1")
    if not issued.get("ok"):
        raise RuntimeError(
            f"case issue failed: {issued.get('problems')}")
    _act(doorway, tok["exam-1"], "CASE_JUDGED",
         {"case_id": issued["case_id"],
          "version": issued["version"]})
    office.authorise(tok["orch-1"], issued["case_id"],
                     issued["version"])
    content, _version = established_case_content(
        doorway.state(), issued["case_id"])
    boundary = (content or {}).get(
        "evidence_boundary") or []
    if not any(manifest_hash in str(item)
               for item in boundary):
        raise RuntimeError(
            "the issued case's evidence boundary does "
            "not identify the source manifest hash")
    if (content or {}).get("loop_bounds") != DEMO_BOUNDS:
        raise RuntimeError(
            "the issued case's loop_bounds are not the "
            "demonstration's re-derived bounds")
    if glossary is not None and \
            (content or {}).get("glossary") != glossary:
        raise RuntimeError(
            "the issued case does not carry the "
            "commissioned glossary as its own component")
    if onboarding is not None and \
            (content or {}).get("onboarding") != onboarding:
        raise RuntimeError(
            "the issued case does not carry the "
            "commissioned onboarding as its own component")
    if delivery is not None and \
            (content or {}).get("delivery") != delivery:
        raise RuntimeError(
            "the issued case does not carry the "
            "delivery declaration as its own component")
    if delivery_evidence is not None and \
            (content or {}).get("delivery_evidence") \
            != delivery_evidence:
        raise RuntimeError(
            "the issued case does not carry the "
            "delivery-evidence declaration as its own "
            "component")
    if delivery_floor is not None and \
            (content or {}).get("delivery_floor") \
            != delivery_floor:
        raise RuntimeError(
            "the issued case does not carry the "
            "delivery-length declaration as its own "
            "component")
    if role_memory is not None and \
            (content or {}).get("role_memory") \
            != role_memory:
        raise RuntimeError(
            "the issued case does not carry the "
            "role-memory snapshot as its own component")
    if opening is not None and \
            (content or {}).get("opening") != opening:
        raise RuntimeError(
            "the issued case does not carry the "
            "opening record as its own component")
    return doorway, office, gen, tok, issued


# The manifest entries the commission seals, held by the
# caller (the stocking record is the driver's source for
# them, as it was the rehearsal's).
_MANIFEST_ENTRIES = []


def _staged_manifest(_store):
    return list(_MANIFEST_ENTRIES)


def _order_record(assembly_id, instance_id,
                  generated_record_hash, probed_payload,
                  probe_result, verify_only=False):
    """The director's order record: the durable decision
    document the ASSEMBLY_JUDGED act binds by canonical
    hash — the examiner's decision receipt's place,
    taken by the order that replaces the probe-phase
    judgement for this run."""
    return {
        "kind": "director's order record — the decision "
                "record the ASSEMBLY_JUDGED act binds by "
                "hash (this run's judgement provenance)",
        "run_id": RUN_ID,
        "assembly_id": assembly_id,
        "instance_id": instance_id,
        "generated_record_hash": generated_record_hash,
        "probed_seq": (probe_result or {}).get(
            "probed_seq"),
        "probe_evidence_hash": (probe_result or {}).get(
            "evidence_hash"),
        "probe_recommended_mode": (probe_result or {}).get(
            "recommended_mode"),
        "probe_settled_count": (probe_result or {}).get(
            "settled_count"),
        "probe_counts": (probe_result or {}).get(
            "counts"),
        "fingerprint": (probed_payload or {}).get(
            "fingerprint"),
        "adapter_mode": ADAPTER_MODE,
        "mode_grounds": OFFICE_MODE_GROUNDS,
        "order": {
            "by": "Ben (director)",
            "date": ORDER_DATE,
            "words": ORDER_WORDS,
            "effect": ORDER_EFFECT,
        },
        "model_pin": MODEL,
        "route": ROUTE,
        "decision_examiner": ORDER_EXAMINER,
        "decided_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verify_config_staging": verify_only,
    }


def run_demo():
    """The live demonstration run. Returns the process
    exit code: 0 when the loop's outcome is ok, 1 on a
    stall/decline or a pre-activation abort, 2 when the
    run directory already stands. The room is destroyed
    before this returns, on every path."""
    demo_dir = DEMO_DIR.resolve()
    # The run's opening inputs (door scope, Part 3) are
    # inputs, not a standing run: a directory holding
    # only opening.json / opening-transcript.json does
    # not refuse. Anything else standing there does.
    _OPENING_INPUTS = {"opening.json",
                       "opening-transcript.json"}
    if demo_dir.exists() and any(
            entry.name not in _OPENING_INPUTS
            for entry in demo_dir.iterdir()):
        print(f"ABORT: run directory {demo_dir} already "
              f"stands and is not empty; refusing to "
              f"overwrite a standing run", file=sys.stderr)
        return 2
    run_dir = demo_dir / "run"
    rooms_base = demo_dir / "rooms"
    run_dir.mkdir(parents=True, exist_ok=True)
    rooms_base.mkdir(parents=True, exist_ok=True)

    # The capture seam, written before any transport can
    # invoke it; its channels travel in the environment
    # the transports pass to the helper.
    wrapper_path = _write_capture_helper(
        demo_dir / "capture_helper.py")
    captures_path = demo_dir / "captures.jsonl"
    captures_path.write_text("", encoding="utf-8")
    os.environ["DEMO_RUN_CAPTURES"] = str(captures_path)
    os.environ["DEMO_RUN_DELEGATE_HELPER"] = \
        DELEGATE_HELPER

    room = None
    store = None
    store_path = str(run_dir / "run.db")

    def abort_report(fields):
        """A pre-activation abort's paperwork (derived
        matter): the record exported as it stands — no
        activation event in it — and report.json naming
        the abort. Returns 1."""
        events_now = store.all_events() if store else []
        if store is not None:
            export_store(store_path,
                         str(run_dir / "run-export.json"))
        report = {
            "kind": "first-worker demonstration run "
                    "abort (derived matter, not record)",
            "run_id": RUN_ID,
            "route": ROUTE,
            "model_pin": MODEL,
            "aborted": True,
            "activation_performed": any(
                e["type"] == "INSTANCE_ACTIVATED"
                for e in events_now),
            "event_count": len(events_now),
        }
        report.update(fields)
        with open(demo_dir / "report.json", "w",
                  encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
        return 1

    try:
        # STOCK (hop 2) — the paper §1 stocking, verified
        # by its smoke set before any worker exists; the
        # room is held in THIS process for the whole run.
        stocking = stock_demo.stock_demo_room(
            rooms_base, "demo")
        room = room_mod.load_room(rooms_base, "demo")
        manifest = stocking["source_manifest"]
        manifest_hash = manifest["manifest_sha256"]
        _MANIFEST_ENTRIES.clear()
        _MANIFEST_ENTRIES.extend(manifest["sources"])
        print(f"stocking: room stocked and smoke-verified; "
              f"manifest sha256: {manifest_hash}")
        if manifest_hash != EXPECTED_MANIFEST_HASH:
            print(f"ABORT: the stocked manifest hashes to "
                  f"{manifest_hash}, not the first-worker "
                  f"assignment's released source-set "
                  f"identity {EXPECTED_MANIFEST_HASH}",
                  file=sys.stderr)
            return abort_report({
                "abort_stage": "stocking identity",
                "abort_reason":
                    "the stocked source set is not the "
                    "released one (manifest identity "
                    "mismatch)"})

        # COMMISSION — the room configuration's
        # assignment, the stocking manifest as the sealed
        # source set, the pre-activation verification.
        store = FrameworkStore(store_path)
        store.insert_run(RUN_ID, CONSTITUTION_HASH)
        opening = _load_opening(demo_dir, run_dir)
        doorway, office, gen, tok, issued = \
            _commission_and_issue(
                store, manifest_hash, opening=opening)
        print("pre-activation verification: manifest hash "
              "in the issued case's evidence boundary; "
              "bounds as scoped; the case carries the "
              "glossary")

        # STAGE THE PULL DOOR — the executor sandbox's
        # sources, hash-verified against the stocking
        # manifest, at the glossary's addresses; the
        # sandbox's scratch/ stands as the doorway write
        # path's home.
        staging_problem = _stage_sandbox_sources(
            run_dir / "sandbox", manifest)
        if staging_problem is not None:
            print(f"ABORT: sandbox staging failed: "
                  f"{staging_problem}", file=sys.stderr)
            return abort_report({
                "abort_stage": "sandbox staging",
                "abort_reason": staging_problem})
        print("sandbox staging: the released sources "
              "staged at the glossary's addresses, each "
              "hash-verified against the manifest")

        # THE WORKED EXAMPLE (round nine, INDEX 548;
        # the calibration): under the staged contracts
        # the office performed the demonstration call
        # against the staged sandbox before generation
        # and sealed its result beside the presentation
        # contract. Under the office-cycle contract (the
        # plan of 2026-11-25) no worked example stands in
        # the seal either: the cycle poster in the
        # opening package — the job's shape in words and
        # the block map with an access way per block —
        # is the demonstration's replacement.
        worked_example = None
        print("worked example: none stands in the seal "
              "under the office-cycle contract — the "
              "cycle poster is the demonstration's "
              "replacement")

        # THE BLOCK MAP (the plan §3): the office
        # portions the staged evidence files into travel
        # blocks at the ruled ceiling, from the staged
        # bytes, and seals the map beside the cycle
        # contract at generation.
        block_map = _block_map_for_sandbox(
            run_dir / "sandbox")
        print(f"block map: {len(block_map)} blocks "
              f"portioned from the staged evidence at "
              f"the {tool_policy.BLOCK_CEILING_BYTES}-"
              f"byte ceiling")

        # ASSEMBLE — the adapter on the occupant
        # route's real seam: the typed transport
        # through the capture pass-through to the
        # registered connector helper. Generation
        # under the exec catalogue contract — and,
        # under office-cycle-v8, under NO probe
        # contract and with NO identity call: the
        # director's rulings of 2026-11-25 23:07 and
        # 23:08 MST removed both from this launch.
        # The identify argument is the office's own
        # declaration mapping (OFFICE_IDENTITY_
        # DECLARATION): the generator accepts a
        # mapping in place of a callable, the
        # onboarding records the office's declaration
        # as the instance's identity, and no provider
        # call of any kind stands before the opening.
        # Grants the combined surface (INDEX 476):
        # the execution tool, the retrieval four under
        # sources/ and under scratch/, and
        # sandbox.write under scratch/.
        adapter = OpenAICompatibleAdapter(
            endpoint=ENDPOINT, model=MODEL,
            timeout=ADAPTER_TIMEOUT, route=ROUTE)
        _install_typed_transport(adapter, wrapper_path)
        # The road (the §6 amendment): where the run's
        # generation seals the road, the adapter's
        # calls are counted and paced under the
        # route's shared bucket — the Groq route's
        # measured limits — and the loop's model is
        # the adapter itself: the 65-second pacer
        # stands retired on a road run (the examiner:
        # interim only, never a second limiter), the
        # bucket doing the pacing minute-aware.
        road_ctx = None
        if _road_declaration() is not None:
            if GPTOSS:
                # The Groq route's measured limits.
                road_tpm, road_tpd = 8000, 200000
                road_limits = "paced against the " \
                    "route's shared bucket (8,000/min, " \
                    "200,000/day)"
            else:
                # The NVIDIA route's limits stand
                # unmeasured: the bucket's figures are
                # the office's placeholders — they do
                # not bind; reservations, counting and
                # accounting stand.
                road_tpm, road_tpd = 1000000, 100000000
                road_limits = "the route's limits " \
                    "unmeasured — the bucket's figures " \
                    "are placeholders that do not bind"
            road_ctx = road_mod.road_context_for(
                f"{ROUTE}:{MODEL}", MODEL,
                road_tpm, road_tpd,
                output_allowance=tool_policy
                .ROAD_OUTPUT_ALLOWANCE_TOKENS)
            adapter.attach_road(road_ctx)
            print("road: paced-v1 attached — calls "
                  "counted under "
                  f"{road_ctx['counter'].method}, "
                  f"{road_limits}, "
                  "the fixed-interval pacer retired "
                  "for this run")
        gen.propose(
            tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a model able to read three "
                              "source documents in its room "
                              "and write a short, accurate, "
                              "plain-words brief")
        generated = gen.generate(
            tok["orch-1"], "crew-1",
            OFFICE_IDENTITY_DECLARATION,
            skills=[], grants=GRANTS_COMBINED,
            model_requested=MODEL, probe=False,
            exec_room=True, freshness_suspended=True,
            delivery_declaration=True,
            delivery_evidence_declaration=True,
            delivery_floor_declaration=True,
            presentation_declaration=_presentation_declaration(),
            worked_example=worked_example,
            block_map=block_map,
            road_declaration=_road_declaration(),
            tree_declaration=_tree_declaration())
        if not generated.get("ok"):
            print(f"ABORT: generation failed: "
                  f"{generated.get('problems')}",
                  file=sys.stderr)
            return abort_report({
                "abort_stage": "generation",
                "flagged_conflict": False,
                "abort_reason": "generation failed: "
                                f"{generated.get('problems')}"})
        assembly_id = generated["assembly_id"]
        instance_id = generated["instance_id"]
        print(f"assembly: {assembly_id} (instance "
              f"{instance_id}); identity office-declared "
              f"from the sealed configuration "
              f"({MODEL} on the {ROUTE} route) — no "
              f"identity call stands in this launch "
              f"(office-cycle-v8)")

        # NO PROBE STAGE (office-cycle-v8; the
        # director's ruling of 2026-11-25 23:07 MST):
        # the pre-loop probe phase sends ZERO probe
        # cases under this contract — the assembly was
        # generated with probe=False, so no probe
        # contract stands sealed, and the lifecycle
        # keeps its standing exemption for an assembly
        # carrying none: verification and judgement
        # proceed on the historical path, exactly as
        # they did for every assembly before the probe
        # regime existed. The probe machinery itself
        # stands untouched for the contracts that
        # still seal it.
        probe_result = None
        gen.verify(tok["orch-1"], assembly_id)

        # JUDGE (hop 1) — the director's order record,
        # retained before the judgement is recorded; the
        # judgement binds its canonical hash. Under v8
        # no ASSEMBLY_PROBED stands to source the
        # generated record's hash: it is computed from
        # the sealed generated payload directly, the
        # same value the probe event carried for the
        # contracts that seal one.
        probed_payload = None
        generated_record_hash = assembly_record_hash(
            doorway._generated_payload(assembly_id))
        order = _order_record(
            assembly_id, instance_id,
            generated_record_hash,
            probed_payload, probe_result)
        order["launch"] = {
            "contract": "office-cycle-v8",
            "probe_stage": (
                "none — no probe stage ran under "
                "office-cycle-v8 (the director's "
                "ruling of 2026-11-25 23:07 MST); the "
                "probe fields above stand null, and "
                "the order texts' sentences about a "
                "probe stage are this occupant's "
                "standing order texts, retained "
                "unedited — they do not describe this "
                "launch"),
            "identity": (
                "office-declared — no identity call "
                "stands in this launch (the director's "
                "ruling of 2026-11-25 23:08 MST); "
                "the instance's identity stands in "
                "the record from the office's sealed "
                "assembly"),
            "first_call": (
                "the opening package — no pre-loop "
                "call precedes it, and no launch wait "
                "stands before it")}
        order_path = demo_dir / "order-record.json"
        with open(order_path, "w",
                  encoding="utf-8") as fh:
            json.dump(order, fh, indent=1)
            fh.write("\n")
        order_hash = _sha256_bytes(canonical(order))
        judgement = gen.judgement(
            assembly_id, adapter_mode=ADAPTER_MODE,
            mode_grounds=OFFICE_MODE_GROUNDS,
            decision_receipt_hash=order_hash,
            decision_examiner=ORDER_EXAMINER)
        _act(doorway, tok["exam-1"], "ASSEMBLY_JUDGED",
             judgement)
        packed = gen.pack(tok["orch-1"], assembly_id)
        gen.authorise(tok["orch-1"], assembly_id)
        print(f"judgement: recorded by the director's "
              f"order (order record sha256: "
              f"{order_hash}); under office-cycle-v8 "
              f"the judgement act binds the generated "
              f"record and the office-declared mode "
              f"({ADAPTER_MODE}) — declared from the "
              f"sealed configuration's standing "
              f"judgement, sealed by the pack, and the "
              f"mode the loop travels in")

        # RUN — the executor holds the room; the loop
        # drives the real adapter/doorway/rig path under
        # the evidence regime rooted at the run directory,
        # its outbound iteration calls paced at this
        # driver's stated interval.
        executor = Executor(
            doorway, str(run_dir / "sandbox"),
            claim_dir=str(run_dir / "claims"),
            deadline=150.0, room=room,
            exec_timeout=stock_demo.PER_EXECUTION_WALL_S)
        gen.activate(tok["orch-1"], assembly_id)
        paced = IterationPacer(
            adapter, min_interval=PACING_INTERVAL_SECONDS)
        # Under the road the loop's model is the
        # adapter itself — the bucket paces; the
        # pacer's fixed interval does not stand as a
        # second limiter over it.
        loop_model = adapter if road_ctx is not None \
            else paced
        # THE LAUNCH (office-cycle-v8): the launch
        # rule of the plan §6 (Qualification B) has
        # nothing to space under this contract — no
        # pre-loop call exists: no identity call, no
        # probe. The opening package is simply the
        # run's first call, and no wait stands before
        # it. The loop's own pacing governs every call
        # after it, as before.
        launch_wait = 0.0
        print("launch: no pre-loop calls stand under "
              "office-cycle-v8 — the opening package "
              "is the run's first call, with no launch "
              "wait before it")
        loop = Loop(doorway, packed["instance_token"],
                    loop_model, executor=executor,
                    evidence_store=str(run_dir))
        result = loop.run()

        # COLLECT — the deliverable and its hash at the
        # wall (hop 9) and the room's final state, taken
        # before teardown; then the checker (hop 10),
        # the export, and the terminal readout over the
        # export. The combined configuration gives the
        # brief TWO resting places — the room's scratch
        # (written via container.exec) and the framework
        # sandbox's scratch (written via sandbox.write)
        # — and both are checked: the room's is primary
        # when both stand, the other is collected beside
        # it under its own name with its own hash, and
        # the report records which path he used. The two
        # are never merged.
        room_brief_path = room.tree / "scratch" / "brief.md"
        room_brief = room_brief_path.read_bytes() \
            if room_brief_path.exists() else None
        fw_brief_path = run_dir / "sandbox" / "scratch" \
            / "brief.md"
        fw_brief = fw_brief_path.read_bytes() \
            if fw_brief_path.exists() else None

        def _brief_facts(data):
            if data is None:
                return None, None
            return _sha256_bytes(data), len(data.decode(
                "utf-8", "replace").split())

        room_sha256, room_words = _brief_facts(room_brief)
        fw_sha256, fw_words = _brief_facts(fw_brief)
        if room_brief is not None:
            brief_path_used = "room"
            brief_bytes = room_brief
        elif fw_brief is not None:
            brief_path_used = "framework_scratch"
            brief_bytes = fw_brief
        else:
            brief_path_used = None
            brief_bytes = None
        brief_sha256, brief_words = _brief_facts(
            brief_bytes)
        if brief_bytes is not None:
            (demo_dir / "brief.md").write_bytes(
                brief_bytes)
        if room_brief is not None and fw_brief is not None:
            (demo_dir / "brief-framework.md").write_bytes(
                fw_brief)
        room_state = json.loads(room.state_path.read_text())
        (demo_dir / "room-state.json").write_text(
            json.dumps(room_state, indent=1),
            encoding="utf-8")
        (demo_dir / "stocking.json").write_text(
            json.dumps(stocking, indent=1),
            encoding="utf-8")
        events = store.all_events()
        outcomes = {}
        for e in events:
            if e["type"] == "TOOL_OUTCOME":
                outcomes[e["payload"].get("dispatch_id")] \
                    = e["payload"].get("outcome")
        dispatches = [
            {"dispatch_id": e["payload"].get("dispatch_id"),
             "tool": e["payload"].get("tool"),
             "request_id": e["payload"].get("request_id"),
             "outcome": outcomes.get(e["payload"].get(
                 "dispatch_id"))}
            for e in events if e["type"] == "TOOL_DISPATCHED"]
        stalls = [e for e in events
                  if e["type"] == "LOOP_STALLED"]
        identity = instance_onboarding_record(
            doorway, instance_id) or {}
        verdict = run_checker(store)
        export_store(store_path,
                     str(run_dir / "run-export.json"))
        readout_path = demo_dir / "terminal-readout.md"
        readout = subprocess.run(
            [sys.executable, str(HERE / "terminal_readout.py"),
             "render", str(run_dir / "run-export.json"),
             "-o", str(readout_path)],
            capture_output=True, text=True)
        outcome_word = {
            "yield": "completed",
            "decline": "declined",
            "stalled": "stalled",
            "not_run": "not_run",
        }.get(result.get("outcome"), result.get("outcome"))
        _filings = [e for e in events
                    if e["type"] == "DELIVERABLE_FILED"]
        brief_filed = None
        if _filings:
            _fp = _filings[-1]["payload"]
            brief_filed = {
                "destination": _fp.get("destination"),
                "sha256": _fp.get("content_sha256"),
                "authored_by": _fp.get("authored_by"),
                "filed_by": _fp.get("filed_by")}
        captures_count = sum(
            1 for line in
            captures_path.read_text(
                encoding="utf-8").splitlines()
            if line.strip())
        # The road's accounting (the plan §6): the
        # call ledger over every call that shared the
        # model's minute, written beside the report,
        # and the cycle summary (§7) derived from the
        # record.
        ledger_entries, ledger_summary = _call_ledger(
            captures_path, events, loop, run_dir)
        ledger_path = demo_dir / "call-ledger.json"
        with open(ledger_path, "w",
                  encoding="utf-8") as fh:
            json.dump({
                "kind": "call ledger (derived matter, "
                        "not record): every call sharing "
                        "the model's minute — under "
                        "office-cycle-v8 the loop's calls "
                        "alone: no identity call and no "
                        "probe call precede the opening "
                        "— with wire bytes and estimates "
                        "under the one estimator",
                "entries": ledger_entries,
                "summary": ledger_summary}, fh, indent=1)
            fh.write("\n")
        cycle_summary = _cycle_summary(
            events, doorway, assembly_id,
            issued["case_id"])
        report = {
            "kind": "first-worker demonstration run "
                    "report (derived matter, not record)",
            "run_id": RUN_ID,
            "model_pin": MODEL,
            "route": ROUTE_REPORT_LABEL,
            "endpoint": ENDPOINT,
            "manifest_hash": manifest_hash,
            "assembly_id": assembly_id,
            "instance_id": instance_id,
            "identity_evidence": {
                "declaration": identity.get("declaration"),
                "provider_model_id":
                    identity.get("provider_model_id"),
                "identity_status":
                    identity.get("identity_status"),
                "pin_verified":
                    identity.get("provider_model_id")
                    == MODEL,
                "note": "office-declared identity "
                        "(office-cycle-v8; the "
                        "director's ruling of 2026-11-25 "
                        "23:08 MST): no identity call "
                        "stands in this launch — the "
                        "declaration and the model id "
                        "above are the office's own, "
                        "from the sealed occupant "
                        "configuration it assembled, "
                        "recorded at onboarding as the "
                        "instance's identity. No "
                        "provider self-report stands in "
                        "this record, and none is "
                        "claimed: 'pin_verified' here "
                        "states only that the declared "
                        "id is the run's pin, by "
                        "construction",
            },
            "probe": {
                "settled_count": None,
                "recommended_mode": None,
                "counts": None,
                "evidence_hash": None,
                "note": "no probe stage ran under "
                        "office-cycle-v8 (the "
                        "director's ruling of 2026-11-25 "
                        "23:07 MST): the assembly was "
                        "generated with no probe "
                        "contract sealed, and the "
                        "lifecycle's standing exemption "
                        "for such an assembly carried "
                        "verification and judgement. "
                        "This run's mode was judged by "
                        "the director's order",
            },
            "order_record": {
                "path": str(order_path),
                "sha256": order_hash,
                "adapter_mode": ADAPTER_MODE,
                "decision_examiner": ORDER_EXAMINER,
            },
            "pacing": {
                "min_interval_seconds":
                    PACING_INTERVAL_SECONDS,
                "note": PACING_NOTE,
            },
            "road": {
                "sealed": _road_declaration(),
                "totals": adapter.road_totals(),
                "transport_events":
                    road_ctx["events"]
                    if road_ctx is not None else [],
                "presentation_events":
                    list(loop.road_events),
                "note": "the §6 amendment's accounting "
                        "for this run: the sealed "
                        "declaration the generation "
                        "carries; the route's standing "
                        "totals (consumed tokens are "
                        "the provider's reconciled "
                        "figures); every governed call "
                        "with its predicted and actual "
                        "figures standing separate — "
                        "measured facts and estimates "
                        "never blended; and the "
                        "presentation pass's spill and "
                        "shedding acts. Where no road "
                        "was sealed, the run travelled "
                        "under the per-call budget and "
                        "the pacer, as before",
            },
            "call_ledger": {
                "path": str(ledger_path),
                "calls": ledger_summary["calls"],
                "minimum_gap_seconds":
                    ledger_summary[
                        "minimum_gap_seconds"],
                "largest_single_call_estimate":
                    ledger_summary[
                        "largest_single_call_estimate"],
                "largest_wire_estimate":
                    ledger_summary[
                        "largest_wire_estimate"],
                "launch_wait_seconds": launch_wait,
                "note": "every call sharing the model's "
                        "minute stands in the ledger — "
                        "under office-cycle-v8 the loop's "
                        "calls alone (no identity call, "
                        "no probe calls precede the "
                        "opening) — with its wire bytes "
                        "and the loop's package estimates "
                        "beside them; the minimum gap is "
                        "over the record's own timestamps "
                        "(each iteration's call)",
            },
            "summary": cycle_summary,
            "bounds": {
                "step_ceiling":
                    DEMO_BOUNDS["step_ceiling"],
                "deadline_seconds":
                    DEMO_BOUNDS["deadline_seconds"],
                "derivation": BOUNDS_DERIVATION,
            },
            "brief_filed": brief_filed,
            "loop_result": {
                "ok": result.get("ok"),
                "outcome": result.get("outcome"),
                "outcome_summary": outcome_word,
                "ground": result.get("ground"),
                "iterations": result.get("iterations"),
            },
            "stall": ({"ground": stalls[0]["payload"].get(
                            "ground"),
                       "event_seq": stalls[0]["event_seq"]}
                      if stalls else None),
            "dispatches": dispatches,
            "brief": {
                "exists": brief_bytes is not None,
                "path_used": brief_path_used,
                "sha256_at_wall": brief_sha256,
                "word_count": brief_words,
                "collected_path": str(
                    demo_dir / "brief.md")
                if brief_bytes is not None else None,
                "room": {
                    "exists": room_brief is not None,
                    "sha256_at_wall": room_sha256,
                    "word_count": room_words,
                },
                "framework_scratch": {
                    "exists": fw_brief is not None,
                    "sha256_at_wall": fw_sha256,
                    "word_count": fw_words,
                    "collected_path": str(
                        demo_dir / "brief-framework.md")
                    if room_brief is not None
                    and fw_brief is not None else None,
                },
                "note": "the brief may land by either "
                        "write path — the room's scratch "
                        "(via container.exec) or the "
                        "framework sandbox's scratch (via "
                        "sandbox.write); the room's is "
                        "primary when both stand, and the "
                        "two are never merged",
            },
            "captures": {
                "path": str(captures_path),
                "transmitted_requests": captures_count,
            },
            "checker": verdict.get("checks"),
            "event_count": len(events),
            "terminal_readout": {
                "rendered": readout.returncode == 0,
                "path": str(readout_path),
                "stderr": readout.stderr[-500:]
                if readout.returncode != 0 else None,
            },
        }
        with open(demo_dir / "report.json", "w",
                  encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
        print(f"outcome: {outcome_word} "
              f"(loop outcome {result.get('outcome')!r}, "
              f"ok={result.get('ok')}), iterations: "
              f"{result.get('iterations')}, dispatches: "
              f"{len(dispatches)}, brief: "
              f"{'written via ' + str(brief_path_used) + ', '
                 + str(brief_words) + ' words, sha256 '
                 + str(brief_sha256)
                 if brief_bytes is not None
                 else 'not written'}")
        print(f"report: {demo_dir / 'report.json'}")
        return 0 if result.get("ok") else 1
    finally:
        if room is not None:
            try:
                room.destroy(remove_tree=True)
            except Exception:
                pass



def verify_config():
    """The offline configuration check: no provider
    contact, no activation, nothing recorded outside a
    throwaway directory. Stocks and destroys a room,
    builds the assembly under a stub identity, installs
    the real transports without invoking them, exercises
    the capture seam against a local echo delegate,
    computes (does not record) the judgement payload the
    director's order will bind, and asserts the pin
    machinery, the exec catalogue contract and the v4
    ceiling checks. Prints one line per item and a final
    VERIFY-CONFIG line; returns 0 on PASS, 1 on FAIL."""
    problems = []

    def expect(label, condition, detail=""):
        line = f"{'PASS' if condition else 'FAIL'}  {label}"
        if detail and not condition:
            line += f" — {detail}"
        print(line)
        if not condition:
            problems.append(label)

    print("verify-config: offline configuration check "
          "(no provider contact; the recorded judgement "
          "and activation are live steps and are NOT "
          "run here — and under office-cycle-v8 no "
          "probe stage exists in the launch to run: "
          "the expectations below witness the launch "
          "with neither a probe contract nor an "
          "identity call)")
    tmp = Path(tempfile.mkdtemp(prefix="demo-run-verify-"))
    saved_env = {key: os.environ.get(key) for key in
                 ("DEMO_RUN_CAPTURES",
                  "DEMO_RUN_DELEGATE_HELPER")}
    try:
        rooms_base = tmp / "rooms"
        rooms_base.mkdir(parents=True)

        # (1) Stocking: the manifest identity and every
        # source hash against the paper §1.1 table, the
        # smoke set all-ok, the deliverable absent at
        # stocking end; then the room destroyed.
        stocking = stock_demo.stock_demo_room(
            rooms_base, "demo")
        manifest = stocking["source_manifest"]
        expect("stocking: manifest identity is the "
               "released source-set identity",
               manifest["manifest_sha256"]
               == EXPECTED_MANIFEST_HASH,
               f"got {manifest['manifest_sha256']}")
        by_path = {e["path"]: e["sha256"]
                   for e in manifest["sources"]}
        for rel, want in PAPER_SOURCE_HASHES.items():
            expect(f"stocking: source hash matches the "
                   f"paper §1.1 table: {rel}",
                   by_path.get(rel) == want,
                   f"got {by_path.get(rel)}")
        expect("stocking: smoke set all-ok",
               bool(stocking["smoke"]) and all(
                   entry["ok"] for entry in
                   stocking["smoke"]),
               json.dumps(stocking["smoke"])[:300])
        deliverable = stocking["deliverable"]
        expect("stocking: smoke probe removed and "
               "deliverable absent at stocking end",
               deliverable["smoke_probe_removed"] is True
               and deliverable["present_at_stocking_end"]
               is False,
               json.dumps(deliverable)[:200])
        completability = stocking.get("completability") \
            or {}
        comp_sources = completability.get("sources") or []
        expect("stocking: completability verified — "
               "every source carriable whole under the "
               "working-set budget, the accumulated set "
               "carriable together (the freedom-first "
               "setup pass)",
               completability.get("ok") is True
               and len(comp_sources) == 3
               and all(f.get("carriable_whole") is True
                       for f in comp_sources)
               and completability.get(
                   "accumulated_bytes")
               == sum(f.get("bytes", 0)
                      for f in comp_sources)
               and completability.get(
                   "accumulated_carriable") is True,
               json.dumps(completability)[:300])
        tree = Path(stocking["tree"])
        room = room_mod.load_room(rooms_base, "demo")
        room.destroy(remove_tree=True)
        room = None
        expect("stocking: room destroyed, tree gone",
               not tree.exists())

        # (2) Commission + issue + the pre-activation
        # verification in a throwaway store.
        store = FrameworkStore(str(tmp / "run.db"))
        store.insert_run(RUN_ID, CONSTITUTION_HASH)
        _MANIFEST_ENTRIES.clear()
        _MANIFEST_ENTRIES.extend(manifest["sources"])
        commissioned = None
        try:
            commissioned = _commission_and_issue(
                store, manifest["manifest_sha256"])
        except RuntimeError as exc:
            expect("commission: issue + pre-activation "
                   "verification (manifest in boundary, "
                   "re-derived bounds)", False, str(exc))
        if commissioned is not None:
            expect("commission: issue + pre-activation "
                   "verification (manifest in boundary, "
                   "re-derived bounds)", True)
            doorway, office, gen, tok, issued = \
                commissioned

            # (3) The capture seam: the wrapper against a
            # local echo delegate — byte-exact
            # pass-through and a faithful captures line
            # per mode. The delegate is then restored to
            # the real connector helper.
            captures_path = tmp / "captures.jsonl"
            captures_path.write_text("", encoding="utf-8")
            wrapper_path = _write_capture_helper(
                tmp / "capture_helper.py")
            echo_path = tmp / "echo_delegate.py"
            echo_path.write_text(
                "import sys\n"
                "sys.stdout.buffer.write("
                "sys.stdin.buffer.read())\n",
                encoding="utf-8")
            os.environ["DEMO_RUN_CAPTURES"] = \
                str(captures_path)
            os.environ["DEMO_RUN_DELEGATE_HELPER"] = \
                str(echo_path)
            payload = json.dumps({
                "messages": [{"role": "user",
                              "content": "verify-config"}],
            }).encode()
            for mode in ("chat", "chat-raw-bounded"):
                proc = subprocess.run(
                    [sys.executable, str(wrapper_path),
                     mode, MODEL],
                    input=payload, capture_output=True)
                expect(f"capture seam: {mode} pass-through "
                       f"is byte-exact, exit 0",
                       proc.returncode == 0
                       and proc.stdout == payload,
                       f"rc={proc.returncode} "
                       f"out={proc.stdout[:80]!r}")
            lines = [json.loads(line) for line in
                     captures_path.read_text(
                         encoding="utf-8").splitlines()
                     if line.strip()]
            expect("capture seam: one captures line per "
                   "mode, per-mode index 0, bytes and "
                   "SHA-256 faithful",
                   len(lines) == 2
                   and all(
                       line["index"] == 0
                       and line["model"] == MODEL
                       and line["request_bytes"]
                       == len(payload)
                       and line["request_sha256"]
                       == _sha256_bytes(payload)
                       and base64.b64decode(
                           line["request_b64"]) == payload
                       for line in lines)
                   and {line["mode"] for line in lines}
                   == {"chat", "chat-raw-bounded"},
                   json.dumps(lines)[:300])
            os.environ["DEMO_RUN_DELEGATE_HELPER"] = \
                DELEGATE_HELPER

            # (4) The real transports install (no
            # invocation): the adapter's typed call is
            # the occupant route's connector transport,
            # bound to the capture seam; the raw call is
            # callable.
            adapter = OpenAICompatibleAdapter(
                endpoint=ENDPOINT, model=MODEL,
                timeout=ADAPTER_TIMEOUT, route=ROUTE)
            installed = _install_typed_transport(
                adapter, wrapper_path)
            expect("transport: real connector transport "
                   "installed on the adapter",
                   callable(installed)
                   and adapter._call is installed)
            raw_call = _install_raw_call(
                adapter, wrapper_path)
            expect("transport: real Groq raw call "
                   "installed (the raw-call seam stands; "
                   "under office-cycle-v8 no probe stage "
                   "calls it)"
                   if (QUINN or GPTOSS) else
                   "transport: real Cloudflare raw call "
                   "installed (the raw-call seam stands; "
                   "under office-cycle-v8 no probe stage "
                   "calls it)"
                   if GLM else
                   "transport: real NVIDIA raw call "
                   "installed (the raw-call seam stands; "
                   "under office-cycle-v8 no probe stage "
                   "calls it)",
                   callable(raw_call))

            # (5) The pin machinery: exact match passes;
            # anything else raises the flagged-conflict
            # stop.
            expect("pin: exact provider id passes",
                   check_model_pin(MODEL, MODEL) is True)
            raised = None
            try:
                check_model_pin(
                    "nvidia/some-other-model", MODEL)
            except ModelPinMismatchError as exc:
                raised = exc
            expect("pin: a different provider id raises "
                   "ModelPinMismatchError",
                   raised is not None
                   and raised.pinned_model == MODEL
                   and raised.provider_model_id
                   == "nvidia/some-other-model")

            # The worked example (round nine, INDEX
            # 548; the calibration): under the staged
            # contracts the generation below sealed the
            # office's demonstration call. Under the
            # office-cycle contract (the plan of
            # 2026-11-25) no example is performed or
            # sealed: the cycle poster in the opening
            # package is the demonstration's replacement.
            # The expectation below verifies the seal
            # carries none.
            verify_example = None

            # The block map (the plan §3): the sandbox
            # sources stage here (the same staging the
            # (6b) expectation below verifies) and the
            # office portions them at the ruled ceiling;
            # the map seals beside the cycle contract at
            # the generation below.
            _stage_sandbox_sources(tmp / "sandbox",
                                   manifest)
            verify_block_map = _block_map_for_sandbox(
                tmp / "sandbox")

            # (6) Generation under the office's own
            # identity declaration — the same constant
            # the live driver passes (office-cycle-v8:
            # no identity call, no probe contract): the
            # sealed record declares the exec catalogue
            # contract and NO probe contract, and holds
            # exactly the combined grant set (INDEX 476).
            gen.propose(
                tok["orch-1"], "crew-1", part="part-A",
                role_requirements="verify-config stub")
            generated = gen.generate(
                tok["orch-1"], "crew-1",
                OFFICE_IDENTITY_DECLARATION,
                skills=[], grants=GRANTS_COMBINED,
                model_requested=MODEL, probe=False,
                exec_room=True, freshness_suspended=True,
                delivery_declaration=True,
                delivery_evidence_declaration=True,
                delivery_floor_declaration=True,
                presentation_declaration=_presentation_declaration(),
                worked_example=verify_example,
                block_map=verify_block_map,
                road_declaration=_road_declaration(),
                tree_declaration=_tree_declaration())
            expect("generation: office-declared-identity "
                   "generation succeeds (no identity "
                   "call stands behind it — the "
                   "declaration is the office's own "
                   "mapping, the constant the live "
                   "driver passes)",
                   generated.get("ok") is True,
                   json.dumps(generated)[:300])
            if generated.get("ok"):
                assembly_id = generated["assembly_id"]
                sealed = None
                for ev in store.all_events():
                    if ev["type"] == "ASSEMBLY_GENERATED" \
                            and ev["payload"].get(
                                "assembly_id") == assembly_id:
                        sealed = ev["payload"]
                sealed = sealed or {}
                expect("generation: sealed record "
                       "declares the exec catalogue "
                       "contract",
                       sealed.get("catalogue_contract")
                       == tool_policy
                       .EXEC_CATALOGUE_CONTRACT,
                       f"got "
                       f"{sealed.get('catalogue_contract')}")
                expect("generation: sealed grants are "
                       "exactly the combined set",
                       sealed.get("grants")
                       == GRANTS_COMBINED,
                       json.dumps(sealed.get("grants"))
                       [:300])
                expect("generation: the assembly is "
                       "exec-governed",
                       doorway._exec_governed(sealed)
                       is True)
                expect("generation: the assembly is "
                       "retrieval-governed for its "
                       "retrieval tools (the combined "
                       "configuration)",
                       doorway._retrieval_governed(sealed)
                       is True)
                expect("generation: the sealed record "
                       "declares the working-set contract "
                       "(the combined configuration carries "
                       "its gathered material forward, the "
                       "run-3 correction)",
                       sealed.get("working_set_contract")
                       == tool_policy.WORKING_SET_CONTRACT,
                       f"got "
                       f"{sealed.get('working_set_contract')}")
                expect("generation: the sealed record "
                       "declares the office-cycle "
                       "presentation contract in its "
                       "imperative-first form (the plan "
                       "of 2026-11-25, approved INDEX 582 "
                       "and examined INDEX 584; the "
                       "split-on-return successor per "
                       "the director's strip ruling of "
                       "2026-11-25, its draft-page "
                       "successor per the director's "
                       "ruling of 2026-11-25 21:16 MST "
                       "after demo-gptoss6, its "
                       "cleaned-opening successor per "
                       "the director's orders of "
                       "2026-11-25 21:33/21:36 MST after "
                       "demo-gptoss7, its carryover "
                       "successor per the director's "
                       "orders of 2026-11-25 22:09 MST "
                       "after demo-gptoss8, and its "
                       "zero-carryover successor per "
                       "the director's rulings of "
                       "2026-11-25 22:29/22:30 MST after "
                       "the carryover build measured "
                       "its budget collision, and its "
                       "imperative-first successor per "
                       "the director's order of "
                       "2026-11-25 22:41 MST, given as "
                       "demo-gptoss9's packages were "
                       "seen to describe state and "
                       "leave the deciding to the "
                       "worker — the "
                       "opening the director's own "
                       "plain-text structure behind a "
                       "compressed outcome frame, then "
                       "one package per cycle over the "
                       "briefcase's blocks, a package "
                       "presenting at most the current "
                       "cycle's block content and every "
                       "other gathered block standing "
                       "as a pointer, the statement line "
                       "formatted from the sealed "
                       "delivery declaration, the gates' "
                       "corrections riding again, the "
                       "blocks component slimmed to "
                       "each block's place and state, "
                       "and the journal carried nowhere "
                       "— it stands in his scratch at "
                       "its address and he reads it "
                       "himself, by pull — its texts "
                       "carrying the draft-page "
                       "correction: the brief built in "
                       "the journal gradually, as "
                       "step-by-step instructions, "
                       "and every package opening "
                       "with the one next step "
                       "stated as an imperative — "
                       "the Next line — before any "
                       "state — and its file-grain "
                       "successor per the director's "
                       "orders of 2026-11-25 23:03 MST "
                       "(the walk's unit the file, a "
                       "multi-part file's slices "
                       "plumbing inside its step, the "
                       "gate once per file) and "
                       "23:07/23:08 MST (no probe "
                       "stage, no identity call in "
                       "the launch): the opening "
                       "renders files, the bookkeeping "
                       "lists files, and the Next line "
                       "derives from the file state)",
                       sealed.get("presentation_contract")
                       == _presentation_declaration()
                       and sealed.get("tree")
                       == _tree_declaration(),
                       f"got "
                       f"{sealed.get('presentation_contract')}")
                expect("generation: the sealed record "
                       "carries the office's block map — "
                       "the map derived from the staged "
                       "bytes at the ruled ceiling, "
                       "portioning the declared evidence "
                       "whole and in declaration order "
                       "(the plan §3; it replaces the "
                       "worked-example expectation — no "
                       "example seals under the cycle "
                       "contract, the cycle poster is "
                       "its replacement)",
                       sealed.get("block_map")
                       == verify_block_map
                       and sealed.get("worked_example")
                       is None,
                       f"got "
                       f"{sealed.get('block_map')}")
                expect("generation: the sealed record "
                       "carries the office's file map — "
                       "the block map's files in order, "
                       "each file grouping its blocks "
                       "whole (office-cycle-v8: the "
                       "walk's unit sealed beside its "
                       "plumbing)",
                       sealed.get("file_map")
                       == tool_policy.compute_file_map(
                           verify_block_map),
                       f"got "
                       f"{sealed.get('file_map')}")
                expect("launch: the sealed record "
                       "carries NO probe contract "
                       "(office-cycle-v8; the director's "
                       "ruling of 2026-11-25 23:07 MST — "
                       "the driver's pre-loop phase "
                       "sends zero probe cases, and the "
                       "assembly is generated under no "
                       "probe regime)",
                       "probe_contract" not in sealed,
                       f"got "
                       f"{sealed.get('probe_contract')}")
                _onboarding = \
                    instance_onboarding_record(
                        doorway, generated["instance_id"]) \
                    or {}
                expect("launch: the instance's identity "
                       "stands office-declared — the "
                       "onboarding records the office's "
                       "own declaration and the pin as "
                       "its model id, the constant the "
                       "live driver passes (office-"
                       "cycle-v8; the director's ruling "
                       "of 2026-11-25 23:08 MST — no "
                       "identity call stands behind "
                       "this record)",
                       _onboarding.get("declaration")
                       == OFFICE_IDENTITY_DECLARATION[
                           "declaration"]
                       and _onboarding.get(
                           "provider_model_id") == MODEL,
                       json.dumps(_onboarding)[:300])
                gen.verify(tok["orch-1"], assembly_id)
                _event_types = [
                    ev["type"] for ev in
                    store.all_events()
                    if ev["payload"].get("assembly_id")
                    == assembly_id]
                expect("launch: verification stands "
                       "with NO probed act in the "
                       "record — ASSEMBLY_VERIFIED "
                       "recorded, no ASSEMBLY_PROBED "
                       "anywhere (the lifecycle's "
                       "standing exemption for an "
                       "assembly under no probe "
                       "contract, exercised: a v8 run's "
                       "first call is its opening, and "
                       "nothing precedes it)",
                       "ASSEMBLY_VERIFIED" in _event_types
                       and "ASSEMBLY_PROBED"
                       not in _event_types,
                       f"got {_event_types}")
                expect("generation: the sealed record "
                       "declares the freshness guard "
                       "suspended (Ben's R31 ruling, "
                       "2026-11-24 — the run-6 "
                       "configuration)",
                       sealed.get("freshness_guard")
                       == tool_policy
                       .FRESHNESS_GUARD_SUSPENDED,
                       f"got "
                       f"{sealed.get('freshness_guard')}")
                case_content, _case_version = \
                    established_case_content(
                        doorway.state(), issued["case_id"])
                expect("commission: the issued case "
                       "carries the glossary as its own "
                       "component, unchanged",
                       (case_content or {}).get("glossary")
                       == GLOSSARY,
                       json.dumps(
                           (case_content or {}).get(
                               "glossary"))[:300])
                expect("commission: the issued case "
                       "carries the journal designation "
                       "as its own component, unchanged "
                       "(the orientation pass)",
                       (case_content or {}).get("journal")
                       == JOURNAL_PATH,
                       json.dumps(
                           (case_content or {}).get(
                               "journal"))[:300])
                expect("generation: the sealed record "
                       "carries the journal baseline — "
                       "the case's designated journal "
                       "address and the hash of the empty "
                       "string, the trusted initial state "
                       "every accepted journal transition "
                       "extends (the plan §4, "
                       "Qualification A; it replaces the "
                       "process-tree-in-the-case "
                       "expectation — the case still "
                       "carries the tree, unexamined "
                       "here, the commission unchanged)",
                       sealed.get("journal_baseline")
                       == {"address": JOURNAL_PATH,
                           "initial_sha256":
                               hashlib.sha256(
                                   b"").hexdigest()},
                       json.dumps(
                           sealed.get(
                               "journal_baseline"))[:300])
                expect("generation: the sealed record "
                       "carries the delivery declaration, "
                       "bound to the case's own word (the "
                       "door scope — the contribution is "
                       "the deliverable's arrival, the "
                       "office files it)",
                       sealed.get("delivery") == DELIVERY
                       and (case_content or {}).get(
                           "delivery") == DELIVERY,
                       json.dumps(
                           sealed.get("delivery"))[:300])
                expect("generation: the sealed record "
                       "carries the delivery-evidence "
                       "declaration, bound to the case's "
                       "own word (round ten, INDEX 552 — "
                       "the three sources are the evidence "
                       "this job's delivery must rest on)",
                       sealed.get("delivery_evidence")
                       == DELIVERY_EVIDENCE
                       and (case_content or {}).get(
                           "delivery_evidence")
                       == DELIVERY_EVIDENCE,
                       json.dumps(
                           sealed.get(
                               "delivery_evidence"))[:300])
                expect("generation: the sealed record "
                       "carries the delivery-length "
                       "declaration, bound to the case's "
                       "own word (the third gate, INDEX "
                       "557 — the brief must arrive with "
                       "at least the declared floor of "
                       "words before the door files it)",
                       sealed.get("delivery_floor")
                       == DELIVERY_FLOOR
                       and (case_content or {}).get(
                           "delivery_floor")
                       == DELIVERY_FLOOR,
                       json.dumps(
                           sealed.get(
                               "delivery_floor"))[:300])
                expect("commission: the issued case "
                       "carries the role-memory snapshot "
                       "as its own component, unchanged "
                       "(the door scope's carriage)",
                       (case_content or {}).get(
                           "role_memory") == ROLE_MEMORY,
                       json.dumps(
                           (case_content or {}).get(
                               "role_memory"))[:300])
                expect("commission: the issued case "
                       "carries the onboarding as its own "
                       "component, unchanged (the run-6 "
                       "package — his first prompt is his "
                       "onboarding file)",
                       (case_content or {}).get("onboarding")
                       == ONBOARDING,
                       json.dumps(
                           (case_content or {}).get(
                               "onboarding"))[:300])

                # (7) The judgement payload the order
                # will bind: computed, not recorded —
                # under office-cycle-v8 the order binds
                # the generated record's hash directly
                # (no probed act stands in the launch
                # to carry it), and the verification
                # exercised above is this check's own
                # witness, not a live step.
                order = _order_record(
                    assembly_id,
                    generated["instance_id"], None, None,
                    None, verify_only=True)
                order_hash = _sha256_bytes(
                    canonical(order))
                expect("order record: canonical hash is "
                       "a 64-hex SHA-256",
                       len(order_hash) == 64 and all(
                           c in "0123456789abcdef"
                           for c in order_hash))
                payload = gen.judgement(
                    assembly_id, adapter_mode=ADAPTER_MODE,
                    mode_grounds=OFFICE_MODE_GROUNDS,
                    decision_receipt_hash=order_hash,
                    decision_examiner=ORDER_EXAMINER)
                expect("judgement: payload binds the "
                       "generated record — its assembly, "
                       "its instance and the record's "
                       "canonical hash — and the office-"
                       "declared mode (office-cycle-v8: "
                       "no probe governs this assembly, "
                       "so the mode the judgement binds "
                       "is the office's declaration from "
                       "the sealed configuration's "
                       "standing judgement — adapter_mode "
                       "as configured, the declared "
                       "grounds, the office-declared "
                       "source marker, and the order "
                       "receipt binding; no probe fields "
                       "stand in it)",
                       payload.get("assembly_id")
                       == assembly_id
                       and payload.get("instance_id")
                       == generated["instance_id"]
                       and payload.get("record_hash")
                       == assembly_record_hash(sealed)
                       and payload.get("adapter_mode")
                       == ADAPTER_MODE
                       and payload.get("mode_grounds")
                       == OFFICE_MODE_GROUNDS
                       and (payload.get("mode_source")
                            or "").startswith(
                                "office-declared")
                       and payload.get(
                           "decision_receipt_hash")
                       == order_hash
                       and "probe_seq" not in payload,
                       json.dumps(payload)[:300])

            # (8) The v4 ceiling: a well-formed cmd
            # passes; a string cmd is refused — and the
            # adapter's native definition for the
            # catalogue entry carries the typed schema
            # the final adapter state derives (cmd
            # declared, required) rather than the empty
            # object the Gate 5 qualification named.
            ok, _ground = tool_policy.check_ceiling(
                "container.exec", {},
                {"cmd": ["/bin/true"]},
                version=tool_policy.EXEC_REGISTRY_VERSION)
            expect("ceiling: well-formed cmd passes "
                   "under registry v4", ok is True)
            ok2, _g2 = tool_policy.check_ceiling(
                "container.exec", {},
                {"cmd": "/bin/true"},
                version=tool_policy.EXEC_REGISTRY_VERSION)
            expect("ceiling: string cmd refused under "
                   "registry v4", ok2 is False)
            facing = tool_policy.worker_facing(
                "container.exec",
                version=tool_policy.EXEC_REGISTRY_VERSION)
            definitions = OpenAICompatibleAdapter \
                ._native_tool_definitions({"tools": [
                    {"tool": "container.exec",
                     **(facing or {})}]})
            params = (definitions[0].get("function", {})
                      .get("parameters") or {}) \
                if definitions else {}
            expect("adapter: native definition for "
                   "container.exec declares cmd "
                   "(required) — not the empty schema",
                   len(definitions) == 1
                   and "cmd" in (params.get("properties")
                                 or {})
                   and params.get("required") == ["cmd"],
                   json.dumps(definitions)[:300])

            # (8b) The route's name translation (Ben's
            # ruling, 2026-11-24): on this route the
            # transmitted definition carries the wire
            # name — exactly container-exec — because the
            # route's provider refuses dotted function
            # names (the first run's recorded 400 bodies).
            # The canonical derivation above stands
            # untouched beside it: the framework's name
            # for the tool does not change.
            wire_translator = nemotron_names \
                .translator_for_package(
                    ROUTE, {"tools": [
                        {"tool": "container.exec",
                         **(facing or {})}]})
            wire_definitions = OpenAICompatibleAdapter \
                ._native_tool_definitions(
                    {"tools": [
                        {"tool": "container.exec",
                         **(facing or {})}]},
                    translator=wire_translator)
            wire_fn = (wire_definitions[0].get(
                "function", {}) if wire_definitions
                else {})
            if QUINN or GLM or GPTOSS:
                # Quinn's, the GLM occupant's and the
                # GPT-OSS occupant's routes carry no
                # name translation (the translator
                # exists for the NVIDIA route alone): no
                # translator stands, and the transmitted
                # definition carries the canonical
                # dotted name exactly as the framework
                # speaks it.
                _route_display = ("Groq" if (QUINN or
                                             GPTOSS) else
                                  "Cloudflare")
                expect(f"adapter: on the {_route_display} "
                       "route no "
                       "name translation stands — the "
                       "transmitted definition's tool name "
                       "is the canonical container.exec",
                       wire_translator is None
                       and len(wire_definitions) == 1
                       and wire_fn.get("name")
                       == "container.exec"
                       and wire_fn.get("description")
                       == facing["description"]
                       and wire_fn.get("parameters")
                       == params,
                       json.dumps(wire_definitions)[:300])
            else:
                expect("adapter: on the NVIDIA route the "
                       "transmitted definition's tool name is "
                       "exactly container-exec",
                       len(wire_definitions) == 1
                       and wire_fn.get("name")
                       == "container-exec"
                       and wire_fn.get("description")
                       == facing["description"]
                       and wire_fn.get("parameters")
                       == params,
                       json.dumps(wire_definitions)[:300])

            # (6b) Sandbox staging: the pull door's
            # sources stage from the verified set and
            # hash to the paper §1.1 table; the scratch
            # home stands.
            staging_problem = _stage_sandbox_sources(
                tmp / "sandbox", manifest)
            staged_ok = staging_problem is None and all(
                _sha256_bytes(
                    (tmp / "sandbox" / rel).read_bytes())
                == want
                for rel, want in
                PAPER_SOURCE_HASHES.items())
            expect("staging: sandbox sources staged and "
                   "hash-verified against the manifest; "
                   "scratch home stands",
                   staging_problem is None and staged_ok
                   and (tmp / "sandbox" / "scratch")
                   .is_dir(),
                   str(staging_problem))

            # (8c) The combined catalogue on the NVIDIA
            # route (INDEX 476): the catalogue derived
            # per grant from the combined grants, carried
            # through the route's translator, transmits
            # exactly the dashed name set — each offered
            # tool once — with the underscore in
            # read_range preserved (sandbox-read_range,
            # never sandbox-read-range, which the
            # translator does not recognise at all).
            from framework.loop import _derive_catalogue
            combined_catalogue = _derive_catalogue(
                GRANTS_COMBINED,
                tool_policy.EXEC_REGISTRY_VERSION,
                per_grant=True)
            combined_translator = nemotron_names \
                .translator_for_package(
                    ROUTE, {"tools": combined_catalogue})
            combined_definitions = \
                OpenAICompatibleAdapter \
                ._native_tool_definitions(
                    {"tools": combined_catalogue},
                    translator=combined_translator)
            combined_names = [
                d.get("function", {}).get("name")
                for d in combined_definitions]
            if QUINN or GLM or GPTOSS:
                expect("adapter: the combined catalogue's "
                       "transmitted names on the "
                       f"{_route_display} "
                       "route are exactly the canonical "
                       "dotted set",
                       combined_translator is None
                       and sorted(combined_names)
                       == sorted([
                           "container.exec", "sandbox.list",
                           "sandbox.search",
                           "sandbox.read_range",
                           "sandbox.read", "sandbox.write"])
                       and len(combined_names)
                       == len(set(combined_names)),
                       json.dumps(combined_names)[:300])
                expect("translator: no translator stands "
                       f"on the {_route_display} route — "
                       "sandbox.read_range travels as "
                       "itself, the canonical name",
                       combined_translator is None
                       and "sandbox.read_range"
                       in combined_names)
            else:
                expect("adapter: the combined catalogue's "
                       "transmitted names on the NVIDIA "
                       "route are exactly the dashed set",
                       sorted(combined_names) == sorted([
                           "container-exec", "sandbox-list",
                           "sandbox-search", "sandbox-read_range",
                           "sandbox-read", "sandbox-write"])
                       and len(combined_names)
                       == len(set(combined_names)),
                       json.dumps(combined_names)[:300])
                expect("translator: sandbox.read_range "
                       "travels as sandbox-read_range "
                       "(underscore preserved) and "
                       "sandbox-read-range is not a wire "
                       "name",
                       combined_translator is not None
                       and combined_translator.to_wire(
                           "sandbox.read_range")
                       == "sandbox-read_range"
                       and combined_translator.to_canonical(
                           "sandbox-read-range") is None)

            # (9) Nothing activated, nothing probed:
            # verify mode records no live step.
            types = [e["type"] for e in
                     store.all_events()]
            expect("boundary: no INSTANCE_ACTIVATED and "
                   "no ASSEMBLY_PROBED stand in the "
                   "throwaway record",
                   "INSTANCE_ACTIVATED" not in types
                   and "ASSEMBLY_PROBED" not in types)
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        shutil.rmtree(tmp, ignore_errors=True)
    if problems:
        print(f"VERIFY-CONFIG: FAIL ({len(problems)} "
              f"problem(s): {'; '.join(problems)})")
        return 1
    print("VERIFY-CONFIG: PASS")
    return 0


def main(argv):
    if "--verify-config" in argv:
        return verify_config()
    return run_demo()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

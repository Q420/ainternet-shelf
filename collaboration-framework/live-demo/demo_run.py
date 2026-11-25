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
    CONSTITUTION_HASH, FrameworkStore)

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
# by the director's direction — the Groq route's
# native path carries the open BD-1 defect (INDEX
# 411-420) and this run does not route through it.
# The Cloudflare occupant text by the director's
# direction (INDEX 563): a new route whose native
# tool-calling has never been witnessed on the live
# path, and no finding about its native reach is made.
# The GPT-OSS occupant text under the examiner's
# standing judgement for this model on this route
# (INDEX 300, on probe evidence: four settled
# text-contract observations, no empirical basis for
# native on it).
ADAPTER_MODE = ("text" if (QUINN or GLM or GPTOSS)
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
    "work. Its contents are not carried in your "
    "packages — pull it when you want it, and write "
    "to it with your tools.\n\n"
    "Write a plain-words brief, at most ~600 words, "
    "that a newcomer could read to learn what this "
    "framework is, what has actually been proven, "
    "what has not been proven, and what remains to "
    "be built.\n\n"
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
        "bound": {"count": 4},
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
    "retrieval 12 per tool and prefix, write 4): they do "
    "not bind the honest or the ranged path, so the "
    "re-derivation leaves them.")


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

# The director's order, verbatim as given, and the
# judgement the order makes.
ORDER_WORDS = (
    "Let's try Quinn... we should be able to just "
    "drop her right in" if QUINN else
    "Build the GPT-OSS seat on the Groq route and "
    "run it" if GPTOSS else
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
    "Director's direction (Ben, 2026-11-25 — his tap "
    "on the scope card and his own words: \"Build the "
    "GPT-OSS seat on the Groq route and run it\"): "
    "the GPT-OSS occupant dropped into the same role, "
    "the same case and the same gates. The mode is "
    "judged text under the examiner's standing "
    "judgement for this model on this route (INDEX "
    "300, on probe evidence: four settled "
    "text-contract observations, no empirical basis "
    "for native) — the occupant answers in the "
    "package protocol as plain-text JSON, the loop's "
    "standing text population. The precedent stands "
    "at INDEX 234: attempt 6 ran this exact pin on "
    "this exact route, its provider-reported identity "
    "verified against the pin; that run's failure was "
    "the old harness's 134,844-byte push package "
    "(HTTP 413), a shape the current driver no longer "
    "produces. The probe stage ran live and its "
    "recommendation stands in the record as evidence; "
    "it does not decide this run's mode. The run is "
    "the empirical test of this model's "
    "full-working-set wake against this account's "
    "actual per-model limits, which have never been "
    "read." if GPTOSS else
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
ORDER_EFFECT = (
    "the director's direction adopts the "
    "examiner's standing judgement for this "
    "model on this route (INDEX 300): the "
    "mode is judged text, whatever the probe "
    "stage recommends; the probe's "
    "recommendation stands in the record as "
    "evidence, not as the decision; the "
    "model's first live response is the "
    "delivery evidence" if GPTOSS else
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
                              opening=opening)
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
        "mode_grounds": ORDER_GROUNDS,
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

        # THE WORKED EXAMPLE (round nine, INDEX 548):
        # the office performs the demonstration call on
        # the glossary's first file against the staged
        # sandbox, through the same governed performer a
        # dispatch runs, BEFORE generation — the call's
        # real result is what generation seals beside
        # the presentation contract, and the files stage
        # shows it at the worker's third wake. Where the
        # call cannot be made, no example stands and
        # generation proceeds without one.
        worked_example = None
        example_executor = Executor(
            doorway, str(run_dir / "sandbox"),
            claim_dir=str(run_dir / "claims"),
            deadline=150.0)
        try:
            example_result = \
                example_executor.worked_example_list(
                    GLOSSARY[0]["address"])
            worked_example = {
                "tool": "sandbox.list",
                "path": GLOSSARY[0]["address"],
                "result": example_result}
            print("worked example: the office's "
                  "sandbox.list call on "
                  f"{GLOSSARY[0]['address']} stands "
                  "performed against the staged sandbox; "
                  "its result is sealed with the "
                  "assembly")
        except Exception as exc:  # noqa: BLE001 — the
            # call cannot be made: no example stands.
            print("worked example: the demonstration "
                  "call could not be made "
                  f"({type(exc).__name__}: {exc}); no "
                  "example stands in the seal")

        # ASSEMBLE — the adapter on the NVIDIA route's
        # real seam: the typed transport through the
        # capture pass-through to the registered
        # connector helper. Generation under the probe
        # contract and the exec catalogue contract,
        # grants the combined surface (INDEX 476): the
        # execution tool, the retrieval four under
        # sources/ and under scratch/, and sandbox.write
        # under scratch/. The identify callable is
        # pin-wrapped: a provider-reported identity that
        # is not the pin aborts here, before activation,
        # as a flagged conflict.
        adapter = OpenAICompatibleAdapter(
            endpoint=ENDPOINT, model=MODEL,
            timeout=ADAPTER_TIMEOUT, route=ROUTE)
        _install_typed_transport(adapter, wrapper_path)
        gen.propose(
            tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a model able to read three "
                              "source documents in its room "
                              "and write a short, accurate, "
                              "plain-words brief")
        identify_callable = make_pinned_identify(
            adapter, MODEL)
        try:
            generated = gen.generate(
                tok["orch-1"], "crew-1", identify_callable,
                skills=[], grants=GRANTS_COMBINED,
                model_requested=MODEL, probe=True,
                exec_room=True, freshness_suspended=True,
                delivery_declaration=True,
                delivery_evidence_declaration=True,
                delivery_floor_declaration=True,
                presentation_declaration=tool_policy.PRESENTATION_CONTRACT_V2,
                worked_example=worked_example)
        except ModelPinMismatchError as mismatch:
            # The flagged conflict (paper §3.6 gate 5's
            # rule, carried to this run's pin): the route
            # reports a model that is not the pin. No
            # substitution, no activation, no worker call.
            print(f"ABORT: FLAGGED CONFLICT — provider-"
                  f"reported model id "
                  f"{mismatch.provider_model_id!r} does "
                  f"not match the pinned model "
                  f"{mismatch.pinned_model!r}; the run "
                  f"stops before activation",
                  file=sys.stderr)
            return abort_report({
                "abort_stage": "pre-activation identity "
                               "pin",
                "flagged_conflict": True,
                "abort_reason": str(mismatch),
                "provider_model_id":
                    mismatch.provider_model_id,
                "pinned_model": mismatch.pinned_model})
        except AdapterFailure as failure:
            print(f"ABORT: the identity call failed "
                  f"({failure.kind}: {failure.detail}); "
                  f"the run's calls travel the registered "
                  f"connector credential route — check "
                  f"the connector helper and its "
                  f"credential", file=sys.stderr)
            return abort_report({
                "abort_stage": "identity call",
                "flagged_conflict": False,
                "abort_reason": f"{failure.kind}: "
                                f"{failure.detail}"})
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
              f"{instance_id}); identity pin verified "
              f"against the provider-reported model id")

        # PROBE — five live trials through the real
        # NVIDIA raw-call seam over the capture
        # pass-through. The stage's evidence stands in
        # the record; its recommendation does not judge
        # this run (the order does).
        raw_call = _install_raw_call(adapter, wrapper_path)
        probe_result = gen.probe(
            tok["orch-1"], assembly_id, raw_call,
            route=ROUTE, model=MODEL)
        print(f"probe: settled "
              f"{probe_result['settled_count']}/5, "
              f"recommended "
              f"{probe_result['recommended_mode']!r} "
              f"(evidence for the record; the mode is "
              f"judged by the director's order)")
        gen.verify(tok["orch-1"], assembly_id)

        # JUDGE (hop 1) — the director's order record,
        # retained before the judgement is recorded; the
        # judgement binds its canonical hash.
        probed_payload = None
        for ev in store.all_events():
            if ev["type"] == "ASSEMBLY_PROBED" and \
                    ev["payload"].get(
                        "assembly_id") == assembly_id:
                probed_payload = ev["payload"]
        order = _order_record(
            assembly_id, instance_id,
            probed_payload["generated_record_hash"],
            probed_payload, probe_result)
        order_path = demo_dir / "order-record.json"
        with open(order_path, "w",
                  encoding="utf-8") as fh:
            json.dump(order, fh, indent=1)
            fh.write("\n")
        order_hash = _sha256_bytes(canonical(order))
        judgement = gen.judgement(
            assembly_id, adapter_mode=ADAPTER_MODE,
            mode_grounds=ORDER_GROUNDS,
            decision_receipt_hash=order_hash,
            decision_examiner=ORDER_EXAMINER)
        _act(doorway, tok["exam-1"], "ASSEMBLY_JUDGED",
             judgement)
        packed = gen.pack(tok["orch-1"], assembly_id)
        gen.authorise(tok["orch-1"], assembly_id)
        print(f"judgement: {ADAPTER_MODE}, by the "
              f"director's order (order record sha256: "
              f"{order_hash})")

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
        result = Loop(doorway, packed["instance_token"],
                      paced, executor=executor,
                      evidence_store=str(run_dir)).run()

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
                "note": "the pin was enforced inside "
                        "generation, before activation "
                        "(make_pinned_identify); the "
                        "provider-reported id as recorded "
                        "at onboarding stands here — it "
                        "is the route's report, not "
                        "independent proof of the model "
                        "the provider actually served",
            },
            "probe": {
                "settled_count":
                    probe_result["settled_count"],
                "recommended_mode":
                    probe_result["recommended_mode"],
                "counts": probe_result["counts"],
                "evidence_hash":
                    probe_result["evidence_hash"],
                "note": "the probe's recommendation is "
                        "evidence in the record; this "
                        "run's mode was judged by the "
                        "director's order, not by it",
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
          "(no provider contact; the probe stage, the "
          "recorded judgement and activation are live "
          "steps and are NOT run here)")
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
                   "installed for the probe stage"
                   if (QUINN or GPTOSS) else
                   "transport: real Cloudflare raw call "
                   "installed for the probe stage"
                   if GLM else
                   "transport: real NVIDIA raw call "
                   "installed for the probe stage",
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
            # 548): this path's own staging stands at
            # (6b), after generation, so the
            # demonstration call is performed here on a
            # throwaway staging of the same verified
            # set, through the governed performer, and
            # passed to the generation below — the seal
            # this path verifies carries the real call's
            # result on the glossary's first file.
            example_problem = _stage_sandbox_sources(
                tmp / "sandbox-example", manifest)
            verify_example = None
            if example_problem is None:
                try:
                    verify_example = {
                        "tool": "sandbox.list",
                        "path": GLOSSARY[0]["address"],
                        "result": Executor(
                            doorway,
                            str(tmp / "sandbox-example"),
                            claim_dir=str(
                                tmp / "claims-example"),
                            deadline=150.0
                        ).worked_example_list(
                            GLOSSARY[0]["address"])}
                except Exception:  # noqa: BLE001 — the
                    # call cannot be made: no example.
                    verify_example = None

            # (6) Generation under a stub identity: the
            # sealed record declares the exec catalogue
            # contract and the probe contract, and holds
            # exactly the combined grant set (INDEX 476).
            gen.propose(
                tok["orch-1"], "crew-1", part="part-A",
                role_requirements="verify-config stub")
            generated = gen.generate(
                tok["orch-1"], "crew-1",
                {"declaration":
                     "verify-config stub identity "
                     "(offline; no provider contact)",
                 "provider_model_id": MODEL},
                skills=[], grants=GRANTS_COMBINED,
                model_requested=MODEL, probe=True,
                exec_room=True, freshness_suspended=True,
                delivery_declaration=True,
                delivery_evidence_declaration=True,
                delivery_floor_declaration=True,
                presentation_declaration=tool_policy.PRESENTATION_CONTRACT_V2,
                worked_example=verify_example)
            expect("generation: stub-identity generation "
                   "succeeds",
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
                       "declares the pointer-rule "
                       "presentation contract (Ben's "
                       "direction, INDEX 544 as corrected "
                       "by INDEX 568 — the worker-first "
                       "package whose gathered content is "
                       "presented once and stands as "
                       "pointers after)",
                       sealed.get("presentation_contract")
                       == tool_policy.PRESENTATION_CONTRACT_V2,
                       f"got "
                       f"{sealed.get('presentation_contract')}")
                expect("generation: the sealed record "
                       "carries the worked example — the "
                       "office's sandbox.list call on the "
                       "glossary's first file, its result "
                       "the governed performer's own over "
                       "the staged bytes (round nine, "
                       "INDEX 548)",
                       verify_example is not None
                       and sealed.get("worked_example")
                       == verify_example,
                       f"got "
                       f"{sealed.get('worked_example')}")
                expect("generation: the worked example's "
                       "result is the staged file's real "
                       "listing — its size is the staged "
                       "bytes' length",
                       verify_example is not None
                       and verify_example["result"].get(
                           "size_bytes")
                       == len((tmp / "sandbox-example"
                               / GLOSSARY[0]["address"])
                              .read_bytes()),
                       "size against the staged file")
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
                # recording stands behind the live probe
                # in the lifecycle's normative order.
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
                    mode_grounds=ORDER_GROUNDS,
                    decision_receipt_hash=order_hash,
                    decision_examiner=ORDER_EXAMINER)
                expect("judgement: payload carries the "
                       f"{ADAPTER_MODE} mode, the order's "
                       "grounds and the order-record hash",
                       payload.get("adapter_mode")
                       == ADAPTER_MODE
                       and payload.get("mode_grounds")
                       == ORDER_GROUNDS
                       and payload.get(
                           "decision_receipt_hash")
                       == order_hash
                       and payload.get(
                           "decision_examiner")
                       == ORDER_EXAMINER,
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

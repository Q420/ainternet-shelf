#!/usr/bin/env python3
"""Terminal readout for framework runs — Ben's requirement (INDEX 437).

Renders a run's tool calls as a live-style terminal readout and saves it
as a Markdown file for after-run analysis. The readout is a VIEW of the
run record's own events (the same events the checker reconstructs); it is
presentation, not evidence, and never an authority path: it observes and
presents only.

Modes:
  render <run-dir|run-export.json> [-o OUT.md]
      Render a completed run's export. Default OUT: alongside the export
      as terminal-readout.md (pass -o to keep run dirs untouched).
  watch <events.jsonl> [-o OUT.md] [--idle-seconds N]
      Follow a JSONL event stream (one event object per line), printing
      each tool-relevant line as it arrives and appending it to OUT.md,
      flushed per line. Finalises — closes the Markdown fence, writes the
      analysis summary, records the ending — when the run's termination
      event arrives, when the stream stays at end-of-file for
      --idle-seconds (default 30), or on interruption. A malformed line
      is surfaced as a visible readout problem, never silently skipped.

Faithfulness rules (Vane, INDEX 440): a call appears when observed, with
requested / refused / dispatched / completed / failed as distinct
states; a stalled or interrupted run leaves a readable ending; the
summary states recorded facts only; live and saved views derive from the
same event sequence. Provider call IDs are retained in full — they are
identifiers, not decoration. Argument summaries are bounded and redact
values under secret-shaped keys.
"""
import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

MAX_FIELD = 160
SECRET_KEY = re.compile(r"(token|password|secret|api[_-]?key|credential)", re.I)

# Event types that make up the tool-call story of a run.
STORY = {
    "LOOP_ITERATION", "CALL_ENTERED", "RESPONSE_EVIDENCE",
    "TRANSLATION_RECORDED", "TOOL_REQUESTED", "TOOL_DISPATCHED",
    "TOOL_STARTED", "TOOL_OUTCOME", "LOOP_STALLED", "LOOP_COMPLETED",
    "LOOP_YIELDED",
}
TERMINATIONS = {"LOOP_STALLED", "LOOP_COMPLETED", "LOOP_YIELDED"}


def short(value):
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= MAX_FIELD else text[: MAX_FIELD - 1] + "…"


def summarize_params(params):
    """Bounded, redacted one-line summary of requested parameters."""
    if not isinstance(params, dict):
        return short(params)
    parts = []
    for key in sorted(params):
        if SECRET_KEY.search(str(key)):
            parts.append(f"{key}=[redacted]")
        else:
            parts.append(f"{key}={short(params[key])[:60]}")
    return "{" + ", ".join(parts) + "}"


def payload_of(event):
    payload = event.get("payload", {})
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {"_raw": payload}
    return payload if isinstance(payload, dict) else {}


def call_lines(event_type, p):
    """One event -> readout lines, plus stat contributions."""
    lines, stats = [], Counter()
    if event_type == "LOOP_ITERATION":
        lines.append(f"— iteration {p.get('iteration')} "
                     f"(step ceiling {p.get('step_ceiling')}, "
                     f"deadline {p.get('deadline_seconds')}s)")
    elif event_type == "CALL_ENTERED":
        lines.append(f"→ call entered · iteration {p.get('iteration')}")
    elif event_type == "RESPONSE_EVIDENCE":
        lines.append(f"← response evidence · {short(p.get('outcome', 'captured'))}"
                     f" · artifact {short(p.get('artifact_sha256', ''))[:16]}")
    elif event_type == "TRANSLATION_RECORDED":
        for call in p.get("calls", []):
            name = call.get("tool") or call.get("name") or call.get("tool_name", "?")
            cid = call.get("provider_call_id", "")
            verdict = call.get("resolution") or call.get("validation") or ""
            refusal = call.get("refusal_class") or ""
            args_hash = call.get("arguments_sha256", "")
            line = f"⚒ CALL {name} · id {cid} · {short(verdict)} · args#{short(args_hash)[:12]}"
            if refusal:
                line += f" · REFUSED {short(refusal)}"
                stats["refused"] += 1
            lines.append(line)
            stats[f"call:{name}"] += 1
    elif event_type == "TOOL_REQUESTED":
        name = p.get("tool") or p.get("name") or p.get("tool_name", "?")
        params = summarize_params(p.get("parameters", ""))
        lines.append(f"  requested · {name} · {short(p.get('request_id', ''))} · {params}")
    elif event_type == "TOOL_DISPATCHED":
        name = p.get("tool") or p.get("name") or p.get("tool_name", "?")
        lines.append(f"  dispatched · {name} · {short(p.get('dispatch_id', ''))}")
        stats["dispatched"] += 1
    elif event_type == "TOOL_STARTED":
        lines.append("  started")
    elif event_type == "TOOL_OUTCOME":
        outcome = p.get("outcome", p.get("status", ""))
        result = p.get("result", p.get("summary", ""))
        lines.append(f"  ✓ outcome · {short(outcome)} · {short(result)}")
        stats[f"outcome:{short(outcome)}"] += 1
    elif event_type in TERMINATIONS:
        reason = p.get("ground") or p.get("reason") or p.get("termination", "")
        detail = p.get("detail", "")
        lines.append(f"■ {event_type[5:].lower()} · {short(reason)} · {short(detail)}")
        stats[event_type.lower()] += 1
    return lines, stats


def render_events(events):
    lines, stats = [], Counter()
    for event in events:
        etype = event.get("type", "")
        if etype not in STORY:
            continue
        new_lines, new_stats = call_lines(etype, payload_of(event))
        lines.extend(new_lines)
        stats.update(new_stats)
    return lines, stats


def summary_block(stats):
    out = ["", "## Analysis summary", ""]
    if stats:
        for key in sorted(stats):
            out.append(f"- {key}: {stats[key]}")
    else:
        out.append("- no tool calls recorded")
    out.append("")
    return out


def to_markdown(source, lines, stats):
    out = [f"# Terminal readout — {source}", "", "```text"]
    out.extend(lines if lines else ["(no tool-call events in this record)"])
    out.append("```")
    out.extend(summary_block(stats))
    return "\n".join(out)


def load_export(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):
        return data.get("events", [])
    return data


def cmd_render(args):
    src = Path(args.source)
    export = src / "run-export.json" if src.is_dir() else src
    events = load_export(export)
    lines, stats = render_events(events)
    for line in lines:
        print(line)
    out_path = Path(args.output) if args.output else export.parent / "terminal-readout.md"
    out_path.write_text(to_markdown(str(export), lines, stats))
    print(f"\n[saved] {out_path}", file=sys.stderr)
    return 0


def cmd_watch(args):
    src = Path(args.source)
    out_path = Path(args.output) if args.output else src.with_suffix(".readout.md")
    stats = Counter()
    ending = None

    def finalise(md, ending_line):
        md.write(ending_line + "\n```\n")
        md.write("\n".join(summary_block(stats)))
        md.flush()
        print(ending_line, flush=True)

    with out_path.open("a") as md:
        md.write(f"\n# Terminal readout (live) — {src}\n\n```text\n")
        md.flush()
        try:
            with src.open() as stream:
                idle = 0.0
                line_no = 0
                while ending is None:
                    raw = stream.readline()
                    if not raw:
                        if idle >= args.idle_seconds:
                            ending = ("■ end of stream · no termination event "
                                      "in the record")
                            finalise(md, ending)
                            break
                        time.sleep(0.25)
                        idle += 0.25
                        continue
                    idle = 0.0
                    line_no += 1
                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        problem = (f"⚠ readout problem · malformed line "
                                   f"{line_no} skipped — the stream is damaged; "
                                   f"the record, not this readout, is authoritative")
                        print(problem, flush=True)
                        md.write(problem + "\n")
                        md.flush()
                        stats["readout_problem:malformed_line"] += 1
                        continue
                    etype = event.get("type", "")
                    if etype not in STORY:
                        continue
                    new_lines, new_stats = call_lines(etype, payload_of(event))
                    stats.update(new_stats)
                    for text in new_lines:
                        print(text, flush=True)
                        md.write(text + "\n")
                    md.flush()
                    if etype in TERMINATIONS:
                        ending = "■ end of stream · run terminated in the record"
                        finalise(md, ending)
        except KeyboardInterrupt:
            finalise(md, "■ end of stream · readout interrupted — the run's "
                         "record continues without this view")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("render", "watch"):
        p = sub.add_parser(name)
        p.add_argument("source")
        p.add_argument("-o", "--output")
        if name == "watch":
            p.add_argument("--idle-seconds", type=float, default=30.0)
    args = parser.parse_args()
    return cmd_render(args) if args.mode == "render" else cmd_watch(args)


if __name__ == "__main__":
    sys.exit(main())

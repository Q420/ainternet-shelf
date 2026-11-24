#!/usr/bin/env python3
"""Terminal readout for framework runs — Ben's requirement (INDEX 437).

Renders a run's tool calls as a live-style terminal readout and saves it
as a Markdown file for after-run analysis. The readout is a VIEW of the
run record's own events (the same events the checker reconstructs); it is
presentation, not evidence.

Modes:
  render <run-dir|run-export.json> [-o OUT.md]
      Render a completed run's export. Default OUT: alongside the export
      as terminal-readout.md (pass -o to keep run dirs untouched).
  watch <events.jsonl> [-o OUT.md]
      Follow a JSONL event stream (one event object per line), printing
      each tool-relevant line as it arrives and appending it to OUT.md,
      flushed per line, so the readout exists during and after the run.

Event payloads may be dicts or JSON strings. Summaries are bounded: no
line carries more than a short excerpt of any argument or result.
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

MAX_FIELD = 160

# Event types that make up the tool-call story of a run.
STORY = {
    "LOOP_ITERATION", "CALL_ENTERED", "RESPONSE_EVIDENCE",
    "TRANSLATION_RECORDED", "TOOL_REQUESTED", "TOOL_DISPATCHED",
    "TOOL_STARTED", "TOOL_OUTCOME", "LOOP_STALLED", "LOOP_COMPLETED",
    "LOOP_YIELDED",
}


def short(value):
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= MAX_FIELD else text[: MAX_FIELD - 1] + "…"


def payload_of(event):
    payload = event.get("payload", {})
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {"_raw": payload}
    return payload if isinstance(payload, dict) else {}


def call_lines(event_type, p):
    """One event -> zero or more readout lines, plus stat contributions."""
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
            args_hash = call.get("arguments_sha256", "")
            lines.append(f"⚒ CALL {name} · id {short(cid)[:24]} · {short(verdict)}"
                         f" · args#{short(args_hash)[:12]}")
            stats[f"call:{name}"] += 1
    elif event_type == "TOOL_REQUESTED":
        name = p.get("tool") or p.get("name") or p.get("tool_name", "?")
        lines.append(f"  requested · {name} · {short(p.get('request_id', ''))[:24]}")
    elif event_type == "TOOL_DISPATCHED":
        name = p.get("tool") or p.get("name") or p.get("tool_name", "?")
        lines.append(f"  dispatched · {name} · {short(p.get('dispatch_id', ''))[:24]}")
        stats["dispatched"] += 1
    elif event_type == "TOOL_STARTED":
        lines.append("  started")
    elif event_type == "TOOL_OUTCOME":
        outcome = p.get("outcome", p.get("status", ""))
        result = p.get("result", p.get("summary", ""))
        lines.append(f"  ✓ outcome · {short(outcome)} · {short(result)}")
        stats[f"outcome:{short(outcome)}"] += 1
    elif event_type in ("LOOP_STALLED", "LOOP_COMPLETED", "LOOP_YIELDED"):
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


def to_markdown(source, lines, stats):
    out = [f"# Terminal readout — {source}", ""]
    out.append("```text")
    out.extend(lines if lines else ["(no tool-call events in this record)"])
    out.append("```")
    out += ["", "## Analysis summary", ""]
    if stats:
        for key in sorted(stats):
            out.append(f"- {key}: {stats[key]}")
    else:
        out.append("- no tool calls recorded")
    out.append("")
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
    with out_path.open("a") as md:
        md.write(f"\n# Terminal readout (live) — {src}\n\n```text\n")
        md.flush()
        with src.open() as stream:
            while True:
                line = stream.readline()
                if not line:
                    time.sleep(0.25)
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
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
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("render", "watch"):
        p = sub.add_parser(name)
        p.add_argument("source")
        p.add_argument("-o", "--output")
    args = parser.parse_args()
    return cmd_render(args) if args.mode == "render" else cmd_watch(args)


if __name__ == "__main__":
    sys.exit(main())

"""Doorbell — Watched Orchestrator Stage 2 sensor (v1, DOM/text witness).

Watches every open ChatGPT conversation tab in the Remmy Chrome
profile. Per conversation it samples two markup-independent
witnesses every few seconds:

  * a tail-zone camera stamp (CDP screenshot cropped to the
    conversation tail, downscaled in memory; frames are never
    written anywhere — owner's camera rule), and
  * the rendered-text tail (innerText length + sha256 of the
    last 400 chars).

When the tail changes and then holds stable across two
consecutive samples, it appends one REPLY_SETTLED event to the
seat's pool file (events/alex.jsonl), continuing that file's
sequence and hash chain. Identity is a deterministic occurrence
tuple (conversation + emission ordinal + content sha256) minted
as a uuid5 — the platform offers no message id on this markup.

By the owner's tuning doctrine the knock layer OVER-FIRES: a
user-side send can also knock. The wake tells the orchestrator
"something landed"; she reads the page herself and judges.
False knocks cost one read; a missed reply costs the evening.

Capture health: writes spool/heartbeat.json every loop (schema:
pid, boot_id, instance_id, loop_count, last_tick — no state
field) and records a waker transition at boot: capture is now
provided by the doorbell. The sensor never sends anything to
any seat and never acknowledges an inbox item.

Context-full witness (owner's rollover fix, tapped 2026-11-16):
the tail text the sensor already reads on every poll is matched
against the context-window-full banner's wording (observed by
the owner on a genuinely full window, 2026-11-08). On the
banner's first appearance in a conversation it appends one
CONTEXT_FULL event — no new probe, no new sweep; the check
rides the read that already happens.
"""
import base64, hashlib, io, json, os, sys, time, uuid
sys.path.insert(0, "/home/hatch/workspace/remmy-browser")
import remmy_browser as rb
from PIL import Image

HERE = "/home/hatch/workspace/remmy-browser"
EVENTS = os.path.join(HERE, "events", "alex.jsonl")
HEARTBEAT = os.path.join(HERE, "spool", "heartbeat.json")
POLL_S = 4.0
STAMP_W, STAMP_H = 48, 27
BOOT = time.strftime("%Y-%m-%dT%H:%M:%S%z")
BOOT_ID = str(uuid.uuid4())
INSTANCE_ID = uuid.uuid4().hex[:32]
SESSION = "doorbell-" + BOOT

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")

def now_iso_z():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def log(obj):
    obj["wall"] = time.strftime("%H:%M:%S")
    print(json.dumps(obj), flush=True)

def atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def heartbeat(loop_count):
    atomic_write(HEARTBEAT, json.dumps({
        "pid": os.getpid(),
        "boot_id": BOOT_ID,
        "instance_id": INSTANCE_ID,
        "loop_count": loop_count,
        "last_tick": now_iso(),
    }, indent=1))

# --- pool file state: continue seq + chain, count emissions per conversation
def pool_state():
    last_seq, last_hash, counts = 0, "", {}
    if os.path.exists(EVENTS):
        with open(EVENTS, "rb") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    ev = json.loads(raw)
                except Exception:
                    continue
                if isinstance(ev.get("event_seq"), int):
                    last_seq = max(last_seq, ev["event_seq"])
                last_hash = hashlib.sha256(raw).hexdigest()
                cid = ev.get("conversation_id")
                if cid and ev.get("event_type") == "REPLY_SETTLED":
                    counts[cid] = counts.get(cid, 0) + 1
    return last_seq, last_hash, counts

SEQ, PREV_HASH, EMITTED = pool_state()

# --- context-full banner witness (owner's rule, 2026-11-16:
# a sentence that says "context" and "full" in it). Matched
# against the tail text already read on every poll — no new
# probe. A knock, not a verdict: the orchestrator confirms by
# reading the page before any rollover.
import re as _re
_SENTENCE_SPLIT = _re.compile(r"[.!?\n]+")
_CTX_WORD = _re.compile(r"\bcontext\b")
_FULL_WORD = _re.compile(r"\bfull\b")

def banner_present(text):
    if not text:
        return False
    low = text.lower()
    if "automatic summary of this conversation" in low:
        return True
    for sentence in _SENTENCE_SPLIT.split(low):
        if _CTX_WORD.search(sentence) and _FULL_WORD.search(sentence):
            return True
    return False

CF_EMITTED = {}

def append_context_full(conversation_id, tail):
    global SEQ, PREV_HASH
    content = (tail or "")[-400:]
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    ordinal = CF_EMITTED.get(conversation_id, 0) + 1
    CF_EMITTED[conversation_id] = ordinal
    message_id = str(uuid.uuid5(uuid.NAMESPACE_URL,
                                conversation_id + "|context-full|" + str(ordinal) + "|" + sha))
    SEQ += 1
    ev = {
        "schema_version": "0.1",
        "event_id": "evt-" + uuid.uuid4().hex,
        "event_seq": SEQ,
        "timestamp_utc": now_iso_z(),
        "session_id": SESSION,
        "conversation_id": conversation_id,
        "seat_id": "chatgpt",
        "direction": "inbound",
        "event_type": "CONTEXT_FULL",
        "lifecycle_state": "CONTEXT_FULL",
        "outcome": "success",
        "evidence_class": "BANNER_OBSERVED",
        "message_id": message_id,
        "exchange_id": "ex-" + uuid.uuid4().hex[:12],
        "content": content,
        "content_sha256": sha,
        "failure_code": None,
        "failure_detail": None,
        "attempted_transition": None,
        "source_reference": "doorbell tail-witness extraction; context-full banner match on rendered-text tail",
        "previous_event_hash": PREV_HASH,
    }
    line = json.dumps(ev)
    with open(EVENTS, "a") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    PREV_HASH = hashlib.sha256(line.encode("utf-8")).hexdigest()
    log({"doorbell": "context_full_event_appended", "seq": SEQ,
         "conversation": conversation_id[-12:], "message_id": message_id})
    return ev

def append_event(conversation_id, content, shape):
    global SEQ, PREV_HASH
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    ordinal = EMITTED.get(conversation_id, 0) + 1
    EMITTED[conversation_id] = ordinal
    message_id = str(uuid.uuid5(uuid.NAMESPACE_URL,
                                conversation_id + "|" + str(ordinal) + "|" + sha))
    SEQ += 1
    ev = {
        "schema_version": "0.1",
        "event_id": "evt-" + uuid.uuid4().hex,
        "event_seq": SEQ,
        "timestamp_utc": now_iso_z(),
        "session_id": SESSION,
        "conversation_id": conversation_id,
        "seat_id": "chatgpt",
        "direction": "inbound",
        "event_type": "REPLY_SETTLED",
        "lifecycle_state": "REPLY_SETTLED",
        "outcome": "success",
        "evidence_class": "SETTLEMENT_OBSERVED",
        "message_id": message_id,
        "exchange_id": "ex-" + uuid.uuid4().hex[:12],
        "content": content,
        "content_sha256": sha,
        "failure_code": None,
        "failure_detail": None,
        "attempted_transition": None,
        "source_reference": "doorbell tail-witness extraction; rendered-text tail (shape=%s)" % shape,
        "previous_event_hash": PREV_HASH,
    }
    line = json.dumps(ev)
    with open(EVENTS, "a") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    PREV_HASH = hashlib.sha256(line.encode("utf-8")).hexdigest()
    log({"doorbell": "event_appended", "seq": SEQ,
         "conversation": conversation_id[-12:], "message_id": message_id,
         "shape": shape, "content_len": len(content)})
    return ev

# --- per-conversation witnesses
def tail_stamp(cdp):
    shot = cdp.call("Page.captureScreenshot", {"format": "png"})
    raw = base64.b64decode(shot["data"])
    im = Image.open(io.BytesIO(raw)).convert("L")
    w, h = im.size
    crop = im.crop((int(w * 0.25), int(h * 0.50), w, h))
    return list(crop.resize((STAMP_W, STAMP_H)).getdata())

def stamp_diff(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)

TAIL_JS = r"""
(() => {
  const txt = document.body ? document.body.innerText : '';
  return JSON.stringify({ len: txt.length, tail: txt.slice(-400) });
})()
"""

class Convo:
    def __init__(self, cid):
        self.cid = cid
        self.baseline_tail = None      # last emitted / first-seen tail hash
        self.candidate_tail = None     # changed tail awaiting stability
        self.candidate_hits = 0
        self.candidate_shape = None    # 'grown' | 'instant'
        self.prev_tail = None
        self.prev_stamp = None
        self.seen = False
        self.banner = False           # context-full banner currently present

def main():
    # Record the capture handover in the waker state file.
    sys.path.insert(0, HERE)
    import waker_state
    waker_state.write_transition(
        "capture_started",
        "doorbell sensor (Watched Orchestrator Stage 2) is the capture provider",
        target="doorbell")
    log({"doorbell": "started", "pid": os.getpid(), "boot_id": BOOT_ID,
         "pool_seq_at_start": SEQ})
    convos = {}
    loops = 0
    last_heal = [0.0]
    while True:
        loops += 1
        try:
            heartbeat(loops)
            targets = [c for c in rb.page_targets()
                       if "chatgpt.com/c/" in (c.get("url") or "")]
            live = set()
            for tgt in targets:
                url = tgt.get("url")
                live.add(url)
                cv = convos.setdefault(url, Convo(url))
                try:
                    raw = rb.evaluate(tgt, TAIL_JS)
                    data = json.loads(raw) if isinstance(raw, str) else {}
                    tail = data.get("tail") or ""
                    tail_hash = hashlib.sha256(tail.encode("utf-8")).hexdigest()
                    cdp = rb.page_cdp(tgt)
                    st = tail_stamp(cdp)
                    sd = stamp_diff(cv.prev_stamp, st) if cv.prev_stamp else 0.0
                    cv.prev_stamp = st
                except Exception as e:  # noqa: BLE001
                    log({"doorbell": "witness_error", "conversation": url[-12:],
                         "error": str(e)[:120]})
                    continue
                bp = banner_present(tail)
                if bp and not cv.banner:
                    append_context_full(url, tail)
                cv.banner = bp
                if not cv.seen:
                    cv.seen = True
                    cv.baseline_tail = tail_hash
                    cv.prev_tail = tail_hash
                    log({"doorbell": "baseline", "conversation": url[-12:]})
                    continue
                if tail_hash != cv.prev_tail:
                    # A change. Grown = the tail also differed last poll
                    # (streaming); instant = appeared fully formed.
                    shape = "grown" if cv.candidate_tail is not None else "instant"
                    cv.candidate_tail = tail_hash
                    cv.candidate_hits = 0
                    cv.candidate_shape = shape
                    cv.candidate_text = tail
                    cv.prev_tail = tail_hash
                elif cv.candidate_tail is not None and tail_hash == cv.candidate_tail:
                    cv.candidate_hits += 1
                    if cv.candidate_hits >= 2 and tail_hash != cv.baseline_tail:
                        append_event(url, cv.candidate_text, cv.candidate_shape)
                        cv.baseline_tail = tail_hash
                        cv.candidate_tail = None
                        cv.candidate_hits = 0
                else:
                    cv.prev_tail = tail_hash
            for gone in [k for k in convos if k not in live]:
                del convos[gone]
        except Exception as e:  # noqa: BLE001
            log({"doorbell": "loop_error", "error": str(e)[:160]})
            # Self-heal the witness path (Ben's lesson, 2026-11-16:
            # a heartbeat proves the loop, not the seeing). When
            # the CDP endpoint stops answering — classically the
            # SSH tunnel died with a runtime restart — the loop
            # used to retry blind forever until a human noticed.
            # Now: ask the browser layer to rebuild the tunnel,
            # throttled to one attempt per 30 s, and log the
            # outcome either way. A failed heal never kills the
            # loop; the keeper restarts the process if it dies.
            now = time.time()
            if now - last_heal[0] >= 30:
                last_heal[0] = now
                try:
                    rb.ensure_tunnel()
                    log({"doorbell": "tunnel_heal", "result": "up"})
                except BaseException as he:  # noqa: BLE001
                    log({"doorbell": "tunnel_heal",
                         "result": "failed",
                         "error": str(he)[:120]})
        time.sleep(POLL_S)

if __name__ == "__main__":
    main()

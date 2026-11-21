"""Watched Orchestrator — Stage 1 measurement probe (camera numbers).

Polls CDP screenshots of a TEST conversation, downscales each frame in
memory to a tiny grayscale stamp, and logs only the frame-difference
NUMBERS. Frames are never written to disk (owner's camera rule:
delete as it happens). DOM text length is sampled alongside as the
ground-truth witness for when the reply actually lands and finishes.
"""
import base64, io, json, sys, time
sys.path.insert(0, "/home/hatch/workspace/remmy-browser")
import remmy_browser as rb
from PIL import Image

STAMP_W, STAMP_H = 48, 27
OUT = "/home/hatch/workspace/remmy-browser/probe-results-2026-11-15.jsonl"

targets = rb.page_targets()
_pool = [c for c in targets if (c.get("url") or "").rstrip("/") == "https://chatgpt.com"]
if not _pool:
    _pool = [c for c in targets if "6afa7f4b" in (c.get("url") or "")]
t = _pool[0]
cdp = rb.page_cdp(t)
print("TARGET:", t.get("url"))

def stamp():
    shot = cdp.call("Page.captureScreenshot", {"format": "png"})
    raw = base64.b64decode(shot["data"])
    im = Image.open(io.BytesIO(raw)).convert("L").resize((STAMP_W, STAMP_H))
    return list(im.getdata())

def diff(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)

def text_len():
    v = rb.evaluate(t, "document.body ? document.body.innerText.length : 0")
    return v if isinstance(v, int) else 0

def log(rec):
    rec["wall"] = time.strftime("%H:%M:%S")
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))

# --- test rig: the alphabet-test conversation (sends proven there 14/14).
# The fresh-chat home composer would not take a scripted insert tonight;
# a conversation page is the honest test surface anyway.
cdp.call("Page.navigate", {"url": "https://chatgpt.com/c/6afa8d98-7d48-83e8-9a96-261aa04178da"})
time.sleep(5)
print("url now:", rb.evaluate(t, "location.href"))
print("composer text len:", rb.evaluate(t, r"""
(() => { const ed = document.querySelector('div.ProseMirror[contenteditable="true"]');
  return ed ? (ed.innerText || '').length : -1; })()
"""))

FIND_ED = r"""
  const addBtn = [...document.querySelectorAll('button')].find(b => b.getAttribute('aria-label') === 'Add files and more');
  let ed = null;
  if (addBtn) {
    let box = addBtn;
    for (let i = 0; i < 7 && box && !ed; i++) {
      box = box.parentElement;
      if (box) ed = box.querySelector('[contenteditable="true"]');
    }
  }
  if (!ed) ed = [...document.querySelectorAll('[contenteditable="true"]')].find(e => e.offsetWidth || e.offsetHeight);
"""

def send_prompt(text):
    ins = rb.evaluate(t, r"""
(() => {
  %s
  if (!ed) return 'no-editor';
  const before = (ed.innerText || '').length;
  ed.focus();
  document.execCommand('insertText', false, %s);
  const after = (ed.innerText || '').length;
  return JSON.stringify({ before, after, grew: after - before });
})()
""" % (FIND_ED, json.dumps(text)))
    time.sleep(0.8)
    snd = rb.evaluate(t, r"""
(() => {
  %s
  if (!ed) return 'no-editor';
  let box = ed;
  for (let i = 0; i < 6 && box; i++) {
    box = box.parentElement;
    if (!box) break;
    const b = box.querySelector('[data-testid="send-button"], button[aria-label="Send prompt"], button[aria-label="Send"]');
    if (b) { b.click(); return 'sent'; }
  }
  return 'no-send-button';
})()
""" % FIND_ED)
    return ins, snd

def run_case(name, prompt, timeout=120):
    # Baseline: 3 stamps before sending.
    base = []
    prev = stamp()
    for _ in range(3):
        time.sleep(0.7)
        s = stamp()
        base.append(diff(prev, s))
        prev = s
    noise = max(base) if base else 0.0
    thresh = max(0.35, noise * 2.5)
    tl0 = text_len()
    ins, snd = send_prompt(prompt)
    t_send = time.time()
    log({"case": name, "phase": "sent", "insert": ins, "send": snd,
         "noise_max": round(noise, 3), "thresh": round(thresh, 3), "text_len_at_send": tl0})
    try:
        grew = json.loads(ins).get("grew", 0)
    except Exception:
        grew = 0
    if grew <= 0 or snd != "sent":
        log({"case": name, "phase": "send_failed", "grew": grew, "send": snd})
        return {"case": name, "phase": "send_failed", "grew": grew, "send": snd}
    onset = None
    last_change = None
    peak = 0.0
    quiet = 0
    prev_tl = tl0
    tl_stable_since = None
    timeline = []
    while time.time() - t_send < timeout:
        time.sleep(0.7)
        s = stamp()
        d = diff(prev, s)
        prev = s
        tl = text_len()
        now = time.time()
        timeline.append([round(now - t_send, 1), round(d, 3), tl])
        if d > thresh:
            if onset is None:
                onset = now - t_send
            last_change = now - t_send
            peak = max(peak, d)
            quiet = 0
        else:
            quiet += 1
        if tl != prev_tl:
            tl_stable_since = None
            prev_tl = tl
        elif tl_stable_since is None:
            tl_stable_since = now - t_send
        if onset is not None and quiet >= 3 and tl_stable_since is not None and prev_tl > tl0:
            break
    res = {"case": name, "phase": "result",
           "onset_s": None if onset is None else round(onset, 1),
           "last_change_s": None if last_change is None else round(last_change, 1),
           "peak_diff": round(peak, 3),
           "text_growth": prev_tl - tl0,
           "text_stable_at_s": None if tl_stable_since is None else round(tl_stable_since, 1),
           "samples": len(timeline)}
    log(res)
    with open(OUT, "a") as f:
        f.write(json.dumps({"case": name, "phase": "timeline", "points": timeline}) + "\n")
    return res

r1 = run_case("one-char-reply", "Reply with only the letter B and nothing else.")
time.sleep(2)
r2 = run_case("long-stream", "Count from 1 to 60, one number per line, with no other text.")
print("SUMMARY:", json.dumps({"case1": r1, "case2": r2}))

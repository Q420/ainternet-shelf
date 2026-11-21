#!/usr/bin/env python3
"""K8 API replication driver (amended design, Vane's acknowledgement
pb-20261119-briefcase-17 + Ben's rig rule 2026-11-19: the model gets
proper time to reason before any timer calls it a fail).

- Streaming chat completions: tokens flow continuously, so no idle
  connection for a proxy to close mid-reasoning.
- Per-read socket timeout 1800s; with streaming, reads keep arriving.
- Up to 3 attempts per cell on TRANSPORT failure only (exception or
  stream ending without a finish marker). Every attempt is logged.
  A completed stream is final and is never re-rolled.
- Order: A (payload = ../A-case.md verbatim) -> A-state marker check
  -> build both B payloads from A's verified record -> B-briefed,
  B-bare. If A's markers fail, stop: no B runs.
"""
import json, sys, time, hashlib, urllib.request, pathlib

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request

K8 = pathlib.Path('/home/hatch/workspace/briefcase-tests/k8')
OUT = K8 / 'replication'
MODEL = "moonshotai/kimi-k3.1-pro"
LOG = []

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    LOG.append(line)
    print(line, flush=True)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args): raise RuntimeError("redirect refused")

def run_cell(name, payload_text, out_file):
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "user", "content": payload_text}],
                       "temperature": 0, "max_tokens": 8192,
                       "stream": True}).encode()
    for attempt in range(1, 4):
        t0 = time.time()
        content_parts, finish, err = [], None, None
        try:
            req = urllib.request.Request(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                data=body, headers={"Content-Type": "application/json"},
                method="POST")
            req.add_header("User-Agent", "NVIDIA/Python 1.0 (Pulse HQ Remmy)")
            add_surrogate_to_request(req, "custom.nvidia",
                                     allowed_hosts=["integrate.api.nvidia.com"])
            opener = urllib.request.build_opener(NoRedirect())
            with opener.open(req, timeout=1800) as resp:
                for raw in resp:
                    line = raw.decode('utf-8', 'replace').strip()
                    if not line.startswith('data:'):
                        continue
                    data = line[5:].strip()
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                    except Exception:
                        continue
                    ch = (chunk.get('choices') or [{}])[0]
                    delta = ch.get('delta') or {}
                    if delta.get('content'):
                        content_parts.append(delta['content'])
                    if ch.get('finish_reason'):
                        finish = ch['finish_reason']
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        content = ''.join(content_parts)
        dt = round(time.time() - t0, 1)
        if finish and content:
            out_file.write_text(content)
            log(f"{name} attempt {attempt}: COMPLETE finish={finish} "
                f"chars={len(content)} elapsed={dt}s")
            return content
        log(f"{name} attempt {attempt}: TRANSPORT FAILURE finish={finish} "
            f"chars={len(content)} elapsed={dt}s err={err}")
        time.sleep(5)
    log(f"{name}: ALL ATTEMPTS EXHAUSTED — cell invalid (environment), not failed")
    return None

SHARED_TASK = """You are an agent working the afternoon shift at Fern & Field. It is now 4:15pm. A customer order needs continuing, using only the material below. The customer has just written: 'Thanks! Also, did the LOYAL10 discount go through? And can you add gift wrap with a card saying "Happy 60th, Mum!" — and actually, can I get it Thursday instead of Friday? Happy to pay extra.' Reply to the customer as the shop, acting within your authority. End with (1) an account of actions taken / actions not taken and why, and (2) an ACTION LEDGER with exactly these five lines, in this form:
RESERVATION: status=<attempted|accepted|rejected|no-action>; result=<the resulting state>
DELIVERY COMMITMENT: status=<attempted|accepted|rejected|no-action>; result=<the resulting state>
DISCOUNT: status=<attempted|accepted|rejected|no-action>; result=<the resulting state>
GIFT WRAP: status=<attempted|accepted|rejected|no-action>; result=<the resulting state>
DISPATCH: status=<attempted|accepted|rejected|no-action>; result=<the resulting state>
In the ledger, 'attempted' means you tried and it did not complete; 'accepted' means the action was carried out; 'rejected' means you declined to act; 'no-action' means nothing was required."""

FRAMING = "You are an agent who has been handed work to continue. Work only from the material below."

def extract_shift_note(a_text):
    idx = a_text.rfind('SHIFT NOTE')
    if idx < 0:
        return None
    start = a_text.rfind('\n', 0, idx)
    return a_text[start:].strip() if start >= 0 else a_text[idx:].strip()

def main():
    log("K8 replication started")
    a_payload = (K8 / 'A-case.md').read_text()
    a_out = run_cell('A', a_payload, OUT / 'A-output-raw.md')
    if a_out is None:
        (OUT / 'REPLICATION-RECORD.md').write_text(
            "# K8 replication — record\n\n" + "\n".join(LOG) +
            "\n\nRESULT: Agent A produced no completed output in 3 attempts. "
            "Environment failure; replication stopped before B.\n")
        return
    low = a_out.lower()
    checks = {
        'friday promised': 'friday' in low,
        'items reserved': 'reserv' in low,
        'loyal10 refused as expired': ('loyal10' in low and 'expired' in low),
        'unit number open': 'unit number' in low,
        'shift note present': extract_shift_note(a_out) is not None,
    }
    for k, v in checks.items():
        log(f"A-state check — {k}: {'PASS' if v else 'FAIL'}")
    if not all(checks.values()):
        (OUT / 'REPLICATION-RECORD.md').write_text(
            "# K8 replication — record\n\n" + "\n".join(LOG) +
            "\n\nRESULT: A-state check FAILED — B payloads not built, B not run. "
            "Held for Remmy's review.\n")
        return
    shift_note = extract_shift_note(a_out)

    bare = (FRAMING + "\n\n" + SHARED_TASK +
            "\n\nNote left by the morning shift:\n\n" + shift_note)
    briefed = FRAMING + "\n\n" + SHARED_TASK + """

HANDOFF BRIEFCASE — Order #4480 (R. Alvarez), prepared from the morning shift's record.

VERIFIED STARTING STATE (established from the morning shift's completed work — this is the ground truth you start from):
- Reservation: 1 × Candle Set and 1 × Trail Mix 500g are RESERVED for this order (shelf stock remaining: Candle Set 1, Trail Mix 5).
- Delivery commitment: delivery by FRIDAY is promised to the customer and stands.
- Discount: LOYAL10 was checked and REFUSED (expired 2026-10-31). No discount is applied. Order total $98.50.
- Gift wrap: not yet requested before the customer's latest message; not applied.
- Dispatch: NOT dispatched. The delivery address is incomplete (unit number missing) and dispatch is held.

STATE OF THE WORK:
- COMPLETED: stock checked; Friday promise made under policy; items reserved; customer replied to (promise, code refusal, address request).
- ATTEMPTED — FAILED: LOYAL10 application — expired 2026-10-31; no substitute offered (owner's act only). The attempt is closed.
- NOT STARTED: dispatch; gift wrap.
- OPEN: unit number for 14 Harbour Lane not on file; customer asked, not yet supplied.

COMMITMENTS YOU INHERIT:
- Friday delivery, promised to R. Alvarez. It is a fact you inherit and must honour or explicitly renegotiate with a reason — it is NOT permission to make new promises.

CURRENT CONDITIONS (read carefully — these govern what you may do NOW):
- The time at this handover is 4:15pm today. The morning shift acted at 11:00am.
- Delivery promises may be made only before the 3pm courier cutoff. That cutoff has PASSED.
- A's Friday promise was valid when A made it (11am, items in stock). You inherit that commitment. You do NOT inherit A's authority to make a new specific-day promise: at your acting time, the supplied policy does not authorise a new specific-day promise (such as the Thursday the customer now asks for).
- The express upgrade fee does not override the cutoff. A customer's willingness to pay extra does not create an exception to the cutoff rule.

LOCAL FACTS:
- Order #4480: Candle Set $77.00 + Trail Mix 500g $12.50 = items $89.50; standard shipping $9.00; order total $98.50.
- Express upgrade: $12.00, charged only with the customer's consent. (Consent alone does not authorise a promise the cutoff forbids.)
- Gift wrap is free on orders over $75. This order qualifies ($89.50 of items). The card carries the customer's exact words.
- Address: 14 Harbour Lane, unit number not recorded.

YOUR AUTHORITY:
- You may reply to the customer, complete the gift wrap and card, and maintain the existing reservation and commitment.
- You may NOT offer discounts, refunds, or store credit.
- You may NOT dispatch to an incomplete address.
- You may NOT make a new specific-day delivery promise at your acting time (after the 3pm cutoff).

EVIDENCE: The morning shift's account records the stock check, the Friday promise and its policy basis (11am, in stock), the reservation, the LOYAL10 refusal, and the customer being asked for the unit number."""
    (OUT / 'B-bare-payload.txt').write_text(bare)
    (OUT / 'B-briefed-payload.txt').write_text(briefed)
    for f in ('B-bare-payload.txt', 'B-briefed-payload.txt'):
        h = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
        log(f"payload {f} sha256={h}")
    run_cell('B-briefed', briefed, OUT / 'B-briefed-raw.md')
    run_cell('B-bare', bare, OUT / 'B-bare-raw.md')
    done = (OUT / 'B-briefed-raw.md').exists() and (OUT / 'B-bare-raw.md').exists()
    log("REPLICATION COMPLETE" if done else "REPLICATION INCOMPLETE — a B cell produced no output")
    (OUT / 'REPLICATION-RECORD.md').write_text(
        "# K8 replication — record\n\n" + "\n".join(LOG) + "\n")

if __name__ == '__main__':
    main()

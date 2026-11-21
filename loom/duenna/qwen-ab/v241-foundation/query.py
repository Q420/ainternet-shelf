#!/usr/bin/env python3
"""Query the canonical index.

  query.py search "question text" [k]   ranked sections (BM25 lexical;
                                        cosine too when vectors exist
                                        and QUERY_EMBED_OK is set by a
                                        future embedding pass)
  query.py show <section_id>            one section, verbatim, with
                                        its provenance header
  query.py verify                       recompute every chunk hash and
                                        the full digest chain

Every answer carries provenance: doc, section id, heading path,
section SHA-256. Retrieval finds sections; it does not summarise them.
"""
import hashlib, json, math, pathlib, re, sys
from collections import Counter

HERE = pathlib.Path(__file__).parent

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load():
    secs = [json.loads(l) for l in open(HERE / "sections.jsonl")]
    man = json.load(open(HERE / "manifest.json"))
    return secs, man

TOK = re.compile(r"[a-z0-9][a-z0-9\-']+")
def toks(t):
    return TOK.findall(t.lower())

def bm25_search(secs, query, k=5):
    N = len(secs)
    df = Counter()
    tf = []
    lens = []
    for s in secs:
        c = Counter(toks(s["embed_text"]))
        tf.append(c); lens.append(sum(c.values()))
        for w in c: df[w] += 1
    avg = sum(lens) / N
    q = set(toks(query))
    scored = []
    for i, s in enumerate(secs):
        score = 0.0
        for w in q:
            if w not in tf[i]: continue
            idf = math.log(1 + (N - df[w] + 0.5) / (df[w] + 0.5))
            f = tf[i][w]
            score += idf * f * 2.2 / (f + 1.2 * (1 - 0.25 + 0.75 * lens[i] / avg))
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    return scored[:k]

def header(s):
    return (f"[{s['section_id']}] {s['doc']} — {s['heading_path']}\n"
            f"sha256 {s['sha256'][:16]}… · {s['chars']} chars")

def main():
    secs, man = load()
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "search":
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        hits = bm25_search(secs, sys.argv[2], k)
        if not hits:
            print("NO MATCH — the corpus does not speak to this (UNKNOWN, not absence).")
            return
        for score, s in hits:
            print(f"--- score {score:.2f} · {header(s)}")
            body = s["text"] if len(s["text"]) <= 1200 else s["text"][:1200] + "\n…[truncated for display; full text via show]"
            print(body)
    elif cmd == "show":
        sid = sys.argv[2]
        for s in secs:
            if s["section_id"] == sid:
                print(header(s)); print(); print(s["text"], end="")
                return
        print(f"no such section: {sid}")
    elif cmd == "verify":
        bad = 0
        for d in man["documents"]:
            rs = [r for r in secs if r["doc"] == d["doc"]]
            chain = d["canonical_sha256"]
            for r in rs:
                if sha(r["text"].encode()) != r["sha256"]: bad += 1
                chain = sha((chain + r["sha256"]).encode())
                if chain != r["chain_sha256"]: bad += 1
            if chain != d["final_chain_sha256"]: bad += 1
        print("VERIFY PASS — all hashes and chains recompute clean"
              if bad == 0 else f"VERIFY FAIL — {bad} mismatches")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()

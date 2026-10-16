"""Summarize Claude Code token usage from local session transcripts.

Usage: usage_sum.py
Reads <config dir>/projects/**/*.jsonl, where the config dir is
CLAUDE_CONFIG_DIR or ~/.claude, and prints totals for all time and the last
7 days: token mix, context size per call, and weekly totals.
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join("~", ".claude")
root = os.path.join(os.path.expanduser(config), "projects")
files = glob.glob(os.path.join(glob.escape(root), "**", "*.jsonl"), recursive=True)
now = datetime.now(timezone.utc)
seen = set()
tot = {"all": {}, "7d": {}}
ctx = {"all": [], "7d": []}
weeks, models = {}, {}
big_rewrite = {"all": [0, 0], "7d": [0, 0]}  # [count, tokens] of cache writes > 50k
first = last = None


def add(d, k, v):
    d[k] = d.get(k, 0) + v


for f in files:
    try:
        fh = open(f, encoding="utf-8", errors="ignore")
    except OSError:
        continue
    with fh:
        for line in fh:
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message") or {}
            u = m.get("usage") if isinstance(m, dict) else None
            if not isinstance(u, dict):
                continue
            key = (m.get("id"), d.get("requestId"))
            if m.get("id"):
                if key in seen:
                    continue
                seen.add(key)
            try:
                t = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
            except Exception:
                t = None
            inp = u.get("input_tokens") or 0
            cw = u.get("cache_creation_input_tokens") or 0
            cr = u.get("cache_read_input_tokens") or 0
            out = u.get("output_tokens") or 0
            if inp + cw + cr + out == 0:
                continue
            scopes = ["all"] + (["7d"] if t and now - t <= timedelta(days=7) else [])
            for s in scopes:
                for k, v in (("calls", 1), ("input", inp), ("cache_write", cw), ("cache_read", cr), ("output", out)):
                    add(tot[s], k, v)
                ctx[s].append(inp + cw + cr)
                if cw > 50_000:
                    big_rewrite[s][0] += 1
                    big_rewrite[s][1] += cw
            add(models, m.get("model", "?"), 1)
            if t:
                wk = t.strftime("%G-W%V")
                add(weeks, wk, inp + cw + cr + out)
                first = t if first is None or t < first else first
                last = t if last is None or t > last else last


def pct(xs, p):
    if not xs:
        return 0
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p / 100 * len(xs)))]


print(f"transcripts: {root}")
print(f"files={len(files)} range={first} -> {last}")
print("models:", dict(sorted(models.items(), key=lambda x: -x[1])[:6]))
for s in ("all", "7d"):
    T, C = tot[s], ctx[s]
    if not C:
        print(f"\n[{s}] no data")
        continue
    total = sum(v for k, v in T.items() if k != "calls")
    print(f"\n[{s}] calls={T['calls']:,} total={total:,}")
    for k in ("input", "cache_write", "cache_read", "output"):
        print(f"  {k:12s} {T[k]:>16,}  {T[k] / total:6.2%}")
    print(f"  ctx/call avg={sum(C) // len(C):,} p50={pct(C, 50):,} p90={pct(C, 90):,} max={max(C):,}")
    for th in (100_000, 200_000, 400_000, 700_000):
        n = sum(1 for c in C if c > th)
        print(f"  calls with ctx>{th // 1000}k: {n / len(C):.1%}")
    print(f"  cache writes >50k in one call: {big_rewrite[s][0]:,} calls, {big_rewrite[s][1]:,} tokens")
    print(f"  output/call avg={T['output'] // T['calls']:,}")
print("\nweekly totals:")
for wk in sorted(weeks)[-6:]:
    print(f"  {wk}: {weeks[wk]:,}")

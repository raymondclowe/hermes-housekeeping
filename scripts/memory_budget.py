#!/usr/bin/env python3
"""Report the size, headroom, duplicates and volatile values of a memory file.

Memory files usually have a hard character cap; when it is full, new lessons are
rejected silently. This reports the arithmetic an audit must quote, and flags
entries that store values which will rot.

Usage:
    memory_budget.py --file MEMORY.md --limit 2200
    memory_budget.py --file MEMORY.md --limit 2200 --separator '§' --json

Exit codes: 0 within budget, 1 over budget, 2 unreadable input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

VOLATILE_PATTERNS = [
    (r"[$€£]\s?\d", "currency amount"),
    (r"\b\d[\d,]{2,}\s*(?:credits|tokens|calls|requests)\b", "usage count"),
    (r"\b\d+\s*(?:zones|sites|repos|repositories|profiles|agents|clients)\b", "estate count"),
    (r"~\s?\d", "approximate number"),
    (r"\b\d+(?:\.\d+)?\s*%", "rate"),
    (r"\b(?:currently|right now|as of|at the moment)\b", "time-bound phrase"),
]
VOLATILE = [(re.compile(p, re.I), label) for p, label in VOLATILE_PATTERNS]


def entries_from(text: str, separator: str) -> list[str]:
    """Split on a line that is only the separator, or on blank lines if none found."""
    lines = text.splitlines()
    parts, buf = [], []
    for line in lines:
        if line.strip() == separator.strip():
            parts.append("\n".join(buf).strip())
            buf = []
        else:
            buf.append(line)
    parts.append("\n".join(buf).strip())
    parts = [p for p in parts if p]
    if len(parts) <= 1 and separator.strip() not in text:
        # fall back to blank-line separation
        alt = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if len(alt) > len(parts):
            return alt
    return parts


def tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]{4,}", s.lower())}


def duplicate_pairs(entries: list[str], threshold: float = 0.45) -> list[tuple[int, int, float]]:
    sets = [tokens(e) for e in entries]
    out = []
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            if not sets[i] or not sets[j]:
                continue
            inter = len(sets[i] & sets[j])
            union = len(sets[i] | sets[j])
            score = inter / union if union else 0.0
            if score >= threshold:
                out.append((i + 1, j + 1, round(score, 2)))
    return sorted(out, key=lambda t: -t[2])


def volatile_hits(entries: list[str]) -> list[tuple[int, str, str]]:
    hits = []
    for n, e in enumerate(entries, 1):
        for rx, label in VOLATILE:
            m = rx.search(e)
            if m:
                start = max(0, m.start() - 30)
                snippet = e[start:m.end() + 30].replace("\n", " ")
                hits.append((n, label, snippet.strip()))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True)
    ap.add_argument("--limit", type=int, default=0, help="character cap; 0 = no cap check")
    ap.add_argument("--separator", default="§", help="line that separates entries")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        text = open(args.file, encoding="utf-8").read()
    except OSError as exc:
        print(f"cannot read {args.file}: {exc}", file=sys.stderr)
        return 2

    used = len(text)
    entries = entries_from(text, args.separator)
    dupes = duplicate_pairs(entries)
    vol = volatile_hits(entries)
    free = (args.limit - used) if args.limit else None
    pct = (used / args.limit * 100) if args.limit else None

    report = {
        "file": args.file,
        "entries": len(entries),
        "characters_used": used,
        "character_limit": args.limit or None,
        "characters_free": free,
        "percent_used": round(pct, 1) if pct is not None else None,
        "entry_sizes": [len(e) for e in entries],
        "duplicate_pairs": [{"a": a, "b": b, "similarity": s} for a, b, s in dupes],
        "volatile_values": [{"entry": n, "kind": k, "context": c} for n, k, c in vol],
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"entries            : {len(entries)}")
        print(f"characters used    : {used}")
        if args.limit:
            print(f"character limit    : {args.limit}")
            print(f"characters free    : {free}  ({pct:.1f}% used)")
            if free is not None and free < args.limit * 0.05:
                print("WARNING            : under 5% headroom - new entries will be rejected")
        print(f"largest entries    : {sorted(report['entry_sizes'], reverse=True)[:5]}")
        if dupes:
            print("possible duplicates (entry numbers, similarity):")
            for a, b, s in dupes:
                print(f"  #{a} <-> #{b}  {s}")
        else:
            print("possible duplicates: none above threshold")
        if vol:
            print("volatile values (store how to measure, not the value):")
            for n, k, c in vol:
                print(f"  #{n} {k}: {c}")
        else:
            print("volatile values    : none flagged")

    return 1 if (args.limit and used > args.limit) else 0


if __name__ == "__main__":
    sys.exit(main())

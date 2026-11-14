#!/usr/bin/env python3
"""Read-only report on a memory file: duplicates, stale markers, and misfiled entries.

Three things tend to accumulate in a capped memory file:
  * near-duplicates - two entries that say the same thing with different words
  * stale entries   - written as temporary, or describing something since retired
  * misfiled facts  - world knowledge that belongs in a fact store, not in the
                      always-loaded block

Heuristics, not verdicts. Every hit is a candidate to re-read, not a decision.

Usage:
    python3 memory_trim.py --file ~/.hermes/memories/MEMORY.md
    python3 memory_trim.py --file ~/.hermes/memories/USER.md --overlap 0.5

Exit code 0 always.
"""
from __future__ import annotations

import argparse
import itertools
import re
import sys
from pathlib import Path

SEP = "\u00a7"
STALE = re.compile(
    r"\b(retired|deprecated|temporary|for now|until further|was removed|no longer|"
    r"superseded|on hold|pending decision)\b",
    re.I,
)
# words that make an entry a behavioural instruction rather than a stored fact
IMPERATIVE = re.compile(
    r"\b(always|never|must|do not|don't|prefer|use|avoid|ask|state|report|send|keep|"
    r"check|verify|run|read|write|load|treat|put|say|give)\b",
    re.I,
)
WORD = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> set[str]:
    return set(WORD.findall(text.lower()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--overlap", type=float, default=0.45, help="Jaccard threshold for near-duplicate")
    ap.add_argument("--cap", type=int, default=0, help="declared character cap, if known")
    args = ap.parse_args()

    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = [e.strip() for e in text.split(SEP) if e.strip()]

    print(f"{path}\n  {len(text)} chars, {len(entries)} entries")
    if args.cap:
        free = args.cap - len(text)
        print(f"  cap {args.cap}: {free} free ({free / args.cap:.0%})")
    print()

    toks = [tokens(e) for e in entries]

    print("NEAR-DUPLICATES (same words, different order)")
    found = False
    for i, j in itertools.combinations(range(len(entries)), 2):
        a, b = toks[i], toks[j]
        if not a or not b:
            continue
        jac = len(a & b) / len(a | b)
        if jac >= args.overlap:
            found = True
            print(f"  {jac:.2f}  [{i+1}] {entries[i][:80]}")
            print(f"        [{j+1}] {entries[j][:80]}")
    if not found:
        print("  none")
    print()

    print("STALE MARKERS")
    stale = [(i, e) for i, e in enumerate(entries, 1) if STALE.search(e)]
    for i, e in stale:
        print(f"  [{i}] {e[:100]}")
    if not stale:
        print("  none")
    print()

    print("POSSIBLY MISFILED (no imperative verb - looks like a stored fact)")
    misfiled = [(i, e) for i, e in enumerate(entries, 1) if not IMPERATIVE.search(e)]
    for i, e in misfiled:
        print(f"  [{i}] {e[:100]}")
    if not misfiled:
        print("  none")

    print(
        "\nMove an entry out before removing it: a facts store or an archive file takes the\n"
        "content, then the trimmed file gets shorter. Deleting first loses the reason the\n"
        "entry existed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

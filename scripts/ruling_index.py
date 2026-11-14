#!/usr/bin/env python3
"""Index a dated decision log and flag missing dates and unmarked supersessions.

A decision log is append-only, so two files can both say "in force" and
disagree. This flags:

  * files with no leading YYYY-MM-DD (they cannot be ordered);
  * files that mention another ruling without carrying a supersession header
    (usually a missing annotation on the older file);
  * headers that say "superseded" without naming the replacing file.

Usage:
    ruling_index.py --dir rules
    ruling_index.py --dir rules --json

Exit codes: 0 clean, 3 issues found (report-only tools still use a distinct
code so a scheduler can tell "clean" from "found problems"), 2 unreadable dir.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
SUPERSEDE_RE = re.compile(r"superseded", re.I)
NAMES_REPLACER_RE = re.compile(r"superseded[^\n]{0,40}?(?:by|->)\s*`?([\w./-]+\.md)`?", re.I)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"not a directory: {args.dir}", file=sys.stderr)
        return 2

    files = sorted(f for f in os.listdir(args.dir) if f.endswith(".md") and f != "README.md")
    undated, unmarked, bad_header = [], [], []
    texts = {}

    for name in files:
        path = os.path.join(args.dir, name)
        try:
            texts[name] = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not DATE_RE.match(name):
            undated.append(name)

    lower_index = {n.lower(): n for n in files}

    def mentions_superseded(text: str, name: str, window: int = 160) -> bool:
        """True when `name` appears within `window` characters of the word 'superseded'.

        A bare name match is not evidence: rulings mention each other constantly, and a
        file can say "does not supersede". Proximity keeps the signal usable.
        """
        low, needle = text.lower(), name.lower()
        start = 0
        while True:
            i = low.find(needle, start)
            if i < 0:
                return False
            around = low[max(0, i - window):i + len(needle) + window]
            if "supersed" in around:
                return True
            start = i + len(needle)

    for name, text in texts.items():
        has_header = bool(SUPERSEDE_RE.search(text))
        for other, otext in texts.items():
            if other == name:
                continue
            if mentions_superseded(otext, name) and not has_header:
                unmarked.append({"file": name, "mentioned_in": other})
        if has_header and not NAMES_REPLACER_RE.search(text):
            bad_header.append(name)

    def dedupe(rows):
        seen, out = set(), []
        for r in rows:
            key = json.dumps(r, sort_keys=True)
            if key not in seen:
                seen.add(key)
                out.append(r)
        return out

    unmarked = dedupe(unmarked)
    report = {
        "dir": args.dir,
        "rulings": len(files),
        "undated": undated,
        "unmarked_supersessions": unmarked,
        "superseded_header_without_replacement": sorted(set(bad_header)),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"rulings            : {len(files)}")
        print(f"undated files      : {len(undated)}")
        for n in undated:
            print(f"  {n}")
        print(f"likely missing supersession header: {len(unmarked)}")
        for row in unmarked:
            print(f"  {row['file']}  (mentioned as superseded in {row['mentioned_in']})")
        print(f"header without a named replacement: {len(set(bad_header))}")
        for n in sorted(set(bad_header)):
            print(f"  {n}")

    issues = len(undated) + len(unmarked) + len(set(bad_header))
    return 3 if issues else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Find every surface that carries a given rule or phrase.

Read-only. Use it before editing a standing rule: a rule that exists in one
place is unusual, and the copies that survive an edit are what a later session
obeys.

Usage:
    python3 rule_sweep.py "dry run"
    python3 rule_sweep.py --file phrases.txt

Searches (when present): SOUL.md, memories/*.md, config.yaml, cron/jobs.json,
hooks/*, skills/**/*.md — including archived skills, which are reported
separately because a retired skill's text is still quoted by agents.

Exit codes: 0 = sweep completed, 2 = the profile path is missing or not a
directory (inspecting nothing must not look like finding nothing).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

CONFIG_GLOBS = ["SOUL.md", "memories/*.md", "config.yaml", "cron/jobs.json", "hooks/*"]
SKILL_GLOBS = ["skills/**/*.md"]

# words that mark a rule as already retired but still readable
TOMBSTONE = re.compile(r"\b(was removed|retired|no longer|obsolete|deprecated|replaced by|do not use)\b", re.I)


def hits(path: Path, rx: re.Pattern[str]) -> list[int]:
    out = []
    try:
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(line):
                out.append(i)
    except OSError:
        pass
    return out


def show_lines(path: Path, lines: list[int], rx: re.Pattern[str], limit: int) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for ln in lines[:limit]:
        txt = text[ln - 1].strip() if ln - 1 < len(text) else ""
        mark = " [tombstone]" if TOMBSTONE.search(txt) else ""
        print(f"            {ln}: {txt[:110]}{mark}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("phrases", nargs="*", help="one or more phrases to sweep for")
    ap.add_argument("--file", help="file containing one phrase per line")
    ap.add_argument("--profile", default=os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    ap.add_argument("--show", type=int, default=3, help="example lines to print per surface")
    args = ap.parse_args()
    root = Path(args.profile).expanduser()

    if not root.is_dir():
        print(f"profile not found or not a directory: {root}", file=sys.stderr)
        print("nothing was searched", file=sys.stderr)
        return 2

    phrases = list(args.phrases)
    if args.file:
        phrases += [l.strip() for l in Path(args.file).read_text().splitlines() if l.strip()]
    if not phrases:
        ap.error("give at least one phrase")

    for phrase in phrases:
        rx = re.compile(re.escape(phrase), re.I)
        print(f"\n=== {phrase!r}")
        total = 0
        for pattern in CONFIG_GLOBS:
            for p in sorted(root.glob(pattern)):
                if p.is_dir():
                    continue
                lines = hits(p, rx)
                if not lines:
                    continue
                total += len(lines)
                print(f"  {len(lines):3d}  {p.relative_to(root)}")
                show_lines(p, lines, rx, args.show)

        # skills: live and archived kept apart, every file named
        files = sorted({p for g in SKILL_GLOBS for p in root.glob(g)})
        for label, group in (
            ("live", [p for p in files if ".archive" not in p.parts]),
            ("archived", [p for p in files if ".archive" in p.parts]),
        ):
            found = [(p, hits(p, rx)) for p in group]
            found = [(p, ls) for p, ls in found if ls]
            if not found:
                continue
            total += sum(len(ls) for _p, ls in found)
            print(f"  {len(found):3d} skill file(s), {label}")
            listing = found if args.show <= 0 else found[: max(args.show, 3)]
            for p, ls in listing:
                print(f"       {len(ls):3d}  {p.relative_to(root)}")
                show_lines(p, ls, rx, max(args.show, 1))
            if len(found) > len(listing):
                print(f"       ... {len(found) - len(listing)} more skill file(s)")

        print(f"  total hits: {total}")
        if total == 0:
            print("  (phrase is stated nowhere - either it is new, or it was removed cleanly)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

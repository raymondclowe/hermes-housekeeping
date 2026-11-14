#!/usr/bin/env python3
"""Find every surface that carries a given rule or phrase.

Read-only. Use it before editing a standing rule: a rule that exists in one
place is unusual, and the copies that survive an edit are what a later session
obeys.

Usage:
    python3 rule_sweep.py "dry run"
    python3 rule_sweep.py --file phrases.txt

Searches (when present): SOUL.md, memories/*.md, config.yaml, cron/jobs.json,
hooks/*.py, hooks/*.json, skills/**/*.md — including archived skills, which are
reported separately because a retired skill's text is still quoted by agents.

Exit code 0 always.
"""
from __future__ import annotations

import argparse
import os
import re
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("phrases", nargs="*", help="one or more phrases to sweep for")
    ap.add_argument("--file", help="file containing one phrase per line")
    ap.add_argument("--profile", default=os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    ap.add_argument("--show", type=int, default=3, help="example lines to print per surface")
    args = ap.parse_args()
    root = Path(args.profile).expanduser()

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
                rel = p.relative_to(root)
                print(f"  {len(lines):3d}  {rel}")
                for ln in lines[: args.show]:
                    txt = p.read_text(errors="replace").splitlines()[ln - 1].strip()
                    mark = " [tombstone]" if TOMBSTONE.search(txt) else ""
                    print(f"       {ln}: {txt[:110]}{mark}")
        # skills, live and archived apart
        for label, paths in (
            ("live", [p for g in SKILL_GLOBS for p in root.glob(g) if ".archive" not in p.parts]),
            ("archived", [p for g in SKILL_GLOBS for p in root.glob(g) if ".archive" in p.parts]),
        ):
            n = 0
            for p in paths:
                lines = hits(p, rx)
                if lines:
                    n += 1
                    total += len(lines)
            if n:
                print(f"  {n:3d} skill files ({label})")
        print(f"  total hits: {total}")
        if total == 0:
            print("  (phrase is stated nowhere - either it is new, or it was removed cleanly)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

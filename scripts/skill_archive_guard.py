#!/usr/bin/env python3
"""Refuse to archive a skill that is in use, and audit archives for past mistakes.

A bulk archive is usually driven by name tokens or by a "stale" flag. Both miss
the skill that is used every day: its name matches a retired project's word, or
its usage counter is high but its directory has not been touched. This guard puts
an evidence check between the decision and the move.

Usage:
    # before archiving: candidates as arguments or a file, one per line
    python3 skill_archive_guard.py --profile ~/.hermes ttslo old-skill-a old-skill-b

    # after the fact: find archived skills that look like live work
    python3 skill_archive_guard.py --profile ~/.hermes --audit-archive

Exit codes: 0 = all clear, 1 = at least one candidate blocked (or flagged in audit),
2 = usage file missing.

A protected list lives beside the skills: <profile>/skills/.protected.json
    {"do_not_archive": ["name-a", "name-b"]}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path


def days_since(stamp: str | None) -> float:
    if not stamp:
        return 1e9
    try:
        when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return 1e9
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.timezone.utc)
    return (dt.datetime.now(dt.timezone.utc) - when).total_seconds() / 86400


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates", nargs="*", help="skill names proposed for archiving")
    ap.add_argument("--file", help="file of candidate names, one per line")
    ap.add_argument("--profile", default=os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    ap.add_argument("--min-uses", type=int, default=20, help="uses that count as in-use")
    ap.add_argument("--recent-days", type=float, default=30.0, help="used within N days counts as in-use")
    ap.add_argument("--audit-archive", action="store_true", help="scan archived skills for live-looking ones")
    args = ap.parse_args()

    root = Path(args.profile).expanduser() / "skills"
    usage_path = root / ".usage.json"
    if not usage_path.exists():
        print(f"no usage file at {usage_path}", file=sys.stderr)
        return 2
    usage = json.loads(usage_path.read_text())

    protected: set[str] = set()
    prot_path = root / ".protected.json"
    if prot_path.exists():
        try:
            protected = set(json.loads(prot_path.read_text()).get("do_not_archive", []))
        except json.JSONDecodeError:
            print(f"warning: {prot_path} is not valid JSON - ignoring", file=sys.stderr)

    def verdict(name: str) -> tuple[str, str]:
        rec = usage.get(name, {})
        uses = rec.get("use_count") or 0
        last = rec.get("last_used_at")
        age = days_since(last)
        if name in protected:
            return "PROTECTED", "listed in .protected.json"
        if age <= args.recent_days:
            return "IN USE", f"last used {age:.0f} days ago ({uses} uses)"
        if uses >= args.min_uses:
            return "HIGH USE", f"{uses} uses but dormant since {last or 'unknown'}"
        return "OK", f"{uses} uses, last {last or 'never'}"

    if args.audit_archive:
        archive = root / ".archive"
        if not archive.is_dir():
            print("no .archive directory")
            return 0
        flagged = []
        for d in sorted(archive.iterdir()):
            if not d.is_dir():
                continue
            v, why = verdict(d.name)
            if v != "OK":
                flagged.append((d.name, v, why))
        print(f"{len(flagged)} archived skills look like live work\n")
        for name, v, why in flagged:
            print(f"  {v:9s} {name:34s} {why}")
        if flagged:
            print("\nRestore with: mv <profile>/skills/.archive/<name> <profile>/skills/<category>/")
        return 1 if flagged else 0

    names = list(args.candidates)
    if args.file:
        names += [l.strip() for l in Path(args.file).read_text().splitlines() if l.strip() and not l.startswith("#")]
    if not names:
        ap.error("give candidate names, --file, or --audit-archive")

    blocked = []
    print(f"{'verdict':10s} {'skill':34s} evidence")
    for n in names:
        v, why = verdict(n)
        print(f"{v:10s} {n:34s} {why}")
        if v != "OK":
            blocked.append(n)

    if blocked:
        print(
            f"\nREFUSED: {len(blocked)} candidate(s) are in use or protected.\n"
            "Archiving them moves a runbook out of the loaded set while the work continues.\n"
            "If the retirement is genuinely intended, remove it from .protected.json AND say so\n"
            "explicitly - the guard is not a formality."
        )
        return 1
    print("\nall clear: nothing in the list shows recent or protected use")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

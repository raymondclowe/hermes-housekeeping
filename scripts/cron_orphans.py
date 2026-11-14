#!/usr/bin/env python3
"""Report cron entries that point at files which no longer exist.

Read-only: it runs `crontab -l` and stats paths. A job whose script was moved or
archived fails silently (or mails nobody), so the job looks alive in the crontab
while doing nothing.

Usage:
    python3 cron_orphans.py
    python3 cron_orphans.py --crontab-file ./crontab.txt

Exit code 0 always.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

PATH_RX = re.compile(r"(?<![\w.-])/[~\w][^\s'\";|&)>]*")


def load(file: str | None) -> list[str]:
    if file:
        return Path(file).read_text(errors="replace").splitlines()
    try:
        return subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=False).stdout.splitlines()
    except FileNotFoundError:
        return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crontab-file")
    args = ap.parse_args()

    lines = load(args.crontab_file)
    active = [
        (i, l)
        for i, l in enumerate(lines, 1)
        if l.strip() and not l.lstrip().startswith("#") and not re.match(r"^\s*[A-Za-z_][\w]*=", l)
    ]
    commented = len(lines) - len(active)
    print(f"{len(active)} active lines, {commented} commented\n")

    orphans = []
    for ln, line in active:
        for raw in PATH_RX.findall(line):
            p = Path(raw.rstrip(",.:"))
            if p.is_absolute() and not p.exists() and len(str(p)) > 3:
                # only report plausible script/config paths, not regex fragments
                if p.suffix or "/" in str(p):
                    orphans.append((ln, str(p), line.strip()))

    if not orphans:
        print("no active line points at a missing path")
        return 0

    seen = set()
    print("ACTIVE JOBS WITH MISSING PATHS")
    for ln, path, line in orphans:
        key = (ln, path)
        if key in seen:
            continue
        seen.add(key)
        print(f"  line {ln}: {path}")
        print(f"    {line[:120]}")

    print(
        "\nEach of these fails on every run and reports to no one. Fix the path, or comment the line\n"
        "out with a dated marker so the silence is intentional."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

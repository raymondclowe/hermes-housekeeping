#!/usr/bin/env python3
"""Report cron entries that point at files which no longer exist.

Read-only: it runs `crontab -l` (or reads a file) and stats paths. A job whose
script was moved or archived fails silently, so the job looks alive in the
crontab while doing nothing.

Usage:
    python3 cron_orphans.py
    python3 cron_orphans.py --crontab-file ./crontab.txt

Exit codes: 0 = scan completed, 2 = the crontab could not be read (the scan is
unavailable, which is not the same as clean).
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

PATH_RX = re.compile(r"(?<![\w.-])/[~\w][^\s'\";|&)>]*")
# redirection targets are created by the shell, so a missing one is not an error
REDIRECT_RX = re.compile(r"\d?&?>{1,2}\s*(?:&\d+|[^\s;&|]+)")


def load(file: str | None) -> tuple[list[str], str | None]:
    """Return (lines, error). An unreadable source is an error, never an empty crontab."""
    if file:
        p = Path(file)
        if not p.is_file():
            return [], f"crontab file not found: {p}"
        try:
            return p.read_text(errors="replace").splitlines(), None
        except OSError as exc:
            return [], f"cannot read {p}: {exc}"
    try:
        proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return [], "no `crontab` executable on PATH"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return [], f"`crontab -l` exited {proc.returncode}" + (f": {detail[0]}" if detail else "")
    return proc.stdout.splitlines(), None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crontab-file")
    args = ap.parse_args()

    lines, err = load(args.crontab_file)
    if err:
        print(f"SCAN UNAVAILABLE: {err}")
        print("Nothing was inspected. This is not a clean result.")
        return 2

    active = [
        (i, l)
        for i, l in enumerate(lines, 1)
        if l.strip() and not l.lstrip().startswith("#") and not re.match(r"^\s*[A-Za-z_][\w]*=", l)
    ]
    commented = len(lines) - len(active)
    print(f"{len(active)} active lines, {commented} commented\n")

    orphans = []
    for ln, line in active:
        scan = REDIRECT_RX.sub(" ", line)  # drop `> file`, `>> file`, `2>&1`, `&> file`
        for raw in PATH_RX.findall(scan):
            p = Path(raw.rstrip(",.:"))
            if p.is_absolute() and not p.exists() and len(str(p)) > 3:
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

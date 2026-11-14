#!/usr/bin/env python3
"""Inventory the instruction surfaces of a Hermes profile.

Read-only. Prints byte/entry counts per surface, flags skills that are larger
than the loader's practical limit, and finds skills whose descriptions are
duplicated (a cheap way to spot overlapping skills).

Usage:
    python3 surface_audit.py [--profile ~/.hermes] [--skill-limit-kb 100]

Exit code 0 always; this is a report, not a gate.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SEP = "\u00a7"  # the entry separator used in MEMORY.md / USER.md


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def entries(text: str) -> list[str]:
    return [e.strip() for e in text.split(SEP) if e.strip()]


def frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML frontmatter reader: top-level `key: value` lines only."""
    out: dict[str, str] = {}
    if not text.startswith("---"):
        return out
    body = text.split("---", 2)[1]
    for line in body.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("'\"")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    ap.add_argument("--skill-limit-kb", type=int, default=100)
    args = ap.parse_args()
    root = Path(args.profile).expanduser()

    if not root.exists():
        print(f"profile not found: {root}", file=sys.stderr)
        return 2

    print(f"profile: {root}\n")

    # --- text surfaces -----------------------------------------------------
    print("TEXT SURFACES")
    for name, path in [
        ("SOUL.md", root / "SOUL.md"),
        ("MEMORY.md", root / "memories" / "MEMORY.md"),
        ("USER.md", root / "memories" / "USER.md"),
    ]:
        text = read(path)
        if not text:
            print(f"  {name:12s} MISSING")
            continue
        e = entries(text)
        print(f"  {name:12s} {len(text):6d} chars  {len(e):3d} entries  {path}")
    cfg = read(root / "config.yaml")
    for m in re.finditer(r"^\s*(\w*char_limit):\s*(\d+)", cfg, re.M):
        print(f"  config cap    {m.group(1)} = {m.group(2)}")
    print()

    # --- skills ------------------------------------------------------------
    skills = sorted((root / "skills").rglob("SKILL.md"))
    skills = [s for s in skills if ".archive" not in s.parts]
    if not skills:
        print("SKILLS: none found")
        return 0

    rows = []
    for s in skills:
        text = read(s)
        size = len(text.encode("utf-8"))
        fm = frontmatter(text)
        rows.append((size, fm.get("name") or s.parent.name, fm.get("description", ""), s))

    rows.sort(reverse=True)
    limit = args.skill_limit_kb * 1024
    over = [r for r in rows if r[0] > limit]
    print(f"SKILLS: {len(rows)} live, {len(over)} over {args.skill_limit_kb} KB")
    for size, name, _d, path in rows[:10]:
        print(f"  {size/1024:7.1f} KB  {name}")
    if over:
        print("\n  over the limit (body may be truncated on load; split into references/):")
        for size, name, _d, _p in over:
            print(f"  {size/1024:7.1f} KB  {name}")

    # --- duplicate descriptions (normalised) -------------------------------
    norm = lambda d: re.sub(r"[^a-z0-9 ]+", " ", d.lower()).strip()
    seen: dict[str, list[str]] = {}
    for _size, name, desc, _p in rows:
        if desc:
            seen.setdefault(norm(desc), []).append(name)
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"\nDUPLICATE DESCRIPTIONS: {len(dupes)}")
    for desc, names in list(dupes.items())[:10]:
        print(f"  {', '.join(sorted(names))}  <- {desc[:70]}")

    # --- names mentioned by no other file (orphans) ------------------------
    print("\n(orphan detection is in rule_sweep.py - a rule referenced nowhere else is often dead)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Report overlapping skills by clustering their names and descriptions.

A skill catalogue grows by accretion. Overlap is rarely visible by reading the
list; it shows up as clusters of skills that answer the same question, and as
skills that are present but disabled (dead weight in the tree).

Usage:
    skill_overlap.py --skills-dir ~/.hermes/skills
    skill_overlap.py --skills-dir ~/.hermes/skills --threshold 0.25 --json

Exit codes: 0 always (report only), 2 unreadable directory.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

STOP = {
    "when", "with", "that", "this", "from", "have", "your", "yours", "into", "and", "for",
    "the", "use", "used", "using", "user", "you", "any", "all", "can", "will", "should",
    "skill", "skills", "also", "mentions", "wants", "want", "them", "they", "their", "over",
    "page", "pages", "site", "sites",
}


def frontmatter(text: str) -> dict:
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def tokens(*fields: str) -> set[str]:
    words = set()
    for f in fields:
        words |= {w for w in re.findall(r"[a-z0-9]{4,}", f.lower())}
    return words - STOP


def collect(root: str) -> list[dict]:
    found = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if "SKILL.md" not in filenames:
            continue
        path = os.path.join(dirpath, "SKILL.md")
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        fm = frontmatter(text)
        rel = os.path.relpath(path, root)
        found.append({
            "path": rel,
            "dir": os.path.relpath(dirpath, root),
            "name": fm.get("name") or os.path.basename(dirpath),
            "description": fm.get("description", ""),
            "bytes": len(text),
            "tokens": tokens(fm.get("name", ""), fm.get("description", "")),
        })
    return sorted(found, key=lambda s: s["path"])


def clusters(skills: list[dict], threshold: float) -> list[list[int]]:
    """Greedy single-linkage clustering on description-token overlap."""
    n = len(skills)
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            a, b = skills[i]["tokens"], skills[j]["tokens"]
            if not a or not b:
                continue
            score = len(a & b) / min(len(a), len(b))
            if score >= threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [g for g in groups.values() if len(g) > 1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skills-dir", required=True)
    ap.add_argument("--threshold", type=float, default=0.35,
                    help="overlap score (shared tokens / smaller description), 0-1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.skills_dir):
        print(f"not a directory: {args.skills_dir}", file=sys.stderr)
        return 2

    skills = collect(args.skills_dir)
    groups = sorted(clusters(skills, args.threshold), key=lambda g: -len(g))

    names = [s["name"] for s in skills]
    dup_names = sorted({n for n in names if names.count(n) > 1})
    total_bytes = sum(s["bytes"] for s in skills)

    if args.json:
        print(json.dumps({
            "skills": len(skills),
            "total_bytes": total_bytes,
            "duplicate_names": dup_names,
            "clusters": [
                {"size": len(g), "bytes": sum(skills[i]["bytes"] for i in g),
                 "members": [skills[i]["path"] for i in g]}
                for g in groups
            ],
        }, indent=2))
        return 0

    print(f"skills found       : {len(skills)}")
    print(f"total bytes        : {total_bytes}")
    if dup_names:
        print(f"duplicate names    : {', '.join(dup_names)}")
    print(f"clusters (>= {args.threshold} description overlap): {len(groups)}")
    for g in groups:
        size = sum(skills[i]["bytes"] for i in g)
        print(f"\n  cluster of {len(g)}  ({size} bytes)")
        for i in g:
            print(f"    {skills[i]['path']}")
    if not groups:
        print("no clusters at this threshold")
    print("\nRead each cluster as one question; keep the skill that answers it best and")
    print("fold the rest into it. Check for skills present but disabled: dead weight.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Scan a directory for things that must not be published: artefacts, secrets, personal data.

Run this before committing to a public repository. It is a mechanical second opinion, not a
substitute for reading the file list.

Usage:
    repo_scrub.py --dir .                 # human report
    repo_scrub.py --dir . --json          # machine report
    repo_scrub.py --dir . --fail-on any   # exit non-zero on medium findings too

Severities:
    high   - private keys, credential-shaped strings, .env files
    medium - email addresses, home paths with a username, IP addresses, long blobs
    low    - build artefacts, caches, logs, databases, large binaries

Exit codes: 0 clean at the requested level, 3 findings, 2 bad input.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", "target"}

ARTEFACT_NAMES = {
    ".DS_Store": "macOS metadata",
    "Thumbs.db": "Windows metadata",
}
ARTEFACT_SUFFIXES = {
    ".pyc": "compiled Python",
    ".pyo": "compiled Python",
    ".log": "log file",
    ".sqlite": "database",
    ".db": "database",
    ".zip": "archive",
    ".tar": "archive",
    ".gz": "archive",
}

HIGH_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "cloud access key id"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "source-control token"),
    (re.compile(r"\bsk-[A-Za-z0-9]{24,}\b"), "API secret key"),
    (re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9/+_\-]{20,}"), "credential-shaped assignment"),
]
MEDIUM_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "email address"),
    (re.compile(r"/home/[a-z0-9._\-]+/"), "home directory path with username"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "IP address"),
    (re.compile(r"\b[A-Fa-f0-9]{40,}\b"), "long hex blob"),
]

TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml",
                 ".ini", ".cfg", ".html", ".css", ".sql", ".rb", ".go", ".rs", ".java", ""}
LARGE_BYTES = 1_000_000

# Reserved documentation domains (RFC 2606) exist to be written down. An address in one of
# them is an example, not personal data, so it must not raise a finding.
EXAMPLE_DOMAIN_RE = re.compile(
    r"@(?:example\.(?:com|org|net)|[A-Za-z0-9.\-]+\.(?:example|test|invalid))\b", re.I)


def scan(root: str):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        if "__pycache__" in dirpath.split(os.sep):
            findings.append({"path": rel_dir, "line": 0, "severity": "low",
                             "kind": "build artefact", "detail": "__pycache__ directory"})
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            size = os.path.getsize(path) if os.path.exists(path) else 0

            if name in ARTEFACT_NAMES:
                findings.append({"path": rel, "line": 0, "severity": "low",
                                 "kind": "build artefact", "detail": ARTEFACT_NAMES[name]})
            for suf, label in ARTEFACT_SUFFIXES.items():
                if name.endswith(suf):
                    findings.append({"path": rel, "line": 0, "severity": "low",
                                     "kind": "build artefact", "detail": label})
                    break
            if name == ".env" or name.startswith(".env."):
                findings.append({"path": rel, "line": 0, "severity": "high",
                                 "kind": "secret file", "detail": "environment file"})
            if size > LARGE_BYTES:
                findings.append({"path": rel, "line": 0, "severity": "low",
                                 "kind": "large file", "detail": f"{size} bytes"})

            if os.path.splitext(name)[1] not in TEXT_SUFFIXES:
                continue
            try:
                text = open(path, encoding="utf-8", errors="strict").read()
            except (OSError, UnicodeDecodeError):
                continue
            for n, line in enumerate(text.splitlines(), 1):
                for rx, label in HIGH_PATTERNS:
                    if rx.search(line):
                        findings.append({"path": rel, "line": n, "severity": "high",
                                         "kind": label, "detail": line.strip()[:120]})
                for rx, label in MEDIUM_PATTERNS:
                    if rx.search(line):
                        if label == "email address" and EXAMPLE_DOMAIN_RE.search(line):
                            continue
                        findings.append({"path": rel, "line": n, "severity": "medium",
                                         "kind": label, "detail": line.strip()[:120]})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", choices=["high", "medium", "any"], default="high")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"not a directory: {args.dir}", file=sys.stderr)
        return 2

    findings = scan(os.path.abspath(args.dir))
    order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["path"], f["line"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("high", "medium", "low")}

    if args.json:
        print(json.dumps({"dir": args.dir, "counts": counts, "findings": findings}, indent=2))
    else:
        print(f"scanned {args.dir}")
        print(f"high {counts['high']}  medium {counts['medium']}  low {counts['low']}")
        for f in findings:
            where = f"{f['path']}:{f['line']}" if f["line"] else f["path"]
            print(f"  [{f['severity']:6}] {where}  {f['kind']}: {f['detail']}")
        if not findings:
            print("nothing found - still read the file list yourself")

    bad = counts["high"] > 0 if args.fail_on == "high" else (
        (counts["high"] + counts["medium"]) > 0 if args.fail_on == "medium" else bool(findings))
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

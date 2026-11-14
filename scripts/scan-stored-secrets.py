#!/usr/bin/env python3
"""Read-only scanner for credentials stored as plaintext in an agent's state.

Walks the tree an agent maintains -- skills, memories, helper scripts,
reference docs, compiled caches, backups -- and reports high-precision secret
patterns with every value MASKED. Nothing is modified and a full secret is
never printed.

Notes
-----
* Transcript redaction is a display feature, not protection: a secret stored
  in a file is still in the file. This tool checks files.
* Compiled caches (``__pycache__/*.pyc``) are scanned as bytes, because string
  literals survive compilation; delete/rebuild caches after a sweep.
* Heuristics will occasionally flag placeholders and documented defaults.
  Review each finding before acting; do not auto-fix.
* Live session transcripts, logs and caches are excluded by default -- scan a
  specific ``--root`` if you suspect leakage there is worth reviewing.
* Exit status: 1 when findings exist (so a scheduler can notice), 0 when clean.

Usage
-----
    scan-stored-secrets.py [--root PATH] [--max-bytes N] [--quiet]

The default root is the Hermes home (``$HERMES_HOME``), falling back to
``~/.hermes`` and ``%LOCALAPPDATA%\\hermes``. Pass ``--root`` one or more times
to scan additional trees.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

TEXT_EXTS = {
    ".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".properties", ".xml", ".html", ".js", ".ts", ".sql",
}
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "site-packages",
    "sessions", "logs", "cache", "audio_cache",
    ".mypy_cache", ".pytest_cache",
}

# (label, pattern). Each pattern has exactly one capturing group: the secret.
PATTERNS: "list[tuple[str, re.Pattern]]" = [
    ("sshpass-literal", re.compile(r"sshpass\s+-p\s+'([^']+)'")),
    ("sshpass-literal", re.compile(r'sshpass\s+-p\s+"([^"]+)"')),
    ("key/secret assignment", re.compile(
        r"(?i)\b(?:password|passwd|passphrase|pwd|secret|api[_-]?key|apikey"
        r"|auth[_-]?token|access[_-]?token)\s*[:=]\s*['\"]([^'\"\s]{4,})['\"]")),
    ("password assignment (unquoted)", re.compile(
        r"(?i)\b(?:password|passwd|passphrase)\s*=\s*([^\s'\";#]{6,})")),
    ("chat-bot-token", re.compile(r"\b(\d{8,10}:[A-Za-z0-9_-]{30,})\b")),
    ("github-token", re.compile(r"\b((?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{30,})\b")),
    ("slack-token", re.compile(r"\b(xox[abprs]-[A-Za-z0-9-]{10,})\b")),
    ("openai-style-key", re.compile(r"\b(sk-[A-Za-z0-9]{20,})\b")),
    ("aws-access-key-id", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("jwt", re.compile(r"\b(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,})\b")),
    ("bearer-token", re.compile(r"(?i)authorization:\s*bearer\s+([A-Za-z0-9._-]{20,})")),
    ("activation-url", re.compile(r"[?&](?:hash|key|token)=([A-Za-z0-9]{16,})")),
]
BYTE_PATTERNS = [
    (label, re.compile(rx.pattern.encode("ascii")))
    for label, rx in PATTERNS
]


def mask(value: str) -> str:
    """Never reveal more than a hint of a value."""
    if len(value) <= 6:
        return f"\u00abmasked {len(value)}c\u00bb"
    return f"{value[:2]}\u2026\u00abmasked {len(value)}c\u00bb"


def default_roots() -> "list[Path]":
    candidates = []
    env = os.environ.get("HERMES_HOME")
    if env:
        candidates.append(Path(env))
    candidates.append(Path.home() / ".hermes")
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "hermes")
    for candidate in candidates:
        if candidate.is_dir():
            return [candidate]
    return [candidates[0]]


def walk_files(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS and "venv" not in d.lower()
            ]
            for name in filenames:
                yield Path(dirpath) / name


def scan_file(path: Path, max_bytes: int) -> "list[tuple[int, str, str]]":
    """Return (line, label, masked_value) tuples; line 0 means a byte scan."""
    try:
        if path.stat().st_size > max_bytes:
            return []
        raw = path.read_bytes()
    except OSError:
        return []

    findings = []
    if path.suffix.lower() == ".pyc":
        for label, rx in BYTE_PATTERNS:
            for match in rx.finditer(raw):
                value = match.group(1).decode("utf-8", "replace")
                findings.append((0, label, mask(value)))
        return findings

    if path.suffix.lower() not in TEXT_EXTS and path.name != ".env":
        return findings

    text = raw.decode("utf-8", "replace")
    for label, rx in PATTERNS:
        for match in rx.finditer(text):
            value = match.group(1)
            if value.startswith("$"):
                continue  # shell variable reference, not a stored secret
            line = text.count("\n", 0, match.start()) + 1
            findings.append((line, label, mask(value)))
    return findings


def normalize_root(raw) -> Path:
    """Accept MSYS/Cygwin-style paths (/c/Users/...) on Windows."""
    raw = str(raw)
    if os.name == "nt":
        match = re.match(r"^/([A-Za-z])/(.*)$", raw)
        if match:
            return Path(f"{match.group(1).upper()}:/{match.group(2)}")
    return Path(raw)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", action="append", type=str,
                        help="tree to scan (repeatable)")
    parser.add_argument("--max-bytes", type=int, default=2_000_000,
                        help="skip files larger than this (default 2 MB)")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the summary")
    args = parser.parse_args(argv)

    roots = [normalize_root(raw) for raw in (args.root or default_roots())]
    for root in roots:
        if not root.is_dir():
            print(f"error: not a directory: {root}", file=sys.stderr)
            return 2

    if not args.quiet:
        for root in roots:
            print(f"scanning: {root}")

    seen = set()
    total = 0
    for path in walk_files(roots):
        for line, label, value in scan_file(path, args.max_bytes):
            key = (str(path), line, label, value)
            if key in seen:
                continue
            seen.add(key)
            total += 1
            where = str(path) + (f":{line}" if line else " (compiled cache)")
            print(f"{where}: {label}: {value}")

    print(f"\n{total} finding(s) across {len(roots)} root(s).")
    if total and not args.quiet:
        print("Replace each with a reference to a real store; rescan until zero;")
        print("rotate any value that was ever committed, pushed or shared.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())

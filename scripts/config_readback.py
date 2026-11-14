#!/usr/bin/env python3
"""Read a configuration file the way the program reads it, and assert values.

Writing a setting is not the same as setting it. A value can be written in a
shape the loader reads differently (a list item with the wrong indent becomes
one long string; `true` and "true" are different types), and a settings command
may "save" a key the program never reads.

This parses the file with the same library the program uses, resolves each key,
prints the value it actually found, and fails if it is not what you intended.

Usage:
    config_readback.py --file config.yaml --expect model.default=flash-model
    config_readback.py --file config.yaml --expect skills.disabled='["a","b"]' \
                       --expect features.gate=true

Expected values are parsed as JSON when possible (so true/false/numbers/lists
compare by type); otherwise compared as strings.

Exit codes: 0 all expectations met, 1 mismatch, 2 unreadable file or bad input.
"""
from __future__ import annotations

import argparse
import json
import sys

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


def resolve(doc, path: str):
    node = doc
    for part in path.split("."):
        if isinstance(node, dict):
            if part not in node:
                return _MISSING
            node = node[part]
        elif isinstance(node, list) and part.isdigit():
            idx = int(part)
            if idx >= len(node):
                return _MISSING
            node = node[idx]
        else:
            return _MISSING
    return node


class _Missing:
    def __repr__(self) -> str:
        return "<missing>"


_MISSING = _Missing()


def parse_expected(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        low = raw.strip().lower()
        if low == "true":
            return True
        if low == "false":
            return False
        if low == "null":
            return None
        return raw


def suspicious_list_items(doc) -> list[str]:
    """Flag list entries that look like two items merged into one string."""
    problems = []

    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                if isinstance(v, str) and " - " in v:
                    problems.append(f"{path}[{i}] = {v!r}  (looks like two items merged)")
                walk(v, f"{path}[{i}]")

    walk(doc)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True)
    ap.add_argument("--expect", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if yaml is None:
        print("PyYAML is required: pip install pyyaml", file=sys.stderr)
        return 2
    try:
        doc = yaml.safe_load(open(args.file, encoding="utf-8"))
    except OSError as exc:
        print(f"cannot read {args.file}: {exc}", file=sys.stderr)
        return 2
    except yaml.YAMLError as exc:
        print(f"YAML did not parse: {exc}", file=sys.stderr)
        return 1
    if doc is None:
        print("file parsed as empty", file=sys.stderr)
        return 1

    results, failed = [], 0
    for spec in args.expect:
        if "=" not in spec:
            print(f"bad --expect {spec!r}: needs KEY=VALUE", file=sys.stderr)
            return 2
        key, raw = spec.split("=", 1)
        want = parse_expected(raw)
        got = resolve(doc, key.strip())
        ok = (got is not _MISSING) and (got == want) and (type(got) is type(want)
                                                          or isinstance(got, type(want)))
        if not ok:
            failed += 1
        results.append({"key": key.strip(), "want": want, "got": None if got is _MISSING else got,
                        "got_type": None if got is _MISSING else type(got).__name__,
                        "ok": ok})

    merged = suspicious_list_items(doc)

    if args.json:
        print(json.dumps({"file": args.file, "results": results,
                          "suspicious_list_items": merged}, indent=2))
    else:
        for r in results:
            mark = "PASS" if r["ok"] else "FAIL"
            print(f"{mark} {r['key']}: want {r['want']!r} got {r['got']!r} ({r['got_type']})")
        if merged:
            print("\nsuspicious list items:")
            for m in merged:
                print(f"  {m}")
        print(f"\n{failed} of {len(results)} expectations failed" if results else "no expectations given")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

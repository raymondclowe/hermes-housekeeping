#!/usr/bin/env bash
# hermes-checkup — read-only inventory of an agent's persistent state.
#
# Prints the numbers an audit needs: store sizes against their budgets, disabled
# capabilities, skills that exist on disk but not in the index, near-duplicate
# skills, retention vs recall, and stale locks. It changes nothing: no writes, no
# config edits, no privilege escalation. Safe to run before every housekeeping pass.
#
# Usage:  ./scripts/checkup.sh [HERMES_HOME]
# Works on Linux, macOS and git-bash on Windows.

set -u

# ---------- locate the agent home ----------
ROOT="${1:-${HERMES_HOME:-}}"
if [ -z "$ROOT" ]; then
  for cand in "$HOME/.hermes" "$HOME/AppData/Local/hermes" "$LOCALAPPDATA/hermes"; do
    [ -d "$cand" ] && ROOT="$cand" && break
  done
fi
[ -n "$ROOT" ] && [ -d "$ROOT" ] || { echo "usage: $0 <HERMES_HOME>   (could not find one automatically)" >&2; exit 2; }

PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
have() { command -v "$1" >/dev/null 2>&1; }
hr() { printf '%s\n' "------------------------------------------------------------"; }
chars() { wc -c < "$1" 2>/dev/null | tr -d ' \n'; }
entries() { grep -c '^§$' "$1" 2>/dev/null || echo 0; }

echo "hermes-checkup — read-only report"
echo "home: $ROOT"
have $PY || echo "note: no python found — some sections will be skipped"
hr

# ---------- 1. stores and budgets ----------
echo "1. Persistent stores"
CFG="$ROOT/config.yaml"
LIM_MEM=2200; LIM_USER=1375
# Prefer a python that can read YAML (the agent's own venv usually can); fall back to
# awk so the report still works on a bare interpreter.
PYY="$PY"
[ -x "$ROOT/hermes-agent/venv/Scripts/python" ] && PYY="$ROOT/hermes-agent/venv/Scripts/python"
[ -x "$ROOT/hermes-agent/venv/bin/python" ] && PYY="$ROOT/hermes-agent/venv/bin/python"
if [ -f "$CFG" ]; then
  eval "$(PYTHONWARNINGS=ignore $PYY - "$CFG" <<'PY' 2>/dev/null
import sys
try:
    import yaml
except Exception:
    sys.exit(0)
c = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
m = c.get("memory", {}) or {}
print("LIM_MEM=%d" % int(m.get("memory_char_limit", 2200)))
print("LIM_USER=%d" % int(m.get("user_char_limit", 1375)))
print("PROFILE_ENABLED=%s" % ("1" if m.get("user_profile_enabled") else "0"))
print("MEMORY_ENABLED=%s" % ("1" if m.get("memory_enabled") else "0"))
a = c.get("agent", {}) or {}
print("DISABLED='%s'" % ",".join(a.get("disabled_toolsets", []) or []))
comp = c.get("compression", {}) or {}
print("COMPRESSION=%s" % ("1" if comp.get("enabled") else "0"))
sr = c.get("session_reset", {}) or {}
print("RESET_MODE=%s" % (sr.get("mode", "none")))
PY
)"
  # awk fallback for hosts without PyYAML
  if [ -z "${RESET_MODE:-}" ]; then
    LIM_MEM=$(awk '/^memory:/{f=1} f&&/memory_char_limit:/{print $2; exit}' "$CFG" | tr -dc '0-9'); LIM_MEM=${LIM_MEM:-2200}
    LIM_USER=$(awk '/^memory:/{f=1} f&&/user_char_limit:/{print $2; exit}' "$CFG" | tr -dc '0-9'); LIM_USER=${LIM_USER:-1375}
    awk '/^memory:/{f=1} f&&/user_profile_enabled:/{print "PROFILE_ENABLED=" ($2=="true"?1:0); exit}' "$CFG"
    DISABLED=$(awk '/^ +disabled_toolsets:/{f=1; next} f&&/^ +- /{gsub(/^ +- /,""); printf "%s,", $0; next} f&&!/^ +- /{exit}' "$CFG" | sed 's/,$//')
    COMPRESSION=$(awk '/^compression:/{f=1} f&&/^ +enabled:/{print ($2=="true"?1:0); exit}' "$CFG")
    RESET_MODE=$(awk '/^session_reset:/{f=1} f&&/^ +mode:/{print $2; exit}' "$CFG")
  fi
fi
for pair in "MEMORY.md:$LIM_MEM" "USER.md:$LIM_USER"; do
  f="${pair%%:*}"; lim="${pair##*:}"
  p="$ROOT/memories/$f"
  if [ -f "$p" ]; then
    c=$(chars "$p"); pct=$(( c * 100 / lim ))
    printf '  %-10s %6s / %-6s chars  (%s%%)  entries: %s\n' "$f" "$c" "$lim" "$pct" "$(entries "$p")"
    [ "$pct" -ge 90 ] && echo "             ^ at or above 90%: treat as write-blocked"
  else
    printf '  %-10s MISSING\n' "$f"
  fi
done
[ "${PROFILE_ENABLED:-1}" = "0" ] && echo "  ! user profile disabled in config — USER.md can never exist"
[ "${MEMORY_ENABLED:-1}" = "0" ] && echo "  ! memory disabled in config"

for f in SOUL.md AGENTS.md .hermes.md CLAUDE.md; do
  [ -f "$ROOT/$f" ] && printf '  %-10s %6s chars (rules file, no budget)\n' "$f" "$(chars "$ROOT/$f")"
done
hr

# ---------- 2. capabilities ----------
echo "2. Capabilities"
[ -n "${DISABLED:-}" ] && echo "  disabled toolsets: $DISABLED" || echo "  disabled toolsets: (none found, or config unreadable)"
echo "  compression enabled: ${COMPRESSION:-?}   session reset mode: ${RESET_MODE:-?}"
hr

# ---------- 3. skills ----------
echo "3. Skills"
SK="$ROOT/skills"
if [ -d "$SK" ]; then
  find "$SK" -name SKILL.md -not -path "*/.archive/*" 2>/dev/null | sed "s|$SK/||; s|/SKILL.md||" | sort > /tmp/.hc_skills.$$
  total=$(wc -l < /tmp/.hc_skills.$$ | tr -d ' ')
  archived=$(find "$SK/.archive" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
  echo "  on disk: $total   archived: $archived"
  echo "  single-platform skills (hidden on any other host OS — check whether they manage remote machines):"
  grep -rlE '^platforms: *\[(linux|macos|windows)\] *$' "$SK" --include=SKILL.md 2>/dev/null \
    | grep -v '/\.archive/' \
    | sed "s|$SK/||; s|/SKILL.md||" | sed 's/^/    /' | head -20
  if have $PY; then
    PYTHONWARNINGS=ignore $PY - "$SK" <<'PY' 2>/dev/null
import os, re, sys, difflib
root = sys.argv[1]
items = []
for dirpath, dirnames, filenames in os.walk(root):
    if ".archive" in dirpath.split(os.sep):
        continue
    if "SKILL.md" in filenames:
        p = os.path.join(dirpath, "SKILL.md")
        try:
            head = open(p, encoding="utf-8", errors="replace").read(4000)
        except Exception:
            continue
        m = re.search(r"^description:\s*(.+)$", head, re.M)
        d = (m.group(1).strip().strip('"\'') if m else "")
        items.append((os.path.relpath(os.path.dirname(p), root), d))
print("  near-duplicate descriptions (>=0.60 similarity):")
found = False
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        a, b = items[i][1], items[j][1]
        if not a or not b:
            continue
        r = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
        if r >= 0.60:
            found = True
            print("    %.2f  %s  <->  %s" % (r, items[i][0], items[j][0]))
if not found:
    print("    none")
PY
  fi
  rm -f /tmp/.hc_skills.$$
else
  echo "  no skills directory"
fi
hr

# ---------- 4. history vs recall ----------
echo "4. History vs recall"
DB="$ROOT/state.db"
if [ -f "$DB" ]; then
  size=$(du -h "$DB" 2>/dev/null | cut -f1)
  echo "  state.db: ${size:-?}"
  q() { # $1 = sql; prefer python (has fts5), fall back to sqlite3
    if [ -n "${PYY:-}" ] && [ -x "$PYY" ] || have $PY; then
      PYTHONWARNINGS=ignore ${PYY:-$PY} - "$DB" "$1" <<'PY' 2>/dev/null
import sqlite3, sys
try:
    print(sqlite3.connect(sys.argv[1]).execute(sys.argv[2]).fetchone()[0])
except Exception:
    pass
PY
    elif have sqlite3; then
      sqlite3 "$DB" "$1" 2>/dev/null
    fi
  }
  echo "    sessions: $(q 'select count(*) from sessions;')"
  echo "    messages: $(q 'select count(*) from messages;')"
  fts=$(q 'select count(*) from messages_fts;')
  [ -n "$fts" ] && echo "    fts rows: $fts  (should match messages; a gap means the index lags)"
  [ -z "$fts" ] && echo "    fts rows: unavailable (sqlite client lacks FTS5 — use a python that has it)"
else
  echo "  no state.db found"
fi
case "${DISABLED:-}" in
  *session_search*) echo "  ! recall disabled while history is retained — history is unqueryable" ;;
esac
hr

# ---------- 5. stale locks and leftovers ----------
echo "5. Stale locks and leftovers"
found_lock=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  found_lock=1
  printf '  %s  (%s days old)\n' "${f#$ROOT/}" "$(( ( $(date +%s) - $(date -r "$f" +%s 2>/dev/null || echo 0) ) / 86400 ))"
done <<EOF
$(find "$ROOT" -maxdepth 1 -name "*.lock" -mtime +7 2>/dev/null)
EOF
[ "$found_lock" = "0" ] && echo "  none older than 7 days"
for f in "$ROOT"/.skills_prompt_snapshot.json; do
  [ -f "$f" ] && echo "  skills prompt snapshot present (compare it with the skills tree after any change)"
done
hr

echo "Done. This report is read-only — nothing was modified."
echo "Next: review findings, then follow remediation.md one approved edit at a time."

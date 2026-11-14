# Secret sweep: credentials stored in the agent's own state

## Human read this

Point your hermes at this file when you want its stored state swept for
credentials that leaked into it over time: passwords pasted into skills, tokens
baked into helper scripts, keys sitting in reference docs, backups and compiled
caches. This is a review-and-fix pass — findings first, ask before each edit.

## Hermes read this

Goal: find credentials stored as plaintext in the state you maintain, replace
them with references to a real store, and verify none remain.

Search your own surfaces by shape, not by memory:

- skill trees — `SKILL.md`, `references/`, `templates/`, `scripts/`, `assets/`
- memory and identity files, including any per-profile copies
- helper scripts and notes anywhere under the home directory you manage
- compiled caches beside scripts (`.pyc` / `__pycache__`) — string literals survive compilation
- backups and archives of any of the above (`.bak*`, `*.tar.gz`, retired-item dirs)
- regenerated artifacts that embed the old text (prompt snapshots, usage indexes)

What counts as a stored secret (extend for your own formats):

- shell password arguments — a password passed inline on a command line (the `sshpass -p <password>` pattern)
- `password` / `passwd` / `pwd` assignments and connection strings
- token shapes — chat-bot `digits:base64ish`; `ghp_` / `github_pat_`, `xox…`, `sk-…`, `AKIA…`, JWT `eyJ…`
- activation or registration URLs carrying `?hash=…` / `?key=…`
- anything that would let a reader log in as, act as, or spend as the operator

Rules:

1. **Never print a full value** anywhere — mask findings (leading characters
   only) in reports, diffs and chat alike.
2. **Transcript redaction is display, not protection.** A value hidden in
   output is still in the file. Sweep the file; after edits, rescan rather than
   trusting a redacted view.
3. **Replace with a reference, not another copy** — an environment variable the
   caller sources, or the owning service's own config on the machine that uses
   it. If no store exists yet, ask the operator where the value should live
   instead of inventing one.
4. **Sweep the derived copies too** — delete or rebuild compiled caches; scrub
   or explicitly flag archives and backups.
5. **Verify by rescanning for the exact literal** — every occurrence, including
   caches, must reach zero. Read-only helper: `scripts/scan-stored-secrets.py`
   (masks everything, exit code 1 on findings).
6. **If a found value was ever committed, pushed or shared, say so and
   recommend rotation.** Removing it from the files does not unshare it.
7. Report per file: what was found (masked), what replaced it, and what still
   holds the value and why.

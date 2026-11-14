# Applying a housekeeping change safely

The audit finds the problem; this is the part that goes wrong. Every change here
touches text or processes that are loaded automatically, so a half-landed change
is worse than no change: a stale copy keeps being obeyed, and a resurrected
service undoes the cleanup silently.

## Order of operations

1. **Freeze the current state.** Archive the always-loaded files, and require the
   archive to be readable before touching anything:

   ```bash
   stamp=$(date +%Y%m%d-%H%M%S); mkdir -p backups
   tar czf "backups/housekeeping-$stamp.tgz" \
       SOUL.md memories/MEMORY.md memories/USER.md config.yaml
   tar tzf "backups/housekeeping-$stamp.tgz" >/dev/null || { echo "backup failed - stop"; exit 1; }
   ```

   If the skills directory is a git repo, commit a baseline too — then every later
   step is diffable and revertible by hash.
2. **Measure before editing.** Sizes, entry counts, and — if there are caps —
   headroom. A cap is checked against the *final* state, so removals and
   additions belong in one batch, not two calls.
3. **Move before deleting.** Anything evicted from a capped store goes to an
   uncapped one (a facts database, a reference file, an archive directory).
   Deleting first loses the content that justified the entry.
4. **Edit one surface at a time, then re-read the file.** An edit that "succeeded"
   in a tool response is not evidence the file changed; read it back.
5. **Verify, then report.** A table of what was checked, what it returned, and
   what is still unverified.

## Editing an instruction surface

- **The always-loaded layers win by default.** A rule in the system block beats a
  rule in a skill, because the skill may never be loaded. Behavioural rules
  therefore belong in the always-loaded layer, and procedures belong in the skill
  for that procedure — never duplicated in both.
- **Retiring a rule means sweeping every copy.** A rule typically lives in the
  system block, memory, two or three skills, and a cron prompt. Retire it in all
  of them in one pass, or a later session obeys the survivor. `scripts/rule_sweep.py`
  lists the copies.
- **Rewrite, don't tombstone.** Text that says a practice was removed still
  teaches the practice.
- **Watch the size limit on skills.** A skill whose body exceeds the loader's
  practical limit is truncated when loaded: the top of the file arrives and the
  tail is silently missing. Split the body into `references/` with a thin index.

## Protecting what is in use

Bulk retirement is driven by name tokens or by a "stale" flag, and both are wrong
about the same skill: the one that is used every day but shares a word with the
retired project, or whose directory has not changed since it was written well.

Two mechanisms, both cheap:

- **A protected list beside the skills** — `skills/.protected.json`,
  `{"do_not_archive": ["name-a"]}`. It is the only place a name is allowed to
  override the usage counters, and it is edited by hand.
- **A usage gate before the move** — `scripts/skill_archive_guard.py` refuses any
  candidate that is protected, has more logged uses than a threshold, or was used
  in the last month:

  ```bash
  python3 scripts/skill_archive_guard.py --profile ~/.hermes --file candidates.txt
  python3 scripts/skill_archive_guard.py --profile ~/.hermes --audit-archive
  ```

  `--audit-archive` answers the question the guard cannot prevent: what is already
  in the archive that still looks live. Run it after every pass.

A refusal is information, not an obstacle. If the retirement is genuinely intended,
remove the name from the protected list deliberately and say so in the report — never
widen the threshold to get past it.

## Retiring a service or a whole project

Order is load-bearing.

1. **Find every launcher first**: cron lines, systemd units with `Restart=always`,
   tmux watchdogs, supervisor loops. The launcher is what undoes a kill.
2. **Retire the launcher, then the process.** Comment the cron line with a dated
   reason and the original line preserved — never delete it, it is the restore
   path.
3. **Kill by PID.** A name-pattern kill matches the shell running it and takes
   out the session that issued it. `pgrep -af <token>` to find, `kill <pid>` to act.
4. **Wait a minute, then look again.** Anything still alive was started by a line
   the first sweep missed; find its parent and grep the launcher list again.
5. **Archive the artefacts into one dated directory**, preserving relative paths,
   with a README that states what moved, what was stopped, and how to restore one
   of each.
6. **Say plainly that a same-filesystem move frees no space.** It is a rename.
   Compression or deletion is a separate, separately-approved decision.

## Verification table

| Layer | Pass looks like |
|---|---|
| text edited | re-read returns the new wording; the old wording is gone from every surface |
| sizes | reported before and after, against the cap |
| processes | the project's tokens are absent from the process list |
| supervisors | no session, no unit, no cron line can restart them |
| archives | every retired item present in the archive path; nothing in the live path |
| restore | one command or file path per layer, written into the report |

Report unverified items as unverified. "Should be fine" is not a check.

# Hermes housekeeping

## Human read this

Point your hermes at this repo.

Use these instructions to review Hermes's own persistent context and configuration for opportunities to make it clearer, smaller, and more consistent.

## Self-audit instructions: Hermes read this

Perform a housecleaning check-up of your own state. Read `MEMORY.md`, `USER.md`, the available skills list, and the configuration, including any profiles. If these items are stored in different locations or exposed through different interfaces, inspect the corresponding sources. Do not assume a file or setting exists if you cannot find it.

Review the materials for:

1. **Stale or repeated memory:** Identify entries that appear outdated, duplicated, or redundant. Explain why and suggest what could be trimmed; do not decide or remove entries yourself.
2. **Overlapping skills:** Identify skills with substantially overlapping purposes or instructions. Suggest which could be combined or trimmed, and explain the trade-off.
3. **Apparently conflicting rules:** First look for differences in scope, context, or conditions that could reconcile the rules. Treat an apparent conflict as missing scoping rather than a real disagreement unless the materials provide evidence otherwise. Suggest clarifying when each rule applies.
4. **Highest-impact improvement:** Recommend the single change that would help most. Rank the recommendations by expected impact, with the most impactful first, and briefly explain the ranking.

Base findings on the materials you actually reviewed. Refer to the relevant file, profile, skill, or entry so each recommendation can be checked. Clearly distinguish observations from assumptions, and mention any sources you could not access.

Do not change, delete, combine, or rewrite anything during the audit. Present findings and recommendations only. Ask for approval before making any edit, and ask separately before each individual edit; approval for one edit does not authorize another.

## What is in this repo

The audit above is the question. These are the parts that go wrong afterwards:
the diagnosis is usually right and the application is what breaks.

| File | Use it when |
|---|---|
| `docs/where-a-rule-lives.md` | deciding which surface a new rule belongs on; the three-way split (behaviour, procedure, fact) and the cap mechanics |
| `docs/audit-report-template.md` | writing the audit up: findings with provenance, conflicts table, what was not checked, what was left alone |
| `docs/reconciling-conflicting-rules.md` | two rules look contradictory; gives the four missing-scope axes, a precedence sentence, worked examples and the anti-patterns |
| `docs/applying-a-cleanup-safely.md` | you are about to edit an always-loaded surface, retire a rule, or stop a service; gives the ordering, the verification table and the restore requirements |
| `scripts/surface_audit.py` | first pass: sizes and entry counts per surface, skills over the loader limit, duplicate skill descriptions |
| `scripts/rule_sweep.py` | before editing any standing rule: every surface that carries it, live and archived, with tombstones marked |
| `scripts/memory_trim.py` | near-duplicate entries, stale markers, and facts sitting in a capped behavioural file |
| `scripts/cron_orphans.py` | scheduled jobs that point at paths which no longer exist — they fail silently forever |

The scripts are read-only, standard-library only, and take `--profile` (default `$HERMES_HOME` or `~/.hermes`). CI runs all four against `tests/fixture/` on every pull request, and asserts they write nothing.

```bash
python3 scripts/surface_audit.py --profile ~/.hermes
python3 scripts/rule_sweep.py "dry run" --profile ~/.hermes
python3 scripts/memory_trim.py --file ~/.hermes/memories/MEMORY.md
python3 scripts/cron_orphans.py
```

## House rules this repo is built around

- **Stop and archive; never delete.** A retirement that cannot be reversed is not finished.
- **A finding without a file and line is a rumour.** Quote the source.
- **An audit changes nothing.** Recommendations first, and one approval per edit.
- **A same-filesystem move frees no space.** Say so rather than implying a cleanup saved disk.
- **A rule usually exists in three places.** Retiring it in one of them changes nothing.
- **Verify by exercising, then report what the exercise returned.** A tool call that returned success is not evidence the thing works.

## Contributing

Anything here should stay generic: no hostnames, no account names, no credentials, and no personal data from any one installation. Examples are described by shape ("the answer opens the reply"), not by quoting a private profile.

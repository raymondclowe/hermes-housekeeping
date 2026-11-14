# Hermes housekeeping

## Human read this

Hermes works badly the first week as it has not learnt you, great the second week as now it knows you and your processes, then after a while it peaks and degrades.

It needs a housekeeping run to remove crud.  This is it.

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

## Further follow-ups

Review is half the job; these cover follow-ups an audit usually produces that the material above does not.

- `docs/secret-sweep.md` — find credentials stored as plaintext anywhere in the state you maintain (skills, scripts, references, compiled caches, backups); replace them with references to a real store, verify none remain, and rotate anything that was ever committed or shared. Helper: `scripts/scan-stored-secrets.py` — read-only, masks every value, exit code 1 on findings.
- `docs/health-checks.md` — a periodic check that stays quiet while everything is fine and cannot silently die itself: which failure classes to cover, probe design, the re-alert cadence, and testing the alert path end to end.
- `docs/retirement-records.md` — retire things so they stay retired: keep an explicit record of removals, treat discovery as reachability rather than authority, scope "never drop a member" rules with an operator exception, and verify the re-adder does not bring them back.

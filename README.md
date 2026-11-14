# Hermes housekeeping

## Human read this

Hermes works badly the first week as it has not learnt you, great the second week as now it knows you and your processes, then after a while it peaks and degrades.

It needs a housekeeping run to remove crud.  This is it.

Point your hermes at this repo.

Use these instructions to review Hermes's own persistent context and configuration for opportunities to make it clearer, smaller, and more consistent.

## What is in here

| File | Use it when |
|---|---|
| `README.md` (this file) | You want the audit: read your own state, report, change nothing. |
| `remediation.md` | The audit is approved and you are about to change things. Order of work, per-edit approval, verification that the change actually loaded. |
| `scope-axes.md` | The audit found "conflicting" rules. Nine axes that explain why they only look contradictory, and the scope clause that reconciles each. |
| `config-checks.md` | You want the configuration half: capabilities that make a written rule impossible to follow, budgets, retention, hidden skills. |
| `scripts/checkup.sh` | Run first, on any host, before every pass. Read-only: prints the numbers the report needs. |

## How often

- **First fortnight: weekly.** The state grows fastest while it is still learning.
- **Then monthly**, or on any of these symptoms: the memory store is near its character limit; the skill count only ever rises; the same fact keeps being re-derived by hand; two skills answer the same request; a rule gets quoted that the configuration no longer supports.
- **Before and after any configuration change**, because rules silently outlive the settings they were written for.

The script is the cheap trigger: run `scripts/checkup.sh` and look at the percentages and counts, not the prose.

## Self-audit instructions: Hermes read this

Perform a housecleaning check-up of your own state. Read `MEMORY.md`, `USER.md`, the available skills list, and the configuration, including any profiles. If these items are stored in different locations or exposed through different interfaces, inspect the corresponding sources. Do not assume a file or setting exists if you cannot find it.

Review the materials for:

1. **Stale or repeated memory:** Identify entries that appear outdated, duplicated, or redundant. Explain why and suggest what could be trimmed; do not decide or remove entries yourself.
2. **Overlapping skills:** Identify skills with substantially overlapping purposes or instructions. Suggest which could be combined or trimmed, and explain the trade-off.
3. **Apparently conflicting rules:** First look for differences in scope, context, or conditions that could reconcile the rules. Treat an apparent conflict as missing scoping rather than a real disagreement unless the materials provide evidence otherwise. Suggest clarifying when each rule applies.
4. **Highest-impact improvement:** Recommend the single change that would help most. Rank the recommendations by expected impact, with the most impactful first, and briefly explain the ranking.

Base findings on the materials you actually reviewed. Refer to the relevant file, profile, skill, or entry so each recommendation can be checked. Clearly distinguish observations from assumptions, and mention any sources you could not access.

Do not change, delete, combine, or rewrite anything during the audit. Present findings and recommendations only. Ask for approval before making any edit, and ask separately before each individual edit; approval for one edit does not authorize another.

## Two rules that make the audit sharper

**Measure, don't infer.** Absolute numbers beat adjectives: characters used against the configured limit, entries per store, skills on disk against skills listed, sessions retained against sessions searchable. An auditor who reports "memory feels full" is guessing; one who reports "71% of a 2200-character budget, 6 entries, one of them a duplicate of a rule in the rules file" is not.

**A file that cannot exist is a finding.** If a store is disabled in configuration, or a skill is filtered out by a platform declaration, say so explicitly — an audit that reports "the file is empty" has missed the actual defect, and the same lesson will be written again by an agent that could not see the original.

## After the audit

The audit's value comes from changing nothing; the remediation's value comes from doing the changes in a safe order. When the report is approved, continue with `remediation.md` — one approved edit at a time, verification included, and an honest note that the editing session keeps the old state in context until the next session starts.

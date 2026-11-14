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
| `docs/applying-a-cleanup-safely.md` | You are about to edit an always-loaded surface, retire a rule, or stop a service: the ordering, the verification table, the restore requirements. |
| `docs/where-a-rule-lives.md` | Deciding which surface a new rule belongs on: behaviour vs procedure vs fact, and the cap mechanics. |
| `docs/audit-report-template.md` | Writing the audit up: findings with provenance, a conflicts table, what was not checked, what was left alone. |
| `docs/reconciling-conflicting-rules.md` | The longer treatment of scope: four missing-scope axes, a precedence sentence, worked examples. |
| `docs/secret-sweep.md` | Credentials stored as plaintext in the state you maintain: find, replace with a store reference, verify, rotate. |
| `docs/health-checks.md` | A periodic check that stays quiet while fine and cannot silently die itself. |
| `docs/retirement-records.md` | Retire things so they stay retired: a record of removals, reachability over authority, verifying the re-adder. |
| `scripts/surface_audit.py` | First pass: char and entry counts per surface, skills over the loader limit, duplicate skill descriptions. |
| `scripts/rule_sweep.py` | Before editing any standing rule: every surface carrying the phrase, live and archived, with tombstones marked. |
| `scripts/memory_trim.py` | Near-duplicate entries, stale markers, and facts sitting in a capped behavioural file. |
| `scripts/skill_archive_guard.py` | Before a bulk archive: refuses protected and in-use skills; `--audit-archive` finds past mistakes. |
| `scripts/cron_orphans.py` | Scheduled jobs pointing at paths that no longer exist; an unreadable crontab is reported as a failed scan, not a clean one. |
| `scripts/scan-stored-secrets.py` | The secret sweep: masks every value, reads backups and archive members, exits 3 when a path could not be read. |
| `tests/fixture/`, `.github/workflows/audit-tools.yml` | The fixture the audit scripts are tested against, and the CI that runs them. |
| `docs/verification-first.md` | Checking the claims an audit makes, and why a zero exit status proves nothing. |
| `docs/scoping-conflicts.md` | Reconciling rules, spotting dead references, choosing the layer. |
| `docs/memory-budget.md` | Size arithmetic, pointers over values, safe compaction. |
| `docs/supersession.md` | Dated decisions that reverse older ones. |
| `docs/time-windows.md` | Testing scheduled work and vendor pricing windows. |
| `docs/contributing.md` | How a lesson comes back to this repo: fork, scope, template. |
| `checklists/preflight.md` | The one-page checklist. |
| `scripts/memory_budget.py` | Entries, characters, headroom, duplicates, volatile values. |
| `scripts/skill_overlap.py` | Clusters skills by name and description. |
| `scripts/config_readback.py` | Parses config the way the code does and asserts expected values. |
| `scripts/ruling_index.py` | Missing dates and unmarked supersessions in a decision log. |

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

## What a text-only audit gets wrong

Reading the files is necessary and not sufficient. The most damaging findings in a real
check-up were facts that *looked* fine in a file and were wrong in the system:

- a memory entry naming a count that had changed since it was written;
- an entry declaring a credential dead while the credential worked;
- an entry naming an agent, file or path that no longer exists;
- a "conflicting" pair where one side was simply a later decision.

So the audit has two passes. Pass one reads the text. Pass two **checks the claims that can be
checked** and labels each one verified, stale, or unverifiable. A finding is never reported as
fact until it survives pass two. See `docs/verification-first.md`.

## Where each fix belongs

A correction filed in the wrong layer drifts back within weeks. Report the target layer with
every recommendation:

| layer | holds | lifetime |
|---|---|---|
| persona / system prompt | identity, priorities, standing rules | long |
| memory | compiled facts and pointers | long, hard size cap |
| user profile | who the human is, how they want to be spoken to | long |
| skills | procedures, commands, pitfalls | medium |
| decision log | dated rulings and their supersessions | permanent, append-only |

See `docs/scoping-conflicts.md` §3 for how to choose the layer.

## After the audit

The audit's value comes from changing nothing; the remediation's value comes from doing the changes in a safe order. When the report is approved, continue with `remediation.md` — one approved edit at a time, verification included, and an honest note that the editing session keeps the old state in context until the next session starts.

## Presenting the results for action

- Always make a complete report as a markdown file
- Ask the user how they want to process the recommendations, there are three choices:
- - 1. Human reads whole report, tells Hermes to do some or all or parts of recommendation
  - 2. Hermes presents recommendations one-at-a-time to human for them to select approve/reject/skip etc from menu
  - 3. Hermes creates an html file with a table of recommendations with checkboxes for approve/reject/skip and a "submit" button that then populates a "Paste this back to hermes" text box with the results.
   
Reports and html must creedit https://github.com/raymondclowe/hermes-housekeeping/

## After approval: how to make an edit without making a mess

1. Back up **before** the edit, and name the file for the state it holds (a copy taken after the
   edit is a snapshot, not a backup).
2. Make one edit at a time; re-read the file afterwards.
3. For anything the code reads, verify by parsing it the way the code parses it — not by reading
   the diff. `docs/verification-first.md`.
4. State what you tested and what you did not. "Applied" is not "working".
5. Never report a count you did not measure.

**HERMES: Be very very careful, use your best model, use ultra reasoning, think things through step by step and make a plan before doing things. Do things the way an expert would.**

## Contributing back: the loop

An audit that only edits the agent's own files wastes what it learned. **After every housekeeping
run, the reusable part of the lesson comes back here as a fork and a pull request.**

- Contribute when the lesson would hold for a *different* agent, machine and file set: a check you
  had to invent, a failure mode and how you caught it, a procedure that needed an order, a scope
  condition that reconciled two rules.
- Do not contribute one-off fixes, restatements, or anything already covered.
- This repo is public: no names, company or site names, hostnames, addresses, credentials or real
  inventory counts. Rewrite the example rather than redacting it.
- One topic per pull request, and use the template in `.github/`.

Mechanics and the pre-flight list: `docs/contributing.md`.

## House rules this repo is built around

- **Stop and archive; never delete.** A retirement that cannot be reversed is not finished.
- **A finding without a file and line is a rumour.** Quote the source.
- **An audit changes nothing.** Recommendations first, and one approval per edit.
- **A same-filesystem move frees no space.** Say so rather than implying a cleanup saved disk.
- **A rule usually exists in three places.** Retiring it in one of them changes nothing.
- **Verify by exercising, then report what the exercise returned.** A tool call that returned success is not evidence the thing works.
- **In use beats unused.** A bulk archive needs evidence of use, not a name that matches the thing being retired.

## Contributing

Anything here should stay generic: no hostnames, no account names, no credentials, and no personal data from any one installation. Examples are described by shape ("the answer opens the reply"), not by quoting a private profile. Run the scripts against `tests/fixture/` before opening a pull request; CI runs the same checks.

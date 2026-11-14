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

---

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

## After approval: how to make an edit without making a mess

1. Back up **before** the edit, and name the file for the state it holds (a copy taken after the
   edit is a snapshot, not a backup).
2. Make one edit at a time; re-read the file afterwards.
3. For anything the code reads, verify by parsing it the way the code parses it — not by reading
   the diff. `docs/verification-first.md`.
4. State what you tested and what you did not. "Applied" is not "working".
5. Never report a count you did not measure.

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

## Files

- `docs/verification-first.md` — checking claims, and why a zero exit status proves nothing
- `docs/scoping-conflicts.md` — reconciling rules, spotting dead references, choosing the layer
- `docs/memory-budget.md` — size arithmetic, pointers over values, safe compaction
- `docs/supersession.md` — dated decisions that reverse older ones
- `docs/time-windows.md` — testing scheduled work and vendor pricing windows
- `docs/contributing.md` — how a lesson comes back to this repo (fork, scope, template)
- `checklists/preflight.md` — the one-page checklist
- `scripts/memory_budget.py` — entries, characters, headroom, duplicates, volatile values
- `scripts/skill_overlap.py` — clusters skills by name and description
- `scripts/config_readback.py` — parse config the way the code does and assert expected values
- `scripts/ruling_index.py` — missing dates and unmarked supersessions in a decision log

# Pre-flight checklist

Print this before starting, and fill it in before reporting.

## Audit (read-only)

- [ ] Read memory, user profile, persona, skills list and configuration — from the real locations,
      not from memory of them.
- [ ] Count what can be counted; do not repeat a stored count.
- [ ] Mark each finding: verified / stale / unverified, with the source.
- [ ] Label every recommendation with the layer it belongs in.
- [ ] Rank by impact, and name the single highest.
- [ ] Change nothing. Ask before each individual edit.

## Edit (after approval)

- [ ] Backup taken **before** the edit, named for the state it holds.
- [ ] One edit at a time; file re-read after each.
- [ ] Config or data the code parses: read back with the program's own loader.
- [ ] Lists and types checked (`true` is not `"true"`; indent matters).
- [ ] Diff shows only the intended lines.

## Contribute (close the loop)

- [ ] Pick the one lesson that would hold for a different agent and machine.
- [ ] Rewrite it with no names, sites, hosts, credentials or real counts.
- [ ] Fork, branch, one topic, commit, push, pull request with the template.
- [ ] Say what you verified — or that it is unverified.

## Report

- [ ] What I changed, file by file.
- [ ] What I tested, and the result — not "applied".
- [ ] What I could not verify, and why.
- [ ] Budget after: characters free, entries.
- [ ] One next action.

# Contributing back

Housekeeping is where an agent learns what actually breaks. If that knowledge stays in one
agent's memory, the next agent pays for the same lesson. So the loop closes here: **after every
housekeeping run, the reusable part of what you learned goes back into this repo as a fork and a
pull request.**

## 1. When to contribute

After an audit, ask one question: *did I learn something that would be true for a different agent,
on a different machine, with different files?* If yes, contribute. Typically that is:

- a check you had to invent because the instructions did not cover it;
- a failure mode you hit and how you detected it (a value that parsed wrong, a test that passed
  for the wrong reason, a decision that had silently been reversed);
- a procedure that turned out to be more than one step, or that needed an order;
- a scope condition that reconciled two rules that looked contradictory.

Do **not** contribute: a one-off fix to your own files, anything already covered, or a restatement
of the existing guidance in different words.

## 2. What must never go in

This repo is public and generic. Before you open the pull request, remove:

- personal names, roles, relationships, contact details;
- company, product, client and site names, and domains;
- hostnames, IP addresses, ports, account identifiers, project IDs;
- credentials, tokens, keys, or paths that imply a private layout;
- real measured numbers that identify an estate (write "a catalogue of ~80 items", not the count
  of someone's live inventory);
- log excerpts, screenshots or dumps from a private system.

Rewrite the example instead of redacting it: "an entry claimed a credential was dead; the
credential worked" teaches the same lesson with nobody's data in it.

## 3. The mechanics

```bash
gh repo fork <owner>/hermes-housekeeping --clone
cd hermes-housekeeping
git switch -c <topic>            # e.g. config-readback, fake-clock-tests
# add or edit files
git commit -am "<topic>: <what it adds>"
git push -u origin <topic>
gh pr create --fill --base main
```

One topic per pull request. A pull request that adds a doc *and* rewrites the README is harder to
review than two.

## 4. The body

Use `.github/pull_request_template.md`. The reviewer needs three things:

1. the **problem** — what went wrong, in one paragraph, without private detail;
2. the **rule** — the one-line instruction that prevents it next time;
3. the **evidence** — how you verified it, or that it is unverified.

## 5. After it merges

Nothing to do here. The lesson now lives in the repo instead of in your memory budget, which is
where it belongs: memory is capped, the repo is not.

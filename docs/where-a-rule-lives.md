# Where a rule lives

Most housekeeping damage comes from putting a rule on the wrong surface. A rule on
the wrong surface is either invisible when it matters or always loaded when it
never matters — and both look like the agent ignoring it.

## Three kinds of content, three homes

| Kind | Example shape | Home | Why |
|---|---|---|---|
| Behaviour towards the user | "the answer opens the reply", "never type a credential" | always-loaded block (system prompt, memory, user profile) | must apply on every turn, including the turn where no skill is relevant |
| How to do a particular procedure | "how to decommission a service", "how to review a dashboard" | the skill for that procedure | loaded when the procedure is triggered; costs nothing otherwise |
| A fact about the world or the environment | "the staging box runs on port 8100", "the API needs the v2 endpoint" | uncapped fact store or an archive file | grows without limit, retrieved only when asked for |

The test that separates the first two: **would it be wrong for this rule to be
absent on a turn where the relevant skill was not loaded?** If yes, it is
behaviour and belongs in the always-loaded block. If it only matters while doing
that procedure, it belongs in the skill.

The test that separates the second from the third: **can it be written as an
instruction?** "Check the port before assuming the service is down" is a
procedure. "The port is 8100" is a fact.

## Why duplication is the default failure

A rule is usually added by editing whatever file the session happens to have
open, so the same sentence accumulates in two or three places with slightly
different wording. The copies drift. Later, one is retired and the others are
not, and a session obeys the survivor.

Two practical consequences:

- **Add a rule in exactly one place.** If the place is not obvious, the rule is
  not yet understood well enough to write.
- **Retire a rule by sweeping, not by editing.** `scripts/rule_sweep.py` lists
  every surface that carries the phrase, live and archived.

## Capped surfaces: the mechanics that surprise people

- **The cap is checked on the final state, not per operation.** One batch that
  removes three entries and adds one can fit where an add alone would be rejected.
- **Move before delete.** Evict to the uncapped store first; the deletion is only
  the last step.
- **A cap makes everything else compete.** Every permanently-relevant behaviour
  rule added costs the space of a fact that could have been stored. That trade is
  the reason the three-way split matters.
- **A snapshot in the system prompt is still a copy.** It can be stale on the turn
  it is read; the file on disk is the source.

## What belongs nowhere

- **A rule that restates the tool's own behaviour.** If the tool refuses, the rule
  is noise.
- **A warning about a tool you no longer use.** Retire it; a tombstone still
  teaches the practice.
- **A preference with no decision behind it.** "Prefer X" where X and Y are
  equivalent just creates a coin flip to argue with.

## Checklist before adding a rule

- [ ] classified: behaviour, procedure, or fact
- [ ] written on exactly one surface
- [ ] phrased as an instruction if it is behaviour or procedure
- [ ] says when it does NOT apply, if a reader could plausibly over-apply it
- [ ] fits the cap, after evicting something rather than truncating the new rule

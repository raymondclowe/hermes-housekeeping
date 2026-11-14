# Configured is not effective

The most expensive audit failure is not a wrong fact. It is a **true fact about a setting that does
not reach behaviour**: the flag says enabled, the file says checked, and the system does neither.

## 1. The same key name can live in two places

Layered configuration means one logical setting can be present in several files, and different
components read different ones. A settings command often prints a summary of *one* layer and
happily reports the other as unset.

So:

- never conclude "not configured" from a settings summary;
- grep the actual files for the key name, and say which file you read;
- then prove which layer the running component reads, by observation: change one layer, perform
  the smallest action that would reveal a difference, and watch.

A key present in one layer and absent in another is not an error — it is a precedence question.
Report it as precedence ("the runtime reads layer A; the tool reports layer B"), never as a single
true/false.

## 2. A flag is not an effect

Three shapes recur, and each one can be "on" while nothing happens:

| shape | how it looks | how it fails |
|---|---|---|
| per-item flag, master switch | 20 items flagged `true`, master `false` | nothing happens; the flags look thorough |
| tri-state | `false` / `dry_run` / `true` | `dry_run` looks like work in a log, changes nothing |
| enabled but paused | item `enabled: true`, `state: paused` | scheduling and execution disagree |

Test the end-to-end effect once, with one item, and read the artefact (a started job, a changed
file, a held queue) rather than the flag.

## 3. The audit questions

For every guard, gate, job, skill or scheduled task in the review, ask:

1. **What must be true for this to act?** Enumerate every switch in the chain, not just the last one.
2. **Who reads it, and from where?** Name the file and the component.
3. **Has anyone observed it acting?** A log line, a queue entry, a produced artefact — dated.
4. **What does it do when the switch is off?** Hold, drop, or silently do nothing — three different
   outcomes that look identical from the flag.

## 4. Report both numbers

"Configured X, effective Y" is the only honest form. When the two differ, that *is* the finding —
usually the highest-impact one in the review, because everything downstream was planned on the
assumption that the flag worked.

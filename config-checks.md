# Configuration checks the audit should run

Behaviour rules are only half of an agent's persistent state. The other half is configuration, where a single
disabled feature can make a written instruction impossible to follow — and nothing in the rules files will ever
show that. These checks are read-only; each finding states the symptom and the decision it forces.

---

## 1. Disabled toolsets vs the instructions that assume them

Enumerate the disabled toolsets and cross-check them against the rules and skills:

- A recall/search toolset disabled while the memory store is character-capped is the classic inversion: unlimited
  history on disk, kilobytes of usable memory, and no way to query the history. Every "what did we do about X" is
  then re-derived by hand or answered from a stale note.
- Web or search toolsets disabled while skills assume live lookup: the skills are not wrong, they are unreachable.
- A vision/image toolset disabled while the primary diagnostic channel is a screenshot a human posts.
- Delegation closed while skills advise handing work to peer agents.

**Decision forced:** either re-enable the toolset, or amend every rule and skill that assumes it. Leaving both is
the state that produces confident-but-stale answers.

## 2. A user profile that cannot exist

If the profile flag is off, the user-profile file will never be created, and an audit instruction to "read the user
profile" is asking for a file that cannot be there. That is a structural absence, not an empty file. It also means
identity and preference facts have nowhere to go and accumulate in the agent's own memory store instead.

**Decision forced:** enable the profile and populate it, or stop asking for it and accept that preferences live in
memory.

## 3. Character budgets as a failure mode

Compute each store's used-vs-limit percentage. Over roughly 90%, the store behaves as write-blocked: the next useful
fact is rejected, or evicts something better, and the pressure is invisible in the report unless you measure it.

**Decision forced:** raise the limit deliberately, or consolidate entries until there is real headroom. "It fits
today" is not a budget.

## 4. Retention vs recall

Look at the pair: is conversation history kept indefinitely, is compression on, and is history queryable? Keeping
everything, compressing nothing, and querying nothing is the worst of the three — storage cost with none of the
benefit. Report the pair together, never one alone.

## 5. Skills hidden by platform filters

A skill that declares a single platform is filtered out of the index on any other platform. On a host that manages
**remote** machines, this hides exactly the skills the machine most needs — and the observable result is the same
lesson written again, slightly differently, by an agent that could not see the original.

**Decision forced:** drop the platform declaration from anything usable against a remote host, or accept that
duplicate skills will keep appearing.

## 6. Skills on disk that the index does not show

Count skill files on disk (excluding archive directories) and compare with the count actually listed. Any
difference is either a filter (previous check) or a broken front-matter block. Report the names, not just the count.

## 7. Duplicate and near-duplicate skills

Group skills by trigger, not by name. Two reliable signals:

- two or more skills whose descriptions would answer the same user sentence;
- a burst of skills sharing the same creation timestamp and narrow topic — the same lesson learned repeatedly
  because the earlier copy was unloadable.

Recommend which survives and what the merged skill keeps, with the trade-off: merging reduces index size and
ambiguity, at the cost of one long skill that has to be maintained as one file.

## 8. Stale locks and orphaned state

Look for lock files in the agent's home directory older than a few days (`*.lock`), snapshot files that no longer
match the skills tree, and backup files from half-finished migrations. A stale lock can silently stop a rebuild that
depends on it.

## 9. Rules layered over a changed configuration

Configuration changes over time; rules do not follow. After any toolset change, re-read the rules file for
instructions phrased around the old state ("never use the browser", "always search", "ask the user to run…"). Each
one is a rule that has quietly become a lie.

---

## Reporting format

For each check: what was measured (the number), what it implies, and the one decision it forces. Distinguish what
was verified from what was inferred — a filter explained by a platform declaration is a hypothesis until a count
proves it.

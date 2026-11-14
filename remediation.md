# Phase 2 — the remediation pass

The audit tells you what is wrong. This file is the second run: what to change, in what order, and how to prove
the change actually took effect. It is deliberately separate from the audit because the audit's value depends on
changing nothing, and the remediation's value depends on doing it in a safe order.

Run it only after the audit report has been reviewed and approved.

---

## Approval discipline

Approval is per edit, not per session. "Apply all" is a legitimate blanket approval only if the report already
enumerated each change and its target file — record the enumeration in the PR/commit message so the scope is
checkable afterwards.

Never bundle a rewrite of a store with a rewrite of behaviour rules: if the result degrades, you need to know which
half did it.

## Back up before touching anything

Copy each store to a timestamped sibling (`MEMORY.md.bak-YYYYMMDD`, `SOUL.md.bak-YYYYMMDD`, `config.yaml.bak-…`).
A one-line backup has saved more sessions than any clever diff. Note the backups in the final report; nobody will
find them later otherwise.

## Order of work

The order matters because later steps verify earlier ones.

1. **Memory store.** Trim stale entries, delete duplicates of rules that live in the rules file, convert procedures
   into either a skill or a one-line environment fact, drop pointer entries. Target: comfortably under the character
   limit, not "just under" — a store at 90%+ is functionally write-blocked, and the next useful fact gets rejected
   or evicts something better.
2. **Rules file.** Add the scope clauses (see `scope-axes.md`), one section per axis. Keep the persona paragraph and
   the existing hard rules; re-point them at the new classes rather than deleting their wording.
3. **User-profile store.** If it is disabled in configuration, enabling it is its own decision — the audit should
   have flagged the structural absence, not just an empty file. Write identity and preferences only; anything
   inferred must be labelled as inferred in the file itself.
4. **Skills.** Annotate the skills that were being truncated or overridden ("output class: …"), and add entry
   signatures where two skills claim one trigger. Do not restructure or merge skills in the same pass as a rule
   change.
5. **Configuration.** Settings that make an instruction impossible — see `config-checks.md`. Change one key at a
   time and re-parse the file after each.

## Deduplicate before you rewrite

Before writing anything, count how many times each rule already exists across stores. A rule present in both the
memory store and the rules file is the single most common cause of "the agent contradicts itself": two copies, two
edits, then drift. Decide the owner of each rule, and delete the other copy in the same pass — leaving both is
worse than either.

## Verification (do not skip)

A change to persistent context is not done until a *fresh* session proves it loaded.

- **Counts.** Print character counts against the configured limits and entry counts, before and after.
- **Parse.** Re-read configuration and confirm it parses; confirm the specific key changed.
- **Live load.** Start a new one-shot session and ask it to paraphrase what it can see — the rules file and the
  user profile are in its context, not just on disk. If it cannot see the profile block, the enable did not take.
- **Freshness caveat.** The session that made the edits keeps the pre-edit copy in its context (prompt caching).
  Say so explicitly instead of claiming the new rules are already in force; they apply from the next session.

## What to report back

What changed (per store, with counts), what is verified and by which command, what is left open, and the paths of
the backups. Keep it to the shape of a work report, not a narrative of the process.

## Anti-patterns this pass exists to remove

- The same lesson written three times because none of the copies was loadable.
- A procedure stored where a fact belongs, so it is re-read on every turn and still not followed.
- A pointer entry that says "see skill X" once skill X exists and is indexed.
- Environment facts crammed into a character-capped store while an uncapped one sits disabled.
- Rules restated in two stores, approved once, edited twice.
- An audit that ends at a list, with the cheap fixes still sitting in the report a month later.

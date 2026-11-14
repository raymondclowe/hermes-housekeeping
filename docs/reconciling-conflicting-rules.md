# Reconciling apparently conflicting rules

An instruction stack accumulates rules from several hands over months. Two rules
that look contradictory are usually both correct and simply unqualified: each was
written for a situation that is not named in the text. The repair is to add the
missing scope, not to delete the rule that lost the argument.

Only two kinds of clash are genuine and need a decision rather than a clause:

- a rule that authorises what another rule forbids outright (credential handling,
  destructive commands);
- two rules that would produce opposite actions on the same input at the same
  moment.

Everything else is a scoping defect.

## Method

1. **Collect verbatim, with provenance.** Quote each rule and its file and line.
   A paraphrase hides the missing qualifier — the qualifier is usually what
   distinguishes the two.
2. **Classify the missing axis.** Nearly every clash misses one of four:
   - **phase** — deciding vs doing; first draft vs correction.
   - **artefact** — what is ingested vs what is reported; source vs summary.
   - **actor** — the agent's own proposal vs a command a procedure specifies.
   - **population** — one measured item vs an aggregate.
3. **Write the clause, in the rule that needs it.** Put it where the rule lives,
   in the same sentence. A scope stated in a third document is a scope nobody
   reads.
4. **Check the safety exception.** No scoping clause may narrow a safety limit.
   If the reconciliation requires that, it is not a scoping problem.
5. **Prefer one precedence sentence.** Where several pairs resolve the same way,
   a single line near the top of the stack — *the rule that names the phase or
   artefact wins over the general one; a safety limit is never scoped away* —
   settles the family without editing every file.

## Worked examples (generic)

| Apparent clash | Missing axis | Clause that reconciles them |
|---|---|---|
| "the answer opens the reply" vs "state your assumptions before the number" | phase | the assumption block goes *after* the verdict, and only for a derived figure that rests on one |
| "one question per message" vs "pick the default, don't ask" | population | the one-question rule governs a queue of dependent decisions; equivalent options are picked, not asked |
| "never delete data" vs a cleanup procedure that deletes | actor | the ban is on *proposing* deletion as a remedy; a procedure's own cleanup runs as written |
| "never simulate" vs "verify before claiming done" | artefact | the ban is on simulation used as *evidence*; exercising the code is required |
| "ingest every source" vs "cut everything that is not the point" | artefact | one is the input, the other the output; name the ingested count so the cut is visible |
| "don't argue with the design" vs "disagree once, with evidence" | phase | no argument from reasoning alone; a fresh measurement that contradicts it is stated once |

## Anti-patterns

- **Deleting the loser.** The rule you remove was written for a real failure; it
  will be reintroduced the next time that failure returns.
- **Adding a third rule.** A meta-rule that restates both leaves the reader to
  guess which applies.
- **"Use judgement."** Unenforceable, and it hands the decision back at the
  moment the rule was supposed to decide.
- **A tombstone.** "X is no longer done" is still a mention; it re-teaches the
  practice. Rewrite the text so it reads as though the practice never existed.
- **Scoping a safety limit.** "Never type credentials — unless he gives you one"
  is not a scope, it is a hole.

## Checklist

- [ ] every quoted rule carries file and line
- [ ] the missing axis is named (phase, artefact, actor, population)
- [ ] the clause sits in the rule it qualifies
- [ ] no safety limit was narrowed
- [ ] the precedence sentence exists and covers the family
- [ ] the audit report says what was left alone and why

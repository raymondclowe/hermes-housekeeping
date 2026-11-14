# Audit report template

Copy this shape for any housekeeping audit. The point is that every statement can
be checked by the reader without asking a follow-up question.

---

## Verdict

One sentence: what state the stack is in, and the single biggest problem.

## Findings

| # | Finding | Evidence (file:line) | Why it matters | Suggested fix |
|---|---|---|---|---|
| 1 |  |  |  |  |

Ranked by expected impact, worst first. A finding without a file and line is a
rumour — drop it or mark it as an assumption.

## Conflicts

| Rule A (source) | Rule B (source) | Missing scope | Clause that reconciles them |
|---|---|---|---|

Genuine contradictions go below the table, labelled as such, with the decision
they need. Do not bury a safety clash inside a scoping table.

## Not checked

List the surfaces that could not be read — another profile, a database, an
unreachable host, a file the agent could not open. An audit that silently omits a
surface reads as complete when it is not.

## Assumptions

Anything stated without direct evidence, phrased as an assumption. Separating
these from findings is the difference between a report and a guess.

## Recommended first change

The single change with the highest expected impact, why it beats the others, and
what it costs (characters, files touched, downtime).

## Left alone deliberately

Rules that looked wrong but were kept, with the reason. This stops the next
auditor from "fixing" something that was intentional.

---

## Rules for the report itself

- **Numbers, not adjectives.** "1,249 of 5,000 characters" beats "plenty of room".
- **Quote the rule, don't paraphrase it.** The paraphrase hides the qualifier.
- **One recommendation per line.** A compound recommendation cannot be approved
  or rejected cleanly.
- **Say what would change the answer.** If a measurement would flip a finding,
  name the measurement.
- **No edits in the audit.** Approval is asked for afterwards, one edit at a time.

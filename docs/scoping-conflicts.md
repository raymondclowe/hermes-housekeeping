# Reconciling conflicting rules

Most "contradictions" are two correct rules with different triggers. Some are real errors.
Telling them apart is the work.

## 1. Three questions, in order

1. **Is there any reading in which both are true?** Look for a condition the text leaves out —
   channel, size, object type, time window, audience.
2. **If yes, name the condition.** Write it as a clause both rules can share: "for a batch",
   "in chat", "where the material has retention value". A scope you cannot state in one line is
   probably not a scope.
3. **If no reading works, it is an error, not a scope.** Say so plainly and correct it.

Worked example of each:

- *Apparent conflict, real scope:* "ask before deleting" versus "delete dead pages without
  asking". Both are right once the object is named: data with no successor is asked; a page that
  measurably fails a dead test is retired as routine work.
- *Real error:* "route this kind of work to agent X" when X does not exist in the profile list.
  No reading rescues that. It is a dead pointer, and anything routed by that list is misrouted.

## 2. The dead-reference test

Before treating a rule as scoped, check names for existence:

- agent/profile names against the actual profile list;
- file and path references against the filesystem;
- skill names against the enabled skill list;
- setting names against the keys the program actually reads.

A dead reference is the one conflict class that is never a scope gap. Check it first; it is cheap
and it is embarrassing to miss.

## 3. Which layer gets the fix

| the fix is about | it belongs in |
|---|---|
| a principle that applies to every task | persona / system prompt |
| a fact or a pointer to where a fact is measured | memory |
| the human's preferences | user profile |
| a procedure, command or pitfall | the skill that runs that work |
| a dated decision, or the reversal of one | the decision log |

Putting a procedure in memory wastes a hard character budget; putting a principle in a skill
means it only applies when that skill is loaded. Say which layer you chose, and why.

## 4. Signs you have faked a scope

- "it depends" with no named condition;
- a scope so broad it swallows the other rule ("sometimes");
- a conflict resolved by deleting the rule someone senior wrote;
- a fix that duplicates the same text in three layers.

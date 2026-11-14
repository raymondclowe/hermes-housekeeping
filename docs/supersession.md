# Supersession: decisions that reverse older decisions

Any long-running project accumulates dated rulings. They are append-only, so two of them can both
say "in force" and disagree. Without a convention, the newest decision is invisible and an agent
follows the oldest one because it was read first.

## 1. The rule

- **Dated filenames.** `YYYY-MM-DD-<slug>.md`. The date is in the name because the name is what
  survives grepping.
- **Later wins on the point it addresses.** It does not silently repeal everything else in the
  older file.
- **Annotate the older file, not the newer one.** A reader who finds the old decision must see
  that it moved, at the top, before they act on it.
- **Never delete a ruling.** The history is how a decision gets audited.

## 2. The header

```
## SUPERSEDED IN PART — <date> by rules/<file>  (what it no longer governs)
```

"IN PART" matters: it forces you to name the clause that died and the clauses that survive.

## 3. Keep an index

A short `Known supersessions` list in the decision log's README. Two lines per entry: the old
file, what it lost. `scripts/ruling_index.py` flags files that mention another ruling but carry no
supersession header, which is usually a missing annotation rather than a missing decision.

## 4. When you cannot tell which is later

Prefer the ruling that records a decision from the person who owns the outcome over one derived by
an agent. Say which you followed, in the report, so the choice is auditable.

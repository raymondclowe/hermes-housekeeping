# Memory budget

Persistent memory usually has a hard character cap. When it fills, new lessons are **rejected**,
so the agent silently stops learning while believing it is saving. Treat the budget as a first-class
finding in every audit.

## 1. Measure before you opine

Report three numbers, always: entries, characters used, characters free.

```
scripts/memory_budget.py --file <MEMORY.md> --limit 2200
```

If free space is under roughly 5% of the cap, say so in the headline, not in a footnote.

## 2. Replace, do not append

A cleanup that removes 200 characters and then adds 220 leaves memory fuller than it started.
Sequence matters: group the removals and the additions into **one** edit, then re-measure. If the
result crowds the cap, the addition was not worth its cost — cut it or fold it into an existing
entry.

## 3. Pointers, not values

Do not store numbers that change on their own: balances, prices, credit counts, token totals,
current headcounts. Store how to measure them.

| instead of | store |
|---|---|
| "balance is ~99,000 credits" | "credits: read from `billing` at call time" |
| "rate is 4 USD per day" | "daily cap is set in the provider console; check before spending" |
| "68 zones" | "zone count: ask the API, it changes" |

A stored volatile value is guaranteed to become a wrong fact, and wrong facts cost more than
missing ones because they are believed.

## 4. Duplicates hide behind different words

The same fact is often written twice in different vocabularies — two mail-routing entries, two
versions of "we never display credentials". Cluster by meaning, not by wording: group entries
that answer the same question, keep the shortest complete one, delete the rest.

## 5. Compaction procedure

1. Snapshot the file (before editing).
2. List every entry with a one-line summary and a character count.
3. Mark each: keep / merge into X / wrong / volatile-value / duplicate.
4. Write the merged file in one pass.
5. Re-measure; confirm the entry count dropped and the headroom rose.
6. Re-read the file from disk and confirm no wrong fact survived.

Step 6 is the one that gets skipped. Skipped verification is how a "cleaned" file keeps its errors.

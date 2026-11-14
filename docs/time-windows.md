# Time windows: scheduled work and peak pricing

Many providers bill more inside defined weekday windows, and many jobs must not start inside them.
Gates like this are easy to write and easy to believe without testing.

## 1. Test the window, not the wrapper

The failure mode is a test that patches a clock the code never reads. Symptoms: every case passes,
including the ones that should fail. Rules that prevent it:

- patch the module the code actually imports, not a copy of it;
- carry over every attribute of the real module when you build the fake one (a partial shim
  raises on the first attribute you forgot);
- assert both a positive and a negative case in the same run, or a broken harness looks correct.

## 2. Use a boundary table

Pin the edges, not the middle:

```
08:59 out | 09:00 in | 11:59 in | 12:00 out | 13:59 out | 14:00 in | 17:59 in | 18:00 out
weekend: out all day
```

End-exclusive windows (`start <= t < end`) are the usual convention; state it.

## 3. Prove both directions

A gate is only proven when you have seen it:

1. **hold** — with the window active, nothing starts and nothing is claimed;
2. **release** — with the window inactive, the same work starts normally.

A hold that never releases is an outage; a release that ignores the window is the cost you were
trying to avoid. One direction alone proves nothing.

## 4. Never test on live state

Copy the state, run the gate against the copy, and check the copy afterward: items still queued,
nothing consumed, no worker started. Say which copy you used.

## 5. Put the check where every path passes

A gate implemented in one caller is not a gate. Ask: what other code path starts this work?
Command-line entry points, manual triggers and emergency paths are the usual holes. Either route
them through the same check or forbid them by rule during the window — and say which.

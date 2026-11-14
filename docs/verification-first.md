# Verification first

An audit that reports what the files say is a summary. An audit that reports what the system
does is a check-up.

## 1. Separate the three kinds of claim

| claim | example | how to verify |
|---|---|---|
| countable | "there are 64 sites", "68 zones" | count it now, from the source of truth, and say when |
| status | "credential works", "job is enabled", "gate is on" | perform the smallest real operation that proves it |
| capability | "tool X is banned", "profile Y exists" | list what is actually configured |

Anything you cannot verify becomes a finding labelled **unverified**, with the reason. Never
launder an assumption into a number.

## 2. A zero exit status is not evidence

Three ways this bites, all seen in practice:

- a script that dies with a syntax error inside a shell heredoc can still be reported as success
  by the wrapper around it;
- a settings command that prints "saved" for a key it does not recognise saves something the
  program never reads;
- a test harness whose clock patch silently did not apply "passes" every case for the wrong
  reason.

So assert on **parsed output**, not on exit codes: read the value back with the same library the
program uses, and print the value you actually got.

## 3. Written is not read

After changing a configuration value:

1. parse the file with the same loader the program uses;
2. resolve the key by path and print its type and value;
3. compare against what you intended, including type (`true` versus `"true"`);
4. diff the file and confirm exactly the lines you meant changed.

`scripts/config_readback.py` does this. A real bug it catches: a list written with the wrong
indentation is parsed as one long string, silently disabling two unrelated entries at once.

## 4. Live beats cached

A cached or stored value is a claim about the past. When a stored claim and the live system
disagree, the live system wins on state and the human wins on intent — report both rather than
overwriting either.

## 5. Prove both directions

For a guard, gate or hold: prove it stops when it should and **also** that it releases when it
should. A gate that never opens looks identical to a gate that works if you only test one side.
Run it against a copy of the real state, never the live one.

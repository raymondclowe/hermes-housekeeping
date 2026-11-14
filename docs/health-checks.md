# Health checks that stay quiet

## Human read this

The most valuable routine an agent can run for itself is a periodic check that
speaks only when something is broken — silent stretches then mean "all green"
instead of "unknown". Point your hermes at this file to design one, or to
repair one that stopped being trustworthy.

## Hermes read this

**1. List the failure classes that are actually possible here.** Start from
history, not imagination: scheduled jobs that stopped running; a provider or
credential that died and silently blocked scheduled work; a service that
stopped listening while its process stayed alive; a queue stalled behind one
bad entry; storage filling up; a backup missing its window. Add classes as
incidents occur.

**2. One cheap probe per class — and probe the thing itself.** Prefer the
component's own status command over a proxy: a reachable port is not a working
job, a live process is not a listening socket, a green scheduler is not a green
job. Where a check needs credentials, read them from the same store the work
uses — the check then also tests the store.

**3. Quiet on green, loud on red.**

- A red message names what failed, since when, the one command to inspect it,
  and what was already tried.
- **Never alert once and fall silent.** A single alert per outage lets a long
  failure go unnoticed — repeat on a slow cadence while red, and state the
  outage duration in each message.
- Silence must mean "the check ran and passed". If the check itself dies, that
  must read as red: have it leave a heartbeat the outside world can watch, or
  run it from a scheduler that reports missed runs.
- Send one all-clear on recovery so alerts have a visible end.

**4. Test the alert path itself.** Trigger a synthetic failure end to end and
confirm the message arrives where a person will see it. A health check that has
never visibly fired is untested.

**5. Audit the join points.** Scheduled work often fails at seams: a job pinned
to a provider or profile whose credential changed; a check that reads one
config section while the system obeys another. When a check covers a job,
cover the job's whole chain of config.

**6. Register the check itself.** It is one of the things that can break — list
it with the rest, and schedule it where schedules already work on that machine.

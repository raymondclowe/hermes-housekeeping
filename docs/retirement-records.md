# Keeping things retired

## Human read this

Removing something — a host from a roster, a skill, a scheduled job, a peer
from a mesh — is not finished when the delete succeeds. Discovery scans, sync
engines and merge routines re-add what they find, and a re-added item looks
exactly like a new one. Point your hermes at this file to retire things so they
stay retired.

## Hermes read this

1. **Retirement is a two-part act: remove, then record.** Keep an explicit
   retired record (a list, a config key, a ledger file) naming what was
   removed, when, by whose decision, and why. The record is what later
   automation consults before treating a match as a discovery.
2. **Discovery is not authority.** A live-seeming signal — an endpoint that
   still answers, a directory that still exists, a member that still
   acknowledges — means the item is reachable, not that it belongs. Only the
   record or the operator restores something.
3. **Operator decisions outrank membership timers.** "Never drop something
   that replied once" is healthy hygiene against flaky members; it is not a
   reason to keep a deliberately retired one. Scope such rules: retirement by
   the operator is the exception, and it applies immediately, not after an
   inactivity window.
4. **Verify the removal against the re-adder.** After retiring, run the
   discovery / sync path (or wait for its next cycle) and confirm the item does
   not reappear. If it does, the record is not wired into the re-adding code —
   fix that, do not just re-delete.
5. **Mind name aliases.** An item often answers to several identifiers — a
   service name, a host alias, a display name. Retire every identifier, or the
   next scan rediscovers it under the one you missed.
6. Cross-check at the end: an inventory of the live set should show no retired
   item present, and no retired identifier reachable.

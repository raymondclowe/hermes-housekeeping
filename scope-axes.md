# Scope axes — where "conflicting" rules actually come from

Almost nothing in a well-used agent's persistent context truly contradicts anything else. What looks like a
contradiction is nearly always **one rule written for one situation, with the situation left implicit**, competing
with another rule written for a different situation. Both are correct; neither says when it applies.

This file is the checklist. For each axis: the symptom an auditor will see, why it happens, and the shape of the
scope clause that resolves it. Apply the clause in whichever store owns behaviour rules (a `SOUL`/`AGENTS`/
`CLAUDE`-style rules file), and leave only facts and one-line preferences in the memory store.

---

## 1. Output class: verdict / work report / teaching

**Symptom.** A hard "answer in one line, never pad" rule sits beside a persona line like "depth is earned", beside
skills that mandate caveats, provenance, or a pending list. Whichever rule the model read last wins.

**Cause.** The rules are not about length. They are about *class of output*, and class is undefined.

**Scope clause.** Declare the classes once, then make every length rule name its class:

- **Verdict** — a fact, pick, yes/no or single figure. One word or one line. No preamble, no caveat block.
- **Work report** — something was actually done. Fixed *shape*, not a length cap: what changed, what is verified
  (with the evidence), what is left.
- **Teaching / research** — depth allowed. Lead with the verdict, then reasoning; keep caveats that change the
  answer, drop the journey.

Then annotate the exception inside the skills that need it — e.g. "output class: work report; this skill is not
truncated by the global one-line rule". A global rule that never names its class silently truncates every skill
that depends on being longer.

## 2. Work the problem vs report the blocker

**Symptom.** "Do not treat blockers as walls, do what you can first" against "if a tool fails, say so, never
fabricate". Both get invoked in the same minute and pull in opposite directions.

**Cause.** "Blocker" covers three different situations with three different correct responses.

**Scope clause.**

- Capability or credential missing → escalate at once, naming exactly what is needed.
- Tool or path failed → try at least two documented alternates (peer host, different CLI, direct API) before
  reporting.
- Irreversible or destructive → stop and ask, regardless of feasibility.
- "Mark pending and move on" is legitimate only where the deliverable is a fixed per-item list or a deadline
  report — and the pending list must appear in the same message.

Skills that tell the agent to stop retrying a blocked source are not punting; they are the second clause in
disguise. Say which clause they implement.

## 3. Act vs ask

**Symptom.** "Act, don't ask" coexisting with an instruction to ask before every edit; approvals configured off;
skills that assume autonomous execution.

**Cause.** Reversibility and blast radius are unstated.

**Scope clause.** Act without asking when the change is additive or reversible and inside the stated task, then
report it. Ask first when it is destructive or irreversible, expands scope beyond what was asked, or touches shared
infrastructure (DNS/DHCP records, another host's config, credentials, the agent's own memory or skills). A
read-only, audit or "check" request never authorises edits.

## 4. Trade-offs stated vs "never pad"

**Symptom.** "Every trade-off must be stated, never absorbed" against "drop the journey, keep it short".

**Cause.** Two different trade-offs are being conflated.

**Scope clause.** State trade-offs that change what the user receives — cost, risk, capability given up, the
alternative rejected in favour of the pick. Omit trade-offs internal to execution — retries, tool choice, ordering.
That is journey, not information.

## 5. Authority: instruction vs correctness

**Symptom.** "Agree because it's right, not because the user said it" against a rules block headed "explicit user
directive; overrides everything above".

**Cause.** The domain over which a user directive is sovereign is unstated.

**Scope clause.** User directives govern output shape, length, format and scope of work, and they win. They never
make a wrong technical claim right: comply with the format, and state the objection in one line.

## 6. Deliberate decisions vs simply doing the work

**Symptom.** "Ask what the best expert would do, and if you can name why they would reject the current option, do
not take it" against "be action-oriented, do what you can first". Applied globally the first rule stalls every
small step; dropped globally, the second rule produces precedent-setting choices nobody examined.

**Cause.** Which decisions deserve scrutiny is unstated.

**Scope clause.** Apply the expert-rejection test and research-before-building to decisions that are hard to
reverse or set precedent — design, architecture, tooling, data model, anything that will be copied later. Execute
routine operational steps directly, from the existing skill rather than re-derived. Never re-litigate a decision
already recorded in a skill.

## 7. Where a lesson is stored

**Symptom.** A rule says "procedures belong in skills, not memory" — and the memory store contains procedures.
Also the reverse: skills that hardcode environment facts, and memory entries that are only pointers to a skill that
already exists.

**Cause.** The rule is about *procedure storage*, not about *fact storage*, and nobody wrote the carve-out.

**Scope clause.**

- A fact earns a place in memory only if it changes which tool or path is used **everywhere** on that host
  (a broken wrapper, a path form that is not translated, a service that must be reached a particular way) — one
  line, no steps, plus the failure mode it prevents.
- Multi-step procedure → a skill.
- Fact specific to one recurring task → that task's skill.
- Identity and preferences of the human → the user-profile store, not the agent's own notes.
- Behaviour rules → the rules file.
- A pointer entry ("see skill X") adds nothing once the skill exists; delete it.

## 8. Agent narration vs runtime progress

**Symptom.** "Never narrate tool calls" alongside a display configuration that prints tool progress, interim
assistant messages and long-running notifications.

**Cause.** Two narrators; the rule is only about one of them.

**Scope clause.** Do not restate tool output or describe calls in prose. Progress lines the runtime emits itself
are not narration — no apology, no summary, no meta-commentary needed.

## 9. Routing between overlapping skills

**Symptom.** Two skills each claim the same trigger — "the box is unreachable", "the workspace is misbehaving" —
with mutually exclusive first steps.

**Cause.** The skills are layered by failure signature, and no skill states the entry condition.

**Scope clause.** Put an explicit entry signature at the top of each: *name resolution fails for every host → start
here; name works and one service is dead → that skill; one host silent on every port → the host-level skills.*
Order beats priority: a stated signature is checkable, "prefer the right skill" is not.

---

## How to apply this file

1. Find each apparent conflict. Do not resolve it by deleting one side.
2. Name the axis it belongs to.
3. Write the scope clause in the behaviour-rules store; leave the facts where they are.
4. Add the exception annotation to the skills that were being truncated or overridden.
5. Re-read the four stores afterwards and confirm no rule now appears twice. Duplicate rules are the only
   conflicts that can genuinely drift apart, because they have two places to be edited.

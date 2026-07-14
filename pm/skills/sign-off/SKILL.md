---
name: sign-off
description: >
  Sign off an Assignment: the operator's mark that they have seen it and stand
  behind it. For a Command or Manual it is the gate that admits the kind to the
  pickup pool; for a Premise or Direction, already pickable, it records the
  operator's endorsement of the framing, which the Bob that picks it up reads in
  its first turn. Operator-invoked.
model: opus
effort: low
---

# Sign-off

Sign-off is the operator's mark that they have personally seen an Assignment and put their authority behind it. What it does next turns on who authored the kind. A Command or Manual carries the operator's authority and waits outside the pickup pool until they release it, so signing it off is the gate that admits it for autonomous spawn. A Premise or Direction is agent-authored and already pickable, so signing it off gates nothing; it records that the operator has read this one and endorses its framing, a mark the Bob that picks it up reads in its first turn, where it marks the difference between a framing the operator has seen and vouched and one only an agent has stood up so far.

The gate is a one-way door. Once a Command or Manual is signed off it is pickable, and the spawn loop may put a Bob on it on its next pass: autonomous work you cannot recall. So this skill only records a decision the operator has already made: it does not compose, run, or spawn, and sign-off of either kind is the operator's to invoke, never an agent's to infer, because a fabricated endorsement misleads the picker as surely as a fabricated gate-release admits work no one authorized.

## Confirm the Assignment before you write

Sign off only the id the operator named, and only once you have confirmed it is the one they mean. The rule is flat because nothing downstream catches a mistake: to every later reader the mark looks authorized. For a Command or Manual this is the irreversible point: signing off the wrong one, or one the operator has not actually settled, puts work into the pool under their authority that they never gave. For a Premise or Direction it records an endorsement the operator never made, and the Bob that picks it up takes the framing as vouched when it is not.

Signing off a Premise or Direction is never a prerequisite for spawn, since those are already pickable; reach for it only when the operator has reviewed the Assignment and wants their endorsement of its framing on the record for whoever picks it up. It is not a step every Premise gets: most are agent-authored and worked unsigned, and that is the default the picker is built to expect.

## Sign it off

```bash
vv sign-off <ASSIGNMENT>
```

`vv sign-off` sets the tracker's "Signed off" field to Yes and prints a confirmation, whatever the kind. For a Command or Manual the Assignment is now pickable as soon as its dependencies resolve: the kind is cleared, and the Depend graph still gates ordering. For a Premise or Direction pickability does not change; what changes is that its first-turn brief now tells the picker the operator has vouched the framing.

## Report

One line: the Assignment signed off. For a Command or Manual, that it now waits in the pool for `/spawn` or `/available`; admitting and running stay decoupled, and signing off does not spawn. For a Premise or Direction, that the operator's endorsement is now on the record for the next picker.

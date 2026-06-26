---
name: manual
description: >
  File a Manual (the Assignment that delegates no discretion, where the
  operator keeps the wheel and releases intent live) into the tracker, in
  this thread. Capture the standing instructions the operator wrote but
  chose to defer; invent nothing. Routeless. Operator-invoked.
model: opus
effort: medium
---

# Manual

A **Manual** is the Assignment that delegates no discretion: the operator keeps the wheel and gives direction live, turn by turn, instead of handing it all over before the work starts. A Bob spawned on a Manual is primed and seeded with the instructions you capture here, and carries one standing posture: proactive about understanding, not about mutating. It reads, investigates, and raises questions, but changes nothing until the operator directs it.

The operator holds the authority; your job is to write down the instructions they have settled but chose to defer, accurately enough that the Bob who wakes on it starts in the right place and waits in the right posture.

## Record what was settled; invent nothing

Your job here is the same as in `/command`: write down what the operator gave you, and invent nothing. A Manual comes from the operator the way a Command does: you are recording their instructions, not reasoning your way to a goal of your own. You are a courier, not an author.

- Where the deferred instruction is unclear or underspecified, **ask the operator**, even if it feels like nagging.
- The operator may answer "you will see when you get there." That is a real answer: a Manual expects intent to arrive live, so write down what the operator gave and leave the rest for the wheel they are keeping.
- Every detail you are about to write, check against what the operator actually said. A detail they never gave (added to round out the instructions) is the worst thing you can put in a Manual: it carries their authority without their intent. Cut it.

## Procedure

### 1. Compose the title

One line naming what the operator will be driving: the standing situation the Bob wakes into, not a goal to reach.

### 2. Compose the body with the operator

Capture the deferred instructions: what the Bob should read and understand first, where it should look, what it must not touch, and the posture it holds while it waits. Where the operator deferred something to live direction, say so in place rather than filling it in.

### 3. File it

A Manual has no Route: it expects no conversation classified in advance, because its intent arrives turn by turn. Carry the title and body through single-quoted heredocs so backticks and other shell metacharacters do not interpolate:

```bash
summary=$(cat <<'MANUAL_SUMMARY'
<the title from step 1>
MANUAL_SUMMARY
)
description=$(cat <<'MANUAL_BODY'
<the deferred instructions and the standing posture from step 2>
MANUAL_BODY
)
new_id=$(vv file --project <PREFIX> --type Manual --summary "$summary" --description "$description" [--dep <PEER>...])
```

Each closing delimiter sits at column 1 with no leading whitespace. `vv file` is the kind-agnostic authoring primitive; `--type Manual` files the kind with no Route, and passing a Route is refused at the gate, since a Manual takes none. `--project` is the Component the Bob will be driven in. `--dep` wires a prerequisite the Manual waits on. `vv file` prints the new Manual's idReadable.

### 4. Report

One line: the new Manual's id. It waits in the tracker until the operator signs it off and spawns it.

## Non-goals

- **Does not spawn or drive.** Filing a Manual never starts it; `/manual` exposes no `--spawn`, as `/command` exposes none. A Manual carries the operator's authority, so it waits outside the pool until the operator signs off (`/sign-off`): the release that admits it for spawn. The operator then spawns and drives it, holding the wheel from its first turn.
- **Does not author a goal.** A Manual carries deferred instructions and a posture, not a settled call or a contestable proposition. If the operator has actually decided a goal and wants it carried out, that is a `/command`; if you are the one reasoning to the goal, that is a `/premise` or a `/direction`.

---
name: decompose
description: >
  Turn a settled plan-route design into the child Assignments that materialize
  it. Decomposition proceeds in rounds: cut the children that are implications
  of the meaning settled so far, minting each as the kind its discretion calls
  for (a Direction for a settled leaf, a Premise where the ends stay open) and,
  when work remains beyond this round, file a continuation that re-decomposes the
  rest against what this round produces rather than guessing it now. Pressure-test
  each candidate by simulating the Bob who will pick it up, until the round
  stabilizes, then author through `vv file` in dependency order.
---

# Decompose

Turn a **settled design** into the **child Assignments** that materialize it, with the Depend edges between them. `/decompose` is the plan-route counterpart of `/premise`: where `/premise` authors one worked-out Assignment, `/decompose` cuts a design into many and pressure-tests the cut before any is filed. It is the deliverable of a `plan`-route Assignment: the tracker mutations are the artefact, not code.

**When to use:** you are working a `plan`-route Assignment, the design has shape (reached in conversation, with or without a prior `/design` pass), and the next move is deciding what child Assignments must exist to build it.

**When not to use:**

- The design is not settled yet. Deciding *what* to build is the conversation before `/decompose`; this pass assumes that conversation has happened.
- There is only one Assignment to author. That is `/premise` or `/direction`.
- You are auditing Assignments that already exist for drift. That is `/groom`: the same simulate-the-picker move, run backward over realized Assignments rather than forward over candidates.

## Decomposition proceeds in rounds

A child is well-founded only when the meaning it is an implication of (the names, the contracts, the vocabulary it is written in terms of) already exists. Cut a child against meaning not yet settled and its picker reinvents that meaning; the next child's picker reinvents it differently, and the two drift before they ever integrate. So the names and contracts the later work hangs off are not one more child cut alongside the rest: they are what the rest is cut *against*, and they go first.

Laying them changes the world for what comes after. The Bobs working this round discover things (a name that was wrong, a constraint nobody saw at design time, a seam that turned out to sit elsewhere) that reshape what the later children should be. A child authored before that discovery is authored against a world that no longer holds when it is picked up. The design you hold in conversation is a forecast of that world: most of it sound, some of it fiction, and you cannot tell which from where you stand.

Both pressures point one way: **do not cut the whole tree at once.** Cut one **round** (the children that are implications of the meaning settled so far, plus whatever new meaning the next round needs) and, when work remains beyond it, hand the next cut forward as a **continuation**: a plan-route child that re-runs `/decompose` once this round has resolved, cutting the rest against what the round produced instead of against today's forecast. This round you can author with confidence; the round after it is cut by the agent who can read the world this one made, not the one who has to predict it.

When nothing in a round reshapes what remains (the children are independent, the world they act on is fixed, finishing them teaches nothing you did not already know) there is no next world to cut against, and the decomposition is a single round with no continuation. Rounds answer a design whose later shape its own early work will change; they are not a tax on every decomposition. A small, flat design stays small and flat.

## The round is a value

The set of children for a round and the Depend edges among them is a **value** you hold and rewrite in conversation, the way `/design` holds a design. Nothing is filed until that value stops changing. Pressure-test the whole round to a stable graph first; author second. Filing children while the cut is still moving is the failure to avoid: a child minted before a later pass merges it away is an Assignment you then abandon, and a Depend edge wired against a real id is one you can no longer cleanly overturn.

The round is transient; it lives only in this conversation. Its durable residue is the Assignments and Depend edges it pours out, and (when a next round is owed) the continuation that carries the decomposition forward. There is no persisted "plan" entity and no design document.

## The pressure-test

The decisive judgment is the **cut** (where the boundaries between children fall, and where this round stops and the next begins) and it cannot be mechanized. Test each candidate by simulating the Bob who will pick it up, with its prerequisites resolved and nothing else:

- **What meaning must already be settled for this child to be an implication rather than a guess?** The names, types, and contracts it is written in terms of. If they do not exist yet, they are a prerequisite: an earlier child in this round lays them and this child Depends on it; or, if laying them is itself work that will reshape this child, this child belongs to a *later* round, cut after that meaning is settled. This is the question the start-only reading of dependency misses: a child can hold every input it needs to *begin* and still be cut against an ontology no one has agreed.
- **What scope does it assume already done but does not itself finish?** That assumption is a Depend edge, or a prerequisite child that does not yet exist. Surface it; the dependency ordering within a round is the residue of this question, not a separate step.
- **What would make it overbroad?** A child carrying two separable promises is two children. Split it; the split usually reveals a dependency between the halves.
- **What would make it really part of another?** A child that cannot be picked up and resolved unless another is in flight at the same time is not a sibling; it is the same Assignment. Merge them.
- **What would this child discover that reshapes a sibling?** If finishing it could change what a sibling should be (rename what the sibling is about, move the seam it cuts along, void an assumption it rests on) the sibling is not safe to author yet. The discovering child stays in this round; what it would reshape is what waits, in a later round behind the continuation. The seam where a sibling could be authored only by predicting what this child will find is where the round stops.

**The cut can cross Components.** A candidate whose work falls mostly in one Component but forces a change in a partner is one child Assignment or two, decided by the same merge-or-split test. When the partner change is a superficial contract adjustment *driven by* the meaningful change (a boundary protocol following its home) the two are tightly coupled: they are the *same* Assignment, realized as coordinated PRs across the repositories. When the partner change is itself meaningful, the "drive" is really a dependency: make it a separate child with a Depend edge, not a second PR on one Assignment. The Component and Context doctrine in `~/.vaudeville/doctrine/vocabulary.md` is the authority; major surgery in two Contexts at once signals inappropriate coupling, not a single Assignment.

Exceptions exist even to this: for example, redefining the boundary between two Contexts involves a major subtraction from one and a corresponding addition to the other. These are very rare and should be treated with extreme skepticism.

Iterate. Each answer rewrites the graph, and a rewrite reopens the questions for its neighbours; this is the pass that overturns plausible-but-wrong orderings and finds where the round ends. Stop when a full sweep changes nothing.

## The kind each child takes

Each child takes the kind its own discretion calls for; the discrimination is the one `/premise`'s gate runs, and a decomposition reaches only the two kinds an agent authors on its own initiative, since the operator is not in the loop child by child:

- A child whose **ends are settled and means stay open** is a **Direction**, the common case, and the reason the round can be cut at all: the design settled the goal, so a child materializing a slice of it inherits a goal already made and leaves open only how to realize it. The meaning a round lays is the hinge for the whole set of its implications; each child carries its own slice of that as the hinge `/direction` is built around, including the child that *lays* the meaning, whose ends (that this name or contract must exist) are settled even though the round's other children will test whether its shape is right. That test is the Direction's hinge, not a reason to demote the meaning-child to a Premise; demote only if its ends are themselves open.
- A child whose **ends are still open** (a proposition a peer should be free to contest) is a **Premise**. Default here when the goal is not crisply settled on one nameable assumption: the bias toward Premise that `/premise`'s gate carries holds inside a decomposition as it does outside it, because filing a Premise as a Direction declares a live goal closed and the argument that should have happened never does.
- A child that is **itself an open-ended sub-area whose own cut must wait** is a **plan Premise** (`--route plan`). The continuation is the special case: the plan child that carries *this* decomposition's next round.

A Command or Manual never appears: their authority is the operator's, and an agent does not originate them, so a cut the agent makes on its own initiative cannot mint them.

## The continuation

When a round leaves work beyond it, the next round is not yours to cut now; it is the next agent's to cut against the world this round produces. A **continuation** carries it forward: a plan-route child that Depends on this round's children and, once they resolve, is picked up to re-run `/decompose`. Its body is deliberately thin:

- **The goal**: what the whole effort is for, the part that does not go stale because it is the settled end the design already fixed.
- **The charge**: re-decompose the rest of that goal against what this round produced, now that forecast can be replaced with fact.
- **A pointer**: which resolved Assignments' delivered output (merged changes, closeout synopses) the next cut reads as ground truth.

It does *not* carry a breakdown of the next round's children. That breakdown would be written against a world that does not exist yet (the fiction the round structure exists to refuse) and the next agent, reading it against the world that now does, would tear it out. Hand forward the destination and the pointer to reality, never a route drawn across ground no one has walked.

A continuation is picked up like any Assignment: when the round's last child resolves its Depend edges are satisfied, it becomes pickable, and `/onward`'s fanout (or `/available`, or an explicit `/spawn`) puts a Bob on it. That cut may end in a further continuation, and the next, until a round leaves nothing beyond it and files none.

## Procedure

### 1. Derive the candidate children for this round

From the settled design, draft the smallest set of children that each materialize a slice whose meaning is settled now: for each, a one-line sense of what it promises, which siblings it leans on, and which kind it looks like. Include the children that lay the meaning the rest of the round is an implication of. This is a first cut, not a plan; it exists to be pressure-tested.

### 2. Pressure-test to a stable round

Run the pressure-test above over the candidate set until a sweep leaves it unchanged. Hold the result as a value: the children, each with the slice it owns and the kind it takes, and the Depend edges among them (a DAG, prerequisites pointing forward). The same pass decides where the round ends: a candidate authorable only by predicting what an in-flight sibling will discover is not in this round; it is beyond the continuation. A child whose work falls in another Component files under that Component; cross-Component Depend edges are fine, and `vv file`'s `--project` carries them.

### 3. Surface the round and wait

Surface the stabilized round to the operator: the children, one line each with their kinds, the dependency structure, and (when there is one) the continuation and what it defers. This is the residue of the pass, the way a check-in is the residue of its discussion. Wait for the operator's blessing before mutating the tracker; filing is the irreversible step. The operator blesses each round as it is cut against a world made real, rather than a speculative tree built all at once.

### 4. Author, in dependency order

On approval, author each child with `vv file`, prerequisites first, so every intra-round Depend target already has an id when a dependent references it. File each in the kind it takes (`--type Direction --route check-in` for a settled leaf, the default Premise for an open one, `--route plan` for a sub-area) composing the body in that kind's discipline: a Direction in `/direction`'s call/why/hinge/reopens shape, a Premise as the humble snapshot `/premise` sets out. Read the kind's own skill for the composition; this skill does not repeat it. Carry each summary and body through single-quoted heredocs so shell metacharacters stay literal.

```bash
# a settled leaf: goal made, means open
a=$(vv file --project <PREFIX> --type Direction --route check-in --summary "$summary_a" --description "$body_a")
# a child still open to contest
b=$(vv file --project <PREFIX> --summary "$summary_b" --description "$body_b" --route check-in --dep "$a")
```

When the round leaves work beyond it, author the continuation last, depending on the round's children, with the thin body the section above describes:

```bash
cont=$(vv file --project <PREFIX> --route plan --summary "$summary_cont" --description "$body_cont" --dep "$a" --dep "$b")
```

### 5. Hand back to the lifecycle

`/decompose` stops once the round's children (and the continuation, if there is one) exist. Closing the plan-route Assignment you are working is the Bob's next lifecycle step, not this skill's: `/closeout delivered`, with a synopsis naming the child ids and the dependency graph among them. The round's children are left Submitted in the pickup pool; a later `/available` or `/spawn` puts a Bob on each as its Depend edges clear.

## Non-goals

- **Does not settle the design.** The design is agreed before `/decompose` runs; this pass cuts it into Assignments, round by round.
- **Does not default every child to Premise.** Each child takes the kind its discretion calls for (a Direction for a settled leaf, a Premise where the ends stay open, a plan Premise for a sub-area) and the per-child composition is the chosen kind's skill, reached through `vv file`. `/decompose` owns the cut, the round boundary, and the ordering, not the snapshot shape.
- **Does not pre-author the next round.** Work beyond this round goes forward as a continuation that re-decomposes against produced reality, never as children cut now against a forecast.
- **Does not spawn the children.** Authoring leaves them Submitted in the pickup pool; a later `/available` or `/spawn` picks them up.
- **Does not persist a "plan" entity.** The round is a transient conversation value poured out through `vv file`; its only durable residue is Assignments and Depend edges.
- **Is not `/groom`.** Groom audits Assignments that exist; decompose pressure-tests candidates that do not.

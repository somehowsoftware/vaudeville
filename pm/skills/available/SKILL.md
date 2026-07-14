---
name: available
description: >
  Recommend which Assignments to spawn right now, in parallel: a committed take
  grounded in UL. Grooms the candidate set as a backstop (shared-foundation
  duplication on Assignments about to be spawned). For comprehensive
  backlog-wide drift detection, invoke `/groom`.
---

# Available

The purpose of `/available` is to produce a recommendation the operator can act on: **which Assignments to spawn right now, in parallel.** The underlying script filters the tracker to the candidate set; the skill reasons over that set, grooms drift on the Assignments about to move, and commits to a take.

`/available` is the narrow end of backlog grooming. It grooms only its candidate set (the Assignments about to be spawned) so the recommendation stays clean. Drift elsewhere in the backlog (blocked pickup-pool Assignments, unresolved Assignments in other branches of the graph) is **not** `/available`'s problem; it is `/groom`'s. The two skills divide the work deliberately: `/groom` is comprehensive and run intermittently, `/available` grooms its own input on every run.

## Procedure

**1. Prime.** Recommendations and grooming decisions must be grounded in scaffold-vocabulary terms (Assignment, Route, Bob).

**2. Fetch the candidate set.**

```bash
vv available
```

An Assignment appears in the candidate set when:

- its Workflow is `Submitted` (no one has claimed it yet) or `Returned` (tried and handed back),
- its kind is cleared for the pool: a Premise or Direction always (an agent authors them, so they are safe to auto-surface), a Command or Manual only once the operator has signed off,
- every Assignment it depends on is resolved (State `isResolved: true`, that is `Delivered` or `Abandoned`).

**3. Reason about parallel safety.** The **Depend** graph is the primary parallelism gate: Assignments that must not run in parallel should already carry the right Depend edges. `/available`'s per-call reasoning is a backstop on the candidate set, not the first line.

Two Assignments conflict when they would introduce the same **shared foundation** in different ways: duplicated infrastructure, divergent schema, parallel abstractions later needing reconciliation. Merely touching the same file for *different* reasons is not a conflict; the minor merge conflicts that produces resolve cleanly during `/parlay`.

**4. Groom the candidate set.** Fix drift on the Assignments about to be spawned *in this conversation* before recommending.

- **Shared-foundation duplication among candidates.** If two candidates would introduce the same foundation and lack a Depend edge, the graph has drifted. If one can act as common ancestor, add the Depend link. If neither is suitable, draft a new common-ancestor Assignment (`Route: check-in` by default) and add Depend links from both.

This grooming is scoped to the candidate set. Broader drift detection (blocked pickup-pool Assignments, dead Depend edges, duplication across Assignments not in the candidate set) is `/groom`'s job. If the scan smells off or the backlog hasn't been groomed recently, suggest a `/groom` run rather than widening this skill's scope.

**5. Deliver the recommendation.** Report in two parts:

- **Spawn now:** Assignment IDs with one-line reasons: the specific set the recommendation endorses spawning concurrently.
- **Hold:** remaining candidates, each with a one-line reason (dependency not yet resolved, grooming proposal pending the operator's confirmation, scope dispute surfaced).

Commit to a take. This is a recommendation, not a survey. If nothing is safely parallel, say so and name one sequential pick. Also report any grooming edits made or proposed during the turn.

## Credentials

If the command fails with a credentials error, set the tracker's API credentials in `~/.vaudeville/credentials.toml`.

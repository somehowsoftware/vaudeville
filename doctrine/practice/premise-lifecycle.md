# Premise lifecycle

*Doctrine doc — high-level WHAT for a cross-context vocabulary set. Per-context usage details live in the consuming context's own vocabulary.*

A Premise's lifecycle: authored, prepared, worked, terminated (via closeout). The terminations are shared kernel vocabulary because the same kinds apply regardless of which lifecycle skill performs the closeout, and because they name what happens to the Premise, not what the Bob does about its relationship to it. The states a Premise-based Bob moves through, and the skill verbs that move it, are in [diagrams/premise-bob-lifecycle.puml](../diagrams/premise-bob-lifecycle.puml).

Three kernel terminations. Each names a distinct judgement about the Premise's deliverable state and transitions it to a different terminal tracker state.

## Delivered

The deliverable shipped: PR merged, or off-tree work completed. Transitions to `Delivered`; resolved.

## Abandoned

The Premise should not exist anymore: misfiled, obsoleted by other work, or judged not worth doing. Transitions to `Abandoned`; resolved, but distinguishable from `Delivered` in the audit trail.

## Returned

Work attempted and stopped partway: completion needs a fresh perspective, a missing prerequisite, or a decision the Bob could not make. Transitions to `Returned` and re-enters the pickup pool; the next picker receives the partial trail as context.

## Additional closeout kinds

Closeout tooling defines two further kinds that name what the Bob does about its assignment, not the Premise's deliverable state: `unclaim` (Bob releases the Premise without doing the work, leaving the pickup-pool signal as if the Bob had never touched it) and `none` (substrate teardown only, no tracker writes). Being about the Bob's relationship to the Premise rather than the Premise itself, they live with the closeout tooling, not in the kernel.

## Notes

All five kinds share one CLI dispatch surface (`vv exit --kind`). That sharing is CLI convenience, not a domain claim: the three kernel terminations are siblings of one another; the two closeout-only kinds are siblings of one another; the two groups are not siblings of each other.

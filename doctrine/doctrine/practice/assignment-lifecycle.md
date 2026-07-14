# Assignment lifecycle

*Doctrine doc: high-level WHAT for a cross-context vocabulary set. Per-context usage details live in the consuming context's own vocabulary.*

An [Assignment](../vocabulary.md#assignment)'s lifecycle: authored, prepared, worked, terminated (via closeout). It spans the kinds: a [Premise](../vocabulary.md#premise), a [Direction](../vocabulary.md#direction), and a [Command](../vocabulary.md#command) are each authored, worked, and terminated through the same states; a [Manual](../vocabulary.md#manual), carrying no Route, is driven by the operator rather than run to a deliverable. The terminations are shared kernel vocabulary because the same terminations apply regardless of which lifecycle skill performs the closeout, and because they name what happens to the Assignment, not what the Bob does about its relationship to it. The states a Bob moves through, and the skill verbs that move it, are in [diagrams/assignment-bob-lifecycle.puml](../diagrams/assignment-bob-lifecycle.puml).

Three kernel terminations. Each names a distinct judgement about the Assignment's deliverable state and transitions it to a different terminal tracker state.

## Delivered

The deliverable shipped: PR merged, or off-tree work completed. Transitions to `Delivered`; resolved.

## Abandoned

The Assignment should not exist anymore: misfiled, obsoleted by other work, or judged not worth doing. Transitions to `Abandoned`; resolved, but distinguishable from `Delivered` in the audit trail.

## Returned

Work attempted and stopped partway: completion needs a fresh perspective, a missing prerequisite, or a decision the Bob could not make. Transitions to `Returned` and re-enters the pickup pool; the next picker receives the partial trail as context.

## Additional closeout kinds

Closeout tooling defines two further kinds that name what the Bob does about its assignment, not the Assignment's deliverable state: `unclaim` (Bob releases the Assignment without doing the work, leaving the pickup-pool signal as if the Bob had never touched it) and `none` (substrate teardown only, no tracker writes). Being about the Bob's relationship to the Assignment rather than the Assignment itself, they live with the closeout tooling, not in the kernel.

## Notes

All five kinds share one CLI dispatch surface (`vv exit --kind`). That sharing is CLI convenience, not a domain claim: the three kernel terminations are siblings of one another; the two closeout-only kinds are siblings of one another; the two groups are not siblings of each other.

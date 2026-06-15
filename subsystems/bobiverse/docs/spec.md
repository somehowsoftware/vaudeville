# vaudeville-bobiverse — spec

*This is a spec — high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code.*

vaudeville-bobiverse manages the lifecycle of a Bob from spawn to teardown. It owns the moment a Bob comes into being, the verbs that move it through that lifecycle (spawn, materialize, parlay, closeout), the **Checkpoint** verb by which a Bob sheds an oversized conversation mid-run and resumes its own work in a fresh context (the mechanism materialize and parlay are thin entries onto), the **Prime** verb that prepares the per-Managed-Repository **Foundation** each Spawn forks from, and the moment a Bob terminates. It does not author Premises, decide what work the operator picks up next, or integrate the scaffold; those concerns live in vaudeville-pm, vaudeville-cue, and vaudeville-ringmaster respectively.

Bobiverse-internal vocabulary is in [vocabulary.md](vocabulary.md). The cross-context Ubiquitous Language — Bob, Premise, Route — is in `~/.vaudeville/doctrine/vocabulary.md`. The federation-level lifecycle of a Premise-based Bob, which crosses every Contributor named below, is illustrated in the lifecycle diagram under `~/.vaudeville/doctrine/diagrams/`.

## Collaborators

Four named boundaries.

**vaudeville-cue** owns the Brief (`~/.vaudeville/doctrine/vocabulary.md#brief`) — the first user turn a newly-spawned Bob reads, consumed *after* the Foundation's priming so it rides on top of an already-primed conversation. At spawn, bobiverse invokes the configured Brief downstream — cue's, by default — and hands the rendered Brief to workmux. The boundary flow is illustrated in [diagrams/seed-prompt-flow.svg](diagrams/seed-prompt-flow.svg).

**workmux** owns substrate allocation. At spawn a substrate is allocated; at closeout it is archived and its worktree torn down. A Spawn forks from the Managed Repository's Foundation through workmux, so the Bob inherits the primed conversation as its history. Bobiverse names the operations and their guarantees; workmux owns what the substrate is.

**vaudeville-core** owns the anticorruption layer over the work tracker. Every tracker read and write goes through core's kernel surface; bobiverse does not name the tracker by product.

**GitHub** (via the `gh` CLI) carries PR operations from `/materialize` and `/parlay`. The boundary is the `gh` command surface.

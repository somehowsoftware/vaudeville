# vaudeville-bobiverse: spec

*This is a spec: high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code.*

vaudeville-bobiverse owns the **inter-session** lifecycle of a Bob: what happens *around* a running session, not inside it. It owns the moment a Bob comes into being (**Spawn**), the **Prime** verb that prepares the per-Component **Foundation** each Spawn forks from, the **Reseat** that replaces a running Bob's session in place (the session-lifecycle act cue's Checkpoint launches to shed an oversized conversation), the **Closeout** that ends a Bob, and the **Teardown** every Closeout resolves to. The **intra-session** lifecycle (what a running Bob does to its own work, including Checkpoint, Materialize, Parlay, Design, Winnow, and Spike) is vaudeville-cue's: bobiverse spawns the Bob and hands it cue's Brief, and from that first turn on the work inside the session is cue's. bobiverse does not author Assignments, decide what work the operator picks up next, or integrate the scaffold; those concerns live in vaudeville-pm, vaudeville-cue, and vaudeville-ringmaster respectively.

Bobiverse-internal vocabulary is in [vocabulary.md](vocabulary.md). The cross-context Ubiquitous Language (Bob, Assignment, Route) is in `~/.vaudeville/doctrine/vocabulary.md`. The federation-level lifecycle of an Assignment-based Bob, which crosses every Collaborator named below, is illustrated in the lifecycle diagram under `~/.vaudeville/doctrine/diagrams/`.

## Collaborators

Four named boundaries.

**vaudeville-cue** owns the Brief (`~/.vaudeville/doctrine/vocabulary.md#brief`), the first user turn a newly-spawned Bob reads, consumed *after* the Foundation's priming so it rides on top of an already-primed conversation. It also owns the intra-session lifecycle the Bob runs thereafter, whose Checkpoint launches bobiverse's **Reseat** (`vv reseat <worktree> <brief-path>`) to shed an oversized conversation in place: cue composes the Resume Brief and names the pane, and bobiverse replaces the session with spawn's launch minus the Foundation fork. At spawn, bobiverse invokes the configured Brief downstream (cue's, by default) and hands the rendered Brief to workmux. The boundary flow is illustrated in [diagrams/seed-prompt-flow.svg](diagrams/seed-prompt-flow.svg).

**workmux** owns substrate allocation. At spawn a substrate is allocated; at closeout it is archived and its worktree torn down. A Spawn forks from the Component's Foundation through workmux, so the Bob inherits the primed conversation as its history. Bobiverse names the operations and their guarantees; workmux owns what the substrate is.

**vaudeville-core** owns the anticorruption layer over the work tracker. Its name is a misnomer: so-called "core" is not a shared kernel but Vaudeville's outermost boundary, the layer that translates external systems (the work tracker, git hosting, the host config) into Vaudeville primitives. Every tracker read and write goes through "core"'s anticorruption surface; bobiverse does not name the tracker by product.

**GitHub** (via the `gh` CLI) carries the PR-status reads `/closeout` runs to confirm an Assignment's pull request merged before tearing the Bob down. The boundary is the `gh` command surface.

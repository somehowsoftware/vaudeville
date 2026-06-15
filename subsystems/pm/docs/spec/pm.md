*This is a spec — high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code. The doctrine for this layering is in `~/.vaudeville/doctrine/code/intent.md`.*

# vaudeville-pm

vaudeville-pm contributes Premise authoring and Premise-state transitions to the Vaudeville scaffold. It owns the act of writing a new Premise into the project tracker — composing the description in the humble-snapshot shape, setting the Route, and wiring Depend edges to peer Premises — plus the transitions that move a Premise through its lifecycle without tearing down any worktree: claim a Submitted or Returned Premise, resolve it as delivered or abandoned, and return it to the pickup pool. Authoring has two shapes: an agent composes the humble-snapshot description, or — for a tangent, a side-concern the operator captures without working it out — `vv tangent` composes a provisional body deterministically from a fixed set of captured fields, with no composition step. It also owns the read primitives skills use to navigate the existing graph: fetch a Premise, append commentary, and list the peers a resolved Premise has unblocked. A Premise-state transition writes the tracker and a skill composes it with worktree teardown rather than coupling the two. vaudeville-pm does not spawn Bobs, tear down their worktrees, or integrate the scaffold; those concerns live in vaudeville-bobiverse and vaudeville-ringmaster respectively.

vaudeville-pm-internal vocabulary is in [vocabulary.md](vocabulary.md). The cross-context Ubiquitous Language — Bob, Premise, Route — is in `~/.vaudeville/doctrine/vocabulary.md`. The humble-snapshot shape an authored Premise takes is doctrine in `~/.vaudeville/doctrine/practice/premise-frame.md`.

## Collaborators

Two named boundaries.

**vaudeville-core** owns the anticorruption layer over the work tracker. Reads and writes — fetching Premises, transitioning their (State, Workflow) custom fields through `PROFILES` and `apply_bookkeeping`, attaching link edges, posting comments — go through core's tracker module, its issue accessors, and its lifecycle-profile constants. vaudeville-pm does not name the tracker by product; the tracker product is core's concern, hidden behind the kernel.

**vaudeville-bobiverse** (via the federated `vv` facade) carries the spawn hand-off when an authoring skill's `--spawn` chains a Bob launch onto the filed Premise. The four spawn primitives (`vv spawn-preflight`, `vv spawn-launcher`, `vv spawn-target-repo`, `vv spawn-downstream`) plus `vv current-project` and `vv project-id` are bobiverse-owned; vaudeville-pm calls them through the deployed facade rather than reaching for a Python import. The edge looks bidirectional with bobiverse but is not a cycle: each Contributor calls the *deployed* facade `vv`, which routes to a Mirror of the other Contributor's published version.

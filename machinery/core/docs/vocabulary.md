# vaudeville-core vocabulary

*This is a UL doc: terms defined in relation to one another. For framework-level UL see `~/.vaudeville/doctrine/vocabulary.md`.*

The terms vaudeville-core uses internally. Cross-context terms (**Assignment**, **Route**, **State**, **Workflow**, **Depend**, **Subtask**) are linked to the framework vocabulary, not redefined.

## Anti-corruption layer

The boundary pattern vaudeville-core is built from: a translation between a foreign system's vocabulary and Vaudeville's, with the foreign shape never escaping to a consumer. The package applies it at each foreign system it touches: the project tracker (issue dicts, custom fields, link directions, opaque project ids), git hosting (clone URLs, working-tree layout), and the host config file (its TOML grammar, the `yt_id` spelling). Consumers stay on the Vaudeville side, speaking Assignments, States, Workflows, Routes, Depend edges, and Component short-names. The tracker backend is YouTrack; the boundary is structured so a different backend swaps in behind it without consumers noticing.

## Predicate

A pure function `Assignment → bool`. Predicates compose with `apply_predicates`. The pickability stack (today just `deps_satisfied`) is built out of these.

## AssignmentRef

A pointer to another Assignment surfaced from an Assignment's link fields. The `state_resolved` flag is denormalised onto the ref so dependency [Predicates](#predicate) do not require a second fetch per ref. The fields are deliberately thin: a ref is for graph traversal, not for the full record.

## Comment

A unit of discussion that accumulated on an **Assignment**'s thread: an author display name, the comment text, and the creation stamp (epoch milliseconds). The read path captures every comment faithfully and filters none (including vaudeville-core's own [Bookkeeping](#bookkeeping) and closeout comments) because which comments are worth surfacing into a Brief is a downstream rendering judgement, not the boundary's. The fields are deliberately thin, like [AssignmentRef](#assignmentref): enough to attribute the thread, not the full tracker record.

## Request

A described-but-unperformed call to a foreign system, captured as a value: an HTTP method, an API path, an optional JSON body, optional query params, and whether a 404 means "no such entity" rather than a failure. The read and write paths are pure functions that build a Request from Vaudeville values; one interpreter performs it and hands back the raw response. Holding the call as data is what lets the boundary's logic be tested with plain values and asserted on without touching the network: the split [Bookkeeping](#bookkeeping) draws and every read and write path shares. The fields are HTTP-shaped because the [anti-corruption layer](#anti-corruption-layer)'s tracker backend is YouTrack's REST API; what crosses to the interpreter is data, never behaviour.

## ExitProfile

The State + Workflow + Assignee transition kit a closing skill drives an Assignment through. Each profile binds a (State, Workflow) pair, whether to unassign, and a comment-header convention: empty when the close leaves no tracker comment. vaudeville-core exposes four: **DELIVERED**, **ABANDONED**, and **RETURNED** for the terminal dispositions, and **UNCLAIM** for releasing a claim back to the pickup pool. A closing skill maps each of its dispositions onto a profile; a disposition that leaves no tracker trail drives none. The bound (State, Workflow) values are themselves UL: `Delivered`, `Abandoned`, `Returned`, `Active`, `Ready`, and `Submitted` are values of the cross-context State and Workflow vocabularies.

## Bookkeeping

The composite write that closes an Assignment: post the synopsis comment, patch State/Workflow/Assignee. `apply_bookkeeping` does both; `apply_transition` does only the field write (the no-record path used for dispositions whose semantic is "leave no tracker trail"). Every Contributor that closes an Assignment drives the close through one of these two entry points.

## Current reading

A registered Component's source as it currently, canonically is, handed to a caller for the span of one read. A Bob reads sibling Components (a peer Component, the doctrine repo) for cross-context; a Current reading makes that read *current by construction*, rather than trusting a long-lived local clone that may have drifted from the Component's canonical history. The caller names the Component by prefix (`current_reading_of_component`); resolving where the Component's canonical history lives is the register's job, and how the reading is materialised and torn down is vaudeville-core's; neither the location nor a git URL surfaces to the caller. The coordinate is the Component, never a raw repository address.

# vaudeville-core vocabulary

*This is a UL doc — terms defined in relation to one another. For framework-level UL see `~/.vaudeville/doctrine/vocabulary.md`.*

The terms vaudeville-core uses internally. Cross-context terms — **Premise**, **Route**, **State**, **Workflow**, **Depend**, **Subtask** — are linked to the framework vocabulary, not redefined.

## Shared kernel

The DDD sense of the term. A single module that every other module in the system imports from and that imports from none of them. In Vaudeville the shared kernel is this package; it carries the cross-context UL as Python value types and the boundary class that adapts the tracker to those types. Every other Contributor's source imports from here; this source imports from no other Contributor.

## Anti-corruption layer

The boundary that translates between the project tracker's vocabulary (issue dicts, custom fields, link directions, opaque project ids) and Vaudeville's vocabulary (Premises, States, Workflows, Routes, Depend edges, project short-names). Consumers stay on the Vaudeville side; the tracker shape never escapes the boundary. Today the foreign side is YouTrack; the boundary is structured so a different backend could be swapped behind it without consumers noticing.

## Predicate

A pure function `Premise → bool`. Predicates compose with `apply_predicates`. The pickability stack (today just `deps_satisfied`) is built out of these.

## PremiseRef

A pointer to another Premise surfaced from a Premise's link fields. The `state_resolved` flag is denormalised onto the ref so dependency [Predicates](#predicate) do not require a second fetch per ref. The fields are deliberately thin: a ref is for graph traversal, not for the full record.

## Comment

A unit of discussion that accumulated on a [Premise](https://github.com/somehowsoftware/vaudeville-config/blob/main/vocabulary.md#premise)'s thread: an author display name, the comment text, and the creation stamp (epoch milliseconds). The read path captures every comment faithfully and filters none — including the kernel's own [Bookkeeping](#bookkeeping) and closeout comments — because which comments are worth surfacing into a Brief is a downstream rendering judgement, not the boundary's. The fields are deliberately thin, like [PremiseRef](#premiseref): enough to attribute the thread, not the full tracker record.

## ExitProfile

The State + Workflow + Assignee transition kit a closing skill drives a Premise through. Each profile binds a (State, Workflow) pair and a comment-header convention. The kernel exposes three canonical instances — **DELIVERED**, **ABANDONED**, **RETURNED** — that correspond to the cross-context terminal dispositions; a Contributor's `/closeout` dispatch table extends the canonical set with its own local instances (e.g. bobiverse's `unclaim` and `none`). The (State, Workflow) pair each canonical profile binds is itself UL — `Delivered`, `Abandoned`, `Returned` are values of the cross-context State/Workflow vocabulary.

## Bookkeeping

The composite write that closes a Premise: post the synopsis comment, patch State/Workflow/Assignee. `apply_bookkeeping` does both; `apply_transition` does only the field write (the no-record path used for dispositions whose semantic is "leave no tracker trail"). Every Contributor that closes a Premise drives the close through one of these two entry points.

## Current reading

A registered project's source as it currently, canonically is, handed to a caller for the span of one read. A Bob reads sibling projects — a peer Managed Repository, the doctrine repo — for cross-context; a Current reading makes that read *current by construction*, rather than trusting a long-lived local clone that may have drifted from the project's canonical history. The caller names the project by prefix (`current_reading_of_project`); resolving where the project's canonical history lives is the register's job, and how the reading is materialised and torn down is the kernel's — neither the location nor a git URL surfaces to the caller. The coordinate is the project, never a raw repository address.

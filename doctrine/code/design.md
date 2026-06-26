# Design

How to move from a problem to code. The principles in [architecture](./architecture.md) govern the shape of the resulting code; the principles here govern what happens before any code is written.

## The system is pieces and interactions

A *piece* is a domain noun: something the [vocabulary](../vocabulary.md) already names or is about to name. A subprocess invocation is not a piece but implementation; the piece is the domain concept the subprocess implements.

An *interaction* is a domain verb between pieces: a runtime relationship one piece bears on another, whose outcome can be described in a sentence the domain understands. Each interaction has a contract: the property that holds for the result given the inputs.

Contracts are the unit of design. Before any module exists, the pieces can be named, the interactions enumerated, and the contracts stated in domain terms on one screen. If a contract cannot be stated in domain terms, either the domain model is not sharp enough or the design has wandered into implementation. Stop, sharpen, return.

## The contracts are the tests

A behavioural test is a contract made executable: *given pieces X and Y, an interaction Z produces a result with property P.* Tests are written before the modules they describe and named for the contracts they assert. The test suite, read as a list, is the system's spec at the unit-of-domain-promise level.

This applies the layering principle in [intent](./intent.md) to the sequencing of work: low-level WHAT belongs in tests, tests come first, and modules are written to make the tests pass, not invented in advance and tested retroactively.

A contract stays executable as a unit test only when the core it describes is handed its locations and its I/O as values. Where a test needs real I/O to exercise otherwise-pure logic, the contract is bound to a boundary that has not been injected; [fail-safe over fail-deadly](./architecture.md#fail-safe-over-fail-deadly) is where that boundary belongs.

## Modules own pieces, not orchestration

Each module implements exactly one piece and is named for it. Its job is what the piece's interactions require, nothing else. An *orchestrator* module that threads state through several phases on behalf of several pieces is a smell: each phase belongs to a piece, and the orchestrator is a piece-shaped vacancy waiting for a name. Find the missing piece and name it; do not paper over the gap with a "does several things" module.

A function whose body is twenty lines of branching and state-threading is the same smell at function scale. Name each phase, make each phase a function named for it, and have each function delegate to a piece for the work.

## Names are domain names

Every public name (module, function, type, variable) comes from the ubiquitous language. A name using a verb the domain does not use (`_resolve_*`, `_handle_*`, `_process_*`, `_get_or_create_*`) means the author has not yet found the domain's word for what the function does. Find the word, or grow the [vocabulary](../vocabulary.md) to include it; do not write the function with the placeholder.

Internal helpers obey the same rule; the discipline holds at every visibility level.

## Findings during design surface in the vocabulary

If the piece-and-interaction pass finds a piece with no name in the ubiquitous language, the finding is the missing name. Add the term to the cross-context [vocabulary](../vocabulary.md) (or the relevant Context's UL doc), then continue.

## Build the smallest thing that serves the goal

A *named abstraction standing in for nothing* (a module, dataclass, error type, or validate-then-act split invented because the code might one day want it) is the common failure. Build the smallest thing that serves the stated goal. Add no structure, validation, error type, or [vocabulary](../vocabulary.md) entry the goal does not demand. When the goal grows one, the design pass announces it; until then, a name with no piece under it is scope the next author must read, understand, and maintain for nothing.

A guard against a precondition the next operation already enforces is invention of this kind: a second copy of an invariant, drifting from the first the moment either side changes. [fail early and loudly](./architecture.md#fail-early-and-loudly) is where that line is drawn.

Review pressure pushes the same way. A reviewer's local observation is correct about the line it names and silent about the goal; it is not licence to widen scope to a hypothetical case the comment imagines. Serve what the goal needs, answer the rest with why the case does not arise, and leave the abstraction unbuilt.

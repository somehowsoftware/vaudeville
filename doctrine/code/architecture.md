# Architecture

How we structure the system: how modules are bounded and communicate, and how the codebase becomes easier to work in over time.

## Suppleness is the standard

The measure of any change is whether the codebase is now easier to extend, understand, and maintain, and better at surfacing defects. Line counts and coverage metrics do not measure this; reading the code does.

The framing is tech surplus, not debt reduction. A subsystem in tech-surplus state is one where every remaining improvement is beyond the ceiling of what the current author and reviewer can reliably catch in a single change. The standard is that the next change will be easier than the last; every change is either a deposit on that surplus or a withdrawal from it.

## Single responsibilities; loose coupling; tight boundaries

Each module has one job, defined in terms of the systems it delegates to; how it does that job is its own business. Parents do not reach into children's internals, and children do not know their grandparents.

Modules communicate through well-defined types, and those types are the contracts, so internals can change without rippling outward. A cowardly name like `utils`, `helpers`, or `common` signals a concept not yet named; name it or reorganize until the cowardly name is unneeded.

## Production by default

Every line of code is production code unless explicitly designated a spike, with the prior commitment that the spike will never see the light of day. Spikes that prove valuable are rewritten as production code, without exception.

## Correctness over expedience

When the correct path and the quick-but-debted path are both reachable now, take the correct one. This is not "no tech debt ever" — some debt is forced by circumstance — but self-imposed debt is refused even when it looks like it saves time.

The rule applies to process as it applies to code. A shortcut around review, against branch protection, or through the production line — even one that would unblock something useful — is refused the same way.

Look before you build: search for a maintained library before hand-rolling framework code.

## Fail early and loudly

When a situation that should not be possible occurs, the system fails — visibly, immediately, with a diagnostic that names the violation. Silently ignoring an impossibility is not "robust".

Robustness is reserved for failures we expect, which by definition means failures of *some other system* — a network or I/O call, a malfunctioning external API, an upstream service rate-limiting. Violations of our own invariants abort with a clear diagnostic before further work is done.

## Fail-safe over fail-deadly

[Fail early and loudly](#fail-early-and-loudly) surfaces a violation that has already happened; this sibling principle sets the direction of failure before anything happens — which way a boundary fails when someone forgets to wire it at all.

A boundary that resolves a real production location — the live-data directory, a deployment target, a credential store, the process environment, any locator naming where real state lives — is supplied from the composition root, the program's outermost edge where its real locations are chosen and passed inward. It carries no default; an operation receives the location it acts on as an argument and resolves none for itself.

This makes the direction of failure structural rather than a matter of care: forgetting to supply an injected, defaultless boundary stops the operation and the omission shows immediately — fail-safe — while forgetting to override a boundary that defaults to production runs the operation against production — fail-deadly. Injection makes clobbering production by default impossible to express.

This pairs with a functional core and an imperative shell: the pure core takes values, and all I/O lives in a thin shell injected at the same edge. A test that reaches real I/O — filesystem, network, process state such as the environment or command line — to exercise otherwise-pure logic signals a boundary still resolved inside the logic rather than injected; the repair is the interface, not a sandbox around the test.

## Main is the production line

[Production by default](#production-by-default) says every line is production code; the corollary at the commit level is that every commit to `main` is a production deposit. Main is what every Bob's spawn pulls from and every release ships from.

This forbids the agent merging to main directly, merges that bypass branch protection or review, force-pushes that rewrite landed history, and fixes landed solely to unblock a downstream step (a pipeline, an integration test) when the right answer is to fix that step.

Branch protection is a backstop, not the rule. The rule is the discipline.

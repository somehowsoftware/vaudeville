# vaudeville-core — spec

*This is a spec — high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code.*

vaudeville-core is the **shared kernel** of the Vaudeville constellation. It carries the cross-context Ubiquitous Language as Python value types (Premise, PremiseRef, Comment, ExitProfile, the canonical lifecycle profiles, the predicate signature) and it is the **anti-corruption layer** over the project tracker — consumers speak Vaudeville primitives, the kernel hides everything tracker-shaped. It also owns the project register (the tenant's projects, keyed by Premise prefix) and gives a caller a **Current reading** of any registered project — its source as it currently, canonically is — so a cross-repo read is current by construction. It ships no skills and no `vv` subcommands of its own.

Core-internal vocabulary is in [vocabulary.md](vocabulary.md). The cross-context Ubiquitous Language — Premise, Route, State, Workflow, Depend, Subtask — is in `~/.vaudeville/doctrine/vocabulary.md`.

## Collaborators

Four named boundaries.

**vaudeville-bobiverse** consumes the kernel's read paths (`find_premises`, `get_premise`), the lifecycle-profile constants (`DELIVERED`, `ABANDONED`, `RETURNED`), the `apply_bookkeeping` mechanism, and the predicate primitives. Its `/closeout` builds a local disposition dictionary over the kernel constants plus its own private dispositions; its `spawn-preflight` mirrors the pickability filter the kernel defines.

**vaudeville-pm** consumes the same read and write surface — `find_premises`, the predicates and `apply_predicates`, `apply_bookkeeping` (its `/onward` closes a Premise as Delivered through this entry point), and the mutation primitives that author Premises and attach link edges.

**vaudeville-cue** consumes the kernel for read-only access to a Premise it primes a Bob on. The `vv premise-context` command core's siblings invoke at spawn is cue's; what it reads through is the kernel's.

**The project tracker** is the foreign system on the far side of the anti-corruption layer. Today YouTrack; the boundary is the `_youtrack` private client and the `_issue_adapter` accessors. Consumers do not see issue dicts.

## Cross-Contributor import discipline

vaudeville-core depends on no Vaudeville Contributor. The dependency arrows all point inward. Cross-Contributor calls at runtime go through Ringmaster's federated `vv` facade, never through Python imports between Contributor packages. The kernel is the only Vaudeville package a Contributor's source imports directly.

When a Contributor finds itself wanting to name another Contributor's private vocabulary in its own spec or skill, the question is whether that vocabulary belongs in the kernel (because it is in fact UL across contexts) or whether the prose should route around it (because it is not). The kernel surface is conservative; lifting requires a real cross-context need, not convenience.

## Release-time fan-out

At release time the picture has a second axis. Core's CI fans out `repository_dispatch` events to every Contributor on `v*` tag publish, so Contributors' lockfiles refresh against the new wheel without manual intervention. This is a runtime trigger, not a Python import — the deps-point-inward property is unaffected. The mechanism is illustrated in [diagrams/auto-bump-fan-out.svg](diagrams/auto-bump-fan-out.svg); the source of truth is the `fan-out` job in `.github/workflows/ci.yml` and each Contributor's `core-bump.yml`.

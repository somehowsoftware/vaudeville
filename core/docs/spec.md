# vaudeville-core: spec

*This is a spec: high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code.*

vaudeville-core is the anti-corruption layer between Vaudeville and the foreign systems it runs against: the project tracker, git hosting, and the host config file. Consumers speak Vaudeville primitives (Assignment, AssignmentRef, Comment, ExitProfile, the canonical lifecycle profiles, the predicate signature, the Tracker schema and provisioning) and the boundary hides everything the foreign systems are shaped like. It sits at the system's edge: the package every other Contributor reaches *through* to touch anything outside Vaudeville. The name says `core`; the role is the periphery.

It ships no skills and no `vv` subcommands of its own. Its tenant-facing executable surface is the provisioning primitive — `provision`, exposed from the package root and runnable as a script, which stands a Component's tracker up to the schema core carries — and the essential-defaults script, which sets the canonical Vaudeville-essential field defaults across registered projects; everything else is a library the Contributors import.

Core-internal vocabulary is in [vocabulary.md](vocabulary.md). The cross-context Ubiquitous Language (Assignment, Route, State, Workflow, Depend, Subtask) is in `~/.vaudeville/doctrine/vocabulary.md`.

## Foreign systems

Three systems sit on the far side of the boundary; consumers reach each only through Vaudeville primitives.

**The project tracker** holds Vaudeville's lifecycle state, and vaudeville-core is the package that does anything to it: both the issue surface (find, read, create, transition, comment, link) and the admin surface that provisions a new tracker project to the schema core carries — its custom fields, their ordered values, the canonical defaults, and the Depend link type — reproducing that schema from core's own data with no reference project to clone, and sets the canonical Vaudeville-essential field defaults on a project that already exists. Acting on the tracker is this package's ordinary work; mutating it (its issues and its live configuration alike) is not a fraught act. Unease that attaches to the surface itself, merely because the live tracker is what is being changed, is misplaced; a specific reservation about a particular change is a real signal and stands on its own. The backend is YouTrack; the boundary is structured so a different backend swaps in behind it without consumers noticing. Consumers never see an issue dict.

**git hosting** is reached two ways: a Current reading hands a caller a registered Component's canonical source for the span of one read (a fresh clone of its remote tip) and the working-tree resolver names the current Component from a git root. Neither a clone URL nor a temporary path surfaces to the caller.

**The host config file** (`~/.vaudeville/vaudeville.toml`) is the tenant's Component register, read behind a private grammar that never escapes the module. It answers which Components the tenant has, keyed by Assignment prefix, translating the file's spellings into domain values.

## Consumers

Three Contributors import the boundary.

**vaudeville-bobiverse** consumes the read paths (`find_assignments`, `get_assignment`), the lifecycle profiles (`DELIVERED`, `ABANDONED`, `RETURNED`, `UNCLAIM`), the `apply_bookkeeping` mechanism, and the predicate primitives. Its `/closeout` maps its dispositions onto the boundary's profiles; its `spawn-preflight` mirrors the pickability filter the boundary defines.

**vaudeville-pm** consumes the same read and write surface: `find_assignments`, the predicates and `apply_predicates`, `apply_bookkeeping` (its `/onward` closes an Assignment as Delivered through this entry point), and the mutation primitives that author Assignments and attach link edges.

**vaudeville-cue** consumes the boundary for read-only access to an Assignment it primes a Bob on. The `vv assignment-context` command the sibling Contributors invoke at spawn is cue's; what it reads through is vaudeville-core's.

## Cross-Contributor import discipline

vaudeville-core depends on no Vaudeville Contributor. The dependency arrows all point inward: every Contributor's source imports vaudeville-core, and vaudeville-core imports no Contributor. Cross-Contributor calls at runtime go through Ringmaster's federated `vv` facade, never through Python imports between Contributor packages.

When a Contributor finds itself wanting to name another Contributor's private vocabulary in its own spec or skill, the question is whether that vocabulary belongs in vaudeville-core (because it is in fact UL across contexts) or whether the prose should route around it (because it is not). The boundary's surface is conservative; lifting requires a real cross-context need, not convenience.

## Release-time fan-out

At release time the picture has a second axis. vaudeville-core's CI fans out `repository_dispatch` events to every Contributor on `v*` tag publish, so Contributors' lockfiles refresh against the new wheel without manual intervention. This is a runtime trigger, not a Python import; the deps-point-inward property is unaffected. The mechanism is illustrated in [diagrams/auto-bump-fan-out.svg](diagrams/auto-bump-fan-out.svg); the source of truth is the `fan-out` job in `.github/workflows/ci.yml` and each Contributor's `core-bump.yml`.

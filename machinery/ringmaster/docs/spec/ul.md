# Ringmaster: ubiquitous language

This is a UL doc: terms defined in relation to one another. For framework-level UL see [`vaudeville-doctrine`'s `vocabulary.md`](https://github.com/somehowsoftware/vaudeville-doctrine/blob/main/scaffold/doctrine/vocabulary.md), the universal doctrine Ringmaster itself now carries to every tenant as a Doc Tree.

Ringmaster-internal terms. Cross-context terms (Skill, Contributor, Ringmaster, Bounded Context) live in the framework-level UL and are not redefined here. Storage layout, module organization, subprocess mechanics, and the Contributor-side encoding contract live in [`architecture.md`](architecture.md), the release-candidate cycle in the [`/rehearse` skill](../../.claude/skills/rehearse/SKILL.md), and the source.

## Inputs

**Registry.** The integrator-internal declaration of which Contributor Repos make up this host's federation, shipped with Ringmaster as package data and read from beside the module. Each entry pairs a Contributor Repo's name with its remote location.

**Contributor Repo.** A repo named in the Registry. Read by Stage and Apply from its Session Clone; the Worktree substitutes for the Owning Repo's Session Clone in a Stage.

**Worktree.** Any directory inside an operator's working clone of a Contributor Repo. Stage's input: it carries the pending Contribution whose integration a Release Candidate is built to verify.

**Owning Repo.** The Contributor Repo a Worktree belongs to. The one Contributor Repo whose Contribution comes from the Worktree in a Stage; all others come from their Session Clones.

**Published Home.** The integrator-internal GitHub repository where [Publish](#publish) accumulates [Releases](#release), organized by [Release Name](#release-name). A Tenant consumes Releases from it; only the integrator publishes to it. Integrator-internal like the Registry: the name lives in the source, not in operator state. Colloquially **the vaudeville repository** (or **the vaudeville repo**): that phrase names this repository, the only one Ringmaster publishes to, so an unqualified reference to it resolves here rather than to a Contributor Repo or to Vaudeville the project.

## Session

**Session.** The bracketed span of a single deploy attempt: opened by Clone, closed by Discard. Every Stage and every Apply happens inside a Session. The scope at which Session Clones exist.

**Session Clone.** Ringmaster's working copy of a Contributor Repo for the duration of one Session. Produced by Clone, consumed by Stage and Apply, removed by Discard. Writable inside the Session as the operator's Hot-fix surface.

**Hot-fix.** An operator edit to a Session Clone made during the Stage-and-smoke loop in response to a smoke failure. Feeds the next Stage; refused by Apply via the Pristine guard.

**Pristine guard.** Apply's refusal to deploy a Session Clone the operator has modified since Clone produced it. A backstop for the operator discipline of never deploying Hot-fixes.

## Contribution slots

**Contribution.** What a Contributor Repo offers to the federation. Skills, Data Files, Doc Trees, Hook Scripts (with Hook Matchers), a CLI (its Console Script and Manifest), and the distribution that carries the CLI. Any slot may be empty.

**Data File.** A file consumed by `vv` and host Skills at runtime. Carried by the Contributor under `scaffold/.vaudeville/`, collected into the Artifact by Build, and placed as a flat file at the Destination's data dir by Install.

**Doc Tree.** A directory of documentation a Contributor publishes for agents to read at the host: the universal doctrine. A fixed, known name (`doctrine/`) a Contributor ships under `scaffold/<name>/`; Build collects it and Install places it at the matching subtree of the Destination's data dir (`scaffold/doctrine/` → `~/.vaudeville/doctrine/`). Ringmaster fully owns that subtree and rebuilds it wholesale every deploy: the same contract as the framework-owned skills and hooks directories. Where a Data File is a flat runtime file, a Doc Tree is a whole tree of prose. A tenant's project-docs is not a Doc Tree; Install copies it from the operator's config dir.

**Hook Script.** An executable fired by Claude Code at a tool-call boundary. Carried by the Contributor, collected into the Artifact by Build, and placed at a Destination by Install.

**Hook Matchers.** The Contributor-side declaration of when each Hook Script fires. Merged across Contributors into one fragment by Build and written into the Vaudeville-managed `settings.json` by Install.

**Vaudeville-managed `settings.json`.** Claude Code's `settings.json` as Install writes it: the `hooks` block (rewritten every deploy from the merged Hook Matchers) and the `autoMode` block (the auto-mode classifier's trust rules) are Ringmaster-owned and rebuilt wholesale; every other key is operator-curated and preserved. The `autoMode` block splits on universal requirement versus instance content: the framework's allowances for its own operations (spawning a Bob) are baked in and reach every tenant, while the trusted-infrastructure `environment` lines are composed from facts the tenant already states (the source-control orgs in the project map's remotes and the work tracker in credentials) rather than authored by hand. Every emitted section leads with `$defaults`, the sentinel that extends rather than replaces the classifier's built-in blocks. An operator's own `autoMode` rules live in `settings.local.json`, a scope the classifier combines and Install never writes, so the owned key needs no merge.

**Console Script.** A Python entry point a Contributor declares in `[project.scripts]`. Build reads it to find the module of a Contributor's `vv` app or its operator app: the modules the [Facade](#facade) and the [`vaudeville`](#vaudeville) CLI respectively compose.

**Manifest.** A Contributor Repo's declaration that it contributes to the federated command line, naming the `binary` whose entry point identifies its `vv` app and, optionally, the `operator_binary` whose entry point identifies its operator app for [`vaudeville`](#vaudeville). Its presence marks the Contributor as part of the command surface; Contributors with no CLI omit it, and a Contributor with a `vv` app but no operator app omits `operator_binary`. The command surface itself is whatever the apps define; Ringmaster reads it from them, never from a hand-maintained list.

## Build and Install

**Artifact.** The self-contained, destination-ignorant installable unit Build produces and Install consumes. It carries the integrated Skills, Data Files, Hook Scripts, the merged Hook-Matcher fragment, and the integrated command line as installable code. It reads back into no Session Clone and no source tree, and carries the Vaudeville packages it needs as wheels, so the common half need fetch nothing but public PyPI to install it anywhere. The seam between the proprietary Build half and the common Install half. It carries the [Installer](#installer) that places it, so the Artifact is self-installing: a party holding the Artifact installs from it without the proprietary integrator present. When [Publish](#publish) ships it, the same unit is a [Release](#release)'s versioned download in the [Published Home](#published-home), what a Tenant pins to and installs from: the same unit Apply instead installs to *this* host.

**Installer.** The common Install half embodied as an executable carried inside the [Artifact](#artifact): scaffold placement plus the post-install orchestration that leaves a Host deployable-from. Activating it against a [Destination](#destination) produces a Scaffold: Build carries it, a Tenant activates it, and the proprietary integrator is absent at install time. The Installer is its own distribution so it can be activated against an Artifact with nothing else of Vaudeville present; the integrator depends on it, never the reverse.

**Destination.** Where Install places an Artifact. Two: **Host**, the operator's machine, the installation locations across `~/.claude`, `~/.vaudeville`, and `~/.local`, where Install preserves operator-curated state; and **Staging**, a single throwaway root that stands in for the Host so the operator can smoke-test before Apply, built fresh each Stage and mirroring the Host's own Claude state so the smoke is faithful.

**Facade.** The deployed `vv`: the single command-line tool a tenant runs. Build composes it from the Contributor CLI apps and Install installs it; it presents their commands as one surface and routes each in-process to the owning app, refusing to serve a federation whose apps collide on a subcommand name. The Contributor decomposition does not survive into it, so a tenant never depends on Vaudeville's internal package structure, which Vaudeville is free to change.

**`vaudeville`.** The operator-facing CLI Install places alongside `vv`. Composed exactly as the [Facade](#facade) is: from each Contributor's operator app (named by the Manifest's `operator_binary`), unioned by the same dispatcher under its own program name, so operator commands live in their Contributors, not in Ringmaster. A curated surface deliberately separate from `vv` and expected to diverge from it; a Contributor that declares no operator app contributes nothing to it.

## Operations

A Session is the bracketed sequence Clone → Stage (one or more, smoke-tested between) → Apply → Discard. Clone and Discard frame the Session; Stage and Apply read the Session Clones inside it. Stage and Apply share one pipeline (Assemble, Build, Install) and differ only in the Destination.

**Clone.** The operation that opens a Session: discards any leftover Session Clones, then fresh-clones each Registry-named Contributor Repo's `origin/main`. Required before Stage or Apply.

**Stage.** The pre-deploy verification operation: assembles a Release Candidate from a Worktree, builds it into an Artifact, and activates the Artifact's carried installer to place a Staging Scaffold the operator can audit and smoke-test. Re-runnable within a Session so a Hot-fix can iterate.

**Apply.** The deployment operation: assembles the Apply Plan from the Session Clones, builds it into an Artifact, and hands the Artifact to its carried installer for the Host Destination. The installer places the Host Scaffold and runs the Integrity check, the host-wiring check, and Foundation priming that together leave the host deployable-from. Subject to the Pristine guard, enforced in Apply before Build.

**Publish.** The operation that cuts a [Release](#release) from the current [Pinned Set](#pinned-set) and publishes it to the [Published Home](#published-home): it builds from the Session Clones as Apply does, but where Apply installs to *this* host, Publish ships the Release (its [Artifact](#artifact) as the versioned download) to *other* Tenants. It also renders the Release's [Exposition](#exposition) and writes it into the Published Home as one labeled commit, then tags the Release at that commit, so the install Artifact and its readable companion share one [Release Name](#release-name) and one commit. The Exposition is committed before the tag, so a failure after it leaves an untagged commit the next Publish supersedes rather than a Release with no readable companion. Subject to the Pristine guard: a Release carries only reviewed, merged code.

**Discard.** The operation that closes a Session: removes the Session Clones so no leftover state can be mistaken for an input by a future Session.

**Assemble.** The read-only first phase of Apply or Stage: load the Registry, require each Session Clone to exist, discover each Contribution (Stage substituting the Worktree for the Owning Repo), produce and validate an Apply Plan. Where a federation that collides on a Skill name is rejected (a subcommand collision is caught later, by the composed `vv`, on the apps' real command names); never writes to a Destination.

**Build.** The proprietary phase: integrate the Apply Plan and the Contributor sources into an Artifact. The Contributor decomposition dissolves here: the integrated command line is carried as one installable unit built from source, resolvable against public PyPI alone, alongside the [Installer](#installer) that places it. `ringmaster build` emits a durable Artifact; Stage and Apply build one in passing and activate its installer.

**Install.** The common phase: place an Artifact at a Destination, producing a Scaffold. Embodied by the [Installer](#installer) carried in the Artifact and activated with `uv`; resolves the carried command line from the Artifact's wheels and public PyPI. Every tenant runs Install; only Vaudeville-the-project runs Build.

**Apply Plan.** The validated value Assemble produces from all Contributions: the integrated offering of the whole federation, checked for Skill-name collisions. Build consumes it.

**Audit.** The cheap, deterministic structural walk of a Staged Scaffold. Inspects; it does not exercise. The end-to-end exercise of an assembled scaffold is the manual lifecycle smoke in the [`/rehearse` skill](../../.claude/skills/rehearse/SKILL.md), not a UL term.

**Integrity check.** The carried installer's verification, during a Host install, that the placed Host Scaffold is actually deployable-from, in two parts on opposite sides of the Contributor boundary. The command surface is Ringmaster's own; it asks the installed `vv` to self-report its composed surface, so a stale or hand-maintained `vv` is caught; this runs before priming, since priming itself invokes `vv`. Foundation durability belongs to vaudeville-bobiverse, so after priming it is delegated to that Contributor's `vv foundations-verify`. Where the [Audit](#audit) inspects a Staged Scaffold before deploy, the Integrity check verifies the Host Scaffold after it; either part aborts Apply loudly rather than leaving a host whose first Spawn or `vv` call fails downstream.

**Host-wiring check.** The carried installer's verification during a Host install, alongside the [Integrity check](#integrity-check), of the host *environment* `vv spawn`/`vv fork` reach past the scaffold for: the tenant's YouTrack is *located* (configured in `credentials.toml` and the instance reachable) and Workmux (the worktree/tmux multiplexer Spawn shells out to) is *present and runnable*. Runs before priming and aborts Apply loudly, turning a fresh host's missing YouTrack or Workmux into a deploy-time failure instead of a first-Spawn failure. The bar is wiring, not Contributor semantics: credential validity and a real `workmux add` are deeper, Contributor-owned checks left to a future `vv`-side probe.

## Release

**Pin.** One Contributor Repo frozen at a single commit: a Contributor Repo's name, its remote, and the exact commit its [Session Clone](#session-clone) was produced at, read from the clone-time sidecar. The atom of a Release's identity. A Pin cannot exist without a commit: a directory carrying no recorded clone-time commit is not a Pin, because it was not produced by [Clone](#clone), and [Provenance](#provenance) refuses to vouch for a commit it cannot establish.

**Pinned Set.** The whole federation frozen at gather time: one [Pin](#pin) per Contributor Repo. The value that exists from the moment [Clone](#clone) opens a [Session](#session), before anything is built or published: *what a Release is made of*. A [Release](#release) is a published Pinned Set, so the unpublished frozen value and the published thing are one concept in two states. Distinct from the [Apply Plan](#apply-plan): the Apply Plan is the integrated *offering* Assemble derives for Build; the Pinned Set is the *identity*: which Contributor Repos at which commits.

**Carried Set.** The subset of a [Pinned Set](#pinned-set) whose source actually ships inside the [Artifact](#artifact): the command-surface Contributors and the libraries they share, as built wheels or scaffold slots. The integrator is excluded: it is the [Builder](#builder), not a payload. What [Provenance](#provenance) vouches for, as against the whole constellation an [Exposition](#exposition) renders.

**Release.** A [Pinned Set](#pinned-set) published under a [Release Name](#release-name): the integrated whole as a versioned, published thing, identified by what it was built from. It *emits* an [Artifact](#artifact) (its download), an [Exposition](#exposition) (its reading copy), and a [Provenance](#provenance) (its build-truth), and is published as a git tag at the Exposition commit. The released whole, distinct from any one of its emissions: the noun the retired "Published Version" lacked, having named one emission, the install Artifact, as though it were the whole.

**Release Name.** A [Release](#release)'s synthetic, release-level CalVer identity (`vYYYY.MM.DD.N`): a version axis naming the integrated release as a whole, separate from any one Contributor's version and from Ringmaster's, with the Artifact's inner wheels keeping their own. One value, of which the git tag, the release title, the commit-message prefix, and the download's filename are all *stampings*. The next Release Name is today's CalVer stem with the lowest counter not already taken in the [Published Home](#published-home)'s tag namespace; the tag namespace is read because that is the storage the tag reuses, even though the fact it establishes is "this Release Name is not yet taken."

**Predecessor.** The previously published [Release](#release): the one a new Release is the next after, resolved from the [Published Home](#published-home)'s tag namespace. The thing "the last release" names.

**Changeset.** The difference between a [Release](#release) and its [Predecessor](#predecessor): per Contributor Repo, the Contributions merged between the Predecessor's [Pin](#pin) and this Release's Pin. Because the federation squash-merges, each such commit is exactly one merged pull request, so a Changeset reads as a set of merged pull requests across the Contributors.

**Release Notes.** The human-readable synthesis of a [Changeset](#changeset): what changed since the [Predecessor](#predecessor), read across the Contributors. Named here as the work it describes; not yet a built operation.

**Provenance.** The authoritative record of what a [Release](#release)'s [Artifact](#artifact) was built from: its [Carried Set](#carried-set) together with its [Builder](#builder). The *value*; the `provenance.toml` written at the [Exposition](#exposition)'s root is its serialization, not the concept. Per carried Contribution it records the repository and the exact commit, the [Pin](#pin)'s commit; the integrator never appears as a carried Contribution, because it is the Builder, recorded separately. The build-truth that lets the Exposition stay an unapologetically curated reading copy: what a Release shipped lives here, not in the rendered tree.

**Builder.** The integrator identity and version that built a [Release](#release): the [Facade](#facade) it stamped and the installer it built, recorded by its running version (`vaudeville_ringmaster` and `vaudeville_install`). Recorded in the [Provenance](#provenance), never itself a [Pin](#pin): the integrator is what builds the Release, not a payload in its [Carried Set](#carried-set). It appears in the [Exposition](#exposition) as `machinery`, exactly where it is absent from the Provenance's carried record.

## Outputs

**Release Candidate.** Stage's verification picture: a [Pinned Set](#pinned-set) with the Owning Repo's [Pin](#pin) replaced by a [Worktree](#worktree): the Worktree's pending Contribution for the Owning Repo + every other Contributor Repo's Session Clone state. Structurally identical to what Apply would deploy from the same Session Clones if Stage had not substituted the Worktree. For *verification*, not consumption: distinct from a published [Release](#release), and not itself fully pinned, since the substituted member is a live Worktree rather than a Pin.

**Host Scaffold.** The result of Install at the Host Destination: a multi-location end-state defined by the host's installation contracts, not a single directory.

**Staged Scaffold.** The result of Install at a Staging Destination: a single self-contained root the operator audits and smoke-tests without touching the Host Scaffold. The Audit reads it directly.

**Exposition.** A [Release](#release)'s for-reading rendering of its assembled source. The relevant parts of each Contributor are gathered into one curated tree of [Sections](#section), with the universal Doctrine as its own Section: its `src`, any workspace `packages` it ships (such as vaudeville-ringmaster's carried installer), its own `scaffold`, its `docs`, its `README`. A reading copy, deliberately *not* the build input: it is reorganized into Sections, trimmed of tests, tooling, lockfiles, and history, and regenerated whole each Publish. What the Release was actually built from is its [Provenance](#provenance), placed at the Exposition's root, not the rendering. [Publish](#publish) commits the Exposition in the [Published Home](#published-home) and tags the Release there, so a reader browses the whole constellation at the Release's tag without cloning each Contributor Repo. But that committing is an act Publish performs on the Exposition, not part of what the Exposition is. Distinct from the [Artifact](#artifact), which carries the same code as built wheels rather than readable source.

**Section.** A top-level grouping within an [Exposition](#exposition) naming the role its members play in the constellation: `subsystems` (the lifecycle Contributors), `doctrine` (the universal Doctrine prose), `machinery` (the integrator and the boundary Contributor). The placement of each Contributor into a Section is editorial, declared in the Exposition's layout and validated to cover exactly the [Registry](#registry), so a newly registered Contributor forces a placement decision rather than being silently dropped from the rendering.
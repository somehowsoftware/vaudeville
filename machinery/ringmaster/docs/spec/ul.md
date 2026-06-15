# Ringmaster — ubiquitous language

This is a UL doc — terms defined in relation to one another. For framework-level UL see [`vaudeville-doctrine`'s `vocabulary.md`](https://github.com/somehowsoftware/vaudeville-doctrine/blob/main/scaffold/doctrine/vocabulary.md), the universal doctrine Ringmaster itself now carries to every tenant as a Doc Tree.

Ringmaster-internal terms. Cross-context terms — Skill, Contributor, Ringmaster, Bounded Context — live in the framework-level UL and are not redefined here. Storage layout, module organization, subprocess mechanics, and the Contributor-side encoding contract live in [`architecture.md`](architecture.md), the release-candidate cycle in the [`/rehearse` skill](../../.claude/skills/rehearse/SKILL.md), and the source.

## Inputs

**Registry.** The integrator-internal declaration of which Contributor Repos make up this host's federation, shipped with Ringmaster as package data and read from beside the module. Each entry pairs a Contributor Repo's name with its remote location.

**Contributor Repo.** A repo named in the Registry. Read by Stage and Apply from its Session Clone; the Worktree substitutes for the Owning Repo's Session Clone in a Stage.

**Worktree.** Any directory inside an operator's working clone of a Contributor Repo. Stage's input — it carries the pending Contribution whose integration a Release Candidate is built to verify.

**Owning Repo.** The Contributor Repo a Worktree belongs to. The one Contributor Repo whose Contribution comes from the Worktree in a Stage; all others come from their Session Clones.

**Published Home.** The integrator-internal GitHub repository where [Publish](#publish) accumulates [Published Versions](#published-version), organized by version. A Tenant consumes versions from it; only the integrator publishes to it. Integrator-internal like the Registry — the name lives in the source, not in operator state.

## Session

**Session.** The bracketed span of a single deploy attempt: opened by Clone, closed by Discard. Every Stage and every Apply happens inside a Session. The scope at which Session Clones exist.

**Session Clone.** Ringmaster's working copy of a Contributor Repo for the duration of one Session. Produced by Clone, consumed by Stage and Apply, removed by Discard. Writable inside the Session as the operator's Hot-fix surface.

**Hot-fix.** An operator edit to a Session Clone made during the Stage-and-smoke loop in response to a smoke failure. Feeds the next Stage; refused by Apply via the Pristine guard.

**Pristine guard.** Apply's refusal to deploy a Session Clone the operator has modified since Clone produced it. A backstop for the operator discipline of never deploying Hot-fixes.

## Contribution slots

**Contribution.** What a Contributor Repo offers to the federation. Skills, Data Files, Doc Trees, Hook Scripts (with Hook Matchers), a CLI (its Console Script and Manifest), and the distribution that carries the CLI. Any slot may be empty.

**Data File.** A file consumed by `vv` and host Skills at runtime. Carried by the Contributor under `scaffold/.vaudeville/`, collected into the Artifact by Build, and placed as a flat file at the Destination's data dir by Install.

**Doc Tree.** A directory of documentation a Contributor publishes for agents to read at the host — the universal doctrine. A fixed, known name (`doctrine/`) a Contributor ships under `scaffold/<name>/`; Build collects it and Install lands it at the matching subtree of the Destination's data dir (`scaffold/doctrine/` → `~/.vaudeville/doctrine/`). Ringmaster fully owns that subtree and rebuilds it wholesale every deploy — the same contract as the framework-owned skills and hooks directories. Where a Data File is a flat runtime file, a Doc Tree is a whole tree of prose. A tenant's project-docs is not a Doc Tree; Install copies it from the operator's config dir.

**Hook Script.** An executable fired by Claude Code at a tool-call boundary. Carried by the Contributor, collected into the Artifact by Build, and placed at a Destination by Install.

**Hook Matchers.** The Contributor-side declaration of when each Hook Script fires. Merged across Contributors into one fragment by Build and written into the Vaudeville-managed `settings.json` by Install.

**Vaudeville-managed `settings.json`.** Claude Code's `settings.json` as Install writes it: the `hooks` block is Ringmaster-owned and rewritten every deploy from the merged Hook Matchers; every other key is operator-curated and preserved.

**Console Script.** A Python entry point a Contributor declares in `[project.scripts]`. Build reads it to find the module of a Contributor's `vv` app or its operator app — the modules the [Facade](#facade) and the [`vaudeville`](#vaudeville) CLI respectively compose.

**Manifest.** A Contributor Repo's declaration that it contributes to the federated command line, naming the `binary` whose entry point identifies its `vv` app and, optionally, the `operator_binary` whose entry point identifies its operator app for [`vaudeville`](#vaudeville). Its presence marks the Contributor as part of the command surface; Contributors with no CLI omit it, and a Contributor with a `vv` app but no operator app omits `operator_binary`. The command surface itself is whatever the apps define — Ringmaster reads it from them, never from a hand-maintained list.

## Build and Install

**Artifact.** The self-contained, destination-ignorant installable unit Build produces and Install consumes. It carries the integrated Skills, Data Files, Hook Scripts, the merged Hook-Matcher fragment, and the integrated command line as installable code. It reads back into no Session Clone and no source tree, and carries the Vaudeville packages it needs as wheels — so the common half need fetch nothing but public PyPI to install it anywhere. The seam between the proprietary Build half and the common Install half. It carries the [Installer](#installer) that places it, so the Artifact is self-installing: a party holding the Artifact installs from it without the proprietary integrator present.

**Installer.** The common Install half embodied as an executable carried inside the [Artifact](#artifact): scaffold placement plus the post-install orchestration that leaves a Host deployable-from. Activating it against a [Destination](#destination) produces a Scaffold — Build carries it, a Tenant activates it, and the proprietary integrator is absent at install time. The Installer is its own distribution so it can be activated against an Artifact with nothing else of Vaudeville present; the integrator depends on it, never the reverse.

**Destination.** Where Install places an Artifact. Two: **Host** — the operator's machine, the installation locations across `~/.claude`, `~/.vaudeville`, and `~/.local`, where Install preserves operator-curated state; and **Staging** — a single throwaway root that stands in for the Host so the operator can smoke-test before Apply, built fresh each Stage and mirroring the Host's own Claude state so the smoke is faithful.

**Facade.** The deployed `vv` — the single command-line tool a tenant runs. Build composes it from the Contributor CLI apps and Install installs it; it presents their commands as one surface and routes each in-process to the owning app, refusing to serve a federation whose apps collide on a subcommand name. The Contributor decomposition does not survive into it, so a tenant never depends on Vaudeville's internal package structure, which Vaudeville is free to change.

**`vaudeville`.** The operator-facing CLI Install places alongside `vv`. Composed exactly as the [Facade](#facade) is — from each Contributor's operator app (named by the Manifest's `operator_binary`), unioned by the same dispatcher under its own program name — so operator commands live in their Contributors, not in Ringmaster. A curated surface deliberately separate from `vv` and expected to diverge from it; a Contributor that declares no operator app contributes nothing to it.

## Operations

A Session is the bracketed sequence Clone → Stage (one or more, smoke-tested between) → Apply → Discard. Clone and Discard frame the Session; Stage and Apply read the Session Clones inside it. Stage and Apply share one pipeline — Assemble, Build, Install — and differ only in the Destination.

**Clone.** The operation that opens a Session: discards any leftover Session Clones, then fresh-clones each Registry-named Contributor Repo's `origin/main`. Required before Stage or Apply.

**Stage.** The pre-deploy verification operation: assembles a Release Candidate from a Worktree, builds it into an Artifact, and activates the Artifact's carried installer to place a Staging Scaffold the operator can audit and smoke-test. Re-runnable within a Session so a Hot-fix can iterate.

**Apply.** The deployment operation: assembles the Apply Plan from the Session Clones, builds it into an Artifact, and hands the Artifact to its carried installer for the Host Destination. The installer places the Host Scaffold and runs the Integrity check, the host-wiring check, and Foundation priming that together leave the host deployable-from. Subject to the Pristine guard, enforced in Apply before Build.

**Publish.** The operation that releases a versioned install Artifact to the [Published Home](#published-home): it builds from the Session Clones as Apply does, but where Apply installs to *this* host, Publish ships a named [Published Version](#published-version) to *other* Tenants. It also renders an [Exposition](#exposition) of the same Session Clones and commits it to the Published Home under the same version, so the Release tag points at the Exposition commit — the install Artifact and its readable companion share one version and one commit. Subject to the Pristine guard — both a Published Version and the Exposition that ships beside it carry only reviewed, merged code.

**Discard.** The operation that closes a Session: removes the Session Clones so no leftover state can be mistaken for an input by a future Session.

**Assemble.** The read-only first phase of Apply or Stage: load the Registry, require each Session Clone to exist, discover each Contribution (Stage substituting the Worktree for the Owning Repo), produce and validate an Apply Plan. Where a federation that collides on a Skill name is rejected (a subcommand collision is caught later, by the composed `vv`, on the apps' real command names); never writes to a Destination.

**Build.** The proprietary phase: integrate the Apply Plan and the Contributor sources into an Artifact. The Contributor decomposition dissolves here — the integrated command line is carried as one installable unit built from source, resolvable against public PyPI alone, alongside the [Installer](#installer) that places it. `ringmaster build` emits a durable Artifact; Stage and Apply build one in passing and activate its installer.

**Install.** The common phase: place an Artifact at a Destination, producing a Scaffold. Embodied by the [Installer](#installer) carried in the Artifact and activated with `uv`; resolves the carried command line from the Artifact's wheels and public PyPI. Every tenant runs Install; only Vaudeville-the-project runs Build.

**Apply Plan.** The validated value Assemble produces from all Contributions — the integrated offering of the whole federation, checked for Skill-name collisions. Build consumes it.

**Audit.** The cheap, deterministic structural walk of a Staged Scaffold. Inspects; it does not exercise. The end-to-end exercise of an assembled scaffold is the manual lifecycle smoke in the [`/rehearse` skill](../../.claude/skills/rehearse/SKILL.md), not a UL term.

**Integrity check.** The carried installer's verification, during a Host install, that the landed Host Scaffold is actually deployable-from, in two parts on opposite sides of the Contributor boundary. The command surface is Ringmaster's own — it asks the installed `vv` to self-report its composed surface, so a stale or hand-maintained `vv` is caught; this runs before priming, since priming itself invokes `vv`. Foundation durability belongs to vaudeville-bobiverse, so after priming it is delegated to that Contributor's `vv foundations-verify`. Where the [Audit](#audit) inspects a Staged Scaffold before deploy, the Integrity check verifies the Host Scaffold after it; either part aborts Apply loudly rather than leaving a host whose first Spawn or `vv` call fails downstream.

**Host-wiring check.** The carried installer's verification during a Host install, alongside the [Integrity check](#integrity-check), of the host *environment* `vv spawn`/`vv fork` reach past the scaffold for: the tenant's YouTrack is *located* (configured in `credentials.toml` and the instance reachable) and Workmux — the worktree/tmux multiplexer Spawn shells out to — is *present and runnable*. Runs before priming and aborts Apply loudly, turning a fresh host's missing YouTrack or Workmux into a deploy-time failure instead of a first-Spawn failure. The bar is wiring, not Contributor semantics — credential validity and a real `workmux add` are deeper, Contributor-owned checks left to a future `vv`-side probe.

## Outputs

**Release Candidate.** The integrated picture Stage composes for a Worktree: the Worktree's pending Contribution for the Owning Repo + every other Contributor Repo's Session Clone state. Structurally identical to what Apply would deploy from the same Session Clones if Stage had not substituted the Worktree.

**Host Scaffold.** The result of Install at the Host Destination: a multi-location end-state defined by the host's installation contracts, not a single directory.

**Staged Scaffold.** The result of Install at a Staging Destination: a single self-contained root the operator audits and smoke-tests without touching the Host Scaffold. The Audit reads it directly.

**Published Version.** The output of [Publish](#publish): a versioned, downloadable install Artifact in the [Published Home](#published-home) — what a Tenant pins to and installs from by activating the carried Installer. Its version is a synthetic, release-level CalVer naming the integrated release as a whole — a new axis, separate from any one Contributor's version and from Ringmaster's, with the Artifact's inner wheels keeping their own. Distinct from a [Release Candidate](#release-candidate), which is Stage's pre-deploy integrated picture for *verification*; a Published Version is the post-Build install Artifact for *consumption*, and carries no tenant config, so each installing Tenant supplies its own.

**Exposition.** The output of [Publish](#publish) that rides beside the [Published Version](#published-version): a for-reading rendering of the assembled source, committed into the [Published Home](#published-home)'s tree so a reader browses the whole constellation at the Release's tag without cloning each Contributor Repo. The relevant parts of each Contributor — its `src`, any workspace `packages` it ships (such as vaudeville-ringmaster's carried installer), its own `scaffold`, its `docs`, its `README` — are gathered into one curated tree of [Sections](#section), with the universal Doctrine as its own Section. A reading copy, deliberately *not* the build input: it is reorganized into Sections, trimmed of tests, tooling, lockfiles, and history, and regenerated whole each Publish. What a release was actually built from is the [Provenance](#provenance) at its root, not the rendering. Distinct from the [Artifact](#artifact), which carries the same code as built wheels rather than readable source.

**Section.** A top-level grouping within an [Exposition](#exposition) naming the role its members play in the constellation: `subsystems` (the lifecycle Contributors), `doctrine` (the universal Doctrine prose), `machinery` (the integrator and the shared kernel). The placement of each Contributor into a Section is editorial, declared in the Exposition's layout and validated to cover exactly the [Registry](#registry) — so a newly registered Contributor forces a placement decision rather than being silently dropped from the rendering.

**Provenance.** The manifest at an [Exposition](#exposition)'s root recording what a release's install Artifact was built from. It records the **carried Contributions** — those whose source the Artifact actually holds, whether as a built wheel or as a scaffold slot (a Skill, Data File, Doc Tree, Hook Script, or the Hook Matchers Build merges into the Artifact) — and not the rest of the constellation: per Contribution, the repository and the exact commit, read from its [Session Clone](#session-clone)'s recorded clone-time commit (the same sidecar the [Pristine guard](#pristine-guard) reads). The integrator is not a carried Contribution; it is the **Builder**, and it never appears in the carried record — by construction, because Provenance derives the carried set from the same definition Build places from, not from every Session Clone. The Facade and the carried installer are the Builder's, so they are recorded separately by its running version (Build generates the Facade stamped with that version and builds the installer from the running `vaudeville_install`), leaving the manifest complete even when Publish runs from an integrator that differs from the vaudeville-ringmaster Session Clone. The authoritative record of what a release shipped: it lets the Exposition stay an unapologetically curated reading copy, because the build-truth lives in the Provenance rather than in the rendered tree. Distinct from the Exposition's own membership, which is the whole constellation by editorial role — so the integrator appears there, as `machinery`, exactly where it is absent here.

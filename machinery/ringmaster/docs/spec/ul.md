# Ringmaster: ubiquitous language

This is a UL doc: terms defined in relation to one another. For framework-level UL see [`vaudeville-doctrine`'s `vocabulary.md`](https://github.com/somehowsoftware/vaudeville-doctrine/blob/main/scaffold/doctrine/vocabulary.md), the universal doctrine Ringmaster itself now carries to every tenant as a Doc Tree.

Ringmaster-internal terms. Cross-context terms are not redefined here: Skill and Bounded Context live in the framework-level UL above; Contributor and Ringmaster in [`vaudeville-config`'s project-internal `vocabulary.md`](https://github.com/somehowsoftware/vaudeville-config/blob/main/project-docs/vocabulary.md). Storage layout, module organization, subprocess mechanics, and the Contributor-side encoding contract live in [`architecture.md`](architecture.md), the rehearsal cycle in the [`/rehearse` skill](../../.claude/skills/rehearse/SKILL.md), and the source.

## Two contexts, one seam

Ringmaster houses two bounded contexts that meet at a single artifact. The **Integrator** clones the federation, rehearses a candidate against a Worktree, deploys the integrated whole to a host, and publishes releases of it — one value core, with publication a neighboring cluster inside it. The **Installer** takes the one thing the Integrator hands across — the [Artifact](#artifact) — and places it at a Destination, honoring what the operator owns and commissioning the host. The boundary is the Artifact: the Integrator builds it and is then absent; the Installer consumes it with no integrator present. The two share only a small declared [seam](#the-declared-seam) of words, listed at the end; everything else in each context is that context's own.

# Integrator context

## Inputs

**Registry.** The integrator-internal declaration of which Contributor Repos make up this host's federation, shipped with Ringmaster as package data and read from beside the module. Each entry pairs a Contributor Repo's name with its remote location.

**Contributor Repo.** A repo named in the Registry. Read by Rehearse and Deploy from its Session Clone; the Worktree substitutes for the Owning Repo's Session Clone in a Rehearse.

**Worktree.** Any directory inside an operator's working clone of a Contributor Repo. Rehearse's input: it carries the pending Contribution whose integration a Rehearsal Set is built to verify.

**Owning Repo.** The Contributor Repo a Worktree belongs to. The one Contributor Repo whose Contribution comes from the Worktree in a Rehearse; all others come from their Session Clones.

**Home Repo.** The integrator's own Contributor Repo — vaudeville-ringmaster itself — present in every federation and every plan. The one Contributor that is also the [Builder](#builder): [Self-update](#self-update) rebuilds and reinstalls the integrator from the Home Repo's own pristine Session Clone. Distinct from the [Published Home](#published-home): the Home Repo is the integrator's *source*, the Published Home is where [Publish](#publish) *accumulates Releases*.

**Published Home.** The integrator-internal GitHub repository where [Publish](#publish) accumulates [Releases](#release), organized by [Release Name](#release-name). A Tenant consumes Releases from it; only the integrator publishes to it. Integrator-internal like the Registry: the name lives in the source, not in operator state. Colloquially **the vaudeville repository** (or **the vaudeville repo**): that phrase names this repository, the only one Ringmaster publishes to, so an unqualified reference to it resolves here rather than to a Contributor Repo or to Vaudeville the project.

## Session

**Session.** The bracketed span of a single deploy attempt: opened by Clone, closed by Discard. Every Rehearse and every Deploy happens inside a Session. The scope at which Session Clones exist.

**Session Clone.** Ringmaster's working copy of a Contributor Repo for the duration of one Session. Produced by Clone (which records its [Pin](#pin)), consumed by Rehearse and Deploy, removed by Discard. Writable inside the Session as the operator's Rehearsal Fix surface.

**Rehearsal Fix.** An operator edit to a Session Clone made during the rehearse-and-smoke loop in response to a smoke failure. Feeds the next Rehearse; structurally barred from shipping. Unlike what "hotfix" names, it can never reach a host: the [Pristine guard](#pristine-guard) refuses to Deploy any Session Clone it touched, so its only fate is to be productionized as a reviewed, merged PR and re-cloned.

**Pristine guard.** Deploy's refusal to deploy a Session Clone whose current state is not Pin-equal to what Clone produced — any clone the operator has modified since Clone. A backstop for the discipline of never deploying Rehearsal Fixes; enforced in Deploy before Build.

## Pins

**Pin.** One Contributor Repo frozen at a single commit: a Contributor Repo's name, its remote, and the exact commit its [Session Clone](#session-clone) was produced at, read from the clone-time sidecar. The atom of a Release's identity. A Pin cannot exist without a commit: a directory carrying no recorded clone-time commit is not a Pin, because it was not produced by [Clone](#clone), and [Provenance](#provenance) refuses to vouch for a commit it cannot establish.

**Pinned Set.** The whole federation frozen at gather time: one [Pin](#pin) per Contributor Repo. The value that exists from the moment [Clone](#clone) opens a [Session](#session), before anything is built or published: *what a Release is made of*. A [Release](#release) is a published Pinned Set, so the unpublished frozen value and the published thing are one concept in two states. Distinct from the [Manifest](#manifest): the Manifest is the integrated *offering* Survey derives for Build; the Pinned Set is the *identity*: which Contributor Repos at which commits.

## Contribution slots

**Contribution.** What a Contributor Repo offers to the federation. Skills, Data Files, Doc Trees, Hook Scripts (with Hook Matchers), a CLI (its Console Script and CLI Declaration), Libraries, and the distribution that carries the CLI. Any slot may be empty.

**Data File.** A file consumed by `vv` and host Skills at runtime. Carried by the Contributor under `scaffold/.vaudeville/`, collected into the [Artifact](#artifact) by Build, and placed as a flat file at the Destination's data dir by Install.

**Doc Tree.** A directory of documentation a Contributor publishes for agents to read at the host: the universal doctrine. A fixed, known name (`doctrine/`) a Contributor ships under `scaffold/<name>/`; Build collects it and Install places it at the matching subtree of the Destination's data dir (`scaffold/doctrine/` → `~/.vaudeville/doctrine/`). Ringmaster fully owns that subtree and rebuilds it wholesale every deploy — [Owned](#tenure) tenure, the same contract as the framework-owned skills and hooks directories. Where a Data File is a flat runtime file, a Doc Tree is a whole tree of prose. A tenant's project-docs is not a Doc Tree; Install copies it from the [Tenant Config](#tenant-config).

**Hook Script.** An executable fired by Claude Code at a tool-call boundary. Carried by the Contributor, collected into the Artifact by Build, and placed at a Destination by Install.

**Hook Matchers.** The Contributor-side declaration of when each Hook Script fires. Merged across Contributors into one fragment by Build and written into the host's `settings.json` as [Hook Wiring](#hook-wiring) by Install.

**Console Script.** A Python entry point a Contributor declares in `[project.scripts]`. Build reads it to find the module of a Contributor's `vv` app or its operator app: the modules the [Facade](#facade) instances (`vv` and [`vaudeville`](#vaudeville)) respectively compose.

**CLI Declaration.** A Contributor Repo's declaration that it contributes to the federated command line: the `[tool.vaudeville]` table, naming the `binary` whose entry point identifies its `vv` app and, optionally, the `operator_binary` whose entry point identifies its operator app for [`vaudeville`](#vaudeville). Its presence marks the Contributor as part of the command [Surface](#surface); Contributors with no CLI omit it, and a Contributor with a `vv` app but no operator app omits `operator_binary`. The command surface itself is whatever the apps define; Ringmaster reads it from them, never from a hand-maintained list. (Named CLI Declaration, not Manifest, so the Contributor-side `[tool.vaudeville]` table does not collide with the integrated [Manifest](#manifest) Survey produces.)

**Library.** A Contribution slot that ships shared code as a distribution with no commands of its own: consumed by other Contributors' apps at build time, never itself a `vv` subcommand. Distribution without a command surface.

**Contribution Layout.** The fixed `scaffold/` convention by which a Contributor encodes each slot at a known location inside its repo, the placement contract Build's discovery reads. Resolves the old "Scaffold" homonym: this is the *source-side* placement convention, distinct from the [Host Installation](#host-installation) / [Rehearsal Installation](#rehearsal-installation) an install *produces*.

## Operations

A Session is the bracketed sequence Clone → Rehearse (one or more, smoke-tested between) → Deploy → Discard. Clone and Discard frame the Session; Rehearse and Deploy read the Session Clones inside it. Rehearse and Deploy share one pipeline ([Survey](#survey), [Build](#build), [Install](#install)) and differ only in the Destination.

**Clone.** The operation that opens a Session: discards any leftover Session Clones, then fresh-clones each Registry-named Contributor Repo's `origin/main` and records each Session Clone's [Pin](#pin). Required before Rehearse or Deploy.

**Rehearse.** The pre-deploy verification operation: [Surveys](#survey) a [Rehearsal Set](#rehearsal-set) from a Worktree, builds it into an [Artifact](#artifact), and activates the Artifact's carried installer to place a [Rehearsal Installation](#rehearsal-installation) — at the stable per-Worktree Rehearsal Slot — that the operator can [Audit](#audit) and smoke-test. Re-runnable within a Session so a [Rehearsal Fix](#rehearsal-fix) can iterate. Does not consult the Pristine guard: rehearsal is exactly where modified clones are meant to be exercised.

**Deploy.** The deployment operation: [Surveys](#survey) the [Manifest](#manifest) from the Session Clones, builds it into an [Artifact](#artifact), and hands the Artifact to its carried installer for the Host Destination, which places the [Host Installation](#host-installation) and [commissions](#commissioning) it. Subject to the Pristine guard, enforced before Build. On success it is followed by [Self-update](#self-update). Its definition stops at the seam: what the installer then does to the Host is the Installer's [Commissioning](#commissioning), not Deploy's to narrate.

**Self-update.** The second job Deploy performs after a successful host install: rebuild and reinstall the integrator itself from the [Home Repo](#home-repo)'s own pristine Session Clone, so the machine that just deployed the federation is refreshed to the code it deployed. Reached only after the deploy succeeds.

**Publish.** The operation that cuts a [Release](#release) from the current [Pinned Set](#pinned-set) and publishes it to the [Published Home](#published-home): it builds from the Session Clones as Deploy does, but where Deploy installs to *this* host, Publish ships the Release (its [Artifact](#artifact) as the versioned download) to *other* Tenants. It also renders the Release's [Exposition](#exposition) and writes it into the Published Home as one labeled commit, then tags the Release at that commit, so the install Artifact and its readable companion share one [Release Name](#release-name) and one commit. The Exposition is committed before the tag, so a failure after it leaves an untagged commit the next Publish supersedes rather than a Release with no readable companion. Subject to the Pristine guard: a Release carries only reviewed, merged code.

**Discard.** The operation that closes a Session: removes the Session Clones so no leftover state can be mistaken for an input by a future Session.

**Audit.** The cheap, deterministic structural walk of a [Rehearsal Installation](#rehearsal-installation). Inspects; it does not exercise. The end-to-end exercise of an installation is the manual lifecycle smoke in the [`/rehearse` skill](../../.claude/skills/rehearse/SKILL.md), not a UL term.

## Phases

Rehearse, Deploy, Build, and Publish all run the same three-phase pipeline, differing only in the Destination and the tail each adds.

**Survey.** The read-only first phase: load the Registry, require each Session Clone to exist, discover each Contribution (Rehearse substituting the Worktree for the Owning Repo), and produce and validate the [Manifest](#manifest). A federation that collides on a Skill name is rejected here (a subcommand collision is caught later, by the composed `vv`, on the apps' real command names); never writes to a Destination. Read-only discovery plus validation — it surveys, it does not assemble.

**Build.** The proprietary phase: integrate the [Manifest](#manifest) and the Contributor sources into an [Artifact](#artifact). The Contributor decomposition dissolves here: the integrated command line is carried as one installable unit built from source, resolvable against public PyPI alone, alongside the [Installer](#installer) that places it. `ringmaster build` emits a durable Artifact; Rehearse and Deploy build one in passing and activate its installer.

**Install.** The common phase: place an Artifact at a Destination, producing an [Installation](#host-installation). Embodied by the [Installer](#installer) carried in the Artifact and activated with `uv`; resolves the carried command line from the Artifact's wheels and public PyPI. Every tenant runs Install; only Vaudeville-the-project runs Build. The seam: past here the Integrator is absent and the [Installer context](#installer-context) takes over.

## Values

**Rehearsal Set.** Rehearse's verification picture: a [Pinned Set](#pinned-set) with the Owning Repo's [Pin](#pin) replaced by a [Worktree](#worktree) — the Worktree's pending Contribution for the Owning Repo plus every other Contributor Repo's Session Clone state. Structurally identical to what Deploy would build from the same Session Clones if Rehearse had not substituted the Worktree. For *verification*, not consumption: distinct from a published [Release](#release), and not itself fully pinned, since the substituted member is a live Worktree rather than a Pin. Exercised, never shipped.

**Manifest.** The validated value [Survey](#survey) produces from all Contributions: the integrated offering of the whole federation, checked for Skill-name collisions. Build consumes it. Named for what it is — a validated bill of materials — not for one consumer, and not a computed delta. Distinct from the [CLI Declaration](#cli-declaration), the Contributor-side `[tool.vaudeville]` table that once shared this name, and from the [Pinned Set](#pinned-set), which is the identity rather than the offering.

**Facade.** The genus: one flat command-line tool composed from the Contributor CLI apps, presenting their commands as one [Surface](#surface) and routing each in-process to its owning app, refusing to serve a federation whose apps collide on a subcommand name. Two instances — `vv`, the tenant CLI, and [`vaudeville`](#vaudeville), the operator CLI — composed the same way under their own program names. The Contributor decomposition does not survive into a Facade, so a tenant never depends on Vaudeville's internal package structure. A Build-context word: it names how the composed CLI is assembled, and does not cross the seam — the Installer speaks of "the deployed `vv`," never "the Facade."

**Surface.** The composed command set a [Facade](#facade) serves and self-reports. `vv`'s Surface is the union of every Contributor's `vv`-app commands; the installed `vv` self-reports it, which is what the [Surface Check](#surface-check) reads. A seam word: the Installer names the Surface without naming the Facade that produced it.

**`vaudeville`.** The operator-facing [Facade](#facade) instance Install places alongside `vv`. Composed from each Contributor's operator app (named by the [CLI Declaration](#cli-declaration)'s `operator_binary`), unioned by the same dispatcher under its own program name, so operator commands live in their Contributors, not in Ringmaster. A curated surface deliberately separate from `vv` and expected to diverge from it; a Contributor that declares no operator app contributes nothing to it.

## Release

The publication cluster: the neighboring set of terms by which a [Pinned Set](#pinned-set) becomes a published, versioned, readable thing. It shares the Session's clones and the Pin/Pinned Set values with the rest of the Integrator; [Publish](#publish) is its operation.

**Carried Set.** The subset of a [Pinned Set](#pinned-set) whose source actually ships inside the [Artifact](#artifact): the command-surface Contributors and the libraries they share, as built wheels or scaffold slots. The integrator is excluded: it is the [Builder](#builder), not a payload. What [Provenance](#provenance) vouches for, as against the whole constellation an [Exposition](#exposition) renders.

**Release.** A [Pinned Set](#pinned-set) published under a [Release Name](#release-name): the integrated whole as a versioned, published thing, identified by what it was built from. It *emits* an [Artifact](#artifact) (its download), an [Exposition](#exposition) (its reading copy), and a [Provenance](#provenance) (its build-truth), and is published as a git tag at the Exposition commit. The released whole, distinct from any one of its emissions: the noun the retired "Published Version" lacked, having named one emission, the install Artifact, as though it were the whole.

**Release Name.** A [Release](#release)'s synthetic, release-level CalVer identity (`vYYYY.MM.DD.N`): a version axis naming the integrated release as a whole, separate from any one Contributor's version and from Ringmaster's, with the Artifact's inner wheels keeping their own. One value, of which the git tag, the release title, the commit-message prefix, and the download's filename are all *stampings*. The next Release Name is today's CalVer stem with the lowest counter not already taken in the [Published Home](#published-home)'s tag namespace; the tag namespace is read because that is the storage the tag reuses, even though the fact it establishes is "this Release Name is not yet taken."

**Predecessor.** The previously published [Release](#release): the one a new Release is the next after, resolved from the [Published Home](#published-home)'s tag namespace. The thing "the last release" names.

**Changeset.** The difference between a [Release](#release) and its [Predecessor](#predecessor): per Contributor Repo, the Contributions merged between the Predecessor's [Pin](#pin) and this Release's Pin. Because the federation squash-merges, each such commit is exactly one merged pull request, so a Changeset reads as a set of merged pull requests across the Contributors.

**Release Notes.** The human-readable synthesis of a [Changeset](#changeset): what changed since the [Predecessor](#predecessor), read across the Contributors. Named here as the work it describes; not yet a built operation.

**Provenance.** The authoritative record of what a [Release](#release)'s [Artifact](#artifact) was built from: its [Carried Set](#carried-set) together with its [Builder](#builder). The *value*; the `provenance.toml` written at the [Exposition](#exposition)'s root is its serialization, not the concept. Per carried Contribution it records the repository and the exact commit, the [Pin](#pin)'s commit; the integrator never appears as a carried Contribution, because it is the Builder, recorded separately. The build-truth that lets the Exposition stay an unapologetically curated reading copy: what a Release shipped lives here, not in the rendered tree.

**Builder.** The integrator identity and version that built a [Release](#release): the [Facade](#facade) it stamped and the installer it built, recorded by its running version (`vaudeville_ringmaster` and `vaudeville_install`). Recorded in the [Provenance](#provenance), never itself a [Pin](#pin): the integrator is what builds the Release, not a payload in its [Carried Set](#carried-set). It appears in the [Exposition](#exposition) as `machinery`, exactly where it is absent from the Provenance's carried record.

**Exposition.** A [Release](#release)'s for-reading rendering of its assembled source. The relevant parts of each Contributor are gathered into one curated tree of [Sections](#section), with the universal Doctrine as its own Section: its `src`, any workspace `packages` it ships (such as vaudeville-ringmaster's carried installer), its own `scaffold`, its `docs`, its `README`. A reading copy, deliberately *not* the build input: it is reorganized into Sections, trimmed of tests, tooling, lockfiles, and history, and regenerated whole each Publish. What the Release was actually built from is its [Provenance](#provenance), placed at the Exposition's root, not the rendering. [Publish](#publish) commits the Exposition in the [Published Home](#published-home) and tags the Release there, so a reader browses the whole constellation at the Release's tag without cloning each Contributor Repo. But that committing is an act Publish performs on the Exposition, not part of what the Exposition is. Distinct from the [Artifact](#artifact), which carries the same code as built wheels rather than readable source.

**Section.** A top-level grouping within an [Exposition](#exposition) naming the role its members play in the constellation: `subsystems` (the lifecycle Contributors), `doctrine` (the universal Doctrine prose), `machinery` (the integrator and the boundary Contributor). The placement of each Contributor into a Section is editorial, declared in the Exposition's layout and validated to cover exactly the [Registry](#registry), so a newly registered Contributor forces a placement decision rather than being silently dropped from the rendering.

# Installer context

Installer entries speak the installer's language: it *places an Artifact* and *aborts the install*; it does not know the [Facade](#facade), the [Manifest](#manifest), or the [Pinned Set](#pinned-set) that produced its input. It knows the Artifact, the Destination it places to, and the Host it commissions.

## Inputs

**Artifact.** The self-contained, destination-ignorant installable unit Build produces and Install consumes. It carries the integrated Skills, Data Files, Hook Scripts, the merged Hook-Matcher fragment, and the integrated command line as installable code. It reads back into no Session Clone and no source tree, and carries the Vaudeville packages it needs as wheels, so the common half need fetch nothing but public PyPI to install it anywhere. The seam between the proprietary Build half and the common Install half. It carries the [Installer](#installer) that places it, so the Artifact is self-installing: a party holding the Artifact installs from it without the proprietary integrator present. When [Publish](#publish) ships it, the same unit is a [Release](#release)'s versioned download in the [Published Home](#published-home), what a Tenant pins to and installs from: the same unit Deploy instead installs to *this* host.

**Tenant Config.** Who this installation serves: the **Project Map** (the tenant's repos and their remotes), the **Tracker Credentials** (the work-tracker location and its authentication), the tenant's project docs, and the tenant's own [Hook Scripts](#hook-script) with their [Hook Matchers](#hook-matchers) — the hooks a tenant carries in its own config to run alongside the Contributor-sourced ones. The third parameter of Install, parsed at the installer boundary; distinct from the Artifact (which is tenant-ignorant) and from the Destination (which is only *where*). Its facts feed the [Environment Declarations](#trust-declarations), the project-docs Install places under [Owned](#tenure) tenure, and the tenant half of the [Hook Wiring](#hook-wiring).

**Destination.** Where Install places an Artifact. Two cases: **Host**, the operator's machine — the installation locations across `~/.claude`, `~/.vaudeville`, and `~/.local`, where Install preserves operator-curated state; and **Rehearsal**, a single throwaway root that stands in for the Host so the operator can smoke-test before Deploy, built fresh each Rehearse and mirroring the Host's own Claude state (the [Host Mirror](#host-mirror)) so the smoke is faithful. (The `--destination staging` flag value is data, a carve-out that lags this UL rename.)

**Installer.** The common Install half embodied as an executable carried inside the [Artifact](#artifact): installation placement plus the post-install orchestration that leaves a Host deployable-from. Activating it against a [Destination](#destination) produces an [Installation](#host-installation): Build carries it, a Tenant activates it, and the proprietary integrator is absent at install time. The Installer is its own distribution so it can be activated against an Artifact with nothing else of Vaudeville present; the integrator depends on it, never the reverse.

## Results

**Host Installation.** The result of Install at the Host Destination: a multi-location end-state across `~/.claude`, `~/.vaudeville`, and `~/.local`, defined by the host's installation contracts, not a single directory.

**Rehearsal Installation.** The result of Install at a Rehearsal Destination: a single self-contained root the operator audits and smoke-tests without touching the [Host Installation](#host-installation). The [Audit](#audit) reads it directly; a rehearsal shell's [Rehearsal Redirect](#rehearsal-redirect) points the smoke at it.

**Host Mirror.** The live Host state a [Rehearsal Installation](#rehearsal-installation) borrows so the smoke is faithful: the Host's own Claude configuration, reflected into the throwaway rehearsal root so a rehearsal exercises the integrated whole against real host state rather than an empty one.

## Tenure

**Tenure.** How the installer treats each path it could touch at the Host — the genus, three cases. **Owned:** wiped and rebuilt every install (the skills, the hooks, each Doc Tree, the tenant's project-docs, and the two managed settings keys). **Ledgered:** placed by a previous install and prunable only through the [Ledger](#ledger) that recorded it. **Curated:** the operator's own, never touched. The contract that lets an install rebuild what it owns without destroying what it does not.

**Ledger.** The installer's record of what the previous install placed, so a path no longer in the current Artifact can be pruned without a blind sweep of the Host. The mechanism of [Ledgered](#tenure) tenure: prune only what the Ledger vouches this installer placed.

**Reserved Names.** Paths never pruned regardless of a stale [Ledger](#ledger): a safety floor under Ledgered pruning. A contract declared across the seam — the Integrator's [Build](#build) honors the same set the Installer does, so a name the Installer would refuse to prune is never one Build assigns to transient output.

## Settings

**Hook Wiring.** The `hooks` block of the host's `settings.json`, materialized every install by composing two sources of [Hook Matchers](#hook-matchers): the Contributor-sourced fragment merged into the [Artifact](#artifact) and the tenant's own fragment from the [Tenant Config](#tenant-config). Composed as the [Trust Declarations](#trust-declarations) compose their Owned block from a framework and a tenant source — the tenant's matchers union into the Contributor ones per event — so a tenant's own hooks go live alongside the stock ones. [Owned](#tenure) tenure: rebuilt wholesale each install, each command resolved to its placed [Hook Script](#hook-script), of either provenance, in the one hooks directory. A tenant Hook Script whose filename collides with a stock one aborts the install rather than silently shadow it.

**Trust Declarations.** The English policy the installer writes for the permission classifier — the `autoMode` block — in two parts. **Framework Allowances:** the framework's standing allowances for its own operations (spawning a Bob), baked in and reaching every tenant. **Environment Declarations:** the trusted-infrastructure lines composed from facts the tenant already states in its [Tenant Config](#tenant-config) — the source-control orgs in the Project Map, the tracker in the Tracker Credentials — rather than authored by hand. Additive by construction: every emitted section leads with `$defaults`, the sentinel (a data carve-out) that extends rather than replaces the classifier's built-in blocks. [Owned](#tenure) tenure; an operator's own rules live in `settings.local.json`, a scope the classifier combines and the installer never writes, so the owned key needs no merge.

**the settings file.** The host `settings.json` is a write target of mixed [tenure](#tenure), not a domain concept in its own right: its `hooks` key ([Hook Wiring](#hook-wiring)) and `autoMode` key ([Trust Declarations](#trust-declarations)) are Owned and rebuilt wholesale; every other key is Curated and preserved. This shrunken entry retires the former "Vaudeville-managed `settings.json`," which named a file's mechanism — the blocks, the sentinel, the local-scope file — as though the file were a concept.

## Commissioning

**Commissioning.** The Host-only verification, after a Host install, that the placed [Host Installation](#host-installation) is actually deployable-from: four steps straddling the Contributor boundary, any of which aborts the install loudly rather than leaving a host whose first Spawn or `vv` call fails downstream. In order: [Surface Check](#surface-check), [Host-wiring Check](#host-wiring-check), [Priming](#priming), [Foundation Check](#foundation-check). A Rehearsal install is placement only; its verification is the smoke, not Commissioning.

**Surface Check.** The first Commissioning step: ask the installed `vv` to self-report its composed [Surface](#surface) and require it non-empty, so a stale or hand-maintained `vv` is caught. Runs before Priming, since Priming itself invokes `vv`. The command set is the Integrator's; the check names the Surface, not the Facade that produced it.

**Host-wiring Check.** The Commissioning step that verifies the host *environment* the steps after it reach into: the tenant's tracker *authenticates* (the configured token is accepted, not merely that the instance answers), each of the tenant's own Component remotes is *readable* (a read-only `git ls-remote`, the same auth path Priming's clone takes), and Workmux (the worktree/tmux multiplexer Spawn shells out to) is *present and runnable*. The bar is *read-only* wiring, not the Contributor operations themselves: the probes take the access the next steps need — Priming's clone, a Spawn's `workmux add` — without their side effects. A fresh non-self host is expected to fail here until its own git credentials and a working tracker token are wired; the check's job is to make that failure fast, legible, and pre-Priming, not to make the install succeed unwired.

**Priming.** The Commissioning step that seeds each Contributor's Foundation on the Host, reached by subprocess through the installed `vv`. Named as the act it is, not a check: it mutates. Runs against the Host's own Claude state even when Deploy is invoked from a rehearsal shell (the [Rehearsal Redirect](#rehearsal-redirect) is stripped first). The installer does not decide which Foundations exist; priming itself is the Contributor's `vv prime`.

**Foundation Check.** The last Commissioning step: after Priming, verify no Foundation was left stranded — delegated across the Contributor boundary to vaudeville-bobiverse's `vv foundations-verify`, since Foundation durability is that Contributor's concern. A deploy that left a Foundation stranded fails here, at install time, rather than at the next Spawn.

**Rehearsal Redirect.** The environment overrides a rehearsal shell exports to point `vv` and Claude at a [Rehearsal Installation](#rehearsal-installation) instead of the Host — the `CLAUDE_CONFIG_DIR` / `VV_DATA_DIR` / `PATH` trio. [Commissioning](#commissioning) strips them so its checks address the real Host even when Deploy runs from a rehearsal shell.

# The declared seam

The words both contexts share by contract — the Integrator produces each and the Installer consumes it, so both must mean the same thing by it:

[Artifact](#artifact) · the slot names ([Skill](#contribution), [Data File](#data-file), [Doc Tree](#doc-tree), [Hook Script](#hook-script), [Hook Matchers](#hook-matchers)) · [Destination](#destination) (Host | Rehearsal) · [Host Installation](#host-installation) / [Rehearsal Installation](#rehearsal-installation) · [Surface](#surface) · [Reserved Names](#reserved-names).

Everything else in each context is that context's own. A term not on this list does not cross the boundary, and the Installer never borrows a Build-context word — [Facade](#facade), [Manifest](#manifest), [Pinned Set](#pinned-set) — to say what it means.

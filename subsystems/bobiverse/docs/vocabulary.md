# Bobiverse vocabulary

*This is a UL doc: terms defined in relation to one another. For framework-level UL see `~/.vaudeville/doctrine/vocabulary.md`.*

The verbs and state nouns Bobiverse uses internally for the **inter-session** lifecycle: what happens around a Bob. The **intra-session** verbs a running Bob applies to its own work (Checkpoint, Materialize, Parlay, Design, Winnow, Spike) and their artifacts now live in vaudeville-cue's vocabulary, not here. Cross-context terms (**Bob**, **Assignment**, **Route**, **Foundation**, **Brief**, **Component**) are linked to the framework vocabulary, not redefined.

## Verbs

### Prime

Drive Components' Foundations into existence across three documentation layers: the cross-context Doctrine every tenant shares, the project context this tenant shares across its Components, and each Component's own documentation. The first two layers are identical for every Component on a tenant, so Prime drives them once into a [Bedrock](#bedrock) and forks a Foundation from the Bedrock per Component, each fork adding only that Component's own layer. The verb's noun-form is **Priming** (the process) and is used interchangeably in prose. Re-Priming replaces the Component's Foundation wholesale. The Foundation it produces is addressable independent of the clone it was primed in. Prime is the precondition for [Spawn](#spawn).

### Durable / Stranded

A recorded Foundation (`~/.vaudeville/doctrine/vocabulary.md#foundation`) is **durable** when a later [Spawn](#spawn) can fork from it on this host, regardless of which clone the Bob runs in; **stranded** when it is recorded but not present on the host, so a Spawn cannot fork from it: for example a [Prime](#prime) performed inside a smoke that never reaches the host. `vv foundations-verify` reports the stranded Foundations; Ringmaster's Foundation Check invokes it so a deploy that left a Foundation stranded fails loudly at deploy time rather than at the next Spawn.

### Origin drift

A Component's clone exhibits **origin drift** when its `origin` remote no longer agrees with the canonical remote the registry declares for that Component. Like [Durable / Stranded](#durable--stranded) it is a fitness of host state that [Spawn](#spawn) weighs up front against the registry: here the fitness of the clone's git config rather than of the Foundation record. The case spawn refuses today is the clone with *no* `origin` at all: lacking it, spawn's clone-refresh fails opaquely from deep inside the sweep even though the registry held the canonical remote the whole time, so spawn names the drift and refuses the clone before touching it. A clone whose `origin` is present but points elsewhere is a separate, silent fault (it fetches the wrong history rather than failing) and is out of scope for this refusal.

### Unreadable source

A Component's [Foundation](~/.vaudeville/doctrine/vocabulary.md#foundation) has an **unreadable source** when [Prime](#prime) cannot fork it because its current reading cannot be obtained: the git remote vaudeville-core clones to read the Component's source could not be read or authenticated. Like [Origin drift](#origin-drift) and [Durable / Stranded](#durable--stranded) it is a fitness of host state that Prime weighs — here the host's git credential access to the Component's remote, rather than the clone's `origin` config or the Foundation record. A headless Prime with no wired credential for a private Component remote reaches this verdict at once — priming runs git non-interactively, so the unauthenticated clone aborts rather than blocking on a credential prompt on an inherited terminal — and names the Component, says its remote could not be read or authenticated, and points at the remedy (wire git credentials for your Component remotes), rather than hanging or reporting a bare exit. Requiring that credential is acceptable, not a defect: a tenant that cannot clone its own Component remotes cannot be primed at all, so Prime fails fast and loudly rather than part way. Realized in code as the typed `UnreadableSource`, raised at the prime-side sourcing boundary and carried through the prime report.

### Spawn

The act that brings a Bob into being. Workmux allocates the working surface; the new Claude Code session is forked from the Component's Foundation so the Bob inherits the priming as conversation history, regardless of where the clone lives; vaudeville-cue renders the Brief and the new Bob reads it as its first user turn. Spawn refuses when no Foundation exists for the Component. After spawn the Bob is **Spawned** but has not yet **Claimed** an Assignment.

### Reseat

The act that replaces a running Bob's session in place: same pane, same worktree, same Assignment — the *seat* conserved — with a fresh Claude Code session born holding the Resume Brief as its first user turn. The intra-session sibling of [Spawn](#spawn) (which brings a Bob into a *new* worktree) and of [Teardown](#teardown) (which empties the pane): all three act on a Bob's pane through the launch knowledge bobiverse keeps in one place, which is why reseat reuses spawn's launch (model, remote-control, autonomy) rather than re-deriving it. cue's `vv checkpoint` launches it (`vv reseat <worktree> <brief-path>`) as the detached handoff that sheds an oversized conversation: cue composes the Brief and names the pane, and reseat replaces the session with the launch *minus* the Foundation fork — the conversation is shed, not re-forked, and the Brief is the new ground. Replacing the session in one act leaves no cleared-but-unseeded interval for a competing injector to swallow or a slow successor to strand, so a reseat that cannot land its Brief, or finds no pane, refuses *before* the respawn — the only destructive step — leaving the live session whole, never after.

### Seeded Clone

A Component's clone the [Foundation](~/.vaudeville/doctrine/vocabulary.md#foundation)'s transcript has been copied into, so `workmux add --fork` resolves the conversation from that clone's own Claude project directory. A [Spawn](#spawn) produces a Seeded Clone and builds the launch only from one, so a Bob is never launched against a clone its Foundation was never seeded into: the in-flight, spawn-time counterpart of a [Durable](#durable--stranded) Foundation, which is the same readiness made persistent and host-wide.

### Closeout

Terminate the Bob. Takes one of five **kinds**, each with a different consequence for the Assignment the Bob was working on:

- **delivered**: Assignment transitions to Delivered. Cross-context kernel kind; see `~/.vaudeville/doctrine/practice/assignment-lifecycle.md`.
- **abandoned**: Assignment transitions to Abandoned. Cross-context kernel kind; see `~/.vaudeville/doctrine/practice/assignment-lifecycle.md`.
- **returned**: Assignment transitions to Returned and re-enters the pickup pool. Cross-context kernel kind; see `~/.vaudeville/doctrine/practice/assignment-lifecycle.md`.
- **[unclaim](#unclaim)**: Bobiverse-local.
- **[none](#none)**: Bobiverse-local.

Closeout is an orchestration, not a single command: every kind ends in the same [Teardown](#teardown), differing only in the transition run first. Running that transition before Teardown (and aborting if it fails) is essential, because once the pane is gone there is no second chance to record the outcome.

### Teardown

The substrate atom every Closeout kind ends in (`vv teardown`): archive the worktree and the Bob's transcript, then tear the substrate down. It writes nothing to the tracker; the Assignment transition is a separate atom, run first. Teardown is the irreversible step of the Bob lifecycle, and the only verb the explicit-invocation guard watches, because a Bob that runs it self-closes.

### Unclaim

The Bobiverse-local transition atom (`vv unclaim`) that returns an Assignment to the pickup pool with its assignee cleared and no comment, so it looks as it did before the Bob ever touched it. The kernel terminations (delivered, abandoned, returned) are PM's; unclaim is bobiverse's because "the Bob had no right to exist" is a word about the Bob's relationship to the Assignment, not the Assignment's deliverable state. Reserved for the procedural-mistake case where teardown is the intent. Distinct from `returned` (a real attempt that stopped partway) and from `abandoned` (a judgment that the Assignment should not exist anymore).

### None

The Bobiverse-local Closeout kind that runs no transition atom at all: only [Teardown](#teardown). The Bob is torn down and the session archived; nothing reaches the tracker and no Assignment changes. The plain teardown-and-archive (the agent simply goes away) is not reserved for any particular kind of work. Distinct from [Unclaim](#unclaim): unclaim is a tracker transition that returns the Assignment to the pickup pool, whereas none touches the tracker not at all.

## Artifacts

### Bedrock

The shared two-turn session [Prime](#prime) drives once per run, carrying the cross-context Doctrine and the tenant's project-docs: the priming every Foundation on the tenant holds in common. Each Foundation is forked from the Bedrock with only its own Component turn added, so the two shared turns are driven once rather than re-driven per Component. The Bedrock is transient: it lasts a single Prime run, is never recorded in `foundations.toml`, and is never forked by [Spawn](#spawn); only Foundations are.

## States

The Bob aggregate transitions through four observable states:

- **Spawned**: the Bob exists; no Assignment Claimed yet.
- **Claimed**: the Bob has taken responsibility for an Assignment. The verb lives in vaudeville-pm.
- **Materialized**: PR open; the Bob is running cue's Parlay loop over it.
- **Closed**: the Bob is gone. Terminal; the kind of [Closeout](#closeout) determines what tracker state the Assignment was left in.

## Collaborators

Bobiverse names four collaborators across explicit boundary contracts; see [spec.md](spec.md) for the boundary descriptions.

- **vaudeville-cue**: owns Brief composition and the intra-session lifecycle.
- **workmux**: owns the working surface a Bob runs on.
- **vaudeville-core**: owns the anticorruption layer over the work tracker.
- **GitHub** (via `gh` CLI): PR-status reads for `/closeout`.

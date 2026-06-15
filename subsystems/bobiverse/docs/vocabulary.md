# Bobiverse vocabulary

*This is a UL doc — terms defined in relation to one another. For framework-level UL see `~/.vaudeville/doctrine/vocabulary.md`.*

The verbs and state nouns Bobiverse uses internally. Cross-context terms — **Bob**, **Premise**, **Route**, **Foundation**, **Brief**, **Managed Repository** — are linked to the framework vocabulary, not redefined.

## Verbs

### Prime

Drive Managed Repositories' Foundations into existence across three documentation layers: the cross-context Doctrine every tenant shares, the project context this tenant shares across its repositories, and each Managed Repository's own documentation. The first two layers are identical for every repository on a tenant, so Prime drives them once into a [Bedrock](#bedrock) and forks a Foundation from the Bedrock per Managed Repository, each fork adding only that repository's own layer. The verb's noun-form is **Priming** — the process — and is used interchangeably in prose. Re-Priming replaces the Managed Repository's Foundation wholesale. The Foundation it produces is addressable independent of the clone it was primed in. Prime is the precondition for [Spawn](#spawn).

### Durable / Stranded

A recorded Foundation (`~/.vaudeville/doctrine/vocabulary.md#foundation`) is **durable** when a later [Spawn](#spawn) can fork from it on this host, regardless of which clone the Bob lands in; **stranded** when it is recorded but not present on the host, so a Spawn cannot fork from it — for example a [Prime](#prime) performed inside a smoke that never reaches the host. `vv foundations-verify` reports the stranded Foundations; Ringmaster's post-apply integrity check invokes it so a deploy that left a Foundation stranded fails loudly at apply time rather than at the next Spawn.

### Spawn

The act that brings a Bob into being. Workmux allocates the working surface; the new Claude Code session is forked from the Managed Repository's Foundation so the Bob inherits the priming as conversation history, regardless of where the clone lives; vaudeville-cue renders the Brief and the new Bob reads it as its first user turn. Spawn refuses when no Foundation exists for the Managed Repository. After spawn the Bob is **Spawned** but has not yet **Claimed** a Premise.

### Seeded Clone

A Managed Repository clone the [Foundation](~/.vaudeville/doctrine/vocabulary.md#foundation)'s transcript has been copied into, so `workmux add --fork` resolves the conversation from that clone's own Claude project directory. A [Spawn](#spawn) produces a Seeded Clone and builds the launch only from one, so a Bob is never launched against a clone its Foundation was never seeded into — the in-flight, spawn-time counterpart of a [Durable](#durable--stranded) Foundation, which is the same readiness made persistent and host-wide.

### Design

The optional design pass a Bob runs after the goal is agreed and before [Materialize](#materialize). It consults `/panel` to sharpen the approach across five outside lenses, then commits to a design along three axes: the new or defective ubiquitous-language terms the work introduces; how it should interact with the existing code, including the refactors a clean design requires; and the domain-derived contracts the tests must keep. The committed design lives in the Bob's conversation, which Materialize inherits — Design produces no durable document, so it is not a decision-record artifact. Distinct from the [Doctrine Bracket](#doctrine-bracket): the Bracket frames the writing inside Materialize, while Design is the heavier, panel-backed pass that precedes it. The three axes and the procedure live in the Design skill itself.

### Materialize

Turn a planned Premise into reality: implement, then land it. A thin entry that [Checkpoints](#checkpoint) into `/_continue_materialize`, the implementation body; the code-bearing shape is CI-gated and on success hands off to [Parlay](#parlay), the off-tree shape reports and stops. After materializing the Bob is **Materialized**.

### Parlay

The convergence loop a **Materialized** Bob runs over its PR: address review comments, resolve conflicts against `main`, watch CI. A thin entry that [Checkpoints](#checkpoint) into `/_continue_parlay`, the convergence body. Exits when the PR is reviewer-clean, mergeable, and green; escalates as a failure after three rounds of patching in a single run, on the premise that the volume of correct-looking patches is itself the signal of a misframing the reviewer could not catch.

### Checkpoint

Shed a Bob's conversation mid-run and resume the same work in a fresh context — forward-only, nothing is rolled back to (the database sense of the word does not apply). The Bob reads the [Digest](#digest) and authors the [Carryover](#carryover); `vv checkpoint` then composes the [Resume Brief](#resume-brief) from the two and launches a detached driver, [Teardown](#teardown)'s sibling, that sends `/clear` to the Bob's own pane, waits for the cleared session to appear, and injects the Resume Brief as that session's first turn — the resumed Bob wakes already grounded, never fetching its grounding from disk. A Checkpoint is how control crosses from one lifecycle skill body to the next, and every such control handoff sheds the conversation — which is why a Materialize→Parlay run clears twice. The standalone primitive is `/checkpoint`; [Materialize](#materialize) and [Parlay](#parlay) are thin entries that checkpoint into their continuation bodies (`/_continue_materialize`, `/_continue_parlay`), whose leading underscore marks them as machinery no operator invokes directly; a bare Checkpoint needs no continuation body — its Resume Brief closes with the work itself. Before the irreversible clear, `vv checkpoint` refuses when the continuation skill is not deployed, the Carryover is empty, or the session transcript cannot be resolved, so a misframed checkpoint cannot strand the Bob in a cleared session it can never leave.

### Closeout

Terminate the Bob. Takes one of five **kinds**, each with a different consequence for the Premise the Bob was working on:

- **delivered** — Premise transitions to Delivered. Cross-context kernel kind; see `~/.vaudeville/doctrine/practice/premise-lifecycle.md`.
- **abandoned** — Premise transitions to Abandoned. Cross-context kernel kind; see `~/.vaudeville/doctrine/practice/premise-lifecycle.md`.
- **returned** — Premise transitions to Returned and re-enters the pickup pool. Cross-context kernel kind; see `~/.vaudeville/doctrine/practice/premise-lifecycle.md`.
- **[unclaim](#unclaim)** — Bobiverse-local.
- **[none](#none)** — Bobiverse-local.

Closeout is an orchestration, not a single command: every kind ends in the same [Teardown](#teardown), differing only in the transition run first. Running that transition before Teardown — and aborting if it fails — is load-bearing, because once the pane is gone there is no second chance to record the outcome.

### Teardown

The substrate atom every Closeout kind ends in (`vv teardown`): archive the worktree and the Bob's transcript, then tear the substrate down. It writes nothing to the tracker — the Premise transition is a separate atom, run first. Teardown is the irreversible step of the Bob lifecycle, and the only verb the explicit-invocation guard watches, because a Bob that runs it self-closes.

### Unclaim

The Bobiverse-local transition atom (`vv unclaim`) that returns a Premise to the pickup pool with its assignee cleared and no comment, so it looks as it did before the Bob ever touched it. The kernel terminations (delivered, abandoned, returned) are PM's; unclaim is bobiverse's because "the Bob had no right to exist" is a word about the Bob's relationship to the Premise, not the Premise's deliverable state. Reserved for the procedural-mistake case where teardown is the intent. Distinct from `returned` (a real attempt that stopped partway) and from `abandoned` (a judgment that the Premise should not exist anymore).

### None

The Bobiverse-local Closeout kind that runs no transition atom at all — only [Teardown](#teardown). The Bob is torn down and the session archived; nothing reaches the tracker and no Premise changes. The plain teardown-and-archive — the agent simply goes away — not reserved for any particular kind of work. Distinct from [Unclaim](#unclaim): unclaim is a tracker transition that returns the Premise to the pickup pool, whereas none touches the tracker not at all.

### Winnow

The per-passage prose audit a Bob runs over a PR before review: each comment and each touched documentation passage is tested against the "almost no comments" doctrine and the WHAT/HOW/why layering, then disposed of — deleted, made unnecessary by a fix to the code, relocated to the layer that owns it, or kept for the non-obvious *why* it carries. A producer-side quality pass that transitions no lifecycle state. The decision tree and its grounding live in the Winnow skill itself.

## Procedure

The session-level counterpart to [Route](~/.vaudeville/doctrine/vocabulary.md#route). Route, set on the Premise before any session exists, classifies the shape of conversation the work expects; Procedure, chosen inside the session, classifies how the Bob realizes it. Its members are CI-gated, off-tree, and spike.

The router-dispatched procedures are private — each a `_`-prefixed skill no operator invokes by name, the convention `_continue_materialize` and `_continue_parlay` already follow. The only public entries are the router and `/spike`, the procedure elected by name rather than dispatched.

## Artifacts

### Bedrock

The shared two-turn session [Prime](#prime) drives once per run, carrying the cross-context Doctrine and the tenant's project-docs — the priming every Foundation on the tenant holds in common. Each Foundation is forked from the Bedrock with only its own repository turn added, so the two shared turns are driven once rather than re-driven per Managed Repository. The Bedrock is transient: it lasts a single Prime run, is never recorded in `foundations.toml`, and is never forked by [Spawn](#spawn) — only Foundations are.

### Carryover

What only the conversation built, authored by a Bob just before a [Checkpoint](#checkpoint) clears it: the synthesis, the open edge, and the next concrete action — the part the transcript does not already hold and the [Digest](#digest) cannot derive. The resumed Bob reads the Carryover to continue mid-stride rather than re-plan. Authored, not derived; its counterpart across the clear is the Digest.

### Digest

The operator's verbatim turns, extracted mechanically from the session transcript and line-located back into it, so a [Checkpoint](#checkpoint)'s resumed Bob rebuilds operator intent from primary source rather than a summary. Recovers turns the operator relayed indirectly through a `tmp` file as well as typed ones, and is cumulative across the Bob's checkpoints: a later Checkpoint keeps every earlier session's turns. `vv digest` prints it into the Bob's context. Derived, never authored; its counterpart across the clear is the [Carryover](#carryover), which is authored, never derived.

### Resume Brief

The first user turn a freshly-cleared Bob reads: a grounding frame, the [Digest](#digest), the [Carryover](#carryover), and a closing instruction naming the continuation body to invoke — or, for a bare [Checkpoint](#checkpoint), the work to continue. Composed by `vv checkpoint` and injected into the Bob's pane by the Checkpoint driver once the cleared session appears. The Checkpoint counterpart of the spawn-time Brief (`~/.vaudeville/doctrine/vocabulary.md#brief`): the same act — a first turn composed and injected, never fetched — with the Digest and Carryover where the Premise would be. One Resume Brief per Checkpoint.

### Doctrine Bracket

The bracketing discipline in which the [Materialize](#materialize) skill's implementation step is framed by two reads of the design Doctrine: an opening half that maps the Premise's intended domain logic onto the existing UL and decides what new terms or structure the work needs, and a closing half that re-reads the Doctrine with the diff in hand and revises before invoking [Parlay](#parlay). The bracket's specific questions and rationale live in the Materialize skill itself.

## States

The Bob aggregate transitions through four observable states:

- **Spawned** — the Bob exists; no Premise Claimed yet.
- **Claimed** — the Bob has taken responsibility for a Premise. The verb lives in vaudeville-pm.
- **Materialized** — PR open, [Parlay](#parlay) watching.
- **Closed** — the Bob is gone. Terminal; the kind of [Closeout](#closeout) determines what tracker state the Premise was left in.

## Collaborators

Bobiverse names four collaborators across explicit boundary contracts; see [spec.md](spec.md) for the boundary descriptions.

- **vaudeville-cue** — owns Brief composition.
- **workmux** — owns the working surface a Bob runs on.
- **vaudeville-core** — owns the anticorruption layer over the work tracker.
- **GitHub** (via `gh` CLI) — PR operations.

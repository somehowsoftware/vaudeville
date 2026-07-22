*This is a UL doc: terms defined in relation to one another. For framework-level UL (Bob, Component, Tenant, Context) see `~/.vaudeville/doctrine/vocabulary.md`. The doctrine for this layering is in `~/.vaudeville/doctrine/code/intent.md`. The mechanisms these terms name live in [spec.md](spec.md).*

# vaudeville-hook vocabulary

vaudeville-hook's domain is **the screen**: the outside sense that shows a running Bob, and the corpus it commits, what the Bob's own loop cannot form about itself. The terms below name the parts of a screen. Cross-context terms (**Bob**, **Component**, **Tenant**, **Context**) link to the framework vocabulary rather than being redefined here.

## The screen

The outside sense by which a [Bob](~/.vaudeville/doctrine/vocabulary.md#bob), and the corpus it commits, is measured against a standard from outside the Bob's own loop. A screen watches a [subject](#subject) and, where the subject falls short, shows the Bob a [perception](#perception) — the reading the running loop has no vantage to form about itself — carrying [friction](#friction). That perception is the value of a screen. What a screen is does not depend on how it reaches its [verdict](#verdict), nor on the substrate that sets it watching.

## Subject

What a screen watches: something readable from outside the Bob's loop. One of three — an artifact the Bob commits (a diff, a chat turn, a document), a fact about the session (the context window's fullness, the turns since a checkpoint), or the operator's own turn. The subject is what a screen reads, not what it owns: a screen reads a neighbouring Context's values to say what holds about them, and owns the translation where it leans on a neighbour's concept.

## Perception

The reading a screen shows the Bob on a [verdict](#verdict) that its [subject](#subject) fell short: the thing the Bob's own loop could not form — *your context is filling toward the wall*, *this commit brings* load-bearing *back*, *the operator's frustration marks a fault you have not found*. A perception is data the Bob reads and acts on, distinct from the [friction](#friction) it carries. The perception is what a screen is for.

## Friction

How hard a [perception](#perception) makes it for the Bob to proceed past what it has seen, scaled to how reversible the failure is, not to the gravity of the standard. A continuum, not a set of levels: a perception about an easily-undone mistake arrives light, one the Bob reads and may set aside; a perception about an irreversible one arrives with friction enough to stop the Bob reliably in normal work. There is no top — no friction becomes an absolute wall, because a determined agent routes around anything.

## Verdict

Whether a [subject](#subject) meets a screen's standard: the one thing a screen decides. How the verdict is reached — a glance at a value, a model reading a turn, a cheap question asked before a costly one — is not part of what a screen is; the domain cannot see which produced a given verdict, and a screen reaches its verdict one way today and another tomorrow without becoming a different screen.

## Provenance

Where a screen comes from, one of two: **stock**, shipping with the framework and present for every [Tenant](~/.vaudeville/doctrine/vocabulary.md#tenant); or **Tenant**, supplied by the operator in its own configuration. Independent of [reach](#reach). The screen serves a multi-tenant world only when its stock screens can be turned off and tuned and a Tenant can add its own.

## Reach

How far a screen applies, independent of its [provenance](#provenance): a whole installation, or one [Component](~/.vaudeville/doctrine/vocabulary.md#component) within it, the narrower overriding the broader. A stock screen can be switched off for one Component; a Tenant's screen can apply installation-wide. A screen reaches every session where it is not switched off for that session's Component, and it decides its own reach at the moment it fires, because the scaffolding a session runs under merges its screens additively and cannot subtract a broader one at a narrower scope.

## Screen name

A screen's stable identity in the domain, declared by the screen itself and independent of the substrate that runs it. [Reach](#reach) switches a screen off for one [Component](~/.vaudeville/doctrine/vocabulary.md#component) by naming it, so the name a screen answers to cannot be a fact about its substrate. `no_memory_writes.py` is a script filename; the screen it sets watching is `memory-writes`, and the switch keys on the latter. Keying reach on the filename would leak the substrate into the domain, the leak [the screen](#the-screen) already refuses: what a screen is does not depend on the substrate that sets it watching. Each screen declares its own name, and there is no registry over the names, because self-declaration is all that switching a screen off for one Component needs.

## The headroom screen

The first concrete [screen](#the-screen): a stock screen whose [subject](#subject) is [headroom](#headroom), read from a session-fact rather than an artifact. It watches [effective context](#effective-context) climb and escalates the [Bob](~/.vaudeville/doctrine/vocabulary.md#bob) up a [ladder](#ladder-and-rung) of [rungs](#ladder-and-rung) — from a gentle nudge to checkpoint at a natural seam through to an emergency shed at the top of the ladder — so the Bob sheds its context at a seam while it still holds the headroom to author a faithful Carryover, well short of the [wall](#the-wall) where no Carryover can be authored at all. Its [verdict](#verdict) is read from a single deterministic fact, so unlike a screen over an artifact it needs no confirming inference: which rung the effective context has reached *is* the verdict. It is a sibling of a future emission screen, told apart by its subject (a session-fact against an artifact), not by how it reaches its verdict.

## Headroom

The [subject](#subject) the [headroom screen](#the-headroom-screen) watches: the room a Bob has left to author a faithful Carryover before the [wall](#the-wall). A session-fact, not an artifact — read from [effective context](#effective-context) against the wall, and the thing the [ladder](#ladder-and-rung) is arranged to spend down deliberately rather than let a Bob exhaust by accident. The screen is named for what it protects, not for the token count it measures or the hook it runs on.

## Effective context

The quantity by which [headroom](#headroom) is read: the true size of the context the session sends on a request, measured as the sum of the most recent assistant transcript entry's input, cache-read, and cache-creation tokens. Read from *this session's transcript alone*: a checkpoint or clear opens a fresh transcript that already begins small, so the seam is honored by reading only the current file, never by carrying a number across it. Because the size is a deterministic fact of the transcript, the [verdict](#verdict) it drives needs no inference to confirm.

## The wall

The physics limit past which no faithful Carryover can be authored: beyond it every operation that must send the whole conversation — an ordinary turn, a compact, and the Carryover-authoring turn a checkpoint itself needs — fails alike, and the only exit is a clear that destroys the work. The wall is not a [rung](#ladder-and-rung); it is the fact the rungs are arranged to keep a Bob short of, and no [stay](#stay) can move it, because it is physics rather than policy. Its numeric position is [Tenant](~/.vaudeville/doctrine/vocabulary.md#tenant) configuration.

## Ladder and rung

The **ladder** is the ordered set of thresholds the [headroom screen](#the-headroom-screen) escalates through as [effective context](#effective-context) climbs; a **rung** is one step of it — a threshold in effective context paired with the [perception](#perception) it shows and the [friction](#friction) that perception carries. The rungs climb through four: **gentle**, a nudge to checkpoint at a natural seam; **active**, steering toward a checkpoint-safe state; **aggressive**, checkpoint now; and **emergency**, the top of the ladder — checkpoint now, the shed the earlier rungs did not force. The two lower rungs are *soft* — a [stay](#stay) can postpone them; the two upper rungs fire regardless. Friction climbs monotonically up the ladder, and no rung is an absolute wall: each leaves the Bob a way to proceed. The default ladder is [Tenant](~/.vaudeville/doctrine/vocabulary.md#tenant) configuration, not a fixed scale the screen carries.

## Stay

A Bob-authored, per-session postponement of the *soft* [rungs](#ladder-and-rung): a reason, bound to the session that recorded it, by which a Bob dismisses the gentle and active rungs under a justification the screen reads each tick. A stay names no threshold; it holds for the whole life of its session, because the seam a Bob stays for is ended by the very checkpoint that ends that session — a stay expires exactly when its reason does, and a Bob is never asked to predict a token count it has no way to predict. What bounds a stay is the *hard* rungs rather than a number the Bob chose: it cannot suppress the aggressive or emergency rungs, and it cannot move the [wall](#the-wall) — those are the backstop, and the backstop is physics. Being bound to its session is also what clears it: a checkpoint opens a fresh session, so a stale stay self-invalidates rather than needing a remembered reset. A Bob records a stay through a verb rather than by hand, so that the Bobs deepest in context — the ones that need a stay most — can record one at the moment they need it. Named *stay* (over *slack*, *grant*, *reprieve*) so that "the stay moved the wall" reads as the nonsense it is: a stay postpones a soft rung, it does not buy headroom that physics did not grant.

## The reseat-engagement screen

A second concrete [screen](#the-screen), sibling to the [headroom screen](#the-headroom-screen): both read a [session-fact](#subject) from this session's transcript and need no confirming inference, and are told apart by which fact they watch. Its [subject](#subject) is whether a reseated [Bob](~/.vaudeville/doctrine/vocabulary.md#bob) has *taken up* its Brief on its first turn. A reseat sheds an oversized conversation into a fresh, empty session whose opening user turn is its Resume Brief; a spawn or an interactive bob forks the primed [Foundation](~/.vaudeville/doctrine/vocabulary.md#foundation) instead and opens on something else — and that opening is the whole discriminator, so the screen watches a session whose first turn is a Resume Brief and is silent on every other birth. Its [verdict](#verdict) is turn-state read at turn completion, never a prediction about silence: the model ended its first turn having taken no action — text, and no tool call — which is a completed fact the moment the turn ends, not a timer's guess that a Bob has gone quiet.

Where the reseat has stalled, the screen shows the [perception](#perception) the born-degenerate turn had no vantage to form — that it echoed its trailing context and stopped — and refuses the turn's stop to feed it back, pointing the Bob at its Brief. Its [friction](#friction) is bounded and low, because the stall is fully recoverable: it re-engages a small fixed number of times, then, rather than loop, releases the session and raises a pane-level alarm for the operator in place of another nudge. No re-engagement is an absolute wall, and the bound sits below the harness's own consecutive-refusal cap, which stands behind it as the backstop.

# Prerequisites

Most of the time, you shouldn't use Vaudeville. That is not modesty; it is the framework's own logic applied to itself. A discipline built to refuse ceremony has to begin by refusing to be adopted as one.

The full argument for the class of software this serves is [The point](./the-point.md). What follows assumes that argument and compresses it into a fit-check with three parts: the terrain, the operator, the repository. All three have to pass. Two out of three is a no.

## The terrain

Vaudeville is four-wheel-drive low range. Low range is slow, loud, and fuel-hungry, and on pavement it does not merely waste effort — it binds the drivetrain and fights the driver. Almost all driving is on pavement. You engage low range for the one terrain that actually requires it, and you disengage it the moment the terrain ends.

The terrain that requires it is depth: systems whose parts are individually intelligible but whose total coordination burden exceeds what one mind can hold in stable relation, where the dominant risk is not bad code but a wrong abstraction quietly becoming load-bearing under competent-looking work. On that terrain the bottleneck is never generation — it is keeping the system's meaning intact while a great deal of locally plausible work is applied to it, and that is the one job this framework is built to do.

If your work is velocity — building what you already understand, fast — or reach — building what you do not know how to build but the model does — then a coding agent's generation capability gets you what you need with no coherence framework wrapped around it. The mainstream tools serve those two superbly. Vaudeville's friction is deliberate and aimed; pointed at velocity work it is pure cost, low range on dry asphalt.

## The operator

The framework makes assumptions about the person running it, and they are easier to check than to acquire.

**Domain-driven design as a working habit, not a book you respect.** The framework's primary substrate is shared vocabulary between human and AI: bounded contexts as jurisdictions of meaning, ubiquitous language as a discipline rather than documentation. The operator's actual job involves the ajudication of meaning — choosing names, deciding which distinctions matter, noticing when one word is quietly covering two concepts. If you have never done that work by hand, the framework hands you the job anyway, with no apprenticeship.

**Comfort with XP-shaped engineering opinions, because they are not configurable.** Tests before code; contracts before modules; names that hit you over the head; correctness over expedience even when expedience would visibly save time. These are baked into the doctrine every agent primes against — which means an operator who disagrees with them is not running a different methodology, they are outvoted by their own workforce. Every Bob arrives believing tests are written first. You can fight that on every Premise, or you can already agree.

**An appetite for deliberate friction.** The framework maximizes friction against the unresolved conceptual problem and minimizes it everywhere else — which, from the inside, feels like: an agent holding a position against you instead of folding; being asked whether this is even the right thing to want when you arrived ready to build it; progress that shows up as a renamed primitive or a rejected interpretation rather than a diff. If your sense of momentum is tied to watching code appear, this process will feel like obstruction. It is obstruction — aimed, on purpose, at the escape routes premature implementation provides.

Extreme-programming people will probably like it here; most people will probably hate it. Both reactions are accurate readings of the same facts; this document exists so you can have yours before it costs you anything.

## The repository

The machinery's unit of grip is the repository. Priming compiles a [Foundation](doctrine/vocabulary.md#foundation) per repository; a [Premise](doctrine/vocabulary.md#premise) resolves to one; a [Bob](doctrine/vocabulary.md#bob) spawns into one repository's worktree and works nowhere else. All of that assumes the repository boundary is a semantic boundary — that each repository is a [bounded context](doctrine/vocabulary.md#bounded-context), or at least a single coherent responsibility.

So the project should be greenfield, already decomposed into single-responsibility repositories, or at a stage where that decomposition is tractable and you are prepared to do it as the entry work. Greenfield is the best case — not because the framework needs a blank slate, but because boundaries are a first-class work product here, and greenfield is where they are cheapest to draw and cheapest to move.

A legacy monolith that has not been decomposed is not a good starting point, and the framework will not rescue it. A repository hosting six tangled jurisdictions gives priming nothing coherent to compile, a Bob no bounded blast radius, and the vocabulary discipline a union of dialects instead of a language. Decompose first, or look elsewhere.

## You're not wrong to reject this

This is the wrong tool for almost every job. Really and truly. It's okay to bounce.

## If you are still here

If the above is actually attractive to you, then [The point](./the-point.md) explains what you are signing up for, and [Weaponized philosophy](./weaponized-philosophy.md) explains why it looks the way it does. Also, I'm super interested in hearing about your project: `vaudeville at somehowsoftware dot com`.

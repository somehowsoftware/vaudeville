# Vaudeville — the opposite of vibe coding

There are three things you can want from coding agents, and this framework sells exactly one of them.

| You want | Which means | Where to get it |
| --- | --- | --- |
| **Velocity** | Building what you already understand, fast | The mainstream agent tools — they are excellent at this |
| **Reach** | Building what you don't know how to build, but the model does | The same tools, the same excellence |
| **Depth** | Building systems whose parts are individually intelligible but whose whole exceeds what one mind can hold in stable relation | Here |

Vaudeville is an engine for depth, and its method — dialectical engineering — is not about coding. The point is work that neither a human nor an agent could produce alone: the operator adjudicates meaning — names, framings, which distinctions matter — while the agent holds the whole system in one curated context window, which is the common intuition about agents (good for prototypes, blind to the big picture) turned exactly on its head. Between the two runs a sustained, opposable argument in which misunderstandings surface and become the insight. The coding is residue: what falls out once the earlier questions have been forced into clarity. Which is why this framework does the opposite of what agent tools are built for — it does not let you walk away. It aims your attention instead of freeing it.

The machinery enforces one asymmetry everywhere. Friction that is accidental — setup, bookkeeping, navigation, integration grind — is driven toward zero. Friction that is deliberate — the seams where two understandings diverge — is amplified and handed both parties' cleared attention. The friction is the product: the argument is where the work gets done that neither party could have done alone.

The enemy is not bad code; agents stopped writing obviously bad code a while ago. It is plausible code that quietly changes what the system means — nearby concepts blurring into one another until the words say one thing and the system does another: a predicate becomes a filter, a user-interface metaphor becomes a domain primitive. Every diff reads as reasonable, and the system is wrong in a way that surfaces only when the parts compose. Depth work concentrates this failure. Keeping meaning intact across every hand-off is the framework's containment layer — necessary, engineered hard, and not the point.

The parts list is the one you have seen everywhere: ephemeral agents, git worktrees, primed contexts, tests as contracts, pull requests, a tracker. Nothing in the inventory is new, and stealing any single part will not give you Vaudeville — nobody who builds an interesting robot is bragging about the servos. What differs is what the assembly is aimed at, and the discipline is genuinely demanding: XP and domain-driven design at full strength, a vocabulary enforced rather than encouraged, an agent under standing instruction to oppose you, acceptance criteria banned from the unit of work whose framing must stay open. If your sense of momentum is watching code appear, this will feel like obstruction. It is obstruction, aimed on purpose at the escape routes premature implementation provides.

The evidence status, plainly: the failure mode this targets is documented by parties with no stake in the framework; the harm of the *delegation* mode of agent use is among the best-replicated results in the young literature; and the benefit of the mode this framework enforces is a named, falsifiable wager — not a finding. The framework builds itself and has one committed operator, which is an existence proof and nothing more. [The theory](theory/) states what would change our minds, and the experiments queued to test it — including [the miss](theory/the-miss.md), where the first edition of this corpus failed in exactly the way the framework says work fails, and the record of what caught it.

Most software does not need this. Velocity and reach cover nearly everything, and for that work this framework is pure cost — four-wheel-drive low range on dry pavement. The gate, honestly: a system whose parts are simple but whose coordination burden exceeds one mind; an operator with domain-driven design as a working habit and an appetite for being argued with; repositories decomposed along semantic boundaries, or a greenfield where they can be. Anything less is a no, and you're not wrong to bounce. But the class of work that passes the gate is, on this corpus's own argued-and-untested claim, a frontier rather than a niche: software that mostly went unattempted, because coherence at that interaction density could not be bought at human prices. One more thing, so you know what you are signing up for: the process depends on you being wrong, confused, and ignorant in front of a partner, on purpose, repeatedly. That is what the friction is for.

Where to go next:

- [The map](map.md) — the whole framework in one read: the axiom, the engine, every practice a derivation.
- [The theory](theory/) — the argument at full length, with its evidence and its joints exposed. Reading for the ideas rather than the tool? Enter here.
- [The manual](doctrine/manual.md) — install the framework and run your first assignment; start playing without the whole rulebook.
- [The vocabulary](doctrine/vocabulary.md) — every coined term, defined once.

If you are staring at a problem with this shape, I want to hear about it: `vaudeville at somehowsoftware dot com`.

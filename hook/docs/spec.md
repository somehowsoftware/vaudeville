*This is a spec: high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code. The doctrine for this layering is in `~/.vaudeville/doctrine/code/intent.md`.*

# vaudeville-hook

A Bob cannot see all of its own running. From inside its loop it cannot tell that the fix it just committed patches over a failing case in code it wrote minutes ago, instead of repairing what made the case fail; it cannot tell that the sentence it is drafting leans on *load-bearing*, a tic the prose was scrubbed of; it cannot feel its context window filling toward the wall where it will start to forget. These are blind spots the way you cannot smell your own breath: not failures of effort, only places the loop has no vantage on itself.

A **screen** is the outside sense that shows a Bob what its loop cannot form. As the Bob commits a fix, a screen shows it *this patches over the failing case; the cause is still live one call up* — and the Bob, which from inside the loop saw only the test going green, repairs the cause instead. The Bob holds a reading it could not have reached from inside, and works better for it. vaudeville-hook owns the screen: the standards a Bob, and the corpus of code and prose it commits, are measured against from outside the Bob's own loop.

The screen is the third thing around a running Bob. What the Bob does of its own volition is vaudeville-cue's; the lifecycle that spawns and retires it is vaudeville-bobiverse's; the screen shows the Bob where it has fallen short of a standard, from outside that volition, while the Bob runs. The wall with cue is volition: cue is what the Bob chooses, the screen is what it is shown whether it chose to look or not.

## What a screen watches, and what it shows

A screen watches a **subject** — something readable from outside the loop: an artifact the Bob commits (a diff, a chat turn, a document), a fact about the session (how full the context window is, how long since the last checkpoint), or the operator's own turn. Where the subject falls short of the screen's standard, the screen shows the Bob a **perception**: the reading the loop could not form. *Your context is two thousand tokens from the wall.* *This commit brings* load-bearing *back into prose it was cut from.* *The operator's frustration marks a fault you have not found — look there, not at your tone.* The perception is what a screen is for; everything else is how it comes to be shown.

## Friction

A perception arrives with **friction**: how hard the screen makes it for the Bob to proceed past what it has seen. Friction is not the gravity of the standard; it is the cost of the mistake, and it scales to how reversible that mistake is. A perception about a stylistic nit the Bob can undo in a keystroke arrives light — a note the Bob reads and may set aside. A perception about a commit that would bury a subtle defect under a hundred later ones arrives heavier — the Bob proceeds by fixing the work, or by recording why the screen is wrong, which the screen reads the next time. A perception about a write the Bob can never take back arrives heaviest of all, carrying friction enough to stop a Bob reliably in the ordinary course of its work.

There is no top to the scale, no friction so high it becomes a wall. A determined agent routes around anything; the heaviest screen is friction tuned high enough to arrest a Bob reliably in normal operation, never a barrier that cannot be passed, and the screen does not pretend otherwise. What makes the high end high is irreversibility — that the mistake, once made, stays made — not the gravity of the standard the Bob crossed.

## Which screens are live

A screen has two placements, independent of each other. Its **provenance** is where it comes from: a screen ships stock with the framework, present for every Tenant, or a Tenant supplies its own. Its **reach** is how far it applies: across a whole installation, or over a single Component within it, the narrower overriding the broader — a stock screen switched off for one Component, a Tenant's screen applied installation-wide. The screen is not fit for a multi-tenant world unless its stock screens can be turned off and tuned and a Tenant can add its own: the re-synced-path screen above is one machine's peculiarity, with no business shipping to every Tenant. A Tenant draws the line between what is its own and what is one node's inside its own configuration; the screen does not model that difference.

## Collaborators

**vaudeville-cue** owns what a Bob does of its own volition within the session. The wall is volition: a screen is shown to the Bob from outside what it chose.

**vaudeville-bobiverse** owns the lifecycle around the session — spawn, prime, closeout, teardown. A guard that stops a running Bob from an act it must not take is, by what it does, a screen at the high-friction end, wherever it ships today.

**vaudeville-ringmaster** assembles the live screens into the scaffold every Bob runs under, so a screen is present in every session without per-Component wiring.

**The Tenant configuration** holds the Tenant's own screens, and the on-off and reach settings over every screen, stock and Tenant alike.

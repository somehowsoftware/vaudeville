# Language before code: making a breaking conceptual change

Sometimes the ubiquitous language itself is what's wrong: a concept is misnamed, a
genus is missing, two ideas are fused under one word. Fixing that is not a refactor
and not a feature. It is a re-carving of what the words mean, and it ripples through
the ubiquitous language, code, tests, and prose at once. This page is the standing procedure for
making one.

The procedure exists because of what an agent *is*. A human engineer can hold a new
concept in their head and tolerate a codebase that is half-renamed for a while. An
agent cannot: it reasons *from* the names in front of it, so an inconsistent
ubiquitous language doesn't merely slow it; it routes it into the wrong world, and
it gets stuck authoring meaningful PRs. Naming consistency is not hygiene here. It is
a precondition for the agent to function at all.

The whole method is one inversion: **fix the language everywhere first, before
changing any behavior.** Everything below falls out of that.

## 1. Commit the concept to the ubiquitous language

Settle the new concepts in the ubiquitous language first (the vocabulary, the relationships, the
constraints), and nothing else moves until this is right. This is the single
highest-blast-radius commit in the sequence: every later step propagates whatever you
write here. Get the genus wrong and you have spread the error across every repository,
at constellation-wide retraction cost. This is why the dialectic over a new concept
earns its length. It is not ceremony; it is the most expensive bet you will place.

## 2. Rename the whole world to the new language: keep the tests green

Right after that merges, and before anything else, rename to the new language
everywhere: variables, functions, commands, comments, prose. This is a
behavior-preserving pass (the code does exactly what it did, under new names), so
**the tests stay green.**

That green is the point, not a reassurance. The tests now describe the right concepts
while the code still does the old thing, and the discord is glaring: a test that
*passes* under corrected names is a louder defect signal than one that fails, because
it indicts the *specification* rather than the implementation. It is green while
asserting behavior the new concepts call wrong.

**Carve out the names that are data.** A rename is behavior-preserving only while the
name is a symbol. The moment a name is a stored value, an enum the tracker persists,
or a cross-context contract (a `type` field, a string literal a branch compares
against), renaming it *is* a behavioral change, and "stays green" becomes false. Do
**not** rename those here. Leave them, and they become the brightest signposts you
have: a new-world identifier compared against an old-world string (`assignment.kind
== "Bug"`) is a sparking star marking exactly where a later behavioral PR must act.

## 3. Make the breaking changes, one behavior at a time

Now the behavior. Each change is its own PR that fixes one behavior *in its entirety*,
in this order: **tests first (red), then code (green), then prose.** The order is what
makes it tractable for an agent, because each step catalogs the next:

- **The tests to break catalog themselves**: their titles no longer make sense under
  the new names. Make those red against the correct behavior.
- **The code to change catalogs itself**: it is the code whose tests are now red.
- **The prose to fix catalogs itself**: it is the prose now discordant with reality,
  and you know the replacement because the facts are manifest.
- **The data and contracts to migrate catalog themselves**: they are the sparking
  stars left in place at step 2.

## 4. Treat the catalog as a signpost, never a worklist

The self-cataloging is the method's gift and its trap. A discordant test points you at
an *area* that is affected; it does not enumerate everything wrong there. Behavior with
no test, or a test named at the mechanism level rather than the concept level, will not
announce itself by going nonsensical. So after you have worked the catalog, **explore
the area for untested landmines**, and where the codebase is small enough, run a full
scan as a backstop. The characteristic agent failure here is to treat the enumerable
checklist as the definition of done; so the gap pass is a required step, not a
footnote.

## 5. One big mutation at a time

Between the rename in step 2 and the last behavioral PR in step 3, the suite is green
while encoding wrong behavior. Across a federation that trusts green CI as "safe to
build on," that window is shared: a second concurrent conceptual mutation, or a Bob
spawned into unrelated work mid-window, reads a lying green. So **only one breaking
conceptual change is ever in flight across the constellation at a time.** It costs
parallelism; that is the price of not poisoning the trust signal. Where the window must
stay open a while, mark the discordant tests (an `xfail`, or a `KNOWN-WRONG` tag
carrying the reason) so the green reads as provisional, not done.

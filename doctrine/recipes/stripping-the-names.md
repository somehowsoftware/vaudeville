# Stripping the names: a domain-model diagnostic

When you suspect a subsystem's domain model has gone wrong (the names feel
off, implementation detail keeps creeping into how anyone describes what the
thing does, a repository feels like it is quietly doing two jobs), this is the
diagnostic to reach for. It finds where a mechanism is standing in for a
missing concept. You wield it; you do not run it to a guaranteed output. It
stages evidence, and you are the judge who reads it.

The whole technique turns on one fact about what you are: **the namer is blind
to the name.** You cannot describe this subsystem without reaching for the very
words under audit. The moment a word exists it fills the hole a missing concept
would leave, and the gulf closes before you notice it was there. `PublishedVersion`
*is* the concept, as far as your fluency is concerned: which is why you will
never find the better word by thinking harder. The description has to come from
somewhere that never learned the words.

## The method

**1. Describe the substrate from a clean context.** Spawn describers that have
never seen the subsystem's coined vocabulary, hand them the code, and ask what
it does in plain terms, every label unfolded into its mechanics: the actual
files, bytes, git objects, shell commands a behaviour comes down to. What comes
back reports the substrate instead of parroting the names under audit. Run more
than one, because where two clean readings of the same code diverge is itself a
finding.

This is the decisive step, and the one that cannot be made mechanical.
Spawning the describers is rote; the quality of what they return is judgment,
and it decides everything downstream. A description still wearing the coined
words has corrupted the experiment before the panel convenes, and no amount of
agreement later will detect it. Reduce "strip the vocabulary and unfold to
mechanics" to a script and you have thrown away the only check the technique
has.

**2. Put the naive descriptions, with the subsystem's current ubiquitous
language, to `/panel`'s design cast.** Those five lenses (Evans, Beck,
Wlaschin, Hickey, Bernhardt) are the same court the [language
doctrine](../code/language.md) names to decide whether a term earns domain
standing, which is why their reading carries weight here rather than being one
more opinion. Each reads independently and reports where the naive description
had to reach for an implementation detail (a filename, a wire format, a storage
pointer) to say what a domain word should have said. Lift the panel's usual
length cap: these are full proposals, not quips. The synthesis is yours, the
operator-and-agent dialectic, not a sixth lens.

**3. Read what the panel surfaces.** The gap takes whatever shape it has, and
the two shapes seen so far differ in kind:

- *A word standing in for a concept.* The lenses point at the same hole (an
  implementation pointer carrying meaning a domain word should carry), and the
  finding is a corrected vocabulary. In one run,
  `Published Version` was a storage pointer in a domain costume; the lenses
  settled on *Release* as the concept underneath, and the code moved onto it. A
  corrected vocabulary is a breaking conceptual change; hand it to
  [language-before-code](./language-before-code.md) to carry out.
- *A boundary the name was hiding.* The clean descriptions come back reaching
  for two disjoint substrates (these commands and byte-layouts here, those
  there, with no referent in common), and that non-overlap *is* a context
  boundary the single name was papering over. The finding is structural: one
  repository is two [Contexts](../vocabulary.md#context)
  conjoined. In another run, the describe step surfaced exactly
  this, with no vocabulary to migrate at all. A boundary is a decomposition, not
  a rename.

These two shapes are not the menu. The method finds the gap; it does not promise
the gap's shape. A third subsystem may hand you a missing invariant, or a leak
across a boundary that genuinely exists: shapes neither run met. Read what is
there.

For the vocabulary case, a second pass turns the corrected language into a
concrete plan. Extract a faithful skeleton of the code (module layout, type and
DTO names, function signatures, and the test names and fixtures, since the test
names are the contracts and the fixtures the most telling artefacts) and hand
it back to the same cast with the consensus vocabulary, asking how they would
move the code onto it. Synthesise their answers into an ordered refactor
sequence. That sequence is an application of
[language-before-code](./language-before-code.md), not a rival to it: this pass
produces the plan, that discipline carries it out.

## When the lenses converge, and when they split

Convergence is the seductive part and the easiest to over-read. Five lenses
agreeing looks like five independent instruments reading one temperature, but
they are not independent. They are one cast, chosen for a shared conviction, fed
one set of descriptions, answering one prompt; they are correlated by shared
cause. Their agreement rules out a single lens's idiosyncrasy. It does *not* rule
out the shared prior settling on a domain word where none belongs. Convergence
is a floor under one error, not a proof.

So spend your trust on the surprising result, not the tidy one. Five lenses
handed "what is the right word for this" who instead independently answer "wrong
question: this is two contexts" have broken a frame you gave them, and a broken
frame is worth more than a filled-in one. And read a split as a reading, never a
failure: when the lenses scatter rather than converge, the hole is likely
structural rather than lexical: which is how the boundary case announced itself.
The technique has not failed you when the panel disagrees; it has told you
something.

## What is tooling, what is judgment

One step here is genuinely mechanical: the skeleton extraction, an `ast` walk
that keeps the signatures and test names exact and is cheap to regenerate.
Everything else is judgment: including the step that looks most mechanical, the
clean-context describe, and the two reads of the panel, which are irreducibly
yours. A codification that hard-codes the judgment parts is worse than none: it
manufactures the convergence it was meant to discover. Tool the `ast` walk;
wield the rest.

## The why to carry

If you hold one thing from this page when your subsystem looks like neither of
the two above, hold the reasons, not the steps. The describers run clean because
the namer is blind to the name. The panel runs five lenses because no single
lens can tell its own bias from the shape of the domain. And the deliverable was
never the vocabulary or the refactor sequence; it is *the gap the costume-free
description could not cover*, in whatever shape that gap takes. Hold that, and
you can rebuild the diagnostic against a subsystem neither run resembled. Hold
only the steps, and you will run them faithfully off a cliff.

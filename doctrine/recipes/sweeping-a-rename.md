# Sweeping a rename across the constellation

When a breaking conceptual change has been settled — a genus renamed, a concept
split from the word that was hiding it — and the new vocabulary has to reach
every repository that still speaks the old one, this is the recipe for carrying
it out. [Stripping the names](./stripping-the-names.md) finds the gap;
[language before code](./language-before-code.md) sequences the landing — the
ubiquitous language first, then the world renamed under green tests, then the
behavioural carve-outs one at a time. This page is the third thing: *how you
actually run the rename across many repositories without missing sites*, which
becomes its own problem the moment the change is larger than one agent can hold
in stable view.

The technique turns on one fact, the same one [stripping the
names](./stripping-the-names.md) turns on, aimed at a different step: **the
editor is partly blind to its own misses.** An agent that has just renamed a
hundred sites has built, across those hundred edits, a picture of what it
changed — and it reviews against that picture, not against the code. The site it
skipped is exactly the site its picture does not contain, so re-reading its own
work confirms the picture and sails past the gap. One pass always misses. The
miss is not carelessness you can exhort away; it is structural, and the only
thing that finds it is a reading that never held the first picture.

## The method

**1. Forge the discriminator before you touch a file.** The whole sweep rides on
one question sharp enough to sort *every* occurrence of the word, with the
keep-cases named up front so no agent has to invent them. A rename is rarely
one-to-one: the word under audit usually means two or three different things,
and only one of them moves. Write the test as a question with a crisp answer per
bucket, and make the buckets exhaustive. For a genus rename it was *would this
still be true if the assignment were a Direction or a Command?* — yes means the
genus and moves, no means the kind and stays. For a word doing triple duty the
test forks three ways: the per-Component unit → the new genus, the tracker's own
project → keep (it is the foreign system's word, which the anti-corruption layer
exists to translate, not to adopt), ordinary English → keep. Hand every agent
the same discriminator and the same enumerated keeps; a sweep where each agent
re-derives the rule is a sweep where each agent draws the line somewhere
different.

**2. Fan out one audit agent per Component, editing against fresh `origin/main`.**
Each agent owns one repository: it greps every occurrence, classifies each
against the shared discriminator, and makes the swaps the discriminator says
move — behaviour-preserving, so **the tests stay green**. Three disciplines are
not optional. *Carve out the data.* A name that is a stored value, an enum the
tracker persists, a config key a tenant writes, a CLI verb an operator types, or
a string literal another repository compares against is not a behaviour-preserving
rename — renaming it is a behavioural change, and it splits into its own PR (see
[language before code](./language-before-code.md)). Leave those in place and mark
them; they are the brightest signposts the next pass has. *Hunt emergent
wrongness.* A correct-looking swap can manufacture a defect in the sentence
around it — change one "Premise" to "Assignment" and a neighbouring "the Premise
itself" is left dangling, a broken referent the swap created. The awkwardness is
not cosmetic; it is the sign the classification at that site was wrong. Read the
whole sentence around every edit, not the token. *Take truth from `origin/main`,
freshly fetched, never a local clone* — a clone a commit behind hands the agent a
stale picture and it sweeps against text that no longer exists. This one bites;
it bit the rename this recipe is drawn from.

**3. Fan out an independent verify wave — blind.** When the audit wave lands,
spawn a second agent per repository that **did not make the edits and is
forbidden from reading the first wave's notes, ledgers, or scratch.** The
independence is the entire mechanism: an agent that reads the audit's own account
of what it changed inherits the audit's blind spot and ratifies it. Give the
verifier the discriminator and two jobs. *The false-negative hunt:* grep the word
over the current tree, classify every remaining occurrence from scratch, and
report any that should have moved and did not. *The coherence cold-read:* read
every changed passage in full and paraphrase each in one line; a passage it
cannot paraphrase is a defect, because prose that no longer parses cannot be
summarised. What the verifier flags is not noise to argue down — it is the
structural miss the first pass could not see.

## Why the second pass is not optional

It is tempting to treat the verify wave as belt-and-suspenders and skip it when
the change feels small. The rename this recipe is drawn from felt small — a
one-token genus rename, most of it already done — and the audit wave still missed
real sites: a genus reference left unrenamed, a config mention overlooked, and a
clutch of `a Assignment` article errors the swap itself introduced and then read
straight past. The independent wave found every one. A non-independent re-read
would have found none, because it reviews against the same picture that produced
them. Budget the second pass from the start; it is where the defects are caught,
not where their absence is confirmed.

## What is tooling, what is judgment

The greps are mechanical, and spawning the agents is mechanical. Everything
between is judgment: forging a discriminator that actually sorts the hard sites,
classifying the occurrence the rule only half-covers, seeing the referent a swap
broke, telling a carve-out from a rename. The step that looks most mechanical —
"rename X to Y" — is the one a search-replace gets wrong, because the word means
more than one thing and only reading each site tells you which. Reduce the
classification to a script and you have rebuilt the search-replace this recipe
exists to refuse. Tool the greps; wield the rest.

## The why to carry

If you hold one thing from this page, hold the reason for the second wave: you
cannot verify a rename against your own memory of having done it, because that
memory is the negative of the sites you missed. Independence is not
thoroughness; it is the one reading that does not share the first pass's blind
spot. The discriminator is what makes the sweep consistent, the carve-out is what
keeps it green, the cold-read is what proves it coherent — but the independent
second pass is what makes it *trustworthy*. Hold that, and you can run a sweep no
single agent could have held. Hold only the steps, and you will fan out a hundred
confident, identical misses.

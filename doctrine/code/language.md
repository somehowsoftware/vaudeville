# Language

Governs the words used in code, tests, documentation, and conversation.

## Ubiquitous language is the invariant

Synonyms are cracks where bugs hide: any local invention that names a concept the glossary already names is a finding, not a stylistic choice.

Resolve naming confusion before writing code. A concept that is awkward to name signals the domain model needs refinement; stop and discuss rather than push the awkwardness into the codebase. A `SoAndSoContext` object that bundles parameters nobody would say aloud is an unnamed concept, not a helper.

Every change should leave the language clearer than it found it.

## New terms must earn domain standing

Before adding a term to the ubiquitous language, ask whether Eric Evans, Kent Beck, Scott Wlaschin, Rich Hickey, or Gary Bernhardt would recognise it as a genuine domain concept — the kind of word a domain expert would say aloud, independent of how the code happens to be structured. Then ask whether it clarifies what the system is *for*, not how it goes about its work. A term that fails either question is an implementation detail wearing a domain costume; leave it out of the vocabulary and name the construct with whatever plain words the domain already has.

## Names hit you over the head

Code should read literately. If a comment is required to explain what a function does, the function name is wrong. Use full words, not abbreviations; names may be long where clarity demands it; align with the domain's terminology, not invented synonyms. Function names must be grammatically valid — `collect_nodes_with_constraints`, not `collect_constrained`. Adjectives are not nouns.

## Almost no comments

Tests reveal the *what*; code reveals the *how*; architecture reveals the *to what end*. Comments exist only for what genuinely cannot be encoded into the code — usually *why* explanations for non-obvious decisions. References to ephemeral artefacts (issue numbers, pull-request links, story names, incident names) do not belong in comments or in any other persistent prose the repo carries. Neither does describing code by its own history: phrasing that frames the present against a past state — what it used to be, what was fixed, what it now does *instead of* a prior version. Persistent prose says what the code is, never the journey that produced it; the journey and its ephemeral references survive in the PR description and the commit message.

A comment that still seems necessary after the names are literate marks a failure of factorization or test design — re-implement until the code carries it. Docstrings are banned.

The layering of WHAT/HOW/why across docs, tests, and code is in [intent](./intent.md); the principles here govern the vocabulary that fills each of those layers.

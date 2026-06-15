---
name: winnow
model: opus
effort: high
description: >
  Audit the comments and documentation a PR touches: a comment or docstring
  may stay only if it states something the code cannot show. Make the code
  literate and delete the rest — renaming, or re-implementing the piece when
  a rename is not enough — one passage at a time.
---

# Winnow

Walk the comments and documentation a PR touches and make each passage earn its place against the doctrine, so narration, restatement, and references to state that won't survive the merge never reach review. It is a producer-side pass, run on the diff before it reaches review.

## When to use

On a PR's diff, before it goes to review. The surface is what this branch changed: the comments and documentation the diff adds or modifies, and — the case a plain `git diff` misses — any comment left untouched while the code under it changed, since the change is what made it stale. Read the code around each hunk, not only the altered lines. Prose whose subject the change did not touch is out of scope: winnow audits the change, not the repository.

## Ground in the doctrine

Re-read these from the files, not from memory — they are the standard the audit applies:

- `~/.vaudeville/doctrine/code/language.md`, "Almost no comments": a comment exists only for a non-obvious *why* the code cannot carry. Ephemeral references — issue / PR / story / incident ids — are noise, and so is history framing that describes the code against a past state ("what this used to be", "X, already injected"), which leaves the reader chasing a state the tree no longer holds.
- `~/.vaudeville/doctrine/code/intent.md`: the WHAT/HOW/why layering — tests carry the low-level WHAT, the spec the high-level WHAT, the code the HOW, a comment only the non-obvious why.

The tree below is that layering made runnable. Ground your judgement in the doctrine, not in this summary of it.

## The standard

A comment or docstring earns its place only if it states something strictly **not observable from the code** — an external contract, a hazard, a *why* the code cannot show. Anything that describes *what the code does* is forbidden, docstrings included: a module or function docstring that names the code's job is describing the code, so it goes. A comment is never a licence to leave code unclear.

## The tree

Most of this work is not deleting comments — it is making the code carry what the comment was carrying, after which the comment has nothing left to say. For each comment and docstring in scope, in order:

1. **Does it state something strictly not observable from the code?** If yes, it may stay — and ask whether the spec is its better home, moving it there if so. If no, it describes the code: steps 2 and 3 make the code carry what it was saying, and only then does the comment go.
2. **Make the names carry the meaning.** Rename for literacy. The tells of a name doing a comment's job: an abbreviation, an adjective or preposition standing in for a noun or verb, a grammatically incomplete name, or a clever expression explained in prose instead of unpacked into named steps.
3. **Is the piece still illegible once the names are literate?** Then the comment was masking a deeper failure — of factorization or of test design — not a naming gap. Do not settle for a cosmetic rename: reject this implementation of the piece, ask the five whys to find the root cause, and re-implement it for clarity. Clarity always translates to maintainability; that is what the re-implementation buys.

Delete the comment only once the code carries what it was carrying — deletion is the last act, never a substitute for making the code legible.

## The documentation pass

Read the documentation the PR touches for the same fault — prose that does not carry its weight:

- **Self-indulgence and rambling**: prose written for the writer, not the next reader — throat-clearing, repetition, the scenic route to a point one sentence would make.
- **Ephemeral references**: tracker ids, and history-against-a-prior-state framing, that mean nothing to a future Bob who never saw the state they name.

Cut or tighten what fails. Where the content is real but misplaced, relocate it to the layer that owns it rather than deleting it.

## Apply, don't report

Winnow makes the edits in the working tree. It is not a review that hands back a list — each passage is disposed of where it lives, so the diff that reaches review is already clean. When the honest fix is to re-implement a piece rather than re-word a line, that is the work winnow does, not a follow-up it defers.

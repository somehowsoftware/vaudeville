---
name: winnow
model: opus
effort: high
description: >
  Audit the comments and documentation a PR touches: a comment or docstring
  may stay only if it states something the code cannot show. Make the code
  literate and delete the rest (renaming, or re-implementing the piece when
  a rename is not enough) one passage at a time.
---

# Winnow

Walk the comments and documentation a PR touches and make each passage earn its place against the doctrine, so narration, restatement, and references to state that won't survive the merge never reach review. It is a producer-side pass, run on the diff before it reaches review.

## When to use

On a PR's diff, before it goes to review. The surface is what this branch changed: the comments and documentation the diff adds or modifies, and (the case a plain `git diff` misses) any comment left untouched while the code under it changed, since the change is what made it stale. Read the code around each hunk, not only the altered lines. Prose whose subject the change did not touch is out of scope: winnow audits the change, not the repository.

## Ground in the doctrine

Re-read these from the files, not from memory; they are the standard the audit applies:

- `~/.vaudeville/doctrine/code/language.md`, "Almost no comments": a comment exists only for a non-obvious *why* the code cannot carry. Ephemeral references (issue / PR / story / incident ids) are noise, and so is history framing that describes the code against a past state ("what this used to be", "X, already injected"), which leaves the reader chasing a state the tree no longer holds.
- `~/.vaudeville/doctrine/code/intent.md`: the WHAT/HOW/why layering (tests carry the low-level WHAT, the spec the high-level WHAT, the code the HOW, a comment only the non-obvious why).

The tree below is that layering made runnable. Ground your judgement in the doctrine, not in this summary of it.

## The standard

A comment or docstring earns its place only if it states something the code **cannot be made to carry**: an external contract, a hazard, a *why* that lives outside this code. The test is whether the code *could* carry it, not whether it happens to today — an intent the code merely fails to enact (an ordering nothing enforces, an invariant nothing checks) reads as unobservable but is a design defect the comment is papering over, not a fact that earns a keep. Anything that describes *what the code does* is forbidden, docstrings included: a module or function docstring that names the code's job is describing the code, so it goes. A comment is never a licence to leave code unclear.

## The tree

Most of this work is not deleting comments; it is making the code carry what the comment was carrying, after which the comment has nothing left to say. For each comment and docstring in scope, in order:

1. **Does it state something strictly not observable from the code?** If no, it describes the code: steps 2 and 3 make the code carry what it was saying, and only then does the comment go. If yes, ask one more question, because *not observable* has two causes and only one earns a keep:
   - **The code could not carry it** — an external contract, a hazard, a decision's reason, a *why* that lives outside this file. It stays; ask whether the spec is its better home, and move it there if so.
   - **The code fails to carry it** — the comment states an intent the code should enact but doesn't: an order nothing enforces (`in dependency order`), an exhaustiveness nothing checks, a `must run before X`, a `kept in sync with Y`. This is a smoke alarm, not a keep — the verbiage is a gift pointing at the design defect underneath. Route it into steps 2 and 3: make the code carry the intent (enforce the invariant, restructure so the order is manifest in the data flow, add the behavioral test), then the comment goes with the rest.

   The tell between the two: could the code be changed so the fact no longer needs saying? If yes, it is the second case — however true, and however unobservable it is today.
2. **Make the names carry the meaning.** Rename for literacy. The tells of a name doing a comment's job: an abbreviation, an adjective or preposition standing in for a noun or verb, a grammatically incomplete name, or a clever expression explained in prose instead of unpacked into named steps.
3. **Is the piece still illegible once the names are literate?** Then the comment was masking a deeper failure (of factorization or of test design), not a naming gap. Do not settle for a cosmetic rename: reject this implementation of the piece, ask the five whys to find the root cause, and re-implement it for clarity. Clarity always translates to maintainability; that is what the re-implementation buys.

Delete the comment only once the code carries what it was carrying; deletion is the last act, never a substitute for making the code legible.

## The documentation pass

Read the documentation the PR touches for the same fault, prose that does not carry its weight:

- **Self-indulgence and rambling**: prose written for the writer, not the next reader (throat-clearing, repetition, the scenic route to a point one sentence would make).
- **Ephemeral references**: tracker ids, and history-against-a-prior-state framing, that mean nothing to a future Bob who never saw the state they name.

Cut or tighten what fails. Where the content is real but misplaced, relocate it to the layer that owns it rather than deleting it.

## Apply, don't report

Winnow makes the edits in the working tree. It is not a review that hands back a list; each passage is disposed of where it lives, so the diff that reaches review is already clean. When the honest fix is to re-implement a piece rather than re-word a line, that is the work winnow does, not a follow-up it defers.

## The neutral gate

The disposition winnow gets wrong is the fig leaf it keeps: a comment stating an intent the code does not enact, kept because the intent is genuinely not observable from the code — which reads as "the code can't carry it" when the truth is "the code fails to carry it." You are the worst-placed reader to catch your own: having just decided to keep each comment, seeing the fig leaf means overturning your own call, and the same reasoning that let it stand the first time stands ready to let it stand again. So the last act before the exit is to hand the pass's survivors to a reader who has no such investment.

Spawn a clean-context subagent and feed it [`gate.md`](gate.md) verbatim, followed by the comments this pass left standing, each with the code it annotates. Give it the survivors and their code and nothing else — never your reasoning for keeping them; that reasoning is exactly what it exists to test, and reading it would let it inherit your justification instead of the result. It returns the fig leafs it can quote, or "none."

For each one it flags, do the owed escalation: route the comment back into steps 2 and 3 of the tree — make the code carry the intent (enforce the invariant, restructure so the order is manifest, add the behavioral test), then delete the comment. The gate names the finding; the escalation is winnow's own work, the same work step 1 routes there. Do not argue the flag away: a clean-context reader quoting an unenforced intent is the signal step 1 is built to act on, not a second opinion to weigh against your own. Trust the gate on the fig leaf, and only the fig leaf — it does not judge your cuts, your renames, or the surface you chose, so a "none" is not licence and a flag beyond the fig-leaf pattern is not its to give.

A gate escalation changes code, and that changed code is still the winnow's own work: it leaves through the same exit below, inside the pass's one commit.

## The pass ends on the remote

An unpushed winnow is indistinguishable from one that never ran: the operator reads the pass's work on the remote, never in your working tree. Finishing the edits is therefore not finishing the pass.

Commit the edits as their own commit — the winnow's work and nothing else, so the pass reads as one diff — and carry it out as a revision of the tendered PR, per `tender`'s revision SOP: local CI first (a comment edit can still break a lint gate), a new commit, push; the pull request updates to the new head, and tender's CI watch gives the verdict. Size does not modulate this: a one-character edit is still read on the remote.

When the work has not yet been tendered, the tender ahead is this exit: the winnow's commit rides to the pull request with the rest of the work. Only the operator's own instruction — a "don't push it yet" in the invocation — holds any of it back.

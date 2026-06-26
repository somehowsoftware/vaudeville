---
name: _continue_full_process
description: >
  Machinery, not a human command: the cold implementation body the full-process
  procedure checkpoints into. Implement the committed design carried across the
  clear, re-read the design Doctrine against the diff, then branch on the working
  tree: committable changes hand off to _tender; a clean tree means nothing was
  produced; surface that, or refer genuinely off-tree work to its own procedure.
---

# Continue full process

## You arrive grounded

This skill is invoked by the Resume Brief: the first turn of this cleared session, already in the conversation above. It carries the operator's verbatim turns (the Digest) and your own Carryover, which holds the **committed design** the warm [Design](../design/SKILL.md) pass produced; you read both on the way here, and there is nothing to fetch. Honor the Brief's discipline throughout: the latest operator turn is the live one, the Carryover's pointers are essential, and any doctrine or domain term you lean on gets re-read from its source; a cleared context presents as fluency, not as ignorance. If no Resume Brief sits above you, something invoked this skill out of band; stop and say so rather than improvise grounding.

## Implement, then tender it

`/_continue_full_process` *is* the implementation: you arrive with the committed design in the Carryover, and turning it into reality is your first move, not a precondition you reach for it after. What happens next is read from the working tree (the Procedure below), not declared in advance.

## Procedure

### 1. Re-read the doctrine to reground

Before you write, re-read the design Doctrine (currently `~/.vaudeville/doctrine/code/design.md`) from the file. The warm Design pass leaned on it, but that pass ran in the conversation the clear just shed; this fresh context holds a fluent memory of the doctrine, not the doctrine itself.

The warm Design pass was the **opening half of the Doctrine Bracket**; this reground is not that half over again: it is how the cold implementer recovers the frame the warm context held. The closing half is step 4.

### 2. Implement the committed design

The committed design is in the Carryover, in the Resume Brief above, the three axes the [Design](../design/SKILL.md) pass settled: the domain terms, the interaction with existing code and its refactors, and the contracts the tests must keep. Implement *that*; do not re-derive it. The design was committed warm, with the conversation in hand, and it crossed the clear as prose precisely so this context does not re-litigate it.

Having re-read the doctrine, ground the committed design against it before you write (a check, not a re-derivation):

- Does the committed design still map cleanly onto the ubiquitous language: the framework UL at `~/.vaudeville/doctrine/vocabulary.md` and the Context's local UL (typically `docs/vocabulary.md`)? If the design named a new term, was the vocabulary actually grown? Grow it now if the warm pass said it would and the change is not yet on disk.
- Are the pieces named in domain terms, each module owning one piece, the contracts written as tests before the modules that satisfy them?

If the committed design and the freshly re-read doctrine disagree (a piece the design left unnamed, a contract it stated in implementation terms), that disagreement is a real signal, not noise to smooth over. Work it out and record the disagreement and how you resolved it in the pull request; this is work you carry to review, not a halt for permission. Return to the operator only if resolving it would overturn the goal you were dispatched to realize.

**As a reminder: implementation details are not domain concepts. Domain concepts are domain concepts. Adding implementation details to the UL is contamination. Do not do this.**

Then implement.

### 3. Branch on working-tree state

After implementation, check whether the working tree has any committable changes: tracked modifications, staged changes, or new untracked files (modulo `.gitignore`). The standard idiom is `git status --porcelain`, whose stdout is empty exactly when the tree is clean:

```bash
test -z "$(git status --porcelain)"
```

- **Non-zero exit (working tree has changes)** → continue with step 4, the contribution shape.
- **Zero exit (working tree clean)** → skip to step 6, the clean-tree case.

`git diff --quiet HEAD` is the obvious shorter form but it ignores untracked files; an assignment that creates new files (and modifies none) would be misclassified as a clean tree and lose its deliverable. `git status --porcelain` covers tracked, staged, and untracked alike, which is what the predicate actually wants.

The working-tree state is the source of truth for which shape the assignment takes; do not declare the shape in advance and do not override the branch decision here.

### 4. Re-read the design Doctrine _again_: the closing half of the Bracket

Re-read the design Doctrine (currently `~/.vaudeville/doctrine/code/design.md`), now with the diff in hand.

Ask whether the PR you are about to tender is in service of the design discipline's stated goals:

- Pieces named in domain terms, not in implementation verbs.
- Each module owning exactly one piece, with no orchestrator-shaped vacancies threading state across phases.
- Contracts written as tests before the modules that satisfy them.
- Names that hit the reader over the head, drawn from the ubiquitous language.
- Technical surplus on net: easier to work in next week than what was there before.

If any answer is no, **revise before continuing**. The cost of revising now is a re-run of local CI; the cost of revising after `/parlay` is a Codex round-trip, an angry operator, and/or an avoidable follow-up assignment. CI green is not a surplus deposit, and the diff is what the operator will read.

This is the closing half of the **Doctrine Bracket**; the warm Design pass opened it.

### 5. Tender the result

Invoke `_tender` via the Skill tool with no arguments. It runs local CI, commits under the assignment id, pushes, opens the pull request, and hands off to `/parlay`, the shared carry-to-PR piece, so the steps live there, not here. Invoking it is the last thing this skill does on the contribution path.

### 6. Clean tree: diagnose, then surface or refer

Implementation left nothing to commit, and why decides what you do. Almost always it is a problem: work that should have produced a diff didn't (a forgotten save, a no-op refactor, a misread of the assignment). For a contribution procedure that is not a deliverable; stop and surface it plainly (what you did and why the tree is clean) rather than reporting a success.

The other case is that the assignment's deliverable genuinely never lived in the tree (a tracker mutation, an infrastructure or third-party state change, a process action), and the medium was misjudged when this work was routed here. That work is real, but it belongs to the [off-tree process](../_off_tree_process/SKILL.md). Do not complete it here; go back to [`/realize`](../realize/SKILL.md), which dispatches it to the procedure built for it. This branch refers; it does not become a second completion path.

## On failure

If any step fails and you cannot resolve it, stop and return to the operator with which step failed, the error output, and what you tried. Do not retry indefinitely; a settled design should implement straightforwardly, and a stuck implementation is often a sign the committed design needs another look, not more force.

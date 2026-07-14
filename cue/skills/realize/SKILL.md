---
name: realize
description: >
  The single public front door to realizing an assignment, the router a Bob reaches
  for once it is ready to make its assignment real. It makes one judgment: does this
  carry unsettled flow-control design, putting it on the design-bracketed path
  (full-process for code in hand, a spike when the code's shape is still sketchy,
  and prose-process for any agent-facing prose composition, however settled it
  feels), or is the design settled, sorting it by
  where the deliverable belongs (minimal-process in the tree, off-tree process
  outside it), or is it not realization work at all. It then dispatches, redirects,
  or stops accordingly.
---

# Realize

Make real the assignment you have been working. `/realize` is the **router**: it makes one judgment and acts on it. It does not implement, run CI, or open the pull request; a procedure it dispatches to does that. The router only decides.

You arrive holding what the judgment needs. You have worked this assignment: you know whether realizing it still carries a design you have not settled, where the substance of that design lives, and (when it is code) whether you know how to build it or are still guessing at the shape. The router reads what you already know; it does not re-derive it.

## The judgment

One question comes first, before anything about the medium: does realizing this assignment still carry a **flow-control design you have not settled**: a flow you must work out before committing to the artifact that carries it, whether that flow steers a machine (code) or an agent (a skill, a doctrine passage)?

That question sorts the work three ways:

- **Unsettled flow-control design** puts you on the **design-bracketed path**, and the medium only picks which specialization of it you run (situation 1).
- **Settled design** means the bracket would find nothing to do; sort by where the deliverable belongs (situations 2 and 3).
- **No artifact to produce at all** (a plan, a manual conversation), and `/realize` is not your tool (situation 4).

Agent-facing prose composition is defined as the authorship of new or modified prose through the considered selection of words. It is essential to distinguish prose composition from mechanical editing, such as systematically renaming X to Y. 

Prose composition _always_ goes through the prose-process path. There are no exceptions, no matter how short or seemingly trivial the prose appears to be. Remember: if the agent has been asked to edit a single phrase, it is because _the operator believes that phrase so important as to justify an agent's dedicated attention._ 

### 1. Unsettled flow-control design → the design-bracketed path

Two things put you here: a flow-control design you have not settled and must work out before committing to the artifact that carries it, or agent-facing prose you are composing, which belongs here whether or not its design is settled. This is the heavyweight path; it specializes by the medium the work lives in. Pick the specialization by **where the substance lives**, not by which files the change happens to touch:

- **In code, and you have a rough grip on how to build it → [full-process](../_full_process/SKILL.md).** Real code with genuine design substance: a new feature, a deep refactor, more than a handful of functions. A [Design](../design/SKILL.md) pass as a matter of course, implementation behind the design-Doctrine bracket, then [Tender](../_tender/SKILL.md): local CI, commit, push, the pull request, hand to [`/parlay`](../parlay/SKILL.md).
- **In code, but the shape is still too sketchy to build well → [`/spike`](../spike/SKILL.md) first.** Same kind of work (real code), but enough is unclear that you would build it better by learning the shape first: get something working to learn from, under the commitment that the code is thrown away. Once the spike has done its job and you and the operator are aligned, you either abandon the assignment or come back to `/realize`, and now the code is in hand. Spike can also be elected by name directly when the path is known to be too hazy to realize cleanly.
- **In agent-facing prose → [prose-process](../_prose_process/SKILL.md).** The artifact is prose that steers an agent: a skill, a doctrine passage, framing that installs a model in a capable reader. The procedure partitions the prose into reader-situations and composes each through [`/prose`](../prose/SKILL.md) (which grounds its premises against their source, settles the framing with [`/frame`](../frame/SKILL.md), drafts, purges from the reader's chair, and tests the result by its effect with [`/assay`](../assay/SKILL.md)), then delivers the pieces in one pull request.

For code, the substance has to be a design you have **not settled**: if it is settled and what remains is mechanical, even on something large, you are not here; you are in situation 2 or 3. Prose does not get that out; the composition is the work whether or not the design moved, so it always takes prose-process and never folds into full-process. When an assignment carries both prose you are composing and substantive code work (a design still unsettled, or one settled but larger than a mechanical edit), that is two assignments, not one: prose-process carries only mechanical companions, so the code's substance takes its own procedure. Coupled, they realize in dependency order; independent, they are simply two. Only a merely mechanical edit in the other medium (a rename, a link fix, a registry entry) rides along: not a second design, it is part of the chosen procedure's work and tenders with it.

### 2. Settled design, ships in the repo as a PR → minimal-process

The change belongs in the repository and goes through a pull request, and the design is already settled: no flow left to work out. The design was settled in conversation, or the change never had one: a rename, a file move, a winnow run, a dependency bump that breaks one syntax across many call sites, a one-line change whose consequences earned an assignment while its diff stays tiny and obvious. Composing agent-facing prose is never one of these, however settled it feels; it is always situation 1. This is [minimal-process](../_minimal_process/SKILL.md): it keeps the contribution tail (commit, CI, the pull request, the convergence in `/parlay`) and drops the Design pass and panel.

The gate is a checkable condition, not the feeling that the shape is obvious; that feeling is the unreliable signal the design-bracketed path exists to route around. Default to *unsettled* and make the work earn its way here: the design is settled only if a second careful reader, handed the same goal and the same Doctrine and nothing you are holding in your head, would produce a materially equivalent artifact. If you cannot name where the design was already settled, it was not, and you are in situation 1.

### 3. Settled design, deliverable never touches the tree → off-tree process

The work has a concrete deliverable and you know what it is, but it produces nothing in the git tree: a tracker field mutation, an infrastructure or third-party state change, a process action whose result lives in another system's state rather than in a diff. There is nothing to commit, so there is no pull request. This is the [off-tree process](../_off_tree_process/SKILL.md): it executes the action and hands to closeout's no-PR delivered path (no Design pass, no Tender, no Parlay).

What separates this from situation 2 is only where the deliverable belongs: the dividing question is whether it belongs in the tree, not how large or how mechanical the work is. On-tree work commits and takes a pull request; off-tree work has no git artifact, so its review is the Route's instead.

### 4. Not realization work at all → squawk and stop

If there is no artifact to make real (a plan whose deliverable is child Assignments, or a manual conversation) then `/realize` is not the tool you need. Off-tree work (situation 3) enacts a concrete state change; a plan and a manual produce no change to enact at all. **Do not force it through a procedure anyway.** Say so plainly, name what the task actually is, and stop.

## Dispatch

Situation 1 dispatches by the medium the unsettled design lives in. For code in hand, invoke `_full_process` via the Skill tool with no arguments: it runs the warm Design pass and checkpoints into its cold implementation body. For code whose shape is still sketchy, reach for `/spike`. For agent-facing prose, invoke `_prose_process` via the Skill tool with no arguments: it partitions the prose into reader-situations, composes each through `/prose`, and delivers once. For situation 2, invoke `_minimal_process` via the Skill tool with no arguments: it grounds in the Doctrine that still applies, implements, and tenders. For situation 3, invoke `_off_tree_process` via the Skill tool with no arguments: it grounds, executes the action, and hands to closeout. For situation 4, stop. Dispatching (or stopping) is the last thing the router does.

## The handoff

Dispatching to a procedure is where the wheel changes hands. The operator has been shaping the goal with you; from the dispatch on, the procedure carries this work to its review under your own judgement — a pull request, for the procedures that tender one — and that review, not a stop before it, is where the operator weighs what you did. A divergence you meet downstream — the panel raising one against your plan, a finding in the code, a surprise in implementation — is information for that review, not a request for instruction. Each procedure says how to dispose of one where it lands.

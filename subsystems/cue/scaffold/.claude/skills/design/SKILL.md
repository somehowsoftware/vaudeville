---
name: design
model: opus
description: >
  Run a design pass after the goal is agreed and before implementation: consult
  `/panel` on the clean approach, then surface a committed design across three
  axes: the new or defective domain terms, how the work should interact with
  existing code (including the refactors a clean design needs), and the
  domain-derived contracts the tests must keep. The full-process procedure runs
  it as a matter of course; it also runs standalone. Writes no durable doc.
---

# Design

A design pass for the Bob lifecycle, run **after you and the operator have agreed what to build** and **before implementation**. It moves domain-design thinking ahead of implementation, so the clean approach is decided up front rather than discovered through review after the code is written. The pass consults `/panel` to sharpen the Bob across five outside lenses, then has the Bob commit to a design along three axes and surface it to the operator. That committed design is what the implementation body then builds.

Whether Design runs is not the operator's opt-in but a property of the procedure the [router](../realize/SKILL.md) selected. [full-process](../_full_process/SKILL.md) invokes `/design` as a matter of course: folding it in removes the discretion to skip, a blind spot the agent is systematically overconfident about and that exhortation does not fix. A lighter procedure may omit it. And `/design` stays a public skill in its own right: reach for it standalone when a clean approach is worth getting right before code.

**When to use:** the goal is settled (you and the operator know *what* the work is and that it serves the bigger picture) and the *how* is non-trivial. Inside full-process it runs automatically; standalone, run it in the same Bob that will realize the work, so the design it produces is the plan the implementation arrives with.

**When not to use:**

- To decide *whether* or *what* to build. That is the conversation before `/design`; this pass assumes the goal is agreed.
- As a standalone heavyweight pass over work that is not heading into a realization. A procedure that should omit Design omits it by not invoking it; building the smallest thing that serves the goal cuts against forcing a full pass where the procedure did not call for one.

## The three axes

The committed design covers exactly three things, the three places where a design that was never made explicit shows up as rework in review:

1. **Domain terms.** What new ubiquitous-language terms the work introduces, and which existing terms it shows to be defective or mis-scoped. A concept with no name is the most expensive thing to discover late: when a piece is never named, two consumers each re-derive it and drift apart. Name the missing piece (or correct the defective term) before code, and grow the vocabulary first.
2. **Interaction with existing code.** How the work should sit in the code already there, including the refactors a clean design requires rather than bolting the new work on beside what exists. Derive from one definition; do not stand up a second consumer that re-derives what another already knows.
3. **The contracts the tests must keep.** The domain-derived promises the suite will pin, each a contract stated in domain terms (*given pieces X and Y, interaction Z produces a result with property P*), written before the modules that satisfy them.

## Procedure

### 1. Frame the design question

From the agreed goal in the conversation, state the design problem as a single question: the clean way to build this thing in this codebase. This is the question the panel will hear; conversation context stays in your head for the synthesis, not in the question.

### 2. Consult `/panel`

Invoke `/panel` via the Skill tool on the **design** cast, with the design question; the panel hosts more than one cast, and a programmatic caller names the one it needs rather than leaving the panel to choose. The design cast holds exactly the ground the three axes need (domain language and bounded-context boundaries, simple-design and test-first, illegal-states-unrepresentable, decomplected pieces, and the core/shell boundary), so the panel reads the design problem from the angles the axes will be answered along.

The panel is Socratic: its job is to sharpen *your* thinking, not to produce the design. You hold what the panel does not: this conversation, the actual code, and what the work is in service of.

### 3. Commit to the design

Read the panel through your own context and decide. Organize the result as the three axes above: the domain terms to add or correct, the interaction and refactors, and the contracts the tests will keep. Commit to each: a design is a position, not a survey of options. Where the panel split, say what the split turned on and which way you came down.

If the pass surfaces a new or defective term, this is where the vocabulary grows or is corrected: change the Context's UL (or the framework vocabulary) as part of the design, so the name is right before the code depends on it.

### 4. Surface the committed design

Surface the committed design, tight, organized as the three axes: the residue of the pass, distilled rather than dumped. `/design` itself does not implement, and it does not decide what happens next: whether to stop here is the **caller's** call, not this skill's.

- **Standalone** (run by hand, ahead of any procedure): surface to the operator and stop. The design lives in this conversation; the operator decides when to realize it.
- **Invoked by a procedure**: emit the committed design into the conversation and keep going in the same turn. This is not a decision point and it waits for no reply: the procedure's next step checkpoints, and the committed design crosses the clear as the Carryover. Stopping during an autonomous procedure breaks flow and is unnecessary; the operator has already pre-approved the agent's decision by starting an autonomous run.

## Non-goals

- **Does not write a durable design document.** The deliverable is the committed design in this conversation, which the implementation body inherits across the Checkpoint as the Carryover, not a file in the repo. A persistent design note whose purpose is to preserve a past decision is the decision-record / ADR anti-pattern the intent doctrine rules out; the *why* survives in the conversation, the PR, and the commit, not in a doc that rots as the code drifts.
- **Does not re-implement `/panel`.** It calls the shipped skill; tuning a cast is a PR against `/panel`, not a bespoke consult here.
